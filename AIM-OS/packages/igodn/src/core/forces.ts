/**
 * Force calculations
 * 
 * Implements gravitational, repulsive, holding, and damping forces
 * with all critical refinements applied
 */

import { IGODNNode, IGODNField, Vector3D, CompatibilityMatrix, ConflictMatrix, ConstitutionalLinkMatrix } from '../types';
import { compute_distance_decomposed } from './distance';
import { dual_quat_to_position } from '../utils/quaternions';
import { vector_add, vector_scale, vector_subtract, vector_normalize } from '../utils/vectors';

/**
 * Compute gravitational force (attraction between compatible nodes)
 * 
 * Uses spatial distance for physics forces
 */
export function compute_gravitational_force(
  node1: IGODNNode,
  node2: IGODNNode,
  field: IGODNField,
  compatibility: CompatibilityMatrix
): Vector3D {
  // Only attract if compatible
  if (!compatibility.are_compatible(node1, node2)) {
    return { x: 0, y: 0, z: 0 };
  }
  
  // Get cluster-specific G
  const cluster = node1.cluster;
  const cluster_params = field.parameters.cluster_params.get(cluster);
  const G_effective = field.parameters.G * (cluster_params?.G_multiplier || 1.0);
  
  // CRITICAL REFINEMENT: Use spatial distance for physics forces
  const dist = compute_distance_decomposed(node1, node2, undefined, field.parameters.distance_weights);
  if (dist.spatial < 1e-10) return { x: 0, y: 0, z: 0 };  // Avoid division by zero
  
  const force_magnitude = G_effective * node1.mass * node2.mass / (dist.spatial * dist.spatial);
  
  // Direction from dual quaternion positions
  const pos1_3d = dual_quat_to_position(node1.position);
  const pos2_3d = dual_quat_to_position(node2.position);
  const direction = vector_normalize(vector_subtract(pos2_3d, pos1_3d));
  
  return vector_scale(direction, force_magnitude);
}

/**
 * Compute repulsive force (conflict between incompatible nodes)
 * 
 * Uses spatial distance for perimeter checks
 */
export function compute_repulsive_force(
  node1: IGODNNode,
  node2: IGODNNode,
  field: IGODNField,
  conflict: ConflictMatrix
): Vector3D {
  // Only repel if conflicting
  if (!conflict.are_conflicting(node1, node2)) {
    return { x: 0, y: 0, z: 0 };
  }
  
  // Get cluster-specific k_barrier
  const cluster = node1.cluster;
  const cluster_params = field.parameters.cluster_params.get(cluster);
  const k_barrier_effective = field.parameters.k_barrier * (cluster_params?.k_barrier_multiplier || 1.0);
  
  // CRITICAL REFINEMENT: Use spatial distance for perimeter checks
  const dist = compute_distance_decomposed(node1, node2, undefined, field.parameters.distance_weights);
  const d_perimeter = node1.perimeter_radius + node2.perimeter_radius;
  
  if (dist.spatial >= d_perimeter) {
    return { x: 0, y: 0, z: 0 };  // No repulsion if beyond perimeter
  }
  
  const force_magnitude = k_barrier_effective * (d_perimeter - dist.spatial);
  
  // Direction from dual quaternion positions
  const pos1_3d = dual_quat_to_position(node1.position);
  const pos2_3d = dual_quat_to_position(node2.position);
  const direction = vector_normalize(vector_subtract(pos1_3d, pos2_3d));
  
  return vector_scale(direction, force_magnitude);
}

/**
 * Compute holding force (constitutional bonds)
 * 
 * Uses spatial + semantic distance
 */
export function compute_holding_force(
  node1: IGODNNode,
  node2: IGODNNode,
  field: IGODNField,
  constitutional: ConstitutionalLinkMatrix
): Vector3D {
  // Only hold if constitutionally linked
  if (!constitutional.are_linked(node1, node2)) {
    return { x: 0, y: 0, z: 0 };
  }
  
  // Get cluster-specific k_hold
  const cluster = node1.cluster;
  const cluster_params = field.parameters.cluster_params.get(cluster);
  const k_hold_effective = field.parameters.k_hold * (cluster_params?.k_hold_multiplier || 1.0);
  
  // Get link strength
  const link_strength = constitutional.get_link_strength(node1, node2);
  
  // Use spatial distance for physics
  const dist = compute_distance_decomposed(node1, node2, undefined, field.parameters.distance_weights);
  const bond_distance = node1.bond_distance || node2.bond_distance || 1.0;
  
  // Spring-like force toward equilibrium bond distance
  const displacement = dist.spatial - bond_distance;
  const force_magnitude = -k_hold_effective * link_strength * displacement;
  
  // Direction from dual quaternion positions
  const pos1_3d = dual_quat_to_position(node1.position);
  const pos2_3d = dual_quat_to_position(node2.position);
  const direction = vector_normalize(vector_subtract(pos2_3d, pos1_3d));
  
  return vector_scale(direction, force_magnitude);
}

/**
 * Compute net force on a node
 * 
 * CRITICAL REFINEMENT: Per-node damping (not pairwise)
 * Damping opposes node's own velocity, preventing center-of-mass drift
 */
export function compute_net_force(
  node: IGODNNode,
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix
): Vector3D {
  let net_force: Vector3D = { x: 0, y: 0, z: 0 };
  
  // Sum forces from all other nodes
  for (const other_node of field.nodes.values()) {
    if (other_node.id === node.id) continue;
    
    // Gravitational (attraction)
    const F_gravity = compute_gravitational_force(
      node, other_node, field, compatibility
    );
    net_force = vector_add(net_force, F_gravity);
    
    // Repulsive (conflict)
    const F_repulse = compute_repulsive_force(
      node, other_node, field, conflict
    );
    net_force = vector_add(net_force, F_repulse);
    
    // Holding (constitutional)
    const F_hold = compute_holding_force(
      node, other_node, field, constitutional
    );
    net_force = vector_add(net_force, F_hold);
  }
  
  // CRITICAL REFINEMENT: Per-node damping (not pairwise)
  // Damping opposes node's own velocity, preventing center-of-mass drift
  const cluster = node.cluster;
  const cluster_params = field.parameters.cluster_params.get(cluster);
  const c_damp_effective = field.parameters.c_damp * (cluster_params?.c_damp_multiplier || 1.0);
  
  const F_damp = vector_scale(node.velocity, -c_damp_effective);
  net_force = vector_add(net_force, F_damp);
  
  return net_force;
}

