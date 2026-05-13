/**
 * Hair Simulation System
 * Strand-based hair physics with GPU rendering
 * 
 * Based on:
 * - AMD TressFX
 * - Follow-the-Leader (FTL) integration
 */

import * as THREE from 'three';

export interface HairConfig {
  strandCount: number;        // Number of hair strands
  segmentsPerStrand: number;  // Segments per strand
  strandLength: number;       // Base strand length
  lengthVariation: number;    // Random length variation (0-1)
  stiffness: number;          // Strand stiffness (0-1)
  damping: number;            // Velocity damping
  gravity: THREE.Vector3;     // Gravity vector
  windStrength: number;       // Wind force multiplier
  collisionRadius: number;    // Strand thickness for collision
  rootStrength: number;       // How strongly strands return to root
}

export const DEFAULT_HAIR_CONFIG: HairConfig = {
  strandCount: 1000,
  segmentsPerStrand: 8,
  strandLength: 0.3,
  lengthVariation: 0.2,
  stiffness: 0.8,
  damping: 0.95,
  gravity: new THREE.Vector3(0, -9.81, 0),
  windStrength: 1.0,
  collisionRadius: 0.002,
  rootStrength: 0.5
};

interface HairStrand {
  nodes: THREE.Vector3[];
  prevNodes: THREE.Vector3[];
  restLengths: number[];
  rootPosition: THREE.Vector3;
  rootNormal: THREE.Vector3;
  strandLength: number;
}

export class HairSimulation {
  private config: HairConfig;
  private strands: HairStrand[] = [];
  private colliders: THREE.Sphere[] = [];
  
  // Rendering
  public lineSegments: THREE.LineSegments;
  private lineGeometry: THREE.BufferGeometry;
  private linePositions: Float32Array;
  
  // Wind
  private windDirection = new THREE.Vector3(1, 0, 0);
  private windTurbulence = 0;
  private time = 0;

  constructor(
    rootPositions: THREE.Vector3[],
    rootNormals: THREE.Vector3[],
    config: Partial<HairConfig> = {}
  ) {
    this.config = { ...DEFAULT_HAIR_CONFIG, ...config };
    
    this.initializeStrands(rootPositions, rootNormals);
    this.initializeGeometry();
    
    const material = new THREE.LineBasicMaterial({
      color: 0x553311,
      transparent: true,
      opacity: 0.8
    });
    
    this.lineSegments = new THREE.LineSegments(this.lineGeometry, material);
  }

  private initializeStrands(
    rootPositions: THREE.Vector3[],
    rootNormals: THREE.Vector3[]
  ): void {
    const count = Math.min(this.config.strandCount, rootPositions.length);
    
    for (let i = 0; i < count; i++) {
      const rootPos = rootPositions[i];
      const rootNormal = rootNormals[i] || new THREE.Vector3(0, 1, 0);
      
      const lengthMod = 1 + (Math.random() - 0.5) * this.config.lengthVariation * 2;
      const strandLength = this.config.strandLength * lengthMod;
      const segmentLength = strandLength / this.config.segmentsPerStrand;
      
      const nodes: THREE.Vector3[] = [];
      const prevNodes: THREE.Vector3[] = [];
      const restLengths: number[] = [];
      
      // Initialize nodes along normal direction
      for (let j = 0; j <= this.config.segmentsPerStrand; j++) {
        const pos = rootPos.clone().addScaledVector(rootNormal, j * segmentLength);
        nodes.push(pos);
        prevNodes.push(pos.clone());
        
        if (j > 0) {
          restLengths.push(segmentLength);
        }
      }
      
      this.strands.push({
        nodes,
        prevNodes,
        restLengths,
        rootPosition: rootPos.clone(),
        rootNormal: rootNormal.clone(),
        strandLength
      });
    }
  }

  private initializeGeometry(): void {
    const totalSegments = this.strands.length * this.config.segmentsPerStrand;
    this.linePositions = new Float32Array(totalSegments * 6); // 2 points per segment * 3
    
    this.lineGeometry = new THREE.BufferGeometry();
    this.lineGeometry.setAttribute(
      'position',
      new THREE.BufferAttribute(this.linePositions, 3)
    );
  }

  /**
   * Add sphere collider
   */
  public addCollider(sphere: THREE.Sphere): void {
    this.colliders.push(sphere);
  }

  /**
   * Set wind parameters
   */
  public setWind(direction: THREE.Vector3, turbulence: number = 0.5): void {
    this.windDirection.copy(direction).normalize();
    this.windTurbulence = turbulence;
  }

  /**
   * Update simulation
   */
  public update(dt: number): void {
    this.time += dt;
    
    // Calculate wind force with turbulence
    const windForce = new THREE.Vector3();
    const turbulenceOffset = Math.sin(this.time * 3) * this.windTurbulence;
    windForce.copy(this.windDirection).multiplyScalar(
      this.config.windStrength * (1 + turbulenceOffset)
    );
    
    // Update each strand
    for (const strand of this.strands) {
      this.updateStrand(strand, windForce, dt);
    }
    
    // Update geometry
    this.updateGeometry();
  }

  private updateStrand(strand: HairStrand, windForce: THREE.Vector3, dt: number): void {
    const nodes = strand.nodes;
    const prevNodes = strand.prevNodes;
    
    // Verlet integration for each node (skip root)
    for (let i = 1; i < nodes.length; i++) {
      const node = nodes[i];
      const prev = prevNodes[i];
      
      // Calculate velocity
      const velocity = new THREE.Vector3().subVectors(node, prev);
      velocity.multiplyScalar(this.config.damping);
      
      // Store current position
      prev.copy(node);
      
      // Apply forces
      const acceleration = new THREE.Vector3()
        .copy(this.config.gravity)
        .add(windForce);
      
      // Verlet step
      node.add(velocity);
      node.addScaledVector(acceleration, dt * dt);
    }
    
    // Constraint solving (multiple iterations for stability)
    for (let iter = 0; iter < 3; iter++) {
      // Pin root
      nodes[0].copy(strand.rootPosition);
      
      // Distance constraints (Follow-the-Leader)
      for (let i = 1; i < nodes.length; i++) {
        const restLength = strand.restLengths[i - 1];
        const diff = new THREE.Vector3().subVectors(nodes[i], nodes[i - 1]);
        const dist = diff.length();
        
        if (dist > 0.0001) {
          const correction = diff.multiplyScalar((dist - restLength) / dist);
          
          // Move child node (parent is fixed in FTL)
          nodes[i].sub(correction);
        }
      }
      
      // Stiffness constraint (shape preservation)
      if (this.config.stiffness > 0) {
        for (let i = 1; i < nodes.length; i++) {
          const t = i / (nodes.length - 1);
          const restPos = strand.rootPosition.clone()
            .addScaledVector(strand.rootNormal, t * strand.strandLength);
          
          const toRest = new THREE.Vector3().subVectors(restPos, nodes[i]);
          const stiffnessFactor = this.config.stiffness * this.config.rootStrength * (1 - t);
          nodes[i].addScaledVector(toRest, stiffnessFactor * 0.1);
        }
      }
      
      // Collision handling
      for (let i = 1; i < nodes.length; i++) {
        for (const collider of this.colliders) {
          const toNode = new THREE.Vector3().subVectors(nodes[i], collider.center);
          const dist = toNode.length();
          const minDist = collider.radius + this.config.collisionRadius;
          
          if (dist < minDist && dist > 0) {
            toNode.normalize();
            nodes[i].copy(collider.center).addScaledVector(toNode, minDist);
          }
        }
      }
    }
  }

  private updateGeometry(): void {
    let offset = 0;
    
    for (const strand of this.strands) {
      for (let i = 0; i < strand.nodes.length - 1; i++) {
        const p1 = strand.nodes[i];
        const p2 = strand.nodes[i + 1];
        
        this.linePositions[offset++] = p1.x;
        this.linePositions[offset++] = p1.y;
        this.linePositions[offset++] = p1.z;
        this.linePositions[offset++] = p2.x;
        this.linePositions[offset++] = p2.y;
        this.linePositions[offset++] = p2.z;
      }
    }
    
    this.lineGeometry.attributes.position.needsUpdate = true;
  }

  /**
   * Generate root positions on a mesh surface
   */
  public static generateRootsOnMesh(
    geometry: THREE.BufferGeometry,
    count: number
  ): { positions: THREE.Vector3[]; normals: THREE.Vector3[] } {
    const positions: THREE.Vector3[] = [];
    const normals: THREE.Vector3[] = [];
    
    const posAttr = geometry.getAttribute('position');
    const normAttr = geometry.getAttribute('normal');
    const indices = geometry.index;
    
    if (!indices) return { positions, normals };
    
    // Calculate face areas for weighted random selection
    const faceCount = indices.count / 3;
    const faceAreas: number[] = [];
    let totalArea = 0;
    
    const v0 = new THREE.Vector3();
    const v1 = new THREE.Vector3();
    const v2 = new THREE.Vector3();
    const edge1 = new THREE.Vector3();
    const edge2 = new THREE.Vector3();
    
    for (let i = 0; i < faceCount; i++) {
      const i0 = indices.getX(i * 3);
      const i1 = indices.getX(i * 3 + 1);
      const i2 = indices.getX(i * 3 + 2);
      
      v0.fromBufferAttribute(posAttr, i0);
      v1.fromBufferAttribute(posAttr, i1);
      v2.fromBufferAttribute(posAttr, i2);
      
      edge1.subVectors(v1, v0);
      edge2.subVectors(v2, v0);
      
      const area = edge1.cross(edge2).length() * 0.5;
      faceAreas.push(area);
      totalArea += area;
    }
    
    // Generate random points
    for (let i = 0; i < count; i++) {
      // Select random face weighted by area
      let r = Math.random() * totalArea;
      let faceIndex = 0;
      
      for (let f = 0; f < faceCount; f++) {
        r -= faceAreas[f];
        if (r <= 0) {
          faceIndex = f;
          break;
        }
      }
      
      // Get face vertices
      const i0 = indices.getX(faceIndex * 3);
      const i1 = indices.getX(faceIndex * 3 + 1);
      const i2 = indices.getX(faceIndex * 3 + 2);
      
      v0.fromBufferAttribute(posAttr, i0);
      v1.fromBufferAttribute(posAttr, i1);
      v2.fromBufferAttribute(posAttr, i2);
      
      // Random barycentric coordinates
      let u = Math.random();
      let v = Math.random();
      if (u + v > 1) {
        u = 1 - u;
        v = 1 - v;
      }
      const w = 1 - u - v;
      
      // Interpolate position
      const pos = new THREE.Vector3()
        .addScaledVector(v0, w)
        .addScaledVector(v1, u)
        .addScaledVector(v2, v);
      
      positions.push(pos);
      
      // Interpolate normal
      const n0 = new THREE.Vector3().fromBufferAttribute(normAttr, i0);
      const n1 = new THREE.Vector3().fromBufferAttribute(normAttr, i1);
      const n2 = new THREE.Vector3().fromBufferAttribute(normAttr, i2);
      
      const normal = new THREE.Vector3()
        .addScaledVector(n0, w)
        .addScaledVector(n1, u)
        .addScaledVector(n2, v)
        .normalize();
      
      normals.push(normal);
    }
    
    return { positions, normals };
  }

  public dispose(): void {
    this.lineGeometry.dispose();
    (this.lineSegments.material as THREE.Material).dispose();
  }
}

