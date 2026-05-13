/**
 * FFT-Based Ocean Simulation
 * Based on Tessendorf's "Simulating Ocean Water" (2001)
 * 
 * Features:
 * - Phillips spectrum for wave generation
 * - FFT for height and displacement calculation
 * - Choppy waves with displacement
 * - Foam/whitecaps from Jacobian
 */

import * as THREE from 'three';

export interface OceanConfig {
  // Grid
  resolution: number;        // FFT resolution (power of 2)
  size: number;              // Physical size in meters
  
  // Waves
  windSpeed: number;         // Wind speed in m/s
  windDirection: THREE.Vector2; // Wind direction
  waveAmplitude: number;     // Wave amplitude multiplier
  shortestWave: number;      // Minimum wavelength
  gravity: number;           // Gravity constant
  choppiness: number;        // Horizontal displacement (0-1)
  
  // Time
  timeScale: number;         // Animation speed
  
  // Foam
  foamThreshold: number;     // Jacobian threshold for foam
  foamDecay: number;         // How fast foam disappears
  
  // LOD
  lodLevels: number;         // Number of LOD levels
}

export const DEFAULT_OCEAN_CONFIG: OceanConfig = {
  resolution: 256,
  size: 1000,
  windSpeed: 20,
  windDirection: new THREE.Vector2(1, 0).normalize(),
  waveAmplitude: 0.0002,
  shortestWave: 0.001,
  gravity: 9.81,
  choppiness: 0.8,
  timeScale: 1,
  foamThreshold: -0.5,
  foamDecay: 0.95,
  lodLevels: 4
};

interface Complex {
  re: number;
  im: number;
}

export class FFTOcean {
  private config: OceanConfig;
  
  // FFT data
  private h0: Complex[] = [];           // Initial spectrum
  private ht: Complex[] = [];           // Height at time t
  private dx: Complex[] = [];           // Displacement X
  private dz: Complex[] = [];           // Displacement Z
  
  // Output
  private heightData: Float32Array;
  private displacementData: Float32Array;
  private normalData: Float32Array;
  private foamData: Float32Array;
  
  // Three.js
  public geometry!: THREE.BufferGeometry;
  public mesh!: THREE.Mesh;
  private material!: THREE.ShaderMaterial;
  
  // Textures for GPU
  public heightTexture!: THREE.DataTexture;
  public normalTexture!: THREE.DataTexture;
  public foamTexture!: THREE.DataTexture;
  
  private time: number = 0;

  constructor(config: Partial<OceanConfig> = {}) {
    this.config = { ...DEFAULT_OCEAN_CONFIG, ...config };
    
    const n = this.config.resolution;
    const n2 = n * n;
    
    this.heightData = new Float32Array(n2);
    this.displacementData = new Float32Array(n2 * 2);
    this.normalData = new Float32Array(n2 * 3);
    this.foamData = new Float32Array(n2);
    
    this.h0 = new Array(n2);
    this.ht = new Array(n2);
    this.dx = new Array(n2);
    this.dz = new Array(n2);
    
    for (let i = 0; i < n2; i++) {
      this.h0[i] = { re: 0, im: 0 };
      this.ht[i] = { re: 0, im: 0 };
      this.dx[i] = { re: 0, im: 0 };
      this.dz[i] = { re: 0, im: 0 };
    }
    
    this.initSpectrum();
    this.initTextures();
    this.createGeometry();
    this.createMaterial();
  }

  /**
   * Initialize Phillips spectrum
   */
  private initSpectrum(): void {
    const { resolution: n, size, windSpeed, windDirection, waveAmplitude, shortestWave, gravity } = this.config;
    
    const halfN = n / 2;
    const L = windSpeed * windSpeed / gravity;
    const l = shortestWave;
    
    for (let m = 0; m < n; m++) {
      for (let i = 0; i < n; i++) {
        const idx = m * n + i;
        
        // Wave vector
        const kx = (2 * Math.PI * (i - halfN)) / size;
        const kz = (2 * Math.PI * (m - halfN)) / size;
        const k = Math.sqrt(kx * kx + kz * kz);
        
        if (k < 0.00001) {
          this.h0[idx] = { re: 0, im: 0 };
          continue;
        }
        
        // Phillips spectrum
        const kDotW = (kx * windDirection.x + kz * windDirection.y) / k;
        const phillips = waveAmplitude * 
          Math.exp(-1 / (k * k * L * L)) / (k * k * k * k) *
          kDotW * kDotW *
          Math.exp(-k * k * l * l);
        
        // Complex Gaussian random
        const g1 = this.gaussianRandom();
        const g2 = this.gaussianRandom();
        
        const sqrt2 = Math.sqrt(2);
        const sqrtPhillips = Math.sqrt(phillips);
        
        this.h0[idx] = {
          re: (g1.re * sqrtPhillips) / sqrt2,
          im: (g1.im * sqrtPhillips) / sqrt2
        };
      }
    }
  }

  private gaussianRandom(): Complex {
    // Box-Muller transform
    const u1 = Math.random();
    const u2 = Math.random();
    const r = Math.sqrt(-2 * Math.log(Math.max(u1, 0.0001)));
    const theta = 2 * Math.PI * u2;
    return {
      re: r * Math.cos(theta),
      im: r * Math.sin(theta)
    };
  }

  /**
   * Update wave simulation
   */
  public update(dt: number): void {
    this.time += dt * this.config.timeScale;
    
    // Update spectrum at time t
    this.updateSpectrum();
    
    // Perform FFT to get spatial domain
    this.performFFT();
    
    // Calculate normals and foam
    this.calculateNormals();
    this.updateFoam(dt);
    
    // Update textures
    this.updateTextures();
    
    // Update geometry
    this.updateGeometry();
  }

  private updateSpectrum(): void {
    const { resolution: n, size, gravity, choppiness } = this.config;
    const halfN = n / 2;
    const t = this.time;
    
    for (let m = 0; m < n; m++) {
      for (let i = 0; i < n; i++) {
        const idx = m * n + i;
        
        // Wave vector
        const kx = (2 * Math.PI * (i - halfN)) / size;
        const kz = (2 * Math.PI * (m - halfN)) / size;
        const k = Math.sqrt(kx * kx + kz * kz);
        
        // Dispersion relation
        const omega = Math.sqrt(gravity * k);
        
        // Complex exponential
        const cosOmegaT = Math.cos(omega * t);
        const sinOmegaT = Math.sin(omega * t);
        
        // h0(k)
        const h0k = this.h0[idx];
        
        // h0(-k) - conjugate at opposite wave vector
        const negIdx = ((n - m) % n) * n + ((n - i) % n);
        const h0mk = this.h0[negIdx];
        
        // h(k, t) = h0(k) * exp(i*omega*t) + h0*(-k) * exp(-i*omega*t)
        this.ht[idx] = {
          re: (h0k.re * cosOmegaT - h0k.im * sinOmegaT) +
              (h0mk.re * cosOmegaT + h0mk.im * sinOmegaT),
          im: (h0k.re * sinOmegaT + h0k.im * cosOmegaT) +
              (-h0mk.re * sinOmegaT + h0mk.im * cosOmegaT)
        };
        
        // Displacement spectrum
        if (k > 0.00001) {
          const factor = choppiness / k;
          this.dx[idx] = {
            re: -this.ht[idx].im * kx * factor,
            im: this.ht[idx].re * kx * factor
          };
          this.dz[idx] = {
            re: -this.ht[idx].im * kz * factor,
            im: this.ht[idx].re * kz * factor
          };
        } else {
          this.dx[idx] = { re: 0, im: 0 };
          this.dz[idx] = { re: 0, im: 0 };
        }
      }
    }
  }

  /**
   * Perform 2D inverse FFT
   */
  private performFFT(): void {
    const n = this.config.resolution;
    
    // Height
    const htReal = new Float32Array(n * n);
    const htImag = new Float32Array(n * n);
    for (let i = 0; i < n * n; i++) {
      htReal[i] = this.ht[i].re;
      htImag[i] = this.ht[i].im;
    }
    this.fft2d(htReal, htImag, n, true);
    
    // Displacement X
    const dxReal = new Float32Array(n * n);
    const dxImag = new Float32Array(n * n);
    for (let i = 0; i < n * n; i++) {
      dxReal[i] = this.dx[i].re;
      dxImag[i] = this.dx[i].im;
    }
    this.fft2d(dxReal, dxImag, n, true);
    
    // Displacement Z
    const dzReal = new Float32Array(n * n);
    const dzImag = new Float32Array(n * n);
    for (let i = 0; i < n * n; i++) {
      dzReal[i] = this.dz[i].re;
      dzImag[i] = this.dz[i].im;
    }
    this.fft2d(dzReal, dzImag, n, true);
    
    // Copy results with sign correction for centering
    for (let m = 0; m < n; m++) {
      for (let i = 0; i < n; i++) {
        const idx = m * n + i;
        const sign = ((i + m) % 2 === 0) ? 1 : -1;
        
        this.heightData[idx] = htReal[idx] * sign;
        this.displacementData[idx * 2] = dxReal[idx] * sign;
        this.displacementData[idx * 2 + 1] = dzReal[idx] * sign;
      }
    }
  }

  /**
   * Cooley-Tukey FFT
   */
  private fft1d(real: Float32Array, imag: Float32Array, n: number, inverse: boolean): void {
    // Bit reversal
    for (let i = 0, j = 0; i < n; i++) {
      if (i < j) {
        [real[i], real[j]] = [real[j], real[i]];
        [imag[i], imag[j]] = [imag[j], imag[i]];
      }
      let m = n / 2;
      while (m >= 1 && j >= m) {
        j -= m;
        m /= 2;
      }
      j += m;
    }
    
    // FFT
    const sign = inverse ? 1 : -1;
    for (let mmax = 1; mmax < n; mmax *= 2) {
      const theta = sign * Math.PI / mmax;
      const wpr = Math.cos(theta);
      const wpi = Math.sin(theta);
      
      let wr = 1;
      let wi = 0;
      
      for (let m = 0; m < mmax; m++) {
        for (let i = m; i < n; i += mmax * 2) {
          const j = i + mmax;
          const tr = wr * real[j] - wi * imag[j];
          const ti = wr * imag[j] + wi * real[j];
          
          real[j] = real[i] - tr;
          imag[j] = imag[i] - ti;
          real[i] += tr;
          imag[i] += ti;
        }
        
        const wtemp = wr;
        wr = wr * wpr - wi * wpi;
        wi = wi * wpr + wtemp * wpi;
      }
    }
    
    // Normalize for inverse
    if (inverse) {
      for (let i = 0; i < n; i++) {
        real[i] /= n;
        imag[i] /= n;
      }
    }
  }

  private fft2d(real: Float32Array, imag: Float32Array, n: number, inverse: boolean): void {
    // Row FFTs
    const rowReal = new Float32Array(n);
    const rowImag = new Float32Array(n);
    
    for (let y = 0; y < n; y++) {
      for (let x = 0; x < n; x++) {
        rowReal[x] = real[y * n + x];
        rowImag[x] = imag[y * n + x];
      }
      this.fft1d(rowReal, rowImag, n, inverse);
      for (let x = 0; x < n; x++) {
        real[y * n + x] = rowReal[x];
        imag[y * n + x] = rowImag[x];
      }
    }
    
    // Column FFTs
    const colReal = new Float32Array(n);
    const colImag = new Float32Array(n);
    
    for (let x = 0; x < n; x++) {
      for (let y = 0; y < n; y++) {
        colReal[y] = real[y * n + x];
        colImag[y] = imag[y * n + x];
      }
      this.fft1d(colReal, colImag, n, inverse);
      for (let y = 0; y < n; y++) {
        real[y * n + x] = colReal[y];
        imag[y * n + x] = colImag[y];
      }
    }
  }

  private calculateNormals(): void {
    const n = this.config.resolution;
    const scale = this.config.size / n;
    
    for (let y = 0; y < n; y++) {
      for (let x = 0; x < n; x++) {
        const idx = y * n + x;
        
        // Sample neighboring heights
        const xm = (x - 1 + n) % n;
        const xp = (x + 1) % n;
        const ym = (y - 1 + n) % n;
        const yp = (y + 1) % n;
        
        const hL = this.heightData[y * n + xm];
        const hR = this.heightData[y * n + xp];
        const hD = this.heightData[ym * n + x];
        const hU = this.heightData[yp * n + x];
        
        // Calculate normal
        const nx = (hL - hR) / (2 * scale);
        const ny = 1;
        const nz = (hD - hU) / (2 * scale);
        
        const len = Math.sqrt(nx * nx + ny * ny + nz * nz);
        this.normalData[idx * 3] = nx / len;
        this.normalData[idx * 3 + 1] = ny / len;
        this.normalData[idx * 3 + 2] = nz / len;
      }
    }
  }

  private updateFoam(dt: number): void {
    const n = this.config.resolution;
    const scale = this.config.size / n;
    const { foamThreshold, foamDecay } = this.config;
    
    for (let y = 0; y < n; y++) {
      for (let x = 0; x < n; x++) {
        const idx = y * n + x;
        
        // Calculate Jacobian (measure of surface convergence)
        const xm = (x - 1 + n) % n;
        const xp = (x + 1) % n;
        const ym = (y - 1 + n) % n;
        const yp = (y + 1) % n;
        
        const dxdx = (this.displacementData[(y * n + xp) * 2] - 
                      this.displacementData[(y * n + xm) * 2]) / (2 * scale);
        const dzdz = (this.displacementData[(yp * n + x) * 2 + 1] - 
                      this.displacementData[(ym * n + x) * 2 + 1]) / (2 * scale);
        
        const jacobian = (1 + dxdx) * (1 + dzdz);
        
        // Generate foam where surface folds
        if (jacobian < foamThreshold) {
          this.foamData[idx] = Math.min(1, this.foamData[idx] + (foamThreshold - jacobian) * 0.5);
        }
        
        // Decay foam
        this.foamData[idx] *= foamDecay;
      }
    }
  }

  private initTextures(): void {
    const n = this.config.resolution;
    
    this.heightTexture = new THREE.DataTexture(
      this.heightData, n, n, THREE.RedFormat, THREE.FloatType
    );
    this.heightTexture.wrapS = THREE.RepeatWrapping;
    this.heightTexture.wrapT = THREE.RepeatWrapping;
    
    this.normalTexture = new THREE.DataTexture(
      this.normalData, n, n, THREE.RGBFormat, THREE.FloatType
    );
    this.normalTexture.wrapS = THREE.RepeatWrapping;
    this.normalTexture.wrapT = THREE.RepeatWrapping;
    
    this.foamTexture = new THREE.DataTexture(
      this.foamData, n, n, THREE.RedFormat, THREE.FloatType
    );
    this.foamTexture.wrapS = THREE.RepeatWrapping;
    this.foamTexture.wrapT = THREE.RepeatWrapping;
  }

  private updateTextures(): void {
    this.heightTexture.needsUpdate = true;
    this.normalTexture.needsUpdate = true;
    this.foamTexture.needsUpdate = true;
  }

  private createGeometry(): void {
    const n = this.config.resolution;
    const size = this.config.size;
    
    this.geometry = new THREE.PlaneGeometry(size, size, n - 1, n - 1);
    this.geometry.rotateX(-Math.PI / 2);
  }

  private updateGeometry(): void {
    const posAttr = this.geometry.getAttribute('position') as THREE.BufferAttribute;
    const n = this.config.resolution;
    
    for (let i = 0; i < n * n; i++) {
      posAttr.setY(i, this.heightData[i]);
      
      // Apply displacement
      const baseX = posAttr.getX(i);
      const baseZ = posAttr.getZ(i);
      posAttr.setX(i, baseX + this.displacementData[i * 2]);
      posAttr.setZ(i, baseZ + this.displacementData[i * 2 + 1]);
    }
    
    posAttr.needsUpdate = true;
    this.geometry.computeVertexNormals();
  }

  private createMaterial(): void {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uSunDirection: { value: new THREE.Vector3(0.5, 0.7, 0.5).normalize() },
        uWaterColor: { value: new THREE.Color(0.0, 0.2, 0.4) },
        uSkyColor: { value: new THREE.Color(0.5, 0.7, 1.0) },
        uFoamTexture: { value: this.foamTexture },
        uEnvMap: { value: null }
      },
      vertexShader: `
        varying vec3 vNormal;
        varying vec3 vWorldPosition;
        varying vec2 vUv;
        
        void main() {
          vNormal = normalMatrix * normal;
          vUv = uv;
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vWorldPosition = worldPos.xyz;
          gl_Position = projectionMatrix * viewMatrix * worldPos;
        }
      `,
      fragmentShader: `
        uniform float uTime;
        uniform vec3 uSunDirection;
        uniform vec3 uWaterColor;
        uniform vec3 uSkyColor;
        uniform sampler2D uFoamTexture;
        
        varying vec3 vNormal;
        varying vec3 vWorldPosition;
        varying vec2 vUv;
        
        void main() {
          vec3 normal = normalize(vNormal);
          vec3 viewDir = normalize(cameraPosition - vWorldPosition);
          vec3 lightDir = normalize(uSunDirection);
          
          // Fresnel
          float fresnel = pow(1.0 - max(dot(normal, viewDir), 0.0), 5.0);
          fresnel = 0.02 + 0.98 * fresnel;
          
          // Specular (sun reflection)
          vec3 halfDir = normalize(lightDir + viewDir);
          float spec = pow(max(dot(normal, halfDir), 0.0), 256.0);
          
          // Base color
          vec3 color = mix(uWaterColor, uSkyColor, fresnel);
          
          // Add specular
          color += vec3(1.0, 0.95, 0.8) * spec;
          
          // Foam
          float foam = texture2D(uFoamTexture, vUv).r;
          color = mix(color, vec3(1.0), foam * 0.8);
          
          // Subsurface scattering approximation
          float sss = pow(max(dot(viewDir, -lightDir), 0.0), 4.0) * 0.25;
          color += uWaterColor * sss;
          
          gl_FragColor = vec4(color, 0.95);
        }
      `,
      transparent: true,
      side: THREE.DoubleSide
    });
    
    this.mesh = new THREE.Mesh(this.geometry, this.material);
  }

  public setWindSpeed(speed: number): void {
    this.config.windSpeed = speed;
    this.initSpectrum();
  }

  public setWindDirection(dir: THREE.Vector2): void {
    this.config.windDirection.copy(dir).normalize();
    this.initSpectrum();
  }

  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
    this.heightTexture.dispose();
    this.normalTexture.dispose();
    this.foamTexture.dispose();
  }
}

