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

