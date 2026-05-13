/**
 * Volumetric Cloud Rendering System
 * Real-time raymarched clouds with 3D noise and atmospheric scattering
 * 
 * Based on:
 * - "Real-Time Volumetric Cloudscapes" (Horizon Zero Dawn, GDC 2015)
 * - "Physically Based Sky, Atmosphere and Cloud Rendering" (Schneider)
 */

import * as THREE from 'three';

export interface CloudConfig {
  // Domain
  cloudLayerBottom: number;      // meters above ground
  cloudLayerTop: number;         // meters above ground
  cloudScale: number;            // World scale of noise
  
  // Density
  baseDensity: number;           // Base cloud density (0-1)
  detailDensity: number;         // Detail noise contribution
  coverageMin: number;           // Minimum coverage (0-1)
  coverageMax: number;           // Maximum coverage (0-1)
  
  // Shape
  shapeNoiseScale: number;       // Primary shape noise scale
  detailNoiseScale: number;      // Detail noise scale
  erosionStrength: number;       // Edge erosion amount
  
  // Animation
  windDirection: THREE.Vector3;  // Wind direction
  windSpeed: number;             // m/s
  detailWindMultiplier: number;  // Detail moves faster
  
  // Lighting
  sunDirection: THREE.Vector3;
  sunColor: THREE.Color;
  ambientColor: THREE.Color;
  scatteringCoefficient: number;
  absorptionCoefficient: number;
  phaseG: number;                // Henyey-Greenstein phase parameter
  
  // Raymarching
  maxSteps: number;              // Primary ray steps
  lightSteps: number;            // Light sampling steps
  jitterStrength: number;        // Temporal jitter
  
  // Optimizations
  useLowResBuffer: boolean;      // Render at lower res
  bufferScale: number;           // 0.5 = half resolution
  temporalBlending: number;      // Blend with previous frame
}

export const DEFAULT_CLOUD_CONFIG: CloudConfig = {
  cloudLayerBottom: 1500,
  cloudLayerTop: 4000,
  cloudScale: 0.0002,
  
  baseDensity: 0.5,
  detailDensity: 0.3,
  coverageMin: 0.0,
  coverageMax: 0.8,
  
  shapeNoiseScale: 0.0003,
  detailNoiseScale: 0.002,
  erosionStrength: 0.3,
  
  windDirection: new THREE.Vector3(1, 0, 0.2).normalize(),
  windSpeed: 20,
  detailWindMultiplier: 3,
  
  sunDirection: new THREE.Vector3(0.5, 0.7, 0.5).normalize(),
  sunColor: new THREE.Color(1.0, 0.95, 0.8),
  ambientColor: new THREE.Color(0.4, 0.5, 0.7),
  scatteringCoefficient: 0.05,
  absorptionCoefficient: 0.02,
  phaseG: 0.8,
  
  maxSteps: 64,
  lightSteps: 6,
  jitterStrength: 1.0,
  
  useLowResBuffer: true,
  bufferScale: 0.5,
  temporalBlending: 0.95
};

export class VolumetricClouds {
  private config: CloudConfig;
  private material!: THREE.ShaderMaterial;
  public mesh!: THREE.Mesh;
  
  // Noise textures
  private shapeNoiseTexture!: THREE.Data3DTexture;
  private detailNoiseTexture!: THREE.Data3DTexture;
  private weatherTexture!: THREE.DataTexture;
  private blueNoiseTexture!: THREE.DataTexture;
  
  private time: number = 0;
  private frameIndex: number = 0;

  constructor(config: Partial<CloudConfig> = {}) {
    this.config = { ...DEFAULT_CLOUD_CONFIG, ...config };
    this.generateNoiseTextures();
    this.createMaterial();
    this.createMesh();
  }

  private generateNoiseTextures(): void {
    // 3D Shape Noise (Worley + Perlin)
    const shapeSize = 128;
    const shapeData = new Float32Array(shapeSize * shapeSize * shapeSize * 4);
    
    for (let z = 0; z < shapeSize; z++) {
      for (let y = 0; y < shapeSize; y++) {
        for (let x = 0; x < shapeSize; x++) {
          const idx = (z * shapeSize * shapeSize + y * shapeSize + x) * 4;
          
          const px = x / shapeSize;
          const py = y / shapeSize;
          const pz = z / shapeSize;
          
          // Layered FBM with different frequencies
          const perlin = this.fbm3D(px * 4, py * 4, pz * 4, 4);
          const worley1 = 1.0 - this.worley3D(px * 2, py * 2, pz * 2);
          const worley2 = 1.0 - this.worley3D(px * 4, py * 4, pz * 4);
          const worley3 = 1.0 - this.worley3D(px * 8, py * 8, pz * 8);
          
          // Perlin-Worley combination
          const shape = this.remap(perlin, worley1 * 0.5, 1.0, 0.0, 1.0);
          
          shapeData[idx] = shape;
          shapeData[idx + 1] = worley1;
          shapeData[idx + 2] = worley2;
          shapeData[idx + 3] = worley3;
        }
      }
    }
    
    this.shapeNoiseTexture = new THREE.Data3DTexture(
      shapeData, shapeSize, shapeSize, shapeSize
    );
    this.shapeNoiseTexture.format = THREE.RGBAFormat;
    this.shapeNoiseTexture.type = THREE.FloatType;
    this.shapeNoiseTexture.wrapS = THREE.RepeatWrapping;
    this.shapeNoiseTexture.wrapT = THREE.RepeatWrapping;
    this.shapeNoiseTexture.wrapR = THREE.RepeatWrapping;
    this.shapeNoiseTexture.minFilter = THREE.LinearFilter;
    this.shapeNoiseTexture.magFilter = THREE.LinearFilter;
    this.shapeNoiseTexture.needsUpdate = true;
    
    // 3D Detail Noise
    const detailSize = 32;
    const detailData = new Float32Array(detailSize * detailSize * detailSize * 4);
    
    for (let z = 0; z < detailSize; z++) {
      for (let y = 0; y < detailSize; y++) {
        for (let x = 0; x < detailSize; x++) {
          const idx = (z * detailSize * detailSize + y * detailSize + x) * 4;
          
          const px = x / detailSize;
          const py = y / detailSize;
          const pz = z / detailSize;
          
          const w1 = 1.0 - this.worley3D(px * 2, py * 2, pz * 2);
          const w2 = 1.0 - this.worley3D(px * 4, py * 4, pz * 4);
          const w3 = 1.0 - this.worley3D(px * 8, py * 8, pz * 8);
          
          detailData[idx] = w1 * 0.625 + w2 * 0.25 + w3 * 0.125;
          detailData[idx + 1] = w1;
          detailData[idx + 2] = w2;
          detailData[idx + 3] = w3;
        }
      }
    }
    
    this.detailNoiseTexture = new THREE.Data3DTexture(
      detailData, detailSize, detailSize, detailSize
    );
    this.detailNoiseTexture.format = THREE.RGBAFormat;
    this.detailNoiseTexture.type = THREE.FloatType;
    this.detailNoiseTexture.wrapS = THREE.RepeatWrapping;
    this.detailNoiseTexture.wrapT = THREE.RepeatWrapping;
    this.detailNoiseTexture.wrapR = THREE.RepeatWrapping;
    this.detailNoiseTexture.minFilter = THREE.LinearFilter;
    this.detailNoiseTexture.magFilter = THREE.LinearFilter;
    this.detailNoiseTexture.needsUpdate = true;
    
    // 2D Weather/Coverage Texture
    const weatherSize = 512;
    const weatherData = new Float32Array(weatherSize * weatherSize * 4);
    
    for (let y = 0; y < weatherSize; y++) {
      for (let x = 0; x < weatherSize; x++) {
        const idx = (y * weatherSize + x) * 4;
        const px = x / weatherSize;
        const py = y / weatherSize;
        
        // Coverage map (where clouds form)
        const coverage = this.fbm2D(px * 3, py * 3, 5);
        // Type (cumulus vs stratus)
        const cloudType = this.fbm2D(px * 2 + 100, py * 2, 4);
        // Height gradient
        const heightGradient = this.fbm2D(px * 4, py * 4 + 50, 3);
        
        weatherData[idx] = coverage * 0.5 + 0.5;
        weatherData[idx + 1] = cloudType * 0.5 + 0.5;
        weatherData[idx + 2] = heightGradient * 0.5 + 0.5;
        weatherData[idx + 3] = 1.0;
      }
    }
    
    this.weatherTexture = new THREE.DataTexture(
      weatherData, weatherSize, weatherSize, THREE.RGBAFormat, THREE.FloatType
    );
    this.weatherTexture.wrapS = THREE.RepeatWrapping;
    this.weatherTexture.wrapT = THREE.RepeatWrapping;
    this.weatherTexture.minFilter = THREE.LinearFilter;
    this.weatherTexture.magFilter = THREE.LinearFilter;
    this.weatherTexture.needsUpdate = true;
    
    // Blue noise for jittering
    const blueSize = 128;
    const blueData = new Float32Array(blueSize * blueSize * 4);
    for (let i = 0; i < blueSize * blueSize; i++) {
      blueData[i * 4] = Math.random();
      blueData[i * 4 + 1] = Math.random();
      blueData[i * 4 + 2] = Math.random();
      blueData[i * 4 + 3] = 1.0;
    }
    
    this.blueNoiseTexture = new THREE.DataTexture(
      blueData, blueSize, blueSize, THREE.RGBAFormat, THREE.FloatType
    );
    this.blueNoiseTexture.wrapS = THREE.RepeatWrapping;
    this.blueNoiseTexture.wrapT = THREE.RepeatWrapping;
    this.blueNoiseTexture.needsUpdate = true;
  }

  // Noise helper functions
  private hash(n: number): number {
    return (Math.sin(n) * 43758.5453123) % 1;
  }
  
  private noise3D(x: number, y: number, z: number): number {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    const iz = Math.floor(z);
    const fx = x - ix;
    const fy = y - iy;
    const fz = z - iz;
    
    const ux = fx * fx * (3 - 2 * fx);
    const uy = fy * fy * (3 - 2 * fy);
    const uz = fz * fz * (3 - 2 * fz);
    
    const a = this.hash(ix + iy * 157 + iz * 113);
    const b = this.hash(ix + 1 + iy * 157 + iz * 113);
    const c = this.hash(ix + (iy + 1) * 157 + iz * 113);
    const d = this.hash(ix + 1 + (iy + 1) * 157 + iz * 113);
    const e = this.hash(ix + iy * 157 + (iz + 1) * 113);
    const f = this.hash(ix + 1 + iy * 157 + (iz + 1) * 113);
    const g = this.hash(ix + (iy + 1) * 157 + (iz + 1) * 113);
    const h = this.hash(ix + 1 + (iy + 1) * 157 + (iz + 1) * 113);
    
    return this.lerp(
      this.lerp(this.lerp(a, b, ux), this.lerp(c, d, ux), uy),
      this.lerp(this.lerp(e, f, ux), this.lerp(g, h, ux), uy),
      uz
    );
  }
  
  private fbm3D(x: number, y: number, z: number, octaves: number): number {
    let value = 0;
    let amplitude = 0.5;
    let frequency = 1;
    
    for (let i = 0; i < octaves; i++) {
      value += amplitude * this.noise3D(x * frequency, y * frequency, z * frequency);
      amplitude *= 0.5;
      frequency *= 2;
    }
    
    return value;
  }
  
  private fbm2D(x: number, y: number, octaves: number): number {
    return this.fbm3D(x, y, 0, octaves);
  }
  
  private worley3D(x: number, y: number, z: number): number {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    const iz = Math.floor(z);
    
    let minDist = 1.0;
    
    for (let dz = -1; dz <= 1; dz++) {
      for (let dy = -1; dy <= 1; dy++) {
        for (let dx = -1; dx <= 1; dx++) {
          const cx = ix + dx;
          const cy = iy + dy;
          const cz = iz + dz;
          
          const h = this.hash(cx + cy * 157 + cz * 113);
          const px = cx + h;
          const py = cy + this.hash(h * 1000);
          const pz = cz + this.hash(h * 2000);
          
          const dist = Math.sqrt(
            (x - px) * (x - px) +
            (y - py) * (y - py) +
            (z - pz) * (z - pz)
          );
          
          minDist = Math.min(minDist, dist);
        }
      }
    }
    
    return minDist;
  }
  
  private lerp(a: number, b: number, t: number): number {
    return a + t * (b - a);
  }
  
  private remap(value: number, low1: number, high1: number, low2: number, high2: number): number {
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1);
  }

  private createMaterial(): void {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uFrameIndex: { value: 0 },
        uResolution: { value: new THREE.Vector2(1920, 1080) },
        uCameraPosition: { value: new THREE.Vector3() },
        uInverseProjection: { value: new THREE.Matrix4() },
        uInverseView: { value: new THREE.Matrix4() },
        
        uShapeNoise: { value: this.shapeNoiseTexture },
        uDetailNoise: { value: this.detailNoiseTexture },
        uWeatherMap: { value: this.weatherTexture },
        uBlueNoise: { value: this.blueNoiseTexture },
        
        uCloudLayerBottom: { value: this.config.cloudLayerBottom },
        uCloudLayerTop: { value: this.config.cloudLayerTop },
        uCloudScale: { value: this.config.cloudScale },
        
        uBaseDensity: { value: this.config.baseDensity },
        uDetailDensity: { value: this.config.detailDensity },
        uCoverageMin: { value: this.config.coverageMin },
        uCoverageMax: { value: this.config.coverageMax },
        
        uShapeNoiseScale: { value: this.config.shapeNoiseScale },
        uDetailNoiseScale: { value: this.config.detailNoiseScale },
        uErosionStrength: { value: this.config.erosionStrength },
        
        uWindDirection: { value: this.config.windDirection },
        uWindSpeed: { value: this.config.windSpeed },
        
        uSunDirection: { value: this.config.sunDirection },
        uSunColor: { value: this.config.sunColor },
        uAmbientColor: { value: this.config.ambientColor },
        uScattering: { value: this.config.scatteringCoefficient },
        uAbsorption: { value: this.config.absorptionCoefficient },
        uPhaseG: { value: this.config.phaseG },
        
        uMaxSteps: { value: this.config.maxSteps },
        uLightSteps: { value: this.config.lightSteps },
        uJitterStrength: { value: this.config.jitterStrength }
      },
      vertexShader: this.getVertexShader(),
      fragmentShader: this.getFragmentShader(),
      transparent: true,
      depthWrite: false,
      depthTest: false
    });
  }

  private createMesh(): void {
    // Fullscreen quad
    const geometry = new THREE.PlaneGeometry(2, 2);
    this.mesh = new THREE.Mesh(geometry, this.material);
    this.mesh.frustumCulled = false;
  }

  public update(dt: number, camera: THREE.Camera): void {
    this.time += dt;
    this.frameIndex++;
    
    this.material.uniforms.uTime.value = this.time;
    this.material.uniforms.uFrameIndex.value = this.frameIndex;
    this.material.uniforms.uCameraPosition.value.copy(camera.position);
    
    if (camera instanceof THREE.PerspectiveCamera) {
      this.material.uniforms.uInverseProjection.value.copy(camera.projectionMatrixInverse);
      this.material.uniforms.uInverseView.value.copy(camera.matrixWorld);
    }
  }

  public setSunDirection(dir: THREE.Vector3): void {
    this.config.sunDirection.copy(dir).normalize();
    this.material.uniforms.uSunDirection.value.copy(this.config.sunDirection);
  }

  public setCoverage(min: number, max: number): void {
    this.config.coverageMin = min;
    this.config.coverageMax = max;
    this.material.uniforms.uCoverageMin.value = min;
    this.material.uniforms.uCoverageMax.value = max;
  }

  private getVertexShader(): string {
    return `
      varying vec2 vUv;
      
      void main() {
        vUv = uv;
        gl_Position = vec4(position.xy, 0.0, 1.0);
      }
    `;
  }

  private getFragmentShader(): string {
    return `
      precision highp float;
      precision highp sampler3D;
      
      uniform float uTime;
      uniform int uFrameIndex;
      uniform vec2 uResolution;
      uniform vec3 uCameraPosition;
      uniform mat4 uInverseProjection;
      uniform mat4 uInverseView;
      
      uniform sampler3D uShapeNoise;
      uniform sampler3D uDetailNoise;
      uniform sampler2D uWeatherMap;
      uniform sampler2D uBlueNoise;
      
      uniform float uCloudLayerBottom;
      uniform float uCloudLayerTop;
      uniform float uCloudScale;
      
      uniform float uBaseDensity;
      uniform float uDetailDensity;
      uniform float uCoverageMin;
      uniform float uCoverageMax;
      
      uniform float uShapeNoiseScale;
      uniform float uDetailNoiseScale;
      uniform float uErosionStrength;
      
      uniform vec3 uWindDirection;
      uniform float uWindSpeed;
      
      uniform vec3 uSunDirection;
      uniform vec3 uSunColor;
      uniform vec3 uAmbientColor;
      uniform float uScattering;
      uniform float uAbsorption;
      uniform float uPhaseG;
      
      uniform int uMaxSteps;
      uniform int uLightSteps;
      uniform float uJitterStrength;
      
      varying vec2 vUv;
      
      #define PI 3.14159265359
      #define EARTH_RADIUS 6371000.0
      
      // Remap utility
      float remap(float value, float low1, float high1, float low2, float high2) {
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1);
      }
      
      // Henyey-Greenstein phase function
      float henyeyGreenstein(float cosTheta, float g) {
        float g2 = g * g;
        return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * cosTheta, 1.5));
      }
      
      // Dual-lobe phase for silver lining
      float dualLobePhase(float cosTheta) {
        return mix(henyeyGreenstein(cosTheta, uPhaseG), henyeyGreenstein(cosTheta, -0.5), 0.3);
      }
      
      // Height gradient for cloud shape
      float getHeightFraction(vec3 pos) {
        return clamp((pos.y - uCloudLayerBottom) / (uCloudLayerTop - uCloudLayerBottom), 0.0, 1.0);
      }
      
      // Sample cloud density at position
      float sampleCloudDensity(vec3 pos, bool cheap) {
        float heightFraction = getHeightFraction(pos);
        
        // Wind offset
        vec3 windOffset = uWindDirection * uWindSpeed * uTime * 0.001;
        vec3 samplePos = pos * uCloudScale + windOffset;
        
        // Weather map (coverage)
        vec2 weatherUV = pos.xz * 0.00005;
        vec4 weather = texture2D(uWeatherMap, weatherUV);
        float coverage = mix(uCoverageMin, uCoverageMax, weather.r);
        
        // Shape noise (low frequency)
        vec4 shapeNoise = texture(uShapeNoise, samplePos * uShapeNoiseScale);
        float shapeFBM = shapeNoise.g * 0.625 + shapeNoise.b * 0.25 + shapeNoise.a * 0.125;
        
        // Base cloud shape
        float baseCloud = remap(shapeNoise.r, shapeFBM - 1.0, 1.0, 0.0, 1.0);
        
        // Height gradient (rounded cumulus shape)
        float heightGradient = smoothstep(0.0, 0.2, heightFraction) * 
                               smoothstep(1.0, 0.7, heightFraction);
        
        // Apply coverage and height
        float density = baseCloud * heightGradient;
        density = remap(density, 1.0 - coverage, 1.0, 0.0, 1.0);
        density *= coverage;
        
        if (cheap || density <= 0.0) {
          return max(0.0, density * uBaseDensity);
        }
        
        // Detail noise (high frequency erosion)
        vec3 detailSamplePos = samplePos * uDetailNoiseScale + 
                               windOffset * 3.0; // Detail moves faster
        vec4 detailNoise = texture(uDetailNoise, detailSamplePos);
        float detailFBM = detailNoise.r * 0.625 + detailNoise.g * 0.25 + detailNoise.b * 0.125;
        
        // Erode edges with detail
        float detailModifier = mix(detailFBM, 1.0 - detailFBM, clamp(heightFraction * 2.0, 0.0, 1.0));
        density = remap(density, detailModifier * uErosionStrength, 1.0, 0.0, 1.0);
        
        return max(0.0, density * uBaseDensity);
      }
      
      // Light marching (towards sun)
      float lightMarch(vec3 pos) {
        vec3 lightDir = normalize(uSunDirection);
        float stepSize = (uCloudLayerTop - uCloudLayerBottom) / float(uLightSteps);
        
        float totalDensity = 0.0;
        
        for (int i = 0; i < 6; i++) {
          if (i >= uLightSteps) break;
          
          pos += lightDir * stepSize;
          
          if (pos.y > uCloudLayerTop) break;
          
          totalDensity += sampleCloudDensity(pos, true) * stepSize;
        }
        
        float transmittance = exp(-totalDensity * (uScattering + uAbsorption));
        return transmittance;
      }
      
      // Ray-sphere intersection for cloud layers
      vec2 rayCloudLayerIntersection(vec3 rayOrigin, vec3 rayDir, float layerHeight) {
        // Simplified: treat as horizontal planes
        float t = (layerHeight - rayOrigin.y) / rayDir.y;
        return vec2(t, t > 0.0 ? 1.0 : 0.0);
      }
      
      void main() {
        // Reconstruct ray from screen position
        vec2 ndc = vUv * 2.0 - 1.0;
        vec4 clipPos = vec4(ndc, 1.0, 1.0);
        vec4 viewPos = uInverseProjection * clipPos;
        viewPos /= viewPos.w;
        vec3 rayDir = normalize((uInverseView * vec4(viewPos.xyz, 0.0)).xyz);
        
        // Blue noise jitter
        vec2 blueNoiseUV = gl_FragCoord.xy / 128.0;
        float jitter = texture2D(uBlueNoise, blueNoiseUV).r;
        jitter = fract(jitter + float(uFrameIndex) * 0.618033988749);
        
        // Find entry/exit points in cloud layer
        vec2 tBottom = rayCloudLayerIntersection(uCameraPosition, rayDir, uCloudLayerBottom);
        vec2 tTop = rayCloudLayerIntersection(uCameraPosition, rayDir, uCloudLayerTop);
        
        float tStart = max(0.0, min(tBottom.x, tTop.x));
        float tEnd = max(tBottom.x, tTop.x);
        
        if (tStart >= tEnd || tEnd < 0.0) {
          gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
          return;
        }
        
        // Raymarching
        float stepSize = (tEnd - tStart) / float(uMaxSteps);
        float t = tStart + jitter * stepSize * uJitterStrength;
        
        vec3 accumulatedColor = vec3(0.0);
        float transmittance = 1.0;
        
        float cosTheta = dot(rayDir, uSunDirection);
        float phase = dualLobePhase(cosTheta);
        
        for (int i = 0; i < 128; i++) {
          if (i >= uMaxSteps) break;
          if (transmittance < 0.01) break;
          if (t > tEnd) break;
          
          vec3 pos = uCameraPosition + rayDir * t;
          
          float density = sampleCloudDensity(pos, false);
          
          if (density > 0.001) {
            // Light contribution
            float lightTransmittance = lightMarch(pos);
            
            // Beer-Powder approximation for self-shadowing
            float powder = 1.0 - exp(-density * stepSize * 2.0);
            float beerPowder = exp(-density * stepSize) * (1.0 - powder * 0.5);
            
            // Scattering
            vec3 sunLight = uSunColor * lightTransmittance * phase;
            vec3 ambient = uAmbientColor * 0.25;
            vec3 light = sunLight + ambient;
            
            // Accumulate
            float sampleTransmittance = exp(-density * stepSize * (uScattering + uAbsorption));
            accumulatedColor += light * transmittance * (1.0 - sampleTransmittance) * beerPowder;
            transmittance *= sampleTransmittance;
          }
          
          t += stepSize;
        }
        
        float alpha = 1.0 - transmittance;
        gl_FragColor = vec4(accumulatedColor, alpha);
      }
    `;
  }

  public dispose(): void {
    this.material.dispose();
    this.mesh.geometry.dispose();
    this.shapeNoiseTexture.dispose();
    this.detailNoiseTexture.dispose();
    this.weatherTexture.dispose();
    this.blueNoiseTexture.dispose();
  }
}

