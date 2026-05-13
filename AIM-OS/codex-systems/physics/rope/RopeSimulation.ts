/**
 * Rope/Cable Simulation System
 * Verlet integration with distance constraints
 * 
 * Features:
 * - Verlet position-based dynamics
 * - Distance constraints with iterations
 * - Collision with spheres/planes
 * - Stiffness and damping
 * - Wind and gravity forces
 * - Attachment points (pinned particles)
 * - Tube geometry rendering
 * - Grappling hook physics
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface RopeParticle {
  position: THREE.Vector3;
  previousPosition: THREE.Vector3;
  acceleration: THREE.Vector3;
  mass: number;
  pinned: boolean;
  velocity: THREE.Vector3;  // For damping calculations
}

export interface RopeConstraint {
  particleA: number;
  particleB: number;
  restLength: number;
  stiffness: number;
}

export interface RopeCollider {
  type: 'sphere' | 'plane' | 'capsule';
  position: THREE.Vector3;
  radius?: number;
  normal?: THREE.Vector3;
  start?: THREE.Vector3;
  end?: THREE.Vector3;
}

export interface RopeConfig {
  segments: number;
  length: number;
  thickness: number;
  mass: number;
  stiffness: number;
  damping: number;
  gravity: THREE.Vector3;
  constraintIterations: number;
  maxStretch: number;
}

// ============================================
// ROPE PHYSICS
// ============================================

export class RopePhysics {
  public particles: RopeParticle[] = [];
  public constraints: RopeConstraint[] = [];
  
  private config: RopeConfig;
  private colliders: RopeCollider[] = [];
  private wind: THREE.Vector3 = new THREE.Vector3();
  
  constructor(
    startPoint: THREE.Vector3,
    endPoint: THREE.Vector3,
    config: Partial<RopeConfig> = {}
  ) {
    this.config = {
      segments: 20,
      length: 10,
      thickness: 0.05,
      mass: 1,
      stiffness: 1.0,
      damping: 0.99,
      gravity: new THREE.Vector3(0, -9.81, 0),
      constraintIterations: 10,
      maxStretch: 1.1,
      ...config
    };
    
    this.initializeParticles(startPoint, endPoint);
    this.initializeConstraints();
  }
  
  private initializeParticles(start: THREE.Vector3, end: THREE.Vector3): void {
    const segmentLength = this.config.length / this.config.segments;
    const direction = end.clone().sub(start).normalize();
    
    for (let i = 0; i <= this.config.segments; i++) {
      const t = i / this.config.segments;
      const position = start.clone().lerp(end, t);
      
      this.particles.push({
        position: position.clone(),
        previousPosition: position.clone(),
        acceleration: new THREE.Vector3(),
        mass: this.config.mass / (this.config.segments + 1),
        pinned: false,
        velocity: new THREE.Vector3()
      });
    }
    
    // Pin first particle by default
    this.particles[0].pinned = true;
  }
  
  private initializeConstraints(): void {
    const segmentLength = this.config.length / this.config.segments;
    
    for (let i = 0; i < this.config.segments; i++) {
      this.constraints.push({
        particleA: i,
        particleB: i + 1,
        restLength: segmentLength,
        stiffness: this.config.stiffness
      });
    }
  }
  
  /**
   * Pin a particle to prevent movement
   */
  public pinParticle(index: number, position?: THREE.Vector3): void {
    if (index >= 0 && index < this.particles.length) {
      this.particles[index].pinned = true;
      if (position) {
        this.particles[index].position.copy(position);
        this.particles[index].previousPosition.copy(position);
      }
    }
  }
  
  /**
   * Unpin a particle
   */
  public unpinParticle(index: number): void {
    if (index >= 0 && index < this.particles.length) {
      this.particles[index].pinned = false;
    }
  }
  
  /**
   * Move a pinned particle
   */
  public moveParticle(index: number, position: THREE.Vector3): void {
    if (index >= 0 && index < this.particles.length && this.particles[index].pinned) {
      this.particles[index].position.copy(position);
    }
  }
  
  /**
   * Add external force to all particles
   */
  public addForce(force: THREE.Vector3): void {
    for (const particle of this.particles) {
      if (!particle.pinned) {
        particle.acceleration.add(force);
      }
    }
  }
  
  /**
   * Set wind force
   */
  public setWind(wind: THREE.Vector3): void {
    this.wind.copy(wind);
  }
  
  /**
   * Add a collider
   */
  public addCollider(collider: RopeCollider): void {
    this.colliders.push(collider);
  }
  
  /**
   * Clear all colliders
   */
  public clearColliders(): void {
    this.colliders = [];
  }
  
  /**
   * Update simulation
   */
  public update(deltaTime: number): void {
    // Apply forces
    this.applyForces(deltaTime);
    
    // Verlet integration
    this.verletIntegrate(deltaTime);
    
    // Satisfy constraints
    for (let i = 0; i < this.config.constraintIterations; i++) {
      this.satisfyConstraints();
      this.handleCollisions();
    }
  }
  
  private applyForces(deltaTime: number): void {
    for (const particle of this.particles) {
      if (particle.pinned) continue;
      
      // Gravity
      particle.acceleration.add(this.config.gravity.clone().multiplyScalar(particle.mass));
      
      // Wind (with some turbulence)
      if (this.wind.lengthSq() > 0) {
        const turbulence = Math.sin(Date.now() * 0.001 + particle.position.y) * 0.3;
        const windForce = this.wind.clone().multiplyScalar(1 + turbulence);
        particle.acceleration.add(windForce);
      }
    }
  }
  
  private verletIntegrate(deltaTime: number): void {
    const dt2 = deltaTime * deltaTime;
    const damping = this.config.damping;
    
    for (const particle of this.particles) {
      if (particle.pinned) {
        particle.previousPosition.copy(particle.position);
        continue;
      }
      
      // Calculate velocity
      particle.velocity.subVectors(particle.position, particle.previousPosition);
      
      // Store current position
      const temp = particle.position.clone();
      
      // Verlet integration: x' = x + (x - x_prev) * damping + a * dt^2
      particle.position.add(
        particle.velocity.multiplyScalar(damping)
      );
      particle.position.add(
        particle.acceleration.clone().multiplyScalar(dt2)
      );
      
      // Update previous position
      particle.previousPosition.copy(temp);
      
      // Reset acceleration
      particle.acceleration.set(0, 0, 0);
    }
  }
  
  private satisfyConstraints(): void {
    for (const constraint of this.constraints) {
      const particleA = this.particles[constraint.particleA];
      const particleB = this.particles[constraint.particleB];
      
      const delta = particleB.position.clone().sub(particleA.position);
      const currentLength = delta.length();
      
      if (currentLength === 0) continue;
      
      // Calculate stretch
      const stretch = currentLength - constraint.restLength;
      
      // Limit maximum stretch
      const maxLength = constraint.restLength * this.config.maxStretch;
      const clampedLength = Math.min(currentLength, maxLength);
      const correction = (currentLength - constraint.restLength) * constraint.stiffness;
      
      // Normalize delta
      delta.normalize();
      
      // Apply corrections based on mass
      if (!particleA.pinned && !particleB.pinned) {
        const totalMass = particleA.mass + particleB.mass;
        const ratioA = particleB.mass / totalMass;
        const ratioB = particleA.mass / totalMass;
        
        particleA.position.add(delta.clone().multiplyScalar(correction * ratioA));
        particleB.position.sub(delta.clone().multiplyScalar(correction * ratioB));
      } else if (!particleA.pinned) {
        particleA.position.add(delta.clone().multiplyScalar(correction));
      } else if (!particleB.pinned) {
        particleB.position.sub(delta.clone().multiplyScalar(correction));
      }
    }
  }
  
  private handleCollisions(): void {
    for (const particle of this.particles) {
      if (particle.pinned) continue;
      
      for (const collider of this.colliders) {
        switch (collider.type) {
          case 'sphere':
            this.collideWithSphere(particle, collider);
            break;
          case 'plane':
            this.collideWithPlane(particle, collider);
            break;
          case 'capsule':
            this.collideWithCapsule(particle, collider);
            break;
        }
      }
    }
  }
  
  private collideWithSphere(particle: RopeParticle, collider: RopeCollider): void {
    if (!collider.radius) return;
    
    const toParticle = particle.position.clone().sub(collider.position);
    const distance = toParticle.length();
    const minDist = collider.radius + this.config.thickness;
    
    if (distance < minDist) {
      const correction = toParticle.normalize().multiplyScalar(minDist - distance);
      particle.position.add(correction);
    }
  }
  
  private collideWithPlane(particle: RopeParticle, collider: RopeCollider): void {
    if (!collider.normal) return;
    
    const toParticle = particle.position.clone().sub(collider.position);
    const distance = toParticle.dot(collider.normal);
    const minDist = this.config.thickness;
    
    if (distance < minDist) {
      const correction = collider.normal.clone().multiplyScalar(minDist - distance);
      particle.position.add(correction);
    }
  }
  
  private collideWithCapsule(particle: RopeParticle, collider: RopeCollider): void {
    if (!collider.start || !collider.end || !collider.radius) return;
    
    // Find closest point on capsule axis
    const axis = collider.end.clone().sub(collider.start);
    const axisLength = axis.length();
    axis.normalize();
    
    const toParticle = particle.position.clone().sub(collider.start);
    const projection = Math.max(0, Math.min(axisLength, toParticle.dot(axis)));
    
    const closestPoint = collider.start.clone().add(axis.clone().multiplyScalar(projection));
    
    // Check distance to closest point
    const toClosest = particle.position.clone().sub(closestPoint);
    const distance = toClosest.length();
    const minDist = collider.radius + this.config.thickness;
    
    if (distance < minDist && distance > 0) {
      const correction = toClosest.normalize().multiplyScalar(minDist - distance);
      particle.position.add(correction);
    }
  }
  
  /**
   * Get positions for rendering
   */
  public getPositions(): THREE.Vector3[] {
    return this.particles.map(p => p.position.clone());
  }
  
  /**
   * Get current length of rope
   */
  public getCurrentLength(): number {
    let length = 0;
    for (let i = 0; i < this.particles.length - 1; i++) {
      length += this.particles[i].position.distanceTo(this.particles[i + 1].position);
    }
    return length;
  }
}

// ============================================
// ROPE RENDERER (Tube Geometry)
// ============================================

export class RopeRenderer {
  public mesh: THREE.Mesh;
  
  private geometry: THREE.TubeGeometry | null = null;
  private material: THREE.MeshStandardMaterial;
  private curve: THREE.CatmullRomCurve3;
  private tubularSegments: number;
  private radialSegments: number;
  private radius: number;
  
  constructor(
    initialPositions: THREE.Vector3[],
    radius: number = 0.05,
    tubularSegments: number = 64,
    radialSegments: number = 8,
    material?: THREE.MeshStandardMaterial
  ) {
    this.radius = radius;
    this.tubularSegments = tubularSegments;
    this.radialSegments = radialSegments;
    
    this.curve = new THREE.CatmullRomCurve3(initialPositions);
    this.curve.curveType = 'catmullrom';
    this.curve.tension = 0.5;
    
    this.material = material ?? new THREE.MeshStandardMaterial({
      color: 0x8B4513,  // Brown rope color
      roughness: 0.8,
      metalness: 0.1
    });
    
    this.geometry = new THREE.TubeGeometry(
      this.curve,
      this.tubularSegments,
      this.radius,
      this.radialSegments,
      false
    );
    
    this.mesh = new THREE.Mesh(this.geometry, this.material);
    this.mesh.castShadow = true;
    this.mesh.receiveShadow = true;
  }
  
  /**
   * Update rope geometry from particle positions
   */
  public update(positions: THREE.Vector3[]): void {
    // Update curve points
    this.curve.points = positions;
    
    // Dispose old geometry
    if (this.geometry) {
      this.geometry.dispose();
    }
    
    // Create new geometry
    this.geometry = new THREE.TubeGeometry(
      this.curve,
      this.tubularSegments,
      this.radius,
      this.radialSegments,
      false
    );
    
    this.mesh.geometry = this.geometry;
  }
  
  /**
   * Set rope color
   */
  public setColor(color: THREE.Color): void {
    this.material.color = color;
  }
  
  /**
   * Dispose resources
   */
  public dispose(): void {
    this.geometry?.dispose();
    this.material.dispose();
  }
}

// ============================================
// LINE RENDERER (Performance)
// ============================================

export class RopeLineRenderer {
  public line: THREE.Line;
  
  private geometry: THREE.BufferGeometry;
  private material: THREE.LineBasicMaterial;
  private positionAttribute: THREE.BufferAttribute;
  
  constructor(
    particleCount: number,
    color: THREE.Color = new THREE.Color(0x8B4513)
  ) {
    this.geometry = new THREE.BufferGeometry();
    
    const positions = new Float32Array(particleCount * 3);
    this.positionAttribute = new THREE.BufferAttribute(positions, 3);
    this.positionAttribute.setUsage(THREE.DynamicDrawUsage);
    this.geometry.setAttribute('position', this.positionAttribute);
    
    this.material = new THREE.LineBasicMaterial({
      color,
      linewidth: 2
    });
    
    this.line = new THREE.Line(this.geometry, this.material);
  }
  
  public update(positions: THREE.Vector3[]): void {
    const array = this.positionAttribute.array as Float32Array;
    
    for (let i = 0; i < positions.length; i++) {
      array[i * 3] = positions[i].x;
      array[i * 3 + 1] = positions[i].y;
      array[i * 3 + 2] = positions[i].z;
    }
    
    this.positionAttribute.needsUpdate = true;
  }
  
  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// GRAPPLING HOOK
// ============================================

export interface GrapplingHookConfig {
  maxLength: number;
  retractSpeed: number;
  extendSpeed: number;
  hookMass: number;
  stiffness: number;
}

export class GrapplingHook {
  public rope: RopePhysics;
  public renderer: RopeRenderer;
  public isAttached: boolean = false;
  public isExtending: boolean = false;
  public isRetracting: boolean = false;
  
  private config: GrapplingHookConfig;
  private attachPoint: THREE.Vector3 | null = null;
  private targetLength: number = 0;
  
  constructor(
    startPoint: THREE.Vector3,
    direction: THREE.Vector3,
    config: Partial<GrapplingHookConfig> = {}
  ) {
    this.config = {
      maxLength: 50,
      retractSpeed: 10,
      extendSpeed: 20,
      hookMass: 2,
      stiffness: 0.9,
      ...config
    };
    
    const endPoint = startPoint.clone().add(direction.clone().normalize());
    
    this.rope = new RopePhysics(startPoint, endPoint, {
      segments: 30,
      length: 1,
      stiffness: this.config.stiffness,
      mass: this.config.hookMass
    });
    
    // Pin the start (player end)
    this.rope.pinParticle(0);
    
    this.renderer = new RopeRenderer(this.rope.getPositions(), 0.03);
  }
  
  /**
   * Fire grappling hook in direction
   */
  public fire(direction: THREE.Vector3): void {
    if (this.isAttached) return;
    
    this.isExtending = true;
    this.isRetracting = false;
    
    // Give the hook particle initial velocity
    const hookParticle = this.rope.particles[this.rope.particles.length - 1];
    hookParticle.pinned = false;
    
    // Apply impulse
    const impulse = direction.clone().normalize().multiplyScalar(30);
    hookParticle.position.add(impulse.clone().multiplyScalar(0.016));
  }
  
  /**
   * Attach hook to a point
   */
  public attach(point: THREE.Vector3): void {
    this.isAttached = true;
    this.isExtending = false;
    this.attachPoint = point.clone();
    
    // Pin the hook end
    this.rope.pinParticle(this.rope.particles.length - 1, point);
  }
  
  /**
   * Detach hook
   */
  public detach(): void {
    this.isAttached = false;
    this.attachPoint = null;
    
    // Unpin the hook end
    this.rope.unpinParticle(this.rope.particles.length - 1);
  }
  
  /**
   * Start retracting rope
   */
  public startRetract(): void {
    if (!this.isAttached) return;
    this.isRetracting = true;
  }
  
  /**
   * Stop retracting
   */
  public stopRetract(): void {
    this.isRetracting = false;
  }
  
  /**
   * Update player position (start of rope)
   */
  public updatePlayerPosition(position: THREE.Vector3): void {
    this.rope.moveParticle(0, position);
  }
  
  /**
   * Get pull direction for player movement
   */
  public getPullDirection(): THREE.Vector3 | null {
    if (!this.isAttached || !this.attachPoint) return null;
    
    const playerPos = this.rope.particles[0].position;
    return this.attachPoint.clone().sub(playerPos).normalize();
  }
  
  /**
   * Get pull force magnitude
   */
  public getPullForce(): number {
    if (!this.isAttached) return 0;
    
    const currentLength = this.rope.getCurrentLength();
    const restLength = this.rope.constraints.reduce((sum, c) => sum + c.restLength, 0);
    
    // Force increases with stretch
    return Math.max(0, (currentLength - restLength) * 10);
  }
  
  /**
   * Update grappling hook
   */
  public update(deltaTime: number): void {
    // Update attached position
    if (this.isAttached && this.attachPoint) {
      this.rope.moveParticle(this.rope.particles.length - 1, this.attachPoint);
    }
    
    // Handle retraction
    if (this.isRetracting && this.isAttached) {
      // Shorten rest lengths
      for (const constraint of this.rope.constraints) {
        constraint.restLength = Math.max(
          0.1,
          constraint.restLength - this.config.retractSpeed * deltaTime / this.rope.constraints.length
        );
      }
    }
    
    // Update physics
    this.rope.update(deltaTime);
    
    // Update renderer
    this.renderer.update(this.rope.getPositions());
  }
  
  /**
   * Get the mesh for scene
   */
  public getMesh(): THREE.Mesh {
    return this.renderer.mesh;
  }
  
  /**
   * Dispose resources
   */
  public dispose(): void {
    this.renderer.dispose();
  }
}

// ============================================
// MAIN ROPE SYSTEM
// ============================================

export class RopeSystem {
  private scene: THREE.Scene;
  private ropes: Map<string, { physics: RopePhysics; renderer: RopeRenderer }> = new Map();
  private grapplingHooks: Map<string, GrapplingHook> = new Map();
  private globalColliders: RopeCollider[] = [];
  
  constructor(scene: THREE.Scene) {
    this.scene = scene;
  }
  
  /**
   * Create a rope
   */
  public createRope(
    id: string,
    startPoint: THREE.Vector3,
    endPoint: THREE.Vector3,
    config: Partial<RopeConfig> = {}
  ): { physics: RopePhysics; renderer: RopeRenderer } {
    const physics = new RopePhysics(startPoint, endPoint, config);
    const renderer = new RopeRenderer(physics.getPositions(), config.thickness);
    
    // Add global colliders
    for (const collider of this.globalColliders) {
      physics.addCollider(collider);
    }
    
    this.scene.add(renderer.mesh);
    this.ropes.set(id, { physics, renderer });
    
    return { physics, renderer };
  }
  
  /**
   * Create a grappling hook
   */
  public createGrapplingHook(
    id: string,
    startPoint: THREE.Vector3,
    direction: THREE.Vector3,
    config: Partial<GrapplingHookConfig> = {}
  ): GrapplingHook {
    const hook = new GrapplingHook(startPoint, direction, config);
    
    // Add global colliders
    for (const collider of this.globalColliders) {
      hook.rope.addCollider(collider);
    }
    
    this.scene.add(hook.getMesh());
    this.grapplingHooks.set(id, hook);
    
    return hook;
  }
  
  /**
   * Add global collider
   */
  public addGlobalCollider(collider: RopeCollider): void {
    this.globalColliders.push(collider);
    
    // Add to existing ropes
    for (const { physics } of this.ropes.values()) {
      physics.addCollider(collider);
    }
    for (const hook of this.grapplingHooks.values()) {
      hook.rope.addCollider(collider);
    }
  }
  
  /**
   * Update all ropes and hooks
   */
  public update(deltaTime: number): void {
    for (const { physics, renderer } of this.ropes.values()) {
      physics.update(deltaTime);
      renderer.update(physics.getPositions());
    }
    
    for (const hook of this.grapplingHooks.values()) {
      hook.update(deltaTime);
    }
  }
  
  /**
   * Remove rope
   */
  public removeRope(id: string): void {
    const rope = this.ropes.get(id);
    if (rope) {
      this.scene.remove(rope.renderer.mesh);
      rope.renderer.dispose();
      this.ropes.delete(id);
    }
  }
  
  /**
   * Remove grappling hook
   */
  public removeGrapplingHook(id: string): void {
    const hook = this.grapplingHooks.get(id);
    if (hook) {
      this.scene.remove(hook.getMesh());
      hook.dispose();
      this.grapplingHooks.delete(id);
    }
  }
  
  /**
   * Get rope
   */
  public getRope(id: string): { physics: RopePhysics; renderer: RopeRenderer } | undefined {
    return this.ropes.get(id);
  }
  
  /**
   * Get grappling hook
   */
  public getGrapplingHook(id: string): GrapplingHook | undefined {
    return this.grapplingHooks.get(id);
  }
  
  /**
   * Dispose all resources
   */
  public dispose(): void {
    for (const [id] of this.ropes) {
      this.removeRope(id);
    }
    for (const [id] of this.grapplingHooks) {
      this.removeGrapplingHook(id);
    }
  }
}
