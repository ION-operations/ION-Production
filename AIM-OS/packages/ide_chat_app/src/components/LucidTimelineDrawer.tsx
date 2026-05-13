// packages/ide_chat_app/src/components/LucidTimelineDrawer.tsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  SkipBack, 
  SkipForward,
  Clock,
  Activity,
  Zap,
  Target,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  Settings
} from 'lucide-react';

interface TimelineEvent {
  id: string;
  nodeId: string;
  timestamp: number;
  type: 'execution' | 'error' | 'test' | 'modification' | 'focus' | 'drift';
  duration: number;
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  nodeName: string;
  filePath: string;
  line: number;
}

interface TimelineNode {
  id: string;
  name: string;
  type: 'function' | 'component' | 'class' | 'interface' | 'test';
  color: string;
  events: TimelineEvent[];
}

export const LucidTimelineDrawer: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [maxTime, setMaxTime] = useState(1000);
  const [zoom, setZoom] = useState(1);
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);
  const [showGrid, setShowGrid] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  
  const timelineRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();

  // Mock data for demonstration
  const [timelineNodes, setTimelineNodes] = useState<TimelineNode[]>([
    {
      id: 'node-1',
      name: 'processUserData',
      type: 'function',
      color: 'bg-blue-500',
      events: [
        {
          id: 'event-1',
          nodeId: 'node-1',
          timestamp: 0,
          type: 'execution',
          duration: 150,
          status: 'success',
          message: 'processUserData executed successfully',
          nodeName: 'processUserData',
          filePath: 'src/utils/user.ts',
          line: 45
        },
        {
          id: 'event-2',
          nodeId: 'node-1',
          timestamp: 200,
          type: 'test',
          duration: 80,
          status: 'success',
          message: 'processUserData test passed',
          nodeName: 'processUserData',
          filePath: 'src/utils/user.ts',
          line: 45
        }
      ]
    },
    {
      id: 'node-2',
      name: 'UserComponent',
      type: 'component',
      color: 'bg-green-500',
      events: [
        {
          id: 'event-3',
          nodeId: 'node-2',
          timestamp: 100,
          type: 'execution',
          duration: 120,
          status: 'success',
          message: 'UserComponent rendered',
          nodeName: 'UserComponent',
          filePath: 'src/components/User.tsx',
          line: 12
        },
        {
          id: 'event-4',
          nodeId: 'node-2',
          timestamp: 300,
          type: 'focus',
          duration: 0,
          status: 'info',
          message: 'UserComponent focused',
          nodeName: 'UserComponent',
          filePath: 'src/components/User.tsx',
          line: 12
        }
      ]
    },
    {
      id: 'node-3',
      name: 'validateInput',
      type: 'function',
      color: 'bg-yellow-500',
      events: [
        {
          id: 'event-5',
          nodeId: 'node-3',
          timestamp: 250,
          type: 'error',
          duration: 0,
          status: 'error',
          message: 'Validation failed: invalid email format',
          nodeName: 'validateInput',
          filePath: 'src/utils/validation.ts',
          line: 8
        }
      ]
    }
  ]);

  // Calculate max time from all events
  useEffect(() => {
    const allEvents = timelineNodes.flatMap(node => node.events);
    const maxEventTime = Math.max(...allEvents.map(e => e.timestamp + e.duration));
    setMaxTime(Math.max(maxEventTime, 1000));
  }, [timelineNodes]);

  // Animation loop
  useEffect(() => {
    if (isPlaying) {
      const animate = () => {
        setCurrentTime(prev => {
          const newTime = prev + (0.1 * playbackSpeed);
          if (newTime >= maxTime) {
            setIsPlaying(false);
            return 0;
          }
          return newTime;
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
  }, [isPlaying, maxTime, playbackSpeed]);

  const getEventStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      case 'info': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getEventTypeIcon = (type: string) => {
    switch (type) {
      case 'execution': return <Activity className="w-3 h-3" />;
      case 'error': return <Target className="w-3 h-3" />;
      case 'test': return <Zap className="w-3 h-3" />;
      case 'modification': return <Settings className="w-3 h-3" />;
      case 'focus': return <Eye className="w-3 h-3" />;
      case 'drift': return <Clock className="w-3 h-3" />;
      default: return <Activity className="w-3 h-3" />;
    }
  };

  const formatTime = (time: number) => {
    return `${Math.round(time)}ms`;
  };

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (timelineRef.current) {
      const rect = timelineRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = x / rect.width;
      const newTime = percentage * maxTime;
      setCurrentTime(newTime);
    }
  };

  return (
    <div className="h-full bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-orange-400" />
            <h2 className="text-lg font-semibold">Lucid Timeline</h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Live</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-2 rounded ${showGrid ? 'bg-blue-600' : 'bg-gray-700'} hover:bg-blue-700`}
            title="Toggle Grid"
          >
            <Target className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`p-2 rounded ${showLabels ? 'bg-blue-600' : 'bg-gray-700'} hover:bg-blue-700`}
            title="Toggle Labels"
          >
            <Eye className="w-4 h-4" />
          </button>
          <div className="w-px h-6 bg-gray-600"></div>
          <span className="text-sm text-gray-400">Speed:</span>
          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
            className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>
        </div>
      </div>

      {/* Timeline Controls */}
      <div className="flex items-center gap-2 p-3 border-b border-gray-700 bg-gray-800">
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-2 rounded bg-blue-600 hover:bg-blue-700"
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>
        <button
          onClick={() => setCurrentTime(0)}
          className="p-2 rounded bg-gray-700 hover:bg-gray-600"
          title="Reset"
        >
          <Square className="w-4 h-4" />
        </button>
        <button
          onClick={() => setCurrentTime(Math.max(0, currentTime - 100))}
          className="p-2 rounded bg-gray-700 hover:bg-gray-600"
          title="Skip Back"
        >
          <SkipBack className="w-4 h-4" />
        </button>
        <button
          onClick={() => setCurrentTime(Math.min(maxTime, currentTime + 100))}
          className="p-2 rounded bg-gray-700 hover:bg-gray-600"
          title="Skip Forward"
        >
          <SkipForward className="w-4 h-4" />
        </button>
        
        <div className="flex-1 mx-4">
          <div className="w-full bg-gray-700 rounded h-2 cursor-pointer" onClick={handleTimelineClick}>
            <div 
              className="bg-blue-500 h-2 rounded transition-all duration-100 relative"
              style={{ width: `${(currentTime / maxTime) * 100}%` }}
            >
              <div className="absolute right-0 top-0 w-2 h-2 bg-blue-400 rounded-full transform translate-x-1 -translate-y-1"></div>
            </div>
          </div>
        </div>
        
        <div className="text-sm text-gray-400 min-w-0">
          {formatTime(currentTime)} / {formatTime(maxTime)}
        </div>
      </div>

      {/* Timeline Content */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex">
          {/* Node Labels */}
          <div className="w-48 border-r border-gray-700 bg-gray-800">
            <div className="p-3 border-b border-gray-700">
              <h3 className="text-sm font-medium text-gray-300">Nodes</h3>
            </div>
            <div className="overflow-y-auto">
              {timelineNodes.map((node) => (
                <div key={node.id} className="p-3 border-b border-gray-700 hover:bg-gray-700">
                  <div className="flex items-center gap-2 mb-1">
                    <div className={`w-3 h-3 rounded ${node.color}`}></div>
                    <span className="text-sm font-medium">{node.name}</span>
                  </div>
                  <div className="text-xs text-gray-400">{node.type}</div>
                  <div className="text-xs text-gray-500">{node.events.length} events</div>
                </div>
              ))}
            </div>
          </div>

          {/* Timeline Visualization */}
          <div className="flex-1 relative overflow-x-auto">
            <div 
              ref={timelineRef}
              className="h-full relative cursor-pointer"
              onClick={handleTimelineClick}
            >
              {/* Grid */}
              {showGrid && (
                <div className="absolute inset-0 opacity-20">
                  <svg className="w-full h-full">
                    <defs>
                      <pattern id="timeline-grid" width="50" height="30" patternUnits="userSpaceOnUse">
                        <path d="M 50 0 L 0 0 0 30" fill="none" stroke="currentColor" strokeWidth="1"/>
                      </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#timeline-grid)" />
                  </svg>
                </div>
              )}

              {/* Time Ruler */}
              <div className="absolute top-0 left-0 right-0 h-8 bg-gray-800 border-b border-gray-700">
                <div className="flex h-full">
                  {Array.from({ length: Math.ceil(maxTime / 100) }, (_, i) => (
                    <div key={i} className="flex-1 border-r border-gray-600 text-xs text-gray-400 flex items-center justify-center">
                      {i * 100}ms
                    </div>
                  ))}
                </div>
              </div>

              {/* Timeline Tracks */}
              <div className="pt-8 h-full">
                {timelineNodes.map((node, nodeIndex) => (
                  <div key={node.id} className="h-12 border-b border-gray-700 relative">
                    {/* Node Track Background */}
                    <div className="absolute inset-0 bg-gray-800/50"></div>
                    
                    {/* Events */}
                    {node.events.map((event) => {
                      const leftPercent = (event.timestamp / maxTime) * 100;
                      const widthPercent = (event.duration / maxTime) * 100;
                      const isActive = event.timestamp <= currentTime && currentTime <= event.timestamp + event.duration;
                      
                      return (
                        <div
                          key={event.id}
                          className={`absolute top-1 h-10 rounded cursor-pointer transition-all duration-200 ${
                            isActive ? 'opacity-100 scale-105' : 'opacity-80'
                          } ${getEventStatusColor(event.status)}`}
                          style={{
                            left: `${leftPercent}%`,
                            width: `${Math.max(widthPercent, 2)}%`,
                            minWidth: '8px'
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedEvent(event);
                          }}
                          title={`${event.message} (${event.timestamp}ms - ${event.timestamp + event.duration}ms)`}
                        >
                          <div className="flex items-center justify-center h-full text-white">
                            {getEventTypeIcon(event.type)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>

              {/* Current Time Indicator */}
              <div 
                className="absolute top-0 bottom-0 w-0.5 bg-blue-400 pointer-events-none z-10"
                style={{ left: `${(currentTime / maxTime) * 100}%` }}
              >
                <div className="absolute -top-1 -left-1 w-2 h-2 bg-blue-400 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Event Details Panel */}
      {selectedEvent && (
        <div className="border-t border-gray-700 bg-gray-800 p-4 max-h-32 overflow-y-auto">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-medium text-sm">{selectedEvent.message}</h3>
            <button
              onClick={() => setSelectedEvent(null)}
              className="text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            <div>Node: {selectedEvent.nodeName}</div>
            <div>File: {selectedEvent.filePath}:{selectedEvent.line}</div>
            <div>Time: {formatTime(selectedEvent.timestamp)} - {formatTime(selectedEvent.timestamp + selectedEvent.duration)}</div>
            <div>Type: {selectedEvent.type} • Status: {selectedEvent.status}</div>
          </div>
        </div>
      )}
    </div>
  );
};
