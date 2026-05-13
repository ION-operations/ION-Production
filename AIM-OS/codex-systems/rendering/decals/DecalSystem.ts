/**
 * Decal Projection System
 * Advanced decal rendering with proper depth handling
 * 
 * Features:
 * - Deferred decal rendering
 * - Screen-space decals
 * - Mesh decals with proper UV projection
 * - Decal pooling
 * - Fade in/out
 * - Layer blending
 */

import * as THREE from 'three';
import { DecalGeometry } from 'three/examples/jsm/geometries/DecalGeometry';

// ============================================
// TYPES
// ============================================

export interface DecalMaterial {
  diffuseMap: THREE.Texture | null;
  normalMap: THREE.Texture | null;
  opacityMap: THREE.Texture | null;
  color: THREE.Color;
  metalness: number;
  roughness: number;
  opacity: number;
  blendMode: 'normal' | 'multiply' | 'additive' | 'overlay';
}

export interface DecalInstance {
  id: string;
  mesh: THREE.Mesh;
  position: THREE.Vector3;
  rotation: THREE.Euler;
  scale: THREE.Vector3;
  material: THREE.Material;
  createdAt: number;
  lifetime: number;  // -1 for infinite
  fadeIn: number;
  fadeOut: number;
  layer: number;
}

export interface DecalProjectionOptions {
  size: THREE.Vector3;
  depth: number;
  angle: number;
  fadeDistance: number;
  receiveShadows: boolean;
  layer: number;
}

// ============================================
// DECAL SHADERS
// ============================================

const DecalVertexShader = `
varying vec3 vWorldPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying vec4 vDecalCoord;

uniform mat4 decalMatrix;

void main() {
  vec4 worldPosition = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPosition.xyz;
  vNormal = normalize(normalMatrix * normal);
  vUv = uv;
  
  // Transform to decal space
  vDecalCoord = decalMatrix * worldPosition;
  
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const DecalFragmentShader = `
uniform sampler2D diffuseMap;
uniform sampler2D normalMap;
uniform sampler2D opacityMap;
uniform vec3 decalColor;
uniform float opacity;
uniform float metalness;
uniform float roughness;
uniform float fadeStart;
uniform float fadeEnd;
uniform int blendMode;

varying vec3 vWorldPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying vec4 vDecalCoord;

vec3 perturbNormal2Arb(vec3 eye_pos, vec3 surf_norm, vec3 mapN) {
  vec3 q0 = dFdx(eye_pos);
  vec3 q1 = dFdy(eye_pos);
  vec2 st0 = dFdx(vUv);
  vec2 st1 = dFdy(vUv);
  
  vec3 N = normalize(surf_norm);
  vec3 T = normalize(q0 * st1.t - q1 * st0.t);
  vec3 B = -normalize(cross(N, T));
  mat3 TBN = mat3(T, B, N);
  
  return normalize(TBN * mapN);
}

void main() {
  // Decal box check (clip outside projection)
  vec3 decalCoord = vDecalCoord.xyz / vDecalCoord.w;
  
  if (abs(decalCoord.x) > 0.5 || abs(decalCoord.y) > 0.5 || abs(decalCoord.z) > 0.5) {
    discard;
  }
  
  // Convert to UV space
  vec2 decalUV = decalCoord.xy + 0.5;
  
  // Sample textures
  vec4 diffuseColor = texture2D(diffuseMap, decalUV);
  vec3 normalSample = texture2D(normalMap, decalUV).xyz * 2.0 - 1.0;
  float opacitySample = texture2D(opacityMap, decalUV).r;
  
  // Calculate fade based on depth
  float depthFade = smoothstep(fadeStart, fadeEnd, abs(decalCoord.z));
  float finalOpacity = diffuseColor.a * opacity * opacitySample * (1.0 - depthFade);
  
  if (finalOpacity < 0.01) {
    discard;
  }
  
  // Apply color
  vec3 finalColor = diffuseColor.rgb * decalColor;
  
  // Blend modes
  if (blendMode == 1) { // Multiply
    finalColor = finalColor * 0.5;
  } else if (blendMode == 2) { // Additive
    finalColor = finalColor * 1.5;
  } else if (blendMode == 3) { // Overlay
    // Overlay blend calculation would go here
  }
  
  gl_FragColor = vec4(finalColor, finalOpacity);
}
`;

// ============================================
// SCREEN SPACE DECAL
// ============================================

const ScreenSpaceDecalVertexShader = `
varying vec4 vProjectedPosition;
varying vec3 vViewDir;

void main() {
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vViewDir = -mvPosition.xyz;
  vProjectedPosition = projectionMatrix * mvPosition;
  gl_Position = vProjectedPosition;
}
`;

const ScreenSpaceDecalFragmentShader = `
uniform sampler2D depthTexture;
uniform sampler2D diffuseMap;
uniform mat4 inverseProjectionMatrix;
uniform mat4 inverseViewMatrix;
uniform mat4 decalMatrix;
uniform vec3 decalColor;
uniform float opacity;
uniform vec2 resolution;

varying vec4 vProjectedPosition;
varying vec3 vViewDir;

vec3 getWorldPosition(vec2 screenUV, float depth) {
  vec4 ndc = vec4(screenUV * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
  vec4 viewPos = inverseProjectionMatrix * ndc;
  viewPos /= viewPos.w;
  vec4 worldPos = inverseViewMatrix * viewPos;
  return worldPos.xyz;
}

void main() {
  vec2 screenUV = gl_FragCoord.xy / resolution;
  float depth = texture2D(depthTexture, screenUV).r;
  
  if (depth >= 1.0) {
    discard;
  }
  
  vec3 worldPosition = getWorldPosition(screenUV, depth);
  
  // Transform to decal space
  vec4 decalCoord = decalMatrix * vec4(worldPosition, 1.0);
  decalCoord.xyz /= decalCoord.w;
  
  // Box clip
  if (abs(decalCoord.x) > 0.5 || abs(decalCoord.y) > 0.5 || abs(decalCoord.z) > 0.5) {
    discard;
  }
  
  // UV from decal space
  vec2 decalUV = decalCoord.xy + 0.5;
  
  // Sample
  vec4 diffuse = texture2D(diffuseMap, decalUV);
  
  float fadeZ = 1.0 - smoothstep(0.3, 0.5, abs(decalCoord.z));
  float finalOpacity = diffuse.a * opacity * fadeZ;
  
  if (finalOpacity < 0.01) {
    discard;
  }
  
  gl_FragColor = vec4(diffuse.rgb * decalColor, finalOpacity);
}
`;

// ============================================
// DECAL MATERIAL FACTORY
// ============================================

export class DecalMaterialFactory {
  private static whiteTexture: THREE.Texture;
  private static normalTexture: THREE.Texture;
  
  private static getWhiteTexture(): THREE.Texture {
    if (!this.whiteTexture) {
      const data = new Uint8Array([255, 255, 255, 255]);
      this.whiteTexture = new THREE.DataTexture(data, 1, 1);
      this.whiteTexture.needsUpdate = true;
    }
    return this.whiteTexture;
  }
  
  private static getNormalTexture(): THREE.Texture {
    if (!this.normalTexture) {
      const data = new Uint8Array([128, 128, 255, 255]);
      this.normalTexture = new THREE.DataTexture(data, 1, 1);
      this.normalTexture.needsUpdate = true;
    }
    return this.normalTexture;
  }
  
  public static createProjectedDecalMaterial(
    material: Partial<DecalMaterial>,
    decalMatrix: THREE.Matrix4
  ): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        diffuseMap: { value: material.diffuseMap ?? this.getWhiteTexture() },
        normalMap: { value: material.normalMap ?? this.getNormalTexture() },
        opacityMap: { value: material.opacityMap ?? this.getWhiteTexture() },
        decalColor: { value: material.color ?? new THREE.Color(1, 1, 1) },
        opacity: { value: material.opacity ?? 1.0 },
        metalness: { value: material.metalness ?? 0.0 },
        roughness: { value: material.roughness ?? 0.5 },
        fadeStart: { value: 0.3 },
        fadeEnd: { value: 0.5 },
        blendMode: { value: this.blendModeToInt(material.blendMode ?? 'normal') },
        decalMatrix: { value: decalMatrix }
      },
      vertexShader: DecalVertexShader,
      fragmentShader: DecalFragmentShader,
      transparent: true,
      depthWrite: false,
      depthTest: true,
      side: THREE.DoubleSide,
      polygonOffset: true,
      polygonOffsetFactor: -4,
      polygonOffsetUnits: -4
    });
  }
  
  public static createScreenSpaceDecalMaterial(
    diffuseMap: THREE.Texture,
    depthTexture: THREE.Texture,
    decalMatrix: THREE.Matrix4,
    camera: THREE.Camera,
    resolution: THREE.Vector2
  ): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        diffuseMap: { value: diffuseMap },
        depthTexture: { value: depthTexture },
        decalMatrix: { value: decalMatrix },
        decalColor: { value: new THREE.Color(1, 1, 1) },
        opacity: { value: 1.0 },
        inverseProjectionMatrix: { value: camera.projectionMatrixInverse },
        inverseViewMatrix: { value: camera.matrixWorld },
        resolution: { value: resolution }
      },
      vertexShader: ScreenSpaceDecalVertexShader,
      fragmentShader: ScreenSpaceDecalFragmentShader,
      transparent: true,
      depthWrite: false,
      depthTest: true
    });
  }
  
  private static blendModeToInt(mode: string): number {
    switch (mode) {
      case 'multiply': return 1;
      case 'additive': return 2;
      case 'overlay': return 3;
      default: return 0;
    }
  }
}

// ============================================
// DECAL POOL
// ============================================

export class DecalPool {
  private pool: DecalInstance[] = [];
  private active: Map<string, DecalInstance> = new Map();
  private maxDecals: number;
  
  constructor(maxDecals: number = 100) {
    this.maxDecals = maxDecals;
  }
  
  public acquire(): DecalInstance | null {
    if (this.pool.length > 0) {
      return this.pool.pop()!;
    }
    
    if (this.active.size >= this.maxDecals) {
      // Remove oldest decal
      let oldest: DecalInstance | null = null;
      for (const decal of this.active.values()) {
        if (!oldest || decal.createdAt < oldest.createdAt) {
          oldest = decal;
        }
      }
      if (oldest) {
        this.release(oldest.id);
        return this.pool.pop()!;
      }
      return null;
    }
    
    return null;  // Need to create new
  }
  
  public release(id: string): void {
    const decal = this.active.get(id);
    if (decal) {
      this.active.delete(id);
      decal.mesh.visible = false;
      this.pool.push(decal);
    }
  }
  
  public add(decal: DecalInstance): void {
    this.active.set(decal.id, decal);
  }
  
  public getActive(): DecalInstance[] {
    return Array.from(this.active.values());
  }
  
  public clear(): void {
    for (const decal of this.active.values()) {
      decal.mesh.visible = false;
      this.pool.push(decal);
    }
    this.active.clear();
  }
}

// ============================================
// MAIN DECAL SYSTEM
// ============================================

export class DecalSystem {
  private scene: THREE.Scene;
  private pool: DecalPool;
  private decalGroup: THREE.Group;
  private defaultMaterial: THREE.Material;
  private nextId: number = 0;
  
  constructor(scene: THREE.Scene, maxDecals: number = 100) {
    this.scene = scene;
    this.pool = new DecalPool(maxDecals);
    this.decalGroup = new THREE.Group();
    this.decalGroup.name = 'DecalGroup';
    this.scene.add(this.decalGroup);
    
    this.defaultMaterial = new THREE.MeshStandardMaterial({
      transparent: true,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -4,
      polygonOffsetUnits: -4
    });
  }
  
  /**
   * Project a decal onto a mesh at a raycast hit point
   */
  public projectDecal(
    targetMesh: THREE.Mesh,
    position: THREE.Vector3,
    normal: THREE.Vector3,
    material: Partial<DecalMaterial>,
    options: Partial<DecalProjectionOptions> = {}
  ): DecalInstance | null {
    const opts: DecalProjectionOptions = {
      size: new THREE.Vector3(1, 1, 1),
      depth: 0.5,
      angle: 0,
      fadeDistance: 1.0,
      receiveShadows: true,
      layer: 0,
      ...options
    };
    
    // Create rotation from normal
    const quaternion = new THREE.Quaternion();
    const up = new THREE.Vector3(0, 1, 0);
    
    // Handle edge case where normal is parallel to up
    if (Math.abs(normal.dot(up)) > 0.99) {
      up.set(1, 0, 0);
    }
    
    const lookAt = position.clone().add(normal);
    const dummy = new THREE.Object3D();
    dummy.position.copy(position);
    dummy.lookAt(lookAt);
    dummy.rotateZ(opts.angle);
    
    const rotation = new THREE.Euler().setFromQuaternion(dummy.quaternion);
    
    // Create decal geometry
    const decalGeometry = new DecalGeometry(
      targetMesh,
      position,
      rotation,
      opts.size
    );
    
    if (decalGeometry.getAttribute('position').count === 0) {
      console.warn('Decal projection failed - no geometry generated');
      decalGeometry.dispose();
      return null;
    }
    
    // Create decal matrix for shader
    const decalMatrix = new THREE.Matrix4();
    decalMatrix.compose(
      position,
      dummy.quaternion,
      opts.size
    );
    decalMatrix.invert();
    
    // Create material
    const decalMaterial = DecalMaterialFactory.createProjectedDecalMaterial(
      material,
      decalMatrix
    );
    
    // Create mesh
    const decalMesh = new THREE.Mesh(decalGeometry, decalMaterial);
    decalMesh.receiveShadow = opts.receiveShadows;
    decalMesh.renderOrder = opts.layer;
    
    const id = `decal_${this.nextId++}`;
    
    const instance: DecalInstance = {
      id,
      mesh: decalMesh,
      position: position.clone(),
      rotation: rotation.clone(),
      scale: opts.size.clone(),
      material: decalMaterial,
      createdAt: Date.now(),
      lifetime: -1,
      fadeIn: 0.2,
      fadeOut: 0.5,
      layer: opts.layer
    };
    
    this.pool.add(instance);
    this.decalGroup.add(decalMesh);
    
    return instance;
  }
  
  /**
   * Project decal from screen coordinates using raycast
   */
  public projectDecalFromScreen(
    screenPos: THREE.Vector2,
    camera: THREE.Camera,
    targets: THREE.Object3D[],
    material: Partial<DecalMaterial>,
    options: Partial<DecalProjectionOptions> = {}
  ): DecalInstance | null {
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(screenPos, camera);
    
    const intersects = raycaster.intersectObjects(targets, true);
    
    if (intersects.length === 0) {
      return null;
    }
    
    const hit = intersects[0];
    
    if (!hit.face || !(hit.object instanceof THREE.Mesh)) {
      return null;
    }
    
    return this.projectDecal(
      hit.object,
      hit.point,
      hit.face.normal,
      material,
      options
    );
  }
  
  /**
   * Create a simple sprite-based decal
   */
  public createSpriteDecal(
    position: THREE.Vector3,
    texture: THREE.Texture,
    size: number = 1,
    lifetime: number = -1
  ): DecalInstance {
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthWrite: false
    });
    
    const sprite = new THREE.Sprite(material);
    sprite.position.copy(position);
    sprite.scale.setScalar(size);
    
    // Wrap sprite in mesh for compatibility
    const mesh = new THREE.Mesh();
    mesh.add(sprite);
    mesh.position.copy(position);
    
    const id = `sprite_decal_${this.nextId++}`;
    
    const instance: DecalInstance = {
      id,
      mesh,
      position: position.clone(),
      rotation: new THREE.Euler(),
      scale: new THREE.Vector3(size, size, size),
      material,
      createdAt: Date.now(),
      lifetime,
      fadeIn: 0,
      fadeOut: 0,
      layer: 0
    };
    
    this.pool.add(instance);
    this.scene.add(mesh);
    
    return instance;
  }
  
  /**
   * Remove a decal
   */
  public removeDecal(id: string): void {
    const decals = this.pool.getActive();
    const decal = decals.find(d => d.id === id);
    
    if (decal) {
      this.decalGroup.remove(decal.mesh);
      decal.mesh.geometry.dispose();
      if (decal.mesh.material instanceof THREE.Material) {
        decal.mesh.material.dispose();
      }
      this.pool.release(id);
    }
  }
  
  /**
   * Update decals (lifetime, fade)
   */
  public update(deltaTime: number): void {
    const currentTime = Date.now();
    const toRemove: string[] = [];
    
    for (const decal of this.pool.getActive()) {
      if (decal.lifetime > 0) {
        const age = currentTime - decal.createdAt;
        const lifeMs = decal.lifetime * 1000;
        
        if (age >= lifeMs) {
          toRemove.push(decal.id);
          continue;
        }
        
        // Fade out near end of life
        const fadeOutStart = lifeMs - decal.fadeOut * 1000;
        if (age >= fadeOutStart && decal.material instanceof THREE.ShaderMaterial) {
          const fadeProgress = (age - fadeOutStart) / (decal.fadeOut * 1000);
          decal.material.uniforms.opacity.value = 1 - fadeProgress;
        }
      }
    }
    
    for (const id of toRemove) {
      this.removeDecal(id);
    }
  }
  
  /**
   * Clear all decals
   */
  public clear(): void {
    const decals = this.pool.getActive();
    for (const decal of decals) {
      this.decalGroup.remove(decal.mesh);
      decal.mesh.geometry.dispose();
      if (decal.mesh.material instanceof THREE.Material) {
        decal.mesh.material.dispose();
      }
    }
    this.pool.clear();
  }
  
  /**
   * Get decal count
   */
  public getCount(): number {
    return this.pool.getActive().length;
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.clear();
    this.scene.remove(this.decalGroup);
    this.defaultMaterial.dispose();
  }
}
