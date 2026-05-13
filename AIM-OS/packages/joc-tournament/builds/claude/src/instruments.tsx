import React from 'react';
import type { TruthState } from './store';

// ═══════════════════════════════════════════════════════════════
// Truth Badge — Law 2: Data truth must be explicit
// ═══════════════════════════════════════════════════════════════

const TRUTH_LABELS: Record<TruthState, string> = {
  LIVE: 'LIVE',
  CACHED: 'CACHED',
  MOCK: 'MOCK',
  OFFLINE: 'OFFLINE',
  SPECULATIVE: 'AI PRED',
};

const TRUTH_LED: Record<TruthState, string> = {
  LIVE: 'green',
  CACHED: 'amber',
  MOCK: 'amber',
  OFFLINE: 'off',
  SPECULATIVE: 'purple',
};

export const TruthBadge: React.FC<{ state: TruthState }> = ({ state }) => (
  <span className={`truth-badge ${state}`}>
    <span className={`led ${TRUTH_LED[state]}`} />
    {TRUTH_LABELS[state]}
  </span>
);

// ═══════════════════════════════════════════════════════════════
// Instrument Header — Section header with truth badge
// ═══════════════════════════════════════════════════════════════

export const InstrumentHeader: React.FC<{
  title: string;
  truthState: TruthState;
  subtitle?: string;
}> = ({ title, truthState, subtitle }) => (
  <div className="instrument-header">
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span className="instrument-title">{title}</span>
      {subtitle && (
        <span style={{ fontSize: 9, color: 'var(--text-ghost)', fontFamily: 'var(--font-data)' }}>
          {subtitle}
        </span>
      )}
    </div>
    <TruthBadge state={truthState} />
  </div>
);

// ═══════════════════════════════════════════════════════════════
// Instrument Panel — Recessed bay container
// ═══════════════════════════════════════════════════════════════

export const InstrumentPanel: React.FC<{
  title: string;
  truthState: TruthState;
  subtitle?: string;
  children: React.ReactNode;
}> = ({ title, truthState, subtitle, children }) => (
  <div className="instrument-panel">
    <InstrumentHeader title={title} truthState={truthState} subtitle={subtitle} />
    <div className="instrument-body">
      {children}
    </div>
  </div>
);

// ═══════════════════════════════════════════════════════════════
// LED — Status indicator light
// ═══════════════════════════════════════════════════════════════

export const LED: React.FC<{
  color: 'green' | 'amber' | 'red' | 'blue' | 'off' | 'purple';
  pulse?: boolean;
  size?: number;
}> = ({ color, pulse, size }) => (
  <span
    className={`led ${color}${pulse ? ' pulse' : ''}`}
    style={size ? { width: size, height: size } : undefined}
  />
);

// ═══════════════════════════════════════════════════════════════
// LCD Readout — Phosphor display
// ═══════════════════════════════════════════════════════════════

export const LCD: React.FC<{
  children: React.ReactNode;
  variant?: 'amber' | 'cyan' | 'green' | 'red';
}> = ({ children, variant }) => (
  <span className={`lcd${variant && variant !== 'amber' ? ` ${variant}` : ''}`}>
    {children}
  </span>
);

// ═══════════════════════════════════════════════════════════════
// Health Bar — VU-meter segmented indicator
// ═══════════════════════════════════════════════════════════════

export const HealthBar: React.FC<{
  value: number; // 0-1
  segments?: number;
  label?: string;
  showValue?: boolean;
}> = ({ value, segments = 12, label, showValue = true }) => {
  const litCount = Math.round(value * segments);

  const getSegmentClass = (index: number): string => {
    if (index >= litCount) return 'health-segment';
    const position = index / segments;
    if (position < 0.6) return 'health-segment lit-green';
    if (position < 0.8) return 'health-segment lit-amber';
    return 'health-segment lit-red';
  };

  return (
    <div className="health-bar">
      {label && <span className="health-bar-label">{label}</span>}
      <div className="health-bar-track">
        {Array.from({ length: segments }, (_, i) => (
          <div key={i} className={getSegmentClass(i)} />
        ))}
      </div>
      {showValue && (
        <span className="health-bar-value">{Math.round(value * 100)}%</span>
      )}
    </div>
  );
};
