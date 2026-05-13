/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Custom SVG Icon Library
   Every icon is hand-crafted SVG. Zero stock icons. Zero lucide. Zero emoji.
   ═══════════════════════════════════════════════════════════════════════════ */
import React from 'react';

type P = React.SVGProps<SVGSVGElement> & { size?: number };
const D = ({ size = 16, children, ...p }: P & { children: React.ReactNode }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}>{children}</svg>
);

// ─── Tool Icons ─────────────────────────────────────────────────────────────

/** Cursor/Select — arrow pointer with selection box */
export const IconSelect = (p: P) => (
    <D {...p}>
        <path d="M5 3l10 10-3.5 1L13 18l-2 .5L9.5 14 6 15.5z" fill="currentColor" strokeWidth="1.2" />
        <rect x="14" y="14" width="7" height="7" rx="1" strokeDasharray="2 1.5" opacity=".5" />
    </D>
);

/** Move — four-way arrow cross */
export const IconMove = (p: P) => (
    <D {...p}>
        <path d="M12 2v20M2 12h20" />
        <path d="M12 2l-3 3m3-3l3 3" />
        <path d="M12 22l-3-3m3 3l3-3" />
        <path d="M2 12l3-3m-3 3l3 3" />
        <path d="M22 12l-3-3m3 3l-3 3" />
    </D>
);

/** Resize — diagonal double-headed arrow with corner brackets */
export const IconResize = (p: P) => (
    <D {...p}>
        <path d="M4 4h4M4 4v4" />
        <path d="M20 20h-4M20 20v-4" />
        <path d="M6 18l12-12" />
        <path d="M14 6l4 0 0 4" />
        <path d="M10 18l-4 0 0-4" />
    </D>
);

/** Style — paint bucket / droplet with sparkle */
export const IconStyle = (p: P) => (
    <D {...p}>
        <path d="M12 2C8 6.5 5 10 5 13.5a7 7 0 0014 0C19 10 16 6.5 12 2z" />
        <circle cx="12" cy="14" r="2" fill="currentColor" opacity=".3" />
        <path d="M19 4l1 2 2 1-2 1-1 2-1-2-2-1 2-1z" strokeWidth="1.2" fill="currentColor" opacity=".6" />
    </D>
);

/** Animate — play triangle with motion lines */
export const IconAnimate = (p: P) => (
    <D {...p}>
        <path d="M8 5v14l11-7z" fill="currentColor" opacity=".2" />
        <path d="M8 5v14l11-7z" />
        <path d="M3 8h2M2 12h3M3 16h2" opacity=".5" strokeWidth="1.5" />
    </D>
);

/** Inspect — magnifying glass with code brackets */
export const IconInspect = (p: P) => (
    <D {...p}>
        <circle cx="10" cy="10" r="7" />
        <path d="M15.5 15.5L21 21" strokeWidth="2" />
        <path d="M8 8l-1.5 2 1.5 2" strokeWidth="1.5" />
        <path d="M12 8l1.5 2-1.5 2" strokeWidth="1.5" />
    </D>
);

/** Reparent — node being dragged to new parent tree */
export const IconReparent = (p: P) => (
    <D {...p}>
        <circle cx="6" cy="5" r="2.5" />
        <path d="M6 7.5v3" />
        <circle cx="6" cy="14" r="2" opacity=".4" />
        <circle cx="18" cy="14" r="2.5" />
        <path d="M6 16v2h12v-2" opacity=".4" strokeDasharray="2 1.5" />
        <path d="M10 10l6 2" strokeWidth="1.5" />
        <path d="M16 12l-2-2m2 2l-1 2.5" strokeWidth="1.2" />
    </D>
);

/** Constraint — lock/anchor with dimension lines */
export const IconConstraint = (p: P) => (
    <D {...p}>
        <rect x="7" y="10" width="10" height="10" rx="2" />
        <path d="M9 10V7a3 3 0 016 0v3" />
        <circle cx="12" cy="15" r="1.5" fill="currentColor" />
        <path d="M12 16.5v2" strokeWidth="2" />
    </D>
);

// ─── Breakpoint Icons ───────────────────────────────────────────────────────

/** Desktop — monitor with stand */
export const IconDesktop = (p: P) => (
    <D {...p}>
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <path d="M8 21h8" />
        <path d="M12 17v4" />
        <rect x="4" y="5" width="16" height="10" rx="1" fill="currentColor" opacity=".08" />
    </D>
);

/** Tablet — rounded rect device */
export const IconTablet = (p: P) => (
    <D {...p}>
        <rect x="4" y="2" width="16" height="20" rx="3" />
        <path d="M10 18h4" strokeWidth="2" strokeLinecap="round" />
        <rect x="6" y="4" width="12" height="12" rx="1" fill="currentColor" opacity=".08" />
    </D>
);

/** Mobile — phone with notch */
export const IconMobile = (p: P) => (
    <D {...p}>
        <rect x="6" y="1" width="12" height="22" rx="3" />
        <path d="M10 4h4" strokeWidth="1.5" />
        <circle cx="12" cy="20" r="1" fill="currentColor" />
        <rect x="8" y="6" width="8" height="11" rx="1" fill="currentColor" opacity=".08" />
    </D>
);

// ─── Panel & UI Icons ───────────────────────────────────────────────────────

/** Layers — stacked planes */
export const IconLayers = (p: P) => (
    <D {...p}>
        <path d="M12 2L2 7l10 5 10-5z" />
        <path d="M2 12l10 5 10-5" opacity=".5" />
        <path d="M2 17l10 5 10-5" opacity=".3" />
    </D>
);

/** Templates — grid of preset blocks */
export const IconTemplates = (p: P) => (
    <D {...p}>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="4" rx="1.5" />
        <rect x="14" y="10" width="7" height="7" rx="1.5" />
        <rect x="3" y="13" width="7" height="8" rx="1.5" />
        <rect x="14" y="20" width="7" height="1" rx=".5" opacity=".4" />
    </D>
);

/** SVG Builder — pen tool with sparkle */
export const IconSvgBuilder = (p: P) => (
    <D {...p}>
        <path d="M12 20l-8-8 12-9 5 5-9 12z" />
        <path d="M4 12l2.5 2.5" />
        <circle cx="16.5" cy="7.5" r="1.5" fill="currentColor" opacity=".3" />
        <path d="M19 2l1 2 2 1-2 1-1 2-1-2-2-1 2-1z" strokeWidth="1" fill="currentColor" opacity=".7" />
    </D>
);

/** Timeline — horizontal tracks */
export const IconTimeline = (p: P) => (
    <D {...p}>
        <path d="M3 6h18" />
        <path d="M3 12h14" />
        <path d="M3 18h10" />
        <circle cx="8" cy="6" r="2" fill="currentColor" />
        <circle cx="13" cy="12" r="2" fill="currentColor" />
        <circle cx="10" cy="18" r="2" fill="currentColor" />
    </D>
);

/** Patches — diff/merge icon */
export const IconPatches = (p: P) => (
    <D {...p}>
        <path d="M4 4h6v6H4z" />
        <path d="M14 14h6v6h-6z" />
        <path d="M10 7h4l-4 10h4" strokeWidth="1.5" />
        <path d="M7 10v4" opacity=".4" />
        <path d="M17 10v4" opacity=".4" />
    </D>
);

/** Console — terminal prompt */
export const IconConsole = (p: P) => (
    <D {...p}>
        <rect x="2" y="4" width="20" height="16" rx="2" />
        <path d="M6 10l3 2-3 2" strokeWidth="2" />
        <path d="M12 16h5" strokeWidth="2" opacity=".5" />
    </D>
);

/** Chevron — expandable toggle */
export const IconChevron = (p: P & { direction?: 'right' | 'down' }) => {
    const rot = p.direction === 'down' ? 'rotate(90)' : undefined;
    return (
        <D {...p}>
            <g transform={rot}>
                <path d="M9 5l7 7-7 7" />
            </g>
        </D>
    );
};

/** Close/Collapse — X */
export const IconClose = (p: P) => (
    <D {...p}>
        <path d="M6 6l12 12M18 6L6 18" strokeWidth="2" />
    </D>
);

/** Panel toggle — horizontal lines with arrow */
export const IconPanelToggle = (p: P) => (
    <D {...p}>
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M3 9h18" />
        <path d="M9 3v18" opacity=".5" />
    </D>
);

/** Zoom In / Zoom Out */
export const IconZoomIn = (p: P) => (
    <D {...p}>
        <circle cx="10" cy="10" r="7" />
        <path d="M15.5 15.5L21 21" strokeWidth="2" />
        <path d="M7 10h6M10 7v6" strokeWidth="1.8" />
    </D>
);
export const IconZoomOut = (p: P) => (
    <D {...p}>
        <circle cx="10" cy="10" r="7" />
        <path d="M15.5 15.5L21 21" strokeWidth="2" />
        <path d="M7 10h6" strokeWidth="1.8" />
    </D>
);

// ─── Tree / Node Icons ──────────────────────────────────────────────────────

/** Component node — diamond */
export const IconComponent = (p: P) => (
    <D size={14} {...p}>
        <path d="M12 3l7 9-7 9-7-9z" fill="currentColor" opacity=".15" />
        <path d="M12 3l7 9-7 9-7-9z" />
    </D>
);

/** Element node — hollow diamond */
export const IconElement = (p: P) => (
    <D size={14} {...p}>
        <path d="M12 5l5 7-5 7-5-7z" />
    </D>
);

// ─── OmniBuilder Logo ───────────────────────────────────────────────────────

/** Logo — interlocking O/B prism */
export const IconLogo = (p: P) => (
    <svg width={p.size || 22} height={p.size || 22} viewBox="0 0 24 24" fill="none" {...p}>
        <defs>
            <linearGradient id="ob-grad" x1="0" y1="0" x2="24" y2="24">
                <stop offset="0%" stopColor="hsl(215, 92%, 62%)" />
                <stop offset="100%" stopColor="hsl(265, 72%, 62%)" />
            </linearGradient>
        </defs>
        <rect x="0" y="0" width="24" height="24" rx="5" fill="url(#ob-grad)" />
        <path d="M7 7l5-3 5 3v4l-5 3-5-3z" fill="white" opacity=".9" />
        <path d="M7 13l5 3 5-3v4l-5 3-5-3z" fill="white" opacity=".5" />
        <path d="M12 10v6" stroke="white" strokeWidth="1" opacity=".3" />
    </svg>
);

// ─── Template Category Icons ────────────────────────────────────────────────

/** Button template */
export const IconTplButton = (p: P) => (
    <D {...p}>
        <rect x="3" y="7" width="18" height="10" rx="5" />
        <path d="M8 12h5" strokeWidth="2" />
        <path d="M15 12h1" strokeWidth="2" opacity=".4" />
    </D>
);

/** Card template */
export const IconTplCard = (p: P) => (
    <D {...p}>
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <rect x="5" y="5" width="14" height="6" rx="1.5" fill="currentColor" opacity=".1" />
        <path d="M5 14h10" strokeWidth="1.5" />
        <path d="M5 17h6" strokeWidth="1.5" opacity=".4" />
    </D>
);

/** Navigation template */
export const IconTplNav = (p: P) => (
    <D {...p}>
        <rect x="2" y="6" width="20" height="4" rx="1" />
        <circle cx="5" cy="8" r="1" fill="currentColor" />
        <path d="M9 8h4" strokeWidth="1.5" opacity=".5" />
        <path d="M15 8h2" strokeWidth="1.5" opacity=".3" />
        <path d="M19 8h1" strokeWidth="1.5" opacity=".3" />
    </D>
);

/** Hero section template */
export const IconTplHero = (p: P) => (
    <D {...p}>
        <rect x="2" y="2" width="20" height="20" rx="2" />
        <path d="M7 8h10" strokeWidth="2" />
        <path d="M8 12h8" strokeWidth="1.5" opacity=".4" />
        <rect x="9" y="16" width="6" height="3" rx="1.5" fill="currentColor" opacity=".3" />
    </D>
);

/** Form template */
export const IconTplForm = (p: P) => (
    <D {...p}>
        <rect x="4" y="3" width="16" height="18" rx="2" />
        <path d="M7 7h10" strokeWidth="1.5" />
        <rect x="7" y="10" width="10" height="3" rx="1" opacity=".3" />
        <rect x="7" y="15" width="10" height="3" rx="1" opacity=".3" />
    </D>
);

/** Page layout template */
export const IconTplLayout = (p: P) => (
    <D {...p}>
        <rect x="2" y="2" width="20" height="20" rx="2" />
        <path d="M2 7h20" />
        <path d="M8 7v15" />
        <rect x="10" y="9" width="10" height="5" rx="1" fill="currentColor" opacity=".06" />
        <rect x="10" y="16" width="4.5" height="4" rx="1" fill="currentColor" opacity=".06" />
        <rect x="16" y="16" width="4.5" height="4" rx="1" fill="currentColor" opacity=".06" />
    </D>
);

/** Grid / Feature section template */
export const IconTplGrid = (p: P) => (
    <D {...p}>
        <rect x="2" y="2" width="9" height="9" rx="2" />
        <rect x="13" y="2" width="9" height="9" rx="2" />
        <rect x="2" y="13" width="9" height="9" rx="2" />
        <rect x="13" y="13" width="9" height="9" rx="2" />
    </D>
);

/** Footer template */
export const IconTplFooter = (p: P) => (
    <D {...p}>
        <rect x="2" y="14" width="20" height="8" rx="2" />
        <path d="M6 17h3" strokeWidth="1.5" opacity=".5" />
        <path d="M6 20h5" strokeWidth="1.5" opacity=".3" />
        <path d="M14 17h4" strokeWidth="1.5" opacity=".5" />
        <path d="M14 20h3" strokeWidth="1.5" opacity=".3" />
        <rect x="2" y="2" width="20" height="8" rx="2" opacity=".15" />
    </D>
);

/** Modal / Dialog template */
export const IconTplModal = (p: P) => (
    <D {...p}>
        <rect x="1" y="1" width="22" height="22" rx="2" opacity=".15" />
        <rect x="4" y="5" width="16" height="14" rx="2.5" />
        <path d="M7 9h10" strokeWidth="1.5" />
        <path d="M7 12h6" strokeWidth="1.2" opacity=".4" />
        <rect x="12" y="15" width="5" height="2" rx="1" fill="currentColor" opacity=".3" />
    </D>
);

// ─── SVG Builder Icons ──────────────────────────────────────────────────────

/** Pen tool */
export const IconPenTool = (p: P) => (
    <D {...p}>
        <path d="M12 20L4 12l10-9 7 7-9 10z" />
        <circle cx="14" cy="10" r="1.5" fill="currentColor" />
        <path d="M4 12l2 2" strokeWidth="2" />
    </D>
);

/** Path/Bezier */
export const IconBezier = (p: P) => (
    <D {...p}>
        <circle cx="4" cy="18" r="2" />
        <circle cx="20" cy="6" r="2" />
        <path d="M6 18C6 8 18 16 18 6" />
        <path d="M6 18L10 10" strokeDasharray="2 2" opacity=".4" />
        <path d="M18 6L14 14" strokeDasharray="2 2" opacity=".4" />
    </D>
);

/** Shape rect */
export const IconShapeRect = (p: P) => (
    <D {...p}>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <circle cx="3" cy="5" r="1.5" fill="currentColor" />
        <circle cx="21" cy="5" r="1.5" fill="currentColor" />
        <circle cx="3" cy="19" r="1.5" fill="currentColor" />
        <circle cx="21" cy="19" r="1.5" fill="currentColor" />
    </D>
);

/** Shape circle */
export const IconShapeCircle = (p: P) => (
    <D {...p}>
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="3" r="1.5" fill="currentColor" />
        <circle cx="21" cy="12" r="1.5" fill="currentColor" />
        <circle cx="12" cy="21" r="1.5" fill="currentColor" />
        <circle cx="3" cy="12" r="1.5" fill="currentColor" />
    </D>
);

/** Keyframe diamond */
export const IconKeyframe = (p: P) => (
    <D {...p}>
        <path d="M12 3l7 9-7 9-7-9z" fill="currentColor" opacity=".15" />
        <path d="M12 3l7 9-7 9-7-9z" />
        <circle cx="12" cy="12" r="2" fill="currentColor" />
    </D>
);

/** Easing curve */
export const IconEasing = (p: P) => (
    <D {...p}>
        <rect x="3" y="3" width="18" height="18" rx="2" opacity=".2" />
        <path d="M5 19C5 9 19 15 19 5" strokeWidth="2" />
        <circle cx="5" cy="19" r="1.5" fill="currentColor" />
        <circle cx="19" cy="5" r="1.5" fill="currentColor" />
    </D>
);

/** Color palette / fill */
export const IconPalette = (p: P) => (
    <D {...p}>
        <path d="M12 2a10 10 0 000 20c1.7 0 3-1.3 3-3 0-.8-.3-1.5-.7-2-.4-.5-.7-1.2-.7-2 0-1.7 1.3-3 3-3h2.5A7.5 7.5 0 0012 2z" />
        <circle cx="7" cy="10" r="1.5" fill="currentColor" />
        <circle cx="10" cy="6.5" r="1.5" fill="currentColor" />
        <circle cx="15" cy="6.5" r="1.5" fill="currentColor" />
    </D>
);

/** Play */
export const IconPlay = (p: P) => (
    <D {...p}><path d="M6 4v16l14-8z" fill="currentColor" opacity=".3" /><path d="M6 4v16l14-8z" /></D>
);

/** Pause */
export const IconPause = (p: P) => (
    <D {...p}><rect x="5" y="4" width="4" height="16" rx="1" /><rect x="15" y="4" width="4" height="16" rx="1" /></D>
);

/** Plus */
export const IconPlus = (p: P) => (
    <D {...p}><path d="M12 5v14M5 12h14" strokeWidth="2" /></D>
);

/** Minus */
export const IconMinus = (p: P) => (
    <D {...p}><path d="M5 12h14" strokeWidth="2" /></D>
);

/** Search */
export const IconSearch = (p: P) => (
    <D {...p}>
        <circle cx="10" cy="10" r="7" />
        <path d="M15.5 15.5L21 21" strokeWidth="2.5" />
    </D>
);

/** File / Document */
export const IconFile = (p: P) => (
    <D {...p}>
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" />
        <path d="M14 2v6h6" />
        <path d="M8 14h8M8 18h5" opacity=".4" />
    </D>
);

/** Star / Favorite */
export const IconStar = (p: P) => (
    <D {...p}>
        <path d="M12 2l3 6.5 7 1-5 5 1.2 7L12 18l-6.2 3.5L7 14.5l-5-5 7-1z" />
    </D>
);

/** Download */
export const IconDownload = (p: P) => (
    <D {...p}>
        <path d="M12 3v14" strokeWidth="2" />
        <path d="M7 12l5 5 5-5" strokeWidth="2" />
        <path d="M5 20h14" strokeWidth="2" />
    </D>
);

// ─── Visual Instrument Editor Icons ─────────────────────────────────────────

/** Visual Instruments — eye with tuning fork prongs */
export const IconVisualInstruments = (p: P) => (
    <D {...p}>
        <circle cx="12" cy="12" r="3" />
        <path d="M2 12c2-4 5.5-7 10-7s8 3 10 7c-2 4-5.5 7-10 7s-8-3-10-7z" />
        <path d="M15 8l2-5M17 8l2-5" strokeWidth="1.4" opacity=".6" />
    </D>
);

/** Box Model — nested rectangles for margin/padding/content */
export const IconBoxModel = (p: P) => (
    <D {...p}>
        <rect x="2" y="2" rx="1" width="20" height="20" strokeDasharray="2 2" opacity=".4" />
        <rect x="5" y="5" rx="1" width="14" height="14" opacity=".7" />
        <rect x="8" y="8" rx="1" width="8" height="8" fill="currentColor" opacity=".3" stroke="currentColor" />
    </D>
);

/** Radius — rounded corner with arc handle */
export const IconRadius = (p: P) => (
    <D {...p}>
        <path d="M4 20V10a6 6 0 016-6h10" />
        <circle cx="10" cy="4" r="2" fill="currentColor" opacity=".6" />
        <path d="M4 15l3-3M9 4l3 3" strokeWidth="1.2" opacity=".4" />
    </D>
);

/** Gradient Strip — horizontal bar with color stops */
export const IconGradientStrip = (p: P) => (
    <D {...p}>
        <rect x="2" y="8" rx="3" width="20" height="8" opacity=".4" fill="currentColor" />
        <circle cx="6" cy="12" r="2" fill="currentColor" />
        <circle cx="12" cy="12" r="2" fill="currentColor" opacity=".7" />
        <circle cx="18" cy="12" r="2" fill="currentColor" opacity=".4" />
        <path d="M6 6v2M12 6v2M18 6v2" strokeWidth="1.5" />
    </D>
);

/** Shadow Sculptor — element with offset glow/shadow */
export const IconShadow = (p: P) => (
    <D {...p}>
        <rect x="7" y="7" rx="2" width="10" height="10" opacity=".3" fill="currentColor" strokeWidth="0" />
        <rect x="5" y="5" rx="2" width="10" height="10" />
        <circle cx="18" cy="4" r="2.5" fill="currentColor" opacity=".5" strokeWidth="0" />
        <path d="M16 5.5l-2 2" strokeWidth="1.2" opacity=".4" />
    </D>
);

/** Typography Scale — stacked text lines at different sizes */
export const IconTypography = (p: P) => (
    <D {...p}>
        <path d="M4 5h16" strokeWidth="2.5" />
        <path d="M4 10h12" strokeWidth="1.8" />
        <path d="M4 15h9" strokeWidth="1.3" />
        <path d="M4 19h6" strokeWidth="1" opacity=".6" />
        <path d="M20 10v10" strokeWidth="1" opacity=".3" />
        <path d="M18 12l2-2 2 2" strokeWidth="1" opacity=".3" />
    </D>
);

/** Logo Studio — spectral prism with radiating beams */
export const IconLogoStudio = (p: P) => (
    <D {...p}>
        <polygon points="12,3 20,14 12,21 4,14" fill="none" />
        <line x1="12" y1="3" x2="12" y2="0" opacity=".5" />
        <line x1="20" y1="14" x2="23" y2="13" opacity=".4" />
        <line x1="4" y1="14" x2="1" y2="13" opacity=".4" />
        <line x1="12" y1="21" x2="12" y2="24" opacity=".5" />
        <line x1="17" y1="8" x2="21" y2="4" opacity=".3" />
        <line x1="7" y1="8" x2="3" y2="4" opacity=".3" />
        <circle cx="12" cy="12" r="2" fill="currentColor" strokeWidth="0" opacity=".6" />
    </D>
);
