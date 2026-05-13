/**
 * AnimForge Drawers Component
 * 
 * Drawer panels for tools, properties, and AI features
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import React from 'react'
import {
  X, Pencil, Brush, PenTool, Square, Type, MousePointer2, Move, Eraser,
  Bone, Target, Paintbrush, Bot, Video, Sparkles,
  Users, Library, Film, Settings, Layers, Palette, Sliders,
  Upload, Camera, Play, Pause, Circle
} from 'lucide-react'
import { useAnimForgeStore, AnimForgeMode, DrawingTool, RiggingTool } from './store/animForgeStore'

interface AnimForgeDrawersProps {
  side: 'left' | 'right'
  activeDrawer: string | null
  onClose: () => void
  mode: AnimForgeMode
}

export const AnimForgeDrawers: React.FC<AnimForgeDrawersProps> = ({
  side,
  activeDrawer,
  onClose,
  mode
}) => {
  if (!activeDrawer) return null

  return (
    <div 
      className={`w-72 bg-gray-850 border-gray-800 flex flex-col shrink-0 ${
        side === 'left' ? 'border-r' : 'border-l'
      }`}
    >
      <DrawerContent drawer={activeDrawer} onClose={onClose} />
    </div>
  )
}

// Drawer content router
const DrawerContent: React.FC<{ drawer: string; onClose: () => void }> = ({ drawer, onClose }) => {
  switch (drawer) {
    // Drawing tools
    case 'pencil':
    case 'brush':
    case 'pen':
    case 'eraser':
      return <DrawingToolDrawer tool={drawer} onClose={onClose} />
    case 'shapes':
      return <ShapesDrawer onClose={onClose} />
    case 'selection':
    case 'transform':
      return <SelectionDrawer onClose={onClose} />
    
    // Rigging tools
    case 'rigging':
      return <RiggingDrawer onClose={onClose} />
    case 'ik':
      return <IKDrawer onClose={onClose} />
    case 'weights':
      return <WeightsDrawer onClose={onClose} />
    
    // AI tools
    case 'autorig':
      return <AutoRigDrawer onClose={onClose} />
    case 'mocap':
      return <MocapDrawer onClose={onClose} />
    case 'inbetween':
      return <InbetweenDrawer onClose={onClose} />
    
    // Library
    case 'characters':
      return <CharactersDrawer onClose={onClose} />
    case 'symbols':
      return <SymbolsDrawer onClose={onClose} />
    case 'animations':
      return <AnimationsDrawer onClose={onClose} />
    
    // Properties
    case 'properties':
      return <PropertiesDrawer onClose={onClose} />
    case 'color':
      return <ColorDrawer onClose={onClose} />
    case 'layers':
      return <LayersDrawer onClose={onClose} />
    
    default:
      return <PlaceholderDrawer title={drawer} onClose={onClose} />
  }
}

// Drawer header component
const DrawerHeader: React.FC<{ title: string; icon?: React.ElementType; onClose: () => void }> = ({ 
  title, icon: Icon, onClose 
}) => (
  <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center px-3 gap-2 shrink-0">
    {Icon && <Icon className="w-4 h-4 text-purple-400" />}
    <span className="flex-1 text-sm font-semibold text-gray-200">{title}</span>
    <button
      onClick={onClose}
      className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
    >
      <X className="w-4 h-4" />
    </button>
  </div>
)

// ===== DRAWING TOOL DRAWERS =====

const DrawingToolDrawer: React.FC<{ tool: string; onClose: () => void }> = ({ tool, onClose }) => {
  const { strokeColor, fillColor, strokeWidth, brushSize, setStrokeColor, setFillColor, setStrokeWidth, setBrushSize } = useAnimForgeStore()

  const titles: Record<string, string> = {
    pencil: 'Pencil Tool',
    brush: 'Brush Tool',
    pen: 'Pen Tool',
    eraser: 'Eraser'
  }

  return (
    <>
      <DrawerHeader title={titles[tool] || tool} icon={Pencil} onClose={onClose} />
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Stroke Color */}
        <div>
          <label className="text-xs text-gray-400 block mb-2">Stroke Color</label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={strokeColor}
              onChange={(e) => setStrokeColor(e.target.value)}
              className="w-10 h-10 rounded cursor-pointer bg-transparent"
            />
            <input
              type="text"
              value={strokeColor}
              onChange={(e) => setStrokeColor(e.target.value)}
              className="flex-1 bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700"
            />
          </div>
        </div>

        {/* Fill Color */}
        {tool !== 'eraser' && (
          <div>
            <label className="text-xs text-gray-400 block mb-2">Fill Color</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={fillColor === 'transparent' ? '#000000' : fillColor}
                onChange={(e) => setFillColor(e.target.value)}
                className="w-10 h-10 rounded cursor-pointer bg-transparent"
              />
              <input
                type="text"
                value={fillColor}
                onChange={(e) => setFillColor(e.target.value)}
                className="flex-1 bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700"
              />
            </div>
          </div>
        )}

        {/* Stroke Width */}
        <div>
          <label className="text-xs text-gray-400 block mb-2">
            Stroke Width: {strokeWidth}px
          </label>
          <input
            type="range"
            min={1}
            max={50}
            value={strokeWidth}
            onChange={(e) => setStrokeWidth(parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Brush Size (for brush tool) */}
        {tool === 'brush' && (
          <div>
            <label className="text-xs text-gray-400 block mb-2">
              Brush Size: {brushSize}px
            </label>
            <input
              type="range"
              min={1}
              max={100}
              value={brushSize}
              onChange={(e) => setBrushSize(parseInt(e.target.value))}
              className="w-full"
            />
          </div>
        )}

        {/* Smoothing */}
        <div>
          <label className="text-xs text-gray-400 block mb-2">Smoothing</label>
          <input
            type="range"
            min={0}
            max={100}
            defaultValue={50}
            className="w-full"
          />
        </div>
      </div>
    </>
  )
}

const ShapesDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Shape Tools" icon={Square} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4">
      <div className="grid grid-cols-3 gap-2">
        {['Rectangle', 'Ellipse', 'Polygon', 'Star', 'Line', 'Arrow'].map(shape => (
          <button
            key={shape}
            className="aspect-square bg-gray-800 hover:bg-gray-700 rounded flex items-center justify-center text-gray-400 hover:text-white transition-colors"
          >
            <span className="text-xs">{shape}</span>
          </button>
        ))}
      </div>
    </div>
  </>
)

const SelectionDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Selection" icon={MousePointer2} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Click and drag to select objects on the canvas.
      </div>
      <div className="space-y-2">
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm text-left">
          Select All (Ctrl+A)
        </button>
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm text-left">
          Deselect All (Ctrl+D)
        </button>
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm text-left">
          Invert Selection
        </button>
      </div>
    </div>
  </>
)

// ===== RIGGING DRAWERS =====

const RiggingDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { skeleton, addBone, selectBone, selectedBoneId } = useAnimForgeStore()

  return (
    <>
      <DrawerHeader title="Rigging Tools" icon={Bone} onClose={onClose} />
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="text-xs text-gray-400">
          Click and drag on canvas to create bones. Click bones to select.
        </div>

        {/* Bone list */}
        <div>
          <label className="text-xs text-gray-400 block mb-2">Bones</label>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {skeleton?.bones.map(bone => (
              <button
                key={bone.id}
                onClick={() => selectBone(bone.id)}
                className={`w-full px-3 py-2 rounded text-sm text-left flex items-center gap-2 ${
                  selectedBoneId === bone.id ? 'bg-purple-600' : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: bone.color }} />
                <span>{bone.name}</span>
              </button>
            )) || (
              <div className="text-xs text-gray-500 py-2">No bones created yet</div>
            )}
          </div>
        </div>

        {/* Quick actions */}
        <div className="space-y-2">
          <button className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm">
            + Add Bone
          </button>
          <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
            Mirror Skeleton
          </button>
          <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
            Reset Bind Pose
          </button>
        </div>
      </div>
    </>
  )
}

const IKDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="IK/FK Tools" icon={Target} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Create IK chains for natural limb movement.
      </div>
      <div className="space-y-2">
        <button className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm">
          Create IK Chain
        </button>
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
          Convert to FK
        </button>
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
          Add IK Constraint
        </button>
      </div>
    </div>
  </>
)

const WeightsDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Weight Painting" icon={Paintbrush} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Paint bone influence weights on your character.
      </div>
      
      {/* Brush settings */}
      <div>
        <label className="text-xs text-gray-400 block mb-2">Brush Size</label>
        <input type="range" min={1} max={100} defaultValue={20} className="w-full" />
      </div>
      <div>
        <label className="text-xs text-gray-400 block mb-2">Weight Value</label>
        <input type="range" min={0} max={100} defaultValue={100} className="w-full" />
      </div>
      <div>
        <label className="text-xs text-gray-400 block mb-2">Falloff</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>Linear</option>
          <option>Smooth</option>
          <option>Sharp</option>
        </select>
      </div>

      <div className="space-y-2">
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
          Auto-Calculate Weights
        </button>
        <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
          Normalize Weights
        </button>
      </div>
    </div>
  </>
)

// ===== AI DRAWERS =====

const AutoRigDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="AI Auto-Rig" icon={Bot} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Automatically rig your character using AI keypoint detection.
      </div>

      {/* Upload section */}
      <div className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center">
        <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
        <p className="text-sm text-gray-400">Drop character image here</p>
        <p className="text-xs text-gray-500 mt-1">or click to browse</p>
      </div>

      {/* Settings */}
      <div>
        <label className="text-xs text-gray-400 block mb-2">Detection Model</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>MediaPipe Pose</option>
          <option>OpenPose</option>
          <option>Custom Model</option>
        </select>
      </div>

      <div>
        <label className="text-xs text-gray-400 block mb-2">Skeleton Type</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>Humanoid</option>
          <option>Creature (4 legs)</option>
          <option>Bird</option>
          <option>Custom</option>
        </select>
      </div>

      <div>
        <label className="text-xs text-gray-400 block mb-2">Bone Complexity</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>Simple (10 bones)</option>
          <option>Standard (20 bones)</option>
          <option>Complex (40+ bones)</option>
        </select>
      </div>

      <button className="w-full px-3 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded text-sm font-semibold">
        🤖 Generate Rig (~5 seconds)
      </button>
    </div>
  </>
)

const MocapDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const [isRecording, setIsRecording] = React.useState(false)
  const [cameraEnabled, setCameraEnabled] = React.useState(false)

  return (
    <>
      <DrawerHeader title="Motion Capture" icon={Video} onClose={onClose} />
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="text-xs text-gray-400">
          Capture your movements with webcam and apply to character.
        </div>

        {/* Camera preview */}
        <div className="aspect-video bg-gray-800 rounded-lg flex items-center justify-center">
          {cameraEnabled ? (
            <div className="text-center">
              <Camera className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <p className="text-xs text-gray-400">Camera active</p>
            </div>
          ) : (
            <button
              onClick={() => setCameraEnabled(true)}
              className="text-center"
            >
              <Camera className="w-8 h-8 text-gray-500 mx-auto mb-2" />
              <p className="text-xs text-gray-400">Click to enable camera</p>
            </button>
          )}
        </div>

        {/* Settings */}
        <div className="flex items-center gap-2">
          <input type="checkbox" id="mirror" defaultChecked className="rounded" />
          <label htmlFor="mirror" className="text-sm text-gray-400">Mirror horizontally</label>
        </div>

        <div>
          <label className="text-xs text-gray-400 block mb-2">Smoothing</label>
          <input type="range" min={0} max={100} defaultValue={70} className="w-full" />
        </div>

        {/* Recording controls */}
        <div className="space-y-2">
          {isRecording ? (
            <button
              onClick={() => setIsRecording(false)}
              className="w-full px-3 py-3 bg-red-600 hover:bg-red-500 rounded text-sm font-semibold flex items-center justify-center gap-2"
            >
              <Pause className="w-4 h-4" />
              Stop Recording
            </button>
          ) : (
            <button
              onClick={() => setIsRecording(true)}
              disabled={!cameraEnabled}
              className="w-full px-3 py-3 bg-red-600 hover:bg-red-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-sm font-semibold flex items-center justify-center gap-2"
            >
              <Circle className="w-4 h-4 fill-current" />
              Start Recording
            </button>
          )}
          <button className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
            Apply to Character
          </button>
        </div>
      </div>
    </>
  )
}

const InbetweenDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="AI Inbetweening" icon={Sparkles} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Generate smooth in-between frames using AI.
      </div>

      {/* Frame selection */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-gray-400 block mb-2">Start Frame</label>
          <input
            type="number"
            defaultValue={1}
            className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700"
          />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-2">End Frame</label>
          <input
            type="number"
            defaultValue={30}
            className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700"
          />
        </div>
      </div>

      {/* Settings */}
      <div>
        <label className="text-xs text-gray-400 block mb-2">Method</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>AI Neural (Best Quality)</option>
          <option>Traditional Tween</option>
          <option>Motion Blur</option>
        </select>
      </div>

      <div>
        <label className="text-xs text-gray-400 block mb-2">Style</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>Maintain Art Style</option>
          <option>Smooth Motion</option>
          <option>Stylized</option>
        </select>
      </div>

      <div>
        <label className="text-xs text-gray-400 block mb-2">Quality</label>
        <select className="w-full bg-gray-800 text-white text-sm px-2 py-1 rounded border border-gray-700">
          <option>High (Slower)</option>
          <option>Medium</option>
          <option>Low (Faster)</option>
        </select>
      </div>

      <button className="w-full px-3 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded text-sm font-semibold">
        ✨ Generate Inbetweens
      </button>
    </div>
  </>
)

// ===== LIBRARY DRAWERS =====

const CharactersDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Characters" icon={Users} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Import characters from Casting Studio or create new ones.
      </div>
      <button className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm">
        Import from Casting Studio
      </button>
      <div className="grid grid-cols-2 gap-2">
        {['Character 1', 'Character 2', 'Character 3'].map(char => (
          <div key={char} className="aspect-square bg-gray-800 rounded flex items-center justify-center">
            <span className="text-xs text-gray-500">{char}</span>
          </div>
        ))}
      </div>
    </div>
  </>
)

const SymbolsDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Symbols" icon={Library} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Reusable symbols (like Flash symbols). Drag to stage.
      </div>
      <button className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm">
        + Create Symbol
      </button>
      <div className="text-xs text-gray-500 py-4 text-center">
        No symbols yet
      </div>
    </div>
  </>
)

const AnimationsDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Animations" icon={Film} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Saved animation clips. Drag to timeline.
      </div>
      <button className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm">
        + Save Current Animation
      </button>
      <div className="text-xs text-gray-500 py-4 text-center">
        No saved animations
      </div>
    </div>
  </>
)

// ===== PROPERTY DRAWERS =====

const PropertiesDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => (
  <>
    <DrawerHeader title="Properties" icon={Sliders} onClose={onClose} />
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="text-xs text-gray-400">
        Select an object to view its properties.
      </div>
    </div>
  </>
)

const ColorDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { strokeColor, fillColor, setStrokeColor, setFillColor } = useAnimForgeStore()

  return (
    <>
      <DrawerHeader title="Color" icon={Palette} onClose={onClose} />
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Color pickers */}
        <div>
          <label className="text-xs text-gray-400 block mb-2">Stroke</label>
          <input
            type="color"
            value={strokeColor}
            onChange={(e) => setStrokeColor(e.target.value)}
            className="w-full h-10 rounded cursor-pointer"
          />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-2">Fill</label>
          <input
            type="color"
            value={fillColor === 'transparent' ? '#000000' : fillColor}
            onChange={(e) => setFillColor(e.target.value)}
            className="w-full h-10 rounded cursor-pointer"
          />
        </div>

        {/* Swatches */}
        <div>
          <label className="text-xs text-gray-400 block mb-2">Swatches</label>
          <div className="grid grid-cols-8 gap-1">
            {[
              '#ffffff', '#000000', '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff',
              '#f87171', '#fb923c', '#fbbf24', '#a3e635', '#34d399', '#22d3ee', '#818cf8', '#e879f9'
            ].map(color => (
              <button
                key={color}
                onClick={() => setStrokeColor(color)}
                className="w-6 h-6 rounded border border-gray-700"
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

const LayersDrawer: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { layers, selectedLayerId, selectLayer, toggleLayerVisibility, toggleLayerLock, addLayer, removeLayer } = useAnimForgeStore()

  return (
    <>
      <DrawerHeader title="Layers" icon={Layers} onClose={onClose} />
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {layers.map(layer => (
          <div
            key={layer.id}
            onClick={() => selectLayer(layer.id)}
            className={`px-3 py-2 rounded flex items-center gap-2 cursor-pointer ${
              selectedLayerId === layer.id ? 'bg-purple-600' : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            <button onClick={(e) => { e.stopPropagation(); toggleLayerVisibility(layer.id) }}>
              {layer.visible ? '👁️' : '🔒'}
            </button>
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: layer.color }} />
            <span className="flex-1 text-sm truncate">{layer.name}</span>
          </div>
        ))}
      </div>
      <div className="p-2 border-t border-gray-700">
        <button
          onClick={() => addLayer('drawing')}
          className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm"
        >
          + Add Layer
        </button>
      </div>
    </>
  )
}

// Placeholder drawer
const PlaceholderDrawer: React.FC<{ title: string; onClose: () => void }> = ({ title, onClose }) => (
  <>
    <DrawerHeader title={title} onClose={onClose} />
    <div className="flex-1 flex items-center justify-center p-4">
      <div className="text-center text-gray-500">
        <div className="text-4xl mb-2">🚧</div>
        <div className="text-sm">Coming soon</div>
      </div>
    </div>
  </>
)

export default AnimForgeDrawers

