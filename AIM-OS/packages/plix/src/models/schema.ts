/**
 * PLIx v1 JSON Schema and TypeScript Types
 * 
 * Core schema for typed intent/contract layer
 * Enhanced with Phase 1 improvements: constraints, error taxonomy
 */

import type { PLIXConstraint } from './constraints';
import type { ErrorClause } from './errors';
import type { GeometricOperation } from './quaternion-types';

export interface PLIxIntent {
  /** Natural language intent description */
  intent: string;
  
  /** Context information */
  context: {
    /** Relevant entities */
    entities: string[];
    
    /** Scope of the intent */
    scope: string;
    
    /** Risk level (0-1) */
    risk: number;
    
    /** Additional context metadata */
    metadata?: Record<string, any>;
  };
  
  /** Contract specification */
  contract: {
    /** Preconditions (must be true before execution) - Enhanced with logical/quantified/temporal constraints */
    pre: (string | PLIXConstraint)[];
    
    /** Postconditions (must be true after execution) - Enhanced with logical/quantified/temporal constraints */
    post: (string | PLIXConstraint)[];
    
    /** Required capabilities */
    capabilities: string[];
    
    /** Policy constraints */
    policies: string[];
    
    /** Invariants (must hold throughout execution) */
    invariants?: string[];
    
    /** Gemini Extensions: DSL Structure (SmaCoNat methodology) */
    dsl_structure?: {
      /** Ordered sequence of distinct rules */
      rules: Array<{
        type: 'Heading' | 'Account' | 'Asset' | 'Agreement' | 'Event' | string;
        content: string;
      }>;
      /** Domain-specific operations ontology */
      ontology: string[];
    };
    
    /** Gemini Extensions: Formal Validation */
    formal_validation?: {
      /** Alloy model for invariant verification */
      alloy_model?: string;
      /** TLA+ specification for recovery verification */
      tla_spec?: string;
      /** Validation status */
      validation_status: 'pending' | 'valid' | 'invalid';
      /** Validation errors if invalid */
      validation_errors?: string[];
    };
    
    /** Gemini Extensions: Layer-1 Guards (fast, lightweight) */
    layer1_guards?: {
      /** JSON Schema constraints */
      json_schema?: object;
      /** Regular expression constraints */
      regex_constraints?: string[];
      /** GBNF controllers */
      gbnf_controllers?: string[];
    };
    
    /** Gemini Extensions: Layer-2 Validators (rigorous semantic/logic) */
    layer2_validators?: {
      /** SHACL shapes for graph constraints */
      shacl_shapes?: string[];
      /** SMT solvers for numeric/temporal properties */
      smt_solvers?: string[];
    };
  };
  
  /** Execution plan (ChatGPT: TaskList structure) */
  plan: {
    /** Plan steps (ChatGPT: TaskEntry[]) */
    steps: PLIxPlanStep[];
    
    /** Step dependencies */
    deps: Array<{
      step: string;      // Step ID
      depends_on: string[]; // Step IDs this depends on
    }>;
    
    /** Plan metadata */
    metadata?: {
      estimated_duration?: number;
      estimated_cost?: number;
      parallelizable?: boolean;
    };
  };
  
  /** Recoverable conditions */
  conditions: {
    /** Action on test failure */
    onTestFail: 'retry' | 'compensate' | 'fail' | 'escalate';
    
    /** Action on low confidence */
    onLowConfidence: 'retry' | 'compensate' | 'fail' | 'escalate';
    
    /** Action on policy breach */
    onPolicyBreach: 'retry' | 'compensate' | 'fail' | 'escalate';
    
    /** Action on timeout */
    onTimeout?: 'retry' | 'compensate' | 'fail' | 'escalate';
    
    /** Action on error */
    onError?: 'retry' | 'compensate' | 'fail' | 'escalate';
    
    /** Custom conditions */
    custom?: Array<{
      condition: string;
      action: 'retry' | 'compensate' | 'fail' | 'escalate';
    }>;
    
    /** Gemini Extensions: Saga Pattern Support */
    saga_pattern?: {
      /** Compensation callbacks (executed in reverse order on failure) */
      compensations: Array<{
        step_id: string;
        compensation_action: string;
        compensation_tool?: string;
        compensation_args?: Record<string, any>;
      }>;
      /** TLA+ recovery verification */
      recovery_verification?: {
        tla_spec?: string;
        verification_status: 'pending' | 'verified' | 'failed';
        verification_errors?: string[];
      };
    };
  };
  
  /** Evidence requirements */
  evidence: {
    /** Required evidence artifacts */
    required: Array<{
      type: 'code' | 'doc' | 'decision' | 'test' | 'diff' | 'lineage';
      description: string;
      optional?: boolean;
    }>;
    
    /** Evidence to produce */
    produce: Array<{
      type: 'code' | 'doc' | 'decision' | 'test' | 'diff' | 'lineage';
      description: string;
      format?: string;
    }>;
    
    /** Gemini Extensions: OpenLineage Integration */
    openlineage?: {
      /** Job Event (design-time metadata) */
      job_event?: {
        source_code_location: string;
        declared_inputs: string[];
        declared_outputs: string[];
      };
      
      /** Run Events (runtime execution) */
      run_events?: Array<{
        state: 'START' | 'COMPLETE' | 'FAIL';
        timestamp: string;
        input_datasets: string[];
        output_datasets: string[];
        error_message?: string;
        execution_time_ms?: number;
      }>;
      
      /** Dataset Events (data artifact tracking) */
      dataset_events?: Array<{
        dataset_id: string;
        schema?: object;
        ownership?: string;
        data_source_location?: string;
      }>;
    };
    
    /** Gemini Extensions: W3C PROV Trace */
    prov_trace?: {
      entities: Array<{
        id: string;
        type: string;
        attributes: Record<string, any>;
      }>;
      activities: Array<{
        id: string;
        type: string;
        started_at: string;
        ended_at?: string;
        used: string[];
        generated: string[];
      }>;
    };
    
    /** Gemini Extensions: Intent Lineage */
    intent_lineage?: {
      original_nl_intent: string;
      compiled_dsl_contract: string;
      execution_plan_id: string;
      evidence_chain: string[]; // SEG edge IDs
    };
  };
  
  /** Telemetry and monitoring */
  telemetry: {
    /** Confidence thresholds */
    confidenceThresholds: {
      minimum: number;      // 0-1
      warning: number;      // 0-1
      critical: number;     // 0-1
    };
    
    /** Timeouts (milliseconds) */
    timeouts: {
      step: number;
      plan: number;
      retry?: number;
    };
    
    /** Cost budgets */
    costBudgets?: {
      tokens?: number;
      api_calls?: number;
      compute_time_ms?: number;
    };
    
    /** Gemini Extensions: Safety Gates */
    safety_gates?: {
      /** Linguistic Confidence Gate (Self-REF) */
      linguistic_confidence?: {
        method: 'self-ref';
        confidence_score: number; // 0-1
        threshold: number;
        confidence_tokens?: string[];
      };
      
      /** Economic Router Gate (BaRP - Bandit-feedback Routing) */
      economic_router?: {
        method: 'barp';
        preference_vector: number[]; // w_t
        estimated_reward: number;
        cost_estimate: number;
      };
      
      /** Compliance Gate (OPA/Cedar) */
      compliance_gate?: {
        engine: 'opa' | 'cedar';
        policy_queries: string[];
        decision: 'permit' | 'forbid';
        policy_results: Array<{
          query: string;
          result: boolean;
          explanation?: string;
        }>;
      };
    };
  };
  
  /** Provenance information */
  provenance: {
    /** Who created this intent */
    who: string;
    
    /** When it was created */
    when: string; // ISO 8601
    
    /** Lineage (references to related intents/plans) */
    lineage: string[];
    
    /** Version */
    version?: string;
  };
  
  /** Metadata */
  metadata?: {
    tags?: string[];
    priority?: 'low' | 'medium' | 'high' | 'critical';
    status?: 'draft' | 'approved' | 'executing' | 'completed' | 'failed';
    [key: string]: any;
  };
}

/**
 * Plan Step (ChatGPT: TaskEntry structure)
 */
export interface PLIxPlanStep {
  /** Step identifier */
  id: string;
  
  /** Step description (human-readable, ChatGPT: "step" field) */
  step: string;
  
  /** Agent responsible for this step */
  agent: string;
  
  /** Tool/action to use (ChatGPT: "action" field) */
  tool: string;
  
  /** Target (file, resource, etc.) */
  target: string;
  
  /** Tool arguments (ChatGPT: "params" field) */
  args: Record<string, any>;
  
  /** Step dependencies (which steps must complete before this) */
  depends_on?: string[];
  
  /** Retry configuration */
  retry?: {
    max_attempts: number;
    backoff: 'linear' | 'exponential' | 'fixed';
    backoff_ms: number;
    min_delay?: string; // Duration string (e.g., "100ms")
    max_delay?: string; // Duration string (e.g., "2s")
    jitter?: boolean; // Add jitter to backoff
    conditions?: string[]; // Conditions that trigger retry
  };
  
  /** Error handling - Enhanced with typed error taxonomy */
  errors?: ErrorClause[];
  
  /** Fallback step (alternative if this step fails) */
  fallback?: string; // Step ID
  
  /** Compensation action (if step fails) */
  compensate?: {
    action: string;
    tool?: string;
    args?: Record<string, any>;
  };
  
  /** Step-specific confidence threshold */
  confidence_threshold?: number;
  
  /** Step-specific evidence requirements */
  evidence_required?: string[];
  
  /** Step metadata */
  metadata?: Record<string, any>;
}

/**
 * PLIx Execution Result
 */
export interface PLIxExecutionResult {
  /** Plan ID */
  planId: string;
  
  /** Execution status */
  status: 'success' | 'failure' | 'partial' | 'cancelled';
  
  /** Completed steps */
  completed_steps: string[];
  
  /** Failed steps */
  failed_steps: Array<{
    step_id: string;
    error: string;
    attempt: number;
  }>;
  
  /** Evidence collected */
  evidence: Array<{
    type: string;
    content: any;
    step_id?: string;
    timestamp: string;
  }>;
  
  /** Confidence scores per step */
  confidence_scores: Record<string, number>;
  
  /** Violations */
  violations: Array<{
    type: 'precondition' | 'postcondition' | 'policy' | 'confidence' | 'timeout';
    step_id?: string;
    message: string;
    severity: 'warning' | 'error' | 'critical';
  }>;
  
  /** Execution metrics */
  metrics: {
    total_duration_ms: number;
    step_durations: Record<string, number>;
    retry_count: number;
    compensation_count: number;
    evidence_completeness: number; // 0-1
  };
  
  /** Provenance */
  provenance: {
    executed_by: string;
    executed_at: string;
    plan_version: string;
    lineage: string[];
  };
  
  /** Phase 2, Week 5: Geometric Operations (Quaternion Extensions) */
  geometric?: {
    /** Geometric operations (place, move, sense, emit) */
    operations?: GeometricOperation[];
    
    /** Quantum context for operations */
    quantumContext?: import('./quaternion-types').QuantumContext;
  };
}

