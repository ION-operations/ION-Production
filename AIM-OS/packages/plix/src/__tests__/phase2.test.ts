/**
 * PLIX Phase 2 Tests
 * 
 * Tests for AIP compiler, tag resolution, and APOE compilation
 */

import { describe, it, expect } from 'vitest';
import { PLIXParser } from '../parser';
import { PLIXToAIPCompiler } from '../compiler/aip-compiler';

describe('PLIX Phase 2 Tests', () => {
  
  describe('AIP Graph Compilation', () => {
    it('should compile PLIX intent to AIP graph', async () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:schema_intact == h_prev
  post:
    con:schema_fingerprint == h_next
`;
      
      const parseResult = parser.parse(text);
      expect(parseResult.intent).not.toBeNull();
      
      const compiler = new PLIXToAIPCompiler();
      const aipGraph = await compiler.compileToAIPGraph(parseResult.intent!);
      
      expect(aipGraph.nodes.length).toBeGreaterThan(0);
      expect(aipGraph.edges.length).toBeGreaterThan(0);
      expect(aipGraph.nodes.some(n => n.type === 'entity')).toBe(true);
      expect(aipGraph.nodes.some(n => n.type === 'action' || n.type === 'capability')).toBe(true);
    });
    
    it('should include constraint nodes in AIP graph', async () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  pre:
    con:schema_intact == h_prev
    con:rowcount_stable <= 0
  post:
    con:schema_fingerprint == h_next
`;
      
      const parseResult = parser.parse(text);
      const compiler = new PLIXToAIPCompiler();
      const aipGraph = await compiler.compileToAIPGraph(parseResult.intent!);
      
      const constraintNodes = aipGraph.nodes.filter(n => n.type === 'constraint');
      expect(constraintNodes.length).toBeGreaterThanOrEqual(2); // At least 2 preconditions
    });
  });
  
  describe('Tag Resolution', () => {
    it('should resolve tags with cache', async () => {
      const compiler = new PLIXToAIPCompiler();
      
      const result1 = await compiler.resolveTag('plix://db/table/users#rev@h_98fa');
      expect(result1.tag).toBe('plix://db/table/users#rev@h_98fa');
      
      // Second call should use cache
      const result2 = await compiler.resolveTag('plix://db/table/users#rev@h_98fa');
      expect(result2.source).toBe('cache');
    });
    
    it('should handle invalid tag format', async () => {
      const compiler = new PLIXToAIPCompiler();
      
      const result = await compiler.resolveTag('invalid_tag_format');
      expect(result.source).toBe('not_found');
      expect(result.confidence).toBe(0.0);
    });
  });
  
  describe('APOE Compilation', () => {
    it('should compile PLIX plan to APOE execution plan', async () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  plan [
    step validate_preconditions
    step migrate_schema
      depends_on: [validate_preconditions]
  ]
`;
      
      const parseResult = parser.parse(text);
      const compiler = new PLIXToAIPCompiler();
      const apoeResult = await compiler.compileToAPOE(parseResult.intent!);
      
      expect(apoeResult.plan).not.toBeNull();
      expect(apoeResult.plan.steps.length).toBeGreaterThan(0);
      expect(apoeResult.plan.name).toBe('ensure');
    });
    
    it('should include dependencies in APOE plan', async () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  plan [
    step step1
    step step2
      depends_on: [step1]
    step step3
      depends_on: [step2]
  ]
`;
      
      const parseResult = parser.parse(text);
      const compiler = new PLIXToAIPCompiler();
      const apoeResult = await compiler.compileToAPOE(parseResult.intent!);
      
      expect(Object.keys(apoeResult.plan.dependencies).length).toBeGreaterThan(0);
    });
    
    it('should generate witness requirements', async () => {
      const parser = new PLIXParser();
      const text = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  plan [
    step validate_preconditions
      confidence_threshold: 0.90
  ]
`;
      
      const parseResult = parser.parse(text);
      const compiler = new PLIXToAIPCompiler();
      const apoeResult = await compiler.compileToAPOE(parseResult.intent!);
      
      expect(apoeResult.witnessRequirements.length).toBeGreaterThan(0);
      expect(apoeResult.witnessRequirements.some(r => r.operation.includes('execute_plan'))).toBe(true);
      expect(apoeResult.witnessRequirements.some(r => r.operation.includes('execute_step'))).toBe(true);
    });
  });
  
  describe('VIF Witness Requirements', () => {
    it('should generate witness requirements from evidence clauses', () => {
      const intent = {
        intent: 'ensure',
        context: {
          entities: [],
          scope: 'default',
          risk: 0.5
        },
        contract: {
          pre: [],
          post: [],
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
      
      (intent as any).evidence = ['w:pg.schema_before', 'w:pg.schema_after'];
      
      const compiler = new PLIXToAIPCompiler();
      const requirements = compiler.generateWitnessRequirements(intent);
      
      expect(requirements.length).toBeGreaterThan(0);
      expect(requirements[0].operation).toContain('execute_plan');
    });
  });
  
  describe('Cache Management', () => {
    it('should clear cache', () => {
      const compiler = new PLIXToAIPCompiler();
      
      compiler.resolveTag('plix://test/tag');
      expect(compiler.getCacheStats().size).toBeGreaterThan(0);
      
      compiler.clearCache();
      expect(compiler.getCacheStats().size).toBe(0);
    });
    
    it('should provide cache statistics', () => {
      const compiler = new PLIXToAIPCompiler();
      
      const stats = compiler.getCacheStats();
      expect(stats).toHaveProperty('size');
      expect(stats).toHaveProperty('hits');
      expect(stats).toHaveProperty('misses');
    });
  });
});

