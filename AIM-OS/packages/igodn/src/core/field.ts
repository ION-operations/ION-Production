/**
 * Field initialization and management
 * 
 * CRITICAL REFINEMENT: Persistent field (long-lived, not per-utterance reset)
 */

import { 
  IGODNField, 
  IGODNNode, 
  FieldParameters, 
  FieldState,
  ClusterId
} from '../types';
import { infer_cluster, get_default_cluster_params } from './clusters';

/**
 * Default field parameters
 */
export function get_default_field_parameters(): FieldParameters {
  return {
    // Force parameters
    G: 1.0,
    k_barrier: 10.0,
    k_hold: 5.0,
    c_damp: 0.1,
    
    // Cluster-specific parameters
    cluster_params: get_default_cluster_params(),
    
    // Distance weights
    distance_weights: {
      spatial: 0.30,
      semantic: 0.40,
      policy: 0.20,
      temporal: 0.10
    },
    
    // Mass calculation weights
    mass_weights: {
      authority: 0.30,
      priority: 0.25,
      entanglement: 0.20,
      historical_support: 0.15,
      inverse_risk: 0.10
    },
    
    // Type multipliers
    type_multipliers: new Map([
      ['ANCHOR', 2.0],
      ['CONTRACT', 1.5],
      ['INTENT', 1.0],
      ['CONCEPT', 0.8],
      ['INCIDENT', 1.2],
      ['METRIC', 0.9]
    ]),
    
    // Hopf phase
    enable_hopf_phase: true,
    hopf_phase_coherence_weight: 0.3,
    
    // VIF witness
    enable_vif_witness: true,
    vif_energy_threshold: 1e-8,
    
    // Simulation
    dt: 0.01,
    max_iterations: 1000,
    convergence_threshold: 1e-8
  };
}

/**
 * Create initial field state
 */
export function create_initial_field_state(): FieldState {
  return {
    iteration: 0,
    total_energy: 0,
    previous_energy: 0,
    energy_delta: Infinity,
    converged: false,
    new_nodes: []
  };
}

/**
 * Create a new IGODN field
 */
export function create_igodn_field(
  nodes: IGODNNode[] = [],
  parameters?: Partial<FieldParameters>
): IGODNField {
  const field_params = get_default_field_parameters();
  if (parameters) {
    Object.assign(field_params, parameters);
  }
  
  // Assign clusters to nodes
  for (const node of nodes) {
    if (!node.cluster) {
      node.cluster = infer_cluster(node);
    }
  }
  
  // Create nodes map
  const nodes_map = new Map<string, IGODNNode>();
  for (const node of nodes) {
    nodes_map.set(node.id, node);
  }
  
  return {
    nodes: nodes_map,
    parameters: field_params,
    state: create_initial_field_state()
  };
}

/**
 * Add node to field
 */
export function add_node_to_field(
  field: IGODNField,
  node: IGODNNode
): void {
  // Assign cluster if not set
  if (!node.cluster) {
    node.cluster = infer_cluster(node);
  }
  
  field.nodes.set(node.id, node);
  
  // Track as new node
  if (!field.state.new_nodes) {
    field.state.new_nodes = [];
  }
  field.state.new_nodes.push(node);
}

/**
 * Remove node from field
 */
export function remove_node_from_field(
  field: IGODNField,
  node_id: string
): boolean {
  return field.nodes.delete(node_id);
}

/**
 * Get node from field
 */
export function get_node_from_field(
  field: IGODNField,
  node_id: string
): IGODNNode | undefined {
  return field.nodes.get(node_id);
}

/**
 * Create default anchor nodes
 */
export function create_default_anchors(): IGODNNode[] {
  const anchors: IGODNNode[] = [];
  
  const anchor_types: Array<{ id: string; name: string }> = [
    { id: 'SAFETY', name: 'Safety' },
    { id: 'HONESTY', name: 'Honesty' },
    { id: 'NON_CORRUPTION', name: 'Non-Corruption' },
    { id: 'CHARTER', name: 'Charter' }
  ];
  
  for (const anchor of anchor_types) {
    anchors.push({
      id: anchor.id,
      type: 'ANCHOR',
      cluster: 'SAFETY',
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 0, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 10.0,
      perimeter_radius: 1.0,
      metadata: {
        timestamp: new Date().toISOString(),
        intent_authority: 0.9,
        intent_priority: 1.0
      }
    });
  }
  
  return anchors;
}

