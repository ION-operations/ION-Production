/**
 * PLIX Parser - Phase 1 Implementation
 * 
 * Human-PLIX parser with indentation-based syntax and optional delimiters
 * Based on External AI Feedback (Grok, Gemini, Perplexity)
 */

import type { PLIxIntent } from '../models/schema';
import type { PLIXConstraint } from '../models/constraints';
import { ConstraintParser } from './constraint-parser';
import { SFormParser } from './sform-parser';
import {
  parsePlaceOperation,
  parseMoveOperation,
  parseSenseOperation,
  parseEmitOperation,
  parseQQuatLiteral,
  parseDualQuatLiteral,
  parseVec3Literal,
  parseVec4Literal,
  parseQPoseLiteral,
  parseQAddrLiteral,
  parseQuantumContext
} from './quaternion-parser';
import { PLIXTypeChecker } from '../type-checker/quaternion-type-checker';

export interface ParseOptions {
  /** Support optional delimiters ({}) for deep nesting */
  allowDelimiters?: boolean;
  
  /** Strict mode - fail on unknown constructs */
  strict?: boolean;
  
  /** Tag registry for resolving tags */
  tagRegistry?: Map<string, any>;
}

export interface ParseError {
  line: number;
  column: number;
  message: string;
  suggestion?: string;
}

export interface ParseResult {
  /** Parsed PLIX intent */
  intent: PLIxIntent | null;
  
  /** Parse errors */
  errors: ParseError[];
  
  /** Warnings (non-fatal issues) */
  warnings: ParseError[];
}

/**
 * PLIX Parser
 * 
 * Parses Human-PLIX syntax into Canonical JSON format
 */
export class PLIXParser {
  private options: ParseOptions;
  private tagRegistry: Map<string, any>;
  private constraintParser: ConstraintParser;
  private sFormParser: SFormParser;
  private typeChecker: PLIXTypeChecker;
  private currentContext: 'pre' | 'post' | 'none' = 'none';
  
  constructor(options: ParseOptions = {}) {
    this.options = {
      allowDelimiters: true,
      strict: false,
      ...options
    };
    this.tagRegistry = options.tagRegistry || new Map();
    this.constraintParser = new ConstraintParser();
    this.sFormParser = new SFormParser();
    this.typeChecker = new PLIXTypeChecker();
  }
  
  /**
   * Parse Human-PLIX text into PLIxIntent
   */
  parse(text: string): ParseResult {
    const errors: ParseError[] = [];
    const warnings: ParseError[] = [];
    
    try {
      // Check if input is S-form (starts with '(')
      if (text.trim().startsWith('(')) {
        return this.parseSForm(text, errors, warnings);
      }
      
      // Tokenize input
      const tokens = this.tokenize(text);
      
      // Parse tokens into AST
      const ast = this.parseTokens(tokens, errors, warnings);
      
      // Validate AST
      this.validateAST(ast, errors, warnings);
      
      // Type check geometric operations (Phase 2, Week 6 integration)
      if (ast.geometric && ast.geometric.operations) {
        this.typeCheckGeometricOperations(ast.geometric.operations, errors, warnings);
      }
      
      // Check for circular dependencies in plan
      this.checkCircularDependencies(ast, errors, warnings);
      
      // Convert AST to PLIxIntent
      const intent = ast ? this.astToIntent(ast) : null;
      
      return {
        intent,
        errors,
        warnings
      };
    } catch (error: any) {
      errors.push({
        line: 0,
        column: 0,
        message: `Parse error: ${error.message}`,
        suggestion: 'Check syntax and try again'
      });
      
      return {
        intent: null,
        errors,
        warnings
      };
    }
  }
  
  /**
   * Parse S-form text
   */
  private parseSForm(text: string, errors: ParseError[], warnings: ParseError[]): ParseResult {
    const result = this.sFormParser.parse(text);
    
    // Convert S-form errors to ParseError format
    const parseErrors: ParseError[] = result.errors.map(err => ({
      line: err.line,
      column: err.column,
      message: err.message,
      suggestion: err.suggestion
    }));
    
    return {
      intent: result.intent,
      errors: [...errors, ...parseErrors],
      warnings
    };
  }
  
  /**
   * Tokenize Human-PLIX text
   */
  private tokenize(text: string): Token[] {
    const tokens: Token[] = [];
    const lines = text.split('\n');
    
    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];
      const trimmed = line.trim();
      
      if (!trimmed || trimmed.startsWith('#')) {
        continue; // Skip empty lines and comments
      }
      
      // Calculate indentation
      const indent = line.length - line.trimStart().length;
      
      // Tokenize line
      const lineTokens = this.tokenizeLine(trimmed, lineNum + 1, indent);
      tokens.push(...lineTokens);
    }
    
    return tokens;
  }
  
  /**
   * Tokenize a single line
   */
  private tokenizeLine(line: string, lineNum: number, indent: number): Token[] {
    const tokens: Token[] = [];
    
    // Speech act (ask, assert, plan, ensure, measure, decide, retract)
    const speechActMatch = line.match(/^(ask|assert|plan|ensure|measure|decide|retract)\s+/);
    if (speechActMatch) {
      tokens.push({
        type: 'speech',
        value: speechActMatch[1],
        line: lineNum,
        column: indent,
        indent
      });
      line = line.substring(speechActMatch[0].length);
    }
    
    // Entity clause (ent:plix://...)
    const entityMatch = line.match(/^ent:(\S+)/);
    if (entityMatch) {
      tokens.push({
        type: 'entity',
        value: entityMatch[1],
        line: lineNum,
        column: indent + (line.indexOf('ent:') || 0),
        indent
      });
      line = line.substring(entityMatch[0].length);
    }
    
    // Action clause (act:... or using cap:...)
    const actionMatch = line.match(/^(act:(\S+)|using\s+cap:(\S+))/);
    if (actionMatch) {
      tokens.push({
        type: 'action',
        value: actionMatch[2] || actionMatch[3],
        isCapability: !!actionMatch[3],
        line: lineNum,
        column: indent + (line.indexOf('act:') || line.indexOf('using')) || 0,
        indent
      });
      line = line.substring(actionMatch[0].length);
    }
    
    // With clause
    if (line.trim().startsWith('with:')) {
      tokens.push({
        type: 'with_start',
        value: 'with',
        line: lineNum,
        column: indent,
        indent
      });
      // Parse with fields on subsequent lines
    }
    
    // Pre clause (supports both 'pre:' and 'requires')
    if (line.trim().startsWith('pre:') || line.trim().startsWith('requires')) {
      tokens.push({
        type: 'pre_start',
        value: 'pre',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Post clause (supports both 'post:' and 'ensures')
    if (line.trim().startsWith('post:') || line.trim().startsWith('ensures')) {
      tokens.push({
        type: 'post_start',
        value: 'post',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Tests clause
    if (line.trim().startsWith('tests:')) {
      tokens.push({
        type: 'tests_start',
        value: 'tests',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Evidence clause (supports both 'evidence:' and 'evidence')
    if (line.trim().startsWith('evidence:') || line.trim().startsWith('evidence')) {
      tokens.push({
        type: 'evidence_start',
        value: 'evidence',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Evidence require/produce keywords
    if (line.trim().startsWith('require')) {
      tokens.push({
        type: 'evidence_require',
        value: 'require',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    if (line.trim().startsWith('produce')) {
      tokens.push({
        type: 'evidence_produce',
        value: 'produce',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Time clause (bt:)
    if (line.trim().startsWith('bt:')) {
      tokens.push({
        type: 'time_start',
        value: 'bt',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Plan clause
    if (line.trim().startsWith('plan')) {
      tokens.push({
        type: 'plan_start',
        value: 'plan',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Constraint (con:...)
    const constraintMatch = line.match(/^con:(\S+)/);
    if (constraintMatch) {
      tokens.push({
        type: 'constraint',
        value: constraintMatch[1],
        line: lineNum,
        column: indent + (line.indexOf('con:') || 0),
        indent
      });
    }
    
    // Geometric operations (Phase 2, Week 5)
    if (line.trim().startsWith('place')) {
      tokens.push({
        type: 'geometric_op',
        value: 'place',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    if (line.trim().startsWith('move')) {
      tokens.push({
        type: 'geometric_op',
        value: 'move',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    if (line.trim().startsWith('sense')) {
      tokens.push({
        type: 'geometric_op',
        value: 'sense',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    if (line.trim().startsWith('emit')) {
      tokens.push({
        type: 'geometric_op',
        value: 'emit',
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Quantum context (with Q(...))
    if (line.trim().startsWith('with Q(')) {
      tokens.push({
        type: 'quantum_context',
        value: line.trim(),
        line: lineNum,
        column: indent,
        indent
      });
    }
    
    // Test (tst:...)
    const testMatch = line.match(/^tst:(\S+)/);
    if (testMatch) {
      tokens.push({
        type: 'test',
        value: testMatch[1],
        line: lineNum,
        column: indent + (line.indexOf('tst:') || 0),
        indent
      });
    }
    
    // Witness (w:...)
    const witnessMatch = line.match(/^w:(\S+)/);
    if (witnessMatch) {
      tokens.push({
        type: 'witness',
        value: witnessMatch[1],
        line: lineNum,
        column: indent + (line.indexOf('w:') || 0),
        indent
      });
    }
    
    return tokens;
  }
  
  /**
   * Parse tokens into AST
   */
  private parseTokens(tokens: Token[], errors: ParseError[], warnings: ParseError[]): any {
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
    this.currentContext = 'none';
    
    while (i < tokens.length) {
      const token = tokens[i];
      
      switch (token.type) {
        case 'speech':
          ast.speech = token.value;
          break;
        case 'entity':
          ast.entity = token.value;
          this.validateTag(token.value, token, errors);
          break;
        case 'action':
          ast.action = {
            type: token.isCapability ? 'capability' : 'action',
            value: token.value
          };
          this.validateTag(token.value, token, errors);
          break;
        case 'pre_start':
          this.currentContext = 'pre';
          break;
        case 'post_start':
          this.currentContext = 'post';
          break;
        case 'constraint':
          // Parse constraint expression with enhanced parser
          const constraint = this.parseConstraint(token.value, token, errors);
          if (constraint) {
            if (this.currentContext === 'pre') {
              ast.pre.push(constraint);
            } else if (this.currentContext === 'post') {
              ast.post.push(constraint);
            } else {
              // Default to pre if context not set
              ast.pre.push(constraint);
              warnings.push({
                line: token.line,
                column: token.column,
                message: `Constraint found outside pre/post clause, assuming pre`,
                suggestion: 'Explicitly mark constraints with pre: or post:'
              });
            }
          }
          break;
        case 'test':
          ast.tests.push({
            test: token.value
          });
          break;
        case 'witness':
          // Legacy 'w:' syntax - treat as 'produce'
          if (!ast.evidence_produce) ast.evidence_produce = [];
          ast.evidence_produce.push(token.value);
          this.validateTag(token.value, token, warnings);
          break;
        case 'evidence_require':
          this.currentContext = 'evidence_require';
          break;
        case 'evidence_produce':
          this.currentContext = 'evidence_produce';
          break;
        case 'plan_start':
          // Parse plan block
          const planResult = this.parsePlanBlock(tokens, i, errors, warnings);
          ast.plan = planResult.steps;
          i = planResult.nextIndex;
          continue;
        case 'geometric_op':
          // Parse geometric operation (Phase 2, Week 5)
          const geoResult = this.parseGeometricOperation(tokens, i, errors, warnings);
          if (geoResult.operation) {
            if (!ast.geometric) ast.geometric = { operations: [] };
            if (!ast.geometric.operations) ast.geometric.operations = [];
            ast.geometric.operations.push(geoResult.operation);
          }
          i = geoResult.nextIndex;
          continue;
        case 'quantum_context':
          // Parse quantum context block
          const qcResult = this.parseQuantumContextBlock(tokens, i, errors, warnings);
          if (qcResult.context) {
            if (!ast.geometric) ast.geometric = {};
            ast.geometric.quantumContext = qcResult.context;
          }
          i = qcResult.nextIndex;
          continue;
      }
      
      i++;
    }
    
    return ast;
  }
  
  /**
   * Parse geometric operation (Phase 2, Week 5)
   */
  private parseGeometricOperation(tokens: Token[], startIndex: number, errors: ParseError[], warnings: ParseError[]): { operation: any | null; nextIndex: number } {
    const token = tokens[startIndex];
    const fullLine = this.getFullLine(tokens, startIndex);
    
    let operation: any = null;
    
    try {
      switch (token.value) {
        case 'place':
          const placeResult = parsePlaceOperation(fullLine);
          if (placeResult.operation) {
            operation = placeResult.operation;
          }
          errors.push(...placeResult.errors.map(msg => ({
            line: token.line,
            column: token.column,
            message: msg,
            suggestion: 'Check place operation syntax'
          })));
          break;
        case 'move':
          const moveResult = parseMoveOperation(fullLine);
          if (moveResult.operation) {
            operation = moveResult.operation;
          }
          errors.push(...moveResult.errors.map(msg => ({
            line: token.line,
            column: token.column,
            message: msg,
            suggestion: 'Check move operation syntax'
          })));
          break;
        case 'sense':
          const senseResult = parseSenseOperation(fullLine);
          if (senseResult.operation) {
            operation = senseResult.operation;
          }
          errors.push(...senseResult.errors.map(msg => ({
            line: token.line,
            column: token.column,
            message: msg,
            suggestion: 'Check sense operation syntax'
          })));
          break;
        case 'emit':
          const emitResult = parseEmitOperation(fullLine);
          if (emitResult.operation) {
            operation = emitResult.operation;
          }
          errors.push(...emitResult.errors.map(msg => ({
            line: token.line,
            column: token.column,
            message: msg,
            suggestion: 'Check emit operation syntax'
          })));
          break;
      }
    } catch (error: any) {
      errors.push({
        line: token.line,
        column: token.column,
        message: `Error parsing geometric operation: ${error.message}`,
        suggestion: 'Check geometric operation syntax'
      });
    }
    
    // Find end of operation (next token at same or less indentation)
    let nextIndex = startIndex + 1;
    while (nextIndex < tokens.length && tokens[nextIndex].indent > token.indent) {
      nextIndex++;
    }
    
    return { operation, nextIndex };
  }
  
  /**
   * Parse quantum context block
   */
  private parseQuantumContextBlock(tokens: Token[], startIndex: number, errors: ParseError[], warnings: ParseError[]): { context: any | null; nextIndex: number } {
    const token = tokens[startIndex];
    const fullLine = token.value;
    
    // Extract quantum context from line
    const qcMatch = fullLine.match(/with\s+Q\s*\(([^)]+)\)/);
    if (qcMatch) {
      const result = parseQuantumContext(qcMatch[0]);
      return { context: result.context, nextIndex: startIndex + 1 };
    }
    
    return { context: null, nextIndex: startIndex + 1 };
  }
  
  /**
   * Get full line text from tokens
   */
  private getFullLine(tokens: Token[], startIndex: number): string {
    const token = tokens[startIndex];
    const lineTokens: Token[] = [token];
    
    // Collect all tokens on the same line
    for (let i = startIndex + 1; i < tokens.length; i++) {
      if (tokens[i].line === token.line) {
        lineTokens.push(tokens[i]);
      } else {
        break;
      }
    }
    
    // Reconstruct line text (simplified - full implementation would preserve spacing)
    return lineTokens.map(t => t.value).join(' ');
  }
  
  /**
   * Parse constraint expression with enhanced parser
   */
  private parseConstraint(expr: string, token: Token, errors: ParseError[]): PLIXConstraint | string | null {
    const result = this.constraintParser.parse(expr);
    
    if (result.errors.length > 0) {
      errors.push({
        line: token.line,
        column: token.column,
        message: `Constraint parse error: ${result.errors.join(', ')}`,
        suggestion: 'Check constraint syntax (supports logical, quantified, temporal operators)'
      });
      
      // Return as string for backward compatibility
      return expr;
    }
    
    return result.constraint || expr;
  }
  
  /**
   * Parse plan block
   */
  private parsePlanBlock(tokens: Token[], startIndex: number, errors: ParseError[], warnings: ParseError[]): { steps: any[]; nextIndex: number } {
    const steps: any[] = [];
    let i = startIndex + 1; // Skip 'plan_start' token
    
    // Look for plan content (indented tokens or delimiters)
    while (i < tokens.length) {
      const token = tokens[i];
      
      // Check if we've left the plan block (same or less indentation)
      if (token.type === 'plan_start' && token.indent <= tokens[startIndex].indent) {
        break;
      }
      
      // Parse step (supports both 'step' and 'task' keywords)
      if (token.value === 'step' || token.value === 'task' || token.type === 'identifier') {
        const stepResult = this.parseStep(tokens, i, errors, warnings);
        if (stepResult.step) {
          steps.push(stepResult.step);
        }
        i = stepResult.nextIndex;
        continue;
      }
      
      i++;
    }
    
    return { steps, nextIndex: i };
  }
  
  /**
   * Parse plan step (supports both 'step id' and 'task id := Action(params)' syntax)
   */
  private parseStep(tokens: Token[], startIndex: number, errors: ParseError[], warnings: ParseError[]): { step: any | null; nextIndex: number } {
    const step: any = {
      id: '',
      step: '',
      depends_on: [],
      errors: [],
      action: null,
      params: {}
    };
    
    let i = startIndex + 1;
    
    // Get step name
    if (i < tokens.length && tokens[i].type === 'identifier') {
      step.id = tokens[i].value;
      step.step = tokens[i].value;
      i++;
    }
    
    // Check for := operator (formal step definition)
    if (i < tokens.length && tokens[i].value === ':=') {
      i++; // Skip :=
      
      // Parse action invocation: Action(params)
      const actionResult = this.parseActionInvocation(tokens, i, errors);
      if (actionResult.action) {
        step.action = actionResult.action;
        step.params = actionResult.params;
      }
      i = actionResult.nextIndex;
    }
    
    // Parse step properties
    while (i < tokens.length) {
      const token = tokens[i];
      
      // Check if we've left the step (same or less indentation)
      if (token.indent <= tokens[startIndex].indent && token.type !== 'constraint') {
        break;
      }
      
      // Parse error clauses
      if (token.value === 'on_error' || token.value.startsWith('on_error:')) {
        const errorClause = this.parseErrorClause(tokens, i, errors);
        if (errorClause.clause) {
          if (!step.errors) step.errors = [];
          step.errors.push(errorClause.clause);
        }
        i = errorClause.nextIndex;
        continue;
      }
      
      // Parse compensation (supports both 'compensate id' and 'compensate id -> Action(params)')
      if (token.value === 'compensate') {
        const compensateResult = this.parseCompensation(tokens, i, errors);
        if (compensateResult.compensation) {
          step.compensation = compensateResult.compensation;
        }
        i = compensateResult.nextIndex;
        continue;
      }
      
      // Parse dependencies
      if (token.value === 'depends' && i + 2 < tokens.length && tokens[i + 1].value === 'on') {
        i += 2; // Skip 'depends on'
        const deps: string[] = [];
        while (i < tokens.length && tokens[i].type === 'identifier') {
          deps.push(tokens[i].value);
          i++;
          if (i < tokens.length && tokens[i].value === ',') {
            i++; // Skip comma
          }
        }
        step.depends_on = deps;
        continue;
      }
      
      i++;
    }
    
    return { step: step.id ? step : null, nextIndex: i };
  }
  
  /**
   * Parse compensation clause (supports both simplified and formal syntax)
   * Simplified: compensate id
   * Formal: compensate id -> Action(params)
   */
  private parseCompensation(tokens: Token[], startIndex: number, errors: ParseError[]): { compensation: any | null; nextIndex: number } {
    let i = startIndex + 1; // Skip 'compensate' keyword
    
    const compensation: any = {
      stepId: '',
      action: null,
      params: {}
    };
    
    // Get step ID to compensate
    if (i < tokens.length && tokens[i].type === 'identifier') {
      compensation.stepId = tokens[i].value;
      i++;
    } else {
      return { compensation: null, nextIndex: i };
    }
    
    // Check for -> operator (formal syntax)
    if (i < tokens.length && tokens[i].value === '->') {
      i++; // Skip ->
      
      // Parse compensation action invocation
      const actionResult = this.parseActionInvocation(tokens, i, errors);
      if (actionResult.action) {
        compensation.action = actionResult.action;
        compensation.params = actionResult.params;
      }
      i = actionResult.nextIndex;
    }
    
    return { compensation, nextIndex: i };
  }
  
  /**
   * Parse action invocation: Action(params)
   * Supports: api.check_auth(), api.query_users(filter: check.ref:filter)
   */
  private parseActionInvocation(tokens: Token[], startIndex: number, errors: ParseError[]): { action: string | null; params: Record<string, any>; nextIndex: number } {
    let i = startIndex;
    let action = '';
    const params: Record<string, any> = {};
    
    // Parse action identifier (may have dots: api.check_auth)
    while (i < tokens.length && (tokens[i].type === 'identifier' || tokens[i].value === '.')) {
      action += tokens[i].value;
      i++;
    }
    
    // Check for opening parenthesis
    if (i < tokens.length && tokens[i].value === '(') {
      i++; // Skip (
      
      // Parse parameters until closing parenthesis
      while (i < tokens.length && tokens[i].value !== ')') {
        const token = tokens[i];
        
        // Parse parameter name
        if (token.type === 'identifier') {
          const paramName = token.value;
          i++;
          
          // Check for colon separator
          if (i < tokens.length && tokens[i].value === ':') {
            i++; // Skip :
            
            // Parse parameter value
            const valueResult = this.parseParameterValue(tokens, i);
            params[paramName] = valueResult.value;
            i = valueResult.nextIndex;
          }
        }
        
        // Skip commas
        if (i < tokens.length && tokens[i].value === ',') {
          i++;
        }
      }
      
      // Skip closing parenthesis
      if (i < tokens.length && tokens[i].value === ')') {
        i++;
      }
    }
    
    return { action: action || null, params, nextIndex: i };
  }
  
  /**
   * Parse parameter value (supports tag references like check.ref:filter)
   */
  private parseParameterValue(tokens: Token[], startIndex: number): { value: any; nextIndex: number } {
    let i = startIndex;
    let value: any = null;
    
    if (i >= tokens.length) {
      return { value, nextIndex: i };
    }
    
    const token = tokens[i];
    
    // Check for tag reference: check.ref:filter
    if (token.type === 'identifier') {
      const identifier = token.value;
      i++;
      
      // Check for .ref: pattern
      if (i + 2 < tokens.length && 
          tokens[i].value === '.' && 
          tokens[i + 1].value === 'ref' && 
          tokens[i + 2].value === ':') {
        i += 3; // Skip .ref:
        
        // Get field name
        if (i < tokens.length && tokens[i].type === 'identifier') {
          value = {
            type: 'tag_ref',
            source: identifier,
            field: tokens[i].value
          };
          i++;
        }
      } else {
        // Plain identifier
        value = identifier;
      }
    } else if (token.type === 'string') {
      value = token.value;
      i++;
    } else if (token.type === 'number') {
      value = parseFloat(token.value);
      i++;
    } else {
      // Try to parse as string
      value = token.value;
      i++;
    }
    
    return { value, nextIndex: i };
  }
  
  /**
   * Parse error clause
   */
  private parseErrorClause(tokens: Token[], startIndex: number, errors: ParseError[]): { clause: any | null; nextIndex: number } {
    // Simplified error clause parsing
    // Format: on_error: error_type -> action
    let i = startIndex + 1;
    
    if (i >= tokens.length) {
      return { clause: null, nextIndex: i };
    }
    
    const errorType = tokens[i].value;
    i++;
    
    if (i >= tokens.length || tokens[i].value !== '->') {
      return { clause: null, nextIndex: i };
    }
    
    i++;
    
    if (i >= tokens.length) {
      return { clause: null, nextIndex: i };
    }
    
    const action = tokens[i].value;
    
    return {
      clause: {
        error: errorType,
        action: action
      },
      nextIndex: i + 1
    };
  }
  
  /**
   * Validate tag format
   */
  private validateTag(tag: string, token: Token, errors: ParseError[]): void {
    if (!this.isValidTag(tag)) {
      errors.push({
        line: token.line,
        column: token.column,
        message: `Invalid tag format: ${tag}`,
        suggestion: 'Tags must follow format: plix://namespace/path#rev@hash'
      });
    }
  }
  
  /**
   * Check for circular dependencies in plan
   */
  private checkCircularDependencies(ast: any, errors: ParseError[], warnings: ParseError[]): void {
    if (!ast.plan || !Array.isArray(ast.plan)) {
      return;
    }
    
    // Build dependency graph
    const graph = new Map<string, string[]>();
    
    for (const step of ast.plan) {
      const stepId = step.id || step.step;
      const deps = step.depends_on || [];
      graph.set(stepId, deps);
    }
    
    // Check for cycles using DFS
    const visited = new Set<string>();
    const recStack = new Set<string>();
    
    const hasCycle = (node: string): boolean => {
      if (recStack.has(node)) {
        return true; // Cycle detected
      }
      
      if (visited.has(node)) {
        return false; // Already processed
      }
      
      visited.add(node);
      recStack.add(node);
      
      const deps = graph.get(node) || [];
      for (const dep of deps) {
        if (hasCycle(dep)) {
          errors.push({
            line: 0,
            column: 0,
            message: `Circular dependency detected: ${node} depends on ${dep}`,
            suggestion: 'Remove circular dependencies from plan steps'
          });
          return true;
        }
      }
      
      recStack.delete(node);
      return false;
    };
    
    // Check all nodes
    for (const stepId of graph.keys()) {
      if (!visited.has(stepId)) {
        hasCycle(stepId);
      }
    }
  }
  
  /**
   * Type check geometric operations (Phase 2, Week 6 integration)
   */
  private typeCheckGeometricOperations(operations: any[], errors: ParseError[], warnings: ParseError[]): void {
    for (const operation of operations) {
      try {
        const result = this.typeChecker.checkGeometricOperation(operation);
        
        // Add type errors to parse errors
        for (const error of result.errors) {
          errors.push({
            line: 0,
            column: 0,
            message: `Type error in ${operation.type}: ${error}`,
            suggestion: 'Check geometric operation types and quantum context'
          });
        }
        
        // Add type warnings to parse warnings
        for (const warning of result.warnings) {
          warnings.push({
            line: 0,
            column: 0,
            message: `Type warning in ${operation.type}: ${warning}`,
            suggestion: 'Review geometric operation types'
          });
        }
      } catch (error: any) {
        errors.push({
          line: 0,
          column: 0,
          message: `Type checking error: ${error.message}`,
          suggestion: 'Check geometric operation syntax'
        });
      }
    }
  }
  
  /**
   * Validate AST
   */
  private validateAST(ast: any, errors: ParseError[], warnings: ParseError[]): void {
    // Validate required fields
    if (!ast.speech) {
      errors.push({
        line: 0,
        column: 0,
        message: 'Missing speech act (ask, assert, plan, ensure, etc.)',
        suggestion: 'Add a speech act at the beginning'
      });
    }
    
    if (!ast.entity) {
      errors.push({
        line: 0,
        column: 0,
        message: 'Missing entity clause (ent:...)',
        suggestion: 'Add an entity clause'
      });
    }
    
    // Validate tag format
    if (ast.entity && !this.isValidTag(ast.entity)) {
      errors.push({
        line: 0,
        column: 0,
        message: `Invalid tag format: ${ast.entity}`,
        suggestion: 'Tags must follow format: plix://namespace/path#rev@hash'
      });
    }
    
    // Check for dangling references
    this.checkDanglingReferences(ast, warnings);
  }
  
  /**
   * Check for dangling tag references
   */
  private checkDanglingReferences(ast: any, warnings: ParseError[]): void {
    // Extract all tag references
    const tagRefs = this.extractTagReferences(ast);
    
    for (const ref of tagRefs) {
      if (!this.tagRegistry.has(ref) && !this.isValidTag(ref)) {
        warnings.push({
          line: 0,
          column: 0,
          message: `Dangling tag reference: ${ref}`,
          suggestion: `Register tag in registry or check spelling`
        });
      }
    }
  }
  
  /**
   * Extract tag references from AST
   */
  private extractTagReferences(ast: any): string[] {
    const refs: string[] = [];
    
    if (ast.entity && this.isValidTag(ast.entity)) {
      refs.push(ast.entity);
    }
    
    // Recursively extract from nested structures
    // Simplified - full implementation would traverse all nodes
    
    return refs;
  }
  
  /**
   * Check if string is valid PLIX tag
   */
  private isValidTag(tag: string): boolean {
    // PLIX tag format: plix://namespace/path#rev@hash
    const tagPattern = /^plix:\/\/[a-z0-9._-]+(\/[a-z0-9._-]+)*(#rev@[a-f0-9]+)?$/i;
    return tagPattern.test(tag);
  }
  
  /**
   * Convert AST to PLIxIntent
   */
  private astToIntent(ast: any): PLIxIntent {
    const intent: PLIxIntent = {
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
        required: ast.evidence_require || [],
        produce: ast.evidence_produce || ast.evidence || []
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
        executed_by: 'system',
        executed_at: new Date().toISOString(),
        plan_version: '1.0',
        lineage: []
      }
    };
    
    // Add geometric operations (Phase 2, Week 5)
    if (ast.geometric) {
      intent.geometric = {
        operations: ast.geometric.operations || [],
        quantumContext: ast.geometric.quantumContext
      };
    }
    
    return intent;
  }
  
  /**
   * Register tag in registry
   */
  registerTag(tag: string, definition: any): void {
    this.tagRegistry.set(tag, definition);
  }
  
  /**
   * Resolve tag from registry
   */
  resolveTag(tag: string): any {
    return this.tagRegistry.get(tag);
  }
}

/**
 * Token structure
 */
interface Token {
  type: TokenType;
  value: string;
  isCapability?: boolean;
  line: number;
  column: number;
  indent: number;
}

type TokenType =
  | 'speech'
  | 'entity'
  | 'action'
  | 'with_start'
  | 'pre_start'
  | 'post_start'
  | 'tests_start'
  | 'evidence_start'
  | 'evidence_require'
  | 'evidence_produce'
  | 'time_start'
  | 'plan_start'
  | 'constraint'
  | 'test'
  | 'witness'
  | 'identifier'
  | 'string'
  | 'number'
  | 'operator'
  | 'geometric_op'
  | 'quantum_context';

/**
 * Round-trip conversion helpers
 */
export const RoundTripConverter = {
  /**
   * Convert Human-PLIX to Canonical JSON
   */
  humanToJSON(text: string, options?: ParseOptions): { json: any; errors: ParseError[] } {
    const parser = new PLIXParser(options);
    const result = parser.parse(text);
    
    return {
      json: result.intent,
      errors: result.errors
    };
  },
  
  /**
   * Convert Canonical JSON to Human-PLIX
   */
  jsonToHuman(intent: PLIxIntent): string {
    // Simplified - full implementation would format with proper indentation
    const lines: string[] = [];
    
    lines.push(`${intent.intent} ent:${(intent as any).entity || 'plix://entity/default'}`);
    
    if (intent.contract.pre.length > 0) {
      lines.push('  pre:');
      for (const pre of intent.contract.pre) {
        const preStr = typeof pre === 'string' ? pre : `con:${pre}`;
        lines.push(`    ${preStr}`);
      }
    }
    
    if (intent.contract.post.length > 0) {
      lines.push('  post:');
      for (const post of intent.contract.post) {
        const postStr = typeof post === 'string' ? post : `con:${post}`;
        lines.push(`    ${postStr}`);
      }
    }
    
    return lines.join('\n');
  },
  
  /**
   * Convert Canonical JSON to S-form
   */
  jsonToSForm(intent: PLIxIntent): string {
    const parts: string[] = [];
    
    parts.push(`(${intent.intent}`);
    
    // Entity
    if ((intent as any).entity) {
      parts.push(`  (ent ${(intent as any).entity})`);
    }
    
    // Action
    if ((intent as any).action) {
      const action = (intent as any).action;
      if (action.type === 'capability') {
        parts.push(`  (use ${action.value})`);
      } else {
        parts.push(`  (act ${action.value})`);
      }
    }
    
    // Preconditions
    if (intent.contract.pre.length > 0) {
      parts.push('  (pre');
      for (const pre of intent.contract.pre) {
        const preStr = RoundTripConverter.formatConstraintForSForm(pre);
        parts.push(`    ${preStr}`);
      }
      parts.push('  )');
    }
    
    // Postconditions
    if (intent.contract.post.length > 0) {
      parts.push('  (post');
      for (const post of intent.contract.post) {
        const postStr = RoundTripConverter.formatConstraintForSForm(post);
        parts.push(`    ${postStr}`);
      }
      parts.push('  )');
    }
    
    // Tests
    if (intent.plan.steps.length > 0) {
      parts.push('  (tests');
      for (const test of (intent as any).tests || []) {
        parts.push(`    ${test.test || test}`);
      }
      parts.push('  )');
    }
    
    // Evidence
    if ((intent as any).evidence && (intent as any).evidence.length > 0) {
      parts.push('  (evidence');
      for (const ev of (intent as any).evidence) {
        parts.push(`    ${ev}`);
      }
      parts.push('  )');
    }
    
    // Bitemporal
    if ((intent as any).bt) {
      parts.push('  (bt');
      if ((intent as any).bt.tx_time) {
        parts.push(`    tx_time "${(intent as any).bt.tx_time}"`);
      }
      if ((intent as any).bt.valid_time) {
        parts.push(`    valid_time "${(intent as any).bt.valid_time}"`);
      }
      parts.push('  )');
    }
    
    // Plan
    if (intent.plan.steps.length > 0) {
      parts.push('  (plan');
      for (const step of intent.plan.steps) {
        parts.push(`    (step ${step.id || step.step})`);
        if (step.errors && step.errors.length > 0) {
          for (const err of step.errors) {
            parts.push(`      (on_error ${err.error} ${err.action})`);
          }
        }
      }
      parts.push('  )');
    }
    
    parts.push(')');
    
    return parts.join('\n');
  }
  
  /**
   * Format constraint for S-form
   */
  formatConstraintForSForm(constraint: string | PLIXConstraint): string {
    if (typeof constraint === 'string') {
      return constraint;
    }
    
    // Format constraint based on type
    switch (constraint.type) {
      case 'simple':
        return `(= ${constraint.expr} ${constraint.value})`;
      case 'logical':
        if (constraint.operator === 'not') {
          return `(not ${RoundTripConverter.formatConstraintForSForm(constraint.left)})`;
        }
        return `(${constraint.operator} ${RoundTripConverter.formatConstraintForSForm(constraint.left)} ${constraint.right ? RoundTripConverter.formatConstraintForSForm(constraint.right) : ''})`;
      case 'quantified':
        const domainStr = constraint.domain ? ` in ${constraint.domain}` : '';
        return `(${constraint.quantifier} ${constraint.variable}${domainStr} ${RoundTripConverter.formatConstraintForSForm(constraint.constraint)})`;
      case 'temporal':
        const durationStr = constraint.duration ? ` ${constraint.duration}` : '';
        return `(${constraint.operator} ${RoundTripConverter.formatConstraintForSForm(constraint.constraint)}${durationStr})`;
      default:
        return String(constraint);
    }
  },
  
  /**
   * Convert S-form to Canonical JSON
   */
  sFormToJSON(sForm: string): { json: any; errors: ParseError[] } {
    const parser = new SFormParser();
    const result = parser.parse(sForm);
    
    return {
      json: result.intent,
      errors: result.errors
    };
  }
};

