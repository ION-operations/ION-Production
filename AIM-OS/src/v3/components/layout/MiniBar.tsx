import { ReactNode } from 'react';
import { Eye, EyeOff, Lock, Unlock } from 'lucide-react';

export interface MiniBarItem {
  id: string;
  name: string;
  thumbnailUrl?: string;
  thumbnailElement?: ReactNode;
  visible?: boolean;
  locked?: boolean;
  status?: 'draft' | 'in-progress' | 'complete';
}

export type MiniBarType = 
  | 'layers' 
  | 'characters' 
  | 'panels' 
  | 'clips' 
  | 'tracks' 
  | 'shots';

interface MiniBarProps {
  type: MiniBarType;
  items: MiniBarItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onVisibilityToggle?: (id: string) => void;
  onLockToggle?: (id: string) => void;
  onReorder?: (fromIndex: number, toIndex: number) => void;
  className?: string;
}

interface MiniBarItemProps {
  item: MiniBarItem;
  isSelected: boolean;
  showVisibility?: boolean;
  showLock?: boolean;
  onClick: () => void;
  onVisibilityToggle?: () => void;
  onLockToggle?: () => void;
}

function MiniBarItemComponent({
  item,
  isSelected,
  showVisibility,
  showLock,
  onClick,
  onVisibilityToggle,
  onLockToggle,
}: MiniBarItemProps) {
  const getStatusColor = () => {
    switch (item.status) {
      case 'complete': return 'border-green-500';
      case 'in-progress': return 'border-yellow-500';
      case 'draft': return 'border-gray-500';
      default: return 'border-gray-600';
    }
  };

  return (
    <div 
      className={`
        group relative w-full
        ${isSelected ? 'bg-purple-600/20' : 'hover:bg-gray-700/30'}
        transition-colors duration-150
      `}
    >
      {isSelected && (
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-purple-500" />
      )}

      <button
        onClick={onClick}
        className={`
          w-full aspect-square p-1
          flex items-center justify-center
        `}
      >
        {item.thumbnailUrl ? (
          <img
            src={item.thumbnailUrl}
            alt={item.name}
            className={`
              w-full h-full object-cover rounded
              border-2 ${getStatusColor()}
            `}
          />
        ) : item.thumbnailElement ? (
          <div className={`w-full h-full rounded border-2 ${getStatusColor()} overflow-hidden`}>
            {item.thumbnailElement}
          </div>
        ) : (
          <div 
            className={`
              w-full h-full rounded bg-gray-700
              border-2 ${getStatusColor()}
              flex items-center justify-center
              text-xs text-gray-400 font-medium
            `}
          >
            {item.name.charAt(0).toUpperCase()}
          </div>
        )}
      </button>

      <div className="absolute inset-x-0 bottom-0 opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-t from-black/80 to-transparent p-1">
        <div className="flex justify-center gap-0.5">
          {showVisibility && onVisibilityToggle && (
            <button
              onClick={(e) => { e.stopPropagation(); onVisibilityToggle(); }}
              className="p-0.5 hover:bg-white/10 rounded"
              title={item.visible ? 'Hide' : 'Show'}
            >
              {item.visible !== false ? (
                <Eye className="w-3 h-3 text-white" />
              ) : (
                <EyeOff className="w-3 h-3 text-gray-400" />
              )}
            </button>
          )}
          {showLock && onLockToggle && (
            <button
              onClick={(e) => { e.stopPropagation(); onLockToggle(); }}
              className="p-0.5 hover:bg-white/10 rounded"
              title={item.locked ? 'Unlock' : 'Lock'}
            >
              {item.locked ? (
                <Lock className="w-3 h-3 text-yellow-400" />
              ) : (
                <Unlock className="w-3 h-3 text-white" />
              )}
            </button>
          )}
        </div>
      </div>

      <div className="absolute left-full ml-2 top-1/2 -translate-y-1/2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-50">
        <div className="bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap shadow-lg">
          {item.name}
        </div>
      </div>
    </div>
  );
}

export function MiniBar({
  type,
  items,
  selectedId,
  onSelect,
  onVisibilityToggle,
  onLockToggle,
  onReorder,
  className = '',
}: MiniBarProps) {
  const showVisibility = type === 'layers';
  const showLock = type === 'layers';

  const getTypeLabel = () => {
    switch (type) {
      case 'layers': return 'Layers';
      case 'characters': return 'Characters';
      case 'panels': return 'Panels';
      case 'clips': return 'Clips';
      case 'tracks': return 'Tracks';
      case 'shots': return 'Shots';
      default: return 'Items';
    }
  };

  return (
    <div 
      className={`
        w-12 bg-[#1a1a1a] border-r border-gray-700/50
        flex flex-col
        ${className}
      `}
    >
      <div className="py-2 text-center border-b border-gray-700/50">
        <span className="text-[10px] font-medium text-gray-500 uppercase tracking-wider">
          {getTypeLabel()}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden py-1">
        {items.map((item) => (
          <MiniBarItemComponent
            key={item.id}
            item={item}
            isSelected={item.id === selectedId}
            showVisibility={showVisibility}
            showLock={showLock}
            onClick={() => onSelect(item.id)}
            onVisibilityToggle={onVisibilityToggle ? () => onVisibilityToggle(item.id) : undefined}
            onLockToggle={onLockToggle ? () => onLockToggle(item.id) : undefined}
          />
        ))}
      </div>

      <div className="py-1 text-center border-t border-gray-700/50">
        <span className="text-[10px] text-gray-500">
          {items.length}
        </span>
      </div>
    </div>
  );
}

