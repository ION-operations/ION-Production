/**
 * Ghost Preview Renderer Component
 * @module @lumin/snap-system/components/GhostPreviewRenderer
 * 
 * NL_TAG: LUMIN-GHOST-001 | Renders transparent ghost preview at snap position | GhostPreviewRenderer | [Scene3D]
 * NL_TAG_INTENT: LUMIN-UX-002 | Visual feedback before committing snap action | ghost + measurements + collisions | [UX_REQUIREMENTS]
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import { LODManager } from '../utils/LODManager';
import {
  GhostPreviewRendererProps,
  GhostRenderEvent,
  Collision,
  Measurement,
  LODLevel,
  GHOST_COLORS,
  CollisionSeverity
} from '../types';

/**
 * Ghost Preview Renderer
 * 
 * Renders a transparent ghost object at the target snap position,
 * with collision detection, measurements, and visual feedback.
 * 
 * @example
 * ```tsx
 * <GhostPreviewRenderer
 *   originalObject={selectedMesh}
 *   targetPosition={new THREE.Vector3(5, 0, 0)}
 *   snapOption="snap_right"
 *   scene={scene}
 *   onRenderComplete={(e) => console.log(`Render: ${e.renderTimeMs}ms`)}
 * />
 * ```
 */
export const GhostPreviewRenderer: React.FC<GhostPreviewRendererProps> = ({
  originalObject,
  targetPosition,
  snapOption,
  scene,
  onRenderComplete,
  opacity = 0.5,
  enableCollisionDetection = true,
  enableMeasurements = true
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const lodManager = useMemo(() => LODManager.getInstance(), []);
  
  const [ghostObject, setGhostObject] = useState<THREE.Object3D | null>(null);
  const [collisions, setCollisions] = useState<Collision[]>([]);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [ghostColor, setGhostColor] = useState<number>(GHOST_COLORS.VALID);
  const [lodLevel, setLodLevel] = useState<LODLevel>(LODLevel.FULL_DETAIL);

  // Create ghost object when inputs change
  useEffect(() => {
    if (!originalObject || !targetPosition) {
      setGhostObject(null);
      setCollisions([]);
      setMeasurements([]);
      return;
    }

    const startTime = performance.now();

    // 1. Select LOD level
    const level = lodManager.selectLOD(originalObject);
    setLodLevel(level);

    // 2. Create ghost object
    const ghost = lodManager.createLODObject(originalObject, level);
    
    // 3. Position ghost at target
    ghost.position.copy(targetPosition);
    ghost.rotation.copy(originalObject.rotation);
    ghost.scale.copy(originalObject.scale);

    // 4. Apply ghost material
    applyGhostMaterial(ghost, opacity);

    // 5. Detect collisions
    let detectedCollisions: Collision[] = [];
    if (enableCollisionDetection) {
      detectedCollisions = detectCollisions(ghost, scene, originalObject);
      setCollisions(detectedCollisions);
    }

    // 6. Create measurements
    if (enableMeasurements) {
      const meas = createMeasurements(originalObject.position, targetPosition);
      setMeasurements(meas);
    }

    // 7. Set color based on collisions
    const color = getGhostColor(detectedCollisions);
    setGhostColor(color);
    applyGhostColor(ghost, color);

    setGhostObject(ghost);

    // Record performance
    const renderTime = performance.now() - startTime;
    lodManager.recordRenderTime(originalObject.uuid, renderTime);
    
    // Callback
    onRenderComplete?.({
      lodLevel: level,
      renderTimeMs: renderTime,
      polygonCount: lodManager.countPolygons(ghost),
      collisionCount: detectedCollisions.length
    });

    // Cleanup
    return () => {
      disposeObject(ghost);
    };
  }, [originalObject, targetPosition, snapOption, opacity, enableCollisionDetection, enableMeasurements]);

  // Don't render if no ghost
  if (!ghostObject || !targetPosition || !originalObject) {
    return null;
  }

  return (
    <group ref={groupRef}>
      {/* Ghost object */}
      <primitive object={ghostObject} />

      {/* Measurements */}
      {enableMeasurements && measurements.map((measurement, index) => (
        <MeasurementLine key={`measurement-${index}`} measurement={measurement} />
      ))}

      {/* Collision indicators */}
      {enableCollisionDetection && collisions.map((collision, index) => (
        <CollisionIndicator key={`collision-${index}`} collision={collision} />
      ))}

      {/* Snap option label */}
      {snapOption && (
        <Text
          position={[
            targetPosition.x,
            targetPosition.y + 2,
            targetPosition.z
          ]}
          fontSize={0.3}
          color={ghostColor}
          anchorX="center"
          anchorY="bottom"
        >
          {formatSnapOption(snapOption)}
        </Text>
      )}
    </group>
  );
};

// ============================================
// Sub-components
// ============================================

/**
 * Measurement line with label
 */
const MeasurementLine: React.FC<{ measurement: Measurement }> = ({ measurement }) => {
  const { from, to, label, color } = measurement;
  
  const points = useMemo(() => {
    return [from.clone(), to.clone()];
  }, [from, to]);

  const midpoint = useMemo(() => {
    return new THREE.Vector3(
      (from.x + to.x) / 2,
      (from.y + to.y) / 2,
      (from.z + to.z) / 2
    );
  }, [from, to]);

  return (
    <group>
      {/* Line */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={2}
            array={new Float32Array([
              from.x, from.y, from.z,
              to.x, to.y, to.z
            ])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color={color} linewidth={2} />
      </line>

      {/* Label */}
      <Text
        position={[midpoint.x + 0.1, midpoint.y + 0.1, midpoint.z]}
        fontSize={0.15}
        color={color}
        anchorX="left"
        anchorY="middle"
      >
        {label}
      </Text>
    </group>
  );
};

/**
 * Collision warning indicator
 */
const CollisionIndicator: React.FC<{ collision: Collision }> = ({ collision }) => {
  const color = useMemo(() => {
    switch (collision.severity) {
      case 'minor': return 0xffff00;
      case 'moderate': return 0xff8800;
      case 'severe': return 0xff0000;
      default: return 0xffff00;
    }
  }, [collision.severity]);

  const position = useMemo(() => {
    const box = new THREE.Box3().setFromObject(collision.object);
    const center = new THREE.Vector3();
    box.getCenter(center);
    return center;
  }, [collision.object]);

  return (
    <mesh position={position}>
      <sphereGeometry args={[0.2, 16, 16]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={0.7}
      />
    </mesh>
  );
};

// ============================================
// Helper Functions
// ============================================

/**
 * Apply ghost material to object (transparent, no depth write)
 */
function applyGhostMaterial(object: THREE.Object3D, opacity: number): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh && child.material) {
      // Clone material to avoid modifying original
      const material = child.material.clone();
      
      material.transparent = true;
      material.opacity = opacity;
      material.depthWrite = false; // Prevent z-fighting
      
      if ('wireframe' in material) {
        (material as THREE.MeshBasicMaterial).wireframe = false;
      }
      
      child.material = material;
    }
  });
}

/**
 * Apply color to ghost object
 */
function applyGhostColor(object: THREE.Object3D, color: number): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh && child.material) {
      const material = child.material;
      
      if ('color' in material) {
        (material as THREE.MeshBasicMaterial).color.setHex(color);
      }
    }
  });
}

/**
 * Detect collisions with other objects in scene
 */
function detectCollisions(
  ghost: THREE.Object3D,
  scene: THREE.Scene,
  originalObject: THREE.Object3D
): Collision[] {
  const collisions: Collision[] = [];
  const ghostBox = new THREE.Box3().setFromObject(ghost);

  scene.traverse((object) => {
    // Skip ghost itself and original object
    if (object === ghost || object === originalObject) return;
    if (!object.visible) return;
    if (!(object instanceof THREE.Mesh)) return;
    
    const objectBox = new THREE.Box3().setFromObject(object);
    
    if (ghostBox.intersectsBox(objectBox)) {
      const penetration = calculatePenetrationDepth(ghostBox, objectBox);
      
      collisions.push({
        object,
        penetrationDepth: penetration,
        severity: getSeverity(penetration)
      });
    }
  });

  return collisions;
}

/**
 * Calculate penetration depth between two boxes
 */
function calculatePenetrationDepth(box1: THREE.Box3, box2: THREE.Box3): number {
  const overlap = box1.clone().intersect(box2);
  
  const size = new THREE.Vector3();
  overlap.getSize(size);
  
  // Return smallest dimension as penetration
  return Math.min(size.x, size.y, size.z);
}

/**
 * Get severity from penetration depth
 */
function getSeverity(depth: number): CollisionSeverity {
  if (depth < 0.1) return 'minor';
  if (depth < 0.5) return 'moderate';
  return 'severe';
}

/**
 * Get ghost color based on collisions
 */
function getGhostColor(collisions: Collision[]): number {
  if (collisions.length === 0) {
    return GHOST_COLORS.VALID;
  }
  
  const hassSevere = collisions.some(c => c.severity === 'severe');
  if (hassSevere) {
    return GHOST_COLORS.COLLISION;
  }
  
  return GHOST_COLORS.WARNING;
}

/**
 * Create measurement lines from source to target
 */
function createMeasurements(from: THREE.Vector3, to: THREE.Vector3): Measurement[] {
  const measurements: Measurement[] = [];
  
  // Total distance
  const distance = from.distanceTo(to);
  measurements.push({
    from: from.clone(),
    to: to.clone(),
    label: `${distance.toFixed(2)}`,
    color: 0xffff00,
    type: 'distance'
  });
  
  // X component (red)
  if (Math.abs(to.x - from.x) > 0.01) {
    measurements.push({
      from: new THREE.Vector3(from.x, from.y, from.z),
      to: new THREE.Vector3(to.x, from.y, from.z),
      label: `ΔX: ${(to.x - from.x).toFixed(2)}`,
      color: 0xff0000,
      type: 'delta_x'
    });
  }
  
  // Y component (green)
  if (Math.abs(to.y - from.y) > 0.01) {
    measurements.push({
      from: new THREE.Vector3(to.x, from.y, from.z),
      to: new THREE.Vector3(to.x, to.y, from.z),
      label: `ΔY: ${(to.y - from.y).toFixed(2)}`,
      color: 0x00ff00,
      type: 'delta_y'
    });
  }
  
  // Z component (blue)
  if (Math.abs(to.z - from.z) > 0.01) {
    measurements.push({
      from: new THREE.Vector3(to.x, to.y, from.z),
      to: new THREE.Vector3(to.x, to.y, to.z),
      label: `ΔZ: ${(to.z - from.z).toFixed(2)}`,
      color: 0x0000ff,
      type: 'delta_z'
    });
  }
  
  return measurements;
}

/**
 * Format snap option for display
 */
function formatSnapOption(option: string): string {
  return option
    .replace('snap_', '')
    .replace('_', ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

/**
 * Dispose of Three.js object to prevent memory leaks
 */
function disposeObject(object: THREE.Object3D): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.geometry?.dispose();
      
      if (Array.isArray(child.material)) {
        child.material.forEach(m => m.dispose());
      } else {
        child.material?.dispose();
      }
    }
  });
}

export default GhostPreviewRenderer;

