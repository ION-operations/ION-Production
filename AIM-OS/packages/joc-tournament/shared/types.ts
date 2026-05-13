/**
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║                                                                       ║
 * ║        ____. _____  __________  ____   ____.___.  _________           ║
 * ║       |    |/  _  \ \______   \ \   \ /   /|   |/   _____/           ║
 * ║       |    /  /_\  \ |       _/  \   Y   / |   |\_____  \            ║
 * ║   |   |   /    |    \|    |   \   \     /  |   |/        \           ║
 * ║   |___|___\____|__  /|____|   /    \___/   |___/_______  /           ║
 * ║                   \/        \/                         \/            ║
 * ║                                                                       ║
 * ║   Joint AI Research & Visualization Intelligence System               ║
 * ║   AIM-OS Command Surface — Shared Foundation                          ║
 * ║                                                                       ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 *
 * This file provides the common type definitions and utilities shared
 * across all tournament competitor builds.
 *
 * TOURNAMENT RULE: All competitors must use these shared types.
 * You may extend them, but not contradict them.
 */

// ─── Re-export from canonical source ──────────────────────────
// Competitors: import from this file, not from the JOC source directly.
// This ensures version consistency across builds.

export type {
    AIMOSSystem,
    DataStatus,
    DockTarget,
    PanelDomain,
    NavGroup,
    PanelRegistryEntry,
    WorkspaceDefinition,
} from '../../joc/src/store/panelRegistry';

export {
    DATA_STATUS_CONFIG,
    PANEL_REGISTRY,
    WORKSPACE_REGISTRY,
    getPanel,
    getWorkspace,
    getPanelsForWorkspace,
    getWorkspacesByGroup,
} from '../../joc/src/store/panelRegistry';

// ─── Tournament-Specific Types ────────────────────────────────

/** Truth state that each panel surface must declare (Codex RULES.md Law 2) */
export type TruthState = 'LIVE' | 'CACHED' | 'MOCK' | 'OFFLINE' | 'SPECULATIVE';

/** Codex's recommended primary workspace set (7 core + 5 secondary) */
export const PRIMARY_WORKSPACES = [
    'dashboard',        // Mission Control
    'dispatch',         // Multi-target dispatch
    'agent-workforce',  // Agent fleet monitoring
    'context-lab',      // Context strategy evolution
    'infra-console',    // Infrastructure control plane
    'oracle',           // Aether Oracle — approvals
    'code-editor',      // Builder workbench / code editor
] as const;

export const SECONDARY_WORKSPACES = [
    'calendar',
    'context-graph',
    'system-atlas',
    'session',
    'mission-builder',
] as const;

/** Operator action categories from Codex RULES.md Law 4 */
export type OperatorAction =
    | 'dispatch'    // Send commands to agents
    | 'inspect'     // View state and data
    | 'recover'     // Handle failures
    | 'correlate'   // Connect related information
    | 'adjudicate'; // Approve or deny actions
