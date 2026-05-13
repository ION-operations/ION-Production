import { create } from 'zustand';

// ═══════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════

export type TruthState = 'LIVE' | 'CACHED' | 'MOCK' | 'OFFLINE' | 'SPECULATIVE';

export type AgentStatus = 'active' | 'idle' | 'error' | 'offline';
export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  currentTask: string;
  uptime: string;
}

export type MissionStatus = 'running' | 'queued' | 'complete' | 'failed' | 'paused';
export interface Mission {
  id: string;
  name: string;
  status: MissionStatus;
  agent: string;
  progress: number;
  elapsed: string;
  target: string;
}

export type SystemId = 'CMC' | 'HHNI' | 'VIF' | 'SEG' | 'APOE' | 'TCS' | 'CAS' | 'MCP';
export interface SubsystemStatus {
  id: SystemId;
  name: string;
  health: number;
  status: 'online' | 'degraded' | 'offline';
  latency: number;
}

export type ActivityType = 'mission' | 'agent' | 'system' | 'user';
export interface ActivityEvent {
  id: string;
  type: ActivityType;
  agent?: string;
  message: string;
  timestamp: string;
}

export type WorkspaceId =
  | 'mission-control' | 'dispatch' | 'agent-workforce'
  | 'context-lab' | 'oracle' | 'infra-console' | 'code-editor';

export type NavGroup = 'operations' | 'intelligence' | 'infrastructure' | 'tools';

export interface Workspace {
  id: WorkspaceId;
  title: string;
  navGroup: NavGroup;
  iconKey: string;
}

export type BottomBarSize = 'collapsed' | 'mid' | 'full';
export type BottomTab = 'timeline' | 'comms' | 'output' | 'terminal' | 'diagnostics';
export type AssistantMode = 'chat' | 'context' | 'actions' | 'memory';
export type OracleMode = 'AUTO' | 'SUPERVISED' | 'MANUAL' | 'OFFLINE';
export type LeftDrawerPanel = 'system-status' | 'agent-fleet' | 'mission-queue';

// ═══════════════════════════════════════════════════════════════
// Store
// ═══════════════════════════════════════════════════════════════

interface DashboardStore {
  activeWorkspace: WorkspaceId;
  setActiveWorkspace: (ws: WorkspaceId) => void;

  leftDrawerOpen: boolean;
  leftDrawerPanel: LeftDrawerPanel;
  toggleLeftDrawer: (panel: LeftDrawerPanel) => void;
  closeLeftDrawer: () => void;

  bottomBarSize: BottomBarSize;
  bottomActiveTab: BottomTab;
  setBottomBarSize: (size: BottomBarSize) => void;
  setBottomActiveTab: (tab: BottomTab) => void;

  assistantExpanded: boolean;
  assistantMode: AssistantMode;
  toggleAssistant: () => void;
  setAssistantMode: (mode: AssistantMode) => void;

  oracleMode: OracleMode;
  pendingApprovals: number;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  activeWorkspace: 'mission-control',
  setActiveWorkspace: (ws) => set({ activeWorkspace: ws }),

  leftDrawerOpen: true,
  leftDrawerPanel: 'system-status',
  toggleLeftDrawer: (panel) =>
    set((state) => ({
      leftDrawerOpen: state.leftDrawerPanel === panel && state.leftDrawerOpen ? false : true,
      leftDrawerPanel: panel,
    })),
  closeLeftDrawer: () => set({ leftDrawerOpen: false }),

  bottomBarSize: 'collapsed',
  bottomActiveTab: 'diagnostics',
  setBottomBarSize: (size) => set({ bottomBarSize: size }),
  setBottomActiveTab: (tab) => set({ bottomActiveTab: tab }),

  assistantExpanded: true,
  assistantMode: 'chat',
  toggleAssistant: () => set((state) => ({ assistantExpanded: !state.assistantExpanded })),
  setAssistantMode: (mode) => set({ assistantMode: mode, assistantExpanded: true }),

  oracleMode: 'SUPERVISED',
  pendingApprovals: 3,
}));

// ═══════════════════════════════════════════════════════════════
// Static Data
// ═══════════════════════════════════════════════════════════════

export const WORKSPACES: Workspace[] = [
  { id: 'mission-control', title: 'Mission Control', navGroup: 'operations', iconKey: 'radar' },
  { id: 'dispatch', title: 'Dispatch', navGroup: 'operations', iconKey: 'launch' },
  { id: 'agent-workforce', title: 'Agent Workforce', navGroup: 'intelligence', iconKey: 'constellation' },
  { id: 'context-lab', title: 'Context Lab', navGroup: 'intelligence', iconKey: 'hex' },
  { id: 'oracle', title: 'Oracle', navGroup: 'intelligence', iconKey: 'bolt' },
  { id: 'infra-console', title: 'Infra Console', navGroup: 'infrastructure', iconKey: 'chip' },
  { id: 'code-editor', title: 'Code Editor', navGroup: 'tools', iconKey: 'chip' },
];

export const NAV_GROUPS: { id: NavGroup; label: string; defaultWorkspace: WorkspaceId }[] = [
  { id: 'operations', label: 'OPERATIONS', defaultWorkspace: 'mission-control' },
  { id: 'intelligence', label: 'INTELLIGENCE', defaultWorkspace: 'agent-workforce' },
  { id: 'infrastructure', label: 'INFRASTRUCTURE', defaultWorkspace: 'infra-console' },
  { id: 'tools', label: 'TOOLS', defaultWorkspace: 'code-editor' },
];

// ═══════════════════════════════════════════════════════════════
// Mock Data — All surfaces declare MOCK truth state
// ═══════════════════════════════════════════════════════════════

export const MOCK_AGENTS: Agent[] = [
  { id: 'aether', name: 'Aether', role: 'Strategic Planner', status: 'active', currentTask: 'Context synthesis for Q1 roadmap', uptime: '4h 23m' },
  { id: 'codex', name: 'Codex', role: 'Backend Architect', status: 'active', currentTask: 'MCP gateway hardening', uptime: '6h 11m' },
  { id: 'dac', name: 'Dac', role: 'UI Engineer', status: 'idle', currentTask: 'Awaiting dispatch', uptime: '2h 45m' },
  { id: 'lex', name: 'Lex', role: 'Integration Specialist', status: 'active', currentTask: 'PDAS contradiction scan', uptime: '3h 08m' },
  { id: 'rev', name: 'Rev', role: 'Research Analyst', status: 'error', currentTask: 'HHNI index rebuild failed', uptime: '1h 32m' },
  { id: 'sam', name: 'Sam', role: 'Consciousness Monitor', status: 'offline', currentTask: 'Session expired', uptime: '0m' },
];

export const MOCK_SYSTEMS: SubsystemStatus[] = [
  { id: 'CMC', name: 'Context Memory Core', health: 0.94, status: 'online', latency: 12 },
  { id: 'HHNI', name: 'Holonic Nav Index', health: 0.87, status: 'online', latency: 45 },
  { id: 'VIF', name: 'Verifiable Intel Framework', health: 0.91, status: 'online', latency: 23 },
  { id: 'SEG', name: 'Semantic Evidence Graph', health: 0.78, status: 'degraded', latency: 89 },
  { id: 'APOE', name: 'Orchestration Engine', health: 0.96, status: 'online', latency: 18 },
  { id: 'TCS', name: 'Timeline Context Sys', health: 0.82, status: 'online', latency: 34 },
  { id: 'CAS', name: 'Cognitive Analysis Sys', health: 0.65, status: 'degraded', latency: 156 },
  { id: 'MCP', name: 'Model Context Protocol', health: 0.99, status: 'online', latency: 8 },
];

export const MOCK_MISSIONS: Mission[] = [
  { id: 'M-001', name: 'Context Synthesis Pipeline', status: 'running', agent: 'Aether', progress: 0.72, elapsed: '1h 14m', target: 'CMC + SEG' },
  { id: 'M-002', name: 'MCP Gateway Hardening', status: 'running', agent: 'Codex', progress: 0.45, elapsed: '2h 30m', target: 'MCP' },
  { id: 'M-003', name: 'PDAS Contradiction Audit', status: 'running', agent: 'Lex', progress: 0.88, elapsed: '45m', target: 'SEG + VIF' },
  { id: 'M-004', name: 'HHNI Index Rebuild', status: 'failed', agent: 'Rev', progress: 0.34, elapsed: '23m', target: 'HHNI' },
  { id: 'M-005', name: 'Agent Genome Backup', status: 'queued', agent: 'Unassigned', progress: 0, elapsed: '--', target: 'CMC' },
  { id: 'M-006', name: 'Dashboard UI Sprint', status: 'complete', agent: 'Dac', progress: 1.0, elapsed: '3h 45m', target: 'JOC' },
];

export const MOCK_ACTIVITY: ActivityEvent[] = [
  { id: 'E-001', type: 'mission', agent: 'Lex', message: 'PDAS scan complete — 2 contradictions found in SEG', timestamp: '14:23:08' },
  { id: 'E-002', type: 'system', message: 'CAS cognitive drift detected: 0.12 above threshold', timestamp: '14:21:45' },
  { id: 'E-003', type: 'agent', agent: 'Rev', message: 'HHNI index rebuild failed — insufficient memory atoms', timestamp: '14:19:22' },
  { id: 'E-004', type: 'mission', agent: 'Aether', message: 'Context synthesis 72% — merging 34 evidence chains', timestamp: '14:17:56' },
  { id: 'E-005', type: 'user', message: 'Braden approved Oracle escalation policy v2.1', timestamp: '14:15:30' },
  { id: 'E-006', type: 'system', message: 'MCP latency nominal at 8ms — all 92 tools registered', timestamp: '14:12:11' },
  { id: 'E-007', type: 'agent', agent: 'Codex', message: 'MCP gateway TLS handshake hardened — gate 7 passed', timestamp: '14:09:44' },
  { id: 'E-008', type: 'mission', agent: 'Dac', message: 'Dashboard UI Sprint completed — PR submitted', timestamp: '14:05:18' },
];

// System color map for subsystem identification
export const SYSTEM_COLORS: Record<SystemId, string> = {
  CMC: '#00BCD4',
  HHNI: '#4CAF50',
  VIF: '#FFC107',
  SEG: '#9C27B0',
  APOE: '#FF5722',
  TCS: '#2196F3',
  CAS: '#E91E63',
  MCP: '#F5A623',
};
