/**
 * Vector3D utility functions
 */

import { Vector3D } from '../types';

export function vector_add(v1: Vector3D, v2: Vector3D): Vector3D {
  return { x: v1.x + v2.x, y: v1.y + v2.y, z: v1.z + v2.z };
}

export function vector_subtract(v1: Vector3D, v2: Vector3D): Vector3D {
  return { x: v1.x - v2.x, y: v1.y - v2.y, z: v1.z - v2.z };
}

export function vector_scale(v: Vector3D, s: number): Vector3D {
  return { x: v.x * s, y: v.y * s, z: v.z * s };
}

export function vector_magnitude(v: Vector3D): number {
  return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

export function vector_normalize(v: Vector3D): Vector3D {
  const mag = vector_magnitude(v);
  if (mag < 1e-10) return { x: 0, y: 0, z: 0 };
  return vector_scale(v, 1.0 / mag);
}

export function vector_dot(v1: Vector3D, v2: Vector3D): number {
  return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
}

export function vector_cross(v1: Vector3D, v2: Vector3D): Vector3D {
  return {
    x: v1.y * v2.z - v1.z * v2.y,
    y: v1.z * v2.x - v1.x * v2.z,
    z: v1.x * v2.y - v1.y * v2.x
  };
}

