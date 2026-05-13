import { Vec3, clone } from './types';
import { FABRIKSolver, FABRIKOptions, FABRIKResult } from './FABRIKSolver';
import { CCDIKSolver, CCDIKOptions, CCDIKResult } from './CCDIKSolver';

export interface IKChain {
  joints: Vec3[]; // ordered from root to end effector
}

export interface FullBodyIKConfig {
  solver: 'fabrik' | 'ccd';
  fabrikOptions?: FABRIKOptions;
  ccdOptions?: CCDIKOptions;
}

export interface FullBodyIKResult {
  chains: Vec3[][];
  reached: boolean;
  iterations: number;
}

/**
 * Simple orchestrator to solve multiple IK chains (e.g., limbs) independently.
 * This is intentionally minimal; a production rig would coordinate constraints across chains.
 */
export class FullBodyIK {
  private readonly fabrik: FABRIKSolver;
  private readonly ccd: CCDIKSolver;

  constructor() {
    this.fabrik = new FABRIKSolver();
    this.ccd = new CCDIKSolver();
  }

  solve(chains: IKChain[], targets: Vec3[], config: FullBodyIKConfig): FullBodyIKResult {
    if (chains.length !== targets.length) {
      throw new Error('Chains and targets length mismatch.');
    }
    const solved: Vec3[][] = [];
    let reachedAll = true;
    let maxIter = 0;

    chains.forEach((chain, idx) => {
      const target = targets[idx];
      let result: FABRIKResult | CCDIKResult;
      if (config.solver === 'fabrik') {
        this.fabrik = new FABRIKSolver(config.fabrikOptions);
        result = this.fabrik.solve(chain.joints, target);
      } else {
        this.ccd = new CCDIKSolver(config.ccdOptions);
        result = this.ccd.solve(chain.joints, target);
      }
      solved.push(result.positions.map(clone));
      reachedAll = reachedAll && result.reached;
      maxIter = Math.max(maxIter, result.iterations);
    });

    return { chains: solved, reached: reachedAll, iterations: maxIter };
  }
}

