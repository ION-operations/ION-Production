import React, { useState, useEffect } from 'react'
import { Play, Pause, RotateCcw, ChevronLeft, ChevronRight, Clock } from 'lucide-react'
import { getMCPAPI } from '../services/mcpApi'

interface TimelineEntry {
  id: string
  sequence: number
  timestamp: Date
  eventType: string
  content: string
}

interface TemporalNavigationBarProps {
  filePath: string
  currentSequence: number
  totalSequences: number
  onNavigate: (sequence: number) => void
  onPlay: () => void
  onPause: () => void
  onReset: () => void
  playbackSpeed: number
  onSpeedChange: (speed: number) => void
  className?: string
}

export const TemporalNavigationBar: React.FC<TemporalNavigationBarProps> = ({
  filePath,
  currentSequence,
  totalSequences,
  onNavigate,
  onPlay,
  onPause,
  onReset,
  playbackSpeed,
  onSpeedChange,
  className = ''
}) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [versionMarkers, setVersionMarkers] = useState<{ sequence: number; label: string }[]>([])
  const [selectedMarker, setSelectedMarker] = useState<number | null>(null)

  // Fetch real timeline data from AIM-OS
  useEffect(() => {
    const fetchTimelineData = async () => {
      const mcpApi = getMCPAPI()
      
      try {
        // Fetch timeline entries for this file via MCP
        const timelineResponse = await mcpApi.executeTool('get_timeline_entries', {
          limit: 100,
          // TODO: Add file filter when available
        })
        
        if (timelineResponse.success && timelineResponse.result?.entries) {
          const entries = timelineResponse.result.entries
          
          // Extract version markers from significant events
          const markers = entries
            .filter((entry: any, idx: number) => {
              // Mark significant events (every 10th entry, or entries with specific types)
              return idx % 10 === 0 || 
                     entry.event_type === 'modification' || 
                     entry.event_type === 'execution'
            })
            .slice(0, 10)
            .map((entry: any, idx: number) => ({
              sequence: entry.sequence || idx + 1,
              label: entry.event_type === 'modification' ? 'Code Change' :
                     entry.event_type === 'execution' ? 'Execution' :
                     entry.event_type === 'test' ? 'Test Run' :
                     `Event ${idx + 1}`
            }))
          
          setVersionMarkers(markers)
          
          // Update total sequences if available
          if (entries.length > 0) {
            const maxSequence = Math.max(...entries.map((e: any) => e.sequence || 0))
            if (maxSequence > totalSequences) {
              // Note: We can't directly update totalSequences prop, but we can use it
            }
          }
        }
      } catch (error) {
        console.warn('Failed to fetch timeline data, using fallback:', error)
        // Fallback to mock markers
        setVersionMarkers([
          { sequence: 10, label: 'Initial commit' },
          { sequence: 25, label: 'Feature added' },
          { sequence: 50, label: 'Refactor' },
          { sequence: 75, label: 'Bug fix' }
        ])
      }
    }

    fetchTimelineData()
  }, [filePath, totalSequences])

  const handlePlay = () => {
    setIsPlaying(true)
    onPlay()
  }

  const handlePause = () => {
    setIsPlaying(false)
    onPause()
  }

  const handleReset = () => {
    setIsPlaying(false)
    onReset()
  }

  const handlePrevious = () => {
    if (currentSequence > 1) {
      onNavigate(currentSequence - 1)
    }
  }

  const handleNext = () => {
    if (currentSequence < totalSequences) {
      onNavigate(currentSequence + 1)
    }
  }

  const handleMarkerClick = (sequence: number) => {
    setSelectedMarker(sequence)
    onNavigate(sequence)
  }

  const getMarkerPosition = (sequence: number) => {
    return (sequence / totalSequences) * 100
  }

  return (
    <div className={`bg-gray-800 border-t border-gray-700 px-4 py-2 flex items-center gap-4 ${className}`}>
      {/* Playback Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleReset}
          className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          title="Reset to beginning"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <button
          onClick={handlePrevious}
          disabled={currentSequence <= 1}
          className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Previous sequence"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        {isPlaying ? (
          <button
            onClick={handlePause}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Pause playback"
          >
            <Pause className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handlePlay}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Start playback"
          >
            <Play className="w-4 h-4" />
          </button>
        )}
        <button
          onClick={handleNext}
          disabled={currentSequence >= totalSequences}
          className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Next sequence"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Timeline Slider */}
      <div className="flex-1 relative">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 min-w-[3rem]">
            Seq {currentSequence}
          </span>
          <div className="flex-1 relative h-6">
            {/* Timeline Track */}
            <div className="absolute inset-0 bg-gray-700 rounded-full" />
            
            {/* Version Markers */}
            {versionMarkers.map((marker) => (
              <button
                key={marker.sequence}
                onClick={() => handleMarkerClick(marker.sequence)}
                className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 ${
                  selectedMarker === marker.sequence
                    ? 'bg-blue-500 border-blue-400'
                    : 'bg-gray-600 border-gray-500 hover:bg-gray-500'
                }`}
                style={{ left: `${getMarkerPosition(marker.sequence)}%` }}
                title={marker.label}
              />
            ))}

            {/* Current Position Indicator */}
            <div
              className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-blue-500 rounded-full border-2 border-blue-400 shadow-lg"
              style={{ left: `${getMarkerPosition(currentSequence)}%`, marginLeft: '-8px' }}
            />

            {/* Progress Fill */}
            <div
              className="absolute inset-0 bg-blue-600 rounded-full"
              style={{ width: `${getMarkerPosition(currentSequence)}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 min-w-[3rem] text-right">
            {totalSequences}
          </span>
        </div>

        {/* Timeline Labels */}
        <div className="relative mt-1 h-4">
          {versionMarkers.map((marker) => (
            <div
              key={marker.sequence}
              className="absolute text-xs text-gray-500"
              style={{ left: `${getMarkerPosition(marker.sequence)}%`, transform: 'translateX(-50%)' }}
            >
              {marker.label}
            </div>
          ))}
        </div>
      </div>

      {/* Speed Control */}
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-gray-400" />
        <select
          value={playbackSpeed}
          onChange={(e) => onSpeedChange(Number(e.target.value))}
          className="bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded border border-gray-600"
        >
          <option value={0.5}>0.5x</option>
          <option value={1}>1x</option>
          <option value={2}>2x</option>
          <option value={4}>4x</option>
        </select>
      </div>

      {/* File Path */}
      <div className="text-xs text-gray-500 truncate max-w-[200px]" title={filePath}>
        {filePath}
      </div>
    </div>
  )
}

