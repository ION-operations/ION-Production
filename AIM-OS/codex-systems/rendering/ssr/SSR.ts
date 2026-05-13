/**
 * Screen Space Reflections (SSR)
 * Ray marching in screen space for real-time reflections
 * 
 * Based on:
 * - Stochastic Screen-Space Reflections (Tomasz Stachowiak)
 * - Hi-Z Screen-Space Reflections
 */

import * as THREE from 'three';

export interface SSRConfig {
  maxSteps: number;          // Max ray march steps
  maxBinarySearchSteps: number; // Binary search refinement
  rayStep: number;           // Initial step size
  thickness: number;         // Surface thickness tolerance
  maxDistance: number;       // Max reflection distance
  jitter: number;            // Ray jitter for noise reduction
  fadeStart: number;         // Fade start distance (0-1)
  fadeEnd: number;           // Fade end distance (0-1)
  fresnelFalloff: number;    // Fresnel intensity falloff
  roughnessFade: number;     // Fade reflections for rough surfaces
}

export const DEFAULT_SSR_CONFIG: SSRConfig = {
  maxSteps: 64,
  maxBinarySearchSteps: 5,
  rayStep: 0.1,
  thickness: 0.5,
  maxDistance: 100,
  jitter: 0.1,
  fadeStart: 0.8,
  fadeEnd: 1.0,
  fresnelFalloff: 5.0,
  roughnessFade: 0.5
};

export class SSR {
  private config: SSRConfig;
  
  private ssrRenderTarget: THREE.WebGLRenderTarget;
  private blurRenderTarget: THREE.WebGLRenderTarget;
  
  private ssrMaterial: THREE.ShaderMaterial;
  private blurMaterial: THREE.ShaderMaterial;
  private compositeMaterial: THREE.ShaderMaterial;
  
  private quad: THREE.Mesh;
  private camera: THREE.OrthographicCamera;

  constructor(
    width: number,
    height: number,
    config: Partial<SSRConfig> = {}
  ) {
    this.config = { ...DEFAULT_SSR_CONFIG, ...config };
    
    this.ssrRenderTarget = new THREE.WebGLRenderTarget(width, height, {
      format: THREE.RGBAFormat,
      type: THREE.HalfFloatType
    });
    
    this.blurRenderTarget = new THREE.WebGLRenderTarget(width, height, {
      format: THREE.RGBAFormat,
      type: THREE.HalfFloatType
    });
    
    this.ssrMaterial = this.createSSRMaterial();
    this.blurMaterial = this.createBlurMaterial();
    this.compositeMaterial = this.createCompositeMaterial();
    
    this.quad = new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      this.ssrMaterial
    );
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  }

  private createSSRMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tColor: { value: null },
        tDepth: { value: null },
        tNormal: { value: null },
        tRoughness: { value: null },
        uResolution: { value: new THREE.Vector2() },
        uProjection: { value: new THREE.Matrix4() },
        uInverseProjection: { value: new THREE.Matrix4() },
        uView: { value: new THREE.Matrix4() },
        uInverseView: { value: new THREE.Matrix4() },
        uCameraNear: { value: 0.1 },
        uCameraFar: { value: 1000 },
        uMaxSteps: { value: this.config.maxSteps },
        uMaxBinarySearchSteps: { value: this.config.maxBinarySearchSteps },
        uRayStep: { value: this.config.rayStep },
        uThickness: { value: this.config.thickness },
        uMaxDistance: { value: this.config.maxDistance },
        uJitter: { value: this.config.jitter },
        uFadeStart: { value: this.config.fadeStart },
        uFadeEnd: { value: this.config.fadeEnd },
        uFresnelFalloff: { value: this.config.fresnelFalloff },
        uRoughnessFade: { value: this.config.roughnessFade },
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
        uniform sampler2D tColor;
        uniform sampler2D tDepth;
        uniform sampler2D tNormal;
        uniform sampler2D tRoughness;
        uniform vec2 uResolution;
        uniform mat4 uProjection;
        uniform mat4 uInverseProjection;
        uniform mat4 uView;
        uniform mat4 uInverseView;
        uniform float uCameraNear;
        uniform float uCameraFar;
        uniform int uMaxSteps;
        uniform int uMaxBinarySearchSteps;
        uniform float uRayStep;
        uniform float uThickness;
        uniform float uMaxDistance;
        uniform float uJitter;
        uniform float uFadeStart;
        uniform float uFadeEnd;
        uniform float uFresnelFalloff;
        uniform float uRoughnessFade;
        uniform float uTime;
        
        varying vec2 vUv;
        
        float rand(vec2 co) {
          return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
        }
        
        float getDepth(vec2 uv) {
          return texture2D(tDepth, uv).r;
        }
        
        float linearizeDepth(float depth) {
          return (2.0 * uCameraNear * uCameraFar) / 
                 (uCameraFar + uCameraNear - depth * (uCameraFar - uCameraNear));
        }
        
        vec3 getViewPosition(vec2 uv, float depth) {
          vec4 clipPos = vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
          vec4 viewPos = uInverseProjection * clipPos;
          return viewPos.xyz / viewPos.w;
        }
        
        vec3 getViewNormal(vec2 uv) {
          vec3 normal = texture2D(tNormal, uv).xyz * 2.0 - 1.0;
          return normalize((uView * vec4(normal, 0.0)).xyz);
        }
        
        vec3 projectToScreen(vec3 viewPos) {
          vec4 clipPos = uProjection * vec4(viewPos, 1.0);
          clipPos.xyz /= clipPos.w;
          return vec3(clipPos.xy * 0.5 + 0.5, clipPos.z * 0.5 + 0.5);
        }
        
        bool rayMarch(vec3 origin, vec3 dir, out vec2 hitUV, out float hitDepth) {
          vec3 rayPos = origin;
          float stepSize = uRayStep;
          
          // Jitter starting position
          float jitter = rand(vUv + uTime) * uJitter;
          rayPos += dir * stepSize * jitter;
          
          for (int i = 0; i < 128; i++) {
            if (i >= uMaxSteps) break;
            
            rayPos += dir * stepSize;
            
            // Check if ray is too far
            float rayDepth = -rayPos.z;
            if (rayDepth > uMaxDistance) {
              return false;
            }
            
            // Project to screen
            vec3 screenPos = projectToScreen(rayPos);
            
            // Check screen bounds
            if (screenPos.x < 0.0 || screenPos.x > 1.0 ||
                screenPos.y < 0.0 || screenPos.y > 1.0) {
              return false;
            }
            
            // Sample depth at this position
            float sampledDepth = getDepth(screenPos.xy);
            float sampledViewZ = linearizeDepth(sampledDepth);
            
            // Check for intersection
            float diff = rayDepth - sampledViewZ;
            
            if (diff > 0.0 && diff < uThickness) {
              // Binary search refinement
              vec3 refinedPos = rayPos;
              float refinedStep = stepSize * 0.5;
              
              for (int j = 0; j < 10; j++) {
                if (j >= uMaxBinarySearchSteps) break;
                
                refinedPos -= dir * refinedStep * sign(diff);
                
                vec3 refinedScreen = projectToScreen(refinedPos);
                float refinedSampledDepth = getDepth(refinedScreen.xy);
                float refinedSampledViewZ = linearizeDepth(refinedSampledDepth);
                float refinedRayDepth = -refinedPos.z;
                
                diff = refinedRayDepth - refinedSampledViewZ;
                refinedStep *= 0.5;
              }
              
              hitUV = projectToScreen(refinedPos).xy;
              hitDepth = -refinedPos.z;
              return true;
            }
            
            // Adaptive step size
            stepSize *= 1.1;
          }
          
          return false;
        }
        
        void main() {
          float depth = getDepth(vUv);
          
          if (depth >= 1.0) {
            gl_FragColor = vec4(0.0);
            return;
          }
          
          // Get view space position and normal
          vec3 viewPos = getViewPosition(vUv, depth);
          vec3 viewNormal = getViewNormal(vUv);
          
          // Get roughness
          float roughness = texture2D(tRoughness, vUv).r;
          
          // Skip very rough surfaces
          if (roughness > uRoughnessFade) {
            gl_FragColor = vec4(0.0);
            return;
          }
          
          // Calculate reflection direction
          vec3 viewDir = normalize(viewPos);
          vec3 reflectDir = reflect(viewDir, viewNormal);
          
          // Ray march
          vec2 hitUV;
          float hitDepth;
          
          if (rayMarch(viewPos, reflectDir, hitUV, hitDepth)) {
            // Sample reflected color
            vec4 reflectedColor = texture2D(tColor, hitUV);
            
            // Fresnel
            float fresnel = pow(1.0 - max(dot(-viewDir, viewNormal), 0.0), uFresnelFalloff);
            
            // Edge fade
            vec2 edgeFade = smoothstep(0.0, 0.1, hitUV) * (1.0 - smoothstep(0.9, 1.0, hitUV));
            float fade = edgeFade.x * edgeFade.y;
            
            // Distance fade
            float distanceFade = 1.0 - smoothstep(uFadeStart * uMaxDistance, uFadeEnd * uMaxDistance, hitDepth);
            
            // Roughness fade
            float roughFade = 1.0 - (roughness / uRoughnessFade);
            
            // Combine
            float alpha = fresnel * fade * distanceFade * roughFade;
            
            gl_FragColor = vec4(reflectedColor.rgb, alpha);
          } else {
            gl_FragColor = vec4(0.0);
          }
        }
      `
    });
  }

  private createBlurMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        tRoughness: { value: null },
        uDirection: { value: new THREE.Vector2(1, 0) },
        uResolution: { value: new THREE.Vector2() }
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
        uniform sampler2D tRoughness;
        uniform vec2 uDirection;
        uniform vec2 uResolution;
        varying vec2 vUv;
        
        void main() {
          float roughness = texture2D(tRoughness, vUv).r;
          int kernelSize = int(roughness * 8.0) + 1;
          
          vec2 texelSize = 1.0 / uResolution;
          vec4 result = vec4(0.0);
          float weightSum = 0.0;
          
          for (int i = -8; i <= 8; i++) {
            if (abs(i) > kernelSize) continue;
            
            vec2 offset = uDirection * texelSize * float(i);
            vec4 sample = texture2D(tInput, vUv + offset);
            float weight = exp(-float(i * i) * 0.05);
            
            result += sample * weight;
            weightSum += weight;
          }
          
          gl_FragColor = result / weightSum;
        }
      `
    });
  }

  private createCompositeMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tColor: { value: null },
        tSSR: { value: null },
        uIntensity: { value: 1.0 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tColor;
        uniform sampler2D tSSR;
        uniform float uIntensity;
        varying vec2 vUv;
        
        void main() {
          vec4 color = texture2D(tColor, vUv);
          vec4 ssr = texture2D(tSSR, vUv);
          
          vec3 result = mix(color.rgb, ssr.rgb, ssr.a * uIntensity);
          gl_FragColor = vec4(result, color.a);
        }
      `
    });
  }

  public render(
    renderer: THREE.WebGLRenderer,
    camera: THREE.PerspectiveCamera,
    colorTexture: THREE.Texture,
    depthTexture: THREE.Texture,
    normalTexture: THREE.Texture,
    roughnessTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null,
    time: number = 0
  ): void {
    const width = this.ssrRenderTarget.width;
    const height = this.ssrRenderTarget.height;
    
    // Update SSR uniforms
    this.ssrMaterial.uniforms.tColor.value = colorTexture;
    this.ssrMaterial.uniforms.tDepth.value = depthTexture;
    this.ssrMaterial.uniforms.tNormal.value = normalTexture;
    this.ssrMaterial.uniforms.tRoughness.value = roughnessTexture;
    this.ssrMaterial.uniforms.uResolution.value.set(width, height);
    this.ssrMaterial.uniforms.uProjection.value.copy(camera.projectionMatrix);
    this.ssrMaterial.uniforms.uInverseProjection.value.copy(camera.projectionMatrixInverse);
    this.ssrMaterial.uniforms.uView.value.copy(camera.matrixWorldInverse);
    this.ssrMaterial.uniforms.uInverseView.value.copy(camera.matrixWorld);
    this.ssrMaterial.uniforms.uCameraNear.value = camera.near;
    this.ssrMaterial.uniforms.uCameraFar.value = camera.far;
    this.ssrMaterial.uniforms.uTime.value = time;
    
    // Render SSR
    this.quad.material = this.ssrMaterial;
    renderer.setRenderTarget(this.ssrRenderTarget);
    renderer.render(this.quad, this.camera);
    
    // Roughness-based blur
    this.blurMaterial.uniforms.tInput.value = this.ssrRenderTarget.texture;
    this.blurMaterial.uniforms.tRoughness.value = roughnessTexture;
    this.blurMaterial.uniforms.uResolution.value.set(width, height);
    
    // Horizontal
    this.blurMaterial.uniforms.uDirection.value.set(1, 0);
    this.quad.material = this.blurMaterial;
    renderer.setRenderTarget(this.blurRenderTarget);
    renderer.render(this.quad, this.camera);
    
    // Vertical
    this.blurMaterial.uniforms.tInput.value = this.blurRenderTarget.texture;
    this.blurMaterial.uniforms.uDirection.value.set(0, 1);
    renderer.setRenderTarget(this.ssrRenderTarget);
    renderer.render(this.quad, this.camera);
    
    // Composite
    this.compositeMaterial.uniforms.tColor.value = colorTexture;
    this.compositeMaterial.uniforms.tSSR.value = this.ssrRenderTarget.texture;
    this.quad.material = this.compositeMaterial;
    renderer.setRenderTarget(outputTarget);
    renderer.render(this.quad, this.camera);
  }

  public getSSRTexture(): THREE.Texture {
    return this.ssrRenderTarget.texture;
  }

  public resize(width: number, height: number): void {
    this.ssrRenderTarget.setSize(width, height);
    this.blurRenderTarget.setSize(width, height);
  }

  public dispose(): void {
    this.ssrRenderTarget.dispose();
    this.blurRenderTarget.dispose();
    this.ssrMaterial.dispose();
    this.blurMaterial.dispose();
    this.compositeMaterial.dispose();
    this.quad.geometry.dispose();
  }
}

