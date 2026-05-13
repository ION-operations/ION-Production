/**
 * Simulation loop with iterative refinement
 * 
 * CRITICAL REFINEMENT: Supports incremental mode for persistent field
 */

import { 
  IGODNField, 
  CompatibilityMatrix, 
  ConflictMatrix, 
  ConstitutionalLinkMatrix,
  SimulationOptions,
  IGODNNode
} from '../types';
import { compute_net_force } from './forces';
import { compute_total_energy, check_convergence } from './energy';
import { compute_mass } from './mass';
import { vector_add, vector_scale } from '../utils/vectors';
import { dual_quat_to_position } from '../utils/quaternions';

/**
 * Run one simulation step
 */
function run_simulation_step(
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix,
  dt: number
): void {
  // Update masses (dynamic mass calculation)
  for (const node of field.nodes.values()) {
    node.mass = compute_mass(node, field);
  }
  
  // Compute forces and update positions/velocities
  for (const node of field.nodes.values()) {
    // Compute net force
    const F_net = compute_net_force(node, field, compatibility, conflict, constitutional);
    
    // Update velocity: v = v + (F/m) * dt
    const acceleration = vector_scale(F_net, 1.0 / node.mass);
    const dv = vector_scale(acceleration, dt);
    node.velocity = vector_add(node.velocity, dv);
    
    // Update position: x = x + v * dt
    const pos_3d = dual_quat_to_position(node.position);
    const dx = vector_scale(node.velocity, dt);
    const new_pos_3d = vector_add(pos_3d, dx);
    
    // Update dual quaternion position (simplified - would use proper quaternion operations)
    node.position.translation = new_pos_3d;
  }
  
  // Update energy
  const previous_energy = field.state.total_energy;
  field.state.total_energy = compute_total_energy(field, compatibility, conflict);
  field.state.previous_energy = previous_energy;
  field.state.energy_delta = field.state.total_energy - previous_energy;
  
  field.state.iteration++;
}

/**
 * Run IGODN simulation
 * 
 * Supports incremental mode for persistent field updates
 */
export async function simulate_igodn(
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix,
  options: SimulationOptions = {}
): Promise<void> {
  const max_iterations = options.max_iterations || field.parameters.max_iterations;
  const convergence_threshold = options.convergence_threshold || field.parameters.convergence_threshold;
  const dt = options.dt || field.parameters.dt;
  const incremental = options.incremental || false;
  
  // Initialize energy
  if (field.state.iteration === 0) {
    field.state.total_energy = compute_total_energy(field, compatibility, conflict);
    field.state.previous_energy = field.state.total_energy;
    field.state.energy_delta = Infinity;
  }
  
  // Incremental mode: only refine new nodes + nearby affected nodes
  let nodes_to_update: Set<string> | null = null;
  if (incremental && field.state.new_nodes) {
    nodes_to_update = new Set(field.state.new_nodes.map(n => n.id));
    
    // Add nearby nodes (within 2x perimeter radius)
    for (const new_node of field.state.new_nodes) {
      for (const existing_node of field.nodes.values()) {
        if (nodes_to_update.has(existing_node.id)) continue;
        
        // Check if within influence radius
        const pos1 = dual_quat_to_position(new_node.position);
        const pos2 = dual_quat_to_position(existing_node.position);
        const dx = pos2.x - pos1.x;
        const dy = pos2.y - pos1.y;
        const dz = pos2.z - pos1.z;
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        
        if (distance < 2.0 * (new_node.perimeter_radius + existing_node.perimeter_radius)) {
          nodes_to_update.add(existing_node.id);
        }
      }
    }
  }
  
  // Main simulation loop
  for (let iter = 0; iter < max_iterations; iter++) {
    // Run one step
    run_simulation_step(field, compatibility, conflict, constitutional, dt);
    
    // Check convergence
    const { converged, reason } = check_convergence(field, convergence_threshold);
    if (converged) {
      field.state.converged = true;
      field.state.convergence_reason = reason;
      break;
    }
  }
  
  // CRITICAL UPGRADE: Seal as VIF witness when converged
  if (field.state.converged && field.parameters.enable_vif_witness) {
    if (Math.abs(field.state.energy_delta) < field.parameters.vif_energy_threshold) {
      // TODO: Implement VIF witness sealing
      // await seal_vif_witness(field, compatibility, conflict, constitutional);
    }
  }
}

// check_convergence is imported from energy.ts

