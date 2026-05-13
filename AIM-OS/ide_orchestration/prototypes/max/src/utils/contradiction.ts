// Contradiction Detection Utilities - Max V2
// Shared utilities for SEG contradiction detection

export type ContradictionType = 'logical_conflict' | 'semantic_conflict' | 'temporal_conflict' | 'factual_conflict' | 'unknown';

export type ContradictionSeverity = 'high' | 'medium' | 'low';

export interface SEGContradiction {
  id: string; // "contradiction_{uuid}"
  entity1_id: string; // First conflicting entity
  entity2_id: string; // Second conflicting entity
  contradiction_type: ContradictionType;
  similarity: number; // 0-1 semantic similarity
  confidence: number; // 0-1 confidence in contradiction detection
  explanation: string; // Human-readable explanation
  resolved: boolean; // Whether contradiction has been resolved
  resolution?: string; // Resolution description if resolved
  resolved_at?: string; // ISO timestamp when resolved
  detected_at: string; // ISO timestamp when detected
  tags: string[]; // Tags for categorization
}

export interface ContradictionSummary {
  total: number;
  unresolved: number;
  resolved: number;
  byType: Record<ContradictionType, number>;
  bySeverity: Record<ContradictionSeverity, number>;
}

/**
 * Calculate contradiction severity from confidence
 */
export const calculateContradictionSeverity = (confidence: number): ContradictionSeverity => {
  if (confidence >= 0.80) return 'high';
  if (confidence >= 0.60) return 'medium';
  return 'low';
};

/**
 * Get contradiction type label
 */
export const getContradictionTypeLabel = (type: ContradictionType): string => {
  switch (type) {
    case 'logical_conflict':
      return 'Logical Conflict';
    case 'semantic_conflict':
      return 'Semantic Conflict';
    case 'temporal_conflict':
      return 'Temporal Conflict';
    case 'factual_conflict':
      return 'Factual Conflict';
    case 'unknown':
      return 'Unknown';
  }
};

/**
 * Get contradiction severity color
 */
export const getContradictionSeverityColor = (severity: ContradictionSeverity): string => {
  switch (severity) {
    case 'high':
      return '#f87171'; // red
    case 'medium':
      return '#fbbf24'; // yellow
    case 'low':
      return '#60a5fa'; // blue
  }
};

/**
 * Get contradiction type icon
 */
export const getContradictionTypeIcon = (type: ContradictionType): string => {
  switch (type) {
    case 'logical_conflict':
      return '⚡';
    case 'semantic_conflict':
      return '🔀';
    case 'temporal_conflict':
      return '⏰';
    case 'factual_conflict':
      return '❌';
    case 'unknown':
      return '❓';
  }
};

/**
 * Calculate contradiction summary
 */
export const calculateContradictionSummary = (contradictions: SEGContradiction[]): ContradictionSummary => {
  const summary: ContradictionSummary = {
    total: contradictions.length,
    unresolved: contradictions.filter(c => !c.resolved).length,
    resolved: contradictions.filter(c => c.resolved).length,
    byType: {
      logical_conflict: 0,
      semantic_conflict: 0,
      temporal_conflict: 0,
      factual_conflict: 0,
      unknown: 0,
    },
    bySeverity: {
      high: 0,
      medium: 0,
      low: 0,
    },
  };

  contradictions.forEach(contradiction => {
    summary.byType[contradiction.contradiction_type]++;
    const severity = calculateContradictionSeverity(contradiction.confidence);
    summary.bySeverity[severity]++;
  });

  return summary;
};

/**
 * Filter contradictions by type
 */
export const filterContradictionsByType = (
  contradictions: SEGContradiction[],
  type: ContradictionType
): SEGContradiction[] => {
  return contradictions.filter(c => c.contradiction_type === type);
};

/**
 * Filter contradictions by severity
 */
export const filterContradictionsBySeverity = (
  contradictions: SEGContradiction[],
  severity: ContradictionSeverity
): SEGContradiction[] => {
  return contradictions.filter(c => calculateContradictionSeverity(c.confidence) === severity);
};

/**
 * Filter unresolved contradictions
 */
export const filterUnresolvedContradictions = (contradictions: SEGContradiction[]): SEGContradiction[] => {
  return contradictions.filter(c => !c.resolved);
};

/**
 * Sort contradictions by confidence (highest first)
 */
export const sortContradictionsByConfidence = (contradictions: SEGContradiction[]): SEGContradiction[] => {
  return [...contradictions].sort((a, b) => b.confidence - a.confidence);
};

/**
 * Format contradiction for display
 */
export const formatContradiction = (contradiction: SEGContradiction): string => {
  const typeLabel = getContradictionTypeLabel(contradiction.contradiction_type);
  const severity = calculateContradictionSeverity(contradiction.confidence);
  return `${typeLabel} (${severity} severity, ${(contradiction.confidence * 100).toFixed(0)}% confidence)`;
};

