# IGODN: Intent GODN Technical Specification

**Date:** 2025-01-27  
**Author:** Aether (Technical Design)  
**Status:** 📐 **DESIGN PHASE** - Technical Specification  
**Related:** `GODN_INTEGRATION_RESEARCH.md`

---

## Executive Summary

This document provides the **technical specification** for **IGODN (Intent GODN)**, a custom operating mode of GODN repurposed as an intent-field engine for CIF/Stratum 3. It includes data structures, algorithms, APIs, and integration points.

---

## Table of Contents

1. [Data Structures](#1-data-structures)
2. [Core Algorithms](#2-core-algorithms)
3. [Force Calculations](#3-force-calculations)
4. [Energy Calculations](#4-energy-calculations)
5. [Iterative Refinement](#5-iterative-refinement)
6. [Integration APIs](#6-integration-apis)
7. [Performance Considerations](#7-performance-considerations)

---

## 1. Data Structures

### 1.1 Node Types

```typescript
// Base node interface
interface IGODNNode {
  id: string;
  type: NodeType;
  cluster: ClusterId;      // CRITICAL REFINEMENT: Explicit cluster assignment
  position: DualQuatPose;  // Position in intent space (quaternion-native)
  velocity: Vector3D;      // Current velocity
  mass: number;            // Dynamic mass (includes Hopf phase coherence)
  perimeter_radius: number;  // Repulsive barrier radius (torsional vortex radius)
  bond_distance?: number;    // Equilibrium bond distance (for holding forces)
  hopf_fiber?: HopfFiber;    // S¹ fiber for phase coherence (optional)
  metadata: NodeMetadata;
}

// CRITICAL REFINEMENT: Deterministic cluster inference
function infer_cluster(node: IGODNNode): ClusterId {
  if (node.type === 'ANCHOR') return 'SAFETY';
  if (node.type === 'CONTRACT' && 
      node.metadata.contract_kind === 'Constraint') return 'SAFETY';
  if (node.type === 'INCIDENT') return 'SAFETY';
  if (node.type === 'METRIC') return 'PERFORMANCE';
  if (node.type === 'INTENT') return 'EXPERIMENTAL';
  if (node.metadata.contract_kind === 'Invariant') return 'SAFETY';
  
  return 'DEFAULT';
}

type NodeType = 
  | 'CONTRACT'      // PLIx contract
  | 'INTENT'        // Candidate intent from CIF
  | 'CONCEPT'       // CMC/HHNI concept
  | 'INCIDENT'      // Past failure/violation
  | 'METRIC'        // System metric
  | 'ANCHOR';       // Core principle/singularity

// CRITICAL REFINEMENT: Explicit clusters (not magical)
type ClusterId = 
  | 'SAFETY'        // Anchors + strong safety contracts
  | 'PERFORMANCE'   // Metrics, optimization contracts
  | 'EXPERIMENTAL'  // New intents, untested contracts
  | 'LEGACY'        // Old, deprecated contracts
  | 'DEFAULT';      // Everything else

interface NodeMetadata {
  // Contract nodes
  contract_id?: string;
  contract_kind?: 'Goal' | 'Process' | 'Constraint' | 'Invariant';
  contract_scope?: { systems: string[]; modes: string[] };
  
  // Intent nodes
  cif_utterance_id?: string;
  candidate_intent_id?: string;
  roles?: string[];
  local_importance?: number;
  certainty?: number;
  
  // Concept nodes
  concept_id?: string;  // HHNI concept ID
  embedding?: number[];  // Semantic embedding
  
  // Incident nodes
  incident_id?: string;
  incident_type?: string;
  severity?: number;
  
  // Metric nodes
  metric_name?: string;
  metric_value?: number;
  
  // Anchor nodes
  anchor_type?: 'SAFETY' | 'HONESTY' | 'NON_CORRUPTION' | 'CHARTER';
  
  // Common
  authority: number;        // 0..1
  priority: number;         // 0..1
  entanglement: number;     // 0..1
  historical_support: number;  // 0..1
  risk: number;            // 0..1
  timestamp: string;       // ISO timestamp
  source_id?: string;      // Who/what created this
}

// Position in intent space (quaternion-native for SO(3)-invariant distance)
import { DualQuatPose } from '@aimos/quaternion-kernel';

// Velocity in intent space (still 3D vector for now, could be quaternion)
interface Vector3D {
  x: number;
  y: number;
  z: number;
}

// Helper functions for Vector3D
function vector_add(v1: Vector3D, v2: Vector3D): Vector3D {
  return { x: v1.x + v2.x, y: v1.y + v2.y, z: v1.z + v2.z };
}

function vector_subtract(v1: Vector3D, v2: Vector3D): Vector3D {
  return { x: v1.x - v2.x, y: v1.y - v2.y, z: v1.z - v2.z };
}

function vector_scale(v: Vector3D, s: number): Vector3D {
  return { x: v.x * s, y: v.y * s, z: v.z * s };
}

function vector_magnitude(v: Vector3D): number {
  return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

function vector_normalize(v: Vector3D): Vector3D {
  const mag = vector_magnitude(v);
  if (mag < 1e-10) return { x: 0, y: 0, z: 0 };
  return vector_scale(v, 1.0 / mag);
}

// Helper functions for DualQuatPose
function dual_quat_to_position(pose: DualQuatPose): Vector3D {
  // Extract translation from dual quaternion
  // This would use quaternion kernel functions
  return { x: pose.translation.x, y: pose.translation.y, z: pose.translation.z };
}

function get_hopf_fiber(pose: DualQuatPose): HopfFiber {
  // Extract S¹ fiber from dual quaternion
  // This would use quaternion kernel functions
  // For now, return placeholder
  return { phase: 0.0, radius: 1.0 };
}
```

### 1.2 Field Configuration

```typescript
interface IGODNField {
  nodes: Map<string, IGODNNode>;
  parameters: FieldParameters;
  state: FieldState;
}

interface FieldParameters {
  // Gravitational constant
  G: number;  // Default: 1.0
  
  // Elastic constants
  k_barrier: number;  // Repulsive barrier stiffness (Default: 10.0)
  k_hold: number;    // Holding bond stiffness (Default: 5.0)
  
  // Damping
  c_damp: number;     // Damping coefficient (Default: 0.1)
  
  // Convergence
  epsilon: number;    // Energy convergence threshold (Default: 1e-6)
  max_iterations: number;  // Max iterations (Default: 1000)
  
  // Dynamic adjustments
  enable_dynamic_time: boolean;  // Variable time speed
  enable_dynamic_mass: boolean;  // Variable mass scaling
  enable_hopf_phase: boolean;    // Hopf fiber phase coherence (Default: true)
  
  // VIF witness sealing
  enable_vif_witness: boolean;    // Seal converged states as VIF witnesses (Default: true)
  vif_energy_threshold: number;   // Energy delta threshold for VIF sealing (Default: 1e-8)
  
  // Cluster-specific parameters
  cluster_params: Map<string, ClusterParameters>;
}

interface ClusterParameters {
  G_multiplier: number;      // Gravity multiplier for cluster
  k_barrier_multiplier: number;  // Repulsion multiplier
  k_hold_multiplier: number;     // Holding multiplier
  c_damp_multiplier: number;     // Damping multiplier
}

interface FieldState {
  iteration: number;
  total_energy: number;
  previous_energy: number;
  energy_delta: number;
  converged: boolean;
  convergence_reason?: 'ENERGY_THRESHOLD' | 'MAX_ITERATIONS' | 'STABLE_POSITIONS';
}
```

### 1.3 Compatibility & Conflict Matrices

```typescript
interface CompatibilityMatrix {
  // Returns true if nodes are compatible (attract)
  are_compatible(node1: IGODNNode, node2: IGODNNode): boolean;
}

interface ConflictMatrix {
  // Returns true if nodes conflict (repel)
  are_conflicting(node1: IGODNNode, node2: IGODNNode): boolean;
}

interface ConstitutionalLinkMatrix {
  // Returns true if nodes are constitutionally linked (holding force)
  are_constitutionally_linked(node1: IGODNNode, node2: IGODNNode): boolean;
}

// Implementation examples
class SemanticCompatibilityMatrix implements CompatibilityMatrix {
  constructor(private hhni: HHNIClient) {}
  
  are_compatible(node1: IGODNNode, node2: IGODNNode): boolean {
    // Same type and similar scope
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      const scope1 = node1.metadata.contract_scope;
      const scope2 = node2.metadata.contract_scope;
      if (scope1 && scope2) {
        const system_overlap = scope1.systems.filter(s => 
          scope2.systems.includes(s)
        ).length;
        return system_overlap > 0;
      }
    }
    
    // Semantic similarity (via embeddings)
    if (node1.metadata.embedding && node2.metadata.embedding) {
      const similarity = cosine_similarity(
        node1.metadata.embedding,
        node2.metadata.embedding
      );
      return similarity > 0.7;  // Threshold
    }
    
    return false;
  }
}

class PolicyConflictMatrix implements ConflictMatrix {
  are_conflicting(node1: IGODNNode, node2: IGODNNode): boolean {
    // Contract vs Contract: incompatible constraints
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      return this.check_constraint_conflict(node1, node2);
    }
    
    // Intent vs Contract: intent violates contract
    if (node1.type === 'INTENT' && node2.type === 'CONTRACT') {
      return this.check_intent_violates_contract(node1, node2);
    }
    
    // Incident vs Contract: incident shows contract violation
    if (node1.type === 'INCIDENT' && node2.type === 'CONTRACT') {
      return node1.metadata.incident_type === 'CONTRACT_VIOLATION' &&
             node1.metadata.contract_id === node2.id;
    }
    
    return false;
  }
  
  private check_constraint_conflict(
    contract1: IGODNNode,
    contract2: IGODNNode
  ): boolean {
    // Check if constraints are incompatible
    // This would use PLIx constraint solver
    // Simplified: check scope overlap + incompatible conditions
    const scope1 = contract1.metadata.contract_scope;
    const scope2 = contract2.metadata.contract_scope;
    
    if (!scope1 || !scope2) return false;
    
    const system_overlap = scope1.systems.filter(s => 
      scope2.systems.includes(s)
    ).length;
    
    if (system_overlap === 0) return false;  // No overlap, no conflict
    
    // Would need PLIx constraint solver here
    // For now, assume conflict if same scope and different priorities
    return Math.abs(contract1.metadata.priority - contract2.metadata.priority) > 0.5;
  }
  
  private check_intent_violates_contract(
    intent: IGODNNode,
    contract: IGODNNode
  ): boolean {
    // Check if intent would violate contract constraints
    // This would use PLIx constraint checker
    // Simplified: check scope overlap + intent priority vs contract priority
    const intent_scope = intent.metadata.contract_scope;  // If intent has scope
    const contract_scope = contract.metadata.contract_scope;
    
    if (!intent_scope || !contract_scope) return false;
    
    const system_overlap = intent_scope.systems.filter(s => 
      contract_scope.systems.includes(s)
    ).length;
    
    if (system_overlap === 0) return false;
    
    // Would need PLIx constraint checker here
    // For now, assume violation if intent priority < contract priority
    return intent.metadata.priority < contract.metadata.priority;
  }
}

class InvariantLinkMatrix implements ConstitutionalLinkMatrix {
  are_constitutionally_linked(node1: IGODNNode, node2: IGODNNode): boolean {
    // Anchor to Contract: contract implements anchor principle
    if (node1.type === 'ANCHOR' && node2.type === 'CONTRACT') {
      return this.check_contract_implements_anchor(node1, node2);
    }
    
    // Contract to Contract: parent-child relationship
    if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
      return this.check_parent_child(node1, node2);
    }
    
    return false;
  }
  
  private check_contract_implements_anchor(
    anchor: IGODNNode,
    contract: IGODNNode
  ): boolean {
    // Check if contract implements anchor principle
    const anchor_type = anchor.metadata.anchor_type;
    const contract_kind = contract.metadata.contract_kind;
    
    if (anchor_type === 'SAFETY' && contract_kind === 'Constraint') {
      return true;  // Safety constraints implement safety anchor
    }
    
    // More sophisticated checking would use semantic analysis
    return false;
  }
  
  private check_parent_child(
    contract1: IGODNNode,
    contract2: IGODNNode
  ): boolean {
    // Check if contract1 is parent of contract2
    // This would use contract hierarchy from PCE
    // Simplified: check if contract2 extends contract1's scope
    const scope1 = contract1.metadata.contract_scope;
    const scope2 = contract2.metadata.contract_scope;
    
    if (!scope1 || !scope2) return false;
    
    // contract2 extends contract1 if scope2 is subset of scope1
    const systems_subset = scope2.systems.every(s => 
      scope1.systems.includes(s)
    );
    const modes_subset = scope2.modes.every(m => 
      scope1.modes.includes(m)
    );
    
    return systems_subset && modes_subset;
  }
}
```

---

## 2. Core Algorithms

### 2.1 Mass Calculation

```typescript
function compute_mass(node: IGODNNode, field: IGODNField): number {
  const metadata = node.metadata;
  
  // Base mass components
  const authority = metadata.authority;
  const priority = metadata.priority;
  const entanglement = metadata.entanglement;
  const historical_support = metadata.historical_support;
  const risk = metadata.risk;
  const risk_level = 1.0 - risk;  // Inverse risk
  
  // Weighted combination
  let base_mass = (
    authority * 0.30 +
    priority * 0.25 +
    entanglement * 0.20 +
    historical_support * 0.15 +
    risk_level * 0.10
  );
  
  // Type-specific multipliers
  const type_multipliers: Record<NodeType, number> = {
    'ANCHOR': 2.0,      // Anchors are very heavy
    'CONTRACT': 1.5,   // Contracts are heavy
    'CONCEPT': 1.0,    // Concepts are normal
    'INTENT': 0.8,     // Intents are lighter (candidates)
    'INCIDENT': 0.6,   // Incidents are lighter
    'METRIC': 0.5      // Metrics are lightest
  };
  
  base_mass *= type_multipliers[node.type] || 1.0;
  
  // CRITICAL UPGRADE: Hopf fiber phase coherence
  if (field.parameters.enable_hopf_phase && node.hopf_fiber) {
    const phase_coherence = compute_phase_coherence(node, field);
    base_mass *= (1.0 + 0.3 * phase_coherence);  // Phase-locked intents weigh more
  }
  
  // Dynamic mass scaling (if enabled)
  if (field.parameters.enable_dynamic_mass) {
    base_mass = apply_dynamic_mass_scaling(node, base_mass, field);
  }
  
  return base_mass;
}

function compute_phase_coherence(
  node: IGODNNode,
  field: IGODNField
): number {
  // Find nearest nodes in same Hopf fiber
  if (!node.hopf_fiber) return 0.0;
  
  let max_coherence = 0.0;
  
  for (const other_node of field.nodes.values()) {
    if (other_node.id === node.id || !other_node.hopf_fiber) continue;
    
    const phase_diff = hopf_fiber_alignment(
      node.hopf_fiber,
      other_node.hopf_fiber
    );  // S¹ angle diff
    
    // Coherence = 1 - normalized phase difference
    const coherence = 1.0 - (Math.abs(phase_diff) / Math.PI);
    max_coherence = Math.max(max_coherence, coherence);
  }
  
  return max_coherence;
}

function apply_dynamic_mass_scaling(
  node: IGODNNode,
  base_mass: number,
  field: IGODNField
): number {
  // Increase mass for frequently used nodes
  const usage_count = get_node_usage_count(node.id, field);
  const usage_multiplier = 1.0 + (usage_count * 0.1);  // +10% per use
  
  // Decrease mass for old nodes (decay)
  const age_days = (Date.now() - new Date(node.metadata.timestamp).getTime()) / (1000 * 60 * 60 * 24);
  const decay_multiplier = Math.exp(-age_days / 365);  // 1/e per year
  
  // Increase mass for nodes near convergence (focus)
  const convergence_multiplier = field.state.converged ? 1.2 : 1.0;
  
  return base_mass * usage_multiplier * decay_multiplier * convergence_multiplier;
}
```

### 2.2 Distance Calculation (Decomposed)

**CRITICAL REFINEMENT:** Separate physics distance from meta distance to avoid breaking physics intuition.

```typescript
// Distance decomposition - explicit separation of concerns
interface DistanceDecomposition {
  spatial: number;    // Raw position distance (for physics forces)
  semantic: number;   // Embedding/HHNI similarity
  policy: number;    // Constraint compatibility
  temporal: number;  // Recency
  combined: number;   // Weighted sum (for semantic decisions)
}

function compute_distance_decomposed(
  node1: IGODNNode,
  node2: IGODNNode,
  hhni?: HHNIClient
): DistanceDecomposition {
  // Spatial (quaternion geodesic) - used for physics forces
  const spatial = quaternion_geodesic_distance(
    node1.position,  // DualQuatPose
    node2.position   // DualQuatPose
  );
  
  // Semantic distance (if embeddings available)
  let semantic = 0.0;
  if (node1.metadata.embedding && node2.metadata.embedding) {
    semantic = 1.0 - cosine_similarity(
      node1.metadata.embedding,
      node2.metadata.embedding
    );
  } else if (hhni) {
    // Use HHNI for semantic distance
    semantic = hhni.compute_semantic_distance(
      node1.metadata.concept_id || node1.id,
      node2.metadata.concept_id || node2.id
    );
  }
  
  // Policy distance (constraint compatibility)
  const policy = compute_policy_distance(node1, node2);
  
  // Temporal distance (recency)
  const temporal = compute_temporal_distance(node1, node2);
  
  // Combined (weighted for semantic decisions)
  const combined = (
    spatial * 0.30 +
    semantic * 0.40 +
    policy * 0.20 +
    temporal * 0.10
  );
  
  return { spatial, semantic, policy, temporal, combined };
}

// Legacy function for backwards compatibility (uses combined)
function compute_distance(
  node1: IGODNNode,
  node2: IGODNNode,
  hhni?: HHNIClient
): number {
  const decomposed = compute_distance_decomposed(node1, node2, hhni);
  return decomposed.combined;
}

function compute_policy_distance(
  node1: IGODNNode,
  node2: IGODNNode
): number {
  // Check if nodes have compatible constraints
  if (node1.type === 'CONTRACT' && node2.type === 'CONTRACT') {
    const scope1 = node1.metadata.contract_scope;
    const scope2 = node2.metadata.contract_scope;
    
    if (!scope1 || !scope2) return 1.0;  // Max distance if no scope
    
    // Compute scope overlap
    const systems1 = new Set(scope1.systems);
    const systems2 = new Set(scope2.systems);
    const intersection = new Set([...systems1].filter(s => systems2.has(s)));
    const union = new Set([...systems1, ...systems2]);
    
    const jaccard = intersection.size / union.size;
    return 1.0 - jaccard;  // Distance = 1 - similarity
  }
  
  return 0.5;  // Default moderate distance
}

function compute_temporal_distance(
  node1: IGODNNode,
  node2: IGODNNode
): number {
  const time1 = new Date(node1.metadata.timestamp).getTime();
  const time2 = new Date(node2.metadata.timestamp).getTime();
  const diff_seconds = Math.abs(time1 - time2) / 1000;
  
  // Normalize to years
  const diff_years = diff_seconds / (365 * 24 * 3600);
  
  // Sigmoid: 0 at same time, 1 at very different times
  return 1.0 / (1.0 + Math.exp(-10 * (diff_years - 0.5)));
}

function cosine_similarity(vec1: number[], vec2: number[]): number {
  if (vec1.length !== vec2.length) return 0.0;
  
  let dot = 0.0;
  let norm1 = 0.0;
  let norm2 = 0.0;
  
  for (let i = 0; i < vec1.length; i++) {
    dot += vec1[i] * vec2[i];
    norm1 += vec1[i] * vec1[i];
    norm2 += vec2[i] * vec2[i];
  }
  
  if (norm1 === 0.0 || norm2 === 0.0) return 0.0;
  
  return dot / (Math.sqrt(norm1) * Math.sqrt(norm2));
}
```

---

## 3. Force Calculations

### 3.1 Gravitational Force

```typescript
function compute_gravitational_force(
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
  const cluster = node1.cluster;  // CRITICAL REFINEMENT: Use explicit cluster
  const G_effective = field.parameters.G * 
    (field.parameters.cluster_params.get(cluster)?.G_multiplier || 1.0);
  
  // CRITICAL REFINEMENT: Use spatial distance for physics forces
  const dist = compute_distance_decomposed(node1, node2);
  if (dist.spatial < 1e-10) return { x: 0, y: 0, z: 0 };  // Avoid division by zero
  
  const force_magnitude = G_effective * node1.mass * node2.mass / (dist.spatial * dist.spatial);
  
  // Direction from dual quaternion positions
  const pos1_3d = dual_quat_to_position(node1.position);
  const pos2_3d = dual_quat_to_position(node2.position);
  const direction = vector_normalize(vector_subtract(pos2_3d, pos1_3d));
  
  return vector_scale(direction, force_magnitude);
}
```

### 3.2 Repulsive Force

```typescript
function compute_repulsive_force(
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
  const cluster = node1.cluster;  // CRITICAL REFINEMENT: Use explicit cluster
  const k_barrier_effective = field.parameters.k_barrier * 
    (field.parameters.cluster_params.get(cluster)?.k_barrier_multiplier || 1.0);
  
  // CRITICAL REFINEMENT: Use spatial distance for perimeter checks
  const dist = compute_distance_decomposed(node1, node2);
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
```

### 3.3 Holding Force

```typescript
function compute_holding_force(
  node1: IGODNNode,
  node2: IGODNNode,
  field: IGODNField,
  constitutional: ConstitutionalLinkMatrix
): Vector3D {
  // Only hold if constitutionally linked
  if (!constitutional.are_constitutionally_linked(node1, node2)) {
    return { x: 0, y: 0, z: 0 };
  }
  
  // Get cluster-specific k_hold
  const cluster = get_node_cluster(node1, field);
  const k_hold_effective = field.parameters.k_hold * 
    (field.parameters.cluster_params.get(cluster)?.k_hold_multiplier || 1.0);
  
  // Elastic bond to equilibrium distance
  const d_contact = node1.bond_distance || node2.bond_distance || 1.0;
  const d_actual = compute_distance(node1, node2);
  
  const force_magnitude = k_hold_effective * (d_contact - d_actual);
  const direction = vector_normalize(vector_subtract(node2.position, node1.position));
  
  return vector_scale(direction, force_magnitude);
}
```

### 3.4 Damping Force

```typescript
// CRITICAL REFINEMENT: Per-node damping (not pairwise)
// Damping is now applied per-node in compute_net_force, not as pairwise force
// This prevents center-of-mass drift and double counting
```

### 3.5 Net Force

```typescript
function compute_net_force(
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
  const c_damp_effective = field.parameters.c_damp * 
    (field.parameters.cluster_params.get(cluster)?.c_damp_multiplier || 1.0);
  
  const F_damp = vector_scale(node.velocity, -c_damp_effective);
  net_force = vector_add(net_force, F_damp);
  
  return net_force;
}
```

---

## 4. Energy Calculations

### 4.1 Total Energy

```typescript
function compute_total_energy(
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix
): number {
  let E_gravity = 0.0;   // Negative (attraction reduces energy)
  let E_repulse = 0.0;   // Positive (repulsion increases energy)
  let E_hold = 0.0;      // Positive (bonds increase energy if stretched)
  
  const nodes = Array.from(field.nodes.values());
  
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const node1 = nodes[i];
      const node2 = nodes[j];
      
      // Gravitational energy (if compatible)
      if (compatibility.are_compatible(node1, node2)) {
        const cluster = get_node_cluster(node1, field);
        const G_effective = field.parameters.G * 
          (field.parameters.cluster_params.get(cluster)?.G_multiplier || 1.0);
        const distance = compute_distance(node1, node2);
        E_gravity -= G_effective * node1.mass * node2.mass / distance;
      }
      
      // Repulsive energy (if conflicting)
      if (conflict.are_conflicting(node1, node2)) {
        const cluster = get_node_cluster(node1, field);
        const k_barrier_effective = field.parameters.k_barrier * 
          (field.parameters.cluster_params.get(cluster)?.k_barrier_multiplier || 1.0);
        const d_perimeter = node1.perimeter_radius + node2.perimeter_radius;
        const d_actual = compute_distance(node1, node2);
        if (d_actual < d_perimeter) {
          E_repulse += 0.5 * k_barrier_effective * Math.pow(d_perimeter - d_actual, 2);
        }
      }
      
      // Holding energy (if constitutionally linked)
      if (constitutional.are_constitutionally_linked(node1, node2)) {
        const cluster = get_node_cluster(node1, field);
        const k_hold_effective = field.parameters.k_hold * 
          (field.parameters.cluster_params.get(cluster)?.k_hold_multiplier || 1.0);
        const d_contact = node1.bond_distance || node2.bond_distance || 1.0;
        const d_actual = compute_distance(node1, node2);
        E_hold += 0.5 * k_hold_effective * Math.pow(d_contact - d_actual, 2);
      }
    }
  }
  
  return E_gravity + E_repulse + E_hold;
}
```

---

## 5. Iterative Refinement

### 5.1 Main Simulation Loop

```typescript
function simulate_igodn(
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix,
  hhni?: HHNIClient
): FieldState {
  // Initialize state
  field.state.iteration = 0;
  field.state.total_energy = compute_total_energy(field, compatibility, conflict, constitutional);
  field.state.previous_energy = field.state.total_energy;
  field.state.converged = false;
  
  // Dynamic time step
  let delta_t = 0.01;  // Initial time step
  
  // Main loop
  while (!field.state.converged && 
         field.state.iteration < field.parameters.max_iterations) {
    
    // Update masses (if dynamic mass enabled)
    if (field.parameters.enable_dynamic_mass) {
      for (const node of field.nodes.values()) {
        node.mass = compute_mass(node, field);
      }
    }
    
    // Compute forces and update positions
    for (const node of field.nodes.values()) {
      // Compute net force
      const F_net = compute_net_force(
        node, field, compatibility, conflict, constitutional
      );
      
      // Update acceleration (F = ma, so a = F/m)
      const acceleration = vector_scale(F_net, 1.0 / node.mass);
      
      // Update velocity (v_new = v_old + a * Δt)
      node.velocity = vector_add(
        node.velocity,
        vector_scale(acceleration, delta_t)
      );
      
      // Update position (r_new = r_old + v_new * Δt)
      node.position = vector_add(
        node.position,
        vector_scale(node.velocity, delta_t)
      );
    }
    
    // Compute new energy
    field.state.previous_energy = field.state.total_energy;
    field.state.total_energy = compute_total_energy(
      field, compatibility, conflict, constitutional
    );
    field.state.energy_delta = Math.abs(
      field.state.total_energy - field.state.previous_energy
    );
    
    // Dynamic time adjustment (if enabled)
    if (field.parameters.enable_dynamic_time) {
      delta_t = adjust_time_step(delta_t, field.state.energy_delta);
    }
    
    // Check convergence
    field.state.iteration++;
    if (field.state.energy_delta < field.parameters.epsilon) {
      field.state.converged = true;
      field.state.convergence_reason = 'ENERGY_THRESHOLD';
      
      // CRITICAL UPGRADE: Seal as VIF witness when converged
      if (field.parameters.enable_vif_witness && 
          field.state.energy_delta < field.parameters.vif_energy_threshold) {
        await seal_vif_witness(field, compatibility, conflict, constitutional);
      }
    }
  }
  
  if (!field.state.converged) {
    field.state.convergence_reason = 'MAX_ITERATIONS';
  }
  
  return field.state;
}

// CRITICAL UPGRADE: VIF Witness Sealing
async function seal_vif_witness(
  field: IGODNField,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix
): Promise<void> {
  const { VIF, CMC } = await import('@aimos/vif');
  const { map_nodes_to_qaddrs } = await import('@aimos/quaternion-kernel');
  
  // Map nodes to QAddrs (quantum kernel addresses)
  const final_positions = map_nodes_to_qaddrs(field);
  
  // Interpret field configuration (if interpreter available)
  let decisions = null;
  if (field.state.new_nodes) {
    const interpreter = new IGODNToPCEInterpreter();
    decisions = interpreter.interpret_field_configuration(field, field.state.new_nodes);
  }
  
  // Create VIF witness
  const witness = await VIF.seal({
    type: 'IGODN_CONVERGENCE',
    field_hash: hash_field_state(field),
    final_positions: final_positions,
    energy: field.state.total_energy,
    decisions: decisions,
    timestamp: new Date().toISOString(),
    metadata: {
      iteration: field.state.iteration,
      convergence_reason: field.state.convergence_reason,
      node_count: field.nodes.size,
      energy_delta: field.state.energy_delta
    }
  });
  
  // Store in CMC with bitemporal tracking
  await CMC.bitemporal_append(witness, {
    tags: ['igodn', 'convergence', 'vif_witness', 'intent_field'],
    valid_from: new Date(),
    valid_to: null
  });
}

function hash_field_state(field: IGODNField): string {
  // Cryptographic hash of field state for verification
  const state_string = JSON.stringify({
    node_ids: Array.from(field.nodes.keys()).sort(),
    total_energy: field.state.total_energy,
    iteration: field.state.iteration,
    timestamp: new Date().toISOString()
  });
  
  return crypto.createHash('sha256').update(state_string).digest('hex');
}

function adjust_time_step(
  current_delta_t: number,
  energy_delta: number
): number {
  // Fast-forward if low energy change
  if (energy_delta < 1e-8) {
    return current_delta_t * 1.5;  // Speed up
  }
  
  // Slow down if high energy change
  if (energy_delta > 1e-4) {
    return current_delta_t * 0.8;  // Slow down
  }
  
  return current_delta_t;  // Keep same
}
```

---

## 6. Persistent Field Architecture

### 6.1 Global Field State

**CRITICAL REFINEMENT:** IGODN field is long-lived, not per-utterance reset.

```typescript
// Global IGODN field (part of AIM-OS state)
let global_igodn_field: IGODNField | null = null;

async function initialize_igodn_field(): Promise<IGODNField> {
  if (global_igodn_field) {
    return global_igodn_field;
  }
  
  // Load existing contracts, anchors, concepts from CMC/HHNI
  const contracts = await load_contracts_from_pce();
  const anchors = create_default_anchors();
  const concepts = await load_concepts_from_hhni();
  
  // Convert to IGODN nodes
  const nodes = new Map<string, IGODNNode>();
  
  for (const contract of contracts) {
    const node = convert_contract_to_node(contract);
    node.cluster = infer_cluster(node);  // Explicit cluster assignment
    nodes.set(node.id, node);
  }
  
  for (const anchor of anchors) {
    const node = convert_anchor_to_node(anchor);
    node.cluster = infer_cluster(node);
    nodes.set(node.id, node);
  }
  
  for (const concept of concepts) {
    const node = convert_concept_to_node(concept);
    node.cluster = infer_cluster(node);
    nodes.set(node.id, node);
  }
  
  // Initialize field
  const field: IGODNField = {
    nodes,
    parameters: DEFAULT_FIELD_PARAMETERS,
    state: {
      iteration: 0,
      total_energy: 0,
      previous_energy: 0,
      energy_delta: Infinity,
      converged: false,
      new_nodes: []  // Track new nodes for this update
    }
  };
  
  // Run initial convergence (full simulation)
  await simulate_igodn(field, compatibility, conflict, constitutional, {
    max_iterations: 1000
  });
  
  global_igodn_field = field;
  return field;
}

async function process_cif_utterance(
  cif_utterance: CIFUtterance
): Promise<ContractDecisions> {
  // Get or initialize field
  const field = await initialize_igodn_field();
  
  // Convert CIF to IGODN nodes
  const converter = new CIFToIGODNConverter();
  const new_nodes = converter.convert_cif_to_nodes(cif_utterance);
  
  // Assign clusters
  for (const node of new_nodes) {
    node.cluster = infer_cluster(node);
  }
  
  // Place nodes in existing field
  converter.place_nodes_in_field(new_nodes, field, hhni);
  
  // Track new nodes
  field.state.new_nodes = new_nodes;
  
  // Run incremental refinement (small iterations, not full reset)
  await simulate_igodn(field, compatibility, conflict, constitutional, {
    max_iterations: 50,  // Small refinement, not full convergence
    incremental: true     // Only refine new nodes + nearby affected nodes
  });
  
  // Interpret decisions for new nodes only
  const interpreter = new IGODNToPCEInterpreter(compatibility, conflict, constitutional);
  const decisions = interpreter.interpret_field_configuration(field, new_nodes);
  
  // Update field state (persistent)
  global_igodn_field = field;
  
  return decisions;
}
```

---

## 7. Integration APIs

### 7.1 CIF Integration API

```typescript
interface CIFToIGODN {
  /**
   * Convert CIF utterance to IGODN nodes
   */
  convert_cif_to_nodes(
    cif_utterance: CIFUtterance
  ): IGODNNode[];
  
  /**
   * Place nodes in field with initial positions
   */
  place_nodes_in_field(
    nodes: IGODNNode[],
    field: IGODNField,
    hhni: HHNIClient
  ): void;
}

class CIFToIGODNConverter implements CIFToIGODN {
  convert_cif_to_nodes(cif_utterance: CIFUtterance): IGODNNode[] {
    const nodes: IGODNNode[] = [];
    
    // Convert each candidate intent to a node
    for (const phrase of cif_utterance.phrases) {
      if (this.is_contract_candidate(phrase)) {
        const node: IGODNNode = {
          id: `intent_${cif_utterance.id}_${phrase.phraseId}`,
          type: 'INTENT',
          position: { x: 0, y: 0, z: 0 },  // Will be set by placement
          velocity: { x: 0, y: 0, z: 0 },
          mass: 0,  // Will be computed
          perimeter_radius: 0.5,
          metadata: {
            cif_utterance_id: cif_utterance.id,
            candidate_intent_id: phrase.phraseId,
            roles: phrase.roles,
            local_importance: phrase.localImportance,
            certainty: phrase.certainty,
            authority: this.compute_authority(cif_utterance),
            priority: phrase.localImportance,
            entanglement: this.compute_entanglement(phrase, cif_utterance),
            historical_support: 0.5,  // Default
            risk: 0.3,  // Default
            timestamp: cif_utterance.timestampRecord
          }
        };
        nodes.push(node);
      }
    }
    
    return nodes;
  }
  
  place_nodes_in_field(
    nodes: IGODNNode[],
    field: IGODNField,
    hhni: HHNIClient
  ): void {
    for (const node of nodes) {
      // Get initial position from semantic mapping
      const alignment = this.find_alignment(node, field);
      if (alignment) {
        // Place near aligned concept
        const concept_node = field.nodes.get(alignment.conceptId);
        if (concept_node) {
          // Place at small random offset from concept
          const offset = {
            x: (Math.random() - 0.5) * 0.1,
            y: (Math.random() - 0.5) * 0.1,
            z: (Math.random() - 0.5) * 0.1
          };
          node.position = vector_add(concept_node.position, offset);
        } else {
          // Random position if no alignment
          node.position = {
            x: (Math.random() - 0.5) * 10,
            y: (Math.random() - 0.5) * 10,
            z: (Math.random() - 0.5) * 10
          };
        }
      } else {
        // Random position
        node.position = {
          x: (Math.random() - 0.5) * 10,
          y: (Math.random() - 0.5) * 10,
          z: (Math.random() - 0.5) * 10
        };
      }
      
      // Compute initial mass
      node.mass = compute_mass(node, field);
      
      // Add to field
      field.nodes.set(node.id, node);
    }
  }
  
  private is_contract_candidate(phrase: CIFPhrase): boolean {
    const contract_roles = ['goal', 'constraint', 'invariant', 'policy_proposal'];
    return phrase.roles.some(r => contract_roles.includes(r)) &&
           phrase.localImportance > 0.6;
  }
  
  private compute_authority(cif: CIFUtterance): number {
    // Map speaker role to authority
    const role_authority: Record<string, number> = {
      'architect': 0.97,
      'core_developer': 0.85,
      'agent': 0.70,
      'observer': 0.50
    };
    return role_authority[cif.speakerRole] || 0.50;
  }
  
  private compute_entanglement(
    phrase: CIFPhrase,
    cif: CIFUtterance
  ): number {
    // Count how many systems/concepts this phrase touches
    const alignments = cif.alignments.filter(a => a.phraseId === phrase.phraseId);
    return Math.min(alignments.length / 10.0, 1.0);  // Normalize
  }
  
  private find_alignment(
    node: IGODNNode,
    field: IGODNField
  ): CIFAlignment | null {
    // Find best alignment for this node
    // This would use CIF alignment data
    return null;  // Placeholder
  }
}
```

### 7.2 PCE Integration API

```typescript
interface IGODNToPCE {
  /**
   * Interpret field configuration and generate contract decisions
   */
  interpret_field_configuration(
    field: IGODNField,
    new_nodes: IGODNNode[]
  ): ContractDecisions;
}

interface ContractDecisions {
  reinforcements: ReinforcementDecision[];
  conflicts: ConflictDecision[];
  new_doctrines: NewDoctrineDecision[];
}

interface ReinforcementDecision {
  intent_node: IGODNNode;
  target_contract_id: string;
  action: 'EXTEND' | 'STRENGTHEN' | 'CHILD_CONTRACT';
  confidence: number;
}

interface ConflictDecision {
  intent_node: IGODNNode;
  conflicting_contract_id: string;
  action: 'REJECT' | 'FLAG_FOR_REVIEW' | 'REQUIRE_OVERRIDE';
  confidence: number;
}

interface NewDoctrineDecision {
  intent_nodes: IGODNNode[];
  cluster_id: string;
  action: 'NEW_CONTRACT_FAMILY';
  confidence: number;
}

class IGODNToPCEInterpreter implements IGODNToPCE {
  constructor(
    private compatibility: CompatibilityMatrix,
    private conflict: ConflictMatrix,
    private constitutional: ConstitutionalLinkMatrix
  ) {}
  
  interpret_field_configuration(
    field: IGODNField,
    new_nodes: IGODNNode[]
  ): ContractDecisions {
    const decisions: ContractDecisions = {
      reinforcements: [],
      conflicts: [],
      new_doctrines: []
    };
    
    for (const node of new_nodes) {
      // CRITICAL REFINEMENT: Energy-based scoring (not just distance)
      const scores = this.compute_intent_scores(node, field);
      
      // Decision based on dominant score
      if (scores.reinforcement_score > 0.7 && 
          scores.reinforcement_score > scores.conflict_score &&
          scores.reinforcement_score > scores.novelty_score) {
        // Find nearest contract for reinforcement
        const nearest = this.find_nearest_contract(node, field);
        decisions.reinforcements.push({
          intent_node: node,
          target_contract_id: nearest.id,
          action: scores.reinforcement_score > 0.9 ? 'STRENGTHEN' : 'CHILD_CONTRACT',
          confidence: scores.reinforcement_score
        });
      } else if (scores.conflict_score > 0.7 &&
                 scores.conflict_score > scores.novelty_score) {
        // Find conflicting contract
        const conflicting = this.find_conflicting_contract(node, field);
        decisions.conflicts.push({
          intent_node: node,
          conflicting_contract_id: conflicting.id,
          action: scores.conflict_score > 0.9 ? 'REJECT' : 'FLAG_FOR_REVIEW',
          confidence: scores.conflict_score
        });
      } else if (scores.novelty_score > 0.6) {
        // Check if other new nodes form cluster
        const nearby_new = new_nodes.filter(n => {
          if (n.id === node.id) return false;
          const dist = compute_distance_decomposed(node, n);
          return dist.combined < 1.0;
        });
        
        if (nearby_new.length >= 2) {
          decisions.new_doctrines.push({
            intent_nodes: [node, ...nearby_new],
            cluster_id: `cluster_${node.id}`,
            action: 'NEW_CONTRACT_FAMILY',
            confidence: scores.novelty_score
          });
        }
      }
    }
    
    return decisions;
  }
  
  // CRITICAL REFINEMENT: Energy-based scoring
  private compute_intent_scores(
    intent_node: IGODNNode,
    field: IGODNField
  ): { reinforcement_score: number; conflict_score: number; novelty_score: number } {
    let E_gravity_local = 0.0;
    let E_repulse_local = 0.0;
    let nearest_contract_distance = Infinity;
    let nearest_anchor_distance = Infinity;
    
    for (const other_node of field.nodes.values()) {
      if (other_node.id === intent_node.id) continue;
      
      const dist = compute_distance_decomposed(intent_node, other_node);
      
      // Gravitational energy (if compatible)
      if (this.compatibility.are_compatible(intent_node, other_node)) {
        const cluster = intent_node.cluster;
        const G_effective = field.parameters.G * 
          (field.parameters.cluster_params.get(cluster)?.G_multiplier || 1.0);
        E_gravity_local -= G_effective * intent_node.mass * other_node.mass / dist.spatial;
      }
      
      // Repulsive energy (if conflicting)
      if (this.conflict.are_conflicting(intent_node, other_node)) {
        const cluster = intent_node.cluster;
        const k_barrier_effective = field.parameters.k_barrier * 
          (field.parameters.cluster_params.get(cluster)?.k_barrier_multiplier || 1.0);
        const d_perimeter = intent_node.perimeter_radius + other_node.perimeter_radius;
        if (dist.spatial < d_perimeter) {
          E_repulse_local += 0.5 * k_barrier_effective * Math.pow(d_perimeter - dist.spatial, 2);
        }
      }
      
      // Track nearest contracts/anchors (using combined distance for semantic decisions)
      if (other_node.type === 'CONTRACT') {
        nearest_contract_distance = Math.min(nearest_contract_distance, dist.combined);
      }
      if (other_node.type === 'ANCHOR') {
        nearest_anchor_distance = Math.min(nearest_anchor_distance, dist.combined);
      }
    }
    
    // Compute scores
    const reinforcement_score = 
      Math.abs(E_gravity_local) * 0.5 +  // High attraction
      (1.0 / (1.0 + E_repulse_local)) * 0.3 +  // Low repulsion
      (1.0 / (1.0 + nearest_contract_distance)) * 0.2;  // Close to contract
    
    const conflict_score = 
      E_repulse_local * 0.6 +  // High repulsion
      (1.0 / (1.0 + nearest_anchor_distance)) * 0.4;  // Near anchors
    
    const novelty_score = 
      (1.0 / (1.0 + Math.abs(E_gravity_local))) * 0.5 +  // Low attraction
      (1.0 / (1.0 + E_repulse_local)) * 0.3 +  // Low repulsion
      Math.min(nearest_contract_distance, nearest_anchor_distance) * 0.2;  // Far from clusters
    
    return { reinforcement_score, conflict_score, novelty_score };
  }
  
  private find_nearest_contract(
    node: IGODNNode,
    field: IGODNField
  ): IGODNNode {
    let nearest: IGODNNode | null = null;
    let min_distance = Infinity;
    
    for (const other_node of field.nodes.values()) {
      if (other_node.type === 'CONTRACT') {
        const dist = compute_distance_decomposed(node, other_node);
        if (dist.combined < min_distance) {
          min_distance = dist.combined;
          nearest = other_node;
        }
      }
    }
    
    if (!nearest) {
      throw new Error(`No contracts found in field`);
    }
    
    return nearest;
  }
  
  private find_conflicting_contract(
    node: IGODNNode,
    field: IGODNField
  ): IGODNNode {
    let conflicting: IGODNNode | null = null;
    let max_repulsion = -Infinity;
    
    for (const other_node of field.nodes.values()) {
      if (this.conflict.are_conflicting(node, other_node)) {
        const dist = compute_distance_decomposed(node, other_node);
        const d_perimeter = node.perimeter_radius + other_node.perimeter_radius;
        const repulsion = dist.spatial < d_perimeter ? 
          (d_perimeter - dist.spatial) : 0;
        
        if (repulsion > max_repulsion) {
          max_repulsion = repulsion;
          conflicting = other_node;
        }
      }
    }
    
    if (!conflicting) {
      throw new Error(`No conflicting contracts found for node ${node.id}`);
    }
    
    return conflicting;
  }
  
  private find_nearest_contracts(
    node: IGODNNode,
    field: IGODNField
  ): Array<{ node: IGODNNode; distance: number }> {
    const contracts: Array<{ node: IGODNNode; distance: number }> = [];
    
    for (const other_node of field.nodes.values()) {
      if (other_node.type === 'CONTRACT') {
        const dist = compute_distance_decomposed(node, other_node);
        contracts.push({ node: other_node, distance: dist.combined });
      }
    }
    
    // Sort by distance
    contracts.sort((a, b) => a.distance - b.distance);
    
    return contracts.slice(0, 5);  // Top 5 nearest
  }
  
  private check_reinforcement(
    node: IGODNNode,
    nearest_contracts: Array<{ node: IGODNNode; distance: number }>,
    field: IGODNField
  ): ReinforcementDecision | null {
    if (nearest_contracts.length === 0) return null;
    
    const nearest = nearest_contracts[0];
    
    // If very close to existing contract, it's reinforcement
    if (nearest.distance < 0.5) {
      return {
        intent_node: node,
        target_contract_id: nearest.node.id,
        action: 'STRENGTHEN',
        confidence: 1.0 - nearest.distance
      };
    }
    
    // If moderately close, might be extension
    if (nearest.distance < 1.0) {
      return {
        intent_node: node,
        target_contract_id: nearest.node.id,
        action: 'CHILD_CONTRACT',
        confidence: 0.8 - nearest.distance * 0.3
      };
    }
    
    return null;
  }
  
  private check_conflict(
    node: IGODNNode,
    nearest_contracts: Array<{ node: IGODNNode; distance: number }>,
    field: IGODNField
  ): ConflictDecision | null {
    // Check if node is in high repulsion region
    for (const contract_info of nearest_contracts) {
      const contract = contract_info.node;
      
      // Check if within repulsive perimeter
      const d_perimeter = node.perimeter_radius + contract.perimeter_radius;
      if (contract_info.distance < d_perimeter) {
        return {
          intent_node: node,
          conflicting_contract_id: contract.id,
          action: 'FLAG_FOR_REVIEW',
          confidence: 1.0 - (contract_info.distance / d_perimeter)
        };
      }
    }
    
    return null;
  }
  
  private check_new_doctrine(
    node: IGODNNode,
    all_new_nodes: IGODNNode[],
    field: IGODNField
  ): NewDoctrineDecision | null {
    // Check if node is far from all existing contracts
    const nearest_contracts = this.find_nearest_contracts(node, field);
    
    if (nearest_contracts.length === 0 || nearest_contracts[0].distance > 2.0) {
      // Check if other new nodes are nearby (forming cluster)
      const nearby_new_nodes = all_new_nodes.filter(n => {
        if (n.id === node.id) return false;
        const distance = compute_distance(node, n);
        return distance < 1.0;
      });
      
      if (nearby_new_nodes.length >= 2) {
        return {
          intent_nodes: [node, ...nearby_new_nodes],
          cluster_id: `cluster_${node.id}`,
          action: 'NEW_CONTRACT_FAMILY',
          confidence: 0.7
        };
      }
    }
    
    return null;
  }
}
```

---

## 8. Performance Considerations

### 8.1 Spatial Indexing

For large fields (1000+ nodes), use spatial indexing:

```typescript
class SpatialIndex {
  private quadtree: Quadtree3D;
  
  constructor(bounds: BoundingBox) {
    this.quadtree = new Quadtree3D(bounds);
  }
  
  insert(node: IGODNNode): void {
    this.quadtree.insert(node.position, node);
  }
  
  query_nearby(
    position: Vector3D,
    radius: number
  ): IGODNNode[] {
    return this.quadtree.query_radius(position, radius);
  }
}
```

### 8.2 Force Computation Optimization

Only compute forces for nearby nodes:

```typescript
function compute_net_force_optimized(
  node: IGODNNode,
  field: IGODNField,
  spatial_index: SpatialIndex,
  compatibility: CompatibilityMatrix,
  conflict: ConflictMatrix,
  constitutional: ConstitutionalLinkMatrix
): Vector3D {
  // Query nearby nodes only
  const nearby_nodes = spatial_index.query_nearby(
    node.position,
    node.perimeter_radius * 3.0  // 3x perimeter radius
  );
  
  let net_force: Vector3D = { x: 0, y: 0, z: 0 };
  
  for (const other_node of nearby_nodes) {
    if (other_node.id === node.id) continue;
    
    // ... compute forces as before ...
  }
  
  return net_force;
}
```

### 8.3 Parallelization

Force computations can be parallelized:

```typescript
async function simulate_igodn_parallel(
  field: IGODNField,
  // ... other params
): Promise<FieldState> {
  // Parallel force computation
  const force_promises = Array.from(field.nodes.values()).map(node =>
    Promise.resolve(compute_net_force(node, field, ...))
  );
  
  const forces = await Promise.all(force_promises);
  
  // Update positions
  let i = 0;
  for (const node of field.nodes.values()) {
    const F_net = forces[i++];
    // ... update position ...
  }
  
  // ... rest of simulation ...
}
```

---

## 9. Field Invariants (L5 - Self-Trust)

**CRITICAL:** Field-level invariants ensure physics behaves correctly.

```typescript
interface FieldInvariants {
  // No anchor node ever loses mass below threshold
  min_anchor_mass: number;  // Default: 1.0
  
  // Total energy must be monotone decreasing under pure relaxation
  energy_monotone: boolean;  // Enforced
  
  // No single update step may move node farther than d_max spatially
  max_spatial_step: number;  // Default: 1.0
  
  // If conflict tension between INTENT and SAFETY anchor crosses threshold, always log
  conflict_log_threshold: number;  // Default: 10.0
}

function validate_field_invariants(
  field: IGODNField,
  invariants: FieldInvariants
): { valid: boolean; violations: string[] } {
  const violations: string[] = [];
  
  // Check anchor masses
  for (const node of field.nodes.values()) {
    if (node.type === 'ANCHOR' && node.mass < invariants.min_anchor_mass) {
      violations.push(`Anchor ${node.id} mass ${node.mass} below threshold ${invariants.min_anchor_mass}`);
    }
  }
  
  // Check energy monotonicity
  if (invariants.energy_monotone) {
    if (field.state.total_energy > field.state.previous_energy + 1e-6) {
      violations.push(`Energy increased: ${field.state.previous_energy} -> ${field.state.total_energy}`);
    }
  }
  
  // Check spatial step limits
  // (Would need to track previous positions)
  
  return {
    valid: violations.length === 0,
    violations
  };
}
```

**These are axioms about how physics is allowed to behave—type system for the field.**

---

## 10. Next Steps

1. **Implement Core Engine** - Basic IGODN simulation
2. **Implement CIF Integration** - Convert utterances to nodes
3. **Implement PCE Integration** - Interpret field configuration
4. **Testing** - Validate with synthetic contracts
5. **Visualization** - Visualize intent space dynamics
6. **Performance** - Optimize for large fields
7. **Production** - Integrate with AIM-OS systems

---

**Status:** 📐 **DESIGN PHASE**  
**Confidence:** 0.80 (Technical design clear, implementation details specified)  
**Next:** Begin Phase 2 implementation (Core IGODN Engine)

