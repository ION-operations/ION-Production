// Evolution Explorer Panel (Timeline ↔ Chain ↔ Goals Bidirectional) - Enhanced with Playback Controls
import React, { useState, useEffect, useRef } from 'react'
import { GitBranch, Clock, ArrowRight, ArrowLeft, Play, Pause, RotateCcw, SkipForward, SkipBack } from 'lucide-react'
import { Panel } from '@/types'
import { useAIMOS } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface EvolutionExplorerProps {
  panel: Panel
}

export const EvolutionExplorer: React.FC<EvolutionExplorerProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { tcs, apoe, isLoading, error, isConnected } = useAIMOS()
  const [viewMode, setViewMode] = useState<'timeline' | 'chain' | 'both' | 'goals'>('both')
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [currentIndex, setCurrentIndex] = useState(0)
  const playbackIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const handleTogglePanel = (e: CustomEvent) => {
      if (e.detail.panelId === panel.id) {
        togglePanelVisibility(panel.id)
      }
    }
    window.addEventListener('togglePanel', handleTogglePanel as EventListener)
    return () => {
      window.removeEventListener('togglePanel', handleTogglePanel as EventListener)
    }
  }, [panel.id, togglePanelVisibility])

  // Playback control
  useEffect(() => {
    if (isPlaying && tcs.entries.length > 0) {
      playbackIntervalRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= tcs.entries.length - 1) {
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
  }, [isPlaying, playbackSpeed, tcs.entries.length])

  const handlePlay = () => {
    setIsPlaying(true)
  }

  const handlePause = () => {
    setIsPlaying(false)
  }

  const handleReset = () => {
    setIsPlaying(false)
    setCurrentIndex(0)
  }

  const handleNext = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, tcs.entries.length - 1))
  }

  const handlePrevious = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0))
  }

  const displayedEntries = tcs.entries.slice(0, currentIndex + 1)
  const goals = apoe.plans

  const headerActions = (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {isConnected && (
        <span style={{ fontSize: '10px', color: '#10B981', backgroundColor: '#374151', padding: '2px 6px', borderRadius: '4px' }}>
          AIM-OS
        </span>
      )}
      <div style={{ display: 'flex', gap: '4px' }}>
        {(['timeline', 'both', 'chain', 'goals'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            style={{
              padding: '4px 8px',
              fontSize: '11px',
              backgroundColor: viewMode === mode ? '#374151' : 'transparent',
              border: '1px solid #374151',
              borderRadius: '4px',
              color: '#F9FAFB',
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {mode}
          </button>
        ))}
      </div>
    </div>
  )

  return (
    <BasePanel panel={panel} headerActions={headerActions} isLoading={isLoading} error={error || null}>
      {/* Playback Controls */}
      <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#111827', borderRadius: '4px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              style={{
                padding: '6px',
                backgroundColor: '#374151',
                border: 'none',
                borderRadius: '4px',
                color: '#F9FAFB',
                cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
                opacity: currentIndex === 0 ? 0.5 : 1,
              }}
            >
              <SkipBack size={14} />
            </button>
            {isPlaying ? (
              <button
                onClick={handlePause}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#3B82F6',
                  border: 'none',
                  borderRadius: '4px',
                  color: '#F9FAFB',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Pause size={14} />
              </button>
            ) : (
              <button
                onClick={handlePlay}
                disabled={currentIndex >= tcs.entries.length - 1}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#10B981',
                  border: 'none',
                  borderRadius: '4px',
                  color: '#F9FAFB',
                  cursor: currentIndex >= tcs.entries.length - 1 ? 'not-allowed' : 'pointer',
                  opacity: currentIndex >= tcs.entries.length - 1 ? 0.5 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Play size={14} />
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={currentIndex >= tcs.entries.length - 1}
              style={{
                padding: '6px',
                backgroundColor: '#374151',
                border: 'none',
                borderRadius: '4px',
                color: '#F9FAFB',
                cursor: currentIndex >= tcs.entries.length - 1 ? 'not-allowed' : 'pointer',
                opacity: currentIndex >= tcs.entries.length - 1 ? 0.5 : 1,
              }}
            >
              <SkipForward size={14} />
            </button>
            <button
              onClick={handleReset}
              style={{
                padding: '6px',
                backgroundColor: '#374151',
                border: 'none',
                borderRadius: '4px',
                color: '#F9FAFB',
                cursor: 'pointer',
              }}
            >
              <RotateCcw size={14} />
            </button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '11px', color: '#9CA3AF' }}>Speed:</span>
            <select
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              style={{
                padding: '4px 8px',
                backgroundColor: '#374151',
                border: '1px solid #4B5563',
                borderRadius: '4px',
                color: '#F9FAFB',
                fontSize: '11px',
              }}
            >
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={4}>4x</option>
            </select>
          </div>
        </div>
        {/* Timeline Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '10px', color: '#9CA3AF', minWidth: '40px' }}>
            {currentIndex + 1}/{tcs.entries.length}
          </span>
          <input
            type="range"
            min={0}
            max={Math.max(0, tcs.entries.length - 1)}
            value={currentIndex}
            onChange={(e) => setCurrentIndex(Number(e.target.value))}
            style={{
              flex: 1,
              height: '4px',
              backgroundColor: '#374151',
              borderRadius: '2px',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {viewMode === 'both' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '12px', overflow: 'auto' }}>
          {/* Timeline Column */}
          <div>
            <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={14} />
              Timeline ({displayedEntries.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '400px', overflow: 'auto' }}>
              {displayedEntries.map((entry, index) => (
                <div
                  key={entry.id}
                  onClick={() => setSelectedEntry(entry.id)}
                  style={{
                    padding: '8px',
                    backgroundColor: selectedEntry === entry.id ? '#374151' : index === currentIndex ? '#1F2937' : '#111827',
                    border: index === currentIndex ? '2px solid #3B82F6' : '1px solid #374151',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: '11px', color: '#D1D5DB', marginBottom: '4px' }}>
                    {entry.content || entry.type}
                  </div>
                  <div style={{ fontSize: '10px', color: '#9CA3AF' }}>
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Connection Arrow */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7280' }}>
            <ArrowRight size={20} />
          </div>

          {/* Chain/Goals Column */}
          <div>
            <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <GitBranch size={14} />
              {viewMode === 'goals' ? 'Goals' : 'Chain'} ({goals.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '400px', overflow: 'auto' }}>
              {goals.map((plan) => (
                <div
                  key={plan.id}
                  onClick={() => setSelectedEntry(plan.id)}
                  style={{
                    padding: '8px',
                    backgroundColor: selectedEntry === plan.id ? '#374151' : '#111827',
                    border: '1px solid #374151',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: '11px', color: '#D1D5DB', marginBottom: '4px' }}>{plan.goal}</div>
                  <div style={{ fontSize: '10px', color: '#9CA3AF' }}>Status: {plan.status}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {viewMode === 'timeline' && (
        <div style={{ flex: 1, overflow: 'auto', padding: '12px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {displayedEntries.map((entry, index) => (
              <div
                key={entry.id}
                style={{
                  padding: '10px',
                  backgroundColor: index === currentIndex ? '#1F2937' : '#111827',
                  border: index === currentIndex ? '2px solid #3B82F6' : '1px solid #374151',
                  borderRadius: '4px',
                }}
              >
                <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '4px' }}>
                  {entry.content || entry.type}
                </div>
                <div style={{ fontSize: '11px', color: '#9CA3AF' }}>
                  {entry.type} • {entry.agentId || 'System'} • {new Date(entry.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'chain' && (
        <div style={{ flex: 1, overflow: 'auto', padding: '12px' }}>
          <div style={{ fontSize: '12px', color: '#9CA3AF', fontStyle: 'italic', textAlign: 'center', padding: '20px' }}>
            Chain visualization shows relationships between timeline entries. Use playback controls to explore evolution.
          </div>
        </div>
      )}

      {viewMode === 'goals' && (
        <div style={{ flex: 1, overflow: 'auto', padding: '12px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {goals.map((plan) => (
              <div
                key={plan.id}
                style={{
                  padding: '12px',
                  backgroundColor: '#111827',
                  border: '1px solid #374151',
                  borderRadius: '4px',
                }}
              >
                <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#F9FAFB', marginBottom: '8px' }}>
                  {plan.goal}
                </div>
                <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '4px' }}>Status: {plan.status}</div>
                <div style={{ fontSize: '11px', color: '#9CA3AF' }}>Tasks: {plan.tasks?.length || 0}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </BasePanel>
  )
}

