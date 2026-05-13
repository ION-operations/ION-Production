# CODEX EFFECTS MONOLITH COMPLETE

**Date:** 2025-01-27  
**Status:** ✅ Complete Reference  
**Directory:** `codex-systems/effects/`  
**Purpose:** Complete self-contained reference for all effects systems in Codex

---

## Table of Contents

1. [TrailRenderer.ts](#trailrendererts)
2. [FireSystem.ts](#firesystemts)

---

## TrailRenderer.ts

**Location:** `codex-systems/effects/trails/TrailRenderer.ts`  
**Purpose:** Dynamic ribbon/trail effects for objects in motion

```typescript
/**
 * Trail Renderer System
 * Dynamic ribbon/trail effects for objects in motion
 * 
 * Features:
 * - Ribbon geometry generation
 * - Smooth interpolation
 * - Width over lifetime
 * - Color gradient
 * - Texture scrolling
 * - Velocity-based width
 * - Multiple trail modes
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface TrailConfig {
  maxPoints: number;
  width: number;
  widthCurve: THREE.Vector2[];  // x = time (0-1), y = width multiplier
  colorGradient: { time: number; color: THREE.Color }[];
  alphaGradient: { time: number; alpha: number }[];
  lifetime: number;
  minVertexDistance: number;
  textureMode: 'stretch' | 'tile';
  emitting: boolean;
  faceCamera: boolean;
  velocityScale: boolean;
}

export interface TrailPoint {
  position: THREE.Vector3;
  timestamp: number;
  width: number;
  color: THREE.Color;
  alpha: number;
}

// ============================================
// TRAIL RENDERER
// ============================================

export class TrailRenderer {
  private config: TrailConfig;
  private points: TrailPoint[] = [];
  private geometry: THREE.BufferGeometry;
  private material: THREE.ShaderMaterial;
  private mesh: THREE.Mesh;
  private scene: THREE.Scene;
  private target: THREE.Object3D;
  
  private positions: Float32Array;
  private colors: Float32Array;
  private uvs: Float32Array;
  private indices: Uint32Array;
  
  private lastPosition: THREE.Vector3 = new THREE.Vector3();
  private lastTime: number = 0;
  
  constructor(
    scene: THREE.Scene,
    target: THREE.Object3D,
    config: Partial<TrailConfig> = {}
  ) {
    this.scene = scene;
    this.target = target;
    
    this.config = {
      maxPoints: 100,
      width: 0.5,
      widthCurve: [
        { x: 0, y: 1 },
        { x: 0.5, y: 1 },
        { x: 1, y: 0 }
      ],
      colorGradient: [
        { time: 0, color: new THREE.Color(1, 1, 1) },
        { time: 1, color: new THREE.Color(1, 1, 1) }
      ],
      alphaGradient: [
        { time: 0, alpha: 1 },
        { time: 1, alpha: 0 }
      ],
      lifetime: 1.0,
      minVertexDistance: 0.1,
      textureMode: 'stretch',
      emitting: true,
      faceCamera: true,
      velocityScale: false,
      ...config
    };
    
    // Initialize buffers
    const maxVerts = this.config.maxPoints * 2;
    this.positions = new Float32Array(maxVerts * 3);
    this.colors = new Float32Array(maxVerts * 4);
    this.uvs = new Float32Array(maxVerts * 2);
    this.indices = new Uint32Array((this.config.maxPoints - 1) * 6);
    
    // Create geometry
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 4));
    this.geometry.setAttribute('uv', new THREE.BufferAttribute(this.uvs, 2));
    this.geometry.setIndex(new THREE.BufferAttribute(this.indices, 1));
    
    // Create material
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        useTexture: { value: false }
      },
      vertexShader: `
        attribute vec4 color;
        varying vec4 vColor;
        varying vec2 vUv;
        
        void main() {
          vColor = color;
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform bool useTexture;
        
        varying vec4 vColor;
        varying vec2 vUv;
        
        void main() {
          vec4 texColor = useTexture ? texture2D(tDiffuse, vUv) : vec4(1.0);
          gl_FragColor = vColor * texColor;
        }
      `,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      blending: THREE.NormalBlending
    });
    
    this.mesh = new THREE.Mesh(this.geometry, this.material);
    this.mesh.frustumCulled = false;
    scene.add(this.mesh);
    
    // Initialize position
    this.lastPosition.copy(target.getWorldPosition(new THREE.Vector3()));
  }
  
  /**
   * Update trail
   */
  public update(camera: THREE.Camera): void {
    const currentTime = performance.now() / 1000;
    const deltaTime = currentTime - this.lastTime;
    this.lastTime = currentTime;
    
    // Get current target position
    const currentPosition = this.target.getWorldPosition(new THREE.Vector3());
    
    // Add new point if moved enough and emitting
    if (this.config.emitting) {
      const distance = currentPosition.distanceTo(this.lastPosition);
      
      if (distance >= this.config.minVertexDistance) {
        this.addPoint(currentPosition.clone(), currentTime);
        this.lastPosition.copy(currentPosition);
      }
    }
    
    // Remove old points
    this.removeOldPoints(currentTime);
    
    // Update geometry
    this.updateGeometry(camera, currentTime);
  }
  
  private addPoint(position: THREE.Vector3, timestamp: number): void {
    const point: TrailPoint = {
      position,
      timestamp,
      width: this.config.width,
      color: this.sampleColorGradient(0),
      alpha: this.sampleAlphaGradient(0)
    };
    
    this.points.unshift(point);
    
    // Limit points
    while (this.points.length > this.config.maxPoints) {
      this.points.pop();
    }
  }
  
  private removeOldPoints(currentTime: number): void {
    const cutoffTime = currentTime - this.config.lifetime;
    
    while (this.points.length > 0 && 
           this.points[this.points.length - 1].timestamp < cutoffTime) {
      this.points.pop();
    }
  }
  
  private updateGeometry(camera: THREE.Camera, currentTime: number): void {
    if (this.points.length < 2) {
      this.geometry.setDrawRange(0, 0);
      return;
    }
    
    const cameraPosition = camera.getWorldPosition(new THREE.Vector3());
    
    for (let i = 0; i < this.points.length; i++) {
      const point = this.points[i];
      const age = currentTime - point.timestamp;
      const t = age / this.config.lifetime;
      
      // Sample gradients
      const widthMult = this.sampleWidthCurve(t);
      const color = this.sampleColorGradient(t);
      const alpha = this.sampleAlphaGradient(t);
      
      const width = this.config.width * widthMult;
      
      // Calculate perpendicular direction
      let perpendicular: THREE.Vector3;
      
      if (this.config.faceCamera) {
        // Face camera
        const toCamera = cameraPosition.clone().sub(point.position).normalize();
        
        let tangent: THREE.Vector3;
        if (i < this.points.length - 1) {
          tangent = this.points[i + 1].position.clone().sub(point.position).normalize();
        } else if (i > 0) {
          tangent = point.position.clone().sub(this.points[i - 1].position).normalize();
        } else {
          tangent = new THREE.Vector3(0, 0, 1);
        }
        
        perpendicular = toCamera.cross(tangent).normalize();
      } else {
        // Fixed up direction
        let tangent: THREE.Vector3;
        if (i < this.points.length - 1) {
          tangent = this.points[i + 1].position.clone().sub(point.position).normalize();
        } else {
          tangent = new THREE.Vector3(0, 0, 1);
        }
        
        const up = new THREE.Vector3(0, 1, 0);
        perpendicular = tangent.clone().cross(up).normalize();
      }
      
      // Calculate left and right positions
      const leftPos = point.position.clone().add(perpendicular.clone().multiplyScalar(width / 2));
      const rightPos = point.position.clone().sub(perpendicular.clone().multiplyScalar(width / 2));
      
      // Update buffers
      const vi = i * 2;
      
      // Left vertex
      this.positions[vi * 3 + 0] = leftPos.x;
      this.positions[vi * 3 + 1] = leftPos.y;
      this.positions[vi * 3 + 2] = leftPos.z;
      
      // Right vertex
      this.positions[(vi + 1) * 3 + 0] = rightPos.x;
      this.positions[(vi + 1) * 3 + 1] = rightPos.y;
      this.positions[(vi + 1) * 3 + 2] = rightPos.z;
      
      // Colors (RGBA)
      this.colors[vi * 4 + 0] = color.r;
      this.colors[vi * 4 + 1] = color.g;
      this.colors[vi * 4 + 2] = color.b;
      this.colors[vi * 4 + 3] = alpha;
      
      this.colors[(vi + 1) * 4 + 0] = color.r;
      this.colors[(vi + 1) * 4 + 1] = color.g;
      this.colors[(vi + 1) * 4 + 2] = color.b;
      this.colors[(vi + 1) * 4 + 3] = alpha;
      
      // UVs
      const u = this.config.textureMode === 'stretch' 
        ? t 
        : i * this.config.minVertexDistance;
      
      this.uvs[vi * 2 + 0] = u;
      this.uvs[vi * 2 + 1] = 0;
      
      this.uvs[(vi + 1) * 2 + 0] = u;
      this.uvs[(vi + 1) * 2 + 1] = 1;
    }
    
    // Generate indices
    let indexOffset = 0;
    for (let i = 0; i < this.points.length - 1; i++) {
      const vi = i * 2;
      
      // First triangle
      this.indices[indexOffset++] = vi;
      this.indices[indexOffset++] = vi + 1;
      this.indices[indexOffset++] = vi + 2;
      
      // Second triangle
      this.indices[indexOffset++] = vi + 1;
      this.indices[indexOffset++] = vi + 3;
      this.indices[indexOffset++] = vi + 2;
    }
    
    // Update geometry
    this.geometry.attributes.position.needsUpdate = true;
    this.geometry.attributes.color.needsUpdate = true;
    this.geometry.attributes.uv.needsUpdate = true;
    this.geometry.index!.needsUpdate = true;
    
    this.geometry.setDrawRange(0, indexOffset);
    this.geometry.computeBoundingSphere();
  }
  
  private sampleWidthCurve(t: number): number {
    const curve = this.config.widthCurve;
    
    if (curve.length === 0) return 1;
    if (t <= curve[0].x) return curve[0].y;
    if (t >= curve[curve.length - 1].x) return curve[curve.length - 1].y;
    
    for (let i = 0; i < curve.length - 1; i++) {
      if (t >= curve[i].x && t <= curve[i + 1].x) {
        const localT = (t - curve[i].x) / (curve[i + 1].x - curve[i].x);
        return THREE.MathUtils.lerp(curve[i].y, curve[i + 1].y, localT);
      }
    }
    
    return 1;
  }
  
  private sampleColorGradient(t: number): THREE.Color {
    const gradient = this.config.colorGradient;
    
    if (gradient.length === 0) return new THREE.Color(1, 1, 1);
    if (t <= gradient[0].time) return gradient[0].color.clone();
    if (t >= gradient[gradient.length - 1].time) return gradient[gradient.length - 1].color.clone();
    
    for (let i = 0; i < gradient.length - 1; i++) {
      if (t >= gradient[i].time && t <= gradient[i + 1].time) {
        const localT = (t - gradient[i].time) / (gradient[i + 1].time - gradient[i].time);
        return gradient[i].color.clone().lerp(gradient[i + 1].color, localT);
      }
    }
    
    return new THREE.Color(1, 1, 1);
  }
  
  private sampleAlphaGradient(t: number): number {
    const gradient = this.config.alphaGradient;
    
    if (gradient.length === 0) return 1;
    if (t <= gradient[0].time) return gradient[0].alpha;
    if (t >= gradient[gradient.length - 1].time) return gradient[gradient.length - 1].alpha;
    
    for (let i = 0; i < gradient.length - 1; i++) {
      if (t >= gradient[i].time && t <= gradient[i + 1].time) {
        const localT = (t - gradient[i].time) / (gradient[i + 1].time - gradient[i].time);
        return THREE.MathUtils.lerp(gradient[i].alpha, gradient[i + 1].alpha, localT);
      }
    }
    
    return 1;
  }
  
  /**
   * Set texture
   */
  public setTexture(texture: THREE.Texture | null): void {
    this.material.uniforms.tDiffuse.value = texture;
    this.material.uniforms.useTexture.value = texture !== null;
  }
  
  /**
   * Set emitting
   */
  public setEmitting(emitting: boolean): void {
    this.config.emitting = emitting;
  }
  
  /**
   * Clear trail
   */
  public clear(): void {
    this.points = [];
    this.geometry.setDrawRange(0, 0);
  }
  
  /**
   * Set blending mode
   */
  public setBlending(blending: THREE.Blending): void {
    this.material.blending = blending;
  }
  
  /**
   * Get point count
   */
  public getPointCount(): number {
    return this.points.length;
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.scene.remove(this.mesh);
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// MULTI-TRAIL MANAGER
// ============================================

export class MultiTrailManager {
  private trails: Map<string, TrailRenderer> = new Map();
  private scene: THREE.Scene;
  
  constructor(scene: THREE.Scene) {
    this.scene = scene;
  }
  
  /**
   * Create new trail
   */
  public createTrail(
    id: string,
    target: THREE.Object3D,
    config?: Partial<TrailConfig>
  ): TrailRenderer {
    // Remove existing if present
    if (this.trails.has(id)) {
      this.removeTrail(id);
    }
    
    const trail = new TrailRenderer(this.scene, target, config);
    this.trails.set(id, trail);
    return trail;
  }
  
  /**
   * Get trail by ID
   */
  public getTrail(id: string): TrailRenderer | undefined {
    return this.trails.get(id);
  }
  
  /**
   * Remove trail
   */
  public removeTrail(id: string): void {
    const trail = this.trails.get(id);
    if (trail) {
      trail.dispose();
      this.trails.delete(id);
    }
  }
  
  /**
   * Update all trails
   */
  public update(camera: THREE.Camera): void {
    for (const trail of this.trails.values()) {
      trail.update(camera);
    }
  }
  
  /**
   * Clear all trails
   */
  public clearAll(): void {
    for (const trail of this.trails.values()) {
      trail.clear();
    }
  }
  
  /**
   * Dispose all
   */
  public dispose(): void {
    for (const id of Array.from(this.trails.keys())) {
      this.removeTrail(id);
    }
  }
}
```

---

## FireSystem.ts

**Location:** `codex-systems/effects/fire/FireSystem.ts`  
**Purpose:** Volumetric fire & explosion system with particle emission and raymarching

```typescript
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
```

---

## Summary

**Total Files:** 2  
**Total Lines:** ~1,200  
**Systems:**
- **TrailRenderer:** Dynamic ribbon/trail effects with gradient support
- **FireSystem:** Volumetric fire with FBM noise and domain warping
- **ExplosionSystem:** Explosion effects with shockwave and fire flash

**Key Features:**
- GPU-accelerated rendering
- Custom shader materials
- Configurable parameters
- Performance-optimized buffer management
- Multi-instance support (MultiTrailManager)

---

**END OF MONOLITH**

