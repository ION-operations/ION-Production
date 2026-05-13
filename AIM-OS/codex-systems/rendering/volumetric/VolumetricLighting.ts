/**
 * Volumetric Lighting System (God Rays)
 * Screen-space and raymarched volumetric light scattering
 * 
 * Features:
 * - Radial blur god rays (fast)
 * - Raymarched volumetric fog
 * - Shadow-aware scattering
 * - Colored light volumes
 * - Dust particles
 * - Animated noise
 */

import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';

// ============================================
// TYPES
// ============================================

export interface VolumetricLightConfig {
  samples: number;
  density: number;
  weight: number;
  decay: number;
  exposure: number;
  clampMax: number;
}

export interface VolumetricFogConfig {
  density: number;
  heightFalloff: number;
  scatteringCoeff: number;
  absorptionCoeff: number;
  phaseG: number;  // Henyey-Greenstein phase function parameter
  noiseScale: number;
  noiseSpeed: number;
}

// ============================================
// RADIAL BLUR GOD RAYS (Screen Space)
// ============================================

export const GodRayShader = {
  uniforms: {
    tDiffuse: { value: null },
    tOcclusion: { value: null },
    lightPositionOnScreen: { value: new THREE.Vector2(0.5, 0.5) },
    samples: { value: 50 },
    density: { value: 0.96 },
    weight: { value: 0.4 },
    decay: { value: 0.93 },
    exposure: { value: 0.5 },
    clampMax: { value: 1.0 }
  },
  
  vertexShader: `
    varying vec2 vUv;
    
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform sampler2D tOcclusion;
    uniform vec2 lightPositionOnScreen;
    uniform int samples;
    uniform float density;
    uniform float weight;
    uniform float decay;
    uniform float exposure;
    uniform float clampMax;
    
    varying vec2 vUv;
    
    void main() {
      vec2 texCoord = vUv;
      vec2 deltaTextCoord = texCoord - lightPositionOnScreen;
      deltaTextCoord *= 1.0 / float(samples) * density;
      
      vec4 color = texture2D(tDiffuse, texCoord);
      vec4 occlusionColor = texture2D(tOcclusion, texCoord);
      
      float illuminationDecay = 1.0;
      vec3 godRays = vec3(0.0);
      
      for (int i = 0; i < 100; i++) {
        if (i >= samples) break;
        
        texCoord -= deltaTextCoord;
        vec4 sample = texture2D(tOcclusion, texCoord);
        
        sample *= illuminationDecay * weight;
        godRays += sample.rgb;
        illuminationDecay *= decay;
      }
      
      godRays *= exposure;
      godRays = clamp(godRays, 0.0, clampMax);
      
      gl_FragColor = vec4(color.rgb + godRays, color.a);
    }
  `
};

// ============================================
// OCCLUSION MASK GENERATOR
// ============================================

export const OcclusionMaskShader = {
  uniforms: {
    tDepth: { value: null },
    tScene: { value: null },
    lightPosition: { value: new THREE.Vector3() },
    cameraNear: { value: 0.1 },
    cameraFar: { value: 1000 },
    lightColor: { value: new THREE.Color(1, 1, 1) },
    threshold: { value: 0.95 }
  },
  
  vertexShader: `
    varying vec2 vUv;
    
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  
  fragmentShader: `
    uniform sampler2D tDepth;
    uniform sampler2D tScene;
    uniform vec3 lightPosition;
    uniform float cameraNear;
    uniform float cameraFar;
    uniform vec3 lightColor;
    uniform float threshold;
    
    varying vec2 vUv;
    
    float readDepth(sampler2D depthSampler, vec2 coord) {
      float fragCoordZ = texture2D(depthSampler, coord).x;
      float viewZ = (cameraNear * cameraFar) / ((cameraFar - cameraNear) * fragCoordZ - cameraFar);
      return viewZ;
    }
    
    void main() {
      float depth = readDepth(tDepth, vUv);
      vec4 sceneColor = texture2D(tScene, vUv);
      
      // If depth is very far (sky), show light
      float mask = step(threshold * cameraFar, -depth);
      
      // Also include very bright areas
      float luminance = dot(sceneColor.rgb, vec3(0.299, 0.587, 0.114));
      mask = max(mask, step(threshold, luminance));
      
      gl_FragColor = vec4(lightColor * mask, 1.0);
    }
  `
};

// ============================================
// GOD RAY PASS
// ============================================

export class GodRayPass {
  private occlusionRenderTarget: THREE.WebGLRenderTarget;
  private occlusionPass: ShaderPass;
  private godRayPass: ShaderPass;
  private lightScreenPosition: THREE.Vector2 = new THREE.Vector2();
  
  constructor(
    width: number,
    height: number,
    private light: THREE.Light,
    private camera: THREE.Camera,
    config: Partial<VolumetricLightConfig> = {}
  ) {
    // Create occlusion render target
    this.occlusionRenderTarget = new THREE.WebGLRenderTarget(width / 2, height / 2, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat
    });
    
    // Occlusion mask pass
    this.occlusionPass = new ShaderPass({
      uniforms: THREE.UniformsUtils.clone(OcclusionMaskShader.uniforms),
      vertexShader: OcclusionMaskShader.vertexShader,
      fragmentShader: OcclusionMaskShader.fragmentShader
    });
    
    // God ray pass
    this.godRayPass = new ShaderPass({
      uniforms: THREE.UniformsUtils.clone(GodRayShader.uniforms),
      vertexShader: GodRayShader.vertexShader,
      fragmentShader: GodRayShader.fragmentShader
    });
    
    // Apply config
    const fullConfig: VolumetricLightConfig = {
      samples: 50,
      density: 0.96,
      weight: 0.4,
      decay: 0.93,
      exposure: 0.5,
      clampMax: 1.0,
      ...config
    };
    
    this.godRayPass.uniforms.samples.value = fullConfig.samples;
    this.godRayPass.uniforms.density.value = fullConfig.density;
    this.godRayPass.uniforms.weight.value = fullConfig.weight;
    this.godRayPass.uniforms.decay.value = fullConfig.decay;
    this.godRayPass.uniforms.exposure.value = fullConfig.exposure;
    this.godRayPass.uniforms.clampMax.value = fullConfig.clampMax;
  }
  
  public update(): void {
    // Project light position to screen
    const lightPos = this.light.position.clone();
    lightPos.project(this.camera);
    
    this.lightScreenPosition.set(
      (lightPos.x + 1) / 2,
      (lightPos.y + 1) / 2
    );
    
    this.godRayPass.uniforms.lightPositionOnScreen.value = this.lightScreenPosition;
    this.occlusionPass.uniforms.lightPosition.value = this.light.position;
    
    if (this.light instanceof THREE.DirectionalLight || this.light instanceof THREE.PointLight) {
      this.occlusionPass.uniforms.lightColor.value = this.light.color;
    }
  }
  
  public getOcclusionPass(): ShaderPass {
    return this.occlusionPass;
  }
  
  public getGodRayPass(): ShaderPass {
    return this.godRayPass;
  }
  
  public setDepthTexture(texture: THREE.DepthTexture): void {
    this.occlusionPass.uniforms.tDepth.value = texture;
  }
  
  public setExposure(value: number): void {
    this.godRayPass.uniforms.exposure.value = value;
  }
  
  public setDensity(value: number): void {
    this.godRayPass.uniforms.density.value = value;
  }
  
  public dispose(): void {
    this.occlusionRenderTarget.dispose();
  }
}

// ============================================
// RAYMARCHED VOLUMETRIC FOG
// ============================================

export const VolumetricFogShader = {
  uniforms: {
    tDiffuse: { value: null },
    tDepth: { value: null },
    tNoise: { value: null },
    cameraNear: { value: 0.1 },
    cameraFar: { value: 1000 },
    cameraPosition: { value: new THREE.Vector3() },
    viewMatrix: { value: new THREE.Matrix4() },
    projectionMatrixInverse: { value: new THREE.Matrix4() },
    lightPosition: { value: new THREE.Vector3() },
    lightColor: { value: new THREE.Color(1, 1, 1) },
    lightIntensity: { value: 1.0 },
    fogColor: { value: new THREE.Color(0.5, 0.6, 0.7) },
    density: { value: 0.02 },
    heightFalloff: { value: 0.1 },
    scatteringCoeff: { value: 0.5 },
    absorptionCoeff: { value: 0.1 },
    phaseG: { value: 0.5 },
    noiseScale: { value: 0.01 },
    noiseSpeed: { value: 0.1 },
    time: { value: 0 },
    steps: { value: 32 },
    resolution: { value: new THREE.Vector2() }
  },
  
  vertexShader: `
    varying vec2 vUv;
    
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform sampler2D tDepth;
    uniform sampler2D tNoise;
    
    uniform float cameraNear;
    uniform float cameraFar;
    uniform vec3 cameraPosition;
    uniform mat4 viewMatrix;
    uniform mat4 projectionMatrixInverse;
    
    uniform vec3 lightPosition;
    uniform vec3 lightColor;
    uniform float lightIntensity;
    
    uniform vec3 fogColor;
    uniform float density;
    uniform float heightFalloff;
    uniform float scatteringCoeff;
    uniform float absorptionCoeff;
    uniform float phaseG;
    
    uniform float noiseScale;
    uniform float noiseSpeed;
    uniform float time;
    uniform int steps;
    uniform vec2 resolution;
    
    varying vec2 vUv;
    
    // Convert depth buffer value to linear depth
    float linearizeDepth(float depth) {
      float z = depth * 2.0 - 1.0;
      return (2.0 * cameraNear * cameraFar) / (cameraFar + cameraNear - z * (cameraFar - cameraNear));
    }
    
    // Get world position from UV and depth
    vec3 getWorldPosition(vec2 uv, float depth) {
      vec4 clipPos = vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
      vec4 viewPos = projectionMatrixInverse * clipPos;
      viewPos /= viewPos.w;
      vec4 worldPos = inverse(viewMatrix) * viewPos;
      return worldPos.xyz;
    }
    
    // Henyey-Greenstein phase function
    float phaseHG(float cosTheta, float g) {
      float g2 = g * g;
      float denom = 1.0 + g2 - 2.0 * g * cosTheta;
      return (1.0 - g2) / (4.0 * 3.14159 * pow(denom, 1.5));
    }
    
    // Sample 3D noise
    float sampleNoise(vec3 pos) {
      vec3 noisePos = pos * noiseScale + vec3(0.0, 0.0, time * noiseSpeed);
      vec2 noiseUv = noisePos.xz * 0.1 + noisePos.y * 0.01;
      return texture2D(tNoise, noiseUv).r;
    }
    
    // Get fog density at position
    float getFogDensity(vec3 pos) {
      float baseDensity = density;
      
      // Height falloff
      baseDensity *= exp(-pos.y * heightFalloff);
      
      // Noise modulation
      float noise = sampleNoise(pos);
      baseDensity *= 0.5 + noise * 0.5;
      
      return max(0.0, baseDensity);
    }
    
    void main() {
      vec4 sceneColor = texture2D(tDiffuse, vUv);
      float depth = texture2D(tDepth, vUv).r;
      
      // Get ray direction
      vec3 rayOrigin = cameraPosition;
      vec3 worldPos = getWorldPosition(vUv, depth);
      vec3 rayDir = normalize(worldPos - rayOrigin);
      
      float linearDepth = linearizeDepth(depth);
      float maxDist = min(linearDepth, cameraFar);
      
      // Raymarch through fog
      float stepSize = maxDist / float(steps);
      vec3 currentPos = rayOrigin;
      
      vec3 inScattering = vec3(0.0);
      float transmittance = 1.0;
      
      // Light direction
      vec3 lightDir = normalize(lightPosition - currentPos);
      
      for (int i = 0; i < 64; i++) {
        if (i >= steps) break;
        
        float t = (float(i) + 0.5) * stepSize;
        currentPos = rayOrigin + rayDir * t;
        
        // Sample density
        float fogDensity = getFogDensity(currentPos);
        
        if (fogDensity > 0.001) {
          // Light direction at this point
          lightDir = normalize(lightPosition - currentPos);
          float cosTheta = dot(rayDir, lightDir);
          
          // Phase function
          float phase = phaseHG(cosTheta, phaseG);
          
          // Light attenuation (simple)
          float lightDist = length(lightPosition - currentPos);
          float lightAtten = lightIntensity / (1.0 + lightDist * 0.1);
          
          // Scattering
          vec3 scatter = scatteringCoeff * fogDensity * phase * lightColor * lightAtten;
          
          // Absorption
          float absorption = absorptionCoeff * fogDensity * stepSize;
          
          // Integrate
          inScattering += transmittance * scatter * stepSize;
          transmittance *= exp(-absorption);
          
          // Early exit
          if (transmittance < 0.01) break;
        }
      }
      
      // Combine with scene
      vec3 finalColor = sceneColor.rgb * transmittance + inScattering + fogColor * (1.0 - transmittance) * 0.1;
      
      gl_FragColor = vec4(finalColor, sceneColor.a);
    }
  `
};

// ============================================
// VOLUMETRIC FOG SYSTEM
// ============================================

export class VolumetricFogSystem {
  private shaderPass: ShaderPass;
  private noiseTexture: THREE.DataTexture;
  private config: VolumetricFogConfig;
  private time: number = 0;
  
  constructor(
    private camera: THREE.Camera,
    private light: THREE.Light,
    config: Partial<VolumetricFogConfig> = {}
  ) {
    this.config = {
      density: 0.02,
      heightFalloff: 0.1,
      scatteringCoeff: 0.5,
      absorptionCoeff: 0.1,
      phaseG: 0.5,
      noiseScale: 0.01,
      noiseSpeed: 0.1,
      ...config
    };
    
    // Create noise texture
    this.noiseTexture = this.createNoiseTexture(256);
    
    // Create shader pass
    this.shaderPass = new ShaderPass({
      uniforms: THREE.UniformsUtils.clone(VolumetricFogShader.uniforms),
      vertexShader: VolumetricFogShader.vertexShader,
      fragmentShader: VolumetricFogShader.fragmentShader
    });
    
    this.shaderPass.uniforms.tNoise.value = this.noiseTexture;
    this.applyConfig();
  }
  
  private createNoiseTexture(size: number): THREE.DataTexture {
    const data = new Uint8Array(size * size);
    
    // Simple Perlin-like noise
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        // Multiple octaves
        let value = 0;
        let amplitude = 1;
        let frequency = 1;
        
        for (let o = 0; o < 4; o++) {
          const nx = x * frequency / size;
          const ny = y * frequency / size;
          value += (Math.sin(nx * 6.28 + Math.random()) * 0.5 + 0.5 +
                   Math.sin(ny * 6.28 + Math.random()) * 0.5 + 0.5) * 0.5 * amplitude;
          amplitude *= 0.5;
          frequency *= 2;
        }
        
        data[y * size + x] = Math.floor(value * 128 + 64);
      }
    }
    
    const texture = new THREE.DataTexture(data, size, size, THREE.RedFormat);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.needsUpdate = true;
    
    return texture;
  }
  
  private applyConfig(): void {
    const u = this.shaderPass.uniforms;
    u.density.value = this.config.density;
    u.heightFalloff.value = this.config.heightFalloff;
    u.scatteringCoeff.value = this.config.scatteringCoeff;
    u.absorptionCoeff.value = this.config.absorptionCoeff;
    u.phaseG.value = this.config.phaseG;
    u.noiseScale.value = this.config.noiseScale;
    u.noiseSpeed.value = this.config.noiseSpeed;
  }
  
  public update(deltaTime: number): void {
    this.time += deltaTime;
    
    const u = this.shaderPass.uniforms;
    u.time.value = this.time;
    u.cameraPosition.value.copy(this.camera.position);
    u.viewMatrix.value.copy(this.camera.matrixWorldInverse);
    
    if (this.camera instanceof THREE.PerspectiveCamera) {
      u.cameraNear.value = this.camera.near;
      u.cameraFar.value = this.camera.far;
      u.projectionMatrixInverse.value.copy(this.camera.projectionMatrixInverse);
    }
    
    u.lightPosition.value.copy(this.light.position);
    
    if (this.light instanceof THREE.DirectionalLight || this.light instanceof THREE.PointLight) {
      u.lightColor.value = this.light.color;
      u.lightIntensity.value = this.light.intensity;
    }
  }
  
  public setDepthTexture(texture: THREE.DepthTexture): void {
    this.shaderPass.uniforms.tDepth.value = texture;
  }
  
  public setResolution(width: number, height: number): void {
    this.shaderPass.uniforms.resolution.value.set(width, height);
  }
  
  public getPass(): ShaderPass {
    return this.shaderPass;
  }
  
  public setDensity(value: number): void {
    this.config.density = value;
    this.shaderPass.uniforms.density.value = value;
  }
  
  public setFogColor(color: THREE.Color): void {
    this.shaderPass.uniforms.fogColor.value = color;
  }
  
  public dispose(): void {
    this.noiseTexture.dispose();
  }
}

// ============================================
// DUST PARTICLES
// ============================================

export class DustParticles {
  public points: THREE.Points;
  private geometry: THREE.BufferGeometry;
  private velocities: Float32Array;
  private opacities: Float32Array;
  private sizes: Float32Array;
  private particleCount: number;
  
  constructor(
    count: number = 5000,
    bounds: THREE.Box3 = new THREE.Box3(
      new THREE.Vector3(-20, 0, -20),
      new THREE.Vector3(20, 10, 20)
    )
  ) {
    this.particleCount = count;
    
    // Create geometry
    this.geometry = new THREE.BufferGeometry();
    
    const positions = new Float32Array(count * 3);
    this.velocities = new Float32Array(count * 3);
    this.opacities = new Float32Array(count);
    this.sizes = new Float32Array(count);
    
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    
    for (let i = 0; i < count; i++) {
      // Random position within bounds
      positions[i * 3] = (Math.random() - 0.5) * size.x + center.x;
      positions[i * 3 + 1] = (Math.random() - 0.5) * size.y + center.y;
      positions[i * 3 + 2] = (Math.random() - 0.5) * size.z + center.z;
      
      // Random velocity (slow drift)
      this.velocities[i * 3] = (Math.random() - 0.5) * 0.02;
      this.velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.01;
      this.velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
      
      // Random opacity and size
      this.opacities[i] = Math.random() * 0.5 + 0.2;
      this.sizes[i] = Math.random() * 0.05 + 0.02;
    }
    
    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('opacity', new THREE.BufferAttribute(this.opacities, 1));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));
    
    // Material
    const material = new THREE.ShaderMaterial({
      uniforms: {
        lightPosition: { value: new THREE.Vector3(0, 10, 0) },
        lightColor: { value: new THREE.Color(1, 1, 1) },
        lightIntensity: { value: 1.0 }
      },
      vertexShader: `
        attribute float opacity;
        attribute float size;
        
        varying float vOpacity;
        varying vec3 vWorldPosition;
        
        void main() {
          vOpacity = opacity;
          
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vWorldPosition = worldPos.xyz;
          
          vec4 mvPosition = viewMatrix * worldPos;
          
          gl_Position = projectionMatrix * mvPosition;
          gl_PointSize = size * 100.0 / -mvPosition.z;
        }
      `,
      fragmentShader: `
        uniform vec3 lightPosition;
        uniform vec3 lightColor;
        uniform float lightIntensity;
        
        varying float vOpacity;
        varying vec3 vWorldPosition;
        
        void main() {
          // Circular point shape
          vec2 center = gl_PointCoord - 0.5;
          float dist = length(center);
          if (dist > 0.5) discard;
          
          float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
          alpha *= vOpacity;
          
          // Light contribution
          vec3 lightDir = normalize(lightPosition - vWorldPosition);
          float lightDist = length(lightPosition - vWorldPosition);
          float atten = lightIntensity / (1.0 + lightDist * 0.1);
          
          vec3 color = lightColor * atten + vec3(0.1);
          
          gl_FragColor = vec4(color, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    
    this.points = new THREE.Points(this.geometry, material);
  }
  
  public update(deltaTime: number, wind: THREE.Vector3 = new THREE.Vector3()): void {
    const positions = this.geometry.getAttribute('position');
    const posArray = positions.array as Float32Array;
    
    for (let i = 0; i < this.particleCount; i++) {
      // Apply velocity + wind
      posArray[i * 3] += (this.velocities[i * 3] + wind.x) * deltaTime;
      posArray[i * 3 + 1] += (this.velocities[i * 3 + 1] + wind.y) * deltaTime;
      posArray[i * 3 + 2] += (this.velocities[i * 3 + 2] + wind.z) * deltaTime;
      
      // Slight random perturbation
      this.velocities[i * 3] += (Math.random() - 0.5) * 0.01;
      this.velocities[i * 3 + 1] += (Math.random() - 0.5) * 0.005;
      this.velocities[i * 3 + 2] += (Math.random() - 0.5) * 0.01;
      
      // Damping
      this.velocities[i * 3] *= 0.99;
      this.velocities[i * 3 + 1] *= 0.99;
      this.velocities[i * 3 + 2] *= 0.99;
      
      // Respawn if too far
      if (Math.abs(posArray[i * 3]) > 30 ||
          posArray[i * 3 + 1] < -5 || posArray[i * 3 + 1] > 15 ||
          Math.abs(posArray[i * 3 + 2]) > 30) {
        posArray[i * 3] = (Math.random() - 0.5) * 40;
        posArray[i * 3 + 1] = Math.random() * 10;
        posArray[i * 3 + 2] = (Math.random() - 0.5) * 40;
      }
    }
    
    positions.needsUpdate = true;
  }
  
  public setLightPosition(position: THREE.Vector3): void {
    (this.points.material as THREE.ShaderMaterial).uniforms.lightPosition.value = position;
  }
  
  public setLightColor(color: THREE.Color): void {
    (this.points.material as THREE.ShaderMaterial).uniforms.lightColor.value = color;
  }
  
  public dispose(): void {
    this.geometry.dispose();
    (this.points.material as THREE.Material).dispose();
  }
}

// ============================================
// VOLUMETRIC SPOTLIGHT
// ============================================

export class VolumetricSpotlight {
  public mesh: THREE.Mesh;
  private cone: THREE.ConeGeometry;
  private material: THREE.ShaderMaterial;
  
  constructor(
    distance: number = 10,
    angle: number = Math.PI / 4,
    color: THREE.Color = new THREE.Color(1, 1, 1),
    intensity: number = 1.0
  ) {
    const radius = distance * Math.tan(angle);
    this.cone = new THREE.ConeGeometry(radius, distance, 32, 1, true);
    
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        lightColor: { value: color },
        intensity: { value: intensity },
        falloff: { value: 0.5 },
        time: { value: 0 }
      },
      vertexShader: `
        varying vec3 vPosition;
        varying float vHeight;
        
        void main() {
          vPosition = position;
          vHeight = (position.y + 0.5);  // 0 at tip, 1 at base
          
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 lightColor;
        uniform float intensity;
        uniform float falloff;
        uniform float time;
        
        varying vec3 vPosition;
        varying float vHeight;
        
        void main() {
          // Radial falloff from center
          float dist = length(vPosition.xz);
          float maxRadius = vHeight * 0.5;  // Cone radius at this height
          float radialFalloff = 1.0 - smoothstep(0.0, maxRadius, dist);
          
          // Height falloff
          float heightFalloff = pow(1.0 - vHeight, falloff);
          
          // Combine
          float alpha = radialFalloff * heightFalloff * intensity;
          
          // Add subtle noise
          float noise = sin(vPosition.x * 10.0 + time) * sin(vPosition.z * 10.0 - time) * 0.1;
          alpha *= 1.0 + noise;
          
          gl_FragColor = vec4(lightColor * alpha, alpha * 0.3);
        }
      `,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending
    });
    
    this.mesh = new THREE.Mesh(this.cone, this.material);
    this.mesh.rotation.x = Math.PI;  // Point downward
  }
  
  public update(deltaTime: number): void {
    this.material.uniforms.time.value += deltaTime;
  }
  
  public setColor(color: THREE.Color): void {
    this.material.uniforms.lightColor.value = color;
  }
  
  public setIntensity(intensity: number): void {
    this.material.uniforms.intensity.value = intensity;
  }
  
  public dispose(): void {
    this.cone.dispose();
    this.material.dispose();
  }
}

