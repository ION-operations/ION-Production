/**
 * Annotated Typing System Tests
 * 
 * Tests for Γ ⊢ t : T ! ε ▷ φ judgment
 */

import {
  TypingContext,
  AnnotatedTypeChecker,
  TypingRules,
  EffectRowOps,
  ConfidenceLattice,
  CapabilityGating,
  type EffectRow,
  type Confidence,
  type TypeJudgment
} from '../annotated-typing';

describe('Typing Context (Γ)', () => {
  test('should bind and lookup types', () => {
    const ctx = new TypingContext();
    ctx.bind('x', { kind: 'primitive', type: 'Number' });
    
    const type = ctx.lookup('x');
    expect(type).toEqual({ kind: 'primitive', type: 'Number' });
  });
  
  test('should support scoping with extend', () => {
    const parent = new TypingContext();
    parent.bind('x', { kind: 'primitive', type: 'Number' });
    
    const child = parent.extend();
    child.bind('y', { kind: 'primitive', type: 'String' });
    
    expect(child.has('x')).toBe(true);
    expect(child.has('y')).toBe(true);
    expect(parent.has('y')).toBe(false);
  });
});

describe('Annotated Type Checker', () => {
  let checker: AnnotatedTypeChecker;
  let context: TypingContext;
  
  beforeEach(() => {
    checker = new AnnotatedTypeChecker();
    context = new TypingContext();
  });
  
  test('should check string literals', () => {
    const judgment = checker.check(context, 'hello');
    
    expect(judgment.type).toEqual({ kind: 'primitive', type: 'String' });
    expect(judgment.effects).toEqual({});
    expect(judgment.confidence).toBe(1.0);
  });
  
  test('should check number literals', () => {
    const judgment = checker.check(context, 42);
    
    expect(judgment.type).toEqual({ kind: 'primitive', type: 'Number' });
    expect(judgment.effects).toEqual({});
    expect(judgment.confidence).toBe(1.0);
  });
  
  test('should check boolean literals', () => {
    const judgment = checker.check(context, true);
    
    expect(judgment.type).toEqual({ kind: 'primitive', type: 'Bool' });
    expect(judgment.effects).toEqual({});
    expect(judgment.confidence).toBe(1.0);
  });
  
  test('should check constraints as pure', () => {
    const constraint = {
      type: 'constraint',
      expr: 'x == 1'
    };
    
    const judgment = checker.check(context, constraint);
    
    expect(judgment.type).toEqual({ kind: 'constraint', returnType: 'Bool' });
    expect(judgment.effects).toEqual({}); // Pure
    expect(judgment.confidence).toBe(1.0);
  });
  
  test('should check actions with effects', () => {
    const action = {
      type: 'action',
      id: 'api.query_db',
      tool: 'api.query_db'
    };
    
    const judgment = checker.check(context, action);
    
    expect(judgment.effects.db).toBe(true); // Inferred from name
    expect(judgment.confidence).toBeLessThan(1.0);
  });
  
  test('should check plan with multiple steps', () => {
    const plan = {
      type: 'plan',
      steps: [
        { type: 'action', id: 'read_file', tool: 'read_file' },
        { type: 'action', id: 'api_call', tool: 'http_fetch' }
      ]
    };
    
    const judgment = checker.check(context, plan);
    
    expect(judgment.effects.io).toBe(true); // From read_file
    expect(judgment.effects.net).toBe(true); // From http_fetch
    expect(judgment.confidence).toBeLessThan(1.0);
  });
  
  test('should check intent', () => {
    const intent = {
      type: 'intent',
      contract: {
        pre: [{ type: 'constraint', expr: 'x == 1' }],
        post: [{ type: 'constraint', expr: 'y == 2' }]
      },
      plan: {
        type: 'plan',
        steps: [
          { type: 'action', id: 'compute', tool: 'compute' }
        ]
      }
    };
    
    const judgment = checker.check(context, intent);
    
    expect(judgment.type.kind).toBe('intent');
    expect(judgment.confidence).toBeGreaterThan(0);
    expect(judgment.confidence).toBeLessThanOrEqual(1.0);
  });
});

describe('Effect Row Operations', () => {
  test('should check subeffect relationship', () => {
    const e1: EffectRow = { io: true };
    const e2: EffectRow = { io: true, net: true };
    
    expect(EffectRowOps.isSubEffect(e1, e2)).toBe(true);
    expect(EffectRowOps.isSubEffect(e2, e1)).toBe(false);
  });
  
  test('should compute union of effects', () => {
    const e1: EffectRow = { io: true, db: true };
    const e2: EffectRow = { net: true, db: true };
    
    const union = EffectRowOps.union(e1, e2);
    
    expect(union.io).toBe(true);
    expect(union.net).toBe(true);
    expect(union.db).toBe(true);
  });
  
  test('should compute intersection of effects', () => {
    const e1: EffectRow = { io: true, db: true };
    const e2: EffectRow = { net: true, db: true };
    
    const intersection = EffectRowOps.intersection(e1, e2);
    
    expect(intersection.db).toBe(true);
    expect(intersection.io).toBeUndefined();
    expect(intersection.net).toBeUndefined();
  });
  
  test('should check if empty (pure)', () => {
    expect(EffectRowOps.isEmpty({})).toBe(true);
    expect(EffectRowOps.isEmpty({ io: true })).toBe(false);
  });
  
  test('should check idempotence', () => {
    expect(EffectRowOps.isIdempotent({ idempotent: true })).toBe(true);
    expect(EffectRowOps.isIdempotent({})).toBe(false);
  });
});

describe('Confidence Lattice', () => {
  test('should compute join (max)', () => {
    expect(ConfidenceLattice.join(0.7, 0.9)).toBe(0.9);
    expect(ConfidenceLattice.join(0.3, 0.5)).toBe(0.5);
  });
  
  test('should compute meet (min)', () => {
    expect(ConfidenceLattice.meet(0.7, 0.9)).toBe(0.7);
    expect(ConfidenceLattice.meet(0.3, 0.5)).toBe(0.3);
  });
  
  test('should have bottom (0) and top (1)', () => {
    expect(ConfidenceLattice.bottom()).toBe(0.0);
    expect(ConfidenceLattice.top()).toBe(1.0);
  });
  
  test('should validate confidence range', () => {
    expect(ConfidenceLattice.validate(0.5)).toBe(true);
    expect(ConfidenceLattice.validate(-0.1)).toBe(false);
    expect(ConfidenceLattice.validate(1.1)).toBe(false);
  });
  
  test('should compute product of confidences', () => {
    const product = ConfidenceLattice.product([0.9, 0.8, 0.7]);
    expect(product).toBeCloseTo(0.504);
  });
  
  test('should compute minimum of confidences', () => {
    const min = ConfidenceLattice.minimum([0.9, 0.7, 0.8]);
    expect(min).toBe(0.7);
  });
});

describe('Typing Rules', () => {
  let rules: TypingRules;
  let context: TypingContext;
  
  beforeEach(() => {
    rules = new TypingRules();
    context = new TypingContext();
  });
  
  test('should check tag resolution', () => {
    const judgment = rules.checkTagResolution(context, 'plix://test/entity', 0.9);
    
    expect(judgment.type.kind).toBe('tag');
    expect(judgment.effects).toEqual({});
    expect(judgment.confidence).toBe(0.9);
  });
  
  test('should check action invocation', () => {
    const effects: EffectRow = { io: true, db: true };
    const judgment = rules.checkActionInvocation(context, 'api.query', effects, 0.85);
    
    expect(judgment.type.kind).toBe('action');
    expect(judgment.effects).toEqual(effects);
    expect(judgment.confidence).toBe(0.85);
  });
  
  test('should check task', () => {
    const action = { type: 'action', id: 'compute', tool: 'compute' };
    const judgment = rules.checkTask(context, 'task1', action, { param1: 'value1' });
    
    expect(judgment.metadata?.taskId).toBe('task1');
    expect(judgment.metadata?.paramCount).toBe(1);
  });
  
  test('should check dependency as pure', () => {
    const judgment = rules.checkDependency(context, 'task2', 'task1');
    
    expect(judgment.effects).toEqual({});
    expect(judgment.confidence).toBe(1.0);
  });
  
  test('should check retry with confidence increase for idempotent', () => {
    const effects: EffectRow = { io: true, idempotent: true };
    const judgment = rules.checkRetry(context, 'task1', 3, effects, 0.7);
    
    // Confidence should increase: 1 - (1-0.7)^3 = 1 - 0.027 = 0.973
    expect(judgment.confidence).toBeGreaterThan(0.7);
    expect(judgment.confidence).toBeCloseTo(0.973, 2);
  });
  
  test('should check retry with same confidence for non-idempotent', () => {
    const effects: EffectRow = { net: true };
    const judgment = rules.checkRetry(context, 'task1', 3, effects, 0.7);
    
    // Confidence stays same (conservative)
    expect(judgment.confidence).toBe(0.7);
  });
  
  test('should check compensation', () => {
    const compAction = { type: 'action', id: 'rollback', tool: 'rollback' };
    const compEffects: EffectRow = { db: true, compensable: true };
    const judgment = rules.checkCompensation(context, 'task1', compAction, compEffects, 0.9);
    
    expect(judgment.metadata?.compensable).toBe(true);
    expect(judgment.effects).toEqual(compEffects);
    expect(judgment.confidence).toBe(0.9);
  });
});

describe('Capability Gating', () => {
  test('should allow action when capabilities match', () => {
    const allowedEffects: EffectRow = { io: true, net: true, db: true };
    const actionEffects: EffectRow = { io: true, db: true };
    
    const result = CapabilityGating.checkCapability(allowedEffects, actionEffects);
    
    expect(result.allowed).toBe(true);
    expect(result.violations).toHaveLength(0);
  });
  
  test('should deny action when capabilities insufficient', () => {
    const allowedEffects: EffectRow = { io: true };
    const actionEffects: EffectRow = { io: true, net: true, db: true };
    
    const result = CapabilityGating.checkCapability(allowedEffects, actionEffects);
    
    expect(result.allowed).toBe(false);
    expect(result.violations).toContain('net');
    expect(result.violations).toContain('db');
  });
  
  test('should filter actions by capabilities', () => {
    const allowedEffects: EffectRow = { io: true, db: true };
    const actions = [
      { id: 'action1', effects: { io: true } },
      { id: 'action2', effects: { io: true, net: true } }, // Should be filtered out
      { id: 'action3', effects: { db: true } }
    ];
    
    const filtered = CapabilityGating.filterByCapabilities(actions, allowedEffects);
    
    expect(filtered).toHaveLength(2);
    expect(filtered[0].id).toBe('action1');
    expect(filtered[1].id).toBe('action3');
  });
});

describe('Integration Tests', () => {
  test('should type check complete intent', () => {
    const checker = new AnnotatedTypeChecker();
    const context = new TypingContext();
    
    const intent = {
      type: 'intent',
      contract: {
        pre: [{ type: 'constraint', expr: 'authenticated == true' }],
        post: [{ type: 'constraint', expr: 'result_valid == true' }]
      },
      plan: {
        type: 'plan',
        steps: [
          { type: 'action', id: 'auth', tool: 'api_check_auth' },
          { type: 'action', id: 'query', tool: 'db_query' }
        ]
      }
    };
    
    const judgment = checker.check(context, intent);
    
    expect(judgment.type.kind).toBe('intent');
    expect(judgment.effects.net).toBe(true); // From api_check_auth
    expect(judgment.effects.db).toBe(true); // From db_query
    expect(judgment.confidence).toBeGreaterThan(0);
    expect(judgment.confidence).toBeLessThanOrEqual(1.0);
  });
  
  test('should enforce purity for constraints', () => {
    const checker = new AnnotatedTypeChecker();
    const context = new TypingContext();
    
    const constraint = {
      type: 'constraint',
      expr: 'x == 1'
    };
    
    const judgment = checker.check(context, constraint);
    
    expect(judgment.effects).toEqual({}); // Pure
    expect(judgment.confidence).toBe(1.0); // Deterministic
  });
});

