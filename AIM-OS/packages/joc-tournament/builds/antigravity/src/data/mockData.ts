// ═══════════════════════════════════════════════════════════════════
// MOCK DATA V2 — Enriched for instrument-grade density
// All data declared MOCK per Law 2. Every surface must show badge.
// ═══════════════════════════════════════════════════════════════════

export interface Agent {
    id: string;
    name: string;
    rank: string;
    rankLevel: number; // 1=CEO, 2=COO, 3=XO, 4=Lead, 5=Specialist, 6=Worker
    status: 'active' | 'idle' | 'offline' | 'error';
    currentTask: string;
    model: string;
    color: string; // unique agent color
    confidence: number; // VIF κ 0-1
    tokenBudget: number; // max tokens
    tokensUsed: number; // current usage
    uptime: string; // e.g. "2h 47m"
    lastActive: string; // relative time e.g. "2m ago"
    activityHistory: number[]; // sparkline data (12 intervals)
    missionsCompleted: number;
    missionsActive: number;
}

export interface Subsystem {
    acronym: string;
    name: string;
    health: number; // 0-100
    status: 'healthy' | 'degraded' | 'down' | 'offline';
    healthHistory: number[]; // sparkline data (12 intervals)
    lastCheck: string;
    toolCount: number;
    callsThisSession: number;
    avgLatency: number; // ms
}

export interface Mission {
    id: string;
    title: string;
    agent: string;
    agentColor: string;
    status: 'running' | 'pending' | 'completed' | 'failed';
    progress: number; // 0-100
    startedAt: string;
    elapsed: string;
    estimatedRemaining: string;
    stepsCompleted: number;
    stepsTotal: number;
    velocity: number[]; // sparkline: progress over time
}

export interface Message {
    id: string;
    from: string;
    to: string;
    content: string;
    timestamp: string;
    timeAgo: string;
    type: 'discussion' | 'task_handoff' | 'status_update' | 'urgent';
}

export interface Approval {
    id: string;
    action: string;
    agent: string;
    detail: string;
    risk: 'low' | 'medium' | 'high';
    timestamp: string;
    timeAgo: string;
    affectedSystems: number;
}

export interface ActivityEvent {
    id: string;
    timestamp: string;
    source: string;
    text: string;
    level: 'info' | 'warn' | 'error';
}

// ─── Agent Fleet (enriched) ─────────────────────────────────────

export const MOCK_AGENTS: Agent[] = [
    {
        id: 'opus', name: 'Opus', rank: 'COO', rankLevel: 2,
        status: 'active', currentTask: 'Reviewing tournament builds',
        model: 'Claude Opus 4.6', color: '#8B5CF6',
        confidence: 0.94, tokenBudget: 200000, tokensUsed: 142300,
        uptime: '4h 12m', lastActive: 'now',
        activityHistory: [3, 5, 8, 12, 7, 9, 14, 11, 8, 15, 13, 10],
        missionsCompleted: 12, missionsActive: 1,
    },
    {
        id: 'sev', name: 'Severina', rank: 'XO', rankLevel: 3,
        status: 'active', currentTask: 'Analyzing swarm topology',
        model: 'GPT-5.2', color: '#EC4899',
        confidence: 0.91, tokenBudget: 128000, tokensUsed: 89600,
        uptime: '3h 45m', lastActive: 'now',
        activityHistory: [4, 6, 5, 8, 10, 7, 12, 9, 11, 8, 14, 12],
        missionsCompleted: 8, missionsActive: 1,
    },
    {
        id: 'codex', name: 'Codex', rank: 'Lead', rankLevel: 4,
        status: 'idle', currentTask: 'Awaiting dispatch',
        model: 'Codex', color: '#06B6D4',
        confidence: 0.87, tokenBudget: 128000, tokensUsed: 12400,
        uptime: '2h 10m', lastActive: '8m ago',
        activityHistory: [8, 6, 4, 3, 2, 1, 1, 0, 0, 0, 1, 0],
        missionsCompleted: 5, missionsActive: 0,
    },
    {
        id: 'gemini', name: 'Gemini', rank: 'Spec', rankLevel: 5,
        status: 'active', currentTask: 'Visual analysis pipeline',
        model: 'Gem 3.1 Pro', color: '#F59E0B',
        confidence: 0.89, tokenBudget: 100000, tokensUsed: 67200,
        uptime: '2h 47m', lastActive: '1m ago',
        activityHistory: [2, 3, 5, 4, 7, 8, 6, 9, 10, 7, 5, 8],
        missionsCompleted: 3, missionsActive: 1,
    },
    {
        id: 'composer', name: 'Composer', rank: 'Spec', rankLevel: 5,
        status: 'offline', currentTask: 'Last: doc audit',
        model: 'Cursor', color: '#6B7280',
        confidence: 0.0, tokenBudget: 64000, tokensUsed: 0,
        uptime: '—', lastActive: '45m ago',
        activityHistory: [4, 5, 3, 6, 2, 1, 0, 0, 0, 0, 0, 0],
        missionsCompleted: 2, missionsActive: 0,
    },
    {
        id: 'dac', name: 'DAC', rank: 'Worker', rankLevel: 6,
        status: 'active', currentTask: 'Building JARVIS UI',
        model: 'Antigravity', color: '#22C55E',
        confidence: 0.86, tokenBudget: 200000, tokensUsed: 156800,
        uptime: '1h 22m', lastActive: 'now',
        activityHistory: [0, 0, 2, 5, 8, 12, 15, 18, 22, 20, 25, 28],
        missionsCompleted: 0, missionsActive: 1,
    },
];

// ─── Subsystem Health (enriched) ─────────────────────────────────

export const MOCK_SUBSYSTEMS: Subsystem[] = [
    { acronym: 'CMC', name: 'Memory Core', health: 98, status: 'healthy', healthHistory: [95, 96, 97, 98, 97, 98, 98, 99, 98, 97, 98, 98], lastCheck: '12s', toolCount: 8, callsThisSession: 23, avgLatency: 89 },
    { acronym: 'HHNI', name: 'Nav Index', health: 92, status: 'healthy', healthHistory: [90, 91, 90, 92, 93, 91, 92, 93, 92, 91, 92, 92], lastCheck: '15s', toolCount: 4, callsThisSession: 12, avgLatency: 142 },
    { acronym: 'VIF', name: 'Confidence', health: 95, status: 'healthy', healthHistory: [93, 94, 95, 94, 95, 96, 95, 94, 95, 96, 95, 95], lastCheck: '8s', toolCount: 3, callsThisSession: 41, avgLatency: 34 },
    { acronym: 'SEG', name: 'Evidence', health: 88, status: 'healthy', healthHistory: [85, 86, 87, 88, 87, 88, 89, 88, 87, 88, 88, 88], lastCheck: '20s', toolCount: 3, callsThisSession: 7, avgLatency: 210 },
    { acronym: 'APOE', name: 'Orchestration', health: 91, status: 'healthy', healthHistory: [88, 89, 90, 91, 90, 91, 92, 91, 90, 91, 91, 91], lastCheck: '5s', toolCount: 5, callsThisSession: 9, avgLatency: 156 },
    { acronym: 'TCS', name: 'Timeline', health: 85, status: 'healthy', healthHistory: [82, 83, 84, 85, 84, 85, 86, 85, 84, 85, 85, 85], lastCheck: '30s', toolCount: 4, callsThisSession: 6, avgLatency: 112 },
    { acronym: 'CAS', name: 'Cognition', health: 78, status: 'degraded', healthHistory: [92, 90, 88, 85, 82, 80, 78, 79, 78, 77, 78, 78], lastCheck: '10s', toolCount: 3, callsThisSession: 5, avgLatency: 198 },
    { acronym: 'MCP', name: 'Protocol', health: 100, status: 'healthy', healthHistory: [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100], lastCheck: '1s', toolCount: 92, callsThisSession: 47, avgLatency: 42 },
    { acronym: 'NLT', name: 'NL Tags', health: 90, status: 'healthy', healthHistory: [88, 89, 90, 90, 89, 90, 91, 90, 89, 90, 90, 90], lastCheck: '25s', toolCount: 4, callsThisSession: 3, avgLatency: 95 },
    { acronym: 'ORC', name: 'Oracle', health: 94, status: 'healthy', healthHistory: [92, 93, 94, 93, 94, 95, 94, 93, 94, 95, 94, 94], lastCheck: '12s', toolCount: 2, callsThisSession: 8, avgLatency: 67 },
    { acronym: 'GEN', name: 'Genome', health: 96, status: 'healthy', healthHistory: [94, 95, 96, 95, 96, 97, 96, 95, 96, 97, 96, 96], lastCheck: '18s', toolCount: 3, callsThisSession: 4, avgLatency: 78 },
    { acronym: 'IIS', name: 'Intuition', health: 72, status: 'degraded', healthHistory: [85, 82, 80, 78, 75, 73, 72, 73, 72, 71, 72, 72], lastCheck: '22s', toolCount: 3, callsThisSession: 2, avgLatency: 340 },
    { acronym: 'SDF', name: 'Semantic', health: 65, status: 'degraded', healthHistory: [78, 75, 72, 70, 68, 66, 65, 66, 65, 64, 65, 65], lastCheck: '35s', toolCount: 2, callsThisSession: 1, avgLatency: 450 },
    { acronym: 'SEER', name: 'Vision', health: 0, status: 'offline', healthHistory: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], lastCheck: '—', toolCount: 5, callsThisSession: 0, avgLatency: 0 },
];

// ─── Active Missions (enriched) ──────────────────────────────────

export const MOCK_MISSIONS: Mission[] = [
    {
        id: 'MSN-042', title: 'JARVIS Tournament Phase 1',
        agent: 'DAC', agentColor: '#22C55E', status: 'running', progress: 35,
        startedAt: '14:22', elapsed: '1h 12m', estimatedRemaining: '2h 15m',
        stepsCompleted: 7, stepsTotal: 20,
        velocity: [0, 2, 5, 8, 12, 15, 18, 22, 26, 30, 33, 35],
    },
    {
        id: 'MSN-041', title: 'Swarm topology executor audit',
        agent: 'Severina', agentColor: '#EC4899', status: 'running', progress: 72,
        startedAt: '13:45', elapsed: '1h 49m', estimatedRemaining: '42m',
        stepsCompleted: 18, stepsTotal: 25,
        velocity: [0, 5, 12, 20, 28, 35, 42, 48, 55, 62, 68, 72],
    },
    {
        id: 'MSN-040', title: 'AI Engine facade integration',
        agent: 'Opus', agentColor: '#8B5CF6', status: 'running', progress: 88,
        startedAt: '12:30', elapsed: '3h 4m', estimatedRemaining: '25m',
        stepsCompleted: 22, stepsTotal: 25,
        velocity: [0, 8, 18, 30, 40, 50, 58, 65, 72, 78, 84, 88],
    },
    {
        id: 'MSN-039', title: 'Ghost Engine contract validation',
        agent: 'Codex', agentColor: '#06B6D4', status: 'pending', progress: 0,
        startedAt: '—', elapsed: '—', estimatedRemaining: '~1h',
        stepsCompleted: 0, stepsTotal: 12,
        velocity: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    {
        id: 'MSN-038', title: 'Chrome extension mapper v2',
        agent: 'Gemini', agentColor: '#F59E0B', status: 'completed', progress: 100,
        startedAt: '11:15', elapsed: '1h 8m', estimatedRemaining: '—',
        stepsCompleted: 8, stepsTotal: 8,
        velocity: [0, 10, 25, 40, 55, 68, 80, 90, 95, 98, 100, 100],
    },
];

// ─── Recent Messages ─────────────────────────────────────────────

export const MOCK_MESSAGES: Message[] = [
    { id: 'msg-1', from: 'Opus', to: 'Braden', content: 'Tournament builds ready. 7 competitor entries populated. Phase 1 review gate available.', timestamp: '14:38', timeAgo: '4m', type: 'status_update' },
    { id: 'msg-2', from: 'Severina', to: 'Opus', content: 'Parallel topology passing 5/5 benchmarks. Gated has 1 edge case in quality evaluation.', timestamp: '14:22', timeAgo: '20m', type: 'discussion' },
    { id: 'msg-3', from: 'DAC', to: 'Braden', content: 'Design brief approved. Beginning build phase — Mission Control + full shell.', timestamp: '14:15', timeAgo: '27m', type: 'status_update' },
    { id: 'msg-4', from: 'Gemini', to: 'Opus', content: 'Chrome extension DOM mapper v2 deployed. Native messaging host stable at 14ms.', timestamp: '13:58', timeAgo: '44m', type: 'task_handoff' },
    { id: 'msg-5', from: 'Opus', to: 'Severina', content: 'Proceed with debate topology test. Use 3 workers, cap at 45s per round.', timestamp: '13:52', timeAgo: '50m', type: 'discussion' },
];

// ─── Pending Approvals (enriched) ────────────────────────────────

export const MOCK_APPROVALS: Approval[] = [
    { id: 'apr-1', action: 'Deploy AI Engine v2.0 → staging', agent: 'Opus', detail: '14 subsystems affected', risk: 'high', timestamp: '14:30', timeAgo: '12m', affectedSystems: 14 },
    { id: 'apr-2', action: 'Execute swarm: debate topology', agent: 'Severina', detail: '3 workers, est. 45s', risk: 'medium', timestamp: '14:25', timeAgo: '17m', affectedSystems: 3 },
    { id: 'apr-3', action: 'Batch index 47 CMC atoms → HHNI', agent: 'Codex', detail: 'Semantic graph mutation', risk: 'low', timestamp: '14:10', timeAgo: '32m', affectedSystems: 2 },
];

// ─── Activity Feed ───────────────────────────────────────────────

export const MOCK_ACTIVITY: ActivityEvent[] = [
    { id: 'act-1', timestamp: '14:42', source: 'MCP', text: 'store_memory → atom #194 persisted', level: 'info' },
    { id: 'act-2', timestamp: '14:40', source: 'VIF', text: 'κ=0.82 gate passed for MSN-041', level: 'info' },
    { id: 'act-3', timestamp: '14:38', source: 'Opus', text: 'Status update → Braden: tournament ready', level: 'info' },
    { id: 'act-4', timestamp: '14:35', source: 'CAS', text: 'Drift score elevated: 0.23 (threshold: 0.3)', level: 'warn' },
    { id: 'act-5', timestamp: '14:32', source: 'APOE', text: 'Plan created: Ghost Engine Phase 2', level: 'info' },
    { id: 'act-6', timestamp: '14:30', source: 'Oracle', text: 'Approval requested: Deploy AI Engine v2.0', level: 'warn' },
    { id: 'act-7', timestamp: '14:28', source: 'SEG', text: 'Knowledge synthesis: 3 topics → 1 merged entity', level: 'info' },
    { id: 'act-8', timestamp: '14:25', source: 'HHNI', text: '12 atoms indexed into semantic graph', level: 'info' },
    { id: 'act-9', timestamp: '14:22', source: 'TCS', text: 'Timeline entry: MSN-042 started', level: 'info' },
    { id: 'act-10', timestamp: '14:15', source: 'Genome', text: 'Agent genome loaded: DAC worker overlay', level: 'info' },
];

// ─── Assistant Chat Messages ─────────────────────────────────────

export const MOCK_CHAT: { role: 'user' | 'assistant'; content: string; confidence?: number }[] = [
    { role: 'user', content: 'What is the current status of the AI Engine?' },
    { role: 'assistant', content: 'The AI Engine v2.0 is operational with all 14 subsystems online. The Smart Router, Intent Classifier, and Work Detector are fully functional. One item needs attention: CAS cognitive drift score is elevated at 0.23 (threshold 0.3), which is being monitored.', confidence: 0.87 },
    { role: 'user', content: 'Show me the most recent agent activity.' },
    { role: 'assistant', content: 'In the last 30 minutes: Opus completed tournament review. Severina is running swarm topology tests (72% progress). DAC began JARVIS build. Gemini deployed Chrome extension update. Codex is idle awaiting dispatch. Composer is offline (last: documentation audit).', confidence: 0.92 },
];

// ─── Aggregate metrics helper ────────────────────────────────────

export const AGGREGATE = {
    agentsActive: MOCK_AGENTS.filter((a) => a.status === 'active').length,
    agentsTotal: MOCK_AGENTS.length,
    missionsRunning: MOCK_MISSIONS.filter((m) => m.status === 'running').length,
    missionsTotal: MOCK_MISSIONS.length,
    systemsHealthy: MOCK_SUBSYSTEMS.filter((s) => s.status === 'healthy').length,
    systemsDegraded: MOCK_SUBSYSTEMS.filter((s) => s.status === 'degraded').length,
    systemsOffline: MOCK_SUBSYSTEMS.filter((s) => s.status === 'offline').length,
    systemsTotal: MOCK_SUBSYSTEMS.length,
    approvalsPending: MOCK_APPROVALS.length,
    avgConfidence: +(MOCK_AGENTS.filter((a) => a.confidence > 0).reduce((s, a) => s + a.confidence, 0) / MOCK_AGENTS.filter((a) => a.confidence > 0).length).toFixed(2),
    mcpToolCalls: MOCK_SUBSYSTEMS.reduce((s, sys) => s + sys.callsThisSession, 0),
    mcpTools: 92,
    cmcAtoms: 194,
};
