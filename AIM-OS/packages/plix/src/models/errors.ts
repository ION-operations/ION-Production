/**
 * PLIX Error Taxonomy
 * 
 * Typed error system for declarative error handling in PLIX contracts
 * Based on External AI Feedback (Grok, Gemini)
 */

export type NetworkError = 
  | 'net.timeout'
  | 'net.unreachable'
  | 'net.connection_failed';

export type PolicyError =
  | 'policy.denied'
  | 'policy.insufficient_authority'
  | 'policy.quorum_not_met';

export type ConstraintError =
  | 'constraint.violated'
  | 'constraint.precondition_failed'
  | 'constraint.postcondition_failed'
  | 'constraint.invariant_broken';

export type ContractError =
  | 'contract.precondition_failed'
  | 'contract.postcondition_failed'
  | 'contract.compensation_failed';

export type ProofError =
  | 'proof.missing'
  | 'proof.invalid'
  | 'proof.insufficient';

export type AuthError =
  | 'auth.insufficient'
  | 'auth.expired'
  | 'auth.invalid';

export type ResourceError =
  | 'resource.exceeded'
  | 'resource.unavailable'
  | 'resource.throttled';

export type ExecutionError =
  | 'execution.failed'
  | 'execution.timeout'
  | 'execution.cancelled';

export type PLIXErrorType =
  | NetworkError
  | PolicyError
  | ConstraintError
  | ContractError
  | ProofError
  | AuthError
  | ResourceError
  | ExecutionError;

export type ErrorAction = 'retry' | 'compensate' | 'fail' | 'escalate' | 'fallback';

export interface ErrorConfig {
  /** Retry configuration */
  retry?: {
    max: number;
    min_delay: string; // Duration string (e.g., "100ms")
    max_delay: string; // Duration string (e.g., "2s")
  };
  
  /** Compensation action */
  compensate?: string; // Step ID or action name
  
  /** Escalation target */
  escalate?: 'admin' | 'operator' | string;
  
  /** Fallback step */
  fallback?: string; // Step ID
}

export interface ErrorClause {
  /** Error type */
  error: PLIXErrorType;
  
  /** Action to take */
  action: ErrorAction;
  
  /** Action configuration */
  config?: ErrorConfig;
}

/**
 * Error taxonomy helper functions
 */
export const ErrorTaxonomy = {
  /** Check if error is network-related */
  isNetworkError(error: PLIXErrorType): error is NetworkError {
    return error.startsWith('net.');
  },
  
  /** Check if error is policy-related */
  isPolicyError(error: PLIXErrorType): error is PolicyError {
    return error.startsWith('policy.');
  },
  
  /** Check if error is constraint-related */
  isConstraintError(error: PLIXErrorType): error is ConstraintError {
    return error.startsWith('constraint.');
  },
  
  /** Check if error is contract-related */
  isContractError(error: PLIXErrorType): error is ContractError {
    return error.startsWith('contract.');
  },
  
  /** Check if error is proof-related */
  isProofError(error: PLIXErrorType): error is ProofError {
    return error.startsWith('proof.');
  },
  
  /** Check if error is auth-related */
  isAuthError(error: PLIXErrorType): error is AuthError {
    return error.startsWith('auth.');
  },
  
  /** Check if error is resource-related */
  isResourceError(error: PLIXErrorType): error is ResourceError {
    return error.startsWith('resource.');
  },
  
  /** Check if error is execution-related */
  isExecutionError(error: PLIXErrorType): error is ExecutionError {
    return error.startsWith('execution.');
  },
  
  /** Get error category */
  getCategory(error: PLIXErrorType): string {
    if (this.isNetworkError(error)) return 'network';
    if (this.isPolicyError(error)) return 'policy';
    if (this.isConstraintError(error)) return 'constraint';
    if (this.isContractError(error)) return 'contract';
    if (this.isProofError(error)) return 'proof';
    if (this.isAuthError(error)) return 'auth';
    if (this.isResourceError(error)) return 'resource';
    if (this.isExecutionError(error)) return 'execution';
    return 'unknown';
  }
};

