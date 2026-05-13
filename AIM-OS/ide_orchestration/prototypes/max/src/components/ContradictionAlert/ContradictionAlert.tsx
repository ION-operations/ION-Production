// Contradiction Alert Component - Max V2
// Compact alert for displaying contradiction count

import React from 'react';
import { AlertTriangle } from 'lucide-react';
import './ContradictionAlert.css';

export interface ContradictionAlertProps {
  count: number;
  onClick?: () => void;
  severity?: 'high' | 'medium' | 'low';
  className?: string;
}

export const ContradictionAlert: React.FC<ContradictionAlertProps> = ({
  count,
  onClick,
  severity,
  className = '',
}) => {
  if (count === 0) return null;

  const getSeverityColor = () => {
    if (severity === 'high') return '#f87171'; // red
    if (severity === 'medium') return '#fbbf24'; // yellow
    return '#60a5fa'; // blue
  };

  const color = severity ? getSeverityColor() : '#fbbf24'; // Default yellow

  return (
    <div
      className={`contradiction-alert ${onClick ? 'contradiction-alert-clickable' : ''} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : 'status'}
      aria-label={`${count} contradiction${count !== 1 ? 's' : ''} detected`}
      title={`${count} contradiction${count !== 1 ? 's' : ''} detected`}
      style={{ color }}
    >
      <AlertTriangle className="contradiction-alert-icon" />
      <span className="contradiction-alert-count">{count}</span>
    </div>
  );
};

