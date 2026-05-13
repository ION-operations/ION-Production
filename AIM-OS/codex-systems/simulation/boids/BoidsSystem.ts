/**
 * Boids Flocking Simulation System
 * Classic Reynolds boids with spatial hashing
 * 
 * Features:
 * - Separation, Alignment, Cohesion
 * - Spatial hashing for O(n) performance
 * - Obstacle avoidance
 * - Predator/prey dynamics
 * - Goal seeking
 * - GPU acceleration option
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface BoidConfig {
  maxSpeed: number;
  maxForce: number;
  perceptionRadius: number;
  separationRadius: number;
  separationWeight: number;
  alignmentWeight: number;
  cohesionWeight: number;
  avoidanceWeight: number;
  goalWeight: number;
  wanderWeight: number;
  bounds: THREE.Box3;
  boundaryForce: number;
}

export interface Boid {
  id: number;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  acceleration: THREE.Vector3;
  type: 'normal' | 'predator' | 'prey';
  color: THREE.Color;
  size: number;
}

export interface Obstacle {
  type: 'sphere' | 'box' | 'plane';
  position: THREE.Vector3;
  radius?: number;
  size?: THREE.Vector3;
  normal?: THREE.Vector3;
}

// ============================================
// SPATIAL HASH GRID
// ============================================

export class SpatialHashGrid {
  private cellSize: number;
  private cells: Map<string, Boid[]>;
  private bounds: THREE.Box3;
  
  constructor(cellSize: number, bounds: THREE.Box3) {
    this.cellSize = cellSize;
    this.bounds = bounds;
    this.cells = new Map();
  }
  
  private getCellKey(x: number, y: number, z: number): string {
    return `${Math.floor(x / this.cellSize)},${Math.floor(y / this.cellSize)},${Math.floor(z / this.cellSize)}`;
  }
  
  public clear(): void {
    this.cells.clear();
  }
  
  public insert(boid: Boid): void {
    const key = this.getCellKey(boid.position.x, boid.position.y, boid.position.z);
    
    if (!this.cells.has(key)) {
      this.cells.set(key, []);
    }
    
    this.cells.get(key)!.push(boid);
  }
  
  public getNeighbors(position: THREE.Vector3, radius: number): Boid[] {
    const neighbors: Boid[] = [];
    
    const minX = Math.floor((position.x - radius) / this.cellSize);
    const maxX = Math.floor((position.x + radius) / this.cellSize);
    const minY = Math.floor((position.y - radius) / this.cellSize);
    const maxY = Math.floor((position.y + radius) / this.cellSize);
    const minZ = Math.floor((position.z - radius) / this.cellSize);
    const maxZ = Math.floor((position.z + radius) / this.cellSize);
    
    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        for (let z = minZ; z <= maxZ; z++) {
          const key = `${x},${y},${z}`;
          const cell = this.cells.get(key);
          
          if (cell) {
            for (const boid of cell) {
              const dist = position.distanceTo(boid.position);
              if (dist < radius && dist > 0) {
                neighbors.push(boid);
              }
            }
          }
        }
      }
    }
    
    return neighbors;
  }
}

// ============================================
// BOID BEHAVIOR
// ============================================

export class BoidBehavior {
  /**
   * Separation: Steer to avoid crowding local flockmates
   */
  public static separation(
    boid: Boid,
    neighbors: Boid[],
    separationRadius: number
  ): THREE.Vector3 {
    const steer = new THREE.Vector3();
    let count = 0;
    
    for (const other of neighbors) {
      const dist = boid.position.distanceTo(other.position);
      
      if (dist < separationRadius && dist > 0) {
        const diff = boid.position.clone().sub(other.position);
        diff.normalize();
        diff.divideScalar(dist);  // Weight by distance
        steer.add(diff);
        count++;
      }
    }
    
    if (count > 0) {
      steer.divideScalar(count);
    }
    
    return steer;
  }
  
  /**
   * Alignment: Steer towards the average heading of local flockmates
   */
  public static alignment(boid: Boid, neighbors: Boid[]): THREE.Vector3 {
    const avgVelocity = new THREE.Vector3();
    let count = 0;
    
    for (const other of neighbors) {
      if (other.type === boid.type) {
        avgVelocity.add(other.velocity);
        count++;
      }
    }
    
    if (count > 0) {
      avgVelocity.divideScalar(count);
      avgVelocity.normalize();
    }
    
    return avgVelocity;
  }
  
  /**
   * Cohesion: Steer to move toward the average position of local flockmates
   */
  public static cohesion(boid: Boid, neighbors: Boid[]): THREE.Vector3 {
    const centerOfMass = new THREE.Vector3();
    let count = 0;
    
    for (const other of neighbors) {
      if (other.type === boid.type) {
        centerOfMass.add(other.position);
        count++;
      }
    }
    
    if (count > 0) {
      centerOfMass.divideScalar(count);
      return centerOfMass.sub(boid.position).normalize();
    }
    
    return new THREE.Vector3();
  }
  
  /**
   * Avoid obstacles
   */
  public static avoidObstacles(
    boid: Boid,
    obstacles: Obstacle[],
    lookAhead: number
  ): THREE.Vector3 {
    const steer = new THREE.Vector3();
    
    for (const obstacle of obstacles) {
      let avoidForce: THREE.Vector3 | null = null;
      
      if (obstacle.type === 'sphere' && obstacle.radius) {
        const toObstacle = obstacle.position.clone().sub(boid.position);
        const dist = toObstacle.length();
        
        if (dist < obstacle.radius + lookAhead) {
          avoidForce = boid.position.clone().sub(obstacle.position);
          avoidForce.normalize();
          avoidForce.multiplyScalar((obstacle.radius + lookAhead - dist) / lookAhead);
        }
      } else if (obstacle.type === 'plane' && obstacle.normal) {
        const dist = boid.position.dot(obstacle.normal) - obstacle.position.dot(obstacle.normal);
        
        if (dist < lookAhead && dist > 0) {
          avoidForce = obstacle.normal.clone();
          avoidForce.multiplyScalar((lookAhead - dist) / lookAhead);
        }
      }
      
      if (avoidForce) {
        steer.add(avoidForce);
      }
    }
    
    return steer;
  }
  
  /**
   * Flee from predators
   */
  public static flee(boid: Boid, predators: Boid[], fleeRadius: number): THREE.Vector3 {
    const steer = new THREE.Vector3();
    
    for (const predator of predators) {
      const dist = boid.position.distanceTo(predator.position);
      
      if (dist < fleeRadius) {
        const diff = boid.position.clone().sub(predator.position);
        diff.normalize();
        diff.multiplyScalar((fleeRadius - dist) / fleeRadius);
        steer.add(diff);
      }
    }
    
    return steer;
  }
  
  /**
   * Chase prey (for predators)
   */
  public static chase(boid: Boid, prey: Boid[], chaseRadius: number): THREE.Vector3 {
    let nearestPrey: Boid | null = null;
    let nearestDist = Infinity;
    
    for (const p of prey) {
      const dist = boid.position.distanceTo(p.position);
      if (dist < chaseRadius && dist < nearestDist) {
        nearestPrey = p;
        nearestDist = dist;
      }
    }
    
    if (nearestPrey) {
      return nearestPrey.position.clone().sub(boid.position).normalize();
    }
    
    return new THREE.Vector3();
  }
  
  /**
   * Seek a goal position
   */
  public static seek(boid: Boid, target: THREE.Vector3): THREE.Vector3 {
    return target.clone().sub(boid.position).normalize();
  }
  
  /**
   * Wander randomly
   */
  public static wander(boid: Boid, wanderRadius: number, time: number): THREE.Vector3 {
    const theta = time * 0.5 + boid.id * 0.1;
    const phi = time * 0.3 + boid.id * 0.2;
    
    const wander = new THREE.Vector3(
      Math.sin(theta) * Math.cos(phi),
      Math.sin(phi) * 0.5,
      Math.cos(theta) * Math.cos(phi)
    );
    
    return wander.normalize().multiplyScalar(wanderRadius);
  }
  
  /**
   * Stay within bounds
   */
  public static stayInBounds(
    boid: Boid,
    bounds: THREE.Box3,
    margin: number
  ): THREE.Vector3 {
    const steer = new THREE.Vector3();
    
    // X bounds
    if (boid.position.x < bounds.min.x + margin) {
      steer.x = 1;
    } else if (boid.position.x > bounds.max.x - margin) {
      steer.x = -1;
    }
    
    // Y bounds
    if (boid.position.y < bounds.min.y + margin) {
      steer.y = 1;
    } else if (boid.position.y > bounds.max.y - margin) {
      steer.y = -1;
    }
    
    // Z bounds
    if (boid.position.z < bounds.min.z + margin) {
      steer.z = 1;
    } else if (boid.position.z > bounds.max.z - margin) {
      steer.z = -1;
    }
    
    return steer;
  }
}

// ============================================
// BOIDS INSTANCED MESH RENDERER
// ============================================

export class BoidsRenderer {
  public instancedMesh: THREE.InstancedMesh;
  private dummy: THREE.Object3D;
  private colorArray: Float32Array;
  
  constructor(
    count: number,
    geometry: THREE.BufferGeometry = new THREE.ConeGeometry(0.2, 0.5, 4)
  ) {
    const material = new THREE.MeshStandardMaterial({
      vertexColors: true
    });
    
    this.instancedMesh = new THREE.InstancedMesh(geometry, material, count);
    this.instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    
    this.dummy = new THREE.Object3D();
    this.colorArray = new Float32Array(count * 3);
    
    // Initialize color attribute
    this.instancedMesh.instanceColor = new THREE.InstancedBufferAttribute(
      this.colorArray,
      3
    );
  }
  
  public update(boids: Boid[]): void {
    for (let i = 0; i < boids.length; i++) {
      const boid = boids[i];
      
      // Position
      this.dummy.position.copy(boid.position);
      
      // Rotation (face velocity direction)
      if (boid.velocity.lengthSq() > 0.001) {
        this.dummy.lookAt(boid.position.clone().add(boid.velocity));
        this.dummy.rotateX(Math.PI / 2);  // Cone points along Y, rotate to face forward
      }
      
      // Scale
      this.dummy.scale.setScalar(boid.size);
      
      this.dummy.updateMatrix();
      this.instancedMesh.setMatrixAt(i, this.dummy.matrix);
      
      // Color
      this.colorArray[i * 3] = boid.color.r;
      this.colorArray[i * 3 + 1] = boid.color.g;
      this.colorArray[i * 3 + 2] = boid.color.b;
    }
    
    this.instancedMesh.instanceMatrix.needsUpdate = true;
    if (this.instancedMesh.instanceColor) {
      this.instancedMesh.instanceColor.needsUpdate = true;
    }
  }
  
  public dispose(): void {
    this.instancedMesh.geometry.dispose();
    if (this.instancedMesh.material instanceof THREE.Material) {
      this.instancedMesh.material.dispose();
    }
  }
}

// ============================================
// MAIN BOIDS SYSTEM
// ============================================

export class BoidsSystem {
  public boids: Boid[] = [];
  public obstacles: Obstacle[] = [];
  public goals: THREE.Vector3[] = [];
  
  private config: BoidConfig;
  private spatialHash: SpatialHashGrid;
  private renderer: BoidsRenderer;
  private time: number = 0;
  
  constructor(
    count: number,
    config: Partial<BoidConfig> = {}
  ) {
    this.config = {
      maxSpeed: 5,
      maxForce: 0.5,
      perceptionRadius: 5,
      separationRadius: 2,
      separationWeight: 1.5,
      alignmentWeight: 1.0,
      cohesionWeight: 1.0,
      avoidanceWeight: 2.0,
      goalWeight: 0.5,
      wanderWeight: 0.3,
      bounds: new THREE.Box3(
        new THREE.Vector3(-50, -25, -50),
        new THREE.Vector3(50, 25, 50)
      ),
      boundaryForce: 1.0,
      ...config
    };
    
    this.spatialHash = new SpatialHashGrid(
      this.config.perceptionRadius,
      this.config.bounds
    );
    
    this.renderer = new BoidsRenderer(count);
    
    // Initialize boids
    this.initializeBoids(count);
  }
  
  private initializeBoids(count: number): void {
    const center = this.config.bounds.getCenter(new THREE.Vector3());
    const size = this.config.bounds.getSize(new THREE.Vector3());
    
    for (let i = 0; i < count; i++) {
      const boid: Boid = {
        id: i,
        position: new THREE.Vector3(
          center.x + (Math.random() - 0.5) * size.x * 0.5,
          center.y + (Math.random() - 0.5) * size.y * 0.5,
          center.z + (Math.random() - 0.5) * size.z * 0.5
        ),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2
        ),
        acceleration: new THREE.Vector3(),
        type: 'normal',
        color: new THREE.Color().setHSL(Math.random() * 0.2 + 0.5, 0.8, 0.5),
        size: 0.8 + Math.random() * 0.4
      };
      
      this.boids.push(boid);
    }
  }
  
  /**
   * Add a predator boid
   */
  public addPredator(position?: THREE.Vector3): Boid {
    const center = this.config.bounds.getCenter(new THREE.Vector3());
    
    const predator: Boid = {
      id: this.boids.length,
      position: position ?? center.clone(),
      velocity: new THREE.Vector3(Math.random() - 0.5, 0, Math.random() - 0.5),
      acceleration: new THREE.Vector3(),
      type: 'predator',
      color: new THREE.Color(0xff0000),
      size: 2
    };
    
    this.boids.push(predator);
    return predator;
  }
  
  /**
   * Add obstacle
   */
  public addObstacle(obstacle: Obstacle): void {
    this.obstacles.push(obstacle);
  }
  
  /**
   * Add goal
   */
  public addGoal(position: THREE.Vector3): void {
    this.goals.push(position);
  }
  
  /**
   * Update simulation
   */
  public update(deltaTime: number): void {
    this.time += deltaTime;
    
    // Rebuild spatial hash
    this.spatialHash.clear();
    for (const boid of this.boids) {
      this.spatialHash.insert(boid);
    }
    
    // Get predators for flee behavior
    const predators = this.boids.filter(b => b.type === 'predator');
    const prey = this.boids.filter(b => b.type === 'prey' || b.type === 'normal');
    
    // Update each boid
    for (const boid of this.boids) {
      const neighbors = this.spatialHash.getNeighbors(
        boid.position,
        this.config.perceptionRadius
      );
      
      // Calculate forces
      const separation = BoidBehavior.separation(
        boid,
        neighbors,
        this.config.separationRadius
      ).multiplyScalar(this.config.separationWeight);
      
      const alignment = BoidBehavior.alignment(boid, neighbors)
        .multiplyScalar(this.config.alignmentWeight);
      
      const cohesion = BoidBehavior.cohesion(boid, neighbors)
        .multiplyScalar(this.config.cohesionWeight);
      
      const avoidance = BoidBehavior.avoidObstacles(
        boid,
        this.obstacles,
        this.config.perceptionRadius
      ).multiplyScalar(this.config.avoidanceWeight);
      
      const wander = BoidBehavior.wander(boid, 1, this.time)
        .multiplyScalar(this.config.wanderWeight);
      
      const boundary = BoidBehavior.stayInBounds(
        boid,
        this.config.bounds,
        this.config.perceptionRadius
      ).multiplyScalar(this.config.boundaryForce);
      
      // Type-specific behavior
      let typeForce = new THREE.Vector3();
      
      if (boid.type === 'normal' && predators.length > 0) {
        typeForce = BoidBehavior.flee(boid, predators, this.config.perceptionRadius * 2)
          .multiplyScalar(3);
      } else if (boid.type === 'predator') {
        typeForce = BoidBehavior.chase(boid, prey, this.config.perceptionRadius * 3)
          .multiplyScalar(2);
      }
      
      // Goal seeking
      let goalForce = new THREE.Vector3();
      if (this.goals.length > 0) {
        const nearestGoal = this.goals.reduce((nearest, goal) => {
          const dist = boid.position.distanceTo(goal);
          const nearestDist = boid.position.distanceTo(nearest);
          return dist < nearestDist ? goal : nearest;
        }, this.goals[0]);
        
        goalForce = BoidBehavior.seek(boid, nearestGoal)
          .multiplyScalar(this.config.goalWeight);
      }
      
      // Sum forces
      boid.acceleration.set(0, 0, 0);
      boid.acceleration.add(separation);
      boid.acceleration.add(alignment);
      boid.acceleration.add(cohesion);
      boid.acceleration.add(avoidance);
      boid.acceleration.add(wander);
      boid.acceleration.add(boundary);
      boid.acceleration.add(typeForce);
      boid.acceleration.add(goalForce);
      
      // Limit force
      if (boid.acceleration.length() > this.config.maxForce) {
        boid.acceleration.normalize().multiplyScalar(this.config.maxForce);
      }
      
      // Apply acceleration
      boid.velocity.add(boid.acceleration.clone().multiplyScalar(deltaTime));
      
      // Limit speed
      const speed = boid.velocity.length();
      const maxSpeed = boid.type === 'predator'
        ? this.config.maxSpeed * 1.2
        : this.config.maxSpeed;
      
      if (speed > maxSpeed) {
        boid.velocity.normalize().multiplyScalar(maxSpeed);
      }
      
      // Update position
      boid.position.add(boid.velocity.clone().multiplyScalar(deltaTime));
    }
    
    // Update renderer
    this.renderer.update(this.boids);
  }
  
  /**
   * Get instanced mesh for scene
   */
  public getMesh(): THREE.InstancedMesh {
    return this.renderer.instancedMesh;
  }
  
  /**
   * Get boid count
   */
  public getCount(): number {
    return this.boids.length;
  }
  
  /**
   * Clear all boids
   */
  public clear(): void {
    this.boids = [];
    this.obstacles = [];
    this.goals = [];
  }
  
  /**
   * Dispose resources
   */
  public dispose(): void {
    this.renderer.dispose();
  }
}

