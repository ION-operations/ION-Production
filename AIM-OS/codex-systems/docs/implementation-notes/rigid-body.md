# Rigid Body Physics (Codex Systems)

**Status:** Scaffolding started  
**Encyclopedia References:**  
- `docs/encyclopedia/01_Foundations/Physics/RIGID_BODY_PHYSICS_COMPLETE.md`  
- `docs/encyclopedia/01_Foundations/Physics/COLLISION_DETECTION_ADVANCED.md`  
- `docs/encyclopedia/01_Foundations/Physics/Engines/BULLET_PHYSICS_WASM_COMPLETE.md`  

## Plan
- Implement SAT/GJK narrow phase, add EPA if needed for penetration depth.
- Broadphase: start with sweep-and-prune or spatial hash.
- Contact manifolds with friction & restitution (impulse-based).
- Joints: ball and hinge constraints.
- Ragdoll: use joint chain constraints + limit cones.
- Demos: stacking, ragdoll fall, jointed chain swing.

## Current Scaffolding
- Types: shapes, bodies, contacts (`RigidBodyTypes.ts`).
- Shapes: basic support functions for sphere/box (`CollisionShapes.ts`).
- Detector: placeholder narrow phase (`CollisionDetector.ts`).
- Engine: integration scaffolding (`RigidBodyEngine.ts`).

## Next Steps
- Implement broadphase (AABB generation, sweep or hash).
- Implement SAT for box/box, sphere/box; GJK for general convex pairs.
- Build contact manifold generator.
- Implement impulse solver with friction and restitution.
- Add quaternion-based angular integration + inertia tensors.
- Add demo scene under `demos/physics-demo/rigid-body-demo.tsx`.

## Success Criteria
- Stable stacking at 60 FPS.
- Correct friction and restitution responses.
- Joints remain stable under load.
- Clear, typed APIs and readable code.

