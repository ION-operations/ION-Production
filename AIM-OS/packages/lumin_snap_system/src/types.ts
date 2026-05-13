/**
 * Lumin Snap System - Type Definitions
 * @module @lumin/snap-system/types
 */

import * as THREE from 'three';

// ============================================
// LOD Types
// ============================================

/**
 * Level of Detail levels for ghost preview rendering
 */
export enum LODLevel {
  /** Full geometry with materials - <1,000 polygons */
  FULL_DETAIL = 'full_detail',
  
  /** 50% polygon reduction - 1,000-10,000 polygons */
  SIMPLIFIED_MESH = 'simplified_mesh',
  
  /** Bounding box + wireframe overlay - 10,000-100,000 polygons */
  WIREFRAME = 'wireframe',
  
  /** Bounding box only - >100,000 polygons */
  BOUNDING_BOX = 'bounding_box'
}

/**
 * Performance thresholds for LOD selection (in milliseconds)
 */
export const LOD_THRESHOLDS = {
  FULL_DETAIL: { maxPolygons: 1000, targetMs: 5 },
  SIMPLIFIED_MESH: { maxPolygons: 10000, targetMs: 10 },
  WIREFRAME: { maxPolygons: 100000, targetMs: 15 },
  BOUNDING_BOX: { maxPolygons: Infinity, targetMs: 20 }
} as const;

/**
 * Cache entry for LOD objects
 */
export interface LODCacheEntry {
  object: THREE.Object3D;
  level: LODLevel;
  createdAt: number;
  accessCount: number;
}

/**
 * LOD statistics for monitoring
 */
export interface LODStats {
  cacheEntries: number;
  cacheHits: number;
  cacheMisses: number;
  averageRenderTimeMs: number;
  memoryUsageMB: number;
}

// ============================================
// Snap Types
// ============================================

/**
 * Available snap options for positioning objects
 */
export type SnapOption = 
  | 'snap_top'
  | 'snap_right'
  | 'snap_bottom'
  | 'snap_left'
  | 'snap_center_x'
  | 'snap_center_y'
  | 'snap_center_xy';

/**
 * All snap option IDs
 */
export const SNAP_OPTIONS: SnapOption[] = [
  'snap_top',
  'snap_right',
  'snap_bottom',
  'snap_left',
  'snap_center_x',
  'snap_center_y',
  'snap_center_xy'
];

/**
 * Snap option metadata for UI
 */
export interface SnapOptionMeta {
  id: SnapOption;
  label: string;
  description: string;
  icon: string;
  shortcut?: string;
}

/**
 * Available snap types (from SnapConfigPanel)
 */
export type SnapType = 
  | 'grid'
  | 'element'
  | 'guide'
  | 'magnetic'
  | 'semantic'
  | 'gravity'
  | 'fluid'
  | 'layout_inference';

/**
 * Snap target detected in scene
 */
export interface SnapTarget {
  position: THREE.Vector3;
  object: THREE.Object3D;
  type: SnapType;
  priority: number;
  distance: number;
}

/**
 * Snap configuration settings
 */
export interface SnapConfig {
  /** Grid size in units (default: 10) */
  gridSize: number;
  
  /** Snap threshold distance in units (default: 15) */
  snapThreshold: number;
  
  /** Magnetic attraction strength 0-100 (default: 75) */
  magneticStrength: number;
  
  /** Magnetic attraction radius in units (default: 50) */
  magneticRadius: number;
  
  /** Gravity strength 0-100 (default: 60) */
  gravityStrength: number;
  
  /** Enabled snap types */
  enabledTypes: SnapType[];
  
  /** Show visual feedback */
  showVisualFeedback: boolean;
  
  /** Enable ghost preview on hover */
  enableGhostPreview: boolean;
}

/**
 * Default snap configuration
 */
export const DEFAULT_SNAP_CONFIG: SnapConfig = {
  gridSize: 10,
  snapThreshold: 15,
  magneticStrength: 75,
  magneticRadius: 50,
  gravityStrength: 60,
  enabledTypes: ['grid', 'element', 'magnetic'],
  showVisualFeedback: true,
  enableGhostPreview: true
};

/**
 * Snap preset configurations
 */
export interface SnapPreset {
  name: string;
  description: string;
  config: Partial<SnapConfig>;
}

/**
 * Built-in snap presets
 */
export const SNAP_PRESETS: SnapPreset[] = [
  {
    name: 'Precise',
    description: 'Fine-grained snapping for technical work',
    config: { gridSize: 5, snapThreshold: 8, magneticStrength: 60, gravityStrength: 40 }
  },
  {
    name: 'Balanced',
    description: 'Default settings for general use',
    config: { gridSize: 10, snapThreshold: 15, magneticStrength: 75, gravityStrength: 60 }
  },
  {
    name: 'Magnetic',
    description: 'Strong magnetic attraction for quick roughing',
    config: { gridSize: 15, snapThreshold: 20, magneticStrength: 90, gravityStrength: 80 }
  },
  {
    name: 'Fluid',
    description: 'Maximum fluidity for organic layouts',
    config: { gridSize: 20, snapThreshold: 25, magneticStrength: 95, gravityStrength: 90 }
  }
];

// ============================================
// Ghost Preview Types
// ============================================

/**
 * Collision severity levels
 */
export type CollisionSeverity = 'minor' | 'moderate' | 'severe';

/**
 * Detected collision with another object
 */
export interface Collision {
  /** The object being collided with */
  object: THREE.Object3D;
  
  /** Depth of penetration in units */
  penetrationDepth: number;
  
  /** Severity classification */
  severity: CollisionSeverity;
  
  /** Suggested resolution */
  resolution?: 'adjust_position' | 'resize_object' | 'remove_obstacle';
}

/**
 * Measurement line for visual feedback
 */
export interface Measurement {
  from: THREE.Vector3;
  to: THREE.Vector3;
  label: string;
  color: number;
  type: 'distance' | 'delta_x' | 'delta_y' | 'delta_z';
}

/**
 * Ghost preview state
 */
export interface GhostPreviewState {
  /** Is ghost preview currently active */
  isActive: boolean;
  
  /** Original object being previewed */
  originalObject: THREE.Object3D | null;
  
  /** Target snap position */
  targetPosition: THREE.Vector3 | null;
  
  /** Current snap option being previewed */
  snapOption: SnapOption | null;
  
  /** LOD level used for ghost */
  lodLevel: LODLevel | null;
  
  /** Detected collisions */
  collisions: Collision[];
  
  /** Measurement lines */
  measurements: Measurement[];
  
  /** Last render time in ms */
  renderTimeMs: number;
  
  /** Ghost color (hex) */
  color: number;
}

/**
 * Initial ghost preview state
 */
export const INITIAL_GHOST_STATE: GhostPreviewState = {
  isActive: false,
  originalObject: null,
  targetPosition: null,
  snapOption: null,
  lodLevel: null,
  collisions: [],
  measurements: [],
  renderTimeMs: 0,
  color: 0x00ffff
};

/**
 * Ghost preview colors
 */
export const GHOST_COLORS = {
  /** Safe position - no collisions */
  VALID: 0x00ffff,    // Cyan
  
  /** Tight fit - close to other objects */
  WARNING: 0xffff00,  // Yellow
  
  /** Collision detected */
  COLLISION: 0xff0000, // Red
  
  /** Magnetic attraction active */
  MAGNETIC: 0xff00ff   // Magenta
} as const;

// ============================================
// Event Types
// ============================================

/**
 * Snap option hover event
 */
export interface SnapOptionHoverEvent {
  option: SnapOption;
  targetPosition: THREE.Vector3;
  originalObject: THREE.Object3D;
}

/**
 * Snap option click event
 */
export interface SnapOptionClickEvent {
  option: SnapOption;
  targetPosition: THREE.Vector3;
  originalObject: THREE.Object3D;
  previousPosition: THREE.Vector3;
}

/**
 * Ghost preview render event
 */
export interface GhostRenderEvent {
  lodLevel: LODLevel;
  renderTimeMs: number;
  polygonCount: number;
  collisionCount: number;
}

// ============================================
// Component Props
// ============================================

/**
 * GhostPreviewRenderer component props
 */
export interface GhostPreviewRendererProps {
  /** Object to create ghost from */
  originalObject: THREE.Object3D | null;
  
  /** Target position for ghost */
  targetPosition: THREE.Vector3 | null;
  
  /** Current snap option */
  snapOption: SnapOption | null;
  
  /** Scene for collision detection */
  scene: THREE.Scene;
  
  /** Callback when ghost render completes */
  onRenderComplete?: (event: GhostRenderEvent) => void;
  
  /** Ghost opacity (0-1) */
  opacity?: number;
  
  /** Enable collision detection */
  enableCollisionDetection?: boolean;
  
  /** Enable measurements */
  enableMeasurements?: boolean;
}

/**
 * SnapOptionPanel component props
 */
export interface SnapOptionPanelProps {
  /** Currently selected object */
  selectedObject: THREE.Object3D | null;
  
  /** Callback when hovering snap option */
  onSnapOptionHover: (event: SnapOptionHoverEvent) => void;
  
  /** Callback when leaving snap option */
  onSnapOptionLeave: () => void;
  
  /** Callback when clicking snap option */
  onSnapOptionClick: (event: SnapOptionClickEvent) => void;
  
  /** Current snap configuration */
  config?: SnapConfig;
  
  /** Custom class name */
  className?: string;
  
  /** Show keyboard shortcuts */
  showShortcuts?: boolean;
}

// ============================================
// Hook Return Types
// ============================================

/**
 * useSnapEngine hook return type
 */
export interface UseSnapEngineReturn {
  /** Calculate snap position for option */
  calculateSnapPosition: (object: THREE.Object3D, option: SnapOption) => THREE.Vector3;
  
  /** Detect snap targets near position */
  detectSnapTargets: (position: THREE.Vector3, radius: number) => SnapTarget[];
  
  /** Apply magnetic force to position */
  applyMagneticForce: (position: THREE.Vector3, targets: SnapTarget[]) => THREE.Vector3;
  
  /** Update snap configuration */
  updateConfig: (config: Partial<SnapConfig>) => void;
  
  /** Current configuration */
  config: SnapConfig;
}

/**
 * useGhostPreview hook return type
 */
export interface UseGhostPreviewReturn {
  /** Current ghost state */
  state: GhostPreviewState;
  
  /** Show ghost preview */
  showPreview: (object: THREE.Object3D, position: THREE.Vector3, option: SnapOption) => void;
  
  /** Hide ghost preview */
  hidePreview: () => void;
  
  /** Update ghost position */
  updatePosition: (position: THREE.Vector3) => void;
}

/**
 * useLODManager hook return type
 */
export interface UseLODManagerReturn {
  /** Select appropriate LOD level for object */
  selectLOD: (object: THREE.Object3D) => LODLevel;
  
  /** Create LOD version of object */
  createLODObject: (object: THREE.Object3D, level: LODLevel) => THREE.Object3D;
  
  /** Get polygon count for object */
  countPolygons: (object: THREE.Object3D) => number;
  
  /** Get cache statistics */
  getStats: () => LODStats;
  
  /** Clear LOD cache */
  clearCache: () => void;
}

