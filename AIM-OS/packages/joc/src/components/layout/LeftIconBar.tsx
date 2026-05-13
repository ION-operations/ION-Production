import React from 'react';
import { useJOCStore, type PageType, type DrawerPosition, type LeftDrawerDef } from '../../store/jocStore';
import {
    RadarIcon,
    ConstellationIcon,
    LaunchVectorIcon,
    SignalPulseIcon,
    HexLatticeIcon,
    ChipDieIcon,
    TuningForkIcon,
    CloseIcon,
} from '../icons';

// ─── Icon Mapping ───

const ICON_MAP: Record<string, React.ComponentType<{ size?: number }>> = {
    RadarIcon,
    ConstellationIcon,
    LaunchVectorIcon,
    SignalPulseIcon,
    HexLatticeIcon,
    ChipDieIcon,
    TuningForkIcon,
};

// ─── Per-Page Left Drawer Configurations ───
// Each page declares what left-side drawers it needs.
// The right bar stays universal; this bar is contextual.

const LEFT_DRAWER_CONFIGS: Partial<Record<PageType, Array<LeftDrawerDef & { icon: string }>>> = {
    dashboard: [
        { type: 'sys-status', icon: 'RadarIcon', label: 'System Status' },
        { type: 'activity-feed', icon: 'SignalPulseIcon', label: 'Activity Feed' },
        { type: 'quick-launch', icon: 'LaunchVectorIcon', label: 'Quick Launch' },
    ],
    session: [
        { type: 'driver-status', icon: 'ConstellationIcon', label: 'Driver Status' },
        { type: 'dom-inspector', icon: 'HexLatticeIcon', label: 'DOM Inspector' },
        { type: 'injection-log', icon: 'LaunchVectorIcon', label: 'Injection Log' },
    ],
    projects: [
        { type: 'file-tree', icon: 'HexLatticeIcon', label: 'File Explorer' },
        { type: 'git-graph', icon: 'ConstellationIcon', label: 'Git Graph' },
        { type: 'relationships', icon: 'SignalPulseIcon', label: 'Relationships' },
    ],
    editor: [
        { type: 'file-tree', icon: 'HexLatticeIcon', label: 'File Explorer' },
        { type: 'symbols', icon: 'RadarIcon', label: 'Symbols' },
        { type: 'search', icon: 'LaunchVectorIcon', label: 'Search' },
    ],
    atlas: [
        { type: 'system-list', icon: 'ConstellationIcon', label: 'Systems' },
        { type: 'connections', icon: 'SignalPulseIcon', label: 'Connections' },
    ],
    compute: [
        { type: 'resources', icon: 'ChipDieIcon', label: 'Resources' },
        { type: 'jobs', icon: 'LaunchVectorIcon', label: 'Jobs' },
    ],
    comms: [
        { type: 'threads', icon: 'SignalPulseIcon', label: 'Threads' },
        { type: 'agents', icon: 'ConstellationIcon', label: 'Agents' },
    ],
    dispatch: [
        { type: 'targets', icon: 'ConstellationIcon', label: 'Targets' },
        { type: 'templates', icon: 'HexLatticeIcon', label: 'Templates' },
    ],
    synthesizer: [
        { type: 'responses', icon: 'SignalPulseIcon', label: 'Responses' },
        { type: 'evidence', icon: 'RadarIcon', label: 'Evidence' },
    ],
    context: [
        { type: 'memory-browser', icon: 'RadarIcon', label: 'Memory Browser' },
        { type: 'retrieval-log', icon: 'SignalPulseIcon', label: 'Retrieval Log' },
    ],
    'context-graph': [
        { type: 'timeline-rail', icon: 'ConstellationIcon', label: 'Timeline' },
        { type: 'filters', icon: 'TuningForkIcon', label: 'Filters' },
        { type: 'systems', icon: 'RadarIcon', label: 'Systems' },
    ],
    'mission-builder': [
        { type: 'agent-pool', icon: 'ConstellationIcon', label: 'Agent Pool' },
        { type: 'templates', icon: 'HexLatticeIcon', label: 'Templates' },
    ],
    gpu: [
        { type: 'models', icon: 'ChipDieIcon', label: 'Models' },
        { type: 'queue', icon: 'LaunchVectorIcon', label: 'Queue' },
    ],
    health: [
        { type: 'sessions', icon: 'ConstellationIcon', label: 'Sessions' },
        { type: 'dom-health', icon: 'RadarIcon', label: 'DOM Health' },
    ],
    settings: [
        { type: 'sections', icon: 'TuningForkIcon', label: 'Sections' },
    ],
    calendar: [
        { type: 'events', icon: 'RadarIcon', label: 'Events' },
        { type: 'macros', icon: 'LaunchVectorIcon', label: 'Macros' },
        { type: 'schedule', icon: 'SignalPulseIcon', label: 'Schedule' },
    ],
    'context-lab': [
        { type: 'leaderboard', icon: 'RadarIcon', label: 'Leaderboard' },
        { type: 'lineage', icon: 'ConstellationIcon', label: 'Lineage' },
        { type: 'tournament', icon: 'LaunchVectorIcon', label: 'Tournament' },
    ],
    infra: [
        { type: 'services', icon: 'RadarIcon', label: 'Services' },
        { type: 'agents', icon: 'ConstellationIcon', label: 'Agents' },
        { type: 'logs', icon: 'SignalPulseIcon', label: 'Logs' },
    ],
    'agent-workforce': [
        { type: 'hierarchy', icon: 'ConstellationIcon', label: 'Hierarchy' },
        { type: 'dossier', icon: 'RadarIcon', label: 'Dossier' },
        { type: 'comms', icon: 'SignalPulseIcon', label: 'Comms' },
    ],
    'intelligence-map': [
        { type: 'ast-topology', icon: 'HexLatticeIcon', label: 'AST Topology' },
        { type: 'os-stream', icon: 'SignalPulseIcon', label: 'OS Stream' },
        { type: 'hypernodes', icon: 'ConstellationIcon', label: 'Hypernodes' },
    ],
};

// ─── Component ───

export function LeftIconBar() {
    const { leftOpenDrawers, toggleLeftDrawer, closeAllLeftDrawers, activeTab, tabs } = useJOCStore();

    // Determine current page type
    const activeTabData = tabs.find(t => t.id === activeTab);
    const currentPage: PageType = activeTabData?.type || 'dashboard';

    // Get drawer config for current page
    const buttons = LEFT_DRAWER_CONFIGS[currentPage] || [];

    const isActive = (type: string) => leftOpenDrawers.some(d => d.type === type);

    const handleZoneClick = (type: string, position: DrawerPosition, e: React.MouseEvent) => {
        e.stopPropagation();
        toggleLeftDrawer(type, position);
    };

    const renderIconButton = ({ type, icon, label }: { type: string; icon: string; label: string }) => {
        const Icon = ICON_MAP[icon] || RadarIcon;
        return (
            <div key={type} className={`icon-btn ${isActive(type) ? 'active' : ''}`}>
                <Icon size={20} />

                {/* Split-click zones — the Lucid pattern */}
                <div className="icon-btn-zones">
                    <button
                        className="icon-zone-full"
                        onClick={(e) => handleZoneClick(type, 'full', e)}
                        title={`${label} — Full Height`}
                    />
                    <button
                        className="icon-zone-top"
                        onClick={(e) => handleZoneClick(type, 'top', e)}
                        title={`${label} — Top Half`}
                    />
                    <button
                        className="icon-zone-bottom"
                        onClick={(e) => handleZoneClick(type, 'bottom', e)}
                        title={`${label} — Bottom Half`}
                    />
                </div>

                {/* Tooltip — positioned to the right for left bar */}
                <div className="icon-btn-tooltip left-tooltip">{label}</div>
            </div>
        );
    };

    if (buttons.length === 0) return null;

    return (
        <div className="left-icon-bar">
            {buttons.map(renderIconButton)}

            <div className="icon-bar-spacer" />

            {leftOpenDrawers.length > 0 && (
                <button
                    className="icon-btn"
                    onClick={closeAllLeftDrawers}
                    title="Close All Left Panels"
                >
                    <CloseIcon size={16} />
                </button>
            )}
        </div>
    );
}
