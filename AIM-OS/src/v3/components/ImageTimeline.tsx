import { useState, useRef, useCallback } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Plus,
  Trash2,
  Copy,
  Diamond,
  ChevronUp,
  ChevronDown,
  Minimize2,
  Maximize2,
  GripHorizontal,
  ZoomIn,
  ZoomOut,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Move,
  RotateCcw,
  Maximize2 as ScaleIcon,
  Palette,
  type LucideIcon,
} from 'lucide-react';

export type TimelineSize = 'mini' | 'medium' | 'large';

export type EasingType = 
  | 'linear'
  | 'ease-in'
  | 'ease-out'
  | 'ease-in-out'
  | 'bounce'
  | 'elastic'
  | 'cubic-bezier';

export type TweenProperty =
  | 'position'
  | 'rotation'
  | 'scale'
  | 'opacity'
  | 'color'
  | 'blur'
  | 'path'
  | 'morph'
  | 'custom';

export interface Keyframe {
  id: string;
  frame: number;
  value: any;
  easing: EasingType;
  bezierHandles?: {
    in: { x: number; y: number };
    out: { x: number; y: number };
  };
}

export interface AnimationTrack {
  id: string;
  name: string;
  layerId: string;
  property: TweenProperty;
  keyframes: Keyframe[];
  color: string;
  muted: boolean;
  locked: boolean;
  visible: boolean;
}

export interface ImageTimelineProps {
  tracks: AnimationTrack[];
  currentFrame: number;
  totalFrames: number;
  fps: number;
  isPlaying: boolean;
  selectedKeyframeId: string | null;
  onPlayPause: () => void;
  onSeek: (frame: number) => void;
  onSelectKeyframe: (id: string | null) => void;
  onAddKeyframe: (trackId: string, frame: number) => void;
  onDeleteKeyframe: (trackId: string, keyframeId: string) => void;
  onTrackToggle: (trackId: string, property: 'muted' | 'locked' | 'visible') => void;
  onKeyframeMove?: (trackId: string, keyframeId: string, newFrame: number) => void;
}

const EASING_ICONS: Record<EasingType, LucideIcon> = {
  'linear': Maximize2,
  'ease-in': ChevronUp,
  'ease-out': ChevronDown,
  'ease-in-out': Diamond,
  'bounce': Maximize2,
  'elastic': Maximize2,
  'cubic-bezier': Diamond,
};

const PROPERTY_CONFIG: Record<TweenProperty, { icon: LucideIcon; color: string; label: string }> = {
  position: { icon: Move, color: '#3B82F6', label: 'Position' },
  rotation: { icon: RotateCcw, color: '#8B5CF6', label: 'Rotation' },
  scale: { icon: ScaleIcon, color: '#10B981', label: 'Scale' },
  opacity: { icon: Eye, color: '#F59E0B', label: 'Opacity' },
  color: { icon: Palette, color: '#EC4899', label: 'Color' },
  blur: { icon: Maximize2, color: '#6366F1', label: 'Blur' },
  path: { icon: Maximize2, color: '#14B8A6', label: 'Path' },
  morph: { icon: Maximize2, color: '#F97316', label: 'Morph' },
  custom: { icon: Diamond, color: '#64748B', label: 'Custom' },
};

interface KeyframeMarkerProps {
  keyframe: Keyframe;
  trackColor: string;
  isSelected: boolean;
  position: number;
  height: number;
  onSelect: () => void;
  onMove?: (newFrame: number) => void;
}

function KeyframeMarker({
  keyframe,
  trackColor,
  isSelected,
  position,
  height,
  onSelect,
  onMove,
}: KeyframeMarkerProps) {
  const EasingIcon = EASING_ICONS[keyframe.easing];
  const size = height > 40 ? 12 : 8;
  const isDraggingRef = useRef(false);
  const startXRef = useRef(0);
  const startFrameRef = useRef(0);
  
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    isDraggingRef.current = true;
    startXRef.current = e.clientX;
    startFrameRef.current = keyframe.frame;
    
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current || !onMove) return;
      const deltaX = e.clientX - startXRef.current;
      const zoom = 8; // TODO: Get from context
      const deltaFrame = Math.round(deltaX / zoom);
      onMove(startFrameRef.current + deltaFrame);
    };
    
    const handleMouseUp = () => {
      isDraggingRef.current = false;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [keyframe.frame, onMove]);
  
  return (
    <div
      className={`absolute top-1/2 -translate-y-1/2 cursor-move ${
        isSelected ? 'z-20' : 'z-10'
      }`}
      style={{ left: `${position}px` }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
      onMouseDown={handleMouseDown}
    >
      <div
        className={`
          rounded transition-all
          ${isSelected 
            ? 'ring-2 ring-white shadow-lg' 
            : 'hover:ring-1 hover:ring-gray-400'
          }
        `}
        style={{
          width: size,
          height: size,
          backgroundColor: trackColor,
        }}
      >
        <EasingIcon 
          className="w-full h-full p-0.5 text-white opacity-80" 
          style={{ width: size, height: size }}
        />
      </div>
    </div>
  );
}

interface TweenSpanProps {
  startFrame: number;
  endFrame: number;
  startKeyframe: Keyframe;
  endKeyframe: Keyframe;
  trackColor: string;
  zoom: number;
  height: number;
}

function TweenSpan({
  startFrame,
  endFrame,
  startKeyframe,
  endKeyframe,
  trackColor,
  zoom,
  height,
}: TweenSpanProps) {
  const width = (endFrame - startFrame) * zoom;
  const left = startFrame * zoom;
  
  const generateEasingPath = () => {
    const h = Math.min(height - 8, 20);
    const w = width;
    
    switch (endKeyframe.easing) {
      case 'ease-in':
        return `M 0 ${h} Q ${w * 0.6} ${h} ${w} 0`;
      case 'ease-out':
        return `M 0 ${h} Q ${w * 0.4} 0 ${w} 0`;
      case 'ease-in-out':
        return `M 0 ${h} C ${w * 0.4} ${h} ${w * 0.6} 0 ${w} 0`;
      case 'bounce':
        return `M 0 ${h} Q ${w * 0.2} 0 ${w * 0.4} ${h * 0.5} Q ${w * 0.6} ${h} ${w * 0.8} ${h * 0.3} L ${w} 0`;
      case 'elastic':
        return `M 0 ${h} Q ${w * 0.3} ${h * -0.5} ${w * 0.5} ${h * 0.5} Q ${w * 0.7} ${h * 1.5} ${w} 0`;
      default:
        return `M 0 ${h} L ${w} 0`;
    }
  };
  
  return (
    <div
      className="absolute top-1 bottom-1 pointer-events-none"
      style={{ left, width }}
    >
      <div 
        className="absolute inset-0 rounded opacity-20"
        style={{ 
          background: `linear-gradient(90deg, ${trackColor}00, ${trackColor}40, ${trackColor}00)` 
        }}
      />
      
      {height > 30 && (
        <svg className="absolute inset-0 w-full h-full overflow-visible">
          <path
            d={generateEasingPath()}
            fill="none"
            stroke={trackColor}
            strokeWidth="1.5"
            strokeDasharray="4 2"
            opacity="0.6"
          />
        </svg>
      )}
      
      <div 
        className="absolute right-1 top-1/2 -translate-y-1/2 opacity-40"
        style={{ color: trackColor }}
      >
        →
      </div>
    </div>
  );
}

export function ImageTimeline({
  tracks,
  currentFrame,
  totalFrames,
  fps,
  isPlaying,
  selectedKeyframeId,
  onPlayPause,
  onSeek,
  onSelectKeyframe,
  onAddKeyframe,
  onDeleteKeyframe,
  onTrackToggle,
  onKeyframeMove,
}: ImageTimelineProps) {
  const [size, setSize] = useState<TimelineSize>('mini');
  const [zoom, setZoom] = useState(8);
  const [largeHeight, setLargeHeight] = useState(250);
  const resizeRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const timelineRef = useRef<HTMLDivElement>(null);

  const formatTimecode = (frame: number) => {
    const totalSeconds = frame / fps;
    const mins = Math.floor(totalSeconds / 60);
    const secs = Math.floor(totalSeconds % 60);
    const frames = frame % fps;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}:${frames.toString().padStart(2, '0')}`;
  };

  const handleResizeMouseDown = useCallback((e: React.MouseEvent) => {
    isDraggingRef.current = true;
    const startY = e.clientY;
    const startHeight = largeHeight;

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;
      const deltaY = startY - e.clientY;
      setLargeHeight(Math.max(200, Math.min(500, startHeight + deltaY)));
    };

    const handleMouseUp = () => {
      isDraggingRef.current = false;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [largeHeight]);

  const handleTimelineClick = useCallback((e: React.MouseEvent) => {
    if (!timelineRef.current) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const headerWidth = size === 'large' ? 180 : size === 'medium' ? 120 : 0;
    const x = e.clientX - rect.left - headerWidth;
    if (x >= 0) {
      const frame = Math.max(0, Math.min(totalFrames - 1, Math.round(x / zoom)));
      onSeek(frame);
    }
  }, [size, zoom, totalFrames, onSeek]);

  const getHeight = () => {
    switch (size) {
      case 'mini': return 40;
      case 'medium': return 120;
      case 'large': return largeHeight;
    }
  };

  const trackHeight = size === 'large' ? 50 : size === 'medium' ? 24 : 16;

  return (
    <div 
      className="bg-[#1a1a1a] border-t border-gray-700/50 flex flex-col flex-shrink-0"
      style={{ height: `${getHeight()}px` }}
    >
      {size === 'large' && (
        <div
          ref={resizeRef}
          onMouseDown={handleResizeMouseDown}
          className="h-1 bg-gray-700/50 hover:bg-purple-500/50 cursor-ns-resize flex items-center justify-center"
        >
          <GripHorizontal className="w-4 h-4 text-gray-500" />
        </div>
      )}

      <div className="h-10 bg-[#1e1e1e] border-b border-gray-700/50 flex items-center px-2 gap-2 flex-shrink-0">
        <div className="flex items-center gap-0.5">
          <button onClick={() => onSeek(0)} className="p-1.5 hover:bg-gray-700 rounded">
            <SkipBack className="w-4 h-4 text-gray-400" />
          </button>
          <button onClick={onPlayPause} className="p-1.5 hover:bg-gray-700 rounded">
            {isPlaying ? <Pause className="w-4 h-4 text-gray-400" /> : <Play className="w-4 h-4 text-gray-400" />}
          </button>
          <button onClick={() => onSeek(totalFrames - 1)} className="p-1.5 hover:bg-gray-700 rounded">
            <SkipForward className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        <div className="flex items-center gap-2 px-2 border-l border-gray-700">
          <div className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-300 font-mono">
            {formatTimecode(currentFrame)}
          </div>
          <span className="text-xs text-gray-500">F{currentFrame}</span>
        </div>

        <div className="flex items-center gap-0.5 px-2 border-l border-gray-700">
          <button 
            className="p-1.5 hover:bg-gray-700 rounded text-yellow-500"
            title="Add Keyframe (K)"
          >
            <Diamond className="w-4 h-4" />
          </button>
          <button 
            className="p-1.5 hover:bg-gray-700 rounded text-gray-400"
            title="Delete Keyframe"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button 
            className="p-1.5 hover:bg-gray-700 rounded text-gray-400"
            title="Copy Keyframe"
          >
            <Copy className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 mx-4">
          <div className="relative h-6 bg-[#1e1e1e] rounded overflow-hidden border border-gray-700/50">
            <div className="absolute inset-0 flex flex-col justify-center py-0.5 px-1">
              {tracks.slice(0, 4).map((track) => (
                <div key={track.id} className="relative h-1 mb-0.5 last:mb-0">
                  <div 
                    className="absolute inset-0 rounded-full opacity-20"
                    style={{ backgroundColor: track.color }}
                  />
                  {track.keyframes.map(kf => (
                    <div
                      key={kf.id}
                      className="absolute w-1 h-1 rounded-full top-0"
                      style={{
                        left: `${(kf.frame / totalFrames) * 100}%`,
                        backgroundColor: track.color,
                      }}
                    />
                  ))}
                </div>
              ))}
            </div>
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-10"
              style={{ left: `${(currentFrame / totalFrames) * 100}%` }}
            />
            <div 
              className="absolute inset-0 cursor-pointer"
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const x = e.clientX - rect.left;
                onSeek(Math.round((x / rect.width) * totalFrames));
              }}
            />
            {size !== 'mini' && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="px-2 py-0.5 bg-black/60 backdrop-blur-sm rounded text-[10px] text-gray-400">
                  {fps} fps • {totalFrames} frames • {(totalFrames / fps).toFixed(1)}s
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 border-l border-gray-700 pl-2">
          <button 
            onClick={() => setZoom(Math.max(2, zoom - 2))}
            className="p-1.5 hover:bg-gray-700 rounded"
          >
            <ZoomOut className="w-4 h-4 text-gray-400" />
          </button>
          <span className="text-xs text-gray-500 w-6 text-center">{zoom}</span>
          <button 
            onClick={() => setZoom(Math.min(20, zoom + 2))}
            className="p-1.5 hover:bg-gray-700 rounded"
          >
            <ZoomIn className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        <div className="flex items-center gap-0.5 border-l border-gray-700 pl-2">
          {size !== 'mini' && (
            <button onClick={() => setSize('mini')} className="p-1.5 hover:bg-gray-700 rounded" title="Mini">
              <Minimize2 className="w-4 h-4 text-gray-400" />
            </button>
          )}
          {size !== 'medium' && (
            <button onClick={() => setSize('medium')} className="p-1.5 hover:bg-gray-700 rounded" title="Medium">
              <ChevronUp className="w-4 h-4 text-gray-400" />
            </button>
          )}
          {size !== 'large' && (
            <button onClick={() => setSize('large')} className="p-1.5 hover:bg-gray-700 rounded" title="Large">
              <Maximize2 className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      </div>

      {size !== 'mini' && (
        <div className="flex-1 flex overflow-hidden">
          <div className={`flex-shrink-0 overflow-y-auto bg-[#1a1a1a] ${size === 'large' ? 'w-[180px]' : 'w-[120px]'}`}>
            {tracks.map((track) => {
              const config = PROPERTY_CONFIG[track.property];
              const Icon = config.icon;
              
              return (
                <div 
                  key={track.id}
                  className="flex items-center gap-1 px-2 border-b border-gray-800"
                  style={{ height: trackHeight }}
                >
                  <div 
                    className="w-2 h-2 rounded-sm flex-shrink-0"
                    style={{ backgroundColor: track.color }}
                  />
                  <Icon className="w-3 h-3 flex-shrink-0" style={{ color: track.color }} />
                  <span className={`flex-1 truncate ${size === 'large' ? 'text-sm' : 'text-xs'} text-gray-300`}>
                    {track.name}
                  </span>
                  {size === 'large' && (
                    <div className="flex items-center gap-0.5">
                      <button
                        onClick={() => onTrackToggle(track.id, 'muted')}
                        className={`p-0.5 rounded ${track.muted ? 'bg-red-500/20 text-red-400' : 'text-gray-500 hover:bg-gray-700'}`}
                      >
                        M
                      </button>
                      <button
                        onClick={() => onTrackToggle(track.id, 'locked')}
                        className={`p-0.5 rounded ${track.locked ? 'bg-yellow-500/20 text-yellow-400' : 'text-gray-500 hover:bg-gray-700'}`}
                      >
                        {track.locked ? <Lock className="w-3 h-3" /> : <Unlock className="w-3 h-3" />}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div 
            ref={timelineRef}
            className="flex-1 overflow-auto"
            onClick={handleTimelineClick}
          >
            <div style={{ width: `${totalFrames * zoom}px`, minWidth: '100%' }}>
              <div className={`bg-[#252525] border-b border-gray-700/50 relative ${size === 'large' ? 'h-6' : 'h-4'}`}>
                {Array.from({ length: Math.ceil(totalFrames / 10) + 1 }).map((_, i) => (
                  <div
                    key={i}
                    className="absolute top-0 bottom-0 border-l border-gray-600/50"
                    style={{ left: `${i * 10 * zoom}px` }}
                  >
                    <span className="text-[9px] text-gray-500 ml-1">
                      {i * 10}
                    </span>
                  </div>
                ))}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20"
                  style={{ left: `${currentFrame * zoom}px` }}
                >
                  <div className="w-3 h-3 bg-red-500 -ml-[5px] -mt-0.5 rotate-45" />
                </div>
              </div>

              {tracks.map((track) => {
                const sortedKeyframes = [...track.keyframes].sort((a, b) => a.frame - b.frame);
                
                return (
                  <div
                    key={track.id}
                    className="relative border-b border-gray-800"
                    style={{ 
                      height: trackHeight,
                      opacity: track.visible ? 1 : 0.3,
                    }}
                    onDoubleClick={(e) => {
                      if (track.locked) return;
                      const rect = e.currentTarget.getBoundingClientRect();
                      const x = e.clientX - rect.left;
                      const frame = Math.round(x / zoom);
                      onAddKeyframe(track.id, frame);
                    }}
                  >
                    {sortedKeyframes.map((kf, index) => {
                      if (index === sortedKeyframes.length - 1) return null;
                      const nextKf = sortedKeyframes[index + 1];
                      return (
                        <TweenSpan
                          key={`tween-${kf.id}`}
                          startFrame={kf.frame}
                          endFrame={nextKf.frame}
                          startKeyframe={kf}
                          endKeyframe={nextKf}
                          trackColor={track.color}
                          zoom={zoom}
                          height={trackHeight}
                        />
                      );
                    })}
                    
                    {sortedKeyframes.map((kf) => (
                      <KeyframeMarker
                        key={kf.id}
                        keyframe={kf}
                        trackColor={track.color}
                        isSelected={selectedKeyframeId === kf.id}
                        position={kf.frame * zoom}
                        height={trackHeight}
                        onSelect={() => onSelectKeyframe(kf.id)}
                        onMove={onKeyframeMove ? (newFrame) => onKeyframeMove(track.id, kf.id, newFrame) : undefined}
                      />
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

