/**
 * Snap Engine - Core Snap Position Calculation
 * @module @lumin/snap-system/utils/SnapEngine
 * 
 * NL_TAG: LUMIN-SNAP-001 | Calculates snap positions for all 8 snap types | SnapEngine class | [GhostPreviewRenderer, SnapOptionPanel]
 * NL_TAG_INTENT: LUMIN-UX-001 | Provides precise object positioning with intelligent snapping | physics-based + grid | [SNAP_REQUIREMENTS]
 */

import * as THREE from 'three';
import {
  SnapOption,
  SnapType,
  SnapTarget,
  SnapConfig,
  DEFAULT_SNAP_CONFIG,
  SnapPreset,
  SNAP_PRESETS
} from '../types';

/**
 * Snap Engine
 * 
 * Centralized snap position calculation for all 8 snap types:
 * - Grid, Element, Guide, Magnetic, Semantic, Gravity, Fluid, Layout Inference
 * 
 * @example
 * ```typescript
 * import { SnapEngine } from '@lumin/snap-system';
 * 
 * const engine = SnapEngine.getInstance();
 * const position = engine.calculateSnapPosition(object, 'snap_top');
 * ```
 */
export class SnapEngine {
  private static instance: SnapEngine | null = null;
  
  /** Current snap configuration */
  private config: SnapConfig;
  
  /** Container bounding box for snap calculations */
  private containerBox: THREE.Box3;
  
  /** Reference to scene for target detection */
  private scene: THREE.Scene | null = null;

  private constructor() {
    this.config = { ...DEFAULT_SNAP_CONFIG };
    this.containerBox = new THREE.Box3(
      new THREE.Vector3(-10, -10, -10),
      new THREE.Vector3(10, 10, 10)
    );
  }

  /**
   * Get singleton instance
   */
  static getInstance(): SnapEngine {
    if (!SnapEngine.instance) {
      SnapEngine.instance = new SnapEngine();
    }
    return SnapEngine.instance;
  }

  /**
   * Reset singleton (for testing)
   */
  static resetInstance(): void {
    SnapEngine.instance = null;
  }

  // ============================================
  // Configuration
  // ============================================

  /**
   * Update snap configuration
   */
  updateConfig(config: Partial<SnapConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current configuration
   */
  getConfig(): SnapConfig {
    return { ...this.config };
  }

  /**
   * Apply a preset configuration
   */
  applyPreset(presetName: string): void {
    const preset = SNAP_PRESETS.find(p => p.name === presetName);
    if (preset) {
      this.updateConfig(preset.config);
    }
  }

  /**
   * Set container bounding box
   */
  setContainer(box: THREE.Box3): void {
    this.containerBox = box.clone();
  }

  /**
   * Set container from object (e.g., viewport bounds)
   */
  setContainerFromObject(object: THREE.Object3D): void {
    this.containerBox = new THREE.Box3().setFromObject(object);
  }

  /**
   * Set scene reference for target detection
   */
  setScene(scene: THREE.Scene): void {
    this.scene = scene;
  }

  // ============================================
  // Snap Position Calculation
  // ============================================

  /**
   * Calculate target snap position for given option
   */
  calculateSnapPosition(
    object: THREE.Object3D,
    snapOption: SnapOption
  ): THREE.Vector3 {
    // Get object bounding box
    const objectBox = new THREE.Box3().setFromObject(object);
    const objectSize = new THREE.Vector3();
    objectBox.getSize(objectSize);
    
    // Get container center
    const containerCenter = new THREE.Vector3();
    this.containerBox.getCenter(containerCenter);
    
    // Start from current position
    let targetPosition = object.position.clone();
    
    // Apply snap option
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
    
    // Apply magnetic snapping if enabled
    if (this.config.enabledTypes.includes('magnetic') && this.scene) {
      const targets = this.detectSnapTargets(targetPosition, this.config.magneticRadius);
      targetPosition = this.applyMagneticForce(targetPosition, targets);
    }
    
    return targetPosition;
  }

  /**
   * Calculate snap position relative to another object
   */
  calculateSnapToObject(
    source: THREE.Object3D,
    target: THREE.Object3D,
    edge: 'top' | 'right' | 'bottom' | 'left'
  ): THREE.Vector3 {
    const sourceBox = new THREE.Box3().setFromObject(source);
    const targetBox = new THREE.Box3().setFromObject(target);
    
    const sourceSize = new THREE.Vector3();
    sourceBox.getSize(sourceSize);
    
    const position = source.position.clone();
    
    switch (edge) {
      case 'top':
        position.y = targetBox.max.y + sourceSize.y / 2;
        break;
      case 'right':
        position.x = targetBox.max.x + sourceSize.x / 2;
        break;
      case 'bottom':
        position.y = targetBox.min.y - sourceSize.y / 2;
        break;
      case 'left':
        position.x = targetBox.min.x - sourceSize.x / 2;
        break;
    }
    
    return position;
  }

  // ============================================
  // Grid Snapping
  // ============================================

  /**
   * Snap position to grid
   */
  snapToGrid(position: THREE.Vector3): THREE.Vector3 {
    const { gridSize } = this.config;
    
    return new THREE.Vector3(
      Math.round(position.x / gridSize) * gridSize,
      Math.round(position.y / gridSize) * gridSize,
      Math.round(position.z / gridSize) * gridSize
    );
  }

  /**
   * Check if position is on grid
   */
  isOnGrid(position: THREE.Vector3): boolean {
    const { gridSize } = this.config;
    const epsilon = 0.001;
    
    return (
      Math.abs(position.x % gridSize) < epsilon &&
      Math.abs(position.y % gridSize) < epsilon &&
      Math.abs(position.z % gridSize) < epsilon
    );
  }

  // ============================================
  // Magnetic Snapping
  // ============================================

  /**
   * Apply magnetic force to position based on nearby targets
   */
  applyMagneticForce(
    position: THREE.Vector3,
    targets: SnapTarget[]
  ): THREE.Vector3 {
    const result = position.clone();
    const { magneticStrength, magneticRadius } = this.config;
    
    for (const target of targets) {
      const distance = position.distanceTo(target.position);
      
      if (distance < magneticRadius && distance > 0.001) {
        // Inverse square law for magnetic force
        const normalizedDistance = distance / magneticRadius;
        const force = (magneticStrength / 100) * (1 - normalizedDistance) * 0.1;
        
        // Direction toward target
        const direction = target.position.clone().sub(position).normalize();
        
        // Apply force
        result.add(direction.multiplyScalar(force));
      }
    }
    
    return result;
  }

  /**
   * Calculate magnetic field strength at position
   */
  getMagneticFieldStrength(
    position: THREE.Vector3,
    targets: SnapTarget[]
  ): number {
    const { magneticStrength, magneticRadius } = this.config;
    let totalStrength = 0;
    
    for (const target of targets) {
      const distance = position.distanceTo(target.position);
      
      if (distance < magneticRadius) {
        const normalizedDistance = distance / magneticRadius;
        totalStrength += (magneticStrength / 100) * (1 - normalizedDistance);
      }
    }
    
    return Math.min(1, totalStrength);
  }

  // ============================================
  // Target Detection
  // ============================================

  /**
   * Detect snap targets near position
   */
  detectSnapTargets(
    position: THREE.Vector3,
    radius: number
  ): SnapTarget[] {
    const targets: SnapTarget[] = [];
    
    if (!this.scene) return targets;
    
    this.scene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;
      if (!child.visible) return;
      
      const distance = position.distanceTo(child.position);
      
      if (distance < radius) {
        // Get snap points from object
        const snapPoints = this.getObjectSnapPoints(child);
        
        for (const point of snapPoints) {
          const pointDistance = position.distanceTo(point.position);
          
          if (pointDistance < radius) {
            targets.push({
              position: point.position,
              object: child,
              type: point.type,
              priority: 1 - (pointDistance / radius), // Higher priority for closer
              distance: pointDistance
            });
          }
        }
      }
    });
    
    // Sort by priority (closest first)
    targets.sort((a, b) => b.priority - a.priority);
    
    return targets;
  }

  /**
   * Get snap points from object (center, corners, edges)
   */
  private getObjectSnapPoints(object: THREE.Object3D): Array<{ position: THREE.Vector3; type: SnapType }> {
    const box = new THREE.Box3().setFromObject(object);
    const center = new THREE.Vector3();
    box.getCenter(center);
    
    const points: Array<{ position: THREE.Vector3; type: SnapType }> = [];
    
    // Center point
    points.push({ position: center.clone(), type: 'element' });
    
    // Corner points
    points.push({ position: new THREE.Vector3(box.min.x, box.min.y, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.max.x, box.min.y, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.min.x, box.max.y, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.max.x, box.max.y, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.min.x, box.min.y, box.max.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.max.x, box.min.y, box.max.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.min.x, box.max.y, box.max.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.max.x, box.max.y, box.max.z), type: 'element' });
    
    // Edge midpoints (top/bottom/left/right of front face for simplicity)
    points.push({ position: new THREE.Vector3((box.min.x + box.max.x) / 2, box.min.y, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3((box.min.x + box.max.x) / 2, box.max.y, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.min.x, (box.min.y + box.max.y) / 2, box.min.z), type: 'element' });
    points.push({ position: new THREE.Vector3(box.max.x, (box.min.y + box.max.y) / 2, box.min.z), type: 'element' });
    
    return points;
  }

  // ============================================
  // Gravity Snapping
  // ============================================

  /**
   * Apply gravity-like force toward layout centers
   */
  applyGravityForce(
    position: THREE.Vector3,
    gravityCenter: THREE.Vector3
  ): THREE.Vector3 {
    const { gravityStrength } = this.config;
    
    const direction = gravityCenter.clone().sub(position).normalize();
    const distance = position.distanceTo(gravityCenter);
    
    // Inverse square law
    const force = (gravityStrength / 100) * (1 / Math.max(1, distance * distance)) * 0.5;
    
    return position.clone().add(direction.multiplyScalar(force));
  }

  // ============================================
  // Collision Detection
  // ============================================

  /**
   * Check if position would cause collision
   */
  wouldCollide(
    object: THREE.Object3D,
    position: THREE.Vector3
  ): boolean {
    if (!this.scene) return false;
    
    // Create temporary box at new position
    const box = new THREE.Box3().setFromObject(object);
    const offset = position.clone().sub(object.position);
    box.translate(offset);
    
    let collides = false;
    
    this.scene.traverse((child) => {
      if (child === object) return;
      if (!(child instanceof THREE.Mesh)) return;
      if (!child.visible) return;
      
      const childBox = new THREE.Box3().setFromObject(child);
      
      if (box.intersectsBox(childBox)) {
        collides = true;
      }
    });
    
    return collides;
  }

  // ============================================
  // Utility Methods
  // ============================================

  /**
   * Get all available snap options with metadata
   */
  getSnapOptions(): Array<{
    option: SnapOption;
    label: string;
    description: string;
  }> {
    return [
      { option: 'snap_top', label: 'Top', description: 'Snap to top edge of container' },
      { option: 'snap_right', label: 'Right', description: 'Snap to right edge of container' },
      { option: 'snap_bottom', label: 'Bottom', description: 'Snap to bottom edge of container' },
      { option: 'snap_left', label: 'Left', description: 'Snap to left edge of container' },
      { option: 'snap_center_x', label: 'Center X', description: 'Center horizontally' },
      { option: 'snap_center_y', label: 'Center Y', description: 'Center vertically' },
      { option: 'snap_center_xy', label: 'Center XY', description: 'Center both axes' }
    ];
  }

  /**
   * Calculate distance between two positions
   */
  getDistance(from: THREE.Vector3, to: THREE.Vector3): number {
    return from.distanceTo(to);
  }

  /**
   * Get component distances (ΔX, ΔY, ΔZ)
   */
  getComponentDistances(from: THREE.Vector3, to: THREE.Vector3): {
    deltaX: number;
    deltaY: number;
    deltaZ: number;
    total: number;
  } {
    return {
      deltaX: to.x - from.x,
      deltaY: to.y - from.y,
      deltaZ: to.z - from.z,
      total: from.distanceTo(to)
    };
  }
}

/**
 * Default SnapEngine instance
 */
export default SnapEngine.getInstance();

