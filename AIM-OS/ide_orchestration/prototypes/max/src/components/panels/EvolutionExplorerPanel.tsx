// Evolution Explorer Panel - Max V2
// Bidirectional Timeline ↔ Chain ↔ Goals Visualization
// Shows how timeline events connect to chains and goals

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { GitBranch, Clock, ArrowRight, ArrowLeft, Play, Pause, RotateCcw, SkipForward, SkipBack, Target } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { PanelLoading } from '../Loading/Loading';
import './EvolutionExplorerPanel.css';

export interface TimelineEntry {
  id: string;
  sequence: number;
  type: 'execution' | 'error' | 'test' | 'modification' | 'focus' | 'drift';
  content: string;
  timestamp: string;
  agentId?: string;
  confidence: number;
  evidence: string[];
  chainId?: string;
  goalId?: string;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
}

export interface ChainEntry {
  id: string;
  name: string;
  type: 'epic' | 'phase' | 'workstream' | 'task';
  status: 'planned' | 'in_progress' | 'completed' | 'blocked';
  progress: number;
  timelineEntryIds: string[];
  goalId?: string;
  confidence: number;
}

export interface GoalEntry {
  id: string;
  name: string;
  description: string;
  status: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled';
  progress: number;
  targetSequence: number;
  currentSequence: number;
  timelineEntryIds: string[];
  chainIds: string[];
  confidence: number;
}

export type ViewMode = 'timeline' | 'chain' | 'goals' | 'both';

export const EvolutionExplorerPanel: React.FC = () => {
  const { tcs, apoe, loading, errors } = useAIMOS();
  const [viewMode, setViewMode] = useState<ViewMode>('both');
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [currentIndex, setCurrentIndex] = useState(0);
  const playbackIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Mock timeline entries (will be replaced with real TCS data)
  const timelineEntries: TimelineEntry[] = useMemo(() => [
    {
      id: 'entry_1',
      sequence: 1,
      type: 'execution',
      content: 'Created Layout component',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      agentId: 'max',
      confidence: 0.95,
      evidence: ['atom_123'],
      chainId: 'chain_1',
      goalId: 'goal_1',
      bitemporal: { valid_from: new Date(Date.now() - 3600000).toISOString(), valid_to: null },
    },
    {
      id: 'entry_2',
      sequence: 2,
      type: 'modification',
      content: 'Added Panel System',
      timestamp: new Date(Date.now() - 3300000).toISOString(),
      agentId: 'max',
      confidence: 0.92,
      evidence: ['atom_456'],
      chainId: 'chain_1',
      goalId: 'goal_1',
      bitemporal: { valid_from: new Date(Date.now() - 3300000).toISOString(), valid_to: null },
    },
    {
      id: 'entry_3',
      sequence: 3,
      type: 'execution',
      content: 'Integrated useAIMOS hook',
      timestamp: new Date(Date.now() - 3000000).toISOString(),
      agentId: 'max',
      confidence: 0.94,
      evidence: ['atom_789'],
      chainId: 'chain_2',
      goalId: 'goal_1',
      bitemporal: { valid_from: new Date(Date.now() - 3000000).toISOString(), valid_to: null },
    },
    {
      id: 'entry_4',
      sequence: 4,
      type: 'execution',
      content: 'Implemented Debug Console',
      timestamp: new Date(Date.now() - 2700000).toISOString(),
      agentId: 'max',
      confidence: 0.90,
      evidence: ['atom_101'],
      chainId: 'chain_2',
      goalId: 'goal_1',
      bitemporal: { valid_from: new Date(Date.now() - 2700000).toISOString(), valid_to: null },
    },
    {
      id: 'entry_5',
      sequence: 5,
      type: 'execution',
      content: 'Implemented Context Web',
      timestamp: new Date(Date.now() - 2400000).toISOString(),
      agentId: 'max',
      confidence: 0.90,
      evidence: ['atom_202'],
      chainId: 'chain_2',
      goalId: 'goal_1',
      bitemporal: { valid_from: new Date(Date.now() - 2400000).toISOString(), valid_to: null },
    },
  ], []);

  // Mock chain entries (will be replaced with real APOE data)
  const chainEntries: ChainEntry[] = useMemo(() => [
    {
      id: 'chain_1',
      name: 'UI Development',
      type: 'phase',
      status: 'completed',
      progress: 1.0,
      timelineEntryIds: ['entry_1', 'entry_2'],
      goalId: 'goal_1',
      confidence: 0.95,
    },
    {
      id: 'chain_2',
      name: 'AIM-OS Integration',
      type: 'phase',
      status: 'in_progress',
      progress: 0.67,
      timelineEntryIds: ['entry_3', 'entry_4', 'entry_5'],
      goalId: 'goal_1',
      confidence: 0.92,
    },
  ], []);

  // Mock goal entries (will be replaced with real Goal Timeline data)
  const goalEntries: GoalEntry[] = useMemo(() => [
    {
      id: 'goal_1',
      name: 'Complete IDE Prototype',
      description: 'Build production-ready IDE prototype with AIM-OS integration',
      status: 'in_progress',
      progress: 0.65,
      targetSequence: 10,
      currentSequence: 5,
      timelineEntryIds: ['entry_1', 'entry_2', 'entry_3', 'entry_4', 'entry_5'],
      chainIds: ['chain_1', 'chain_2'],
      confidence: 0.92,
    },
  ], []);

  // Playback control
  useEffect(() => {
    if (isPlaying && timelineEntries.length > 0) {
      playbackIntervalRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= timelineEntries.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1000 / playbackSpeed);
    } else {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
        playbackIntervalRef.current = null;
      }
    }

    return () => {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, timelineEntries.length]);

  const displayedEntries = useMemo(() => {
    return timelineEntries.slice(0, currentIndex + 1);
  }, [timelineEntries, currentIndex]);

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentIndex(0);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, timelineEntries.length - 1));
  };

  const handlePrevious = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const getEntryTypeColor = (type: string) => {
    switch (type) {
      case 'execution':
        return '#4ade80'; // green
      case 'error':
        return '#f87171'; // red
      case 'test':
        return '#60a5fa'; // blue
      case 'modification':
        return '#fbbf24'; // yellow
      case 'focus':
        return '#a78bfa'; // purple
      case 'drift':
        return '#fb7185'; // pink
      default:
        return '#858585'; // gray
    }
  };

  const getEntryTypeIcon = (type: string) => {
    switch (type) {
      case 'execution':
        return '▶️';
      case 'error':
        return '❌';
      case 'test':
        return '✅';
      case 'modification':
        return '✏️';
      case 'focus':
        return '🎯';
      case 'drift':
        return '⚠️';
      default:
        return '🔷';
    }
  };

  if (loading.tcs || loading.apoe) {
    return <PanelLoading message="Loading Evolution Explorer..." />;
  }

  if (errors.tcs || errors.apoe) {
    return (
      <div className="evolution-explorer-error" role="alert">
        <p>Error loading Evolution Explorer: {errors.tcs?.message || errors.apoe?.message}</p>
      </div>
    );
  }

  return (
    <div className="evolution-explorer" role="region" aria-label="Evolution Explorer">
      {/* Header */}
      <div className="evolution-explorer-header">
        <div className="evolution-explorer-header-top">
          <div className="evolution-explorer-title">
            <GitBranch className="evolution-explorer-icon" />
            <div>
              <h3 className="evolution-explorer-title-text">Evolution Explorer</h3>
              <p className="evolution-explorer-subtitle">
                Bidirectional Graph • Timeline ↔ Chain ↔ Goals • TCS + APOE Powered
              </p>
            </div>
          </div>
        </div>

        {/* View Mode Selector */}
        <div className="view-mode-selector">
          {(['timeline', 'both', 'chain', 'goals'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`view-mode-button ${viewMode === mode ? 'view-mode-button-active' : ''}`}
              aria-pressed={viewMode === mode}
              aria-label={`View mode: ${mode}`}
            >
              {mode === 'timeline' && <Clock className="view-mode-icon" />}
              {mode === 'chain' && <GitBranch className="view-mode-icon" />}
              {mode === 'goals' && <Target className="view-mode-icon" />}
              {mode === 'both' && <ArrowRight className="view-mode-icon" />}
              <span>{mode}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Playback Controls */}
      <div className="playback-controls">
        <div className="playback-controls-top">
          <div className="playback-buttons">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="playback-button"
              aria-label="Previous entry"
            >
              <SkipBack className="playback-icon" />
            </button>
            {isPlaying ? (
              <button
                onClick={handlePause}
                className="playback-button playback-button-pause"
                aria-label="Pause playback"
              >
                <Pause className="playback-icon" />
              </button>
            ) : (
              <button
                onClick={handlePlay}
                disabled={currentIndex >= timelineEntries.length - 1}
                className="playback-button playback-button-play"
                aria-label="Play playback"
              >
                <Play className="playback-icon" />
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={currentIndex >= timelineEntries.length - 1}
              className="playback-button"
              aria-label="Next entry"
            >
              <SkipForward className="playback-icon" />
            </button>
            <button
              onClick={handleReset}
              className="playback-button"
              aria-label="Reset playback"
            >
              <RotateCcw className="playback-icon" />
            </button>
          </div>
          <div className="playback-speed">
            <label htmlFor="playback-speed-select" className="playback-speed-label">
              Speed:
            </label>
            <select
              id="playback-speed-select"
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              className="playback-speed-select"
              aria-label="Playback speed"
            >
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={4}>4x</option>
            </select>
          </div>
        </div>
        {/* Timeline Slider */}
        <div className="timeline-slider-container">
          <span className="timeline-slider-label">
            {currentIndex + 1}/{timelineEntries.length}
          </span>
          <input
            type="range"
            min={0}
            max={Math.max(0, timelineEntries.length - 1)}
            value={currentIndex}
            onChange={(e) => setCurrentIndex(Number(e.target.value))}
            className="timeline-slider"
            aria-label="Timeline position"
            aria-valuemin={0}
            aria-valuemax={timelineEntries.length - 1}
            aria-valuenow={currentIndex}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="evolution-explorer-content">
        {viewMode === 'both' && (
          <div className="evolution-explorer-grid">
            {/* Timeline Column */}
            <div className="evolution-column timeline-column">
              <div className="column-header">
                <Clock className="column-icon" />
                <h4 className="column-title">Timeline ({displayedEntries.length})</h4>
              </div>
              <div className="column-content">
                {displayedEntries.map((entry, index) => (
                  <div
                    key={entry.id}
                    onClick={() => setSelectedEntry(selectedEntry === entry.id ? null : entry.id)}
                    className={`entry-card ${selectedEntry === entry.id ? 'entry-card-selected' : ''} ${index === currentIndex ? 'entry-card-current' : ''}`}
                    role="button"
                    tabIndex={0}
                    aria-label={`Timeline entry ${entry.sequence}: ${entry.content}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedEntry(selectedEntry === entry.id ? null : entry.id);
                      }
                    }}
                  >
                    <div className="entry-header">
                      <span className="entry-type-icon" style={{ color: getEntryTypeColor(entry.type) }}>
                        {getEntryTypeIcon(entry.type)}
                      </span>
                      <span className="entry-sequence">[{entry.sequence}]</span>
                      <span className="entry-type">{entry.type}</span>
                    </div>
                    <div className="entry-content">{entry.content}</div>
                    <div className="entry-meta">
                      <span>{entry.agentId || 'System'}</span>
                      <span>•</span>
                      <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                      <span>•</span>
                      <span className="entry-confidence">Conf: {(entry.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Connection Arrow */}
            <div className="connection-arrow">
              <ArrowRight className="connection-arrow-icon" />
            </div>

            {/* Chain/Goals Column */}
            <div className="evolution-column chain-goals-column">
              <div className="column-header">
                <GitBranch className="column-icon" />
                <h4 className="column-title">Chains ({chainEntries.length})</h4>
              </div>
              <div className="column-content">
                {chainEntries.map((chain) => (
                  <div
                    key={chain.id}
                    onClick={() => setSelectedEntry(selectedEntry === chain.id ? null : chain.id)}
                    className={`chain-card ${selectedEntry === chain.id ? 'entry-card-selected' : ''}`}
                    role="button"
                    tabIndex={0}
                    aria-label={`Chain: ${chain.name}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedEntry(selectedEntry === chain.id ? null : chain.id);
                      }
                    }}
                  >
                    <div className="chain-header">
                      <span className="chain-name">{chain.name}</span>
                      <span className={`chain-status chain-status-${chain.status}`}>
                        {chain.status}
                      </span>
                    </div>
                    <div className="chain-progress">
                      <div className="chain-progress-bar">
                        <div
                          className="chain-progress-fill"
                          style={{ width: `${chain.progress * 100}%` }}
                          role="progressbar"
                          aria-valuenow={chain.progress * 100}
                          aria-valuemin={0}
                          aria-valuemax={100}
                        />
                      </div>
                      <span className="chain-progress-text">{(chain.progress * 100).toFixed(0)}%</span>
                    </div>
                    <div className="chain-meta">
                      <span>{chain.type}</span>
                      <span>•</span>
                      <span>{chain.timelineEntryIds.length} entries</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="column-header" style={{ marginTop: '16px' }}>
                <Target className="column-icon" />
                <h4 className="column-title">Goals ({goalEntries.length})</h4>
              </div>
              <div className="column-content">
                {goalEntries.map((goal) => (
                  <div
                    key={goal.id}
                    onClick={() => setSelectedEntry(selectedEntry === goal.id ? null : goal.id)}
                    className={`goal-card ${selectedEntry === goal.id ? 'entry-card-selected' : ''}`}
                    role="button"
                    tabIndex={0}
                    aria-label={`Goal: ${goal.name}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedEntry(selectedEntry === goal.id ? null : goal.id);
                      }
                    }}
                  >
                    <div className="goal-header">
                      <span className="goal-name">{goal.name}</span>
                      <span className={`goal-status goal-status-${goal.status}`}>
                        {goal.status}
                      </span>
                    </div>
                    <div className="goal-description">{goal.description}</div>
                    <div className="goal-progress">
                      <div className="goal-progress-bar">
                        <div
                          className="goal-progress-fill"
                          style={{ width: `${goal.progress * 100}%` }}
                          role="progressbar"
                          aria-valuenow={goal.progress * 100}
                          aria-valuemin={0}
                          aria-valuemax={100}
                        />
                      </div>
                      <span className="goal-progress-text">{(goal.progress * 100).toFixed(0)}%</span>
                    </div>
                    <div className="goal-meta">
                      <span>Sequence: {goal.currentSequence}/{goal.targetSequence}</span>
                      <span>•</span>
                      <span>{goal.timelineEntryIds.length} entries</span>
                      <span>•</span>
                      <span>{goal.chainIds.length} chains</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {viewMode === 'timeline' && (
          <div className="timeline-view">
            <div className="column-header">
              <Clock className="column-icon" />
              <h4 className="column-title">Timeline ({displayedEntries.length})</h4>
            </div>
            <div className="timeline-list">
              {displayedEntries.map((entry, index) => (
                <div
                  key={entry.id}
                  className={`entry-card ${index === currentIndex ? 'entry-card-current' : ''}`}
                >
                  <div className="entry-header">
                    <span className="entry-type-icon" style={{ color: getEntryTypeColor(entry.type) }}>
                      {getEntryTypeIcon(entry.type)}
                    </span>
                    <span className="entry-sequence">[{entry.sequence}]</span>
                    <span className="entry-type">{entry.type}</span>
                  </div>
                  <div className="entry-content">{entry.content}</div>
                  <div className="entry-meta">
                    <span>{entry.agentId || 'System'}</span>
                    <span>•</span>
                    <span>{new Date(entry.timestamp).toLocaleString()}</span>
                    <span>•</span>
                    <span className="entry-confidence">Conf: {(entry.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'chain' && (
          <div className="chain-view">
            <div className="column-header">
              <GitBranch className="column-icon" />
              <h4 className="column-title">Chains ({chainEntries.length})</h4>
            </div>
            <div className="chain-list">
              {chainEntries.map((chain) => (
                <div key={chain.id} className="chain-card">
                  <div className="chain-header">
                    <span className="chain-name">{chain.name}</span>
                    <span className={`chain-status chain-status-${chain.status}`}>
                      {chain.status}
                    </span>
                  </div>
                  <div className="chain-progress">
                    <div className="chain-progress-bar">
                      <div
                        className="chain-progress-fill"
                        style={{ width: `${chain.progress * 100}%` }}
                        role="progressbar"
                        aria-valuenow={chain.progress * 100}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      />
                    </div>
                    <span className="chain-progress-text">{(chain.progress * 100).toFixed(0)}%</span>
                  </div>
                  <div className="chain-meta">
                    <span>{chain.type}</span>
                    <span>•</span>
                    <span>{chain.timelineEntryIds.length} timeline entries</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'goals' && (
          <div className="goals-view">
            <div className="column-header">
              <Target className="column-icon" />
              <h4 className="column-title">Goals ({goalEntries.length})</h4>
            </div>
            <div className="goals-list">
              {goalEntries.map((goal) => (
                <div key={goal.id} className="goal-card">
                  <div className="goal-header">
                    <span className="goal-name">{goal.name}</span>
                    <span className={`goal-status goal-status-${goal.status}`}>
                      {goal.status}
                    </span>
                  </div>
                  <div className="goal-description">{goal.description}</div>
                  <div className="goal-progress">
                    <div className="goal-progress-bar">
                      <div
                        className="goal-progress-fill"
                        style={{ width: `${goal.progress * 100}%` }}
                        role="progressbar"
                        aria-valuenow={goal.progress * 100}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      />
                    </div>
                    <span className="goal-progress-text">{(goal.progress * 100).toFixed(0)}%</span>
                  </div>
                  <div className="goal-meta">
                    <span>Sequence: {goal.currentSequence}/{goal.targetSequence}</span>
                    <span>•</span>
                    <span>{goal.timelineEntryIds.length} timeline entries</span>
                    <span>•</span>
                    <span>{goal.chainIds.length} chains</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

