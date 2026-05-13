import React, { useState, useMemo } from 'react';
import { 
  Grid3X3, 
  Target, 
  Maximize, 
  SplitSquareHorizontal, 
  Activity,
  Ruler,
  X,
  ChevronUp,
} from 'lucide-react';

type CameraPreset = 'perspective' | 'front' | 'back' | 'top' | 'left' | 'right' | 'bottom';
type RenderMode = 'solid' | 'wireframe' | 'xray' | 'points' | 'flat' | 'normal';
type SplitViewMode = 'single' | 'side-by-side' | 'dual-3d' | 'overlay' | 'pip' | 'fullscreen-2d' | 'fullscreen-3d';

interface GuidePlane {
  id: string;
  axis: 'x' | 'y' | 'z';
  position: number;
  visible: boolean;
}

interface ThreeDBottomBarProps {
  showGrid: boolean;
  onToggleGrid?: () => void;
  showCursor: boolean;
  onToggleCursor?: () => void;
  showRulerPreviewPlanes: boolean;
  onToggleRulerPreviewPlanes?: () => void;
  cameraPreset: CameraPreset;
  onCameraPresetChange?: (preset: CameraPreset) => void;
  showStats: boolean;
  onToggleStats?: () => void;
  stats?: { fps: number; triangles: number; calls: number };
  renderMode: RenderMode;
  onRenderModeChange?: (mode: RenderMode) => void;
  viewMode: SplitViewMode;
  onViewModeChange?: (mode: SplitViewMode) => void;
  xrayMode: boolean;
  onXrayModeChange?: (enabled: boolean) => void;
  selectedObjectId: string | null;
  guidePlanes?: GuidePlane[];
  onDeleteGuidePlane?: (id: string) => void;
  onClearAllGuides?: () => void;
  onHighlightGuidePlane?: (id: string | null) => void;
}

const CAMERA_PRESETS: Record<CameraPreset, { name: string }> = {
  perspective: { name: 'Perspective' },
  front: { name: 'Front' },
  back: { name: 'Back' },
  top: { name: 'Top' },
  left: { name: 'Left' },
  right: { name: 'Right' },
  bottom: { name: 'Bottom' },
};

const RENDER_MODES: { value: RenderMode; label: string }[] = [
  { value: 'solid', label: 'Solid' },
  { value: 'wireframe', label: 'Wireframe' },
  { value: 'xray', label: 'X-Ray' },
  { value: 'points', label: 'Points' },
  { value: 'flat', label: 'Flat' },
  { value: 'normal', label: 'Normal' },
];

const VIEW_MODES: { value: SplitViewMode; label: string }[] = [
  { value: 'single', label: '3D Only' },
  { value: 'fullscreen-2d', label: '2D Only' },
  { value: 'side-by-side', label: 'Split H' },
  { value: 'dual-3d', label: 'Dual 3D' },
  { value: 'overlay', label: 'Overlay' },
  { value: 'pip', label: 'PiP' },
];

interface RulerManagementDropdownProps {
  guidePlanes: GuidePlane[];
  onDeleteGuidePlane?: (id: string) => void;
  onClearAllGuides?: () => void;
  onHighlightGuidePlane?: (id: string | null) => void;
}

function RulerManagementDropdown({
  guidePlanes,
  onDeleteGuidePlane,
  onClearAllGuides,
  onHighlightGuidePlane,
}: RulerManagementDropdownProps) {
  const [showDropdown, setShowDropdown] = useState(false);
  const [hoveredPlaneId, setHoveredPlaneId] = useState<string | null>(null);
  
  const planesByAxis = useMemo(() => ({
    x: guidePlanes.filter(p => p.axis === 'x' && p.visible),
    y: guidePlanes.filter(p => p.axis === 'y' && p.visible),
    z: guidePlanes.filter(p => p.axis === 'z' && p.visible),
  }), [guidePlanes]);
  
  const totalCount = planesByAxis.x.length + planesByAxis.y.length + planesByAxis.z.length;
  const hasGuides = totalCount > 0;
  
  React.useEffect(() => {
    if (onHighlightGuidePlane) {
      onHighlightGuidePlane(hoveredPlaneId);
    }
  }, [hoveredPlaneId, onHighlightGuidePlane]);
  
  React.useEffect(() => {
    if (!showDropdown && onHighlightGuidePlane) {
      onHighlightGuidePlane(null);
      setHoveredPlaneId(null);
    }
  }, [showDropdown, onHighlightGuidePlane]);
  
  const AXIS_COLORS = {
    x: '#ff4444',
    y: '#44ff44',
    z: '#4444ff',
  };
  
  const AXIS_LABELS = {
    x: 'X',
    y: 'Y',
    z: 'Z',
  };
  
  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
          hasGuides
            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
            : 'bg-gray-800/50 text-gray-500 border border-gray-700/30 hover:bg-gray-800/70'
        }`}
        title="Ruler Lines Management"
      >
        <Ruler className="w-3.5 h-3.5" />
        <span>Rulers</span>
        
        {hasGuides && (
          <div className="flex items-center gap-1">
            {planesByAxis.x.length > 0 && (
              <span 
                className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
                style={{ color: AXIS_COLORS.x, backgroundColor: `${AXIS_COLORS.x}20` }}
              >
                {AXIS_LABELS.x}:{planesByAxis.x.length}
              </span>
            )}
            {planesByAxis.y.length > 0 && (
              <span 
                className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
                style={{ color: AXIS_COLORS.y, backgroundColor: `${AXIS_COLORS.y}20` }}
              >
                {AXIS_LABELS.y}:{planesByAxis.y.length}
              </span>
            )}
            {planesByAxis.z.length > 0 && (
              <span 
                className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
                style={{ color: AXIS_COLORS.z, backgroundColor: `${AXIS_COLORS.z}20` }}
              >
                {AXIS_LABELS.z}:{planesByAxis.z.length}
              </span>
            )}
          </div>
        )}
        
        <ChevronUp className={`w-3 h-3 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
      </button>
      
      {showDropdown && (
        <>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setShowDropdown(false)}
          />
          
          <div className="absolute bottom-full left-0 mb-2 w-64 max-h-80 overflow-auto bg-gray-900/95 backdrop-blur-sm rounded-lg border border-gray-700/50 shadow-xl z-50">
            <div className="sticky top-0 px-3 py-2 bg-gray-800/50 border-b border-gray-700/50 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-300">Guide Planes</span>
              {onClearAllGuides && totalCount > 0 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Clear all ${totalCount} guide${totalCount !== 1 ? 's' : ''}?`)) {
                      onClearAllGuides();
                    }
                  }}
                  className="text-[10px] text-red-400 hover:text-red-300 transition-colors"
                >
                  Clear All
                </button>
              )}
            </div>
            
            <div className="py-1">
              {planesByAxis.x.length > 0 && (
                <div className="mb-2">
                  <div className="px-3 py-1 text-[10px] text-gray-500 uppercase font-medium">
                    X Axis ({planesByAxis.x.length})
                  </div>
                  {planesByAxis.x.map((plane) => (
                    <GuidePlaneItem
                      key={plane.id}
                      plane={plane}
                      axisColor={AXIS_COLORS.x}
                      axisLabel={AXIS_LABELS.x}
                      isHovered={hoveredPlaneId === plane.id}
                      onHover={() => setHoveredPlaneId(plane.id)}
                      onLeave={() => setHoveredPlaneId(null)}
                      onDelete={() => {
                        if (onDeleteGuidePlane) {
                          onDeleteGuidePlane(plane.id);
                        }
                      }}
                    />
                  ))}
                </div>
              )}
              
              {planesByAxis.y.length > 0 && (
                <div className="mb-2">
                  <div className="px-3 py-1 text-[10px] text-gray-500 uppercase font-medium">
                    Y Axis ({planesByAxis.y.length})
                  </div>
                  {planesByAxis.y.map((plane) => (
                    <GuidePlaneItem
                      key={plane.id}
                      plane={plane}
                      axisColor={AXIS_COLORS.y}
                      axisLabel={AXIS_LABELS.y}
                      isHovered={hoveredPlaneId === plane.id}
                      onHover={() => setHoveredPlaneId(plane.id)}
                      onLeave={() => setHoveredPlaneId(null)}
                      onDelete={() => {
                        if (onDeleteGuidePlane) {
                          onDeleteGuidePlane(plane.id);
                        }
                      }}
                    />
                  ))}
                </div>
              )}
              
              {planesByAxis.z.length > 0 && (
                <div className="mb-2">
                  <div className="px-3 py-1 text-[10px] text-gray-500 uppercase font-medium">
                    Z Axis ({planesByAxis.z.length})
                  </div>
                  {planesByAxis.z.map((plane) => (
                    <GuidePlaneItem
                      key={plane.id}
                      plane={plane}
                      axisColor={AXIS_COLORS.z}
                      axisLabel={AXIS_LABELS.z}
                      isHovered={hoveredPlaneId === plane.id}
                      onHover={() => setHoveredPlaneId(plane.id)}
                      onLeave={() => setHoveredPlaneId(null)}
                      onDelete={() => {
                        if (onDeleteGuidePlane) {
                          onDeleteGuidePlane(plane.id);
                        }
                      }}
                    />
                  ))}
                </div>
              )}
              
              {!hasGuides && (
                <div className="px-3 py-8 text-center text-xs text-gray-500">
                  No guide planes
                  <div className="text-[10px] text-gray-600 mt-1">
                    Click on rulers to create guides
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

interface GuidePlaneItemProps {
  plane: GuidePlane;
  axisColor: string;
  axisLabel: string;
  isHovered: boolean;
  onHover: () => void;
  onLeave: () => void;
  onDelete: () => void;
}

function GuidePlaneItem({
  plane,
  axisColor,
  axisLabel,
  isHovered,
  onHover,
  onLeave,
  onDelete,
}: GuidePlaneItemProps) {
  return (
    <div
      className={`
        px-3 py-2 flex items-center justify-between
        transition-colors
        ${isHovered ? 'bg-gray-800/80' : 'hover:bg-gray-800/50'}
      `}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      style={{
        borderLeft: `3px solid ${isHovered ? axisColor : 'transparent'}`,
      }}
    >
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <div
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: axisColor }}
        />
        
        <div className="flex-1 min-w-0">
          <div className="text-xs text-gray-300 font-mono">
            {axisLabel} = {plane.position.toFixed(2)}
          </div>
          {!plane.visible && (
            <div className="text-[9px] text-gray-500">Hidden</div>
          )}
        </div>
      </div>
      
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="p-1 rounded hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors flex-shrink-0"
        title="Delete guide"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );
}

export function ThreeDBottomBar({
  showGrid,
  onToggleGrid,
  showCursor,
  onToggleCursor,
  showRulerPreviewPlanes,
  onToggleRulerPreviewPlanes,
  cameraPreset,
  onCameraPresetChange,
  showStats,
  onToggleStats,
  stats,
  renderMode,
  onRenderModeChange,
  viewMode,
  onViewModeChange,
  xrayMode,
  onXrayModeChange,
  selectedObjectId,
  guidePlanes,
  onDeleteGuidePlane,
  onClearAllGuides,
  onHighlightGuidePlane,
}: ThreeDBottomBarProps) {
  const [showCameraMenu, setShowCameraMenu] = useState(false);
  const [showRenderMenu, setShowRenderMenu] = useState(false);
  const [showViewMenu, setShowViewMenu] = useState(false);

  return (
    <div className="h-12 bg-[#1a1a1a] border-t border-gray-700/50 flex items-center gap-2 px-3 flex-shrink-0">
      {onViewModeChange && (
        <div className="relative">
          <button
            onClick={() => setShowViewMenu(!showViewMenu)}
            className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
              viewMode !== 'single'
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                : 'bg-gray-800/50 text-gray-400 border border-gray-700/30 hover:bg-gray-800/70'
            }`}
            title="Split View Mode"
          >
            <SplitSquareHorizontal className="w-3.5 h-3.5" />
            <span>{VIEW_MODES.find(m => m.value === viewMode)?.label || 'Single'}</span>
          </button>
          
          {showViewMenu && (
            <div className="absolute bottom-full left-0 mb-1 bg-gray-900/95 backdrop-blur-sm rounded-lg overflow-hidden border border-gray-700/50 shadow-xl z-50">
              {VIEW_MODES.map(mode => (
                <button
                  key={mode.value}
                  onClick={() => {
                    onViewModeChange(mode.value);
                    setShowViewMenu(false);
                  }}
                  className={`w-full px-4 py-2 text-xs text-left hover:bg-gray-800/80 flex items-center gap-2 ${
                    viewMode === mode.value ? 'text-blue-400 bg-blue-500/10' : 'text-gray-300'
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {onRenderModeChange && (
        <div className="relative">
          <button
            onClick={() => setShowRenderMenu(!showRenderMenu)}
            className="px-3 py-1.5 rounded text-xs flex items-center gap-2 bg-gray-800/50 text-gray-400 border border-gray-700/30 hover:bg-gray-800/70 transition-all"
            title="Render Mode"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{RENDER_MODES.find(m => m.value === renderMode)?.label || 'Solid'}</span>
          </button>
          
          {showRenderMenu && (
            <div className="absolute bottom-full left-0 mb-1 bg-gray-900/95 backdrop-blur-sm rounded-lg overflow-hidden border border-gray-700/50 shadow-xl z-50">
              {RENDER_MODES.map(mode => (
                <button
                  key={mode.value}
                  onClick={() => {
                    onRenderModeChange(mode.value);
                    setShowRenderMenu(false);
                  }}
                  className={`w-full px-4 py-2 text-xs text-left hover:bg-gray-800/80 flex items-center gap-2 ${
                    renderMode === mode.value ? 'text-purple-400 bg-purple-500/10' : 'text-gray-300'
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="w-px h-6 bg-gray-700/50" />

      {onToggleGrid && (
        <button
          onClick={onToggleGrid}
          className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
            showGrid 
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' 
              : 'bg-gray-800/50 text-gray-500 border border-gray-700/30 hover:bg-gray-800/70'
          }`}
          title="Toggle Grid"
        >
          <Grid3X3 className="w-3.5 h-3.5" />
          <span>Grid</span>
        </button>
      )}

      {onToggleCursor && (
        <button
          onClick={onToggleCursor}
          className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
            showCursor 
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' 
              : 'bg-gray-800/50 text-gray-500 border border-gray-700/30 hover:bg-gray-800/70'
          }`}
          title="Toggle 3D Cursor"
        >
          <Target className="w-3.5 h-3.5" />
          <span>3D Cursor</span>
        </button>
      )}

      {onToggleRulerPreviewPlanes && (
        <button
          onClick={onToggleRulerPreviewPlanes}
          className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
            showRulerPreviewPlanes 
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' 
              : 'bg-gray-800/50 text-gray-500 border border-gray-700/30 hover:bg-gray-800/70'
          }`}
          title="Toggle Ruler Preview Planes"
        >
          <Maximize className="w-3.5 h-3.5" />
          <span>Ruler Preview</span>
        </button>
      )}

      <div className="w-px h-6 bg-gray-700/50" />

      {onCameraPresetChange && (
        <div className="relative">
          <button
            onClick={() => setShowCameraMenu(!showCameraMenu)}
            className="px-3 py-1.5 rounded text-xs flex items-center gap-2 bg-gray-800/50 text-gray-400 border border-gray-700/30 hover:bg-gray-800/70 transition-all"
            title="Camera View"
          >
            <Maximize className="w-3.5 h-3.5" />
            <span>{CAMERA_PRESETS[cameraPreset]?.name || 'Perspective'}</span>
          </button>
          
          {showCameraMenu && (
            <div className="absolute bottom-full left-0 mb-1 bg-gray-900/95 backdrop-blur-sm rounded-lg overflow-hidden border border-gray-700/50 shadow-xl z-50">
              {Object.entries(CAMERA_PRESETS).map(([key, value]) => (
                <button
                  key={key}
                  onClick={() => {
                    onCameraPresetChange(key as CameraPreset);
                    setShowCameraMenu(false);
                  }}
                  className={`w-full px-4 py-2 text-xs text-left hover:bg-gray-800/80 flex items-center gap-2 ${
                    cameraPreset === key ? 'text-purple-400 bg-purple-500/10' : 'text-gray-300'
                  }`}
                >
                  {value.name}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {selectedObjectId && onXrayModeChange && (
        <button
          onClick={() => onXrayModeChange(!xrayMode)}
          className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
            xrayMode
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
              : 'bg-gray-800/50 text-gray-400 border border-gray-700/30 hover:bg-gray-800/70'
          }`}
          title="X-Ray Selected"
        >
          <Target className="w-3.5 h-3.5" />
          <span>X-Ray</span>
        </button>
      )}

      {onToggleStats && (
        <button
          onClick={onToggleStats}
          className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-all ${
            showStats
              ? 'bg-green-500/20 text-green-300 border border-green-500/30'
              : 'bg-gray-800/50 text-gray-500 border border-gray-700/30 hover:bg-gray-800/70'
          }`}
          title="Toggle Stats"
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Stats</span>
        </button>
      )}

      {showStats && stats && (
        <div className="ml-auto flex items-center gap-4 px-3 py-1.5 bg-gray-900/90 backdrop-blur-sm rounded text-xs font-mono">
          <div>
            <span className="text-gray-500">FPS</span>
            <span className={`ml-1 ${stats.fps >= 50 ? 'text-green-400' : stats.fps >= 30 ? 'text-yellow-400' : 'text-red-400'}`}>
              {stats.fps || '60'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Tris</span>
            <span className="ml-1 text-cyan-400">{(stats.triangles || 2500).toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-500">Calls</span>
            <span className="ml-1 text-purple-400">{stats.calls || 15}</span>
          </div>
        </div>
      )}

      {guidePlanes && (
        <RulerManagementDropdown
          guidePlanes={guidePlanes}
          onDeleteGuidePlane={onDeleteGuidePlane}
          onClearAllGuides={onClearAllGuides}
          onHighlightGuidePlane={onHighlightGuidePlane}
        />
      )}
    </div>
  );
}

