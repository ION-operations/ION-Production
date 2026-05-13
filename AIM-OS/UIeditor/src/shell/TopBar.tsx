/* OmniBuilder — Top Bar (Custom SVG Icons) */
import { useEditorStore } from '../store/editorStore';
import type { ToolMode, Breakpoint, SimulatedState } from '../types';
import {
    IconSelect, IconMove, IconResize, IconStyle, IconAnimate, IconInspect,
    IconDesktop, IconTablet, IconMobile, IconLogo, IconPanelToggle,
} from '../icons/Icons';

const TOOLS: { mode: ToolMode; label: string; Icon: React.FC<{ size?: number }> }[] = [
    { mode: 'select', label: 'Select', Icon: IconSelect },
    { mode: 'move', label: 'Move', Icon: IconMove },
    { mode: 'resize', label: 'Resize', Icon: IconResize },
    { mode: 'style', label: 'Style', Icon: IconStyle },
    { mode: 'animate', label: 'Animate', Icon: IconAnimate },
    { mode: 'inspect', label: 'Inspect', Icon: IconInspect },
];

const BREAKPOINTS: { bp: Breakpoint; label: string; Icon: React.FC<{ size?: number }> }[] = [
    { bp: 'desktop', label: '1440', Icon: IconDesktop },
    { bp: 'tablet', label: '768', Icon: IconTablet },
    { bp: 'mobile', label: '375', Icon: IconMobile },
];

const STATES: SimulatedState[] = [
    'normal', 'hover', 'focus', 'pressed', 'disabled', 'loading', 'error', 'success',
];

export default function TopBar() {
    const { toolMode, setToolMode, breakpoint, setBreakpoint,
        simulatedState, setSimulatedState, operatingMode,
        zoom, toggleBottomPanel } = useEditorStore();

    return (
        <header className="ob-topbar">
            <div className="ob-logo">
                <IconLogo size={24} />
                <span>OmniBuilder</span>
            </div>

            <div className="ob-topbar-divider" />

            <div className="ob-toolbar">
                {TOOLS.map((t) => (
                    <button
                        key={t.mode}
                        className={`ob-tool-btn${toolMode === t.mode ? ' active' : ''}`}
                        onClick={() => setToolMode(t.mode)}
                        title={t.label}
                    >
                        <t.Icon size={16} />
                    </button>
                ))}
            </div>

            <div className="ob-topbar-divider" />

            <div className="ob-breakpoints">
                {BREAKPOINTS.map((b) => (
                    <button
                        key={b.bp}
                        className={`ob-bp-btn${breakpoint === b.bp ? ' active' : ''}`}
                        onClick={() => setBreakpoint(b.bp)}
                    >
                        <b.Icon size={14} />
                        <span>{b.label}</span>
                    </button>
                ))}
            </div>

            <div className="ob-topbar-divider" />

            <div className="ob-state-sim">
                <span style={{ fontSize: '10px', color: 'var(--ob-text-tertiary)' }}>STATE</span>
                <select
                    className="ob-state-select"
                    value={simulatedState}
                    onChange={(e) => setSimulatedState(e.target.value as SimulatedState)}
                >
                    {STATES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>
            </div>

            <div className="ob-topbar-spacer" />

            <div className="ob-mode-badge">
                <span className="ob-mode-dot" />
                {operatingMode === 'source-owned' ? 'Source-Owned' :
                    operatingMode === 'localhost-bridge' ? 'Local Bridge' : 'Recon'}
            </div>

            <div className="ob-topbar-divider" />

            <span className="ob-zoom-display">{Math.round(zoom * 100)}%</span>

            <button className="ob-bottom-toggle" onClick={toggleBottomPanel} title="Toggle bottom panel">
                <IconPanelToggle size={14} />
            </button>
        </header>
    );
}
