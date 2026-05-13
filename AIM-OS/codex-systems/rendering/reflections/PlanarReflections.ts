/**
 * Planar Reflections System
 * High-quality real-time reflections for flat surfaces
 * 
 * Features:
 * - Mirror-accurate reflections
 * - Multiple reflection planes
 * - Fresnel effect
 * - Blur/roughness support
 * - Clip plane optimization
 * - LOD for reflected objects
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface ReflectionPlaneConfig {
  id: string;
  position: THREE.Vector3;
  normal: THREE.Vector3;
  width: number;
  height: number;
  textureWidth: number;
  textureHeight: number;
  clipBias: number;
  roughness: number;
  fresnel: boolean;
  fresnelPower: number;
}

export interface ReflectorData {
  config: ReflectionPlaneConfig;
  camera: THREE.PerspectiveCamera;
  renderTarget: THREE.WebGLRenderTarget;
  reflectorPlane: THREE.Plane;
  mesh: THREE.Mesh;
  clipPlane: THREE.Vector4;
}

// ============================================
// REFLECTION MATERIAL
// ============================================

const reflectionVertexShader = `
  uniform mat4 textureMatrix;
  varying vec4 vUvReflection;
  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  
  void main() {
    vUvReflection = textureMatrix * vec4(position, 1.0);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const reflectionFragmentShader = `
  uniform sampler2D tReflection;
  uniform vec3 color;
  uniform float roughness;
  uniform bool useFresnel;
  uniform float fresnelPower;
  uniform float opacity;
  
  varying vec4 vUvReflection;
  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  
  void main() {
    vec4 reflectionColor = textureProj(tReflection, vUvReflection);
    
    // Apply roughness blur (simplified - real impl would use mipmap)
    if (roughness > 0.0) {
      vec2 offset = vec2(roughness * 0.01);
      reflectionColor += textureProj(tReflection, vUvReflection + vec4(offset.x, 0.0, 0.0, 0.0));
      reflectionColor += textureProj(tReflection, vUvReflection + vec4(-offset.x, 0.0, 0.0, 0.0));
      reflectionColor += textureProj(tReflection, vUvReflection + vec4(0.0, offset.y, 0.0, 0.0));
      reflectionColor += textureProj(tReflection, vUvReflection + vec4(0.0, -offset.y, 0.0, 0.0));
      reflectionColor /= 5.0;
    }
    
    // Fresnel effect
    float fresnel = 1.0;
    if (useFresnel) {
      vec3 viewDir = normalize(cameraPosition - vWorldPosition);
      float cosAngle = abs(dot(viewDir, vWorldNormal));
      fresnel = pow(1.0 - cosAngle, fresnelPower);
      fresnel = clamp(fresnel, 0.0, 1.0);
    }
    
    vec3 finalColor = mix(color, reflectionColor.rgb, fresnel);
    gl_FragColor = vec4(finalColor, opacity);
  }
`;

// ============================================
// PLANAR REFLECTIONS SYSTEM
// ============================================

export class PlanarReflections {
  private scene: THREE.Scene;
  private renderer: THREE.WebGLRenderer;
  private reflectors: Map<string, ReflectorData> = new Map();
  
  constructor(scene: THREE.Scene, renderer: THREE.WebGLRenderer) {
    this.scene = scene;
    this.renderer = renderer;
  }
  
  /**
   * Add reflection plane
   */
  public addReflectionPlane(config: ReflectionPlaneConfig): THREE.Mesh {
    // Create reflection camera
    const camera = new THREE.PerspectiveCamera();
    
    // Create render target
    const renderTarget = new THREE.WebGLRenderTarget(
      config.textureWidth,
      config.textureHeight,
      {
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter,
        format: THREE.RGBAFormat,
        encoding: THREE.sRGBEncoding
      }
    );
    
    // Create reflector plane
    const reflectorPlane = new THREE.Plane();
    const clipPlane = new THREE.Vector4();
    
    // Create material
    const material = new THREE.ShaderMaterial({
      uniforms: {
        tReflection: { value: renderTarget.texture },
        textureMatrix: { value: new THREE.Matrix4() },
        color: { value: new THREE.Color(0x333333) },
        roughness: { value: config.roughness },
        useFresnel: { value: config.fresnel },
        fresnelPower: { value: config.fresnelPower },
        opacity: { value: 1.0 }
      },
      vertexShader: reflectionVertexShader,
      fragmentShader: reflectionFragmentShader,
      transparent: true
    });
    
    // Create mesh
    const geometry = new THREE.PlaneGeometry(config.width, config.height);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(config.position);
    
    // Align with normal
    const up = new THREE.Vector3(0, 0, 1);
    const quaternion = new THREE.Quaternion().setFromUnitVectors(up, config.normal);
    mesh.quaternion.copy(quaternion);
    
    this.scene.add(mesh);
    
    // Store reflector data
    const reflectorData: ReflectorData = {
      config,
      camera,
      renderTarget,
      reflectorPlane,
      mesh,
      clipPlane
    };
    
    this.reflectors.set(config.id, reflectorData);
    
    return mesh;
  }
  
  /**
   * Update reflections
   */
  public update(mainCamera: THREE.Camera): void {
    for (const [id, reflector] of this.reflectors) {
      this.updateReflector(reflector, mainCamera);
    }
  }
  
  private updateReflector(reflector: ReflectorData, mainCamera: THREE.Camera): void {
    const { config, camera, renderTarget, reflectorPlane, mesh, clipPlane } = reflector;
    
    // Get reflector world matrix
    mesh.updateMatrixWorld(true);
    const reflectorWorldPosition = new THREE.Vector3();
    const reflectorWorldQuaternion = new THREE.Quaternion();
    mesh.getWorldPosition(reflectorWorldPosition);
    mesh.getWorldQuaternion(reflectorWorldQuaternion);
    
    // Calculate normal in world space
    const normal = config.normal.clone().applyQuaternion(reflectorWorldQuaternion).normalize();
    
    // Set up reflection plane
    reflectorPlane.setFromNormalAndCoplanarPoint(normal, reflectorWorldPosition);
    
    // Calculate reflection matrix
    const reflectionMatrix = new THREE.Matrix4();
    const q = new THREE.Vector4();
    q.set(normal.x, normal.y, normal.z, -reflectorPlane.constant);
    
    reflectionMatrix.set(
      1 - 2 * q.x * q.x, -2 * q.x * q.y, -2 * q.x * q.z, -2 * q.x * q.w,
      -2 * q.x * q.y, 1 - 2 * q.y * q.y, -2 * q.y * q.z, -2 * q.y * q.w,
      -2 * q.x * q.z, -2 * q.y * q.z, 1 - 2 * q.z * q.z, -2 * q.z * q.w,
      0, 0, 0, 1
    );
    
    // Set up reflection camera
    camera.copy(mainCamera as THREE.PerspectiveCamera);
    camera.applyMatrix4(reflectionMatrix);
    
    // Calculate texture matrix
    const textureMatrix = new THREE.Matrix4();
    textureMatrix.set(
      0.5, 0.0, 0.0, 0.5,
      0.0, 0.5, 0.0, 0.5,
      0.0, 0.0, 0.5, 0.5,
      0.0, 0.0, 0.0, 1.0
    );
    textureMatrix.multiply(camera.projectionMatrix);
    textureMatrix.multiply(camera.matrixWorldInverse);
    
    (mesh.material as THREE.ShaderMaterial).uniforms.textureMatrix.value = textureMatrix;
    
    // Set up clip plane
    clipPlane.set(normal.x, normal.y, normal.z, reflectorPlane.constant);
    
    // Render reflection
    const currentRenderTarget = this.renderer.getRenderTarget();
    const currentXrEnabled = this.renderer.xr.enabled;
    
    this.renderer.xr.enabled = false;
    
    // Hide reflector mesh during render
    mesh.visible = false;
    
    // Set clipping plane
    const clippingPlanes = this.renderer.clippingPlanes;
    this.renderer.clippingPlanes = [new THREE.Plane().copy(reflectorPlane)];
    
    this.renderer.setRenderTarget(renderTarget);
    this.renderer.clear();
    this.renderer.render(this.scene, camera);
    
    // Restore
    this.renderer.clippingPlanes = clippingPlanes;
    mesh.visible = true;
    this.renderer.setRenderTarget(currentRenderTarget);
    this.renderer.xr.enabled = currentXrEnabled;
  }
  
  /**
   * Remove reflection plane
   */
  public removeReflectionPlane(id: string): void {
    const reflector = this.reflectors.get(id);
    if (reflector) {
      this.scene.remove(reflector.mesh);
      reflector.renderTarget.dispose();
      reflector.mesh.geometry.dispose();
      (reflector.mesh.material as THREE.Material).dispose();
      this.reflectors.delete(id);
    }
  }
  
  /**
   * Set reflector roughness
   */
  public setRoughness(id: string, roughness: number): void {
    const reflector = this.reflectors.get(id);
    if (reflector) {
      (reflector.mesh.material as THREE.ShaderMaterial).uniforms.roughness.value = roughness;
    }
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    for (const [id] of this.reflectors) {
      this.removeReflectionPlane(id);
    }
  }
}

