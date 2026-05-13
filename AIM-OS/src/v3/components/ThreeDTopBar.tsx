import { useState } from 'react';
import { 
  Undo2, 
  Redo2, 
  Clock,
  Magnet,
  SplitSquareHorizontal,
  Box,
  Grid3x3,
  Stamp,
  Flame,
  Spline,
  Sun,
  Moon,
  Eye,
  Palette,
  Circle,
  ChevronDown,
  Zap,
  Sparkles,
  Star,
  Copy,
  Trash2,
} from 'lucide-react';

interface ThreeDTopBarProps {
  // Undo/Redo
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onHistory: () => void;
  
  // Tools
  quickSnapEnabled?: boolean;
  onQuickSnapToggle?: () => void;
  splitViewMode?: string;
  onSplitViewToggle?: () => void;
  onDualViewToggle?: () => void;
  crossCanvasEnabled?: boolean;
  onCrossCanvasToggle?: () => void;
  effectsEnabled?: boolean;
  onEffectsToggle?: () => void;
  pathAnimationEnabled?: boolean;
  onPathAnimationToggle?: () => void;
  
  // Render controls
  lightingMode?: 'day' | 'night';
  onLightingToggle?: () => void;
  renderMode?: string;
  onRenderModeChange?: (mode: string) => void;
  renderQuality?: string;
  onRenderQualityChange?: (quality: string) => void;
  
  // Selection actions
  hasSelection: boolean;
  onDelete?: () => void;
  onDuplicate?: () => void;
  onCopy?: () => void;
  onPaste?: () => void;
}

export function ThreeDTopBar({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  onHistory,
  quickSnapEnabled = false,
  onQuickSnapToggle,
  splitViewMode = 'single',
  onSplitViewToggle,
  onDualViewToggle,
  crossCanvasEnabled = false,
  onCrossCanvasToggle,
  effectsEnabled = false,
  onEffectsToggle,
  pathAnimationEnabled = false,
  onPathAnimationToggle,
  lightingMode = 'night',
  onLightingToggle,
  renderMode = 'solid',
  onRenderModeChange,
  renderQuality = 'standard',
  onRenderQualityChange,
  hasSelection,
  onDelete,
  onDuplicate,
  onCopy,
  onPaste,
}: ThreeDTopBarProps) {
  const [showRenderMenu, setShowRenderMenu] = useState(false);
  const [showQualityMenu, setShowQualityMenu] = useState(false);
  
  return (
    <div className="h-14 bg-[#1a1a1a] border-b border-gray-800 flex items-center justify-between px-4 flex-shrink-0">
      <div className="flex items-center gap-1">
        {onQuickSnapToggle && (
          <button 
            onClick={onQuickSnapToggle}
            className={`p-2 rounded transition-colors ${
              quickSnapEnabled
                ? 'bg-purple-600/30 text-purple-400'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
            }`}
            title="Quick Snap (Shift+S)"
          >
            <Magnet className="w-4 h-4" />
          </button>
        )}
        
        {onSplitViewToggle && (
          <div className="relative group">
            <button 
              className={`p-2 rounded transition-colors flex items-center gap-0.5 ${
                splitViewMode !== 'single'
                  ? 'bg-blue-500/20 text-blue-400'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
              title="Split View Options"
            >
              <SplitSquareHorizontal className="w-4 h-4" />
              <ChevronDown className="w-3 h-3" />
            </button>
            
            <div className="absolute top-full mt-1 right-0 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 min-w-[180px] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto">
              <div className="px-3 py-1.5 text-[10px] text-gray-500 uppercase tracking-wider border-b border-gray-700">
                View Layout
              </div>
              <button
                onClick={onSplitViewToggle}
                className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-800 transition-colors flex items-center gap-2 ${
                  splitViewMode === 'single' ? 'text-purple-400 bg-purple-500/10' : 'text-gray-300'
                }`}
              >
                <Box className="w-3.5 h-3.5" />
                <span>Single 3D View</span>
                {splitViewMode === 'single' && <span className="ml-auto">✓</span>}
              </button>
              <button
                onClick={onSplitViewToggle}
                className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-800 transition-colors flex items-center gap-2 ${
                  splitViewMode === 'side-by-side' ? 'text-blue-400 bg-blue-500/10' : 'text-gray-300'
                }`}
              >
                <SplitSquareHorizontal className="w-3.5 h-3.5" />
                <span>2D/3D Split</span>
                {splitViewMode === 'side-by-side' && <span className="ml-auto">✓</span>}
              </button>
              {onDualViewToggle && (
                <button
                  onClick={onDualViewToggle}
                  className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-800 transition-colors flex items-center gap-2 ${
                    splitViewMode === 'dual-3d' ? 'text-pink-400 bg-pink-500/10' : 'text-gray-300'
                  }`}
                >
                  <Grid3x3 className="w-3.5 h-3.5" />
                  <span>Dual 3D (Persp + Ortho)</span>
                  {splitViewMode === 'dual-3d' && <span className="ml-auto">✓</span>}
                </button>
              )}
            </div>
          </div>
        )}
        
        {onCrossCanvasToggle && (
          <button 
            onClick={onCrossCanvasToggle}
            className={`p-2 rounded transition-colors ${
              crossCanvasEnabled
                ? 'bg-green-500/20 text-green-400'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
            }`}
            title="Cross-Canvas Paint"
          >
            <Stamp className="w-4 h-4" />
          </button>
        )}
        
        <div className="h-8 w-px bg-gray-800" />
        
        {onEffectsToggle && (
          <button 
            onClick={onEffectsToggle}
            className={`p-2 rounded transition-colors ${
              effectsEnabled
                ? 'bg-amber-500/20 text-amber-400'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
            }`}
            title="Effects Library"
          >
            <Flame className="w-4 h-4" />
          </button>
        )}
        
        {onPathAnimationToggle && (
          <button 
            onClick={onPathAnimationToggle}
            className={`p-2 rounded transition-colors ${
              pathAnimationEnabled
                ? 'bg-purple-500/20 text-purple-400'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
            }`}
            title="Path Animation (P)"
          >
            <Spline className="w-4 h-4" />
          </button>
        )}
        
        <div className="h-8 w-px bg-gray-800" />
        
        {onLightingToggle && (
          <button 
            onClick={onLightingToggle}
            className={`p-2 rounded transition-colors ${
              lightingMode === 'day'
                ? 'bg-yellow-500/20 text-yellow-400'
                : 'bg-indigo-500/20 text-indigo-400'
            }`}
            title={lightingMode === 'day' ? 'Switch to Night' : 'Switch to Day'}
          >
            {lightingMode === 'day' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        )}
        
        {onRenderModeChange && (
          <div className="relative">
            <button 
              onClick={() => {
                setShowRenderMenu(!showRenderMenu);
                setShowQualityMenu(false);
              }}
              className={`p-2 rounded transition-colors flex items-center gap-0.5 ${
                renderMode !== 'solid'
                  ? 'bg-purple-600/30 text-purple-400'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
              title={`Render Mode: ${renderMode.charAt(0).toUpperCase() + renderMode.slice(1)}`}
            >
              {renderMode === 'solid' && <Box className="w-4 h-4" />}
              {renderMode === 'wireframe' && <Grid3x3 className="w-4 h-4" />}
              {renderMode === 'xray' && <Eye className="w-4 h-4" />}
              {renderMode === 'points' && <Circle className="w-4 h-4" />}
              {renderMode === 'flat' && <Box className="w-4 h-4" />}
              {renderMode === 'normal' && <Palette className="w-4 h-4" />}
              <ChevronDown className="w-3 h-3" />
            </button>
            
            {showRenderMenu && (
              <div className="absolute top-full mt-1 right-0 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 min-w-[140px]">
                <div className="px-3 py-1.5 text-[10px] text-gray-500 uppercase tracking-wider border-b border-gray-700">
                  Render Mode
                </div>
                {[
                  { value: 'solid', label: 'Solid', icon: <Box className="w-3.5 h-3.5" /> },
                  { value: 'wireframe', label: 'Wireframe', icon: <Grid3x3 className="w-3.5 h-3.5" /> },
                  { value: 'xray', label: 'X-Ray', icon: <Eye className="w-3.5 h-3.5" /> },
                  { value: 'points', label: 'Points', icon: <Circle className="w-3.5 h-3.5" /> },
                  { value: 'flat', label: 'Flat', icon: <Box className="w-3.5 h-3.5" /> },
                  { value: 'normal', label: 'Normals', icon: <Palette className="w-3.5 h-3.5" /> },
                ].map((mode) => (
                  <button
                    key={mode.value}
                    onClick={() => {
                      onRenderModeChange(mode.value);
                      setShowRenderMenu(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-800 transition-colors flex items-center gap-2 ${
                      renderMode === mode.value ? 'text-purple-400 bg-purple-500/10' : 'text-gray-300'
                    }`}
                  >
                    {mode.icon}
                    <span>{mode.label}</span>
                    {renderMode === mode.value && <span className="ml-auto">✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        
        {onRenderQualityChange && (
          <div className="relative">
            <button 
              onClick={() => {
                setShowQualityMenu(!showQualityMenu);
                setShowRenderMenu(false);
              }}
              className={`p-2 rounded transition-colors flex items-center gap-0.5 ${
                renderQuality !== 'standard'
                  ? 'bg-amber-600/30 text-amber-400'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
              title={`Quality: ${renderQuality.charAt(0).toUpperCase() + renderQuality.slice(1)}`}
            >
              {renderQuality === 'draft' && <Zap className="w-4 h-4" />}
              {renderQuality === 'standard' && <Box className="w-4 h-4" />}
              {renderQuality === 'high' && <Sparkles className="w-4 h-4" />}
              {renderQuality === 'ultra' && <Star className="w-4 h-4" />}
              <ChevronDown className="w-3 h-3" />
            </button>
            
            {showQualityMenu && (
              <div className="absolute top-full mt-1 right-0 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 min-w-[140px]">
                <div className="px-3 py-1.5 text-[10px] text-gray-500 uppercase tracking-wider border-b border-gray-700">
                  Render Quality
                </div>
                {[
                  { value: 'draft', label: 'Draft', icon: <Zap className="w-3.5 h-3.5" /> },
                  { value: 'standard', label: 'Standard', icon: <Box className="w-3.5 h-3.5" /> },
                  { value: 'high', label: 'High', icon: <Sparkles className="w-3.5 h-3.5" /> },
                  { value: 'ultra', label: 'Ultra', icon: <Star className="w-3.5 h-3.5" /> },
                ].map((quality) => (
                  <button
                    key={quality.value}
                    onClick={() => {
                      onRenderQualityChange(quality.value);
                      setShowQualityMenu(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-800 transition-colors flex items-center gap-2 ${
                      renderQuality === quality.value ? 'text-amber-400 bg-amber-500/10' : 'text-gray-300'
                    }`}
                  >
                    {quality.icon}
                    <span>{quality.label}</span>
                    {renderQuality === quality.value && <span className="ml-auto">✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="h-8 w-px bg-gray-800" />

      <div className="flex items-center gap-1">
        <button onClick={onUndo} disabled={!canUndo} className="p-2 hover:bg-gray-800 rounded transition-colors disabled:opacity-50" title="Undo">
          <Undo2 className="w-4 h-4 text-gray-400" />
        </button>
        <button onClick={onRedo} disabled={!canRedo} className="p-2 hover:bg-gray-800 rounded transition-colors disabled:opacity-50" title="Redo">
          <Redo2 className="w-4 h-4 text-gray-400" />
        </button>
        <button onClick={onHistory} className="p-2 hover:bg-gray-800 rounded transition-colors" title="History">
          <Clock className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {hasSelection && (
        <>
          <div className="h-8 w-px bg-gray-800" />
          <div className="flex items-center gap-1">
            {onCopy && (
              <button onClick={onCopy} className="p-2 hover:bg-gray-800 rounded transition-colors" title="Copy">
                <Copy className="w-4 h-4 text-gray-400" />
              </button>
            )}
            {onPaste && (
              <button onClick={onPaste} className="p-2 hover:bg-gray-800 rounded transition-colors" title="Paste">
                <Copy className="w-4 h-4 text-gray-400 rotate-180" />
              </button>
            )}
            {onDuplicate && (
              <button onClick={onDuplicate} className="p-2 hover:bg-gray-800 rounded transition-colors" title="Duplicate">
                <Copy className="w-4 h-4 text-gray-400" />
              </button>
            )}
            {onDelete && (
              <button onClick={onDelete} className="p-2 hover:bg-gray-800 rounded transition-colors text-red-400 hover:text-red-300" title="Delete">
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}

