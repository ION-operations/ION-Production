/**
 * Constitutional Link Matrix Implementation
 * 
 * Determines if two nodes are constitutionally linked (should have holding bonds)
 */

import { IGODNNode, ConstitutionalLinkMatrix } from '../types';

/**
 * Default constitutional link matrix
 * 
 * Nodes are linked if:
 * - Parent-child contract relationships
 * - Anchor to contract relationships
 * - Concept to contract relationships
 */
export class DefaultConstitutionalLinkMatrix implements ConstitutionalLinkMatrix {
  are_linked(node1: IGODNNode, node2: IGODNNode): boolean {
    // Same node
    if (node1.id === node2.id) return false;
    
    // Anchor to contract links
    if (node1.type === 'ANCHOR' && node2.type === 'CONTRACT') {
      return node2.cluster === 'SAFETY' || node1.id === 'CHARTER';
    }
    if (node2.type === 'ANCHOR' && node1.type === 'CONTRACT') {
      return node1.cluster === 'SAFETY' || node2.id === 'CHARTER';
    }
    
    // Contract parent-child relationships
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      return this.contracts_linked(node1, node2);
    }
    
    // Concept to contract links
    if (node1.type === 'CONCEPT' && node2.type === 'CONTRACT') {
      return this.concept_linked_to_contract(node1, node2);
    }
    if (node2.type === 'CONCEPT' && node1.type === 'CONTRACT') {
      return this.concept_linked_to_contract(node2, node1);
    }
    
    // Default: not linked
    return false;
  }
  
  get_link_strength(node1: IGODNNode, node2: IGODNNode): number {
    if (!this.are_linked(node1, node2)) {
      return 0.0;
    }
    
    // Base link strength
    let strength = 0.5;
    
    // Anchor links are stronger
    if (node1.type === 'ANCHOR' || node2.type === 'ANCHOR') {
      strength = 0.9;
    }
    
    // Same cluster increases strength
    if (node1.cluster === node2.cluster) {
      strength += 0.2;
    }
    
    // Contract parent-child relationships
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      const scope_overlap = this.compute_scope_overlap(node1, node2);
      strength += scope_overlap * 0.3;
    }
    
    return Math.min(strength, 1.0);
  }
  
  private contracts_linked(node1: IGODNNode, node2: IGODNNode): boolean {
    // Contracts are linked if one is a child of the other
    // This would be determined by PLIx contract hierarchy
    // For now, use scope containment as heuristic
    
    const scope1 = node1.metadata.contract_scope;
    const scope2 = node2.metadata.contract_scope;
    
    if (!scope1 || !scope2) {
      return false;
    }
    
    const systems1 = new Set(scope1.systems || []);
    const systems2 = new Set(scope2.systems || []);
    
    // Check if one scope contains the other (parent-child relationship)
    const intersection = new Set([...systems1].filter(s => systems2.has(s)));
    const is_subset1 = intersection.size === systems1.size && systems1.size < systems2.size;
    const is_subset2 = intersection.size === systems2.size && systems2.size < systems1.size;
    
    return is_subset1 || is_subset2;
  }
  
  private concept_linked_to_contract(concept: IGODNNode, contract: IGODNNode): boolean {
    // Concepts are linked to contracts if they share semantic similarity
    // This would use HHNI for actual semantic checking
    // For now, use concept_id matching
    
    const concept_id = concept.metadata.concept_id;
    const contract_scope = contract.metadata.contract_scope;
    
    if (!concept_id || !contract_scope) {
      return false;
    }
    
    // Simple heuristic: if concept is mentioned in contract scope
    // TODO: Use HHNI for actual semantic checking
    return false;
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

