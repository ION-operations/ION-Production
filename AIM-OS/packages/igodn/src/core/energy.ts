/**
 * Energy calculation and minimization
 * 
 * Total energy = gravitational potential + repulsive potential + kinetic
 */

import { IGODNField, CompatibilityMatrix, ConflictMatrix } from '../types';
import { compute_distance_decomposed } from './distance';
import { vector_magnitude } from '../utils/vectors';

/**
 * Compute total energy of the field
 * 
 * E_total = E_gravity + E_repulse + E_kinetic
 */
export function compute_total_energy(
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix
): number {
  let E_gravity = 0.0;
  let E_repulse = 0.0;
  let E_kinetic = 0.0;
  
  const nodes = Array.from(field.nodes.values());
  
  // Compute gravitational potential energy
  for (let i = 0; i < nodes.length; i++) {
    const node1 = nodes[i];
    
    for (let j = i + 1; j < nodes.length; j++) {
      const node2 = nodes[j];
      
      // Gravitational energy (if compatible)
      if (compatibility.are_compatible(node1, node2)) {
        const cluster = node1.cluster;
        const cluster_params = field.parameters.cluster_params.get(cluster);
        const G_effective = field.parameters.G * (cluster_params?.G_multiplier || 1.0);
        
        const dist = compute_distance_decomposed(
          node1, 
          node2, 
          undefined, 
          field.parameters.distance_weights
        );
        
        if (dist.spatial > 1e-10) {
          E_gravity -= G_effective * node1.mass * node2.mass / dist.spatial;
        }
      }
      
      // Repulsive energy (if conflicting)
      if (conflict.are_conflicting(node1, node2)) {
        const cluster = node1.cluster;
        const cluster_params = field.parameters.cluster_params.get(cluster);
        const k_barrier_effective = field.parameters.k_barrier * (cluster_params?.k_barrier_multiplier || 1.0);
        
        const dist = compute_distance_decomposed(
          node1, 
          node2, 
          undefined, 
          field.parameters.distance_weights
        );
        const d_perimeter = node1.perimeter_radius + node2.perimeter_radius;
        
        if (dist.spatial < d_perimeter) {
          const compression = d_perimeter - dist.spatial;
          E_repulse += 0.5 * k_barrier_effective * compression * compression;
        }
      }
    }
    
    // Kinetic energy
    const v_mag = vector_magnitude(node1.velocity);
    E_kinetic += 0.5 * node1.mass * v_mag * v_mag;
  }
  
  return E_gravity + E_repulse + E_kinetic;
}

/**
 * Check if field has converged
 */
export function check_convergence(
  field: IGODNField,
  threshold: number = 1e-8
): { converged: boolean; reason?: string } {
  const energy_delta = Math.abs(field.state.energy_delta);
  
  if (energy_delta < threshold) {
    return { converged: true, reason: 'energy_delta_below_threshold' };
  }
  
  // Check if all velocities are small
  let max_velocity = 0.0;
  for (const node of field.nodes.values()) {
    const v_mag = vector_magnitude(node.velocity);
    max_velocity = Math.max(max_velocity, v_mag);
  }
  
  if (max_velocity < 1e-6) {
    return { converged: true, reason: 'velocities_near_zero' };
  }
  
  return { converged: false };
}

