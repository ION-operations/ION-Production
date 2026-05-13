import { create } from 'zustand';

// ─── Types ──────────────────────────────────────────────────────────

export type NavGroup = 'operations' | 'intelligence' | 'infrastructure' | 'tools';
export type RailMode = 'chat' | 'context' | 'actions' | 'memory';
export type TruthState = 'LIVE' | 'CACHED' | 'MOCK' | 'OFFLINE' | 'SPECULATIVE';

export interface Workspace {
    id: string;
    title: string;
    navGroup: NavGroup;
    icon: string;  // emoji for now
    description: string;
    primary: boolean;
}

export const WORKSPACES: Workspace[] = [
    // Operations
    { id: 'dashboard', title: 'Mission Control', navGroup: 'operations', icon: '◎', description: 'Central command overview', primary: true },
    { id: 'dispatch', title: 'Dispatch', navGroup: 'operations', icon: '⭷', description: 'Multi-target prompt dispatch', primary: true },
    { id: 'mission-builder', title: 'Mission Builder', navGroup: 'operations', icon: '⊞', description: 'Compose multi-step missions', primary: false },
    { id: 'calendar', title: 'Calendar', navGroup: 'operations', icon: '▦', description: 'Scheduled missions & events', primary: false },
    // Intelligence
    { id: 'agent-workforce', title: 'Agent Workforce', navGroup: 'intelligence', icon: '⬡', description: 'Agent fleet monitoring', primary: true },
    { id: 'context-lab', title: 'Context Lab', navGroup: 'intelligence', icon: '⎔', description: 'Context strategy evolution', primary: true },
    { id: 'oracle', title: 'Oracle', navGroup: 'intelligence', icon: '⚡', description: 'Approvals & autonomy control', primary: true },
    { id: 'context-graph', title: 'Context Graph', navGroup: 'intelligence', icon: '◇', description: 'Force-directed visualization', primary: false },
    { id: 'session', title: 'Session', navGroup: 'intelligence', icon: '◉', description: 'Active AI session management', primary: false },
    // Infrastructure
    { id: 'infra-console', title: 'Infra Console', navGroup: 'infrastructure', icon: '⊟', description: 'Infrastructure control plane', primary: true },
    { id: 'system-atlas', title: 'System Atlas', navGroup: 'infrastructure', icon: '◎', description: 'Spatial architecture map', primary: false },
    // Tools
    { id: 'code-editor', title: 'Code Editor', navGroup: 'tools', icon: '⌨', description: 'AI-enhanced Monaco editor', primary: true },
];

export const NAV_GROUPS: { id: NavGroup; label: string }[] = [
    { id: 'operations', label: 'OPERATIONS' },
    { id: 'intelligence', label: 'INTELLIGENCE' },
    { id: 'infrastructure', label: 'INFRASTRUCTURE' },
    { id: 'tools', label: 'TOOLS' },
];

// ─── Shell Store ──────────────────────────────────────────────────

interface ShellState {
    // Workspace
    activeWorkspace: string;
    setActiveWorkspace: (id: string) => void;

    // Left drawer
    leftDrawerOpen: boolean;
    toggleLeftDrawer: () => void;

    // Assistant rail
    railExpanded: boolean;
    railMode: RailMode;
    toggleRail: () => void;
    setRailMode: (mode: RailMode) => void;

    // Bottom bar
    bottomExpanded: boolean;
    activeBottomTab: string;
    toggleBottom: () => void;
    setBottomTab: (tab: string) => void;

    // Nav dropdown
    openNavGroup: string | null;
    setOpenNavGroup: (group: string | null) => void;
}

export const useShellStore = create<ShellState>((set) => ({
    activeWorkspace: 'dashboard',
    setActiveWorkspace: (id) => set({ activeWorkspace: id, openNavGroup: null }),

    leftDrawerOpen: true,
    toggleLeftDrawer: () => set((s) => ({ leftDrawerOpen: !s.leftDrawerOpen })),

    railExpanded: true,
    railMode: 'chat',
    toggleRail: () => set((s) => ({ railExpanded: !s.railExpanded })),
    setRailMode: (mode) => set({ railMode: mode, railExpanded: true }),

    bottomExpanded: false,
    activeBottomTab: 'activity',
    toggleBottom: () => set((s) => ({ bottomExpanded: !s.bottomExpanded })),
    setBottomTab: (tab) => set({ activeBottomTab: tab, bottomExpanded: true }),

    openNavGroup: null,
    setOpenNavGroup: (group) => set((s) => ({
        openNavGroup: s.openNavGroup === group ? null : group,
    })),
}));
