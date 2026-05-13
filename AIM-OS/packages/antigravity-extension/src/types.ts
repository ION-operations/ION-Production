/** Shared types for the Antigravity Console extension. */

export interface SystemHealth {
    mcp: { status: 'online' | 'offline' | 'error'; toolCount: number };
    cmc: { status: 'online' | 'offline' | 'error'; atomCount: number; backend: string };
    hhni: { indexAvailable: boolean; retrieverAvailable: boolean };
    vif: { kappaGateAvailable: boolean; eceAvailable: boolean };
    timestamp: string;
}

export interface GhostStatus {
    bridgeHealthy: boolean;
    lastChecked: string;
    latencyMs: number | null;
    lastMessageTimestamp: string | null;
    unreadCount: number;
}

export interface AgentMessage {
    id: string;
    from: string;
    to: string;
    content: string;
    type: string;
    priority: string;
    timestamp: string;
}

export interface MemoryPulse {
    totalAtoms: number;
    sessionAtoms: number;
    lastStoreTime: string | null;
    lastConfidence: number | null;
    integrityOk: boolean;
}

export interface DashboardState {
    system: SystemHealth;
    ghost: GhostStatus;
    memory: MemoryPulse;
    messages: AgentMessage[];
    lastRefresh: string;
}

/** Messages sent from extension host → webview */
export type ExtToWebviewMessage =
    | { type: 'updateDashboard'; data: DashboardState }
    | { type: 'updateGhost'; data: GhostStatus }
    | { type: 'updateMessages'; data: AgentMessage[] }
    | { type: 'showError'; message: string }
    | { type: 'showInfo'; message: string };

/** Messages sent from webview → extension host */
export type WebviewToExtMessage =
    | { type: 'refresh' }
    | { type: 'sendMessage'; to: string; content: string }
    | { type: 'storeMemory'; content: string }
    | { type: 'checkGhost' }
    | { type: 'ready' };
