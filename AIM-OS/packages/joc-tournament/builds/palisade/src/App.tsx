import React, { useEffect, useState } from 'react';
import {
    ChevronDownIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    ChevronUpIcon,
    ConstellationIcon,
    JOCLogo,
    RadarIcon,
    RobotHeadIcon,
} from '../../../../joc/src/components/icons';
import { getPanel, getWorkspace } from '../../../shared/types';
import {
    activityFeed,
    fleetAgents,
    subsystemHealth,
} from './data/mockData';
import { PRIMARY_WORKSPACE_IDS, type WorkspaceId, useShellStore } from './store/shellStore';
import type { TruthState } from '../../../shared/types';

// Mission Control left drawer: agent-fleet, system-status only (per DESIGN_BRIEF)
const MISSION_CONTROL_DRAWER = ['agent-fleet', 'system-status'] as const;

const RAIL_MODES = [
    { id: 'chat' as const, label: 'Chat' },
    { id: 'context' as const, label: 'Context' },
    { id: 'actions' as const, label: 'Actions' },
    { id: 'memory' as const, label: 'Memory' },
];

function App() {
    const {
        activeWorkspace,
        assistantMode,
        assistantOpen,
        bottomExpanded,
        leftDrawerOpen,
        setAssistantMode,
        setWorkspace,
        toggleAssistant,
        toggleBottom,
        toggleLeftDrawer,
    } = useShellStore();
    const [clock, setClock] = useState(formatClock(new Date()));

    useEffect(() => {
        const timer = window.setInterval(() => setClock(formatClock(new Date())), 1000);
        return () => window.clearInterval(timer);
    }, []);

    const workspace = getWorkspace(activeWorkspace) ?? getWorkspace('dashboard')!;
    const drawerPanels = activeWorkspace === 'dashboard' ? MISSION_CONTROL_DRAWER : ['system-status'];

    return (
        <div className="jarvis-shell">
            <header className="topbar">
                <div className="topbar-brand">
                    <JOCLogo size={16} />
                    <div>
                        <div className="brand-title">J.A.R.V.I.S.</div>
                        <div className="brand-subtitle">Palisade Mission Control</div>
                    </div>
                </div>

                <div className="topbar-workspace-tabs">
                    {PRIMARY_WORKSPACE_IDS.map((id) => {
                        const w = getWorkspace(id);
                        if (!w) return null;
                        const Icon = w.icon;
                        const isActive = id === activeWorkspace;
                        return (
                            <button
                                key={id}
                                className={`workspace-tab ${isActive ? 'is-active' : ''}`}
                                onClick={() => setWorkspace(id)}>
                                <Icon size={12} />
                                <span>{w.title}</span>
                            </button>
                        );
                    })}
                </div>

                <div className="topbar-status">
                    <span className="status-dot live" title="MCP Live" />
                    <span className="clock-readout">{clock}</span>
                </div>
            </header>

            <section
                className={[
                    'shell-main',
                    leftDrawerOpen ? 'drawer-open' : 'drawer-closed',
                    assistantOpen ? 'assistant-open' : 'assistant-closed',
                ].join(' ')}>
                <nav className="icon-rail">
                    {PRIMARY_WORKSPACE_IDS.map((id) => {
                        const w = getWorkspace(id);
                        if (!w) return null;
                        const Icon = w.icon;
                        const isActive = id === activeWorkspace;
                        return (
                            <button
                                key={id}
                                className={`icon-rail-button ${isActive ? 'is-active' : ''}`}
                                title={w.title}
                                onClick={() => setWorkspace(id)}>
                                <Icon size={16} />
                            </button>
                        );
                    })}
                    <div className="icon-rail-separator" />
                    <button className="icon-rail-button" onClick={toggleLeftDrawer} title="Toggle left drawer">
                        {leftDrawerOpen ? <ChevronLeftIcon size={14} /> : <ChevronRightIcon size={14} />}
                    </button>
                    <button className="icon-rail-button" onClick={toggleAssistant} title="Toggle assistant rail">
                        <RobotHeadIcon size={14} />
                    </button>
                </nav>

                <aside className={`left-drawer ${leftDrawerOpen ? '' : 'is-collapsed'}`}>
                    <div className="drawer-header">
                        <div>
                            <div className="eyebrow">Workspace payload</div>
                            <div className="drawer-title">{workspace.title}</div>
                        </div>
                        <button className="ghost-button" onClick={toggleLeftDrawer}>
                            {leftDrawerOpen ? <ChevronLeftIcon size={12} /> : <ChevronRightIcon size={12} />}
                        </button>
                    </div>

                    <div className="drawer-body">
                        {activeWorkspace === 'dashboard' &&
                            drawerPanels.map((panelId) => {
                                const panel = getPanel(panelId);
                                if (!panel) return null;
                                const PanelIcon = panel.icon;
                                return (
                                    <section className="drawer-section" key={panelId}>
                                        <div className="drawer-section-header">
                                            <div className="drawer-section-title">
                                                <PanelIcon size={14} />
                                                <span>{panel.title}</span>
                                            </div>
                                            <TruthBadge truth={panelId === 'agent-fleet' ? 'LIVE' : 'LIVE'} />
                                        </div>
                                        {panelId === 'agent-fleet' && (
                                            <div className="drawer-list">
                                                {fleetAgents.slice(0, 6).map((a) => (
                                                    <div className="drawer-row" key={a.callsign}>
                                                        <div>
                                                            <div className="drawer-row-title">{a.callsign}</div>
                                                            <div className="drawer-row-subtitle">{a.role}</div>
                                                        </div>
                                                        <span className={`agent-led ${a.tone}`} />
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        {panelId === 'system-status' && (
                                            <div className="drawer-list">
                                                {subsystemHealth.map((s) => (
                                                    <div className="drawer-row" key={s.acronym}>
                                                        <div>
                                                            <div className="drawer-row-title">{s.acronym}</div>
                                                            <div className="drawer-row-subtitle">{s.label}</div>
                                                        </div>
                                                        <span className={`mini-health ${s.tone}`} />
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </section>
                                );
                            })}
                        {activeWorkspace !== 'dashboard' && (
                            <div className="drawer-section">
                                <div className="drawer-section-header">
                                    <div className="drawer-section-title">
                                        <RadarIcon size={14} />
                                        <span>Workspace preview</span>
                                    </div>
                                    <TruthBadge truth="CACHED" />
                                </div>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                                    Phase 1 only. Mission Control fully built. Other workspaces reconfigure shell but
                                    center canvas is schematic until promoted.
                                </p>
                            </div>
                        )}
                    </div>
                </aside>

                <main className="workspace-stage">
                    {activeWorkspace === 'dashboard' ? (
                        <MissionControlPage />
                    ) : (
                        <WorkspacePreview workspaceId={activeWorkspace} />
                    )}
                </main>

                <aside className={`assistant-rail ${assistantOpen ? '' : 'is-collapsed'}`}>
                    <div className="assistant-header">
                        <div>
                            <div className="eyebrow">Assistant rail</div>
                            <div className="assistant-title">Operator intelligence</div>
                        </div>
                        <TruthBadge truth="LIVE" />
                    </div>

                    <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)', display: 'flex', gap: '0.4rem' }}>
                        {RAIL_MODES.map((m) => (
                            <button
                                key={m.id}
                                className={`workspace-tab ${assistantMode === m.id ? 'is-active' : ''}`}
                                onClick={() => setAssistantMode(m.id)}
                                style={{ padding: '0.35rem 0.6rem' }}>
                                {m.label}
                            </button>
                        ))}
                    </div>

                    <div className="assistant-feed">
                        <div className="assistant-card">
                            <div className="assistant-card-lead">Context</div>
                            <p>
                                Mission Control concentrates force visibility, live truth, and command attention. Left drawer:
                                Agent Fleet + System Status. Bottom: Activity Feed. Every surface truth-labeled.
                            </p>
                        </div>
                        <div className="assistant-card">
                            <div className="assistant-card-lead">Operator hint</div>
                            <p>
                                The shell reconfigures when the workspace changes. Phase 1 perfects Mission Control only.
                            </p>
                        </div>
                    </div>
                </aside>
            </section>

            <footer className={`bottom-dock ${bottomExpanded ? 'is-expanded' : ''}`}>
                <div className="bottom-dock-bar">
                    <div className="bottom-dock-title">Activity Feed</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <TruthBadge truth="LIVE" />
                        <button className="ghost-button" onClick={toggleBottom}>
                            {bottomExpanded ? <ChevronDownIcon size={12} /> : <ChevronUpIcon size={12} />}
                        </button>
                    </div>
                </div>

                {bottomExpanded && (
                    <div className="bottom-dock-content">
                        {activityFeed.map((item) => (
                            <div className="dock-log-line" key={`${item.time}-${item.source}-${item.text}`}>
                                <span className="dock-log-time">{item.time}</span>
                                <span className="dock-log-source">{item.source}</span>
                                <span className="dock-log-text">{item.text}</span>
                                <TruthBadge truth={item.truth} />
                            </div>
                        ))}
                    </div>
                )}
            </footer>
        </div>
    );
}

function MissionControlPage() {
    const activeCount = fleetAgents.filter((a) => a.tone === 'busy' || a.tone === 'ready').length;
    const healthyCount = subsystemHealth.filter((s) => s.tone === 'healthy').length;

    return (
        <>
            <div className="force-at-glance">
                <div className="force-tile">
                    <div className="force-tile-label">Agents</div>
                    <div className="force-tile-value">{fleetAgents.length}</div>
                    <div className="force-tile-detail">{activeCount} active</div>
                </div>
                <div className="force-tile">
                    <div className="force-tile-label">Subsystems</div>
                    <div className="force-tile-value">{healthyCount}/{subsystemHealth.length}</div>
                    <div className="force-tile-detail">healthy</div>
                </div>
                <div className="force-tile">
                    <div className="force-tile-label">MCP</div>
                    <div className="force-tile-value">READY</div>
                    <div className="force-tile-detail">5001 OK</div>
                </div>
                <div className="force-tile">
                    <div className="force-tile-label">HHNI</div>
                    <div className="force-tile-value">DOWN</div>
                    <div className="force-tile-detail">Retriever unavailable</div>
                </div>
            </div>
        </>
    );
}

function WorkspacePreview({ workspaceId }: { workspaceId: WorkspaceId }) {
    const workspace = getWorkspace(workspaceId)!;
    const Icon = workspace.icon;

    return (
        <div className="force-at-glance" style={{ display: 'block' }}>
            <div className="force-tile" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
                    <div style={{ width: 48, height: 48, display: 'grid', placeItems: 'center', background: 'rgba(245,166,35,0.1)', borderRadius: 8 }}>
                        <Icon size={24} />
                    </div>
                    <div>
                        <div className="eyebrow">Workspace charter</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{workspace.title}</div>
                    </div>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                    Phase 1 only perfects Mission Control. This workspace reconfigures the shell (drawer, bottom), but
                    the center canvas remains schematic until the operator promotes it.
                </p>
            </div>
        </div>
    );
}

function TruthBadge({ truth }: { truth: TruthState }) {
    return <span className={`truth-badge ${truth.toLowerCase()}`}>{truth}</span>;
}

function formatClock(date: Date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default App;
