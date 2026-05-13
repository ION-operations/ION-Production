---
id: "intelligent_snap_system_l3"
type: "system_implementation"
system: "intelligent_snap_system"
title: "Intelligent Snap System - Implementation Guide"
version: "2.0.0"
created: "2025-12-03"
author: "Aether"
status: "implementation_ready"
word_count: 6500
tags: ["implementation", "code", "ghost_preview", "lod"]
---

# Intelligent Snap System - Implementation Guide (L3)

## **Purpose**

Complete implementation guide for adding ghost preview functionality to Lumin3D's existing snap system.

**Target:** Production-ready ghost preview with LOD optimization maintaining 60 FPS.

---

## **Table of Contents**

1. [Component 1: LODManager.ts](#component-1-lodmanagerts)
2. [Component 2: GhostPreviewRenderer.tsx](#component-2-ghostpreviewrenderertsx)
3. [Component 3: SnapEngine.ts](#component-3-snapenginets)
4. [Component 4: SnapOptionPanel.tsx](#component-4-snapoptionpaneltsx)
5. [Integration: Scene3D.tsx Enhancement](#integration-scene3dtsx-enhancement)
6. [Testing & Validation](#testing--validation)
7. [Performance Profiling](#performance-profiling)
8. [Troubleshooting](#troubleshooting)

---

## **Component 1: LODManager.ts**

### **Purpose**
Automatic level-of-detail selection and mesh simplification for ghost preview performance.

### **Full Implementation**

```typescript
// File: src/utils/LODManager.ts

import * as THREE from 'three';
import { SimplifyModifier } from 'three/examples/jsm/modifiers/SimplifyModifier';

/**
 * LOD (Level of Detail) levels for ghost preview rendering
 */
export enum LODLevel {
  FULL_DETAIL = 'full_detail',       // <1,000 polys: Full geometry
  SIMPLIFIED_MESH = 'simplified_mesh', // 1k-10k polys: 50% reduction
  WIREFRAME = 'wireframe',            // 10k-100k polys: Bounding box + wireframe
  BOUNDING_BOX = 'bounding_box'       // >100k polys: Bounding box only
}

/**
 * Performance thresholds for LOD selection (milliseconds)
 */
const LOD_PERFORMANCE_TARGETS = {
  FULL_DETAIL: 5,
  SIMPLIFIED_MESH: 10,
  WIREFRAME: 15,
  BOUNDING_BOX: 20
};

/**
 * LOD Manager for automatic level-of-detail selection and mesh simplification
 */
export class LODManager {
  private static instance: LODManager;
  private lodCache: Map<string, THREE.Object3D> = new Map();
  private simplifyModifier: SimplifyModifier = new SimplifyModifier();
  private performanceHistory: Map<string, number[]> = new Map();

  /**
   * Singleton instance
   */
  static getInstance(): LODManager {
    if (!LODManager.instance) {
      LODManager.instance = new LODManager();
    }
    return LODManager.instance;
  }

  /**
   * Auto-select appropriate LOD level based on polygon count and performance
   */
  selectLOD(object: THREE.Object3D): LODLevel {
    const polyCount = this.countPolygons(object);
    
    // Check performance history for this object
    const avgRenderTime = this.getAverageRenderTime(object.uuid);
    
    // If performance is poor, downgrade LOD
    if (avgRenderTime > LOD_PERFORMANCE_TARGETS.FULL_DETAIL * 2) {
      return LODLevel.BOUNDING_BOX;
    }
    
    // Standard polygon-based selection
    if (polyCount < 1000) {
      return LODLevel.FULL_DETAIL;
    } else if (polyCount < 10000) {
      return LODLevel.SIMPLIFIED_MESH;
    } else if (polyCount < 100000) {
      return LODLevel.WIREFRAME;
    } else {
      return LODLevel.BOUNDING_BOX;
    }
  }

  /**
   * Count total polygons in object (including children)
   */
  countPolygons(object: THREE.Object3D): number {
    let count = 0;
    
    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        const positions = child.geometry.attributes.position;
        if (positions) {
          count += positions.count / 3; // 3 vertices per triangle
        }
      }
    });
    
    return count;
  }

  /**
   * Create LOD version of object based on level
   */
  createLODObject(
    original: THREE.Object3D,
    level: LODLevel
  ): THREE.Object3D {
    // Check cache first
    const cacheKey = `${original.uuid}_${level}`;
    if (this.lodCache.has(cacheKey)) {
      return this.lodCache.get(cacheKey)!.clone();
    }

    let lodObject: THREE.Object3D;

    switch (level) {
      case LODLevel.FULL_DETAIL:
        lodObject = this.createFullDetail(original);
        break;
        
      case LODLevel.SIMPLIFIED_MESH:
        lodObject = this.createSimplifiedMesh(original, 0.5);
        break;
        
      case LODLevel.WIREFRAME:
        lodObject = this.createWireframe(original);
        break;
        
      case LODLevel.BOUNDING_BOX:
        lodObject = this.createBoundingBox(original);
        break;
    }

    // Cache for reuse
    this.lodCache.set(cacheKey, lodObject);

    return lodObject.clone();
  }

  /**
   * Full detail: Clone entire object with materials
   */
  private createFullDetail(original: THREE.Object3D): THREE.Object3D {
    return original.clone();
  }

  /**
   * Simplified mesh: Reduce polygon count by target ratio
   */
  private createSimplifiedMesh(
    original: THREE.Object3D,
    targetRatio: number
  ): THREE.Object3D {
    const simplified = new THREE.Object3D();

    original.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        try {
          // Use SimplifyModifier to reduce polygons
          const targetVertices = Math.floor(
            child.geometry.attributes.position.count * targetRatio
          );
          
          const simplifiedGeometry = this.simplifyModifier.modify(
            child.geometry,
            targetVertices
          );

          const simplifiedMesh = new THREE.Mesh(
            simplifiedGeometry,
            child.material
          );
          
          simplifiedMesh.position.copy(child.position);
          simplifiedMesh.rotation.copy(child.rotation);
          simplifiedMesh.scale.copy(child.scale);
          
          simplified.add(simplifiedMesh);
        } catch (error) {
          console.warn('Simplification failed, using bounding box:', error);
          return this.createBoundingBox(original);
        }
      }
    });

    return simplified.children.length > 0 ? simplified : this.createBoundingBox(original);
  }

  /**
   * Wireframe: Bounding box + wireframe edges
   */
  private createWireframe(original: THREE.Object3D): THREE.Object3D {
    const group = new THREE.Group();
    
    // Create bounding box
    const box = new THREE.Box3().setFromObject(original);
    
    // Box helper
    const boxHelper = new THREE.Box3Helper(box, 0x00ffff);
    group.add(boxHelper);
    
    // Add wireframe for visual richness
    original.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        const wireframe = new THREE.WireframeGeometry(child.geometry);
        const line = new THREE.LineSegments(
          wireframe,
          new THREE.LineBasicMaterial({ 
            color: 0x00ffff,
            transparent: true,
            opacity: 0.3
          })
        );
        
        line.position.copy(child.position);
        line.rotation.copy(child.rotation);
        line.scale.copy(child.scale);
        
        group.add(line);
      }
    });

    return group;
  }

  /**
   * Bounding box only: Fastest rendering
   */
  private createBoundingBox(original: THREE.Object3D): THREE.Object3D {
    const box = new THREE.Box3().setFromObject(original);
    
    const size = new THREE.Vector3();
    box.getSize(size);
    
    const geometry = new THREE.BoxGeometry(size.x, size.y, size.z);
    const material = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      wireframe: true,
      transparent: true,
      opacity: 0.5
    });
    
    const bbox = new THREE.Mesh(geometry, material);
    
    const center = new THREE.Vector3();
    box.getCenter(center);
    bbox.position.copy(center);
    
    return bbox;
  }

  /**
   * Record render time for performance tracking
   */
  recordRenderTime(objectId: string, renderTime: number): void {
    if (!this.performanceHistory.has(objectId)) {
      this.performanceHistory.set(objectId, []);
    }
    
    const history = this.performanceHistory.get(objectId)!;
    history.push(renderTime);
    
    // Keep last 10 samples
    if (history.length > 10) {
      history.shift();
    }
  }

  /**
   * Get average render time for object
   */
  private getAverageRenderTime(objectId: string): number {
    const history = this.performanceHistory.get(objectId);
    if (!history || history.length === 0) return 0;
    
    const sum = history.reduce((a, b) => a + b, 0);
    return sum / history.length;
  }

  /**
   * Clear cache (call when memory is low)
   */
  clearCache(): void {
    this.lodCache.clear();
    this.performanceHistory.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { entries: number; memoryMB: number } {
    return {
      entries: this.lodCache.size,
      memoryMB: (this.lodCache.size * 0.5) // Rough estimate: 0.5 MB per entry
    };
  }
}

export default LODManager.getInstance();
```

---

## **Component 2: GhostPreviewRenderer.tsx**

### **Purpose**
Render transparent ghost objects at target snap positions with collision detection and measurements.

### **Full Implementation**

```typescript
// File: src/components/viewport/GhostPreviewRenderer.tsx

import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { Text } from '@react-three/drei';
import LODManager, { LODLevel } from '../../utils/LODManager';

interface GhostPreviewRendererProps {
  originalObject: THREE.Object3D | null;
  targetPosition: THREE.Vector3 | null;
  snapOption: string | null; // 'top' | 'right' | 'bottom' | 'left' | 'center_x' | 'center_y' | 'center_xy'
  scene: THREE.Scene;
  onRenderComplete?: (renderTime: number) => void;
}

interface Collision {
  object: THREE.Object3D;
  penetrationDepth: number;
  severity: 'minor' | 'moderate' | 'severe';
}

interface Measurement {
  from: THREE.Vector3;
  to: THREE.Vector3;
  label: string;
  color: number;
}

/**
 * Ghost Preview Renderer Component
 * Renders transparent ghost object at target snap position
 */
export const GhostPreviewRenderer: React.FC<GhostPreviewRendererProps> = ({
  originalObject,
  targetPosition,
  snapOption,
  scene,
  onRenderComplete
}) => {
  const ghostRef = useRef<THREE.Group>(null);
  const [ghostObject, setGhostObject] = useState<THREE.Object3D | null>(null);
  const [collisions, setCollisions] = useState<Collision[]>([]);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [ghostColor, setGhostColor] = useState<number>(0x00ffff); // Cyan by default

  useEffect(() => {
    if (!originalObject || !targetPosition) {
      setGhostObject(null);
      return;
    }

    const startTime = performance.now();

    // 1. Select LOD level
    const lodLevel = LODManager.selectLOD(originalObject);
    
    // 2. Create ghost object
    const ghost = LODManager.createLODObject(originalObject, lodLevel);
    
    // 3. Position ghost at target
    ghost.position.copy(targetPosition);
    ghost.rotation.copy(originalObject.rotation);
    ghost.scale.copy(originalObject.scale);
    
    // 4. Apply ghost material
    applyGhostMaterial(ghost, 0.5);
    
    // 5. Detect collisions
    const detectedCollisions = detectCollisions(ghost, scene);
    setCollisions(detectedCollisions);
    
    // 6. Create measurements
    const meas = createMeasurements(originalObject.position, targetPosition);
    setMeasurements(meas);
    
    // 7. Set color based on collisions
    const color = detectedCollisions.length === 0 ? 0x00ffff : 0xff0000;
    setGhostColor(color);
    applyGhostColor(ghost, color);
    
    setGhostObject(ghost);

    // Record render time
    const renderTime = performance.now() - startTime;
    LODManager.recordRenderTime(originalObject.uuid, renderTime);
    onRenderComplete?.(renderTime);

    // Cleanup
    return () => {
      disposeGhost(ghost);
    };
  }, [originalObject, targetPosition, snapOption, scene]);

  if (!ghostObject) return null;

  return (
    <group ref={ghostRef}>
      {/* Ghost object */}
      <primitive object={ghostObject} />
      
      {/* Measurements */}
      {measurements.map((m, i) => (
        <React.Fragment key={`measurement-${i}`}>
          {/* Measurement line */}
          <line>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={2}
                array={new Float32Array([
                  m.from.x, m.from.y, m.from.z,
                  m.to.x, m.to.y, m.to.z
                ])}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color={m.color} linewidth={2} />
          </line>
          
          {/* Measurement label */}
          <Text
            position={[
              (m.from.x + m.to.x) / 2,
              (m.from.y + m.to.y) / 2,
              (m.from.z + m.to.z) / 2
            ]}
            fontSize={0.2}
            color={m.color}
            anchorX="center"
            anchorY="middle"
          >
            {m.label}
          </Text>
        </React.Fragment>
      ))}
      
      {/* Collision warnings */}
      {collisions.map((collision, i) => (
        <mesh
          key={`collision-${i}`}
          position={collision.object.position}
        >
          <sphereGeometry args={[0.2, 16, 16]} />
          <meshBasicMaterial
            color={
              collision.severity === 'minor' ? 0xffff00 :
              collision.severity === 'moderate' ? 0xff8800 :
              0xff0000
            }
            transparent
            opacity={0.7}
          />
        </mesh>
      ))}
    </group>
  );
};

/**
 * Apply ghost material to object (transparent, no depth write)
 */
function applyGhostMaterial(object: THREE.Object3D, opacity: number): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      const material = child.material.clone();
      
      if (material instanceof THREE.Material) {
        material.transparent = true;
        material.opacity = opacity;
        material.depthWrite = false; // Prevent z-fighting
        
        if ('wireframe' in material) {
          material.wireframe = false;
        }
        
        child.material = material;
      }
    }
  });
}

/**
 * Apply color to ghost object
 */
function applyGhostColor(object: THREE.Object3D, color: number): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh && child.material) {
      const material = child.material as THREE.MeshBasicMaterial;
      if ('color' in material) {
        material.color.setHex(color);
      }
    }
  });
}

/**
 * Detect collisions with other objects in scene
 */
function detectCollisions(
  ghost: THREE.Object3D,
  scene: THREE.Scene
): Collision[] {
  const collisions: Collision[] = [];
  const ghostBox = new THREE.Box3().setFromObject(ghost);
  
  scene.traverse((object) => {
    // Skip if same object or not visible
    if (object === ghost || !object.visible) return;
    if (!(object instanceof THREE.Mesh)) return;
    
    const objectBox = new THREE.Box3().setFromObject(object);
    
    if (ghostBox.intersectsBox(objectBox)) {
      // Calculate penetration depth
      const penetration = calculatePenetrationDepth(ghostBox, objectBox);
      
      collisions.push({
        object,
        penetrationDepth: penetration,
        severity: penetration < 0.1 ? 'minor' :
                  penetration < 0.5 ? 'moderate' : 'severe'
      });
    }
  });
  
  return collisions;
}

/**
 * Calculate penetration depth between two bounding boxes
 */
function calculatePenetrationDepth(
  box1: THREE.Box3,
  box2: THREE.Box3
): number {
  const overlap = new THREE.Box3();
  overlap.copy(box1).intersect(box2);
  
  const size = new THREE.Vector3();
  overlap.getSize(size);
  
  // Return smallest dimension as penetration depth
  return Math.min(size.x, size.y, size.z);
}

/**
 * Create measurement lines from current to target position
 */
function createMeasurements(
  from: THREE.Vector3,
  to: THREE.Vector3
): Measurement[] {
  const measurements: Measurement[] = [];
  
  // Total distance
  const distance = from.distanceTo(to);
  measurements.push({
    from,
    to,
    label: `${distance.toFixed(2)}`,
    color: 0xffff00
  });
  
  // X component
  measurements.push({
    from: new THREE.Vector3(from.x, from.y, from.z),
    to: new THREE.Vector3(to.x, from.y, from.z),
    label: `ΔX: ${(to.x - from.x).toFixed(2)}`,
    color: 0xff0000
  });
  
  // Y component
  measurements.push({
    from: new THREE.Vector3(to.x, from.y, from.z),
    to: new THREE.Vector3(to.x, to.y, from.z),
    label: `ΔY: ${(to.y - from.y).toFixed(2)}`,
    color: 0x00ff00
  });
  
  // Z component
  measurements.push({
    from: new THREE.Vector3(to.x, to.y, from.z),
    to: new THREE.Vector3(to.x, to.y, to.z),
    label: `ΔZ: ${(to.z - from.z).toFixed(2)}`,
    color: 0x0000ff
  });
  
  return measurements;
}

/**
 * Dispose ghost object to prevent memory leaks
 */
function disposeGhost(ghost: THREE.Object3D): void {
  ghost.traverse((child) => {
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
```

---

## **Component 3: SnapEngine.ts**

### **Purpose**
Centralize snap position calculation logic for all 8 snap types.

### **Full Implementation**

```typescript
// File: src/utils/SnapEngine.ts

import * as THREE from 'three';

export type SnapOption = 
  | 'snap_top'
  | 'snap_right'
  | 'snap_bottom'
  | 'snap_left'
  | 'snap_center_x'
  | 'snap_center_y'
  | 'snap_center_xy';

export interface SnapTarget {
  position: THREE.Vector3;
  object: THREE.Object3D;
  type: 'grid' | 'element' | 'guide' | 'semantic';
}

export interface SnapConfig {
  gridSize: number;
  snapThreshold: number;
  magneticStrength: number;
  magneticRadius: number;
  gravityStrength: number;
  enabledTypes: string[];
}

/**
 * Snap Engine: Calculate snap positions for all snap types
 */
export class SnapEngine {
  private static instance: SnapEngine;
  private config: SnapConfig;
  private containerBox: THREE.Box3;

  constructor() {
    this.config = {
      gridSize: 10,
      snapThreshold: 15,
      magneticStrength: 75,
      magneticRadius: 50,
      gravityStrength: 60,
      enabledTypes: ['grid', 'element', 'magnetic']
    };
    
    this.containerBox = new THREE.Box3(
      new THREE.Vector3(-10, -10, -10),
      new THREE.Vector3(10, 10, 10)
    );
  }

  static getInstance(): SnapEngine {
    if (!SnapEngine.instance) {
      SnapEngine.instance = new SnapEngine();
    }
    return SnapEngine.instance;
  }

  /**
   * Update snap configuration
   */
  updateConfig(config: Partial<SnapConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Set container bounding box (viewport or selection bounds)
   */
  setContainer(box: THREE.Box3): void {
    this.containerBox = box;
  }

  /**
   * Calculate snap position for given option
   */
  calculateSnapPosition(
    object: THREE.Object3D,
    snapOption: SnapOption
  ): THREE.Vector3 {
    const objectBox = new THREE.Box3().setFromObject(object);
    const objectSize = new THREE.Vector3();
    objectBox.getSize(objectSize);
    
    const containerCenter = new THREE.Vector3();
    this.containerBox.getCenter(containerCenter);
    
    let targetPosition = object.position.clone();
    
    switch (snapOption) {
      case 'snap_top':
        targetPosition.y = this.containerBox.max.y - objectSize.y / 2;
        break;
        
      case 'snap_right':
        targetPosition.x = this.containerBox.max.x - objectSize.x / 2;
        break;
        
      case 'snap_bottom':
        targetPosition.y = this.containerBox.min.y + objectSize.y / 2;
        break;
        
      case 'snap_left':
        targetPosition.x = this.containerBox.min.x + objectSize.x / 2;
        break;
        
      case 'snap_center_x':
        targetPosition.x = containerCenter.x;
        break;
        
      case 'snap_center_y':
        targetPosition.y = containerCenter.y;
        break;
        
      case 'snap_center_xy':
        targetPosition.x = containerCenter.x;
        targetPosition.y = containerCenter.y;
        break;
    }
    
    // Apply grid snapping if enabled
    if (this.config.enabledTypes.includes('grid')) {
      targetPosition = this.snapToGrid(targetPosition);
    }
    
    return targetPosition;
  }

  /**
   * Snap position to grid
   */
  private snapToGrid(position: THREE.Vector3): THREE.Vector3 {
    const { gridSize } = this.config;
    
    return new THREE.Vector3(
      Math.round(position.x / gridSize) * gridSize,
      Math.round(position.y / gridSize) * gridSize,
      Math.round(position.z / gridSize) * gridSize
    );
  }

  /**
   * Apply magnetic force to position
   */
  applyMagneticForce(
    position: THREE.Vector3,
    targets: SnapTarget[]
  ): THREE.Vector3 {
    let result = position.clone();
    const { magneticStrength, magneticRadius } = this.config;
    
    targets.forEach(target => {
      const distance = position.distanceTo(target.position);
      
      if (distance < magneticRadius) {
        const force = (magneticStrength / 100) * (1 / (distance * distance));
        const direction = target.position.clone().sub(position).normalize();
        
        result.add(direction.multiplyScalar(force));
      }
    });
    
    return result;
  }

  /**
   * Detect snap targets near object
   */
  detectSnapTargets(
    object: THREE.Object3D,
    scene: THREE.Scene,
    radius: number
  ): SnapTarget[] {
    const targets: SnapTarget[] = [];
    const objectPos = object.position;
    
    scene.traverse(child => {
      if (child === object || !(child instanceof THREE.Mesh)) return;
      
      const distance = objectPos.distanceTo(child.position);
      
      if (distance < radius) {
        targets.push({
          position: child.position.clone(),
          object: child,
          type: 'element'
        });
      }
    });
    
    return targets;
  }
}

export default SnapEngine.getInstance();
```

---

## **Component 4: SnapOptionPanel.tsx**

### **Purpose**
UI panel with snap option buttons that trigger ghost preview on hover.

### **Full Implementation**

```typescript
// File: src/components/panels/SnapOptionPanel.tsx

import React, { useState } from 'react';
import {
  ArrowUp, ArrowRight, ArrowDown, ArrowLeft,
  AlignCenter, Crosshair, Minus, Plus
} from 'lucide-react';
import * as THREE from 'three';
import SnapEngine, { SnapOption } from '../../utils/SnapEngine';

interface SnapOptionPanelProps {
  selectedObject: THREE.Object3D | null;
  onSnapOptionHover: (option: SnapOption, targetPos: THREE.Vector3) => void;
  onSnapOptionLeave: () => void;
  onSnapOptionClick: (option: SnapOption, targetPos: THREE.Vector3) => void;
}

interface SnapButton {
  id: SnapOption;
  label: string;
  icon: React.ComponentType<{ size?: number }>;
  description: string;
}

const SNAP_BUTTONS: SnapButton[] = [
  { 
    id: 'snap_top', 
    label: 'Top', 
    icon: ArrowUp,
    description: 'Snap to top edge of container'
  },
  { 
    id: 'snap_right', 
    label: 'Right', 
    icon: ArrowRight,
    description: 'Snap to right edge of container'
  },
  { 
    id: 'snap_bottom', 
    label: 'Bottom', 
    icon: ArrowDown,
    description: 'Snap to bottom edge of container'
  },
  { 
    id: 'snap_left', 
    label: 'Left', 
    icon: ArrowLeft,
    description: 'Snap to left edge of container'
  },
  { 
    id: 'snap_center_x', 
    label: 'Center X', 
    icon: Minus,
    description: 'Center horizontally'
  },
  { 
    id: 'snap_center_y', 
    label: 'Center Y', 
    icon: Plus,
    description: 'Center vertically'
  },
  { 
    id: 'snap_center_xy', 
    label: 'Center XY', 
    icon: Crosshair,
    description: 'Center both axes'
  }
];

export const SnapOptionPanel: React.FC<SnapOptionPanelProps> = ({
  selectedObject,
  onSnapOptionHover,
  onSnapOptionLeave,
  onSnapOptionClick
}) => {
  const [hoveredOption, setHoveredOption] = useState<SnapOption | null>(null);

  const handleMouseEnter = (option: SnapOption) => {
    if (!selectedObject) return;
    
    // Calculate target position
    const targetPos = SnapEngine.calculateSnapPosition(selectedObject, option);
    
    setHoveredOption(option);
    onSnapOptionHover(option, targetPos);
  };

  const handleMouseLeave = () => {
    setHoveredOption(null);
    onSnapOptionLeave();
  };

  const handleClick = (option: SnapOption) => {
    if (!selectedObject) return;
    
    const targetPos = SnapEngine.calculateSnapPosition(selectedObject, option);
    onSnapOptionClick(option, targetPos);
  };

  if (!selectedObject) {
    return (
      <div className="snap-option-panel opacity-50 pointer-events-none">
        <p className="text-gray-400 text-sm">Select an object to snap</p>
      </div>
    );
  }

  return (
    <div className="snap-option-panel bg-gray-800 rounded-lg p-4 shadow-xl">
      <h3 className="text-white font-semibold mb-4 flex items-center">
        <Crosshair className="mr-2" size={18} />
        Snap Options
      </h3>
      
      <div className="grid grid-cols-2 gap-3">
        {SNAP_BUTTONS.map(button => (
          <button
            key={button.id}
            className={`
              snap-option-btn
              flex flex-col items-center justify-center
              p-4 rounded-lg transition-all duration-200
              ${hoveredOption === button.id 
                ? 'bg-cyan-600 scale-105 shadow-lg' 
                : 'bg-gray-700 hover:bg-gray-600'
              }
            `}
            onMouseEnter={() => handleMouseEnter(button.id)}
            onMouseLeave={handleMouseLeave}
            onClick={() => handleClick(button.id)}
            title={button.description}
          >
            <button.icon size={24} className="text-white mb-2" />
            <span className="text-white text-sm font-medium">
              {button.label}
            </span>
          </button>
        ))}
      </div>
      
      {hoveredOption && (
        <div className="mt-4 p-3 bg-gray-700 rounded-lg">
          <p className="text-cyan-400 text-xs">
            👻 Ghost preview active - Click to snap!
          </p>
        </div>
      )}
    </div>
  );
};

export default SnapOptionPanel;
```

---

## **Integration: Scene3D.tsx Enhancement**

### **How to Integrate Ghost Preview into Existing Scene**

```typescript
// File: src/components/viewport/Scene3D.tsx (Enhancement)

import React, { useState } from 'react';
import { GhostPreviewRenderer } from './GhostPreviewRenderer';
import * as THREE from 'three';
import { SnapOption } from '../../utils/SnapEngine';

// Add state for ghost preview
const [ghostPreviewData, setGhostPreviewData] = useState<{
  object: THREE.Object3D | null;
  targetPosition: THREE.Vector3 | null;
  snapOption: SnapOption | null;
}>({
  object: null,
  targetPosition: null,
  snapOption: null
});

// Add handlers
const handleSnapOptionHover = (option: SnapOption, targetPos: THREE.Vector3) => {
  setGhostPreviewData({
    object: selectedObject, // Your selected object state
    targetPosition: targetPos,
    snapOption: option
  });
};

const handleSnapOptionLeave = () => {
  setGhostPreviewData({
    object: null,
    targetPosition: null,
    snapOption: null
  });
};

const handleSnapOptionClick = (option: SnapOption, targetPos: THREE.Vector3) => {
  if (selectedObject) {
    // Apply snap
    selectedObject.position.copy(targetPos);
    
    // Hide ghost
    handleSnapOptionLeave();
  }
};

// In render:
return (
  <>
    {/* Existing scene content */}
    
    {/* Ghost preview renderer */}
    <GhostPreviewRenderer
      originalObject={ghostPreviewData.object}
      targetPosition={ghostPreviewData.targetPosition}
      snapOption={ghostPreviewData.snapOption}
      scene={scene}
      onRenderComplete={(time) => console.log(`Ghost render: ${time}ms`)}
    />
    
    {/* Snap option panel */}
    <SnapOptionPanel
      selectedObject={selectedObject}
      onSnapOptionHover={handleSnapOptionHover}
      onSnapOptionLeave={handleSnapOptionLeave}
      onSnapOptionClick={handleSnapOptionClick}
    />
  </>
);
```

---

## **Testing & Validation**

### **Unit Tests**

```typescript
// File: src/utils/__tests__/LODManager.test.ts

import LODManager, { LODLevel } from '../LODManager';
import * as THREE from 'three';

describe('LODManager', () => {
  test('selectLOD returns FULL_DETAIL for simple objects', () => {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const mesh = new THREE.Mesh(geometry);
    
    const level = LODManager.selectLOD(mesh);
    expect(level).toBe(LODLevel.FULL_DETAIL);
  });

  test('selectLOD returns BOUNDING_BOX for huge objects', () => {
    // Create mesh with >100k polygons
    const geometry = new THREE.IcosahedronGeometry(10, 8); // ~327k polys
    const mesh = new THREE.Mesh(geometry);
    
    const level = LODManager.selectLOD(mesh);
    expect(level).toBe(LODLevel.BOUNDING_BOX);
  });

  test('countPolygons correctly counts mesh triangles', () => {
    const geometry = new THREE.BoxGeometry(1, 1, 1); // 12 triangles
    const mesh = new THREE.Mesh(geometry);
    
    const count = LODManager.countPolygons(mesh);
    expect(count).toBe(12);
  });

  test('cache stores and retrieves LOD objects', () => {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const mesh = new THREE.Mesh(geometry);
    
    const lod1 = LODManager.createLODObject(mesh, LODLevel.FULL_DETAIL);
    const lod2 = LODManager.createLODObject(mesh, LODLevel.FULL_DETAIL);
    
    // Should be different instances (cloned)
    expect(lod1).not.toBe(lod2);
    
    // But should have same geometry
    expect(lod1.children.length).toBe(lod2.children.length);
  });
});
```

### **Performance Tests**

```typescript
// File: src/utils/__tests__/GhostPreviewPerformance.test.ts

import { renderGhostPreview } from '../GhostPreviewRenderer';
import * as THREE from 'three';

describe('Ghost Preview Performance', () => {
  test('renders simple objects in <5ms', async () => {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const mesh = new THREE.Mesh(geometry);
    const targetPos = new THREE.Vector3(5, 5, 5);
    
    const startTime = performance.now();
    await renderGhostPreview(mesh, targetPos);
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(5);
  });

  test('renders medium objects in <10ms', async () => {
    const geometry = new THREE.IcosahedronGeometry(5, 3); // ~5k polys
    const mesh = new THREE.Mesh(geometry);
    const targetPos = new THREE.Vector3(5, 5, 5);
    
    const startTime = performance.now();
    await renderGhostPreview(mesh, targetPos);
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(10);
  });

  test('renders huge objects in <20ms', async () => {
    const geometry = new THREE.IcosahedronGeometry(10, 8); // ~327k polys
    const mesh = new THREE.Mesh(geometry);
    const targetPos = new THREE.Vector3(5, 5, 5);
    
    const startTime = performance.now();
    await renderGhostPreview(mesh, targetPos);
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(20);
  });
});
```

---

## **Performance Profiling**

### **Using Chrome DevTools**

```typescript
// Add performance markers
performance.mark('ghost-preview-start');

// Render ghost
renderGhostPreview(object, targetPos);

performance.mark('ghost-preview-end');
performance.measure(
  'ghost-preview-render',
  'ghost-preview-start',
  'ghost-preview-end'
);

// Get measurement
const measure = performance.getEntriesByName('ghost-preview-render')[0];
console.log(`Ghost render time: ${measure.duration}ms`);
```

### **FPS Monitoring**

```typescript
class FPSMonitor {
  private frames: number[] = [];
  private lastTime: number = performance.now();

  update(): number {
    const now = performance.now();
    const delta = now - this.lastTime;
    this.lastTime = now;
    
    const fps = 1000 / delta;
    this.frames.push(fps);
    
    if (this.frames.length > 60) {
      this.frames.shift();
    }
    
    return this.getAverageFPS();
  }

  getAverageFPS(): number {
    const sum = this.frames.reduce((a, b) => a + b, 0);
    return sum / this.frames.length;
  }
}

const fpsMonitor = new FPSMonitor();

// In render loop
function animate() {
  const fps = fpsMonitor.update();
  
  if (fps < 55) {
    console.warn(`Low FPS detected: ${fps.toFixed(1)}`);
  }
  
  requestAnimationFrame(animate);
}
```

---

## **Troubleshooting**

### **Issue 1: Ghost Not Appearing**

**Symptoms:** Ghost preview doesn't render when hovering snap buttons.

**Solutions:**
1. Check if `originalObject` is not null
2. Verify `targetPosition` is valid Vector3
3. Ensure ghost material opacity > 0
4. Check if ghost is being added to scene
5. Verify camera can see ghost position

```typescript
// Debug logging
console.log('Original object:', originalObject);
console.log('Target position:', targetPosition);
console.log('Ghost object created:', ghost);
console.log('Ghost in scene:', scene.children.includes(ghost));
```

### **Issue 2: Poor Performance (Low FPS)**

**Symptoms:** Frame rate drops below 60 FPS during ghost preview.

**Solutions:**
1. Check LOD level selection
2. Verify polygon count detection
3. Clear LOD cache if memory high
4. Reduce collision detection frequency
5. Simplify measurements (fewer lines)

```typescript
// Performance diagnostics
console.log('Polygon count:', LODManager.countPolygons(object));
console.log('Selected LOD:', lodLevel);
console.log('Cache stats:', LODManager.getCacheStats());
```

### **Issue 3: Collision Detection False Positives**

**Symptoms:** Ghost shows red (collision) when there's no actual overlap.

**Solutions:**
1. Adjust collision threshold
2. Use more precise bounding boxes
3. Filter out irrelevant objects
4. Increase penetration depth tolerance

```typescript
// Adjust collision sensitivity
const COLLISION_THRESHOLD = 0.05; // Minimum penetration to count

if (penetrationDepth > COLLISION_THRESHOLD) {
  // Register collision
}
```

### **Issue 4: Memory Leaks**

**Symptoms:** Memory usage grows over time, eventually causing crashes.

**Solutions:**
1. Ensure `disposeGhost()` is called
2. Clear LOD cache periodically
3. Dispose geometries and materials
4. Remove event listeners

```typescript
// Memory cleanup
useEffect(() => {
  return () => {
    disposeGhost(ghostObject);
    LODManager.clearCache();
  };
}, [ghostObject]);
```

---

## **Implementation Checklist**

### **Phase 1: Foundation** (2-3 days)
- [ ] Create `LODManager.ts` with polygon counting
- [ ] Create `SnapEngine.ts` with position calculations
- [ ] Write unit tests for LODManager
- [ ] Write unit tests for SnapEngine
- [ ] Validate LOD selection accuracy

### **Phase 2: Ghost Rendering** (3-4 days)
- [ ] Create `GhostPreviewRenderer.tsx`
- [ ] Implement LOD-based ghost creation
- [ ] Add collision detection
- [ ] Add measurement rendering
- [ ] Write performance tests
- [ ] Profile render times

### **Phase 3: UI Integration** (2-3 days)
- [ ] Create `SnapOptionPanel.tsx`
- [ ] Add hover listeners
- [ ] Wire up ghost preview triggers
- [ ] Add click handlers for snap
- [ ] Style panel UI

### **Phase 4: Scene Integration** (2-3 days)
- [ ] Enhance `Scene3D.tsx`
- [ ] Add ghost preview state management
- [ ] Connect SnapOptionPanel to Scene3D
- [ ] Test all 8 snap types
- [ ] Verify FPS targets met

### **Phase 5: Polish** (2-3 days)
- [ ] Add keyboard shortcuts
- [ ] Improve visual feedback
- [ ] Add accessibility features
- [ ] Write user documentation
- [ ] Conduct user testing

**Total Time:** 11-16 days (2-3 weeks)

---

## **Next Steps**

1. ✅ Review this L3 implementation guide
2. ⏳ Set up development environment
3. ⏳ Implement Phase 1 (Foundation)
4. ⏳ Test and validate each phase
5. ⏳ Deploy to production

---

**This implementation guide provides everything needed to build the ghost preview system!** 🚀💙

