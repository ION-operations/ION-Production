import { Vec3, clone, distance, normalize, sub, scale, add } from './types';

export interface BoneSegment {
  start: Vec3;
  end: Vec3;
  length: number;
}

export interface FABRIKOptions {
  tolerance?: number; // convergence threshold
  maxIterations?: number;
}

export interface FABRIKResult {
  positions: Vec3[]; // joint positions (including root and end-effector)
  reached: boolean;
  iterations: number;
}

/**
 * FABRIK (Forward And Backward Reaching Inverse Kinematics)
 * Reference: encyclopedia/02_Animation/Character/INVERSE_KINEMATICS_COMPLETE.md
 */
export class FABRIKSolver {
  private readonly tolerance: number;
  private readonly maxIterations: number;

  constructor(options: FABRIKOptions = {}) {
    this.tolerance = options.tolerance ?? 1e-3;
    this.maxIterations = options.maxIterations ?? 25;
  }

  /**
   * Solve IK for a chain of bones toward a target.
   * @param joints Ordered joint positions (root first, end-effector last)
   * @param target Target position to reach
   */
  solve(joints: Vec3[], target: Vec3): FABRIKResult {
    if (joints.length < 2) {
      throw new Error('FABRIK requires at least two joints (one segment).');
    }
    const originalRoot = clone(joints[0]);
    const segments: BoneSegment[] = [];
    for (let i = 0; i < joints.length - 1; i++) {
      const start = joints[i];
      const end = joints[i + 1];
      segments.push({
        start: clone(start),
        end: clone(end),
        length: distance(start, end)
      });
    }

    const totalLength = segments.reduce((sum, s) => sum + s.length, 0);
    const rootToTarget = distance(originalRoot, target);

    // Unreachable target: stretch toward target
    if (rootToTarget > totalLength) {
      const dir = normalize(sub(target, originalRoot));
      const newPositions: Vec3[] = [clone(originalRoot)];
      let acc = clone(originalRoot);
      for (const seg of segments) {
        acc = add(acc, scale(dir, seg.length));
        newPositions.push(acc);
      }
      return { positions: newPositions, reached: false, iterations: 0 };
    }

    // Reachable target: iterative forward/backward passes
    let positions = joints.map(clone);
    let reached = false;
    let iterations = 0;

    while (iterations < this.maxIterations) {
      iterations += 1;

      // 1) Backward reaching: set end effector to target, move backwards
      positions[positions.length - 1] = clone(target);
      for (let i = segments.length - 1; i >= 0; i--) {
        const child = positions[i + 1];
        const dir = normalize(sub(positions[i], child));
        positions[i] = add(child, scale(dir, segments[i].length));
      }

      // 2) Forward reaching: fix root to original, move forward
      positions[0] = clone(originalRoot);
      for (let i = 0; i < segments.length; i++) {
        const dir = normalize(sub(positions[i + 1], positions[i]));
        positions[i + 1] = add(positions[i], scale(dir, segments[i].length));
      }

      // Check convergence
      if (distance(positions[positions.length - 1], target) <= this.tolerance) {
        reached = true;
        break;
      }
    }

    return { positions, reached, iterations };
  }
}

