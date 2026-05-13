// Contradiction Display Component - Max V2
// Full display component for showing contradiction details

import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronRight, CheckCircle, XCircle, Clock } from 'lucide-react';
import { SEGContradiction, getContradictionTypeLabel, getContradictionSeverityColor, getContradictionTypeIcon, calculateContradictionSeverity, formatContradiction } from '../../utils/contradiction';
import './ContradictionDisplay.css';

export interface ContradictionDisplayProps {
  contradiction: SEGContradiction;
  compact?: boolean;
  onResolve?: (contradiction: SEGContradiction) => void;
  onEntityClick?: (entityId: string) => void;
  className?: string;
}

export const ContradictionDisplay: React.FC<ContradictionDisplayProps> = ({
  contradiction,
  compact = false,
  onResolve,
  onEntityClick,
  className = '',
}) => {
  const [expanded, setExpanded] = useState(!compact);
  const severity = calculateContradictionSeverity(contradiction.confidence);
  const severityColor = getContradictionSeverityColor(severity);
  const typeIcon = getContradictionTypeIcon(contradiction.contradiction_type);
  const typeLabel = getContradictionTypeLabel(contradiction.contradiction_type);

  if (compact) {
    return (
      <div className={`contradiction-display contradiction-compact ${className}`}>
        <div className="contradiction-compact-header" onClick={() => setExpanded(!expanded)}>
          {expanded ? (
            <ChevronDown className="expand-icon" />
          ) : (
            <ChevronRight className="expand-icon" />
          )}
          <AlertTriangle className="contradiction-icon" style={{ color: severityColor }} />
          <span className="contradiction-compact-text">{formatContradiction(contradiction)}</span>
        </div>
        {expanded && (
          <div className="contradiction-compact-content">
            <div className="contradiction-explanation">{contradiction.explanation}</div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`contradiction-display contradiction-full ${contradiction.resolved ? 'contradiction-resolved' : ''} ${className}`}
      role="group"
      aria-label={`Contradiction: ${typeLabel}`}
    >
      <div className="contradiction-header" onClick={() => setExpanded(!expanded)}>
        <div className="contradiction-header-left">
          {expanded ? (
            <ChevronDown className="expand-icon" />
          ) : (
            <ChevronRight className="expand-icon" />
          )}
          <AlertTriangle className="contradiction-icon" style={{ color: severityColor }} />
          <div className="contradiction-info">
            <div className="contradiction-type">
              <span className="contradiction-type-icon">{typeIcon}</span>
              <span className="contradiction-type-label">{typeLabel}</span>
            </div>
            <div className="contradiction-meta">
              {contradiction.resolved ? (
                <span className="contradiction-status contradiction-status-resolved">
                  <CheckCircle className="status-icon" />
                  Resolved
                </span>
              ) : (
                <span className="contradiction-status contradiction-status-unresolved">
                  <XCircle className="status-icon" />
                  Unresolved
                </span>
              )}
              <span className="contradiction-severity" style={{ color: severityColor }}>
                {severity} severity
              </span>
              <span className="contradiction-confidence">
                {(contradiction.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>
          </div>
        </div>
        <div className="contradiction-header-right">
          {!contradiction.resolved && onResolve && (
            <button
              className="contradiction-resolve-button"
              onClick={(e) => {
                e.stopPropagation();
                onResolve(contradiction);
              }}
              aria-label="Resolve contradiction"
            >
              Resolve
            </button>
          )}
        </div>
      </div>

      {expanded && (
        <div className="contradiction-content">
          {/* Entities */}
          <div className="contradiction-section">
            <div className="contradiction-section-header">Conflicting Entities</div>
            <div className="contradiction-entities">
              <div
                className="contradiction-entity"
                onClick={() => onEntityClick?.(contradiction.entity1_id)}
                role={onEntityClick ? 'button' : undefined}
                tabIndex={onEntityClick ? 0 : undefined}
              >
                <span className="contradiction-entity-label">Entity 1:</span>
                <span className="contradiction-entity-id">{contradiction.entity1_id}</span>
              </div>
              <div className="contradiction-arrow">↔</div>
              <div
                className="contradiction-entity"
                onClick={() => onEntityClick?.(contradiction.entity2_id)}
                role={onEntityClick ? 'button' : undefined}
                tabIndex={onEntityClick ? 0 : undefined}
              >
                <span className="contradiction-entity-label">Entity 2:</span>
                <span className="contradiction-entity-id">{contradiction.entity2_id}</span>
              </div>
            </div>
          </div>

          {/* Explanation */}
          <div className="contradiction-section">
            <div className="contradiction-section-header">Explanation</div>
            <div className="contradiction-explanation">{contradiction.explanation}</div>
          </div>

          {/* Metrics */}
          <div className="contradiction-section">
            <div className="contradiction-section-header">Metrics</div>
            <div className="contradiction-metrics">
              <div className="contradiction-metric">
                <span className="contradiction-metric-label">Similarity:</span>
                <span className="contradiction-metric-value">{(contradiction.similarity * 100).toFixed(0)}%</span>
              </div>
              <div className="contradiction-metric">
                <span className="contradiction-metric-label">Confidence:</span>
                <span className="contradiction-metric-value">{(contradiction.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          {/* Resolution */}
          {contradiction.resolved && contradiction.resolution && (
            <div className="contradiction-section">
              <div className="contradiction-section-header">Resolution</div>
              <div className="contradiction-resolution">{contradiction.resolution}</div>
              {contradiction.resolved_at && (
                <div className="contradiction-resolved-at">
                  <Clock className="resolved-icon" />
                  <span>Resolved {new Date(contradiction.resolved_at).toLocaleString()}</span>
                </div>
              )}
            </div>
          )}

          {/* Tags */}
          {contradiction.tags.length > 0 && (
            <div className="contradiction-section">
              <div className="contradiction-section-header">Tags</div>
              <div className="contradiction-tags">
                {contradiction.tags.map((tag, index) => (
                  <span key={index} className="contradiction-tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="contradiction-section">
            <div className="contradiction-section-header">Timestamps</div>
            <div className="contradiction-timestamps">
              <div className="contradiction-timestamp">
                <span className="contradiction-timestamp-label">Detected:</span>
                <span className="contradiction-timestamp-value">
                  {new Date(contradiction.detected_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

