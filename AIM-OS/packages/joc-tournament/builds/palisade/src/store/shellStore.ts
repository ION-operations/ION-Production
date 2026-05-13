import { create } from 'zustand';

export const PRIMARY_WORKSPACE_IDS = [
    'dashboard',
    'dispatch',
    'agent-workforce',
    'context-lab',
    'oracle',
    'infra-console',
    'code-editor',
] as const;

export type WorkspaceId = (typeof PRIMARY_WORKSPACE_IDS)[number];
export type AssistantMode = 'chat' | 'context' | 'actions' | 'memory';

interface ShellState {
    activeWorkspace: WorkspaceId;
    leftDrawerOpen: boolean;
    assistantOpen: boolean;
    assistantMode: AssistantMode;
    bottomExpanded: boolean;
    setWorkspace: (workspace: WorkspaceId) => void;
    toggleLeftDrawer: () => void;
    toggleAssistant: () => void;
    setAssistantMode: (mode: AssistantMode) => void;
    toggleBottom: () => void;
}

export const useShellStore = create<ShellState>((set) => ({
    activeWorkspace: 'dashboard',
    leftDrawerOpen: true,
    assistantOpen: true,
    assistantMode: 'context',
    bottomExpanded: true,
    setWorkspace: (workspace) =>
        set({
            activeWorkspace: workspace,
            leftDrawerOpen: true,
        }),
    toggleLeftDrawer: () => set((state) => ({ leftDrawerOpen: !state.leftDrawerOpen })),
    toggleAssistant: () => set((state) => ({ assistantOpen: !state.assistantOpen })),
    setAssistantMode: (mode) => set({ assistantMode: mode }),
    toggleBottom: () => set((state) => ({ bottomExpanded: !state.bottomExpanded })),
}));
