/**
 * @aimos/igodn - Intent Graviton Organic Dynamic Network
 * 
 * Physics engine for intent-space
 * 
 * Main entry point for IGODN package
 */

// Core types
export * from './types';

// Core algorithms
export * from './core/clusters';
export * from './core/distance';
export * from './core/mass';
export * from './core/forces';
export * from './core/energy';
export * from './core/simulation';
export * from './core/field';
export * from './core/invariants';

// Matrices
export * from './matrices';

// Integration (Phase 3)
export * from './integration';

// Utilities
export * from './utils/vectors';
export * from './utils/quaternions';

// Re-export main functions for convenience
import { simulate_igodn } from './core/simulation';
import { create_igodn_field, add_node_to_field, create_default_anchors } from './core/field';
import { validate_field_invariants } from './core/invariants';

export {
  simulate_igodn,
  create_igodn_field,
  add_node_to_field,
  create_default_anchors,
  validate_field_invariants
};

