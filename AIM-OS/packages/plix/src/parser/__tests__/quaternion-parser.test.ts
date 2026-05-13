/**
 * PLIX Quaternion Parser Tests
 * 
 * Comprehensive tests for quaternion parser
 * Phase 2, Week 5: Grammar Extensions
 */

import {
  parseQQuatLiteral,
  parseDualQuatLiteral,
  parseVec3Literal,
  parseVec4Literal,
  parseQPoseLiteral,
  parseQAddrLiteral,
  parsePlaceOperation,
  parseMoveOperation,
  parseSenseOperation,
  parseEmitOperation,
  parseQuantumContext,
  parseSelectionRules
} from './quaternion-parser';

describe('PLIX Quaternion Parser', () => {
  describe('QQuat Literal Parsing', () => {
    it('should parse quaternion literal with positional parameters', () => {
      const result = parseQQuatLiteral('quat(1.0, 0.0, 0.0, 0.0)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('quat');
      expect(result.literal?.w).toBe(1.0);
      expect(result.literal?.x).toBe(0.0);
      expect(result.errors).toHaveLength(0);
    });
    
    it('should parse quaternion literal with named parameters', () => {
      const result = parseQQuatLiteral('quat(w: 0.707, x: 0.707, y: 0.0, z: 0.0)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('quat');
      expect(result.literal?.w).toBeCloseTo(0.707);
      expect(result.errors).toHaveLength(0);
    });
    
    it('should error on invalid quaternion literal', () => {
      const result = parseQQuatLiteral('invalid');
      
      expect(result.literal).toBeNull();
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });
  
  describe('Vec3 Literal Parsing', () => {
    it('should parse Vec3 literal', () => {
      const result = parseVec3Literal('vec3(1.0, 2.0, 3.0)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('vec3');
      expect(result.literal?.x).toBe(1.0);
      expect(result.literal?.y).toBe(2.0);
      expect(result.literal?.z).toBe(3.0);
      expect(result.errors).toHaveLength(0);
    });
    
    it('should parse Vec3 as tuple', () => {
      const result = parseVec3Literal('(1.0, 2.0, 3.0)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('vec3');
    });
  });
  
  describe('Vec4 Literal Parsing', () => {
    it('should parse Vec4 literal', () => {
      const result = parseVec4Literal('vec4(0.1, 0.2, 0.3, 1234567890)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('vec4');
      expect(result.literal?.x).toBe(0.1);
      expect(result.literal?.tau).toBe(1234567890);
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('DualQuat Literal Parsing', () => {
    it('should parse dual quaternion literal', () => {
      const result = parseDualQuatLiteral('dq(quat(1,0,0,0), vec3(1,2,3))');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('dualquat');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should parse screw motion literal', () => {
      const result = parseDualQuatLiteral('dq(screw_axis: vec3(0,0,1), θ: 0.785, t: 0.1)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('dualquat');
      expect(result.literal?.screwAxis).toBeDefined();
      expect(result.literal?.angle).toBeCloseTo(0.785);
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('QPose Literal Parsing', () => {
    it('should parse QPose literal', () => {
      const result = parseQPoseLiteral('pose(vec4(0.1,0.2,0.3,now), quat(1,0,0,0))');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('pose');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('QAddr Literal Parsing', () => {
    it('should parse QAddr literal', () => {
      const result = parseQAddrLiteral('qaddr(n: 1, l: io, m: s3bin(1234), s: act)');
      
      expect(result.literal).not.toBeNull();
      expect(result.literal?.type).toBe('qaddr');
      expect(result.literal?.n).toBe(1);
      expect(result.literal?.l).toBe('io');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Place Operation Parsing', () => {
    it('should parse place operation', () => {
      const result = parsePlaceOperation('place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now)');
      
      expect(result.operation).not.toBeNull();
      expect(result.operation?.type).toBe('place_op');
      expect(result.operation?.entity).toBe('@svc.pg');
      expect(result.errors).toHaveLength(0);
    });
    
    it('should parse place operation with orientation', () => {
      const result = parsePlaceOperation('place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now) ori: ⟨+k, 15°⟩');
      
      expect(result.operation).not.toBeNull();
      expect(result.operation?.orientation).toBeDefined();
    });
  });
  
  describe('Move Operation Parsing', () => {
    it('should parse move operation', () => {
      const result = parseMoveOperation('move @svc.pg by dq(screw_axis: +k, θ: 5°, t: 2cm)');
      
      expect(result.operation).not.toBeNull();
      expect(result.operation?.type).toBe('move_op');
      expect(result.operation?.entity).toBe('@svc.pg');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Sense Operation Parsing', () => {
    it('should parse sense operation', () => {
      const result = parseSenseOperation('sense radius: 5cm where kind: "dataset"');
      
      expect(result.operation).not.toBeNull();
      expect(result.operation?.type).toBe('sense_op');
      expect(result.operation?.region).toBeDefined();
      expect(result.operation?.filters).toBeDefined();
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Emit Operation Parsing', () => {
    it('should parse emit operation', () => {
      const result = parseEmitOperation('emit @event.index_sync');
      
      expect(result.operation).not.toBeNull();
      expect(result.operation?.type).toBe('emit_op');
      expect(result.operation?.event).toBe('@event.index_sync');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Quantum Context Parsing', () => {
    it('should parse quantum context', () => {
      const result = parseQuantumContext('with Q(n: 1, l: io, m: cone(N, 30°), s: act)');
      
      expect(result.context).not.toBeNull();
      expect(result.context?.n).toBe(1);
      expect(result.context?.l).toBe('io');
      expect(result.context?.s).toBe('act');
      expect(result.errors).toHaveLength(0);
    });
  });
  
  describe('Selection Rules Parsing', () => {
    it('should parse selection rules', () => {
      const result = parseSelectionRules('selection: {Δn: 0, Δl: false, Δm: true, Δs: false, ok: true}');
      
      expect(result.rules).not.toBeNull();
      expect(result.rules?.deltaN).toBe(0);
      expect(result.rules?.deltaL).toBe(false);
      expect(result.rules?.ok).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });
});

