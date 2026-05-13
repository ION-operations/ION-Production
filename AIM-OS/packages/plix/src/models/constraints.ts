/**
 * PLIX Enhanced Constraint Types
 * 
 * Enhanced constraint language with logical operators, quantifiers, and temporal operators
 * Based on External AI Feedback (Perplexity, Grok)
 */

export type ComparisonOp = '==' | '!=' | '<=' | '>=' | '<' | '>';

export interface SimpleConstraint {
  type: 'simple';
  expr: string;
  op: ComparisonOp;
  value: string | number | boolean | null;
}

export interface LogicalConstraint {
  type: 'logical';
  operator: 'and' | 'or' | 'not';
  left: PLIXConstraint;
  right?: PLIXConstraint; // Optional for 'not'
}

export interface QuantifiedConstraint {
  type: 'quantified';
  quantifier: 'forall' | 'exists';
  variable: string;
  domain?: string; // Optional domain (e.g., "rows", "users")
  constraint: PLIXConstraint;
}

export interface TemporalConstraint {
  type: 'temporal';
  operator: 'eventually' | 'always' | 'within' | 'after' | 'before';
  constraint: PLIXConstraint;
  duration?: string; // Duration string (e.g., "5000ms", "2h")
  timeout?: string; // Timeout string for 'within'
}

export type PLIXConstraint =
  | SimpleConstraint
  | LogicalConstraint
  | QuantifiedConstraint
  | TemporalConstraint;

/**
 * Constraint evaluation helpers
 */
export const ConstraintEvaluator = {
  /** Evaluate simple constraint */
  evaluateSimple(constraint: SimpleConstraint, context: Record<string, any>): boolean {
    const leftValue = this.resolveValue(constraint.expr, context);
    const rightValue = constraint.value;
    
    switch (constraint.op) {
      case '==': return leftValue === rightValue;
      case '!=': return leftValue !== rightValue;
      case '<=': return leftValue <= rightValue;
      case '>=': return leftValue >= rightValue;
      case '<': return leftValue < rightValue;
      case '>': return leftValue > rightValue;
      default: return false;
    }
  },
  
  /** Evaluate logical constraint */
  evaluateLogical(constraint: LogicalConstraint, context: Record<string, any>): boolean {
    const leftResult = this.evaluate(constraint.left, context);
    
    if (constraint.operator === 'not') {
      return !leftResult;
    }
    
    if (!constraint.right) {
      return leftResult;
    }
    
    const rightResult = this.evaluate(constraint.right, context);
    
    switch (constraint.operator) {
      case 'and': return leftResult && rightResult;
      case 'or': return leftResult || rightResult;
      default: return false;
    }
  },
  
  /** Evaluate quantified constraint */
  evaluateQuantified(constraint: QuantifiedConstraint, context: Record<string, any>): boolean {
    const domain = constraint.domain 
      ? this.resolveValue(constraint.domain, context) 
      : context[constraint.variable] || [];
    
    if (!Array.isArray(domain)) {
      return false;
    }
    
    if (constraint.quantifier === 'forall') {
      return domain.every(item => {
        const itemContext = { ...context, [constraint.variable]: item };
        return this.evaluate(constraint.constraint, itemContext);
      });
    } else { // exists
      return domain.some(item => {
        const itemContext = { ...context, [constraint.variable]: item };
        return this.evaluate(constraint.constraint, itemContext);
      });
    }
  },
  
  /** Evaluate temporal constraint */
  evaluateTemporal(constraint: TemporalConstraint, context: Record<string, any>): boolean {
    // Temporal constraints require runtime evaluation with time tracking
    // This is a placeholder - actual implementation would track time and evaluate constraints
    const baseResult = this.evaluate(constraint.constraint, context);
    
    switch (constraint.operator) {
      case 'always':
        // Always true means constraint must hold at all times
        return baseResult;
      case 'eventually':
        // Eventually true means constraint will hold within duration
        return baseResult; // Simplified - actual would track time
      case 'within':
        // Must be true within duration
        return baseResult; // Simplified - actual would track time
      case 'after':
        // Must be true after duration
        return baseResult; // Simplified - actual would track time
      case 'before':
        // Must be true before duration
        return baseResult; // Simplified - actual would track time
      default:
        return false;
    }
  },
  
  /** Evaluate any constraint */
  evaluate(constraint: PLIXConstraint, context: Record<string, any>): boolean {
    switch (constraint.type) {
      case 'simple':
        return this.evaluateSimple(constraint, context);
      case 'logical':
        return this.evaluateLogical(constraint, context);
      case 'quantified':
        return this.evaluateQuantified(constraint, context);
      case 'temporal':
        return this.evaluateTemporal(constraint, context);
      default:
        return false;
    }
  },
  
  /** Resolve value from context */
  resolveValue(expr: string, context: Record<string, any>): any {
    // Simple property access (e.g., "user_authenticated")
    if (expr in context) {
      return context[expr];
    }
    
    // Nested property access (e.g., "user.role")
    const parts = expr.split('.');
    let value = context;
    for (const part of parts) {
      if (value && typeof value === 'object' && part in value) {
        value = value[part];
      } else {
        return undefined;
      }
    }
    
    return value;
  },
  
  /** Parse constraint string to PLIXConstraint */
  parse(constraintStr: string): PLIXConstraint | null {
    // This is a simplified parser - full implementation would use proper grammar parsing
    // For now, return null to indicate parsing is needed
    return null;
  },
  
  /** Format constraint to string */
  format(constraint: PLIXConstraint): string {
    switch (constraint.type) {
      case 'simple':
        return `${constraint.expr} ${constraint.op} ${constraint.value}`;
      case 'logical':
        if (constraint.operator === 'not') {
          return `NOT (${this.format(constraint.left)})`;
        }
        return `(${this.format(constraint.left)}) ${constraint.operator.toUpperCase()} (${constraint.right ? this.format(constraint.right) : ''})`;
      case 'quantified':
        const domainStr = constraint.domain ? ` in ${constraint.domain}` : '';
        return `${constraint.quantifier} ${constraint.variable}${domainStr}: ${this.format(constraint.constraint)}`;
      case 'temporal':
        const durationStr = constraint.duration ? `, ${constraint.duration}` : '';
        return `${constraint.operator}(${this.format(constraint.constraint)}${durationStr})`;
      default:
        return '';
    }
  }
};

