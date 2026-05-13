/**
 * PLIX Quaternion Compiler Tests
 * 
 * Comprehensive tests for quaternion compiler
 * Phase 2, Week 7: Compiler Extensions
 */

import { PLIXQuaternionCompiler } from './quaternion-compiler';
import type {
  PlaceOperation,
  MoveOperation,
  SenseOperation,
  EmitOperation,
  QAddrLiteral
} from '../models/quaternion-types';
import type { PLIxIntent } from '../models/schema';

describe('PLIX Quaternion Compiler', () => {
  let compiler: PLIXQuaternionCompiler;
  
  beforeEach(() => {
    compiler = new PLIXQuaternionCompiler();
  });
  
  describe('Tag → QAddr Resolution', () => {
    it('should resolve tag to QAddr from quantum context', async () => {
      const tag = '@svc.pg';
      const quantumContext = {
        n: 1,
        l: 'io' as const,
        m: { type: 's3bin' as const, value: 1234 },
        s: 'act' as const
      };
      
      const result = await compiler.resolveTagToQAddr(tag, quantumContext);
      
      expect(result.tag).toBe(tag);
      expect(result.qaddr).not.toBeNull();
      expect(result.qaddr?.n).toBe(1);
      expect(result.qaddr?.l).toBe('io');
      expect(result.source).toBe('computed');
    });
    
    it('should cache resolved QAddrs', async () => {
      const tag = '@svc.pg';
      const quantumContext = {
        n: 1,
        l: 'io' as const
      };
      
      const result1 = await compiler.resolveTagToQAddr(tag, quantumContext);
      const result2 = await compiler.resolveTagToQAddr(tag, quantumContext);
      
      expect(result2.source).toBe('cache');
      expect(result2.qaddr).toEqual(result1.qaddr);
    });
    
    it('should return not_found for unresolvable tag', async () => {
      const tag = '@nonexistent';
      
      const result = await compiler.resolveTagToQAddr(tag);
      
      expect(result.source).toBe('not_found');
      expect(result.qaddr).toBeNull();
    });
  });
  
  describe('Place Operation Compilation', () => {
    it('should compile place operation to syscall', async () => {
      const operation: PlaceOperation = {
        type: 'place_op',
        entity: '@svc.pg',
        position: {
          type: 'vec4',
          x: 0.1,
          y: 0.0,
          z: 0.0,
          tau: 1234567890
        },
        orientation: {
          type: 'quat',
          w: 1.0,
          x: 0.0,
          y: 0.0,
          z: 0.0
        }
      };
      
      const intent: PLIxIntent = {
        intent: 'ensure',
        context: { entities: [], scope: 'default', risk: 0.5 },
        contract: { pre: [], post: [], capabilities: [], policies: [] },
        plan: { steps: [], deps: [] },
        conditions: { onTestFail: 'retry', onLowConfidence: 'escalate', onPolicyBreach: 'fail' },
        evidence: { required: [], produce: [] },
        telemetry: {
          confidenceThresholds: { minimum: 0.7, warning: 0.8, critical: 0.9 },
          timeouts: { step: 30000, plan: 300000 }
        },
        provenance: {
          executed_by: 'system',
          executed_at: new Date().toISOString(),
          plan_version: '1.0',
          lineage: []
        },
        geometric: {
          operations: [operation]
        }
      };
      
      const result = await compiler.compileGeometricOperations(intent);
      
      expect(result.syscalls).toHaveLength(1);
      expect(result.syscalls[0].type).toBe('place');
      expect(result.syscalls[0].entityId).toBe('@svc.pg');
      expect(result.syscalls[0].position).toEqual(operation.position);
    });
  });
  
  describe('Move Operation Compilation', () => {
    it('should compile move operation to syscall', async () => {
      const operation: MoveOperation = {
        type: 'move_op',
        entity: '@svc.pg',
        deltaPose: {
          type: 'dualquat',
          rotation: {
            type: 'quat',
            w: 1.0,
            x: 0.0,
            y: 0.0,
            z: 0.0
          },
          translation: {
            type: 'vec3',
            x: 0.0,
            y: 0.0,
            z: 0.1
          }
        }
      };
      
      const intent: PLIxIntent = {
        intent: 'ensure',
        context: { entities: [], scope: 'default', risk: 0.5 },
        contract: { pre: [], post: [], capabilities: [], policies: [] },
        plan: { steps: [], deps: [] },
        conditions: { onTestFail: 'retry', onLowConfidence: 'escalate', onPolicyBreach: 'fail' },
        evidence: { required: [], produce: [] },
        telemetry: {
          confidenceThresholds: { minimum: 0.7, warning: 0.8, critical: 0.9 },
          timeouts: { step: 30000, plan: 300000 }
        },
        provenance: {
          executed_by: 'system',
          executed_at: new Date().toISOString(),
          plan_version: '1.0',
          lineage: []
        },
        geometric: {
          operations: [operation]
        }
      };
      
      const result = await compiler.compileGeometricOperations(intent);
      
      expect(result.syscalls).toHaveLength(1);
      expect(result.syscalls[0].type).toBe('move');
      expect(result.syscalls[0].entityId).toBe('@svc.pg');
      expect(result.syscalls[0].deltaPose).toEqual(operation.deltaPose);
    });
  });
  
  describe('Sense Operation Compilation', () => {
    it('should compile sense operation to syscall', async () => {
      const operation: SenseOperation = {
        type: 'sense_op',
        region: {
          type: 'radius',
          radius: 5.0
        },
        filters: [
          { kind: 'dataset' }
        ]
      };
      
      const intent: PLIxIntent = {
        intent: 'ensure',
        context: { entities: [], scope: 'default', risk: 0.5 },
        contract: { pre: [], post: [], capabilities: [], policies: [] },
        plan: { steps: [], deps: [] },
        conditions: { onTestFail: 'retry', onLowConfidence: 'escalate', onPolicyBreach: 'fail' },
        evidence: { required: [], produce: [] },
        telemetry: {
          confidenceThresholds: { minimum: 0.7, warning: 0.8, critical: 0.9 },
          timeouts: { step: 30000, plan: 300000 }
        },
        provenance: {
          executed_by: 'system',
          executed_at: new Date().toISOString(),
          plan_version: '1.0',
          lineage: []
        },
        geometric: {
          operations: [operation]
        }
      };
      
      const result = await compiler.compileGeometricOperations(intent);
      
      expect(result.syscalls).toHaveLength(1);
      expect(result.syscalls[0].type).toBe('sense');
      expect(result.syscalls[0].region).toEqual(operation.region);
      expect(result.syscalls[0].filters).toEqual(operation.filters);
    });
  });
  
  describe('Emit Operation Compilation', () => {
    it('should compile emit operation to syscall', async () => {
      const operation: EmitOperation = {
        type: 'emit_op',
        event: '@event.index_sync'
      };
      
      const intent: PLIxIntent = {
        intent: 'ensure',
        context: { entities: [], scope: 'default', risk: 0.5 },
        contract: { pre: [], post: [], capabilities: [], policies: [] },
        plan: { steps: [], deps: [] },
        conditions: { onTestFail: 'retry', onLowConfidence: 'escalate', onPolicyBreach: 'fail' },
        evidence: { required: [], produce: [] },
        telemetry: {
          confidenceThresholds: { minimum: 0.7, warning: 0.8, critical: 0.9 },
          timeouts: { step: 30000, plan: 300000 }
        },
        provenance: {
          executed_by: 'system',
          executed_at: new Date().toISOString(),
          plan_version: '1.0',
          lineage: []
        },
        geometric: {
          operations: [operation]
        }
      };
      
      const result = await compiler.compileGeometricOperations(intent);
      
      expect(result.syscalls).toHaveLength(1);
      expect(result.syscalls[0].type).toBe('emit');
      expect(result.syscalls[0].event).toBe('@event.index_sync');
    });
  });
  
  describe('Hamiltonian Cost Calculation', () => {
    it('should calculate cost for place operation', () => {
      const syscall = {
        type: 'place' as const,
        entityId: '@svc.pg',
        position: { type: 'vec4' as const, x: 0, y: 0, z: 0, tau: 0 }
      };
      
      const cost = compiler.calculateHamiltonianCost(syscall);
      
      expect(cost).toBeGreaterThan(0);
      expect(cost).toBeLessThan(100); // Reasonable upper bound
    });
    
    it('should adjust cost for n-tier', () => {
      const syscall1 = {
        type: 'place' as const,
        entityId: '@svc.pg',
        quantumContext: { n: 0 } // Lower n = lower cost
      };
      
      const syscall2 = {
        type: 'place' as const,
        entityId: '@svc.pg',
        quantumContext: { n: 3 } // Higher n = higher cost
      };
      
      const cost1 = compiler.calculateHamiltonianCost(syscall1);
      const cost2 = compiler.calculateHamiltonianCost(syscall2);
      
      expect(cost1).toBeLessThan(cost2);
    });
    
    it('should adjust cost for selection rules', () => {
      const syscall1 = {
        type: 'place' as const,
        entityId: '@svc.pg'
      };
      
      const syscall2 = {
        type: 'place' as const,
        entityId: '@svc.pg',
        selection: {
          deltaN: 0,
          deltaL: false,
          deltaM: true,
          deltaS: false
        }
      };
      
      const cost1 = compiler.calculateHamiltonianCost(syscall1);
      const cost2 = compiler.calculateHamiltonianCost(syscall2);
      
      expect(cost2).toBeGreaterThan(cost1);
    });
  });
  
  describe('Hamiltonian Budget Validation', () => {
    it('should validate cost against budget', () => {
      const syscall = {
        type: 'place' as const,
        entityId: '@svc.pg'
      };
      
      const budget = 100.0;
      const validation = compiler.validateHamiltonianBudget(syscall, budget);
      
      expect(validation.valid).toBe(true);
      expect(validation.cost).toBeGreaterThan(0);
      expect(validation.budget).toBe(budget);
      expect(validation.remaining).toBeGreaterThan(0);
    });
    
    it('should detect budget violation', () => {
      const syscall = {
        type: 'place' as const,
        entityId: '@svc.pg'
      };
      
      const budget = 1.0; // Very small budget
      const validation = compiler.validateHamiltonianBudget(syscall, budget);
      
      expect(validation.valid).toBe(false);
      expect(validation.remaining).toBeLessThan(0);
    });
  });
  
  describe('Cache Management', () => {
    it('should clear cache', async () => {
      const tag = '@svc.pg';
      const quantumContext = { n: 1 };
      
      await compiler.resolveTagToQAddr(tag, quantumContext);
      expect(compiler['tagCache'].size).toBeGreaterThan(0);
      
      compiler.clearCache();
      expect(compiler['tagCache'].size).toBe(0);
    });
    
    it('should invalidate cache for tag', async () => {
      const tag = '@svc.pg';
      const quantumContext = { n: 1 };
      
      await compiler.resolveTagToQAddr(tag, quantumContext);
      expect(compiler['tagCache'].size).toBeGreaterThan(0);
      
      compiler.invalidateCache(tag);
      expect(compiler['tagCache'].size).toBe(0);
    });
  });
});

