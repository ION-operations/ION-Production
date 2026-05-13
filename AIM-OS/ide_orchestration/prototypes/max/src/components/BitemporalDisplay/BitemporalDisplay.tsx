// Bitemporal Display Component - Max V2
// Reusable component for displaying bitemporal metadata

import React from 'react';
import { Clock, Calendar } from 'lucide-react';
import { BitemporalMetadata, formatBitemporalRange, getValidityDuration } from '../utils/bitemporal';
import './BitemporalDisplay.css';

export interface BitemporalDisplayProps {
  bitemporal: BitemporalMetadata;
  showDuration?: boolean;
  compact?: boolean;
  className?: string;
}

export const BitemporalDisplay: React.FC<BitemporalDisplayProps> = ({
  bitemporal,
  showDuration = true,
  compact = false,
  className = '',
}) => {
  const duration = showDuration ? getValidityDuration(bitemporal) : null;
  const isCurrent = bitemporal.valid_to === null;

  if (compact) {
    return (
      <div className={`bitemporal-display bitemporal-compact ${className}`}>
        <Clock className="bitemporal-icon" />
        <span className="bitemporal-text">
          {new Date(bitemporal.valid_from).toLocaleDateString()}
          {isCurrent && <span className="bitemporal-current"> (Current)</span>}
        </span>
      </div>
    );
  }

  return (
    <div className={`bitemporal-display ${className}`} role="group" aria-label="Bitemporal metadata">
      <div className="bitemporal-row">
        <div className="bitemporal-item">
          <Calendar className="bitemporal-icon" />
          <div className="bitemporal-content">
            <div className="bitemporal-label">Valid From:</div>
            <div className="bitemporal-value">
              {new Date(bitemporal.valid_from).toLocaleString()}
            </div>
          </div>
        </div>
        {bitemporal.valid_to && (
          <div className="bitemporal-item">
            <Calendar className="bitemporal-icon" />
            <div className="bitemporal-content">
              <div className="bitemporal-label">Valid To:</div>
              <div className="bitemporal-value">
                {new Date(bitemporal.valid_to).toLocaleString()}
              </div>
            </div>
          </div>
        )}
        {isCurrent && (
          <div className="bitemporal-badge bitemporal-badge-current">
            Current
          </div>
        )}
      </div>
      {duration && (
        <div className="bitemporal-duration">
          <Clock className="bitemporal-icon-small" />
          <span>Duration: {duration}</span>
        </div>
      )}
      <div className="bitemporal-range">
        {formatBitemporalRange(bitemporal)}
      </div>
    </div>
  );
};

