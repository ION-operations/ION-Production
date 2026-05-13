import React, { useEffect } from 'react';
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels';
import { usePanelStore } from '../../store/panelStore';
import { usePanelInitialization } from '../../hooks/usePanelRegistry';
import { Zone as ZoneComponent } from '../Zone/Zone';
import { TopBar } from '../TopBar/TopBar';
import { ErrorBoundary } from '../ErrorBoundary/ErrorBoundary';
import './Layout.css';

export const Layout: React.FC = () => {
  const { zones, panels, currentLayout, resetLayout } = usePanelStore();
  
  // Initialize panels from registry
  usePanelInitialization();

  useEffect(() => {
    if (!currentLayout) {
      resetLayout();
    }
  }, [currentLayout, resetLayout]);

  // 5-Zone Layout: Top Bar, Left Drawer, Main Content, Right Drawer, Bottom Drawer
  const topZone = zones.find((z) => z.type === 'top');
  const leftZone = zones.find((z) => z.type === 'left');
  const rightZone = zones.find((z) => z.type === 'right');
  const bottomZone = zones.find((z) => z.type === 'bottom');
  const centerZone = zones.find((z) => z.type === 'center');

  const leftPanels = panels.filter((p) => p.zone === 'left' && p.visible).sort((a, b) => a.order - b.order);
  const rightPanels = panels.filter((p) => p.zone === 'right' && p.visible).sort((a, b) => a.order - b.order);
  const bottomPanels = panels.filter((p) => p.zone === 'bottom' && p.visible).sort((a, b) => a.order - b.order);

  return (
    <ErrorBoundary>
      <div className="layout" role="main">
        {/* Top Bar Zone */}
        <div className="top-zone">
          <TopBar />
        </div>

        {/* Main Content Area (Left, Center, Right, Bottom) */}
        <PanelGroup direction="vertical" className="layout-vertical">
          <Panel defaultSize={100} minSize={50}>
            <PanelGroup direction="horizontal" className="layout-horizontal">
              {/* Left Drawer Zone */}
              {leftZone && leftZone.visible && (
                <>
                  <Panel
                    defaultSize={leftZone.size}
                    minSize={leftZone.minSize}
                    maxSize={leftZone.maxSize}
                    collapsible={leftZone.collapsible}
                    className="zone-panel left-zone"
                  >
                    <ZoneComponent zone={leftZone} panels={leftPanels} />
                  </Panel>
                  <PanelResizeHandle className="resize-handle" />
                </>
              )}

              {/* Center Zone (Main Content) */}
              <Panel defaultSize={50} minSize={30} className="zone-panel center-zone">
                <div className="center-content">
                  <div className="center-header">
                    <h2>Code Editor</h2>
                    <div className="center-tabs">
                      <div className="tab active">Button.tsx</div>
                      <div className="tab">Input.tsx</div>
                    </div>
                  </div>
                  <div className="editor-placeholder">
                    <pre>{`import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={\`btn btn-\${variant}\`}
    >
      {label}
    </button>
  );
};`}</pre>
                  </div>
                </div>
              </Panel>

              {/* Right Drawer Zone */}
              {rightZone && rightZone.visible && (
                <>
                  <PanelResizeHandle className="resize-handle" />
                  <Panel
                    defaultSize={rightZone.size}
                    minSize={rightZone.minSize}
                    maxSize={rightZone.maxSize}
                    collapsible={rightZone.collapsible}
                    className="zone-panel right-zone"
                  >
                    <ZoneComponent zone={rightZone} panels={rightPanels} />
                  </Panel>
                </>
              )}
            </PanelGroup>
          </Panel>

          {/* Bottom Drawer Zone */}
          {bottomZone && bottomZone.visible && (
            <>
              <PanelResizeHandle className="resize-handle horizontal" />
              <Panel
                defaultSize={bottomZone.size}
                minSize={bottomZone.minSize}
                maxSize={bottomZone.maxSize}
                collapsible={bottomZone.collapsible}
                className="zone-panel bottom-zone"
              >
                <ZoneComponent zone={bottomZone} panels={bottomPanels} />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </ErrorBoundary>
  );
};

