import React from 'react';
import { TopBar } from './components/shell/TopBar';
import { PageSubBar } from './components/shell/PageSubBar';
import { LeftIconBar, LeftDrawer } from './components/shell/LeftDrawer';
import { RightIconBar, AssistantRail } from './components/shell/AssistantRail';
import { BottomBar } from './components/shell/BottomBar';
import { MissionControl } from './components/dashboard/MissionControl';
import { useShellStore, WORKSPACES } from './store/shellStore';

// ═══════════════════════════════════════════════════════════════════
// J.A.R.V.I.S. — Joint AI Research & Visualization Intelligence System
// DAC Tournament Build — "The Instrument"
// ═══════════════════════════════════════════════════════════════════

export default function App() {
    const { activeWorkspace } = useShellStore();

    return (
        <div className="shell">
            {/* TopBar — 48px, workspace navigation */}
            <TopBar />

            {/* PageSubBar — 36px, workspace-local title + breadcrumb */}
            <PageSubBar />

            {/* Shell Body — flex row */}
            <div className="shell-body">
                {/* Left Icon Bar — 44px */}
                <LeftIconBar />

                {/* Left Drawer — workspace-local panels */}
                <LeftDrawer />

                {/* Center — canvas + bottom bar */}
                <div className="shell-center">
                    <div className="center-canvas">
                        {activeWorkspace === 'dashboard' && <MissionControl />}
                        {activeWorkspace !== 'dashboard' && <WorkspacePlaceholder />}
                    </div>
                </div>

                {/* Assistant Rail — persistent intelligence companion */}
                <AssistantRail />

                {/* Right Icon Bar — rail mode switcher */}
                <RightIconBar />
            </div>

            {/* Bottom Bar — temporal + diagnostic substrate */}
            <BottomBar />
        </div>
    );
}


// ─── Placeholder for non-dashboard workspaces ────────────────────

function WorkspacePlaceholder() {
    const { activeWorkspace } = useShellStore();
    const ws = WORKSPACES.find((w) => w.id === activeWorkspace);

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            gap: 16,
        }}>
            <div className="instrument-panel" style={{ padding: 32, textAlign: 'center', maxWidth: 420 }}>
                <div style={{ fontSize: 32, marginBottom: 12 }}>{ws?.icon}</div>
                <div className="engraved-bright" style={{ fontSize: 14, marginBottom: 8 }}>
                    {ws?.title || 'Unknown Workspace'}
                </div>
                <div style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize: 13,
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5,
                    marginBottom: 16,
                }}>
                    {ws?.description}
                </div>
                <div className="lcd-readout" style={{ textAlign: 'center' }}>
                    <div className="lcd-readout-label">Status</div>
                    <div className="mono-dim">PHASE 2 · NOT YET BUILT</div>
                </div>
            </div>
        </div>
    );
}
