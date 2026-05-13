/**
 * PLIX Type Checker Tests
 * 
 * Comprehensive tests for quaternion type checking
 * Phase 2, Week 6: Type System Extensions
 */

import {
  PLIXTypeChecker,
  TypeInference
} from './quaternion-type-checker';
import type {
  QQuatLiteral,
  DualQuatLiteral,
  Vec3Literal,
  Vec4Literal,
  QPoseLiteral,
  QAddrLiteral,
  PlaceOperation,
  MoveOperation,
  SenseOperation,
  EmitOperation,
  SelectionRules
} from '../models/quaternion-types';

describe('PLIX Quaternion Type Checker', () => {
  let checker: PLIXTypeChecker;
  
  beforeEach(() => {
    checker = new PLIXTypeChecker();
  });
  
  describe('QQuat Literal Type Inference', () => {
    it('should infer QQuat type for valid quaternion', () => {
      const literal: QQuatLiteral = {
        type: 'quat',
        w: 1.0,
        x: 0.0,
        y: 0.0,
        z: 0.0
      };
      
      const result = checker.inferQQuatLiteral(literal);
      
      expect(result.type).toBe('QQuat');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should warn for non-normalized quaternion', () => {
      const literal: QQuatLiteral = {
        type: 'quat',
        w: 2.0,
        x: 0.0,
        y: 0.0,
        z: 0.0
      };
      
      const result = checker.inferQQuatLiteral(literal);
      
      expect(result.type).toBe('QQuat');
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain('normalized');
    });
    
    it('should error for invalid component types', () => {
      const literal: any = {
        type: 'quat',
        w: 'invalid',
        x: 0.0,
        y: 0.0,
        z: 0.0
      };
      
      const result = checker.inferQQuatLiteral(literal);
      
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('numbers');
    });
  });
  
  describe('DualQuat Literal Type Inference', () => {
    it('should infer DualQuat type for valid dual quaternion', () => {
      const literal: DualQuatLiteral = {
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
          x: 1.0,
          y: 2.0,
          z: 3.0
        }
      };
      
      const result = checker.inferDualQuatLiteral(literal);
      
      expect(result.type).toBe('DualQuat');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should validate screw motion parameters', () => {
      const literal: DualQuatLiteral = {
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
          z: 0.0
        },
        screwAxis: {
          type: 'vec3',
          x: 0.0,
          y: 0.0,
          z: 1.0
        },
        angle: 0.785,
        distance: 0.1
      };
      
      const result = checker.inferDualQuatLiteral(literal);
      
      expect(result.type).toBe('DualQuat');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('QAddr Literal Type Inference', () => {
    it('should infer QAddr type for valid QAddr', () => {
      const literal: QAddrLiteral = {
        type: 'qaddr',
        n: 1,
        l: 'io',
        m: { type: 's3bin', value: 1234 },
        s: 'act',
        morton4d: 0x1234567890ABCDEF,
        s3bin: { type: 's3bin', value: 0xABCD }
      };
      
      const result = checker.inferQAddrLiteral(literal);
      
      expect(result.type).toBe('QAddr');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should error for invalid orbital class', () => {
      const literal: any = {
        type: 'qaddr',
        l: 'invalid'
      };
      
      const result = checker.inferQAddrLiteral(literal);
      
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('orbital class');
    });
    
    it('should error for invalid spin mode', () => {
      const literal: any = {
        type: 'qaddr',
        s: 'invalid'
      };
      
      const result = checker.inferQAddrLiteral(literal);
      
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('spin mode');
    });
    
    it('should error for n out of range', () => {
      const literal: QAddrLiteral = {
        type: 'qaddr',
        n: 300 // Out of range [0, 255]
      };
      
      const result = checker.inferQAddrLiteral(literal);
      
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('n');
    });
  });
  
  describe('Place Operation Type Checking', () => {
    it('should check valid place operation', () => {
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
      
      const result = checker.checkPlaceOperation(operation);
      
      expect(result.type).toBe('PlaceOp');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should check place operation with quantum context', () => {
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
        quantumContext: {
          n: 1,
          l: 'io',
          s: 'act'
        },
        selection: {
          deltaN: 0,
          deltaL: false,
          deltaM: true,
          deltaS: false,
          ok: true
        }
      };
      
      const result = checker.checkPlaceOperation(operation);
      
      expect(result.type).toBe('PlaceOp');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Move Operation Type Checking', () => {
    it('should check valid move operation', () => {
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
      
      const result = checker.checkMoveOperation(operation);
      
      expect(result.type).toBe('MoveOp');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Sense Operation Type Checking', () => {
    it('should check valid sense operation', () => {
      const operation: SenseOperation = {
        type: 'sense_op',
        region: {
          type: 'radius',
          radius: 5.0
        },
        filters: [
          { kind: 'dataset' },
          { n: 2 },
          { l: 'io' }
        ]
      };
      
      const result = checker.checkSenseOperation(operation);
      
      expect(result.type).toBe('SenseOp');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Emit Operation Type Checking', () => {
    it('should check valid emit operation', () => {
      const operation: EmitOperation = {
        type: 'emit_op',
        event: '@event.index_sync'
      };
      
      const result = checker.checkEmitOperation(operation);
      
      expect(result.type).toBe('EmitOp');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Selection Rules Validation', () => {
    it('should validate valid selection rules', () => {
      const rules: SelectionRules = {
        deltaN: 0,
        deltaL: false,
        deltaM: true,
        deltaS: false,
        ok: true
      };
      
      const result = checker.checkSelectionRules(rules);
      
      expect(result.type).toBe('SelectionRules');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should error for invalid deltaN', () => {
      const rules: any = {
        deltaN: 5 // Invalid: must be -1, 0, or 1
      };
      
      const result = checker.checkSelectionRules(rules);
      
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('deltaN');
    });
    
    it('should warn if ok=false without reason', () => {
      const rules: SelectionRules = {
        ok: false
        // No reason provided
      };
      
      const result = checker.checkSelectionRules(rules);
      
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain('reason');
    });
  });
  
  describe('Selection Rules Transition Validation', () => {
    it('should validate valid transition', () => {
      const oldAddr: QAddrLiteral = {
        type: 'qaddr',
        n: 1,
        l: 'io',
        m: { type: 's3bin', value: 1000 },
        s: 'act'
      };
      
      const newAddr: QAddrLiteral = {
        type: 'qaddr',
        n: 1, // Same shell (deltaN = 0)
        l: 'io', // Same class (deltaL = false)
        m: { type: 's3bin', value: 1001 }, // Different orientation (deltaM = true)
        s: 'act' // Same spin (deltaS = false)
      };
      
      const rules: SelectionRules = {
        deltaN: 0,
        deltaL: false,
        deltaM: true,
        deltaS: false,
        ok: true
      };
      
      const result = checker.validateSelectionRulesTransition(oldAddr, newAddr, rules);
      
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
    
    it('should detect invalid transition', () => {
      const oldAddr: QAddrLiteral = {
        type: 'qaddr',
        n: 1,
        l: 'io',
        m: { type: 's3bin', value: 1000 },
        s: 'act'
      };
      
      const newAddr: QAddrLiteral = {
        type: 'qaddr',
        n: 2, // Different shell (deltaN = 1, but rules expect 0)
        l: 'io',
        m: { type: 's3bin', value: 1001 },
        s: 'act'
      };
      
      const rules: SelectionRules = {
        deltaN: 0, // Expect no change
        deltaL: false,
        deltaM: true,
        deltaS: false,
        ok: true
      };
      
      const result = checker.validateSelectionRulesTransition(oldAddr, newAddr, rules);
      
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('deltaN');
    });
  });
  
  describe('Quantum Context Type Checking', () => {
    it('should check valid quantum context', () => {
      const context = {
        n: 1,
        l: 'io' as const,
        m: { type: 's3bin' as const, value: 1234 },
        s: 'act' as const
      };
      
      const result = checker.checkQuantumContext(context);
      
      expect(result.type).toBe('QuantumContext');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should error for invalid quantum context', () => {
      const context: any = {
        n: 300, // Out of range
        l: 'invalid', // Invalid orbital class
        s: 'invalid' // Invalid spin mode
      };
      
      const result = checker.checkQuantumContext(context);
      
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });
});

