import { ReactNode, useState } from 'react';
import { useDrawerContext, type DrawerHeight, type DrawerSide } from './DrawerContainer';
import { Maximize2, ChevronsUp, ChevronsDown } from 'lucide-react';

interface IconButtonConfig {
  id: string;
  icon: ReactNode;
  label: string;
  drawerPosition?: 'top' | 'bottom';
  defaultHeight?: DrawerHeight;
  onClick?: () => void;
  type?: 'tool' | 'drawer' | 'custom';
}

interface IconBarProps {
  topButtons: IconButtonConfig[];
  bottomButtons: IconButtonConfig[];
  side: DrawerSide;
  className?: string;
  activeToolId?: string;
}

interface SplitHoverButtonProps {
  config: IconButtonConfig;
  side: DrawerSide;
  isActive: boolean;
  onFullClick: () => void;
  onTopHalfClick: () => void;
  onBottomHalfClick: () => void;
}

function SplitHoverButton({ 
  config, 
  side,
  isActive, 
  onFullClick, 
  onTopHalfClick, 
  onBottomHalfClick 
}: SplitHoverButtonProps) {
  const [isHovered, setIsHovered] = useState(false);
  const hasDrawer = !!config.drawerPosition;

  const baseButton = (
    <button
      onClick={hasDrawer ? onFullClick : config.onClick}
      className={`
        w-full h-full flex items-center justify-center rounded-lg
        transition-all duration-150
        ${isActive 
          ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20' 
          : 'text-gray-400 hover:bg-gray-700/50 hover:text-gray-200'
        }
        ${isHovered && hasDrawer ? 'opacity-0' : 'opacity-100'}
      `}
      aria-label={config.label}
      title={config.label}
    >
      {config.icon}
    </button>
  );

  return (
    <div 
      className="relative w-10 h-10"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {baseButton}

      {hasDrawer && isHovered && (
        <div className="absolute inset-0 flex rounded-lg overflow-hidden border border-gray-600 bg-[#252525] shadow-lg z-10">
          <button
            onClick={onFullClick}
            className={`
              flex-1 flex items-center justify-center
              border-r border-gray-600
              transition-colors
              ${isActive ? 'bg-purple-600/80 text-white' : 'hover:bg-purple-600/50 text-gray-300'}
            `}
            title={`${config.label} - Full Size`}
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>

          <div className="flex-1 flex flex-col">
            <button
              onClick={onTopHalfClick}
              className="flex-1 flex items-center justify-center hover:bg-gray-600/50 transition-colors border-b border-gray-600"
              title={`${config.label} - Top Half`}
            >
              <ChevronsUp className="w-3 h-3 text-gray-400" />
            </button>
            <button
              onClick={onBottomHalfClick}
              className="flex-1 flex items-center justify-center hover:bg-gray-600/50 transition-colors"
              title={`${config.label} - Bottom Half`}
            >
              <ChevronsDown className="w-3 h-3 text-gray-400" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

interface SimpleIconButtonProps {
  config: IconButtonConfig;
  isActive: boolean;
  onClick: () => void;
}

function SimpleIconButton({ config, isActive, onClick }: SimpleIconButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        w-10 h-10 flex items-center justify-center rounded-lg
        transition-all duration-150
        ${isActive 
          ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20' 
          : 'text-gray-400 hover:bg-gray-700/50 hover:text-gray-200'
        }
      `}
      aria-label={config.label}
      title={config.label}
    >
      {config.icon}
    </button>
  );
}

export function IconBar({ topButtons, bottomButtons, side, className = '', activeToolId }: IconBarProps) {
  const context = useDrawerContext();
  const sideState = side === 'left' ? context.left : context.right;

  const handleFullClick = (config: IconButtonConfig) => {
    if (config.drawerPosition) {
      context.toggleDrawer(side, config.id, config.drawerPosition, 'full');
    } else if (config.onClick) {
      config.onClick();
    }
  };

  const handleTopHalfClick = (config: IconButtonConfig) => {
    if (config.drawerPosition) {
      context.openDrawer(side, config.id, 'top', 'top-half');
    }
  };

  const handleBottomHalfClick = (config: IconButtonConfig) => {
    if (config.drawerPosition) {
      context.openDrawer(side, config.id, 'bottom', 'bottom-half');
    }
  };

  const isButtonActive = (config: IconButtonConfig) => {
    if (config.type === 'tool' && activeToolId) {
      return config.id === activeToolId;
    }
    
    return (sideState.top.isOpen && sideState.top.drawerId === config.id) ||
           (sideState.bottom.isOpen && sideState.bottom.drawerId === config.id);
  };

  const renderButton = (config: IconButtonConfig) => {
    if (config.drawerPosition) {
      return (
        <SplitHoverButton
          key={config.id}
          config={config}
          side={side}
          isActive={isButtonActive(config)}
          onFullClick={() => handleFullClick(config)}
          onTopHalfClick={() => handleTopHalfClick(config)}
          onBottomHalfClick={() => handleBottomHalfClick(config)}
        />
      );
    }
    return (
      <SimpleIconButton
        key={config.id}
        config={config}
        isActive={isButtonActive(config)}
        onClick={() => config.onClick?.()}
      />
    );
  };

  return (
    <div 
      className={`
        w-12 bg-[#1a1a1a] 
        ${side === 'left' ? 'border-r' : 'border-l'} border-gray-700/50
        flex flex-col justify-between py-2
        relative z-40
        ${className}
      `}
    >
      <div className="flex flex-col items-center gap-1 px-1">
        {topButtons.map(renderButton)}
      </div>

      <div className="flex flex-col items-center gap-1 px-1">
        {bottomButtons.map(renderButton)}
      </div>
    </div>
  );
}

