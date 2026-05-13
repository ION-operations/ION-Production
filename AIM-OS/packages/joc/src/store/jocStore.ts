import { create } from 'zustand';

// ─── Types ───

export type DrawerType = 'dashboard' | 'fleet' | 'missions' | 'comms' | 'projects' | 'compute' | 'settings';
export type DrawerPosition = 'full' | 'top' | 'bottom';
export type PageType = 'dashboard' | 'session' | 'mission' | 'projects' | 'editor' | 'atlas' | 'compute' | 'dispatch' | 'synthesizer' | 'comms' | 'health' | 'context' | 'vault' | 'cli' | 'storage' | 'settings' | 'mission-builder' | 'gpu' | 'activity' | 'welcome' | 'context-graph' | 'calendar' | 'oracle' | 'agent-builder' | 'diagnostics' | 'surface-demo' | 'context-lab' | 'infra' | 'agent-workforce' | 'intelligence-map';
export type BottomPanelTab = 'timeline' | 'comms' | 'output' | 'missions' | 'resources' | 'terminal' | 'console' | 'diagnostics';
export type BottomPanelSize = 'collapsed' | 'mid' | 'full';

// Left drawer system — page-specific
export type LeftDrawerType = string;

export interface LeftDrawerDef {
    type: string;
    label: string;
}

export interface OpenLeftDrawer {
    type: LeftDrawerType;
    position: DrawerPosition;
}

export interface OpenDrawer {
    type: DrawerType;
    position: DrawerPosition;
}

export interface PageTab {
    id: string;
    type: PageType;
    label: string;
    closable: boolean;
    data?: Record<string, unknown>;
}

export interface AISession {
    id: string;
    name: string;
    provider: 'chatgpt' | 'gemini' | 'claude' | 'perplexity' | 'gemini-cli' | 'local';
    status: 'active' | 'sleeping' | 'dead';
    health: number; // 0-100
    uptime: string;
    lastActivity: string;
}

export interface Mission {
    id: string;
    title: string;
    status: 'draft' | 'dispatched' | 'running' | 'complete' | 'failed';
    progress: number; // 0-100
    targets: string[];
    prompt?: string;
    createdAt: string;
}

export interface ActivityItem {
    id: string;
    time: string;
    text: string;
    type: 'mission' | 'agent' | 'system' | 'user';
}

// ─── Store ───

interface JOCState {
    // Layout — Right drawers (universal)
    openDrawers: OpenDrawer[];
    activeTab: string;
    tabs: PageTab[];
    bottomPanelSize: BottomPanelSize;
    bottomActiveTab: BottomPanelTab;
    drawerSubTabs: Record<DrawerType, string>;

    // Layout — Left drawers (page-specific)
    leftOpenDrawers: OpenLeftDrawer[];
    leftDrawerSubTabs: Record<string, string>;

    // Data (mock for now, will connect to MCP)
    sessions: AISession[];
    missions: Mission[];
    activity: ActivityItem[];

    // Actions — Right drawers
    toggleDrawer: (type: DrawerType, position: DrawerPosition) => void;
    closeDrawer: (type: DrawerType) => void;
    closeAllDrawers: () => void;
    setActiveTab: (id: string) => void;
    addTab: (tab: PageTab) => void;
    closeTab: (id: string) => void;
    toggleBottomPanel: () => void;
    setBottomPanelSize: (size: BottomPanelSize) => void;
    setBottomTab: (tab: BottomPanelTab) => void;
    setDrawerSubTab: (drawer: DrawerType, tab: string) => void;

    // Actions — Mission tracking
    addMission: (mission: Mission) => void;
    updateMission: (id: string, updates: Partial<Mission>) => void;

    // Actions — Left drawers
    toggleLeftDrawer: (type: LeftDrawerType, position: DrawerPosition) => void;
    closeLeftDrawer: (type: LeftDrawerType) => void;
    closeAllLeftDrawers: () => void;
    setLeftDrawerSubTab: (drawer: string, tab: string) => void;
}

// ─── Mock Data ───

const MOCK_SESSIONS: AISession[] = [
    { id: 'gpt-1', name: 'ChatGPT Pro', provider: 'chatgpt', status: 'active', health: 92, uptime: '4h 23m', lastActivity: 'Analyzing WGSL limits' },
    { id: 'gem-1', name: 'Gemini Ultra', provider: 'gemini', status: 'active', health: 88, uptime: '2h 15m', lastActivity: 'Idle (ready)' },
    { id: 'perp-1', name: 'Perplexity Pro', provider: 'perplexity', status: 'sleeping', health: 65, uptime: '45m ago', lastActivity: 'WebGPU compute limits' },
    { id: 'claude-1', name: 'Claude.ai', provider: 'claude', status: 'sleeping', health: 30, uptime: '1h ago', lastActivity: 'Session saved' },
];

const MOCK_MISSIONS: Mission[] = [
    { id: 'M-42', title: 'WGSL compute limits analysis', status: 'running', progress: 70, targets: ['chatgpt', 'gemini'], createdAt: '09:30' },
    { id: 'M-41', title: 'Runbook compilation', status: 'complete', progress: 100, targets: ['gemini-cli'], createdAt: '08:45' },
];

const MOCK_ACTIVITY: ActivityItem[] = [
    { id: 'a1', time: '09:45', text: 'Mission #42: ChatGPT response extracted', type: 'mission' },
    { id: 'a2', time: '09:42', text: 'Opus → Aether: "Design docs ready"', type: 'agent' },
    { id: 'a3', time: '09:38', text: 'Gemini CLI: Batch job complete (50/50)', type: 'system' },
    { id: 'a4', time: '09:35', text: 'Mission #41 completed successfully', type: 'mission' },
    { id: 'a5', time: '09:30', text: 'Mission #42 dispatched to ChatGPT + Gemini', type: 'mission' },
    { id: 'a6', time: '09:28', text: 'Perplexity session entered sleep mode', type: 'system' },
];

const DEFAULT_TABS: PageTab[] = [
    { id: 'dashboard', type: 'dashboard', label: 'Dashboard', closable: false },
    { id: 'intelligence-map', type: 'intelligence-map', label: 'V3 OS Explorer', closable: false },
    { id: 'editor', type: 'editor', label: 'Code Editor', closable: false },
    { id: 'atlas', type: 'atlas', label: 'System Atlas', closable: false },
];

// ─── Create Store ───

export const useJOCStore = create<JOCState>((set, get) => ({
    // Layout state — Right drawers (universal)
    openDrawers: [],
    activeTab: 'dashboard',
    tabs: DEFAULT_TABS,
    bottomPanelSize: 'collapsed' as BottomPanelSize,
    bottomActiveTab: 'timeline',
    drawerSubTabs: {
        dashboard: 'overview',
        fleet: 'sessions',
        missions: 'active',
        comms: 'all',
        projects: 'active',
        compute: 'local',
        settings: 'general',
    },

    // Layout state — Left drawers (page-specific)
    leftOpenDrawers: [],
    leftDrawerSubTabs: {},

    // Mock data
    sessions: MOCK_SESSIONS,
    missions: MOCK_MISSIONS,
    activity: MOCK_ACTIVITY,

    // ─── Drawer Actions (Lucid Pattern) ───
    toggleDrawer: (type, position) => {
        const { openDrawers } = get();
        const existing = openDrawers.find(d => d.type === type);

        // If already open at same position, close it
        if (existing && existing.position === position) {
            set({ openDrawers: openDrawers.filter(d => d.type !== type) });
            return;
        }

        let newDrawers = [...openDrawers];

        if (position === 'full') {
            // Full replaces everything
            newDrawers = [{ type, position: 'full' }];
        } else if (position === 'top') {
            const bottom = newDrawers.find(d => d.position === 'bottom');
            const top = newDrawers.find(d => d.position === 'top');
            if (top) {
                // Replace existing top, keep bottom
                newDrawers = bottom
                    ? [{ type, position: 'top' }, bottom]
                    : [{ type, position: 'top' }, { type: top.type, position: 'bottom' }];
            } else {
                newDrawers = newDrawers.filter(d => d.position !== 'full');
                newDrawers = bottom
                    ? [{ type, position: 'top' }, bottom]
                    : [{ type, position: 'top' }];
            }
        } else if (position === 'bottom') {
            const top = newDrawers.find(d => d.position === 'top');
            const bottom = newDrawers.find(d => d.position === 'bottom');
            if (bottom) {
                newDrawers = top
                    ? [top, { type, position: 'bottom' }]
                    : [{ type: bottom.type, position: 'top' }, { type, position: 'bottom' }];
            } else {
                newDrawers = newDrawers.filter(d => d.position !== 'full');
                newDrawers = top
                    ? [top, { type, position: 'bottom' }]
                    : [{ type, position: 'bottom' }];
            }
        }

        set({ openDrawers: newDrawers });
    },

    closeDrawer: (type) => {
        set({ openDrawers: get().openDrawers.filter(d => d.type !== type) });
    },

    closeAllDrawers: () => {
        set({ openDrawers: [] });
    },

    // ─── Tab Actions ───
    setActiveTab: (id) => set({ activeTab: id }),

    addTab: (tab) => {
        const { tabs } = get();
        if (!tabs.find(t => t.id === tab.id)) {
            set({ tabs: [...tabs, tab], activeTab: tab.id });
        } else {
            set({ activeTab: tab.id });
        }
    },

    closeTab: (id) => {
        const { tabs, activeTab } = get();
        const newTabs = tabs.filter(t => t.id !== id);
        if (activeTab === id) {
            set({ tabs: newTabs, activeTab: newTabs[newTabs.length - 1]?.id || 'dashboard' });
        } else {
            set({ tabs: newTabs });
        }
    },

    // ─── Bottom Panel Actions ───
    toggleBottomPanel: () => {
        const sizes: BottomPanelSize[] = ['collapsed', 'mid', 'full'];
        const current = sizes.indexOf(get().bottomPanelSize);
        set({ bottomPanelSize: sizes[(current + 1) % sizes.length] });
    },
    setBottomPanelSize: (size) => set({ bottomPanelSize: size }),
    setBottomTab: (tab) => set({ bottomActiveTab: tab }),

    // ─── Drawer Sub-Tab Actions ───
    setDrawerSubTab: (drawer, tab) => {
        set({ drawerSubTabs: { ...get().drawerSubTabs, [drawer]: tab } });
    },

    // ─── Mission Tracking ───
    addMission: (mission) => {
        set({ missions: [...get().missions, mission] });
    },
    updateMission: (id, updates) => {
        set({
            missions: get().missions.map(m =>
                m.id === id ? { ...m, ...updates } : m
            ),
        });
    },

    // ─── Left Drawer Actions (Lucid Pattern — mirrored) ───
    toggleLeftDrawer: (type, position) => {
        const { leftOpenDrawers } = get();
        const existing = leftOpenDrawers.find(d => d.type === type);

        if (existing && existing.position === position) {
            set({ leftOpenDrawers: leftOpenDrawers.filter(d => d.type !== type) });
            return;
        }

        let newDrawers = [...leftOpenDrawers];

        if (position === 'full') {
            newDrawers = [{ type, position: 'full' }];
        } else if (position === 'top') {
            const bottom = newDrawers.find(d => d.position === 'bottom');
            const top = newDrawers.find(d => d.position === 'top');
            if (top) {
                newDrawers = bottom
                    ? [{ type, position: 'top' }, bottom]
                    : [{ type, position: 'top' }, { type: top.type, position: 'bottom' }];
            } else {
                newDrawers = newDrawers.filter(d => d.position !== 'full');
                newDrawers = bottom
                    ? [{ type, position: 'top' }, bottom]
                    : [{ type, position: 'top' }];
            }
        } else if (position === 'bottom') {
            const top = newDrawers.find(d => d.position === 'top');
            const bottom = newDrawers.find(d => d.position === 'bottom');
            if (bottom) {
                newDrawers = top
                    ? [top, { type, position: 'bottom' }]
                    : [{ type: bottom.type, position: 'top' }, { type, position: 'bottom' }];
            } else {
                newDrawers = newDrawers.filter(d => d.position !== 'full');
                newDrawers = top
                    ? [top, { type, position: 'bottom' }]
                    : [{ type, position: 'bottom' }];
            }
        }

        set({ leftOpenDrawers: newDrawers });
    },

    closeLeftDrawer: (type) => {
        set({ leftOpenDrawers: get().leftOpenDrawers.filter(d => d.type !== type) });
    },

    closeAllLeftDrawers: () => {
        set({ leftOpenDrawers: [] });
    },

    setLeftDrawerSubTab: (drawer, tab) => {
        set({ leftDrawerSubTabs: { ...get().leftDrawerSubTabs, [drawer]: tab } });
    },
}));
