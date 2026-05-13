import { useState, useEffect } from 'react';
import './styles/joc.css';
import './styles/assistant-rail.css';
import './styles/session.css';
import './styles/comms.css';
import './styles/timeline.css';
import './styles/timeline-v2.css';
import './styles/code-editor.css';
import './styles/system-atlas.css';
import './styles/command-palette.css';
import './styles/compute.css';
import './styles/dispatch.css';
import './styles/synthesizer.css';
import './styles/agent-comms.css';
import './styles/session-health.css';
import './styles/auto-context.css';
import './styles/project-catalog.css';
import './styles/credential-vault.css';
import './styles/cli-terminal.css';
import './styles/storage-browser.css';
import './styles/settings.css';
import './styles/mission-builder.css';
import './styles/notification.css';
import './styles/gpu-monitor.css';
import './styles/activity-log.css';
import './styles/welcome.css';
import './styles/context-graph.css';
import './styles/mcp-diagnostics.css';
import './styles/context-lab.css';
import { TopBar } from './components/layout/TopBar';
import { PageSubBar } from './components/layout/PageSubBar';
import { PageRouter } from './components/layout/PageRouter';
import { DrawerSystem } from './components/layout/DrawerSystem';
import { RightIconBar } from './components/layout/RightIconBar';
import { LeftIconBar } from './components/layout/LeftIconBar';
import { LeftDrawerSystem } from './components/layout/LeftDrawerSystem';
import { AssistantRail } from './components/layout/AssistantRail';
import { BottomBar } from './components/layout/BottomBar';
import { CommandPalette } from './components/CommandPalette';
import { KeyboardShortcutsOverlay } from './components/KeyboardShortcutsOverlay';
import { NotificationCenter } from './components/NotificationCenter';

/**
 * J.A.R.V.I.S. Root Layout
 *
 *  ┌────────────────────── TopBar ──────────────────────────┐
 *  ├────────────────────── PageSubBar ──────────────────────┤
 *  │ Left │ Left     │                            │ Right  │
 *  │ Icon │ Drawers  │  Center Canvas (FULL)      │ Icon   │
 *  │ Bar  │ (per-ws) │  (workspace content)       │ Bar    │
 *  │      │          │                            │        │
 *  ├──────┴──────────┴────────────────────────────┴────────┤
 *  │                     BottomBar                         │
 *  └──────────────────────────────────────────────────────-┘
 *
 *  AssistantRail: OVERLAY from right (position: fixed).
 *  Slides over content, does NOT consume layout width.
 *  DrawerSystem (legacy right drawers) stays in joc-page-area.
 */
export default function App() {
    const [shortcutsOpen, setShortcutsOpen] = useState(false);

    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            // Only trigger on '?' when not focused in input/textarea
            const tag = (e.target as HTMLElement).tagName;
            if (e.key === '?' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
                setShortcutsOpen(prev => !prev);
            }
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, []);

    return (
        <div className="joc-root">
            <CommandPalette />
            <KeyboardShortcutsOverlay isOpen={shortcutsOpen} onClose={() => setShortcutsOpen(false)} />
            <NotificationCenter />
            <TopBar />
            <PageSubBar />

            <div className="joc-main">
                <LeftIconBar />
                <div className="joc-content-area">
                    <LeftDrawerSystem />
                    <div className="joc-page-area">
                        <PageRouter />
                        <DrawerSystem />
                    </div>
                </div>
                <AssistantRail />
                <RightIconBar />
            </div>

            <BottomBar />
        </div>
    );
}

