/**
 * PLIX S-Form Parser
 * 
 * Parses S-expression format into Canonical JSON
 */

import type { PLIxIntent } from '../models/schema';
import type { PLIXConstraint } from '../models/constraints';
import type { ParseError } from './index';
import { ConstraintParser } from './constraint-parser';

export interface SFormParseResult {
  intent: PLIxIntent | null;
  errors: ParseError[];
}

export class SFormParser {
  private constraintParser: ConstraintParser;
  
  constructor() {
    this.constraintParser = new ConstraintParser();
  }
  
  /**
   * Parse S-form text into PLIxIntent
   */
  parse(sForm: string): SFormParseResult {
    const errors: ParseError[] = [];
    
    try {
      // Tokenize S-expressions
      const tokens = this.tokenize(sForm);
      
      // Parse tokens into AST
      const ast = this.parseTokens(tokens, errors);
      
      // Convert AST to PLIxIntent
      const intent = ast ? this.astToIntent(ast, errors) : null;
      
      return {
        intent,
        errors
      };
    } catch (error: any) {
      errors.push({
        line: 0,
        column: 0,
        message: `S-form parse error: ${error.message}`,
        suggestion: 'Check S-expression syntax'
      });
      
      return {
        intent: null,
        errors
      };
    }
  }
  
  /**
   * Tokenize S-form text
   */
  private tokenize(text: string): SFormToken[] {
    const tokens: SFormToken[] = [];
    const lines = text.split('\n');
    
    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];
      const trimmed = line.trim();
      
      if (!trimmed || trimmed.startsWith(';')) {
        continue; // Skip empty lines and comments
      }
      
      // Tokenize line
      const lineTokens = this.tokenizeLine(trimmed, lineNum + 1);
      tokens.push(...lineTokens);
    }
    
    return tokens;
  }
  
  /**
   * Tokenize a single line
   */
  private tokenizeLine(line: string, lineNum: number): SFormToken[] {
    const tokens: SFormToken[] = [];
    
    // Match S-expression patterns
    const patterns = [
      { pattern: /^\((\w+)/, type: 'open' as const },
      { pattern: /^\)/, type: 'close' as const },
      { pattern: /^(\w+):/, type: 'keyword' as const },
      { pattern: /^"([^"]*)"/, type: 'string' as const },
      { pattern: /^(-?\d+(\.\d+)?)/, type: 'number' as const },
      { pattern: /^(true|false|null)/, type: 'boolean' as const },
      { pattern: /^(\S+)/, type: 'identifier' as const }
    ];
    
    let remaining = line.trim();
    let column = 0;
    
    while (remaining.length > 0) {
      let matched = false;
      
      for (const { pattern, type } of patterns) {
        const match = remaining.match(pattern);
        if (match) {
          const value = match[1] || match[0];
          tokens.push({
            type,
            value,
            line: lineNum,
            column: column + line.indexOf(remaining)
          });
          
          remaining = remaining.substring(match[0].length).trim();
          column += match[0].length;
          matched = true;
          break;
        }
      }
      
      if (!matched) {
        // Skip whitespace
        const whitespace = remaining.match(/^\s+/);
        if (whitespace) {
          remaining = remaining.substring(whitespace[0].length);
          column += whitespace[0].length;
        } else {
          break; // Unknown token
        }
      }
    }
    
    return tokens;
  }
  
  /**
   * Parse tokens into AST
   */
  private parseTokens(tokens: SFormToken[], errors: ParseError[]): any {
    const ast: any = {
      speech: null,
      entity: null,
      action: null,
      with: {},
      pre: [],
      post: [],
      tests: [],
      evidence: [],
      bt: {},
      plan: []
    };
    
    let i = 0;
    const stack: any[] = [];
    
    while (i < tokens.length) {
      const token = tokens[i];
      
      if (token.type === 'open') {
        // Start new expression
        const expr: any = {
          type: token.value,
          children: []
        };
        
        if (stack.length > 0) {
          stack[stack.length - 1].children.push(expr);
        }
        
        stack.push(expr);
        i++;
      } else if (token.type === 'close') {
        // End current expression
        if (stack.length > 0) {
          const expr = stack.pop();
          
          // Process expression
          if (stack.length === 0) {
            // Top-level expression
            this.processExpression(expr, ast, errors);
          }
        }
        i++;
      } else if (token.type === 'keyword') {
        // Keyword-value pair
        const key = token.value;
        i++;
        
        if (i < tokens.length) {
          const valueToken = tokens[i];
          const value = this.parseValue(valueToken);
          
          if (stack.length > 0) {
            stack[stack.length - 1][key] = value;
          } else {
            ast[key] = value;
          }
          
          i++;
        }
      } else {
        // Value token
        if (stack.length > 0) {
          stack[stack.length - 1].children.push(this.parseValue(token));
        }
        i++;
      }
    }
    
    return ast;
  }
  
  /**
   * Process S-expression into AST node
   */
  private processExpression(expr: any, ast: any, errors: ParseError[]): void {
    if (!expr.type) return;
    
    switch (expr.type) {
      case 'ensure':
      case 'ask':
      case 'assert':
      case 'plan':
      case 'measure':
      case 'decide':
      case 'retract':
        ast.speech = expr.type;
        this.processChildren(expr.children, ast, errors);
        break;
        
      case 'ent':
        if (expr.children.length > 0) {
          ast.entity = String(expr.children[0]);
        }
        break;
        
      case 'act':
      case 'use':
        if (expr.children.length > 0) {
          ast.action = {
            type: expr.type === 'use' ? 'capability' : 'action',
            value: String(expr.children[0])
          };
        }
        break;
        
      case 'pre':
        ast.pre = this.parseConstraints(expr.children, errors);
        break;
        
      case 'post':
        ast.post = this.parseConstraints(expr.children, errors);
        break;
        
      case 'tests':
        ast.tests = expr.children.map((child: any) => ({
          test: String(child)
        }));
        break;
        
      case 'evidence':
        ast.evidence = expr.children.map((child: any) => String(child));
        break;
        
      case 'bt':
        this.processBitemporal(expr.children, ast, errors);
        break;
        
      case 'plan':
        ast.plan = this.parsePlanSteps(expr.children, errors);
        break;
    }
  }
  
  /**
   * Process children of expression
   */
  private processChildren(children: any[], ast: any, errors: ParseError[]): void {
    for (const child of children) {
      if (typeof child === 'object' && child.type) {
        this.processExpression(child, ast, errors);
      }
    }
  }
  
  /**
   * Parse constraints from children
   */
  private parseConstraints(children: any[], errors: ParseError[]): (string | PLIXConstraint)[] {
    const constraints: (string | PLIXConstraint)[] = [];
    
    for (const child of children) {
      if (typeof child === 'string') {
        const result = this.constraintParser.parse(child);
        if (result.constraint) {
          constraints.push(result.constraint);
        } else {
          constraints.push(child); // Fallback to string
        }
      } else if (typeof child === 'object') {
        // Parse constraint expression
        const exprStr = this.expressionToString(child);
        const result = this.constraintParser.parse(exprStr);
        if (result.constraint) {
          constraints.push(result.constraint);
        } else {
          constraints.push(exprStr);
        }
      }
    }
    
    return constraints;
  }
  
  /**
   * Convert expression to string
   */
  private expressionToString(expr: any): string {
    if (typeof expr === 'string') return expr;
    if (typeof expr === 'number' || typeof expr === 'boolean') return String(expr);
    
    if (expr.type === 'and' || expr.type === 'or' || expr.type === 'not') {
      const left = expr.children[0] ? this.expressionToString(expr.children[0]) : '';
      const right = expr.children[1] ? this.expressionToString(expr.children[1]) : '';
      
      if (expr.type === 'not') {
        return `NOT (${left})`;
      }
      return `(${left}) ${expr.type.toUpperCase()} (${right})`;
    }
    
    return String(expr);
  }
  
  /**
   * Process bitemporal clause
   */
  private processBitemporal(children: any[], ast: any, errors: ParseError[]): void {
    ast.bt = {};
    
    for (let i = 0; i < children.length; i += 2) {
      const key = String(children[i]);
      const value = children[i + 1];
      
      if (key === 'tx_time' || key === 'valid_time') {
        ast.bt[key] = String(value);
      }
    }
  }
  
  /**
   * Parse plan steps
   */
  private parsePlanSteps(children: any[], errors: ParseError[]): any[] {
    const steps: any[] = [];
    
    for (const child of children) {
      if (typeof child === 'object' && child.type === 'step') {
        steps.push({
          step: child.children[0] || '',
          id: child.children[0] || ''
        });
      }
    }
    
    return steps;
  }
  
  /**
   * Parse value token
   */
  private parseValue(token: SFormToken): any {
    switch (token.type) {
      case 'string':
        return token.value;
      case 'number':
        return parseFloat(token.value);
      case 'boolean':
        return token.value === 'true';
      default:
        return token.value;
    }
  }
  
  /**
   * Convert AST to PLIxIntent
   */
  private astToIntent(ast: any, errors: ParseError[]): PLIxIntent {
    return {
      intent: ast.speech || 'ensure',
      context: {
        entities: [],
        scope: 'default',
        risk: 0.5
      },
      contract: {
        pre: ast.pre || [],
        post: ast.post || [],
        capabilities: [],
        policies: []
      },
      plan: {
        steps: ast.plan || [],
        deps: []
      },
      conditions: {
        onTestFail: 'retry',
        onLowConfidence: 'escalate',
        onPolicyBreach: 'fail'
      },
      evidence: {
        required: [],
        produce: []
      },
      telemetry: {
        confidenceThresholds: {
          minimum: 0.70,
          warning: 0.80,
          critical: 0.90
        },
        timeouts: {
          step: 30000,
          plan: 300000
        }
      },
      provenance: {
        who: 'system',
        when: new Date().toISOString(),
        lineage: []
      }
    };
  }
}

interface SFormToken {
  type: 'open' | 'close' | 'keyword' | 'string' | 'number' | 'boolean' | 'identifier';
  value: string;
  line: number;
  column: number;
}

