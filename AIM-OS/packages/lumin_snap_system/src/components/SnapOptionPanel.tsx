/**
 * Snap Option Panel Component
 * @module @lumin/snap-system/components/SnapOptionPanel
 * 
 * NL_TAG: LUMIN-PANEL-001 | UI panel with snap option buttons | SnapOptionPanel | [GhostPreviewRenderer]
 * NL_TAG_INTENT: LUMIN-UX-003 | Trigger ghost preview on hover, apply snap on click | hover + click handlers | [UX_REQUIREMENTS]
 */

import React, { useState, useCallback, useMemo } from 'react';
import * as THREE from 'three';
import {
  ArrowUp,
  ArrowRight,
  ArrowDown,
  ArrowLeft,
  AlignCenterHorizontal,
  AlignCenterVertical,
  Crosshair,
  Magnet,
  Settings
} from 'lucide-react';
import { SnapEngine } from '../utils/SnapEngine';
import {
  SnapOptionPanelProps,
  SnapOption,
  SnapOptionHoverEvent,
  SnapOptionClickEvent,
  SnapConfig,
  DEFAULT_SNAP_CONFIG
} from '../types';

/**
 * Snap option button configuration
 */
interface SnapButton {
  id: SnapOption;
  label: string;
  description: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  shortcut?: string;
  row: number;
  col: number;
}

/**
 * Snap buttons layout configuration
 */
const SNAP_BUTTONS: SnapButton[] = [
  // Row 1: Top
  {
    id: 'snap_top',
    label: 'Top',
    description: 'Snap to top edge',
    icon: ArrowUp,
    shortcut: 'T',
    row: 0,
    col: 1
  },
  // Row 2: Left, Center, Right
  {
    id: 'snap_left',
    label: 'Left',
    description: 'Snap to left edge',
    icon: ArrowLeft,
    shortcut: 'L',
    row: 1,
    col: 0
  },
  {
    id: 'snap_center_xy',
    label: 'Center',
    description: 'Center both axes',
    icon: Crosshair,
    shortcut: 'C',
    row: 1,
    col: 1
  },
  {
    id: 'snap_right',
    label: 'Right',
    description: 'Snap to right edge',
    icon: ArrowRight,
    shortcut: 'R',
    row: 1,
    col: 2
  },
  // Row 3: Bottom
  {
    id: 'snap_bottom',
    label: 'Bottom',
    description: 'Snap to bottom edge',
    icon: ArrowDown,
    shortcut: 'B',
    row: 2,
    col: 1
  },
  // Row 4: Center X, Center Y
  {
    id: 'snap_center_x',
    label: 'Center X',
    description: 'Center horizontally',
    icon: AlignCenterHorizontal,
    shortcut: 'X',
    row: 3,
    col: 0
  },
  {
    id: 'snap_center_y',
    label: 'Center Y',
    description: 'Center vertically',
    icon: AlignCenterVertical,
    shortcut: 'Y',
    row: 3,
    col: 2
  }
];

/**
 * Snap Option Panel
 * 
 * Provides a UI panel with snap option buttons that trigger ghost preview
 * on hover and apply snap on click.
 * 
 * @example
 * ```tsx
 * <SnapOptionPanel
 *   selectedObject={mesh}
 *   onSnapOptionHover={({ option, targetPosition }) => showGhost(targetPosition)}
 *   onSnapOptionLeave={() => hideGhost()}
 *   onSnapOptionClick={({ option, targetPosition }) => applySnap(targetPosition)}
 * />
 * ```
 */
export const SnapOptionPanel: React.FC<SnapOptionPanelProps> = ({
  selectedObject,
  onSnapOptionHover,
  onSnapOptionLeave,
  onSnapOptionClick,
  config = DEFAULT_SNAP_CONFIG,
  className = '',
  showShortcuts = true
}) => {
  const [hoveredOption, setHoveredOption] = useState<SnapOption | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  
  const snapEngine = useMemo(() => SnapEngine.getInstance(), []);

  // Handle mouse enter on button
  const handleMouseEnter = useCallback((option: SnapOption) => {
    if (!selectedObject) return;
    
    // Calculate target position
    const targetPosition = snapEngine.calculateSnapPosition(selectedObject, option);
    
    setHoveredOption(option);
    onSnapOptionHover({
      option,
      targetPosition,
      originalObject: selectedObject
    });
  }, [selectedObject, snapEngine, onSnapOptionHover]);

  // Handle mouse leave
  const handleMouseLeave = useCallback(() => {
    setHoveredOption(null);
    onSnapOptionLeave();
  }, [onSnapOptionLeave]);

  // Handle click
  const handleClick = useCallback((option: SnapOption) => {
    if (!selectedObject) return;
    
    const targetPosition = snapEngine.calculateSnapPosition(selectedObject, option);
    const previousPosition = selectedObject.position.clone();
    
    onSnapOptionClick({
      option,
      targetPosition,
      originalObject: selectedObject,
      previousPosition
    });
    
    // Clear hover state after click
    setHoveredOption(null);
    onSnapOptionLeave();
  }, [selectedObject, snapEngine, onSnapOptionClick, onSnapOptionLeave]);

  // Keyboard shortcuts
  React.useEffect(() => {
    if (!selectedObject || !showShortcuts) return;
    
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if modifier keys are pressed
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      
      const key = e.key.toUpperCase();
      const button = SNAP_BUTTONS.find(b => b.shortcut === key);
      
      if (button) {
        e.preventDefault();
        handleClick(button.id);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedObject, showShortcuts, handleClick]);

  // Group buttons by row for layout
  const buttonRows = useMemo(() => {
    const rows: SnapButton[][] = [[], [], [], []];
    SNAP_BUTTONS.forEach(button => {
      rows[button.row].push(button);
    });
    return rows;
  }, []);

  // Disabled state when no object selected
  const isDisabled = !selectedObject;

  return (
    <div 
      className={`
        snap-option-panel
        bg-gray-800/95 backdrop-blur-sm
        rounded-xl shadow-2xl
        border border-gray-700/50
        overflow-hidden
        ${isDisabled ? 'opacity-50 pointer-events-none' : ''}
        ${className}
      `}
    >
      {/* Header */}
      <div 
        className="
          flex items-center justify-between
          px-4 py-3
          bg-gradient-to-r from-gray-800 to-gray-700
          border-b border-gray-700/50
          cursor-pointer
        "
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <div className="
            w-8 h-8
            bg-gradient-to-r from-cyan-500 to-blue-500
            rounded-lg
            flex items-center justify-center
            shadow-lg
          ">
            <Magnet size={16} className="text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Snap Options</h3>
            <p className="text-xs text-gray-400">
              {selectedObject ? 'Hover to preview' : 'Select an object'}
            </p>
          </div>
        </div>
        <Settings 
          size={16} 
          className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
        />
      </div>

      {/* Button Grid */}
      {isExpanded && (
        <div className="p-4 space-y-2">
          {buttonRows.map((row, rowIndex) => (
            <div 
              key={`row-${rowIndex}`}
              className="flex justify-center gap-2"
            >
              {row.map(button => (
                <SnapButton
                  key={button.id}
                  button={button}
                  isHovered={hoveredOption === button.id}
                  isDisabled={isDisabled}
                  showShortcut={showShortcuts}
                  onMouseEnter={() => handleMouseEnter(button.id)}
                  onMouseLeave={handleMouseLeave}
                  onClick={() => handleClick(button.id)}
                />
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Ghost preview indicator */}
      {hoveredOption && (
        <div className="
          px-4 py-2
          bg-cyan-500/10
          border-t border-cyan-500/20
        ">
          <p className="text-xs text-cyan-400 flex items-center gap-2">
            <span className="animate-pulse">👻</span>
            Ghost preview active - Click to snap!
          </p>
        </div>
      )}
    </div>
  );
};

/**
 * Individual snap button component
 */
interface SnapButtonProps {
  button: SnapButton;
  isHovered: boolean;
  isDisabled: boolean;
  showShortcut: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  onClick: () => void;
}

const SnapButton: React.FC<SnapButtonProps> = ({
  button,
  isHovered,
  isDisabled,
  showShortcut,
  onMouseEnter,
  onMouseLeave,
  onClick
}) => {
  const Icon = button.icon;
  
  return (
    <button
      className={`
        relative
        w-16 h-16
        rounded-xl
        transition-all duration-200
        flex flex-col items-center justify-center
        group
        ${isHovered 
          ? 'bg-cyan-500 scale-110 shadow-lg shadow-cyan-500/30' 
          : 'bg-gray-700/50 hover:bg-gray-600/50'
        }
        ${isDisabled ? 'cursor-not-allowed' : 'cursor-pointer'}
      `}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
      disabled={isDisabled}
      title={`${button.description}${showShortcut && button.shortcut ? ` (${button.shortcut})` : ''}`}
    >
      <Icon 
        size={20} 
        className={`
          transition-colors
          ${isHovered ? 'text-white' : 'text-gray-300 group-hover:text-white'}
        `}
      />
      <span className={`
        mt-1 text-xs font-medium
        transition-colors
        ${isHovered ? 'text-white' : 'text-gray-400 group-hover:text-gray-200'}
      `}>
        {button.label}
      </span>
      
      {/* Shortcut badge */}
      {showShortcut && button.shortcut && (
        <span className="
          absolute top-1 right-1
          w-4 h-4
          bg-gray-600
          rounded
          text-[10px] font-mono
          flex items-center justify-center
          text-gray-400
          group-hover:bg-gray-500 group-hover:text-gray-200
        ">
          {button.shortcut}
        </span>
      )}
    </button>
  );
};

export default SnapOptionPanel;

