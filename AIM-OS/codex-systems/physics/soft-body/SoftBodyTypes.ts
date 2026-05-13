/**
 * Soft Body Physics Types
 * Position-Based Dynamics (PBD) implementation
 */

import * as THREE from 'three';

export interface SoftBodyConfig {
  // Simulation
  substeps: number;           // PBD substeps per frame (4-10)
  iterations: number;         // Constraint iterations per substep (2-5)
  gravity: THREE.Vector3;     // Gravity acceleration
  damping: number;            // Velocity damping (0.98-0.999)
  
  // Material properties
  stretchStiffness: number;   // Distance constraint stiffness (0-1)
  bendStiffness: number;      // Bending constraint stiffness (0-1)
  volumeStiffness: number;    // Volume preservation stiffness (0-1)
  friction: number;           // Collision friction (0-1)
  
  // Collision
  collisionMargin: number;    // Collision detection margin
  selfCollision: boolean;     // Enable self-collision
  
  // Ground
  groundY: number;            // Ground plane Y position
  groundFriction: number;     // Ground friction coefficient
}

export const DEFAULT_SOFT_BODY_CONFIG: SoftBodyConfig = {
  substeps: 4,
  iterations: 3,
  gravity: new THREE.Vector3(0, -9.81, 0),
  damping: 0.99,
  stretchStiffness: 0.9,
  bendStiffness: 0.5,
  volumeStiffness: 0.8,
  friction: 0.3,
  collisionMargin: 0.01,
  selfCollision: false,
  groundY: 0,
  groundFriction: 0.5
};

export interface Particle {
  position: THREE.Vector3;
  prevPosition: THREE.Vector3;
  velocity: THREE.Vector3;
  invMass: number;            // 0 = fixed, >0 = movable
  normal: THREE.Vector3;      // For rendering
}

export interface DistanceConstraint {
  p1: number;                 // Particle index 1
  p2: number;                 // Particle index 2
  restLength: number;         // Rest distance
  stiffness: number;          // Constraint stiffness
}

export interface BendConstraint {
  p1: number;                 // Center particle
  p2: number;                 // Adjacent 1
  p3: number;                 // Adjacent 2
  p4: number;                 // Opposite particle
  restAngle: number;          // Rest dihedral angle
  stiffness: number;
}

export interface VolumeConstraint {
  indices: number[];          // Tetrahedron vertex indices
  restVolume: number;         // Rest volume
  stiffness: number;
}

export interface AttachmentConstraint {
  particleIndex: number;      // Particle to attach
  targetPosition: THREE.Vector3; // Fixed world position
  stiffness: number;          // Attachment stiffness
}

export interface SoftBody {
  id: string;
  particles: Particle[];
  distanceConstraints: DistanceConstraint[];
  bendConstraints: BendConstraint[];
  volumeConstraints: VolumeConstraint[];
  attachments: AttachmentConstraint[];
  
  // Mesh data for rendering
  geometry: THREE.BufferGeometry;
  indices: number[];
  
  // AABB for broad-phase collision
  aabbMin: THREE.Vector3;
  aabbMax: THREE.Vector3;
}

export interface CollisionSphere {
  center: THREE.Vector3;
  radius: number;
}

export interface CollisionBox {
  min: THREE.Vector3;
  max: THREE.Vector3;
}

export interface CollisionPlane {
  normal: THREE.Vector3;
  distance: number;
}

export type CollisionPrimitive = 
  | { type: 'sphere'; data: CollisionSphere }
  | { type: 'box'; data: CollisionBox }
  | { type: 'plane'; data: CollisionPlane };

