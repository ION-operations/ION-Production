/**
 * Portal Rendering System
 * Recursive portal rendering with stencil buffer
 * 
 * Features:
 * - Stencil-based portal masking
 * - Recursive rendering (up to N levels)
 * - Seamless camera teleportation
 * - Oblique near-plane clipping
 * - Portal surface effects
 * - Frustum culling optimization
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface PortalPair {
  id: string;
  portalA: Portal;
  portalB: Portal;
}

export interface Portal {
  id: string;
  mesh: THREE.Mesh;
  position: THREE.Vector3;
  rotation: THREE.Quaternion;
  size: THREE.Vector2;
  linkedPortal: Portal | null;
  renderTarget: THREE.WebGLRenderTarget;
  virtualCamera: THREE.PerspectiveCamera;
  stencilRef: number;
  isActive: boolean;
}

export interface PortalTraveler {
  object: THREE.Object3D;
  previousSide: number;  // -1 or 1
  velocity: THREE.Vector3;
}

// ============================================
// PORTAL SHADERS
// ============================================

const PortalVertexShader = `
varying vec4 vScreenPos;
varying vec2 vUv;
varying vec3 vWorldPos;

void main() {
  vUv = uv;
  vec4 worldPosition = modelMatrix * vec4(position, 1.0);
  vWorldPos = worldPosition.xyz;
  
  vec4 mvPosition = viewMatrix * worldPosition;
  vec4 screenPos = projectionMatrix * mvPosition;
  
  vScreenPos = screenPos;
  gl_Position = screenPos;
}
`;

const PortalFragmentShader = `
uniform sampler2D portalTexture;
uniform float time;
uniform float distortion;
uniform vec3 edgeColor;
uniform float edgeWidth;

varying vec4 vScreenPos;
varying vec2 vUv;
varying vec3 vWorldPos;

void main() {
  // Screen space UVs
  vec2 screenUV = vScreenPos.xy / vScreenPos.w * 0.5 + 0.5;
  
  // Edge glow
  float edgeDist = min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y));
  float edge = smoothstep(0.0, edgeWidth, edgeDist);
  
  // Distortion
  float distortionAmount = distortion * (1.0 - edge);
  vec2 distortedUV = screenUV;
  distortedUV.x += sin(vUv.y * 10.0 + time * 2.0) * distortionAmount * 0.02;
  distortedUV.y += cos(vUv.x * 10.0 + time * 2.0) * distortionAmount * 0.02;
  
  // Sample portal texture
  vec4 portalColor = texture2D(portalTexture, distortedUV);
  
  // Edge glow effect
  vec3 glow = edgeColor * (1.0 - edge) * 2.0;
  
  // Combine
  vec3 finalColor = portalColor.rgb + glow;
  
  gl_FragColor = vec4(finalColor, 1.0);
}
`;

// Simple stencil mask shader
const StencilVertexShader = `
void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const StencilFragmentShader = `
void main() {
  gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
`;

// ============================================
// OBLIQUE NEAR PLANE HELPER
// ============================================

export class ObliqueNearPlane {
  /**
   * Modify projection matrix to use oblique near clipping plane
   * This prevents rendering objects behind the portal
   */
  public static setObliqueClipPlane(
    camera: THREE.PerspectiveCamera,
    clipPlane: THREE.Plane
  ): void {
    const projectionMatrix = camera.projectionMatrix.clone();
    
    // Transform clip plane to camera space
    const viewMatrix = camera.matrixWorldInverse;
    const clipPlaneCamera = new THREE.Vector4(
      clipPlane.normal.x,
      clipPlane.normal.y,
      clipPlane.normal.z,
      clipPlane.constant
    );
    
    // Transform plane normal
    const planeNormal = new THREE.Vector3(
      clipPlane.normal.x,
      clipPlane.normal.y,
      clipPlane.normal.z
    );
    planeNormal.transformDirection(viewMatrix);
    
    // Transform plane point
    const planePoint = clipPlane.normal.clone().multiplyScalar(-clipPlane.constant);
    planePoint.applyMatrix4(viewMatrix);
    
    clipPlaneCamera.set(
      planeNormal.x,
      planeNormal.y,
      planeNormal.z,
      -planePoint.dot(planeNormal)
    );
    
    // Calculate the new projection matrix
    const q = new THREE.Vector4();
    q.x = (Math.sign(clipPlaneCamera.x) + projectionMatrix.elements[8]) / projectionMatrix.elements[0];
    q.y = (Math.sign(clipPlaneCamera.y) + projectionMatrix.elements[9]) / projectionMatrix.elements[5];
    q.z = -1.0;
    q.w = (1.0 + projectionMatrix.elements[10]) / projectionMatrix.elements[14];
    
    const c = clipPlaneCamera.multiplyScalar(2.0 / clipPlaneCamera.dot(q));
    
    projectionMatrix.elements[2] = c.x;
    projectionMatrix.elements[6] = c.y;
    projectionMatrix.elements[10] = c.z + 1.0;
    projectionMatrix.elements[14] = c.w;
    
    camera.projectionMatrix.copy(projectionMatrix);
  }
}

// ============================================
// PORTAL CAMERA
// ============================================

export class PortalCamera {
  private camera: THREE.PerspectiveCamera;
  
  constructor(fov: number, aspect: number, near: number, far: number) {
    this.camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
  }
  
  /**
   * Position the virtual camera as if looking through the portal
   */
  public updateFromPortal(
    mainCamera: THREE.Camera,
    sourcePortal: Portal,
    destPortal: Portal
  ): THREE.PerspectiveCamera {
    // Get camera position relative to source portal
    const relativePos = mainCamera.position.clone()
      .sub(sourcePortal.position);
    
    // Rotate 180 degrees to face out of destination portal
    const rotation = new THREE.Quaternion()
      .setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
    
    // Calculate transformation from source to dest portal
    const sourceToWorld = new THREE.Matrix4().compose(
      sourcePortal.position,
      sourcePortal.rotation,
      new THREE.Vector3(1, 1, 1)
    );
    
    const worldToDest = new THREE.Matrix4().compose(
      destPortal.position,
      destPortal.rotation.clone().multiply(rotation),
      new THREE.Vector3(1, 1, 1)
    );
    
    // Transform camera
    const transform = worldToDest.multiply(
      sourceToWorld.clone().invert()
    );
    
    // Apply to camera
    this.camera.position.copy(mainCamera.position);
    this.camera.quaternion.copy(mainCamera.quaternion);
    this.camera.position.applyMatrix4(transform);
    
    const mainQuat = mainCamera.quaternion.clone();
    const portalQuat = sourcePortal.rotation.clone().invert()
      .multiply(rotation)
      .multiply(destPortal.rotation);
    this.camera.quaternion.copy(portalQuat.multiply(mainQuat));
    
    this.camera.updateMatrixWorld();
    
    // Copy projection settings from main camera
    if (mainCamera instanceof THREE.PerspectiveCamera) {
      this.camera.fov = mainCamera.fov;
      this.camera.aspect = mainCamera.aspect;
      this.camera.near = mainCamera.near;
      this.camera.far = mainCamera.far;
      this.camera.updateProjectionMatrix();
    }
    
    return this.camera;
  }
  
  public getCamera(): THREE.PerspectiveCamera {
    return this.camera;
  }
}

// ============================================
// PORTAL TRAVELER HANDLER
// ============================================

export class TravelerHandler {
  private travelers: Map<string, PortalTraveler> = new Map();
  
  /**
   * Register an object that can travel through portals
   */
  public register(id: string, object: THREE.Object3D, velocity: THREE.Vector3 = new THREE.Vector3()): void {
    this.travelers.set(id, {
      object,
      previousSide: 0,
      velocity
    });
  }
  
  public unregister(id: string): void {
    this.travelers.delete(id);
  }
  
  /**
   * Check and handle portal traversal
   */
  public update(portals: Portal[]): void {
    for (const [id, traveler] of this.travelers) {
      for (const portal of portals) {
        if (!portal.linkedPortal || !portal.isActive) continue;
        
        // Calculate which side of portal plane the traveler is on
        const portalNormal = new THREE.Vector3(0, 0, 1)
          .applyQuaternion(portal.rotation);
        
        const toTraveler = traveler.object.position.clone()
          .sub(portal.position);
        
        const currentSide = Math.sign(toTraveler.dot(portalNormal));
        
        // Check if traveler is within portal bounds
        const localPos = traveler.object.position.clone()
          .sub(portal.position)
          .applyQuaternion(portal.rotation.clone().invert());
        
        const inBounds = Math.abs(localPos.x) < portal.size.x / 2 &&
                         Math.abs(localPos.y) < portal.size.y / 2;
        
        // Detect crossing
        if (traveler.previousSide !== 0 && 
            currentSide !== traveler.previousSide && 
            inBounds) {
          this.teleport(traveler, portal, portal.linkedPortal);
        }
        
        traveler.previousSide = currentSide;
      }
    }
  }
  
  /**
   * Teleport traveler through portal
   */
  private teleport(
    traveler: PortalTraveler,
    sourcePortal: Portal,
    destPortal: Portal
  ): void {
    // Create transformation matrix
    const rotation180 = new THREE.Quaternion()
      .setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
    
    const sourceInverse = new THREE.Matrix4().compose(
      sourcePortal.position,
      sourcePortal.rotation,
      new THREE.Vector3(1, 1, 1)
    ).invert();
    
    const destMatrix = new THREE.Matrix4().compose(
      destPortal.position,
      destPortal.rotation.clone().multiply(rotation180),
      new THREE.Vector3(1, 1, 1)
    );
    
    const transform = destMatrix.multiply(sourceInverse);
    
    // Transform position
    traveler.object.position.applyMatrix4(transform);
    
    // Transform rotation
    const destQuat = sourcePortal.rotation.clone().invert()
      .multiply(rotation180)
      .multiply(destPortal.rotation);
    traveler.object.quaternion.premultiply(destQuat);
    
    // Transform velocity
    traveler.velocity.applyQuaternion(destQuat);
    
    // Flip side
    traveler.previousSide *= -1;
    
    traveler.object.updateMatrixWorld();
  }
}

// ============================================
// MAIN PORTAL SYSTEM
// ============================================

export class PortalSystem {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private portals: Map<string, Portal> = new Map();
  private portalPairs: Map<string, PortalPair> = new Map();
  private travelerHandler: TravelerHandler;
  private portalCamera: PortalCamera;
  private maxRecursion: number;
  private renderSize: THREE.Vector2;
  
  private stencilMaterial: THREE.ShaderMaterial;
  private portalMaterial: THREE.ShaderMaterial;
  private time: number = 0;
  private nextStencilRef: number = 1;
  
  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    maxRecursion: number = 2
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.maxRecursion = maxRecursion;
    this.travelerHandler = new TravelerHandler();
    
    this.renderSize = new THREE.Vector2();
    renderer.getSize(this.renderSize);
    
    this.portalCamera = new PortalCamera(
      75,
      this.renderSize.x / this.renderSize.y,
      0.1,
      1000
    );
    
    // Create stencil material
    this.stencilMaterial = new THREE.ShaderMaterial({
      vertexShader: StencilVertexShader,
      fragmentShader: StencilFragmentShader,
      colorWrite: false,
      depthWrite: false
    });
    
    // Create portal surface material
    this.portalMaterial = new THREE.ShaderMaterial({
      uniforms: {
        portalTexture: { value: null },
        time: { value: 0 },
        distortion: { value: 0.5 },
        edgeColor: { value: new THREE.Color(0x00ffff) },
        edgeWidth: { value: 0.05 }
      },
      vertexShader: PortalVertexShader,
      fragmentShader: PortalFragmentShader,
      transparent: true
    });
  }
  
  /**
   * Create a linked portal pair
   */
  public createPortalPair(
    positionA: THREE.Vector3,
    rotationA: THREE.Euler,
    positionB: THREE.Vector3,
    rotationB: THREE.Euler,
    size: THREE.Vector2 = new THREE.Vector2(2, 3)
  ): PortalPair {
    const id = `portal_pair_${this.portalPairs.size}`;
    
    // Create portals
    const portalA = this.createPortal(`${id}_A`, positionA, rotationA, size);
    const portalB = this.createPortal(`${id}_B`, positionB, rotationB, size);
    
    // Link them
    portalA.linkedPortal = portalB;
    portalB.linkedPortal = portalA;
    
    const pair: PortalPair = {
      id,
      portalA,
      portalB
    };
    
    this.portalPairs.set(id, pair);
    return pair;
  }
  
  /**
   * Create a single portal
   */
  private createPortal(
    id: string,
    position: THREE.Vector3,
    rotation: THREE.Euler,
    size: THREE.Vector2
  ): Portal {
    // Create render target
    const renderTarget = new THREE.WebGLRenderTarget(
      this.renderSize.x,
      this.renderSize.y,
      {
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter,
        format: THREE.RGBAFormat,
        stencilBuffer: true,
        depthBuffer: true
      }
    );
    
    // Create portal mesh
    const geometry = new THREE.PlaneGeometry(size.x, size.y);
    const material = this.portalMaterial.clone();
    material.uniforms.portalTexture.value = renderTarget.texture;
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(position);
    mesh.rotation.copy(rotation);
    
    this.scene.add(mesh);
    
    const portal: Portal = {
      id,
      mesh,
      position: position.clone(),
      rotation: new THREE.Quaternion().setFromEuler(rotation),
      size,
      linkedPortal: null,
      renderTarget,
      virtualCamera: this.portalCamera.getCamera().clone(),
      stencilRef: this.nextStencilRef++,
      isActive: true
    };
    
    this.portals.set(id, portal);
    return portal;
  }
  
  /**
   * Register a traveler
   */
  public registerTraveler(id: string, object: THREE.Object3D, velocity?: THREE.Vector3): void {
    this.travelerHandler.register(id, object, velocity);
  }
  
  public unregisterTraveler(id: string): void {
    this.travelerHandler.unregister(id);
  }
  
  /**
   * Render all portals
   */
  public render(mainCamera: THREE.Camera, renderCallback: () => void): void {
    // Update time
    this.time += 0.016;
    
    // Update travelers
    this.travelerHandler.update(Array.from(this.portals.values()));
    
    // Render each portal
    for (const portal of this.portals.values()) {
      if (!portal.isActive || !portal.linkedPortal) continue;
      
      // Update material time
      if (portal.mesh.material instanceof THREE.ShaderMaterial) {
        portal.mesh.material.uniforms.time.value = this.time;
      }
      
      // Check if portal is visible
      if (!this.isPortalVisible(portal, mainCamera)) continue;
      
      // Render portal view
      this.renderPortalView(portal, mainCamera, renderCallback, 0);
    }
    
    // Final render
    renderCallback();
  }
  
  /**
   * Render what's visible through a portal
   */
  private renderPortalView(
    portal: Portal,
    viewCamera: THREE.Camera,
    renderCallback: () => void,
    recursionLevel: number
  ): void {
    if (recursionLevel >= this.maxRecursion) return;
    if (!portal.linkedPortal) return;
    
    const destPortal = portal.linkedPortal;
    
    // Position virtual camera
    const virtualCamera = this.portalCamera.updateFromPortal(
      viewCamera,
      portal,
      destPortal
    );
    
    // Set up oblique clipping plane
    const portalNormal = new THREE.Vector3(0, 0, 1)
      .applyQuaternion(destPortal.rotation);
    const clipPlane = new THREE.Plane()
      .setFromNormalAndCoplanarPoint(portalNormal, destPortal.position);
    
    ObliqueNearPlane.setObliqueClipPlane(virtualCamera, clipPlane);
    
    // Hide portals during recursive render
    portal.mesh.visible = false;
    if (destPortal.mesh) destPortal.mesh.visible = false;
    
    // Render to portal's render target
    const currentRenderTarget = this.renderer.getRenderTarget();
    this.renderer.setRenderTarget(portal.renderTarget);
    this.renderer.clear();
    
    // Render scene from virtual camera
    this.renderer.render(this.scene, virtualCamera);
    
    // Restore
    this.renderer.setRenderTarget(currentRenderTarget);
    portal.mesh.visible = true;
    if (destPortal.mesh) destPortal.mesh.visible = true;
    
    // Recursively render portals visible through this one
    for (const otherPortal of this.portals.values()) {
      if (otherPortal.id === portal.id || otherPortal.id === destPortal.id) continue;
      if (!otherPortal.isActive || !otherPortal.linkedPortal) continue;
      
      if (this.isPortalVisible(otherPortal, virtualCamera)) {
        this.renderPortalView(otherPortal, virtualCamera, renderCallback, recursionLevel + 1);
      }
    }
  }
  
  /**
   * Check if portal is visible to camera
   */
  private isPortalVisible(portal: Portal, camera: THREE.Camera): boolean {
    // Simple frustum check
    const frustum = new THREE.Frustum();
    const matrix = new THREE.Matrix4().multiplyMatrices(
      camera.projectionMatrix,
      camera.matrixWorldInverse
    );
    frustum.setFromProjectionMatrix(matrix);
    
    // Check portal center
    return frustum.containsPoint(portal.position);
  }
  
  /**
   * Set portal active state
   */
  public setPortalActive(portalId: string, active: boolean): void {
    const portal = this.portals.get(portalId);
    if (portal) {
      portal.isActive = active;
      portal.mesh.visible = active;
    }
  }
  
  /**
   * Remove portal pair
   */
  public removePortalPair(pairId: string): void {
    const pair = this.portalPairs.get(pairId);
    if (!pair) return;
    
    // Remove meshes
    this.scene.remove(pair.portalA.mesh);
    this.scene.remove(pair.portalB.mesh);
    
    // Dispose render targets
    pair.portalA.renderTarget.dispose();
    pair.portalB.renderTarget.dispose();
    
    // Dispose geometry and materials
    pair.portalA.mesh.geometry.dispose();
    pair.portalB.mesh.geometry.dispose();
    
    if (pair.portalA.mesh.material instanceof THREE.Material) {
      pair.portalA.mesh.material.dispose();
    }
    if (pair.portalB.mesh.material instanceof THREE.Material) {
      pair.portalB.mesh.material.dispose();
    }
    
    // Remove from maps
    this.portals.delete(pair.portalA.id);
    this.portals.delete(pair.portalB.id);
    this.portalPairs.delete(pairId);
  }
  
  /**
   * Get all portal pairs
   */
  public getPortalPairs(): PortalPair[] {
    return Array.from(this.portalPairs.values());
  }
  
  /**
   * Resize render targets
   */
  public resize(width: number, height: number): void {
    this.renderSize.set(width, height);
    
    for (const portal of this.portals.values()) {
      portal.renderTarget.setSize(width, height);
    }
    
    const camera = this.portalCamera.getCamera();
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    for (const pairId of this.portalPairs.keys()) {
      this.removePortalPair(pairId);
    }
    
    this.stencilMaterial.dispose();
    this.portalMaterial.dispose();
  }
}

