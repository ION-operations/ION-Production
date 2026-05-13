/**
 * PLIX Quaternion Runtime Tests
 * 
 * Comprehensive tests for quaternion runtime
 * Phase 2, Week 8: Runtime Integration
 */

import {
  PLIXQuaternionRuntime,
  DefaultKernelBridge,
  DefaultFieldSolver
} from './quaternion-runtime';
import type {
  GeometricSyscall,
  GeometricCompilationResult
} from '../compiler/quaternion-compiler';
import type { QAddrLiteral } from '../models/quaternion-types';

// Mock CMC Storage
class MockCMCStorage {
  private entities: Map<string, any> = new Map();
  
  async storeEntity(entityId: string, qaddr: QAddrLiteral, state: any): Promise<void> {
    this.entities.set(entityId, { qaddr, state });
  }
  
  async retrieveEntity(entityId: string): Promise<any | null> {
    return this.entities.get(entityId) || null;
  }
  
  async updateEntity(entityId: string, qaddr: QAddrLiteral, state: any): Promise<void> {
    this.entities.set(entityId, { qaddr, state });
  }
  
  async queryByQAddr(qaddr: QAddrLiteral): Promise<string[]> {
    const results: string[] = [];
    for (const [id, data] of this.entities.entries()) {
      if (this.compareQAddr(data.qaddr, qaddr)) {
        results.push(id);
      }
    }
    return results;
  }
  
  async queryByRegion(region: any): Promise<string[]> {
    return Array.from(this.entities.keys());
  }
  
  private compareQAddr(a: QAddrLiteral, b: QAddrLiteral): boolean {
    return a.n === b.n && a.l === b.l && a.s === b.s;
  }
}

describe('PLIX Quaternion Runtime', () => {
  let runtime: PLIXQuaternionRuntime;
  let mockCMC: MockCMCStorage;
  
  beforeEach(() => {
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
  
  describe('Place Syscall Execution', () => {
    it('should execute place syscall successfully', async () => {
      const syscall: GeometricSyscall = {
        type: 'place',
        entityId: '@svc.pg',
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
      };
      
      const result = await runtime.executeSyscall(syscall);
      
      expect(result.success).toBe(true);
      expect(result.entityId).toBe('@svc.pg');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should store entity in CMC', async () => {
      const syscall: GeometricSyscall = {
        type: 'place',
        entityId: '@svc.pg',
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
      };
      
      await runtime.executeSyscall(syscall);
      
      const stored = await mockCMC.retrieveEntity('@svc.pg');
      expect(stored).not.toBeNull();
      expect(stored.qaddr).toEqual(syscall.qaddr);
    });
    
    it('should initialize field values', async () => {
      const syscall: GeometricSyscall = {
        type: 'place',
        entityId: '@svc.pg',
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
      };
      
      await runtime.executeSyscall(syscall);
      
      const fields = await runtime.getFieldValues('@svc.pg');
      expect(fields.kappa).toBeGreaterThan(0);
      expect(fields.lambda).toBeGreaterThanOrEqual(0);
      expect(fields.rho).toBeGreaterThan(0);
    });
  });
  
  describe('Move Syscall Execution', () => {
    it('should execute move syscall successfully', async () => {
      // First place entity
      const placeSyscall: GeometricSyscall = {
        type: 'place',
        entityId: '@svc.pg',
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
      };
      await runtime.executeSyscall(placeSyscall);
      
      // Then move it
      const moveSyscall: GeometricSyscall = {
        type: 'move',
        entityId: '@svc.pg',
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
      
      const result = await runtime.executeSyscall(moveSyscall);
      
      expect(result.success).toBe(true);
      expect(result.entityId).toBe('@svc.pg');
    });
  });
  
  describe('Sense Syscall Execution', () => {
    it('should execute sense syscall successfully', async () => {
      const syscall: GeometricSyscall = {
        type: 'sense',
        region: {
          type: 'radius',
          radius: 5.0
        },
        filters: [
          { kind: 'dataset' }
        ]
      };
      
      const result = await runtime.executeSyscall(syscall);
      
      expect(result.success).toBe(true);
      expect(result.result).toBeDefined();
      expect(result.result.entities).toBeDefined();
    });
  });
  
  describe('Emit Syscall Execution', () => {
    it('should execute emit syscall successfully', async () => {
      const syscall: GeometricSyscall = {
        type: 'emit',
        event: '@event.index_sync',
        entityId: '@svc.pg'
      };
      
      const result = await runtime.executeSyscall(syscall);
      
      expect(result.success).toBe(true);
    });
    
    it('should update field values on emit', async () => {
      // First place entity
      const placeSyscall: GeometricSyscall = {
        type: 'place',
        entityId: '@svc.pg',
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
      };
      await runtime.executeSyscall(placeSyscall);
      
      const fieldsBefore = await runtime.getFieldValues('@svc.pg');
      
      // Emit event
      const emitSyscall: GeometricSyscall = {
        type: 'emit',
        event: '@event.index_sync',
        entityId: '@svc.pg'
      };
      await runtime.executeSyscall(emitSyscall);
      
      const fieldsAfter = await runtime.getFieldValues('@svc.pg');
      
      // Lambda should increase (attention)
      expect(fieldsAfter.lambda).toBeGreaterThan(fieldsBefore.lambda);
    });
  });
  
  describe('Batch Execution', () => {
    it('should execute batch of syscalls', async () => {
      const compilationResult: GeometricCompilationResult = {
        syscalls: [
          {
            type: 'place',
            entityId: '@svc.pg',
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
            type: 'emit',
            event: '@event.index_sync',
            entityId: '@svc.pg'
          }
        ],
        resolvedQAddrs: new Map(),
        totalHamiltonianCost: 18.0,
        errors: [],
        warnings: []
      };
      
      const result = await runtime.executeBatch(compilationResult);
      
      expect(result.results).toHaveLength(2);
      expect(result.successCount).toBeGreaterThan(0);
      expect(result.totalHamiltonianCost).toBe(18.0);
    });
  });
  
  describe('Field Diffusion', () => {
    it('should diffuse fields', async () => {
      // Place entity
      const placeSyscall: GeometricSyscall = {
        type: 'place',
        entityId: '@svc.pg',
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
      };
      await runtime.executeSyscall(placeSyscall);
      
      const fieldsBefore = await runtime.getFieldValues('@svc.pg');
      
      // Diffuse fields
      await runtime.diffuseFields(1.0);
      
      const fieldsAfter = await runtime.getFieldValues('@svc.pg');
      
      // Fields should decay
      expect(fieldsAfter.lambda).toBeLessThanOrEqual(fieldsBefore.lambda);
    });
  });
});

