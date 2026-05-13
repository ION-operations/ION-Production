/**
 * Mass calculation with Hopf phase coherence
 * 
 * Mass formula: authority × priority × entanglement × historical_support × inverse_risk
 * with type multipliers, dynamic scaling, and Hopf phase coherence
 */

import { IGODNNode, IGODNField } from '../types';

/**
 * Compute phase coherence for Hopf fiber alignment
 * 
 * Phase-locked intents (same S¹ fiber) attract harder
 */
function compute_phase_coherence(
  node: IGODNNode,
  field: IGODNField
): number {
  if (!node.hopf_fiber) return 0.0;
  
  let max_coherence = 0.0;
  
  for (const other_node of field.nodes.values()) {
    if (other_node.id === node.id || !other_node.hopf_fiber) continue;
    
    // Phase difference in S¹ fiber
    const phase_diff = Math.abs(node.hopf_fiber.phase - other_node.hopf_fiber.phase);
    const normalized_diff = Math.min(phase_diff, 2 * Math.PI - phase_diff) / Math.PI;
    
    // Coherence = 1 - normalized phase difference
    const coherence = 1.0 - normalized_diff;
    max_coherence = Math.max(max_coherence, coherence);
  }
  
  return max_coherence;
}

/**
 * Compute dynamic mass for a node
 * 
 * Formula: base_mass × usage_multiplier × decay_multiplier × convergence_multiplier
 * 
 * Base mass = authority × priority × entanglement × historical_support × inverse_risk
 * with type multipliers and Hopf phase coherence
 */
export function compute_mass(
  node: IGODNNode,
  field: IGODNField
): number {
  const params = field.parameters;
  
  // Base components (from metadata)
  const authority = node.metadata.intent_authority || 
    (node.type === 'ANCHOR' ? 0.9 : 0.5);
  const priority = node.metadata.intent_priority || 0.5;
  const entanglement = node.metadata.usage_count ? 
    Math.min(node.metadata.usage_count / 10.0, 1.0) : 0.0;
  const historical_support = node.metadata.last_used ? 
    (Date.now() - new Date(node.metadata.last_used).getTime()) / (365 * 24 * 3600 * 1000) : 0.0;
  const risk = 1.0 - (node.metadata.incident_severity || 0.0);
  
  // Base mass calculation
  let base_mass = (
    authority * params.mass_weights.authority +
    priority * params.mass_weights.priority +
    entanglement * params.mass_weights.entanglement +
    Math.min(historical_support, 1.0) * params.mass_weights.historical_support +
    risk * params.mass_weights.inverse_risk
  );
  
  // Type multiplier
  const type_multiplier = params.type_multipliers.get(node.type) || 1.0;
  base_mass *= type_multiplier;
  
  // CRITICAL UPGRADE: Hopf fiber phase coherence
  if (params.enable_hopf_phase) {
    const phase_coherence = compute_phase_coherence(node, field);
    base_mass *= (1.0 + params.hopf_phase_coherence_weight * phase_coherence);
  }
  
  // RTFT kappa compression (if available)
  if (node.metadata.kappa_compression) {
    base_mass *= (1.0 + 0.2 * node.metadata.kappa_compression);
  }
  
  // Dynamic scaling
  // Increase mass for frequently used nodes
  const usage_count = node.metadata.usage_count || 0;
  const usage_multiplier = 1.0 + Math.min(usage_count / 100.0, 0.5);
  
  // Decrease mass for old nodes (decay)
  const age_days = (Date.now() - new Date(node.metadata.timestamp).getTime()) / (1000 * 60 * 60 * 24);
  const decay_multiplier = Math.exp(-age_days / 365);  // 1/e per year
  
  // Increase mass for nodes near convergence (focus)
  const convergence_multiplier = field.state.converged ? 1.2 : 1.0;
  
  return base_mass * usage_multiplier * decay_multiplier * convergence_multiplier;
}

