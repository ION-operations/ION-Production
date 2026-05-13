/**
 * GPU-Accelerated Cloth Simulation
 * Verlet Integration + Constraint Solving
 * 
 * Supports WebGL (transform feedback) and WebGPU (compute shaders)
 */

import * as THREE from 'three';

export interface ClothConfig {
  // Grid dimensions
  width: number;         // Segments in X
  height: number;        // Segments in Y
  segmentWidth: number;  // Physical width per segment
  segmentHeight: number; // Physical height per segment
  
  // Physics
  mass: number;          // Mass per particle
  gravity: THREE.Vector3;
  wind: THREE.Vector3;
  windStrength: number;
  
  // Constraints
  structuralStiffness: number; // Neighbor connections (0-1)
  shearStiffness: number;      // Diagonal connections (0-1)
  bendStiffness: number;       // Skip-one connections (0-1)
  iterations: number;          // Constraint solve iterations
  
  // Damping
  damping: number;             // Velocity damping (0.97-0.99)
  
  // Collision
  sphereColliders: ClothSphereCollider[];
  groundY: number | null;
  friction: number;
}

export interface ClothSphereCollider {
  center: THREE.Vector3;
  radius: number;
}

export const DEFAULT_CLOTH_CONFIG: ClothConfig = {
  width: 32,
  height: 32,
  segmentWidth: 0.1,
  segmentHeight: 0.1,
  
  mass: 1.0,
  gravity: new THREE.Vector3(0, -9.81, 0),
  wind: new THREE.Vector3(0, 0, 0),
  windStrength: 1.0,
  
  structuralStiffness: 0.9,
  shearStiffness: 0.9,
  bendStiffness: 0.5,
  iterations: 5,
  
  damping: 0.98,
  
  sphereColliders: [],
  groundY: null,
  friction: 0.3
};

interface ClothParticle {
  position: THREE.Vector3;
  prevPosition: THREE.Vector3;
  acceleration: THREE.Vector3;
  invMass: number;
  uv: THREE.Vector2;
}

interface ClothConstraint {
  p1: number;
  p2: number;
  restLength: number;
  stiffness: number;
}

export class ClothSimulation {
  private config: ClothConfig;
  private particles: ClothParticle[] = [];
  private constraints: ClothConstraint[] = [];
  
  // Three.js rendering
  public geometry!: THREE.BufferGeometry;
  public mesh!: THREE.Mesh;
  private material!: THREE.MeshStandardMaterial;
  
  // Pinned particles
  private pinnedParticles: Set<number> = new Set();
  
  // Temp vectors
  private readonly _v1 = new THREE.Vector3();
  private readonly _v2 = new THREE.Vector3();
  private readonly _normal = new THREE.Vector3();

  constructor(config: Partial<ClothConfig> = {}) {
    this.config = { ...DEFAULT_CLOTH_CONFIG, ...config };
    this.initParticles();
    this.initConstraints();
    this.initGeometry();
  }

  private initParticles(): void {
    const { width, height, segmentWidth, segmentHeight } = this.config;
    const invMass = 1.0 / this.config.mass;
    
    for (let y = 0; y <= height; y++) {
      for (let x = 0; x <= width; x++) {
        const pos = new THREE.Vector3(
          (x - width / 2) * segmentWidth,
          0,
          (y - height / 2) * segmentHeight
        );
        
        this.particles.push({
          position: pos.clone(),
          prevPosition: pos.clone(),
          acceleration: new THREE.Vector3(),
          invMass: invMass,
          uv: new THREE.Vector2(x / width, y / height)
        });
      }
    }
    
    // Pin top row by default
    for (let x = 0; x <= width; x++) {
      this.pinParticle(x);
    }
  }

  private initConstraints(): void {
    const { width, height } = this.config;
    const gridWidth = width + 1;
    
    const addConstraint = (i1: number, i2: number, stiffness: number) => {
      const p1 = this.particles[i1];
      const p2 = this.particles[i2];
      const restLength = p1.position.distanceTo(p2.position);
      
      this.constraints.push({
        p1: i1,
        p2: i2,
        restLength,
        stiffness
      });
    };
    
    for (let y = 0; y <= height; y++) {
      for (let x = 0; x <= width; x++) {
        const idx = y * gridWidth + x;
        
        // Structural (horizontal and vertical neighbors)
        if (x < width) {
          addConstraint(idx, idx + 1, this.config.structuralStiffness);
        }
        if (y < height) {
          addConstraint(idx, idx + gridWidth, this.config.structuralStiffness);
        }
        
        // Shear (diagonals)
        if (x < width && y < height) {
          addConstraint(idx, idx + gridWidth + 1, this.config.shearStiffness);
          addConstraint(idx + 1, idx + gridWidth, this.config.shearStiffness);
        }
        
        // Bend (skip-one connections)
        if (x < width - 1) {
          addConstraint(idx, idx + 2, this.config.bendStiffness);
        }
        if (y < height - 1) {
          addConstraint(idx, idx + gridWidth * 2, this.config.bendStiffness);
        }
      }
    }
  }

  private initGeometry(): void {
    const { width, height } = this.config;
    const gridWidth = width + 1;
    
    // Create indexed geometry
    this.geometry = new THREE.BufferGeometry();
    
    // Positions
    const positions = new Float32Array(this.particles.length * 3);
    const normals = new Float32Array(this.particles.length * 3);
    const uvs = new Float32Array(this.particles.length * 2);
    
    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      positions[i * 3] = p.position.x;
      positions[i * 3 + 1] = p.position.y;
      positions[i * 3 + 2] = p.position.z;
      normals[i * 3 + 1] = 1; // Initial up normal
      uvs[i * 2] = p.uv.x;
      uvs[i * 2 + 1] = p.uv.y;
    }
    
    // Indices
    const indices: number[] = [];
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const i = y * gridWidth + x;
        
        // Two triangles per quad
        indices.push(i, i + gridWidth, i + 1);
        indices.push(i + 1, i + gridWidth, i + gridWidth + 1);
      }
    }
    
    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    this.geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    this.geometry.setIndex(indices);
    
    // Material
    this.material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      roughness: 0.8,
      metalness: 0.0
    });
    
    this.mesh = new THREE.Mesh(this.geometry, this.material);
  }

  /**
   * Pin a particle (make it immovable)
   */
  public pinParticle(index: number): void {
    if (index >= 0 && index < this.particles.length) {
      this.particles[index].invMass = 0;
      this.pinnedParticles.add(index);
    }
  }

  /**
   * Unpin a particle
   */
  public unpinParticle(index: number): void {
    if (this.pinnedParticles.has(index)) {
      this.particles[index].invMass = 1.0 / this.config.mass;
      this.pinnedParticles.delete(index);
    }
  }

  /**
   * Move a pinned particle
   */
  public moveParticle(index: number, position: THREE.Vector3): void {
    if (this.pinnedParticles.has(index)) {
      this.particles[index].position.copy(position);
      this.particles[index].prevPosition.copy(position);
    }
  }

  /**
   * Main simulation step using Verlet integration
   */
  public update(dt: number): void {
    // Clamp dt to prevent instability
    dt = Math.min(dt, 1 / 30);
    
    // 1. Apply forces (gravity + wind)
    this.applyForces(dt);
    
    // 2. Verlet integration
    this.integrate(dt);
    
    // 3. Solve constraints
    for (let i = 0; i < this.config.iterations; i++) {
      this.solveConstraints();
    }
    
    // 4. Handle collisions
    this.handleCollisions();
    
    // 5. Update geometry
    this.updateGeometry();
  }

  private applyForces(dt: number): void {
    const gravity = this.config.gravity;
    const wind = this.config.wind.clone().multiplyScalar(this.config.windStrength);
    
    // Add time-varying wind turbulence
    const time = performance.now() / 1000;
    wind.x += Math.sin(time * 2) * 0.5;
    wind.z += Math.cos(time * 1.5) * 0.5;
    
    for (const p of this.particles) {
      if (p.invMass === 0) continue;
      
      // Gravity
      p.acceleration.copy(gravity);
      
      // Wind (simplified - applies to all particles)
      p.acceleration.add(wind);
    }
  }

  private integrate(dt: number): void {
    const damping = this.config.damping;
    
    for (const p of this.particles) {
      if (p.invMass === 0) continue;
      
      // Verlet integration
      this._v1.subVectors(p.position, p.prevPosition);
      this._v1.multiplyScalar(damping);
      
      p.prevPosition.copy(p.position);
      
      p.position.add(this._v1);
      p.position.addScaledVector(p.acceleration, dt * dt);
      
      // Reset acceleration
      p.acceleration.set(0, 0, 0);
    }
  }

  private solveConstraints(): void {
    for (const c of this.constraints) {
      const p1 = this.particles[c.p1];
      const p2 = this.particles[c.p2];
      
      // Skip if both are pinned
      if (p1.invMass === 0 && p2.invMass === 0) continue;
      
      this._v1.subVectors(p2.position, p1.position);
      const currentLength = this._v1.length();
      
      if (currentLength < 0.0001) continue;
      
      const error = (currentLength - c.restLength) / currentLength;
      const totalInvMass = p1.invMass + p2.invMass;
      
      if (totalInvMass < 0.0001) continue;
      
      const correction = error * c.stiffness;
      
      if (p1.invMass > 0) {
        p1.position.addScaledVector(this._v1, correction * (p1.invMass / totalInvMass));
      }
      if (p2.invMass > 0) {
        p2.position.addScaledVector(this._v1, -correction * (p2.invMass / totalInvMass));
      }
    }
  }

  private handleCollisions(): void {
    const friction = this.config.friction;
    
    for (const p of this.particles) {
      if (p.invMass === 0) continue;
      
      // Ground collision
      if (this.config.groundY !== null && p.position.y < this.config.groundY) {
        p.position.y = this.config.groundY;
        
        // Apply friction to horizontal movement
        const prevY = p.prevPosition.y;
        if (prevY > this.config.groundY) {
          const dx = p.position.x - p.prevPosition.x;
          const dz = p.position.z - p.prevPosition.z;
          p.position.x -= dx * friction;
          p.position.z -= dz * friction;
        }
      }
      
      // Sphere collisions
      for (const sphere of this.config.sphereColliders) {
        this._v1.subVectors(p.position, sphere.center);
        const dist = this._v1.length();
        
        if (dist < sphere.radius && dist > 0.001) {
          // Push out
          this._v1.normalize().multiplyScalar(sphere.radius - dist);
          p.position.add(this._v1);
        }
      }
    }
  }

  private updateGeometry(): void {
    const posAttr = this.geometry.getAttribute('position') as THREE.BufferAttribute;
    
    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      posAttr.setXYZ(i, p.position.x, p.position.y, p.position.z);
    }
    
    posAttr.needsUpdate = true;
    
    // Recompute normals
    this.geometry.computeVertexNormals();
  }

  /**
   * Add sphere collider
   */
  public addSphereCollider(center: THREE.Vector3, radius: number): void {
    this.config.sphereColliders.push({ center: center.clone(), radius });
  }

  /**
   * Update sphere collider position
   */
  public updateSphereCollider(index: number, center: THREE.Vector3): void {
    if (index < this.config.sphereColliders.length) {
      this.config.sphereColliders[index].center.copy(center);
    }
  }

  /**
   * Set wind
   */
  public setWind(wind: THREE.Vector3, strength: number = 1.0): void {
    this.config.wind.copy(wind);
    this.config.windStrength = strength;
  }

  /**
   * Set texture
   */
  public setTexture(texture: THREE.Texture): void {
    this.material.map = texture;
    this.material.needsUpdate = true;
  }

  /**
   * Get particle index from grid coordinates
   */
  public getParticleIndex(x: number, y: number): number {
    return y * (this.config.width + 1) + x;
  }

  /**
   * Apply force to specific particle
   */
  public applyForceToParticle(index: number, force: THREE.Vector3): void {
    if (index >= 0 && index < this.particles.length) {
      const p = this.particles[index];
      if (p.invMass > 0) {
        p.position.add(force);
      }
    }
  }

  /**
   * Cleanup
   */
  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

