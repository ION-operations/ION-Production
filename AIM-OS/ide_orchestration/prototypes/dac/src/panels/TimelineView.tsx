// Timeline View Panel - V2 Refactored with BasePanel
// Bitemporal timeline with real TCS TimelineEntry structure and playback controls

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { useTCS, useCMC } from '../hooks/useAIMOS'
import { Clock, Play, Pause, SkipBack, SkipForward, RotateCcw, GitBranch, Target, Activity, History, RefreshCw, Eye, EyeOff, FileDiff, Save } from 'lucide-react'
import type { TimelineEntry } from '../hooks/useAIMOS'

export const TimelineView: React.FC = () => {
  const { entries } = useTCS()
  const { retrieveAtoms } = useCMC()
  const [timelineEvents, setTimelineEvents] = useState<TimelineEntry[]>([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentIndex, setCurrentIndex] = useState<number>(0)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showChanges, setShowChanges] = useState(true)
  const [showBitemporal, setShowBitemporal] = useState(true)
  const [restoredState, setRestoredState] = useState<TimelineEntry | null>(null)
  const [changeDiff, setChangeDiff] = useState<{ before: any; after: any } | null>(null)
  const playbackIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const stateHistoryRef = useRef<Map<number, any>>(new Map())
  
  // Sync entries from hook to local state
  useEffect(() => {
    try {
      setLoading(true)
      setError(null)
      if (entries.length > 0) {
        setTimelineEvents(entries.slice(-50)) // Get last 50 entries
        if (currentIndex === 0 && entries.length > 0) {
          setCurrentIndex(entries.length - 1)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline')
    } finally {
      setLoading(false)
    }
  }, [entries])
  
  // Calculate changes between events
  const calculateChanges = useCallback((currentEvent: TimelineEntry, previousEvent?: TimelineEntry) => {
    if (!previousEvent) return null
    
    const changes: { field: string; before: any; after: any }[] = []
    
    // Compare context_data
    if (currentEvent.context_data && previousEvent.context_data) {
      Object.keys(currentEvent.context_data).forEach(key => {
        if (JSON.stringify(currentEvent.context_data[key]) !== JSON.stringify(previousEvent.context_data[key])) {
          changes.push({
            field: `context.${key}`,
            before: previousEvent.context_data[key],
            after: currentEvent.context_data[key]
          })
        }
      })
    }
    
    // Compare quality_metrics
    if (currentEvent.quality_metrics && previousEvent.quality_metrics) {
      Object.keys(currentEvent.quality_metrics).forEach(key => {
        const currentVal = currentEvent.quality_metrics[key]
        const previousVal = previousEvent.quality_metrics[key]
        if (currentVal !== previousVal) {
          changes.push({
            field: `quality.${key}`,
            before: previousVal,
            after: currentVal
          })
        }
      })
    }
    
    // Compare tags
    const currentTags = new Set(currentEvent.tags || [])
    const previousTags = new Set(previousEvent.tags || [])
    const addedTags = [...currentTags].filter(t => !previousTags.has(t))
    const removedTags = [...previousTags].filter(t => !currentTags.has(t))
    
    if (addedTags.length > 0 || removedTags.length > 0) {
      changes.push({
        field: 'tags',
        before: [...previousTags],
        after: [...currentTags]
      })
    }
    
    return changes.length > 0 ? changes : null
  }, [])
  
  // Restore state to a specific point in time
  const restoreState = useCallback(async (index: number) => {
    if (index < 0 || index >= timelineEvents.length) return
    
    const targetEvent = timelineEvents[index]
    setRestoredState(targetEvent)
    
    // Load bitemporal history if available
    if (showBitemporal && targetEvent.entry_id) {
      try {
        const atoms = await retrieveAtoms(`timeline_${targetEvent.entry_id}`, 10)
        if (atoms.length > 0) {
          stateHistoryRef.current.set(index, {
            event: targetEvent,
            atoms: atoms,
            restoredAt: new Date().toISOString()
          })
        }
      } catch (err) {
        console.warn('Failed to load bitemporal history:', err)
      }
    }
  }, [timelineEvents, showBitemporal, retrieveAtoms])
  
  // Update change diff when current index changes
  useEffect(() => {
    if (showChanges && currentIndex > 0 && timelineEvents.length > 0) {
      const currentEvent = timelineEvents[currentIndex]
      const previousEvent = timelineEvents[currentIndex - 1]
      const changes = calculateChanges(currentEvent, previousEvent)
      setChangeDiff(changes ? { before: previousEvent, after: currentEvent } : null)
    } else {
      setChangeDiff(null)
    }
  }, [currentIndex, timelineEvents, showChanges, calculateChanges])
  
  useEffect(() => {
    // Playback logic
    if (isPlaying && timelineEvents.length > 0) {
      playbackIntervalRef.current = setInterval(() => {
        setCurrentIndex(prev => {
          if (prev >= timelineEvents.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, 1000 / playbackSpeed)
    } else {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current)
        playbackIntervalRef.current = null
      }
    }
    
    return () => {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current)
      }
    }
  }, [isPlaying, playbackSpeed, timelineEvents.length])
  
  const handlePlay = () => {
    if (currentIndex >= timelineEvents.length - 1) {
      setCurrentIndex(0)
    }
    setIsPlaying(true)
  }
  
  const handlePause = () => {
    setIsPlaying(false)
  }
  
  const handleReset = () => {
    setIsPlaying(false)
    setCurrentIndex(0)
  }
  
  const handleSkipBack = () => {
    setIsPlaying(false)
    setCurrentIndex(prev => Math.max(0, prev - 1))
  }
  
  const handleSkipForward = () => {
    setIsPlaying(false)
    setCurrentIndex(prev => Math.min(timelineEvents.length - 1, prev + 1))
  }
  
  const handleJumpTo = (index: number) => {
    setIsPlaying(false)
    setCurrentIndex(index)
    if (restoredState) {
      restoreState(index)
    }
  }
  
  const handleRestoreState = () => {
    restoreState(currentIndex)
  }
  
  const handleSaveState = () => {
    if (restoredState) {
      const stateData = {
        event: restoredState,
        timestamp: new Date().toISOString(),
        index: currentIndex
      }
      const blob = new Blob([JSON.stringify(stateData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `timeline_state_${restoredState.entry_id}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  }
  
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.85) return 'text-green-400'
    if (confidence >= 0.70) return 'text-yellow-400'
    return 'text-red-400'
  }
  
  const progress = timelineEvents.length > 0 ? ((currentIndex + 1) / timelineEvents.length) * 100 : 0
  
  // Calculate AIM-OS metrics
  const overallConfidence = timelineEvents.length > 0
    ? timelineEvents.reduce((sum, event) => {
        const conf = event.quality_metrics?.overall || 0.75
        return sum + conf
      }, 0) / timelineEvents.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  return (
    <BasePanel
      id="panel-timeline-view"
      title="Bitemporal Timeline"
      icon={Clock}
      description="TCS timeline with playback controls and bitemporal tracking"
      loading={loading}
      error={error}
      empty={!loading && !error && timelineEvents.length === 0}
      emptyMessage="Timeline will populate as events occur"
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            Sequential Ordering (Not Date-Based) | Bitemporal Tracking Active
          </span>
          <span className="text-green-400">TCS Integration Active</span>
        </div>
      }
      headerClassName="p-3"
    >
      {/* Playback Controls */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={handleReset}
            className="p-1.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
            title="Reset to Start"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={handleSkipBack}
            className="p-1.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
            title="Previous Event"
            disabled={currentIndex === 0}
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={isPlaying ? handlePause : handlePlay}
            className="p-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white"
            title={isPlaying ? 'Pause' : 'Play'}
            disabled={timelineEvents.length === 0}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={handleSkipForward}
            className="p-1.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
            title="Next Event"
            disabled={currentIndex >= timelineEvents.length - 1}
          >
            <SkipForward className="w-4 h-4" />
          </button>
          
          {/* Speed Control */}
          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
            className="ml-4 px-2 py-1 rounded bg-gray-700 text-gray-300 text-xs border border-gray-600"
          >
            <option value={0.25}>0.25x</option>
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>
          
          {/* State Restoration */}
          <button
            onClick={handleRestoreState}
            className="px-2 py-1 rounded bg-green-600 hover:bg-green-700 text-white text-xs flex items-center gap-1"
            title="Restore State to Current Event"
          >
            <History className="w-3 h-3" />
            Restore
          </button>
          
          {/* Save State */}
          {restoredState && (
            <button
              onClick={handleSaveState}
              className="px-2 py-1 rounded bg-purple-600 hover:bg-purple-700 text-white text-xs flex items-center gap-1"
              title="Save Current State"
            >
              <Save className="w-3 h-3" />
              Save
            </button>
          )}
          
          {/* Toggles */}
          <button
            onClick={() => setShowChanges(!showChanges)}
            className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
              showChanges
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title="Toggle Change Visualization"
          >
            {showChanges ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            Changes
          </button>
          
          <button
            onClick={() => setShowBitemporal(!showBitemporal)}
            className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
              showBitemporal
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title="Toggle Bitemporal History"
          >
            <History className="w-3 h-3" />
            Bitemporal
          </button>
          
          <span className="ml-auto text-xs text-gray-400">
            {currentIndex + 1} / {timelineEvents.length} events
          </span>
        </div>
        
        {/* Progress Bar */}
        {timelineEvents.length > 0 && (
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
        
        {/* Restored State Indicator */}
        {restoredState && (
          <div className="p-2 rounded bg-green-900/20 border border-green-700 flex items-center gap-2 text-xs text-green-300">
            <RefreshCw className="w-3 h-3" />
            <span>State restored to: {restoredState.title || restoredState.event_type}</span>
            <button
              onClick={() => setRestoredState(null)}
              className="ml-auto text-green-400 hover:text-green-300"
            >
              Clear
            </button>
          </div>
        )}
        
        {/* Change Diff Display */}
        {showChanges && changeDiff && (
          <div className="p-2 rounded bg-blue-900/20 border border-blue-700">
            <div className="flex items-center gap-2 mb-2 text-xs text-blue-300">
              <FileDiff className="w-3 h-3" />
              <span>Changes detected</span>
            </div>
            <div className="space-y-1 text-xs">
              {calculateChanges(changeDiff.after, changeDiff.before)?.map((change, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-gray-400 min-w-[100px]">{change.field}:</span>
                  <div className="flex-1 grid grid-cols-2 gap-2">
                    <div className="text-red-400 line-through">
                      {typeof change.before === 'object' ? JSON.stringify(change.before) : String(change.before)}
                    </div>
                    <div className="text-green-400">
                      {typeof change.after === 'object' ? JSON.stringify(change.after) : String(change.after)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Timeline Events */}
      <div className="flex-1 overflow-auto p-3 space-y-2">
        {timelineEvents.map((event, index) => {
          const isCurrent = index === currentIndex
          const eventConfidence = event.quality_metrics?.overall || 0.75
          
          return (
            <div
              key={event.entry_id}
              onClick={() => handleJumpTo(index)}
              className={`p-3 rounded border cursor-pointer transition-all ${
                isCurrent 
                  ? 'bg-blue-500/10 border-blue-500 shadow-lg shadow-blue-500/20' 
                  : 'bg-gray-800 border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Header Row */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {/* Sequence Number */}
                  <div className={`px-2 py-0.5 rounded text-xs font-mono ${
                    isCurrent ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}>
                    #{index + 1}
                  </div>
                  
                  {/* Event Type Badge */}
                  <span className="px-1.5 py-0.5 rounded text-xs bg-gray-700 text-gray-300 capitalize">
                    {event.event_type.replace(/_/g, ' ')}
                  </span>
                  
                  {/* Entry ID */}
                  <span className="text-xs text-gray-400 font-mono truncate">
                    {event.entry_id.substring(0, 12)}...
                  </span>
                  
                  {/* Chain Integration */}
                  {event.executed_via_chain_id && (
                    <div className="flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-purple-900/30 text-purple-300 border border-purple-700">
                      <GitBranch className="w-3 h-3" />
                      <span className="truncate">{event.executed_via_chain_id.substring(0, 12)}</span>
                    </div>
                  )}
                  
                  {/* Goal Integration */}
                  {event.parent_chain_ids.length > 0 && (
                    <div className="flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-green-900/30 text-green-300 border border-green-700">
                      <Target className="w-3 h-3" />
                      <span>{event.parent_chain_ids.length} parents</span>
                    </div>
                  )}
                </div>
                
                {/* Confidence */}
                <div className="flex items-center gap-3 flex-shrink-0">
                  <div className="text-xs">
                    <span className="text-gray-500">Conf:</span>
                    <span className={`ml-1 ${getConfidenceColor(eventConfidence)}`}>
                      {(eventConfidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Title */}
              <div className="text-sm font-semibold text-gray-200 mb-1">
                {event.title}
              </div>
              
              {/* Description */}
              <div className="text-sm text-gray-300 mb-2">
                {event.description}
              </div>
              
              {/* Quality Metrics */}
              {Object.keys(event.quality_metrics).length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2">
                  {Object.entries(event.quality_metrics).map(([key, value]) => (
                    <div key={key} className="text-xs">
                      <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                      <span className={`ml-1 ${getConfidenceColor(value as number)}`}>
                        {((value as number) * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Tags */}
              {event.tags.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-1">
                  {event.tags.slice(0, 5).map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-1.5 py-0.5 rounded text-xs bg-gray-700 text-gray-400"
                    >
                      {tag}
                    </span>
                  ))}
                  {event.tags.length > 5 && (
                    <span className="text-xs text-gray-500">
                      +{event.tags.length - 5} more
                    </span>
                  )}
                </div>
              )}
              
              {/* Chain Evolution Path */}
              {event.evolution_path.length > 0 && (
                <div className="mb-2 pt-2 border-t border-gray-700">
                  <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                    <Activity className="w-3 h-3" />
                    <span>Evolution Path:</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {event.evolution_path.slice(0, 5).map((pathId, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded text-xs bg-gray-700 text-gray-400 font-mono"
                      >
                        {pathId.substring(0, 8)}...
                      </span>
                    ))}
                    {event.evolution_path.length > 5 && (
                      <span className="text-xs text-gray-500">
                        +{event.evolution_path.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}
              
              {/* Bitemporal History */}
              {showBitemporal && stateHistoryRef.current.has(index) && (
                <div className="mb-2 pt-2 border-t border-gray-700">
                  <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                    <History className="w-3 h-3" />
                    <span>Bitemporal History:</span>
                  </div>
                  <div className="text-xs text-gray-400 space-y-1">
                    {stateHistoryRef.current.get(index)?.atoms?.slice(0, 3).map((atom: any, idx: number) => (
                      <div key={idx} className="pl-4 border-l-2 border-gray-700">
                        <div className="text-gray-300">
                          Valid: {new Date(atom.valid_from).toLocaleString()}
                          {atom.valid_to && ` → ${new Date(atom.valid_to).toLocaleString()}`}
                        </div>
                        <div className="text-gray-500 truncate">
                          {atom.content?.inline?.substring(0, 100)}...
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Change Indicators */}
              {showChanges && index > 0 && calculateChanges(event, timelineEvents[index - 1]) && (
                <div className="mb-2 pt-2 border-t border-gray-700">
                  <div className="flex items-center gap-1 text-xs text-green-400 mb-1">
                    <FileDiff className="w-3 h-3" />
                    <span>Modified from previous event</span>
                  </div>
                </div>
              )}
              
              {/* Footer */}
              <div className="flex items-center justify-between text-xs text-gray-500 mt-2 pt-2 border-t border-gray-700">
                <span>{new Date(event.timestamp).toLocaleString()}</span>
                <span className="text-gray-600">
                  {event.parent_chain_ids.length > 0 && `${event.parent_chain_ids.length} parents`}
                  {event.parent_chain_ids.length > 0 && event.child_chain_ids.length > 0 && ' • '}
                  {event.child_chain_ids.length > 0 && `${event.child_chain_ids.length} children`}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </BasePanel>
  )
}
