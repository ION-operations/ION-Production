/**
 * CIF to IGODN Converter
 * 
 * Converts CIF utterances to IGODN nodes
 * 
 * TODO: Implement full conversion logic
 * TODO: Integrate with real CIF package
 * TODO: Add HHNI integration for semantic positioning
 */

import { IGODNNode } from '../types';
import { infer_cluster } from '../core/clusters';
import { CIFUtterance, CIFPhrase, CIFToIGODNOptions } from './cif_types';

/**
 * Convert CIF utterance to IGODN nodes
 * 
 * Phase 3 Task: Implement full conversion
 */
export class CIFToIGODNConverter {
  /**
   * Convert CIF utterance to IGODN nodes
   */
  convert_cif_to_nodes(
    utterance: CIFUtterance,
    options: CIFToIGODNOptions = {}
  ): IGODNNode[] {
    const nodes: IGODNNode[] = [];
    
    // Extract intent nodes from phrases
    for (const phrase of utterance.phrases) {
      if (phrase.intent) {
        const node = this.phrase_to_node(phrase, utterance, options);
        nodes.push(node);
      }
    }
    
    return nodes;
  }
  
  /**
   * Convert phrase to IGODN node
   */
  private phrase_to_node(
    phrase: CIFPhrase,
    utterance: CIFUtterance,
    options: CIFToIGODNOptions
  ): IGODNNode {
    // Compute authority from speaker role
    const authority = this.compute_authority(utterance.speakerRole);
    
    // Compute priority from phrase
    const priority = phrase.priority || 0.5;
    
    // Compute entanglement (how many systems/concepts touched)
    const entanglement = this.compute_entanglement(phrase, utterance);
    
    // Initial position (placeholder - will use HHNI in Phase 3)
    const position = this.compute_initial_position(phrase, utterance, options);
    
    // Create node
    const node: IGODNNode = {
      id: `intent-${phrase.phraseId}`,
      type: 'INTENT',
      cluster: 'DEFAULT', // Will be inferred
      position,
      velocity: { x: 0, y: 0, z: 0 },
      mass: options.default_mass || 1.0,
      perimeter_radius: options.default_radius || 0.5,
      metadata: {
        timestamp: utterance.timestamp,
        intent_id: phrase.phraseId,
        intent_authority: authority,
        intent_priority: priority,
        usage_count: 0
      }
    };
    
    // Infer cluster
    node.cluster = infer_cluster(node);
    
    return node;
  }
  
  /**
   * Compute authority from speaker role
   */
  private compute_authority(role: string): number {
    const role_authority: Record<string, number> = {
      'architect': 0.97,
      'core_developer': 0.85,
      'agent': 0.70,
      'observer': 0.50
    };
    return role_authority[role] || 0.50;
  }
  
  /**
   * Compute entanglement (how many systems/concepts touched)
   */
  private compute_entanglement(phrase: CIFPhrase, utterance: CIFUtterance): number {
    if (!utterance.alignments) return 0.0;
    
    const alignments = utterance.alignments.filter(a => a.phraseId === phrase.phraseId);
    return Math.min(alignments.length / 10.0, 1.0);
  }
  
  /**
   * Compute initial position
   * 
   * TODO: Use HHNI for semantic positioning
   * TODO: Use anchor-based positioning
   */
  private compute_initial_position(
    phrase: CIFPhrase,
    utterance: CIFUtterance,
    options: CIFToIGODNOptions
  ): IGODNNode['position'] {
    // Placeholder: random position
    // Phase 3: Use HHNI for semantic positioning
    // Phase 3: Use anchor-based positioning
    
    const strategy = options.initial_position_strategy || 'random';
    
    if (strategy === 'random') {
      return {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: {
          x: (Math.random() - 0.5) * 10,
          y: (Math.random() - 0.5) * 10,
          z: (Math.random() - 0.5) * 10
        },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      };
    }
    
    // Default: origin
    return {
      rotation: { w: 1, x: 0, y: 0, z: 0 },
      translation: { x: 0, y: 0, z: 0 },
      dual: { w: 0, x: 0, y: 0, z: 0 }
    };
  }
  
  /**
   * Place nodes in existing field
   * 
   * TODO: Use HHNI for semantic positioning relative to existing nodes
   */
  place_nodes_in_field(
    nodes: IGODNNode[],
    field: IGODNField,
    hhni?: any  // HHNIClient when available
  ): void {
    // For now, just add nodes to field
    // Phase 3: Use HHNI to position nodes semantically relative to existing nodes
    
    for (const node of nodes) {
      field.nodes.set(node.id, node);
    }
    
    // Track as new nodes
    if (!field.state.new_nodes) {
      field.state.new_nodes = [];
    }
    field.state.new_nodes.push(...nodes);
  }
}

