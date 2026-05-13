/**
 * Effect System for PLIx
 * 
 * Implements effect row checking and capability gating
 * Based on Core-PLIx Semantics v0.1 final
 */

import type { EffectRow, Confidence } from './annotated-typing';
import { EffectRowOps, CapabilityGating } from './annotated-typing';

/**
 * Effect Checker
 * 
 * Validates effects against capabilities and policies
 */
export class EffectChecker {
  private allowedEffects: Map<string, EffectRow>; // context → allowed effects
  
  constructor() {
    this.allowedEffects = new Map();
  }
  
  /**
   * Register allowed effects for a context
   */
  registerContext(contextId: string, effects: EffectRow): void {
    this.allowedEffects.set(contextId, effects);
  }
  
  /**
   * Check if action is allowed in context
   * 
   * Validates: allowed_effects(context) ⊇ eff(action)
   */
  checkAction(contextId: string, actionEffects: EffectRow): { allowed: boolean; violations: string[]; reason?: string } {
    const allowedEffects = this.allowedEffects.get(contextId);
    
    if (!allowedEffects) {
      return {
        allowed: false,
        violations: Object.keys(actionEffects).filter(k => actionEffects[k] === true),
        reason: `Context '${contextId}' not registered`
      };
    }
    
    return CapabilityGating.checkCapability(allowedEffects, actionEffects);
  }
  
  /**
   * Check if plan is allowed in context
   * 
   * Validates all steps against context capabilities
   */
  checkPlan(
    contextId: string,
    steps: Array<{ id: string; effects: EffectRow }>
  ): { allowed: boolean; violations: Array<{ stepId: string; effects: string[] }>; } {
    const violations: Array<{ stepId: string; effects: string[] }> = [];
    
    for (const step of steps) {
      const check = this.checkAction(contextId, step.effects);
      if (!check.allowed) {
        violations.push({
          stepId: step.id,
          effects: check.violations
        });
      }
    }
    
    return {
      allowed: violations.length === 0,
      violations
    };
  }
  
  /**
   * Get allowed effects for context
   */
  getAllowedEffects(contextId: string): EffectRow | null {
    return this.allowedEffects.get(contextId) || null;
  }
}

/**
 * Policy Engine
 * 
 * Enforces effect policies (which effects are allowed, prohibited, require approval)
 */
export class PolicyEngine {
  private policies: Map<string, EffectPolicy>;
  
  constructor() {
    this.policies = new Map();
  }
  
  /**
   * Register effect policy
   */
  registerPolicy(policyId: string, policy: EffectPolicy): void {
    this.policies.set(policyId, policy);
  }
  
  /**
   * Check if effects comply with policy
   */
  checkPolicy(policyId: string, effects: EffectRow): PolicyCheckResult {
    const policy = this.policies.get(policyId);
    
    if (!policy) {
      return {
        compliant: false,
        violations: [],
        reason: `Policy '${policyId}' not found`
      };
    }
    
    const violations: string[] = [];
    const requiresApproval: string[] = [];
    
    for (const [effect, present] of Object.entries(effects)) {
      if (present !== true) continue;
      
      // Check if prohibited
      if (policy.prohibited.includes(effect)) {
        violations.push(`Effect '${effect}' is prohibited by policy`);
      }
      
      // Check if requires approval
      if (policy.requiresApproval.includes(effect)) {
        requiresApproval.push(effect);
      }
      
      // Check if allowed
      if (!policy.allowed.includes(effect) && !policy.requiresApproval.includes(effect)) {
        violations.push(`Effect '${effect}' is not allowed by policy`);
      }
    }
    
    return {
      compliant: violations.length === 0,
      violations,
      requiresApproval
    };
  }
  
  /**
   * Get policy
   */
  getPolicy(policyId: string): EffectPolicy | null {
    return this.policies.get(policyId) || null;
  }
}

/**
 * Effect Policy
 */
export interface EffectPolicy {
  /** Effects that are always allowed */
  allowed: string[];
  
  /** Effects that are prohibited */
  prohibited: string[];
  
  /** Effects that require approval */
  requiresApproval: string[];
  
  /** Policy metadata */
  metadata?: {
    name?: string;
    description?: string;
    owner?: string;
    tier?: number; // Authority tier
  };
}

/**
 * Policy Check Result
 */
export interface PolicyCheckResult {
  compliant: boolean;
  violations: string[];
  requiresApproval?: string[];
  reason?: string;
}

/**
 * Standard Effect Policies
 */
export const StandardPolicies = {
  /**
   * Read-only policy (no mutations)
   */
  readOnly: (): EffectPolicy => ({
    allowed: ['io'], // Read-only I/O
    prohibited: ['db', 'net'], // No database or network
    requiresApproval: [],
    metadata: {
      name: 'ReadOnly',
      description: 'Allows only read operations',
      tier: 0
    }
  }),
  
  /**
   * Standard policy (typical application)
   */
  standard: (): EffectPolicy => ({
    allowed: ['io', 'net', 'db'],
    prohibited: [],
    requiresApproval: ['compensable'], // Compensable ops need review
    metadata: {
      name: 'Standard',
      description: 'Standard application policy',
      tier: 1
    }
  }),
  
  /**
   * Privileged policy (system operations)
   */
  privileged: (): EffectPolicy => ({
    allowed: ['io', 'net', 'db', 'compensable', 'idempotent'],
    prohibited: [],
    requiresApproval: [],
    metadata: {
      name: 'Privileged',
      description: 'Full system access',
      tier: 2
    }
  }),
  
  /**
   * Restricted policy (sandboxed)
   */
  restricted: (): EffectPolicy => ({
    allowed: [],
    prohibited: ['io', 'net', 'db'],
    requiresApproval: ['io'], // Even I/O requires approval
    metadata: {
      name: 'Restricted',
      description: 'Highly restricted sandbox',
      tier: -1
    }
  })
};

/**
 * Effect Inference Engine
 * 
 * Infers effects from action definitions
 */
export class EffectInference {
  /**
   * Infer effects from action name/tool
   */
  static inferFromName(name: string): EffectRow {
    const effects: EffectRow = {};
    const lower = name.toLowerCase();
    
    // I/O operations
    if (lower.match(/read|write|file|disk|storage/)) {
      effects.io = true;
    }
    
    // Network operations
    if (lower.match(/http|api|fetch|request|network|socket/)) {
      effects.net = true;
    }
    
    // Database operations
    if (lower.match(/db|database|query|sql|insert|update|delete|select/)) {
      effects.db = true;
    }
    
    // Idempotence markers
    if (lower.match(/idempotent|read|get|query|select/)) {
      effects.idempotent = true;
    }
    
    // Compensation markers
    if (lower.match(/compensate|rollback|undo|revert/)) {
      effects.compensable = true;
    }
    
    return effects;
  }
  
  /**
   * Infer effects from action metadata
   */
  static inferFromMetadata(metadata: any): EffectRow {
    const effects: EffectRow = {};
    
    if (metadata.io === true) effects.io = true;
    if (metadata.net === true) effects.net = true;
    if (metadata.db === true) effects.db = true;
    if (metadata.idempotent === true) effects.idempotent = true;
    if (metadata.compensable === true) effects.compensable = true;
    
    return effects;
  }
  
  /**
   * Infer effects from both name and metadata
   */
  static infer(name: string, metadata?: any): EffectRow {
    const fromName = this.inferFromName(name);
    const fromMetadata = metadata ? this.inferFromMetadata(metadata) : {};
    
    return EffectRowOps.union(fromName, fromMetadata);
  }
}

/**
 * Effect Validator
 * 
 * Validates effect usage across intent/contract/plan
 */
export class EffectValidator {
  private effectChecker: EffectChecker;
  private policyEngine: PolicyEngine;
  
  constructor() {
    this.effectChecker = new EffectChecker();
    this.policyEngine = new PolicyEngine();
  }
  
  /**
   * Validate intent against effect policies
   */
  validateIntent(
    intent: any,
    contextId: string,
    policyId: string
  ): { valid: boolean; errors: string[]; warnings: string[] } {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Extract plan steps
    const steps = intent.plan?.steps || [];
    
    // Infer effects for each step
    const stepEffects = steps.map((step: any) => ({
      id: step.id || step.step,
      effects: EffectInference.infer(step.tool || step.id, step.metadata)
    }));
    
    // Check against context capabilities
    const capabilityCheck = this.effectChecker.checkPlan(contextId, stepEffects);
    
    if (!capabilityCheck.allowed) {
      for (const violation of capabilityCheck.violations) {
        errors.push(`Step '${violation.stepId}' requires effects not allowed in context: ${violation.effects.join(', ')}`);
      }
    }
    
    // Check against policy
    const planEffects = EffectRowOps.union(...stepEffects.map(s => s.effects));
    const policyCheck = this.policyEngine.checkPolicy(policyId, planEffects);
    
    if (!policyCheck.compliant) {
      errors.push(...policyCheck.violations);
    }
    
    if (policyCheck.requiresApproval && policyCheck.requiresApproval.length > 0) {
      warnings.push(`Effects require approval: ${policyCheck.requiresApproval.join(', ')}`);
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  /**
   * Get effect checker
   */
  getEffectChecker(): EffectChecker {
    return this.effectChecker;
  }
  
  /**
   * Get policy engine
   */
  getPolicyEngine(): PolicyEngine {
    return this.policyEngine;
  }
}

/**
 * Export for convenience
 */
export {
  EffectChecker,
  PolicyEngine,
  EffectInference
};

