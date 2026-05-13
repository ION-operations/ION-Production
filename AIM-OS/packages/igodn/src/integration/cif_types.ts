/**
 * CIF Integration Types
 * 
 * Types for converting CIF utterances to IGODN nodes
 * 
 * TODO: Integrate with actual CIF package when available
 */

/**
 * CIF Utterance (placeholder - will use real CIF types when available)
 */
export interface CIFUtterance {
  id: string;
  timestamp: string;
  speaker: string;
  speakerRole: 'architect' | 'core_developer' | 'agent' | 'observer';
  content: string;
  phrases: CIFPhrase[];
  alignments?: CIFAlignment[];
}

/**
 * CIF Phrase (placeholder)
 */
export interface CIFPhrase {
  phraseId: string;
  text: string;
  intent?: string;
  priority?: number;
  authority?: number;
}

/**
 * CIF Alignment (placeholder)
 */
export interface CIFAlignment {
  phraseId: string;
  conceptId?: string;
  systemId?: string;
  componentId?: string;
  confidence: number;
}

/**
 * Conversion options
 */
export interface CIFToIGODNOptions {
  default_mass?: number;
  default_radius?: number;
  initial_position_strategy?: 'random' | 'semantic' | 'anchor_based';
  use_hhni?: boolean;  // Use HHNI for semantic positioning
}

