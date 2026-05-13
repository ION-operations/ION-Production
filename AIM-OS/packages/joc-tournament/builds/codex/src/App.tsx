import React, { startTransition, useEffect, useState } from 'react';
import {
    BoltIcon,
    ChevronDownIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    ChevronUpIcon,
    ClipboardListIcon,
    JOCLogo,
    PlusIcon,
    RefreshCycleIcon,
    RobotHeadIcon,
    SatelliteIcon,
} from '../../../../joc/src/components/icons';
import { getPanel, getWorkspace, type TruthState } from '../../../shared/types';
import {
    activityFeed,
    approvalsQueue,
    assistantByMode,
    attentionStack,
    commandMetrics,
    diagnosticsFeed,
    evidenceDeck,
    fleetAgents,
    missionQueue,
    subsystemHealth,
    workspaceBriefs,
} from './data/mockData';
import { PRIMARY_WORKSPACE_IDS, type WorkspaceId, useShellStore } from './store/shellStore';

const DRAWER_LAYOUTS: Record<WorkspaceId, string[]> = {
    dashboard: ['agent-fleet', 'mission-queue', 'system-status'],
    dispatch: ['mission-queue', 'messages', 'approvals-queue'],
    'agent-workforce': ['agent-dossier', 'messages', 'agent-fleet'],
    'context-lab': ['memory-browser', 'system-status'],
    oracle: ['approvals-queue', 'memory-browser'],
    'infra-console': ['system-status', 'credentials', 'diagnostics'],
    'code-editor': ['mission-queue', 'diagnostics'],
};

const WORKSPACE_LABEL_OVERRIDES: Partial<Record<WorkspaceId, string>> = {
    'code-editor': 'Builder',
};

const RAIL_MODES = [
    { id: 'chat', label: 'Chat' },
    { id: 'context', label: 'Context' },
    { id: 'actions', label: 'Actions' },
    { id: 'memory', label: 'Memory' },
] as const;

function App() {
    const {
        activeWorkspace,
        assistantMode,
        assistantOpen,
        bottomExpanded,
        bottomView,
        leftDrawerOpen,
        setAssistantMode,
        setBottomView,
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
    const assistantMessages = assistantByMode[assistantMode];
    const workspaceGroups = groupWorkspaces();
    const drawerPanels = DRAWER_LAYOUTS[activeWorkspace];

    return (
        <div className="jarvis-shell">
            <header className="topbar surface-texture">
                <div className="topbar-brand">
                    <JOCLogo size={18} />
                    <div>
                        <div className="brand-title">J.A.R.V.I.S.</div>
                        <div className="brand-subtitle">Codex Mission Control Candidate</div>
                    </div>
                </div>

                <div className="topbar-workspace-groups">
                    {workspaceGroups.map((group) => (
                        <div className="workspace-group" key={group.label}>
                            <div className="workspace-group-label">{group.label}</div>
                            <div className="workspace-tabs">
                                {group.items.map((entry) => {
                                    const Icon = entry.icon;
                                    const isActive = entry.id === activeWorkspace;
                                    return (
                                        <button
                                            key={entry.id}
                                            className={`workspace-tab ${isActive ? 'is-active' : ''}`}
                                            onClick={() => startTransition(() => setWorkspace(entry.id as WorkspaceId))}
                                        >
                                            <Icon size={14} />
                                            <span>{WORKSPACE_LABEL_OVERRIDES[entry.id as WorkspaceId] ?? entry.title}</span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="topbar-status">
                    <TruthBadge truth="LIVE" />
                    <StatusReadout label="Bridge" value="5001 OK" tone="good" />
                    <StatusReadout label="Retrieval" value="HHNI DOWN" tone="bad" />
                    <div className="clock-readout">{clock}</div>
                </div>
            </header>

            <section
                className={[
                    'shell-main',
                    leftDrawerOpen ? 'drawer-open' : 'drawer-closed',
                    assistantOpen ? 'assistant-open' : 'assistant-closed',
                ].join(' ')}
            >
                <nav className="icon-rail surface-texture">
                    {PRIMARY_WORKSPACE_IDS.map((workspaceId) => {
                        const entry = getWorkspace(workspaceId)!;
                        const Icon = entry.icon;
                        const isActive = workspaceId === activeWorkspace;
                        return (
                            <button
                                key={workspaceId}
                                className={`icon-rail-button ${isActive ? 'is-active' : ''}`}
                                title={entry.title}
                                onClick={() => startTransition(() => setWorkspace(workspaceId))}
                            >
                                <Icon size={18} />
                            </button>
                        );
                    })}

                    <div className="icon-rail-separator" />

                    <button className="icon-rail-button" onClick={toggleLeftDrawer} title="Toggle left drawer">
                        {leftDrawerOpen ? <ChevronLeftIcon size={16} /> : <ChevronRightIcon size={16} />}
                    </button>
                    <button className="icon-rail-button" onClick={toggleAssistant} title="Toggle assistant rail">
                        <RobotHeadIcon size={16} />
                    </button>
                </nav>

                <aside className={`left-drawer surface-texture ${leftDrawerOpen ? '' : 'is-collapsed'}`}>
                    <div className="drawer-header">
                        <div>
                            <div className="eyebrow">Workspace payload</div>
                            <div className="drawer-title">{workspace.title}</div>
                        </div>
                        <button className="ghost-button" onClick={toggleLeftDrawer}>
                            {leftDrawerOpen ? <ChevronLeftIcon size={14} /> : <ChevronRightIcon size={14} />}
                        </button>
                    </div>

                    <div className="drawer-body">
                        {drawerPanels.map((panelId) => {
                            const panel = getPanel(panelId);
                            if (!panel) {
                                return null;
                            }
                            const PanelIcon = panel.icon;
                            return (
                                <section className="drawer-section" key={panelId}>
                                    <div className="drawer-section-header">
                                        <div className="drawer-section-title">
                                            <PanelIcon size={15} />
                                            <span>{panel.title}</span>
                                        </div>
                                        <TruthBadge truth={toTruthState(panel.dataStatus)} small />
                                    </div>
                                    {renderDrawerContent(panelId)}
                                </section>
                            );
                        })}
                    </div>
                </aside>

                <main className="workspace-stage">
                    <div className="workspace-header">
                        <div>
                            <div className="eyebrow">{workspaceBriefs[activeWorkspace].eyebrow}</div>
                            <h1>{workspace.title}</h1>
                            <p>{workspaceBriefs[activeWorkspace].summary}</p>
                        </div>
                        <div className="workspace-header-actions">
                            <button className="instrument-button">
                                <RefreshCycleIcon size={14} />
                                <span>Refresh truth</span>
                            </button>
                            <button className="instrument-button instrument-button--accent">
                                <PlusIcon size={14} />
                                <span>Open mission</span>
                            </button>
                        </div>
                    </div>

                    <div className="workspace-breadcrumb">
                        <span>Objective: {workspaceBriefs[activeWorkspace].objective}</span>
                        <span>Shell: {workspaceBriefs[activeWorkspace].shellNote}</span>
                    </div>

                    <div className="workspace-canvas">
                        {activeWorkspace === 'dashboard' ? (
                            <MissionControlPage />
                        ) : (
                            <WorkspacePreview workspaceId={activeWorkspace} />
                        )}
                    </div>
                </main>

                <aside className={`assistant-rail surface-texture ${assistantOpen ? '' : 'is-collapsed'}`}>
                    <div className="assistant-header">
                        <div>
                            <div className="eyebrow">Assistant rail</div>
                            <div className="assistant-title">Operator intelligence</div>
                        </div>
                        <TruthBadge truth="LIVE" small />
                    </div>

                    <div className="assistant-mode-row">
                        {RAIL_MODES.map((mode) => (
                            <button
                                key={mode.id}
                                className={`assistant-mode ${assistantMode === mode.id ? 'is-active' : ''}`}
                                onClick={() => setAssistantMode(mode.id)}
                            >
                                {mode.label}
                            </button>
                        ))}
                    </div>

                    <div className="assistant-feed">
                        {assistantMessages.map((message) => (
                            <article className="assistant-card" key={`${message.lead}-${message.body}`}>
                                <div className="assistant-card-lead">{message.lead}</div>
                                <p>{message.body}</p>
                                <div className="assistant-card-footer">
                                    <span>confidence {message.confidence}</span>
                                </div>
                            </article>
                        ))}

                        <InstrumentPanel
                            title="Evidence rack"
                            truth="LIVE"
                            compact
                            body={
                                <div className="evidence-list">
                                    {evidenceDeck.map((item) => (
                                        <div className="evidence-item" key={item.title}>
                                            <div>
                                                <div className="evidence-title">{item.title}</div>
                                                <div className="evidence-source">{item.source}</div>
                                            </div>
                                            <TruthBadge truth={item.truth} small />
                                        </div>
                                    ))}
                                </div>
                            }
                        />
                    </div>

                    <div className="assistant-composer">
                        <textarea
                            className="assistant-input"
                            rows={3}
                            defaultValue="Focus on operational truth, not cosmetic certainty."
                        />
                    </div>
                </aside>
            </section>

            <footer className={`bottom-dock surface-texture ${bottomExpanded ? 'is-expanded' : ''}`}>
                <div className="bottom-dock-bar">
                    <div className="bottom-dock-tabs">
                        <button
                            className={`bottom-dock-tab ${bottomView === 'chronicle' ? 'is-active' : ''}`}
                            onClick={() => setBottomView('chronicle')}
                        >
                            Activity Chronicle
                        </button>
                        <button
                            className={`bottom-dock-tab ${bottomView === 'diagnostics' ? 'is-active' : ''}`}
                            onClick={() => setBottomView('diagnostics')}
                        >
                            Diagnostics
                        </button>
                    </div>

                    <div className="bottom-dock-right">
                        <TruthBadge truth={bottomView === 'chronicle' ? 'LIVE' : 'CACHED'} small />
                        <button className="ghost-button" onClick={toggleBottom}>
                            {bottomExpanded ? <ChevronDownIcon size={14} /> : <ChevronUpIcon size={14} />}
                        </button>
                    </div>
                </div>

                {bottomExpanded && (
                    <div className="bottom-dock-content">
                        {(bottomView === 'chronicle' ? activityFeed : diagnosticsFeed).map((item) => (
                            <div className="dock-log-line" key={`${item.time}-${item.source}-${item.text}`}>
                                <span className="dock-log-time">{item.time}</span>
                                <span className="dock-log-source">{item.source}</span>
                                <span className="dock-log-text">{item.text}</span>
                                <TruthBadge truth={item.truth} small />
                            </div>
                        ))}
                    </div>
                )}
            </footer>
        </div>
    );
}

function MissionControlPage() {
    return (
        <div className="mission-control">
            <section className="metric-band">
                {commandMetrics.map((metric) => (
                    <article className="metric-tile surface-texture" key={metric.label}>
                        <div className="metric-label-row">
                            <span className="metric-label">{metric.label}</span>
                            <TruthBadge truth={metric.truth} small />
                        </div>
                        <div className="metric-value">{metric.value}</div>
                        <div className="metric-detail">{metric.detail}</div>
                    </article>
                ))}
            </section>

            <section className="mission-grid">
                <InstrumentPanel
                    title="Force picture"
                    truth="LIVE"
                    body={
                        <div className="fleet-grid">
                            {fleetAgents.map((agent) => (
                                <article className="agent-card" key={agent.callsign}>
                                    <div className={`agent-led ${agent.tone}`} />
                                    <div className="agent-copy">
                                        <div className="agent-line">
                                            <strong>{agent.callsign}</strong>
                                            <TruthBadge truth={agent.trust} small />
                                        </div>
                                        <div className="agent-role">{agent.role}</div>
                                        <div className="agent-task">{agent.task}</div>
                                    </div>
                                </article>
                            ))}
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Attention stack"
                    truth="LIVE"
                    body={
                        <div className="attention-list">
                            {attentionStack.map((item) => (
                                <article className="attention-card" key={item.label}>
                                    <div className="attention-line">
                                        <PriorityBadge priority={item.priority} />
                                        <TruthBadge truth={item.truth} small />
                                    </div>
                                    <div className="attention-title">{item.label}</div>
                                    <p>{item.detail}</p>
                                </article>
                            ))}
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Mission queue"
                    truth="CACHED"
                    body={
                        <div className="mission-list">
                            {missionQueue.map((mission) => (
                                <article className="mission-card" key={mission.title}>
                                    <div className="mission-card-header">
                                        <PriorityBadge priority={mission.priority} />
                                        <TruthBadge truth={mission.truth} small />
                                    </div>
                                    <div className="mission-title">{mission.title}</div>
                                    <div className="mission-meta">
                                        <span>{mission.owner}</span>
                                        <span>{mission.eta}</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${mission.progress}%` }} />
                                    </div>
                                    <div className="progress-label">{mission.progress}% complete</div>
                                </article>
                            ))}
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Truth and recovery strip"
                    truth="LIVE"
                    body={
                        <div className="system-list">
                            {subsystemHealth.map((system) => (
                                <article className="system-row" key={system.acronym}>
                                    <div className="system-head">
                                        <div>
                                            <div className="system-acronym">{system.acronym}</div>
                                            <div className="system-label">{system.label}</div>
                                        </div>
                                        <TruthBadge truth={system.truth} small />
                                    </div>
                                    <div className="system-meter">
                                        <div className="system-meter-track">
                                            <div
                                                className={`system-meter-fill ${system.tone}`}
                                                style={{ width: `${system.health}%` }}
                                            />
                                        </div>
                                        <span>{system.health}%</span>
                                    </div>
                                    <div className="system-note">{system.note}</div>
                                </article>
                            ))}
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Approval pressure"
                    truth="SPECULATIVE"
                    span="wide"
                    body={
                        <div className="approval-strip">
                            {approvalsQueue.map((item) => (
                                <div className="approval-card" key={item.title}>
                                    <div>
                                        <div className="approval-title">{item.title}</div>
                                        <div className="approval-owner">owner {item.owner}</div>
                                    </div>
                                    <div className="approval-actions">
                                        <TruthBadge truth={item.truth} small />
                                        <button className="tiny-action tiny-action--accent">Review</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Activity chronicle"
                    truth="LIVE"
                    span="wide"
                    body={
                        <div className="chronicle-list">
                            {activityFeed.map((item) => (
                                <div className="chronicle-row" key={`${item.time}-${item.source}-${item.text}`}>
                                    <span className="chronicle-time">{item.time}</span>
                                    <span className="chronicle-source">{item.source}</span>
                                    <span className="chronicle-text">{item.text}</span>
                                    <TruthBadge truth={item.truth} small />
                                </div>
                            ))}
                        </div>
                    }
                />
            </section>
        </div>
    );
}

function WorkspacePreview({ workspaceId }: { workspaceId: WorkspaceId }) {
    const workspace = getWorkspace(workspaceId)!;
    const Icon = workspace.icon;
    const panels = DRAWER_LAYOUTS[workspaceId]
        .map((panelId) => getPanel(panelId))
        .filter((panel): panel is NonNullable<typeof panel> => Boolean(panel));

    return (
        <div className="workspace-preview">
            <InstrumentPanel
                title="Workspace charter"
                truth="LIVE"
                body={
                    <div className="workspace-preview-hero">
                        <div className="workspace-preview-mark">
                            <Icon size={28} />
                        </div>
                        <div>
                            <h2>{workspace.title}</h2>
                            <p>{workspaceBriefs[workspaceId].summary}</p>
                        </div>
                    </div>
                }
            />

            <div className="workspace-preview-grid">
                <InstrumentPanel
                    title="Drawer loadout"
                    truth="CACHED"
                    body={
                        <div className="preview-panel-list">
                            {panels.map((panel) => {
                                const PanelIcon = panel.icon;
                                return (
                                    <div className="preview-panel-row" key={panel.id}>
                                        <div className="preview-panel-name">
                                            <PanelIcon size={14} />
                                            <span>{panel.title}</span>
                                        </div>
                                        <TruthBadge truth={toTruthState(panel.dataStatus)} small />
                                    </div>
                                );
                            })}
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Operator objective"
                    truth="LIVE"
                    body={
                        <div className="preview-text-block">
                            <p>{workspaceBriefs[workspaceId].objective}</p>
                            <p>{workspaceBriefs[workspaceId].shellNote}</p>
                        </div>
                    }
                />

                <InstrumentPanel
                    title="Why this page is not overbuilt"
                    truth="SPECULATIVE"
                    body={
                        <div className="preview-text-block">
                            <p>
                                Phase 1 only perfects Mission Control. This workspace still reconfigures the shell,
                                but the center canvas remains intentionally schematic until the operator promotes it.
                            </p>
                        </div>
                    }
                />
            </div>
        </div>
    );
}

function InstrumentPanel({
    body,
    compact = false,
    span,
    title,
    truth,
}: {
    title: string;
    truth: TruthState;
    body: React.ReactNode;
    compact?: boolean;
    span?: 'wide';
}) {
    return (
        <section className={`instrument-panel ${compact ? 'is-compact' : ''} ${span === 'wide' ? 'is-wide' : ''}`}>
            <div className="instrument-panel-header">
                <div className="instrument-title">{title}</div>
                <TruthBadge truth={truth} small />
            </div>
            <div className="instrument-panel-body">{body}</div>
        </section>
    );
}

function StatusReadout({ label, tone, value }: { label: string; value: string; tone: 'good' | 'bad' }) {
    return (
        <div className="status-readout">
            <span className={`status-led ${tone}`} />
            <span className="status-label">{label}</span>
            <span className="status-value">{value}</span>
        </div>
    );
}

function PriorityBadge({ priority }: { priority: 'P0' | 'P1' | 'P2' }) {
    return <span className={`priority-badge priority-${priority.toLowerCase()}`}>{priority}</span>;
}

function TruthBadge({ small = false, truth }: { truth: TruthState; small?: boolean }) {
    return <span className={`truth-badge truth-${truth.toLowerCase()} ${small ? 'is-small' : ''}`}>{truth}</span>;
}

function renderDrawerContent(panelId: string) {
    switch (panelId) {
        case 'agent-fleet':
        case 'agent-dossier':
            return (
                <div className="drawer-list">
                    {fleetAgents.slice(0, 5).map((agent) => (
                        <div className="drawer-row" key={agent.callsign}>
                            <div>
                                <div className="drawer-row-title">{agent.callsign}</div>
                                <div className="drawer-row-subtitle">{agent.role}</div>
                            </div>
                            <div className={`agent-led ${agent.tone}`} />
                        </div>
                    ))}
                </div>
            );
        case 'mission-queue':
            return (
                <div className="drawer-list">
                    {missionQueue.slice(0, 3).map((mission) => (
                        <div className="drawer-row" key={mission.title}>
                            <div>
                                <div className="drawer-row-title">{mission.title}</div>
                                <div className="drawer-row-subtitle">{mission.owner}</div>
                            </div>
                            <PriorityBadge priority={mission.priority} />
                        </div>
                    ))}
                </div>
            );
        case 'system-status':
        case 'diagnostics':
            return (
                <div className="drawer-list">
                    {subsystemHealth.slice(0, 4).map((system) => (
                        <div className="drawer-row" key={system.acronym}>
                            <div>
                                <div className="drawer-row-title">{system.acronym}</div>
                                <div className="drawer-row-subtitle">{system.label}</div>
                            </div>
                            <span className={`mini-health ${system.tone}`} />
                        </div>
                    ))}
                </div>
            );
        case 'messages':
            return (
                <div className="drawer-list">
                    {activityFeed.slice(0, 3).map((item) => (
                        <div className="drawer-row" key={`${item.time}-${item.source}`}>
                            <div>
                                <div className="drawer-row-title">{item.source}</div>
                                <div className="drawer-row-subtitle">{item.text}</div>
                            </div>
                            <TruthBadge truth={item.truth} small />
                        </div>
                    ))}
                </div>
            );
        case 'approvals-queue':
            return (
                <div className="drawer-list">
                    {approvalsQueue.map((item) => (
                        <div className="drawer-row" key={item.title}>
                            <div>
                                <div className="drawer-row-title">{item.title}</div>
                                <div className="drawer-row-subtitle">{item.owner}</div>
                            </div>
                            <TruthBadge truth={item.truth} small />
                        </div>
                    ))}
                </div>
            );
        case 'memory-browser':
            return (
                <div className="drawer-memory">
                    <div className="memory-chip">Atlas</div>
                    <div className="memory-chip">Packets</div>
                    <div className="memory-chip">Lineage</div>
                    <div className="memory-chip">Evidence</div>
                </div>
            );
        case 'credentials':
            return (
                <div className="drawer-list">
                    <div className="drawer-row">
                        <div>
                            <div className="drawer-row-title">MCP bridge token</div>
                            <div className="drawer-row-subtitle">Scoped, active</div>
                        </div>
                        <SatelliteIcon size={14} />
                    </div>
                    <div className="drawer-row">
                        <div>
                            <div className="drawer-row-title">Tournament sandbox</div>
                            <div className="drawer-row-subtitle">Local only</div>
                        </div>
                        <BoltIcon size={14} />
                    </div>
                </div>
            );
        default:
            return (
                <div className="drawer-list">
                    <div className="drawer-row">
                        <div>
                            <div className="drawer-row-title">Panel not modeled</div>
                            <div className="drawer-row-subtitle">Reserved for next phase promotion.</div>
                        </div>
                        <ClipboardListIcon size={14} />
                    </div>
                </div>
            );
    }
}

function groupWorkspaces() {
    const groups = new Map<string, Array<NonNullable<ReturnType<typeof getWorkspace>>>>();
    for (const workspaceId of PRIMARY_WORKSPACE_IDS) {
        const workspace = getWorkspace(workspaceId);
        if (!workspace) {
            continue;
        }
        const label = workspace.navGroup;
        const items = groups.get(label) ?? [];
        items.push(workspace);
        groups.set(label, items);
    }
    return Array.from(groups.entries()).map(([label, items]) => ({ label, items }));
}

function toTruthState(status: string): TruthState {
    switch (status) {
        case 'live':
            return 'LIVE';
        case 'cached':
            return 'CACHED';
        case 'mock':
            return 'MOCK';
        case 'offline':
            return 'OFFLINE';
        default:
            return 'SPECULATIVE';
    }
}

function formatClock(date: Date) {
    return date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}

export default App;
