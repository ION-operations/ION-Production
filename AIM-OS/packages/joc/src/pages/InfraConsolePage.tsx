// ═══════════════════════════════════════════════════════════════════
// INFRASTRUCTURE CONTROL PLANE — AIM-OS Service Registry & Health
// DXL Panavision aesthetic — matches Dashboard design language
//
// Zones:
//   1. System Bar — service count, MCP vitals, auto-refresh toggle
//   2. Main Column — Service registry LED panel, control actions
//   3. Side Column — MCP diagnostics LCD, dependency graph, health log
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useAIMOS } from '../hooks/useAIMOS';
import { useJOCStore } from '../store/jocStore';
import { usePageOracle, type OraclePageAction } from '../hooks/usePageOracle';
import { checkHealth, callTool, getLastLatency, mcp } from '../services/mcpClient';
import {
    RadarIcon, SatelliteIcon, ChipDieIcon, ConstellationIcon,
    RefreshCycleIcon, BoltIcon, LaunchVectorIcon, SignalPulseIcon,
} from '../components/icons';
import '../styles/infra.css';

// ─── Types ───

type ServiceStatus = 'UP' | 'DOWN' | 'DEGRADED' | 'UNKNOWN' | 'STARTING';
type ServiceKind = 'mcp' | 'web' | 'tunnel' | 'agent' | 'process';
type Criticality = 'P0' | 'P1' | 'P2';

interface ServiceDef {
    id: string;
    name: string;
    kind: ServiceKind;
    port?: number;
    transport?: string;
    criticality: Criticality;
    status: ServiceStatus;
    lastCheck?: string;
    lastError?: string;
    details?: Record<string, unknown>;
    startCmd?: string;
    dependsOn?: string[];
}

// ─── Service Registry ───

const SERVICE_REGISTRY: ServiceDef[] = [
    {
        id: 'lucid_mcp_core', name: 'Lucid MCP Core', kind: 'mcp',
        port: 5001, transport: 'stdio→http', criticality: 'P0', status: 'UNKNOWN',
        startCmd: 'node lucid_mcp_server.js',
        details: { tools: 92, transport: 'stdio', bridge: 'HTTP :5001' },
    },
    {
        id: 'mcp_sse_server', name: 'MCP SSE Server', kind: 'mcp',
        port: 8000, transport: 'sse', criticality: 'P0', status: 'UNKNOWN',
        startCmd: 'python scripts/mcp_sse_server.py',
        dependsOn: ['lucid_mcp_core'],
        details: { tools: 19, transport: 'sse', framework: 'FastMCP' },
    },
    {
        id: 'ngrok_tunnel', name: 'HTTPS Tunnel (ngrok)', kind: 'tunnel',
        criticality: 'P0', status: 'UNKNOWN',
        startCmd: 'python scripts/ngrok_tunnel.py',
        dependsOn: ['mcp_sse_server'],
        details: { provider: 'ngrok', purpose: 'ChatGPT ↔ MCP bridge' },
    },
    {
        id: 'http_fallback', name: 'HTTP Fallback Bridge', kind: 'mcp',
        port: 5001, transport: 'http', criticality: 'P0', status: 'UNKNOWN',
        startCmd: 'python scripts/mcp_http_fallback_server.py --port 5001',
        dependsOn: ['lucid_mcp_core'],
        details: { purpose: 'JOC ↔ MCP bridge', lazy: true },
    },
    {
        id: 'hhni_subsystem', name: 'HHNI Retrieval Engine', kind: 'process',
        criticality: 'P1', status: 'UNKNOWN',
        startCmd: 'python -c "from packages.hhni_lite import HierarchicalIndex; print(HierarchicalIndex)"',
        dependsOn: ['lucid_mcp_core'],
        details: { engine: 'Hierarchical Navigable Index', mode: 'fallback (torch-free)' },
    },
    {
        id: 'ai_engine_mcp', name: 'AI Engine v2.0', kind: 'mcp',
        transport: 'stdio', criticality: 'P1', status: 'UNKNOWN',
        startCmd: 'python scripts/ai_engine/ai_engine_mcp_server.py',
        details: { tools: 14, subsystems: 14 },
    },
    {
        id: 'joc_dev', name: 'JOC Dev Server', kind: 'web',
        port: 5011, criticality: 'P1', status: 'UNKNOWN',
        startCmd: 'npm run dev --prefix packages/joc',
        details: { framework: 'Vite + React + TypeScript' },
    },
    {
        id: 'gemini_bridge', name: 'Gemini Bridge', kind: 'process',
        criticality: 'P2', status: 'UNKNOWN',
        details: { type: 'Chrome Extension + Native Messaging Host' },
    },
];

// ─── Helpers ───

function fmt(n: number | undefined | null): string {
    if (n === undefined || n === null) return '—';
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return String(n);
}

function timeAgo(ts: number | string | undefined): string {
    if (!ts) return 'never';
    const t = typeof ts === 'string' ? new Date(ts).getTime() : ts;
    const secs = Math.floor((Date.now() - t) / 1000);
    if (secs < 5) return 'now';
    if (secs < 60) return `${secs}s`;
    if (secs < 3600) return `${Math.floor(secs / 60)}m`;
    return `${Math.floor(secs / 3600)}h`;
}

// ─── Component ───

export function InfraConsolePage() {
    const aimos = useAIMOS({ pollDomains: ['memory', 'consciousness', 'problems'] });
    const { addTab } = useJOCStore();
    const [services, setServices] = useState<ServiceDef[]>(SERVICE_REGISTRY);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastRefresh, setLastRefresh] = useState(0);
    const [infraHealth, setInfraHealth] = useState<Record<string, unknown> | null>(null);
    const [expandedService, setExpandedService] = useState<string | null>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [actionInProgress, setActionInProgress] = useState<string | null>(null);
    const [osProcesses, setOsProcesses] = useState<Array<{ Id: number; ProcessName: string; CPU: number; MemMB: number; UptimeMin: number }>>([]);
    const [diagLines, setDiagLines] = useState<Array<{ text: string; level: string }>>([]);
    const [isDiagRunning, setIsDiagRunning] = useState(false);
    const [tunnelConnections, setTunnelConnections] = useState<{
        cloudflare?: { running: boolean; tunnel_url?: string; chatgpt_sse_url?: string };
        relay?: { connected: boolean; relay_url?: string };
        subdomains: Array<{ name: string; url: string; status: 'UP' | 'DOWN' | 'PENDING'; latency?: number }>;
        updated_at?: string;
    }>({ subdomains: [] });
    const [securityReport, setSecurityReport] = useState<{
        auth_enforced?: boolean;
        api_keys?: Array<{ hash_prefix: string; label: string; use_count: number; last_used?: string }>;
        rate_limit?: { max_requests: number; window_seconds: number; active_ips: Record<string, number> };
        request_log?: { total_requests: number; blocked_requests: number; blocked_ips: Record<string, number>; active_ips: Record<string, number> };
        recent_requests?: Array<{ ip: string; path: string; method: string; blocked: boolean; reason: string; timestamp: string }>;
    } | null>(null);
    const [generatedKey, setGeneratedKey] = useState<string | null>(null);
    const [sentinelStatus, setSentinelStatus] = useState<{
        threat_level?: string; total_processed?: number; total_blocked?: number;
        total_honeypot_hits?: number; banned_count?: number;
        total_attacks_detected?: number;
        anomaly?: { baseline_rpm?: number; current_rpm?: number; std_dev?: number; data_minutes?: number };
        ip_profiles?: { total_ips_tracked?: number; suspicious_ips?: number; top_talkers?: Array<{ ip: string; requests: number; blocked: number }> };
        mcp_audit?: { total_calls?: number; unique_tools?: number; alerts?: number };
        file_integrity?: { files_monitored?: number; last_scan?: number; recent_changes?: Array<{ file: string; status: string }> };
        telemetry?: { events_total?: number; findings_total?: number; actions_total?: number; audit_ledger?: { total_entries?: number; chain_hash?: string }; chain_integrity?: { valid?: boolean; entries_checked?: number } };
        host_baselines?: { secrets?: { total_findings?: number; critical?: number; high?: number; last_scan?: string }; genomes?: { files_watched?: number; modified?: number; last_scan?: string }; outbound?: { total_connections?: number; unknown_connections?: number; last_scan?: string }; identity?: { known_signatures?: number } };
        sessions?: { active_sessions?: number; total_registered?: number; revoked?: number; agents?: string[]; last_registration?: string };
        wraith?: { patterns_loaded?: number; tests_run?: number; passed?: number; failed?: number; vulnerability_score?: number; last_run?: string };
        policies?: { total_policies?: number; active_policies?: number; total_enforced?: number; recent_enforcements?: number; last_enforcement?: string };
        governance?: { tools_governed?: number; critical_tools?: number; elevated_tools?: number; total_checked?: number; total_blocked?: number; total_sanitized?: number; block_rate?: number };
        phantom?: { adversaries_tracked?: number; active_engagements?: number; ethically_excluded?: number; total_cm_deployed?: number; countermeasures_available?: number; bait_credentials?: number };
        recon?: { ips_analyzed?: number; attack_tools_detected?: number; c2_indicators_found?: number; mitre_techniques_mapped?: number; known_tool_signatures?: number };
        chronicle?: { audit_entries?: number; chain_integrity?: string; tampering_detected?: boolean; active_incidents?: number; total_incidents?: number; playbooks_loaded?: number; chain_head?: string };
        nexus?: { defense_posture?: string; total_signals?: number; tracked_threats?: number; active_threats?: number; known_chains?: number; chain_matches?: number; adaptations_active?: number; signal_types?: number };
        uptime_seconds?: number;
    } | null>(null);
    const [sentinelFeed, setSentinelFeed] = useState<Array<{
        time: string; level: string; icon: string; message: string; text: string;
    }>>([]);
    const intervalRef = useRef<ReturnType<typeof setInterval>>();

    // ─── Oracle API Registration ───
    const oracleActions: OraclePageAction[] = useMemo(() => [
        {
            id: 'infra.refreshAll',
            label: 'Refresh All Health Checks',
            system: 'dispatch' as const,
            description: 'Run health probes against all registered services',
            minPermission: 'supervised' as const,
            execute: async () => {
                await runHealthChecks();
                return { success: true, message: 'All health checks refreshed' };
            },
        },
    ], []);

    usePageOracle('infra', {
        actions: oracleActions,
        getState: () => ({
            servicesUp: services.filter(s => s.status === 'UP').length,
            servicesTotal: services.length,
            mcpConnected: aimos.connected,
            lastRefresh,
        }),
    });

    // ─── Health Check Engine ───
    const runHealthChecks = useCallback(async () => {
        setIsRefreshing(true);
        const updated = [...services];
        const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

        // MCP Core (port 5001)
        const mcpIdx = updated.findIndex(s => s.id === 'lucid_mcp_core');
        if (mcpIdx >= 0) {
            try {
                const ok = await checkHealth();
                updated[mcpIdx] = { ...updated[mcpIdx], status: ok ? 'UP' : 'DOWN', lastCheck: now };
            } catch {
                updated[mcpIdx] = { ...updated[mcpIdx], status: 'DOWN', lastCheck: now };
            }
        }

        // SSE Server (port 8000)
        const sseIdx = updated.findIndex(s => s.id === 'mcp_sse_server');
        if (sseIdx >= 0) {
            try {
                const resp = await fetch('http://127.0.0.1:8000/sse', { method: 'GET', signal: AbortSignal.timeout(3000) });
                updated[sseIdx] = { ...updated[sseIdx], status: resp.ok || resp.status === 200 ? 'UP' : 'DOWN', lastCheck: now };
            } catch {
                updated[sseIdx] = { ...updated[sseIdx], status: 'DOWN', lastCheck: now };
            }
        }

        // InfraHealth tool
        try {
            const result = await callTool<Record<string, unknown>>('infra_health', {});
            if (result) setInfraHealth(result);
        } catch { /* non-critical */ }

        // HTTP Fallback (port 5001 direct check)
        const httpIdx = updated.findIndex(s => s.id === 'http_fallback');
        if (httpIdx >= 0) {
            try {
                const resp = await fetch('http://127.0.0.1:5001/health', { method: 'GET', signal: AbortSignal.timeout(3000) });
                updated[httpIdx] = { ...updated[httpIdx], status: resp.ok ? 'UP' : 'DOWN', lastCheck: now };
            } catch {
                updated[httpIdx] = { ...updated[httpIdx], status: 'DOWN', lastCheck: now };
            }
        }

        // HHNI (check via MCP tool)
        const hhniIdx = updated.findIndex(s => s.id === 'hhni_subsystem');
        if (hhniIdx >= 0) {
            try {
                const result = await mcp.getHHNIStatus();
                updated[hhniIdx] = { ...updated[hhniIdx], status: result ? 'UP' : 'DOWN', lastCheck: now };
            } catch {
                updated[hhniIdx] = { ...updated[hhniIdx], status: 'UNKNOWN', lastCheck: now };
            }
        }

        // JOC Dev (if rendering, it's alive)
        const jocIdx = updated.findIndex(s => s.id === 'joc_dev');
        if (jocIdx >= 0) {
            updated[jocIdx] = { ...updated[jocIdx], status: 'UP', lastCheck: now };
        }

        // AI Engine (check via MCP tool)
        const aiIdx = updated.findIndex(s => s.id === 'ai_engine_mcp');
        if (aiIdx >= 0) {
            try {
                const result = await callTool('ai_engine_status', {});
                updated[aiIdx] = { ...updated[aiIdx], status: result ? 'UP' : 'DOWN', lastCheck: now };
            } catch {
                updated[aiIdx] = { ...updated[aiIdx], status: 'UNKNOWN', lastCheck: now };
            }
        }

        // Ngrok and Gemini Bridge stay UNKNOWN unless we have info
        const ngrokIdx = updated.findIndex(s => s.id === 'ngrok_tunnel');
        if (ngrokIdx >= 0) updated[ngrokIdx] = { ...updated[ngrokIdx], lastCheck: now };
        const geminiIdx = updated.findIndex(s => s.id === 'gemini_bridge');
        if (geminiIdx >= 0) updated[geminiIdx] = { ...updated[geminiIdx], lastCheck: now };

        // Fetch OS process list for process monitor
        try {
            const resp = await fetch('http://127.0.0.1:5001/processes', { signal: AbortSignal.timeout(4000) });
            if (resp.ok) {
                const data = await resp.json();
                if (data.processes) setOsProcesses(data.processes);
            }
        } catch { /* non-critical */ }

        // Fetch tunnel connection status
        try {
            const connResp = await fetch('http://127.0.0.1:5001/connections', { signal: AbortSignal.timeout(4000) });
            if (connResp.ok) {
                const connData = await connResp.json();
                const subdomains: Array<{ name: string; url: string; status: 'UP' | 'DOWN' | 'PENDING'; latency?: number }> = [];
                // Check each subdomain via its actual local service
                for (const sub of [
                    { name: 'mcp.helixion.net', url: 'https://mcp.helixion.net', port: 8000, healthPath: '/health' },
                    { name: 'joc.helixion.net', url: 'https://joc.helixion.net', port: 5011, healthPath: '/' },
                    { name: 'api.helixion.net', url: 'https://api.helixion.net', port: 5001, healthPath: '/health' },
                ]) {
                    const localStart = performance.now();
                    try {
                        const resp = await fetch(`http://127.0.0.1:${sub.port}${sub.healthPath}`, { signal: AbortSignal.timeout(2000) });
                        if (resp.ok || resp.status === 200) {
                            subdomains.push({ name: sub.name, url: sub.url, status: 'UP', latency: Math.round(performance.now() - localStart) });
                        } else {
                            subdomains.push({ name: sub.name, url: sub.url, status: 'DOWN' });
                        }
                    } catch {
                        subdomains.push({ name: sub.name, url: sub.url, status: 'DOWN' });
                    }
                }
                // Check if tunnel is running via cloudflared metrics
                let tunnelRunning = false;
                try {
                    const metricsResp = await fetch('http://127.0.0.1:20241/metrics', { signal: AbortSignal.timeout(1500) });
                    tunnelRunning = metricsResp.ok;
                } catch { /* tunnel not running */ }
                setTunnelConnections({
                    cloudflare: { running: tunnelRunning },
                    relay: connData.connections?.relay_bridge
                        ? { connected: connData.connections.relay_connected, relay_url: connData.connections.relay_url }
                        : undefined,
                    subdomains,
                    updated_at: connData.updated_at,
                });
            }
        } catch { /* non-critical - connection manager may not be running */ }

        // Fetch security report
        try {
            const secResp = await fetch('http://127.0.0.1:5001/security/report', { signal: AbortSignal.timeout(3000) });
            if (secResp.ok) {
                const report = await secResp.json();
                setSecurityReport(report);
            }
        } catch { /* non-critical */ }

        // Fetch SENTINEL status + feed
        try {
            const [sStatusResp, sFeedResp] = await Promise.all([
                fetch('http://127.0.0.1:5001/sentinel/status', { signal: AbortSignal.timeout(3000) }),
                fetch('http://127.0.0.1:5001/sentinel/feed', { signal: AbortSignal.timeout(3000) }),
            ]);
            if (sStatusResp.ok) setSentinelStatus(await sStatusResp.json());
            if (sFeedResp.ok) {
                const feedData = await sFeedResp.json();
                setSentinelFeed(feedData.feed || []);
            }
        } catch { /* non-critical */ }

        setServices(updated);
        setLastRefresh(Date.now());
        setIsRefreshing(false);
    }, [services]);

    // Auto-refresh loop
    useEffect(() => {
        runHealthChecks();
        if (autoRefresh) {
            intervalRef.current = setInterval(runHealthChecks, 15000);
        }
        return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [autoRefresh]);

    // ─── Derived Stats ───
    const upCount = services.filter(s => s.status === 'UP').length;
    const downCount = services.filter(s => s.status === 'DOWN').length;
    const p0Services = services.filter(s => s.criticality === 'P0');
    const p0Up = p0Services.filter(s => s.status === 'UP').length;

    const getStatusClass = (s: ServiceStatus) =>
        s === 'UP' ? 'up' : s === 'DOWN' ? 'down' : s === 'DEGRADED' ? 'degraded' : 'unknown';

    const getLedClass = (s: ServiceStatus) =>
        s === 'UP' ? 'infra__led--on' : s === 'DOWN' ? 'infra__led--off' : s === 'DEGRADED' ? 'infra__led--warn' : '';

    const kindIcon = (k: ServiceKind) =>
        k === 'mcp' ? <ChipDieIcon size={11} /> :
            k === 'web' ? <SatelliteIcon size={11} /> :
                k === 'tunnel' ? <BoltIcon size={11} /> :
                    <LaunchVectorIcon size={11} />;

    // ─── Render ───
    return (
        <div className="infra">
            {/* ═══════════════════════════════════════
                ZONE 1: System Status Bar
                ═══════════════════════════════════════ */}
            <div className="infra__sysbar">
                <div className="infra__sysbar-item">
                    <RadarIcon size={11} style={{ opacity: 0.4 }} />
                    <span>INFRA</span>
                </div>

                <div className="infra__sysbar-sep" />

                {/* MCP */}
                <div className="infra__sysbar-item">
                    <span className={`infra__led ${aimos.connected ? 'infra__led--on' : 'infra__led--off'}`} />
                    <span>MCP</span>
                    <span className="infra__sysbar-value">{aimos.connected ? `${aimos.latency}ms` : 'off'}</span>
                </div>

                <div className="infra__sysbar-sep" />

                {/* Service counts */}
                <div className="infra__sysbar-item">
                    <span className="infra__sysbar-label">Up</span>
                    <span className="infra__sysbar-value" style={{ color: upCount === services.length ? 'var(--dxl-led-green)' : 'var(--dxl-led-amber)' }}>
                        {upCount}/{services.length}
                    </span>
                </div>

                <div className="infra__sysbar-item">
                    <span className="infra__sysbar-label">P0</span>
                    <span className="infra__sysbar-value" style={{ color: p0Up === p0Services.length ? 'var(--dxl-led-green)' : 'var(--dxl-led-red)' }}>
                        {p0Up}/{p0Services.length}
                    </span>
                </div>

                {downCount > 0 && (
                    <div className="infra__sysbar-item">
                        <span className="infra__led infra__led--off" />
                        <span style={{ color: 'var(--dxl-led-red)' }}>{downCount} DOWN</span>
                    </div>
                )}

                {/* Memory */}
                {aimos.memory && (
                    <>
                        <div className="infra__sysbar-sep" />
                        <div className="infra__sysbar-item">
                            <span className="infra__sysbar-label">Atoms</span>
                            <span className="infra__sysbar-value">{fmt(aimos.memory.total_atoms)}</span>
                        </div>
                    </>
                )}

                <div className="infra__sysbar-spacer" />

                {/* Refresh controls */}
                <label className="infra__auto-toggle">
                    <input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />
                    Auto 15s
                </label>

                <div className="infra__sysbar-item">
                    <RefreshCycleIcon size={10} style={{ color: '#444' }} />
                    <span className="infra__timestamp">{timeAgo(lastRefresh)}</span>
                </div>
            </div>

            {/* ═══════════════════════════════════════
                ZONE 2+3: Two-column workspace
                ═══════════════════════════════════════ */}
            <div className="infra__workspace">

                {/* ─── Main Column: Service Registry ─── */}
                <div className="infra__col infra__col--main">

                    {/* Service Registry Section */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <ConstellationIcon size={12} />
                            SERVICE REGISTRY
                            <span className="infra__section-badge">
                                {upCount}/{services.length} online
                                {isRefreshing && <> · <RefreshCycleIcon size={10} style={{ verticalAlign: 'middle', animation: 'spin 1s linear infinite' }} /></>}
                            </span>
                        </div>
                        <div className="infra__section-body">
                            <div className="infra__svc-grid">
                                {services.map(svc => (
                                    <div
                                        key={svc.id}
                                        className={`infra__svc-card ${expandedService === svc.id ? 'infra__svc-card--expanded' : ''}`}
                                        onClick={() => setExpandedService(expandedService === svc.id ? null : svc.id)}
                                    >
                                        <div className={`infra__svc-edge infra__svc-edge--${svc.criticality.toLowerCase()}`} />

                                        <div className="infra__svc-header">
                                            <span className={`infra__led ${getLedClass(svc.status)} ${svc.status === 'UP' ? 'infra__led--pulse' : ''}`} />
                                            <span className="infra__svc-name">{svc.name}</span>
                                            <span className={`infra__svc-crit infra__svc-crit--${svc.criticality.toLowerCase()}`}>
                                                {svc.criticality}
                                            </span>
                                        </div>

                                        <div className="infra__svc-meta">
                                            {kindIcon(svc.kind)}
                                            <span>{svc.kind}</span>
                                            {svc.port && <span>:{svc.port}</span>}
                                            {svc.transport && <span>({svc.transport})</span>}
                                            <div style={{ flex: 1 }} />
                                            <span className={`infra__svc-status infra__svc-status--${getStatusClass(svc.status)}`}>
                                                {svc.status}
                                            </span>
                                            {svc.lastCheck && <span className="infra__timestamp">{svc.lastCheck}</span>}
                                        </div>

                                        {/* Expanded details */}
                                        {expandedService === svc.id && (
                                            <div className="infra__svc-detail">
                                                {svc.dependsOn && (
                                                    <div className="infra__svc-detail-row">
                                                        <span className="infra__svc-detail-label">Depends</span>
                                                        <div>
                                                            {svc.dependsOn.map(d => {
                                                                const dep = services.find(s => s.id === d);
                                                                return (
                                                                    <span key={d} className={`infra__svc-dep ${dep?.status === 'UP' ? 'infra__svc-dep--ok' : 'infra__svc-dep--fail'}`}>
                                                                        <span className={`infra__led ${getLedClass(dep?.status || 'UNKNOWN')}`} style={{ width: 5, height: 5 }} />
                                                                        {dep?.name || d}
                                                                    </span>
                                                                );
                                                            })}
                                                        </div>
                                                    </div>
                                                )}
                                                {svc.startCmd && (
                                                    <div className="infra__svc-detail-row">
                                                        <span className="infra__svc-detail-label">Start</span>
                                                        <code className="infra__svc-cmd">{svc.startCmd}</code>
                                                    </div>
                                                )}
                                                {svc.details && Object.entries(svc.details).map(([k, v]) => (
                                                    <div key={k} className="infra__svc-detail-row">
                                                        <span className="infra__svc-detail-label">{k}</span>
                                                        <span className="infra__svc-detail-value">{String(v)}</span>
                                                    </div>
                                                ))}
                                                {/* Service Control Actions */}
                                                <div className="infra__svc-actions">
                                                    {svc.status !== 'UP' && svc.startCmd && (
                                                        <button
                                                            className="infra__btn infra__btn--start"
                                                            disabled={actionInProgress === svc.id}
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                navigator.clipboard.writeText(svc.startCmd!);
                                                                setActionInProgress(svc.id);
                                                                setTimeout(() => setActionInProgress(null), 2000);
                                                            }}
                                                        >
                                                            {actionInProgress === svc.id ? <span className="infra__spinner" /> : <BoltIcon size={9} />}
                                                            {actionInProgress === svc.id ? 'Copied!' : 'Start'}
                                                        </button>
                                                    )}
                                                    {svc.status === 'UP' && (
                                                        <button
                                                            className="infra__btn infra__btn--stop"
                                                            disabled={actionInProgress === svc.id}
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                if (svc.startCmd) navigator.clipboard.writeText(`# Stop: ${svc.name}`);
                                                            }}
                                                        >
                                                            Stop
                                                        </button>
                                                    )}
                                                    <button
                                                        className="infra__btn infra__btn--repair"
                                                        disabled={isDiagRunning}
                                                        onClick={async (e) => {
                                                            e.stopPropagation();
                                                            setIsDiagRunning(true);
                                                            setDiagLines(prev => [...prev, { text: `▶ Diagnosing ${svc.name}...`, level: 'cmd' }]);
                                                            try {
                                                                const result = await mcp.runDiagnostics(svc.id);
                                                                const text = result?.text || 'No diagnostics returned';
                                                                setDiagLines(prev => [
                                                                    ...prev,
                                                                    { text: `[${svc.name}] ${text}`, level: 'info' },
                                                                ]);
                                                            } catch (err) {
                                                                setDiagLines(prev => [...prev, { text: `Error: ${err}`, level: 'error' }]);
                                                            }
                                                            setIsDiagRunning(false);
                                                        }}
                                                    >
                                                        {isDiagRunning ? <span className="infra__spinner" /> : <RadarIcon size={9} />}
                                                        Repair
                                                    </button>
                                                    {svc.startCmd && (
                                                        <button
                                                            className="infra__btn"
                                                            onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(svc.startCmd!); }}
                                                        >
                                                            Copy Cmd
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Control Actions */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <BoltIcon size={12} />
                            CONTROL ACTIONS
                        </div>
                        <div className="infra__section-body">
                            <div className="infra__btn-group">
                                <button className="infra__btn infra__btn--refresh" onClick={runHealthChecks}>
                                    <RefreshCycleIcon size={11} />
                                    Run All Health Checks
                                </button>
                                <button className="infra__btn" onClick={() => navigator.clipboard.writeText('python scripts/mcp_sse_server.py')}>
                                    <ChipDieIcon size={11} />
                                    Copy SSE Start
                                </button>
                                <button className="infra__btn" onClick={() => navigator.clipboard.writeText('python scripts/ngrok_tunnel.py')}>
                                    <BoltIcon size={11} />
                                    Copy Tunnel Start
                                </button>
                                <button className="infra__btn" onClick={() => addTab({ id: 'agent-workforce', type: 'agent-workforce' as any, label: 'Agent Workforce', closable: true })}>
                                    <ConstellationIcon size={11} />
                                    Open Agent Workforce
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ─── Side Column: Diagnostics ─── */}
                <div className="infra__col infra__col--side">

                    {/* MCP Diagnostics */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <SignalPulseIcon size={12} />
                            MCP DIAGNOSTICS
                            <span className="infra__section-badge">{aimos.connected ? 'LIVE' : 'OFFLINE'}</span>
                        </div>
                        <div className="infra__section-body">
                            <div className="infra__diag-lcd">
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Connection</span>
                                    <span className="infra__diag-val">{aimos.connected ? 'CONNECTED' : 'DISCONNECTED'}</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Latency</span>
                                    <span className="infra__diag-val">{aimos.latency}ms</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">CMC Atoms</span>
                                    <span className="infra__diag-val">{fmt(aimos.memory?.total_atoms)}</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Molecules</span>
                                    <span className="infra__diag-val">{fmt(aimos.memory?.total_molecules)}</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Snapshots</span>
                                    <span className="infra__diag-val">{fmt(aimos.memory?.total_snapshots)}</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Storage</span>
                                    <span className="infra__diag-val">{aimos.memory?.storage_size || '—'}</span>
                                </div>
                                {aimos.consciousness && (
                                    <>
                                        <div className="infra__diag-row">
                                            <span className="infra__diag-key">Cog Drift</span>
                                            <span className="infra__diag-val">{((aimos.consciousness.cognitive_drift || 0) * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="infra__diag-row">
                                            <span className="infra__diag-key">Attn Load</span>
                                            <span className="infra__diag-val">{((aimos.consciousness.attention_load || 0) * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="infra__diag-row">
                                            <span className="infra__diag-key">Fail Rate</span>
                                            <span className="infra__diag-val">{((aimos.consciousness.failure_rate || 0) * 100).toFixed(1)}%</span>
                                        </div>
                                    </>
                                )}
                                {aimos.problems && (
                                    <>
                                        <div className="infra__diag-row">
                                            <span className="infra__diag-key">Errors</span>
                                            <span className="infra__diag-val" style={{ color: (aimos.problems.errors || 0) > 0 ? 'var(--dxl-led-red)' : undefined }}>
                                                {aimos.problems.errors || 0}
                                            </span>
                                        </div>
                                        <div className="infra__diag-row">
                                            <span className="infra__diag-key">Warnings</span>
                                            <span className="infra__diag-val" style={{ color: (aimos.problems.warnings || 0) > 0 ? 'var(--dxl-led-amber)' : undefined }}>
                                                {aimos.problems.warnings || 0}
                                            </span>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* SSE Infra Health */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <ChipDieIcon size={12} />
                            SSE HEALTH
                            <span className="infra__section-badge">infra_health</span>
                        </div>
                        <div className="infra__section-body">
                            {infraHealth ? (
                                <div className="infra__diag-lcd">
                                    {Object.entries(infraHealth).map(([key, val]) => (
                                        <div key={key} className="infra__diag-row">
                                            <span className="infra__diag-key">{key.replace(/_/g, ' ')}</span>
                                            <span className="infra__diag-val">
                                                {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="infra__empty">No SSE health data — server may be offline</div>
                            )}
                        </div>
                    </div>

                    {/* Dependency Graph */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <LaunchVectorIcon size={12} />
                            DEPENDENCY MAP
                        </div>
                        <div className="infra__section-body">
                            <svg width="100%" height="180" viewBox="0 0 320 180" style={{ display: 'block' }}>
                                {/* Nodes */}
                                {[
                                    { id: 'lucid_mcp_core', label: 'MCP Core', x: 30, y: 50 },
                                    { id: 'http_fallback', label: 'HTTP Bridge', x: 140, y: 30 },
                                    { id: 'mcp_sse_server', label: 'SSE', x: 250, y: 30 },
                                    { id: 'ngrok_tunnel', label: 'ngrok', x: 290, y: 70 },
                                    { id: 'hhni_subsystem', label: 'HHNI', x: 140, y: 70 },
                                    { id: 'ai_engine_mcp', label: 'AI Engine', x: 140, y: 110 },
                                    { id: 'joc_dev', label: 'JOC', x: 250, y: 110 },
                                    { id: 'gemini_bridge', label: 'Gemini', x: 30, y: 150 },
                                ].map(node => {
                                    const svc = services.find(s => s.id === node.id);
                                    const col = svc?.status === 'UP' ? '#22cc44' : svc?.status === 'DOWN' ? '#cc3333' : '#555';
                                    return (
                                        <g key={node.id}>
                                            <rect x={node.x - 32} y={node.y - 10} width={64} height={20} rx={3}
                                                fill="#0e0e0e" stroke={col} strokeWidth={1} opacity={0.8} />
                                            <circle cx={node.x - 22} cy={node.y} r={3} fill={col} opacity={0.8} />
                                            <text x={node.x + 4} y={node.y + 3} fill="#888" fontSize="7" fontFamily="monospace" textAnchor="middle">
                                                {node.label}
                                            </text>
                                        </g>
                                    );
                                })}
                                {/* Edges */}
                                {[
                                    [62, 45, 108, 30],   /* MCP Core → HTTP Bridge */
                                    [172, 30, 218, 30],   /* HTTP Bridge → SSE */
                                    [262, 40, 278, 60],   /* SSE → ngrok */
                                    [62, 55, 108, 70],    /* MCP Core → HHNI */
                                    [62, 60, 108, 110],   /* MCP Core → AI Engine */
                                ].map(([x1, y1, x2, y2], i) => (
                                    <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
                                        stroke="rgba(255,255,255,0.08)" strokeWidth={1} strokeDasharray="3,3" />
                                ))}
                            </svg>
                        </div>
                    </div>

                    {/* SENTINEL Command Center */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <RadarIcon size={12} />
                            SENTINEL
                            <span className="infra__section-badge" style={{
                                color: sentinelStatus?.threat_level === 'GREEN' ? '#22cc44'
                                    : sentinelStatus?.threat_level === 'YELLOW' ? '#cc8800'
                                        : sentinelStatus?.threat_level === 'RED' ? '#cc3333'
                                            : sentinelStatus?.threat_level === 'CRITICAL' ? '#ff0044'
                                                : '#666',
                            }}>
                                {sentinelStatus?.threat_level ?? 'OFFLINE'}
                            </span>
                        </div>
                        <div className="infra__section-body">
                            <div className="infra__diag-lcd">
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Processed</span>
                                    <span className="infra__diag-val">{sentinelStatus?.total_processed ?? 0}</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Blocked</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.total_blocked ?? 0) > 0 ? '#cc3333' : '#22cc44' }}>
                                        {sentinelStatus?.total_blocked ?? 0}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Honeypots</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.total_honeypot_hits ?? 0) > 0 ? '#ff0044' : '#22cc44' }}>
                                        {sentinelStatus?.total_honeypot_hits ?? 0} hits · {sentinelStatus?.banned_count ?? 0} banned
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Attacks</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.total_attacks_detected ?? 0) > 0 ? '#ff0044' : '#22cc44' }}>
                                        {sentinelStatus?.total_attacks_detected ?? 0} detected
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">IPs</span>
                                    <span className="infra__diag-val">
                                        {sentinelStatus?.ip_profiles?.total_ips_tracked ?? 0} tracked · {sentinelStatus?.ip_profiles?.suspicious_ips ?? 0} suspicious
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Integrity</span>
                                    <span className="infra__diag-val" style={{ color: '#4488cc' }}>
                                        {sentinelStatus?.file_integrity?.files_monitored ?? 0} files baselined
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Audit Chain</span>
                                    <span className="infra__diag-val" style={{ color: sentinelStatus?.telemetry?.chain_integrity?.valid !== false ? '#22cc44' : '#ff0044' }}>
                                        {sentinelStatus?.telemetry?.chain_integrity?.valid !== false ? '✓ INTACT' : '⚠ BROKEN'} · {sentinelStatus?.telemetry?.audit_ledger?.total_entries ?? 0} entries
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Events</span>
                                    <span className="infra__diag-val" style={{ color: '#4488cc' }}>
                                        {sentinelStatus?.telemetry?.events_total ?? 0} captured · {sentinelStatus?.telemetry?.actions_total ?? 0} actions
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Secrets</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.host_baselines?.secrets?.total_findings ?? 0) > 0 ? '#ff4444' : '#22cc44' }}>
                                        {(sentinelStatus?.host_baselines?.secrets?.total_findings ?? 0) === 0 ? '✓ CLEAN' : `⚠ ${sentinelStatus?.host_baselines?.secrets?.total_findings} found`}{(sentinelStatus?.host_baselines?.secrets?.critical ?? 0) > 0 ? ` (${sentinelStatus?.host_baselines?.secrets?.critical} critical)` : ''}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Genomes</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.host_baselines?.genomes?.modified ?? 0) > 0 ? '#cc8800' : '#22cc44' }}>
                                        {sentinelStatus?.host_baselines?.genomes?.files_watched ?? 0} watched{(sentinelStatus?.host_baselines?.genomes?.modified ?? 0) > 0 ? ` · ${sentinelStatus?.host_baselines?.genomes?.modified} modified` : ' · ✓ intact'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Outbound</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.host_baselines?.outbound?.unknown_connections ?? 0) > 0 ? '#cc8800' : '#888' }}>
                                        {sentinelStatus?.host_baselines?.outbound?.total_connections ?? 0} conns{(sentinelStatus?.host_baselines?.outbound?.unknown_connections ?? 0) > 0 ? ` · ${sentinelStatus?.host_baselines?.outbound?.unknown_connections} unknown` : ' · all known'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Sessions</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.sessions?.active_sessions ?? 0) > 0 ? '#22cc44' : '#888' }}>
                                        {sentinelStatus?.sessions?.active_sessions ?? 0} active{sentinelStatus?.sessions?.agents && sentinelStatus.sessions.agents.length > 0 ? ` · ${sentinelStatus.sessions.agents.slice(0, 3).join(', ')}` : ''}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">WRAITH</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.wraith?.failed ?? 0) > 0 ? '#cc3333' : '#22cc44' }}>
                                        {sentinelStatus?.wraith?.patterns_loaded ?? 0} patterns{(sentinelStatus?.wraith?.tests_run ?? 0) > 0 ? ` · score: ${sentinelStatus?.wraith?.vulnerability_score ?? 0}%` : ' · ready'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Policies</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.policies?.total_enforced ?? 0) > 0 ? '#cc8800' : '#22cc44' }}>
                                        {sentinelStatus?.policies?.active_policies ?? 0} active{(sentinelStatus?.policies?.total_enforced ?? 0) > 0 ? ` · ${sentinelStatus?.policies?.total_enforced} enforced` : ' · standby'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Governance</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.governance?.total_blocked ?? 0) > 0 ? '#cc3333' : '#22cc44' }}>
                                        {sentinelStatus?.governance?.tools_governed ?? 0} tools{(sentinelStatus?.governance?.total_blocked ?? 0) > 0 ? ` · ${sentinelStatus?.governance?.total_blocked} blocked` : ' · clear'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key" style={{ color: '#ff4444', fontWeight: 600 }}>PHANTOM</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.phantom?.active_engagements ?? 0) > 0 ? '#ff4444' : '#22cc44' }}>
                                        {sentinelStatus?.phantom?.active_engagements ?? 0} engagements · {sentinelStatus?.phantom?.total_cm_deployed ?? 0} CM deployed · {sentinelStatus?.phantom?.adversaries_tracked ?? 0} tracked
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Recon</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.recon?.attack_tools_detected ?? 0) > 0 ? '#cc8800' : '#22cc44' }}>
                                        {sentinelStatus?.recon?.ips_analyzed ?? 0} analyzed · {sentinelStatus?.recon?.attack_tools_detected ?? 0} tools detected · {sentinelStatus?.recon?.mitre_techniques_mapped ?? 0} MITRE techniques
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Traffic</span>
                                    <span className="infra__diag-val">
                                        {sentinelStatus?.anomaly?.current_rpm ?? 0} rpm (avg {sentinelStatus?.anomaly?.baseline_rpm ?? 0})
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Audit Chain</span>
                                    <span className="infra__diag-val" style={{ color: sentinelStatus?.chronicle?.tampering_detected ? '#ff4444' : '#22cc44' }}>
                                        {sentinelStatus?.chronicle?.audit_entries ?? 0} entries · {sentinelStatus?.chronicle?.chain_integrity ?? 'N/A'} · {sentinelStatus?.chronicle?.chain_head ?? 'genesis'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key" style={{ color: (sentinelStatus?.chronicle?.active_incidents ?? 0) > 0 ? '#ff8800' : undefined }}>Incidents</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.chronicle?.active_incidents ?? 0) > 0 ? '#ff8800' : '#22cc44' }}>
                                        {sentinelStatus?.chronicle?.active_incidents ?? 0} active · {sentinelStatus?.chronicle?.total_incidents ?? 0} total · {sentinelStatus?.chronicle?.playbooks_loaded ?? 0} playbooks
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key" style={{ color: '#ff00ff' }}>Threat Intel</span>
                                    <span className="infra__diag-val" style={{ color: (sentinelStatus?.nexus?.active_threats ?? 0) > 0 ? '#ff4444' : '#22cc44' }}>
                                        {sentinelStatus?.nexus?.tracked_threats ?? 0} tracked · {sentinelStatus?.nexus?.active_threats ?? 0} active · {sentinelStatus?.nexus?.total_signals ?? 0} signals · {sentinelStatus?.nexus?.chain_matches ?? 0} chain matches
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key" style={{ color: '#ff00ff' }}>Adaptive Def</span>
                                    <span className="infra__diag-val" style={{ color: sentinelStatus?.nexus?.defense_posture === 'NOMINAL' ? '#22cc44' : sentinelStatus?.nexus?.defense_posture === 'MAXIMUM' ? '#ff4444' : '#ffaa00' }}>
                                        {sentinelStatus?.nexus?.defense_posture ?? 'NOMINAL'} · {sentinelStatus?.nexus?.known_chains ?? 0} attack chains · {sentinelStatus?.nexus?.signal_types ?? 0} signal types · {sentinelStatus?.nexus?.adaptations_active ?? 0} adaptations
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Traffic</span>
                                    <span className="infra__diag-val">
                                        {sentinelStatus?.anomaly?.current_rpm ?? 0} rpm (avg {sentinelStatus?.anomaly?.baseline_rpm ?? 0})
                                    </span>
                                </div>
                                {(sentinelStatus?.uptime_seconds ?? 0) > 0 && (
                                    <div className="infra__diag-row">
                                        <span className="infra__diag-key">Uptime</span>
                                        <span className="infra__diag-val" style={{ color: '#888' }}>
                                            {Math.floor((sentinelStatus?.uptime_seconds ?? 0) / 60)}m {Math.floor((sentinelStatus?.uptime_seconds ?? 0) % 60)}s
                                        </span>
                                    </div>
                                )}
                            </div>
                            {/* NL Log Feed */}
                            {sentinelFeed.length > 0 && (
                                <div style={{
                                    marginTop: 6, maxHeight: 140, overflowY: 'auto' as const,
                                    fontSize: 8, fontFamily: 'monospace', lineHeight: '14px',
                                    background: '#050a05', border: '1px solid rgba(34,204,68,0.15)',
                                    borderRadius: 3, padding: '4px 6px',
                                }}>
                                    {sentinelFeed.slice(-15).map((entry, i) => (
                                        <div key={i} style={{
                                            color: entry.level === 'alert' || entry.level === 'ban' ? '#cc3333'
                                                : entry.level === 'warning' || entry.level === 'honeypot' ? '#cc8800'
                                                    : entry.level === 'info' ? '#4488cc'
                                                        : '#555',
                                            whiteSpace: 'nowrap' as const,
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                        }}>
                                            {entry.text}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Tunnel Connections */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <ConstellationIcon size={12} />
                            TUNNEL CONNECTIONS
                            <span className="infra__section-badge">
                                {tunnelConnections.subdomains.filter(s => s.status === 'UP').length}/{tunnelConnections.subdomains.length || 3} LIVE
                            </span>
                        </div>
                        <div className="infra__section-body">
                            {/* Cloudflare Tunnel Status */}
                            <div className="infra__diag-lcd">
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Tunnel</span>
                                    <span className="infra__diag-val" style={{ color: tunnelConnections.cloudflare?.running ? '#22cc44' : '#cc3333' }}>
                                        {tunnelConnections.cloudflare?.running ? 'CLOUDFLARE HA' : 'NOT RUNNING'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Method</span>
                                    <span className="infra__diag-val">Named Tunnel (aim-os)</span>
                                </div>
                                {tunnelConnections.relay && (
                                    <div className="infra__diag-row">
                                        <span className="infra__diag-key">Relay</span>
                                        <span className="infra__diag-val" style={{ color: tunnelConnections.relay.connected ? '#22cc44' : '#888' }}>
                                            {tunnelConnections.relay.connected ? 'CONNECTED' : 'OFFLINE'}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Subdomain Health */}
                            <div className="infra__proc-list" style={{ marginTop: 6 }}>
                                {(tunnelConnections.subdomains.length > 0 ? tunnelConnections.subdomains : [
                                    { name: 'mcp.helixion.net', url: 'https://mcp.helixion.net', status: 'PENDING' as const },
                                    { name: 'joc.helixion.net', url: 'https://joc.helixion.net', status: 'PENDING' as const },
                                    { name: 'api.helixion.net', url: 'https://api.helixion.net', status: 'PENDING' as const },
                                ]).map((sub) => (
                                    <div key={sub.name} className="infra__proc-card">
                                        <span className={`infra__led ${sub.status === 'UP' ? 'infra__led--on infra__led--pulse' : sub.status === 'PENDING' ? 'infra__led--warn' : 'infra__led--off'}`} />
                                        <span className="infra__proc-name" style={{ flex: 1, fontSize: 9 }}>{sub.name}</span>
                                        {'latency' in sub && sub.latency !== undefined && (
                                            <span className="infra__proc-stat" style={{ color: '#22cc44' }}>{sub.latency}ms</span>
                                        )}
                                        <span className="infra__proc-stat" style={{
                                            color: sub.status === 'UP' ? '#22cc44' : sub.status === 'PENDING' ? '#cc8800' : '#cc3333'
                                        }}>
                                            {sub.status}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* ChatGPT MCP URL */}
                            <div className="infra__diag-lcd" style={{ marginTop: 6 }}>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">ChatGPT SSE</span>
                                    <span className="infra__diag-val" style={{ fontSize: 8, color: '#cc8800' }}>
                                        mcp.helixion.net/sse
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Security Monitor */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <BoltIcon size={12} />
                            SECURITY MONITOR
                            <span className="infra__section-badge" style={{ color: securityReport?.auth_enforced ? '#22cc44' : '#cc8800' }}>
                                {securityReport?.auth_enforced ? 'ENFORCED' : 'MONITORING'}
                            </span>
                        </div>
                        <div className="infra__section-body">
                            <div className="infra__diag-lcd">
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Auth</span>
                                    <span className="infra__diag-val" style={{ color: securityReport?.auth_enforced ? '#22cc44' : '#cc8800' }}>
                                        {securityReport?.auth_enforced ? 'API KEY REQUIRED' : 'OPEN (no keys yet)'}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Requests</span>
                                    <span className="infra__diag-val">{securityReport?.request_log?.total_requests ?? 0}</span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Blocked</span>
                                    <span className="infra__diag-val" style={{ color: (securityReport?.request_log?.blocked_requests ?? 0) > 0 ? '#cc3333' : '#22cc44' }}>
                                        {securityReport?.request_log?.blocked_requests ?? 0}
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Rate Limit</span>
                                    <span className="infra__diag-val">
                                        {securityReport?.rate_limit?.max_requests ?? 60}/{securityReport?.rate_limit?.window_seconds ?? 60}s
                                    </span>
                                </div>
                                <div className="infra__diag-row">
                                    <span className="infra__diag-key">Active IPs</span>
                                    <span className="infra__diag-val">
                                        {Object.keys(securityReport?.rate_limit?.active_ips ?? {}).length}
                                    </span>
                                </div>
                                {securityReport?.api_keys && securityReport.api_keys.length > 0 && (
                                    <div className="infra__diag-row">
                                        <span className="infra__diag-key">API Keys</span>
                                        <span className="infra__diag-val">{securityReport.api_keys.length} active</span>
                                    </div>
                                )}
                            </div>
                            {/* Recent blocked requests */}
                            {securityReport?.recent_requests && securityReport.recent_requests.filter(r => r.blocked).length > 0 && (
                                <div className="infra__proc-list" style={{ marginTop: 6 }}>
                                    <div style={{ fontSize: 8, color: '#cc3333', marginBottom: 4, textTransform: 'uppercase' as const, letterSpacing: '1px' }}>Blocked Requests</div>
                                    {securityReport.recent_requests.filter(r => r.blocked).slice(-5).map((req, i) => (
                                        <div key={i} className="infra__proc-card">
                                            <span className="infra__led infra__led--off" />
                                            <span className="infra__proc-stat" style={{ color: '#cc3333' }}>{req.ip}</span>
                                            <span className="infra__proc-name" style={{ flex: 1, fontSize: 8 }}>{req.path}</span>
                                            <span className="infra__proc-stat" style={{ color: '#888' }}>{req.reason}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {/* Generate Key Button + Display */}
                            <div className="infra__btn-group" style={{ marginTop: 6 }}>
                                <button
                                    className="infra__btn infra__btn--refresh"
                                    onClick={async () => {
                                        const label = prompt('Key label (e.g. chatgpt, admin, testing):') || 'joc-generated';
                                        try {
                                            const resp = await fetch('http://127.0.0.1:5001/security/generate-key', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify({ label }),
                                            });
                                            const data = await resp.json();
                                            if (data.success && data.key) {
                                                setGeneratedKey(data.key);
                                                setDiagLines(prev => [...prev, { text: `🔑 API key "${label}" generated — save it now!`, level: 'info' }]);
                                            } else {
                                                setDiagLines(prev => [...prev, { text: `✗ Key generation failed: ${data.error}`, level: 'error' }]);
                                            }
                                        } catch (err) {
                                            setDiagLines(prev => [...prev, { text: `✗ Key generation failed: ${err}`, level: 'error' }]);
                                        }
                                    }}
                                >
                                    <BoltIcon size={10} />
                                    Generate API Key
                                </button>
                            </div>
                            {generatedKey && (
                                <div style={{
                                    marginTop: 6, padding: '8px 10px', background: '#0a1a0a',
                                    border: '1px solid #22cc44', borderRadius: 4, fontSize: 9,
                                    fontFamily: 'monospace', wordBreak: 'break-all' as const, color: '#22cc44',
                                }}>
                                    <div style={{ fontSize: 7, color: '#cc8800', marginBottom: 4, textTransform: 'uppercase' as const, letterSpacing: '1px' }}>
                                        ⚠ Save this key — it won't be shown again!
                                    </div>
                                    <div style={{ userSelect: 'all' as const }}>{generatedKey}</div>
                                    <div className="infra__btn-group" style={{ marginTop: 6 }}>
                                        <button
                                            className="infra__btn"
                                            onClick={() => {
                                                navigator.clipboard.writeText(generatedKey);
                                                setDiagLines(prev => [...prev, { text: '✓ API key copied to clipboard', level: 'info' }]);
                                            }}
                                        >
                                            Copy Key
                                        </button>
                                        <button className="infra__btn" onClick={() => setGeneratedKey(null)}>
                                            Dismiss
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Process Monitor */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <ChipDieIcon size={12} />
                            PROCESS MONITOR
                            <span className="infra__section-badge">{osProcesses.length} processes</span>
                        </div>
                        <div className="infra__section-body">
                            {osProcesses.length > 0 ? (
                                <div className="infra__proc-list">
                                    {osProcesses.map((p) => (
                                        <div key={p.Id} className="infra__proc-card">
                                            <span className="infra__led infra__led--on infra__led--pulse" />
                                            <span className="infra__proc-pid">{p.Id}</span>
                                            <span className="infra__proc-name">{p.ProcessName}</span>
                                            <span className="infra__proc-stat">{p.CPU?.toFixed(1) ?? '?'}cpu</span>
                                            <span className="infra__proc-stat">{p.MemMB?.toFixed(0) ?? '?'}MB</span>
                                            <span className="infra__proc-stat">{p.UptimeMin?.toFixed(0) ?? '?'}m</span>
                                            <span className="infra__proc-spacer" />
                                            <button
                                                className="infra__btn infra__btn--kill"
                                                onClick={async () => {
                                                    if (!confirm(`Kill PID ${p.Id} (${p.ProcessName})?`)) return;
                                                    setDiagLines(prev => [...prev, { text: `▶ Killing PID ${p.Id} (${p.ProcessName})...`, level: 'cmd' }]);
                                                    try {
                                                        const resp = await fetch('http://127.0.0.1:5001/processes/kill', {
                                                            method: 'POST',
                                                            headers: { 'Content-Type': 'application/json' },
                                                            body: JSON.stringify({ pid: p.Id }),
                                                        });
                                                        const result = await resp.json();
                                                        if (result.success) {
                                                            setDiagLines(prev => [...prev, { text: `✓ Killed PID ${p.Id}`, level: 'info' }]);
                                                            setOsProcesses(prev => prev.filter(x => x.Id !== p.Id));
                                                        } else {
                                                            setDiagLines(prev => [...prev, { text: `✗ Failed: ${result.error}`, level: 'error' }]);
                                                        }
                                                    } catch (err) {
                                                        setDiagLines(prev => [...prev, { text: `✗ Kill failed: ${err}`, level: 'error' }]);
                                                    }
                                                }}
                                            >
                                                Kill
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="infra__empty">No Python/Node processes detected</div>
                            )}
                            {osProcesses.length > 1 && (
                                <div className="infra__btn-group" style={{ marginTop: 6 }}>
                                    <button
                                        className="infra__btn infra__btn--danger"
                                        onClick={async () => {
                                            if (!confirm(`Kill all ${osProcesses.length} processes? This will stop the MCP server too.`)) return;
                                            for (const p of osProcesses) {
                                                try {
                                                    await fetch('http://127.0.0.1:5001/processes/kill', {
                                                        method: 'POST',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ pid: p.Id }),
                                                    });
                                                } catch { /* server may have died */ }
                                            }
                                            setDiagLines(prev => [...prev, { text: `✗ All processes terminated`, level: 'warn' }]);
                                            setOsProcesses([]);
                                        }}
                                    >
                                        Clean All Zombies
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Gemini CLI Diagnostics */}
                    <div className="infra__section">
                        <div className="infra__section-hdr">
                            <RadarIcon size={12} />
                            GEMINI CLI DIAGNOSTICS
                            <span className="infra__section-badge">{isDiagRunning ? 'RUNNING' : 'IDLE'}</span>
                        </div>
                        <div className="infra__section-body">
                            <div className="infra__diag-terminal">
                                {diagLines.length === 0 ? (
                                    <span className="infra__diag-terminal-line--info">
                                        <span className="infra__diag-terminal-prompt">gemini&gt; </span>
                                        Click "Repair" on any service to run diagnostics
                                    </span>
                                ) : (
                                    diagLines.map((line, i) => (
                                        <span key={i} className={`infra__diag-terminal-line infra__diag-terminal-line--${line.level}`}>
                                            {line.text}
                                        </span>
                                    ))
                                )}
                            </div>
                            <div className="infra__btn-group" style={{ marginTop: 6 }}>
                                <button
                                    className="infra__btn infra__btn--refresh"
                                    disabled={isDiagRunning}
                                    onClick={async () => {
                                        setIsDiagRunning(true);
                                        setDiagLines([{ text: '▶ Running full infrastructure scan...', level: 'cmd' }]);
                                        const downSvcs = services.filter(s => s.status === 'DOWN');
                                        if (downSvcs.length === 0) {
                                            setDiagLines(prev => [...prev, { text: '✓ All services healthy — no issues detected', level: 'info' }]);
                                        } else {
                                            for (const svc of downSvcs) {
                                                setDiagLines(prev => [...prev, { text: `▶ Diagnosing ${svc.name}...`, level: 'cmd' }]);
                                                try {
                                                    const result = await mcp.runDiagnostics(svc.id);
                                                    setDiagLines(prev => [...prev, { text: result?.text || `${svc.name}: No response`, level: result ? 'info' : 'warn' }]);
                                                } catch {
                                                    setDiagLines(prev => [...prev, { text: `✗ ${svc.name}: Diagnostic failed — service unreachable`, level: 'error' }]);
                                                }
                                            }
                                        }
                                        setIsDiagRunning(false);
                                    }}
                                >
                                    {isDiagRunning ? <span className="infra__spinner" /> : <RadarIcon size={10} />}
                                    Full Scan
                                </button>
                                <button className="infra__btn" onClick={() => setDiagLines([])}>
                                    Clear
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
