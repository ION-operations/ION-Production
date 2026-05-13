import { useState } from 'react';

// ─── Types ───

interface ComputeResource {
    id: string;
    name: string;
    type: 'gpu' | 'cloud' | 'api';
    status: 'online' | 'offline' | 'busy';
    usage: number;
    details: Record<string, string>;
}

interface InferenceJob {
    id: string;
    model: string;
    prompt: string;
    status: 'running' | 'queued' | 'completed' | 'failed';
    duration?: string;
    timestamp: string;
    tokens?: number;
}

// ─── Mock Data ───

const MOCK_RESOURCES: ComputeResource[] = [
    {
        id: 'local-gpu', name: 'NVIDIA 3050 Ti', type: 'gpu', status: 'online', usage: 38,
        details: { vram: '3.1 / 4.0 GB', temp: '62°C', model: 'phi-3-mini', fan: '45%' }
    },
];

const MOCK_JOBS: InferenceJob[] = [
    { id: '1', model: 'llama3.2', prompt: 'Summarize the JOC architecture...', status: 'running', timestamp: '20:45:12', tokens: 2400 },
    { id: '2', model: 'nomic-embed', prompt: 'Generate embedding for context files', status: 'completed', duration: '0.8s', timestamp: '20:44:05', tokens: 512 },
    { id: '3', model: 'llama3.2', prompt: 'Review this TypeScript function...', status: 'completed', duration: '4.2s', timestamp: '20:40:33', tokens: 3100 },
    { id: '4', model: 'codellama:13b', prompt: 'Refactor useAIMOS hook...', status: 'failed', timestamp: '20:38:00' },
];

const JOB_STATUS_ICONS: Record<string, string> = {
    running: '⟳', completed: '✓', queued: '○', failed: '✕',
};
const JOB_STATUS_COLORS: Record<string, string> = {
    running: '#cc9900', completed: '#33cc66', queued: '#555', failed: '#cc3333',
};

const API_QUOTAS = [
    { provider: 'Gemini API', used: 0, limit: '∞', color: '#00d4ff', label: 'Ultra — Unlimited' },
    { provider: 'OpenAI API', used: 8.40, limit: 50, color: '#10a37f', label: '$8.40 / $50' },
    { provider: 'Anthropic API', used: 12.20, limit: 100, color: '#cc7722', label: '$12.20 / $100' },
];

// ─── Bar Component ───

function UsageBar({ value, max, color, label }: { value: number; max: number | string; color: string; label: string }) {
    const pct = typeof max === 'number' ? (value / max) * 100 : 0;
    return (
        <div className="compute-bar-row">
            <div className="compute-bar-track">
                <div className="compute-bar-fill" style={{ width: `${pct}%`, background: color }} />
            </div>
            <span className="compute-bar-label">{label}</span>
        </div>
    );
}

// ─── Metric Card ───

function MetricCard({ title, value, unit, color, icon }: { title: string; value: string; unit?: string; color: string; icon: string }) {
    return (
        <div className="compute-metric">
            <span className="compute-metric-icon" style={{ color }}>{icon}</span>
            <div>
                <div className="compute-metric-value">{value}<span className="compute-metric-unit">{unit}</span></div>
                <div className="compute-metric-title">{title}</div>
            </div>
        </div>
    );
}

// ─── Main Component ───

export function ComputePage() {
    const [activeSection, setActiveSection] = useState<'local' | 'cloud' | 'api'>('local');

    return (
        <div className="compute-page">
            <div className="compute-header">
                <h2 className="compute-title">⚡ Compute Fabric</h2>
                <div className="compute-tabs">
                    {(['local', 'cloud', 'api'] as const).map(s => (
                        <button
                            key={s}
                            className={`compute-tab ${activeSection === s ? 'active' : ''}`}
                            onClick={() => setActiveSection(s)}
                        >
                            {s === 'local' ? '🖥️ Local' : s === 'cloud' ? '☁️ Cloud' : '🔑 API Quota'}
                        </button>
                    ))}
                </div>
            </div>

            {activeSection === 'local' && (
                <div className="compute-section">
                    {/* GPU Card */}
                    <div className="compute-card">
                        <div className="compute-card-header">
                            <span className="compute-card-status online" />
                            <h3>NVIDIA 3050 Ti</h3>
                            <span className="compute-card-badge">LOCAL GPU</span>
                        </div>

                        <div className="compute-metrics-row">
                            <MetricCard title="VRAM" value="3.1" unit=" / 4.0 GB" color="#00d4ff" icon="💾" />
                            <MetricCard title="GPU Load" value="38" unit="%" color="#7c4dff" icon="⚡" />
                            <MetricCard title="Temperature" value="62" unit="°C" color="#ff6b6b" icon="🌡️" />
                            <MetricCard title="Fan Speed" value="45" unit="%" color="#4ecdc4" icon="🌀" />
                        </div>

                        <div className="compute-card-section">
                            <h4>Loaded Model</h4>
                            <div className="compute-model-row">
                                <span className="compute-model-name">phi-3-mini</span>
                                <span className="compute-model-detail">3.8B · Q4_K_M</span>
                                <button className="compute-btn-sm">Unload</button>
                            </div>
                        </div>

                        <div className="compute-card-section">
                            <h4>Available Models</h4>
                            {['mistral-7b (Q4)', 'codellama-7b (Q4)', 'nomic-embed-text', 'gemma-2b-it'].map(m => (
                                <div key={m} className="compute-model-row">
                                    <span className="compute-model-name">{m}</span>
                                    <span className="compute-model-detail">○ available</span>
                                    <button className="compute-btn-sm accent">Load</button>
                                </div>
                            ))}
                        </div>

                        <div className="compute-card-footer">
                            <span>Tasks completed today: 142</span>
                            <span>Avg latency: 1.2s</span>
                        </div>
                    </div>

                    {/* System Resources */}
                    <div className="compute-card">
                        <div className="compute-card-header">
                            <h3>System Resources</h3>
                        </div>
                        <div className="compute-metrics-row">
                            <MetricCard title="CPU" value="62" unit="%" color="#4ecdc4" icon="⚙️" />
                            <MetricCard title="RAM" value="12" unit=" / 16 GB" color="#ff6b6b" icon="📊" />
                            <MetricCard title="Network ↓" value="45" unit=" Mbps" color="#00d4ff" icon="📡" />
                            <MetricCard title="Latency" value="23" unit=" ms" color="#ffd93d" icon="⏱️" />
                        </div>
                        <div className="compute-card-section">
                            <h4>Active Processes</h4>
                            <div className="compute-process-list">
                                <div className="compute-process">
                                    <span className="compute-process-dot" style={{ background: '#00d4ff' }} />
                                    4 browser instances
                                </div>
                                <div className="compute-process">
                                    <span className="compute-process-dot" style={{ background: '#7c4dff' }} />
                                    1 Ollama server (port 11434)
                                </div>
                                <div className="compute-process">
                                    <span className="compute-process-dot" style={{ background: '#cc7722' }} />
                                    3 dev servers (5001, 5002, 5011)
                                </div>
                                <div className="compute-process">
                                    <span className="compute-process-dot" style={{ background: '#4ecdc4' }} />
                                    1 MCP server (lucid-mcp)
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Inference Queue (merged from GpuMonitorPage) */}
                    <div className="compute-card">
                        <div className="compute-card-header">
                            <h3>Inference Queue</h3>
                            <span className="compute-card-badge">{MOCK_JOBS.filter(j => j.status === 'running').length} ACTIVE</span>
                        </div>
                        <div className="compute-process-list">
                            {MOCK_JOBS.map(job => (
                                <div key={job.id} className="compute-process" style={{ justifyContent: 'space-between' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
                                        <span style={{ color: JOB_STATUS_COLORS[job.status], fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                                            {JOB_STATUS_ICONS[job.status]}
                                        </span>
                                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#aaa' }}>{job.model}</span>
                                        <span style={{ fontSize: 11, color: '#666', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const }}>{job.prompt}</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                                        {job.tokens && <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#555' }}>{job.tokens} tok</span>}
                                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#444' }}>{job.duration || '...'}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {activeSection === 'cloud' && (
                <div className="compute-section">
                    <div className="compute-card">
                        <div className="compute-card-header">
                            <h3>Google Vertex AI</h3>
                            <span className="compute-card-badge">CLOUD</span>
                        </div>
                        <div className="compute-budget-row">
                            <span>Monthly Budget</span>
                            <span className="compute-budget-value">$45 / $100</span>
                        </div>
                        <UsageBar value={45} max={100} color="#4285f4" label="$45 / $100 this month" />
                        <div className="compute-card-section">
                            <h4>Quick Launch</h4>
                            <div className="compute-launch-grid">
                                <button className="compute-launch-btn">T4 <span>$0.35/hr</span></button>
                                <button className="compute-launch-btn">A100 <span>$3.67/hr</span></button>
                                <button className="compute-launch-btn">H100 <span>$6.98/hr</span></button>
                            </div>
                        </div>
                        <div className="compute-card-section">
                            <div className="compute-process">
                                <span className="compute-process-dot" style={{ background: '#555' }} />
                                No active VMs
                            </div>
                        </div>
                        <div className="compute-card-footer">
                            ⚠ Auto-shutdown: All VMs stop after 4hr idle
                        </div>
                    </div>

                    <div className="compute-card">
                        <div className="compute-card-header">
                            <h3>Google Drive</h3>
                            <span className="compute-card-badge">STORAGE</span>
                        </div>
                        <UsageBar value={4.2} max={30} color="#0f9d58" label="4.2 TB / 30 TB (14%)" />
                        <div className="compute-card-section">
                            <h4>Breakdown</h4>
                            <UsageBar value={2.1} max={4.2} color="#4285f4" label="Projects — 2.1 TB (50%)" />
                            <UsageBar value={1.2} max={4.2} color="#ea4335" label="Assets — 1.2 TB (29%)" />
                            <UsageBar value={0.5} max={4.2} color="#fbbc04" label="Responses — 0.5 TB (12%)" />
                            <UsageBar value={0.3} max={4.2} color="#34a853" label="Models — 0.3 TB (7%)" />
                        </div>
                        <div className="compute-card-footer">
                            Last backup: 15m ago · Next: in 45m
                        </div>
                    </div>
                </div>
            )}

            {activeSection === 'api' && (
                <div className="compute-section">
                    <div className="compute-card">
                        <div className="compute-card-header">
                            <h3>API Quota Tracking</h3>
                        </div>
                        {API_QUOTAS.map(q => (
                            <div key={q.provider} className="compute-api-row">
                                <span className="compute-api-name">{q.provider}</span>
                                <UsageBar
                                    value={q.used}
                                    max={typeof q.limit === 'number' ? q.limit : 100}
                                    color={q.color}
                                    label={q.label}
                                />
                                <button className="compute-btn-sm">Test</button>
                            </div>
                        ))}
                    </div>

                    <div className="compute-card">
                        <div className="compute-card-header">
                            <h3>Ring Strategy</h3>
                        </div>
                        <div className="compute-ring-diagram">
                            <div className="compute-ring ring-3">
                                <span>Ring 3: Cloud</span>
                                <div className="compute-ring ring-2">
                                    <span>Ring 2: API / CLI</span>
                                    <div className="compute-ring ring-1">
                                        <span>Ring 1: Browser</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="compute-card-footer">
                            Work flows outward: try Ring 1 first (cheapest), escalate for speed/power
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
