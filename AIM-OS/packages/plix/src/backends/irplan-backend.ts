/**
 * IRPlan Backend Compiler
 * 
 * Compiles Core-PLIx to IRPlan (Intermediate Representation Plan) for APOE execution
 * This is the primary execution backend
 * Based on pipeline_specification.md
 */

import type { PLIxIntent } from '../models/schema';
import type { Dist } from '../semantics/subdistribution';
import type { TypeJudgment, EffectRow } from '../semantics/annotated-typing';

/**
 * IRPlan Structure
 */
export interface IRPlan {
  /** Plan metadata */
  metadata: {
    name: string;
    intent: string;
    compiledAt: string;
    version: string;
  };
  
  /** State variables */
  state: IRStateDefinition;
  
  /** Steps (tasks) */
  steps: IRStep[];
  
  /** Dependencies (DAG edges) */
  dependencies: Map<string, string[]>;
  
  /** Compensation actions */
  compensations: Map<string, IRCompensation>;
  
  /** Contract */
  contract: IRContract;
  
  /** Execution strategy */
  strategy: {
    parallel?: boolean;
    maxConcurrency?: number;
    timeout?: number;
  };
}

export interface IRStateDefinition {
  variables: Array<{ name: string; type: string; initialValue?: any }>;
}

export interface IRStep {
  id: string;
  action: string; // Action identifier
  params: Record<string, any>;
  effects: EffectRow;
  confidence: number;
  retry?: {
    maxAttempts: number;
    backoff: 'linear' | 'exponential' | 'fixed';
    minDelay: number;
    maxDelay: number;
  };
  fallback?: string; // Fallback step ID
  timeout?: number;
  idempotent: boolean;
}

export interface IRCompensation {
  stepId: string;
  action: string;
  params: Record<string, any>;
  confidence: number;
}

export interface IRContract {
  preconditions: Array<{ expr: string; pure: boolean }>;
  postconditions: Array<{ expr: string; pure: boolean }>;
  invariants: Array<{ expr: string; pure: boolean }>;
}

/**
 * IRPlan Backend Compiler
 */
export class IRPlanBackend {
  /**
   * Compile PLIx intent to IRPlan
   */
  compile(intent: PLIxIntent, typeJudgment?: TypeJudgment): IRPlan {
    const metadata = this.generateMetadata(intent);
    const state = this.generateState(intent);
    const steps = this.generateSteps(intent, typeJudgment);
    const dependencies = this.generateDependencies(intent);
    const compensations = this.generateCompensations(intent);
    const contract = this.generateContract(intent);
    const strategy = this.generateStrategy(intent);
    
    return {
      metadata,
      state,
      steps,
      dependencies,
      compensations,
      contract,
      strategy
    };
  }
  
  /**
   * Generate metadata
   */
  private generateMetadata(intent: PLIxIntent): IRPlan['metadata'] {
    const entity = (intent as any).entity || 'intent';
    const name = entity.split('/').pop() || 'intent';
    
    return {
      name,
      intent: intent.intent,
      compiledAt: new Date().toISOString(),
      version: '1.0.0'
    };
  }
  
  /**
   * Generate state definition
   */
  private generateState(intent: PLIxIntent): IRStateDefinition {
    const variables: IRStateDefinition['variables'] = [];
    
    // Extract variables from contract
    for (const pre of intent.contract.pre) {
      const varName = this.extractVariableName(pre);
      if (varName) {
        variables.push({ name: varName, type: 'boolean', initialValue: true });
      }
    }
    
    for (const post of intent.contract.post) {
      const varName = this.extractVariableName(post);
      if (varName) {
        variables.push({ name: varName, type: 'boolean', initialValue: false });
      }
    }
    
    // Add step state variables
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      variables.push({ name: `${stepId}_state`, type: 'string', initialValue: 'pending' });
      variables.push({ name: `${stepId}_result`, type: 'any', initialValue: null });
    }
    
    return { variables };
  }
  
  /**
   * Generate steps
   */
  private generateSteps(intent: PLIxIntent, typeJudgment?: TypeJudgment): IRStep[] {
    const steps: IRStep[] = [];
    
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      
      // Infer effects from step
      const effects = this.inferEffects(step);
      
      // Get confidence (from metadata or default)
      const confidence = step.confidence_threshold || intent.telemetry.confidenceThresholds.minimum;
      
      // Build IR step
      const irStep: IRStep = {
        id: stepId,
        action: (step as any).action || step.tool || stepId,
        params: step.args || (step as any).params || {},
        effects,
        confidence,
        idempotent: effects.idempotent || false
      };
      
      // Add retry if specified
      if (step.retry) {
        irStep.retry = {
          maxAttempts: step.retry.max_attempts,
          backoff: step.retry.backoff,
          minDelay: this.parseDuration(step.retry.min_delay || '100ms'),
          maxDelay: this.parseDuration(step.retry.max_delay || '5s')
        };
      }
      
      // Add fallback if specified
      if (step.fallback) {
        irStep.fallback = step.fallback;
      }
      
      steps.push(irStep);
    }
    
    return steps;
  }
  
  /**
   * Generate dependencies map
   */
  private generateDependencies(intent: PLIxIntent): Map<string, string[]> {
    const dependencies = new Map<string, string[]>();
    
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      if (step.depends_on && step.depends_on.length > 0) {
        dependencies.set(stepId, step.depends_on);
      }
    }
    
    // Also check plan.deps array
    for (const dep of intent.plan.deps || []) {
      if (!dependencies.has(dep.step)) {
        dependencies.set(dep.step, dep.depends_on);
      }
    }
    
    return dependencies;
  }
  
  /**
   * Generate compensations
   */
  private generateCompensations(intent: PLIxIntent): Map<string, IRCompensation> {
    const compensations = new Map<string, IRCompensation>();
    
    for (const step of intent.plan.steps) {
      if (step.compensate) {
        const stepId = step.id || step.step;
        
        compensations.set(stepId, {
          stepId,
          action: (step.compensate as any).action || step.compensate.action || 'rollback_' + stepId,
          params: (step.compensate as any).params || step.compensate.args || {},
          confidence: 0.9 // Default high confidence for compensation
        });
      }
    }
    
    return compensations;
  }
  
  /**
   * Generate contract
   */
  private generateContract(intent: PLIxIntent): IRContract {
    const preconditions = intent.contract.pre.map(pre => ({
      expr: typeof pre === 'string' ? pre : pre.expr || String(pre),
      pure: true // Constraints are always pure
    }));
    
    const postconditions = intent.contract.post.map(post => ({
      expr: typeof post === 'string' ? post : post.expr || String(post),
      pure: true
    }));
    
    const invariants = (intent.contract.invariants || []).map(inv => ({
      expr: inv,
      pure: true
    }));
    
    return {
      preconditions,
      postconditions,
      invariants
    };
  }
  
  /**
   * Generate execution strategy
   */
  private generateStrategy(intent: PLIxIntent): IRPlan['strategy'] {
    return {
      parallel: false, // Default: sequential
      maxConcurrency: 1,
      timeout: intent.telemetry.timeouts.plan
    };
  }
  
  /**
   * Infer effects from step
   */
  private inferEffects(step: any): EffectRow {
    const effects: EffectRow = {};
    const toolName = (step.tool || step.id || '').toLowerCase();
    
    if (toolName.includes('read') || toolName.includes('write') || toolName.includes('file')) {
      effects.io = true;
    }
    
    if (toolName.includes('http') || toolName.includes('api') || toolName.includes('fetch')) {
      effects.net = true;
    }
    
    if (toolName.includes('db') || toolName.includes('query') || toolName.includes('sql')) {
      effects.db = true;
    }
    
    if (toolName.includes('read') || toolName.includes('get') || toolName.includes('query')) {
      effects.idempotent = true;
    }
    
    if (step.compensate) {
      effects.compensable = true;
    }
    
    return effects;
  }
  
  /**
   * Parse duration string to milliseconds
   */
  private parseDuration(duration: string): number {
    const match = duration.match(/^(\d+)(ms|s|m|h)$/);
    if (!match) return 1000; // Default 1s
    
    const [, value, unit] = match;
    const num = parseInt(value, 10);
    
    switch (unit) {
      case 'ms': return num;
      case 's': return num * 1000;
      case 'm': return num * 60 * 1000;
      case 'h': return num * 60 * 60 * 1000;
      default: return 1000;
    }
  }
  
  /**
   * Extract variable name from constraint
   */
  private extractVariableName(constraint: any): string | null {
    if (typeof constraint === 'string') {
      const match = constraint.match(/^([a-zA-Z_][a-zA-Z0-9_]*)/);
      return match ? match[1] : null;
    } else if (constraint.expr) {
      return constraint.expr;
    }
    
    return null;
  }
  
  /**
   * Serialize IRPlan to JSON
   */
  serializePlan(plan: IRPlan): string {
    // Convert Map to Object for JSON serialization
    const serializable = {
      ...plan,
      dependencies: Object.fromEntries(plan.dependencies),
      compensations: Object.fromEntries(plan.compensations)
    };
    
    return JSON.stringify(serializable, null, 2);
  }
  
  /**
   * Validate IRPlan structure
   */
  validate(plan: IRPlan): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check for circular dependencies
    const hasCycle = this.hasCircularDependency(plan.dependencies);
    if (hasCycle) {
      errors.push('Circular dependency detected in plan');
    }
    
    // Check all dependencies reference valid steps
    const stepIds = new Set(plan.steps.map(s => s.id));
    for (const [stepId, deps] of plan.dependencies.entries()) {
      if (!stepIds.has(stepId)) {
        errors.push(`Dependency references unknown step: ${stepId}`);
      }
      
      for (const dep of deps) {
        if (!stepIds.has(dep)) {
          errors.push(`Step '${stepId}' depends on unknown step '${dep}'`);
        }
      }
    }
    
    // Check all compensations reference valid steps
    for (const [stepId, _] of plan.compensations.entries()) {
      if (!stepIds.has(stepId)) {
        errors.push(`Compensation references unknown step: ${stepId}`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * Check for circular dependencies
   */
  private hasCircularDependency(dependencies: Map<string, string[]>): boolean {
    const visited = new Set<string>();
    const recStack = new Set<string>();
    
    const hasCycle = (node: string): boolean => {
      if (recStack.has(node)) return true;
      if (visited.has(node)) return false;
      
      visited.add(node);
      recStack.add(node);
      
      const deps = dependencies.get(node) || [];
      for (const dep of deps) {
        if (hasCycle(dep)) return true;
      }
      
      recStack.delete(node);
      return false;
    };
    
    for (const node of dependencies.keys()) {
      if (hasCycle(node)) return true;
    }
    
    return false;
  }
}

