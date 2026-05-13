/**
 * AnimForge Mini Bar Component
 * 
 * Vertical frame thumbnails bar (right side)
 * Shows frame previews for quick navigation
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import React, { useMemo } from 'react'
import { useAnimForgeStore, FrameType } from './store/animForgeStore'

export const AnimForgeMiniBar: React.FC = () => {
  const {
    currentFrame,
    totalFrames,
    layers,
    setCurrentFrame
  } = useAnimForgeStore()

  // Generate frame thumbnails (simplified - just indicators)
  const frameThumbnails = useMemo(() => {
    return Array.from({ length: Math.min(totalFrames, 50) }, (_, i) => {
      const frameNumber = i + 1
      const isCurrent = frameNumber === currentFrame
      
      // Check if any layer has a keyframe at this position
      const hasKeyframe = layers.some(layer => {
        const frame = layer.frames[frameNumber - 1]
        return frame?.type === 'keyframe'
      })

      // Check if any layer has content
      const hasContent = layers.some(layer => {
        const frame = layer.frames[frameNumber - 1]
        return frame?.type !== 'empty'
      })

      return {
        frameNumber,
        isCurrent,
        hasKeyframe,
        hasContent
      }
    })
  }, [currentFrame, totalFrames, layers])

  return (
    <div className="w-10 bg-gray-900 border-l border-gray-800 flex flex-col shrink-0">
      {/* Header */}
      <div className="h-8 flex items-center justify-center border-b border-gray-800">
        <span className="text-xs text-gray-500 font-mono">F</span>
      </div>

      {/* Frame list */}
      <div className="flex-1 overflow-y-auto py-1">
        {frameThumbnails.map(({ frameNumber, isCurrent, hasKeyframe, hasContent }) => (
          <button
            key={frameNumber}
            onClick={() => setCurrentFrame(frameNumber)}
            className={`w-full h-8 flex items-center justify-center relative transition-colors ${
              isCurrent
                ? 'bg-purple-600'
                : hasKeyframe
                ? 'bg-gray-700 hover:bg-gray-600'
                : hasContent
                ? 'bg-gray-800 hover:bg-gray-700'
                : 'hover:bg-gray-800'
            }`}
            title={`Frame ${frameNumber}${hasKeyframe ? ' (Keyframe)' : ''}`}
          >
            {/* Frame number */}
            <span className={`text-xs font-mono ${
              isCurrent ? 'text-white' : 'text-gray-500'
            }`}>
              {frameNumber}
            </span>

            {/* Keyframe indicator */}
            {hasKeyframe && !isCurrent && (
              <div className="absolute right-1 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-yellow-400" />
            )}

            {/* Current frame indicator */}
            {isCurrent && (
              <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-white" />
            )}
          </button>
        ))}
      </div>

      {/* Footer with current frame */}
      <div className="h-8 flex items-center justify-center border-t border-gray-800">
        <span className="text-xs text-gray-400 font-mono">{currentFrame}</span>
      </div>
    </div>
  )
}

export default AnimForgeMiniBar

