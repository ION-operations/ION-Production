import { CollisionDetector, CollisionPair } from './CollisionDetector';
import { RigidBodyConfig, RigidBodyState, ContactManifold, Vec3 } from './RigidBodyTypes';

function vec(x = 0, y = 0, z = 0): Vec3 {
  return { x, y, z };
}

function add(a: Vec3, b: Vec3): Vec3 {
  return { x: a.x + b.x, y: a.y + b.y, z: a.z + b.z };
}

function scale(v: Vec3, s: number): Vec3 {
  return { x: v.x * s, y: v.y * s, z: v.z * s };
}

/**
 * Minimal rigid body engine scaffold.
 * TODO: implement full integration, constraint solving, impulses.
 */
export class RigidBodyEngine {
  private bodies: RigidBodyState[] = [];
  private configs: RigidBodyConfig[] = [];
  private detector = new CollisionDetector();
  private gravity: Vec3 = { x: 0, y: -9.81, z: 0 };

  addBody(config: RigidBodyConfig, initialState: Partial<RigidBodyState>): number {
    const invMass = config.mass > 0 ? 1 / config.mass : 0;
    const state: RigidBodyState = {
      transform: initialState.transform ?? { position: vec(), rotation: { x: 0, y: 0, z: 0, w: 1 } },
      linearVelocity: initialState.linearVelocity ?? vec(),
      angularVelocity: initialState.angularVelocity ?? vec(),
      forces: vec(),
      torques: vec(),
      invMass,
      invInertia: initialState.invInertia ?? vec(0, 0, 0)
    };
    this.bodies.push(state);
    this.configs.push(config);
    return this.bodies.length - 1;
  }

  step(dt: number) {
    // 1) Broadphase: naive all-pairs
    const pairs = this.buildPairs();
    // 2) Narrow phase
    const manifolds: ContactManifold[] = this.detector.detect(pairs);
    // 3) Solve contacts
    this.solveContacts(manifolds, dt);
    // 4) Integrate
    this.integrate(dt);
  }

  private buildPairs(): CollisionPair[] {
    const pairs: CollisionPair[] = [];
    for (let i = 0; i < this.bodies.length; i++) {
      for (let j = i + 1; j < this.bodies.length; j++) {
        pairs.push({
          a: i,
          b: j,
          shapeA: this.configs[i].shape,
          shapeB: this.configs[j].shape,
          posA: this.bodies[i].transform.position,
          posB: this.bodies[j].transform.position
        });
      }
    }
    return pairs;
  }

  private solveContacts(manifolds: ContactManifold[], dt: number) {
    for (const m of manifolds) {
      const bodyA = this.bodies[m.bodyA];
      const bodyB = this.bodies[m.bodyB];
      const confA = this.configs[m.bodyA];
      const confB = this.configs[m.bodyB];
      for (const c of m.contacts) {
        const normal = c.normal;

        // Relative velocity along normal
        const rv = sub(bodyB.linearVelocity, bodyA.linearVelocity);
        const velAlongNormal = dot(rv, normal);
        if (velAlongNormal > 0) continue; // separating

        const e = Math.min(confA.restitution, confB.restitution);
        const j = -(1 + e) * velAlongNormal;
        const invMassSum = bodyA.invMass + bodyB.invMass;
        if (invMassSum === 0) continue;
        const impulseMag = j / invMassSum;

        const impulse = scale(normal, impulseMag);
        bodyA.linearVelocity = sub(bodyA.linearVelocity, scale(impulse, bodyA.invMass));
        bodyB.linearVelocity = add(bodyB.linearVelocity, scale(impulse, bodyB.invMass));

        // Positional correction (Baumgarte-like)
        const percent = 0.2;
        const slop = 0.001;
        const correctionMag = Math.max(c.penetration - slop, 0) / invMassSum * percent;
        const correction = scale(normal, correctionMag);
        bodyA.transform.position = sub(bodyA.transform.position, scale(correction, bodyA.invMass));
        bodyB.transform.position = add(bodyB.transform.position, scale(correction, bodyB.invMass));
      }
    }
  }

  private integrate(dt: number) {
    for (let i = 0; i < this.bodies.length; i++) {
      const body = this.bodies[i];
      const conf = this.configs[i];

      // accumulate gravity
      if (conf.useGravity !== false && body.invMass > 0) {
        body.forces = add(body.forces, scale(this.gravity, conf.mass));
      }

      // linear
      body.linearVelocity = add(body.linearVelocity, scale(body.forces, body.invMass * dt));
      body.transform.position = add(body.transform.position, scale(body.linearVelocity, dt));
      // TODO: angular integration with quaternions
      // reset forces
      body.forces = vec();
      body.torques = vec();
    }
  }
}

