/**
 * Portal Rendering System
 * Recursive rendering through portals (like Portal game)
 * 
 * Features:
 * - Linked portal pairs
 * - Recursive rendering with depth limit
 * - Oblique near plane clipping
 * - Seamless object teleportation
 * - Virtual camera calculation
 * - Stencil-based masking
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface PortalDefinition {
  id: string;
  linkedPortalId: string | null;
  position: THREE.Vector3;
  rotation: THREE.Quaternion;
  size: THREE.Vector2;
  color: THREE.Color;
  renderTarget?: THREE.WebGLRenderTarget;
}

export interface PortalPair {
  portalA: string;
  portalB: string;
}

export interface PortalRenderConfig {
  maxRecursionDepth: number;
  renderTargetSize: THREE.Vector2;
  enableObliqueFrustum: boolean;
  portalMargin: number;  // Slightly inset to avoid z-fighting
}

// ============================================
// PORTAL MESH
// ============================================

export class PortalMesh extends THREE.Mesh {
  public portalId: string;
  public linkedPortalId: string | null = null;
  public portalSize: THREE.Vector2;
  
  constructor(id: string, size: THREE.Vector2, color: THREE.Color) {
    const geometry = new THREE.PlaneGeometry(size.x, size.y);
    const material = new THREE.ShaderMaterial({
      uniforms: {
        portalTexture: { value: null },
        portalColor: { value: color },
        time: { value: 0 },
        edgeGlow: { value: 0.1 }
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vWorldPosition;
        
        void main() {
          vUv = uv;
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vWorldPosition = worldPos.xyz;
          gl_Position = projectionMatrix * viewMatrix * worldPos;
        }
      `,
      fragmentShader: `
        uniform sampler2D portalTexture;
        uniform vec3 portalColor;
        uniform float time;
        uniform float edgeGlow;
        
        varying vec2 vUv;
        varying vec3 vWorldPosition;
        
        void main() {
          // Sample portal view texture
          vec4 portalView = texture2D(portalTexture, vUv);
          
          // Edge glow effect
          float edgeDist = min(
            min(vUv.x, 1.0 - vUv.x),
            min(vUv.y, 1.0 - vUv.y)
          );
          float glow = smoothstep(0.0, edgeGlow, edgeDist);
          float edge = 1.0 - glow;
          
          // Animate edge
          float pulse = 0.5 + 0.5 * sin(time * 3.0 + vUv.x * 10.0);
          
          // Combine portal view with edge glow
          vec3 edgeColor = portalColor * (1.0 + pulse * 0.5);
          vec3 finalColor = mix(edgeColor, portalView.rgb, glow);
          
          // Add slight shimmer
          float shimmer = 0.02 * sin(time * 5.0 + vWorldPosition.y * 20.0);
          finalColor += shimmer;
          
          gl_FragColor = vec4(finalColor, 1.0);
        }
      `,
      side: THREE.DoubleSide
    });
    
    super(geometry, material);
    
    this.portalId = id;
    this.portalSize = size;
  }
  
  public setPortalTexture(texture: THREE.Texture): void {
    (this.material as THREE.ShaderMaterial).uniforms.portalTexture.value = texture;
  }
  
  public setTime(time: number): void {
    (this.material as THREE.ShaderMaterial).uniforms.time.value = time;
  }
  
  public getPortalNormal(): THREE.Vector3 {
    return new THREE.Vector3(0, 0, 1).applyQuaternion(this.quaternion);
  }
  
  public getPortalCenter(): THREE.Vector3 {
    return this.position.clone();
  }
}

// ============================================
// VIRTUAL CAMERA CALCULATOR
// ============================================

export class VirtualCameraCalculator {
  /**
   * Calculate the virtual camera position and orientation
   * as if viewing through a linked portal
   */
  public calculateVirtualCamera(
    realCamera: THREE.Camera,
    sourcePortal: PortalMesh,
    destPortal: PortalMesh
  ): { position: THREE.Vector3; quaternion: THREE.Quaternion } {
    // Get camera position relative to source portal
    const sourceInverse = new THREE.Matrix4().copy(sourcePortal.matrixWorld).invert();
    const cameraInSourceSpace = realCamera.position.clone().applyMatrix4(sourceInverse);
    
    // Rotate 180° around Y to face through the portal
    const flipMatrix = new THREE.Matrix4().makeRotationY(Math.PI);
    cameraInSourceSpace.applyMatrix4(flipMatrix);
    
    // Transform to destination portal space
    const cameraInDestSpace = cameraInSourceSpace.clone().applyMatrix4(destPortal.matrixWorld);
    
    // Calculate rotation
    const sourceQuatInverse = sourcePortal.quaternion.clone().invert();
    const relativeQuat = realCamera.quaternion.clone().premultiply(sourceQuatInverse);
    
    // Apply flip
    const flipQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
    relativeQuat.premultiply(flipQuat);
    
    // Apply destination rotation
    const virtualQuat = relativeQuat.premultiply(destPortal.quaternion);
    
    return {
      position: cameraInDestSpace,
      quaternion: virtualQuat
    };
  }
  
  /**
   * Create oblique near plane frustum for portal clipping
   */
  public createObliqueProjectionMatrix(
    camera: THREE.PerspectiveCamera,
    portal: PortalMesh
  ): THREE.Matrix4 {
    // Get portal plane in camera space
    const portalNormal = portal.getPortalNormal();
    const portalCenter = portal.getPortalCenter();
    
    // Transform to camera space
    const viewMatrix = camera.matrixWorldInverse;
    const normalInCameraSpace = portalNormal.clone().transformDirection(viewMatrix);
    const pointInCameraSpace = portalCenter.clone().applyMatrix4(viewMatrix);
    
    // Create clip plane (Ax + By + Cz + D = 0)
    const clipPlane = new THREE.Vector4(
      normalInCameraSpace.x,
      normalInCameraSpace.y,
      normalInCameraSpace.z,
      -normalInCameraSpace.dot(pointInCameraSpace)
    );
    
    // Modify projection matrix
    const projectionMatrix = camera.projectionMatrix.clone();
    const q = new THREE.Vector4();
    
    q.x = (Math.sign(clipPlane.x) + projectionMatrix.elements[8]) / projectionMatrix.elements[0];
    q.y = (Math.sign(clipPlane.y) + projectionMatrix.elements[9]) / projectionMatrix.elements[5];
    q.z = -1;
    q.w = (1 + projectionMatrix.elements[10]) / projectionMatrix.elements[14];
    
    const c = clipPlane.multiplyScalar(2 / clipPlane.dot(q));
    
    projectionMatrix.elements[2] = c.x;
    projectionMatrix.elements[6] = c.y;
    projectionMatrix.elements[10] = c.z + 1;
    projectionMatrix.elements[14] = c.w;
    
    return projectionMatrix;
  }
}

// ============================================
// PORTAL TELEPORTER
// ============================================

export interface TeleportableObject {
  object: THREE.Object3D;
  velocity?: THREE.Vector3;
  onTeleport?: (sourcePortal: PortalMesh, destPortal: PortalMesh) => void;
}

export class PortalTeleporter {
  private teleportables: Map<THREE.Object3D, TeleportableObject> = new Map();
  private previousPositions: Map<THREE.Object3D, THREE.Vector3> = new Map();
  
  public registerTeleportable(teleportable: TeleportableObject): void {
    this.teleportables.set(teleportable.object, teleportable);
    this.previousPositions.set(teleportable.object, teleportable.object.position.clone());
  }
  
  public unregisterTeleportable(object: THREE.Object3D): void {
    this.teleportables.delete(object);
    this.previousPositions.delete(object);
  }
  
  public update(portals: Map<string, PortalMesh>): void {
    for (const [object, teleportable] of this.teleportables) {
      const prevPos = this.previousPositions.get(object);
      if (!prevPos) continue;
      
      const currentPos = object.position.clone();
      
      // Check each portal
      for (const [id, portal] of portals) {
        if (!portal.linkedPortalId) continue;
        
        const linkedPortal = portals.get(portal.linkedPortalId);
        if (!linkedPortal) continue;
        
        if (this.checkPortalCrossing(prevPos, currentPos, portal)) {
          this.teleport(object, teleportable, portal, linkedPortal);
          break;
        }
      }
      
      this.previousPositions.set(object, currentPos);
    }
  }
  
  private checkPortalCrossing(
    prevPos: THREE.Vector3,
    currentPos: THREE.Vector3,
    portal: PortalMesh
  ): boolean {
    const portalNormal = portal.getPortalNormal();
    const portalCenter = portal.getPortalCenter();
    
    // Check if crossed the portal plane
    const prevDist = prevPos.clone().sub(portalCenter).dot(portalNormal);
    const currDist = currentPos.clone().sub(portalCenter).dot(portalNormal);
    
    if (prevDist * currDist > 0) return false;  // Same side
    
    // Interpolate crossing point
    const t = prevDist / (prevDist - currDist);
    const crossingPoint = prevPos.clone().lerp(currentPos, t);
    
    // Check if within portal bounds
    const localPoint = crossingPoint.clone().applyMatrix4(
      new THREE.Matrix4().copy(portal.matrixWorld).invert()
    );
    
    const halfWidth = portal.portalSize.x / 2;
    const halfHeight = portal.portalSize.y / 2;
    
    return Math.abs(localPoint.x) <= halfWidth && Math.abs(localPoint.y) <= halfHeight;
  }
  
  private teleport(
    object: THREE.Object3D,
    teleportable: TeleportableObject,
    sourcePortal: PortalMesh,
    destPortal: PortalMesh
  ): void {
    // Calculate new position
    const sourceInverse = new THREE.Matrix4().copy(sourcePortal.matrixWorld).invert();
    const localPos = object.position.clone().applyMatrix4(sourceInverse);
    
    // Flip through portal
    localPos.z = -localPos.z;
    
    // Apply rotation difference
    const flipY = new THREE.Matrix4().makeRotationY(Math.PI);
    localPos.applyMatrix4(flipY);
    
    // Transform to destination
    const newPos = localPos.applyMatrix4(destPortal.matrixWorld);
    object.position.copy(newPos);
    
    // Transform rotation
    const sourceQuatInverse = sourcePortal.quaternion.clone().invert();
    const relativeQuat = object.quaternion.clone().premultiply(sourceQuatInverse);
    
    const flipQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
    relativeQuat.premultiply(flipQuat);
    
    object.quaternion.copy(relativeQuat.premultiply(destPortal.quaternion));
    
    // Transform velocity if present
    if (teleportable.velocity) {
      teleportable.velocity.applyMatrix4(sourceInverse);
      teleportable.velocity.z = -teleportable.velocity.z;
      teleportable.velocity.applyMatrix4(flipY);
      teleportable.velocity.transformDirection(destPortal.matrixWorld);
    }
    
    // Update previous position
    this.previousPositions.set(object, object.position.clone());
    
    // Callback
    teleportable.onTeleport?.(sourcePortal, destPortal);
  }
}

// ============================================
// MAIN PORTAL SYSTEM
// ============================================

export class PortalSystem {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private mainCamera: THREE.PerspectiveCamera;
  private portals: Map<string, PortalMesh> = new Map();
  private renderTargets: Map<string, THREE.WebGLRenderTarget> = new Map();
  private virtualCamera: THREE.PerspectiveCamera;
  private cameraCalculator: VirtualCameraCalculator;
  private teleporter: PortalTeleporter;
  private config: PortalRenderConfig;
  private time: number = 0;
  
  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.PerspectiveCamera,
    config: Partial<PortalRenderConfig> = {}
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.mainCamera = camera;
    
    this.config = {
      maxRecursionDepth: 4,
      renderTargetSize: new THREE.Vector2(1024, 1024),
      enableObliqueFrustum: true,
      portalMargin: 0.01,
      ...config
    };
    
    this.virtualCamera = camera.clone();
    this.cameraCalculator = new VirtualCameraCalculator();
    this.teleporter = new PortalTeleporter();
  }
  
  /**
   * Create a portal
   */
  public createPortal(
    id: string,
    position: THREE.Vector3,
    rotation: THREE.Quaternion,
    size: THREE.Vector2,
    color: THREE.Color
  ): PortalMesh {
    const portal = new PortalMesh(id, size, color);
    portal.position.copy(position);
    portal.quaternion.copy(rotation);
    
    // Create render target
    const renderTarget = new THREE.WebGLRenderTarget(
      this.config.renderTargetSize.x,
      this.config.renderTargetSize.y,
      {
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter,
        format: THREE.RGBAFormat,
        stencilBuffer: true
      }
    );
    
    this.portals.set(id, portal);
    this.renderTargets.set(id, renderTarget);
    this.scene.add(portal);
    
    return portal;
  }
  
  /**
   * Link two portals together
   */
  public linkPortals(portalAId: string, portalBId: string): void {
    const portalA = this.portals.get(portalAId);
    const portalB = this.portals.get(portalBId);
    
    if (!portalA || !portalB) {
      console.warn('Cannot link portals: one or both not found');
      return;
    }
    
    portalA.linkedPortalId = portalBId;
    portalB.linkedPortalId = portalAId;
  }
  
  /**
   * Unlink portals
   */
  public unlinkPortal(portalId: string): void {
    const portal = this.portals.get(portalId);
    if (!portal || !portal.linkedPortalId) return;
    
    const linkedPortal = this.portals.get(portal.linkedPortalId);
    if (linkedPortal) {
      linkedPortal.linkedPortalId = null;
    }
    portal.linkedPortalId = null;
  }
  
  /**
   * Remove a portal
   */
  public removePortal(id: string): void {
    const portal = this.portals.get(id);
    if (!portal) return;
    
    this.unlinkPortal(id);
    this.scene.remove(portal);
    portal.geometry.dispose();
    (portal.material as THREE.Material).dispose();
    
    const renderTarget = this.renderTargets.get(id);
    if (renderTarget) {
      renderTarget.dispose();
      this.renderTargets.delete(id);
    }
    
    this.portals.delete(id);
  }
  
  /**
   * Register a teleportable object
   */
  public registerTeleportable(teleportable: TeleportableObject): void {
    this.teleporter.registerTeleportable(teleportable);
  }
  
  /**
   * Unregister a teleportable object
   */
  public unregisterTeleportable(object: THREE.Object3D): void {
    this.teleporter.unregisterTeleportable(object);
  }
  
  /**
   * Update and render portals
   */
  public update(deltaTime: number): void {
    this.time += deltaTime;
    
    // Update portal animations
    for (const portal of this.portals.values()) {
      portal.setTime(this.time);
    }
    
    // Update teleportation
    this.teleporter.update(this.portals);
    
    // Render portal views
    this.renderPortals();
  }
  
  private renderPortals(): void {
    // Store current render state
    const currentRenderTarget = this.renderer.getRenderTarget();
    const currentXrEnabled = this.renderer.xr.enabled;
    this.renderer.xr.enabled = false;
    
    // Hide portals during their own rendering to avoid recursion artifacts
    const portalVisibility = new Map<string, boolean>();
    for (const [id, portal] of this.portals) {
      portalVisibility.set(id, portal.visible);
    }
    
    // Render each portal
    for (const [id, portal] of this.portals) {
      if (!portal.linkedPortalId) continue;
      
      const linkedPortal = this.portals.get(portal.linkedPortalId);
      if (!linkedPortal) continue;
      
      const renderTarget = this.renderTargets.get(id);
      if (!renderTarget) continue;
      
      // Render the view through this portal
      this.renderPortalView(portal, linkedPortal, renderTarget, 0);
      
      // Apply texture to portal
      portal.setPortalTexture(renderTarget.texture);
    }
    
    // Restore visibility
    for (const [id, visible] of portalVisibility) {
      const portal = this.portals.get(id);
      if (portal) portal.visible = visible;
    }
    
    // Restore render state
    this.renderer.setRenderTarget(currentRenderTarget);
    this.renderer.xr.enabled = currentXrEnabled;
  }
  
  private renderPortalView(
    sourcePortal: PortalMesh,
    destPortal: PortalMesh,
    renderTarget: THREE.WebGLRenderTarget,
    depth: number
  ): void {
    if (depth >= this.config.maxRecursionDepth) return;
    
    // Hide source portal during rendering
    sourcePortal.visible = false;
    
    // Calculate virtual camera
    const { position, quaternion } = this.cameraCalculator.calculateVirtualCamera(
      this.mainCamera,
      sourcePortal,
      destPortal
    );
    
    this.virtualCamera.position.copy(position);
    this.virtualCamera.quaternion.copy(quaternion);
    this.virtualCamera.updateMatrixWorld();
    
    // Apply oblique near plane if enabled
    if (this.config.enableObliqueFrustum) {
      const obliqueMatrix = this.cameraCalculator.createObliqueProjectionMatrix(
        this.virtualCamera,
        destPortal
      );
      this.virtualCamera.projectionMatrix.copy(obliqueMatrix);
    }
    
    // Recursive rendering for nested portals
    if (depth < this.config.maxRecursionDepth - 1) {
      for (const [id, otherPortal] of this.portals) {
        if (id === sourcePortal.portalId) continue;
        if (!otherPortal.linkedPortalId) continue;
        
        const otherLinked = this.portals.get(otherPortal.linkedPortalId);
        if (!otherLinked) continue;
        
        const otherRenderTarget = this.renderTargets.get(id);
        if (!otherRenderTarget) continue;
        
        // Check if portal is visible from virtual camera
        if (this.isPortalVisible(otherPortal, this.virtualCamera)) {
          this.renderPortalView(otherPortal, otherLinked, otherRenderTarget, depth + 1);
          otherPortal.setPortalTexture(otherRenderTarget.texture);
        }
      }
    }
    
    // Render to target
    this.renderer.setRenderTarget(renderTarget);
    this.renderer.clear();
    this.renderer.render(this.scene, this.virtualCamera);
    
    // Restore source portal visibility
    sourcePortal.visible = true;
  }
  
  private isPortalVisible(portal: PortalMesh, camera: THREE.Camera): boolean {
    // Simple frustum check
    const frustum = new THREE.Frustum();
    const projScreenMatrix = new THREE.Matrix4();
    
    projScreenMatrix.multiplyMatrices(
      camera.projectionMatrix,
      camera.matrixWorldInverse
    );
    frustum.setFromProjectionMatrix(projScreenMatrix);
    
    // Create bounding sphere for portal
    const sphere = new THREE.Sphere(
      portal.position,
      Math.max(portal.portalSize.x, portal.portalSize.y) / 2
    );
    
    return frustum.intersectsSphere(sphere);
  }
  
  /**
   * Get a portal by ID
   */
  public getPortal(id: string): PortalMesh | undefined {
    return this.portals.get(id);
  }
  
  /**
   * Get all portals
   */
  public getAllPortals(): PortalMesh[] {
    return Array.from(this.portals.values());
  }
  
  /**
   * Dispose the system
   */
  public dispose(): void {
    for (const id of this.portals.keys()) {
      this.removePortal(id);
    }
    
    this.virtualCamera.clear();
  }
}

// ============================================
// PORTAL HELPERS
// ============================================

export class PortalHelpers {
  /**
   * Create a portal pair (like Portal game orange/blue)
   */
  public static createPortalPair(
    system: PortalSystem,
    portalAPos: THREE.Vector3,
    portalANormal: THREE.Vector3,
    portalBPos: THREE.Vector3,
    portalBNormal: THREE.Vector3,
    size: THREE.Vector2 = new THREE.Vector2(2, 3)
  ): PortalPair {
    const quatA = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 0, 1),
      portalANormal
    );
    
    const quatB = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 0, 1),
      portalBNormal
    );
    
    const portalA = system.createPortal(
      'portal_orange',
      portalAPos,
      quatA,
      size,
      new THREE.Color(0xff6600)
    );
    
    const portalB = system.createPortal(
      'portal_blue',
      portalBPos,
      quatB,
      size,
      new THREE.Color(0x0066ff)
    );
    
    system.linkPortals('portal_orange', 'portal_blue');
    
    return {
      portalA: 'portal_orange',
      portalB: 'portal_blue'
    };
  }
  
  /**
   * Place portal on surface from raycast
   */
  public static placePortalFromRaycast(
    system: PortalSystem,
    portalId: string,
    raycaster: THREE.Raycaster,
    targets: THREE.Object3D[],
    size: THREE.Vector2,
    color: THREE.Color
  ): PortalMesh | null {
    const intersects = raycaster.intersectObjects(targets, true);
    
    if (intersects.length === 0) return null;
    
    const hit = intersects[0];
    if (!hit.face) return null;
    
    const normal = hit.face.normal.clone().transformDirection(
      hit.object.matrixWorld
    );
    
    const position = hit.point.clone().add(normal.clone().multiplyScalar(0.01));
    
    const quaternion = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 0, 1),
      normal
    );
    
    return system.createPortal(portalId, position, quaternion, size, color);
  }
}

