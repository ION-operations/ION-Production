import { create } from 'zustand';

// ─── Types ───

/** Oracle autonomy modes per the canon */
export type OracleMode = 'auto' | 'supervised' | 'manual' | 'offline';

/** Per-system permission level */
export type PermissionLevel = 'auto' | 'supervised' | 'manual';

/** Systems that Oracle can control */
export type OracleSystem =
    | 'dispatch'
    | 'scheduler'
    | 'macros'
    | 'sessions'
    | 'vault'
    | 'agentComms'
    | 'settings';

/** A single Oracle action log entry */
export interface OracleAction {
    id: string;
    timestamp: string;
    system: OracleSystem;
    action: string;
    mode: 'auto' | 'supervised';
    status: 'executed' | 'approved' | 'denied' | 'pending';
    detail?: string;
}

// ─── Store ───

interface OracleState {
    /** Global Oracle mode — the "master switch" shown in TopBar */
    mode: OracleMode;

    /** Per-system permissions — overrides global mode */
    permissions: Record<OracleSystem, PermissionLevel>;

    /** Whether the Oracle connection is healthy */
    connected: boolean;

    /** Tasks per minute the Oracle is performing (0 = idle) */
    actionsPerMinute: number;

    /** Recent Oracle action log (last 50 entries) */
    actionLog: OracleAction[];

    /** Pending approval requests count */
    pendingApprovals: number;

    // ─── Actions ───
    setMode: (mode: OracleMode) => void;
    cycleMode: () => void;
    setPermission: (system: OracleSystem, level: PermissionLevel) => void;
    setConnected: (connected: boolean) => void;
    logAction: (action: Omit<OracleAction, 'id' | 'timestamp'>) => void;
    approveAction: (id: string) => void;
    denyAction: (id: string) => void;
    clearLog: () => void;
}

// ─── Default Permissions (per canon) ───
// Vault and Settings are ALWAYS manual — Oracle cannot access them in auto mode

const DEFAULT_PERMISSIONS: Record<OracleSystem, PermissionLevel> = {
    dispatch: 'supervised',
    scheduler: 'supervised',
    macros: 'supervised',
    sessions: 'manual',
    vault: 'manual',        // NEVER auto — canon rule
    agentComms: 'supervised',
    settings: 'manual',     // NEVER auto — canon rule
};

// ─── Mock Action Log ───

const MOCK_LOG: OracleAction[] = [
    { id: 'oa-1', timestamp: '2026-03-03T16:30:00', system: 'dispatch', action: 'Dispatched M-043 to ChatGPT + Gemini', mode: 'auto', status: 'executed' },
    { id: 'oa-2', timestamp: '2026-03-03T16:28:15', system: 'macros', action: 'Triggered "Morning Brief" macro', mode: 'auto', status: 'executed' },
    { id: 'oa-3', timestamp: '2026-03-03T16:25:00', system: 'vault', action: 'Requested Vault access', mode: 'supervised', status: 'denied', detail: 'Requires explicit user approval' },
    { id: 'oa-4', timestamp: '2026-03-03T16:22:00', system: 'sessions', action: 'Refreshed Perplexity session', mode: 'supervised', status: 'approved' },
];

// ─── Create Store ───

export const useOracleStore = create<OracleState>((set, get) => ({
    mode: 'supervised',
    permissions: { ...DEFAULT_PERMISSIONS },
    connected: true,
    actionsPerMinute: 3.2,
    actionLog: MOCK_LOG,
    pendingApprovals: 0,

    setMode: (mode) => set({ mode }),

    cycleMode: () => {
        const modes: OracleMode[] = ['auto', 'supervised', 'manual'];
        const current = modes.indexOf(get().mode);
        const next = current === -1 ? 1 : (current + 1) % modes.length;
        set({ mode: modes[next] });
    },

    setPermission: (system, level) => {
        // Canon enforcement: vault and settings CANNOT be set to auto
        if ((system === 'vault' || system === 'settings') && level === 'auto') {
            console.warn(`[Oracle] Canon violation: ${system} cannot be set to "auto" mode`);
            return;
        }
        set({ permissions: { ...get().permissions, [system]: level } });
    },

    setConnected: (connected) => set({ connected }),

    logAction: (action) => {
        const entry: OracleAction = {
            ...action,
            id: `oa-${Date.now()}`,
            timestamp: new Date().toISOString(),
        };
        const log = [entry, ...get().actionLog].slice(0, 50);
        set({ actionLog: log });
    },

    approveAction: (id) => {
        set({
            actionLog: get().actionLog.map(a =>
                a.id === id ? { ...a, status: 'approved' as const } : a
            ),
            pendingApprovals: Math.max(0, get().pendingApprovals - 1),
        });
    },

    denyAction: (id) => {
        set({
            actionLog: get().actionLog.map(a =>
                a.id === id ? { ...a, status: 'denied' as const } : a
            ),
            pendingApprovals: Math.max(0, get().pendingApprovals - 1),
        });
    },

    clearLog: () => set({ actionLog: [] }),
}));
