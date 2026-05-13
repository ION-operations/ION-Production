import React from 'react';

interface IconProps {
    size?: number;
    className?: string;
    style?: React.CSSProperties;
}

/**
 * RadarIcon — Dashboard drawer
 * Concentric arcs with a sweep line, like a real ops center radar.
 */
export function RadarIcon({ size = 20, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Center dot */}
            <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
            {/* Inner arc */}
            <path d="M12 8a4 4 0 0 1 4 4" />
            {/* Middle arc */}
            <path d="M12 5a7 7 0 0 1 7 7" />
            {/* Outer arc */}
            <path d="M12 2a10 10 0 0 1 10 10" />
            {/* Sweep line */}
            <line x1="12" y1="12" x2="19" y2="5" strokeWidth="1" opacity="0.6" />
            {/* Base line */}
            <line x1="2" y1="20" x2="22" y2="20" strokeWidth="1" opacity="0.3" />
            {/* Detection blip */}
            <circle cx="16.5" cy="7.5" r="1" fill="currentColor" stroke="none" opacity="0.8" />
        </svg>
    );
}

/**
 * ConstellationIcon — AI Fleet drawer
 * 4 nodes connected by signal lines, each node a different AI.
 */
export function ConstellationIcon({ size = 20, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Connection lines */}
            <line x1="7" y1="6" x2="17" y2="6" opacity="0.4" />
            <line x1="7" y1="6" x2="5" y2="16" opacity="0.4" />
            <line x1="17" y1="6" x2="19" y2="16" opacity="0.4" />
            <line x1="5" y1="16" x2="19" y2="16" opacity="0.4" />
            <line x1="7" y1="6" x2="19" y2="16" opacity="0.2" />
            <line x1="17" y1="6" x2="5" y2="16" opacity="0.2" />
            {/* Node 1 - top left */}
            <circle cx="7" cy="6" r="2.5" fill="currentColor" stroke="none" opacity="0.9" />
            {/* Node 2 - top right */}
            <circle cx="17" cy="6" r="2" fill="currentColor" stroke="none" opacity="0.7" />
            {/* Node 3 - bottom left */}
            <circle cx="5" cy="16" r="2" fill="currentColor" stroke="none" opacity="0.7" />
            {/* Node 4 - bottom right */}
            <circle cx="19" cy="16" r="2.5" fill="currentColor" stroke="none" opacity="0.9" />
            {/* Signal pulses */}
            <circle cx="12" cy="11" r="1" fill="currentColor" stroke="none" opacity="0.4" />
        </svg>
    );
}

/**
 * LaunchVectorIcon — Missions drawer
 * An arrow trajectory with waypoints, like a flight plan.
 */
export function LaunchVectorIcon({ size = 20, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Trajectory path */}
            <path d="M4 20 Q 8 12, 12 14 Q 16 16, 20 4" strokeWidth="1.5" />
            {/* Arrowhead at end */}
            <polyline points="17,4 20,4 20,7" strokeWidth="1.5" />
            {/* Waypoint 1 */}
            <circle cx="6" cy="17" r="1.5" fill="currentColor" stroke="none" />
            {/* Waypoint 2 */}
            <circle cx="12" cy="14" r="1.5" fill="currentColor" stroke="none" />
            {/* Waypoint 3 - destination */}
            <circle cx="20" cy="4" r="1.5" fill="currentColor" stroke="none" />
            {/* Launch marker */}
            <line x1="4" y1="20" x2="4" y2="22" strokeWidth="2" opacity="0.5" />
        </svg>
    );
}

/**
 * SignalPulseIcon — Comms drawer
 * Two waveforms crossing/interleaving — agent communication.
 */
export function SignalPulseIcon({ size = 20, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Wave 1 - outgoing */}
            <path d="M2 12 L5 12 L7 6 L9 18 L11 8 L13 16 L15 12 L17 12" />
            {/* Wave 2 - incoming (offset) */}
            <path d="M7 12 L9 12 L11 7 L13 17 L15 9 L17 15 L19 12 L22 12" opacity="0.4" />
            {/* Left dot (sender) */}
            <circle cx="2" cy="12" r="1.5" fill="currentColor" stroke="none" />
            {/* Right dot (receiver) */}
            <circle cx="22" cy="12" r="1.5" fill="currentColor" stroke="none" />
        </svg>
    );
}

/**
 * HexLatticeIcon — Projects drawer
 * Interconnected hexagonal cells representing the project ecosystem.
 */
export function HexLatticeIcon({ size = 20, className, style }: IconProps) {
    const hexPath = (cx: number, cy: number, r: number) => {
        const pts = [];
        for (let i = 0; i < 6; i++) {
            const angle = (Math.PI / 3) * i - Math.PI / 6;
            pts.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
        }
        return `M${pts.join('L')}Z`;
    };

    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Center hex */}
            <path d={hexPath(12, 12, 4)} strokeWidth="1.5" />
            {/* Top hex */}
            <path d={hexPath(12, 4.5, 3)} opacity="0.6" />
            {/* Bottom hex */}
            <path d={hexPath(12, 19.5, 3)} opacity="0.6" />
            {/* Left hex */}
            <path d={hexPath(5.5, 8, 3)} opacity="0.5" />
            {/* Right hex */}
            <path d={hexPath(18.5, 8, 3)} opacity="0.5" />
            {/* Center dot */}
            <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
        </svg>
    );
}

/**
 * ChipDieIcon — Compute drawer
 * A processor die with circuit traces radiating outward.
 */
export function ChipDieIcon({ size = 20, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Die core */}
            <rect x="7" y="7" width="10" height="10" rx="1" />
            {/* Inner detail */}
            <rect x="9" y="9" width="6" height="6" rx="0.5" opacity="0.5" />
            {/* Top pins */}
            <line x1="9" y1="7" x2="9" y2="3" />
            <line x1="12" y1="7" x2="12" y2="3" />
            <line x1="15" y1="7" x2="15" y2="3" />
            {/* Bottom pins */}
            <line x1="9" y1="17" x2="9" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
            <line x1="15" y1="17" x2="15" y2="21" />
            {/* Left pins */}
            <line x1="7" y1="9" x2="3" y2="9" />
            <line x1="7" y1="12" x2="3" y2="12" />
            <line x1="7" y1="15" x2="3" y2="15" />
            {/* Right pins */}
            <line x1="17" y1="9" x2="21" y2="9" />
            <line x1="17" y1="12" x2="21" y2="12" />
            <line x1="17" y1="15" x2="21" y2="15" />
            {/* Core glow dot */}
            <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
        </svg>
    );
}

/**
 * TuningForkIcon — Settings drawer
 * A precision calibration instrument, not a generic cog.
 */
export function TuningForkIcon({ size = 20, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Left prong */}
            <path d="M9 3 L9 12 Q9 15 12 15" />
            {/* Right prong */}
            <path d="M15 3 L15 12 Q15 15 12 15" />
            {/* Handle */}
            <line x1="12" y1="15" x2="12" y2="21" strokeWidth="2" />
            {/* Prong tips */}
            <circle cx="9" cy="3" r="1" fill="currentColor" stroke="none" />
            <circle cx="15" cy="3" r="1" fill="currentColor" stroke="none" />
            {/* Sound waves */}
            <path d="M6 7 Q5 9 6 11" opacity="0.3" strokeWidth="1" />
            <path d="M18 7 Q19 9 18 11" opacity="0.3" strokeWidth="1" />
            {/* Handle end */}
            <circle cx="12" cy="21" r="1.5" fill="none" />
        </svg>
    );
}

/**
 * Utility Icons
 */

export function ChevronUpIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <polyline points="18 15 12 9 6 15" />
        </svg>
    );
}

export function ChevronDownIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <polyline points="6 9 12 15 18 9" />
        </svg>
    );
}

export function ChevronLeftIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <polyline points="15 18 9 12 15 6" />
        </svg>
    );
}

export function ChevronRightIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <polyline points="9 6 15 12 9 18" />
        </svg>
    );
}

export function CloseIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
    );
}

export function PlusIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
    );
}

export function DispatchIcon({ size = 14, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <polygon points="5 3 19 12 5 21 5 3" fill="currentColor" opacity="0.8" />
        </svg>
    );
}

/**
 * JOC Logo — the mark of the Joint Operations Center
 * A stylized ops hexagon with a central command point.
 */
export function JOCLogo({ size = 18, className, style }: IconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            style={style}
        >
            {/* Outer hexagon */}
            <polygon points="12,2 21,7 21,17 12,22 3,17 3,7" />
            {/* Inner triangle */}
            <polygon points="12,7 17,15 7,15" opacity="0.5" />
            {/* Command point */}
            <circle cx="12" cy="12" r="2" fill="currentColor" stroke="none" />
            {/* Signal lines */}
            <line x1="12" y1="2" x2="12" y2="7" opacity="0.4" strokeWidth="1" />
            <line x1="21" y1="17" x2="17" y2="15" opacity="0.4" strokeWidth="1" />
            <line x1="3" y1="17" x2="7" y2="15" opacity="0.4" strokeWidth="1" />
        </svg>
    );
}

// ─── Dashboard-Specific Icons ────────────────────────────────────

/**
 * StatusDotIcon — LED indicator with optional glow
 * A small filled circle, like a hardware status LED.
 */
export function StatusDotIcon({ size = 10, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 12 12" className={className} style={style}>
            <circle cx="6" cy="6" r="5" fill="currentColor" />
            <circle cx="6" cy="6" r="3" fill="currentColor" opacity="0.6" />
            <circle cx="4.5" cy="4.5" r="1.2" fill="rgba(255,255,255,0.3)" />
        </svg>
    );
}

/**
 * SatelliteIcon — MCP connection status
 * A satellite dish with signal arcs.
 */
export function SatelliteIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            {/* Dish body */}
            <path d="M4 20 L10 14" />
            <path d="M7 17 L3 21" strokeWidth="2" />
            <circle cx="3" cy="21" r="1" fill="currentColor" stroke="none" />
            {/* Reflector */}
            <path d="M10 14 Q14 10 18 6" />
            <path d="M8 12 Q12 8 16 4" opacity="0.5" />
            {/* Signal arcs */}
            <path d="M15 9 Q18 6 21 3" opacity="0.6" />
            <path d="M17 11 Q20 8 22 6" opacity="0.3" />
            {/* Focus point */}
            <circle cx="10" cy="14" r="1.5" fill="currentColor" stroke="none" />
        </svg>
    );
}

/**
 * AutomationIcon — BAS (Browser Automation System)
 * A gear with a play arrow inside — automated execution.
 */
export function AutomationIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            {/* Outer ring with notches */}
            <circle cx="12" cy="12" r="9" />
            {/* Notches */}
            <line x1="12" y1="2" x2="12" y2="4" />
            <line x1="12" y1="20" x2="12" y2="22" />
            <line x1="2" y1="12" x2="4" y2="12" />
            <line x1="20" y1="12" x2="22" y2="12" />
            {/* Play arrow inside */}
            <polygon points="10,8 10,16 16,12" fill="currentColor" stroke="none" opacity="0.8" />
        </svg>
    );
}

/**
 * BoltIcon — Oracle / lightning action
 * A precise lightning bolt, not a cartoon one.
 */
export function BoltIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <path d="M13 2 L5 14 L12 14 L11 22 L19 10 L12 10 Z" fill="currentColor" opacity="0.15" />
            <path d="M13 2 L5 14 L12 14 L11 22 L19 10 L12 10 Z" />
        </svg>
    );
}

/**
 * RobotHeadIcon — AI Messages
 * Stylized robot/AI head silhouette.
 */
export function RobotHeadIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            {/* Head */}
            <rect x="5" y="6" width="14" height="12" rx="3" />
            {/* Eyes */}
            <circle cx="9" cy="12" r="1.5" fill="currentColor" stroke="none" />
            <circle cx="15" cy="12" r="1.5" fill="currentColor" stroke="none" />
            {/* Antenna */}
            <line x1="12" y1="6" x2="12" y2="3" />
            <circle cx="12" cy="2.5" r="1" fill="currentColor" stroke="none" opacity="0.7" />
            {/* Jaw line */}
            <line x1="8" y1="15" x2="16" y2="15" opacity="0.4" />
            {/* Ears */}
            <line x1="5" y1="10" x2="3" y2="10" />
            <line x1="19" y1="10" x2="21" y2="10" />
        </svg>
    );
}

/**
 * ClipboardListIcon — Activity log entries
 * A clipboard with list lines.
 */
export function ClipboardListIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            {/* Board */}
            <rect x="5" y="4" width="14" height="17" rx="2" />
            {/* Clip */}
            <path d="M9 2 L9 5 L15 5 L15 2" />
            <rect x="9" y="2" width="6" height="3" rx="1" />
            {/* Lines */}
            <line x1="9" y1="10" x2="15" y2="10" opacity="0.6" />
            <line x1="9" y1="13" x2="15" y2="13" opacity="0.6" />
            <line x1="9" y1="16" x2="13" y2="16" opacity="0.4" />
        </svg>
    );
}

/**
 * BellAlertIcon — Notifications
 * A bell with a small alert indicator.
 */
export function BellAlertIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            {/* Bell body */}
            <path d="M10 5 Q10 3 12 3 Q14 3 14 5" fill="currentColor" opacity="0.1" />
            <path d="M6 10 Q6 6 12 5 Q18 6 18 10 L19 16 L5 16 Z" />
            {/* Clapper */}
            <path d="M10 16 Q10 19 12 19 Q14 19 14 16" />
            {/* Top knob */}
            <circle cx="12" cy="3" r="1" fill="currentColor" stroke="none" />
        </svg>
    );
}

/**
 * RefreshCycleIcon — Refresh / Running macro
 * Two curved arrows forming a cycle.
 */
export function RefreshCycleIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <path d="M4 12 A8 8 0 0 1 20 12" />
            <polyline points="18,8 20,12 16,12" />
            <path d="M20 12 A8 8 0 0 1 4 12" />
            <polyline points="6,16 4,12 8,12" />
        </svg>
    );
}

/**
 * ShieldKeyIcon — Vault / credentials
 * A shield with a keyhole.
 */
export function ShieldKeyIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <path d="M12 2 L4 6 L4 12 Q4 18 12 22 Q20 18 20 12 L20 6 Z" />
            {/* Keyhole */}
            <circle cx="12" cy="10" r="2" fill="currentColor" stroke="none" opacity="0.5" />
            <rect x="11" y="11" width="2" height="4" rx="0.5" fill="currentColor" stroke="none" opacity="0.5" />
        </svg>
    );
}

/**
 * CalendarMarkIcon — Upcoming events / schedule
 * A calendar page with a dot marker.
 */
export function CalendarMarkIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            {/* Calendar body */}
            <rect x="4" y="5" width="16" height="16" rx="2" />
            {/* Binding rings */}
            <line x1="8" y1="3" x2="8" y2="7" />
            <line x1="16" y1="3" x2="16" y2="7" />
            {/* Header bar */}
            <line x1="4" y1="9" x2="20" y2="9" />
            {/* Date marker */}
            <circle cx="12" cy="15" r="2" fill="currentColor" stroke="none" opacity="0.6" />
        </svg>
    );
}

// ─── Dispatch Strategy Icons ──────────────────────────────────

// CrosshairIcon — Single target dispatch
// Precision crosshair reticle for focused targeting.
export function CrosshairIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <circle cx="12" cy="12" r="8" />
            <circle cx="12" cy="12" r="3" />
            <line x1="12" y1="2" x2="12" y2="6" />
            <line x1="12" y1="18" x2="12" y2="22" />
            <line x1="2" y1="12" x2="6" y2="12" />
            <line x1="18" y1="12" x2="22" y2="12" />
        </svg>
    );
}

// ParallelLinesIcon — Parallel dispatch (all simultaneous)
// Three parallel signal traces firing in unison.
export function ParallelLinesIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.5" strokeLinecap="round" className={className} style={style}>
            <line x1="4" y1="7" x2="20" y2="7" />
            <line x1="4" y1="12" x2="20" y2="12" />
            <line x1="4" y1="17" x2="20" y2="17" />
            <polygon points="19,5 22,7 19,9" fill="currentColor" stroke="none" opacity="0.6" />
            <polygon points="19,10 22,12 19,14" fill="currentColor" stroke="none" opacity="0.6" />
            <polygon points="19,15 22,17 19,19" fill="currentColor" stroke="none" opacity="0.6" />
        </svg>
    );
}

// ChainLinkIcon — Sequential chaining
// Interlocked chain links showing serial flow.
export function ChainLinkIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
    );
}

// MergePathsIcon — Consensus (merge multiple into one)
// Multiple paths converging to a single point.
export function MergePathsIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <line x1="4" y1="6" x2="14" y2="12" />
            <line x1="4" y1="12" x2="14" y2="12" />
            <line x1="4" y1="18" x2="14" y2="12" />
            <line x1="14" y1="12" x2="22" y2="12" />
            <circle cx="14" cy="12" r="2" fill="currentColor" stroke="none" opacity="0.5" />
        </svg>
    );
}

// CrossedSwordsIcon — Debate (opposing arguments)
// Two crossed blade-like lines — dialectic tension.
export function CrossedSwordsIcon({ size = 16, className, style }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
            <line x1="4" y1="4" x2="20" y2="20" />
            <line x1="20" y1="4" x2="4" y2="20" />
            <line x1="4" y1="4" x2="7" y2="4" />
            <line x1="4" y1="4" x2="4" y2="7" />
            <line x1="20" y1="4" x2="17" y2="4" />
            <line x1="20" y1="4" x2="20" y2="7" />
        </svg>
    );
}
