/**
 * Palisade Bottom Bar — Activity Feed for Mission Control.
 */
import React from 'react';
import { usePalisadeStore } from './store';
import { ActivityFeedPanel } from './panels/ActivityFeedPanel';
import type { TruthState } from './store';

export function PalisadeBottomBar() {
    const { workspaceId, mcpLive } = usePalisadeStore();
    const truth: TruthState = mcpLive ? 'LIVE' : 'MOCK';

    if (workspaceId !== 'dashboard') {
        return (
            <div className="palisade-bottom" style={{ padding: 12, color: 'var(--palisade-text-tertiary)', fontSize: 10 }}>
                Bottom panel for “{workspaceId}” — Phase 1 shows Activity Feed only for Mission Control.
            </div>
        );
    }

    return (
        <div className="palisade-bottom">
            <ActivityFeedPanel truthState={truth} />
        </div>
    );
}
