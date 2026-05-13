/**
 * @aimos/igodn - Core Type Definitions
 * 
 * Intent Graviton Organic Dynamic Network - Physics engine for intent-space
 */

// ============================================================================
// Node Types
// ============================================================================

export type NodeType = 
  | 'CONTRACT'      // PLIx contract
  | 'INTENT'        // Candidate intent from CIF
  | 'CONCEPT'       // CMC/HHNI concept
  | 'INCIDENT'      // Past failure/violation
  | 'METRIC'        // System metric
  | 'ANCHOR';       // Core principle/singularity

export type ClusterId = 
  | 'SAFETY'        // Anchors + strong safety contracts
  | 'PERFORMANCE'   // Metrics, optimization contracts
  | 'EXPERIMENTAL'  // New intents, untested contracts
  | 'LEGACY'        // Old, deprecated contracts
  | 'DEFAULT';      // Everything else

// ============================================================================
// Position & Geometry
// ============================================================================

/**
 * Dual Quaternion Pose - Quaternion-native position in intent space
 * Enables SO(3)-invariant distance and screw-motion intent trajectories
 */
export interface DualQuatPose {
  rotation: Quaternion;      // Rotation quaternion (q)
  translation: Vector3D;      // Translation vector (t)
  dual: Quaternion;          // Dual part (for dual quaternion)
}

export interface Quaternion {
  w: number;
  x: number;
  y: number;
  z: number;
}

export interface Vector3D {
  x: number;
  y: number;
  z: number;
}

/**
 * Hopf Fiber - S¹ fiber for phase coherence
 * Phase-locked intents attract harder (VORTEX-LENS integration)
 */
export interface HopfFiber {
  phase: number;    // S¹ angle (0 to 2π)
  radius: number;   // Fiber radius
}

// ============================================================================
// Distance Decomposition
// ============================================================================

/**
 * Distance Decomposition - Explicit separation of physics and semantic distance
 * 
 * CRITICAL REFINEMENT: Separate physics distance from meta distance
 * - spatial: Used for physics forces (gravity, repulsion, bonds)
 * - combined: Used for semantic decisions (near contracts?, new doctrine?)
 */
export interface DistanceDecomposition {
  spatial: number;    // Raw position distance (for physics forces)
  semantic: number;  // Embedding/HHNI similarity
  policy: number;    // Constraint compatibility
  temporal: number;  // Recency
  combined: number;  // Weighted sum (for semantic decisions)
}

// ============================================================================
// Node Metadata
// ============================================================================

export interface NodeMetadata {
  // Contract nodes
  contract_id?: string;
  contract_kind?: 'Goal' | 'Process' | 'Constraint' | 'Invariant';
  contract_scope?: {
    systems: string[];
    components: string[];
  };
  
  // Intent nodes
  intent_id?: string;
  intent_priority?: number;
  intent_authority?: number;
  
  // Concept nodes
  concept_id?: string;
  embedding?: number[];  // Semantic embedding vector
  
  // Incident nodes
  incident_id?: string;
  incident_severity?: number;
  incident_timestamp?: string;
  
  // Metric nodes
  metric_id?: string;
  metric_value?: number;
  metric_trend?: 'increasing' | 'decreasing' | 'stable';
  
  // Common
  timestamp: string;
  usage_count?: number;
  last_used?: string;
  
  // RTFT fields (κ–λ–ρ)
  kappa_compression?: number;   // κ - compression depth (modulates mass)
  lambda_curvature?: number;     // λ - curvature (modulates perimeter)
  rho_density?: number;         // ρ - density (influences cluster G)
}

// ============================================================================
// IGODN Node
// ============================================================================

/**
 * IGODN Node - Represents a contract, intent, concept, incident, metric, or anchor
 * in the intent field
 */
export interface IGODNNode {
  id: string;
  type: NodeType;
  cluster: ClusterId;              // CRITICAL REFINEMENT: Explicit cluster assignment
  position: DualQuatPose;         // Position in intent space (quaternion-native)
  velocity: Vector3D;             // Current velocity
  mass: number;                   // Dynamic mass (includes Hopf phase coherence)
  perimeter_radius: number;       // Repulsive barrier radius (torsional vortex radius)
  bond_distance?: number;         // Equilibrium bond distance (for holding forces)
  hopf_fiber?: HopfFiber;         // S¹ fiber for phase coherence (optional)
  metadata: NodeMetadata;
}

// ============================================================================
// Field Parameters
// ============================================================================

export interface ClusterParameters {
  G_multiplier: number;           // Gravitational constant multiplier
  k_barrier_multiplier: number;   // Repulsive barrier multiplier
  k_hold_multiplier: number;      // Holding force multiplier
  c_damp_multiplier: number;      // Damping multiplier
}

export interface FieldParameters {
  // Force parameters
  G: number;                      // Gravitational constant (default: 1.0)
  k_barrier: number;               // Repulsive barrier strength (default: 10.0)
  k_hold: number;                 // Holding force strength (default: 5.0)
  c_damp: number;                 // Damping coefficient (default: 0.1)
  
  // Cluster-specific parameters
  cluster_params: Map<ClusterId, ClusterParameters>;
  
  // Distance weights (for combined distance)
  distance_weights: {
    spatial: number;    // Default: 0.30
    semantic: number;   // Default: 0.40
    policy: number;    // Default: 0.20
    temporal: number;  // Default: 0.10
  };
  
  // Mass calculation
  mass_weights: {
    authority: number;           // Default: 0.30
    priority: number;           // Default: 0.25
    entanglement: number;       // Default: 0.20
    historical_support: number; // Default: 0.15
    inverse_risk: number;       // Default: 0.10
  };
  
  // Type multipliers
  type_multipliers: Map<NodeType, number>;
  
  // Hopf phase
  enable_hopf_phase: boolean;     // Default: true
  hopf_phase_coherence_weight: number;  // Default: 0.3
  
  // VIF witness
  enable_vif_witness: boolean;   // Default: true
  vif_energy_threshold: number;  // Default: 1e-8
  
  // Simulation
  dt: number;                     // Time step (default: 0.01)
  max_iterations: number;        // Maximum iterations (default: 1000)
  convergence_threshold: number; // Energy delta threshold (default: 1e-8)
}

// ============================================================================
// Field State
// ============================================================================

export interface FieldState {
  iteration: number;
  total_energy: number;
  previous_energy: number;
  energy_delta: number;
  converged: boolean;
  convergence_reason?: string;
  new_nodes?: IGODNNode[];       // Track new nodes for this update
}

// ============================================================================
// IGODN Field
// ============================================================================

/**
 * IGODN Field - The complete intent field with all nodes and state
 * 
 * CRITICAL REFINEMENT: Field is long-lived, not per-utterance reset
 */
export interface IGODNField {
  nodes: Map<string, IGODNNode>;
  parameters: FieldParameters;
  state: FieldState;
}

// ============================================================================
// Matrix Interfaces (for compatibility, conflict, constitutional links)
// ============================================================================

export interface CompatibilityMatrix {
  are_compatible(node1: IGODNNode, node2: IGODNNode): boolean;
  get_compatibility_score(node1: IGODNNode, node2: IGODNNode): number;
}

export interface ConflictMatrix {
  are_conflicting(node1: IGODNNode, node2: IGODNNode): boolean;
  get_conflict_score(node1: IGODNNode, node2: IGODNNode): number;
}

export interface ConstitutionalLinkMatrix {
  are_linked(node1: IGODNNode, node2: IGODNNode): boolean;
  get_link_strength(node1: IGODNNode, node2: IGODNNode): number;
}

// ============================================================================
// Simulation Options
// ============================================================================

export interface SimulationOptions {
  max_iterations?: number;
  convergence_threshold?: number;
  incremental?: boolean;          // Only refine new nodes + nearby affected nodes
  dt?: number;
}

// ============================================================================
// Field Invariants
// ============================================================================

export interface FieldInvariants {
  min_anchor_mass: number;        // Default: 1.0
  energy_monotone: boolean;       // Default: true
  max_spatial_step: number;        // Default: 1.0
  conflict_log_threshold: number;  // Default: 10.0
}

export interface InvariantValidation {
  valid: boolean;
  violations: string[];
}

