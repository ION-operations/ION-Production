/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — App Shell
   Main layout grid with tabbed left drawer (Layers / Templates / SVG Builder)
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState } from 'react';
import { useEditorStore } from './store/editorStore';
import TopBar from './shell/TopBar';
import LayerTree from './panels/LayerTree';
import TemplateLibrary from './panels/TemplateLibrary';
import SvgIconBuilder from './panels/SvgIconBuilder';
import LogoStudio from './panels/LogoStudio';
import Canvas from './canvas/Canvas';
import PropertiesPanel from './panels/PropertiesPanel';
import BottomPanel from './shell/BottomBar';
import { IconLayers, IconTemplates, IconSvgBuilder, IconLogoStudio } from './icons/Icons';

type LeftDrawerTab = 'layers' | 'templates' | 'icons' | 'logos';

const DRAWER_TABS: { key: LeftDrawerTab; label: string; Icon: React.FC<{ size?: number }> }[] = [
    { key: 'layers', label: 'Layers', Icon: IconLayers },
    { key: 'templates', label: 'Templates', Icon: IconTemplates },
    { key: 'icons', label: 'Icons', Icon: IconSvgBuilder },
    { key: 'logos', label: 'Logos', Icon: IconLogoStudio },
];

export default function App() {
    const bottomOpen = useEditorStore((s) => s.bottomPanelOpen);
    const leftOpen = useEditorStore((s) => s.leftPanelOpen);
    const rightOpen = useEditorStore((s) => s.rightPanelOpen);
    const [leftTab, setLeftTab] = useState<LeftDrawerTab>('layers');

    const style: React.CSSProperties = {
        gridTemplateColumns: `${leftOpen ? 'var(--ob-left-panel-w)' : '0px'} 1fr ${rightOpen ? 'var(--ob-right-panel-w)' : '0px'}`,
    };

    return (
        <div className={`ob-shell${bottomOpen ? ' bottom-open' : ''}`} style={style}>
            <TopBar />

            {leftOpen && (
                <div className="ob-left-drawer">
                    {/* Drawer tabs */}
                    <div className="ob-drawer-tabs">
                        {DRAWER_TABS.map(({ key, label, Icon }) => (
                            <button
                                key={key}
                                className={`ob-drawer-tab${leftTab === key ? ' active' : ''}`}
                                onClick={() => setLeftTab(key)}
                            >
                                <Icon size={14} />
                                {label}
                            </button>
                        ))}
                    </div>

                    {/* Drawer content */}
                    <div className="ob-drawer-content">
                        {leftTab === 'layers' && <LayerTree />}
                        {leftTab === 'templates' && <TemplateLibrary />}
                        {leftTab === 'icons' && <SvgIconBuilder />}
                        {leftTab === 'logos' && <LogoStudio />}
                    </div>
                </div>
            )}

            <Canvas />
            {rightOpen && <PropertiesPanel />}
            {bottomOpen && <BottomPanel />}
        </div>
    );
}
