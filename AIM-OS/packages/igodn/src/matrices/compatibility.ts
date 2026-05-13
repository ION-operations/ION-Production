/**
 * Compatibility Matrix Implementation
 * 
 * Determines if two nodes are compatible (should attract)
 */

import { IGODNNode, CompatibilityMatrix } from '../types';

/**
 * Default compatibility matrix
 * 
 * Nodes are compatible if:
 * - Same type and cluster
 * - Contract nodes with overlapping scopes
 * - Intent nodes compatible with contract nodes
 */
export class DefaultCompatibilityMatrix implements CompatibilityMatrix {
  are_compatible(node1: IGODNNode, node2: IGODNNode): boolean {
    // Same node
    if (node1.id === node2.id) return false;
    
    // Anchors are compatible with everything
    if (node1.type === 'ANCHOR' || node2.type === 'ANCHOR') {
      return true;
    }
    
    // Same cluster = compatible
    if (node1.cluster === node2.cluster) {
      return true;
    }
    
    // Contract nodes: compatible if scopes overlap
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      return this.contracts_compatible(node1, node2);
    }
    
    // Intent nodes: compatible with contracts in same cluster
    if (node1.type === 'INTENT' && node2.type === 'CONTRACT') {
      return node1.cluster === node2.cluster || node2.cluster === 'SAFETY';
    }
    if (node1.type === 'CONTRACT' && node2.type === 'INTENT') {
      return node1.cluster === node2.cluster || node1.cluster === 'SAFETY';
    }
    
    // Concepts: compatible with related nodes
    if (node1.type === 'CONCEPT' || node2.type === 'CONCEPT') {
      return true; // Concepts are generally compatible
    }
    
    // Default: not compatible
    return false;
  }
  
  get_compatibility_score(node1: IGODNNode, node2: IGODNNode): number {
    if (!this.are_compatible(node1, node2)) {
      return 0.0;
    }
    
    // Base score
    let score = 0.5;
    
    // Same cluster increases score
    if (node1.cluster === node2.cluster) {
      score += 0.3;
    }
    
    // Same type increases score
    if (node1.type === node2.type) {
      score += 0.2;
    }
    
    // Contract scope overlap increases score
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      const overlap = this.compute_scope_overlap(node1, node2);
      score += overlap * 0.3;
    }
    
    return Math.min(score, 1.0);
  }
  
  private contracts_compatible(node1: IGODNNode, node2: IGODNNode): boolean {
    const scope1 = node1.metadata.contract_scope;
    const scope2 = node2.metadata.contract_scope;
    
    if (!scope1 || !scope2) {
      // No scope = compatible by default
      return true;
    }
    
    // Check if scopes overlap
    const systems1 = new Set(scope1.systems || []);
    const systems2 = new Set(scope2.systems || []);
    const intersection = new Set([...systems1].filter(s => systems2.has(s)));
    
    return intersection.size > 0;
  }
  
  private compute_scope_overlap(node1: IGODNNode, node2: IGODNNode): number {
    const scope1 = node1.metadata.contract_scope;
    const scope2 = node2.metadata.contract_scope;
    
    if (!scope1 || !scope2) {
      return 0.0;
    }
    
    const systems1 = new Set(scope1.systems || []);
    const systems2 = new Set(scope2.systems || []);
    const intersection = new Set([...systems1].filter(s => systems2.has(s)));
    const union = new Set([...systems1, ...systems2]);
    
    if (union.size === 0) return 0.0;
    
    return intersection.size / union.size; // Jaccard similarity
  }
}

