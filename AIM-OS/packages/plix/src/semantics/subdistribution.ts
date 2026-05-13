/**
 * Subdistribution Monad for PLIx
 * 
 * Implements probabilistic semantics for retry/fallback/compensation
 * Based on Core-PLIx Semantics v0.1 final
 */

/**
 * Subdistribution over type A
 * 
 * A subdistribution is a probability distribution that may assign
 * total probability < 1, representing partial/non-terminating computations
 */
export interface Dist<A> {
  /** Probability mass function: value → probability */
  pmf: Map<A, number>;
  
  /** Total probability mass (may be < 1 for subdistributions) */
  totalMass: number;
  
  /** Metadata for debugging */
  metadata?: Record<string, any>;
}

/**
 * Subdistribution Monad Operations
 */
export class SubdistributionMonad {
  /**
   * Unit (η): Lift a value into a certain distribution
   * 
   * η(v) = distribution that returns v with probability 1
   */
  static unit<A>(value: A): Dist<A> {
    const pmf = new Map<A, number>();
    pmf.set(value, 1.0);
    
    return {
      pmf,
      totalMass: 1.0,
      metadata: { type: 'unit', value }
    };
  }
  
  /**
   * Bind (>>=): Monadic composition
   * 
   * bind(d, f) = for each value v with probability p in d,
   *              apply f(v) and scale by p
   * 
   * Type: Dist(A) × (A → Dist(B)) → Dist(B)
   */
  static bind<A, B>(dist: Dist<A>, f: (a: A) => Dist<B>): Dist<B> {
    const resultPmf = new Map<B, number>();
    let totalMass = 0;
    
    // For each value in input distribution
    for (const [value, prob] of dist.pmf.entries()) {
      // Apply function to get output distribution
      const innerDist = f(value);
      
      // Scale output distribution by input probability
      for (const [innerValue, innerProb] of innerDist.pmf.entries()) {
        const scaledProb = prob * innerProb;
        const currentProb = resultPmf.get(innerValue) || 0;
        resultPmf.set(innerValue, currentProb + scaledProb);
        totalMass += scaledProb;
      }
    }
    
    return {
      pmf: resultPmf,
      totalMass,
      metadata: { type: 'bind', inputMass: dist.totalMass }
    };
  }
  
  /**
   * Map: Apply function to distribution values
   * 
   * map(d, f) = { f(v) with probability p | v with probability p in d }
   */
  static map<A, B>(dist: Dist<A>, f: (a: A) => B): Dist<B> {
    const resultPmf = new Map<B, number>();
    
    for (const [value, prob] of dist.pmf.entries()) {
      const newValue = f(value);
      const currentProb = resultPmf.get(newValue) || 0;
      resultPmf.set(newValue, currentProb + prob);
    }
    
    return {
      pmf: resultPmf,
      totalMass: dist.totalMass,
      metadata: { type: 'map', source: dist.metadata }
    };
  }
  
  /**
   * Fail: Empty distribution (total mass = 0)
   * 
   * Represents complete failure
   */
  static fail<A>(): Dist<A> {
    return {
      pmf: new Map<A, number>(),
      totalMass: 0.0,
      metadata: { type: 'fail' }
    };
  }
  
  /**
   * Choice: Probabilistic choice between two distributions
   * 
   * choice(d1, d2, p) = d1 with probability p, d2 with probability (1-p)
   */
  static choice<A>(d1: Dist<A>, d2: Dist<A>, p: number): Dist<A> {
    if (p < 0 || p > 1) {
      throw new Error(`Invalid probability: ${p}`);
    }
    
    const resultPmf = new Map<A, number>();
    
    // Scale d1 by p
    for (const [value, prob] of d1.pmf.entries()) {
      const scaledProb = prob * p;
      const currentProb = resultPmf.get(value) || 0;
      resultPmf.set(value, currentProb + scaledProb);
    }
    
    // Scale d2 by (1-p)
    for (const [value, prob] of d2.pmf.entries()) {
      const scaledProb = prob * (1 - p);
      const currentProb = resultPmf.get(value) || 0;
      resultPmf.set(value, currentProb + scaledProb);
    }
    
    const totalMass = d1.totalMass * p + d2.totalMass * (1 - p);
    
    return {
      pmf: resultPmf,
      totalMass,
      metadata: { type: 'choice', p, d1Mass: d1.totalMass, d2Mass: d2.totalMass }
    };
  }
}

/**
 * Retry Semantics
 * 
 * Models retry with backoff as a subdistribution
 */
export class RetrySemantics {
  /**
   * Model retry with maximum attempts
   * 
   * retry(action, n) = 
   *   action with prob p_success, or
   *   retry(action, n-1) with prob (1-p_success) if n > 0, or
   *   fail with prob (1-p_success) if n = 0
   */
  static retry<S>(
    action: (state: S) => Dist<S>,
    maxAttempts: number,
    successProb: number
  ): (state: S) => Dist<S> {
    return (state: S): Dist<S> => {
      if (maxAttempts <= 0) {
        return SubdistributionMonad.fail();
      }
      
      // Try action
      const actionDist = action(state);
      
      // If max attempts reached, return action result
      if (maxAttempts === 1) {
        return actionDist;
      }
      
      // Otherwise, model retry
      // Success: action succeeds
      // Failure: retry with (maxAttempts - 1)
      const retryDist = this.retry(action, maxAttempts - 1, successProb);
      
      // Choose between success and retry based on success probability
      return SubdistributionMonad.choice(
        actionDist,
        SubdistributionMonad.bind(actionDist, retryDist),
        successProb
      );
    };
  }
  
  /**
   * Model retry with exponential backoff
   * 
   * Backoff increases delay but doesn't affect probability model
   * (delay is operational concern, not denotational)
   */
  static retryWithBackoff<S>(
    action: (state: S) => Dist<S>,
    maxAttempts: number,
    successProb: number,
    backoffType: 'linear' | 'exponential' | 'fixed'
  ): (state: S) => Dist<S> {
    // For denotational semantics, backoff type doesn't affect distribution
    // It only affects execution timing (operational semantics)
    return this.retry(action, maxAttempts, successProb);
  }
  
  /**
   * Model idempotent retry
   * 
   * For idempotent operations, retry is semantically equivalent to single execution
   * (but may have different probability of success)
   */
  static retryIdempotent<S>(
    action: (state: S) => Dist<S>,
    maxAttempts: number,
    successProbPerAttempt: number
  ): (state: S) => Dist<S> {
    return (state: S): Dist<S> => {
      // Total success probability increases with retries
      // P(success in n attempts) = 1 - (1 - p)^n
      const totalSuccessProb = 1 - Math.pow(1 - successProbPerAttempt, maxAttempts);
      
      // Model as single action with adjusted success probability
      const actionDist = action(state);
      const failDist = SubdistributionMonad.fail<S>();
      
      return SubdistributionMonad.choice(actionDist, failDist, totalSuccessProb);
    };
  }
}

/**
 * Fallback Semantics
 * 
 * Models fallback as choice between primary and alternative actions
 */
export class FallbackSemantics {
  /**
   * Model fallback
   * 
   * fallback(primary, alternative) =
   *   primary with prob p_primary_success, or
   *   alternative with prob (1 - p_primary_success)
   */
  static fallback<S>(
    primary: (state: S) => Dist<S>,
    alternative: (state: S) => Dist<S>,
    primarySuccessProb: number
  ): (state: S) => Dist<S> {
    return (state: S): Dist<S> => {
      const primaryDist = primary(state);
      const alternativeDist = alternative(state);
      
      return SubdistributionMonad.choice(
        primaryDist,
        alternativeDist,
        primarySuccessProb
      );
    };
  }
  
  /**
   * Model fallback chain
   * 
   * fallback([a1, a2, a3]) = try a1, else try a2, else try a3
   */
  static fallbackChain<S>(
    actions: Array<(state: S) => Dist<S>>,
    successProbs: number[]
  ): (state: S) => Dist<S> {
    if (actions.length !== successProbs.length) {
      throw new Error('Actions and success probabilities must have same length');
    }
    
    if (actions.length === 0) {
      return () => SubdistributionMonad.fail();
    }
    
    if (actions.length === 1) {
      return actions[0];
    }
    
    // Build chain recursively
    const [first, ...rest] = actions;
    const [firstProb, ...restProbs] = successProbs;
    
    const restChain = this.fallbackChain(rest, restProbs);
    
    return this.fallback(first, restChain, firstProb);
  }
}

/**
 * Compensation Semantics
 * 
 * Models compensation as reverse execution
 */
export class CompensationSemantics {
  /**
   * Model compensation
   * 
   * compensate(exec, comp) = 
   *   If exec succeeds: apply comp to reverse effects
   *   If exec fails: no compensation needed
   * 
   * Assumption A1 (left inverse): comp ∘ exec ≈ id
   */
  static compensate<S>(
    exec: (state: S) => Dist<S>,
    comp: (state: S) => Dist<S>
  ): (state: S) => Dist<S> {
    return (state: S): Dist<S> => {
      const execDist = exec(state);
      
      // Apply compensation to each outcome
      return SubdistributionMonad.bind(execDist, (resultState) => {
        return comp(resultState);
      });
    };
  }
  
  /**
   * Model saga pattern (compensation chain in reverse order)
   * 
   * saga([a1, a2, a3], [c1, c2, c3]) =
   *   Execute a1, a2, a3 in order
   *   If any fails, execute compensations in reverse: c(i-1), c(i-2), ..., c1
   */
  static saga<S>(
    actions: Array<(state: S) => Dist<S>>,
    compensations: Array<(state: S) => Dist<S>>
  ): (state: S) => Dist<S> {
    if (actions.length !== compensations.length) {
      throw new Error('Actions and compensations must have same length');
    }
    
    if (actions.length === 0) {
      return SubdistributionMonad.unit;
    }
    
    // Execute actions in order
    return (state: S): Dist<S> => {
      let currentDist = SubdistributionMonad.unit(state);
      const executed: number[] = []; // Track which actions executed
      
      for (let i = 0; i < actions.length; i++) {
        currentDist = SubdistributionMonad.bind(currentDist, (s) => {
          const actionDist = actions[i](s);
          
          // If action succeeds, mark as executed
          if (actionDist.totalMass > 0) {
            executed.push(i);
          }
          
          return actionDist;
        });
        
        // Check if we should compensate
        if (currentDist.totalMass < 0.5) { // Simplified failure check
          // Execute compensations in reverse order
          for (let j = executed.length - 1; j >= 0; j--) {
            const compIndex = executed[j];
            currentDist = SubdistributionMonad.bind(currentDist, compensations[compIndex]);
          }
          break;
        }
      }
      
      return currentDist;
    };
  }
}

/**
 * Plan Semantics
 * 
 * Computes denotational semantics of PLIx plans
 */
export class PlanSemantics {
  /**
   * Compute ⟦plan⟧: State → Dist(State)
   * 
   * Represents plan execution as subdistribution over final states
   */
  static computePlanSemantics<S>(
    steps: Array<{
      action: (state: S) => Dist<S>;
      retry?: { max: number; successProb: number };
      fallback?: (state: S) => Dist<S>;
      compensation?: (state: S) => Dist<S>;
    }>,
    dependencies: Map<number, number[]> // stepIndex → dependsOn indices
  ): (state: S) => Dist<S> {
    return (initialState: S): Dist<S> => {
      // Topological sort of steps (respecting dependencies)
      const sorted = this.topologicalSort(steps.length, dependencies);
      
      // Execute steps in order
      let currentDist = SubdistributionMonad.unit(initialState);
      
      for (const stepIndex of sorted) {
        const step = steps[stepIndex];
        
        currentDist = SubdistributionMonad.bind(currentDist, (state) => {
          let stepAction = step.action;
          
          // Wrap with retry if specified
          if (step.retry) {
            stepAction = RetrySemantics.retry(
              stepAction,
              step.retry.max,
              step.retry.successProb
            );
          }
          
          // Wrap with fallback if specified
          if (step.fallback) {
            stepAction = FallbackSemantics.fallback(
              stepAction,
              step.fallback,
              0.7 // Default primary success prob
            );
          }
          
          // Wrap with compensation if specified
          if (step.compensation) {
            stepAction = CompensationSemantics.compensate(
              stepAction,
              step.compensation
            );
          }
          
          return stepAction(state);
        });
      }
      
      return currentDist;
    };
  }
  
  /**
   * Topological sort of plan steps
   */
  private static topologicalSort(numSteps: number, dependencies: Map<number, number[]>): number[] {
    const sorted: number[] = [];
    const visited = new Set<number>();
    const temp = new Set<number>();
    
    const visit = (node: number): void => {
      if (temp.has(node)) {
        throw new Error(`Circular dependency detected at step ${node}`);
      }
      
      if (visited.has(node)) {
        return;
      }
      
      temp.add(node);
      
      // Visit dependencies first
      const deps = dependencies.get(node) || [];
      for (const dep of deps) {
        visit(dep);
      }
      
      temp.delete(node);
      visited.add(node);
      sorted.push(node);
    };
    
    // Visit all nodes
    for (let i = 0; i < numSteps; i++) {
      if (!visited.has(i)) {
        visit(i);
      }
    }
    
    return sorted;
  }
  
  /**
   * Compute expected value of distribution
   * 
   * E[d] = Σ v * p(v) for v in d
   */
  static expectedValue(dist: Dist<number>): number {
    let expected = 0;
    for (const [value, prob] of dist.pmf.entries()) {
      expected += value * prob;
    }
    return expected;
  }
  
  /**
   * Compute probability of success
   * 
   * P(success) = Σ p(v) for all v where success(v) = true
   */
  static successProbability<S>(dist: Dist<S>, success: (s: S) => boolean): number {
    let totalSuccessProb = 0;
    for (const [value, prob] of dist.pmf.entries()) {
      if (success(value)) {
        totalSuccessProb += prob;
      }
    }
    return totalSuccessProb;
  }
  
  /**
   * Sample from distribution (for testing/simulation)
   */
  static sample<A>(dist: Dist<A>): A | null {
    if (dist.totalMass === 0) {
      return null; // Failure
    }
    
    // Sample using cumulative probability
    const r = Math.random() * dist.totalMass;
    let cumulative = 0;
    
    for (const [value, prob] of dist.pmf.entries()) {
      cumulative += prob;
      if (r <= cumulative) {
        return value;
      }
    }
    
    // Shouldn't reach here, but return first value as fallback
    return dist.pmf.keys().next().value || null;
  }
}

/**
 * Utility functions for creating distributions
 */
export const DistUtils = {
  /**
   * Create uniform distribution over values
   */
  uniform<A>(values: A[]): Dist<A> {
    if (values.length === 0) {
      return SubdistributionMonad.fail();
    }
    
    const prob = 1.0 / values.length;
    const pmf = new Map<A, number>();
    
    for (const value of values) {
      pmf.set(value, prob);
    }
    
    return {
      pmf,
      totalMass: 1.0,
      metadata: { type: 'uniform', size: values.length }
    };
  },
  
  /**
   * Create weighted distribution
   */
  weighted<A>(values: A[], weights: number[]): Dist<A> {
    if (values.length !== weights.length) {
      throw new Error('Values and weights must have same length');
    }
    
    if (values.length === 0) {
      return SubdistributionMonad.fail();
    }
    
    const totalWeight = weights.reduce((sum, w) => sum + w, 0);
    const pmf = new Map<A, number>();
    
    for (let i = 0; i < values.length; i++) {
      pmf.set(values[i], weights[i] / totalWeight);
    }
    
    return {
      pmf,
      totalMass: 1.0,
      metadata: { type: 'weighted', totalWeight }
    };
  },
  
  /**
   * Create Bernoulli distribution (success/failure)
   */
  bernoulli<A>(successValue: A, failureValue: A, successProb: number): Dist<A> {
    const pmf = new Map<A, number>();
    pmf.set(successValue, successProb);
    pmf.set(failureValue, 1 - successProb);
    
    return {
      pmf,
      totalMass: 1.0,
      metadata: { type: 'bernoulli', p: successProb }
    };
  }
};

/**
 * Export for convenience
 */
export const Dist = SubdistributionMonad;
export const Retry = RetrySemantics;
export const Fallback = FallbackSemantics;
export const Compensate = CompensationSemantics;
export const Plan = PlanSemantics;

