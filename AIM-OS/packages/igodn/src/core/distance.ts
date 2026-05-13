/**
 * Distance calculation with decomposition
 * 
 * CRITICAL REFINEMENT: Separate physics distance from meta distance
 * - spatial: Used for physics forces (gravity, repulsion, bonds)
 * - combined: Used for semantic decisions (near contracts?, new doctrine?)
 */

import { IGODNNode, DistanceDecomposition } from '../types';
import { quaternion_geodesic_distance } from '../utils/quaternions';
import { vector_magnitude } from '../utils/vectors';

/**
 * Compute cosine similarity between two vectors
 */
function cosine_similarity(vec1: number[], vec2: number[]): number {
  if (vec1.length !== vec2.length) return 0.0;
  
  let dot = 0.0;
  let mag1 = 0.0;
  let mag2 = 0.0;
  
  for (let i = 0; i < vec1.length; i++) {
    dot += vec1[i] * vec2[i];
    mag1 += vec1[i] * vec1[i];
    mag2 += vec2[i] * vec2[i];
  }
  
  if (mag1 === 0 || mag2 === 0) return 0.0;
  
  return dot / (Math.sqrt(mag1) * Math.sqrt(mag2));
}

/**
 * Compute policy distance (constraint compatibility)
 */
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
    const systems1 = new Set(scope1.systems || []);
    const systems2 = new Set(scope2.systems || []);
    const intersection = new Set([...systems1].filter(s => systems2.has(s)));
    const union = new Set([...systems1, ...systems2]);
    
    if (union.size === 0) return 1.0;
    
    const jaccard = intersection.size / union.size;
    return 1.0 - jaccard;  // Distance = 1 - similarity
  }
  
  return 0.5;  // Default moderate distance
}

/**
 * Compute temporal distance (recency)
 */
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

/**
 * Compute semantic distance (embeddings/HHNI)
 */
function compute_semantic_distance(
  node1: IGODNNode,
  node2: IGODNNode,
  hhni?: any  // HHNIClient type would be imported from @aimos/hhni
): number {
  // If embeddings available, use cosine similarity
  if (node1.metadata.embedding && node2.metadata.embedding) {
    const similarity = cosine_similarity(
      node1.metadata.embedding,
      node2.metadata.embedding
    );
    return 1.0 - similarity;  // Distance = 1 - similarity
  }
  
  // TODO: Use HHNI for semantic distance if available
  // if (hhni && node1.metadata.concept_id && node2.metadata.concept_id) {
  //   return hhni.compute_semantic_distance(
  //     node1.metadata.concept_id,
  //     node2.metadata.concept_id
  //   );
  // }
  
  return 0.5;  // Default moderate distance
}

/**
 * Compute distance decomposition
 * 
 * Returns explicit separation of spatial, semantic, policy, and temporal distances
 */
export function compute_distance_decomposed(
  node1: IGODNNode,
  node2: IGODNNode,
  hhni?: any,
  weights?: {
    spatial: number;
    semantic: number;
    policy: number;
    temporal: number;
  }
): DistanceDecomposition {
  // Default weights
  const w = weights || {
    spatial: 0.30,
    semantic: 0.40,
    policy: 0.20,
    temporal: 0.10
  };
  
  // Spatial (quaternion geodesic) - used for physics forces
  const spatial = quaternion_geodesic_distance(
    node1.position,
    node2.position
  );
  
  // Semantic distance
  const semantic = compute_semantic_distance(node1, node2, hhni);
  
  // Policy distance
  const policy = compute_policy_distance(node1, node2);
  
  // Temporal distance
  const temporal = compute_temporal_distance(node1, node2);
  
  // Combined (weighted for semantic decisions)
  const combined = (
    spatial * w.spatial +
    semantic * w.semantic +
    policy * w.policy +
    temporal * w.temporal
  );
  
  return { spatial, semantic, policy, temporal, combined };
}

