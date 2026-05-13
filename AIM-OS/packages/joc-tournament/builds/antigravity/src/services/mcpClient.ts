// ─── MCP HTTP Client ───
// Connects J.A.R.V.I.S. to the AIM-OS MCP server at localhost:5001

const MCP_BASE_URLS = [
    'http://localhost:5001',
    'http://127.0.0.1:5001',
    // Fallback bridge port (kept separate from Cursor command server).
    'http://localhost:5003',
    'http://127.0.0.1:5003',
];

export type ConnectionState = 'connected' | 'disconnected' | 'connecting' | 'error';

interface MCPResponse<T = unknown> {
    success: boolean;
    result?: T;
    error?: string;
}

let connectionState: ConnectionState = 'disconnected';
let lastLatency = 0;
const listeners = new Set<(state: ConnectionState) => void>();

function notifyListeners(state: ConnectionState) {
    connectionState = state;
    listeners.forEach(fn => fn(state));
}

export function onConnectionChange(fn: (state: ConnectionState) => void) {
    listeners.add(fn);
    return () => listeners.delete(fn);
}

export function getConnectionState(): ConnectionState {
    return connectionState;
}

export function getLastLatency(): number {
    return lastLatency;
}

/**
 * Call an MCP tool via the HTTP bridge
 */
export async function callTool<T = unknown>(
    tool: string,
    args: Record<string, unknown> = {},
    retries = 2
): Promise<T | null> {
    const start = performance.now();

    for (let attempt = 0; attempt <= retries; attempt++) {
        for (const baseUrl of MCP_BASE_URLS) {
            try {
                if (connectionState === 'disconnected') {
                    notifyListeners('connecting');
                }

                const timeoutMs = baseUrl.includes(':5003') ? 150000 : 8000;
                const response = await fetch(`${baseUrl}/mcp/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tool, arguments: args }),
                    signal: AbortSignal.timeout(timeoutMs),
                });

                lastLatency = Math.round(performance.now() - start);

                if (!response.ok) {
                    continue;
                }

                const data: MCPResponse<T> = await response.json();
                notifyListeners('connected');

                if (data.success && data.result !== undefined) {
                    return data.result;
                }
                return null;
            } catch (_err) {
                // Try next MCP endpoint candidate.
            }
        }

        if (attempt === retries) {
            notifyListeners(connectionState === 'connecting' ? 'disconnected' : 'error');
            return null;
        }
        // Exponential backoff
        await new Promise(r => setTimeout(r, 500 * Math.pow(2, attempt)));
    }
    return null;
}

/**
 * Check MCP server health
 */
export async function checkHealth(): Promise<boolean> {
    for (const baseUrl of MCP_BASE_URLS) {
        try {
            const response = await fetch(`${baseUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000),
            });
            if (response.ok) {
                notifyListeners('connected');
                return true;
            }
        } catch {
            // Try next endpoint candidate.
        }
    }
    notifyListeners('disconnected');
    return false;
}

// ─── Typed Tool Wrappers ───

export interface MemoryStats {
    total_atoms?: number;
    total_molecules?: number;
    total_snapshots?: number;
    storage_size?: string;
    [key: string]: unknown;
}

export interface TimelineEntry {
    prompt_id: string;
    user_input: string;
    timestamp?: string;
    context_state?: Record<string, unknown>;
    [key: string]: unknown;
}

export interface ConsciousnessMetrics {
    cognitive_drift?: number;
    attention_load?: number;
    failure_rate?: number;
    working_memory_items?: number;
    [key: string]: unknown;
}

export interface AIMessage {
    id?: string;
    from_ai: string;
    to_ai: string;
    content: string;
    message_type?: string;
    priority?: string;
    timestamp?: string;
    thread_id?: string;
    [key: string]: unknown;
}

export interface Goal {
    goal_id: string;
    name: string;
    description: string;
    status: string;
    progress: number;
    priority?: string;
    [key: string]: unknown;
}

export interface ProblemSummary {
    errors?: number;
    warnings?: number;
    info?: number;
    hints?: number;
    total?: number;
    [key: string]: unknown;
}

export const mcp = {
    getMemoryStats: () => callTool<MemoryStats>('get_memory_stats'),
    getTimelineSummary: (limit = 10) => callTool<{ entries?: TimelineEntry[] }>('get_timeline_summary', { limit }),
    getConsciousnessMetrics: () => callTool<ConsciousnessMetrics>('get_consciousness_metrics'),
    getAIMessages: (limit = 20) => callTool<{ messages?: AIMessage[] }>('get_ai_messages', { limit }),
    getGoals: () => callTool<{ goals?: Goal[] }>('query_goal_timeline', {}),
    getProblemSummary: () => callTool<ProblemSummary>('get_problem_summary'),
    getCollaborationSummary: () => callTool<Record<string, unknown>>('get_ai_collaboration_summary'),
    sendAIMessage: (from: string, to: string, content: string, type = 'discussion', priority = 'medium') =>
        callTool('send_ai_message', { from_ai: from, to_ai: to, content, message_type: type, priority }),
    storeMemory: (content: string, tags?: Record<string, unknown>) =>
        callTool('store_memory', { content, tags }),
    // ─── Infrastructure Control ───
    listTerminals: () => callTool<{ terminals?: Array<{ name: string; index: number; state: string }> }>('list_terminals'),
    getHHNIStatus: () => callTool<Record<string, unknown>>('get_hhni_status'),
};
