import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSessionStore, type SessionState } from '../store/sessionStore';
import { useAIMOS } from '../hooks/useAIMOS';
import * as basClient from '../services/basClient';

// ─── Types ───

interface HealthCheckResult {
    sessionId: string;
    provider: string;
    status: 'healthy' | 'degraded' | 'critical' | 'offline';
    score: number; // 0-100
    selectors: SelectorCheck[];
    lastCheck: number;
    cookieFresh: boolean;
    responseTime: number;
    browserStatus?: string; // idle | navigating | automating | error
    browserUrl?: string;
}

interface SelectorCheck {
    name: string;
    selector: string;
    status: 'found' | 'changed' | 'missing';
    lastSeen: number;
}

interface BASHealthState {
    online: boolean;
    status: string;
    services: Record<string, string>;
    lastPing: number;
    pingMs: number;
}

// ─── Component ───

export function SessionHealthPage() {
    const { sessions } = useSessionStore();
    const aimos = useAIMOS({ pollDomains: ['messages'] });
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(30);
    const [countdown, setCountdown] = useState(30);
    const [lastFullCheck, setLastFullCheck] = useState(Date.now());
    const [expandedSession, setExpandedSession] = useState<string | null>(null);

    // ─── BAS Health State ───
    const [basHealth, setBASHealth] = useState<BASHealthState>({
        online: false,
        status: 'unknown',
        services: {},
        lastPing: 0,
        pingMs: 0,
    });
    const [browserStatuses, setBrowserStatuses] = useState<Record<string, { status: string; url?: string; responseTime: number }>>({});

    // Poll BAS health + browser statuses
    const pollBASHealth = useCallback(async () => {
        const start = performance.now();
        try {
            const health = await basClient.checkBASHealth();
            const pingMs = Math.round(performance.now() - start);
            setBASHealth({
                online: health.status === 'ok',
                status: health.status,
                services: health.services || {},
                lastPing: Date.now(),
                pingMs,
            });
        } catch {
            setBASHealth(prev => ({
                ...prev,
                online: false,
                status: 'unreachable',
                lastPing: Date.now(),
                pingMs: Math.round(performance.now() - start),
            }));
        }

        // Query individual browser statuses for sessions with browserIds
        const newStatuses: typeof browserStatuses = {};
        for (const session of Object.values(sessions)) {
            if (session.browserId) {
                const bStart = performance.now();
                try {
                    const result = await basClient.getBrowserStatus(session.browserId);
                    newStatuses[session.sessionId] = {
                        status: result.status?.status || 'unknown',
                        url: result.status?.url,
                        responseTime: Math.round(performance.now() - bStart),
                    };
                } catch {
                    newStatuses[session.sessionId] = {
                        status: 'unreachable',
                        responseTime: Math.round(performance.now() - bStart),
                    };
                }
            }
        }
        if (Object.keys(newStatuses).length > 0) {
            setBrowserStatuses(newStatuses);
        }
    }, [sessions]);

    // Initial + periodic health polling
    useEffect(() => {
        pollBASHealth();
    }, [lastFullCheck, pollBASHealth]);

    // Derive health checks from session store + live BAS data
    const healthChecks: HealthCheckResult[] = useMemo(() => {
        return Object.values(sessions).map((session: SessionState) => {
            const selectors: SelectorCheck[] = session.overlayMarkers.map(m => ({
                name: m.label,
                selector: m.selector || '',
                status: m.status === 'healthy' ? 'found' : m.status === 'missing' ? 'missing' : 'changed',
                lastSeen: Date.now() - (m.status === 'healthy' ? 0 : 3600000),
            }));

            const foundCount = selectors.filter(s => s.status === 'found').length;
            const total = selectors.length;
            const score = total > 0 ? Math.round((foundCount / total) * 100) : 0;

            let status: HealthCheckResult['status'] = 'healthy';
            if (score < 50) status = 'critical';
            else if (score < 80) status = 'degraded';
            if (session.status === 'disconnected' || session.status === 'error') status = 'offline';

            const browserInfo = browserStatuses[session.sessionId];

            return {
                sessionId: session.sessionId,
                provider: session.provider,
                status,
                score: session.health || score,
                selectors,
                lastCheck: lastFullCheck,
                cookieFresh: session.status === 'connected',
                responseTime: browserInfo?.responseTime ?? 0,
                browserStatus: browserInfo?.status,
                browserUrl: browserInfo?.url,
            };
        });
    }, [sessions, lastFullCheck, browserStatuses]);

    // Countdown timer
    useEffect(() => {
        if (!autoRefresh) return;
        const timer = setInterval(() => {
            setCountdown(prev => {
                if (prev <= 1) {
                    setLastFullCheck(Date.now());
                    return refreshInterval;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [autoRefresh, refreshInterval]);

    const runManualCheck = useCallback(() => {
        setLastFullCheck(Date.now());
        setCountdown(refreshInterval);
    }, [refreshInterval]);

    // Aggregate stats
    const stats = useMemo(() => {
        const total = healthChecks.length;
        const healthy = healthChecks.filter(h => h.status === 'healthy').length;
        const degraded = healthChecks.filter(h => h.status === 'degraded').length;
        const critical = healthChecks.filter(h => h.status === 'critical').length;
        const offline = healthChecks.filter(h => h.status === 'offline').length;
        const avgScore = total > 0 ? Math.round(healthChecks.reduce((s, h) => s + h.score, 0) / total) : 0;
        const totalSelectors = healthChecks.reduce((s, h) => s + h.selectors.length, 0);
        const foundSelectors = healthChecks.reduce((s, h) => s + h.selectors.filter(sel => sel.status === 'found').length, 0);
        return { total, healthy, degraded, critical, offline, avgScore, totalSelectors, foundSelectors };
    }, [healthChecks]);

    const statusColors: Record<string, string> = {
        healthy: '#4ecdc4',
        degraded: '#ffd93d',
        critical: '#ff6b6b',
        offline: '#666',
    };

    const selectorStatusIcons: Record<string, { icon: string; color: string }> = {
        found: { icon: '✓', color: '#4ecdc4' },
        changed: { icon: '◎', color: '#ffd93d' },
        missing: { icon: '✗', color: '#ff6b6b' },
    };

    const providerEmoji: Record<string, string> = {
        chatgpt: '⚡',
        gemini: '✦',
        claude: '◈',
        perplexity: '◇',
        'gemini-cli': '⌨',
        local: '🖥',
    };

    const timeAgo = (ts: number) => {
        if (ts === 0) return 'never';
        const secs = Math.floor((Date.now() - ts) / 1000);
        if (secs < 5) return 'just now';
        if (secs < 60) return `${secs}s ago`;
        if (secs < 3600) return `${Math.floor(secs / 60)}m ago`;
        return `${Math.floor(secs / 3600)}h ago`;
    };

    const browserStatusLabel = (bs?: string) => {
        if (!bs) return null;
        const colors: Record<string, string> = {
            idle: '#4ecdc4',
            navigating: '#ffd93d',
            automating: '#61dafb',
            error: '#ff6b6b',
            unreachable: '#666',
            unknown: '#888',
        };
        return (
            <span className="health-browser-status" style={{ color: colors[bs] || '#888' }}>
                ● {bs.toUpperCase()}
            </span>
        );
    };

    return (
        <div className="health-page">
            {/* ─── Header ─── */}
            <div className="health-page-header">
                <div className="health-page-header-left">
                    <span className="health-page-title">◎ Fleet Health Monitor</span>
                    <span className="health-page-subtitle">
                        {stats.foundSelectors}/{stats.totalSelectors} selectors valid
                    </span>
                </div>
                <div className="health-page-header-right">
                    <label className="health-auto-refresh">
                        <input
                            type="checkbox"
                            checked={autoRefresh}
                            onChange={e => setAutoRefresh(e.target.checked)}
                        />
                        Auto-refresh
                    </label>
                    <select
                        className="health-interval-select"
                        value={refreshInterval}
                        onChange={e => { setRefreshInterval(Number(e.target.value)); setCountdown(Number(e.target.value)); }}
                    >
                        <option value={10}>10s</option>
                        <option value={30}>30s</option>
                        <option value={60}>60s</option>
                        <option value={120}>2m</option>
                    </select>
                    {autoRefresh && (
                        <span className="health-countdown">
                            Next check: {countdown}s
                        </span>
                    )}
                    <button className="health-check-btn" onClick={runManualCheck}>
                        ⟳ Check Now
                    </button>
                </div>
            </div>

            {/* ─── BAS Connection Panel ─── */}
            <div className="health-bas-panel" style={{
                display: 'flex', alignItems: 'center', gap: 16,
                padding: '8px 16px', margin: '0 0 12px 0',
                background: basHealth.online ? 'rgba(78, 205, 196, 0.06)' : 'rgba(255, 107, 107, 0.06)',
                border: `1px solid ${basHealth.online ? 'rgba(78, 205, 196, 0.2)' : 'rgba(255, 107, 107, 0.2)'}`,
                borderRadius: 8, fontSize: 13,
            }}>
                <span style={{
                    display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                    background: basHealth.online ? '#4ecdc4' : '#ff6b6b',
                    boxShadow: basHealth.online ? '0 0 8px rgba(78,205,196,0.6)' : '0 0 8px rgba(255,107,107,0.6)',
                }} />
                <span style={{ fontWeight: 600, color: basHealth.online ? '#4ecdc4' : '#ff6b6b' }}>
                    BAS {basHealth.online ? 'ONLINE' : 'OFFLINE'}
                </span>
                <span style={{ opacity: 0.6 }}>Port 5002</span>
                {basHealth.online && (
                    <>
                        <span style={{ opacity: 0.5 }}>·</span>
                        <span style={{ opacity: 0.7 }}>
                            {Object.entries(basHealth.services).map(([k, v]) => `${k}: ${v}`).join(' · ')}
                        </span>
                        <span style={{ opacity: 0.5 }}>·</span>
                        <span style={{ opacity: 0.7, fontFamily: 'monospace' }}>
                            {basHealth.pingMs}ms ping
                        </span>
                    </>
                )}
                <span style={{ marginLeft: 'auto', opacity: 0.5 }}>
                    Last: {timeAgo(basHealth.lastPing)}
                </span>
            </div>

            {/* ─── Summary Cards ─── */}
            <div className="health-summary-bar">
                <div className="health-summary-card">
                    <div className="health-summary-value" style={{ color: '#4ecdc4' }}>{stats.healthy}</div>
                    <div className="health-summary-label">Healthy</div>
                </div>
                <div className="health-summary-card">
                    <div className="health-summary-value" style={{ color: '#ffd93d' }}>{stats.degraded}</div>
                    <div className="health-summary-label">Degraded</div>
                </div>
                <div className="health-summary-card">
                    <div className="health-summary-value" style={{ color: '#ff6b6b' }}>{stats.critical}</div>
                    <div className="health-summary-label">Critical</div>
                </div>
                <div className="health-summary-card">
                    <div className="health-summary-value" style={{ color: '#666' }}>{stats.offline}</div>
                    <div className="health-summary-label">Offline</div>
                </div>
                <div className="health-summary-card avg">
                    <div className="health-summary-value" style={{ color: stats.avgScore > 80 ? '#4ecdc4' : stats.avgScore > 50 ? '#ffd93d' : '#ff6b6b' }}>
                        {stats.avgScore}%
                    </div>
                    <div className="health-summary-label">Avg Score</div>
                </div>
            </div>

            {/* ─── Session Cards ─── */}
            <div className="health-sessions">
                {healthChecks.map(check => (
                    <div
                        key={check.sessionId}
                        className={`health-session-card ${check.status} ${expandedSession === check.sessionId ? 'expanded' : ''}`}
                        onClick={() => setExpandedSession(expandedSession === check.sessionId ? null : check.sessionId)}
                    >
                        <div className="health-session-header">
                            <span className="health-session-provider">
                                <span className="health-provider-emoji">{providerEmoji[check.provider] || '◆'}</span>
                                {check.provider.toUpperCase()}
                            </span>
                            <span className="health-session-score" style={{ color: statusColors[check.status] }}>
                                {check.score}%
                            </span>
                            <span className="health-session-status-badge" style={{ background: `${statusColors[check.status]}18`, color: statusColors[check.status] }}>
                                {check.status.toUpperCase()}
                            </span>
                            {browserStatusLabel(check.browserStatus)}
                            <span className="health-session-spacer" />
                            <span className="health-session-meta">
                                🕰 {timeAgo(check.lastCheck)} · ⚡ {check.responseTime > 0 ? `${check.responseTime}ms` : '—'}
                            </span>
                            <span className="health-session-cookie" style={{ color: check.cookieFresh ? '#4ecdc4' : '#ff6b6b' }}>
                                {check.cookieFresh ? '🍪 Fresh' : '🍪 Stale'}
                            </span>
                        </div>

                        {/* Browser URL (if connected) */}
                        {check.browserUrl && (
                            <div style={{ fontSize: 11, opacity: 0.5, fontFamily: 'monospace', marginTop: 4, paddingLeft: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                🔗 {check.browserUrl}
                            </div>
                        )}

                        {/* Health bar */}
                        <div className="health-session-bar">
                            <div
                                className="health-session-bar-fill"
                                style={{
                                    width: `${check.score}%`,
                                    background: `linear-gradient(90deg, ${statusColors[check.status]}, ${statusColors[check.status]}88)`,
                                }}
                            />
                        </div>

                        {/* Selector grid (expanded) */}
                        {expandedSession === check.sessionId && (
                            <div className="health-selector-grid">
                                {check.selectors.map((sel, i) => {
                                    const si = selectorStatusIcons[sel.status];
                                    return (
                                        <div key={i} className={`health-selector-item ${sel.status}`}>
                                            <span className="health-selector-icon" style={{ color: si.color }}>{si.icon}</span>
                                            <span className="health-selector-name">{sel.name}</span>
                                            <code className="health-selector-css">{sel.selector}</code>
                                            <span className="health-selector-time">{timeAgo(sel.lastSeen)}</span>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
