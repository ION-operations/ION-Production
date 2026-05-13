import React from 'react';
import { useShellStore } from '../../store/shellStore';
import { MOCK_AGENTS, MOCK_SUBSYSTEMS } from '../../data/mockData';

export function LeftIconBar() {
    const { leftDrawerOpen, toggleLeftDrawer } = useShellStore();

    const icons = [
        { id: 'fleet', icon: '⬡', label: 'Agent Fleet' },
        { id: 'status', icon: '◎', label: 'System Status' },
    ];

    return (
        <div className="left-icon-bar textured">
            {icons.map((item) => (
                <button
                    key={item.id}
                    className={`icon-bar-btn ${leftDrawerOpen ? 'active' : ''}`}
                    title={item.label}
                    onClick={toggleLeftDrawer}
                >
                    <span style={{ fontSize: 16 }}>{item.icon}</span>
                </button>
            ))}

            <div className="icon-bar-separator" />

            {/* Quick agent status LEDs */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'center', paddingTop: 4 }}>
                {MOCK_AGENTS.slice(0, 4).map((a) => (
                    <span
                        key={a.id}
                        className={`status-led ${a.status === 'active' ? 'live' : a.status === 'idle' ? 'idle' : 'offline'}`}
                        title={`${a.name}: ${a.status}`}
                    />
                ))}
            </div>
        </div>
    );
}


export function LeftDrawer() {
    const { leftDrawerOpen } = useShellStore();

    return (
        <div className={`left-drawer ${leftDrawerOpen ? '' : 'collapsed'}`}>
            {leftDrawerOpen && (
                <>
                    {/* Agent Fleet Section */}
                    <div className="drawer-section" style={{ flex: '0 0 auto', borderBottom: '1px solid var(--border-subtle)' }}>
                        <div className="drawer-section-header">
                            <span className="drawer-section-title">Agent Fleet</span>
                            <span className="mono-sm">{MOCK_AGENTS.filter((a) => a.status === 'active').length}/{MOCK_AGENTS.length}</span>
                        </div>
                        <div className="drawer-agent-list">
                            {MOCK_AGENTS.map((agent) => (
                                <div key={agent.id} className="drawer-agent-item">
                                    <div className="drawer-agent-initial">{agent.name[0]}</div>
                                    <span
                                        className={`status-led ${agent.status === 'active' ? 'live' :
                                            agent.status === 'idle' ? 'idle' :
                                                agent.status === 'error' ? 'critical' : 'offline'
                                            }`}
                                    />
                                    <span className="drawer-agent-name">{agent.name}</span>
                                    <span className="drawer-agent-status">{agent.rank}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* System Status Section */}
                    <div className="drawer-section">
                        <div className="drawer-section-header">
                            <span className="drawer-section-title">System Status</span>
                            <span className="mono-sm">
                                {MOCK_SUBSYSTEMS.filter((s) => s.status === 'healthy').length}/{MOCK_SUBSYSTEMS.length}
                            </span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            {MOCK_SUBSYSTEMS.map((sys) => (
                                <div key={sys.acronym} className="drawer-sys-item">
                                    <span
                                        className={`status-led ${sys.status === 'healthy' ? 'live' :
                                            sys.status === 'degraded' ? 'warning' :
                                                sys.status === 'down' ? 'critical' : 'offline'
                                            }`}
                                    />
                                    <span className="drawer-sys-acronym">{sys.acronym}</span>
                                    <span className="drawer-sys-label">{sys.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
