/**
 * PLIX Quaternion Type Definitions
 * 
 * Type definitions for quaternion types, geometric operations, and quantum context
 * Phase 2, Week 5: Grammar Extensions
 */

/**
 * Orbital Class (capability class)
 */
export type OrbitalClass = 
  | 'memory'
  | 'io'
  | 'network'
  | 'model'
  | 'crypto'
  | 'ui'
  | 'governance';

/**
 * Spin Mode (chirality/authority mode)
 */
export type SpinMode = 
  | 'read'
  | 'write'
  | 'plan'
  | 'act';

/**
 * Direction Literal (for quantum context m parameter)
 */
export type DirectionLiteral = 
  | 'forward'
  | 'backward'
  | 'left'
  | 'right'
  | 'up'
  | 'down';

/**
 * Vec3 Literal (3D vector)
 */
export interface Vec3Literal {
  type: 'vec3';
  x: number;
  y: number;
  z: number;
}

/**
 * Vec4 Literal (4D vector with tau)
 */
export interface Vec4Literal {
  type: 'vec4';
  x: number;
  y: number;
  z: number;
  tau: number;
}

/**
 * QQuat Literal (quaternion)
 */
export interface QQuatLiteral {
  type: 'quat';
  w: number;
  x: number;
  y: number;
  z: number;
}

/**
 * Dual Quaternion Literal (3D rigid transformation)
 */
export interface DualQuatLiteral {
  type: 'dualquat';
  rotation: QQuatLiteral;
  translation: Vec3Literal;
  screwAxis?: Vec3Literal;
  angle?: number;
  distance?: number;
}

/**
 * Double Quaternion Literal (4D rotation)
 */
export interface DoubleQuatLiteral {
  type: 'doublequat';
  left: QQuatLiteral;
  right: QQuatLiteral;
}

/**
 * Angle-Axis Literal (for orientation specification)
 */
export interface AngleAxisLiteral {
  type: 'angle_axis';
  axis: Vec3Literal;
  angle: number;
  unit?: 'rad' | 'deg';
}

/**
 * Screw Motion Literal
 */
export interface ScrewMotionLiteral {
  type: 'screw_motion';
  screwAxis: Vec3Literal;
  theta: number;
  t: number;
}

/**
 * S3 Bin Literal
 */
export interface S3BinLiteral {
  type: 's3bin';
  value: number;
}

/**
 * Cone Literal (for sense queries)
 */
export interface ConeLiteral {
  type: 'cone';
  direction: Vec3Literal;
  angle: number;
}

/**
 * Composite Key Literal
 */
export interface CompositeKeyLiteral {
  type: 'composite';
  mortonKey: number;
  s3Bin: number;
}

/**
 * QPose Literal (position + orientation)
 */
export interface QPoseLiteral {
  type: 'pose';
  position: Vec4Literal;
  orientation: QQuatLiteral;
  time?: number | string;
}

/**
 * QAddr Literal (Quantum Kernel Address)
 */
export interface QAddrLiteral {
  type: 'qaddr';
  n?: number;
  l?: OrbitalClass;
  m?: number | S3BinLiteral | ConeLiteral | DirectionLiteral;
  s?: SpinMode;
  morton4d?: number;
  s3bin?: S3BinLiteral;
}

/**
 * Selection Rules
 */
export interface SelectionRules {
  deltaN?: number;
  deltaL?: boolean;
  deltaM?: boolean;
  deltaS?: boolean;
  ok?: boolean;
  reason?: string;
}

/**
 * Quantum Context Parameters
 */
export interface QuantumContext {
  n?: number;
  l?: OrbitalClass;
  m?: number | ConeLiteral | DirectionLiteral;
  s?: SpinMode;
  morton4d?: number;
  s3bin?: S3BinLiteral;
}

/**
 * Filter Expression (for sense queries)
 */
export interface FilterExpr {
  kind?: string;
  n?: number;
  l?: OrbitalClass;
  m?: number;
  s?: SpinMode;
}

/**
 * Region (for sense queries)
 */
export interface Region {
  type: 'radius' | 'cone' | 'composite';
  radius?: number;
  cone?: ConeLiteral;
  composite?: CompositeKeyLiteral;
}

/**
 * Place Operation
 */
export interface PlaceOperation {
  type: 'place_op';
  entity: string; // Tag or @identifier
  position: Vec4Literal | QPoseLiteral;
  orientation?: QQuatLiteral | AngleAxisLiteral;
  quantumContext?: QuantumContext;
  guards?: string[];
  witness?: string;
  selection?: SelectionRules;
}

/**
 * Move Operation
 */
export interface MoveOperation {
  type: 'move_op';
  entity: string; // Tag or @identifier
  deltaPose: DualQuatLiteral | ScrewMotionLiteral;
  quantumContext?: QuantumContext;
  guards?: string[];
  witness?: string;
  selection?: SelectionRules;
}

/**
 * Sense Operation
 */
export interface SenseOperation {
  type: 'sense_op';
  region?: Region;
  filters?: FilterExpr[];
  quantumContext?: QuantumContext;
  guards?: string[];
}

/**
 * Emit Operation
 */
export interface EmitOperation {
  type: 'emit_op';
  event: string; // Tag or @identifier
  effect?: any;
  quantumContext?: QuantumContext;
  guards?: string[];
  witness?: string;
  selection?: SelectionRules;
}

/**
 * Quantum Context Block
 */
export interface QuantumContextBlock {
  type: 'quantum_context';
  context: QuantumContext;
  block: GeometricOperation[];
}

/**
 * Geometric Operation (union type)
 */
export type GeometricOperation = 
  | PlaceOperation
  | MoveOperation
  | SenseOperation
  | EmitOperation
  | QuantumContextBlock;

/**
 * Hamiltonian Cost Constraint
 */
export interface HamiltonianCost {
  type: 'hamiltonian';
  operator: 'ΔH' | 'H';
  comparison: '<=' | '>=' | '<' | '>' | '==';
  value: number | string; // number or 'budget' or identifier
}

