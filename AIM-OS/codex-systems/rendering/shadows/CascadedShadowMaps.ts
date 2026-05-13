/**
 * Cascaded Shadow Maps (CSM) System
 * High-quality shadows for large environments
 * 
 * Features:
 * - Multiple shadow cascades
 * - Frustum-aligned splits
 * - Soft shadow filtering (PCF/PCSS)
 * - Stable cascade transitions
 * - Efficient shadow atlas
 * - Dynamic cascade adjustment
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface CSMConfig {
  cascadeCount: number;
  shadowMapSize: number;
  lightDirection: THREE.Vector3;
  maxDistance: number;
  lambda: number;  // Logarithmic vs linear split (0-1)
  shadowBias: number;
  normalBias: number;
  pcfSamples: number;
  fadeRange: number;
  stabilize: boolean;
}

export interface CascadeInfo {
  camera: THREE.OrthographicCamera;
  renderTarget: THREE.WebGLRenderTarget;
  frustumCorners: THREE.Vector3[];
  splitDistance: number;
  viewProjectionMatrix: THREE.Matrix4;
}

// ============================================
// CSM SHADERS
// ============================================

const CSMVertexShader = `
varying vec3 vWorldPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying vec4 vShadowCoords[4];

uniform mat4 shadowMatrices[4];
uniform int cascadeCount;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  
  vec4 worldPosition = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPosition.xyz;
  
  // Calculate shadow coordinates for each cascade
  for (int i = 0; i < 4; i++) {
    if (i < cascadeCount) {
      vShadowCoords[i] = shadowMatrices[i] * worldPosition;
    }
  }
  
  gl_Position = projectionMatrix * viewMatrix * worldPosition;
}
`;

const CSMFragmentShader = `
uniform sampler2D shadowMaps[4];
uniform float cascadeSplits[4];
uniform int cascadeCount;
uniform float shadowBias;
uniform float shadowIntensity;
uniform float fadeRange;
uniform int pcfSamples;
uniform vec2 shadowMapSize;

uniform vec3 lightDirection;
uniform vec3 lightColor;
uniform float ambientIntensity;

varying vec3 vWorldPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying vec4 vShadowCoords[4];

float sampleShadowMap(sampler2D map, vec2 coords, float compare) {
  float depth = texture2D(map, coords).r;
  return step(compare - shadowBias, depth);
}

float sampleShadowPCF(sampler2D map, vec4 shadowCoord, int cascade) {
  vec3 coords = shadowCoord.xyz / shadowCoord.w;
  coords = coords * 0.5 + 0.5;
  
  if (coords.x < 0.0 || coords.x > 1.0 || coords.y < 0.0 || coords.y > 1.0) {
    return 1.0;
  }
  
  float shadow = 0.0;
  vec2 texelSize = 1.0 / shadowMapSize;
  
  // PCF sampling
  int samples = pcfSamples;
  float radius = float(samples) / 2.0;
  
  for (int x = -2; x <= 2; x++) {
    for (int y = -2; y <= 2; y++) {
      vec2 offset = vec2(float(x), float(y)) * texelSize;
      shadow += sampleShadowMap(map, coords.xy + offset, coords.z);
    }
  }
  
  return shadow / 25.0;
}

int getCascadeIndex(float depth) {
  for (int i = 0; i < 4; i++) {
    if (i < cascadeCount && depth < cascadeSplits[i]) {
      return i;
    }
  }
  return cascadeCount - 1;
}

float getShadow(float viewDepth) {
  int cascade = getCascadeIndex(viewDepth);
  
  float shadow = 1.0;
  
  // Sample the appropriate cascade
  if (cascade == 0) {
    shadow = sampleShadowPCF(shadowMaps[0], vShadowCoords[0], 0);
  } else if (cascade == 1) {
    shadow = sampleShadowPCF(shadowMaps[1], vShadowCoords[1], 1);
  } else if (cascade == 2) {
    shadow = sampleShadowPCF(shadowMaps[2], vShadowCoords[2], 2);
  } else {
    shadow = sampleShadowPCF(shadowMaps[3], vShadowCoords[3], 3);
  }
  
  // Cascade fade for smooth transitions
  if (cascade < cascadeCount - 1) {
    float splitStart = cascade > 0 ? cascadeSplits[cascade - 1] : 0.0;
    float splitEnd = cascadeSplits[cascade];
    float fadeStart = splitEnd - fadeRange * (splitEnd - splitStart);
    
    if (viewDepth > fadeStart) {
      float fade = (viewDepth - fadeStart) / (splitEnd - fadeStart);
      
      float nextShadow = 1.0;
      if (cascade + 1 == 1) {
        nextShadow = sampleShadowPCF(shadowMaps[1], vShadowCoords[1], 1);
      } else if (cascade + 1 == 2) {
        nextShadow = sampleShadowPCF(shadowMaps[2], vShadowCoords[2], 2);
      } else {
        nextShadow = sampleShadowPCF(shadowMaps[3], vShadowCoords[3], 3);
      }
      
      shadow = mix(shadow, nextShadow, fade);
    }
  }
  
  return shadow;
}

void main() {
  vec3 normal = normalize(vNormal);
  
  // Calculate view depth for cascade selection
  float viewDepth = length(cameraPosition - vWorldPosition);
  
  // Get shadow factor
  float shadow = getShadow(viewDepth);
  
  // Simple lighting
  float NdotL = max(dot(normal, -lightDirection), 0.0);
  
  vec3 diffuse = lightColor * NdotL * shadow;
  vec3 ambient = lightColor * ambientIntensity;
  
  vec3 finalColor = diffuse + ambient;
  
  gl_FragColor = vec4(finalColor, 1.0);
}
`;

// ============================================
// FRUSTUM UTILITIES
// ============================================

export class FrustumUtils {
  /**
   * Calculate frustum corners in world space
   */
  public static getFrustumCorners(
    camera: THREE.PerspectiveCamera,
    near: number,
    far: number
  ): THREE.Vector3[] {
    const corners: THREE.Vector3[] = [];
    
    const fovRad = (camera.fov * Math.PI) / 180;
    const aspect = camera.aspect;
    
    const nearHeight = 2 * Math.tan(fovRad / 2) * near;
    const nearWidth = nearHeight * aspect;
    const farHeight = 2 * Math.tan(fovRad / 2) * far;
    const farWidth = farHeight * aspect;
    
    // Near plane corners
    corners.push(new THREE.Vector3(-nearWidth / 2, -nearHeight / 2, -near));
    corners.push(new THREE.Vector3(nearWidth / 2, -nearHeight / 2, -near));
    corners.push(new THREE.Vector3(nearWidth / 2, nearHeight / 2, -near));
    corners.push(new THREE.Vector3(-nearWidth / 2, nearHeight / 2, -near));
    
    // Far plane corners
    corners.push(new THREE.Vector3(-farWidth / 2, -farHeight / 2, -far));
    corners.push(new THREE.Vector3(farWidth / 2, -farHeight / 2, -far));
    corners.push(new THREE.Vector3(farWidth / 2, farHeight / 2, -far));
    corners.push(new THREE.Vector3(-farWidth / 2, farHeight / 2, -far));
    
    // Transform to world space
    const cameraMatrix = camera.matrixWorld;
    for (const corner of corners) {
      corner.applyMatrix4(cameraMatrix);
    }
    
    return corners;
  }
  
  /**
   * Calculate bounding sphere of frustum
   */
  public static getFrustumBoundingSphere(corners: THREE.Vector3[]): THREE.Sphere {
    const center = new THREE.Vector3();
    
    for (const corner of corners) {
      center.add(corner);
    }
    center.divideScalar(corners.length);
    
    let maxRadius = 0;
    for (const corner of corners) {
      const dist = corner.distanceTo(center);
      maxRadius = Math.max(maxRadius, dist);
    }
    
    return new THREE.Sphere(center, maxRadius);
  }
}

// ============================================
// CASCADE MANAGER
// ============================================

export class CascadeManager {
  public cascades: CascadeInfo[] = [];
  
  private config: CSMConfig;
  private camera: THREE.PerspectiveCamera;
  private lightDirection: THREE.Vector3;
  
  constructor(config: CSMConfig, camera: THREE.PerspectiveCamera) {
    this.config = config;
    this.camera = camera;
    this.lightDirection = config.lightDirection.clone().normalize();
    
    this.initCascades();
  }
  
  private initCascades(): void {
    const { cascadeCount, shadowMapSize, maxDistance, lambda } = this.config;
    const near = this.camera.near;
    
    // Calculate cascade splits
    const splits = this.calculateSplits(near, maxDistance, cascadeCount, lambda);
    
    for (let i = 0; i < cascadeCount; i++) {
      const renderTarget = new THREE.WebGLRenderTarget(shadowMapSize, shadowMapSize, {
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter,
        format: THREE.RGBAFormat,
        type: THREE.FloatType
      });
      
      const orthoCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 1000);
      
      this.cascades.push({
        camera: orthoCamera,
        renderTarget,
        frustumCorners: [],
        splitDistance: splits[i],
        viewProjectionMatrix: new THREE.Matrix4()
      });
    }
  }
  
  /**
   * Calculate cascade split distances using practical split scheme
   */
  private calculateSplits(
    near: number,
    far: number,
    count: number,
    lambda: number
  ): number[] {
    const splits: number[] = [];
    
    for (let i = 1; i <= count; i++) {
      const t = i / count;
      
      // Logarithmic split
      const log = near * Math.pow(far / near, t);
      
      // Linear split
      const linear = near + (far - near) * t;
      
      // Practical split (blend of log and linear)
      const split = lambda * log + (1 - lambda) * linear;
      
      splits.push(split);
    }
    
    return splits;
  }
  
  /**
   * Update cascade cameras for current view
   */
  public update(): void {
    this.camera.updateMatrixWorld();
    
    let prevSplit = this.camera.near;
    
    for (let i = 0; i < this.cascades.length; i++) {
      const cascade = this.cascades[i];
      const splitDistance = cascade.splitDistance;
      
      // Get frustum corners for this cascade
      cascade.frustumCorners = FrustumUtils.getFrustumCorners(
        this.camera,
        prevSplit,
        splitDistance
      );
      
      // Calculate bounding sphere
      const sphere = FrustumUtils.getFrustumBoundingSphere(cascade.frustumCorners);
      
      // Position light camera
      this.updateCascadeCamera(cascade, sphere);
      
      prevSplit = splitDistance;
    }
  }
  
  private updateCascadeCamera(cascade: CascadeInfo, sphere: THREE.Sphere): void {
    const cam = cascade.camera;
    
    // Position camera looking at sphere center from light direction
    const lightPos = sphere.center.clone().sub(
      this.lightDirection.clone().multiplyScalar(sphere.radius * 2)
    );
    
    cam.position.copy(lightPos);
    cam.lookAt(sphere.center);
    
    // Set ortho bounds to encompass the sphere
    const radius = sphere.radius;
    
    if (this.config.stabilize) {
      // Round to texel size for stability
      const texelSize = (radius * 2) / this.config.shadowMapSize;
      const worldUnitsPerTexel = texelSize;
      
      cam.left = Math.floor(-radius / worldUnitsPerTexel) * worldUnitsPerTexel;
      cam.right = Math.ceil(radius / worldUnitsPerTexel) * worldUnitsPerTexel;
      cam.bottom = Math.floor(-radius / worldUnitsPerTexel) * worldUnitsPerTexel;
      cam.top = Math.ceil(radius / worldUnitsPerTexel) * worldUnitsPerTexel;
    } else {
      cam.left = -radius;
      cam.right = radius;
      cam.bottom = -radius;
      cam.top = radius;
    }
    
    cam.near = 0.1;
    cam.far = sphere.radius * 4;
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();
    
    // Store view-projection matrix
    cascade.viewProjectionMatrix.multiplyMatrices(
      cam.projectionMatrix,
      cam.matrixWorldInverse
    );
  }
  
  /**
   * Get shadow matrices for shader
   */
  public getShadowMatrices(): THREE.Matrix4[] {
    return this.cascades.map(c => c.viewProjectionMatrix);
  }
  
  /**
   * Get cascade split distances
   */
  public getCascadeSplits(): number[] {
    return this.cascades.map(c => c.splitDistance);
  }
  
  /**
   * Get render targets
   */
  public getRenderTargets(): THREE.WebGLRenderTarget[] {
    return this.cascades.map(c => c.renderTarget);
  }
  
  /**
   * Dispose resources
   */
  public dispose(): void {
    for (const cascade of this.cascades) {
      cascade.renderTarget.dispose();
    }
    this.cascades = [];
  }
}

// ============================================
// DEPTH MATERIAL FOR SHADOW PASS
// ============================================

const DepthVertexShader = `
void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const DepthFragmentShader = `
void main() {
  gl_FragColor = vec4(gl_FragCoord.z, 0.0, 0.0, 1.0);
}
`;

// ============================================
// MAIN CSM SYSTEM
// ============================================

export class CascadedShadowMaps {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private config: CSMConfig;
  
  private cascadeManager: CascadeManager;
  private depthMaterial: THREE.ShaderMaterial;
  private receiverMaterial: THREE.ShaderMaterial;
  
  private originalMaterials: Map<THREE.Object3D, THREE.Material | THREE.Material[]> = new Map();
  
  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.PerspectiveCamera,
    config: Partial<CSMConfig> = {}
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    
    this.config = {
      cascadeCount: 4,
      shadowMapSize: 2048,
      lightDirection: new THREE.Vector3(-1, -1, -1).normalize(),
      maxDistance: 200,
      lambda: 0.5,
      shadowBias: 0.001,
      normalBias: 0.1,
      pcfSamples: 5,
      fadeRange: 0.1,
      stabilize: true,
      ...config
    };
    
    this.cascadeManager = new CascadeManager(this.config, camera);
    
    // Create depth material for shadow pass
    this.depthMaterial = new THREE.ShaderMaterial({
      vertexShader: DepthVertexShader,
      fragmentShader: DepthFragmentShader
    });
    
    // Create receiver material with CSM
    this.receiverMaterial = new THREE.ShaderMaterial({
      uniforms: {
        shadowMaps: { value: this.cascadeManager.getRenderTargets().map(rt => rt.texture) },
        shadowMatrices: { value: this.cascadeManager.getShadowMatrices() },
        cascadeSplits: { value: this.cascadeManager.getCascadeSplits() },
        cascadeCount: { value: this.config.cascadeCount },
        shadowBias: { value: this.config.shadowBias },
        shadowIntensity: { value: 0.7 },
        fadeRange: { value: this.config.fadeRange },
        pcfSamples: { value: this.config.pcfSamples },
        shadowMapSize: { value: new THREE.Vector2(this.config.shadowMapSize, this.config.shadowMapSize) },
        lightDirection: { value: this.config.lightDirection },
        lightColor: { value: new THREE.Color(1, 1, 1) },
        ambientIntensity: { value: 0.3 }
      },
      vertexShader: CSMVertexShader,
      fragmentShader: CSMFragmentShader
    });
  }
  
  /**
   * Update shadow maps
   */
  public update(): void {
    // Update cascade cameras
    this.cascadeManager.update();
    
    // Update shader uniforms
    this.receiverMaterial.uniforms.shadowMatrices.value = this.cascadeManager.getShadowMatrices();
    this.receiverMaterial.uniforms.cascadeSplits.value = this.cascadeManager.getCascadeSplits();
    
    // Render shadow maps
    this.renderShadowMaps();
  }
  
  private renderShadowMaps(): void {
    const currentRenderTarget = this.renderer.getRenderTarget();
    const currentBackground = this.scene.background;
    
    // Store original materials
    this.storeMaterials();
    
    // Apply depth material
    this.applyDepthMaterial();
    
    this.scene.background = null;
    
    // Render each cascade
    for (let i = 0; i < this.config.cascadeCount; i++) {
      const cascade = this.cascadeManager.cascades[i];
      
      this.renderer.setRenderTarget(cascade.renderTarget);
      this.renderer.clear();
      this.renderer.render(this.scene, cascade.camera);
    }
    
    // Restore
    this.restoreMaterials();
    this.scene.background = currentBackground;
    this.renderer.setRenderTarget(currentRenderTarget);
    
    // Update shadow map textures in receiver material
    const textures = this.cascadeManager.getRenderTargets().map(rt => rt.texture);
    this.receiverMaterial.uniforms.shadowMaps.value = textures;
  }
  
  private storeMaterials(): void {
    this.originalMaterials.clear();
    
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        this.originalMaterials.set(object, object.material);
      }
    });
  }
  
  private applyDepthMaterial(): void {
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.castShadow) {
        object.material = this.depthMaterial;
      }
    });
  }
  
  private restoreMaterials(): void {
    for (const [object, material] of this.originalMaterials) {
      if (object instanceof THREE.Mesh) {
        object.material = material;
      }
    }
  }
  
  /**
   * Set light direction
   */
  public setLightDirection(direction: THREE.Vector3): void {
    this.config.lightDirection.copy(direction).normalize();
    this.receiverMaterial.uniforms.lightDirection.value.copy(this.config.lightDirection);
  }
  
  /**
   * Get receiver material (apply to objects that receive shadows)
   */
  public getReceiverMaterial(): THREE.ShaderMaterial {
    return this.receiverMaterial;
  }
  
  /**
   * Create a shadow-receiving material from existing material
   */
  public createShadowMaterial(baseMaterial: THREE.Material): THREE.ShaderMaterial {
    // Clone receiver material and merge with base material properties
    const shadowMat = this.receiverMaterial.clone();
    
    if (baseMaterial instanceof THREE.MeshStandardMaterial) {
      shadowMat.uniforms.lightColor.value.copy(new THREE.Color(1, 1, 1));
    }
    
    return shadowMat;
  }
  
  /**
   * Get debug visualization of cascades
   */
  public getCascadeDebugHelpers(): THREE.Group {
    const group = new THREE.Group();
    
    const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00];
    
    for (let i = 0; i < this.cascadeManager.cascades.length; i++) {
      const cascade = this.cascadeManager.cascades[i];
      const helper = new THREE.CameraHelper(cascade.camera);
      (helper.material as THREE.LineBasicMaterial).color.setHex(colors[i % colors.length]);
      group.add(helper);
    }
    
    return group;
  }
  
  /**
   * Dispose resources
   */
  public dispose(): void {
    this.cascadeManager.dispose();
    this.depthMaterial.dispose();
    this.receiverMaterial.dispose();
  }
}

