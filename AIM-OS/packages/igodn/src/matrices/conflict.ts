/**
 * Conflict Matrix Implementation
 * 
 * Determines if two nodes are conflicting (should repel)
 */

import { IGODNNode, ConflictMatrix } from '../types';

/**
 * Default conflict matrix
 * 
 * Nodes are conflicting if:
 * - Intent conflicts with safety constraints
 * - Contracts have contradictory constraints
 * - Incidents indicate violations
 */
export class DefaultConflictMatrix implements ConflictMatrix {
  are_conflicting(node1: IGODNNode, node2: IGODNNode): boolean {
    // Same node
    if (node1.id === node2.id) return false;
    
    // Anchors never conflict
    if (node1.type === 'ANCHOR' && node2.type === 'ANCHOR') {
      return false;
    }
    
    // Intent conflicting with SAFETY anchor/contract
    if (node1.type === 'INTENT' && node2.cluster === 'SAFETY') {
      // Check if intent would violate safety
      return this.intent_violates_safety(node1, node2);
    }
    if (node2.type === 'INTENT' && node1.cluster === 'SAFETY') {
      return this.intent_violates_safety(node2, node1);
    }
    
    // Contract conflicts: contradictory constraints
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      return this.contracts_conflict(node1, node2);
    }
    
    // Incidents conflict with related contracts
    if (node1.type === 'INCIDENT' && node2.type === 'CONTRACT') {
      return this.incident_relates_to_contract(node1, node2);
    }
    if (node2.type === 'INCIDENT' && node1.type === 'CONTRACT') {
      return this.incident_relates_to_contract(node2, node1);
    }
    
    // Default: not conflicting
    return false;
  }
  
  get_conflict_score(node1: IGODNNode, node2: IGODNNode): number {
    if (!this.are_conflicting(node1, node2)) {
      return 0.0;
    }
    
    // Base conflict score
    let score = 0.5;
    
    // Safety conflicts are more severe
    if (node1.cluster === 'SAFETY' || node2.cluster === 'SAFETY') {
      score += 0.3;
    }
    
    // Incident severity increases conflict
    if (node1.type === 'INCIDENT' || node2.type === 'INCIDENT') {
      const incident = node1.type === 'INCIDENT' ? node1 : node2;
      const severity = incident.metadata.incident_severity || 0.5;
      score += severity * 0.2;
    }
    
    return Math.min(score, 1.0);
  }
  
  private intent_violates_safety(intent: IGODNNode, safety_node: IGODNNode): boolean {
    // Simple heuristic: if intent has low authority and safety node has high mass
    // This would be enhanced with actual constraint checking
    if (intent.metadata.intent_authority && intent.metadata.intent_authority < 0.5) {
      if (safety_node.mass > 5.0) {
        return true; // Low authority intent conflicts with strong safety constraint
      }
    }
    
    // TODO: Add actual constraint violation checking
    return false;
  }
  
  private contracts_conflict(node1: IGODNNode, node2: IGODNNode): boolean {
    // Contracts conflict if they have contradictory kinds
    const kind1 = node1.metadata.contract_kind;
    const kind2 = node2.metadata.contract_kind;
    
    // Constraint vs Goal can conflict if scopes overlap
    if ((kind1 === 'Constraint' && kind2 === 'Goal') || 
        (kind1 === 'Goal' && kind2 === 'Constraint')) {
      const scope1 = node1.metadata.contract_scope;
      const scope2 = node2.metadata.contract_scope;
      
      if (scope1 && scope2) {
        const systems1 = new Set(scope1.systems || []);
        const systems2 = new Set(scope2.systems || []);
        const intersection = new Set([...systems1].filter(s => systems2.has(s)));
        
        // If scopes overlap, potential conflict
        return intersection.size > 0;
      }
    }
    
    return false;
  }
  
  private incident_relates_to_contract(incident: IGODNNode, contract: IGODNNode): boolean {
    // Simple heuristic: if incident and contract have related scopes
    // This would be enhanced with actual incident analysis
    const incident_id = incident.metadata.incident_id;
    const contract_id = contract.metadata.contract_id;
    
    // TODO: Add actual incident-contract relationship checking
    return false;
  }
}

