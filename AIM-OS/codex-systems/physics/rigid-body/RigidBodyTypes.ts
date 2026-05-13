export type ShapeType = 'sphere' | 'box' | 'capsule' | 'plane';

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export interface Quaternion {
  x: number;
  y: number;
  z: number;
  w: number;
}

export interface Transform {
  position: Vec3;
  rotation: Quaternion;
}

export interface RigidBodyConfig {
  mass: number;
  restitution: number;
  friction: number;
  linearDamping?: number;
  angularDamping?: number;
  shape: CollisionShape;
  useGravity?: boolean;
}

export interface RigidBodyState {
  transform: Transform;
  linearVelocity: Vec3;
  angularVelocity: Vec3;
  forces: Vec3;
  torques: Vec3;
  invMass: number;
  invInertia: Vec3; // diagonal inertia in local space
}

export interface CollisionShape {
  type: ShapeType;
  // parameters per type
  radius?: number; // sphere/capsule
  halfExtents?: Vec3; // box
  height?: number; // capsule
  normal?: Vec3; // plane
  constant?: number; // plane offset
}

export interface ContactPoint {
  position: Vec3;
  normal: Vec3;
  penetration: number;
  impulse?: number;
}

export interface ContactManifold {
  bodyA: number;
  bodyB: number;
  contacts: ContactPoint[];
}

export interface JointConstraint {
  bodyA: number;
  bodyB: number;
  anchorA: Vec3;
  anchorB: Vec3;
  type: 'ball' | 'hinge';
}

