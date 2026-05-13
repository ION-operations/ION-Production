import React, { useEffect, useRef, useState } from 'react';
import { useShellStore, WORKSPACES, NAV_GROUPS } from '../../store/shellStore';
import { getConnectionState, onConnectionChange, getLastLatency, type ConnectionState } from '../../services/mcpClient';

export function TopBar() {
    const {
        activeWorkspace,
        setActiveWorkspace,
        openNavGroup,
        setOpenNavGroup,
    } = useShellStore();

    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setOpenNavGroup(null);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, [setOpenNavGroup]);

    const activeWs = WORKSPACES.find((w) => w.id === activeWorkspace);
    const activeGroup = activeWs?.navGroup;

    // ─── Live clock ───
    const [time, setTime] = useState('');
    useEffect(() => {
        const tick = () => {
            const now = new Date();
            setTime(
                now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
            );
        };
        tick();
        const id = setInterval(tick, 1000);
        return () => clearInterval(id);
    }, []);

    // ─── Live MCP connection state ───
    const [mcpState, setMcpState] = useState<ConnectionState>(getConnectionState());
    const [mcpLatency, setMcpLatency] = useState(getLastLatency());
    useEffect(() => {
        const unsub = onConnectionChange((state) => {
            setMcpState(state);
            setMcpLatency(getLastLatency());
        });
        return () => { unsub(); };
    }, []);

    return (
        <div className="topbar textured">
            {/* Logo */}
            <div className="topbar-logo">
                <div>
                    <div className="topbar-logo-text">J.A.R.V.I.S.</div>
                    <div className="topbar-logo-version">AIM-OS v2.0</div>
                </div>
            </div>

            {/* Nav Groups */}
            <div className="topbar-nav-groups" ref={dropdownRef}>
                {NAV_GROUPS.map((group) => (
                    <div className="topbar-nav-group" key={group.id}>
                        <button
                            className={`topbar-nav-group-label ${activeGroup === group.id ? 'active' : ''}`}
                            onClick={() => setOpenNavGroup(group.id)}
                        >
                            {group.label}
                        </button>

                        {openNavGroup === group.id && (
                            <div className="topbar-nav-group-dropdown">
                                {WORKSPACES.filter((w) => w.navGroup === group.id).map((ws) => (
                                    <button
                                        key={ws.id}
                                        className={`topbar-workspace-item ${activeWorkspace === ws.id ? 'active' : ''}`}
                                        onClick={() => setActiveWorkspace(ws.id)}
                                    >
                                        <span className="ws-icon" style={{ fontFamily: 'var(--font-mono)', fontSize: 14 }}>
                                            {ws.icon}
                                        </span>
                                        <span>{ws.title}</span>
                                        {!ws.primary && (
                                            <span style={{ marginLeft: 'auto', fontSize: 9, color: 'var(--text-dim)' }}>
                                                2ND
                                            </span>
                                        )}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Right section — LIVE connection status */}
            <div className="topbar-right">
                <div className="topbar-status-group">
                    <span className="mono-sm" style={{ marginRight: 4 }}>MCP</span>
                    <span className={`status-led ${mcpState === 'connected' ? 'live' : mcpState === 'connecting' ? 'idle' : 'offline'}`} />
                    {mcpState === 'connected' && (
                        <span className="mono-sm" style={{ marginLeft: 4, color: 'var(--text-dim)' }}>
                            {mcpLatency}ms
                        </span>
                    )}
                    <span className="mono-sm" style={{ marginLeft: 8, marginRight: 4 }}>BAS</span>
                    <span className="status-led offline" />
                </div>
                <div className="topbar-clock">{time}</div>
            </div>
        </div>
    );
}
