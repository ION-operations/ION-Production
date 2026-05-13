import { CollisionShape, ContactManifold, Vec3 } from './RigidBodyTypes';
import { aabbFromBox, dot, length, normalize, sub } from './CollisionShapes';

export interface CollisionPair {
  a: number;
  b: number;
  shapeA: CollisionShape;
  shapeB: CollisionShape;
  posA: Vec3;
  posB: Vec3;
}

/**
 * Minimal collision detector:
 * - Sphere-Sphere
 * - Sphere-Plane
 * - Box-Plane (axis-aligned box, rotation ignored)
 */
export class CollisionDetector {
  detect(pairs: CollisionPair[]): ContactManifold[] {
    const manifolds: ContactManifold[] = [];
    for (const p of pairs) {
      const { shapeA, shapeB } = p;
      const result = this.collide(p);
      if (result.length > 0) {
        manifolds.push({
          bodyA: p.a,
          bodyB: p.b,
          contacts: result
        });
      }
    }
    return manifolds;
  }

  private collide(pair: CollisionPair) {
    const { shapeA, shapeB } = pair;
    if (shapeA.type === 'sphere' && shapeB.type === 'sphere') {
      return sphereSphere(pair.posA, shapeA.radius!, pair.posB, shapeB.radius!);
    }
    if (shapeA.type === 'sphere' && shapeB.type === 'plane') {
      return spherePlane(pair.posA, shapeA.radius!, shapeB.normal!, shapeB.constant || 0, true);
    }
    if (shapeA.type === 'plane' && shapeB.type === 'sphere') {
      return spherePlane(pair.posB, shapeB.radius!, shapeA.normal!, shapeA.constant || 0, false);
    }
    if (shapeA.type === 'box' && shapeB.type === 'plane') {
      return boxPlane(pair.posA, shapeA.halfExtents!, shapeB.normal!, shapeB.constant || 0, true);
    }
    if (shapeA.type === 'plane' && shapeB.type === 'box') {
      return boxPlane(pair.posB, shapeB.halfExtents!, shapeA.normal!, shapeA.constant || 0, false);
    }
    return [];
  }
}

// --- Narrow phase helpers ---

function sphereSphere(posA: Vec3, rA: number, posB: Vec3, rB: number) {
  const delta = sub(posB, posA);
  const dist = length(delta);
  const radii = rA + rB;
  if (dist >= radii || dist === 0) return [];
  const normal = normalize(delta);
  const penetration = radii - dist;
  const contactPoint = {
    position: {
      x: posA.x + normal.x * (rA - penetration * 0.5),
      y: posA.y + normal.y * (rA - penetration * 0.5),
      z: posA.z + normal.z * (rA - penetration * 0.5)
    },
    normal,
    penetration
  };
  return [contactPoint];
}

function spherePlane(center: Vec3, radius: number, planeNormal: Vec3, planeConstant: number, aIsSphere: boolean) {
  const n = normalize(planeNormal);
  const dist = dot(center, n) + planeConstant;
  const penetration = radius - dist;
  if (penetration <= 0) return [];
  const normal = aIsSphere ? n : { x: -n.x, y: -n.y, z: -n.z };
  const position = {
    x: center.x - n.x * dist,
    y: center.y - n.y * dist,
    z: center.z - n.z * dist
  };
  return [{ position, normal, penetration }];
}

function boxPlane(center: Vec3, halfExtents: Vec3, planeNormal: Vec3, planeConstant: number, aIsBox: boolean) {
  const n = normalize(planeNormal);
  const { min, max } = aabbFromBox(center, halfExtents);
  // Check each corner; take deepest penetration
  const corners: Vec3[] = [
    { x: min.x, y: min.y, z: min.z }, { x: min.x, y: min.y, z: max.z },
    { x: min.x, y: max.y, z: min.z }, { x: min.x, y: max.y, z: max.z },
    { x: max.x, y: min.y, z: min.z }, { x: max.x, y: min.y, z: max.z },
    { x: max.x, y: max.y, z: min.z }, { x: max.x, y: max.y, z: max.z },
  ];
  let bestPen = -Infinity;
  let bestCorner: Vec3 | null = null;
  for (const c of corners) {
    const dist = dot(c, n) + planeConstant;
    const pen = -dist;
    if (pen > bestPen) {
      bestPen = pen;
      bestCorner = c;
    }
  }
  if (!bestCorner || bestPen <= 0) return [];
  const normal = aIsBox ? { x: -n.x, y: -n.y, z: -n.z } : n;
  return [{
    position: bestCorner,
    normal,
    penetration: bestPen
  }];
}

