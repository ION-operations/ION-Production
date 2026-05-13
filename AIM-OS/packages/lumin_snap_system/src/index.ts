/**
 * Lumin Snap System
 * @module @lumin/snap-system
 * 
 * Intelligent 8-type snap system with ghost preview and LOD optimization for Lumin3D.
 * 
 * @example
 * ```tsx
 * import { 
 *   GhostPreviewRenderer, 
 *   SnapOptionPanel, 
 *   LODManager, 
 *   SnapEngine 
 * } from '@lumin/snap-system';
 * 
 * // In your 3D scene
 * <GhostPreviewRenderer
 *   originalObject={selectedMesh}
 *   targetPosition={targetPos}
 *   snapOption="snap_top"
 *   scene={scene}
 * />
 * 
 * // In your UI
 * <SnapOptionPanel
 *   selectedObject={selectedMesh}
 *   onSnapOptionHover={handleHover}
 *   onSnapOptionLeave={handleLeave}
 *   onSnapOptionClick={handleClick}
 * />
 * ```
 */

// ============================================
// Components
// ============================================

export { GhostPreviewRenderer } from './components/GhostPreviewRenderer';
export { default as GhostPreviewRendererDefault } from './components/GhostPreviewRenderer';

export { SnapOptionPanel } from './components/SnapOptionPanel';
export { default as SnapOptionPanelDefault } from './components/SnapOptionPanel';

// ============================================
// Utilities
// ============================================

export { LODManager } from './utils/LODManager';
export { default as LODManagerInstance } from './utils/LODManager';

export { SnapEngine } from './utils/SnapEngine';
export { default as SnapEngineInstance } from './utils/SnapEngine';

// ============================================
// Types
// ============================================

export type {
  // LOD Types
  LODLevel,
  LODCacheEntry,
  LODStats,
  
  // Snap Types
  SnapOption,
  SnapType,
  SnapTarget,
  SnapConfig,
  SnapPreset,
  SnapOptionMeta,
  
  // Ghost Preview Types
  Collision,
  CollisionSeverity,
  Measurement,
  GhostPreviewState,
  GhostRenderEvent,
  
  // Event Types
  SnapOptionHoverEvent,
  SnapOptionClickEvent,
  
  // Component Props
  GhostPreviewRendererProps,
  SnapOptionPanelProps,
  
  // Hook Return Types
  UseSnapEngineReturn,
  UseGhostPreviewReturn,
  UseLODManagerReturn
} from './types';

export {
  // LOD Constants
  LODLevel as LODLevelEnum,
  LOD_THRESHOLDS,
  
  // Snap Constants
  SNAP_OPTIONS,
  SNAP_PRESETS,
  DEFAULT_SNAP_CONFIG,
  
  // Ghost Constants
  GHOST_COLORS,
  INITIAL_GHOST_STATE
} from './types';

// ============================================
// Version
// ============================================

export const VERSION = '1.0.0';

