import { useState } from 'react';
import { useJOCStore, type PageType } from '../../store/jocStore';
import { useOracleStore, type OracleMode } from '../../store/oracleStore';
import { JOCLogo } from '../icons';

// ─── Navigation Group Definitions ───
// Each group is a flat button in the TopBar.
// Clicking navigates to the group's default page.

export interface NavPage {
    type: PageType;
    label: string;
}

export interface NavGroup {
    id: string;
    label: string;
    defaultPage: PageType;
    pages: NavPage[];
}

export const NAV_GROUPS: NavGroup[] = [
    {
        id: 'operations',
        label: 'OPERATIONS',
        defaultPage: 'dashboard',
        pages: [
            { type: 'dashboard', label: 'Dashboard' },
            { type: 'dispatch', label: 'Dispatch' },
            { type: 'mission-builder', label: 'Mission Builder' },
            { type: 'synthesizer', label: 'Synthesizer' },
            { type: 'calendar', label: 'Calendar' },
            { type: 'context', label: 'Context Engine' },
        ],
    },
    {
        id: 'intelligence',
        label: 'INTELLIGENCE',
        defaultPage: 'intelligence-map',
        pages: [
            { type: 'intelligence-map', label: 'V3 OS Explorer' },
            { type: 'session', label: 'Sessions' },
            { type: 'health', label: 'Session Health' },
            { type: 'comms', label: 'Agent Comms' },
            { type: 'context-graph', label: 'Context Graph' },
            { type: 'oracle', label: 'Oracle' },
            { type: 'agent-builder', label: 'Agent Builder' },
            { type: 'context-lab', label: 'Context Lab' },
            { type: 'agent-workforce', label: 'Agent Workforce' },
        ],
    },
    {
        id: 'infrastructure',
        label: 'INFRASTRUCTURE',
        defaultPage: 'compute',
        pages: [
            { type: 'compute', label: 'Compute' },
            { type: 'infra', label: 'Control Plane' },
            { type: 'atlas', label: 'System Atlas' },
            { type: 'vault', label: 'Credential Vault' },
        ],
    },
    {
        id: 'tools',
        label: 'TOOLS',
        defaultPage: 'editor',
        pages: [
            { type: 'editor', label: 'Code Editor' },
            { type: 'cli', label: 'Terminal' },
            { type: 'settings', label: 'Settings' },
        ],
    },
];

// ─── Lookup: which group does a PageType belong to? ───

export function getGroupForPage(pageType: PageType): NavGroup | undefined {
    return NAV_GROUPS.find(g => g.pages.some(p => p.type === pageType));
}

// ─── Oracle Status Badge (DXL aesthetic) ───

const ORACLE_MODES: Record<OracleMode, { color: string; label: string; glow: boolean }> = {
    auto: { color: 'var(--ses-led-green, #33cc66)', label: 'AUTO', glow: true },
    supervised: { color: 'var(--ses-led-amber, #cc9900)', label: 'SUPERVISED', glow: false },
    manual: { color: 'var(--ses-led-red, #cc3333)', label: 'MANUAL', glow: false },
    offline: { color: '#444', label: 'OFFLINE', glow: false },
};

function OracleStatusBadge() {
    const { mode, cycleMode, connected, actionsPerMinute, pendingApprovals } = useOracleStore();
    const { addTab } = useJOCStore();
    const cfg = ORACLE_MODES[mode];

    const openOraclePage = (e: React.MouseEvent) => {
        e.preventDefault();
        addTab({ id: 'oracle', type: 'oracle', label: 'Oracle', closable: true });
    };

    return (
        <button
            className="topbar-oracle-badge"
            onClick={cycleMode}
            onContextMenu={openOraclePage}
            title={`Oracle: ${cfg.label}\nLeft-click: cycle mode | Right-click: open panel\n${connected ? `${actionsPerMinute.toFixed(1)} actions/min` : 'Disconnected'}`}
        >
            <span
                className="topbar-oracle-dot"
                style={{
                    background: cfg.color,
                    boxShadow: cfg.glow ? `0 0 6px ${cfg.color}` : 'none',
                    animation: cfg.glow ? 'oraclePulse 2s ease-in-out infinite' : 'none',
                }}
            />
            <span className="topbar-oracle-label" style={{ color: cfg.color }}>ORACLE</span>
            <span className="topbar-oracle-mode" style={{ color: cfg.color }}>{cfg.label}</span>
            {pendingApprovals > 0 && (
                <span className="topbar-oracle-pending">{pendingApprovals}</span>
            )}
        </button>
    );
}

// ─── Main TopBar ───

export function TopBar() {
    const { addTab, activeTab, tabs } = useJOCStore();

    // Determine which group is active based on current page
    const activeTabData = tabs.find(t => t.id === activeTab);
    const currentPage = activeTabData?.type || 'dashboard';
    const activeGroup = getGroupForPage(currentPage);

    const handleGroupClick = (group: NavGroup) => {
        addTab({
            id: group.defaultPage,
            type: group.defaultPage,
            label: group.pages.find(p => p.type === group.defaultPage)?.label || group.label,
            closable: group.defaultPage !== 'dashboard',
        });
    };

    return (
        <div className="topbar">
            <div className="topbar-logo">
                <JOCLogo size={16} />
                <span>J.A.R.V.I.S.</span>
            </div>

            <div className="topbar-nav-groups">
                {NAV_GROUPS.map(group => (
                    <button
                        key={group.id}
                        className={`topbar-group-btn ${activeGroup?.id === group.id ? 'active' : ''}`}
                        onClick={() => handleGroupClick(group)}
                    >
                        {group.label}
                    </button>
                ))}
            </div>

            <div className="topbar-spacer" />

            <div className="topbar-right">
                <OracleStatusBadge />
                <span className="topbar-shortcut-hint">⌘⇧P</span>
            </div>
        </div>
    );
}
