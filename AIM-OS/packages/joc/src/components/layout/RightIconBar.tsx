import React from 'react';
import { useJOCStore, type DrawerType, type DrawerPosition } from '../../store/jocStore';
import { toggleAssistantRail } from './AssistantRail';
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

// ─── Drawer Button Definitions ───

const DRAWER_BUTTONS: Array<{ type: DrawerType; icon: React.ComponentType<{ size?: number }>; label: string }> = [
    { type: 'dashboard', icon: RadarIcon, label: 'Dashboard' },
    { type: 'fleet', icon: ConstellationIcon, label: 'AI Fleet' },
    { type: 'missions', icon: LaunchVectorIcon, label: 'Missions' },
    { type: 'comms', icon: SignalPulseIcon, label: 'Comms' },
    { type: 'projects', icon: HexLatticeIcon, label: 'Projects' },
    { type: 'compute', icon: ChipDieIcon, label: 'Compute' },
];

const BOTTOM_BUTTONS: Array<{ type: DrawerType; icon: React.ComponentType<{ size?: number }>; label: string }> = [
    { type: 'settings', icon: TuningForkIcon, label: 'Settings' },
];

// ─── Component ───

export function RightIconBar() {
    const { openDrawers, toggleDrawer, closeAllDrawers } = useJOCStore();

    const isActive = (type: DrawerType) => openDrawers.some(d => d.type === type);

    const handleZoneClick = (type: DrawerType, position: DrawerPosition, e: React.MouseEvent) => {
        e.stopPropagation();
        toggleDrawer(type, position);
    };

    const renderIconButton = ({ type, icon: Icon, label }: typeof DRAWER_BUTTONS[0]) => (
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

            {/* Tooltip */}
            <div className="icon-btn-tooltip">{label}</div>
        </div>
    );

    return (
        <div className="icon-bar">
            {/* Assistant Rail Toggle */}
            <button
                className="icon-btn"
                onClick={toggleAssistantRail}
                title="J.A.R.V.I.S. Assistant (Ctrl+\\)"
                style={{ marginBottom: 8 }}
            >
                <span style={{ fontSize: 18 }}>💬</span>
            </button>

            {DRAWER_BUTTONS.map(renderIconButton)}

            <div className="icon-bar-spacer" />

            {BOTTOM_BUTTONS.map(renderIconButton)}

            {openDrawers.length > 0 && (
                <button
                    className="icon-btn"
                    onClick={closeAllDrawers}
                    title="Close All Panels"
                >
                    <CloseIcon size={16} />
                </button>
            )}
        </div>
    );
}
