/**
 * Effect System Tests
 * 
 * Tests for effect row checking and capability gating
 */

import {
  EffectChecker,
  PolicyEngine,
  EffectInference,
  EffectValidator,
  StandardPolicies,
  type EffectRow,
  type EffectPolicy
} from '../effect-system';

describe('Effect Checker', () => {
  let checker: EffectChecker;
  
  beforeEach(() => {
    checker = new EffectChecker();
  });
  
  test('should register and check context capabilities', () => {
    checker.registerContext('ctx1', { io: true, net: true });
    
    const result = checker.checkAction('ctx1', { io: true });
    
    expect(result.allowed).toBe(true);
    expect(result.violations).toHaveLength(0);
  });
  
  test('should deny action with insufficient capabilities', () => {
    checker.registerContext('ctx1', { io: true });
    
    const result = checker.checkAction('ctx1', { io: true, net: true, db: true });
    
    expect(result.allowed).toBe(false);
    expect(result.violations).toContain('net');
    expect(result.violations).toContain('db');
  });
  
  test('should check plan with multiple steps', () => {
    checker.registerContext('ctx1', { io: true, db: true });
    
    const steps = [
      { id: 'step1', effects: { io: true } },
      { id: 'step2', effects: { db: true } },
      { id: 'step3', effects: { net: true } } // Not allowed
    ];
    
    const result = checker.checkPlan('ctx1', steps);
    
    expect(result.allowed).toBe(false);
    expect(result.violations).toHaveLength(1);
    expect(result.violations[0].stepId).toBe('step3');
  });
  
  test('should allow empty effects (pure operations)', () => {
    checker.registerContext('ctx1', {});
    
    const result = checker.checkAction('ctx1', {});
    
    expect(result.allowed).toBe(true);
  });
});

describe('Policy Engine', () => {
  let engine: PolicyEngine;
  
  beforeEach(() => {
    engine = new PolicyEngine();
  });
  
  test('should register and check policies', () => {
    const policy: EffectPolicy = {
      allowed: ['io', 'db'],
      prohibited: ['net'],
      requiresApproval: []
    };
    
    engine.registerPolicy('policy1', policy);
    
    const result = engine.checkPolicy('policy1', { io: true, db: true });
    
    expect(result.compliant).toBe(true);
    expect(result.violations).toHaveLength(0);
  });
  
  test('should deny prohibited effects', () => {
    const policy: EffectPolicy = {
      allowed: ['io'],
      prohibited: ['net', 'db'],
      requiresApproval: []
    };
    
    engine.registerPolicy('policy1', policy);
    
    const result = engine.checkPolicy('policy1', { io: true, net: true });
    
    expect(result.compliant).toBe(false);
    expect(result.violations.length).toBeGreaterThan(0);
  });
  
  test('should flag effects requiring approval', () => {
    const policy: EffectPolicy = {
      allowed: ['io', 'db'],
      prohibited: [],
      requiresApproval: ['db']
    };
    
    engine.registerPolicy('policy1', policy);
    
    const result = engine.checkPolicy('policy1', { io: true, db: true });
    
    expect(result.compliant).toBe(true);
    expect(result.requiresApproval).toContain('db');
  });
});

describe('Standard Policies', () => {
  test('should provide read-only policy', () => {
    const policy = StandardPolicies.readOnly();
    
    expect(policy.allowed).toContain('io');
    expect(policy.prohibited).toContain('db');
    expect(policy.prohibited).toContain('net');
  });
  
  test('should provide standard policy', () => {
    const policy = StandardPolicies.standard();
    
    expect(policy.allowed).toContain('io');
    expect(policy.allowed).toContain('net');
    expect(policy.allowed).toContain('db');
  });
  
  test('should provide privileged policy', () => {
    const policy = StandardPolicies.privileged();
    
    expect(policy.allowed.length).toBeGreaterThan(3);
    expect(policy.prohibited).toHaveLength(0);
  });
  
  test('should provide restricted policy', () => {
    const policy = StandardPolicies.restricted();
    
    expect(policy.allowed).toHaveLength(0);
    expect(policy.prohibited.length).toBeGreaterThan(0);
  });
});

describe('Effect Inference', () => {
  test('should infer I/O effects from name', () => {
    const effects = EffectInference.inferFromName('read_file');
    
    expect(effects.io).toBe(true);
  });
  
  test('should infer network effects from name', () => {
    const effects = EffectInference.inferFromName('http_fetch');
    
    expect(effects.net).toBe(true);
  });
  
  test('should infer database effects from name', () => {
    const effects = EffectInference.inferFromName('db_query');
    
    expect(effects.db).toBe(true);
  });
  
  test('should infer idempotence from name', () => {
    const effects = EffectInference.inferFromName('read_data');
    
    expect(effects.idempotent).toBe(true);
  });
  
  test('should infer from metadata', () => {
    const effects = EffectInference.inferFromMetadata({ io: true, net: true });
    
    expect(effects.io).toBe(true);
    expect(effects.net).toBe(true);
  });
  
  test('should combine name and metadata inference', () => {
    const effects = EffectInference.infer('query', { db: true, idempotent: true });
    
    expect(effects.db).toBe(true);
    expect(effects.idempotent).toBe(true);
  });
});

describe('Effect Validator', () => {
  let validator: EffectValidator;
  
  beforeEach(() => {
    validator = new EffectValidator();
    
    // Register context
    validator.getEffectChecker().registerContext('test_ctx', { io: true, db: true });
    
    // Register policy
    validator.getPolicyEngine().registerPolicy('test_policy', {
      allowed: ['io', 'db'],
      prohibited: ['net'],
      requiresApproval: ['db']
    });
  });
  
  test('should validate intent with allowed effects', () => {
    const intent = {
      plan: {
        steps: [
          { id: 'step1', tool: 'read_file' },
          { id: 'step2', tool: 'db_query' }
        ]
      }
    };
    
    const result = validator.validateIntent(intent, 'test_ctx', 'test_policy');
    
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.warnings.length).toBeGreaterThan(0); // DB requires approval
  });
  
  test('should reject intent with prohibited effects', () => {
    const intent = {
      plan: {
        steps: [
          { id: 'step1', tool: 'http_fetch' } // Network prohibited
        ]
      }
    };
    
    const result = validator.validateIntent(intent, 'test_ctx', 'test_policy');
    
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });
  
  test('should validate pure intents', () => {
    const intent = {
      plan: {
        steps: [
          { id: 'step1', tool: 'compute', metadata: {} } // Pure
        ]
      }
    };
    
    const result = validator.validateIntent(intent, 'test_ctx', 'test_policy');
    
    expect(result.valid).toBe(true);
  });
});

describe('Integration: Complete Effect System', () => {
  test('should enforce capability gating end-to-end', () => {
    const validator = new EffectValidator();
    
    // Context: Only I/O allowed
    validator.getEffectChecker().registerContext('sandbox', { io: true });
    
    // Policy: Prohibits network and database
    validator.getPolicyEngine().registerPolicy('sandbox_policy', {
      allowed: ['io'],
      prohibited: ['net', 'db'],
      requiresApproval: []
    });
    
    // Intent with network operation
    const intent = {
      plan: {
        steps: [
          { id: 'step1', tool: 'read_file' }, // Allowed
          { id: 'step2', tool: 'api_call' }   // Prohibited
        ]
      }
    };
    
    const result = validator.validateIntent(intent, 'sandbox', 'sandbox_policy');
    
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.includes('step2'))).toBe(true);
  });
});

