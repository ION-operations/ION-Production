/**
 * AnimForge - Revolutionary 2D Animation System
 * 
 * Browser-based 2D animation page for Lucid Director
 * Combines traditional animation (Flash-style) with AI-powered features
 * 
 * Features:
 * - Frame-by-frame timeline (like Flash/Animate)
 * - AI Auto-Rigging (MediaPipe keypoint detection)
 * - Webcam Motion Capture (real-time pose → character)
 * - AI Inbetweening (smooth frame generation)
 * - Onion skinning (ghost previous/next frames)
 * - Skeletal rigging system (bones, weights, IK/FK)
 * 
 * AIM-OS Integration:
 * - CMC: Character/animation storage
 * - HHNI: Character consistency
 * - VIF: Quality confidence tracking
 * - TCS: Animation timeline tracking
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import React, { useState, useCallback, useRef, useEffect } from 'react'
import {
  Play, Pause, SkipBack, SkipForward, ChevronFirst, ChevronLast,
  Pencil, Brush, PenTool, Square, Type, MousePointer2, Move,
  Bone, Target, Paintbrush, Bot, Video, Sparkles,
  Users, Library, Film, Settings, Layers, Palette, Sliders,
  Eye, EyeOff, Lock, Unlock, Plus, Trash2, Copy, 
  ZoomIn, ZoomOut, Grid3X3, Ruler, Magnet, RotateCcw, RotateCw,
  Maximize2, Minimize2, ChevronDown, ChevronUp
} from 'lucide-react'
import { AnimForgeCanvas } from './AnimForgeCanvas'
import { AnimForgeTimeline } from './AnimForgeTimeline'
import { AnimForgeToolbar } from './AnimForgeToolbar'
import { AnimForgeMiniBar } from './AnimForgeMiniBar'
import { AnimForgeDrawers } from './AnimForgeDrawers'
import { useAnimForgeStore } from './store/animForgeStore'

// ===== TYPE DEFINITIONS =====

export type AnimForgeMode = 'draw' | 'rig' | 'animate' | 'mocap' | 'preview'

export interface AnimForgeProps {
  projectId?: string
  onSave?: () => void
  onExport?: () => void
}

// ===== MAIN ANIMFORGE COMPONENT =====

export const AnimForge: React.FC<AnimForgeProps> = ({
  projectId,
  onSave,
  onExport
}) => {
  // Store
  const {
    mode,
    setMode,
    currentFrame,
    totalFrames,
    isPlaying,
    frameRate,
    zoomLevel,
    showGrid,
    showRulers,
    showOnionSkin,
    showBones,
    timelineExpanded,
    setTimelineExpanded,
    play,
    pause,
    nextFrame,
    prevFrame,
    firstFrame,
    lastFrame,
    setZoom,
    toggleGrid,
    toggleRulers,
    toggleOnionSkin,
    toggleBones,
    undo,
    redo,
    canUndo,
    canRedo
  } = useAnimForgeStore()

  // Local state
  const [leftDrawer, setLeftDrawer] = useState<string | null>(null)
  const [rightDrawer, setRightDrawer] = useState<string | null>(null)
  const canvasRef = useRef<HTMLDivElement>(null)

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return

      // Playback
      if (e.code === 'Space') {
        e.preventDefault()
        isPlaying ? pause() : play()
      }
      
      // Frame navigation
      if (e.code === 'ArrowRight' && !e.shiftKey) {
        e.preventDefault()
        nextFrame()
      }
      if (e.code === 'ArrowLeft' && !e.shiftKey) {
        e.preventDefault()
        prevFrame()
      }
      if (e.code === 'Home') {
        e.preventDefault()
        firstFrame()
      }
      if (e.code === 'End') {
        e.preventDefault()
        lastFrame()
      }

      // Undo/Redo
      if (e.ctrlKey && e.code === 'KeyZ' && !e.shiftKey) {
        e.preventDefault()
        undo()
      }
      if (e.ctrlKey && e.code === 'KeyZ' && e.shiftKey) {
        e.preventDefault()
        redo()
      }
      if (e.ctrlKey && e.code === 'KeyY') {
        e.preventDefault()
        redo()
      }

      // Mode switching (1-5)
      if (e.code === 'Digit1' && !e.ctrlKey) setMode('draw')
      if (e.code === 'Digit2' && !e.ctrlKey) setMode('rig')
      if (e.code === 'Digit3' && !e.ctrlKey) setMode('animate')
      if (e.code === 'Digit4' && !e.ctrlKey) setMode('mocap')
      if (e.code === 'Digit5' && !e.ctrlKey) setMode('preview')

      // View toggles
      if (e.code === 'KeyG' && !e.ctrlKey) toggleGrid()
      if (e.code === 'KeyO' && !e.ctrlKey) toggleOnionSkin()
      if (e.code === 'KeyB' && !e.ctrlKey) toggleBones()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isPlaying, play, pause, nextFrame, prevFrame, firstFrame, lastFrame, undo, redo, setMode, toggleGrid, toggleOnionSkin, toggleBones])

  return (
    <div className="h-full flex flex-col bg-gray-950 text-gray-100 overflow-hidden">
      {/* ===== TOP BAR ===== */}
      <div className="h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4 gap-4 shrink-0">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Film className="w-5 h-5 text-purple-400" />
          <span className="font-bold text-sm">AnimForge</span>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-gray-700" />

        {/* File Operations */}
        <div className="flex items-center gap-1">
          <button
            onClick={onSave}
            className="px-3 py-1.5 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors"
          >
            💾 Save
          </button>
          <button
            onClick={onExport}
            className="px-3 py-1.5 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors"
          >
            📤 Export
          </button>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-gray-700" />

        {/* Undo/Redo */}
        <div className="flex items-center gap-1">
          <button
            onClick={undo}
            disabled={!canUndo}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded disabled:opacity-30 disabled:cursor-not-allowed"
            title="Undo (Ctrl+Z)"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={redo}
            disabled={!canRedo}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded disabled:opacity-30 disabled:cursor-not-allowed"
            title="Redo (Ctrl+Y)"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-gray-700" />

        {/* View Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setZoom(Math.max(25, zoomLevel - 25))}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs text-gray-400 w-12 text-center">{zoomLevel}%</span>
          <button
            onClick={() => setZoom(Math.min(400, zoomLevel + 25))}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          
          <div className="h-4 w-px bg-gray-700 mx-1" />
          
          <button
            onClick={toggleGrid}
            className={`p-1.5 rounded transition-colors ${showGrid ? 'text-blue-400 bg-blue-900/30' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
            title="Toggle Grid (G)"
          >
            <Grid3X3 className="w-4 h-4" />
          </button>
          <button
            onClick={toggleRulers}
            className={`p-1.5 rounded transition-colors ${showRulers ? 'text-blue-400 bg-blue-900/30' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
            title="Toggle Rulers"
          >
            <Ruler className="w-4 h-4" />
          </button>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-gray-700" />

        {/* Playback Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={firstFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
            title="First Frame (Home)"
          >
            <ChevronFirst className="w-4 h-4" />
          </button>
          <button
            onClick={prevFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
            title="Previous Frame (←)"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={isPlaying ? pause : play}
            className="p-2 text-white bg-purple-600 hover:bg-purple-500 rounded transition-colors"
            title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={nextFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
            title="Next Frame (→)"
          >
            <SkipForward className="w-4 h-4" />
          </button>
          <button
            onClick={lastFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
            title="Last Frame (End)"
          >
            <ChevronLast className="w-4 h-4" />
          </button>
        </div>

        {/* Frame Display */}
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-400">Frame:</span>
          <span className="font-mono text-white">{currentFrame}</span>
          <span className="text-gray-500">/</span>
          <span className="font-mono text-gray-400">{totalFrames}</span>
          <span className="text-gray-500 text-xs ml-2">@ {frameRate}fps</span>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Animation View Toggles */}
        <div className="flex items-center gap-1">
          <button
            onClick={toggleOnionSkin}
            className={`px-2 py-1.5 text-xs rounded transition-colors flex items-center gap-1 ${
              showOnionSkin ? 'text-orange-400 bg-orange-900/30' : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
            title="Toggle Onion Skin (O)"
          >
            👁️ Onion
          </button>
          <button
            onClick={toggleBones}
            className={`px-2 py-1.5 text-xs rounded transition-colors flex items-center gap-1 ${
              showBones ? 'text-cyan-400 bg-cyan-900/30' : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
            title="Toggle Bones (B)"
          >
            🦴 Bones
          </button>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center bg-gray-800 rounded-lg p-1">
          {[
            { id: 'draw', icon: Pencil, label: 'Draw', key: '1' },
            { id: 'rig', icon: Bone, label: 'Rig', key: '2' },
            { id: 'animate', icon: Film, label: 'Animate', key: '3' },
            { id: 'mocap', icon: Video, label: 'Mocap', key: '4' },
            { id: 'preview', icon: Play, label: 'Preview', key: '5' },
          ].map(({ id, icon: Icon, label, key }) => (
            <button
              key={id}
              onClick={() => setMode(id as AnimForgeMode)}
              className={`px-3 py-1.5 text-xs rounded flex items-center gap-1.5 transition-colors ${
                mode === id
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              title={`${label} Mode (${key})`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* ===== MAIN CONTENT ===== */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Icon Bar */}
        <AnimForgeToolbar 
          side="left"
          activeDrawer={leftDrawer}
          onDrawerChange={setLeftDrawer}
          mode={mode}
        />

        {/* Left Drawer */}
        <AnimForgeDrawers
          side="left"
          activeDrawer={leftDrawer}
          onClose={() => setLeftDrawer(null)}
          mode={mode}
        />

        {/* Canvas Area */}
        <div ref={canvasRef} className="flex-1 relative overflow-hidden">
          <AnimForgeCanvas
            mode={mode}
            showGrid={showGrid}
            showRulers={showRulers}
            showOnionSkin={showOnionSkin}
            showBones={showBones}
            zoomLevel={zoomLevel}
          />
        </div>

        {/* Right Drawer */}
        <AnimForgeDrawers
          side="right"
          activeDrawer={rightDrawer}
          onClose={() => setRightDrawer(null)}
          mode={mode}
        />

        {/* Frame Mini Bar */}
        <AnimForgeMiniBar />

        {/* Right Icon Bar */}
        <AnimForgeToolbar
          side="right"
          activeDrawer={rightDrawer}
          onDrawerChange={setRightDrawer}
          mode={mode}
        />
      </div>

      {/* ===== BOTTOM TIMELINE ===== */}
      <div 
        className={`shrink-0 bg-gray-900 border-t border-gray-800 transition-all duration-300 ${
          timelineExpanded ? 'h-64' : 'h-16'
        }`}
      >
        <AnimForgeTimeline
          expanded={timelineExpanded}
          onToggleExpand={() => setTimelineExpanded(!timelineExpanded)}
        />
      </div>
    </div>
  )
}

export default AnimForge

