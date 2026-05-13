/**
 * PLIX Constraint Parser
 * 
 * Parses constraint expressions into PLIXConstraint AST
 * Supports logical, quantified, and temporal operators
 */

import type { PLIXConstraint, SimpleConstraint, LogicalConstraint, QuantifiedConstraint, TemporalConstraint } from '../models/constraints';

export interface ConstraintParseResult {
  constraint: PLIXConstraint | null;
  errors: string[];
}

export class ConstraintParser {
  /**
   * Parse constraint expression string into PLIXConstraint
   */
  parse(expr: string): ConstraintParseResult {
    const errors: string[] = [];
    
    try {
      // Trim whitespace
      expr = expr.trim();
      
      // Check for logical operators
      if (expr.includes(' AND ') || expr.includes(' and ')) {
        return this.parseLogical(expr, 'and', errors);
      }
      
      if (expr.includes(' OR ') || expr.includes(' or ')) {
        return this.parseLogical(expr, 'or', errors);
      }
      
      if (expr.startsWith('NOT ') || expr.startsWith('not ') || expr.startsWith('!')) {
        return this.parseLogical(expr, 'not', errors);
      }
      
      // Check for quantified operators
      if (expr.startsWith('forall ') || expr.startsWith('FORALL ')) {
        return this.parseQuantified(expr, 'forall', errors);
      }
      
      if (expr.startsWith('exists ') || expr.startsWith('EXISTS ')) {
        return this.parseQuantified(expr, 'exists', errors);
      }
      
      // Check for temporal operators
      if (expr.startsWith('eventually') || expr.startsWith('EVENTUALLY')) {
        return this.parseTemporal(expr, 'eventually', errors);
      }
      
      if (expr.startsWith('always') || expr.startsWith('ALWAYS')) {
        return this.parseTemporal(expr, 'always', errors);
      }
      
      if (expr.startsWith('within') || expr.startsWith('WITHIN')) {
        return this.parseTemporal(expr, 'within', errors);
      }
      
      // Parse as simple constraint
      return this.parseSimple(expr, errors);
    } catch (error: any) {
      errors.push(`Parse error: ${error.message}`);
      return { constraint: null, errors };
    }
  }
  
  /**
   * Parse logical constraint (AND, OR, NOT)
   */
  private parseLogical(expr: string, operator: 'and' | 'or' | 'not', errors: string[]): ConstraintParseResult {
    if (operator === 'not') {
      // NOT constraint
      const innerExpr = expr.replace(/^(NOT|not|!)\s*\(?/, '').replace(/\)$/, '').trim();
      const innerResult = this.parse(innerExpr);
      
      if (innerResult.constraint) {
        return {
          constraint: {
            type: 'logical',
            operator: 'not',
            left: innerResult.constraint
          },
          errors: [...errors, ...innerResult.errors]
        };
      }
      
      return { constraint: null, errors: [...errors, ...innerResult.errors] };
    }
    
    // AND or OR constraint
    const opPattern = operator === 'and' ? /\s+(AND|and)\s+/ : /\s+(OR|or)\s+/;
    const match = expr.match(opPattern);
    
    if (!match) {
      errors.push(`Invalid ${operator} constraint: ${expr}`);
      return { constraint: null, errors };
    }
    
    const leftExpr = expr.substring(0, match.index).trim();
    const rightExpr = expr.substring(match.index! + match[0].length).trim();
    
    // Remove outer parentheses if present
    const cleanLeft = this.removeOuterParens(leftExpr);
    const cleanRight = this.removeOuterParens(rightExpr);
    
    const leftResult = this.parse(cleanLeft);
    const rightResult = this.parse(cleanRight);
    
    if (!leftResult.constraint || !rightResult.constraint) {
      errors.push(`Failed to parse ${operator} operands`);
      return { constraint: null, errors: [...errors, ...leftResult.errors, ...rightResult.errors] };
    }
    
    return {
      constraint: {
        type: 'logical',
        operator,
        left: leftResult.constraint,
        right: rightResult.constraint
      },
      errors: [...errors, ...leftResult.errors, ...rightResult.errors]
    };
  }
  
  /**
   * Parse quantified constraint (FORALL, EXISTS)
   */
  private parseQuantified(expr: string, quantifier: 'forall' | 'exists', errors: string[]): ConstraintParseResult {
    // Pattern: quantifier variable [in domain]: constraint
    const match = expr.match(/^(forall|FORALL|exists|EXISTS)\s+(\w+)(?:\s+in\s+(\w+))?\s*:\s*(.+)$/);
    
    if (!match) {
      errors.push(`Invalid ${quantifier} constraint: ${expr}`);
      return { constraint: null, errors };
    }
    
    const variable = match[2];
    const domain = match[3] || undefined;
    const constraintExpr = match[4].trim();
    
    const constraintResult = this.parse(constraintExpr);
    
    if (!constraintResult.constraint) {
      errors.push(`Failed to parse ${quantifier} constraint expression`);
      return { constraint: null, errors: [...errors, ...constraintResult.errors] };
    }
    
    return {
      constraint: {
        type: 'quantified',
        quantifier,
        variable,
        domain,
        constraint: constraintResult.constraint
      },
      errors: [...errors, ...constraintResult.errors]
    };
  }
  
  /**
   * Parse temporal constraint (eventually, always, within)
   */
  private parseTemporal(expr: string, operator: 'eventually' | 'always' | 'within', errors: string[]): ConstraintParseResult {
    // Pattern: operator(constraint, duration) or operator constraint within duration
    let constraintExpr: string;
    let duration: string | undefined;
    
    if (expr.includes('(') && expr.includes(')')) {
      // Function-style: eventually(constraint, duration)
      const match = expr.match(/^(eventually|always|within|EVENTUALLY|ALWAYS|WITHIN)\s*\(([^,]+)(?:,\s*([^)]+))?\)/);
      
      if (!match) {
        errors.push(`Invalid ${operator} constraint: ${expr}`);
        return { constraint: null, errors };
      }
      
      constraintExpr = match[2].trim();
      duration = match[3]?.trim();
    } else {
      // Natural language style: eventually constraint within duration
      const parts = expr.split(/\s+(within|WITHIN)\s+/i);
      
      if (parts.length === 3) {
        constraintExpr = parts[0].replace(/^(eventually|always|EVENTUALLY|ALWAYS)\s+/i, '').trim();
        duration = parts[2].trim();
      } else {
        constraintExpr = expr.replace(/^(eventually|always|within|EVENTUALLY|ALWAYS|WITHIN)\s+/i, '').trim();
      }
    }
    
    const constraintResult = this.parse(constraintExpr);
    
    if (!constraintResult.constraint) {
      errors.push(`Failed to parse ${operator} constraint expression`);
      return { constraint: null, errors: [...errors, ...constraintResult.errors] };
    }
    
    return {
      constraint: {
        type: 'temporal',
        operator,
        constraint: constraintResult.constraint,
        duration
      },
      errors: [...errors, ...constraintResult.errors]
    };
  }
  
  /**
   * Parse simple constraint (expr op value)
   */
  private parseSimple(expr: string, errors: string[]): ConstraintParseResult {
    // Pattern: identifier op value
    const operators = ['==', '!=', '<=', '>=', '<', '>'];
    
    for (const op of operators) {
      const index = expr.indexOf(op);
      if (index > 0) {
        const left = expr.substring(0, index).trim();
        const right = expr.substring(index + op.length).trim();
        
        // Parse right side value
        const value = this.parseValue(right);
        
        return {
          constraint: {
            type: 'simple',
            expr: left,
            op: op as any,
            value
          },
          errors
        };
      }
    }
    
    // Fallback: treat as boolean expression
    return {
      constraint: {
        type: 'simple',
        expr: expr,
        op: '==',
        value: true
      },
      errors
    };
  }
  
  /**
   * Parse value (string, number, boolean, null)
   */
  private parseValue(str: string): string | number | boolean | null {
    str = str.trim();
    
    // Boolean
    if (str === 'true' || str === 'True' || str === 'TRUE') return true;
    if (str === 'false' || str === 'False' || str === 'FALSE') return false;
    
    // Null
    if (str === 'null' || str === 'Null' || str === 'NULL' || str === 'none' || str === 'None') return null;
    
    // Number
    const numMatch = str.match(/^-?\d+(\.\d+)?$/);
    if (numMatch) {
      return parseFloat(str);
    }
    
    // String (remove quotes if present)
    if ((str.startsWith('"') && str.endsWith('"')) || (str.startsWith("'") && str.endsWith("'"))) {
      return str.slice(1, -1);
    }
    
    // Return as-is (identifier or tag)
    return str;
  }
  
  /**
   * Remove outer parentheses
   */
  private removeOuterParens(str: string): string {
    str = str.trim();
    if (str.startsWith('(') && str.endsWith(')')) {
      // Check if parentheses are balanced
      let depth = 0;
      for (let i = 0; i < str.length; i++) {
        if (str[i] === '(') depth++;
        if (str[i] === ')') depth--;
        if (depth === 0 && i < str.length - 1) {
          // Not outer parentheses
          return str;
        }
      }
      return str.slice(1, -1).trim();
    }
    return str;
  }
}

