/**
 * Palisade Left Drawer — Workspace-local panels.
 * Mission Control: Agent Fleet + System Status.
 */
import React from 'react';
import { usePalisadeStore } from './store';
import { AgentFleetPanel } from './panels/AgentFleetPanel';
import { SystemStatusPanel } from './panels/SystemStatusPanel';
import type { TruthState } from './store';

export function PalisadeLeftDrawer() {
    const { workspaceId, mcpLive } = usePalisadeStore();
    const truth: TruthState = mcpLive ? 'LIVE' : 'MOCK'; // Phase 1: MOCK when MCP not wired

    if (workspaceId !== 'dashboard') {
        return (
            <div className="palisade-left" style={{ padding: 12, color: 'var(--palisade-text-tertiary)', fontSize: 11 }}>
                Workspace “{workspaceId}” — panels not implemented in Phase 1.
            </div>
        );
    }

    return (
        <div className="palisade-left">
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 0 }}>
                <div style={{ flex: '1 1 0', minHeight: 200 }}>
                    <AgentFleetPanel truthState={truth} />
                </div>
                <div style={{ flex: '1 1 0', minHeight: 200 }}>
                    <SystemStatusPanel truthState={truth} subsystemsOnline={9} />
                </div>
            </div>
        </div>
    );
}
