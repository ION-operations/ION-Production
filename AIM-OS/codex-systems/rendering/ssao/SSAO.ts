/**
 * Screen Space Ambient Occlusion (SSAO)
 * Approximates ambient occlusion in screen space
 * 
 * Based on:
 * - Crytek's original SSAO (2007)
 * - Scalable Ambient Obscurance (McGuire 2012)
 * - HBAO+ concepts
 */

import * as THREE from 'three';

export interface SSAOConfig {
  kernelSize: number;        // Number of samples (16-64)
  radius: number;            // Sample radius in world units
  bias: number;              // Depth bias to prevent self-occlusion
  intensity: number;         // Occlusion intensity
  minDistance: number;       // Min distance for occlusion
  maxDistance: number;       // Max distance for occlusion
  
  // Blur
  blurEnabled: boolean;
  blurSize: number;          // Blur kernel size
  blurSharpness: number;     // Edge-preserving sharpness
  
  // Quality
  halfResolution: boolean;   // Render at half res for performance
}

export const DEFAULT_SSAO_CONFIG: SSAOConfig = {
  kernelSize: 32,
  radius: 0.5,
  bias: 0.025,
  intensity: 1.0,
  minDistance: 0.001,
  maxDistance: 0.3,
  blurEnabled: true,
  blurSize: 4,
  blurSharpness: 10,
  halfResolution: false
};

export class SSAO {
  private config: SSAOConfig;
  
  // Render targets
  private ssaoRenderTarget: THREE.WebGLRenderTarget;
  private blurRenderTarget: THREE.WebGLRenderTarget;
  
  // Materials
  private ssaoMaterial: THREE.ShaderMaterial;
  private blurMaterial: THREE.ShaderMaterial;
  private compositeMaterial: THREE.ShaderMaterial;
  
  // Kernel and noise
  private kernel: THREE.Vector3[] = [];
  private noiseTexture: THREE.DataTexture;
  
  // Geometry
  private quad: THREE.Mesh;
  private camera: THREE.OrthographicCamera;

  constructor(
    width: number,
    height: number,
    config: Partial<SSAOConfig> = {}
  ) {
    this.config = { ...DEFAULT_SSAO_CONFIG, ...config };
    
    const scale = this.config.halfResolution ? 0.5 : 1;
    const w = Math.floor(width * scale);
    const h = Math.floor(height * scale);
    
    this.ssaoRenderTarget = new THREE.WebGLRenderTarget(w, h, {
      format: THREE.RedFormat,
      type: THREE.FloatType
    });
    
    this.blurRenderTarget = new THREE.WebGLRenderTarget(w, h, {
      format: THREE.RedFormat,
      type: THREE.FloatType
    });
    
    this.generateKernel();
    this.noiseTexture = this.generateNoiseTexture();
    
    this.ssaoMaterial = this.createSSAOMaterial();
    this.blurMaterial = this.createBlurMaterial();
    this.compositeMaterial = this.createCompositeMaterial();
    
    this.quad = new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      this.ssaoMaterial
    );
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  }

  private generateKernel(): void {
    for (let i = 0; i < this.config.kernelSize; i++) {
      const sample = new THREE.Vector3(
        Math.random() * 2 - 1,
        Math.random() * 2 - 1,
        Math.random()
      );
      
      sample.normalize();
      sample.multiplyScalar(Math.random());
      
      // Accelerating interpolation - more samples closer to origin
      let scale = i / this.config.kernelSize;
      scale = 0.1 + scale * scale * 0.9;
      sample.multiplyScalar(scale);
      
      this.kernel.push(sample);
    }
  }

  private generateNoiseTexture(): THREE.DataTexture {
    const size = 4;
    const data = new Float32Array(size * size * 4);
    
    for (let i = 0; i < size * size; i++) {
      const stride = i * 4;
      // Random rotation vectors in tangent space
      data[stride] = Math.random() * 2 - 1;
      data[stride + 1] = Math.random() * 2 - 1;
      data[stride + 2] = 0;
      data[stride + 3] = 1;
    }
    
    const texture = new THREE.DataTexture(
      data, size, size, THREE.RGBAFormat, THREE.FloatType
    );
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.needsUpdate = true;
    
    return texture;
  }

  private createSSAOMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tDepth: { value: null },
        tNormal: { value: null },
        tNoise: { value: this.noiseTexture },
        uKernel: { value: this.kernel },
        uKernelSize: { value: this.config.kernelSize },
        uRadius: { value: this.config.radius },
        uBias: { value: this.config.bias },
        uIntensity: { value: this.config.intensity },
        uMinDistance: { value: this.config.minDistance },
        uMaxDistance: { value: this.config.maxDistance },
        uResolution: { value: new THREE.Vector2() },
        uNoiseScale: { value: new THREE.Vector2() },
        uProjection: { value: new THREE.Matrix4() },
        uInverseProjection: { value: new THREE.Matrix4() },
        uCameraNear: { value: 0.1 },
        uCameraFar: { value: 1000 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tDepth;
        uniform sampler2D tNormal;
        uniform sampler2D tNoise;
        uniform vec3 uKernel[64];
        uniform int uKernelSize;
        uniform float uRadius;
        uniform float uBias;
        uniform float uIntensity;
        uniform float uMinDistance;
        uniform float uMaxDistance;
        uniform vec2 uResolution;
        uniform vec2 uNoiseScale;
        uniform mat4 uProjection;
        uniform mat4 uInverseProjection;
        uniform float uCameraNear;
        uniform float uCameraFar;
        
        varying vec2 vUv;
        
        float getDepth(vec2 uv) {
          return texture2D(tDepth, uv).r;
        }
        
        vec3 getViewPosition(vec2 uv, float depth) {
          vec4 clipPos = vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
          vec4 viewPos = uInverseProjection * clipPos;
          return viewPos.xyz / viewPos.w;
        }
        
        vec3 getViewNormal(vec2 uv) {
          return texture2D(tNormal, uv).xyz * 2.0 - 1.0;
        }
        
        void main() {
          float depth = getDepth(vUv);
          
          if (depth >= 1.0) {
            gl_FragColor = vec4(1.0);
            return;
          }
          
          vec3 viewPos = getViewPosition(vUv, depth);
          vec3 viewNormal = getViewNormal(vUv);
          
          // Random rotation from noise texture
          vec3 randomVec = texture2D(tNoise, vUv * uNoiseScale).xyz * 2.0 - 1.0;
          
          // Gram-Schmidt to create TBN
          vec3 tangent = normalize(randomVec - viewNormal * dot(randomVec, viewNormal));
          vec3 bitangent = cross(viewNormal, tangent);
          mat3 TBN = mat3(tangent, bitangent, viewNormal);
          
          float occlusion = 0.0;
          
          for (int i = 0; i < 64; i++) {
            if (i >= uKernelSize) break;
            
            // Sample position in view space
            vec3 sampleDir = TBN * uKernel[i];
            vec3 samplePos = viewPos + sampleDir * uRadius;
            
            // Project to screen space
            vec4 offset = uProjection * vec4(samplePos, 1.0);
            offset.xy /= offset.w;
            offset.xy = offset.xy * 0.5 + 0.5;
            
            // Sample depth at that position
            float sampleDepth = getDepth(offset.xy);
            vec3 sampleViewPos = getViewPosition(offset.xy, sampleDepth);
            
            // Range check
            float rangeCheck = smoothstep(0.0, 1.0, uRadius / abs(viewPos.z - sampleViewPos.z));
            
            // Compare depths
            float diff = sampleViewPos.z - samplePos.z;
            
            if (diff > uBias && diff < uMaxDistance) {
              occlusion += rangeCheck;
            }
          }
          
          occlusion = 1.0 - (occlusion / float(uKernelSize));
          occlusion = pow(occlusion, uIntensity);
          
          gl_FragColor = vec4(occlusion);
        }
      `
    });
  }

  private createBlurMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tInput: { value: null },
        tDepth: { value: null },
        uDirection: { value: new THREE.Vector2(1, 0) },
        uResolution: { value: new THREE.Vector2() },
        uSharpness: { value: this.config.blurSharpness },
        uKernelSize: { value: this.config.blurSize }
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
        uniform sampler2D tDepth;
        uniform vec2 uDirection;
        uniform vec2 uResolution;
        uniform float uSharpness;
        uniform int uKernelSize;
        
        varying vec2 vUv;
        
        void main() {
          vec2 texelSize = 1.0 / uResolution;
          float centerDepth = texture2D(tDepth, vUv).r;
          
          float result = 0.0;
          float weightSum = 0.0;
          
          for (int i = -4; i <= 4; i++) {
            if (abs(i) > uKernelSize) continue;
            
            vec2 offset = uDirection * texelSize * float(i);
            vec2 sampleUv = vUv + offset;
            
            float sampleDepth = texture2D(tDepth, sampleUv).r;
            float sampleAO = texture2D(tInput, sampleUv).r;
            
            // Edge-preserving weight
            float depthDiff = abs(centerDepth - sampleDepth);
            float weight = exp(-depthDiff * uSharpness) * exp(-float(i * i) * 0.1);
            
            result += sampleAO * weight;
            weightSum += weight;
          }
          
          gl_FragColor = vec4(result / weightSum);
        }
      `
    });
  }

  private createCompositeMaterial(): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        tColor: { value: null },
        tSSAO: { value: null },
        uIntensity: { value: this.config.intensity }
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
        uniform sampler2D tSSAO;
        uniform float uIntensity;
        varying vec2 vUv;
        
        void main() {
          vec4 color = texture2D(tColor, vUv);
          float ao = texture2D(tSSAO, vUv).r;
          ao = mix(1.0, ao, uIntensity);
          gl_FragColor = vec4(color.rgb * ao, color.a);
        }
      `
    });
  }

  public render(
    renderer: THREE.WebGLRenderer,
    camera: THREE.PerspectiveCamera,
    depthTexture: THREE.Texture,
    normalTexture: THREE.Texture,
    colorTexture: THREE.Texture,
    outputTarget: THREE.WebGLRenderTarget | null
  ): void {
    const width = this.ssaoRenderTarget.width;
    const height = this.ssaoRenderTarget.height;
    
    // Update uniforms
    this.ssaoMaterial.uniforms.tDepth.value = depthTexture;
    this.ssaoMaterial.uniforms.tNormal.value = normalTexture;
    this.ssaoMaterial.uniforms.uResolution.value.set(width, height);
    this.ssaoMaterial.uniforms.uNoiseScale.value.set(width / 4, height / 4);
    this.ssaoMaterial.uniforms.uProjection.value.copy(camera.projectionMatrix);
    this.ssaoMaterial.uniforms.uInverseProjection.value.copy(camera.projectionMatrixInverse);
    this.ssaoMaterial.uniforms.uCameraNear.value = camera.near;
    this.ssaoMaterial.uniforms.uCameraFar.value = camera.far;
    
    // Render SSAO
    this.quad.material = this.ssaoMaterial;
    renderer.setRenderTarget(this.ssaoRenderTarget);
    renderer.render(this.quad, this.camera);
    
    // Blur pass
    if (this.config.blurEnabled) {
      // Horizontal
      this.blurMaterial.uniforms.tInput.value = this.ssaoRenderTarget.texture;
      this.blurMaterial.uniforms.tDepth.value = depthTexture;
      this.blurMaterial.uniforms.uDirection.value.set(1, 0);
      this.blurMaterial.uniforms.uResolution.value.set(width, height);
      this.quad.material = this.blurMaterial;
      renderer.setRenderTarget(this.blurRenderTarget);
      renderer.render(this.quad, this.camera);
      
      // Vertical
      this.blurMaterial.uniforms.tInput.value = this.blurRenderTarget.texture;
      this.blurMaterial.uniforms.uDirection.value.set(0, 1);
      renderer.setRenderTarget(this.ssaoRenderTarget);
      renderer.render(this.quad, this.camera);
    }
    
    // Composite
    this.compositeMaterial.uniforms.tColor.value = colorTexture;
    this.compositeMaterial.uniforms.tSSAO.value = this.ssaoRenderTarget.texture;
    this.quad.material = this.compositeMaterial;
    renderer.setRenderTarget(outputTarget);
    renderer.render(this.quad, this.camera);
  }

  public getSSAOTexture(): THREE.Texture {
    return this.ssaoRenderTarget.texture;
  }

  public setRadius(radius: number): void {
    this.config.radius = radius;
    this.ssaoMaterial.uniforms.uRadius.value = radius;
  }

  public setIntensity(intensity: number): void {
    this.config.intensity = intensity;
    this.ssaoMaterial.uniforms.uIntensity.value = intensity;
    this.compositeMaterial.uniforms.uIntensity.value = intensity;
  }

  public resize(width: number, height: number): void {
    const scale = this.config.halfResolution ? 0.5 : 1;
    const w = Math.floor(width * scale);
    const h = Math.floor(height * scale);
    
    this.ssaoRenderTarget.setSize(w, h);
    this.blurRenderTarget.setSize(w, h);
  }

  public dispose(): void {
    this.ssaoRenderTarget.dispose();
    this.blurRenderTarget.dispose();
    this.ssaoMaterial.dispose();
    this.blurMaterial.dispose();
    this.compositeMaterial.dispose();
    this.noiseTexture.dispose();
    this.quad.geometry.dispose();
  }
}

