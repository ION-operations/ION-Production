import { Vec3, sub, normalize, cross, dot, length, vec } from './types';

export interface LookAtResult {
  forward: Vec3;
  right: Vec3;
  up: Vec3;
}

/**
 * Simple look-at orientation builder.
 * Returns orthonormal basis vectors facing target.
 */
export function computeLookAt(origin: Vec3, target: Vec3, worldUp: Vec3 = { x: 0, y: 1, z: 0 }): LookAtResult {
  const forward = normalize(sub(target, origin));
  // If forward parallel to up, choose a fallback up
  let right = cross(worldUp, forward);
  if (length(right) < 1e-6) {
    right = cross({ x: 0, y: 0, z: 1 }, forward);
  }
  right = normalize(right);
  const up = normalize(cross(forward, right));
  return { forward, right, up };
}

/**
 * Lightweight quaternion from look-at basis (optional helper).
 */
export interface Quaternion {
  x: number;
  y: number;
  z: number;
  w: number;
}

export function basisToQuaternion(f: Vec3, r: Vec3, u: Vec3): Quaternion {
  // Convert 3x3 rotation matrix (r,u,f as columns) to quaternion
  const m00 = r.x, m01 = u.x, m02 = f.x;
  const m10 = r.y, m11 = u.y, m12 = f.y;
  const m20 = r.z, m21 = u.z, m22 = f.z;

  const trace = m00 + m11 + m22;
  let x = 0, y = 0, z = 0, w = 1;

  if (trace > 0) {
    const s = Math.sqrt(trace + 1.0) * 2;
    w = 0.25 * s;
    x = (m21 - m12) / s;
    y = (m02 - m20) / s;
    z = (m10 - m01) / s;
  } else if (m00 > m11 && m00 > m22) {
    const s = Math.sqrt(1.0 + m00 - m11 - m22) * 2;
    w = (m21 - m12) / s;
    x = 0.25 * s;
    y = (m01 + m10) / s;
    z = (m02 + m20) / s;
  } else if (m11 > m22) {
    const s = Math.sqrt(1.0 + m11 - m00 - m22) * 2;
    w = (m02 - m20) / s;
    x = (m01 + m10) / s;
    y = 0.25 * s;
    z = (m12 + m21) / s;
  } else {
    const s = Math.sqrt(1.0 + m22 - m00 - m11) * 2;
    w = (m10 - m01) / s;
    x = (m02 + m20) / s;
    y = (m12 + m21) / s;
    z = 0.25 * s;
  }

  return { x, y, z, w };
}

