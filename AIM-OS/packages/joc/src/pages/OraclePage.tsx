import { useState } from 'react';
import { useOracleStore, type OracleMode, type OracleSystem, type PermissionLevel, type OracleAction } from '../store/oracleStore';
import {
    DispatchIcon, CalendarMarkIcon, BoltIcon, AutomationIcon,
    ShieldKeyIcon, SatelliteIcon, RadarIcon, ClipboardListIcon,
} from '../components/icons';
import '../styles/oracle.css';

// ─── Types ───

// Custom SVG icon for each Oracle subsystem
const SYSTEM_ICONS: Record<OracleSystem, React.ComponentType<{ size?: number; style?: React.CSSProperties }>> = {
    dispatch: DispatchIcon,
    scheduler: CalendarMarkIcon,
    macros: BoltIcon,
    sessions: AutomationIcon,
    vault: ShieldKeyIcon,
    agentComms: SatelliteIcon,
    settings: RadarIcon,
};

const SYSTEM_META: Record<OracleSystem, { label: string; description: string; canAuto: boolean }> = {
    dispatch: { label: 'Dispatch Center', description: 'Send prompts to AI providers', canAuto: true },
    scheduler: { label: 'Scheduler', description: 'Create/modify scheduled events', canAuto: true },
    macros: { label: 'Macro Engine', description: 'Trigger automation macros', canAuto: true },
    sessions: { label: 'AI Sessions', description: 'Restart/refresh browser sessions', canAuto: false },
    vault: { label: 'Credential Vault', description: 'Access/modify credentials', canAuto: false },
    agentComms: { label: 'Agent Comms', description: 'Send messages to agents', canAuto: true },
    settings: { label: 'Settings', description: 'Change system configuration', canAuto: false },
};

const MODE_CONFIG: Record<OracleMode, { ledClass: string; label: string; desc: string }> = {
    auto: { ledClass: 'oracle-mode-led--auto', label: 'AUTO', desc: 'Oracle operates independently within permissions' },
    supervised: { ledClass: 'oracle-mode-led--supervised', label: 'SUPERVISED', desc: 'Oracle suggests, you approve each action' },
    manual: { ledClass: 'oracle-mode-led--manual', label: 'MANUAL', desc: 'Oracle is passive — you control everything' },
    offline: { ledClass: 'oracle-mode-led--manual', label: 'OFFLINE', desc: 'Oracle is disconnected' },
};

const STATUS_LED: Record<string, string> = {
    executed: 'var(--orc-led-green)', approved: 'var(--orc-led-green)',
    denied: 'var(--orc-led-red)', pending: 'var(--orc-led-amber)',
};

const MODE_STAT_COLORS: Record<string, string> = {
    auto: 'var(--orc-led-green)', supervised: 'var(--orc-led-amber)', manual: 'var(--orc-led-red)',
};

// ─── Permission Row ───

function PermissionRow({ system }: { system: OracleSystem }) {
    const { permissions, setPermission } = useOracleStore();
    const meta = SYSTEM_META[system];
    const current = permissions[system];
    const levels: PermissionLevel[] = meta.canAuto ? ['auto', 'supervised', 'manual'] : ['supervised', 'manual'];
    const IconComponent = SYSTEM_ICONS[system];

    return (
        <div className="oracle-perm-row">
            <div className="oracle-perm-info">
                <span className="oracle-perm-icon">
                    <IconComponent size={14} />
                </span>
                <div className="oracle-perm-text">
                    <span className="oracle-perm-label">{meta.label}</span>
                    <span className="oracle-perm-desc">{meta.description}</span>
                </div>
            </div>
            <div className="oracle-perm-toggle">
                {levels.map(level => (
                    <button
                        key={level}
                        className={`oracle-perm-btn ${current === level ? 'active' : ''}`}
                        data-level={level}
                        onClick={() => setPermission(system, level)}
                    >
                        {level.toUpperCase()}
                    </button>
                ))}
                {!meta.canAuto && (
                    <span className="oracle-perm-lock" title="Canon restriction: cannot be set to AUTO">
                        <ShieldKeyIcon size={10} />
                    </span>
                )}
            </div>
        </div>
    );
}

// ─── Action Log Entry ───

function ActionLogEntry({ action }: { action: OracleAction }) {
    const { approveAction, denyAction } = useOracleStore();
    const time = new Date(action.timestamp);
    const timeStr = time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });

    return (
        <div className="oracle-log-entry">
            <div className="oracle-log-dot" style={{ background: STATUS_LED[action.status], color: STATUS_LED[action.status] }} />
            <div className="oracle-log-content">
                <div className="oracle-log-header">
                    <span className="oracle-log-status" style={{ color: STATUS_LED[action.status] }}>
                        {action.status === 'pending' ? '…' : action.status === 'denied' ? '✗' : '✓'}
                    </span>
                    <span className="oracle-log-action">{action.action}</span>
                    <span className="oracle-log-mode" style={{
                        color: MODE_STAT_COLORS[action.mode] || '#666',
                    }}>
                        {action.mode}
                    </span>
                    <span className="oracle-log-time">{timeStr}</span>
                </div>
                {action.detail && <div className="oracle-log-detail">{action.detail}</div>}
                {action.status === 'pending' && (
                    <div className="oracle-log-actions">
                        <button className="oracle-approve-btn" onClick={() => approveAction(action.id)}>✓ APPROVE</button>
                        <button className="oracle-deny-btn" onClick={() => denyAction(action.id)}>✗ DENY</button>
                    </div>
                )}
            </div>
        </div>
    );
}

// ─── Main Oracle Page ───

export function OraclePage() {
    const { mode, setMode, connected, actionsPerMinute, actionLog, permissions } = useOracleStore();
    const [activeSection, setActiveSection] = useState<'overview' | 'permissions' | 'log'>('overview');
    const modeCfg = MODE_CONFIG[mode];

    const systems = Object.keys(SYSTEM_META) as OracleSystem[];
    const autoCount = systems.filter(s => permissions[s] === 'auto').length;
    const supervisedCount = systems.filter(s => permissions[s] === 'supervised').length;
    const manualCount = systems.filter(s => permissions[s] === 'manual').length;

    return (
        <div className="oracle-page">
            {/* Header */}
            <div className="oracle-header">
                <div className="oracle-header-left">
                    <span className="oracle-header-icon">
                        <BoltIcon size={22} />
                    </span>
                    <div>
                        <div className="oracle-title">Aether Oracle</div>
                        <div className="oracle-subtitle">Autonomous Operations Manager</div>
                    </div>
                </div>
                <div className="oracle-header-right">
                    <div className="oracle-connection" style={{ color: connected ? 'var(--orc-led-green)' : 'var(--orc-led-red)' }}>
                        <span className={`oracle-conn-led ${connected ? 'oracle-conn-led--on' : 'oracle-conn-led--off'}`} />
                        {connected ? 'ONLINE' : 'OFFLINE'}
                    </div>
                    <div className="oracle-apm">
                        <span className="oracle-apm-value">{actionsPerMinute.toFixed(1)}</span>
                        <span className="oracle-apm-label">act/min</span>
                    </div>
                </div>
            </div>

            {/* Section Tabs */}
            <div className="oracle-tabs">
                {(['overview', 'permissions', 'log'] as const).map(tab => (
                    <button
                        key={tab}
                        className={`oracle-tab ${activeSection === tab ? 'active' : ''}`}
                        onClick={() => setActiveSection(tab)}
                    >
                        {tab.toUpperCase()}
                    </button>
                ))}
            </div>

            {/* Section Content */}
            <div className="oracle-content">

                {/* ─── Overview ─── */}
                {activeSection === 'overview' && (
                    <div className="oracle-overview">
                        {/* Global Mode Selector */}
                        <div className="oracle-card oracle-mode-card">
                            <div className="oracle-card-header">
                                <span>Global Mode</span>
                            </div>
                            <div className="oracle-mode-grid">
                                {(Object.keys(MODE_CONFIG) as OracleMode[]).filter(m => m !== 'offline').map(m => {
                                    const cfg = MODE_CONFIG[m];
                                    return (
                                        <button
                                            key={m}
                                            className={`oracle-mode-btn ${mode === m ? 'active' : ''}`}
                                            onClick={() => setMode(m)}
                                        >
                                            <span className={`oracle-mode-led ${cfg.ledClass}`} />
                                            <span className="oracle-mode-label">{cfg.label}</span>
                                            <span className="oracle-mode-desc">{cfg.desc}</span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Stats Cards */}
                        <div className="oracle-stats-row">
                            <div className="oracle-stat-card">
                                <div className="oracle-stat-value" style={{ color: 'var(--orc-led-green)' }}>{autoCount}</div>
                                <div className="oracle-stat-label">Auto Systems</div>
                            </div>
                            <div className="oracle-stat-card">
                                <div className="oracle-stat-value" style={{ color: 'var(--orc-led-amber)' }}>{supervisedCount}</div>
                                <div className="oracle-stat-label">Supervised</div>
                            </div>
                            <div className="oracle-stat-card">
                                <div className="oracle-stat-value" style={{ color: 'var(--orc-led-red)' }}>{manualCount}</div>
                                <div className="oracle-stat-label">Manual Only</div>
                            </div>
                            <div className="oracle-stat-card">
                                <div className="oracle-stat-value" style={{ color: 'var(--orc-text)' }}>{actionLog.length}</div>
                                <div className="oracle-stat-label">Actions Logged</div>
                            </div>
                        </div>

                        {/* Recent Actions Preview */}
                        <div className="oracle-card">
                            <div className="oracle-card-header">
                                <span>Recent Oracle Actions</span>
                                <button className="oracle-see-all" onClick={() => setActiveSection('log')}>SEE ALL →</button>
                            </div>
                            <div className="oracle-log-list">
                                {actionLog.slice(0, 4).map(action => (
                                    <ActionLogEntry key={action.id} action={action} />
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* ─── Permissions ─── */}
                {activeSection === 'permissions' && (
                    <div className="oracle-permissions">
                        <div className="oracle-card">
                            <div className="oracle-card-header">
                                <span>Per-System Permissions</span>
                                <span className="oracle-card-hint">Configure what Oracle can do in each subsystem</span>
                            </div>
                            <div className="oracle-perm-list">
                                {systems.map(system => (
                                    <PermissionRow key={system} system={system} />
                                ))}
                            </div>
                        </div>

                        <div className="oracle-canon-notice">
                            <span className="oracle-canon-icon">
                                <ShieldKeyIcon size={14} />
                            </span>
                            <div>
                                <strong>Canon Restriction:</strong> Credential Vault and Settings can never be set to AUTO mode.
                                The Oracle can request escalation via Co-Agency but cannot unilaterally modify credentials or system configuration.
                            </div>
                        </div>
                    </div>
                )}

                {/* ─── Action Log ─── */}
                {activeSection === 'log' && (
                    <div className="oracle-log-section">
                        <div className="oracle-card">
                            <div className="oracle-card-header">
                                <span>Full Action Log</span>
                                <span className="oracle-card-hint">{actionLog.length} entries</span>
                            </div>
                            <div className="oracle-log-list oracle-log-full">
                                {actionLog.length === 0 ? (
                                    <div className="oracle-log-empty">No actions recorded yet</div>
                                ) : (
                                    actionLog.map(action => (
                                        <ActionLogEntry key={action.id} action={action} />
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
