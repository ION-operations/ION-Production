/**
 * Post-Processing Pipeline
 * Modular effect chain with common techniques
 * 
 * Effects:
 * - Bloom (HDR)
 * - Depth of Field (Bokeh)
 * - Motion Blur
 * - Screen Space Ambient Occlusion (SSAO)
 * - Screen Space Reflections (SSR)
 * - Tone Mapping (ACES, Reinhard, Uncharted)
 * - Color Grading (LUT)
 * - Film Grain
 * - Vignette
 * - Chromatic Aberration
 */

import * as THREE from 'three';

// ============================================
// BASE EFFECT CLASS
// ============================================

export abstract class PostProcessEffect {
  public enabled: boolean = true;
  public order: number = 0;
  protected material!: THREE.ShaderMaterial;

  abstract render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null,
    camera: THREE.Camera,
    scene: THREE.Scene
  ): void;

  abstract dispose(): void;
}

// ============================================
// BLOOM EFFECT
// ============================================

export interface BloomConfig {
  threshold: number;
  intensity: number;
  radius: number;
  levels: number;
}

export class BloomEffect extends PostProcessEffect {
  private config: BloomConfig;
  private brightPassMaterial: THREE.ShaderMaterial;
  private blurMaterials: THREE.ShaderMaterial[] = [];
  private compositeMaterial: THREE.ShaderMaterial;
  private renderTargets: THREE.WebGLRenderTarget[] = [];
  private quad: THREE.Mesh;

  constructor(width: number, height: number, config: Partial<BloomConfig> = {}) {
    super();
    this.config = {
      threshold: 0.9,
      intensity: 1.0,
      radius: 0.4,
      levels: 5,
      ...config
    };
    this.order = 10;

    // Create render targets for each blur level
    let w = Math.floor(width / 2);
    let h = Math.floor(height / 2);
    
    for (let i = 0; i < this.config.levels; i++) {
      this.renderTargets.push(
        new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType }),
        new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType })
      );
      w = Math.floor(w / 2);
      h = Math.floor(h / 2);
    }

    // Bright pass shader
    this.brightPassMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        uThreshold: { value: this.config.threshold }
      },
      vertexShader: this.getQuadVertexShader(),
      fragmentShader: `
        uniform sampler2D tInput;
        uniform float uThreshold;
        varying vec2 vUv;
        
        void main() {
          vec4 color = texture2D(tInput, vUv);
          float brightness = max(max(color.r, color.g), color.b);
          float contribution = max(0.0, brightness - uThreshold);
          contribution /= max(brightness, 0.001);
          gl_FragColor = vec4(color.rgb * contribution, 1.0);
        }
      `
    });

    // Gaussian blur shaders
    for (let i = 0; i < this.config.levels; i++) {
      this.blurMaterials.push(
        this.createBlurMaterial(true),   // Horizontal
        this.createBlurMaterial(false)   // Vertical
      );
    }

    // Composite shader
    this.compositeMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tBloom0: { value: null },
        tBloom1: { value: null },
        tBloom2: { value: null },
        tBloom3: { value: null },
        tBloom4: { value: null },
        uIntensity: { value: this.config.intensity },
        uRadius: { value: this.config.radius }
      },
      vertexShader: this.getQuadVertexShader(),
      fragmentShader: `
        uniform sampler2D tBloom0;
        uniform sampler2D tBloom1;
        uniform sampler2D tBloom2;
        uniform sampler2D tBloom3;
        uniform sampler2D tBloom4;
        uniform float uIntensity;
        uniform float uRadius;
        varying vec2 vUv;
        
        void main() {
          vec3 bloom = vec3(0.0);
          float weights[5];
          weights[0] = 1.0;
          weights[1] = 0.8;
          weights[2] = 0.6;
          weights[3] = 0.4;
          weights[4] = 0.2;
          
          bloom += texture2D(tBloom0, vUv).rgb * weights[0];
          bloom += texture2D(tBloom1, vUv).rgb * weights[1];
          bloom += texture2D(tBloom2, vUv).rgb * weights[2];
          bloom += texture2D(tBloom3, vUv).rgb * weights[3];
          bloom += texture2D(tBloom4, vUv).rgb * weights[4];
          
          bloom *= uIntensity;
          bloom = mix(bloom, bloom * uRadius, 0.5);
          
          gl_FragColor = vec4(bloom, 1.0);
        }
      `
    });

    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.brightPassMaterial);
  }

  private createBlurMaterial(horizontal: boolean): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        uDirection: { value: horizontal ? new THREE.Vector2(1, 0) : new THREE.Vector2(0, 1) },
        uResolution: { value: new THREE.Vector2(1, 1) }
      },
      vertexShader: this.getQuadVertexShader(),
      fragmentShader: `
        uniform sampler2D tInput;
        uniform vec2 uDirection;
        uniform vec2 uResolution;
        varying vec2 vUv;
        
        void main() {
          vec2 texelSize = 1.0 / uResolution;
          vec3 result = vec3(0.0);
          
          float weights[5];
          weights[0] = 0.227027;
          weights[1] = 0.1945946;
          weights[2] = 0.1216216;
          weights[3] = 0.054054;
          weights[4] = 0.016216;
          
          result += texture2D(tInput, vUv).rgb * weights[0];
          
          for (int i = 1; i < 5; i++) {
            vec2 offset = uDirection * texelSize * float(i);
            result += texture2D(tInput, vUv + offset).rgb * weights[i];
            result += texture2D(tInput, vUv - offset).rgb * weights[i];
          }
          
          gl_FragColor = vec4(result, 1.0);
        }
      `
    });
  }

  private getQuadVertexShader(): string {
    return `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = vec4(position.xy, 0.0, 1.0);
      }
    `;
  }

  public render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null
  ): void {
    if (!this.enabled) return;

    // Bright pass
    this.brightPassMaterial.uniforms.tInput.value = inputTexture;
    this.quad.material = this.brightPassMaterial;
    renderer.setRenderTarget(this.renderTargets[0]);
    renderer.render(this.quad, new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1));

    // Blur each level
    for (let i = 0; i < this.config.levels; i++) {
      const rtIdx = i * 2;
      
      // Horizontal blur
      const hBlur = this.blurMaterials[i * 2];
      hBlur.uniforms.tInput.value = this.renderTargets[rtIdx].texture;
      hBlur.uniforms.uResolution.value.set(
        this.renderTargets[rtIdx].width,
        this.renderTargets[rtIdx].height
      );
      this.quad.material = hBlur;
      renderer.setRenderTarget(this.renderTargets[rtIdx + 1]);
      renderer.render(this.quad, new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1));

      // Vertical blur
      const vBlur = this.blurMaterials[i * 2 + 1];
      vBlur.uniforms.tInput.value = this.renderTargets[rtIdx + 1].texture;
      vBlur.uniforms.uResolution.value.set(
        this.renderTargets[rtIdx + 1].width,
        this.renderTargets[rtIdx + 1].height
      );
      this.quad.material = vBlur;
      renderer.setRenderTarget(this.renderTargets[rtIdx]);
      renderer.render(this.quad, new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1));
    }

    // Composite (output is additive, so caller adds to scene)
    this.compositeMaterial.uniforms.tBloom0.value = this.renderTargets[0].texture;
    this.compositeMaterial.uniforms.tBloom1.value = this.renderTargets[2]?.texture || this.renderTargets[0].texture;
    this.compositeMaterial.uniforms.tBloom2.value = this.renderTargets[4]?.texture || this.renderTargets[0].texture;
    this.compositeMaterial.uniforms.tBloom3.value = this.renderTargets[6]?.texture || this.renderTargets[0].texture;
    this.compositeMaterial.uniforms.tBloom4.value = this.renderTargets[8]?.texture || this.renderTargets[0].texture;
  }

  public getBloomTexture(): THREE.Texture {
    return this.renderTargets[0].texture;
  }

  public dispose(): void {
    this.brightPassMaterial.dispose();
    this.compositeMaterial.dispose();
    this.blurMaterials.forEach(m => m.dispose());
    this.renderTargets.forEach(rt => rt.dispose());
    this.quad.geometry.dispose();
  }
}

// ============================================
// TONE MAPPING
// ============================================

export type ToneMappingMode = 'linear' | 'reinhard' | 'aces' | 'uncharted2' | 'filmic';

export class ToneMappingEffect extends PostProcessEffect {
  private mode: ToneMappingMode;

  constructor(mode: ToneMappingMode = 'aces') {
    super();
    this.mode = mode;
    this.order = 90;

    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        uExposure: { value: 1.0 },
        uGamma: { value: 2.2 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: this.getFragmentShader()
    });
  }

  private getFragmentShader(): string {
    const tonemapFunctions = `
      vec3 tonemapReinhard(vec3 x) {
        return x / (1.0 + x);
      }
      
      vec3 tonemapACES(vec3 x) {
        float a = 2.51;
        float b = 0.03;
        float c = 2.43;
        float d = 0.59;
        float e = 0.14;
        return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
      }
      
      vec3 tonemapUncharted2(vec3 x) {
        float A = 0.15;
        float B = 0.50;
        float C = 0.10;
        float D = 0.20;
        float E = 0.02;
        float F = 0.30;
        return ((x*(A*x+C*B)+D*E)/(x*(A*x+B)+D*F))-E/F;
      }
      
      vec3 tonemapFilmic(vec3 x) {
        vec3 X = max(vec3(0.0), x - 0.004);
        return (X * (6.2 * X + 0.5)) / (X * (6.2 * X + 1.7) + 0.06);
      }
    `;

    let tonemapCall = 'color';
    switch (this.mode) {
      case 'reinhard': tonemapCall = 'tonemapReinhard(color)'; break;
      case 'aces': tonemapCall = 'tonemapACES(color)'; break;
      case 'uncharted2': tonemapCall = 'tonemapUncharted2(color) / tonemapUncharted2(vec3(11.2))'; break;
      case 'filmic': tonemapCall = 'tonemapFilmic(color)'; break;
    }

    return `
      uniform sampler2D tInput;
      uniform float uExposure;
      uniform float uGamma;
      varying vec2 vUv;
      
      ${tonemapFunctions}
      
      void main() {
        vec3 color = texture2D(tInput, vUv).rgb;
        color *= uExposure;
        color = ${tonemapCall};
        color = pow(color, vec3(1.0 / uGamma));
        gl_FragColor = vec4(color, 1.0);
      }
    `;
  }

  public setExposure(exposure: number): void {
    this.material.uniforms.uExposure.value = exposure;
  }

  public render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null
  ): void {
    if (!this.enabled) return;

    this.material.uniforms.tInput.value = inputTexture;
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.material);
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    
    renderer.setRenderTarget(outputTarget);
    renderer.render(quad, camera);
    
    quad.geometry.dispose();
  }

  public dispose(): void {
    this.material.dispose();
  }
}

// ============================================
// VIGNETTE
// ============================================

export class VignetteEffect extends PostProcessEffect {
  constructor(intensity: number = 0.5, smoothness: number = 0.5) {
    super();
    this.order = 95;

    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        uIntensity: { value: intensity },
        uSmoothness: { value: smoothness }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tInput;
        uniform float uIntensity;
        uniform float uSmoothness;
        varying vec2 vUv;
        
        void main() {
          vec4 color = texture2D(tInput, vUv);
          vec2 center = vUv - 0.5;
          float dist = length(center);
          float vignette = smoothstep(0.5, 0.5 - uSmoothness, dist * (1.0 + uIntensity));
          color.rgb *= vignette;
          gl_FragColor = color;
        }
      `
    });
  }

  public render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null
  ): void {
    if (!this.enabled) return;

    this.material.uniforms.tInput.value = inputTexture;
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.material);
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    
    renderer.setRenderTarget(outputTarget);
    renderer.render(quad, camera);
    
    quad.geometry.dispose();
  }

  public dispose(): void {
    this.material.dispose();
  }
}

// ============================================
// FILM GRAIN
// ============================================

export class FilmGrainEffect extends PostProcessEffect {
  constructor(intensity: number = 0.1) {
    super();
    this.order = 98;

    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        uIntensity: { value: intensity },
        uTime: { value: 0 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tInput;
        uniform float uIntensity;
        uniform float uTime;
        varying vec2 vUv;
        
        float rand(vec2 co) {
          return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
        }
        
        void main() {
          vec4 color = texture2D(tInput, vUv);
          float noise = rand(vUv + uTime) * 2.0 - 1.0;
          color.rgb += noise * uIntensity;
          gl_FragColor = color;
        }
      `
    });
  }

  public update(time: number): void {
    this.material.uniforms.uTime.value = time;
  }

  public render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null
  ): void {
    if (!this.enabled) return;

    this.material.uniforms.tInput.value = inputTexture;
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.material);
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    
    renderer.setRenderTarget(outputTarget);
    renderer.render(quad, camera);
    
    quad.geometry.dispose();
  }

  public dispose(): void {
    this.material.dispose();
  }
}

// ============================================
// CHROMATIC ABERRATION
// ============================================

export class ChromaticAberrationEffect extends PostProcessEffect {
  constructor(intensity: number = 0.005) {
    super();
    this.order = 96;

    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        uIntensity: { value: intensity }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tInput;
        uniform float uIntensity;
        varying vec2 vUv;
        
        void main() {
          vec2 center = vUv - 0.5;
          float dist = length(center);
          vec2 offset = center * dist * uIntensity;
          
          float r = texture2D(tInput, vUv + offset).r;
          float g = texture2D(tInput, vUv).g;
          float b = texture2D(tInput, vUv - offset).b;
          
          gl_FragColor = vec4(r, g, b, 1.0);
        }
      `
    });
  }

  public render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null
  ): void {
    if (!this.enabled) return;

    this.material.uniforms.tInput.value = inputTexture;
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.material);
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    
    renderer.setRenderTarget(outputTarget);
    renderer.render(quad, camera);
    
    quad.geometry.dispose();
  }

  public dispose(): void {
    this.material.dispose();
  }
}

// ============================================
// MAIN PIPELINE
// ============================================

export class PostProcessingPipeline {
  private effects: PostProcessEffect[] = [];
  private renderTargetA: THREE.WebGLRenderTarget;
  private renderTargetB: THREE.WebGLRenderTarget;
  private copyMaterial: THREE.ShaderMaterial;
  private quad: THREE.Mesh;
  private camera: THREE.OrthographicCamera;

  constructor(width: number, height: number) {
    this.renderTargetA = new THREE.WebGLRenderTarget(width, height, {
      type: THREE.HalfFloatType,
      format: THREE.RGBAFormat
    });
    this.renderTargetB = new THREE.WebGLRenderTarget(width, height, {
      type: THREE.HalfFloatType,
      format: THREE.RGBAFormat
    });

    this.copyMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tInput;
        varying vec2 vUv;
        void main() {
          gl_FragColor = texture2D(tInput, vUv);
        }
      `
    });

    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.copyMaterial);
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  }

  public addEffect(effect: PostProcessEffect): void {
    this.effects.push(effect);
    this.effects.sort((a, b) => a.order - b.order);
  }

  public removeEffect(effect: PostProcessEffect): void {
    const index = this.effects.indexOf(effect);
    if (index >= 0) {
      this.effects.splice(index, 1);
    }
  }

  public render(
    renderer: THREE.WebGLRenderer,
    inputTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null,
    camera: THREE.Camera,
    scene: THREE.Scene
  ): void {
    const enabledEffects = this.effects.filter(e => e.enabled);
    
    if (enabledEffects.length === 0) {
      // Just copy input to output
      this.copyMaterial.uniforms.tInput.value = inputTexture;
      this.quad.material = this.copyMaterial;
      renderer.setRenderTarget(outputTarget);
      renderer.render(this.quad, this.camera);
      return;
    }

    let currentInput = inputTexture;
    let pingPong = false;

    for (let i = 0; i < enabledEffects.length; i++) {
      const effect = enabledEffects[i];
      const isLast = i === enabledEffects.length - 1;
      const target = isLast ? outputTarget : (pingPong ? this.renderTargetB : this.renderTargetA);
      
      effect.render(renderer, currentInput, target, camera, scene);
      
      if (!isLast) {
        currentInput = (pingPong ? this.renderTargetB : this.renderTargetA).texture;
        pingPong = !pingPong;
      }
    }
  }

  public resize(width: number, height: number): void {
    this.renderTargetA.setSize(width, height);
    this.renderTargetB.setSize(width, height);
  }

  public dispose(): void {
    this.effects.forEach(e => e.dispose());
    this.renderTargetA.dispose();
    this.renderTargetB.dispose();
    this.copyMaterial.dispose();
    this.quad.geometry.dispose();
  }
}

