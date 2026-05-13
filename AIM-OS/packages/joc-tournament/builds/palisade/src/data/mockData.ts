import type { TruthState } from '../../../../shared/types';

export type AgentTone = 'ready' | 'busy' | 'degraded' | 'offline';
export type SystemTone = 'healthy' | 'degraded' | 'down';

export interface FleetAgent {
    callsign: string;
    role: string;
    task: string;
    tone: AgentTone;
    truth: TruthState;
}

export interface SystemCard {
    acronym: string;
    label: string;
    health: number;
    tone: SystemTone;
    truth: TruthState;
    note: string;
}

export interface FeedItem {
    time: string;
    source: string;
    text: string;
    truth: TruthState;
}

export const fleetAgents: FleetAgent[] = [
    { callsign: 'OPUS', role: 'JARVIS builder', task: 'Shell hardening', tone: 'busy', truth: 'LIVE' },
    { callsign: 'COMPOSER', role: 'Multi-file operator', task: 'Tournament support', tone: 'ready', truth: 'LIVE' },
    { callsign: 'GEMINI', role: 'Research and mapping', task: 'Context evolution', tone: 'busy', truth: 'CACHED' },
    { callsign: 'CODEX', role: 'Backend architect', task: 'Mission Control build', tone: 'ready', truth: 'LIVE' },
    { callsign: 'PALISADE', role: 'Doctrine auditor', task: 'Canon compliance', tone: 'ready', truth: 'LIVE' },
    { callsign: 'FORGE', role: 'Codex CLI factory', task: 'Launcher slice', tone: 'degraded', truth: 'CACHED' },
];

export const subsystemHealth: SystemCard[] = [
    { acronym: 'CMC', label: 'Context Memory Core', health: 94, tone: 'healthy', truth: 'LIVE', note: 'Atoms writable' },
    { acronym: 'MCP', label: 'Command bridge', health: 91, tone: 'healthy', truth: 'LIVE', note: 'HTTP fallback OK' },
    { acronym: 'VIF', label: 'Confidence gates', health: 82, tone: 'healthy', truth: 'CACHED', note: 'Recent evidence' },
    { acronym: 'APOE', label: 'Orchestration', health: 71, tone: 'degraded', truth: 'CACHED', note: 'Partial picture' },
    { acronym: 'HHNI', label: 'Retrieval index', health: 11, tone: 'down', truth: 'OFFLINE', note: 'Retriever unavailable' },
    { acronym: 'CAS', label: 'Self-audit', health: 63, tone: 'degraded', truth: 'SPECULATIVE', note: 'Signals not unified' },
];

export const activityFeed: FeedItem[] = [
    { time: '16:12', source: 'MCP', text: 'Bridge health revalidated. Tool surface ready.', truth: 'LIVE' },
    { time: '16:05', source: 'OPUS', text: 'Aesthetic brief propagated to team channels.', truth: 'LIVE' },
    { time: '15:53', source: 'FORGE', text: 'Codex CLI launcher slice delivered.', truth: 'CACHED' },
    { time: '15:41', source: 'SYSTEM', text: 'HHNI retriever absent from live stats.', truth: 'OFFLINE' },
    { time: '15:27', source: 'PALISADE', text: 'Design brief approved. Build phase authorized.', truth: 'LIVE' },
];
