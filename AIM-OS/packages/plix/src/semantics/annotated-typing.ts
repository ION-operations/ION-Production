/**
 * Annotated Typing System for PLIx
 * 
 * Implements Γ ⊢ t : T ! ε ▷ φ judgment
 * (Context Γ, term t has type T, effects ε, confidence φ)
 * 
 * Based on Core-PLIx Semantics v0.1 final
 */

/**
 * Effect Row (ε)
 * 
 * Row-polymorphic set of effects
 */
export interface EffectRow {
  io?: boolean;          // I/O effects
  net?: boolean;         // Network effects
  db?: boolean;          // Database effects
  compensable?: boolean; // Can be compensated
  idempotent?: boolean;  // Idempotent operation
  [key: string]: boolean | undefined; // Extensible
}

/**
 * Confidence Type (φ)
 * 
 * Bounded lattice [0, 1] with operations ⊔ (join/max) and ⊓ (meet/min)
 */
export type Confidence = number; // [0, 1]

/**
 * Type
 */
export type PLIXType =
  | { kind: 'primitive'; type: 'Bool' | 'Number' | 'String' | 'Unit' }
  | { kind: 'tag'; namespace: string; path: string }
  | { kind: 'entity'; entityType: string }
  | { kind: 'action'; actionType: string; effects: EffectRow; confidence: Confidence }
  | { kind: 'constraint'; returnType: 'Bool' }
  | { kind: 'plan'; inputType: PLIXType; outputType: PLIXType; effects: EffectRow }
  | { kind: 'intent'; contractType: PLIXType; planType: PLIXType };

/**
 * Typing Context (Γ)
 * 
 * Maps identifiers to types
 */
export class TypingContext {
  private bindings: Map<string, PLIXType>;
  
  constructor() {
    this.bindings = new Map();
  }
  
  /**
   * Bind identifier to type
   */
  bind(name: string, type: PLIXType): void {
    this.bindings.set(name, type);
  }
  
  /**
   * Lookup type of identifier
   */
  lookup(name: string): PLIXType | null {
    return this.bindings.get(name) || null;
  }
  
  /**
   * Check if identifier is bound
   */
  has(name: string): boolean {
    return this.bindings.has(name);
  }
  
  /**
   * Create child context (for scoping)
   */
  extend(): TypingContext {
    const child = new TypingContext();
    // Copy parent bindings
    for (const [name, type] of this.bindings.entries()) {
      child.bind(name, type);
    }
    return child;
  }
}

/**
 * Type Judgment (Γ ⊢ t : T ! ε ▷ φ)
 * 
 * In context Γ, term t has type T, effects ε, confidence φ
 */
export interface TypeJudgment {
  context: TypingContext;
  term: any; // Term being typed
  type: PLIXType;
  effects: EffectRow;
  confidence: Confidence;
  metadata?: Record<string, any>;
}

/**
 * Annotated Type Checker
 */
export class AnnotatedTypeChecker {
  /**
   * Check type of term and infer effects + confidence
   * 
   * Returns: Γ ⊢ t : T ! ε ▷ φ
   */
  check(context: TypingContext, term: any): TypeJudgment {
    // Determine term type based on structure
    if (typeof term === 'string') {
      return this.checkString(context, term);
    } else if (typeof term === 'number') {
      return this.checkNumber(context, term);
    } else if (typeof term === 'boolean') {
      return this.checkBoolean(context, term);
    } else if (term.type === 'constraint') {
      return this.checkConstraint(context, term);
    } else if (term.type === 'action') {
      return this.checkAction(context, term);
    } else if (term.type === 'plan') {
      return this.checkPlan(context, term);
    } else if (term.type === 'intent') {
      return this.checkIntent(context, term);
    } else {
      // Default: unknown type with no effects, low confidence
      return {
        context,
        term,
        type: { kind: 'primitive', type: 'Unit' },
        effects: {},
        confidence: 0.5,
        metadata: { unknown: true }
      };
    }
  }
  
  /**
   * Check string literal
   */
  private checkString(context: TypingContext, value: string): TypeJudgment {
    return {
      context,
      term: value,
      type: { kind: 'primitive', type: 'String' },
      effects: {}, // Pure
      confidence: 1.0 // Certain
    };
  }
  
  /**
   * Check number literal
   */
  private checkNumber(context: TypingContext, value: number): TypeJudgment {
    return {
      context,
      term: value,
      type: { kind: 'primitive', type: 'Number' },
      effects: {},
      confidence: 1.0
    };
  }
  
  /**
   * Check boolean literal
   */
  private checkBoolean(context: TypingContext, value: boolean): TypeJudgment {
    return {
      context,
      term: value,
      type: { kind: 'primitive', type: 'Bool' },
      effects: {},
      confidence: 1.0
    };
  }
  
  /**
   * Check constraint
   * 
   * Constraints must be pure (effects = ∅) and return Bool
   */
  private checkConstraint(context: TypingContext, constraint: any): TypeJudgment {
    const judgment: TypeJudgment = {
      context,
      term: constraint,
      type: { kind: 'constraint', returnType: 'Bool' },
      effects: {}, // Constraints MUST be pure
      confidence: 1.0, // Constraints are deterministic
      metadata: { purity: 'enforced' }
    };
    
    // Validate purity
    if (this.hasEffects(constraint)) {
      throw new Error('Constraints must be pure (no side effects)');
    }
    
    return judgment;
  }
  
  /**
   * Check action
   * 
   * Actions have effects and confidence based on definition
   */
  private checkAction(context: TypingContext, action: any): TypeJudgment {
    // Infer effects from action type
    const effects = this.inferEffects(action);
    
    // Infer confidence from action metadata
    const confidence = action.confidence || 0.85; // Default
    
    return {
      context,
      term: action,
      type: {
        kind: 'action',
        actionType: action.id || action.name || 'unknown',
        effects,
        confidence
      },
      effects,
      confidence
    };
  }
  
  /**
   * Check plan
   * 
   * Plan effects = union of all step effects
   * Plan confidence = minimum over all execution paths
   */
  private checkPlan(context: TypingContext, plan: any): TypeJudgment {
    const steps = plan.steps || [];
    
    // Check each step
    const stepJudgments = steps.map((step: any) => this.check(context, step));
    
    // Union all effects
    const effects = this.unionEffects(stepJudgments.map(j => j.effects));
    
    // Minimum confidence (conservative)
    const confidence = Math.min(...stepJudgments.map(j => j.confidence), 1.0);
    
    return {
      context,
      term: plan,
      type: {
        kind: 'plan',
        inputType: { kind: 'primitive', type: 'Unit' }, // Simplified
        outputType: { kind: 'primitive', type: 'Unit' },
        effects
      },
      effects,
      confidence,
      metadata: {
        stepCount: steps.length,
        stepJudgments: stepJudgments.length
      }
    };
  }
  
  /**
   * Check intent
   * 
   * Intent combines contract + plan
   */
  private checkIntent(context: TypingContext, intent: any): TypeJudgment {
    // Check contract (preconditions + postconditions)
    const contractJudgment = this.checkContract(context, intent.contract);
    
    // Check plan
    const planJudgment = this.checkPlan(context, intent.plan);
    
    // Intent effects = plan effects (contract is pure)
    const effects = planJudgment.effects;
    
    // Intent confidence = min(contract, plan)
    const confidence = Math.min(contractJudgment.confidence, planJudgment.confidence);
    
    return {
      context,
      term: intent,
      type: {
        kind: 'intent',
        contractType: contractJudgment.type,
        planType: planJudgment.type
      },
      effects,
      confidence
    };
  }
  
  /**
   * Check contract (preconditions + postconditions)
   * 
   * Contracts are pure (all constraints pure)
   */
  private checkContract(context: TypingContext, contract: any): TypeJudgment {
    const pre = contract.pre || [];
    const post = contract.post || [];
    
    // Check all constraints
    const preJudgments = pre.map((c: any) => this.checkConstraint(context, c));
    const postJudgments = post.map((c: any) => this.checkConstraint(context, c));
    
    // All should be pure
    const allPure = [...preJudgments, ...postJudgments].every(j => 
      Object.keys(j.effects).length === 0
    );
    
    if (!allPure) {
      throw new Error('Contract constraints must be pure');
    }
    
    return {
      context,
      term: contract,
      type: { kind: 'primitive', type: 'Bool' }, // Contract evaluates to Bool
      effects: {}, // Pure
      confidence: 1.0 // Deterministic
    };
  }
  
  /**
   * Infer effects from action
   */
  private inferEffects(action: any): EffectRow {
    const effects: EffectRow = {};
    
    // Infer from action name/tool
    const actionName = (action.tool || action.id || '').toLowerCase();
    
    if (actionName.includes('read') || actionName.includes('write') || actionName.includes('file')) {
      effects.io = true;
    }
    
    if (actionName.includes('http') || actionName.includes('api') || actionName.includes('fetch')) {
      effects.net = true;
    }
    
    if (actionName.includes('db') || actionName.includes('query') || actionName.includes('insert')) {
      effects.db = true;
    }
    
    // Check for idempotence markers
    if (action.idempotent === true) {
      effects.idempotent = true;
    }
    
    // Check for compensation
    if (action.compensation || action.compensate) {
      effects.compensable = true;
    }
    
    return effects;
  }
  
  /**
   * Check if term has effects
   */
  private hasEffects(term: any): boolean {
    // Simplified - full implementation would analyze term structure
    const effects = this.inferEffects(term);
    return Object.keys(effects).some(key => effects[key] === true);
  }
  
  /**
   * Union of effect rows (ε₁ ∪ ε₂)
   */
  private unionEffects(effectRows: EffectRow[]): EffectRow {
    const union: EffectRow = {};
    
    for (const row of effectRows) {
      for (const [key, value] of Object.entries(row)) {
        if (value === true) {
          union[key] = true;
        }
      }
    }
    
    return union;
  }
}

/**
 * Effect Row Operations
 */
export class EffectRowOps {
  /**
   * Check if ε₁ ⊆ ε₂ (effect subtyping)
   * 
   * ε₁ is a subeffect of ε₂ if all effects in ε₁ are present in ε₂
   */
  static isSubEffect(e1: EffectRow, e2: EffectRow): boolean {
    for (const [key, value] of Object.entries(e1)) {
      if (value === true && e2[key] !== true) {
        return false; // e1 has effect not in e2
      }
    }
    return true;
  }
  
  /**
   * Union of effects (ε₁ ∪ ε₂)
   */
  static union(e1: EffectRow, e2: EffectRow): EffectRow {
    const union: EffectRow = { ...e1 };
    
    for (const [key, value] of Object.entries(e2)) {
      if (value === true) {
        union[key] = true;
      }
    }
    
    return union;
  }
  
  /**
   * Intersection of effects (ε₁ ∩ ε₂)
   */
  static intersection(e1: EffectRow, e2: EffectRow): EffectRow {
    const intersection: EffectRow = {};
    
    for (const [key, value] of Object.entries(e1)) {
      if (value === true && e2[key] === true) {
        intersection[key] = true;
      }
    }
    
    return intersection;
  }
  
  /**
   * Check if effect row is empty (pure)
   */
  static isEmpty(e: EffectRow): boolean {
    return Object.values(e).every(v => v !== true);
  }
  
  /**
   * Check if effect row is idempotent
   */
  static isIdempotent(e: EffectRow): boolean {
    return e.idempotent === true;
  }
  
  /**
   * Check if effect row is compensable
   */
  static isCompensable(e: EffectRow): boolean {
    return e.compensable === true;
  }
}

/**
 * Confidence Lattice Operations
 */
export class ConfidenceLattice {
  /**
   * Join (⊔): Maximum confidence
   */
  static join(c1: Confidence, c2: Confidence): Confidence {
    return Math.max(c1, c2);
  }
  
  /**
   * Meet (⊓): Minimum confidence
   */
  static meet(c1: Confidence, c2: Confidence): Confidence {
    return Math.min(c1, c2);
  }
  
  /**
   * Bottom (⊥): No confidence
   */
  static bottom(): Confidence {
    return 0.0;
  }
  
  /**
   * Top (⊤): Full confidence
   */
  static top(): Confidence {
    return 1.0;
  }
  
  /**
   * Compare confidences
   */
  static compare(c1: Confidence, c2: Confidence): -1 | 0 | 1 {
    if (c1 < c2) return -1;
    if (c1 > c2) return 1;
    return 0;
  }
  
  /**
   * Validate confidence in range [0, 1]
   */
  static validate(c: Confidence): boolean {
    return c >= 0 && c <= 1;
  }
  
  /**
   * Product of confidences (for sequential composition)
   */
  static product(confidences: Confidence[]): Confidence {
    return confidences.reduce((acc, c) => acc * c, 1.0);
  }
  
  /**
   * Minimum of confidences (conservative)
   */
  static minimum(confidences: Confidence[]): Confidence {
    if (confidences.length === 0) return 1.0;
    return Math.min(...confidences);
  }
}

/**
 * Type Checking Rules
 */
export class TypingRules {
  private typeChecker: AnnotatedTypeChecker;
  
  constructor() {
    this.typeChecker = new AnnotatedTypeChecker();
  }
  
  /**
   * Rule: TAG-RESOLVE
   * 
   * Γ, Σ ⊢ tag : Value ! {} ▷ φ_resolve
   */
  checkTagResolution(context: TypingContext, tag: string, resolveConfidence: Confidence): TypeJudgment {
    // Tags are pure (no effects) but have variable confidence based on resolution
    return {
      context,
      term: tag,
      type: { kind: 'tag', namespace: 'plix', path: tag },
      effects: {}, // Pure
      confidence: resolveConfidence
    };
  }
  
  /**
   * Rule: ACTION
   * 
   * Γ, Σ ⊢ action(id) : Action ! ε_action ▷ φ_action
   */
  checkActionInvocation(
    context: TypingContext,
    actionId: string,
    actionEffects: EffectRow,
    actionConfidence: Confidence
  ): TypeJudgment {
    return {
      context,
      term: { type: 'action', id: actionId },
      type: { kind: 'action', actionType: actionId, effects: actionEffects, confidence: actionConfidence },
      effects: actionEffects,
      confidence: actionConfidence
    };
  }
  
  /**
   * Rule: TASK
   * 
   * Γ ⊢ task id := action(params) : Task ! ε ▷ φ
   */
  checkTask(
    context: TypingContext,
    taskId: string,
    action: any,
    params: Record<string, any>
  ): TypeJudgment {
    // Check action
    const actionJudgment = this.typeChecker.check(context, action);
    
    // Task inherits action's effects and confidence
    return {
      context,
      term: { type: 'task', id: taskId, action, params },
      type: actionJudgment.type,
      effects: actionJudgment.effects,
      confidence: actionJudgment.confidence,
      metadata: { taskId, paramCount: Object.keys(params).length }
    };
  }
  
  /**
   * Rule: DEPENDS
   * 
   * Γ ⊢ depends t2 <- t1 : Dependency ! {} ▷ 1
   */
  checkDependency(context: TypingContext, dependent: string, dependency: string): TypeJudgment {
    // Dependencies are structural (no effects, certain)
    return {
      context,
      term: { type: 'depends', dependent, dependency },
      type: { kind: 'primitive', type: 'Unit' },
      effects: {}, // Pure
      confidence: 1.0 // Certain
    };
  }
  
  /**
   * Rule: RETRY
   * 
   * Γ ⊢ retry task n backoff : Retry ! ε_task ▷ φ_task^n
   * 
   * Note: Confidence decreases with retries (φ^n = product)
   */
  checkRetry(
    context: TypingContext,
    taskId: string,
    maxAttempts: number,
    taskEffects: EffectRow,
    taskConfidence: Confidence
  ): TypeJudgment {
    // Retry inherits task effects
    // Confidence increases with retries if idempotent
    const isIdempotent = EffectRowOps.isIdempotent(taskEffects);
    
    const retryConfidence = isIdempotent
      ? 1 - Math.pow(1 - taskConfidence, maxAttempts) // P(success in n tries)
      : taskConfidence; // Conservative: same as single attempt
    
    return {
      context,
      term: { type: 'retry', taskId, maxAttempts },
      type: { kind: 'primitive', type: 'Unit' },
      effects: taskEffects, // Same effects as task
      confidence: retryConfidence
    };
  }
  
  /**
   * Rule: COMPENSATE
   * 
   * Γ ⊢ compensate task -> comp_action : Compensation ! ε_comp ▷ φ_comp
   */
  checkCompensation(
    context: TypingContext,
    taskId: string,
    compAction: any,
    compEffects: EffectRow,
    compConfidence: Confidence
  ): TypeJudgment {
    return {
      context,
      term: { type: 'compensate', taskId, compAction },
      type: { kind: 'primitive', type: 'Unit' },
      effects: compEffects,
      confidence: compConfidence,
      metadata: { compensable: true }
    };
  }
}

/**
 * Capability Gating
 */
export class CapabilityGating {
  /**
   * Check if action is allowed given context capabilities
   * 
   * allowed_effects(context) ⊇ eff(action)
   */
  static checkCapability(
    allowedEffects: EffectRow,
    actionEffects: EffectRow
  ): { allowed: boolean; violations: string[] } {
    const violations: string[] = [];
    
    for (const [effect, required] of Object.entries(actionEffects)) {
      if (required === true && allowedEffects[effect] !== true) {
        violations.push(effect);
      }
    }
    
    return {
      allowed: violations.length === 0,
      violations
    };
  }
  
  /**
   * Filter actions by capabilities
   */
  static filterByCapabilities(
    actions: Array<{ effects: EffectRow; [key: string]: any }>,
    allowedEffects: EffectRow
  ): Array<{ effects: EffectRow; [key: string]: any }> {
    return actions.filter(action => {
      const check = this.checkCapability(allowedEffects, action.effects);
      return check.allowed;
    });
  }
}

/**
 * Export for convenience
 */
export {
  AnnotatedTypeChecker as TypeChecker,
  TypingRules,
  CapabilityGating
};

