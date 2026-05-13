/**
 * AnimForge Timeline Component
 * 
 * Frame-by-frame animation timeline (like Flash/Animate)
 * Features:
 * - Frame grid with keyframe diamonds (●)
 * - Multi-layer support
 * - Onion skin controls
 * - Playback controls
 * - FPS selector
 * - Loop toggle
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import React, { useRef, useCallback, useState } from 'react'
import {
  Play, Pause, SkipBack, SkipForward, ChevronFirst, ChevronLast,
  Plus, Trash2, Eye, EyeOff, Lock, Unlock, ChevronUp, ChevronDown,
  Repeat, ZoomIn, ZoomOut, Settings
} from 'lucide-react'
import { useAnimForgeStore, AnimationLayer, FrameType } from './store/animForgeStore'

interface AnimForgeTimelineProps {
  expanded: boolean
  onToggleExpand: () => void
}

export const AnimForgeTimeline: React.FC<AnimForgeTimelineProps> = ({
  expanded,
  onToggleExpand
}) => {
  const {
    currentFrame,
    totalFrames,
    frameRate,
    isPlaying,
    loopEnabled,
    layers,
    selectedLayerId,
    onionSkin,
    showOnionSkin,
    play,
    pause,
    nextFrame,
    prevFrame,
    firstFrame,
    lastFrame,
    setCurrentFrame,
    setFrameRate,
    addLayer,
    removeLayer,
    selectLayer,
    toggleLayerVisibility,
    toggleLayerLock,
    insertKeyframe,
    removeKeyframe,
    toggleOnionSkin
  } = useAnimForgeStore()

  const timelineRef = useRef<HTMLDivElement>(null)
  const [timelineZoom, setTimelineZoom] = useState(1)
  const frameWidth = 20 * timelineZoom

  // Frame click handler
  const handleFrameClick = useCallback((layerId: string, frameNumber: number) => {
    setCurrentFrame(frameNumber)
    selectLayer(layerId)
  }, [setCurrentFrame, selectLayer])

  // Frame double-click handler (insert/remove keyframe)
  const handleFrameDoubleClick = useCallback((layerId: string, frameNumber: number) => {
    const layer = layers.find(l => l.id === layerId)
    if (!layer) return

    const frame = layer.frames[frameNumber - 1]
    if (frame.type === 'keyframe') {
      removeKeyframe(layerId, frameNumber)
    } else {
      insertKeyframe(layerId, frameNumber)
    }
  }, [layers, insertKeyframe, removeKeyframe])

  // Frame type indicator
  const getFrameIndicator = (type: FrameType): string => {
    switch (type) {
      case 'keyframe': return '●'
      case 'tweened': return '○'
      case 'static': return '▪'
      default: return ''
    }
  }

  // Frame background color
  const getFrameColor = (type: FrameType, isSelected: boolean, isCurrent: boolean): string => {
    if (isCurrent) return 'bg-purple-600'
    if (isSelected) return 'bg-blue-600/50'
    
    switch (type) {
      case 'keyframe': return 'bg-gray-700'
      case 'tweened': return 'bg-gray-600'
      case 'static': return 'bg-gray-650'
      default: return 'bg-gray-800'
    }
  }

  // Mini timeline (collapsed)
  if (!expanded) {
    return (
      <div className="h-full flex items-center px-4 gap-4">
        {/* Playback controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={firstFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
          >
            <ChevronFirst className="w-4 h-4" />
          </button>
          <button
            onClick={prevFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={isPlaying ? pause : play}
            className="p-2 text-white bg-purple-600 hover:bg-purple-500 rounded"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={nextFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
          >
            <SkipForward className="w-4 h-4" />
          </button>
          <button
            onClick={lastFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
          >
            <ChevronLast className="w-4 h-4" />
          </button>
        </div>

        {/* Scrubber */}
        <div className="flex-1 h-2 bg-gray-800 rounded-full relative">
          <div 
            className="absolute h-full bg-purple-600 rounded-full"
            style={{ width: `${(currentFrame / totalFrames) * 100}%` }}
          />
          <input
            type="range"
            min={1}
            max={totalFrames}
            value={currentFrame}
            onChange={(e) => setCurrentFrame(parseInt(e.target.value))}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
        </div>

        {/* Frame display */}
        <div className="text-sm font-mono">
          <span className="text-white">{currentFrame}</span>
          <span className="text-gray-500"> / </span>
          <span className="text-gray-400">{totalFrames}</span>
        </div>

        {/* Stats */}
        <div className="text-xs text-gray-500">
          Layers: {layers.length} | FPS: {frameRate}
        </div>

        {/* Expand button */}
        <button
          onClick={onToggleExpand}
          className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
          title="Expand timeline"
        >
          <ChevronUp className="w-4 h-4" />
        </button>
      </div>
    )
  }

  // Expanded timeline
  return (
    <div className="h-full flex flex-col">
      {/* Timeline toolbar */}
      <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center px-4 gap-4 shrink-0">
        {/* Playback controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={firstFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="First Frame (Home)"
          >
            <ChevronFirst className="w-4 h-4" />
          </button>
          <button
            onClick={prevFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Previous Frame (←)"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={isPlaying ? pause : play}
            className="p-2 text-white bg-purple-600 hover:bg-purple-500 rounded"
            title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={nextFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Next Frame (→)"
          >
            <SkipForward className="w-4 h-4" />
          </button>
          <button
            onClick={lastFrame}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Last Frame (End)"
          >
            <ChevronLast className="w-4 h-4" />
          </button>
        </div>

        <div className="h-6 w-px bg-gray-700" />

        {/* FPS selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">FPS:</span>
          <select
            value={frameRate}
            onChange={(e) => setFrameRate(parseInt(e.target.value))}
            className="bg-gray-700 text-white text-xs px-2 py-1 rounded border border-gray-600"
          >
            <option value={12}>12</option>
            <option value={15}>15</option>
            <option value={24}>24</option>
            <option value={30}>30</option>
            <option value={60}>60</option>
          </select>
        </div>

        {/* Loop toggle */}
        <button
          onClick={() => useAnimForgeStore.setState({ loopEnabled: !loopEnabled })}
          className={`p-1.5 rounded transition-colors ${
            loopEnabled ? 'text-purple-400 bg-purple-900/30' : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          title="Loop playback"
        >
          <Repeat className="w-4 h-4" />
        </button>

        <div className="h-6 w-px bg-gray-700" />

        {/* Onion skin controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleOnionSkin}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              showOnionSkin ? 'text-orange-400 bg-orange-900/30' : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            👁️ Onion
          </button>
          {showOnionSkin && (
            <>
              <span className="text-xs text-gray-400">Prev:</span>
              <input
                type="number"
                min={0}
                max={5}
                value={onionSkin.previousFrames}
                onChange={(e) => useAnimForgeStore.setState(state => ({
                  onionSkin: { ...state.onionSkin, previousFrames: parseInt(e.target.value) || 0 }
                }))}
                className="w-10 bg-gray-700 text-white text-xs px-1 py-0.5 rounded border border-gray-600 text-center"
              />
              <span className="text-xs text-gray-400">Next:</span>
              <input
                type="number"
                min={0}
                max={5}
                value={onionSkin.nextFrames}
                onChange={(e) => useAnimForgeStore.setState(state => ({
                  onionSkin: { ...state.onionSkin, nextFrames: parseInt(e.target.value) || 0 }
                }))}
                className="w-10 bg-gray-700 text-white text-xs px-1 py-0.5 rounded border border-gray-600 text-center"
              />
            </>
          )}
        </div>

        <div className="flex-1" />

        {/* Timeline zoom */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setTimelineZoom(Math.max(0.5, timelineZoom - 0.25))}
            className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <ZoomOut className="w-3 h-3" />
          </button>
          <span className="text-xs text-gray-400 w-12 text-center">{Math.round(timelineZoom * 100)}%</span>
          <button
            onClick={() => setTimelineZoom(Math.min(3, timelineZoom + 0.25))}
            className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <ZoomIn className="w-3 h-3" />
          </button>
        </div>

        {/* Collapse button */}
        <button
          onClick={onToggleExpand}
          className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          title="Collapse timeline"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* Timeline content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Layer controls */}
        <div className="w-48 bg-gray-850 border-r border-gray-700 flex flex-col shrink-0">
          {/* Layer header */}
          <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-center px-2 gap-2">
            <button
              onClick={() => addLayer('drawing')}
              className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
              title="Add layer"
            >
              <Plus className="w-4 h-4" />
            </button>
            <span className="text-xs text-gray-400">Layers</span>
          </div>

          {/* Layer list */}
          <div className="flex-1 overflow-y-auto">
            {layers.map((layer, index) => (
              <div
                key={layer.id}
                className={`h-8 flex items-center px-2 gap-1 border-b border-gray-700 cursor-pointer ${
                  selectedLayerId === layer.id ? 'bg-blue-900/30' : 'hover:bg-gray-800'
                }`}
                onClick={() => selectLayer(layer.id)}
              >
                {/* Visibility */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleLayerVisibility(layer.id)
                  }}
                  className="p-0.5 hover:bg-gray-700 rounded"
                >
                  {layer.visible ? (
                    <Eye className="w-3 h-3 text-gray-400" />
                  ) : (
                    <EyeOff className="w-3 h-3 text-gray-600" />
                  )}
                </button>

                {/* Lock */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleLayerLock(layer.id)
                  }}
                  className="p-0.5 hover:bg-gray-700 rounded"
                >
                  {layer.locked ? (
                    <Lock className="w-3 h-3 text-yellow-400" />
                  ) : (
                    <Unlock className="w-3 h-3 text-gray-600" />
                  )}
                </button>

                {/* Color indicator */}
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: layer.color }}
                />

                {/* Name */}
                <span className="flex-1 text-xs text-gray-300 truncate">
                  {layer.name}
                </span>

                {/* Delete */}
                {layers.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      removeLayer(layer.id)
                    }}
                    className="p-0.5 text-gray-600 hover:text-red-400 hover:bg-gray-700 rounded opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Frame grid */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Frame ruler */}
          <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-end overflow-x-auto" ref={timelineRef}>
            <div className="flex" style={{ minWidth: totalFrames * frameWidth }}>
              {Array.from({ length: totalFrames }, (_, i) => i + 1).map(frame => (
                <div
                  key={frame}
                  className={`flex items-center justify-center text-xs border-r border-gray-700 ${
                    frame === currentFrame ? 'bg-purple-600 text-white' : 'text-gray-500'
                  }`}
                  style={{ width: frameWidth, minWidth: frameWidth }}
                  onClick={() => setCurrentFrame(frame)}
                >
                  {frame % 5 === 0 || frame === 1 ? frame : ''}
                </div>
              ))}
            </div>
          </div>

          {/* Layer frames */}
          <div className="flex-1 overflow-auto">
            {layers.map(layer => (
              <div
                key={layer.id}
                className={`h-8 flex border-b border-gray-700 ${
                  selectedLayerId === layer.id ? 'bg-blue-900/10' : ''
                }`}
              >
                {layer.frames.map((frame, index) => {
                  const frameNumber = index + 1
                  const isCurrent = frameNumber === currentFrame
                  const isSelected = selectedLayerId === layer.id

                  return (
                    <div
                      key={frameNumber}
                      className={`flex items-center justify-center border-r border-gray-700 cursor-pointer transition-colors ${
                        getFrameColor(frame.type, isSelected && isCurrent, isCurrent)
                      } hover:brightness-110`}
                      style={{ width: frameWidth, minWidth: frameWidth }}
                      onClick={() => handleFrameClick(layer.id, frameNumber)}
                      onDoubleClick={() => handleFrameDoubleClick(layer.id, frameNumber)}
                      title={`Frame ${frameNumber} - ${frame.type}`}
                    >
                      <span className={`text-xs ${
                        frame.type === 'keyframe' ? 'text-white' : 'text-gray-500'
                      }`}>
                        {getFrameIndicator(frame.type)}
                      </span>
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline footer */}
      <div className="h-8 bg-gray-800 border-t border-gray-700 flex items-center px-4 gap-4 shrink-0">
        <button
          onClick={() => addLayer('drawing')}
          className="px-2 py-1 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded flex items-center gap-1"
        >
          <Plus className="w-3 h-3" />
          Add Layer
        </button>

        <div className="flex-1" />

        <div className="text-xs text-gray-500">
          Frame: <span className="text-white font-mono">{currentFrame}</span> / {totalFrames}
          {' | '}
          Layers: {layers.length}
          {' | '}
          {frameRate} FPS
          {loopEnabled && ' | Loop'}
        </div>
      </div>
    </div>
  )
}

export default AnimForgeTimeline

