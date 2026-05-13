/**
 * Mission Control — Force at a glance. Single page to perfection.
 * Agents count, active count, subsystems summary. Recessed, dense, truthful.
 */
import React from 'react';
import { usePalisadeStore } from '../store';

const MOCK_AGENT_COUNT = 6;
const MOCK_ACTIVE = 2;
const MOCK_SUBSYSTEMS = 9;
const MOCK_SUBSYSTEMS_TOTAL = 9;

export function MissionControlPage() {
    const { workspaceId, mcpLive } = usePalisadeStore();

    if (workspaceId !== 'dashboard') {
        return (
            <div className="palisade-mc-glance">
                <p style={{ color: 'var(--palisade-text-tertiary)' }}>
                    Workspace “{workspaceId}” — main content not implemented in Phase 1. Switch to Mission Control.
                </p>
            </div>
        );
    }

    return (
        <div className="palisade-mc-glance">
            <div className="palisade-mc-glance__title">Force at a glance</div>
            <div className="palisade-mc-glance__row">
                <div>
                    <div className="palisade-mc-stat">{MOCK_AGENT_COUNT}</div>
                    <div className="palisade-mc-stat__label">Agents</div>
                </div>
                <div>
                    <div className="palisade-mc-stat">{MOCK_ACTIVE}</div>
                    <div className="palisade-mc-stat__label">Active</div>
                </div>
                <div>
                    <div className="palisade-mc-stat">
                        {MOCK_SUBSYSTEMS}/{MOCK_SUBSYSTEMS_TOTAL}
                    </div>
                    <div className="palisade-mc-stat__label">Subsystems</div>
                </div>
                <div>
                    <div className="palisade-mc-stat" style={{ fontSize: 14, color: mcpLive ? 'var(--palisade-live)' : 'var(--palisade-offline)' }}>
                        {mcpLive ? 'LIVE' : 'MOCK'}
                    </div>
                    <div className="palisade-mc-stat__label">Data</div>
                </div>
            </div>
        </div>
    );
}
