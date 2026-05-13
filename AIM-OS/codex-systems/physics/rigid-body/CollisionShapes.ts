import { CollisionShape, Vec3 } from './RigidBodyTypes';

export function vec(x = 0, y = 0, z = 0): Vec3 {
  return { x, y, z };
}

export function dot(a: Vec3, b: Vec3): number {
  return a.x * b.x + a.y * b.y + a.z * b.z;
}

export function sub(a: Vec3, b: Vec3): Vec3 {
  return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
}

export function length(v: Vec3): number {
  return Math.hypot(v.x, v.y, v.z);
}

export function normalize(v: Vec3): Vec3 {
  const len = length(v) || 1;
  return { x: v.x / len, y: v.y / len, z: v.z / len };
}

// Support functions for SAT/GJK will be added here later.

export function sphereSupport(direction: Vec3, radius: number): Vec3 {
  const dir = normalize(direction);
  return { x: dir.x * radius, y: dir.y * radius, z: dir.z * radius };
}

export function boxSupport(direction: Vec3, halfExtents: Vec3): Vec3 {
  return {
    x: direction.x >= 0 ? halfExtents.x : -halfExtents.x,
    y: direction.y >= 0 ? halfExtents.y : -halfExtents.y,
    z: direction.z >= 0 ? halfExtents.z : -halfExtents.z
  };
}

// Axis-aligned bounding box from center/half extents (ignores rotation)
export function aabbFromBox(center: Vec3, halfExtents: Vec3) {
  return {
    min: { x: center.x - halfExtents.x, y: center.y - halfExtents.y, z: center.z - halfExtents.z },
    max: { x: center.x + halfExtents.x, y: center.y + halfExtents.y, z: center.z + halfExtents.z }
  };
}

