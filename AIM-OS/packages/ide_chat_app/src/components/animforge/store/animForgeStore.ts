/**
 * AnimForge Store - Zustand State Management
 * 
 * Complete state management for AnimForge 2D animation system
 * Follows existing Director patterns with AIM-OS integration
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// ===== TYPE DEFINITIONS =====

export type AnimForgeMode = 'draw' | 'rig' | 'animate' | 'mocap' | 'preview'
export type DrawingTool = 'pencil' | 'brush' | 'pen' | 'shapes' | 'text' | 'selection' | 'transform' | 'eraser'
export type RiggingTool = 'bone' | 'ik' | 'weight' | 'select'
export type FrameType = 'empty' | 'keyframe' | 'tweened' | 'static'
export type LayerType = 'drawing' | 'symbol' | 'bone' | 'guide' | 'mask' | 'audio' | 'reference'
export type InterpolationType = 'linear' | 'bezier' | 'stepped'
export type BlendMode = 'normal' | 'multiply' | 'screen' | 'overlay' | 'add'

// Frame definition
export interface AnimationFrame {
  number: number
  type: FrameType
  content: FrameContent | null
  tweenTo: number | null
  label: string | null
}

export interface FrameContent {
  paths: PathData[]
  transforms: TransformData[]
  boneStates: BoneState[]
}

export interface PathData {
  id: string
  points: Point[]
  strokeColor: string
  fillColor: string
  strokeWidth: number
  closed: boolean
}

export interface TransformData {
  id: string
  x: number
  y: number
  rotation: number
  scaleX: number
  scaleY: number
  opacity: number
}

export interface BoneState {
  boneId: string
  rotation: number
  position: Point
}

export interface Point {
  x: number
  y: number
}

// Layer definition
export interface AnimationLayer {
  id: string
  name: string
  type: LayerType
  visible: boolean
  locked: boolean
  opacity: number
  blendMode: BlendMode
  color: string // Layer color coding
  parent: string | null
  frames: AnimationFrame[]
}

// Skeleton/Rigging
export interface Bone {
  id: string
  name: string
  parentId: string | null
  position: Point
  length: number
  rotation: number
  color: string
}

export interface Skeleton {
  id: string
  name: string
  bones: Bone[]
  bindPose: Map<string, BoneState>
}

// Onion Skin settings
export interface OnionSkinSettings {
  enabled: boolean
  previousFrames: number
  nextFrames: number
  previousOpacity: number
  nextOpacity: number
  previousColor: string
  nextColor: string
}

// History for undo/redo
export interface HistoryEntry {
  timestamp: number
  action: string
  state: Partial<AnimForgeState>
}

// ===== STORE STATE =====

export interface AnimForgeState {
  // Project
  projectId: string | null
  projectName: string
  isDirty: boolean

  // Mode
  mode: AnimForgeMode

  // Playback
  currentFrame: number
  totalFrames: number
  frameRate: number
  isPlaying: boolean
  loopEnabled: boolean
  playbackSpeed: number

  // Layers
  layers: AnimationLayer[]
  selectedLayerId: string | null
  selectedFrames: { layerId: string; frameNumber: number }[]

  // Drawing
  currentTool: DrawingTool
  strokeColor: string
  fillColor: string
  strokeWidth: number
  brushSize: number
  smoothing: number

  // Rigging
  riggingTool: RiggingTool
  skeleton: Skeleton | null
  selectedBoneId: string | null
  showBones: boolean
  showWeights: boolean

  // View
  zoomLevel: number
  panPosition: Point
  showGrid: boolean
  showRulers: boolean
  showGuidelines: boolean
  snapEnabled: boolean

  // Onion Skin
  onionSkin: OnionSkinSettings
  showOnionSkin: boolean

  // Timeline
  timelineExpanded: boolean
  timelineZoom: number
  timelineScrollPosition: number

  // History
  history: HistoryEntry[]
  historyIndex: number
  canUndo: boolean
  canRedo: boolean

  // Actions
  setMode: (mode: AnimForgeMode) => void
  setCurrentFrame: (frame: number) => void
  setTotalFrames: (frames: number) => void
  setFrameRate: (fps: number) => void
  play: () => void
  pause: () => void
  togglePlay: () => void
  nextFrame: () => void
  prevFrame: () => void
  firstFrame: () => void
  lastFrame: () => void
  setZoom: (zoom: number) => void
  toggleGrid: () => void
  toggleRulers: () => void
  toggleOnionSkin: () => void
  toggleBones: () => void
  setTimelineExpanded: (expanded: boolean) => void
  
  // Layer actions
  addLayer: (type: LayerType, name?: string) => void
  removeLayer: (id: string) => void
  selectLayer: (id: string | null) => void
  toggleLayerVisibility: (id: string) => void
  toggleLayerLock: (id: string) => void
  reorderLayers: (fromIndex: number, toIndex: number) => void
  
  // Frame actions
  insertKeyframe: (layerId: string, frameNumber: number) => void
  removeKeyframe: (layerId: string, frameNumber: number) => void
  selectFrame: (layerId: string, frameNumber: number) => void
  clearFrameSelection: () => void
  
  // Drawing actions
  setDrawingTool: (tool: DrawingTool) => void
  setStrokeColor: (color: string) => void
  setFillColor: (color: string) => void
  setStrokeWidth: (width: number) => void
  setBrushSize: (size: number) => void
  
  // Rigging actions
  setRiggingTool: (tool: RiggingTool) => void
  addBone: (bone: Omit<Bone, 'id'>) => void
  removeBone: (id: string) => void
  selectBone: (id: string | null) => void
  
  // History actions
  undo: () => void
  redo: () => void
  pushHistory: (action: string) => void
  
  // Project actions
  setProjectDirty: (dirty: boolean) => void
  resetProject: () => void
}

// ===== INITIAL STATE =====

const initialState: Omit<AnimForgeState, 
  'setMode' | 'setCurrentFrame' | 'setTotalFrames' | 'setFrameRate' | 
  'play' | 'pause' | 'togglePlay' | 'nextFrame' | 'prevFrame' | 'firstFrame' | 'lastFrame' |
  'setZoom' | 'toggleGrid' | 'toggleRulers' | 'toggleOnionSkin' | 'toggleBones' |
  'setTimelineExpanded' | 'addLayer' | 'removeLayer' | 'selectLayer' |
  'toggleLayerVisibility' | 'toggleLayerLock' | 'reorderLayers' |
  'insertKeyframe' | 'removeKeyframe' | 'selectFrame' | 'clearFrameSelection' |
  'setDrawingTool' | 'setStrokeColor' | 'setFillColor' | 'setStrokeWidth' | 'setBrushSize' |
  'setRiggingTool' | 'addBone' | 'removeBone' | 'selectBone' |
  'undo' | 'redo' | 'pushHistory' | 'setProjectDirty' | 'resetProject'
> = {
  // Project
  projectId: null,
  projectName: 'Untitled Animation',
  isDirty: false,

  // Mode
  mode: 'draw',

  // Playback
  currentFrame: 1,
  totalFrames: 120,
  frameRate: 24,
  isPlaying: false,
  loopEnabled: true,
  playbackSpeed: 1,

  // Layers
  layers: [
    {
      id: 'layer-1',
      name: 'Layer 1',
      type: 'drawing',
      visible: true,
      locked: false,
      opacity: 100,
      blendMode: 'normal',
      color: '#6366f1', // Indigo
      parent: null,
      frames: Array.from({ length: 120 }, (_, i) => ({
        number: i + 1,
        type: i === 0 ? 'keyframe' : 'empty',
        content: null,
        tweenTo: null,
        label: null
      }))
    }
  ],
  selectedLayerId: 'layer-1',
  selectedFrames: [],

  // Drawing
  currentTool: 'pencil',
  strokeColor: '#ffffff',
  fillColor: 'transparent',
  strokeWidth: 2,
  brushSize: 10,
  smoothing: 0.5,

  // Rigging
  riggingTool: 'bone',
  skeleton: null,
  selectedBoneId: null,
  showBones: true,
  showWeights: false,

  // View
  zoomLevel: 100,
  panPosition: { x: 0, y: 0 },
  showGrid: true,
  showRulers: false,
  showGuidelines: false,
  snapEnabled: true,

  // Onion Skin
  onionSkin: {
    enabled: true,
    previousFrames: 2,
    nextFrames: 1,
    previousOpacity: 0.3,
    nextOpacity: 0.2,
    previousColor: '#ff6b6b', // Red tint
    nextColor: '#4ecdc4', // Green tint
  },
  showOnionSkin: true,

  // Timeline
  timelineExpanded: true,
  timelineZoom: 1,
  timelineScrollPosition: 0,

  // History
  history: [],
  historyIndex: -1,
  canUndo: false,
  canRedo: false,
}

// ===== STORE CREATION =====

export const useAnimForgeStore = create<AnimForgeState>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,

        // Mode
        setMode: (mode) => set((state) => { state.mode = mode }),

        // Playback
        setCurrentFrame: (frame) => set((state) => {
          state.currentFrame = Math.max(1, Math.min(frame, state.totalFrames))
        }),
        
        setTotalFrames: (frames) => set((state) => {
          state.totalFrames = Math.max(1, frames)
          if (state.currentFrame > frames) {
            state.currentFrame = frames
          }
        }),
        
        setFrameRate: (fps) => set((state) => {
          state.frameRate = Math.max(1, Math.min(60, fps))
        }),

        play: () => set((state) => { state.isPlaying = true }),
        pause: () => set((state) => { state.isPlaying = false }),
        togglePlay: () => set((state) => { state.isPlaying = !state.isPlaying }),
        
        nextFrame: () => set((state) => {
          if (state.currentFrame < state.totalFrames) {
            state.currentFrame++
          } else if (state.loopEnabled) {
            state.currentFrame = 1
          }
        }),
        
        prevFrame: () => set((state) => {
          if (state.currentFrame > 1) {
            state.currentFrame--
          } else if (state.loopEnabled) {
            state.currentFrame = state.totalFrames
          }
        }),
        
        firstFrame: () => set((state) => { state.currentFrame = 1 }),
        lastFrame: () => set((state) => { state.currentFrame = state.totalFrames }),

        // View
        setZoom: (zoom) => set((state) => {
          state.zoomLevel = Math.max(25, Math.min(400, zoom))
        }),
        
        toggleGrid: () => set((state) => { state.showGrid = !state.showGrid }),
        toggleRulers: () => set((state) => { state.showRulers = !state.showRulers }),
        toggleOnionSkin: () => set((state) => { state.showOnionSkin = !state.showOnionSkin }),
        toggleBones: () => set((state) => { state.showBones = !state.showBones }),
        
        setTimelineExpanded: (expanded) => set((state) => {
          state.timelineExpanded = expanded
        }),

        // Layer actions
        addLayer: (type, name) => set((state) => {
          const newId = `layer-${Date.now()}`
          const layerColors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6']
          const newLayer: AnimationLayer = {
            id: newId,
            name: name || `Layer ${state.layers.length + 1}`,
            type,
            visible: true,
            locked: false,
            opacity: 100,
            blendMode: 'normal',
            color: layerColors[state.layers.length % layerColors.length],
            parent: null,
            frames: Array.from({ length: state.totalFrames }, (_, i) => ({
              number: i + 1,
              type: 'empty',
              content: null,
              tweenTo: null,
              label: null
            }))
          }
          state.layers.unshift(newLayer)
          state.selectedLayerId = newId
          state.isDirty = true
        }),

        removeLayer: (id) => set((state) => {
          if (state.layers.length <= 1) return // Keep at least one layer
          state.layers = state.layers.filter(l => l.id !== id)
          if (state.selectedLayerId === id) {
            state.selectedLayerId = state.layers[0]?.id || null
          }
          state.isDirty = true
        }),

        selectLayer: (id) => set((state) => { state.selectedLayerId = id }),

        toggleLayerVisibility: (id) => set((state) => {
          const layer = state.layers.find(l => l.id === id)
          if (layer) layer.visible = !layer.visible
        }),

        toggleLayerLock: (id) => set((state) => {
          const layer = state.layers.find(l => l.id === id)
          if (layer) layer.locked = !layer.locked
        }),

        reorderLayers: (fromIndex, toIndex) => set((state) => {
          const [removed] = state.layers.splice(fromIndex, 1)
          state.layers.splice(toIndex, 0, removed)
          state.isDirty = true
        }),

        // Frame actions
        insertKeyframe: (layerId, frameNumber) => set((state) => {
          const layer = state.layers.find(l => l.id === layerId)
          if (layer && frameNumber >= 1 && frameNumber <= state.totalFrames) {
            const frameIndex = frameNumber - 1
            layer.frames[frameIndex] = {
              ...layer.frames[frameIndex],
              type: 'keyframe',
              content: layer.frames[frameIndex].content || {
                paths: [],
                transforms: [],
                boneStates: []
              }
            }
            state.isDirty = true
          }
        }),

        removeKeyframe: (layerId, frameNumber) => set((state) => {
          const layer = state.layers.find(l => l.id === layerId)
          if (layer && frameNumber >= 1 && frameNumber <= state.totalFrames) {
            const frameIndex = frameNumber - 1
            layer.frames[frameIndex] = {
              ...layer.frames[frameIndex],
              type: 'empty',
              content: null
            }
            state.isDirty = true
          }
        }),

        selectFrame: (layerId, frameNumber) => set((state) => {
          const existingIndex = state.selectedFrames.findIndex(
            f => f.layerId === layerId && f.frameNumber === frameNumber
          )
          if (existingIndex >= 0) {
            state.selectedFrames.splice(existingIndex, 1)
          } else {
            state.selectedFrames.push({ layerId, frameNumber })
          }
        }),

        clearFrameSelection: () => set((state) => {
          state.selectedFrames = []
        }),

        // Drawing actions
        setDrawingTool: (tool) => set((state) => { state.currentTool = tool }),
        setStrokeColor: (color) => set((state) => { state.strokeColor = color }),
        setFillColor: (color) => set((state) => { state.fillColor = color }),
        setStrokeWidth: (width) => set((state) => { state.strokeWidth = width }),
        setBrushSize: (size) => set((state) => { state.brushSize = size }),

        // Rigging actions
        setRiggingTool: (tool) => set((state) => { state.riggingTool = tool }),
        
        addBone: (bone) => set((state) => {
          const newBone: Bone = {
            ...bone,
            id: `bone-${Date.now()}`
          }
          if (!state.skeleton) {
            state.skeleton = {
              id: `skeleton-${Date.now()}`,
              name: 'Character Skeleton',
              bones: [],
              bindPose: new Map()
            }
          }
          state.skeleton.bones.push(newBone)
          state.isDirty = true
        }),

        removeBone: (id) => set((state) => {
          if (state.skeleton) {
            state.skeleton.bones = state.skeleton.bones.filter(b => b.id !== id)
            if (state.selectedBoneId === id) {
              state.selectedBoneId = null
            }
            state.isDirty = true
          }
        }),

        selectBone: (id) => set((state) => { state.selectedBoneId = id }),

        // History actions
        undo: () => set((state) => {
          if (state.historyIndex > 0) {
            state.historyIndex--
            const entry = state.history[state.historyIndex]
            if (entry) {
              Object.assign(state, entry.state)
            }
          }
          state.canUndo = state.historyIndex > 0
          state.canRedo = state.historyIndex < state.history.length - 1
        }),

        redo: () => set((state) => {
          if (state.historyIndex < state.history.length - 1) {
            state.historyIndex++
            const entry = state.history[state.historyIndex]
            if (entry) {
              Object.assign(state, entry.state)
            }
          }
          state.canUndo = state.historyIndex > 0
          state.canRedo = state.historyIndex < state.history.length - 1
        }),

        pushHistory: (action) => set((state) => {
          // Remove any future history entries
          state.history = state.history.slice(0, state.historyIndex + 1)
          
          // Add new entry
          state.history.push({
            timestamp: Date.now(),
            action,
            state: {
              layers: JSON.parse(JSON.stringify(state.layers)),
              skeleton: state.skeleton ? JSON.parse(JSON.stringify(state.skeleton)) : null,
            }
          })
          
          state.historyIndex = state.history.length - 1
          state.canUndo = true
          state.canRedo = false
          
          // Limit history size
          if (state.history.length > 100) {
            state.history.shift()
            state.historyIndex--
          }
        }),

        // Project actions
        setProjectDirty: (dirty) => set((state) => { state.isDirty = dirty }),
        
        resetProject: () => set((state) => {
          Object.assign(state, initialState)
        }),
      })),
      {
        name: 'animforge-storage',
        partialize: (state) => ({
          // Only persist these fields
          onionSkin: state.onionSkin,
          showGrid: state.showGrid,
          showRulers: state.showRulers,
          frameRate: state.frameRate,
          strokeColor: state.strokeColor,
          fillColor: state.fillColor,
          strokeWidth: state.strokeWidth,
          brushSize: state.brushSize,
        })
      }
    ),
    { name: 'AnimForge' }
  )
)

export default useAnimForgeStore

