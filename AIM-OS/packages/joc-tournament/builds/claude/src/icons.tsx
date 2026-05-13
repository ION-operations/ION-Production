import React from 'react';

interface IconProps {
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}

// ─── Radar — Mission Control / System Status ─────────────────
export const RadarIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <circle cx="12" cy="12" r="10" opacity="0.3" />
    <circle cx="12" cy="12" r="6" opacity="0.5" />
    <circle cx="12" cy="12" r="2" />
    <line x1="12" y1="12" x2="18" y2="6" />
    <circle cx="16" cy="8" r="1.5" fill="currentColor" opacity="0.8" />
  </svg>
);

// ─── Constellation — Agent Fleet / Workforce ─────────────────
export const ConstellationIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" className={className} style={style}>
    <circle cx="6" cy="6" r="2" fill="currentColor" opacity="0.9" />
    <circle cx="18" cy="6" r="2" fill="currentColor" opacity="0.7" />
    <circle cx="12" cy="18" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="18" cy="16" r="1.5" fill="currentColor" opacity="0.5" />
    <line x1="6" y1="6" x2="18" y2="6" opacity="0.4" />
    <line x1="6" y1="6" x2="12" y2="18" opacity="0.4" />
    <line x1="18" y1="6" x2="12" y2="18" opacity="0.3" />
    <line x1="18" y1="6" x2="18" y2="16" opacity="0.3" />
  </svg>
);

// ─── Launch Vector — Dispatch / Missions ─────────────────────
export const LaunchVectorIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <path d="M4 20 Q 8 12, 12 10 Q 16 8, 20 4" />
    <circle cx="8" cy="14" r="1.5" fill="currentColor" opacity="0.4" />
    <circle cx="14" cy="8" r="1.5" fill="currentColor" opacity="0.6" />
    <polyline points="16,4 20,4 20,8" fill="none" />
  </svg>
);

// ─── Signal Pulse — Communications ───────────────────────────
export const SignalPulseIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <polyline points="2,12 5,12 8,6 11,18 14,8 17,14 20,12 22,12" />
  </svg>
);

// ─── Hex Lattice — Context Lab / Memory ──────────────────────
export const HexLatticeIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <polygon points="12,2 18,6 18,12 12,16 6,12 6,6" opacity="0.6" />
    <polygon points="12,8 15,10 15,14 12,16 9,14 9,10" fill="currentColor" opacity="0.3" />
    <circle cx="12" cy="12" r="1.5" fill="currentColor" />
  </svg>
);

// ─── Chip Die — Infrastructure / Compute ─────────────────────
export const ChipDieIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <rect x="6" y="6" width="12" height="12" rx="1" />
    <rect x="9" y="9" width="6" height="6" rx="0.5" fill="currentColor" opacity="0.2" />
    <line x1="9" y1="6" x2="9" y2="3" /><line x1="12" y1="6" x2="12" y2="3" /><line x1="15" y1="6" x2="15" y2="3" />
    <line x1="9" y1="18" x2="9" y2="21" /><line x1="12" y1="18" x2="12" y2="21" /><line x1="15" y1="18" x2="15" y2="21" />
    <line x1="6" y1="9" x2="3" y2="9" /><line x1="6" y1="12" x2="3" y2="12" /><line x1="6" y1="15" x2="3" y2="15" />
    <line x1="18" y1="9" x2="21" y2="9" /><line x1="18" y1="12" x2="21" y2="12" /><line x1="18" y1="15" x2="21" y2="15" />
  </svg>
);

// ─── Bolt — Oracle ───────────────────────────────────────────
export const BoltIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className} style={style}>
    <path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z" opacity="0.9" />
  </svg>
);

// ─── Robot Head — Agent Identity ─────────────────────────────
export const RobotHeadIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <rect x="5" y="8" width="14" height="12" rx="3" />
    <circle cx="9" cy="14" r="1.5" fill="currentColor" />
    <circle cx="15" cy="14" r="1.5" fill="currentColor" />
    <line x1="12" y1="4" x2="12" y2="8" />
    <circle cx="12" cy="3" r="1" fill="currentColor" />
    <line x1="3" y1="14" x2="5" y2="14" />
    <line x1="19" y1="14" x2="21" y2="14" />
  </svg>
);

// ─── Clipboard List — Activity Feed ─────────────────────────
export const ClipboardListIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <rect x="5" y="3" width="14" height="18" rx="2" />
    <path d="M9 3h6v2H9z" fill="currentColor" opacity="0.3" />
    <line x1="9" y1="10" x2="15" y2="10" opacity="0.6" />
    <line x1="9" y1="13" x2="15" y2="13" opacity="0.5" />
    <line x1="9" y1="16" x2="13" y2="16" opacity="0.4" />
  </svg>
);

// ─── Satellite — MCP Connection ──────────────────────────────
export const SatelliteIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <circle cx="12" cy="12" r="3" />
    <path d="M12 2v4" /><path d="M12 18v4" />
    <path d="M2 12h4" /><path d="M18 12h4" />
    <path d="M4.93 4.93l2.83 2.83" opacity="0.5" />
    <path d="M16.24 16.24l2.83 2.83" opacity="0.5" />
  </svg>
);

// ─── Close ───────────────────────────────────────────────────
export const CloseIcon: React.FC<IconProps> = ({ size = 16, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" className={className} style={style}>
    <line x1="6" y1="6" x2="18" y2="18" />
    <line x1="18" y1="6" x2="6" y2="18" />
  </svg>
);

// ─── Chevrons ────────────────────────────────────────────────
export const ChevronUpIcon: React.FC<IconProps> = ({ size = 14, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <polyline points="6,15 12,9 18,15" />
  </svg>
);

export const ChevronDownIcon: React.FC<IconProps> = ({ size = 14, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <polyline points="6,9 12,15 18,9" />
  </svg>
);

// ─── JOC Logo — Hexagon Command Mark ─────────────────────────
export const JOCLogo: React.FC<IconProps> = ({ size = 24, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" className={className} style={style}>
    <polygon points="16,2 28,9 28,23 16,30 4,23 4,9"
      fill="none" stroke="#F5A623" strokeWidth="1.5" opacity="0.8" />
    <polygon points="16,8 22,12 22,20 16,24 10,20 10,12"
      fill="#F5A623" opacity="0.15" />
    <text x="16" y="19" textAnchor="middle" fill="#F5A623"
      fontSize="8" fontFamily="Inter" fontWeight="700" letterSpacing="0.5">J</text>
  </svg>
);

// ─── Shield Key — Credentials ────────────────────────────────
export const ShieldKeyIcon: React.FC<IconProps> = ({ size = 18, className, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} style={style}>
    <path d="M12 2l8 4v6c0 5.5-3.84 10.74-8 12-4.16-1.26-8-6.5-8-12V6l8-4z" opacity="0.4" />
    <circle cx="12" cy="11" r="2" />
    <line x1="12" y1="13" x2="12" y2="17" />
  </svg>
);
