/**
 * Screen-Space Global Illumination (SSGI)
 * Real-time indirect lighting approximation
 * 
 * Features:
 * - Horizon-based indirect lighting
 * - Multi-bounce approximation
 * - Color bleeding
 * - Temporal accumulation
 * - Spatial denoising
 * - Performance scalability
 */

import * as THREE from 'three';
import { EffectComposer, Pass, FullScreenQuad } from 'three/examples/jsm/postprocessing/EffectComposer';

// ============================================
// TYPES
// ============================================

export interface SSGIConfig {
  samples: number;
  radius: number;
  intensity: number;
  bounces: number;
  temporalBlend: number;
  spatialRadius: number;
  depthThreshold: number;
  normalThreshold: number;
  colorBleeding: number;
  aoIntensity: number;
  halfResolution: boolean;
}

// ============================================
// SSGI SHADERS
// ============================================

const SSGIVertexShader = `
varying vec2 vUv;

void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const SSGIFragmentShader = `
precision highp float;

uniform sampler2D tDiffuse;      // Scene color
uniform sampler2D tDepth;        // Depth buffer
uniform sampler2D tNormal;       // Normal buffer (view space)
uniform sampler2D tPrevFrame;    // Previous frame for temporal
uniform sampler2D tNoise;        // Blue noise

uniform mat4 projectionMatrix;
uniform mat4 inverseProjectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 inverseViewMatrix;

uniform vec2 resolution;
uniform float cameraNear;
uniform float cameraFar;
uniform float time;
uniform float frame;

uniform int samples;
uniform float radius;
uniform float intensity;
uniform int bounces;
uniform float temporalBlend;
uniform float depthThreshold;
uniform float normalThreshold;
uniform float colorBleeding;
uniform float aoIntensity;

varying vec2 vUv;

const float PI = 3.14159265359;
const float TWO_PI = 6.28318530718;

// ============================================
// UTILITY FUNCTIONS
// ============================================

float linearizeDepth(float depth) {
  float z = depth * 2.0 - 1.0;
  return (2.0 * cameraNear * cameraFar) / (cameraFar + cameraNear - z * (cameraFar - cameraNear));
}

vec3 getViewPosition(vec2 uv, float depth) {
  vec4 clipPos = vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
  vec4 viewPos = inverseProjectionMatrix * clipPos;
  return viewPos.xyz / viewPos.w;
}

vec3 getWorldPosition(vec3 viewPos) {
  return (inverseViewMatrix * vec4(viewPos, 1.0)).xyz;
}

vec3 getViewNormal(vec2 uv) {
  return texture2D(tNormal, uv).xyz * 2.0 - 1.0;
}

// Cosine-weighted hemisphere sampling
vec3 cosineWeightedDirection(vec2 seed, vec3 normal) {
  float u1 = fract(sin(dot(seed, vec2(12.9898, 78.233))) * 43758.5453);
  float u2 = fract(sin(dot(seed + 0.1, vec2(12.9898, 78.233))) * 43758.5453);
  
  float r = sqrt(u1);
  float theta = TWO_PI * u2;
  
  vec3 tangent = normalize(cross(normal, abs(normal.y) < 0.99 ? vec3(0, 1, 0) : vec3(1, 0, 0)));
  vec3 bitangent = cross(normal, tangent);
  
  float x = r * cos(theta);
  float y = r * sin(theta);
  float z = sqrt(1.0 - u1);
  
  return normalize(tangent * x + bitangent * y + normal * z);
}

// Blue noise sampling
vec2 getBlueNoise(vec2 uv, float index) {
  vec2 noiseUV = uv * resolution / 64.0 + vec2(frame * 0.618, frame * 0.382) + index * 0.13;
  return texture2D(tNoise, noiseUV).xy;
}

// ============================================
// SSGI CORE
// ============================================

vec4 traceSSGI(vec3 origin, vec3 direction, float maxDist) {
  const int maxSteps = 16;
  float stepSize = maxDist / float(maxSteps);
  
  vec3 rayPos = origin;
  
  for (int i = 0; i < maxSteps; i++) {
    rayPos += direction * stepSize;
    
    // Project to screen
    vec4 projPos = projectionMatrix * vec4(rayPos, 1.0);
    projPos.xyz /= projPos.w;
    vec2 screenUV = projPos.xy * 0.5 + 0.5;
    
    // Check bounds
    if (screenUV.x < 0.0 || screenUV.x > 1.0 || screenUV.y < 0.0 || screenUV.y > 1.0) {
      break;
    }
    
    // Sample depth
    float sceneDepth = texture2D(tDepth, screenUV).r;
    vec3 sceneViewPos = getViewPosition(screenUV, sceneDepth);
    
    // Check hit
    float diff = rayPos.z - sceneViewPos.z;
    
    if (diff > 0.0 && diff < stepSize * 2.0) {
      // Hit! Sample color
      vec3 hitColor = texture2D(tDiffuse, screenUV).rgb;
      vec3 hitNormal = getViewNormal(screenUV);
      
      // Calculate contribution
      float NdotL = max(dot(-direction, hitNormal), 0.0);
      float attenuation = 1.0 - float(i) / float(maxSteps);
      
      return vec4(hitColor * NdotL * attenuation, 1.0);
    }
  }
  
  return vec4(0.0);
}

// Horizon-based ambient occlusion
float calculateHBAO(vec3 viewPos, vec3 viewNormal, vec2 uv) {
  float occlusion = 0.0;
  
  for (int i = 0; i < 8; i++) {
    vec2 noise = getBlueNoise(uv, float(i));
    float angle = noise.x * TWO_PI;
    float sampleRadius = radius * noise.y;
    
    vec2 offset = vec2(cos(angle), sin(angle)) * sampleRadius / resolution;
    
    float depth = texture2D(tDepth, uv + offset).r;
    vec3 samplePos = getViewPosition(uv + offset, depth);
    
    vec3 diff = samplePos - viewPos;
    float dist = length(diff);
    vec3 sampleDir = diff / dist;
    
    float NdotS = max(dot(viewNormal, sampleDir), 0.0);
    float attenuation = 1.0 / (1.0 + dist * dist * 0.1);
    
    occlusion += NdotS * attenuation;
  }
  
  return occlusion / 8.0;
}

// ============================================
// MAIN
// ============================================

void main() {
  vec2 uv = vUv;
  
  // Sample scene data
  vec4 sceneColor = texture2D(tDiffuse, uv);
  float depth = texture2D(tDepth, uv).r;
  
  // Early out for sky
  if (depth >= 1.0) {
    gl_FragColor = sceneColor;
    return;
  }
  
  vec3 viewPos = getViewPosition(uv, depth);
  vec3 viewNormal = getViewNormal(uv);
  
  // Accumulate indirect lighting
  vec3 indirectLight = vec3(0.0);
  float totalWeight = 0.0;
  
  for (int s = 0; s < 16; s++) {
    if (s >= samples) break;
    
    vec2 noise = getBlueNoise(uv, float(s));
    
    // Generate sample direction
    vec3 sampleDir = cosineWeightedDirection(uv + noise, viewNormal);
    
    // Trace
    vec4 traced = traceSSGI(viewPos, sampleDir, radius);
    
    if (traced.a > 0.0) {
      indirectLight += traced.rgb;
      totalWeight += 1.0;
    }
  }
  
  if (totalWeight > 0.0) {
    indirectLight /= totalWeight;
  }
  
  // Calculate AO
  float ao = 1.0 - calculateHBAO(viewPos, viewNormal, uv) * aoIntensity;
  
  // Apply color bleeding
  vec3 colorBleed = indirectLight * colorBleeding;
  
  // Temporal accumulation
  vec4 prevColor = texture2D(tPrevFrame, uv);
  vec3 currentGI = (sceneColor.rgb * ao + colorBleed * intensity);
  vec3 finalColor = mix(prevColor.rgb, currentGI, 1.0 - temporalBlend);
  
  gl_FragColor = vec4(finalColor, sceneColor.a);
}
`;

// ============================================
// DENOISER SHADER
// ============================================

const DenoiserFragmentShader = `
precision highp float;

uniform sampler2D tInput;
uniform sampler2D tDepth;
uniform sampler2D tNormal;
uniform vec2 resolution;
uniform float spatialRadius;
uniform float depthThreshold;
uniform float normalThreshold;

varying vec2 vUv;

void main() {
  vec3 centerColor = texture2D(tInput, vUv).rgb;
  float centerDepth = texture2D(tDepth, vUv).r;
  vec3 centerNormal = texture2D(tNormal, vUv).xyz * 2.0 - 1.0;
  
  vec3 sum = centerColor;
  float totalWeight = 1.0;
  
  int radius = int(spatialRadius);
  
  for (int x = -3; x <= 3; x++) {
    for (int y = -3; y <= 3; y++) {
      if (x == 0 && y == 0) continue;
      if (abs(x) > radius || abs(y) > radius) continue;
      
      vec2 offset = vec2(float(x), float(y)) / resolution;
      vec2 sampleUV = vUv + offset;
      
      if (sampleUV.x < 0.0 || sampleUV.x > 1.0 || sampleUV.y < 0.0 || sampleUV.y > 1.0) {
        continue;
      }
      
      float sampleDepth = texture2D(tDepth, sampleUV).r;
      vec3 sampleNormal = texture2D(tNormal, sampleUV).xyz * 2.0 - 1.0;
      vec3 sampleColor = texture2D(tInput, sampleUV).rgb;
      
      // Depth weight
      float depthDiff = abs(centerDepth - sampleDepth);
      float depthWeight = exp(-depthDiff * depthDiff / (depthThreshold * depthThreshold));
      
      // Normal weight
      float normalDiff = 1.0 - max(dot(centerNormal, sampleNormal), 0.0);
      float normalWeight = exp(-normalDiff * normalDiff / (normalThreshold * normalThreshold));
      
      // Spatial weight
      float dist = length(vec2(float(x), float(y)));
      float spatialWeight = exp(-dist * dist / (spatialRadius * spatialRadius));
      
      float weight = depthWeight * normalWeight * spatialWeight;
      
      sum += sampleColor * weight;
      totalWeight += weight;
    }
  }
  
  gl_FragColor = vec4(sum / totalWeight, 1.0);
}
`;

// ============================================
// BLUE NOISE GENERATOR
// ============================================

function generateBlueNoise(size: number): THREE.DataTexture {
  const data = new Uint8Array(size * size * 4);
  
  // Simple noise (in production, use proper blue noise)
  for (let i = 0; i < size * size; i++) {
    data[i * 4] = Math.floor(Math.random() * 256);
    data[i * 4 + 1] = Math.floor(Math.random() * 256);
    data[i * 4 + 2] = Math.floor(Math.random() * 256);
    data[i * 4 + 3] = 255;
  }
  
  const texture = new THREE.DataTexture(data, size, size);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.needsUpdate = true;
  
  return texture;
}

// ============================================
// SSGI PASS
// ============================================

export class SSGIPass extends Pass {
  private fsQuad: FullScreenQuad;
  private ssgiMaterial: THREE.ShaderMaterial;
  private denoiseMaterial: THREE.ShaderMaterial;
  
  private renderTargetSSGI: THREE.WebGLRenderTarget;
  private renderTargetDenoise: THREE.WebGLRenderTarget;
  private renderTargetPrev: THREE.WebGLRenderTarget;
  
  private noiseTexture: THREE.DataTexture;
  private config: SSGIConfig;
  private frame: number = 0;
  
  constructor(
    scene: THREE.Scene,
    camera: THREE.Camera,
    depthTexture: THREE.Texture,
    normalTexture: THREE.Texture,
    config: Partial<SSGIConfig> = {}
  ) {
    super();
    
    this.config = {
      samples: 8,
      radius: 2.0,
      intensity: 1.0,
      bounces: 1,
      temporalBlend: 0.9,
      spatialRadius: 2,
      depthThreshold: 0.1,
      normalThreshold: 0.3,
      colorBleeding: 0.5,
      aoIntensity: 0.5,
      halfResolution: false,
      ...config
    };
    
    this.noiseTexture = generateBlueNoise(64);
    
    // Create render targets
    const width = window.innerWidth;
    const height = window.innerHeight;
    const targetScale = this.config.halfResolution ? 0.5 : 1;
    
    const targetOptions: THREE.WebGLRenderTargetOptions = {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat,
      type: THREE.HalfFloatType
    };
    
    this.renderTargetSSGI = new THREE.WebGLRenderTarget(
      width * targetScale,
      height * targetScale,
      targetOptions
    );
    this.renderTargetDenoise = new THREE.WebGLRenderTarget(
      width * targetScale,
      height * targetScale,
      targetOptions
    );
    this.renderTargetPrev = new THREE.WebGLRenderTarget(
      width * targetScale,
      height * targetScale,
      targetOptions
    );
    
    // Create SSGI material
    this.ssgiMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        tDepth: { value: depthTexture },
        tNormal: { value: normalTexture },
        tPrevFrame: { value: this.renderTargetPrev.texture },
        tNoise: { value: this.noiseTexture },
        projectionMatrix: { value: camera.projectionMatrix },
        inverseProjectionMatrix: { value: camera.projectionMatrixInverse },
        viewMatrix: { value: camera.matrixWorldInverse },
        inverseViewMatrix: { value: camera.matrixWorld },
        resolution: { value: new THREE.Vector2(width, height) },
        cameraNear: { value: (camera as THREE.PerspectiveCamera).near },
        cameraFar: { value: (camera as THREE.PerspectiveCamera).far },
        time: { value: 0 },
        frame: { value: 0 },
        samples: { value: this.config.samples },
        radius: { value: this.config.radius },
        intensity: { value: this.config.intensity },
        bounces: { value: this.config.bounces },
        temporalBlend: { value: this.config.temporalBlend },
        depthThreshold: { value: this.config.depthThreshold },
        normalThreshold: { value: this.config.normalThreshold },
        colorBleeding: { value: this.config.colorBleeding },
        aoIntensity: { value: this.config.aoIntensity }
      },
      vertexShader: SSGIVertexShader,
      fragmentShader: SSGIFragmentShader
    });
    
    // Create denoise material
    this.denoiseMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        tDepth: { value: depthTexture },
        tNormal: { value: normalTexture },
        resolution: { value: new THREE.Vector2(width, height) },
        spatialRadius: { value: this.config.spatialRadius },
        depthThreshold: { value: this.config.depthThreshold },
        normalThreshold: { value: this.config.normalThreshold }
      },
      vertexShader: SSGIVertexShader,
      fragmentShader: DenoiserFragmentShader
    });
    
    this.fsQuad = new FullScreenQuad(this.ssgiMaterial);
  }
  
  public render(
    renderer: THREE.WebGLRenderer,
    writeBuffer: THREE.WebGLRenderTarget,
    readBuffer: THREE.WebGLRenderTarget
  ): void {
    this.frame++;
    
    // Update uniforms
    this.ssgiMaterial.uniforms.tDiffuse.value = readBuffer.texture;
    this.ssgiMaterial.uniforms.time.value = performance.now() * 0.001;
    this.ssgiMaterial.uniforms.frame.value = this.frame;
    
    // Render SSGI
    this.fsQuad.material = this.ssgiMaterial;
    renderer.setRenderTarget(this.renderTargetSSGI);
    this.fsQuad.render(renderer);
    
    // Denoise
    this.denoiseMaterial.uniforms.tInput.value = this.renderTargetSSGI.texture;
    this.fsQuad.material = this.denoiseMaterial;
    
    if (this.renderToScreen) {
      renderer.setRenderTarget(null);
    } else {
      renderer.setRenderTarget(writeBuffer);
    }
    this.fsQuad.render(renderer);
    
    // Swap prev frame
    const temp = this.renderTargetPrev;
    this.renderTargetPrev = this.renderTargetSSGI;
    this.renderTargetSSGI = temp;
    this.ssgiMaterial.uniforms.tPrevFrame.value = this.renderTargetPrev.texture;
  }
  
  public setSize(width: number, height: number): void {
    const scale = this.config.halfResolution ? 0.5 : 1;
    this.renderTargetSSGI.setSize(width * scale, height * scale);
    this.renderTargetDenoise.setSize(width * scale, height * scale);
    this.renderTargetPrev.setSize(width * scale, height * scale);
    
    this.ssgiMaterial.uniforms.resolution.value.set(width, height);
    this.denoiseMaterial.uniforms.resolution.value.set(width, height);
  }
  
  public dispose(): void {
    this.renderTargetSSGI.dispose();
    this.renderTargetDenoise.dispose();
    this.renderTargetPrev.dispose();
    this.noiseTexture.dispose();
    this.ssgiMaterial.dispose();
    this.denoiseMaterial.dispose();
    this.fsQuad.dispose();
  }
}

// ============================================
// SSGI SYSTEM WRAPPER
// ============================================

export class SSGISystem {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private ssgiPass: SSGIPass | null = null;
  
  private depthTarget: THREE.WebGLRenderTarget;
  private normalTarget: THREE.WebGLRenderTarget;
  private depthMaterial: THREE.MeshDepthMaterial;
  private normalMaterial: THREE.MeshNormalMaterial;
  
  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.Camera
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // Create depth target
    this.depthTarget = new THREE.WebGLRenderTarget(width, height, {
      minFilter: THREE.NearestFilter,
      magFilter: THREE.NearestFilter,
      format: THREE.RGBAFormat,
      type: THREE.FloatType
    });
    
    // Create normal target
    this.normalTarget = new THREE.WebGLRenderTarget(width, height, {
      minFilter: THREE.NearestFilter,
      magFilter: THREE.NearestFilter,
      format: THREE.RGBAFormat
    });
    
    this.depthMaterial = new THREE.MeshDepthMaterial({
      depthPacking: THREE.RGBADepthPacking
    });
    
    this.normalMaterial = new THREE.MeshNormalMaterial();
  }
  
  public init(config: Partial<SSGIConfig> = {}): SSGIPass {
    this.ssgiPass = new SSGIPass(
      this.scene,
      this.camera,
      this.depthTarget.texture,
      this.normalTarget.texture,
      config
    );
    
    return this.ssgiPass;
  }
  
  public preRender(): void {
    const currentBackground = this.scene.background;
    const currentOverrideMaterial = this.scene.overrideMaterial;
    
    // Render depth
    this.scene.overrideMaterial = this.depthMaterial;
    this.scene.background = null;
    this.renderer.setRenderTarget(this.depthTarget);
    this.renderer.render(this.scene, this.camera);
    
    // Render normals
    this.scene.overrideMaterial = this.normalMaterial;
    this.renderer.setRenderTarget(this.normalTarget);
    this.renderer.render(this.scene, this.camera);
    
    // Restore
    this.scene.overrideMaterial = currentOverrideMaterial;
    this.scene.background = currentBackground;
    this.renderer.setRenderTarget(null);
  }
  
  public resize(width: number, height: number): void {
    this.depthTarget.setSize(width, height);
    this.normalTarget.setSize(width, height);
    this.ssgiPass?.setSize(width, height);
  }
  
  public dispose(): void {
    this.depthTarget.dispose();
    this.normalTarget.dispose();
    this.depthMaterial.dispose();
    this.normalMaterial.dispose();
    this.ssgiPass?.dispose();
  }
}

