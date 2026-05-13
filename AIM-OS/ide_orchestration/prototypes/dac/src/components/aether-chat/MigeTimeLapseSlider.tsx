/**
 * MIGE Time-Lapse Slider Component
 * Phase 5 Week 19: MIGE Time-Lapse
 * 
 * Implements:
 * - Time-lapse slider UI
 * - Past/present navigation
 * - State restoration on slider change
 * - Idea evolution visualization
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Clock, Play, Pause, SkipBack, SkipForward, RotateCcw } from 'lucide-react'
import { retrieveMigeTimeline, restoreStateFromSnapshot, convertToMigeTimelineData, type IdeaSnapshot } from '../../services/aetherChat/migeTimeLapse'
import type { MigeTimelineData } from '../../types/aetherChatTypes'

export interface MigeTimeLapseSliderProps {
  ideaAtomId: string
  onStateRestore?: (snapshot: IdeaSnapshot, contextWeb?: any, evidencePack?: any) => void
  className?: string
}

export const MigeTimeLapseSlider: React.FC<MigeTimeLapseSliderProps> = ({
  ideaAtomId,
  onStateRestore,
  className = ''
}) => {
  const [timeline, setTimeline] = useState<MigeTimelineData | null>(null)
  const [currentIndex, setCurrentIndex] = useState<number>(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load timeline on mount
  useEffect(() => {
    loadTimeline()
  }, [ideaAtomId])

  // Auto-play functionality
  useEffect(() => {
    if (isPlaying && timeline && currentIndex < timeline.snapshots.length - 1) {
      const timer = setTimeout(() => {
        setCurrentIndex(prev => Math.min(prev + 1, timeline.snapshots.length - 1))
      }, 1000) // 1 second per snapshot
      return () => clearTimeout(timer)
    } else if (isPlaying && currentIndex >= (timeline?.snapshots.length || 0) - 1) {
      setIsPlaying(false) // Stop at end
    }
  }, [isPlaying, currentIndex, timeline])

  const loadTimeline = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const timelineData = await retrieveMigeTimeline(ideaAtomId)
      
      if (timelineData) {
        const migeData = convertToMigeTimelineData(timelineData)
        setTimeline(migeData)
        // Start at the most recent snapshot
        setCurrentIndex(migeData.snapshots.length - 1)
      } else {
        setError('No timeline data found for this idea')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline')
    } finally {
      setLoading(false)
    }
  }

  const handleSliderChange = useCallback(async (index: number) => {
    if (!timeline || index < 0 || index >= timeline.snapshots.length) {
      return
    }

    setCurrentIndex(index)
    setIsPlaying(false) // Stop auto-play when manually changing

    // Restore state from snapshot
    try {
      const snapshot = timeline.snapshots[index]
      const restored = await restoreStateFromSnapshot({
        timestamp: snapshot.timestamp,
        validTime: snapshot.timestamp,
        transactionTime: snapshot.timestamp,
        stage: snapshot.stage,
        contextState: snapshot.contextState,
        segAnchors: snapshot.segAnchors,
        ideaAtomId: timeline.ideaAtomId
      })

      if (restored.success && onStateRestore) {
        onStateRestore(
          {
            timestamp: snapshot.timestamp,
            validTime: snapshot.timestamp,
            transactionTime: snapshot.timestamp,
            stage: snapshot.stage,
            contextState: snapshot.contextState,
            segAnchors: snapshot.segAnchors,
            ideaAtomId: timeline.ideaAtomId
          },
          restored.contextWeb,
          restored.evidencePack
        )
      }
    } catch (err) {
      console.error('[MIGE Time-Lapse] Failed to restore state:', err)
    }
  }, [timeline, onStateRestore])

  const handlePrevious = () => {
    if (currentIndex > 0) {
      handleSliderChange(currentIndex - 1)
    }
  }

  const handleNext = () => {
    if (timeline && currentIndex < timeline.snapshots.length - 1) {
      handleSliderChange(currentIndex + 1)
    }
  }

  const handlePlayPause = () => {
    if (timeline && currentIndex >= timeline.snapshots.length - 1) {
      // Reset to beginning if at end
      setCurrentIndex(0)
    }
    setIsPlaying(!isPlaying)
  }

  const handleReset = () => {
    if (timeline) {
      // Reset to most recent snapshot
      const lastIndex = timeline.snapshots.length - 1
      handleSliderChange(lastIndex)
    }
  }

  if (loading) {
    return (
      <div className={`mige-time-lapse-loading ${className}`}>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="w-4 h-4 animate-spin" />
          <span>Loading timeline...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`mige-time-lapse-error ${className}`}>
        <div className="text-sm text-red-500">{error}</div>
        <button
          onClick={loadTimeline}
          className="mt-2 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!timeline || timeline.snapshots.length === 0) {
    return (
      <div className={`mige-time-lapse-empty ${className}`}>
        <div className="text-sm text-gray-500">No timeline data available</div>
      </div>
    )
  }

  const currentSnapshot = timeline.snapshots[currentIndex]
  const progress = timeline.snapshots.length > 1 
    ? (currentIndex / (timeline.snapshots.length - 1)) * 100 
    : 0

  return (
    <div className={`mige-time-lapse-slider ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium">Idea Evolution Timeline</span>
          <span className="text-xs text-gray-500">
            ({currentIndex + 1} / {timeline.snapshots.length})
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleReset}
            className="p-1 hover:bg-gray-100 rounded"
            title="Reset to present"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stage Badge */}
      <div className="mb-3">
        <span className={`inline-block px-2 py-1 text-xs rounded ${
          currentSnapshot.stage === 'SEED' ? 'bg-blue-100 text-blue-800' :
          currentSnapshot.stage === 'VISION_TENSOR' ? 'bg-purple-100 text-purple-800' :
          currentSnapshot.stage === 'TRUNK_INDEX' ? 'bg-green-100 text-green-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {currentSnapshot.stage}
        </span>
        <span className="ml-2 text-xs text-gray-500">
          {new Date(currentSnapshot.timestamp).toLocaleString()}
        </span>
      </div>

      {/* Slider */}
      <div className="mb-4">
        <input
          type="range"
          min={0}
          max={timeline.snapshots.length - 1}
          value={currentIndex}
          onChange={(e) => handleSliderChange(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${progress}%, #e5e7eb ${progress}%, #e5e7eb 100%)`
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Past</span>
          <span>Present</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2 mb-4">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Previous snapshot"
        >
          <SkipBack className="w-4 h-4" />
        </button>
        <button
          onClick={handlePlayPause}
          className="p-2 hover:bg-gray-100 rounded"
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
        </button>
        <button
          onClick={handleNext}
          disabled={currentIndex >= timeline.snapshots.length - 1}
          className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Next snapshot"
        >
          <SkipForward className="w-4 h-4" />
        </button>
      </div>

      {/* Context State Info */}
      <div className="text-xs text-gray-600 space-y-1">
        <div>
          <span className="font-medium">Open Files:</span>{' '}
          {currentSnapshot.contextState.openFiles.length > 0
            ? currentSnapshot.contextState.openFiles.join(', ')
            : 'None'}
        </div>
        <div>
          <span className="font-medium">VIF Confidence:</span>{' '}
          {(currentSnapshot.contextState.vifConfidence * 100).toFixed(0)}%
        </div>
        <div>
          <span className="font-medium">SEG Anchors:</span>{' '}
          {currentSnapshot.segAnchors.length}
        </div>
      </div>
    </div>
  )
}

