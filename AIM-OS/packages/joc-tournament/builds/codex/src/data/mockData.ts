import type { TruthState } from '../../../../shared/types';
import type { AssistantMode, WorkspaceId } from '../store/shellStore';

export type AgentTone = 'ready' | 'busy' | 'degraded' | 'offline';
export type SystemTone = 'healthy' | 'degraded' | 'down';
export type Priority = 'P0' | 'P1' | 'P2';

export interface FleetAgent {
    callsign: string;
    role: string;
    task: string;
    tone: AgentTone;
    trust: TruthState;
}

export interface MissionCard {
    title: string;
    owner: string;
    progress: number;
    priority: Priority;
    truth: TruthState;
    eta: string;
}

export interface SystemCard {
    acronym: string;
    label: string;
    health: number;
    tone: SystemTone;
    truth: TruthState;
    note: string;
}

export interface AttentionItem {
    label: string;
    detail: string;
    priority: Priority;
    truth: TruthState;
}

export interface FeedItem {
    time: string;
    source: string;
    text: string;
    truth: TruthState;
}

export interface EvidenceItem {
    title: string;
    source: string;
    truth: TruthState;
}

export interface WorkspaceBrief {
    eyebrow: string;
    summary: string;
    objective: string;
    shellNote: string;
}

export const commandMetrics = [
    { label: 'MCP Bridge', value: 'READY', detail: '5001 / HEALTHY', truth: 'LIVE' as TruthState },
    { label: 'Fleet Ready', value: '4/6', detail: '2 BUSY / 0 LOST', truth: 'LIVE' as TruthState },
    { label: 'Active Missions', value: '07', detail: '2 REQUIRE COMMAND', truth: 'CACHED' as TruthState },
    { label: 'HHNI', value: 'DOWN', detail: 'RETRIEVER UNAVAILABLE', truth: 'OFFLINE' as TruthState },
];

export const fleetAgents: FleetAgent[] = [
    { callsign: 'OPUS', role: 'JARVIS builder', task: 'JOC security and shell hardening', tone: 'busy', trust: 'LIVE' },
    { callsign: 'COMPOSER', role: 'Multi-file operator', task: 'Tournament execution support', tone: 'ready', trust: 'LIVE' },
    { callsign: 'GEMINI', role: 'Research and mapping', task: 'Context and CLI evolution', tone: 'busy', trust: 'CACHED' },
    { callsign: 'CODEX', role: 'Backend and protocol', task: 'Mission Control cockpit build', tone: 'ready', trust: 'LIVE' },
    { callsign: 'BROWSER', role: 'High-altitude synthesis', task: 'Atlas and journal work', tone: 'busy', trust: 'LIVE' },
    { callsign: 'FORGE', role: 'Codex CLI factory', task: 'Launcher slice follow-through', tone: 'degraded', trust: 'CACHED' },
];

export const missionQueue: MissionCard[] = [
    { title: 'Stabilize Codex tournament build lane', owner: 'CODEX', progress: 58, priority: 'P0', truth: 'LIVE', eta: 'Today' },
    { title: 'Freeze JARVIS shell grammar for competition', owner: 'OPUS', progress: 81, priority: 'P0', truth: 'LIVE', eta: 'Today' },
    { title: 'Map canon versus runtime drift in UI layer', owner: 'PALISADE', progress: 42, priority: 'P1', truth: 'CACHED', eta: 'Next 6h' },
    { title: 'Recover HHNI retrieval path for cockpit search', owner: 'Relay/Forge', progress: 17, priority: 'P1', truth: 'OFFLINE', eta: 'Blocked' },
];

export const subsystemHealth: SystemCard[] = [
    { acronym: 'CMC', label: 'Context Memory Core', health: 94, tone: 'healthy', truth: 'LIVE', note: 'Atoms writable and queryable' },
    { acronym: 'MCP', label: 'Command bridge', health: 91, tone: 'healthy', truth: 'LIVE', note: 'HTTP fallback reachable' },
    { acronym: 'VIF', label: 'Confidence and gates', health: 82, tone: 'healthy', truth: 'CACHED', note: 'Recent packet evidence only' },
    { acronym: 'APOE', label: 'Mission orchestration', health: 71, tone: 'degraded', truth: 'CACHED', note: 'Partial execution picture' },
    { acronym: 'HHNI', label: 'Retrieval index', health: 11, tone: 'down', truth: 'OFFLINE', note: 'Retriever unavailable in live stats' },
    { acronym: 'CAS', label: 'Self-audit stack', health: 63, tone: 'degraded', truth: 'SPECULATIVE', note: 'Signals exist, not unified' },
];

export const attentionStack: AttentionItem[] = [
    {
        label: 'HHNI gap remains visible from the cockpit.',
        detail: 'Mission Control should show search truth as degraded until retriever health is restored.',
        priority: 'P0',
        truth: 'OFFLINE',
    },
    {
        label: 'Shell grammar is more mature than truth wiring.',
        detail: 'This build favors operator legibility over fake completeness.',
        priority: 'P1',
        truth: 'LIVE',
    },
    {
        label: 'Codex host uses MCP through HTTP bridge.',
        detail: 'Native tool mounting is still not the proven path for this lane.',
        priority: 'P1',
        truth: 'LIVE',
    },
];

export const activityFeed: FeedItem[] = [
    { time: '16:12', source: 'MCP', text: 'Bridge health revalidated. Tool surface returned ready.', truth: 'LIVE' },
    { time: '16:05', source: 'OPUS', text: 'Tournament aesthetic brief propagated to live team channels.', truth: 'LIVE' },
    { time: '15:53', source: 'FORGE', text: 'Codex CLI launcher slice delivered for review.', truth: 'CACHED' },
    { time: '15:41', source: 'SYSTEM', text: 'HHNI retriever still absent from live stats payload.', truth: 'OFFLINE' },
    { time: '15:27', source: 'CODEX', text: 'Design brief approved. Implementation phase authorized.', truth: 'LIVE' },
];

export const diagnosticsFeed: FeedItem[] = [
    { time: 'port:5001', source: 'HEALTH', text: 'ready=true mode=fallback-http-bridge security=active', truth: 'LIVE' },
    { time: 'tools:103', source: 'MCP', text: 'Tool listing succeeded; bridge path is operational.', truth: 'LIVE' },
    { time: 'hhni', source: 'INDEX', text: 'index_available=false retriever_available=false', truth: 'OFFLINE' },
    { time: 'shell', source: 'JARVIS', text: 'Workspace switch updates drawer, canvas, and bottom context.', truth: 'LIVE' },
];

export const approvalsQueue = [
    { title: 'Promote Mission Control shell grammar to shared baseline', owner: 'COMMAND', truth: 'SPECULATIVE' as TruthState },
    { title: 'Adopt HHNI outage strip as mandatory cockpit element', owner: 'OPUS', truth: 'CACHED' as TruthState },
];

export const evidenceDeck: EvidenceItem[] = [
    { title: 'MCP bridge healthy on :5001', source: 'health probe', truth: 'LIVE' },
    { title: 'Design brief approved by operator', source: 'tournament prompt', truth: 'LIVE' },
    { title: 'HHNI retriever unavailable', source: 'get_memory_stats', truth: 'LIVE' },
];

export const assistantByMode: Record<AssistantMode, { lead: string; body: string; confidence: string }[]> = {
    chat: [
        {
            lead: 'Assistant rail',
            body: 'Mission Control is keeping the truth surface narrow: live MCP, visible mission queue, explicit HHNI outage.',
            confidence: '0.82',
        },
        {
            lead: 'Operator hint',
            body: 'Open the bottom drawer for diagnostics when evaluating degraded mode behavior.',
            confidence: '0.76',
        },
    ],
    context: [
        {
            lead: 'Context map',
            body: 'Active lineage: proposal approved, build live, shell aligned to canonical workspaces, truth states declared.',
            confidence: '0.79',
        },
        {
            lead: 'Gap note',
            body: 'The retrieval substrate is still weaker than the comms substrate. Search should remain visibly constrained.',
            confidence: '0.84',
        },
    ],
    actions: [
        {
            lead: 'Suggested action',
            body: 'Inspect the infra workspace to review bridge health and degraded recovery notes before expanding beyond Mission Control.',
            confidence: '0.74',
        },
        {
            lead: 'Suggested action',
            body: 'Use Dispatch only after the operator confirms mission packets and truth states for outbound prompts.',
            confidence: '0.71',
        },
    ],
    memory: [
        {
            lead: 'Memory anchor',
            body: 'AIMOS treats IDE habitats as bootstrap surfaces. The runtime target remains CLI and API native.',
            confidence: '0.87',
        },
        {
            lead: 'Memory anchor',
            body: 'The sovereign needs visual control over the organism because code alone is not an accessible view of truth.',
            confidence: '0.81',
        },
    ],
};

export const workspaceBriefs: Record<WorkspaceId, WorkspaceBrief> = {
    dashboard: {
        eyebrow: 'Primary cockpit',
        summary: 'Mission Control concentrates force visibility, live truth, and command attention into one screen.',
        objective: 'Let the sovereign assess system state in under ten seconds.',
        shellNote: 'Left drawer emphasizes fleet, missions, and subsystem truth. Bottom defaults to chronicle.',
    },
    dispatch: {
        eyebrow: 'Execution lane',
        summary: 'Dispatch is the outbound command surface for scoped work, approvals, and response routing.',
        objective: 'Move from operator decision to controlled action without losing provenance.',
        shellNote: 'Drawer shifts toward mission queue and comms. Assistant rail favors actions.',
    },
    'agent-workforce': {
        eyebrow: 'Force governance',
        summary: 'Agent Workforce tracks identity, role, trust, and live collaboration pressure.',
        objective: 'Show who is carrying work and where the command picture is weak.',
        shellNote: 'Drawer pivots toward dossiers, messages, and role structure.',
    },
    'context-lab': {
        eyebrow: 'Context engineering',
        summary: 'Context Lab is where retrieval, packets, and memory topology are tuned.',
        objective: 'Improve how the organism sees itself without hiding epistemic uncertainty.',
        shellNote: 'Bottom stays useful for diagnostics because retrieval drift is usually a substrate issue.',
    },
    oracle: {
        eyebrow: 'Adjudication',
        summary: 'Oracle hosts approvals, doctrine review, and high-authority intervention points.',
        objective: 'Keep autonomy legible and reversible.',
        shellNote: 'Approvals surface moves left; assistant rail favors memory and evidence.',
    },
    'infra-console': {
        eyebrow: 'Service plane',
        summary: 'Infra Console is the machine room for bridges, services, credentials, and degraded mode recovery.',
        objective: 'Reduce transport archaeology into visible service truth.',
        shellNote: 'Bottom switches to diagnostics by default and keeps failure seams visible.',
    },
    'code-editor': {
        eyebrow: 'Builder lane',
        summary: 'Builder is the production workbench for editing, patching, and implementation handoffs.',
        objective: 'Preserve coding focus while keeping cockpit truth one click away.',
        shellNote: 'Drawer can collapse completely; diagnostics remain docked below.',
    },
};
