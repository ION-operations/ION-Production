import React from 'react';

// ═══════════════════════════════════════════════════════════════════
// CUSTOM SVG ICONS — Precision instrument aesthetic
// Every icon is 16×16 by default, stroke-based, amber-compatible
// ═══════════════════════════════════════════════════════════════════

interface IconProps {
    size?: number;
    color?: string;
    className?: string;
}

const d = (props: IconProps) => ({
    width: props.size || 16,
    height: props.size || 16,
    viewBox: '0 0 16 16',
    fill: 'none',
    xmlns: 'http://www.w3.org/2000/svg',
    className: props.className,
    style: { flexShrink: 0 },
});

// ─── Navigation / Workspace Icons ─────────────────────────────

export function IconDashboard(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <rect x="1.5" y="1.5" width="5.5" height="5.5" rx="1" stroke={c} strokeWidth="1.2" />
            <rect x="9" y="1.5" width="5.5" height="3" rx="1" stroke={c} strokeWidth="1.2" />
            <rect x="1.5" y="9" width="5.5" height="5.5" rx="1" stroke={c} strokeWidth="1.2" />
            <rect x="9" y="6.5" width="5.5" height="8" rx="1" stroke={c} strokeWidth="1.2" />
        </svg>
    );
}

export function IconDispatch(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M3 8h8M8 4l4 4-4 4" stroke={c} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="8" cy="8" r="6.5" stroke={c} strokeWidth="1" opacity="0.3" />
        </svg>
    );
}

export function IconAgents(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M8 1.5L13.5 4.75V11.25L8 14.5L2.5 11.25V4.75L8 1.5Z" stroke={c} strokeWidth="1.2" strokeLinejoin="round" />
            <circle cx="8" cy="7.5" r="2" stroke={c} strokeWidth="1" />
            <path d="M5 12.5C5.5 10.5 6.5 9.5 8 9.5s2.5 1 3 3" stroke={c} strokeWidth="1" strokeLinecap="round" opacity="0.6" />
        </svg>
    );
}

export function IconOracle(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M2 8c0 0 2.5-4.5 6-4.5S14 8 14 8s-2.5 4.5-6 4.5S2 8 2 8z" stroke={c} strokeWidth="1.2" />
            <circle cx="8" cy="8" r="2" stroke={c} strokeWidth="1.2" />
            <circle cx="8" cy="8" r="0.8" fill={c} />
        </svg>
    );
}

export function IconInfra(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <rect x="3" y="2" width="10" height="4" rx="1" stroke={c} strokeWidth="1.2" />
            <rect x="3" y="10" width="10" height="4" rx="1" stroke={c} strokeWidth="1.2" />
            <circle cx="5.5" cy="4" r="0.7" fill={c} />
            <circle cx="5.5" cy="12" r="0.7" fill={c} />
            <path d="M8 6v4" stroke={c} strokeWidth="1" strokeDasharray="1.5 1" opacity="0.5" />
        </svg>
    );
}

export function IconCode(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M5.5 4L2 8l3.5 4" stroke={c} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M10.5 4L14 8l-3.5 4" stroke={c} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M9 2.5L7 13.5" stroke={c} strokeWidth="1" opacity="0.4" />
        </svg>
    );
}

export function IconContext(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <circle cx="8" cy="5" r="2" stroke={c} strokeWidth="1.1" />
            <circle cx="4" cy="11" r="1.5" stroke={c} strokeWidth="1.1" />
            <circle cx="12" cy="11" r="1.5" stroke={c} strokeWidth="1.1" />
            <path d="M6.5 6.5L5 9.5M9.5 6.5L11 9.5M5.5 11h5" stroke={c} strokeWidth="0.8" opacity="0.5" />
        </svg>
    );
}

// ─── Panel / Section Icons ────────────────────────────────────

export function IconForce(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <circle cx="5" cy="5" r="2" stroke={c} strokeWidth="1" />
            <circle cx="11" cy="5" r="2" stroke={c} strokeWidth="1" />
            <circle cx="5" cy="11" r="2" stroke={c} strokeWidth="1" />
            <circle cx="11" cy="11" r="2" stroke={c} strokeWidth="1" />
            <path d="M7 5h2M7 11h2M5 7v2M11 7v2" stroke={c} strokeWidth="0.7" opacity="0.4" />
            <circle cx="8" cy="8" r="1" fill={c} opacity="0.6" />
        </svg>
    );
}

export function IconSystems(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <rect x="2" y="2" width="4" height="4" rx="0.5" stroke={c} strokeWidth="1" />
            <rect x="10" y="2" width="4" height="4" rx="0.5" stroke={c} strokeWidth="1" />
            <rect x="2" y="10" width="4" height="4" rx="0.5" stroke={c} strokeWidth="1" />
            <rect x="10" y="10" width="4" height="4" rx="0.5" stroke={c} strokeWidth="1" />
            <path d="M6 4h4M6 12h4M4 6v4M12 6v4" stroke={c} strokeWidth="0.7" opacity="0.35" />
        </svg>
    );
}

export function IconMission(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <circle cx="8" cy="8" r="6.5" stroke={c} strokeWidth="1" />
            <circle cx="8" cy="8" r="4" stroke={c} strokeWidth="0.8" opacity="0.5" />
            <circle cx="8" cy="8" r="1.5" fill={c} />
            <path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2" stroke={c} strokeWidth="0.8" opacity="0.3" />
        </svg>
    );
}

export function IconComms(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M2 4h12v7a1 1 0 01-1 1H6l-3 2v-2H3a1 1 0 01-1-1V4z" stroke={c} strokeWidth="1.1" />
            <path d="M5 7h6M5 9.5h3" stroke={c} strokeWidth="0.9" opacity="0.5" strokeLinecap="round" />
        </svg>
    );
}

export function IconApproval(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M8 1.5L14.5 5v6L8 14.5L1.5 11V5L8 1.5z" stroke={c} strokeWidth="1.1" />
            <path d="M5.5 8l2 2 3.5-4" stroke={c} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconMemory(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <circle cx="8" cy="6" r="3.5" stroke={c} strokeWidth="1.1" />
            <path d="M4 9c0 2.5 1.8 4.5 4 4.5s4-2 4-4.5" stroke={c} strokeWidth="1.1" />
            <path d="M6 5.5c.5-.8 1.2-1 2-1s1.5.2 2 1" stroke={c} strokeWidth="0.8" opacity="0.4" />
        </svg>
    );
}

export function IconActivity(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M1.5 8h3l1.5-4 2 8 1.5-5 1.5 3h3.5" stroke={c} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconTerminal(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <rect x="1.5" y="2.5" width="13" height="11" rx="1.5" stroke={c} strokeWidth="1.1" />
            <path d="M4 7l2.5 2L4 11" stroke={c} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M8.5 11h3.5" stroke={c} strokeWidth="1.1" strokeLinecap="round" />
        </svg>
    );
}

// ─── Rank Icons ─────────────────────────────────────────────

export function IconRankStar(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)} viewBox="0 0 12 12">
            <path d="M6 1l1.5 3.1 3.4.5-2.5 2.4.6 3.4L6 8.9 3 10.4l.6-3.4L1.1 4.6l3.4-.5L6 1z" fill={c} opacity="0.8" />
        </svg>
    );
}

export function IconRankChevron(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)} viewBox="0 0 12 12">
            <path d="M2 4l4 3 4-3" stroke={c} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            <path d="M2 7l4 3 4-3" stroke={c} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" opacity="0.4" />
        </svg>
    );
}

// ─── Status Icons ─────────────────────────────────────────────

export function IconRefresh(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M12.5 3v3.5h-3.5" stroke={c} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M3.5 13v-3.5H7" stroke={c} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M4.5 5.5A5 5 0 0112.5 6.5M11.5 10.5a5 5 0 01-8-1" stroke={c} strokeWidth="1.2" strokeLinecap="round" />
        </svg>
    );
}

export function IconSearch(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <circle cx="7" cy="7" r="4.5" stroke={c} strokeWidth="1.2" />
            <path d="M10.5 10.5L14 14" stroke={c} strokeWidth="1.3" strokeLinecap="round" />
        </svg>
    );
}

export function IconChevronDown(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M4 6l4 4 4-4" stroke={c} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconBolt(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <path d="M8.5 1.5L3.5 9h4l-1 5.5 6-8h-4.5l.5-5z" stroke={c} strokeWidth="1.1" strokeLinejoin="round" fill={c} fillOpacity="0.15" />
        </svg>
    );
}

export function IconClock(p: IconProps) {
    const c = p.color || 'currentColor';
    return (
        <svg {...d(p)}>
            <circle cx="8" cy="8" r="6" stroke={c} strokeWidth="1.1" />
            <path d="M8 4v4.5l3 1.5" stroke={c} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}
