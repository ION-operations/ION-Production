/**
 * Volumetric Fire & Explosion System
 * Combines particle emission with volumetric raymarching
 * 
 * Based on:
 * - GPU Gems 3: Real-Time Simulation and Rendering of 3D Fluids
 * - Noise-based fire shader techniques (FBM, domain warping)
 */

import * as THREE from 'three';

export interface FireConfig {
  // Emission
  baseRadius: number;         // Base fire radius
  height: number;             // Fire height
  intensity: number;          // Overall intensity (0-1)
  turbulence: number;         // Turbulence amount
  speed: number;              // Animation speed
  
  // Colors (HDR values allowed)
  coreColor: THREE.Color;     // Hot core (white-yellow)
  midColor: THREE.Color;      // Middle (orange)
  outerColor: THREE.Color;    // Outer edge (red-black)
  
  // Noise
  noiseScale: number;         // Noise frequency
  noiseOctaves: number;       // FBM octaves (2-6)
  noiseLacunarity: number;    // Frequency multiplier
  noiseGain: number;          // Amplitude multiplier
  
  // Shape
  taper: number;              // How much fire tapers at top (0-1)
  flickerSpeed: number;       // Flicker animation speed
  flickerAmount: number;      // Flicker intensity
  
  // Rendering
  opacity: number;            // Base opacity
  bloomThreshold: number;     // Bloom emission threshold
  softEdge: number;           // Edge softness
}

export const DEFAULT_FIRE_CONFIG: FireConfig = {
  baseRadius: 0.5,
  height: 2.0,
  intensity: 1.0,
  turbulence: 0.5,
  speed: 1.0,
  
  coreColor: new THREE.Color(1.0, 0.9, 0.5),
  midColor: new THREE.Color(1.0, 0.4, 0.0),
  outerColor: new THREE.Color(0.5, 0.0, 0.0),
  
  noiseScale: 3.0,
  noiseOctaves: 4,
  noiseLacunarity: 2.0,
  noiseGain: 0.5,
  
  taper: 0.7,
  flickerSpeed: 8.0,
  flickerAmount: 0.2,
  
  opacity: 1.0,
  bloomThreshold: 0.8,
  softEdge: 0.3
};

export class FireSystem {
  private config: FireConfig;
  public mesh!: THREE.Mesh;
  private material!: THREE.ShaderMaterial;
  private time: number = 0;

  constructor(config: Partial<FireConfig> = {}) {
    this.config = { ...DEFAULT_FIRE_CONFIG, ...config };
    this.createMesh();
  }

  private createMesh(): void {
    // Billboard quad or volumetric box
    const geometry = new THREE.PlaneGeometry(
      this.config.baseRadius * 3,
      this.config.height * 1.5
    );
    
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uBaseRadius: { value: this.config.baseRadius },
        uHeight: { value: this.config.height },
        uIntensity: { value: this.config.intensity },
        uTurbulence: { value: this.config.turbulence },
        uSpeed: { value: this.config.speed },
        uCoreColor: { value: this.config.coreColor },
        uMidColor: { value: this.config.midColor },
        uOuterColor: { value: this.config.outerColor },
        uNoiseScale: { value: this.config.noiseScale },
        uNoiseOctaves: { value: this.config.noiseOctaves },
        uNoiseLacunarity: { value: this.config.noiseLacunarity },
        uNoiseGain: { value: this.config.noiseGain },
        uTaper: { value: this.config.taper },
        uFlickerSpeed: { value: this.config.flickerSpeed },
        uFlickerAmount: { value: this.config.flickerAmount },
        uOpacity: { value: this.config.opacity },
        uBloomThreshold: { value: this.config.bloomThreshold },
        uSoftEdge: { value: this.config.softEdge }
      },
      vertexShader: this.getVertexShader(),
      fragmentShader: this.getFragmentShader(),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });

    this.mesh = new THREE.Mesh(geometry, this.material);
  }

  public update(dt: number): void {
    this.time += dt;
    this.material.uniforms.uTime.value = this.time;
  }

  public setIntensity(intensity: number): void {
    this.config.intensity = intensity;
    this.material.uniforms.uIntensity.value = intensity;
  }

  private getVertexShader(): string {
    return `
      varying vec2 vUv;
      varying vec3 vWorldPos;
      
      void main() {
        vUv = uv;
        vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;
  }

  private getFragmentShader(): string {
    return `
      uniform float uTime;
      uniform float uBaseRadius;
      uniform float uHeight;
      uniform float uIntensity;
      uniform float uTurbulence;
      uniform float uSpeed;
      uniform vec3 uCoreColor;
      uniform vec3 uMidColor;
      uniform vec3 uOuterColor;
      uniform float uNoiseScale;
      uniform float uNoiseOctaves;
      uniform float uNoiseLacunarity;
      uniform float uNoiseGain;
      uniform float uTaper;
      uniform float uFlickerSpeed;
      uniform float uFlickerAmount;
      uniform float uOpacity;
      uniform float uBloomThreshold;
      uniform float uSoftEdge;
      
      varying vec2 vUv;
      varying vec3 vWorldPos;
      
      // Simplex noise functions
      vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
      vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
      
      float snoise(vec3 v) {
        const vec2 C = vec2(1.0/6.0, 1.0/3.0);
        const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
        
        vec3 i = floor(v + dot(v, C.yyy));
        vec3 x0 = v - i + dot(i, C.xxx);
        
        vec3 g = step(x0.yzx, x0.xyz);
        vec3 l = 1.0 - g;
        vec3 i1 = min(g.xyz, l.zxy);
        vec3 i2 = max(g.xyz, l.zxy);
        
        vec3 x1 = x0 - i1 + C.xxx;
        vec3 x2 = x0 - i2 + C.yyy;
        vec3 x3 = x0 - D.yyy;
        
        i = mod289(i);
        vec4 p = permute(permute(permute(
          i.z + vec4(0.0, i1.z, i2.z, 1.0))
          + i.y + vec4(0.0, i1.y, i2.y, 1.0))
          + i.x + vec4(0.0, i1.x, i2.x, 1.0));
        
        float n_ = 0.142857142857;
        vec3 ns = n_ * D.wyz - D.xzx;
        
        vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
        
        vec4 x_ = floor(j * ns.z);
        vec4 y_ = floor(j - 7.0 * x_);
        
        vec4 x = x_ * ns.x + ns.yyyy;
        vec4 y = y_ * ns.x + ns.yyyy;
        vec4 h = 1.0 - abs(x) - abs(y);
        
        vec4 b0 = vec4(x.xy, y.xy);
        vec4 b1 = vec4(x.zw, y.zw);
        
        vec4 s0 = floor(b0) * 2.0 + 1.0;
        vec4 s1 = floor(b1) * 2.0 + 1.0;
        vec4 sh = -step(h, vec4(0.0));
        
        vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
        vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;
        
        vec3 p0 = vec3(a0.xy, h.x);
        vec3 p1 = vec3(a0.zw, h.y);
        vec3 p2 = vec3(a1.xy, h.z);
        vec3 p3 = vec3(a1.zw, h.w);
        
        vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
        p0 *= norm.x;
        p1 *= norm.y;
        p2 *= norm.z;
        p3 *= norm.w;
        
        vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
        m = m * m;
        return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
      }
      
      // Fractal Brownian Motion
      float fbm(vec3 p) {
        float value = 0.0;
        float amplitude = 0.5;
        float frequency = 1.0;
        
        for (int i = 0; i < 6; i++) {
          if (float(i) >= uNoiseOctaves) break;
          value += amplitude * snoise(p * frequency);
          frequency *= uNoiseLacunarity;
          amplitude *= uNoiseGain;
        }
        
        return value;
      }
      
      // Domain warping for organic look
      float warpedFBM(vec3 p) {
        vec3 q = vec3(
          fbm(p),
          fbm(p + vec3(5.2, 1.3, 2.8)),
          fbm(p + vec3(2.7, 8.3, 1.2))
        );
        
        vec3 r = vec3(
          fbm(p + 4.0 * q + vec3(1.7, 9.2, 3.1)),
          fbm(p + 4.0 * q + vec3(8.3, 2.8, 4.7)),
          fbm(p + 4.0 * q + vec3(3.1, 6.4, 8.2))
        );
        
        return fbm(p + 4.0 * r);
      }
      
      void main() {
        // Remap UVs to fire space
        vec2 uv = vUv;
        uv.x = (uv.x - 0.5) * 2.0; // -1 to 1
        uv.y = uv.y; // 0 to 1 (bottom to top)
        
        // Base fire shape (tapered cylinder)
        float heightFactor = uv.y;
        float taperAmount = 1.0 - heightFactor * uTaper;
        float distFromCenter = abs(uv.x) / taperAmount;
        
        // Skip pixels outside fire shape
        if (distFromCenter > 1.0) {
          discard;
        }
        
        // Animated noise coordinates
        vec3 noiseCoord = vec3(
          uv.x * uNoiseScale,
          (uv.y - uTime * uSpeed) * uNoiseScale,
          uTime * uSpeed * 0.5
        );
        
        // Get warped FBM noise for organic fire look
        float noise = warpedFBM(noiseCoord) * uTurbulence;
        
        // Flicker effect
        float flicker = sin(uTime * uFlickerSpeed) * uFlickerAmount;
        flicker += sin(uTime * uFlickerSpeed * 1.7) * uFlickerAmount * 0.5;
        
        // Fire intensity based on height and noise
        float fireShape = 1.0 - distFromCenter;
        fireShape *= 1.0 - pow(heightFactor, 1.5); // Fade at top
        fireShape += noise * 0.5;
        fireShape += flicker;
        fireShape *= uIntensity;
        
        // Clamp and smooth
        fireShape = smoothstep(0.0, 1.0, fireShape);
        
        // Color gradient based on temperature (intensity)
        vec3 color;
        if (fireShape > 0.8) {
          color = mix(uMidColor, uCoreColor, (fireShape - 0.8) / 0.2);
        } else if (fireShape > 0.4) {
          color = mix(uOuterColor, uMidColor, (fireShape - 0.4) / 0.4);
        } else {
          color = uOuterColor * (fireShape / 0.4);
        }
        
        // Soft edge falloff
        float edgeFade = 1.0 - smoothstep(1.0 - uSoftEdge, 1.0, distFromCenter);
        float topFade = 1.0 - smoothstep(0.7, 1.0, heightFactor);
        
        // Final alpha
        float alpha = fireShape * edgeFade * topFade * uOpacity;
        
        // HDR bloom emission
        float bloom = smoothstep(uBloomThreshold, 1.0, fireShape);
        color += color * bloom * 2.0;
        
        gl_FragColor = vec4(color, alpha);
      }
    `;
  }

  public dispose(): void {
    this.mesh.geometry.dispose();
    this.material.dispose();
  }
}

/**
 * Explosion Effect
 */
export interface ExplosionConfig {
  radius: number;
  duration: number;
  intensity: number;
  shockwaveSpeed: number;
  debrisCount: number;
  smokeAmount: number;
}

export const DEFAULT_EXPLOSION_CONFIG: ExplosionConfig = {
  radius: 3.0,
  duration: 1.5,
  intensity: 1.0,
  shockwaveSpeed: 10.0,
  debrisCount: 50,
  smokeAmount: 0.8
};

export class ExplosionSystem {
  private config: ExplosionConfig;
  public group: THREE.Group;
  private fireSystem!: FireSystem;
  private shockwave!: THREE.Mesh;
  private time: number = 0;
  private active: boolean = false;
  
  constructor(config: Partial<ExplosionConfig> = {}) {
    this.config = { ...DEFAULT_EXPLOSION_CONFIG, ...config };
    this.group = new THREE.Group();
    this.createShockwave();
  }

  private createShockwave(): void {
    const geometry = new THREE.RingGeometry(0.1, 0.3, 64);
    const material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uRadius: { value: 0 },
        uMaxRadius: { value: this.config.radius },
        uIntensity: { value: this.config.intensity }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uTime;
        uniform float uRadius;
        uniform float uMaxRadius;
        uniform float uIntensity;
        varying vec2 vUv;
        
        void main() {
          float ring = smoothstep(0.0, 0.1, vUv.x) * smoothstep(1.0, 0.9, vUv.x);
          float fade = 1.0 - (uRadius / uMaxRadius);
          vec3 color = vec3(1.0, 0.8, 0.3) * uIntensity;
          gl_FragColor = vec4(color, ring * fade);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });
    
    this.shockwave = new THREE.Mesh(geometry, material);
    this.shockwave.rotation.x = -Math.PI / 2;
    this.shockwave.visible = false;
    this.group.add(this.shockwave);
  }

  public trigger(position: THREE.Vector3): void {
    this.group.position.copy(position);
    this.time = 0;
    this.active = true;
    this.shockwave.visible = true;
    this.shockwave.scale.setScalar(0.1);
    
    // Create fire flash
    this.fireSystem = new FireSystem({
      baseRadius: this.config.radius * 0.5,
      height: this.config.radius,
      intensity: this.config.intensity * 2,
      speed: 3.0
    });
    this.group.add(this.fireSystem.mesh);
  }

  public update(dt: number): void {
    if (!this.active) return;
    
    this.time += dt;
    const progress = this.time / this.config.duration;
    
    if (progress >= 1.0) {
      this.active = false;
      this.shockwave.visible = false;
      if (this.fireSystem) {
        this.group.remove(this.fireSystem.mesh);
        this.fireSystem.dispose();
      }
      return;
    }
    
    // Expand shockwave
    const radius = progress * this.config.radius * 2;
    this.shockwave.scale.setScalar(radius);
    (this.shockwave.material as THREE.ShaderMaterial).uniforms.uRadius.value = radius;
    
    // Fade fire
    if (this.fireSystem) {
      this.fireSystem.setIntensity((1.0 - progress) * this.config.intensity * 2);
      this.fireSystem.update(dt);
    }
  }

  public isActive(): boolean {
    return this.active;
  }

  public dispose(): void {
    this.shockwave.geometry.dispose();
    (this.shockwave.material as THREE.Material).dispose();
    if (this.fireSystem) {
      this.fireSystem.dispose();
    }
  }
}

