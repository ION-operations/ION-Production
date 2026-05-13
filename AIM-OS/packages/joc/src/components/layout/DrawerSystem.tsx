import React, { useState } from 'react';
import { useJOCStore, type DrawerType, type OpenDrawer } from '../../store/jocStore';
import { ChevronLeftIcon, CloseIcon } from '../icons';
import { AgentCommsDrawer } from '../AgentCommsDrawer';

// ─── Drawer Content Registry ───

const DRAWER_CONFIG: Record<DrawerType, { title: string; width: number; subTabs: string[] }> = {
    dashboard: { title: 'DASHBOARD', width: 360, subTabs: ['overview', 'feed', 'stats'] },
    fleet: { title: 'AI FLEET', width: 340, subTabs: ['sessions', 'health', 'quota', 'memory'] },
    missions: { title: 'MISSIONS', width: 380, subTabs: ['active', 'history', 'templates'] },
    comms: { title: 'COMMS', width: 360, subTabs: ['all', 'by-agent', 'threads'] },
    projects: { title: 'PROJECTS', width: 360, subTabs: ['active', 'dormant', 'search'] },
    compute: { title: 'COMPUTE', width: 340, subTabs: ['local', 'cloud', 'storage', 'api'] },
    settings: { title: 'SETTINGS', width: 320, subTabs: ['general', 'drivers', 'keys', 'theme'] },
};

// ─── Drawer Content Components ───

function FleetSessionsContent() {
    const { sessions } = useJOCStore();

    const statusClass = (status: string) => {
        switch (status) {
            case 'active': return 'active';
            case 'sleeping': return 'sleeping';
            case 'dead': return 'error';
            default: return '';
        }
    };

    const providerEmoji = (provider: string) => {
        switch (provider) {
            case 'chatgpt': return '🟢';
            case 'gemini': return '🔵';
            case 'claude': return '🟠';
            case 'perplexity': return '🟣';
            default: return '⚪';
        }
    };

    return (
        <div>
            {sessions.map(s => (
                <div key={s.id} className="ai-session">
                    <div className="ai-session-icon">{providerEmoji(s.provider)}</div>
                    <div className="ai-session-info">
                        <div className="ai-session-name">{s.name}</div>
                        <div className="ai-session-detail">{s.lastActivity}</div>
                    </div>
                    <div className="ai-session-status">
                        <span className={`status-dot ${statusClass(s.status)}`} />
                        {s.uptime}
                    </div>
                </div>
            ))}
        </div>
    );
}

function FleetHealthContent() {
    const { sessions } = useJOCStore();

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {sessions.map(s => (
                <div key={s.id}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '11px' }}>
                        <span style={{ color: 'var(--text-primary)' }}>{s.name}</span>
                        <span style={{ color: s.health > 70 ? 'var(--success)' : s.health > 40 ? 'var(--warning)' : 'var(--danger)' }}>
                            {s.health}%
                        </span>
                    </div>
                    <div style={{ height: '4px', background: 'var(--bg-input)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{
                            height: '100%',
                            width: `${s.health}%`,
                            background: s.health > 70 ? 'var(--success)' : s.health > 40 ? 'var(--warning)' : 'var(--danger)',
                            borderRadius: '2px',
                            transition: 'width 0.3s ease',
                        }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

function MissionsActiveContent() {
    const { missions } = useJOCStore();
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {missions.map(m => (
                <div key={m.id} style={{
                    padding: '10px 12px',
                    background: 'var(--bg-elevated)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-primary)' }}>
                            {m.id}: {m.title}
                        </span>
                        <span style={{ fontSize: '10px', color: m.status === 'complete' ? 'var(--success)' : 'var(--accent)', textTransform: 'uppercase' }}>
                            {m.status}
                        </span>
                    </div>
                    <div style={{ height: '3px', background: 'var(--bg-input)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{
                            height: '100%',
                            width: `${m.progress}%`,
                            background: m.status === 'complete' ? 'var(--success)' : 'var(--purple)',
                            transition: 'width 0.3s ease',
                        }} />
                    </div>
                    <div style={{ marginTop: '6px', fontSize: '10px', color: 'var(--text-hint)' }}>
                        Targets: {m.targets.join(', ')} • {m.createdAt}
                    </div>
                </div>
            ))}
        </div>
    );
}

function CommsContent() {
    return <AgentCommsDrawer />;
}

function PlaceholderContent({ label }: { label: string }) {
    return (
        <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-hint)', fontSize: '11px' }}>
            {label} content — coming soon
        </div>
    );
}

// ─── Content Resolution ───

function getDrawerContent(type: DrawerType, subTab: string): React.ReactNode {
    switch (type) {
        case 'fleet':
            switch (subTab) {
                case 'sessions': return <FleetSessionsContent />;
                case 'health': return <FleetHealthContent />;
                default: return <PlaceholderContent label={`Fleet > ${subTab}`} />;
            }
        case 'missions':
            switch (subTab) {
                case 'active': return <MissionsActiveContent />;
                default: return <PlaceholderContent label={`Missions > ${subTab}`} />;
            }
        case 'comms':
            // Comms drawer handles its own sub-filtering
            return <CommsContent />;
        default:
            return <PlaceholderContent label={`${type} > ${subTab}`} />;
    }
}

// ─── Single Drawer Panel ───

function DrawerPanel({ drawer }: { drawer: OpenDrawer }) {
    const { closeDrawer, drawerSubTabs, setDrawerSubTab } = useJOCStore();
    const [collapsed, setCollapsed] = useState(false);
    const config = DRAWER_CONFIG[drawer.type];
    const activeSubTab = drawerSubTabs[drawer.type];

    if (collapsed) {
        return (
            <div
                className="drawer-collapsed"
                onClick={() => setCollapsed(false)}
                style={{ flex: drawer.position === 'full' ? 1 : undefined, height: drawer.position !== 'full' ? '50%' : undefined }}
            >
                <span className="drawer-collapsed-title">{config.title}</span>
            </div>
        );
    }

    return (
        <div
            className="drawer animate-slideIn"
            style={{
                width: `${config.width}px`,
                flex: drawer.position === 'full' ? 1 : undefined,
                height: drawer.position !== 'full' ? '50%' : undefined,
            }}
        >
            <div className="drawer-header">
                <span className="drawer-title">{config.title}</span>
                <div className="drawer-controls">
                    <button className="drawer-control-btn" onClick={() => setCollapsed(true)} title="Collapse">
                        <ChevronLeftIcon />
                    </button>
                    <button className="drawer-control-btn" onClick={() => closeDrawer(drawer.type)} title="Close">
                        <CloseIcon />
                    </button>
                </div>
            </div>

            {config.subTabs.length > 1 && (
                <div className="drawer-subtabs">
                    {config.subTabs.map(tab => (
                        <button
                            key={tab}
                            className={`drawer-subtab ${activeSubTab === tab ? 'active' : ''}`}
                            onClick={() => setDrawerSubTab(drawer.type, tab)}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>
            )}

            <div className="drawer-body">
                {getDrawerContent(drawer.type, activeSubTab)}
            </div>
        </div>
    );
}

// ─── Drawer System Container ───

export function DrawerSystem() {
    const { openDrawers } = useJOCStore();

    if (openDrawers.length === 0) return null;

    const fullDrawer = openDrawers.find(d => d.position === 'full');
    const topDrawer = openDrawers.find(d => d.position === 'top');
    const bottomDrawer = openDrawers.find(d => d.position === 'bottom');

    if (fullDrawer) {
        return <DrawerPanel drawer={fullDrawer} />;
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', borderLeft: '1px solid var(--border)' }}>
            {topDrawer && <DrawerPanel drawer={topDrawer} />}
            {topDrawer && bottomDrawer && <div style={{ height: '1px', background: 'var(--border)' }} />}
            {bottomDrawer && <DrawerPanel drawer={bottomDrawer} />}
        </div>
    );
}
