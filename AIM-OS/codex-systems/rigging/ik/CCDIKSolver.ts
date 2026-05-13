import { Vec3, clone, distance, sub, cross, dot, length, normalize, add, scale } from './types';

export interface CCDIKOptions {
  tolerance?: number;
  maxIterations?: number;
  stepFactor?: number; // 0-1 rotation lerp for stability
}

export interface CCDIKResult {
  positions: Vec3[];
  reached: boolean;
  iterations: number;
}

/**
 * CCD IK solver (Cyclic Coordinate Descent)
 * Reference: encyclopedia/02_Animation/Character/INVERSE_KINEMATICS_COMPLETE.md
 */
export class CCDIKSolver {
  private readonly tolerance: number;
  private readonly maxIterations: number;
  private readonly stepFactor: number;

  constructor(options: CCDIKOptions = {}) {
    this.tolerance = options.tolerance ?? 1e-3;
    this.maxIterations = options.maxIterations ?? 25;
    this.stepFactor = options.stepFactor ?? 0.8;
  }

  solve(joints: Vec3[], target: Vec3): CCDIKResult {
    if (joints.length < 2) {
      throw new Error('CCD IK requires at least two joints.');
    }
    const positions = joints.map(clone);
    let reached = false;
    let iterations = 0;

    const endIndex = positions.length - 1;

    while (iterations < this.maxIterations) {
      iterations += 1;

      // For each joint (except end effector), from end to root
      for (let i = endIndex - 1; i >= 0; i--) {
        const jointPos = positions[i];
        const endPos = positions[endIndex];

        const toEnd = sub(endPos, jointPos);
        const toTarget = sub(target, jointPos);

        const lenEnd = length(toEnd);
        const lenTarget = length(toTarget);
        if (lenEnd === 0 || lenTarget === 0) continue;

        const dirEnd = normalize(toEnd);
        const dirTarget = normalize(toTarget);

        const cosTheta = dot(dirEnd, dirTarget);
        // Clamp to avoid NaNs
        const clampedCos = Math.min(1, Math.max(-1, cosTheta));
        const theta = Math.acos(clampedCos);
        if (theta < 1e-6) continue;

        // Rotation axis
        const axis = normalize(cross(dirEnd, dirTarget));
        if (length(axis) === 0) continue;

        const appliedAngle = theta * this.stepFactor;
        const rotMat = rotationAroundAxis(axis, appliedAngle);

        // Rotate all descendants of joint i around joint i
        for (let j = i + 1; j <= endIndex; j++) {
          const rel = sub(positions[j], jointPos);
          const rotated = applyMatrix(rotMat, rel);
          positions[j] = add(jointPos, rotated);
        }
      }

      if (distance(positions[endIndex], target) <= this.tolerance) {
        reached = true;
        break;
      }
    }

    return { positions, reached, iterations };
  }
}

// --- Math helpers for rotation ---

type Mat3 = [number, number, number, number, number, number, number, number, number];

function rotationAroundAxis(axis: Vec3, angle: number): Mat3 {
  const { x, y, z } = axis;
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  const t = 1 - c;
  // Row-major 3x3
  return [
    t * x * x + c, t * x * y - s * z, t * x * z + s * y,
    t * x * y + s * z, t * y * y + c, t * y * z - s * x,
    t * x * z - s * y, t * y * z + s * x, t * z * z + c
  ];
}

function applyMatrix(m: Mat3, v: Vec3): Vec3 {
  return {
    x: m[0] * v.x + m[1] * v.y + m[2] * v.z,
    y: m[3] * v.x + m[4] * v.y + m[5] * v.z,
    z: m[6] * v.x + m[7] * v.y + m[8] * v.z
  };
}

