/**
 * PLIX Quaternion Parser
 * 
 * Parses quaternion literals and geometric operations
 * Phase 2, Week 5: Grammar Extensions
 */

import type {
  QQuatLiteral,
  DualQuatLiteral,
  DoubleQuatLiteral,
  Vec3Literal,
  Vec4Literal,
  QPoseLiteral,
  QAddrLiteral,
  S3BinLiteral,
  AngleAxisLiteral,
  ScrewMotionLiteral,
  ConeLiteral,
  CompositeKeyLiteral,
  PlaceOperation,
  MoveOperation,
  SenseOperation,
  EmitOperation,
  QuantumContextBlock,
  QuantumContext,
  SelectionRules,
  Region,
  FilterExpr,
  OrbitalClass,
  SpinMode
} from '../models/quaternion-types';

export interface QuaternionParseResult {
  literal: QQuatLiteral | DualQuatLiteral | DoubleQuatLiteral | Vec3Literal | Vec4Literal | QPoseLiteral | QAddrLiteral | null;
  errors: string[];
}

export interface GeometricParseResult {
  operation: PlaceOperation | MoveOperation | SenseOperation | EmitOperation | QuantumContextBlock | null;
  errors: string[];
}

/**
 * Parse quaternion literal from string
 */
export function parseQQuatLiteral(text: string): QuaternionParseResult {
  const errors: string[] = [];
  
  // Match: quat(w, x, y, z) or quat(w: 1.0, x: 0.0, y: 0.0, z: 0.0)
  const namedMatch = text.match(/quat\s*\(\s*w:\s*([-\d.]+)\s*,\s*x:\s*([-\d.]+)\s*,\s*y:\s*([-\d.]+)\s*,\s*z:\s*([-\d.]+)\s*\)/);
  const positionalMatch = text.match(/quat\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
  
  if (namedMatch) {
    return {
      literal: {
        type: 'quat',
        w: parseFloat(namedMatch[1]),
        x: parseFloat(namedMatch[2]),
        y: parseFloat(namedMatch[3]),
        z: parseFloat(namedMatch[4])
      },
      errors
    };
  }
  
  if (positionalMatch) {
    return {
      literal: {
        type: 'quat',
        w: parseFloat(positionalMatch[1]),
        x: parseFloat(positionalMatch[2]),
        y: parseFloat(positionalMatch[3]),
        z: parseFloat(positionalMatch[4])
      },
      errors
    };
  }
  
  errors.push(`Invalid quaternion literal: ${text}`);
  return { literal: null, errors };
}

/**
 * Parse Vec3 literal
 */
export function parseVec3Literal(text: string): QuaternionParseResult {
  const errors: string[] = [];
  
  // Match: vec3(x, y, z) or (x, y, z)
  const vec3Match = text.match(/vec3\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
  const tupleMatch = text.match(/\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
  
  if (vec3Match || tupleMatch) {
    const match = vec3Match || tupleMatch!;
    return {
      literal: {
        type: 'vec3',
        x: parseFloat(match[1]),
        y: parseFloat(match[2]),
        z: parseFloat(match[3])
      },
      errors
    };
  }
  
  errors.push(`Invalid Vec3 literal: ${text}`);
  return { literal: null, errors };
}

/**
 * Parse Vec4 literal
 */
export function parseVec4Literal(text: string): QuaternionParseResult {
  const errors: string[] = [];
  
  // Match: vec4(x, y, z, tau) or (x, y, z, tau)
  const vec4Match = text.match(/vec4\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
  const tupleMatch = text.match(/\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
  
  if (vec4Match || tupleMatch) {
    const match = vec4Match || tupleMatch!;
    return {
      literal: {
        type: 'vec4',
        x: parseFloat(match[1]),
        y: parseFloat(match[2]),
        z: parseFloat(match[3]),
        tau: parseFloat(match[4])
      },
      errors
    };
  }
  
  errors.push(`Invalid Vec4 literal: ${text}`);
  return { literal: null, errors };
}

/**
 * Parse dual quaternion literal
 */
export function parseDualQuatLiteral(text: string): QuaternionParseResult {
  const errors: string[] = [];
  
  // Match: dq(quat(...), vec3(...)) or dq(quat(...), vec3(...), screw_axis: vec3(...), θ: ..., t: ...)
  const simpleMatch = text.match(/dq\s*\(\s*quat\s*\([^)]+\)\s*,\s*vec3\s*\([^)]+\)\s*\)/);
  const screwMatch = text.match(/dq\s*\(\s*screw_axis:\s*vec3\s*\([^)]+\)\s*,\s*θ:\s*([-\d.]+)\s*,\s*t:\s*([-\d.]+)\s*\)/);
  
  if (screwMatch) {
    // Parse screw motion
    const axisMatch = text.match(/screw_axis:\s*vec3\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
    if (axisMatch) {
      return {
        literal: {
          type: 'dualquat',
          rotation: { type: 'quat', w: 1, x: 0, y: 0, z: 0 }, // Will be computed from screw motion
          translation: {
            type: 'vec3',
            x: parseFloat(axisMatch[1]),
            y: parseFloat(axisMatch[2]),
            z: parseFloat(axisMatch[3])
          },
          screwAxis: {
            type: 'vec3',
            x: parseFloat(axisMatch[1]),
            y: parseFloat(axisMatch[2]),
            z: parseFloat(axisMatch[3])
          },
          angle: parseFloat(screwMatch[1]),
          distance: parseFloat(screwMatch[2])
        },
        errors
      };
    }
  }
  
  if (simpleMatch) {
    // Parse rotation and translation
    const rotMatch = text.match(/quat\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
    const transMatch = text.match(/vec3\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
    
    if (rotMatch && transMatch) {
      return {
        literal: {
          type: 'dualquat',
          rotation: {
            type: 'quat',
            w: parseFloat(rotMatch[1]),
            x: parseFloat(rotMatch[2]),
            y: parseFloat(rotMatch[3]),
            z: parseFloat(rotMatch[4])
          },
          translation: {
            type: 'vec3',
            x: parseFloat(transMatch[1]),
            y: parseFloat(transMatch[2]),
            z: parseFloat(transMatch[3])
          }
        },
        errors
      };
    }
  }
  
  errors.push(`Invalid dual quaternion literal: ${text}`);
  return { literal: null, errors };
}

/**
 * Parse QPose literal
 */
export function parseQPoseLiteral(text: string): QuaternionParseResult {
  const errors: string[] = [];
  
  // Match: pose(vec4(...), quat(...)) or pose(vec4(...), quat(...), time)
  const match = text.match(/pose\s*\(\s*vec4\s*\([^)]+\)\s*,\s*quat\s*\([^)]+\)(?:\s*,\s*([^)]+))?\s*\)/);
  
  if (match) {
    const vec4Result = parseVec4Literal(text.match(/vec4\s*\([^)]+\)/)![0]);
    const quatResult = parseQQuatLiteral(text.match(/quat\s*\([^)]+\)/)![0]);
    
    if (vec4Result.literal && quatResult.literal && vec4Result.literal.type === 'vec4' && quatResult.literal.type === 'quat') {
      return {
        literal: {
          type: 'pose',
          position: vec4Result.literal,
          orientation: quatResult.literal,
          time: match[1] ? (isNaN(parseFloat(match[1])) ? match[1] : parseFloat(match[1])) : undefined
        },
        errors: [...vec4Result.errors, ...quatResult.errors]
      };
    }
  }
  
  errors.push(`Invalid QPose literal: ${text}`);
  return { literal: null, errors };
}

/**
 * Parse QAddr literal
 */
export function parseQAddrLiteral(text: string): QuaternionParseResult {
  const errors: string[] = [];
  
  // Match: qaddr(n: 1, l: io, m: s3bin(1234), s: act, morton4d: 0x1234, s3bin: 0xABCD)
  const nMatch = text.match(/n:\s*(\d+)/);
  const lMatch = text.match(/l:\s*(\w+)/);
  const mMatch = text.match(/m:\s*(?:s3bin\s*\(\s*(\d+)\s*\)|(\d+)|cone\s*\([^)]+\)|(\w+))/);
  const sMatch = text.match(/s:\s*(\w+)/);
  const mortonMatch = text.match(/morton4d:\s*(0x[\da-fA-F]+|\d+)/);
  const s3binMatch = text.match(/s3bin:\s*(0x[\da-fA-F]+|\d+)/);
  
  const qaddr: QAddrLiteral = {
    type: 'qaddr'
  };
  
  if (nMatch) qaddr.n = parseInt(nMatch[1]);
  if (lMatch) qaddr.l = lMatch[1] as OrbitalClass;
  if (mMatch) {
    if (mMatch[1]) {
      qaddr.m = { type: 's3bin', value: parseInt(mMatch[1]) };
    } else if (mMatch[2]) {
      qaddr.m = parseInt(mMatch[2]);
    } else if (mMatch[3]) {
      qaddr.m = mMatch[3] as any;
    }
  }
  if (sMatch) qaddr.s = sMatch[1] as SpinMode;
  if (mortonMatch) qaddr.morton4d = mortonMatch[1].startsWith('0x') ? parseInt(mortonMatch[1], 16) : parseInt(mortonMatch[1]);
  if (s3binMatch) qaddr.s3bin = { type: 's3bin', value: s3binMatch[1].startsWith('0x') ? parseInt(s3binMatch[1], 16) : parseInt(s3binMatch[1]) };
  
  return {
    literal: qaddr,
    errors
  };
}

/**
 * Parse quantum context
 */
export function parseQuantumContext(text: string): { context: QuantumContext | null; errors: string[] } {
  const errors: string[] = [];
  const context: QuantumContext = {};
  
  // Match: with Q(n: 1, l: io, m: cone(N, 30°), s: act)
  const nMatch = text.match(/n:\s*(\d+)/);
  const lMatch = text.match(/l:\s*(\w+)/);
  const mMatch = text.match(/m:\s*(?:cone\s*\([^)]+\)|(\d+)|(\w+))/);
  const sMatch = text.match(/s:\s*(\w+)/);
  const mortonMatch = text.match(/morton4d:\s*(0x[\da-fA-F]+|\d+)/);
  const s3binMatch = text.match(/s3bin:\s*(0x[\da-fA-F]+|\d+)/);
  
  if (nMatch) context.n = parseInt(nMatch[1]);
  if (lMatch) context.l = lMatch[1] as OrbitalClass;
  if (mMatch) {
    if (mMatch[1]) {
      context.m = parseInt(mMatch[1]);
    } else if (mMatch[2]) {
      context.m = mMatch[2] as any;
    }
  }
  if (sMatch) context.s = sMatch[1] as SpinMode;
  if (mortonMatch) context.morton4d = mortonMatch[1].startsWith('0x') ? parseInt(mortonMatch[1], 16) : parseInt(mortonMatch[1]);
  if (s3binMatch) context.s3bin = { type: 's3bin', value: s3binMatch[1].startsWith('0x') ? parseInt(s3binMatch[1], 16) : parseInt(s3binMatch[1]) };
  
  return { context, errors };
}

/**
 * Parse selection rules
 */
export function parseSelectionRules(text: string): { rules: SelectionRules | null; errors: string[] } {
  const errors: string[] = [];
  const rules: SelectionRules = {};
  
  // Match: selection: {Δn: 0, Δl: false, Δm: true, Δs: false, ok: true}
  const deltaNMatch = text.match(/Δn:\s*([-\d]+)/);
  const deltaLMatch = text.match(/Δl:\s*(true|false)/);
  const deltaMMatch = text.match(/Δm:\s*(true|false)/);
  const deltaSMatch = text.match(/Δs:\s*(true|false)/);
  const okMatch = text.match(/ok:\s*(true|false)/);
  const reasonMatch = text.match(/reason:\s*"([^"]+)"/);
  
  if (deltaNMatch) rules.deltaN = parseInt(deltaNMatch[1]);
  if (deltaLMatch) rules.deltaL = deltaLMatch[1] === 'true';
  if (deltaMMatch) rules.deltaM = deltaMMatch[1] === 'true';
  if (deltaSMatch) rules.deltaS = deltaSMatch[1] === 'true';
  if (okMatch) rules.ok = okMatch[1] === 'true';
  if (reasonMatch) rules.reason = reasonMatch[1];
  
  return { rules, errors };
}

/**
 * Parse place operation
 */
export function parsePlaceOperation(text: string): GeometricParseResult {
  const errors: string[] = [];
  
  // Match: place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now) ori: ⟨+k, 15°⟩
  const entityMatch = text.match(/place\s+(@?\w+\.\w+|\w+)/);
  const atMatch = text.match(/at\s+(pose\s*\([^)]+\)|vec4\s*\([^)]+\)|\([^)]+\))/);
  const oriMatch = text.match(/ori:\s*(quat\s*\([^)]+\)|⟨[^⟩]+⟩)/);
  
  if (!entityMatch || !atMatch) {
    errors.push(`Invalid place operation: ${text}`);
    return { operation: null, errors };
  }
  
  const entity = entityMatch[1];
  let position: Vec4Literal | QPoseLiteral;
  
  if (atMatch[1].startsWith('pose')) {
    const poseResult = parseQPoseLiteral(atMatch[1]);
    if (!poseResult.literal || poseResult.literal.type !== 'pose') {
      errors.push(...poseResult.errors);
      return { operation: null, errors };
    }
    position = poseResult.literal;
  } else {
    const vec4Result = parseVec4Literal(atMatch[1]);
    if (!vec4Result.literal || vec4Result.literal.type !== 'vec4') {
      errors.push(...vec4Result.errors);
      return { operation: null, errors };
    }
    position = vec4Result.literal;
  }
  
  const operation: PlaceOperation = {
    type: 'place_op',
    entity,
    position
  };
  
  if (oriMatch) {
    if (oriMatch[1].startsWith('quat')) {
      const quatResult = parseQQuatLiteral(oriMatch[1]);
      if (quatResult.literal && quatResult.literal.type === 'quat') {
        operation.orientation = quatResult.literal;
      }
    } else {
      // Parse angle-axis: ⟨+k, 15°⟩
      const angleAxisMatch = oriMatch[1].match(/⟨\s*([+-]?[ijkxyz])\s*,\s*([-\d.]+)°?\s*(?:,\s*(rad|deg))?\s*⟩/);
      if (angleAxisMatch) {
        // Convert axis string to vec3
        const axisMap: Record<string, Vec3Literal> = {
          '+k': { type: 'vec3', x: 0, y: 0, z: 1 },
          '-k': { type: 'vec3', x: 0, y: 0, z: -1 },
          '+i': { type: 'vec3', x: 1, y: 0, z: 0 },
          '-i': { type: 'vec3', x: -1, y: 0, z: 0 },
          '+j': { type: 'vec3', x: 0, y: 1, z: 0 },
          '-j': { type: 'vec3', x: 0, y: -1, z: 0 }
        };
        
        const axis = axisMap[angleAxisMatch[1]] || { type: 'vec3', x: 0, y: 0, z: 1 };
        const angle = parseFloat(angleAxisMatch[2]);
        const unit = angleAxisMatch[3] || 'deg';
        
        operation.orientation = {
          type: 'angle_axis',
          axis,
          angle: unit === 'deg' ? (angle * Math.PI / 180) : angle,
          unit: unit as 'rad' | 'deg'
        };
      }
    }
  }
  
  // Parse quantum context if present
  const qcMatch = text.match(/with\s+Q\s*\([^)]+\)/);
  if (qcMatch) {
    const qcResult = parseQuantumContext(qcMatch[0]);
    if (qcResult.context) {
      operation.quantumContext = qcResult.context;
    }
    errors.push(...qcResult.errors);
  }
  
  // Parse selection rules if present
  const selMatch = text.match(/selection:\s*\{[^}]+\}/);
  if (selMatch) {
    const selResult = parseSelectionRules(selMatch[0]);
    if (selResult.rules) {
      operation.selection = selResult.rules;
    }
    errors.push(...selResult.errors);
  }
  
  return { operation, errors };
}

/**
 * Parse move operation
 */
export function parseMoveOperation(text: string): GeometricParseResult {
  const errors: string[] = [];
  
  // Match: move @svc.pg by dq(screw_axis: +k, θ: 5°, t: 2cm)
  const entityMatch = text.match(/move\s+(@?\w+\.\w+|\w+)/);
  const byMatch = text.match(/by\s+(dq\s*\([^)]+\))/);
  
  if (!entityMatch || !byMatch) {
    errors.push(`Invalid move operation: ${text}`);
    return { operation: null, errors };
  }
  
  const entity = entityMatch[1];
  const dqResult = parseDualQuatLiteral(byMatch[1]);
  
  if (!dqResult.literal || dqResult.literal.type !== 'dualquat') {
    errors.push(...dqResult.errors);
    return { operation: null, errors };
  }
  
  const operation: MoveOperation = {
    type: 'move_op',
    entity,
    deltaPose: dqResult.literal
  };
  
  // Parse quantum context and selection rules (similar to place)
  const qcMatch = text.match(/with\s+Q\s*\([^)]+\)/);
  if (qcMatch) {
    const qcResult = parseQuantumContext(qcMatch[0]);
    if (qcResult.context) {
      operation.quantumContext = qcResult.context;
    }
    errors.push(...qcResult.errors);
  }
  
  const selMatch = text.match(/selection:\s*\{[^}]+\}/);
  if (selMatch) {
    const selResult = parseSelectionRules(selMatch[0]);
    if (selResult.rules) {
      operation.selection = selResult.rules;
    }
    errors.push(...selResult.errors);
  }
  
  return { operation, errors };
}

/**
 * Parse sense operation
 */
export function parseSenseOperation(text: string): GeometricParseResult {
  const errors: string[] = [];
  
  // Match: sense radius: 5cm where kind: "dataset"
  const radiusMatch = text.match(/radius:\s*([-\d.]+)\s*(\w+)?/);
  const whereMatch = text.match(/where\s+(.+)/);
  
  const operation: SenseOperation = {
    type: 'sense_op'
  };
  
  if (radiusMatch) {
    operation.region = {
      type: 'radius',
      radius: parseFloat(radiusMatch[1])
    };
  }
  
  if (whereMatch) {
    const filters: FilterExpr[] = [];
    const kindMatch = whereMatch[1].match(/kind:\s*"([^"]+)"/);
    const nMatch = whereMatch[1].match(/n:\s*(\d+)/);
    const lMatch = whereMatch[1].match(/l:\s*(\w+)/);
    const mMatch = whereMatch[1].match(/m:\s*(\d+)/);
    const sMatch = whereMatch[1].match(/s:\s*(\w+)/);
    
    if (kindMatch) filters.push({ kind: kindMatch[1] });
    if (nMatch) filters.push({ n: parseInt(nMatch[1]) });
    if (lMatch) filters.push({ l: lMatch[1] as OrbitalClass });
    if (mMatch) filters.push({ m: parseInt(mMatch[1]) });
    if (sMatch) filters.push({ s: sMatch[1] as SpinMode });
    
    if (filters.length > 0) {
      operation.filters = filters;
    }
  }
  
  // Parse quantum context
  const qcMatch = text.match(/with\s+Q\s*\([^)]+\)/);
  if (qcMatch) {
    const qcResult = parseQuantumContext(qcMatch[0]);
    if (qcResult.context) {
      operation.quantumContext = qcResult.context;
    }
    errors.push(...qcResult.errors);
  }
  
  return { operation, errors };
}

/**
 * Parse emit operation
 */
export function parseEmitOperation(text: string): GeometricParseResult {
  const errors: string[] = [];
  
  // Match: emit @event.index_sync ΔH ≤ budget
  const eventMatch = text.match(/emit\s+(@?\w+\.\w+|\w+)/);
  
  if (!eventMatch) {
    errors.push(`Invalid emit operation: ${text}`);
    return { operation: null, errors };
  }
  
  const operation: EmitOperation = {
    type: 'emit_op',
    event: eventMatch[1]
  };
  
  // Parse quantum context and selection rules
  const qcMatch = text.match(/with\s+Q\s*\([^)]+\)/);
  if (qcMatch) {
    const qcResult = parseQuantumContext(qcMatch[0]);
    if (qcResult.context) {
      operation.quantumContext = qcResult.context;
    }
    errors.push(...qcResult.errors);
  }
  
  const selMatch = text.match(/selection:\s*\{[^}]+\}/);
  if (selMatch) {
    const selResult = parseSelectionRules(selMatch[0]);
    if (selResult.rules) {
      operation.selection = selResult.rules;
    }
    errors.push(...selResult.errors);
  }
  
  return { operation, errors };
}

