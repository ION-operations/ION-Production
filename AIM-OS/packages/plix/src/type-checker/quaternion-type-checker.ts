/**
 * PLIX Type System Extensions
 * 
 * Type checking for geometric and quantum types
 * Phase 2, Week 6: Type System Extensions
 */

import type {
  QQuatLiteral,
  DualQuatLiteral,
  DoubleQuatLiteral,
  Vec3Literal,
  Vec4Literal,
  QPoseLiteral,
  QAddrLiteral,
  PlaceOperation,
  MoveOperation,
  SenseOperation,
  EmitOperation,
  QuantumContextBlock,
  QuantumContext,
  SelectionRules,
  GeometricOperation,
  OrbitalClass,
  SpinMode
} from '../models/quaternion-types';

/**
 * PLIX Type System
 */
export type PLIXType =
  // Primitive types
  | 'string'
  | 'number'
  | 'boolean'
  | 'null'
  // Quaternion types
  | 'QQuat'
  | 'DualQuat'
  | 'DoubleQuat'
  | 'Vec3'
  | 'Vec4'
  | 'QPose'
  | 'QAddr'
  // Geometric operation types
  | 'PlaceOp'
  | 'MoveOp'
  | 'SenseOp'
  | 'EmitOp'
  // Quantum types
  | 'QuantumContext'
  | 'SelectionRules'
  // Composite types
  | { type: 'array'; element: PLIXType }
  | { type: 'object'; fields: Record<string, PLIXType> }
  | { type: 'union'; variants: PLIXType[] }
  | { type: 'optional'; inner: PLIXType };

/**
 * Type inference result
 */
export interface TypeInferenceResult {
  type: PLIXType | null;
  errors: string[];
  warnings: string[];
}

/**
 * Type checking context
 */
export interface TypeContext {
  variables: Map<string, PLIXType>;
  functions: Map<string, { params: PLIXType[]; returns: PLIXType }>;
  quantumContext?: QuantumContext;
}

/**
 * PLIX Type Checker
 * 
 * Implements type checking for geometric and quantum types
 */
export class PLIXTypeChecker {
  private context: TypeContext;
  
  constructor(context: TypeContext = { variables: new Map(), functions: new Map() }) {
    this.context = context;
  }
  
  /**
   * Infer type of quaternion literal
   */
  inferQQuatLiteral(literal: QQuatLiteral): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Validate quaternion components are numbers
    if (typeof literal.w !== 'number' || typeof literal.x !== 'number' ||
        typeof literal.y !== 'number' || typeof literal.z !== 'number') {
      errors.push('Quaternion components must be numbers');
    }
    
    // Check if quaternion is normalized (warning, not error)
    const norm = Math.sqrt(literal.w * literal.w + literal.x * literal.x + 
                          literal.y * literal.y + literal.z * literal.z);
    if (Math.abs(norm - 1.0) > 0.01) {
      warnings.push(`Quaternion may not be normalized (norm=${norm.toFixed(3)})`);
    }
    
    return {
      type: 'QQuat',
      errors,
      warnings
    };
  }
  
  /**
   * Infer type of dual quaternion literal
   */
  inferDualQuatLiteral(literal: DualQuatLiteral): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check rotation quaternion
    const rotResult = this.inferQQuatLiteral(literal.rotation);
    errors.push(...rotResult.errors);
    warnings.push(...rotResult.warnings);
    
    // Check translation vector
    if (literal.translation.type !== 'vec3') {
      errors.push('Dual quaternion translation must be Vec3');
    }
    
    // Validate screw motion parameters if present
    if (literal.screwAxis && literal.angle !== undefined && literal.distance !== undefined) {
      if (literal.screwAxis.type !== 'vec3') {
        errors.push('Screw axis must be Vec3');
      }
      if (typeof literal.angle !== 'number') {
        errors.push('Screw angle must be number');
      }
      if (typeof literal.distance !== 'number') {
        errors.push('Screw distance must be number');
      }
    }
    
    return {
      type: 'DualQuat',
      errors,
      warnings
    };
  }
  
  /**
   * Infer type of Vec3 literal
   */
  inferVec3Literal(literal: Vec3Literal): TypeInferenceResult {
    const errors: string[] = [];
    
    if (typeof literal.x !== 'number' || typeof literal.y !== 'number' || 
        typeof literal.z !== 'number') {
      errors.push('Vec3 components must be numbers');
    }
    
    return {
      type: 'Vec3',
      errors,
      warnings: []
    };
  }
  
  /**
   * Infer type of Vec4 literal
   */
  inferVec4Literal(literal: Vec4Literal): TypeInferenceResult {
    const errors: string[] = [];
    
    if (typeof literal.x !== 'number' || typeof literal.y !== 'number' || 
        typeof literal.z !== 'number' || typeof literal.tau !== 'number') {
      errors.push('Vec4 components must be numbers');
    }
    
    return {
      type: 'Vec4',
      errors,
      warnings: []
    };
  }
  
  /**
   * Infer type of QPose literal
   */
  inferQPoseLiteral(literal: QPoseLiteral): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check position
    if (literal.position.type === 'vec4') {
      const posResult = this.inferVec4Literal(literal.position);
      errors.push(...posResult.errors);
      warnings.push(...posResult.warnings);
    } else {
      errors.push('QPose position must be Vec4');
    }
    
    // Check orientation
    const oriResult = this.inferQQuatLiteral(literal.orientation);
    errors.push(...oriResult.errors);
    warnings.push(...oriResult.warnings);
    
    return {
      type: 'QPose',
      errors,
      warnings
    };
  }
  
  /**
   * Infer type of QAddr literal
   */
  inferQAddrLiteral(literal: QAddrLiteral): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Validate n (principal shell)
    if (literal.n !== undefined) {
      if (typeof literal.n !== 'number' || literal.n < 0 || literal.n > 255) {
        errors.push('QAddr n (principal shell) must be number in [0, 255]');
      }
    }
    
    // Validate l (orbital class)
    if (literal.l !== undefined) {
      const validClasses: OrbitalClass[] = ['memory', 'io', 'network', 'model', 'crypto', 'ui', 'governance'];
      if (!validClasses.includes(literal.l)) {
        errors.push(`Invalid orbital class: ${literal.l}. Must be one of: ${validClasses.join(', ')}`);
      }
    }
    
    // Validate m (magnetic channel)
    if (literal.m !== undefined) {
      if (typeof literal.m === 'number') {
        if (literal.m < 0 || literal.m > 65535) {
          errors.push('QAddr m (magnetic channel) must be number in [0, 65535]');
        }
      } else if (typeof literal.m === 'object' && literal.m.type === 's3bin') {
        // Valid S3Bin
      } else if (typeof literal.m === 'string') {
        // Direction literal - valid
      } else {
        errors.push('QAddr m must be number, S3Bin, Cone, or Direction literal');
      }
    }
    
    // Validate s (spin mode)
    if (literal.s !== undefined) {
      const validSpins: SpinMode[] = ['read', 'write', 'plan', 'act'];
      if (!validSpins.includes(literal.s)) {
        errors.push(`Invalid spin mode: ${literal.s}. Must be one of: ${validSpins.join(', ')}`);
      }
    }
    
    // Validate morton4d
    if (literal.morton4d !== undefined) {
      if (typeof literal.morton4d !== 'number' || literal.morton4d < 0) {
        errors.push('QAddr morton4d must be non-negative number');
      }
    }
    
    // Validate s3bin
    if (literal.s3bin !== undefined) {
      if (literal.s3bin.type !== 's3bin') {
        errors.push('QAddr s3bin must be S3Bin literal');
      } else if (literal.s3bin.value < 0 || literal.s3bin.value > 65535) {
        errors.push('S3Bin value must be in [0, 65535]');
      }
    }
    
    return {
      type: 'QAddr',
      errors,
      warnings
    };
  }
  
  /**
   * Check place operation types
   */
  checkPlaceOperation(operation: PlaceOperation): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check entity reference
    if (!operation.entity || (typeof operation.entity !== 'string')) {
      errors.push('Place operation entity must be string (tag or @identifier)');
    }
    
    // Check position
    if (operation.position.type === 'vec4') {
      const posResult = this.inferVec4Literal(operation.position);
      errors.push(...posResult.errors);
      warnings.push(...posResult.warnings);
    } else if (operation.position.type === 'pose') {
      const poseResult = this.inferQPoseLiteral(operation.position);
      errors.push(...poseResult.errors);
      warnings.push(...poseResult.warnings);
    } else {
      errors.push('Place operation position must be Vec4 or QPose');
    }
    
    // Check orientation if present
    if (operation.orientation) {
      if (operation.orientation.type === 'quat') {
        const oriResult = this.inferQQuatLiteral(operation.orientation);
        errors.push(...oriResult.errors);
        warnings.push(...oriResult.warnings);
      } else if (operation.orientation.type === 'angle_axis') {
        // Angle-axis is valid
      } else {
        errors.push('Place operation orientation must be QQuat or AngleAxis');
      }
    }
    
    // Check quantum context if present
    if (operation.quantumContext) {
      const qcResult = this.checkQuantumContext(operation.quantumContext);
      errors.push(...qcResult.errors);
      warnings.push(...qcResult.warnings);
    }
    
    // Check selection rules if present
    if (operation.selection) {
      const selResult = this.checkSelectionRules(operation.selection);
      errors.push(...selResult.errors);
      warnings.push(...selResult.warnings);
    }
    
    return {
      type: 'PlaceOp',
      errors,
      warnings
    };
  }
  
  /**
   * Check move operation types
   */
  checkMoveOperation(operation: MoveOperation): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check entity reference
    if (!operation.entity || (typeof operation.entity !== 'string')) {
      errors.push('Move operation entity must be string (tag or @identifier)');
    }
    
    // Check delta pose
    if (operation.deltaPose.type === 'dualquat') {
      const dqResult = this.inferDualQuatLiteral(operation.deltaPose);
      errors.push(...dqResult.errors);
      warnings.push(...dqResult.warnings);
    } else if (operation.deltaPose.type === 'screw_motion') {
      // Screw motion is valid
      if (operation.deltaPose.screwAxis.type !== 'vec3') {
        errors.push('Screw motion axis must be Vec3');
      }
      if (typeof operation.deltaPose.theta !== 'number') {
        errors.push('Screw motion theta must be number');
      }
      if (typeof operation.deltaPose.t !== 'number') {
        errors.push('Screw motion t must be number');
      }
    } else {
      errors.push('Move operation deltaPose must be DualQuat or ScrewMotion');
    }
    
    // Check quantum context if present
    if (operation.quantumContext) {
      const qcResult = this.checkQuantumContext(operation.quantumContext);
      errors.push(...qcResult.errors);
      warnings.push(...qcResult.warnings);
    }
    
    // Check selection rules if present
    if (operation.selection) {
      const selResult = this.checkSelectionRules(operation.selection);
      errors.push(...selResult.errors);
      warnings.push(...selResult.warnings);
    }
    
    return {
      type: 'MoveOp',
      errors,
      warnings
    };
  }
  
  /**
   * Check sense operation types
   */
  checkSenseOperation(operation: SenseOperation): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check region if present
    if (operation.region) {
      if (operation.region.type === 'radius') {
        if (typeof operation.region.radius !== 'number' || operation.region.radius < 0) {
          errors.push('Sense region radius must be non-negative number');
        }
      } else if (operation.region.type === 'cone') {
        if (!operation.region.cone) {
          errors.push('Sense region cone must have Cone literal');
        } else if (operation.region.cone.type !== 'cone') {
          errors.push('Sense region cone must be Cone literal');
        }
      } else if (operation.region.type === 'composite') {
        if (!operation.region.composite) {
          errors.push('Sense region composite must have CompositeKey literal');
        }
      }
    }
    
    // Check filters if present
    if (operation.filters) {
      for (const filter of operation.filters) {
        if (filter.kind !== undefined && typeof filter.kind !== 'string') {
          errors.push('Filter kind must be string');
        }
        if (filter.n !== undefined && (typeof filter.n !== 'number' || filter.n < 0)) {
          errors.push('Filter n must be non-negative number');
        }
        if (filter.l !== undefined) {
          const validClasses: OrbitalClass[] = ['memory', 'io', 'network', 'model', 'crypto', 'ui', 'governance'];
          if (!validClasses.includes(filter.l)) {
            errors.push(`Invalid filter orbital class: ${filter.l}`);
          }
        }
        if (filter.m !== undefined && (typeof filter.m !== 'number' || filter.m < 0)) {
          errors.push('Filter m must be non-negative number');
        }
        if (filter.s !== undefined) {
          const validSpins: SpinMode[] = ['read', 'write', 'plan', 'act'];
          if (!validSpins.includes(filter.s)) {
            errors.push(`Invalid filter spin mode: ${filter.s}`);
          }
        }
      }
    }
    
    // Check quantum context if present
    if (operation.quantumContext) {
      const qcResult = this.checkQuantumContext(operation.quantumContext);
      errors.push(...qcResult.errors);
      warnings.push(...qcResult.warnings);
    }
    
    return {
      type: 'SenseOp',
      errors,
      warnings
    };
  }
  
  /**
   * Check emit operation types
   */
  checkEmitOperation(operation: EmitOperation): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check event reference
    if (!operation.event || (typeof operation.event !== 'string')) {
      errors.push('Emit operation event must be string (tag or @identifier)');
    }
    
    // Check quantum context if present
    if (operation.quantumContext) {
      const qcResult = this.checkQuantumContext(operation.quantumContext);
      errors.push(...qcResult.errors);
      warnings.push(...qcResult.warnings);
    }
    
    // Check selection rules if present
    if (operation.selection) {
      const selResult = this.checkSelectionRules(operation.selection);
      errors.push(...selResult.errors);
      warnings.push(...selResult.warnings);
    }
    
    return {
      type: 'EmitOp',
      errors,
      warnings
    };
  }
  
  /**
   * Check quantum context
   */
  checkQuantumContext(context: QuantumContext): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Validate n (principal shell)
    if (context.n !== undefined) {
      if (typeof context.n !== 'number' || context.n < 0 || context.n > 255) {
        errors.push('Quantum context n (principal shell) must be number in [0, 255]');
      }
    }
    
    // Validate l (orbital class)
    if (context.l !== undefined) {
      const validClasses: OrbitalClass[] = ['memory', 'io', 'network', 'model', 'crypto', 'ui', 'governance'];
      if (!validClasses.includes(context.l)) {
        errors.push(`Invalid quantum context orbital class: ${context.l}`);
      }
    }
    
    // Validate m (magnetic channel)
    if (context.m !== undefined) {
      if (typeof context.m === 'number') {
        if (context.m < 0 || context.m > 65535) {
          errors.push('Quantum context m must be number in [0, 65535]');
        }
      } else if (typeof context.m === 'object' && context.m.type === 'cone') {
        // Cone literal - valid
      } else if (typeof context.m === 'string') {
        // Direction literal - valid
      } else {
        errors.push('Quantum context m must be number, Cone, or Direction literal');
      }
    }
    
    // Validate s (spin mode)
    if (context.s !== undefined) {
      const validSpins: SpinMode[] = ['read', 'write', 'plan', 'act'];
      if (!validSpins.includes(context.s)) {
        errors.push(`Invalid quantum context spin mode: ${context.s}`);
      }
    }
    
    // Validate morton4d
    if (context.morton4d !== undefined) {
      if (typeof context.morton4d !== 'number' || context.morton4d < 0) {
        errors.push('Quantum context morton4d must be non-negative number');
      }
    }
    
    // Validate s3bin
    if (context.s3bin !== undefined) {
      if (context.s3bin.type !== 's3bin') {
        errors.push('Quantum context s3bin must be S3Bin literal');
      } else if (context.s3bin.value < 0 || context.s3bin.value > 65535) {
        errors.push('Quantum context S3Bin value must be in [0, 65535]');
      }
    }
    
    return {
      type: 'QuantumContext',
      errors,
      warnings
    };
  }
  
  /**
   * Check selection rules
   */
  checkSelectionRules(rules: SelectionRules): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Validate deltaN
    if (rules.deltaN !== undefined) {
      if (typeof rules.deltaN !== 'number' || rules.deltaN < -1 || rules.deltaN > 1) {
        errors.push('Selection rule deltaN must be -1, 0, or 1 (hydrogen-like selection rules)');
      }
    }
    
    // Validate deltaL, deltaM, deltaS (booleans)
    if (rules.deltaL !== undefined && typeof rules.deltaL !== 'boolean') {
      errors.push('Selection rule deltaL must be boolean');
    }
    if (rules.deltaM !== undefined && typeof rules.deltaM !== 'boolean') {
      errors.push('Selection rule deltaM must be boolean');
    }
    if (rules.deltaS !== undefined && typeof rules.deltaS !== 'boolean') {
      errors.push('Selection rule deltaS must be boolean');
    }
    
    // Validate ok (boolean)
    if (rules.ok !== undefined && typeof rules.ok !== 'boolean') {
      errors.push('Selection rule ok must be boolean');
    }
    
    // Validate reason (string)
    if (rules.reason !== undefined && typeof rules.reason !== 'string') {
      errors.push('Selection rule reason must be string');
    }
    
    // Check consistency: if ok is false, reason should be provided
    if (rules.ok === false && !rules.reason) {
      warnings.push('Selection rule ok=false should have reason provided');
    }
    
    return {
      type: 'SelectionRules',
      errors,
      warnings
    };
  }
  
  /**
   * Check geometric operation (dispatch to specific checker)
   */
  checkGeometricOperation(operation: GeometricOperation): TypeInferenceResult {
    switch (operation.type) {
      case 'place_op':
        return this.checkPlaceOperation(operation);
      case 'move_op':
        return this.checkMoveOperation(operation);
      case 'sense_op':
        return this.checkSenseOperation(operation);
      case 'emit_op':
        return this.checkEmitOperation(operation);
      case 'quantum_context':
        return this.checkQuantumContextBlock(operation);
      default:
        return {
          type: null,
          errors: [`Unknown geometric operation type: ${(operation as any).type}`],
          warnings: []
        };
    }
  }
  
  /**
   * Check quantum context block
   */
  checkQuantumContextBlock(block: QuantumContextBlock): TypeInferenceResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check quantum context
    const qcResult = this.checkQuantumContext(block.context);
    errors.push(...qcResult.errors);
    warnings.push(...qcResult.warnings);
    
    // Check block operations
    if (block.block && Array.isArray(block.block)) {
      for (const op of block.block) {
        const opResult = this.checkGeometricOperation(op);
        errors.push(...opResult.errors);
        warnings.push(...opResult.warnings);
      }
    }
    
    return {
      type: 'QuantumContext',
      errors,
      warnings
    };
  }
  
  /**
   * Validate selection rules for a transition
   * 
   * Checks if a transition from old QAddr to new QAddr satisfies selection rules
   */
  validateSelectionRulesTransition(
    oldAddr: QAddrLiteral,
    newAddr: QAddrLiteral,
    rules: SelectionRules
  ): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check deltaN
    if (rules.deltaN !== undefined && oldAddr.n !== undefined && newAddr.n !== undefined) {
      const deltaN = newAddr.n - oldAddr.n;
      if (deltaN !== rules.deltaN) {
        errors.push(`Selection rule violation: deltaN expected ${rules.deltaN}, got ${deltaN}`);
      }
    }
    
    // Check deltaL
    if (rules.deltaL !== undefined && oldAddr.l !== undefined && newAddr.l !== undefined) {
      const deltaL = oldAddr.l !== newAddr.l;
      if (deltaL !== rules.deltaL) {
        errors.push(`Selection rule violation: deltaL expected ${rules.deltaL}, got ${deltaL}`);
      }
    }
    
    // Check deltaM
    if (rules.deltaM !== undefined && oldAddr.m !== undefined && newAddr.m !== undefined) {
      const deltaM = this.compareMagneticChannels(oldAddr.m, newAddr.m);
      if (deltaM !== rules.deltaM) {
        errors.push(`Selection rule violation: deltaM expected ${rules.deltaM}, got ${deltaM}`);
      }
    }
    
    // Check deltaS
    if (rules.deltaS !== undefined && oldAddr.s !== undefined && newAddr.s !== undefined) {
      const deltaS = oldAddr.s !== newAddr.s;
      if (deltaS !== rules.deltaS) {
        errors.push(`Selection rule violation: deltaS expected ${rules.deltaS}, got ${deltaS}`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * Compare magnetic channels (m values)
   */
  private compareMagneticChannels(oldM: number | any, newM: number | any): boolean {
    // Simplified: if both are numbers, check if they're different
    if (typeof oldM === 'number' && typeof newM === 'number') {
      return oldM !== newM;
    }
    
    // If both are S3Bin literals, compare values
    if (typeof oldM === 'object' && oldM.type === 's3bin' &&
        typeof newM === 'object' && newM.type === 's3bin') {
      return oldM.value !== newM.value;
    }
    
    // Otherwise, assume different
    return true;
  }
}

/**
 * Type inference helper functions
 */
export const TypeInference = {
  /**
   * Infer type of geometric operation
   */
  inferGeometricOperation(operation: GeometricOperation): TypeInferenceResult {
    const checker = new PLIXTypeChecker();
    return checker.checkGeometricOperation(operation);
  },
  
  /**
   * Infer type of quaternion literal
   */
  inferQuaternionLiteral(literal: QQuatLiteral | DualQuatLiteral | DoubleQuatLiteral | QPoseLiteral | QAddrLiteral): TypeInferenceResult {
    const checker = new PLIXTypeChecker();
    
    switch (literal.type) {
      case 'quat':
        return checker.inferQQuatLiteral(literal);
      case 'dualquat':
        return checker.inferDualQuatLiteral(literal);
      case 'doublequat':
        return { type: 'DoubleQuat', errors: [], warnings: [] }; // TODO: implement
      case 'pose':
        return checker.inferQPoseLiteral(literal);
      case 'qaddr':
        return checker.inferQAddrLiteral(literal);
      default:
        return { type: null, errors: [`Unknown literal type: ${(literal as any).type}`], warnings: [] };
    }
  },
  
  /**
   * Validate selection rules transition
   */
  validateTransition(
    oldAddr: QAddrLiteral,
    newAddr: QAddrLiteral,
    rules: SelectionRules
  ): { valid: boolean; errors: string[] } {
    const checker = new PLIXTypeChecker();
    return checker.validateSelectionRulesTransition(oldAddr, newAddr, rules);
  }
};

