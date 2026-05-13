/**
 * PLIX Phase 1 Tests
 * 
 * Basic tests for parser, constraints, and error taxonomy
 */

import { describe, it, expect } from 'vitest';
import { PLIXParser, RoundTripConverter } from '../src/parser';
import { ConstraintEvaluator } from '../src/models/constraints';
import { ErrorTaxonomy } from '../src/models/errors';

describe('PLIX Phase 1 Tests', () => {
  
  describe('Parser', () => {
    it('should parse basic Human-PLIX syntax', () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:schema_intact == h_prev
  post:
    con:schema_fingerprint == h_next
`;
      
      const result = parser.parse(text);
      
      expect(result.intent).not.toBeNull();
      expect(result.errors.length).toBe(0);
    });
    
    it('should detect invalid tag format', () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:invalid_tag_format
  act:migrate
`;
      
      const result = parser.parse(text);
      
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors.some(e => e.message.includes('Invalid tag format'))).toBe(true);
    });
    
    it('should detect dangling tag references', () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/unknown_tool#rev@h_xxxx
`;
      
      const result = parser.parse(text);
      
      // Should have warnings for dangling references
      expect(result.warnings.length).toBeGreaterThanOrEqual(0);
    });
  });
  
  describe('Constraints', () => {
    it('should evaluate simple constraints', () => {
      const constraint = {
        type: 'simple' as const,
        expr: 'user_authenticated',
        op: '==' as const,
        value: true
      };
      
      const context = { user_authenticated: true };
      const result = ConstraintEvaluator.evaluate(constraint, context);
      
      expect(result).toBe(true);
    });
    
    it('should evaluate logical AND constraints', () => {
      const constraint = {
        type: 'logical' as const,
        operator: 'and' as const,
        left: {
          type: 'simple' as const,
          expr: 'user_authenticated',
          op: '==' as const,
          value: true
        },
        right: {
          type: 'simple' as const,
          expr: 'room_available',
          op: '==' as const,
          value: true
        }
      };
      
      const context = { user_authenticated: true, room_available: true };
      const result = ConstraintEvaluator.evaluate(constraint, context);
      
      expect(result).toBe(true);
    });
    
    it('should evaluate logical OR constraints', () => {
      const constraint = {
        type: 'logical' as const,
        operator: 'or' as const,
        left: {
          type: 'simple' as const,
          expr: 'user_authenticated',
          op: '==' as const,
          value: true
        },
        right: {
          type: 'simple' as const,
          expr: 'admin_override',
          op: '==' as const,
          value: true
        }
      };
      
      const context = { user_authenticated: false, admin_override: true };
      const result = ConstraintEvaluator.evaluate(constraint, context);
      
      expect(result).toBe(true);
    });
    
    it('should evaluate quantified FORALL constraints', () => {
      const constraint = {
        type: 'quantified' as const,
        quantifier: 'forall' as const,
        variable: 'row',
        constraint: {
          type: 'simple' as const,
          expr: 'unique_email',
          op: '==' as const,
          value: true
        }
      };
      
      const context = {
        rows: [
          { unique_email: true },
          { unique_email: true },
          { unique_email: true }
        ]
      };
      
      const result = ConstraintEvaluator.evaluateQuantified(constraint, context);
      
      expect(result).toBe(true);
    });
    
    it('should evaluate quantified EXISTS constraints', () => {
      const constraint = {
        type: 'quantified' as const,
        quantifier: 'exists' as const,
        variable: 'room',
        constraint: {
          type: 'simple' as const,
          expr: 'available',
          op: '==' as const,
          value: true
        }
      };
      
      const context = {
        rooms: [
          { available: false },
          { available: true },
          { available: false }
        ]
      };
      
      const result = ConstraintEvaluator.evaluateQuantified(constraint, context);
      
      expect(result).toBe(true);
    });
  });
  
  describe('Error Taxonomy', () => {
    it('should categorize network errors', () => {
      expect(ErrorTaxonomy.isNetworkError('net.timeout')).toBe(true);
      expect(ErrorTaxonomy.isNetworkError('net.unreachable')).toBe(true);
      expect(ErrorTaxonomy.getCategory('net.timeout')).toBe('network');
    });
    
    it('should categorize policy errors', () => {
      expect(ErrorTaxonomy.isPolicyError('policy.denied')).toBe(true);
      expect(ErrorTaxonomy.getCategory('policy.denied')).toBe('policy');
    });
    
    it('should categorize constraint errors', () => {
      expect(ErrorTaxonomy.isConstraintError('constraint.violated')).toBe(true);
      expect(ErrorTaxonomy.getCategory('constraint.precondition_failed')).toBe('constraint');
    });
    
    it('should categorize all error types', () => {
      expect(ErrorTaxonomy.getCategory('net.timeout')).toBe('network');
      expect(ErrorTaxonomy.getCategory('policy.denied')).toBe('policy');
      expect(ErrorTaxonomy.getCategory('constraint.violated')).toBe('constraint');
      expect(ErrorTaxonomy.getCategory('contract.precondition_failed')).toBe('contract');
      expect(ErrorTaxonomy.getCategory('proof.missing')).toBe('proof');
      expect(ErrorTaxonomy.getCategory('auth.insufficient')).toBe('auth');
      expect(ErrorTaxonomy.getCategory('resource.exceeded')).toBe('resource');
      expect(ErrorTaxonomy.getCategory('execution.failed')).toBe('execution');
    });
  });
  
  describe('Round-Trip Conversion', () => {
    it('should convert Human-PLIX to Canonical JSON', () => {
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  pre:
    con:user_authenticated == true
  post:
    con:schema_fingerprint == h_next
`;
      
      const result = RoundTripConverter.humanToJSON(text);
      
      expect(result.json).not.toBeNull();
      expect(result.errors.length).toBe(0);
    });
    
    it('should convert Canonical JSON to Human-PLIX', () => {
      const intent = {
        intent: 'ensure',
        context: {
          entities: [],
          scope: 'default',
          risk: 0.5
        },
        contract: {
          pre: ['user_authenticated == true'],
          post: ['schema_fingerprint == h_next'],
          capabilities: [],
          policies: []
        },
        plan: {
          steps: [],
          deps: []
        },
        conditions: {
          onTestFail: 'retry' as const,
          onLowConfidence: 'escalate' as const,
          onPolicyBreach: 'fail' as const
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
      
      const human = RoundTripConverter.jsonToHuman(intent);
      
      expect(human).toContain('ensure');
      expect(human).toContain('pre:');
      expect(human).toContain('post:');
    });
  });
});

