import { useState, useEffect } from 'react';

// ─── Types ───

interface GpuInfo {
    name: string;
    vramUsed: number;
    vramTotal: number;
    utilization: number;
    temp: number;
    power: number;
    driver: string;
}

interface OllamaModel {
    name: string;
    size: string;
    params: string;
    lastUsed: string;
    quantization: string;
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

const GPU: GpuInfo = {
    name: 'NVIDIA GeForce RTX 3050 Ti',
    vramUsed: 2.8, vramTotal: 4.0,
    utilization: 42, temp: 67, power: 85,
    driver: '551.86 (CUDA 12.4)',
};

const MODELS: OllamaModel[] = [
    { name: 'llama3.2:latest', size: '2.0 GB', params: '3B', lastUsed: '10 min ago', quantization: 'Q4_K_M' },
    { name: 'codellama:13b', size: '7.4 GB', params: '13B', lastUsed: '3 days ago', quantization: 'Q4_0' },
    { name: 'mistral:latest', size: '4.1 GB', params: '7B', lastUsed: '5 days ago', quantization: 'Q4_K_M' },
    { name: 'nomic-embed-text', size: '274 MB', params: '137M', lastUsed: 'Today', quantization: 'F16' },
];

const JOBS: InferenceJob[] = [
    { id: '1', model: 'llama3.2', prompt: 'Summarize the JOC architecture...', status: 'running', timestamp: '20:45:12', tokens: 2400 },
    { id: '2', model: 'nomic-embed', prompt: 'Generate embedding for context files', status: 'completed', duration: '0.8s', timestamp: '20:44:05', tokens: 512 },
    { id: '3', model: 'llama3.2', prompt: 'Review this TypeScript function...', status: 'completed', duration: '4.2s', timestamp: '20:40:33', tokens: 3100 },
    { id: '4', model: 'codellama:13b', prompt: 'Refactor useAIMOS hook...', status: 'failed', timestamp: '20:38:00' },
];

// ─── Component ───

export function GpuMonitorPage() {
    const [gpuAnim, setGpuAnim] = useState(GPU.utilization);

    useEffect(() => {
        const interval = setInterval(() => {
            setGpuAnim(prev => Math.max(0, Math.min(100, prev + (Math.random() * 10 - 5))));
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    const vramPct = (GPU.vramUsed / GPU.vramTotal) * 100;
    const vramColor = vramPct > 85 ? '#ff6b6b' : vramPct > 60 ? '#ffd93d' : '#4ecdc4';
    const tempColor = GPU.temp > 80 ? '#ff6b6b' : GPU.temp > 65 ? '#ffd93d' : '#4ecdc4';
    const utilColor = gpuAnim > 80 ? '#ff6b6b' : gpuAnim > 50 ? '#ffd93d' : '#4ecdc4';

    const jobStatusColor: Record<string, string> = {
        running: '#ffd93d', completed: '#4ecdc4', queued: '#888', failed: '#ff6b6b',
    };

    return (
        <div className="gpu-page">
            <div className="gpu-header">
                <span className="gpu-title">🖥 GPU Monitor</span>
                <span className="gpu-subtitle">{GPU.name} · {GPU.driver}</span>
            </div>

            <div className="gpu-body">
                {/* ─── Main Stats ─── */}
                <div className="gpu-main">
                    {/* GPU Stats Cards */}
                    <div className="gpu-stats-grid">
                        <div className="gpu-stat-card">
                            <div className="gpu-stat-label">Utilization</div>
                            <div className="gpu-stat-value" style={{ color: utilColor }}>{Math.round(gpuAnim)}%</div>
                            <div className="gpu-stat-bar">
                                <div className="gpu-stat-fill" style={{ width: `${gpuAnim}%`, background: utilColor }} />
                            </div>
                        </div>
                        <div className="gpu-stat-card">
                            <div className="gpu-stat-label">VRAM</div>
                            <div className="gpu-stat-value" style={{ color: vramColor }}>
                                {GPU.vramUsed.toFixed(1)} / {GPU.vramTotal.toFixed(1)} GB
                            </div>
                            <div className="gpu-stat-bar">
                                <div className="gpu-stat-fill" style={{ width: `${vramPct}%`, background: vramColor }} />
                            </div>
                        </div>
                        <div className="gpu-stat-card">
                            <div className="gpu-stat-label">Temperature</div>
                            <div className="gpu-stat-value" style={{ color: tempColor }}>{GPU.temp}°C</div>
                            <div className="gpu-stat-bar">
                                <div className="gpu-stat-fill" style={{ width: `${GPU.temp}%`, background: tempColor }} />
                            </div>
                        </div>
                        <div className="gpu-stat-card">
                            <div className="gpu-stat-label">Power Draw</div>
                            <div className="gpu-stat-value">{GPU.power}W</div>
                            <div className="gpu-stat-bar">
                                <div className="gpu-stat-fill" style={{ width: `${(GPU.power / 150) * 100}%`, background: '#a882ff' }} />
                            </div>
                        </div>
                    </div>

                    {/* Inference Queue */}
                    <div className="gpu-section">
                        <div className="gpu-section-title">Inference Queue ({JOBS.length})</div>
                        <div className="gpu-job-list">
                            {JOBS.map(job => (
                                <div key={job.id} className="gpu-job-row">
                                    <span className="gpu-job-status" style={{ color: jobStatusColor[job.status] }}>
                                        {job.status === 'running' ? '⟳' : job.status === 'completed' ? '✓' : job.status === 'failed' ? '✕' : '○'}
                                    </span>
                                    <span className="gpu-job-model">{job.model}</span>
                                    <span className="gpu-job-prompt">{job.prompt}</span>
                                    {job.tokens && <span className="gpu-job-tokens">{job.tokens} tok</span>}
                                    <span className="gpu-job-duration">{job.duration || '...'}</span>
                                    <span className="gpu-job-time">{job.timestamp}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* ─── Model Sidebar ─── */}
                <div className="gpu-model-panel">
                    <div className="gpu-section-title">Ollama Models ({MODELS.length})</div>
                    {MODELS.map(m => (
                        <div key={m.name} className="gpu-model-card">
                            <div className="gpu-model-header">
                                <span className="gpu-model-name">{m.name}</span>
                                <span className="gpu-model-size">{m.size}</span>
                            </div>
                            <div className="gpu-model-meta">
                                <span>{m.params} params</span>
                                <span>·</span>
                                <span>{m.quantization}</span>
                                <span>·</span>
                                <span>{m.lastUsed}</span>
                            </div>
                            <div className="gpu-model-actions">
                                <button className="gpu-model-btn">▶ Run</button>
                                <button className="gpu-model-btn">🗑 Remove</button>
                            </div>
                        </div>
                    ))}
                    <button className="gpu-pull-btn">⬇ Pull New Model</button>

                    <div className="gpu-section-title" style={{ marginTop: 16 }}>Cloud GPUs</div>
                    <div className="gpu-cloud-card">
                        <div className="gpu-cloud-provider">☁️ Vertex AI</div>
                        <div className="gpu-cloud-status">No active instances</div>
                        <button className="gpu-cloud-btn">+ Launch Instance</button>
                    </div>
                    <div className="gpu-cloud-card">
                        <div className="gpu-cloud-provider">⚡ NVIDIA Cloud</div>
                        <div className="gpu-cloud-status">No active instances</div>
                        <button className="gpu-cloud-btn">+ Launch Instance</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
