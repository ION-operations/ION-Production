import { useState, createContext, useContext, ReactNode } from 'react';
import { X, Maximize2, Minimize2 } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export type DrawerHeight = 'full' | 'top-half' | 'bottom-half';
export type DrawerSide = 'left' | 'right';

export interface DrawerState {
  isOpen: boolean;
  height: DrawerHeight;
  drawerId: string | null;
}

export interface DrawerConfig {
  id: string;
  title: string;
  icon: ReactNode;
  content: ReactNode;
  defaultHeight?: DrawerHeight;
  hideHeightControls?: boolean;
}

interface SideDrawerState {
  top: DrawerState;
  bottom: DrawerState;
}

interface DrawerContextValue {
  left: SideDrawerState;
  right: SideDrawerState;
  openDrawer: (side: DrawerSide, id: string, position: 'top' | 'bottom', height?: DrawerHeight) => void;
  closeDrawer: (side: DrawerSide, position: 'top' | 'bottom') => void;
  toggleDrawer: (side: DrawerSide, id: string, position: 'top' | 'bottom', height?: DrawerHeight) => void;
  setDrawerHeight: (side: DrawerSide, position: 'top' | 'bottom', height: DrawerHeight) => void;
  closeAllDrawers: (side: DrawerSide) => void;
}

interface LegacyDrawerContextValue {
  topDrawer: DrawerState;
  bottomDrawer: DrawerState;
  openDrawer: (id: string, position: 'top' | 'bottom', height?: DrawerHeight) => void;
  closeDrawer: (position: 'top' | 'bottom') => void;
  toggleDrawer: (id: string, position: 'top' | 'bottom', height?: DrawerHeight) => void;
  setDrawerHeight: (position: 'top' | 'bottom', height: DrawerHeight) => void;
}

// ============================================================================
// CONTEXT
// ============================================================================

const DrawerContext = createContext<DrawerContextValue | null>(null);

export function useDrawerContext() {
  const context = useContext(DrawerContext);
  if (!context) {
    throw new Error('useDrawerContext must be used within DrawerProvider');
  }
  return context;
}

const SideContext = createContext<DrawerSide>('left');

export function useDrawer(): LegacyDrawerContextValue {
  const context = useContext(DrawerContext);
  const side = useContext(SideContext);
  
  if (!context) {
    throw new Error('useDrawer must be used within DrawerProvider');
  }

  const sideState = side === 'left' ? context.left : context.right;

  return {
    topDrawer: sideState.top,
    bottomDrawer: sideState.bottom,
    openDrawer: (id, position, height) => context.openDrawer(side, id, position, height),
    closeDrawer: (position) => context.closeDrawer(side, position),
    toggleDrawer: (id, position, height) => context.toggleDrawer(side, id, position, height),
    setDrawerHeight: (position, height) => context.setDrawerHeight(side, position, height),
  };
}

// ============================================================================
// DRAWER PROVIDER
// ============================================================================

interface DrawerProviderProps {
  children: ReactNode;
}

const defaultDrawerState: DrawerState = {
  isOpen: false,
  height: 'full',
  drawerId: null,
};

const defaultSideState: SideDrawerState = {
  top: { ...defaultDrawerState },
  bottom: { ...defaultDrawerState },
};

export function DrawerProvider({ children }: DrawerProviderProps) {
  const [left, setLeft] = useState<SideDrawerState>({ ...defaultSideState });
  const [right, setRight] = useState<SideDrawerState>({ ...defaultSideState });

  const getSetter = (side: DrawerSide) => side === 'left' ? setLeft : setRight;
  const getState = (side: DrawerSide) => side === 'left' ? left : right;

  const openDrawer = (side: DrawerSide, id: string, position: 'top' | 'bottom', height: DrawerHeight = 'full') => {
    const setter = getSetter(side);
    const state = getState(side);
    
    setter(prev => {
      const newState = { ...prev };
      
      if (position === 'top') {
        if (height === 'top-half' && prev.bottom.isOpen && prev.bottom.height === 'full') {
          newState.bottom = { ...prev.bottom, height: 'bottom-half' };
        }
        newState.top = { isOpen: true, height, drawerId: id };
      } else {
        if (height === 'bottom-half' && prev.top.isOpen && prev.top.height === 'full') {
          newState.top = { ...prev.top, height: 'top-half' };
        }
        newState.bottom = { isOpen: true, height, drawerId: id };
      }
      
      return newState;
    });
  };

  const closeDrawer = (side: DrawerSide, position: 'top' | 'bottom') => {
    const setter = getSetter(side);
    setter(prev => ({
      ...prev,
      [position]: { isOpen: false, height: 'full', drawerId: null },
    }));
  };

  const toggleDrawer = (side: DrawerSide, id: string, position: 'top' | 'bottom', height: DrawerHeight = 'full') => {
    const state = getState(side);
    const drawer = position === 'top' ? state.top : state.bottom;
    
    if (drawer.isOpen && drawer.drawerId === id) {
      closeDrawer(side, position);
    } else {
      openDrawer(side, id, position, height);
    }
  };

  const setDrawerHeight = (side: DrawerSide, position: 'top' | 'bottom', height: DrawerHeight) => {
    const setter = getSetter(side);
    setter(prev => ({
      ...prev,
      [position]: { ...prev[position], height },
    }));
  };

  const closeAllDrawers = (side: DrawerSide) => {
    const setter = getSetter(side);
    setter({ ...defaultSideState });
  };

  return (
    <DrawerContext.Provider value={{
      left,
      right,
      openDrawer,
      closeDrawer,
      toggleDrawer,
      setDrawerHeight,
      closeAllDrawers,
    }}>
      {children}
    </DrawerContext.Provider>
  );
}

interface SideProviderProps {
  side: DrawerSide;
  children: ReactNode;
}

export function SideProvider({ side, children }: SideProviderProps) {
  return (
    <SideContext.Provider value={side}>
      {children}
    </SideContext.Provider>
  );
}

interface DrawerProps {
  id: string;
  title: string;
  icon?: ReactNode;
  position: 'top' | 'bottom';
  side: DrawerSide;
  children: ReactNode;
  className?: string;
  hideHeightControls?: boolean;
}

export function Drawer({ id, title, icon, position, side, children, className = '', hideHeightControls = false }: DrawerProps) {
  const context = useDrawerContext();
  const sideState = side === 'left' ? context.left : context.right;
  const drawer = position === 'top' ? sideState.top : sideState.bottom;

  if (!drawer.isOpen || drawer.drawerId !== id) {
    return null;
  }

  const getHeightClass = () => {
    if (drawer.height === 'full') return 'h-full';
    if (drawer.height === 'top-half') return 'h-1/2';
    if (drawer.height === 'bottom-half') return 'h-1/2';
    return 'h-full';
  };

  const getPositionClass = () => {
    if (drawer.height === 'top-half') return 'top-0';
    if (drawer.height === 'bottom-half') return 'bottom-0';
    return '';
  };

  return (
    <div 
      className={`
        absolute ${getPositionClass()} left-0 right-0 ${getHeightClass()}
        bg-[#1e1e1e] 
        ${side === 'left' ? 'border-r' : 'border-l'} border-gray-700/50
        flex flex-col
        ${className}
      `}
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700/50 bg-[#1e1e1e]">
        <div className="flex items-center gap-2">
          {icon && <span className="text-gray-400">{icon}</span>}
          <span className="text-sm font-medium text-gray-200">{title}</span>
        </div>
        
        <div className="flex items-center gap-1">
          {!hideHeightControls && (
            <>
              {drawer.height !== 'top-half' && (
                <button
                  onClick={() => context.setDrawerHeight(side, position, 'top-half')}
                  className="p-1 hover:bg-gray-700/50 rounded text-gray-400 hover:text-gray-200"
                  aria-label="Resize to top half"
                >
                  <Minimize2 className="w-3.5 h-3.5 rotate-180" />
                </button>
              )}
              {drawer.height !== 'bottom-half' && (
                <button
                  onClick={() => context.setDrawerHeight(side, position, 'bottom-half')}
                  className="p-1 hover:bg-gray-700/50 rounded text-gray-400 hover:text-gray-200"
                  aria-label="Resize to bottom half"
                >
                  <Minimize2 className="w-3.5 h-3.5" />
                </button>
              )}
              {drawer.height !== 'full' && (
                <button
                  onClick={() => context.setDrawerHeight(side, position, 'full')}
                  className="p-1 hover:bg-gray-700/50 rounded text-gray-400 hover:text-gray-200"
                  aria-label="Resize to full height"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              )}
            </>
          )}
          
          <button
            onClick={() => context.closeDrawer(side, position)}
            className="p-1 hover:bg-gray-700/50 rounded text-gray-400 hover:text-gray-200"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}

interface DrawerContainerProps {
  drawers: DrawerConfig[];
  side: DrawerSide;
  className?: string;
}

export function DrawerContainer({ drawers, side, className = '' }: DrawerContainerProps) {
  const context = useDrawerContext();
  const sideState = side === 'left' ? context.left : context.right;

  const activeTopDrawer = drawers.find(d => d.id === sideState.top.drawerId);
  const activeBottomDrawer = drawers.find(d => d.id === sideState.bottom.drawerId);

  const hasAnyOpen = sideState.top.isOpen || sideState.bottom.isOpen;

  if (!hasAnyOpen) {
    return null;
  }

  return (
    <SideProvider side={side}>
      <div 
        className={`
          relative w-72 bg-[#1e1e1e] 
          ${side === 'left' ? 'border-r' : 'border-l'} border-gray-700/50
          transition-all duration-200
          ${className}
        `}
      >
        {activeTopDrawer && sideState.top.isOpen && (
          <Drawer
            id={activeTopDrawer.id}
            title={activeTopDrawer.title}
            icon={activeTopDrawer.icon}
            position="top"
            side={side}
            hideHeightControls={activeTopDrawer.hideHeightControls}
          >
            {activeTopDrawer.content}
          </Drawer>
        )}

        {activeBottomDrawer && sideState.bottom.isOpen && (
          <Drawer
            id={activeBottomDrawer.id}
            title={activeBottomDrawer.title}
            icon={activeBottomDrawer.icon}
            position="bottom"
            side={side}
            hideHeightControls={activeBottomDrawer.hideHeightControls}
          >
            {activeBottomDrawer.content}
          </Drawer>
        )}
      </div>
    </SideProvider>
  );
}

export type { DrawerConfig };

