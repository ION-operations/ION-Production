// Confidence Indicator Component - Max V2
// Reusable component for displaying VIF confidence scores

import React from 'react';
import { Shield, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import {
  ConfidenceLevel,
  getConfidenceLevel,
  formatConfidence,
  getConfidenceIcon,
  getConfidenceDescription,
  getConfidenceStatus,
} from '../../utils/confidence';
import './ConfidenceIndicator.css';

export interface ConfidenceIndicatorProps {
  confidence: number | null | undefined;
  threshold?: number; // Default threshold for pass/warn/fail
  showPercentage?: boolean;
  showLabel?: boolean;
  showIcon?: boolean;
  showDescription?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'badge' | 'inline' | 'full';
  className?: string;
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidence,
  threshold = 0.70,
  showPercentage = true,
  showLabel = true,
  showIcon = true,
  showDescription = false,
  size = 'md',
  variant = 'badge',
  className = '',
}) => {
  const level: ConfidenceLevel = getConfidenceLevel(confidence);
  const status = getConfidenceStatus(confidence, threshold);
  const icon = getConfidenceIcon(confidence);
  const description = getConfidenceDescription(confidence);

  const getStatusIcon = () => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="confidence-status-icon" />;
      case 'warn':
        return <AlertCircle className="confidence-status-icon" />;
      case 'fail':
        return <XCircle className="confidence-status-icon" />;
    }
  };

  if (variant === 'inline') {
    return (
      <span className={`confidence-indicator confidence-inline confidence-${size} ${className}`}>
        {showIcon && <span className="confidence-icon-emoji">{icon}</span>}
        {showLabel && <span className="confidence-label">{level.label}</span>}
        {showPercentage && (
          <span className="confidence-percentage">{formatConfidence(confidence)}</span>
        )}
      </span>
    );
  }

  if (variant === 'full') {
    return (
      <div className={`confidence-indicator confidence-full confidence-${size} ${className}`} role="group" aria-label="Confidence indicator">
        <div className="confidence-full-header">
          <div className="confidence-full-left">
            {showIcon && <Shield className="confidence-full-icon" style={{ color: level.color }} />}
            <div className="confidence-full-info">
              <div className="confidence-full-label">VIF Confidence</div>
              {showDescription && (
                <div className="confidence-full-description">{description}</div>
              )}
            </div>
          </div>
          <div className="confidence-full-right">
            {getStatusIcon()}
            <span className="confidence-full-value" style={{ color: level.color }}>
              {formatConfidence(confidence)}
            </span>
          </div>
        </div>
        {showLabel && (
          <div className="confidence-full-band">
            <span className="confidence-band-badge" style={{ backgroundColor: level.color + '20', color: level.color }}>
              {level.label} Confidence
            </span>
          </div>
        )}
      </div>
    );
  }

  // Default: badge variant
  return (
    <span
      className={`confidence-indicator confidence-badge confidence-${level.band} confidence-${size} ${className}`}
      style={{ borderColor: level.color + '40', backgroundColor: level.color + '10' }}
      role="status"
      aria-label={`Confidence: ${level.label} (${formatConfidence(confidence)})`}
      title={showDescription ? description : undefined}
    >
      {showIcon && <span className="confidence-icon-emoji">{icon}</span>}
      {showLabel && <span className="confidence-label" style={{ color: level.color }}>{level.label}</span>}
      {showPercentage && (
        <span className="confidence-percentage" style={{ color: level.color }}>
          {formatConfidence(confidence)}
        </span>
      )}
    </span>
  );
};

