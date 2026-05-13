/**
 * Timeline Pane Component
 * 
 * Displays event tracking, timeline visualization, and analytics
 * for the Lucid Orchestrator. Consumes data from the TimelinePaneService.
 */

import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  Clock, 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  RotateCcw,
  Download,
  Filter,
  Search,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Activity,
  Calendar,
  Zap,
  AlertCircle,
  CheckCircle,
  Info,
  Eye,
  EyeOff
} from 'lucide-react';
import { TimelinePaneData, Event, TimelineEvent, ActivityData, QualityData, PerformanceData } from '../../../lucid_orchestrator/data_models/core_interfaces';

interface TimelinePaneProps {
  data: TimelinePaneData;
  onEventSelect?: (event: Event) => void;
  onRefresh?: () => void;
  className?: string;
}

export const TimelinePane: React.FC<TimelinePaneProps> = ({ 
  data, 
  onEventSelect, 
  onRefresh,
  className = '' 
}) => {
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterTimeRange, setFilterTimeRange] = useState<string>('all');
  const [showAnalytics, setShowAnalytics] = useState(true);
  const [selectedChart, setSelectedChart] = useState<'activity' | 'quality' | 'performance'>('activity');
  
  const timelineRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();

  // Get all events
  const allEvents = useMemo(() => {
    return [
      ...data.events.documentation,
      ...data.events.code,
      ...data.events.spec,
      ...data.events.system
    ].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }, [data.events]);

  // Filter events
  const filteredEvents = useMemo(() => {
    let filtered = allEvents;

    if (searchTerm) {
      filtered = filtered.filter(event => 
        event.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.data.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.context.user.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(event => event.type.startsWith(filterType));
    }

    if (filterTimeRange !== 'all') {
      const now = new Date();
      const timeRanges = {
        '1hour': 60 * 60 * 1000,
        '1day': 24 * 60 * 60 * 1000,
        '1week': 7 * 24 * 60 * 60 * 1000,
        '1month': 30 * 24 * 60 * 60 * 1000
      };
      
      if (timeRanges[filterTimeRange as keyof typeof timeRanges]) {
        const cutoff = new Date(now.getTime() - timeRanges[filterTimeRange as keyof typeof timeRanges]);
        filtered = filtered.filter(event => new Date(event.timestamp) >= cutoff);
      }
    }

    return filtered;
  }, [allEvents, searchTerm, filterType, filterTimeRange]);

  // Get event type icon
  const getEventTypeIcon = (type: string) => {
    if (type.startsWith('documentation_')) return <Clock className="w-4 h-4 text-blue-500" />;
    if (type.startsWith('code_') || type.startsWith('test_')) return <Activity className="w-4 h-4 text-green-500" />;
    if (type.startsWith('spec_') || type.startsWith('violation_')) return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    if (type.startsWith('system_') || type === 'deployment' || type === 'rollback') return <Zap className="w-4 h-4 text-purple-500" />;
    return <Info className="w-4 h-4 text-gray-500" />;
  };

  // Get event result icon
  const getEventResultIcon = (result: string) => {
    switch (result) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failure':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'partial':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  // Get event type color
  const getEventTypeColor = (type: string) => {
    if (type.startsWith('documentation_')) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (type.startsWith('code_') || type.startsWith('test_')) return 'bg-green-100 text-green-800 border-green-200';
    if (type.startsWith('spec_') || type.startsWith('violation_')) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (type.startsWith('system_') || type === 'deployment' || type === 'rollback') return 'bg-purple-100 text-purple-800 border-purple-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  // Handle event selection
  const handleEventSelect = (event: Event) => {
    setSelectedEvent(event);
    onEventSelect?.(event);
  };

  // Playback controls
  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackSpeed(speed);
  };

  // Animation loop
  useEffect(() => {
    if (isPlaying) {
      const animate = () => {
        setCurrentTime(prev => {
          const next = prev + (playbackSpeed * 0.1);
          if (next >= filteredEvents.length) {
            setIsPlaying(false);
            return filteredEvents.length;
          }
          return next;
        });
        animationRef.current = requestAnimationFrame(animate);
      };
      animationRef.current = requestAnimationFrame(animate);
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, filteredEvents.length]);

  // Get visible events based on current time
  const visibleEvents = useMemo(() => {
    const endIndex = Math.floor(currentTime);
    return filteredEvents.slice(0, endIndex + 1);
  }, [filteredEvents, currentTime]);

  // Format time
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  // Get relative time
  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const eventTime = new Date(timestamp);
    const diffMs = now.getTime() - eventTime.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div className={`h-full flex flex-col bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Timeline Pane</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={onRefresh}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Refresh"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Export"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Playback Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleReset}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Reset"
            >
              <SkipBack className="w-4 h-4" />
            </button>
            
            <button
              onClick={isPlaying ? handlePause : handlePlay}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            
            <button
              onClick={() => setCurrentTime(filteredEvents.length)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Skip to End"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          {/* Speed Control */}
          <select
            value={playbackSpeed}
            onChange={(e) => handleSpeedChange(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>

          {/* Progress Bar */}
          <div className="flex-1 mx-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-100"
                style={{ width: `${(currentTime / filteredEvents.length) * 100}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {Math.floor(currentTime)} / {filteredEvents.length} events
            </div>
          </div>

          {/* Search and Filters */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="documentation">Documentation</option>
            <option value="code">Code</option>
            <option value="spec">Specifications</option>
            <option value="system">System</option>
          </select>

          <select
            value={filterTimeRange}
            onChange={(e) => setFilterTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Time</option>
            <option value="1hour">Last Hour</option>
            <option value="1day">Last Day</option>
            <option value="1week">Last Week</option>
            <option value="1month">Last Month</option>
          </select>

          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className={`p-2 rounded-md transition-colors ${
              showAnalytics 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
            }`}
            title="Toggle Analytics"
          >
            {showAnalytics ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Timeline */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <div className="space-y-2">
              {visibleEvents.map((event, index) => (
                <div
                  key={event.id}
                  onClick={() => handleEventSelect(event)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                    selectedEvent?.id === event.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      {getEventTypeIcon(event.type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {event.data.action}
                        </h4>
                        <div className="flex items-center space-x-2">
                          {getEventResultIcon(event.data.result)}
                          <span className="text-xs text-gray-500">
                            {getRelativeTime(event.timestamp)}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs rounded-full border ${getEventTypeColor(event.type)}`}>
                          {event.type.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-500">
                          {event.context.user} • {event.context.environment}
                        </span>
                      </div>
                      
                      {event.data.details && (
                        <div className="text-xs text-gray-600">
                          {Object.entries(event.data.details).slice(0, 2).map(([key, value]) => (
                            <span key={key} className="mr-4">
                              <span className="font-medium">{key}:</span> {String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Analytics Sidebar */}
        {showAnalytics && (
          <div className="w-96 border-l border-gray-200 bg-white overflow-y-auto">
            <div className="p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Analytics</h4>
              
              {/* Chart Selection */}
              <div className="flex space-x-2 mb-4">
                <button
                  onClick={() => setSelectedChart('activity')}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    selectedChart === 'activity'
                      ? 'bg-blue-100 text-blue-800'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Activity
                </button>
                <button
                  onClick={() => setSelectedChart('quality')}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    selectedChart === 'quality'
                      ? 'bg-blue-100 text-blue-800'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Quality
                </button>
                <button
                  onClick={() => setSelectedChart('performance')}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    selectedChart === 'performance'
                      ? 'bg-blue-100 text-blue-800'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Performance
                </button>
              </div>

              {/* Activity Chart */}
              {selectedChart === 'activity' && (
                <div className="space-y-4">
                  <h5 className="text-sm font-semibold text-gray-700">Activity Over Time</h5>
                  <div className="space-y-2">
                    {data.analytics.activity.slice(-7).map((activity) => (
                      <div key={activity.date} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">{activity.date}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${(activity.totalActivity / 50) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{activity.totalActivity}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quality Chart */}
              {selectedChart === 'quality' && (
                <div className="space-y-4">
                  <h5 className="text-sm font-semibold text-gray-700">Quality Trends</h5>
                  <div className="space-y-2">
                    {data.analytics.quality.slice(-7).map((quality) => (
                      <div key={quality.date} className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">{quality.date}</span>
                          <span className="text-sm font-medium">
                            {(quality.overallQuality * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${quality.overallQuality * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Performance Chart */}
              {selectedChart === 'performance' && (
                <div className="space-y-4">
                  <h5 className="text-sm font-semibold text-gray-700">Performance Metrics</h5>
                  <div className="space-y-2">
                    {data.analytics.performance.slice(-7).map((perf) => (
                      <div key={perf.date} className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">{perf.date}</span>
                          <span className="text-sm font-medium">{perf.responseTime}ms</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${(perf.responseTime / 200) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Event Statistics */}
              <div className="mt-6">
                <h5 className="text-sm font-semibold text-gray-700 mb-3">Event Statistics</h5>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Documentation</span>
                    <span className="font-medium">{data.events.documentation.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Code</span>
                    <span className="font-medium">{data.events.code.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Specifications</span>
                    <span className="font-medium">{data.events.spec.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">System</span>
                    <span className="font-medium">{data.events.system.length}</span>
                  </div>
                </div>
              </div>

              {/* Evolution Data */}
              <div className="mt-6">
                <h5 className="text-sm font-semibold text-gray-700 mb-3">Evolution</h5>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Versions</span>
                    <span className="font-medium">{data.evolution.versions.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Milestones</span>
                    <span className="font-medium">{data.evolution.milestones.length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Event Details Sidebar */}
        {selectedEvent && (
          <div className="w-80 border-l border-gray-200 bg-white overflow-y-auto">
            <div className="p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Event Details</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Action</label>
                  <p className="text-gray-900">{selectedEvent.data.action}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Type</label>
                  <p className="text-gray-900 capitalize">{selectedEvent.type.replace('_', ' ')}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Result</label>
                  <div className="flex items-center space-x-2">
                    {getEventResultIcon(selectedEvent.data.result)}
                    <span className="text-gray-900 capitalize">{selectedEvent.data.result}</span>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Timestamp</label>
                  <p className="text-gray-900 text-sm">{formatTime(selectedEvent.timestamp)}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">User</label>
                  <p className="text-gray-900">{selectedEvent.context.user}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Environment</label>
                  <p className="text-gray-900 capitalize">{selectedEvent.context.environment}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Version</label>
                  <p className="text-gray-900">{selectedEvent.context.version}</p>
                </div>
                
                {selectedEvent.nodeId && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Node ID</label>
                    <p className="text-gray-900 text-sm">{selectedEvent.nodeId}</p>
                  </div>
                )}
                
                {selectedEvent.data.details && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Details</label>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                        {JSON.stringify(selectedEvent.data.details, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
