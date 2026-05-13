/**
 * Lens Effects System
 * Realistic camera lens simulation
 * 
 * Features:
 * - Lens flare
 * - Lens dirt
 * - Chromatic aberration
 * - Vignette
 * - Barrel/pincushion distortion
 * - Bokeh
 * - Anamorphic effects
 * - Light streaks
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface LensFlareElement {
  texture: THREE.Texture | null;
  color: THREE.Color;
  size: number;
  distance: number;  // Position along flare line (0 = light source, 1 = center, 2 = opposite)
  opacity: number;
}

export interface LensEffectsConfig {
  // Lens flare
  flareEnabled: boolean;
  flareIntensity: number;
  flareElements: LensFlareElement[];
  
  // Lens dirt
  dirtEnabled: boolean;
  dirtTexture: THREE.Texture | null;
  dirtIntensity: number;
  
  // Chromatic aberration
  chromaticEnabled: boolean;
  chromaticStrength: number;
  
  // Vignette
  vignetteEnabled: boolean;
  vignetteIntensity: number;
  vignetteSmoothness: number;
  
  // Distortion
  distortionEnabled: boolean;
  distortionStrength: number;  // Positive = barrel, negative = pincushion
  
  // Bokeh
  bokehEnabled: boolean;
  bokehAperture: number;
  bokehFocus: number;
  bokehMaxBlur: number;
  
  // Anamorphic
  anamorphicEnabled: boolean;
  anamorphicStretch: number;
  anamorphicFlareIntensity: number;
}

// ============================================
// LENS FLARE SYSTEM
// ============================================

export class LensFlareSystem {
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private flareGroup: THREE.Group;
  private flareMeshes: THREE.Mesh[] = [];
  private lightSources: { position: THREE.Vector3; color: THREE.Color; intensity: number }[] = [];
  
  constructor(scene: THREE.Scene, camera: THREE.Camera) {
    this.scene = scene;
    this.camera = camera;
    this.flareGroup = new THREE.Group();
    this.flareGroup.renderOrder = 999;
    scene.add(this.flareGroup);
  }
  
  /**
   * Create default flare elements
   */
  public createDefaultElements(): LensFlareElement[] {
    return [
      // Main glow
      { texture: null, color: new THREE.Color(1, 0.9, 0.8), size: 0.5, distance: 0, opacity: 0.6 },
      // Halo
      { texture: null, color: new THREE.Color(0.8, 0.9, 1), size: 0.3, distance: 0.2, opacity: 0.3 },
      // Ghost reflections
      { texture: null, color: new THREE.Color(0.5, 0.8, 1), size: 0.1, distance: 0.6, opacity: 0.2 },
      { texture: null, color: new THREE.Color(1, 0.5, 0.3), size: 0.15, distance: 0.9, opacity: 0.15 },
      { texture: null, color: new THREE.Color(0.3, 0.5, 1), size: 0.08, distance: 1.2, opacity: 0.1 },
      { texture: null, color: new THREE.Color(1, 1, 0.5), size: 0.2, distance: 1.5, opacity: 0.1 },
      { texture: null, color: new THREE.Color(0.5, 1, 0.5), size: 0.05, distance: 1.8, opacity: 0.1 },
    ];
  }
  
  /**
   * Add light source for flare
   */
  public addLightSource(position: THREE.Vector3, color: THREE.Color, intensity: number = 1): void {
    this.lightSources.push({ position: position.clone(), color: color.clone(), intensity });
  }
  
  /**
   * Clear all light sources
   */
  public clearLightSources(): void {
    this.lightSources = [];
  }
  
  /**
   * Update flares
   */
  public update(elements: LensFlareElement[]): void {
    // Clear existing flare meshes
    for (const mesh of this.flareMeshes) {
      this.flareGroup.remove(mesh);
      mesh.geometry.dispose();
      (mesh.material as THREE.Material).dispose();
    }
    this.flareMeshes = [];
    
    const screenCenter = new THREE.Vector2(0, 0);
    
    for (const light of this.lightSources) {
      // Project light position to screen
      const screenPos = light.position.clone().project(this.camera);
      
      // Check if in front of camera
      if (screenPos.z > 1) continue;
      
      // Check if on screen (with margin)
      if (Math.abs(screenPos.x) > 1.5 || Math.abs(screenPos.y) > 1.5) continue;
      
      // Calculate flare line direction
      const flareDir = new THREE.Vector2(screenPos.x, screenPos.y).negate();
      
      // Create elements along flare line
      for (const element of elements) {
        const pos = new THREE.Vector2()
          .copy(flareDir)
          .multiplyScalar(element.distance)
          .add(new THREE.Vector2(screenPos.x, screenPos.y));
        
        // Calculate visibility based on position
        const edgeFade = 1 - Math.max(Math.abs(screenPos.x), Math.abs(screenPos.y));
        const opacity = element.opacity * light.intensity * Math.max(0, edgeFade);
        
        if (opacity < 0.01) continue;
        
        // Create flare element mesh
        const geometry = new THREE.PlaneGeometry(element.size, element.size);
        const material = new THREE.MeshBasicMaterial({
          color: element.color.clone().multiply(light.color),
          transparent: true,
          opacity,
          blending: THREE.AdditiveBlending,
          depthTest: false,
          depthWrite: false
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(pos.x, pos.y, -1);
        
        this.flareMeshes.push(mesh);
        this.flareGroup.add(mesh);
      }
    }
  }
  
  public dispose(): void {
    for (const mesh of this.flareMeshes) {
      mesh.geometry.dispose();
      (mesh.material as THREE.Material).dispose();
    }
    this.scene.remove(this.flareGroup);
  }
}

// ============================================
// LENS EFFECTS POST PROCESSOR
// ============================================

export class LensEffectsPostProcessor {
  private config: LensEffectsConfig;
  private material: THREE.ShaderMaterial;
  
  constructor(config: Partial<LensEffectsConfig> = {}) {
    this.config = {
      flareEnabled: true,
      flareIntensity: 1,
      flareElements: [],
      dirtEnabled: false,
      dirtTexture: null,
      dirtIntensity: 0.3,
      chromaticEnabled: true,
      chromaticStrength: 0.002,
      vignetteEnabled: true,
      vignetteIntensity: 0.5,
      vignetteSmoothness: 0.5,
      distortionEnabled: false,
      distortionStrength: 0.1,
      bokehEnabled: false,
      bokehAperture: 0.025,
      bokehFocus: 1.0,
      bokehMaxBlur: 0.01,
      anamorphicEnabled: false,
      anamorphicStretch: 1.5,
      anamorphicFlareIntensity: 0.5,
      ...config
    };
    
    this.material = this.createMaterial();
  }
  
  private createMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        tDepth: { value: null },
        tDirt: { value: this.config.dirtTexture },
        
        // Chromatic
        chromaticEnabled: { value: this.config.chromaticEnabled },
        chromaticStrength: { value: this.config.chromaticStrength },
        
        // Vignette
        vignetteEnabled: { value: this.config.vignetteEnabled },
        vignetteIntensity: { value: this.config.vignetteIntensity },
        vignetteSmoothness: { value: this.config.vignetteSmoothness },
        
        // Distortion
        distortionEnabled: { value: this.config.distortionEnabled },
        distortionStrength: { value: this.config.distortionStrength },
        
        // Dirt
        dirtEnabled: { value: this.config.dirtEnabled },
        dirtIntensity: { value: this.config.dirtIntensity },
        
        // Anamorphic
        anamorphicEnabled: { value: this.config.anamorphicEnabled },
        anamorphicStretch: { value: this.config.anamorphicStretch },
        anamorphicIntensity: { value: this.config.anamorphicFlareIntensity },
        
        resolution: { value: new THREE.Vector2(1920, 1080) }
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
        uniform sampler2D tDirt;
        
        uniform bool chromaticEnabled;
        uniform float chromaticStrength;
        
        uniform bool vignetteEnabled;
        uniform float vignetteIntensity;
        uniform float vignetteSmoothness;
        
        uniform bool distortionEnabled;
        uniform float distortionStrength;
        
        uniform bool dirtEnabled;
        uniform float dirtIntensity;
        
        uniform bool anamorphicEnabled;
        uniform float anamorphicStretch;
        uniform float anamorphicIntensity;
        
        uniform vec2 resolution;
        
        varying vec2 vUv;
        
        // Barrel/pincushion distortion
        vec2 distort(vec2 uv) {
          if (!distortionEnabled) return uv;
          
          vec2 centered = uv - 0.5;
          float r2 = dot(centered, centered);
          float distortion = 1.0 + distortionStrength * r2;
          return centered * distortion + 0.5;
        }
        
        // Chromatic aberration
        vec3 chromaticAberration(vec2 uv) {
          vec2 direction = (uv - 0.5) * chromaticStrength;
          
          float r = texture2D(tDiffuse, uv + direction).r;
          float g = texture2D(tDiffuse, uv).g;
          float b = texture2D(tDiffuse, uv - direction).b;
          
          return vec3(r, g, b);
        }
        
        // Vignette
        float vignette(vec2 uv) {
          vec2 centered = uv - 0.5;
          float dist = length(centered) * 2.0;
          float vig = smoothstep(1.0 - vignetteSmoothness, 1.0, dist);
          return 1.0 - vig * vignetteIntensity;
        }
        
        // Anamorphic horizontal blur for flares
        vec3 anamorphicFlare(vec2 uv) {
          if (!anamorphicEnabled) return vec3(0.0);
          
          vec3 flare = vec3(0.0);
          float totalWeight = 0.0;
          
          for (int i = -10; i <= 10; i++) {
            float offset = float(i) * 0.01 * anamorphicStretch;
            float weight = 1.0 - abs(float(i)) / 10.0;
            
            vec3 sample = texture2D(tDiffuse, uv + vec2(offset, 0.0)).rgb;
            float brightness = max(max(sample.r, sample.g), sample.b) - 0.8;
            brightness = max(0.0, brightness);
            
            flare += sample * brightness * weight;
            totalWeight += weight;
          }
          
          return flare / totalWeight * anamorphicIntensity;
        }
        
        void main() {
          vec2 uv = distort(vUv);
          
          // Check bounds
          if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            return;
          }
          
          // Get color
          vec3 color;
          if (chromaticEnabled) {
            color = chromaticAberration(uv);
          } else {
            color = texture2D(tDiffuse, uv).rgb;
          }
          
          // Add anamorphic flares
          color += anamorphicFlare(uv);
          
          // Apply lens dirt
          if (dirtEnabled) {
            vec3 dirt = texture2D(tDirt, vUv).rgb;
            float brightness = max(max(color.r, color.g), color.b);
            color += dirt * brightness * dirtIntensity;
          }
          
          // Apply vignette
          if (vignetteEnabled) {
            color *= vignette(vUv);
          }
          
          gl_FragColor = vec4(color, 1.0);
        }
      `
    });
  }
  
  /**
   * Get material for post-processing
   */
  public getMaterial(): THREE.ShaderMaterial {
    return this.material;
  }
  
  /**
   * Update config
   */
  public setConfig(config: Partial<LensEffectsConfig>): void {
    Object.assign(this.config, config);
    
    const u = this.material.uniforms;
    u.chromaticEnabled.value = this.config.chromaticEnabled;
    u.chromaticStrength.value = this.config.chromaticStrength;
    u.vignetteEnabled.value = this.config.vignetteEnabled;
    u.vignetteIntensity.value = this.config.vignetteIntensity;
    u.vignetteSmoothness.value = this.config.vignetteSmoothness;
    u.distortionEnabled.value = this.config.distortionEnabled;
    u.distortionStrength.value = this.config.distortionStrength;
    u.dirtEnabled.value = this.config.dirtEnabled;
    u.dirtIntensity.value = this.config.dirtIntensity;
    u.anamorphicEnabled.value = this.config.anamorphicEnabled;
    u.anamorphicStretch.value = this.config.anamorphicStretch;
    u.anamorphicIntensity.value = this.config.anamorphicFlareIntensity;
    
    if (config.dirtTexture !== undefined) {
      u.tDirt.value = config.dirtTexture;
    }
  }
  
  /**
   * Set resolution
   */
  public setResolution(width: number, height: number): void {
    this.material.uniforms.resolution.value.set(width, height);
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.material.dispose();
  }
}

// ============================================
// BOKEH DOF SYSTEM
// ============================================

export class BokehDOF {
  private material: THREE.ShaderMaterial;
  
  constructor() {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        tDepth: { value: null },
        focus: { value: 1.0 },
        aperture: { value: 0.025 },
        maxBlur: { value: 0.01 },
        nearClip: { value: 0.1 },
        farClip: { value: 100 },
        aspect: { value: 1.0 }
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
        uniform float focus;
        uniform float aperture;
        uniform float maxBlur;
        uniform float nearClip;
        uniform float farClip;
        uniform float aspect;
        
        varying vec2 vUv;
        
        float getDepth(vec2 uv) {
          float depth = texture2D(tDepth, uv).r;
          return nearClip * farClip / (farClip - depth * (farClip - nearClip));
        }
        
        void main() {
          float depth = getDepth(vUv);
          float blur = abs(depth - focus) * aperture;
          blur = min(blur, maxBlur);
          
          vec4 color = vec4(0.0);
          float totalWeight = 0.0;
          
          // Hexagonal bokeh pattern
          const int SAMPLES = 32;
          const float PI = 3.14159265;
          
          for (int i = 0; i < SAMPLES; i++) {
            float angle = float(i) * PI * 2.0 / float(SAMPLES);
            float radius = blur * (float(i) / float(SAMPLES));
            
            vec2 offset = vec2(cos(angle), sin(angle)) * radius;
            offset.x /= aspect;
            
            vec2 sampleUv = vUv + offset;
            
            if (sampleUv.x >= 0.0 && sampleUv.x <= 1.0 &&
                sampleUv.y >= 0.0 && sampleUv.y <= 1.0) {
              
              float sampleDepth = getDepth(sampleUv);
              float weight = sampleDepth >= depth ? 1.0 : 0.3; // Near objects don't blur background
              
              color += texture2D(tDiffuse, sampleUv) * weight;
              totalWeight += weight;
            }
          }
          
          gl_FragColor = color / totalWeight;
        }
      `
    });
  }
  
  public getMaterial(): THREE.ShaderMaterial {
    return this.material;
  }
  
  public setFocus(focus: number): void {
    this.material.uniforms.focus.value = focus;
  }
  
  public setAperture(aperture: number): void {
    this.material.uniforms.aperture.value = aperture;
  }
  
  public setMaxBlur(maxBlur: number): void {
    this.material.uniforms.maxBlur.value = maxBlur;
  }
  
  public dispose(): void {
    this.material.dispose();
  }
}

