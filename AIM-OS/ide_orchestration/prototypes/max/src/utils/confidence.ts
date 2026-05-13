// Confidence Indicator Utilities - Max V2
// Shared utilities for VIF confidence indicators

export type ConfidenceBand = 'high' | 'medium' | 'low' | 'unknown';

export interface ConfidenceLevel {
  value: number; // 0-1 confidence score
  band: ConfidenceBand;
  color: string;
  label: string;
  threshold: number; // Minimum threshold for this band
}

/**
 * Calculate confidence band from confidence value
 */
export const calculateConfidenceBand = (confidence: number | null | undefined): ConfidenceBand => {
  if (confidence === null || confidence === undefined) return 'unknown';
  if (confidence >= 0.90) return 'high';
  if (confidence >= 0.70) return 'medium';
  return 'low';
};

/**
 * Get confidence level details
 */
export const getConfidenceLevel = (confidence: number | null | undefined): ConfidenceLevel => {
  const band = calculateConfidenceBand(confidence);
  
  switch (band) {
    case 'high':
      return {
        value: confidence || 0,
        band: 'high',
        color: '#4ade80', // green
        label: 'High',
        threshold: 0.90,
      };
    case 'medium':
      return {
        value: confidence || 0,
        band: 'medium',
        color: '#fbbf24', // yellow
        label: 'Medium',
        threshold: 0.70,
      };
    case 'low':
      return {
        value: confidence || 0,
        band: 'low',
        color: '#f87171', // red
        label: 'Low',
        threshold: 0.0,
      };
    case 'unknown':
      return {
        value: 0,
        band: 'unknown',
        color: '#858585', // gray
        label: 'Unknown',
        threshold: 0.0,
      };
  }
};

/**
 * Format confidence as percentage
 */
export const formatConfidence = (confidence: number | null | undefined): string => {
  if (confidence === null || confidence === undefined) return 'N/A';
  return `${(confidence * 100).toFixed(0)}%`;
};

/**
 * Get confidence color
 */
export const getConfidenceColor = (confidence: number | null | undefined): string => {
  return getConfidenceLevel(confidence).color;
};

/**
 * Get confidence label
 */
export const getConfidenceLabel = (confidence: number | null | undefined): string => {
  return getConfidenceLevel(confidence).label;
};

/**
 * Check if confidence meets threshold
 */
export const meetsConfidenceThreshold = (
  confidence: number | null | undefined,
  threshold: number = 0.70
): boolean => {
  if (confidence === null || confidence === undefined) return false;
  return confidence >= threshold;
};

/**
 * Get confidence status (pass/warn/fail)
 */
export const getConfidenceStatus = (
  confidence: number | null | undefined,
  threshold: number = 0.70
): 'pass' | 'warn' | 'fail' => {
  if (confidence === null || confidence === undefined) return 'fail';
  if (confidence >= threshold) return 'pass';
  if (confidence >= threshold * 0.8) return 'warn'; // Within 20% of threshold
  return 'fail';
};

/**
 * Get confidence icon emoji
 */
export const getConfidenceIcon = (confidence: number | null | undefined): string => {
  const band = calculateConfidenceBand(confidence);
  switch (band) {
    case 'high':
      return '🟢';
    case 'medium':
      return '🟡';
    case 'low':
      return '🔴';
    case 'unknown':
      return '⚪';
  }
};

/**
 * Get confidence description
 */
export const getConfidenceDescription = (confidence: number | null | undefined): string => {
  const band = calculateConfidenceBand(confidence);
  switch (band) {
    case 'high':
      return 'High confidence - Ready for production';
    case 'medium':
      return 'Medium confidence - Review recommended';
    case 'low':
      return 'Low confidence - Requires investigation';
    case 'unknown':
      return 'Confidence unknown';
  }
};

