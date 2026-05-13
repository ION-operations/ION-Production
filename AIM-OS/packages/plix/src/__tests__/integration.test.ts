/**
 * PLIX Quaternion Integration Tests
 * 
 * End-to-end tests for parser → type checker → compiler → runtime pipeline
 * Phase 2: Complete Integration
 */

import { PLIXParser } from '../parser/index';
import { PLIXQuaternionCompiler } from '../compiler/quaternion-compiler';
import { PLIXQuaternionRuntime, DefaultKernelBridge, DefaultFieldSolver } from '../runtime/quaternion-runtime';
import type { PLIxIntent } from '../models/schema';

// Mock CMC Storage
class MockCMCStorage {
  private entities: Map<string, any> = new Map();
  
  async storeEntity(entityId: string, qaddr: any, state: any): Promise<void> {
    this.entities.set(entityId, { qaddr, state });
  }
  
  async retrieveEntity(entityId: string): Promise<any | null> {
    return this.entities.get(entityId) || null;
  }
  
  async updateEntity(entityId: string, qaddr: any, state: any): Promise<void> {
    this.entities.set(entityId, { qaddr, state });
  }
  
  async queryByQAddr(qaddr: any): Promise<string[]> {
    return Array.from(this.entities.keys());
  }
  
  async queryByRegion(region: any): Promise<string[]> {
    return Array.from(this.entities.keys());
  }
}

describe('PLIX Quaternion End-to-End Integration', () => {
  let parser: PLIXParser;
  let compiler: PLIXQuaternionCompiler;
  let runtime: PLIXQuaternionRuntime;
  let mockCMC: MockCMCStorage;
  
  beforeEach(() => {
    parser = new PLIXParser();
    compiler = new PLIXQuaternionCompiler();
    mockCMC = new MockCMCStorage();
    runtime = new PLIXQuaternionRuntime({
      kernelBridge: new DefaultKernelBridge(),
      cmcStorage: mockCMC as any,
      fieldSolver: new DefaultFieldSolver(),
      actorQAddr: {
        type: 'qaddr',
        n: 1,
        l: 'io',
        s: 'act'
      }
    });
  });
  
  describe('Full Pipeline: Parse → Type Check → Compile → Execute', () => {
    it('should execute complete pipeline for place operation', async () => {
      const plixText = `
ensure ent:@svc.pg
  place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now) ori: ⟨+k, 15°⟩
    with Q(n: 1, l: io, s: act)
`;
      
      // Step 1: Parse
      const parseResult = parser.parse(plixText);
      expect(parseResult.intent).not.toBeNull();
      expect(parseResult.errors).toHaveLength(0);
      
      // Step 2: Compile
      const compileResult = await compiler.compileGeometricOperations(parseResult.intent!);
      expect(compileResult.syscalls).toHaveLength(1);
      expect(compileResult.errors).toHaveLength(0);
      
      // Step 3: Execute
      const executeResult = await runtime.executeBatch(compileResult);
      expect(executeResult.successCount).toBeGreaterThan(0);
      expect(executeResult.failureCount).toBe(0);
    });
    
    it('should catch type errors during parsing', () => {
      const plixText = `
ensure ent:@svc.pg
  place @svc.pg at invalid_position
    with Q(n: 300, l: invalid, s: invalid)
`;
      
      const parseResult = parser.parse(plixText);
      
      // Should have type errors
      expect(parseResult.errors.length).toBeGreaterThan(0);
      const typeErrors = parseResult.errors.filter(e => e.message.includes('Type error'));
      expect(typeErrors.length).toBeGreaterThan(0);
    });
    
    it('should catch type errors during compilation', async () => {
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
          operations: [
            {
              type: 'place_op',
              entity: '@svc.pg',
              position: {
                type: 'vec4',
                x: 0.1,
                y: 0.0,
                z: 0.0,
                tau: 1234567890
              },
              quantumContext: {
                n: 300, // Invalid: out of range
                l: 'invalid' as any, // Invalid orbital class
                s: 'invalid' as any // Invalid spin mode
              }
            }
          ]
        }
      };
      
      const compileResult = await compiler.compileGeometricOperations(intent);
      
      // Should have type errors
      expect(compileResult.errors.length).toBeGreaterThan(0);
      expect(compileResult.syscalls.length).toBe(0); // Invalid operations skipped
    });
    
    it('should execute move operation pipeline', async () => {
      const plixText = `
ensure ent:@svc.pg
  place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now)
  move @svc.pg by dq(screw_axis: +k, θ: 5°, t: 2cm)
`;
      
      // Parse
      const parseResult = parser.parse(plixText);
      expect(parseResult.intent).not.toBeNull();
      
      // Compile
      const compileResult = await compiler.compileGeometricOperations(parseResult.intent!);
      expect(compileResult.syscalls.length).toBeGreaterThanOrEqual(1);
      
      // Execute
      const executeResult = await runtime.executeBatch(compileResult);
      expect(executeResult.successCount).toBeGreaterThan(0);
    });
    
    it('should calculate Hamiltonian cost correctly', async () => {
      const plixText = `
ensure ent:@svc.pg
  place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now)
  emit @event.index_sync
`;
      
      const parseResult = parser.parse(plixText);
      const compileResult = await compiler.compileGeometricOperations(parseResult.intent!);
      
      // Check Hamiltonian cost
      expect(compileResult.totalHamiltonianCost).toBeGreaterThan(0);
      expect(compileResult.syscalls.every(s => s.hamiltonianCost !== undefined)).toBe(true);
    });
    
    it('should validate Hamiltonian budget', async () => {
      const plixText = `
ensure ent:@svc.pg
  place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now)
`;
      
      const parseResult = parser.parse(plixText);
      const compileResult = await compiler.compileGeometricOperations(parseResult.intent!);
      
      // Validate budget
      const budget = 100.0;
      for (const syscall of compileResult.syscalls) {
        const validation = compiler.validateHamiltonianBudget(syscall, budget);
        expect(validation.valid).toBe(true);
        expect(validation.cost).toBeGreaterThan(0);
        expect(validation.remaining).toBeGreaterThanOrEqual(0);
      }
    });
  });
  
  describe('Type Checker Integration', () => {
    it('should type check during parsing', () => {
      const plixText = `
ensure ent:@svc.pg
  place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now)
    with Q(n: 1, l: io, s: act)
`;
      
      const parseResult = parser.parse(plixText);
      
      // Should have no type errors
      const typeErrors = parseResult.errors.filter(e => e.message.includes('Type error'));
      expect(typeErrors.length).toBe(0);
    });
    
    it('should type check during compilation', async () => {
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
          operations: [
            {
              type: 'place_op',
              entity: '@svc.pg',
              position: {
                type: 'vec4',
                x: 0.1,
                y: 0.0,
                z: 0.0,
                tau: 1234567890
              },
              quantumContext: {
                n: 1,
                l: 'io',
                s: 'act'
              }
            }
          ]
        }
      };
      
      const compileResult = await compiler.compileGeometricOperations(intent);
      
      // Should have no type errors
      expect(compileResult.errors.filter(e => e.includes('Type error')).length).toBe(0);
      expect(compileResult.syscalls.length).toBe(1);
    });
  });
  
  describe('Runtime Integration', () => {
    it('should store entities in CMC after place', async () => {
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
          operations: [
            {
              type: 'place_op',
              entity: '@svc.pg',
              qaddr: {
                type: 'qaddr',
                n: 1,
                l: 'io',
                s: 'act'
              },
              position: {
                type: 'vec4',
                x: 0.1,
                y: 0.0,
                z: 0.0,
                tau: 1234567890
              }
            }
          ]
        }
      };
      
      const compileResult = await compiler.compileGeometricOperations(intent);
      const executeResult = await runtime.executeBatch(compileResult);
      
      expect(executeResult.successCount).toBeGreaterThan(0);
      
      // Check CMC storage
      const stored = await mockCMC.retrieveEntity('@svc.pg');
      expect(stored).not.toBeNull();
    });
    
    it('should update field values after emit', async () => {
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
          operations: [
            {
              type: 'place_op',
              entity: '@svc.pg',
              qaddr: {
                type: 'qaddr',
                n: 1,
                l: 'io',
                s: 'act'
              },
              position: {
                type: 'vec4',
                x: 0.1,
                y: 0.0,
                z: 0.0,
                tau: 1234567890
              }
            },
            {
              type: 'emit_op',
              event: '@event.index_sync',
              entityId: '@svc.pg'
            }
          ]
        }
      };
      
      const compileResult = await compiler.compileGeometricOperations(intent);
      await runtime.executeBatch(compileResult);
      
      // Check field values
      const fields = await runtime.getFieldValues('@svc.pg');
      expect(fields.lambda).toBeGreaterThan(0); // Attention increased
    });
  });
});

