/**
 * Particle Life System
 * Emergent patterns from attraction/repulsion matrices (artificial chemistry)
 *
 * Features:
 * - Arbitrary species count with interaction matrix
 * - Attraction/repulsion force falloff
 * - Collision radius (soft)
 * - Spatial hashing for O(n) neighbor queries
 * - Boundary modes: wrap / clamp
 * - Simple integrator (Euler) with damping
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface Species {
  id: number;
  color: THREE.Color;
  mass: number;
  radius: number;
}

export interface InteractionMatrix {
  /** matrix[a][b] = force from species b on a (positive = attract, negative = repel) */
  matrix: number[][];
  falloff: number; // force falloff exponent
  maxDistance: number;
}

export interface ParticleLifeConfig {
  bounds: THREE.Box3;
  wrap: boolean; // if true, wrap; else clamp
  damping: number;
  timeStep: number;
  maxNeighbors: number;
}

export interface Particle {
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  species: number;
}

// ============================================
// SPATIAL HASH
// ============================================

class SpatialHash {
  private cellSize: number;
  private map: Map<string, number[]> = new Map();

  constructor(cellSize: number) {
    this.cellSize = cellSize;
  }

  public clear(): void {
    this.map.clear();
  }

  public insert(index: number, position: THREE.Vector3): void {
    const key = this.key(position);
    if (!this.map.has(key)) this.map.set(key, []);
    this.map.get(key)!.push(index);
  }

  public query(position: THREE.Vector3, radius: number): number[] {
    const results: number[] = [];
    const min = position.clone().addScalar(-radius);
    const max = position.clone().addScalar(radius);

    const minCell = this.cell(min);
    const maxCell = this.cell(max);

    for (let x = minCell.x; x <= maxCell.x; x++) {
      for (let y = minCell.y; y <= maxCell.y; y++) {
        for (let z = minCell.z; z <= maxCell.z; z++) {
          const key = `${x},${y},${z}`;
          const cell = this.map.get(key);
          if (cell) results.push(...cell);
        }
      }
    }
    return results;
  }

  private cell(p: THREE.Vector3): THREE.Vector3 {
    return new THREE.Vector3(
      Math.floor(p.x / this.cellSize),
      Math.floor(p.y / this.cellSize),
      Math.floor(p.z / this.cellSize)
    );
  }

  private key(p: THREE.Vector3): string {
    const c = this.cell(p);
    return `${c.x},${c.y},${c.z}`;
  }
}

// ============================================
// PARTICLE LIFE SIMULATION
// ============================================

export class ParticleLifeSystem {
  private particles: Particle[] = [];
  private species: Species[] = [];
  private interactions: InteractionMatrix;
  private config: ParticleLifeConfig;
  private hash: SpatialHash;

  constructor(
    species: Species[],
    interactions: InteractionMatrix,
    config: Partial<ParticleLifeConfig> = {}
  ) {
    this.species = species;
    this.interactions = interactions;
    this.config = {
      bounds: new THREE.Box3(
        new THREE.Vector3(-20, -20, -20),
        new THREE.Vector3(20, 20, 20)
      ),
      wrap: true,
      damping: 0.99,
      timeStep: 0.016,
      maxNeighbors: 32,
      ...config,
    };

    this.hash = new SpatialHash(interactions.maxDistance);
  }

  /**
   * Initialize random particles.
   */
  public spawn(count: number): void {
    for (let i = 0; i < count; i++) {
      const s = this.species[Math.floor(Math.random() * this.species.length)];
      const position = new THREE.Vector3(
        THREE.MathUtils.lerp(this.config.bounds.min.x, this.config.bounds.max.x, Math.random()),
        THREE.MathUtils.lerp(this.config.bounds.min.y, this.config.bounds.max.y, Math.random()),
        THREE.MathUtils.lerp(this.config.bounds.min.z, this.config.bounds.max.z, Math.random())
      );

      this.particles.push({
        position,
        velocity: new THREE.Vector3(),
        species: s.id,
      });
    }
  }

  /**
   * Step simulation.
   */
  public update(): void {
    const dt = this.config.timeStep;

    // Rebuild spatial hash
    this.hash.clear();
    for (let i = 0; i < this.particles.length; i++) {
      this.hash.insert(i, this.particles[i].position);
    }

    // Forces
    const maxDist = this.interactions.maxDistance;
    const maxDistSq = maxDist * maxDist;
    const falloff = this.interactions.falloff;

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      const speciesA = p.species;

      let fx = 0, fy = 0, fz = 0;

      const neighbors = this.hash.query(p.position, maxDist);
      let neighborCount = 0;

      for (const nIdx of neighbors) {
        if (nIdx === i) continue;
        const n = this.particles[nIdx];

        const dx = n.position.x - p.position.x;
        const dy = n.position.y - p.position.y;
        const dz = n.position.z - p.position.z;
        const distSq = dx * dx + dy * dy + dz * dz;
        if (distSq < 1e-6 || distSq > maxDistSq) continue;

        const dist = Math.sqrt(distSq);
        const speciesB = n.species;
        const forceMag = this.interactions.matrix[speciesA][speciesB];

        // Attraction/repulsion with falloff
        const fall = Math.pow(1 - dist / maxDist, falloff);
        const f = (forceMag * fall) / (dist + 1e-4);

        fx += dx * f;
        fy += dy * f;
        fz += dz * f;

        neighborCount++;
        if (neighborCount >= this.config.maxNeighbors) break;
      }

      // Integrate
      p.velocity.x = (p.velocity.x + fx * dt) * this.config.damping;
      p.velocity.y = (p.velocity.y + fy * dt) * this.config.damping;
      p.velocity.z = (p.velocity.z + fz * dt) * this.config.damping;

      p.position.x += p.velocity.x * dt;
      p.position.y += p.velocity.y * dt;
      p.position.z += p.velocity.z * dt;

      // Bounds
      this.handleBounds(p);
    }
  }

  private handleBounds(p: Particle): void {
    const b = this.config.bounds;
    if (this.config.wrap) {
      if (p.position.x < b.min.x) p.position.x = b.max.x;
      if (p.position.x > b.max.x) p.position.x = b.min.x;
      if (p.position.y < b.min.y) p.position.y = b.max.y;
      if (p.position.y > b.max.y) p.position.y = b.min.y;
      if (p.position.z < b.min.z) p.position.z = b.max.z;
      if (p.position.z > b.max.z) p.position.z = b.min.z;
    } else {
      p.position.clamp(b.min, b.max);
      p.velocity.multiplyScalar(0.5);
    }
  }

  public getParticles(): Particle[] {
    return this.particles;
  }
}

