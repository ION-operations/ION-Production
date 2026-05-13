// panelRegistry.ts
// ═══════════════════════════════════════════════════════════════════
// Panel Registry — The single source of truth for all dockable panels.
// Every panel in JOC must be registered here. No ad-hoc panel creation.
// ═══════════════════════════════════════════════════════════════════

import React from 'react';

import {
    RadarIcon,
    ConstellationIcon,
    LaunchVectorIcon,
    SignalPulseIcon,
    HexLatticeIcon,
    ChipDieIcon,
    TuningForkIcon,
    BoltIcon,
    RobotHeadIcon,
    ClipboardListIcon,
    ShieldKeyIcon,
    SatelliteIcon,
    CalendarMarkIcon,
} from '../components/icons';

// ─── AIMOS System References ─────────────────────────────────────

export type AIMOSSystem =
    | 'CMC'    // Crystallized Memory Core
    | 'HHNI'   // Hierarchical Holographic Neural Index
    | 'VIF'    // Verifiable Intelligence Framework
    | 'SEG'    // Shared Evidence Graph
    | 'APOE'   // AI-Powered Orchestration Engine
    | 'TCS'    // Timeline Context System
    | 'CAS'    // Cognitive Analysis System
    | 'SDF-CVF' // Semantic Development Flow - Context Vector Fields
    | 'MCP'    // Model Context Protocol
    | 'Oracle' // Oracle System
    | 'Genome'; // Agent Genome System

// ─── Data Epistemic Status ───────────────────────────────────────
// Law 6: Data Truth Law — every surface must declare its status.

export type DataStatus =
    | 'live'        // Real data from AIMOS via MCP
    | 'cached'      // Was live, now stale (>30s old)
    | 'mock'        // Development/fallback data
    | 'offline'     // Cannot reach data source
    | 'speculative'; // AI prediction, not confirmed

// ─── Panel Dock Targets ──────────────────────────────────────────

export type DockTarget = 'left' | 'right' | 'bottom' | 'center';

// ─── Panel Domain ────────────────────────────────────────────────

export type PanelDomain =
    | 'operations'
    | 'intelligence'
    | 'infrastructure'
    | 'tools'
    | 'system';

// ─── Panel Registry Entry ────────────────────────────────────────
// Law 3 of the UI Canon.

export interface PanelRegistryEntry {
    /** Unique identifier, kebab-case */
    id: string;
    /** Display name */
    title: string;
    /** Custom icon component (no generic icons) */
    icon: React.FC<{ size?: number }>;
    /** Which domain this panel belongs to */
    domain: PanelDomain;
    /** Where this panel can dock */
    dockTargets: DockTarget[];
    /** Default dock position */
    defaultDock: DockTarget;
    /** Default size in pixels */
    defaultSize: { width: number; height: number };
    /** Minimum size in pixels */
    minSize: { width: number; height: number };
    /** Whether this panel survives workspace switches */
    persistent: boolean;
    /** Which AIMOS systems this panel reads from */
    dataSources: AIMOSSystem[];
    /** Current epistemic status of data */
    dataStatus: DataStatus;
    /** Keyboard shortcut to toggle */
    keyboard?: string;
    /** Which workspaces show this panel by default */
    workspaces?: string[];
    /** Description for command palette */
    description?: string;
}

// ─── Workspace Definition ────────────────────────────────────────

export type NavGroup = 'operations' | 'intelligence' | 'infrastructure' | 'tools';

export interface WorkspaceDefinition {
    /** Unique identifier */
    id: string;
    /** Display name */
    title: string;
    /** Navigation group in TopBar */
    navGroup: NavGroup;
    /** Custom icon component */
    icon: React.FC<{ size?: number }>;
    /** Left panels shown by default */
    defaultLeftPanels: string[];
    /** Bottom panels added for this workspace */
    bottomPanels?: string[];
    /** Description for command palette */
    description?: string;
}

// ─── Assistant Rail Mode ─────────────────────────────────────────
// Law 4 of the UI Canon.

export type AssistantRailMode = 'chat' | 'context' | 'actions' | 'memory';

export interface AssistantRailConfig {
    /** Currently active mode */
    activeMode: AssistantRailMode;
    /** Whether the rail is expanded or collapsed to icon-only */
    expanded: boolean;
    /** Width in pixels (clamped to 280-420) */
    width: number;
}

// ─── Data Status Badge Helper ────────────────────────────────────
// Law 6: Components can use this to render the correct indicator.

export const DATA_STATUS_CONFIG: Record<DataStatus, {
    label: string;
    cssClass: string;
    icon: string;
}> = {
    live: {
        label: 'Live',
        cssClass: 'data-status--live',
        icon: '',  // No indicator for live (default)
    },
    cached: {
        label: 'Cached',
        cssClass: 'data-status--cached',
        icon: '🕐',
    },
    mock: {
        label: 'Mock Data',
        cssClass: 'data-status--mock',
        icon: '⚠',
    },
    offline: {
        label: 'Offline',
        cssClass: 'data-status--offline',
        icon: '⊘',
    },
    speculative: {
        label: 'AI Prediction',
        cssClass: 'data-status--speculative',
        icon: '✧',
    },
};

// ═══════════════════════════════════════════════════════════════════
// PANEL REGISTRY — 12 Canonical Panels
// Every dockable unit in J.A.R.V.I.S. is registered here.
// ═══════════════════════════════════════════════════════════════════



export const PANEL_REGISTRY: PanelRegistryEntry[] = [
    {
        id: 'system-status',
        title: 'System Status',
        icon: RadarIcon,
        domain: 'system',
        dockTargets: ['left', 'bottom'],
        defaultDock: 'left',
        defaultSize: { width: 320, height: 400 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['CAS', 'VIF'],
        dataStatus: 'offline',
        keyboard: 'Ctrl+Shift+S',
        workspaces: ['dashboard', 'infra-console'],
        description: 'AIM-OS subsystem health and consciousness metrics',
    },
    {
        id: 'agent-fleet',
        title: 'Agent Fleet',
        icon: ConstellationIcon,
        domain: 'intelligence',
        dockTargets: ['left'],
        defaultDock: 'left',
        defaultSize: { width: 320, height: 500 },
        minSize: { width: 240, height: 300 },
        persistent: false,
        dataSources: ['Genome', 'CMC'],
        dataStatus: 'offline',
        keyboard: 'Ctrl+Shift+F',
        workspaces: ['dashboard', 'agent-workforce'],
        description: 'Active agent roster with status indicators',
    },
    {
        id: 'mission-queue',
        title: 'Mission Queue',
        icon: LaunchVectorIcon,
        domain: 'operations',
        dockTargets: ['left', 'bottom'],
        defaultDock: 'left',
        defaultSize: { width: 320, height: 400 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['APOE', 'CMC'],
        dataStatus: 'offline',
        keyboard: 'Ctrl+Shift+M',
        workspaces: ['dispatch', 'mission-builder'],
        description: 'Pending and active dispatch missions',
    },
    {
        id: 'messages',
        title: 'Messages',
        icon: SignalPulseIcon,
        domain: 'intelligence',
        dockTargets: ['left', 'bottom'],
        defaultDock: 'left',
        defaultSize: { width: 320, height: 400 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['CMC', 'MCP'],
        dataStatus: 'offline',
        keyboard: 'Ctrl+Shift+C',
        workspaces: ['agent-workforce', 'dispatch'],
        description: 'Inter-agent communication feed',
    },
    {
        id: 'activity-feed',
        title: 'Activity Feed',
        icon: ClipboardListIcon,
        domain: 'system',
        dockTargets: ['left', 'bottom'],
        defaultDock: 'bottom',
        defaultSize: { width: 320, height: 300 },
        minSize: { width: 240, height: 150 },
        persistent: true,
        dataSources: ['CMC', 'TCS'],
        dataStatus: 'offline',
        workspaces: ['dashboard'],
        description: 'System-wide activity and event log',
    },
    {
        id: 'memory-browser',
        title: 'Memory Browser',
        icon: HexLatticeIcon,
        domain: 'intelligence',
        dockTargets: ['left', 'right'],
        defaultDock: 'left',
        defaultSize: { width: 340, height: 500 },
        minSize: { width: 280, height: 300 },
        persistent: false,
        dataSources: ['CMC', 'HHNI', 'VIF'],
        dataStatus: 'offline',
        keyboard: 'Ctrl+Shift+B',
        workspaces: ['context-lab', 'oracle'],
        description: 'CMC memory atom browser with semantic search',
    },
    {
        id: 'session-health',
        title: 'Session Health',
        icon: SatelliteIcon,
        domain: 'intelligence',
        dockTargets: ['left'],
        defaultDock: 'left',
        defaultSize: { width: 300, height: 350 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['CAS', 'VIF'],
        dataStatus: 'offline',
        workspaces: ['session'],
        description: 'Session cognitive health and drift monitoring',
    },
    {
        id: 'approvals-queue',
        title: 'Approvals',
        icon: BoltIcon,
        domain: 'operations',
        dockTargets: ['right', 'bottom'],
        defaultDock: 'right',
        defaultSize: { width: 320, height: 400 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['Oracle', 'APOE'],
        dataStatus: 'offline',
        keyboard: 'Ctrl+Shift+A',
        workspaces: ['oracle', 'dispatch'],
        description: 'Pending Oracle approval actions',
    },
    {
        id: 'diagnostics',
        title: 'Diagnostics',
        icon: ChipDieIcon,
        domain: 'infrastructure',
        dockTargets: ['bottom'],
        defaultDock: 'bottom',
        defaultSize: { width: 600, height: 300 },
        minSize: { width: 400, height: 200 },
        persistent: false,
        dataSources: ['VIF', 'SEG', 'MCP'],
        dataStatus: 'offline',
        workspaces: ['infra-console'],
        description: 'MCP diagnostics and system telemetry',
    },
    {
        id: 'credentials',
        title: 'Credential Vault',
        icon: ShieldKeyIcon,
        domain: 'infrastructure',
        dockTargets: ['left'],
        defaultDock: 'left',
        defaultSize: { width: 320, height: 400 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['CMC'],
        dataStatus: 'offline',
        workspaces: ['infra-console'],
        description: 'Encrypted credential and API key management',
    },
    {
        id: 'agent-dossier',
        title: 'Agent Dossier',
        icon: RobotHeadIcon,
        domain: 'intelligence',
        dockTargets: ['left', 'right'],
        defaultDock: 'left',
        defaultSize: { width: 340, height: 500 },
        minSize: { width: 260, height: 300 },
        persistent: false,
        dataSources: ['Genome', 'CMC', 'VIF'],
        dataStatus: 'offline',
        workspaces: ['agent-workforce', 'agent-builder'],
        description: 'Deep agent inspection — genome, metrics, history',
    },
    {
        id: 'calendar-view',
        title: 'Calendar',
        icon: CalendarMarkIcon,
        domain: 'operations',
        dockTargets: ['left'],
        defaultDock: 'left',
        defaultSize: { width: 300, height: 350 },
        minSize: { width: 240, height: 200 },
        persistent: false,
        dataSources: ['CMC', 'APOE'],
        dataStatus: 'offline',
        workspaces: ['calendar'],
        description: 'Upcoming events and scheduled tasks',
    },
];

// ═══════════════════════════════════════════════════════════════════
// WORKSPACE REGISTRY — 12 Canonical Workspaces
// Every route-level environment in J.A.R.V.I.S. is defined here.
// ═══════════════════════════════════════════════════════════════════

export const WORKSPACE_REGISTRY: WorkspaceDefinition[] = [
    {
        id: 'dashboard',
        title: 'Mission Control',
        navGroup: 'operations',
        icon: RadarIcon,
        defaultLeftPanels: ['agent-fleet', 'system-status'],
        bottomPanels: ['activity-feed'],
        description: 'Central command overview — fleet, subsystems, missions',
    },
    {
        id: 'dispatch',
        title: 'Dispatch',
        navGroup: 'operations',
        icon: LaunchVectorIcon,
        defaultLeftPanels: ['mission-queue', 'messages'],
        bottomPanels: [],
        description: 'Multi-target AI prompt dispatch and response tracking',
    },
    {
        id: 'mission-builder',
        title: 'Mission Builder',
        navGroup: 'operations',
        icon: LaunchVectorIcon,
        defaultLeftPanels: ['mission-queue'],
        description: 'Compose multi-step agent missions with topology selection',
    },
    {
        id: 'calendar',
        title: 'Calendar',
        navGroup: 'operations',
        icon: CalendarMarkIcon,
        defaultLeftPanels: ['calendar-view'],
        description: 'Scheduled missions, events, and task timeline',
    },
    {
        id: 'context-lab',
        title: 'Context Lab',
        navGroup: 'intelligence',
        icon: HexLatticeIcon,
        defaultLeftPanels: ['memory-browser'],
        description: 'Context strategy evolution — lineage, tournaments, mutations',
    },
    {
        id: 'agent-workforce',
        title: 'Agent Workforce',
        navGroup: 'intelligence',
        icon: ConstellationIcon,
        defaultLeftPanels: ['agent-dossier', 'messages'],
        description: 'Agent fleet monitoring — genome, fission, handoffs',
    },
    {
        id: 'oracle',
        title: 'Oracle',
        navGroup: 'intelligence',
        icon: BoltIcon,
        defaultLeftPanels: ['approvals-queue', 'memory-browser'],
        description: 'Aether Oracle — autonomous control, permissions, approvals',
    },
    {
        id: 'context-graph',
        title: 'Context Graph',
        navGroup: 'intelligence',
        icon: HexLatticeIcon,
        defaultLeftPanels: [],
        description: 'Force-directed context dependency visualization',
    },
    {
        id: 'session',
        title: 'Session',
        navGroup: 'intelligence',
        icon: SatelliteIcon,
        defaultLeftPanels: ['session-health'],
        description: 'Active AI session management and health tracking',
    },
    {
        id: 'infra-console',
        title: 'Infra Console',
        navGroup: 'infrastructure',
        icon: ChipDieIcon,
        defaultLeftPanels: ['system-status', 'credentials'],
        bottomPanels: ['diagnostics'],
        description: 'Infrastructure control plane — services, metrics, compute',
    },
    {
        id: 'system-atlas',
        title: 'System Atlas',
        navGroup: 'infrastructure',
        icon: RadarIcon,
        defaultLeftPanels: [],
        description: 'Spatial architecture map — Z0-Z5 semantic zoom',
    },
    {
        id: 'code-editor',
        title: 'Code Editor',
        navGroup: 'tools',
        icon: ChipDieIcon,
        defaultLeftPanels: [],
        bottomPanels: ['diagnostics'],
        description: 'AI-enhanced Monaco editor with semantic sync states',
    },
];

// ═══════════════════════════════════════════════════════════════════
// Registry Helpers
// ═══════════════════════════════════════════════════════════════════

/** Look up a panel by its ID */
export function getPanel(id: string): PanelRegistryEntry | undefined {
    return PANEL_REGISTRY.find(p => p.id === id);
}

/** Look up a workspace by its ID */
export function getWorkspace(id: string): WorkspaceDefinition | undefined {
    return WORKSPACE_REGISTRY.find(w => w.id === id);
}

/** Get all panels assigned to a workspace */
export function getPanelsForWorkspace(workspaceId: string): PanelRegistryEntry[] {
    return PANEL_REGISTRY.filter(p => p.workspaces?.includes(workspaceId));
}

/** Get all workspaces in a nav group */
export function getWorkspacesByGroup(group: NavGroup): WorkspaceDefinition[] {
    return WORKSPACE_REGISTRY.filter(w => w.navGroup === group);
}
