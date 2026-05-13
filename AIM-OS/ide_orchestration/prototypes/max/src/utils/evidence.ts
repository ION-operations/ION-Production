// Evidence Trail Utilities - Max V2
// Shared utilities for evidence trails and provenance chains

export type EvidenceStrength = 'strong' | 'medium' | 'weak';

export interface EvidenceLink {
  id: string;
  type: 'cmc_atom' | 'seg_node' | 'vif_witness' | 'source';
  reference: string; // Atom ID, node ID, witness ID, or source reference
  confidence?: number; // 0-1 confidence score
  strength?: EvidenceStrength; // Calculated from confidence
  description?: string; // Human-readable description
  timestamp?: string; // When evidence was created
}

export interface EvidenceTrail {
  id: string;
  action: string; // What action this evidence supports
  evidence: EvidenceLink[]; // List of evidence links
  confidence: number; // Overall confidence (0-1)
  strength: EvidenceStrength; // Overall strength
  provenance_chain?: string[]; // Chain of evidence IDs showing derivation
  created_at: string; // ISO timestamp
}

/**
 * Calculate evidence strength from confidence
 */
export const calculateEvidenceStrength = (confidence: number): EvidenceStrength => {
  if (confidence >= 0.80) return 'strong';
  if (confidence >= 0.60) return 'medium';
  return 'weak';
};

/**
 * Calculate overall confidence from evidence links
 */
export const calculateOverallConfidence = (evidence: EvidenceLink[]): number => {
  if (evidence.length === 0) return 0;
  
  const confidences = evidence
    .map(e => e.confidence || 0)
    .filter(c => c > 0);
  
  if (confidences.length === 0) return 0;
  
  // Weighted average (stronger evidence weighted more)
  const weights = confidences.map(c => {
    const strength = calculateEvidenceStrength(c);
    return strength === 'strong' ? 3 : strength === 'medium' ? 2 : 1;
  });
  
  const totalWeight = weights.reduce((sum, w) => sum + w, 0);
  const weightedSum = confidences.reduce((sum, c, i) => sum + c * weights[i], 0);
  
  return weightedSum / totalWeight;
};

/**
 * Create evidence link from CMC atom
 */
export const createCMCAtomLink = (
  atomId: string,
  confidence?: number,
  description?: string
): EvidenceLink => {
  return {
    id: `cmc_${atomId}`,
    type: 'cmc_atom',
    reference: atomId,
    confidence,
    strength: confidence ? calculateEvidenceStrength(confidence) : undefined,
    description,
  };
};

/**
 * Create evidence link from SEG node
 */
export const createSEGNodeLink = (
  nodeId: string,
  confidence?: number,
  description?: string
): EvidenceLink => {
  return {
    id: `seg_${nodeId}`,
    type: 'seg_node',
    reference: nodeId,
    confidence,
    strength: confidence ? calculateEvidenceStrength(confidence) : undefined,
    description,
  };
};

/**
 * Create evidence link from VIF witness
 */
export const createVIFWitnessLink = (
  witnessId: string,
  confidence?: number,
  description?: string
): EvidenceLink => {
  return {
    id: `vif_${witnessId}`,
    type: 'vif_witness',
    reference: witnessId,
    confidence,
    strength: confidence ? calculateEvidenceStrength(confidence) : undefined,
    description,
  };
};

/**
 * Create evidence trail
 */
export const createEvidenceTrail = (
  action: string,
  evidence: EvidenceLink[],
  provenance_chain?: string[]
): EvidenceTrail => {
  const confidence = calculateOverallConfidence(evidence);
  const strength = calculateEvidenceStrength(confidence);
  
  return {
    id: `trail_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    action,
    evidence,
    confidence,
    strength,
    provenance_chain,
    created_at: new Date().toISOString(),
  };
};

/**
 * Format evidence strength for display
 */
export const formatEvidenceStrength = (strength: EvidenceStrength): string => {
  switch (strength) {
    case 'strong':
      return 'Strong';
    case 'medium':
      return 'Medium';
    case 'weak':
      return 'Weak';
    default:
      return 'Unknown';
  }
};

/**
 * Get evidence strength color
 */
export const getEvidenceStrengthColor = (strength: EvidenceStrength): string => {
  switch (strength) {
    case 'strong':
      return '#4ade80'; // green
    case 'medium':
      return '#fbbf24'; // yellow
    case 'weak':
      return '#f87171'; // red
    default:
      return '#858585'; // gray
  }
};

/**
 * Build provenance chain from evidence links
 */
export const buildProvenanceChain = (evidence: EvidenceLink[]): string[] => {
  return evidence.map(e => e.id);
};

/**
 * Filter evidence by strength
 */
export const filterEvidenceByStrength = (
  evidence: EvidenceLink[],
  strength: EvidenceStrength
): EvidenceLink[] => {
  return evidence.filter(e => e.strength === strength);
};

/**
 * Sort evidence by confidence (highest first)
 */
export const sortEvidenceByConfidence = (evidence: EvidenceLink[]): EvidenceLink[] => {
  return [...evidence].sort((a, b) => {
    const aConf = a.confidence || 0;
    const bConf = b.confidence || 0;
    return bConf - aConf;
  });
};

