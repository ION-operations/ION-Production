/**
 * AnimForge - Revolutionary 2D Animation System
 * 
 * Browser-based 2D animation page for Lucid Director
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

// Main component
export { AnimForge, default } from './AnimForge'
export type { AnimForgeProps, AnimForgeMode } from './AnimForge'

// Sub-components
export { AnimForgeCanvas } from './AnimForgeCanvas'
export { AnimForgeTimeline } from './AnimForgeTimeline'
export { AnimForgeToolbar } from './AnimForgeToolbar'
export { AnimForgeMiniBar } from './AnimForgeMiniBar'
export { AnimForgeDrawers } from './AnimForgeDrawers'

// Store
export { useAnimForgeStore } from './store/animForgeStore'
export type {
  AnimForgeState,
  AnimationFrame,
  AnimationLayer,
  Bone,
  Skeleton,
  OnionSkinSettings,
  DrawingTool,
  RiggingTool,
  FrameType,
  LayerType,
  InterpolationType,
  BlendMode,
  Point,
  PathData,
  TransformData,
  BoneState,
  FrameContent,
  HistoryEntry
} from './store/animForgeStore'

