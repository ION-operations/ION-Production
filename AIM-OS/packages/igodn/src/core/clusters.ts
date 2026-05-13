/**
 * Cluster inference and management
 * 
 * CRITICAL REFINEMENT: Explicit clusters (not magical)
 */

import { IGODNNode, ClusterId } from '../types';

/**
 * Deterministic cluster inference
 * 
 * Maps node types and metadata to explicit clusters
 */
export function infer_cluster(node: IGODNNode): ClusterId {
  if (node.type === 'ANCHOR') return 'SAFETY';
  if (node.type === 'CONTRACT' && 
      node.metadata.contract_kind === 'Constraint') return 'SAFETY';
  if (node.type === 'INCIDENT') return 'SAFETY';
  if (node.type === 'METRIC') return 'PERFORMANCE';
  if (node.type === 'INTENT') return 'EXPERIMENTAL';
  if (node.metadata.contract_kind === 'Invariant') return 'SAFETY';
  
  return 'DEFAULT';
}

/**
 * Default cluster parameters
 */
export function get_default_cluster_params(): Map<ClusterId, {
  G_multiplier: number;
  k_barrier_multiplier: number;
  k_hold_multiplier: number;
  c_damp_multiplier: number;
}> {
  const params = new Map<ClusterId, {
    G_multiplier: number;
    k_barrier_multiplier: number;
    k_hold_multiplier: number;
    c_damp_multiplier: number;
  }>();
  
  params.set('SAFETY', {
    G_multiplier: 1.5,        // Stronger gravity
    k_barrier_multiplier: 2.0, // Very stiff barriers
    k_hold_multiplier: 2.0,    // Strong bonds
    c_damp_multiplier: 1.5     // More damping
  });
  
  params.set('PERFORMANCE', {
    G_multiplier: 1.0,
    k_barrier_multiplier: 1.0,
    k_hold_multiplier: 1.0,
    c_damp_multiplier: 1.0
  });
  
  params.set('EXPERIMENTAL', {
    G_multiplier: 0.8,        // Weaker gravity
    k_barrier_multiplier: 0.5, // Softer barriers
    k_hold_multiplier: 0.5,    // Weak bonds
    c_damp_multiplier: 0.8     // Less damping (more motion)
  });
  
  params.set('LEGACY', {
    G_multiplier: 0.6,        // Weak gravity
    k_barrier_multiplier: 1.0,
    k_hold_multiplier: 0.3,    // Weak bonds
    c_damp_multiplier: 2.0     // High decay
  });
  
  params.set('DEFAULT', {
    G_multiplier: 1.0,
    k_barrier_multiplier: 1.0,
    k_hold_multiplier: 1.0,
    c_damp_multiplier: 1.0
  });
  
  return params;
}

