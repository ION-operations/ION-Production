# Inverse Kinematics (Codex Systems)

**Systems:** FABRIK, CCD-IK, Look-At, FullBody orchestrator  
**Encyclopedia References:**
- `docs/encyclopedia/02_Animation/Character/INVERSE_KINEMATICS_COMPLETE.md`
- `docs/encyclopedia/02_Animation/Character/MOTION_RETARGETING_COMPLETE.md`

## Goals
- Production-quality IK solvers in isolation
- No dependencies on existing Lucid code
- Clean TypeScript, testable, demo-friendly

## Implemented
- FABRIK solver (forward/backward passes, unreachable handling)
- CCD-IK solver (axis-angle rotation with damping)
- Look-at basis + quaternion helper
- Full-body orchestrator for multiple chains (independent limbs)

## Key Algorithms
### FABRIK
1. Measure total chain length; if target unreachable, stretch along root→target direction.
2. Backward pass: set end effector to target, reposition joints outward maintaining segment lengths.
3. Forward pass: lock root to original, reposition toward end effector maintaining lengths.
4. Iterate until tolerance or max iterations.

### CCD-IK
1. Iterate joints from end-1 to root.
2. Compute vectors joint→end and joint→target.
3. Find rotation axis via cross, angle via dot/acos.
4. Apply damped rotation to all descendants.
5. Repeat until tolerance or max iterations.

## Parameters
- `tolerance`: convergence threshold (default 1e-3)
- `maxIterations`: iteration cap (default 25)
- `stepFactor` (CCD): rotation damping 0-1 (default 0.8)

## Success Criteria
- Converges on reachable targets within tolerance
- Graceful stretching when unreachable
- Stable with modest iteration counts (<25)
- Clear, typed APIs suitable for demos

## Next Steps
- Add pole vector support (for knees/elbows)
- Add joint angle limits (per-axis constraints)
- Add test harness + sample chains
- Add R3F/Three demo scene to visualize convergence

