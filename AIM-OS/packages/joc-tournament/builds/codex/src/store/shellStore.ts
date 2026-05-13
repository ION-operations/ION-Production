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
export type BottomView = 'chronicle' | 'diagnostics';

interface ShellState {
    activeWorkspace: WorkspaceId;
    leftDrawerOpen: boolean;
    assistantOpen: boolean;
    assistantMode: AssistantMode;
    bottomExpanded: boolean;
    bottomView: BottomView;
    setWorkspace: (workspace: WorkspaceId) => void;
    toggleLeftDrawer: () => void;
    toggleAssistant: () => void;
    setAssistantMode: (mode: AssistantMode) => void;
    toggleBottom: () => void;
    setBottomView: (view: BottomView) => void;
}

export const useShellStore = create<ShellState>((set) => ({
    activeWorkspace: 'dashboard',
    leftDrawerOpen: true,
    assistantOpen: true,
    assistantMode: 'chat',
    bottomExpanded: false,
    bottomView: 'chronicle',
    setWorkspace: (workspace) =>
        set((state) => ({
            activeWorkspace: workspace,
            leftDrawerOpen: true,
            bottomView: workspace === 'infra-console' || workspace === 'code-editor' ? 'diagnostics' : state.bottomView,
        })),
    toggleLeftDrawer: () => set((state) => ({ leftDrawerOpen: !state.leftDrawerOpen })),
    toggleAssistant: () => set((state) => ({ assistantOpen: !state.assistantOpen })),
    setAssistantMode: (mode) => set({ assistantMode: mode }),
    toggleBottom: () => set((state) => ({ bottomExpanded: !state.bottomExpanded })),
    setBottomView: (view) => set({ bottomView: view }),
}));
