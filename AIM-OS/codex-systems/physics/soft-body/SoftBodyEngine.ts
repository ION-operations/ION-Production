/**
 * Soft Body Physics Engine
 * Position-Based Dynamics (PBD) implementation
 * 
 * Based on Müller et al. "Position Based Dynamics" (2006)
 * Extended with XPBD stiffness compliance
 */

import * as THREE from 'three';
import {
  SoftBodyConfig,
  SoftBody,
  Particle,
  DistanceConstraint,
  BendConstraint,
  VolumeConstraint,
  AttachmentConstraint,
  CollisionPrimitive,
  DEFAULT_SOFT_BODY_CONFIG
} from './SoftBodyTypes';

export class SoftBodyEngine {
  private config: SoftBodyConfig;
  private bodies: SoftBody[] = [];
  private colliders: CollisionPrimitive[] = [];
  
  // Temp vectors for constraint solving
  private readonly _v1 = new THREE.Vector3();
  private readonly _v2 = new THREE.Vector3();
  private readonly _correction = new THREE.Vector3();

  constructor(config: Partial<SoftBodyConfig> = {}) {
    this.config = { ...DEFAULT_SOFT_BODY_CONFIG, ...config };
  }

  /**
   * Create soft body from mesh geometry
   */
  public createFromGeometry(
    geometry: THREE.BufferGeometry,
    fixedVertices: number[] = []
  ): SoftBody {
    const posAttr = geometry.getAttribute('position') as THREE.BufferAttribute;
    const indexAttr = geometry.getIndex();
    
    if (!indexAttr) {
      throw new Error('Geometry must be indexed');
    }

    const particles: Particle[] = [];
    const distanceConstraints: DistanceConstraint[] = [];
    const bendConstraints: BendConstraint[] = [];

    // Create particles from vertices
    for (let i = 0; i < posAttr.count; i++) {
      const pos = new THREE.Vector3(
        posAttr.getX(i),
        posAttr.getY(i),
        posAttr.getZ(i)
      );
      
      particles.push({
        position: pos.clone(),
        prevPosition: pos.clone(),
        velocity: new THREE.Vector3(),
        invMass: fixedVertices.includes(i) ? 0 : 1,
        normal: new THREE.Vector3(0, 1, 0)
      });
    }

    // Create distance constraints from edges
    const edgeMap = new Map<string, boolean>();
    const indices = Array.from(indexAttr.array);
    
    for (let i = 0; i < indices.length; i += 3) {
      const i0 = indices[i];
      const i1 = indices[i + 1];
      const i2 = indices[i + 2];
      
      this.addEdgeConstraint(i0, i1, particles, distanceConstraints, edgeMap);
      this.addEdgeConstraint(i1, i2, particles, distanceConstraints, edgeMap);
      this.addEdgeConstraint(i2, i0, particles, distanceConstraints, edgeMap);
    }

    // Create bend constraints for adjacent triangles
    this.createBendConstraints(indices, particles, bendConstraints);

    const body: SoftBody = {
      id: THREE.MathUtils.generateUUID(),
      particles,
      distanceConstraints,
      bendConstraints,
      volumeConstraints: [],
      attachments: [],
      geometry: geometry.clone(),
      indices,
      aabbMin: new THREE.Vector3(),
      aabbMax: new THREE.Vector3()
    };

    this.updateAABB(body);
    this.bodies.push(body);
    
    return body;
  }

  private addEdgeConstraint(
    i0: number,
    i1: number,
    particles: Particle[],
    constraints: DistanceConstraint[],
    edgeMap: Map<string, boolean>
  ): void {
    const key = i0 < i1 ? `${i0}-${i1}` : `${i1}-${i0}`;
    
    if (edgeMap.has(key)) return;
    edgeMap.set(key, true);
    
    const restLength = particles[i0].position.distanceTo(particles[i1].position);
    
    constraints.push({
      p1: i0,
      p2: i1,
      restLength,
      stiffness: this.config.stretchStiffness
    });
  }

  private createBendConstraints(
    indices: number[],
    particles: Particle[],
    constraints: BendConstraint[]
  ): void {
    // Build adjacency map: edge -> [tri1, tri2]
    const edgeToTris = new Map<string, number[]>();
    
    for (let t = 0; t < indices.length / 3; t++) {
      const base = t * 3;
      const tri = [indices[base], indices[base + 1], indices[base + 2]];
      
      for (let e = 0; e < 3; e++) {
        const i0 = tri[e];
        const i1 = tri[(e + 1) % 3];
        const key = i0 < i1 ? `${i0}-${i1}` : `${i1}-${i0}`;
        
        if (!edgeToTris.has(key)) {
          edgeToTris.set(key, []);
        }
        edgeToTris.get(key)!.push(t);
      }
    }
    
    // Create bend constraint for each shared edge
    edgeToTris.forEach((tris, edgeKey) => {
      if (tris.length !== 2) return;
      
      const [a, b] = edgeKey.split('-').map(Number);
      const t0 = tris[0];
      const t1 = tris[1];
      
      // Find opposite vertices
      const tri0 = [indices[t0 * 3], indices[t0 * 3 + 1], indices[t0 * 3 + 2]];
      const tri1 = [indices[t1 * 3], indices[t1 * 3 + 1], indices[t1 * 3 + 2]];
      
      const c = tri0.find(v => v !== a && v !== b)!;
      const d = tri1.find(v => v !== a && v !== b)!;
      
      // Calculate rest dihedral angle
      const restAngle = this.calculateDihedralAngle(
        particles[a].position,
        particles[b].position,
        particles[c].position,
        particles[d].position
      );
      
      constraints.push({
        p1: a,
        p2: b,
        p3: c,
        p4: d,
        restAngle,
        stiffness: this.config.bendStiffness
      });
    });
  }

  private calculateDihedralAngle(
    a: THREE.Vector3,
    b: THREE.Vector3,
    c: THREE.Vector3,
    d: THREE.Vector3
  ): number {
    const ab = this._v1.subVectors(b, a);
    const ac = new THREE.Vector3().subVectors(c, a);
    const ad = new THREE.Vector3().subVectors(d, a);
    
    const n1 = new THREE.Vector3().crossVectors(ab, ac).normalize();
    const n2 = new THREE.Vector3().crossVectors(ab, ad).normalize();
    
    return Math.acos(THREE.MathUtils.clamp(n1.dot(n2), -1, 1));
  }

  /**
   * Add collision primitive
   */
  public addCollider(collider: CollisionPrimitive): void {
    this.colliders.push(collider);
  }

  /**
   * Main simulation step
   */
  public step(dt: number): void {
    const substepDt = dt / this.config.substeps;
    
    for (let s = 0; s < this.config.substeps; s++) {
      for (const body of this.bodies) {
        // 1. Predict positions (integrate gravity + velocity)
        this.integrate(body, substepDt);
        
        // 2. Solve constraints
        for (let i = 0; i < this.config.iterations; i++) {
          this.solveDistanceConstraints(body);
          this.solveBendConstraints(body);
          this.solveVolumeConstraints(body);
          this.solveAttachments(body);
        }
        
        // 3. Handle collisions
        this.handleCollisions(body);
        
        // 4. Update velocities
        this.updateVelocities(body, substepDt);
        
        // 5. Apply damping
        this.applyDamping(body);
      }
    }
    
    // Update geometry for rendering
    for (const body of this.bodies) {
      this.updateGeometry(body);
      this.updateAABB(body);
    }
  }

  private integrate(body: SoftBody, dt: number): void {
    for (const p of body.particles) {
      if (p.invMass === 0) continue;
      
      p.velocity.addScaledVector(this.config.gravity, dt);
      p.prevPosition.copy(p.position);
      p.position.addScaledVector(p.velocity, dt);
    }
  }

  private solveDistanceConstraints(body: SoftBody): void {
    for (const c of body.distanceConstraints) {
      const p1 = body.particles[c.p1];
      const p2 = body.particles[c.p2];
      
      if (p1.invMass === 0 && p2.invMass === 0) continue;
      
      this._v1.subVectors(p2.position, p1.position);
      const currentLength = this._v1.length();
      
      if (currentLength < 0.0001) continue;
      
      const error = currentLength - c.restLength;
      const totalInvMass = p1.invMass + p2.invMass;
      
      if (totalInvMass < 0.0001) continue;
      
      // XPBD compliance factor
      const alpha = 1.0 / (c.stiffness + 0.0001);
      const dlambda = -error / (totalInvMass + alpha);
      
      this._correction.copy(this._v1).normalize().multiplyScalar(dlambda);
      
      if (p1.invMass > 0) {
        p1.position.addScaledVector(this._correction, -p1.invMass);
      }
      if (p2.invMass > 0) {
        p2.position.addScaledVector(this._correction, p2.invMass);
      }
    }
  }

  private solveBendConstraints(body: SoftBody): void {
    // Simplified bending - just maintain distance between opposite vertices
    for (const c of body.bendConstraints) {
      const p3 = body.particles[c.p3];
      const p4 = body.particles[c.p4];
      
      if (p3.invMass === 0 && p4.invMass === 0) continue;
      
      // Distance between opposite vertices
      this._v1.subVectors(p4.position, p3.position);
      const currentDist = this._v1.length();
      
      if (currentDist < 0.0001) continue;
      
      // Compute rest distance from rest angle
      const restDist = currentDist; // Simplified - maintain current as rest
      const error = currentDist - restDist;
      const totalInvMass = p3.invMass + p4.invMass;
      
      if (totalInvMass < 0.0001 || Math.abs(error) < 0.0001) continue;
      
      const correction = error * c.stiffness * 0.5;
      this._correction.copy(this._v1).normalize().multiplyScalar(correction);
      
      if (p3.invMass > 0) {
        p3.position.addScaledVector(this._correction, p3.invMass / totalInvMass);
      }
      if (p4.invMass > 0) {
        p4.position.addScaledVector(this._correction, -p4.invMass / totalInvMass);
      }
    }
  }

  private solveVolumeConstraints(body: SoftBody): void {
    for (const c of body.volumeConstraints) {
      // Tetrahedron volume preservation
      const [i0, i1, i2, i3] = c.indices;
      const p0 = body.particles[i0];
      const p1 = body.particles[i1];
      const p2 = body.particles[i2];
      const p3 = body.particles[i3];
      
      // Calculate current volume
      const v01 = new THREE.Vector3().subVectors(p1.position, p0.position);
      const v02 = new THREE.Vector3().subVectors(p2.position, p0.position);
      const v03 = new THREE.Vector3().subVectors(p3.position, p0.position);
      
      const currentVolume = v01.dot(new THREE.Vector3().crossVectors(v02, v03)) / 6.0;
      const volumeError = currentVolume - c.restVolume;
      
      if (Math.abs(volumeError) < 0.0001) continue;
      
      // Gradient of volume w.r.t. each vertex
      const grad0 = new THREE.Vector3().crossVectors(
        new THREE.Vector3().subVectors(p2.position, p1.position),
        new THREE.Vector3().subVectors(p3.position, p1.position)
      ).multiplyScalar(1/6);
      
      const grad1 = new THREE.Vector3().crossVectors(
        new THREE.Vector3().subVectors(p0.position, p2.position),
        new THREE.Vector3().subVectors(p3.position, p2.position)
      ).multiplyScalar(1/6);
      
      const grad2 = new THREE.Vector3().crossVectors(
        new THREE.Vector3().subVectors(p1.position, p0.position),
        new THREE.Vector3().subVectors(p3.position, p0.position)
      ).multiplyScalar(1/6);
      
      const grad3 = new THREE.Vector3().crossVectors(
        new THREE.Vector3().subVectors(p0.position, p1.position),
        new THREE.Vector3().subVectors(p2.position, p1.position)
      ).multiplyScalar(1/6);
      
      // Compute lambda
      let sumGradSq = 0;
      sumGradSq += p0.invMass * grad0.lengthSq();
      sumGradSq += p1.invMass * grad1.lengthSq();
      sumGradSq += p2.invMass * grad2.lengthSq();
      sumGradSq += p3.invMass * grad3.lengthSq();
      
      if (sumGradSq < 0.0001) continue;
      
      const lambda = -volumeError * c.stiffness / sumGradSq;
      
      if (p0.invMass > 0) p0.position.addScaledVector(grad0, lambda * p0.invMass);
      if (p1.invMass > 0) p1.position.addScaledVector(grad1, lambda * p1.invMass);
      if (p2.invMass > 0) p2.position.addScaledVector(grad2, lambda * p2.invMass);
      if (p3.invMass > 0) p3.position.addScaledVector(grad3, lambda * p3.invMass);
    }
  }

  private solveAttachments(body: SoftBody): void {
    for (const a of body.attachments) {
      const p = body.particles[a.particleIndex];
      if (p.invMass === 0) continue;
      
      this._v1.subVectors(a.targetPosition, p.position);
      p.position.addScaledVector(this._v1, a.stiffness);
    }
  }

  private handleCollisions(body: SoftBody): void {
    for (const p of body.particles) {
      if (p.invMass === 0) continue;
      
      // Ground collision
      if (p.position.y < this.config.groundY + this.config.collisionMargin) {
        p.position.y = this.config.groundY + this.config.collisionMargin;
        
        // Friction
        const vy = p.position.y - p.prevPosition.y;
        if (vy < 0) {
          const vx = p.position.x - p.prevPosition.x;
          const vz = p.position.z - p.prevPosition.z;
          p.position.x -= vx * this.config.groundFriction;
          p.position.z -= vz * this.config.groundFriction;
        }
      }
      
      // Primitive colliders
      for (const collider of this.colliders) {
        this.resolveCollision(p, collider);
      }
    }
  }

  private resolveCollision(p: Particle, collider: CollisionPrimitive): void {
    const margin = this.config.collisionMargin;
    
    switch (collider.type) {
      case 'sphere': {
        const { center, radius } = collider.data;
        this._v1.subVectors(p.position, center);
        const dist = this._v1.length();
        const minDist = radius + margin;
        
        if (dist < minDist && dist > 0.0001) {
          this._v1.normalize().multiplyScalar(minDist);
          p.position.copy(center).add(this._v1);
        }
        break;
      }
      
      case 'box': {
        const { min, max } = collider.data;
        // Simple AABB collision
        if (
          p.position.x > min.x - margin && p.position.x < max.x + margin &&
          p.position.y > min.y - margin && p.position.y < max.y + margin &&
          p.position.z > min.z - margin && p.position.z < max.z + margin
        ) {
          // Push out in shortest direction
          const dx1 = p.position.x - min.x;
          const dx2 = max.x - p.position.x;
          const dy1 = p.position.y - min.y;
          const dy2 = max.y - p.position.y;
          const dz1 = p.position.z - min.z;
          const dz2 = max.z - p.position.z;
          
          const minD = Math.min(dx1, dx2, dy1, dy2, dz1, dz2);
          
          if (minD === dx1) p.position.x = min.x - margin;
          else if (minD === dx2) p.position.x = max.x + margin;
          else if (minD === dy1) p.position.y = min.y - margin;
          else if (minD === dy2) p.position.y = max.y + margin;
          else if (minD === dz1) p.position.z = min.z - margin;
          else p.position.z = max.z + margin;
        }
        break;
      }
      
      case 'plane': {
        const { normal, distance } = collider.data;
        const d = p.position.dot(normal) - distance;
        if (d < margin) {
          p.position.addScaledVector(normal, margin - d);
        }
        break;
      }
    }
  }

  private updateVelocities(body: SoftBody, dt: number): void {
    const invDt = 1.0 / dt;
    
    for (const p of body.particles) {
      if (p.invMass === 0) continue;
      p.velocity.subVectors(p.position, p.prevPosition).multiplyScalar(invDt);
    }
  }

  private applyDamping(body: SoftBody): void {
    for (const p of body.particles) {
      if (p.invMass === 0) continue;
      p.velocity.multiplyScalar(this.config.damping);
    }
  }

  private updateGeometry(body: SoftBody): void {
    const posAttr = body.geometry.getAttribute('position') as THREE.BufferAttribute;
    
    for (let i = 0; i < body.particles.length; i++) {
      const p = body.particles[i];
      posAttr.setXYZ(i, p.position.x, p.position.y, p.position.z);
    }
    
    posAttr.needsUpdate = true;
    body.geometry.computeVertexNormals();
  }

  private updateAABB(body: SoftBody): void {
    body.aabbMin.set(Infinity, Infinity, Infinity);
    body.aabbMax.set(-Infinity, -Infinity, -Infinity);
    
    for (const p of body.particles) {
      body.aabbMin.min(p.position);
      body.aabbMax.max(p.position);
    }
  }

  /**
   * Add attachment to fix particle in space
   */
  public addAttachment(body: SoftBody, particleIndex: number, stiffness: number = 1.0): void {
    const p = body.particles[particleIndex];
    body.attachments.push({
      particleIndex,
      targetPosition: p.position.clone(),
      stiffness
    });
  }

  /**
   * Move attachment target
   */
  public moveAttachment(body: SoftBody, attachmentIndex: number, position: THREE.Vector3): void {
    body.attachments[attachmentIndex].targetPosition.copy(position);
  }

  /**
   * Apply impulse to particle
   */
  public applyImpulse(body: SoftBody, particleIndex: number, impulse: THREE.Vector3): void {
    const p = body.particles[particleIndex];
    if (p.invMass > 0) {
      p.velocity.add(impulse);
    }
  }

  /**
   * Get all bodies
   */
  public getBodies(): SoftBody[] {
    return this.bodies;
  }

  /**
   * Remove body
   */
  public removeBody(body: SoftBody): void {
    const index = this.bodies.indexOf(body);
    if (index >= 0) {
      this.bodies.splice(index, 1);
    }
  }

  /**
   * Clear all
   */
  public dispose(): void {
    for (const body of this.bodies) {
      body.geometry.dispose();
    }
    this.bodies = [];
    this.colliders = [];
  }
}

