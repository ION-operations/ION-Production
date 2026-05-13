# Phase 2 Week 5: PLIX Grammar Extensions for Quaternion Types

**Status:** 🔄 **IN PROGRESS**  
**Date:** 2025-01-27  
**Phase:** Phase 2 - PLIX Integration  
**Week:** Week 5

---

## Overview

Extend PLIX grammar to support quaternion types, geometric operations, and quantum context syntax. This enables PLIX contracts to express geometric intent with quaternion-native operations.

---

## Grammar Extensions

### 1. Quaternion Type Literals

**New Grammar Rules:**
```
(* Quaternion Types *)
QuaternionType ::= "QQuat" | "DualQuat" | "DoubleQuat" | "QPose" | "QAddr"

(* Quaternion Literals *)
QQuatLiteral ::= "quat" "(" [w: Number] [x: Number] [y: Number] [z: Number] ")"
                | "quat" "(" Number "," Number "," Number "," Number ")"

DualQuatLiteral ::= "dq" "(" Rotation: QQuatLiteral "," Translation: Vec3Literal ")"
                   | "dq" "(" Rotation: QQuatLiteral "," Translation: Vec3Literal "," ScrewAxis: Vec3Literal "," Angle: Number "," Distance: Number ")"

DoubleQuatLiteral ::= "dq2" "(" Left: QQuatLiteral "," Right: QQuatLiteral ")"

Vec3Literal ::= "vec3" "(" x: Number "," y: Number "," z: Number ")"
               | "(" x: Number "," y: Number "," z: Number ")"

Vec4Literal ::= "vec4" "(" x: Number "," y: Number "," z: Number "," tau: Number ")"
               | "(" x: Number "," y: Number "," z: Number "," tau: Number ")"

QPoseLiteral ::= "pose" "(" Position: Vec4Literal "," Orientation: QQuatLiteral ")"
                | "pose" "(" Position: Vec4Literal "," Orientation: QQuatLiteral "," Time: Scalar ")"

QAddrLiteral ::= "qaddr" "(" 
                  [n: Number] 
                  [l: OrbitalClass] 
                  [m: Number | S3BinLiteral]
                  [s: SpinMode]
                  [morton4d: Number]
                  [s3bin: S3BinLiteral]
                ")"

S3BinLiteral ::= "s3bin" "(" Number ")"
                | Number

OrbitalClass ::= "memory" | "io" | "network" | "model" | "crypto" | "ui" | "governance"

SpinMode ::= "read" | "write" | "plan" | "act"
```

**Examples:**
```plix
(* Quaternion literals *)
quat(1.0, 0.0, 0.0, 0.0)  (* Identity quaternion *)
quat(w: 0.707, x: 0.707, y: 0.0, z: 0.0)  (* 90° rotation around x-axis *)

(* Dual quaternion (screw motion) *)
dq(quat(1,0,0,0), vec3(1,2,3))  (* Translation only *)
dq(quat(0.707,0.707,0,0), vec3(0,0,0), vec3(0,0,1), 0.785, 0.1)  (* Screw motion *)

(* Pose *)
pose(vec4(0.1, 0.2, 0.3, now), quat(1,0,0,0))  (* Position + orientation *)

(* QAddr *)
qaddr(n: 1, l: io, m: s3bin(1234), s: act, morton4d: 0x1234567890ABCDEF, s3bin: 0xABCD)
```

---

### 2. Geometric Operations

**New Grammar Rules:**
```
(* Geometric Syscalls *)
GeometricOp ::= PlaceOp | MoveOp | SenseOp | EmitOp

PlaceOp ::= "place" EntityRef "at" Position [Orientation] [QuantumContext] [Guards] [Witness] [Selection]
          | "place" EntityRef "at" QPoseLiteral [QuantumContext] [Guards] [Witness] [Selection]

MoveOp ::= "move" EntityRef DeltaPose [QuantumContext] [Guards] [Witness] [Selection]
         | "move" EntityRef "by" DualQuatLiteral [QuantumContext] [Guards] [Witness] [Selection]

SenseOp ::= "sense" [Region] [Filters] [QuantumContext] [Guards]
          | "sense" "radius:" Number [Filters] [QuantumContext] [Guards]

EmitOp ::= "emit" EventRef [Effect] [QuantumContext] [Guards] [Witness] [Selection]

(* Position and Orientation *)
Position ::= Vec4Literal | "(" x: Number "," y: Number "," z: Number "," tau: Scalar ")"
Orientation ::= "ori:" QQuatLiteral | "ori:" AngleAxisLiteral
AngleAxisLiteral ::= "⟨" Axis: Vec3Literal "," Angle: Number "⟩"
                    | "⟨" Axis: Vec3Literal "," Angle: Number "," Unit: ("rad" | "deg") "⟩"

DeltaPose ::= "Δpose:" DualQuatLiteral | "Δpose:" ScrewMotionLiteral
ScrewMotionLiteral ::= "dq" "(" "screw_axis:" Vec3Literal "," "θ:" Number "," "t:" Number ")"

(* Region and Filters *)
Region ::= "region:" CompositeKeyLiteral | "radius:" Number | "cone:" ConeLiteral
ConeLiteral ::= "cone" "(" Direction: Vec3Literal "," Angle: Number ")"

Filters ::= "where" FilterExpr+
FilterExpr ::= "kind:" String | "n:" Number | "l:" OrbitalClass | "m:" Number | "s:" SpinMode

CompositeKeyLiteral ::= "composite" "(" MortonKey: Number "," S3Bin: Number ")"

(* Entity Reference *)
EntityRef ::= Tag | "@" Identifier
EventRef ::= Tag | "@" Identifier
```

**Examples:**
```plix
(* Place entity *)
place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now) ori: ⟨+k, 15°⟩
  with Q(n: 1, l: io, m: cone(N, 30°), s: act)
  guards policy("db.provision")
  witness VIF.ping(host: "pg", n: 3, quorum: "3/3", t ≤ 500ms)
  selection: {Δn: 0, Δl: 0, Δm: 0, Δs: 0, ok: true}

(* Move entity *)
move @svc.pg by dq(screw_axis: +k, θ: 5°, t: 2cm)
  with Q(n: 1, l: io, m: forward, s: act)
  guards policy("db.move")
  selection: {Δn: 0, Δl: false, Δm: true, Δs: false, ok: true}

(* Sense entities *)
sense radius: 5cm where kind: "dataset" 
  with Q(n: 2, l: io, m: forward, s: read)
  guards policy("data.read")

(* Emit event *)
emit @event.index_sync ΔH ≤ budget
  with Q(n: 2, l: io, m: forward, s: write)
  guards policy("index.write")
  witness VIF.commit(hash: "...")
```

---

### 3. Quantum Context Syntax

**New Grammar Rules:**
```
(* Quantum Context *)
QuantumContext ::= "with" "Q" "(" QuantumParams ")" "do" Block
                 | "with" "Q" "(" QuantumParams ")" Statement

QuantumParams ::= QuantumParam ("," QuantumParam)*
QuantumParam ::= "n:" Number
                | "l:" OrbitalClass
                | "m:" (Number | ConeLiteral | "forward" | "backward" | "left" | "right" | "up" | "down")
                | "s:" SpinMode
                | "morton4d:" Number
                | "s3bin:" S3BinLiteral

Block ::= "{" Statement+ "}" | Statement
```

**Examples:**
```plix
(* Quantum context block *)
with Q(n: 1, l: io, m: cone(N, 30°), s: act) do {
  place @svc.pg at (x: 0.1, y: 0.0, z: 0.0, τ: now) ori: ⟨+k, 15°⟩
  move @svc.pg by dq(screw_axis: +k, θ: 5°, t: 2cm)
  emit @event.index_sync
}

(* Quantum context single statement *)
with Q(n: 2, l: io, m: forward, s: read) do
  sense radius: 5cm where kind: "dataset"
```

---

### 4. Selection Rules Syntax

**New Grammar Rules:**
```
(* Selection Rules *)
Selection ::= "selection:" SelectionRulesLiteral
SelectionRulesLiteral ::= "{" SelectionRule ("," SelectionRule)* "}"
SelectionRule ::= "Δn:" Number
                 | "Δl:" Boolean
                 | "Δm:" Boolean
                 | "Δs:" Boolean
                 | "ok:" Boolean
                 | "reason:" String
```

**Examples:**
```plix
selection: {Δn: 0, Δl: false, Δm: true, Δs: false, ok: true}
selection: {Δn: -1, Δl: true, Δm: false, Δs: false, ok: false, reason: "requires quorum"}
```

---

### 5. Hamiltonian Cost Syntax

**New Grammar Rules:**
```
(* Hamiltonian Cost *)
HamiltonianCost ::= "ΔH" ComparisonOp Number
                   | "ΔH" ComparisonOp BudgetLiteral
                   | "H" ComparisonOp Number
                   | "H" ComparisonOp BudgetLiteral

BudgetLiteral ::= "budget" | "budget(" Number ")" | Identifier
```

**Examples:**
```plix
ΔH ≤ budget
ΔH ≤ 100.5
H ≤ budget(db_operations)
```

---

## Updated EBNF Grammar

**Complete Extended Grammar:**
```
(* Extended PLIX Grammar with Quaternion Types *)

Specification ::= SpeechAct EntityClause ActionClause [WithClause] [PreClause] [PostClause] [TestsClause] [EvidenceClause] [TimeClause] [PlanClause] [GeometricOp]

(* ... existing grammar rules ... *)

(* New: Geometric Operations *)
GeometricOp ::= PlaceOp | MoveOp | SenseOp | EmitOp | QuantumContextBlock

(* New: Quaternion Types *)
Type ::= ExistingType | QuaternionType
QuaternionType ::= "QQuat" | "DualQuat" | "DoubleQuat" | "QPose" | "QAddr"

(* New: Quaternion Literals *)
Literal ::= ExistingLiteral | QQuatLiteral | DualQuatLiteral | DoubleQuatLiteral | QPoseLiteral | QAddrLiteral

(* New: Quantum Context *)
QuantumContextBlock ::= "with" "Q" "(" QuantumParams ")" "do" Block

(* ... rest of grammar ... *)
```

---

## Parser Implementation Requirements

### 1. Token Extensions

**New Tokens:**
- `QUAT`, `DUALQUAT`, `DOUBLEQUAT`, `POSE`, `QADDR` (type keywords)
- `PLACE`, `MOVE`, `SENSE`, `EMIT` (operation keywords)
- `WITH`, `DO` (quantum context keywords)
- `QUAT_LITERAL`, `DUALQUAT_LITERAL`, `POSE_LITERAL`, `QADDR_LITERAL` (literal tokens)
- `ANGLE_AXIS`, `SCREW_MOTION`, `CONE` (geometric construct tokens)
- `SELECTION`, `HAMILTONIAN` (constraint tokens)

### 2. AST Extensions

**New AST Nodes:**
```typescript
interface QQuatLiteral {
  type: 'quat_literal';
  w: number;
  x: number;
  y: number;
  z: number;
}

interface DualQuatLiteral {
  type: 'dualquat_literal';
  rotation: QQuatLiteral;
  translation: Vec3Literal;
  screwAxis?: Vec3Literal;
  angle?: number;
  distance?: number;
}

interface QPoseLiteral {
  type: 'pose_literal';
  position: Vec4Literal;
  orientation: QQuatLiteral;
  time?: Scalar;
}

interface QAddrLiteral {
  type: 'qaddr_literal';
  n?: number;
  l?: OrbitalClass;
  m?: number | S3BinLiteral;
  s?: SpinMode;
  morton4d?: number;
  s3bin?: S3BinLiteral;
}

interface PlaceOperation {
  type: 'place_op';
  entity: EntityRef;
  position: Vec4Literal | QPoseLiteral;
  orientation?: QQuatLiteral | AngleAxisLiteral;
  quantumContext?: QuantumContext;
  guards?: Guard[];
  witness?: WitnessRef;
  selection?: SelectionRules;
}

interface MoveOperation {
  type: 'move_op';
  entity: EntityRef;
  deltaPose: DualQuatLiteral | ScrewMotionLiteral;
  quantumContext?: QuantumContext;
  guards?: Guard[];
  witness?: WitnessRef;
  selection?: SelectionRules;
}

interface SenseOperation {
  type: 'sense_op';
  region?: Region;
  filters?: FilterExpr[];
  quantumContext?: QuantumContext;
  guards?: Guard[];
}

interface EmitOperation {
  type: 'emit_op';
  event: EventRef;
  effect?: EffectLiteral;
  quantumContext?: QuantumContext;
  guards?: Guard[];
  witness?: WitnessRef;
  selection?: SelectionRules;
}

interface QuantumContext {
  type: 'quantum_context';
  n?: number;
  l?: OrbitalClass;
  m?: number | ConeLiteral | DirectionLiteral;
  s?: SpinMode;
  morton4d?: number;
  s3bin?: S3BinLiteral;
  block: Block;
}
```

### 3. Parser Extensions

**New Parser Methods:**
- `parseQuaternionLiteral()` - Parse quaternion literals
- `parseDualQuaternionLiteral()` - Parse dual quaternion literals
- `parseQPoseLiteral()` - Parse pose literals
- `parseQAddrLiteral()` - Parse QAddr literals
- `parsePlaceOperation()` - Parse place operations
- `parseMoveOperation()` - Parse move operations
- `parseSenseOperation()` - Parse sense operations
- `parseEmitOperation()` - Parse emit operations
- `parseQuantumContext()` - Parse quantum context blocks
- `parseSelectionRules()` - Parse selection rules
- `parseHamiltonianCost()` - Parse Hamiltonian cost constraints

---

## Implementation Plan

### Step 1: Extend Grammar Specification ✅
- [x] Document new grammar rules
- [x] Provide examples
- [x] Update EBNF grammar

### Step 2: Extend Parser Tokens
- [ ] Add new token types
- [ ] Update tokenizer
- [ ] Add token tests

### Step 3: Extend AST Schema
- [ ] Add new AST node types
- [ ] Update TypeScript interfaces
- [ ] Add AST validation

### Step 4: Implement Parser Extensions
- [ ] Implement quaternion literal parsers
- [ ] Implement geometric operation parsers
- [ ] Implement quantum context parser
- [ ] Add parser tests

### Step 5: Update Canonical JSON Schema
- [ ] Extend JSON schema for quaternion types
- [ ] Add geometric operation JSON format
- [ ] Add quantum context JSON format
- [ ] Update round-trip conversion

### Step 6: Update S-Form Syntax
- [ ] Add S-form quaternion literals
- [ ] Add S-form geometric operations
- [ ] Add S-form quantum context
- [ ] Update S-form parser

### Step 7: Comprehensive Testing
- [ ] Unit tests for all new parsers
- [ ] Integration tests for grammar extensions
- [ ] Round-trip conversion tests
- [ ] Error handling tests

---

## Success Criteria

- ✅ Grammar specification complete
- ⚠️ Parser tokens extended (pending)
- ⚠️ AST schema extended (pending)
- ⚠️ Parser implementation complete (pending)
- ⚠️ Canonical JSON schema updated (pending)
- ⚠️ S-form syntax updated (pending)
- ⚠️ Comprehensive test suite (pending)

---

## Files to Create/Update

### New Files:
- `packages/plix/src/parser/quaternion-parser.ts` - Quaternion literal parsers
- `packages/plix/src/parser/geometric-parser.ts` - Geometric operation parsers
- `packages/plix/src/models/quaternion-types.ts` - Quaternion type definitions
- `packages/plix/src/__tests__/quaternion-grammar.test.ts` - Grammar tests

### Updated Files:
- `knowledge_architecture/systems/plix/GRAMMAR_SPECIFICATION_V2.md` - Add quaternion extensions
- `packages/plix/src/parser/sform-parser.ts` - Extend S-form parser
- `packages/plix/src/models/schema.ts` - Extend AST schema
- `packages/plix/src/compiler/aip-compiler.ts` - Extend compiler (Week 7)

---

**Status:** 🔄 **Grammar Specification Complete, Parser Implementation Pending**  
**Next:** Implement parser extensions and AST schema updates

