import React, { useState, useEffect } from 'react';
import { useShellStore } from '../../store/shellStore';
import { useAIMOS } from '../../hooks/useAIMOS';

const TABS = [
    { id: 'activity', label: 'Activity Feed' },
    { id: 'terminal', label: 'Terminal' },
    { id: 'diagnostics', label: 'Diagnostics' },
];

export function BottomBar() {
    const { bottomExpanded, toggleBottom, activeBottomTab, setBottomTab } = useShellStore();
    const aimos = useAIMOS({
        pollDomains: ['timeline', 'problems', 'memory'],
        pollInterval: 15000,
    });

    // Last timeline event for collapsed preview
    const lastEvent = aimos.timeline[0];

    return (
        <div className={`bottom-bar ${bottomExpanded ? 'expanded' : ''}`}>
            {/* Tab row */}
            <div className="bottom-bar-tabs">
                <button className="bottom-expand-btn" onClick={toggleBottom} title={bottomExpanded ? 'Collapse' : 'Expand'}>
                    <span style={{ fontSize: 12, transform: bottomExpanded ? 'rotate(180deg)' : 'none', display: 'inline-block', transition: 'transform 0.2s' }}>
                        ▴
                    </span>
                </button>
                {TABS.map((tab) => (
                    <button
                        key={tab.id}
                        className={`bottom-tab ${activeBottomTab === tab.id ? 'active' : ''}`}
                        onClick={() => setBottomTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
                {!bottomExpanded && (
                    <div className="bottom-bar-status">
                        {/* Last event preview — LIVE from timeline */}
                        <span className="mono-sm" style={{ color: 'var(--text-dim)' }}>
                            {lastEvent
                                ? `${lastEvent.prompt_id?.slice(0, 8) || '—'}: ${(lastEvent.user_input || '').slice(0, 50)}…`
                                : aimos.connected ? 'No recent events' : 'MCP offline'
                            }
                        </span>
                        {/* Connection LEDs — LIVE */}
                        <span className="mono-sm" style={{ marginLeft: 8 }}>MCP</span>
                        <span className={`status-led ${aimos.connected ? 'live' : 'offline'}`} />
                        {aimos.connected && (
                            <span className="mono-sm" style={{ marginLeft: 2, color: 'var(--text-dim)' }}>{aimos.latency}ms</span>
                        )}
                        <span className="mono-sm" style={{ marginLeft: 4 }}>BAS</span>
                        <span className="status-led offline" />
                        <span className="mono-sm" style={{ marginLeft: 4 }}>SEER</span>
                        <span className="status-led offline" />
                    </div>
                )}
            </div>

            {/* Expanded content */}
            {bottomExpanded && (
                <div className="bottom-bar-content">
                    {activeBottomTab === 'activity' && <ActivityFeed aimos={aimos} />}
                    {activeBottomTab === 'terminal' && <TerminalView aimos={aimos} />}
                    {activeBottomTab === 'diagnostics' && <DiagnosticsView aimos={aimos} />}
                </div>
            )}
        </div>
    );
}


function ActivityFeed({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    return (
        <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span className="engraved">ACTIVITY FEED</span>
                {aimos.connected && <span className="status-led live" style={{ width: 4, height: 4 }} />}
                {!aimos.connected && (
                    <span style={{
                        fontFamily: 'var(--font-mono)', fontSize: 9, fontWeight: 700,
                        color: 'var(--text-dim)', background: 'rgba(255,255,255,0.05)',
                        padding: '1px 6px', borderRadius: 3, letterSpacing: '0.08em',
                    }}>OFFLINE</span>
                )}
            </div>
            {aimos.timeline.length === 0 ? (
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-dim)', padding: 8 }}>
                    {aimos.connected ? 'No timeline events yet' : 'Awaiting MCP connection…'}
                </div>
            ) : (
                aimos.timeline.slice(0, 12).map((evt, i) => (
                    <div key={evt.prompt_id || i} className="activity-item">
                        <span className="activity-time">{evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' }) : '—'}</span>
                        <span className="activity-source">{evt.prompt_id?.slice(0, 8) || '—'}</span>
                        <span className="activity-text" style={{ color: 'var(--text-mid)' }}>
                            {(evt.user_input || '').slice(0, 100)}
                        </span>
                    </div>
                ))
            )}
        </div>
    );
}


function TerminalView({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    return (
        <div>
            <div className="engraved" style={{ marginBottom: 8 }}>TERMINAL</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                <div style={{ color: 'var(--led-green)' }}>$ jarvis --status</div>
                <div style={{ color: 'var(--text-mid)', marginTop: 4 }}>
                    AIM-OS v2.0 — 14 subsystems · 92 MCP tools · 6 agents<br />
                    MCP Server: localhost:5001{' '}
                    <span style={{ color: aimos.connected ? 'var(--led-green)' : 'var(--text-dim)' }}>
                        {aimos.connected ? `● CONNECTED (${aimos.latency}ms)` : '○ OFFLINE'}
                    </span><br />
                    JOC Surface: localhost:5011{' '}
                    <span style={{ color: 'var(--led-green)' }}>● SERVING</span><br />
                    BAS/SEER: localhost:5002{' '}
                    <span style={{ color: 'var(--text-dim)' }}>○ OFFLINE</span><br />
                    <br />
                    Memory atoms: {aimos.memory?.total_atoms ?? '—'} ·{' '}
                    Goals: {aimos.goals.length || '—'} ·{' '}
                    Problems: {aimos.problems ? `${aimos.problems.errors || 0}E ${aimos.problems.warnings || 0}W` : '—'}
                </div>
                <div style={{ color: 'var(--led-green)', marginTop: 8 }}>$ _</div>
            </div>
        </div>
    );
}


function DiagnosticsView({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    return (
        <div>
            <div className="engraved" style={{ marginBottom: 8 }}>MCP DIAGNOSTICS</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-mid)' }}>
                <div>Connection: <span style={{ color: aimos.connected ? 'var(--led-green)' : 'var(--text-dim)' }}>
                    {aimos.health.toUpperCase()}
                </span></div>
                <div>Latency: <span style={{ color: 'var(--text-bright)' }}>{aimos.connected ? `${aimos.latency}ms` : '—'}</span></div>
                <div>Total MCP Tools: <span style={{ color: 'var(--text-bright)' }}>92</span></div>
                <div>CMC Atoms: <span style={{ color: 'var(--text-bright)' }}>{aimos.memory?.total_atoms ?? '—'}</span></div>
                <div>CMC Molecules: <span style={{ color: 'var(--text-bright)' }}>{aimos.memory?.total_molecules ?? '—'}</span></div>
                <div>CMC Snapshots: <span style={{ color: 'var(--text-bright)' }}>{aimos.memory?.total_snapshots ?? '—'}</span></div>
                {aimos.consciousness && (
                    <>
                        <div style={{ marginTop: 4 }}>CAS Drift: <span style={{
                            color: (aimos.consciousness.cognitive_drift || 0) < 0.3 ? 'var(--led-green)' : 'var(--led-amber)',
                        }}>{((aimos.consciousness.cognitive_drift || 0) * 100).toFixed(1)}%</span></div>
                        <div>VIF κ: <span style={{ color: 'var(--led-green)' }}>
                            {(1 - (aimos.consciousness.failure_rate || 0)).toFixed(3)}
                        </span></div>
                    </>
                )}
                {aimos.problems && (
                    <div style={{ marginTop: 4 }}>
                        IDE: <span style={{ color: aimos.problems.errors ? 'var(--led-red)' : 'var(--text-mid)' }}>
                            {aimos.problems.errors || 0}E
                        </span>{' '}
                        <span style={{ color: aimos.problems.warnings ? 'var(--led-amber)' : 'var(--text-mid)' }}>
                            {aimos.problems.warnings || 0}W
                        </span>{' '}
                        <span style={{ color: 'var(--text-dim)' }}>
                            {aimos.problems.info || 0}I {aimos.problems.hints || 0}H
                        </span>
                    </div>
                )}
                <div style={{ marginTop: 8, color: 'var(--text-dim)' }}>
                    Last refresh: {aimos.lastRefresh ? new Date(aimos.lastRefresh).toLocaleTimeString('en-US', { hour12: false }) : '—'}
                </div>
            </div>
        </div>
    );
}
