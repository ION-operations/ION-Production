/**
 * Subdistribution Monad Tests
 * 
 * Tests for probabilistic semantics of retry/fallback/compensation
 */

import {
  Dist,
  Retry,
  Fallback,
  Compensate,
  Plan,
  DistUtils,
  type Dist as DistType
} from '../subdistribution';

describe('Subdistribution Monad', () => {
  describe('Unit (η)', () => {
    test('should create certain distribution', () => {
      const dist = Dist.unit(42);
      
      expect(dist.pmf.get(42)).toBe(1.0);
      expect(dist.totalMass).toBe(1.0);
    });
    
    test('should work with any type', () => {
      const dist = Dist.unit({ value: 'test' });
      
      expect(dist.pmf.size).toBe(1);
      expect(dist.totalMass).toBe(1.0);
    });
  });
  
  describe('Bind (>>=)', () => {
    test('should compose distributions', () => {
      const dist1 = Dist.unit(5);
      const dist2 = Dist.bind(dist1, (n) => Dist.unit(n * 2));
      
      expect(dist2.pmf.get(10)).toBe(1.0);
      expect(dist2.totalMass).toBe(1.0);
    });
    
    test('should preserve probability mass', () => {
      const dist1 = DistUtils.uniform([1, 2, 3]);
      const dist2 = Dist.bind(dist1, (n) => Dist.unit(n * n));
      
      expect(dist2.totalMass).toBeCloseTo(1.0);
      expect(dist2.pmf.get(1)).toBeCloseTo(1/3);
      expect(dist2.pmf.get(4)).toBeCloseTo(1/3);
      expect(dist2.pmf.get(9)).toBeCloseTo(1/3);
    });
    
    test('should handle subdistributions (mass < 1)', () => {
      const dist1: DistType<number> = {
        pmf: new Map([[1, 0.5]]),
        totalMass: 0.5
      };
      
      const dist2 = Dist.bind(dist1, (n) => Dist.unit(n * 2));
      
      expect(dist2.pmf.get(2)).toBeCloseTo(0.5);
      expect(dist2.totalMass).toBeCloseTo(0.5);
    });
  });
  
  describe('Map', () => {
    test('should apply function to values', () => {
      const dist1 = DistUtils.uniform([1, 2, 3]);
      const dist2 = Dist.map(dist1, (n) => n * 2);
      
      expect(dist2.pmf.get(2)).toBeCloseTo(1/3);
      expect(dist2.pmf.get(4)).toBeCloseTo(1/3);
      expect(dist2.pmf.get(6)).toBeCloseTo(1/3);
    });
  });
  
  describe('Fail', () => {
    test('should create empty distribution', () => {
      const dist = Dist.fail<number>();
      
      expect(dist.pmf.size).toBe(0);
      expect(dist.totalMass).toBe(0.0);
    });
  });
  
  describe('Choice', () => {
    test('should choose between distributions', () => {
      const dist1 = Dist.unit(1);
      const dist2 = Dist.unit(2);
      const dist3 = Dist.choice(dist1, dist2, 0.7);
      
      expect(dist3.pmf.get(1)).toBeCloseTo(0.7);
      expect(dist3.pmf.get(2)).toBeCloseTo(0.3);
      expect(dist3.totalMass).toBeCloseTo(1.0);
    });
  });
});

describe('Retry Semantics', () => {
  test('should model retry with max attempts', () => {
    const action = (s: number) => Dist.unit(s + 1);
    const retryAction = Retry.retry(action, 3, 0.5);
    
    const result = retryAction(0);
    
    // Should have successful outcomes
    expect(result.totalMass).toBeGreaterThan(0);
  });
  
  test('should fail after max attempts exhausted', () => {
    const action = (s: number) => Dist.fail<number>();
    const retryAction = Retry.retry(action, 0, 0.5);
    
    const result = retryAction(0);
    
    expect(result.totalMass).toBe(0);
  });
  
  test('should model idempotent retry correctly', () => {
    const action = (s: number) => Dist.unit(s + 1);
    const retryAction = Retry.retryIdempotent(action, 3, 0.5);
    
    const result = retryAction(0);
    
    // Total success prob = 1 - (1 - 0.5)^3 = 1 - 0.125 = 0.875
    expect(result.totalMass).toBeCloseTo(0.875, 1);
  });
});

describe('Fallback Semantics', () => {
  test('should choose primary if successful', () => {
    const primary = (s: number) => Dist.unit(s * 2);
    const alternative = (s: number) => Dist.unit(s * 3);
    const fallbackAction = Fallback.fallback(primary, alternative, 1.0);
    
    const result = fallbackAction(5);
    
    expect(result.pmf.get(10)).toBeCloseTo(1.0);
  });
  
  test('should use alternative if primary fails', () => {
    const primary = (s: number) => Dist.unit(s * 2);
    const alternative = (s: number) => Dist.unit(s * 3);
    const fallbackAction = Fallback.fallback(primary, alternative, 0.0);
    
    const result = fallbackAction(5);
    
    expect(result.pmf.get(15)).toBeCloseTo(1.0);
  });
  
  test('should handle fallback chain', () => {
    const actions = [
      (s: number) => Dist.unit(s + 1),
      (s: number) => Dist.unit(s + 2),
      (s: number) => Dist.unit(s + 3)
    ];
    const probs = [0.5, 0.3, 1.0]; // Last is guaranteed fallback
    
    const fallbackAction = Fallback.fallbackChain(actions, probs);
    const result = fallbackAction(0);
    
    expect(result.totalMass).toBeCloseTo(1.0);
  });
});

describe('Compensation Semantics', () => {
  test('should apply compensation after execution', () => {
    const exec = (s: number) => Dist.unit(s + 10);
    const comp = (s: number) => Dist.unit(s - 10);
    
    const compensated = Compensate.compensate(exec, comp);
    const result = compensated(5);
    
    // After exec: 15, after comp: 5 (left inverse)
    expect(result.pmf.get(5)).toBeCloseTo(1.0);
  });
  
  test('should handle saga pattern', () => {
    const actions = [
      (s: number) => Dist.unit(s + 1),
      (s: number) => Dist.unit(s + 2),
      (s: number) => Dist.unit(s + 3)
    ];
    const compensations = [
      (s: number) => Dist.unit(s - 1),
      (s: number) => Dist.unit(s - 2),
      (s: number) => Dist.unit(s - 3)
    ];
    
    const saga = Compensate.saga(actions, compensations);
    const result = saga(0);
    
    // If all succeed: 0 + 1 + 2 + 3 = 6
    // Compensation would bring back to 0 if triggered
    expect(result.totalMass).toBeGreaterThan(0);
  });
});

describe('Plan Semantics', () => {
  test('should compute plan semantics', () => {
    const steps = [
      { action: (s: number) => Dist.unit(s + 1) },
      { action: (s: number) => Dist.unit(s + 2) },
      { action: (s: number) => Dist.unit(s + 3) }
    ];
    const dependencies = new Map<number, number[]>([
      [1, [0]], // Step 1 depends on step 0
      [2, [1]]  // Step 2 depends on step 1
    ]);
    
    const planAction = Plan.computePlanSemantics(steps, dependencies);
    const result = planAction(0);
    
    // Final state: 0 + 1 + 2 + 3 = 6
    expect(result.pmf.get(6)).toBeCloseTo(1.0);
  });
  
  test('should handle retry in plan', () => {
    const steps = [
      {
        action: (s: number) => Dist.unit(s + 1),
        retry: { max: 3, successProb: 0.8 }
      }
    ];
    const dependencies = new Map<number, number[]>();
    
    const planAction = Plan.computePlanSemantics(steps, dependencies);
    const result = planAction(0);
    
    expect(result.totalMass).toBeGreaterThan(0);
  });
  
  test('should respect dependencies', () => {
    const executionOrder: number[] = [];
    
    const steps = [
      { action: (s: number) => { executionOrder.push(0); return Dist.unit(s + 1); } },
      { action: (s: number) => { executionOrder.push(1); return Dist.unit(s + 2); } },
      { action: (s: number) => { executionOrder.push(2); return Dist.unit(s + 3); } }
    ];
    const dependencies = new Map<number, number[]>([
      [2, [0, 1]] // Step 2 depends on steps 0 and 1
    ]);
    
    const planAction = Plan.computePlanSemantics(steps, dependencies);
    planAction(0);
    
    // Step 2 should execute after steps 0 and 1
    expect(executionOrder.indexOf(2)).toBeGreaterThan(executionOrder.indexOf(0));
    expect(executionOrder.indexOf(2)).toBeGreaterThan(executionOrder.indexOf(1));
  });
});

describe('Utility Functions', () => {
  test('should create uniform distribution', () => {
    const dist = DistUtils.uniform([1, 2, 3, 4]);
    
    expect(dist.pmf.get(1)).toBeCloseTo(0.25);
    expect(dist.pmf.get(2)).toBeCloseTo(0.25);
    expect(dist.pmf.get(3)).toBeCloseTo(0.25);
    expect(dist.pmf.get(4)).toBeCloseTo(0.25);
    expect(dist.totalMass).toBeCloseTo(1.0);
  });
  
  test('should create weighted distribution', () => {
    const dist = DistUtils.weighted([1, 2, 3], [1, 2, 3]);
    
    expect(dist.pmf.get(1)).toBeCloseTo(1/6);
    expect(dist.pmf.get(2)).toBeCloseTo(2/6);
    expect(dist.pmf.get(3)).toBeCloseTo(3/6);
    expect(dist.totalMass).toBeCloseTo(1.0);
  });
  
  test('should create Bernoulli distribution', () => {
    const dist = DistUtils.bernoulli('success', 'failure', 0.7);
    
    expect(dist.pmf.get('success')).toBeCloseTo(0.7);
    expect(dist.pmf.get('failure')).toBeCloseTo(0.3);
    expect(dist.totalMass).toBeCloseTo(1.0);
  });
  
  test('should compute expected value', () => {
    const dist = DistUtils.weighted([1, 2, 3], [1, 2, 3]);
    const expected = Plan.expectedValue(dist);
    
    // E[X] = 1*(1/6) + 2*(2/6) + 3*(3/6) = 1/6 + 4/6 + 9/6 = 14/6 ≈ 2.33
    expect(expected).toBeCloseTo(14/6, 1);
  });
  
  test('should compute success probability', () => {
    const dist = DistUtils.weighted([1, 2, 3, 4], [1, 1, 1, 1]);
    const successProb = Plan.successProbability(dist, (n) => n >= 3);
    
    // P(n >= 3) = P(3) + P(4) = 0.25 + 0.25 = 0.5
    expect(successProb).toBeCloseTo(0.5);
  });
  
  test('should sample from distribution', () => {
    const dist = DistUtils.uniform([1, 2, 3, 4, 5]);
    const sample = Plan.sample(dist);
    
    expect(sample).not.toBeNull();
    expect([1, 2, 3, 4, 5]).toContain(sample);
  });
  
  test('should return null when sampling from failure', () => {
    const dist = Dist.fail<number>();
    const sample = Plan.sample(dist);
    
    expect(sample).toBeNull();
  });
});

describe('Monad Laws', () => {
  test('left identity: unit(a) >>= f === f(a)', () => {
    const a = 42;
    const f = (n: number) => Dist.unit(n * 2);
    
    const lhs = Dist.bind(Dist.unit(a), f);
    const rhs = f(a);
    
    expect(lhs.pmf.get(84)).toBeCloseTo(rhs.pmf.get(84) || 0);
    expect(lhs.totalMass).toBeCloseTo(rhs.totalMass);
  });
  
  test('right identity: m >>= unit === m', () => {
    const m = DistUtils.uniform([1, 2, 3]);
    const result = Dist.bind(m, (n) => Dist.unit(n));
    
    expect(result.pmf.get(1)).toBeCloseTo(m.pmf.get(1) || 0);
    expect(result.pmf.get(2)).toBeCloseTo(m.pmf.get(2) || 0);
    expect(result.pmf.get(3)).toBeCloseTo(m.pmf.get(3) || 0);
    expect(result.totalMass).toBeCloseTo(m.totalMass);
  });
  
  test('associativity: (m >>= f) >>= g === m >>= (x => f(x) >>= g)', () => {
    const m = Dist.unit(1);
    const f = (n: number) => Dist.unit(n + 1);
    const g = (n: number) => Dist.unit(n * 2);
    
    const lhs = Dist.bind(Dist.bind(m, f), g);
    const rhs = Dist.bind(m, (x) => Dist.bind(f(x), g));
    
    expect(lhs.pmf.get(4)).toBeCloseTo(rhs.pmf.get(4) || 0);
    expect(lhs.totalMass).toBeCloseTo(rhs.totalMass);
  });
});

