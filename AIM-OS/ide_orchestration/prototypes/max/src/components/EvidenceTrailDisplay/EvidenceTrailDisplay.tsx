// Evidence Trail Display Component - Max V2
// Reusable component for displaying evidence trails and provenance chains

import React, { useState } from 'react';
import { Link, ChevronDown, ChevronRight, ExternalLink, Shield, FileText, Database, CheckCircle } from 'lucide-react';
import { EvidenceTrail, EvidenceLink, formatEvidenceStrength, getEvidenceStrengthColor } from '../../utils/evidence';
import './EvidenceTrailDisplay.css';

export interface EvidenceTrailDisplayProps {
  trail: EvidenceTrail;
  compact?: boolean;
  showProvenance?: boolean;
  onEvidenceClick?: (evidence: EvidenceLink) => void;
  className?: string;
}

export const EvidenceTrailDisplay: React.FC<EvidenceTrailDisplayProps> = ({
  trail,
  compact = false,
  showProvenance = true,
  onEvidenceClick,
  className = '',
}) => {
  const [expanded, setExpanded] = useState(!compact);

  const getEvidenceIcon = (type: EvidenceLink['type']) => {
    switch (type) {
      case 'cmc_atom':
        return <Database className="evidence-icon" />;
      case 'seg_node':
        return <FileText className="evidence-icon" />;
      case 'vif_witness':
        return <Shield className="evidence-icon" />;
      case 'source':
        return <ExternalLink className="evidence-icon" />;
      default:
        return <Link className="evidence-icon" />;
    }
  };

  const getEvidenceTypeLabel = (type: EvidenceLink['type']) => {
    switch (type) {
      case 'cmc_atom':
        return 'CMC Atom';
      case 'seg_node':
        return 'SEG Node';
      case 'vif_witness':
        return 'VIF Witness';
      case 'source':
        return 'Source';
      default:
        return 'Evidence';
    }
  };

  if (compact) {
    return (
      <div className={`evidence-trail evidence-trail-compact ${className}`}>
        <div className="evidence-trail-header-compact" onClick={() => setExpanded(!expanded)}>
          {expanded ? (
            <ChevronDown className="expand-icon" />
          ) : (
            <ChevronRight className="expand-icon" />
          )}
          <span className="evidence-trail-action">{trail.action}</span>
          <span
            className="evidence-strength-badge"
            style={{ backgroundColor: getEvidenceStrengthColor(trail.strength) + '20', color: getEvidenceStrengthColor(trail.strength) }}
          >
            {formatEvidenceStrength(trail.strength)}
          </span>
          <span className="evidence-confidence">
            {(trail.confidence * 100).toFixed(0)}%
          </span>
        </div>
        {expanded && (
          <div className="evidence-trail-content-compact">
            <div className="evidence-count">{trail.evidence.length} evidence items</div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`evidence-trail ${className}`} role="group" aria-label="Evidence trail">
      <div className="evidence-trail-header" onClick={() => setExpanded(!expanded)}>
        <div className="evidence-trail-header-left">
          {expanded ? (
            <ChevronDown className="expand-icon" />
          ) : (
            <ChevronRight className="expand-icon" />
          )}
          <CheckCircle className="evidence-trail-icon" />
          <div className="evidence-trail-info">
            <div className="evidence-trail-action">{trail.action}</div>
            <div className="evidence-trail-meta">
              {trail.evidence.length} evidence items • Created {new Date(trail.created_at).toLocaleString()}
            </div>
          </div>
        </div>
        <div className="evidence-trail-header-right">
          <span
            className="evidence-strength-badge"
            style={{ backgroundColor: getEvidenceStrengthColor(trail.strength) + '20', color: getEvidenceStrengthColor(trail.strength) }}
          >
            {formatEvidenceStrength(trail.strength)}
          </span>
          <span className="evidence-confidence">
            {(trail.confidence * 100).toFixed(0)}% confidence
          </span>
        </div>
      </div>

      {expanded && (
        <div className="evidence-trail-content">
          {/* Evidence Links */}
          <div className="evidence-links">
            <div className="evidence-links-header">Evidence Links</div>
            {trail.evidence.length === 0 ? (
              <div className="evidence-empty">No evidence available</div>
            ) : (
              trail.evidence.map((evidence, index) => (
                <div
                  key={evidence.id}
                  className="evidence-link-item"
                  onClick={() => onEvidenceClick?.(evidence)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onEvidenceClick?.(evidence);
                    }
                  }}
                >
                  <div className="evidence-link-left">
                    {getEvidenceIcon(evidence.type)}
                    <div className="evidence-link-info">
                      <div className="evidence-link-type">{getEvidenceTypeLabel(evidence.type)}</div>
                      <div className="evidence-link-reference">{evidence.reference}</div>
                      {evidence.description && (
                        <div className="evidence-link-description">{evidence.description}</div>
                      )}
                    </div>
                  </div>
                  <div className="evidence-link-right">
                    {evidence.confidence !== undefined && (
                      <span className="evidence-link-confidence">
                        {(evidence.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                    {evidence.strength && (
                      <span
                        className="evidence-link-strength"
                        style={{ color: getEvidenceStrengthColor(evidence.strength) }}
                      >
                        {formatEvidenceStrength(evidence.strength)}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Provenance Chain */}
          {showProvenance && trail.provenance_chain && trail.provenance_chain.length > 0 && (
            <div className="evidence-provenance">
              <div className="evidence-provenance-header">Provenance Chain</div>
              <div className="evidence-provenance-chain">
                {trail.provenance_chain.map((id, index) => (
                  <React.Fragment key={id}>
                    <span className="provenance-link">{id}</span>
                    {index < trail.provenance_chain!.length - 1 && (
                      <span className="provenance-arrow">→</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

