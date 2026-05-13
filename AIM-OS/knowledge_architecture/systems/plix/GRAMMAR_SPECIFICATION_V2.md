# PLIX Grammar Specification v2.0 - Phase 1 Enhanced
# Formal Grammar, Enhanced Constraints, Error Taxonomy, and Parser Specification

**Status:** ✅ **PHASE 1 IN PROGRESS**  
**Version:** 2.0.0 (Enhanced with External AI Feedback)  
**Date:** 2025-01-27  
**Purpose:** Formal grammar specification for Human-PLIX, Canonical JSON, and S-form with enhanced constraints, error taxonomy, and parser requirements  
**Based on:** External AI Feedback Synthesis (ChatGPT, Grok, Perplexity, Gemini)

---

## 📑 **TABLE OF CONTENTS**

1. [Grammar Overview](#grammar-overview)
2. [EBNF Grammar Specification](#ebnf-grammar-specification)
3. [Enhanced Constraint Language](#enhanced-constraint-language)
4. [Error Taxonomy](#error-taxonomy)
5. [Canonical JSON Schema](#canonical-json-schema)
6. [S-Form Syntax](#s-form-syntax)
7. [Round-Trip Conversion Rules](#round-trip-conversion-rules)
8. [Parser Requirements](#parser-requirements)

---

## 🎯 **GRAMMAR OVERVIEW**

### **Three Synchronized Representations**

PLIX supports three interchangeable representations:

1. **Human-PLIX** - Readable, indentation-based syntax for developers
2. **Canonical JSON** - Machine-executable, AIP-compilable format
3. **S-form** - Minimal, diff-friendly format for version control

**Key Principle:** All three forms are losslessly convertible (round-trip conversion preserves semantics).

### **Design Goals (External AI Feedback)**

- **Deterministic meaning:** Every important noun/verb is a **tagged identity**, not a loose string
- **Executable intent:** Every request compiles to an **AIP route** (tools, calls, pre/postconditions)
- **Provable claims:** Assertions carry **tests** and **witness/evidence hooks** (VIF), not rhetoric
- **Bitemporal truth:** All facts carry `tx_time` and `valid_time`
- **Evolvable grammar:** The language extends through **algorithmic proposals** (GGPs) with proofs and tests
- **Human-first surface, machine-first core:** Readable forms map 1:1 to canonical JSON

---

## 📐 **EBNF GRAMMAR SPECIFICATION**

### **Core Grammar (EBNF)**

```
(* PLIX Grammar v2.0 - Enhanced with External AI Feedback *)

(* Top-Level *)
Specification ::= SpeechAct EntityClause ActionClause [WithClause] [PreClause] [PostClause] [TestsClause] [EvidenceClause] [TimeClause] [PlanClause]

(* Speech Acts *)
SpeechAct ::= "ask" | "assert" | "plan" | "ensure" | "measure" | "decide" | "retract"

(* Entity Clause *)
EntityClause ::= "ent:" Tag

(* Action Clause *)
ActionClause ::= "act:" Identifier | "using" "cap:" Tag

(* With Clause (Parameters) *)
WithClause ::= "with:" WithField+
WithField ::= Key ":" (Scalar | TagRef)
TagRef ::= Tag | Key "." "ref" ":" Tag

(* Preconditions *)
PreClause ::= "pre:" Constraint+
Constraint ::= ConstraintExpr | LogicalConstraint | QuantifiedConstraint | TemporalConstraint
ConstraintExpr ::= Identifier ComparisonOp (Scalar | Identifier | Tag)
ComparisonOp ::= "==" | "!=" | "<=" | ">=" | "<" | ">"
LogicalConstraint ::= ConstraintExpr ("and" | "or" | "not") ConstraintExpr
QuantifiedConstraint ::= ("forall" | "exists") Identifier ":" ConstraintExpr
TemporalConstraint ::= ("eventually" | "always" | "within") "(" ConstraintExpr "," Duration ")"

(* Postconditions *)
PostClause ::= "post:" Constraint+

(* Tests *)
TestsClause ::= "tests:" TestSpec+
TestSpec ::= "tst:" Identifier [TestBound]
TestBound ::= ComparisonOp Scalar

(* Evidence *)
EvidenceClause ::= "evidence:" EvidenceRef+
EvidenceRef ::= "w:" Identifier | Tag

(* Time (Bitemporal) *)
TimeClause ::= "bt:" "tx_time:" Scalar ["valid_time:" Scalar]

(* Plan Block *)
PlanClause ::= "plan" "[" PlanStep+ "]"
PlanStep ::= "step" Identifier [RetrySpec] [FallbackSpec] [CompensationSpec]
RetrySpec ::= "retry" Integer "backoff" ("linear" | "exponential" | "fixed") "(" Duration "," Duration ")" ["jitter"]
FallbackSpec ::= "fallback" Identifier
CompensationSpec ::= "compensate" Identifier

(* Tags *)
Tag ::= "plix://" Namespace "/" Path ["#rev@" Hash]
Namespace ::= Identifier ("." Identifier)*
Path ::= Identifier ("/" Identifier)*
Hash ::= HexString

(* Primitives *)
Identifier ::= Letter (Letter | Digit | "_" | "." | "/")*
Scalar ::= String | Number | Boolean
String ::= '"' StringChar* '"'
Number ::= Integer | Float
Boolean ::= "true" | "false"
Duration ::= Integer ("ms" | "s" | "m" | "h" | "d")
HexString ::= ("0".."9" | "a".."f" | "A".."F")+
Key ::= Identifier

(* Error Handling *)
ErrorClause ::= "on_error:" ErrorType "->" ErrorAction
ErrorType ::= "net.timeout" | "policy.denied" | "constraint.violated" | "contract.precondition_failed" | "contract.postcondition_failed" | "proof.missing" | "auth.insufficient" | "resource.exceeded"
ErrorAction ::= "retry" | "compensate" | "fail" | "escalate" | "fallback" Identifier

(* ============================================ *)
(* QUATERNION EXTENSIONS (Phase 2, Week 5) *)
(* ============================================ *)

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

(* Geometric Operations *)
GeometricOp ::= PlaceOp | MoveOp | SenseOp | EmitOp | QuantumContextBlock

PlaceOp ::= "place" EntityRef "at" Position [Orientation] [QuantumContext] [Guards] [Witness] [Selection]
          | "place" EntityRef "at" QPoseLiteral [QuantumContext] [Guards] [Witness] [Selection]

MoveOp ::= "move" EntityRef DeltaPose [QuantumContext] [Guards] [Witness] [Selection]
         | "move" EntityRef "by" DualQuatLiteral [QuantumContext] [Guards] [Witness] [Selection]

SenseOp ::= "sense" [Region] [Filters] [QuantumContext] [Guards]
          | "sense" "radius:" Number [Filters] [QuantumContext] [Guards]

EmitOp ::= "emit" EventRef [Effect] [QuantumContext] [Guards] [Witness] [Selection]

Position ::= Vec4Literal | "(" x: Number "," y: Number "," z: Number "," tau: Scalar ")"
Orientation ::= "ori:" QQuatLiteral | "ori:" AngleAxisLiteral
AngleAxisLiteral ::= "⟨" Axis: Vec3Literal "," Angle: Number "⟩"
                    | "⟨" Axis: Vec3Literal "," Angle: Number "," Unit: ("rad" | "deg") "⟩"

DeltaPose ::= "Δpose:" DualQuatLiteral | "Δpose:" ScrewMotionLiteral
ScrewMotionLiteral ::= "dq" "(" "screw_axis:" Vec3Literal "," "θ:" Number "," "t:" Number ")"

Region ::= "region:" CompositeKeyLiteral | "radius:" Number | "cone:" ConeLiteral
ConeLiteral ::= "cone" "(" Direction: Vec3Literal "," Angle: Number ")"

Filters ::= "where" FilterExpr+
FilterExpr ::= "kind:" String | "n:" Number | "l:" OrbitalClass | "m:" Number | "s:" SpinMode

CompositeKeyLiteral ::= "composite" "(" MortonKey: Number "," S3Bin: Number ")"

EntityRef ::= Tag | "@" Identifier
EventRef ::= Tag | "@" Identifier

(* Quantum Context *)
QuantumContextBlock ::= "with" "Q" "(" QuantumParams ")" "do" Block
                       | "with" "Q" "(" QuantumParams ")" Statement

QuantumParams ::= QuantumParam ("," QuantumParam)*
QuantumParam ::= "n:" Number
                | "l:" OrbitalClass
                | "m:" (Number | ConeLiteral | "forward" | "backward" | "left" | "right" | "up" | "down")
                | "s:" SpinMode
                | "morton4d:" Number
                | "s3bin:" S3BinLiteral

Block ::= "{" Statement+ "}" | Statement

(* Selection Rules *)
Selection ::= "selection:" SelectionRulesLiteral
SelectionRulesLiteral ::= "{" SelectionRule ("," SelectionRule)* "}"
SelectionRule ::= "Δn:" Number
                 | "Δl:" Boolean
                 | "Δm:" Boolean
                 | "Δs:" Boolean
                 | "ok:" Boolean
                 | "reason:" String

(* Hamiltonian Cost *)
HamiltonianCost ::= "ΔH" ComparisonOp Number
                   | "ΔH" ComparisonOp BudgetLiteral
                   | "H" ComparisonOp Number
                   | "H" ComparisonOp BudgetLiteral

BudgetLiteral ::= "budget" | "budget(" Number ")" | Identifier
```

### **Grammar Enhancements (External AI Feedback)**

**1. Logical Operators (Grok/Perplexity):**
- Added `and`, `or`, `not` to `LogicalConstraint`
- Enables composition: `con:schema_intact AND rowcount_stable`

**2. Quantifiers (Perplexity):**
- Added `forall` and `exists` to `QuantifiedConstraint`
- Enables: `con:forall_rows unique_email`

**3. Temporal Operators (Perplexity):**
- Added `eventually`, `always`, `within` to `TemporalConstraint`
- Enables: `con:eventually_true(condition, within_ms)`

**4. Error Taxonomy (Grok/Gemini):**
- Added `ErrorClause` with typed `ErrorType`
- Enables declarative error handling: `on_error: net.timeout -> retry`

**5. Optional Delimiters (Grok):**
- Human-PLIX supports optional `{}` blocks for deep nesting
- Parser handles both indentation-based and delimiter-based syntax

---

## 🔧 **ENHANCED CONSTRAINT LANGUAGE**

### **Constraint Types**

**1. Simple Constraints:**
```
con:schema_intact == h_prev
con:rowcount_stable <= 0
con:user_authenticated == true
```

**2. Logical Constraints (NEW):**
```
con:schema_intact AND rowcount_stable
con:(user_authenticated == true) OR (admin_override == true)
con:NOT (calendar_conflicts > 0)
```

**3. Quantified Constraints (NEW):**
```
con:forall_rows unique_email
con:exists_room (capacity >= 10 AND available == true)
con:forall_users (age >= 18)
```

**4. Temporal Constraints (NEW):**
```
con:eventually_true(room_reserved, within_ms=5000)
con:always(user_authenticated == true)
con:within(duration <= 4h, timeout=300s)
```

### **Constraint Grammar (Extended)**

```
Constraint ::= SimpleConstraint | LogicalConstraint | QuantifiedConstraint | TemporalConstraint

SimpleConstraint ::= Identifier ComparisonOp (Scalar | Identifier | Tag)

LogicalConstraint ::= "(" Constraint ")" ("and" | "or" | "not") "(" Constraint ")"
                     | Constraint ("and" | "or" | "not") Constraint

QuantifiedConstraint ::= ("forall" | "exists") Identifier ":" ConstraintExpr
                        | ("forall" | "exists") Identifier "in" Identifier ":" ConstraintExpr

TemporalConstraint ::= ("eventually" | "always") "(" ConstraintExpr ")"
                      | "within" "(" ConstraintExpr "," Duration ")"
                      | "after" "(" Duration "," ConstraintExpr ")"
                      | "before" "(" Duration "," ConstraintExpr ")"
```

### **Constraint Examples**

**Example 1: Simple Constraints**
```plix
pre:
  con:user_authenticated == true
  con:room_available == true
  con:duration <= 4h
```

**Example 2: Logical Constraints**
```plix
pre:
  con:(user_authenticated == true) AND (room_available == true)
  con:(duration <= 4h) OR (admin_override == true)
  con:NOT (calendar_conflicts > 0)
```

**Example 3: Quantified Constraints**
```plix
pre:
  con:forall_rows unique_email
  con:exists_room (capacity >= 10 AND available == true)
  con:forall_users in active_users (age >= 18)
```

**Example 4: Temporal Constraints**
```plix
pre:
  con:eventually_true(room_reserved, within_ms=5000)
  con:always(user_authenticated == true)
  con:within(duration <= 4h, timeout=300s)
```

---

## 🚨 **ERROR TAXONOMY**

### **Error Types**

**Network Errors:**
- `net.timeout` - Network request timed out
- `net.unreachable` - Network endpoint unreachable
- `net.connection_failed` - Connection failed

**Policy Errors:**
- `policy.denied` - Policy check denied access
- `policy.insufficient_authority` - Insufficient authority tier
- `policy.quorum_not_met` - Quorum requirement not met

**Constraint Errors:**
- `constraint.violated` - Constraint check failed
- `constraint.precondition_failed` - Precondition not satisfied
- `constraint.postcondition_failed` - Postcondition not satisfied
- `constraint.invariant_broken` - Invariant violated during execution

**Contract Errors:**
- `contract.precondition_failed` - Contract precondition failed
- `contract.postcondition_failed` - Contract postcondition failed
- `contract.compensation_failed` - Compensation action failed

**Proof Errors:**
- `proof.missing` - Required proof/witness missing
- `proof.invalid` - Proof/witness validation failed
- `proof.insufficient` - Proof quality below threshold

**Authentication Errors:**
- `auth.insufficient` - Insufficient authentication
- `auth.expired` - Authentication token expired
- `auth.invalid` - Invalid authentication token

**Resource Errors:**
- `resource.exceeded` - Resource limit exceeded
- `resource.unavailable` - Resource not available
- `resource.throttled` - Resource access throttled

**Execution Errors:**
- `execution.failed` - Step execution failed
- `execution.timeout` - Step execution timed out
- `execution.cancelled` - Step execution cancelled

### **Error Action Types**

- `retry` - Retry the step with backoff
- `compensate` - Execute compensation action
- `fail` - Fail immediately (no retry/compensation)
- `escalate` - Escalate to human operator
- `fallback` - Use fallback step/strategy

### **Error Handling Grammar**

```
ErrorClause ::= "on_error:" ErrorType "->" ErrorAction
               | "on_error:" ErrorType "->" ErrorAction "with" ErrorConfig

ErrorConfig ::= "retry" "(" Integer "," Duration "," Duration ")"
               | "compensate" "(" Identifier ")"
               | "escalate" "(" EscalationTarget ")"
               | "fallback" "(" Identifier ")"

EscalationTarget ::= "admin" | "operator" | Identifier
```

### **Error Handling Examples**

**Example 1: Network Timeout**
```plix
plan [
  step connect
    retry 3 backoff exponential(100ms, 2s) jitter
    on_error: net.timeout -> retry with retry(3, 100ms, 2s)
    on_error: net.unreachable -> fallback use_replica
]
```

**Example 2: Policy Denied**
```plix
plan [
  step reserve_room
    on_error: policy.denied -> escalate(admin)
    on_error: policy.insufficient_authority -> fail
]
```

**Example 3: Constraint Violated**
```plix
plan [
  step migrate_schema
    on_error: constraint.violated -> compensate rollback_migration
    on_error: constraint.precondition_failed -> fail
]
```

**Example 4: Proof Missing**
```plix
plan [
  step create_witness
    on_error: proof.missing -> retry with retry(2, 500ms, 1s)
    on_error: proof.invalid -> fail
]
```

---

## 📋 **CANONICAL JSON SCHEMA**

### **JSON Schema Definition**

```json
{
  "$schema": "http://json-schema.org/draft/2020-12/schema",
  "$id": "https://aimos.dev/schema/plix.canonical.schema.json",
  "title": "PLIX Canonical JSON Schema",
  "type": "object",
  "required": ["speech", "entity", "action"],
  "properties": {
    "speech": {
      "type": "string",
      "enum": ["ask", "assert", "plan", "ensure", "measure", "decide", "retract"]
    },
    "entity": {
      "type": "string",
      "pattern": "^plix://[a-z0-9._-]+(/[a-z0-9._-]+)*(#rev@[a-f0-9]+)?$"
    },
    "action": {
      "oneOf": [
        {"type": "string"},
        {"type": "object", "properties": {"capability": {"type": "string"}}}
      ]
    },
    "with": {
      "type": "object",
      "additionalProperties": {
        "oneOf": [
          {"type": "string"},
          {"type": "number"},
          {"type": "boolean"},
          {"type": "object", "properties": {"ref": {"type": "string"}}}
        ]
      }
    },
    "pre": {
      "type": "array",
      "items": {"$ref": "#/$defs/Constraint"}
    },
    "post": {
      "type": "array",
      "items": {"$ref": "#/$defs/Constraint"}
    },
    "tests": {
      "type": "array",
      "items": {"$ref": "#/$defs/TestSpec"}
    },
    "evidence": {
      "type": "array",
      "items": {"type": "string"}
    },
    "bt": {
      "type": "object",
      "properties": {
        "tx_time": {"type": "string", "format": "date-time"},
        "valid_time": {"type": "string", "format": "date-time"}
      },
      "required": ["tx_time"]
    },
    "plan": {
      "type": "array",
      "items": {"$ref": "#/$defs/PlanStep"}
    },
    "errors": {
      "type": "array",
      "items": {"$ref": "#/$defs/ErrorClause"}
    }
  },
  "$defs": {
    "Constraint": {
      "oneOf": [
        {"$ref": "#/$defs/SimpleConstraint"},
        {"$ref": "#/$defs/LogicalConstraint"},
        {"$ref": "#/$defs/QuantifiedConstraint"},
        {"$ref": "#/$defs/TemporalConstraint"}
      ]
    },
    "SimpleConstraint": {
      "type": "object",
      "properties": {
        "expr": {"type": "string"},
        "op": {"type": "string", "enum": ["==", "!=", "<=", ">=", "<", ">"]},
        "value": {"oneOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}]}
      },
      "required": ["expr", "op", "value"]
    },
    "LogicalConstraint": {
      "type": "object",
      "properties": {
        "type": {"type": "string", "enum": ["and", "or", "not"]},
        "left": {"$ref": "#/$defs/Constraint"},
        "right": {"$ref": "#/$defs/Constraint"}
      },
      "required": ["type", "left"]
    },
    "QuantifiedConstraint": {
      "type": "object",
      "properties": {
        "quantifier": {"type": "string", "enum": ["forall", "exists"]},
        "variable": {"type": "string"},
        "domain": {"type": "string"},
        "constraint": {"$ref": "#/$defs/Constraint"}
      },
      "required": ["quantifier", "variable", "constraint"]
    },
    "TemporalConstraint": {
      "type": "object",
      "properties": {
        "type": {"type": "string", "enum": ["eventually", "always", "within", "after", "before"]},
        "constraint": {"$ref": "#/$defs/Constraint"},
        "duration": {"type": "string"}
      },
      "required": ["type", "constraint"]
    },
    "TestSpec": {
      "type": "object",
      "properties": {
        "test": {"type": "string"},
        "op": {"type": "string", "enum": ["==", "!=", "<=", ">=", "<", ">"]},
        "value": {"oneOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}]}
      },
      "required": ["test"]
    },
    "PlanStep": {
      "type": "object",
      "properties": {
        "step": {"type": "string"},
        "retry": {"$ref": "#/$defs/RetrySpec"},
        "fallback": {"type": "string"},
        "compensate": {"type": "string"},
        "timeout": {"type": "string"}
      },
      "required": ["step"]
    },
    "RetrySpec": {
      "type": "object",
      "properties": {
        "max": {"type": "integer"},
        "backoff": {"type": "string", "enum": ["linear", "exponential", "fixed"]},
        "min_delay": {"type": "string"},
        "max_delay": {"type": "string"},
        "jitter": {"type": "boolean"}
      },
      "required": ["max", "backoff", "min_delay", "max_delay"]
    },
    "ErrorClause": {
      "type": "object",
      "properties": {
        "error": {"type": "string"},
        "action": {"type": "string", "enum": ["retry", "compensate", "fail", "escalate", "fallback"]},
        "config": {"type": "object"}
      },
      "required": ["error", "action"]
    }
  }
}
```

---

## 🔤 **S-FORM SYNTAX**

### **S-Form Grammar**

```
SForm ::= "(" SpeechAct Entity Action [With] [Pre] [Post] [Tests] [Evidence] [Time] [Plan] ")"

Entity ::= "(" "ent" Tag ")"
Action ::= "(" ("act" Identifier | "use" Tag) ")"
With ::= "(" "with" WithField+ ")"
WithField ::= "(" Key Scalar ")" | "(" Key "." "ref" Tag ")"
Pre ::= "(" "pre" Constraint+ ")"
Post ::= "(" "post" Constraint+ ")"
Tests ::= "(" "tests" TestSpec+ ")"
Evidence ::= "(" "evidence" EvidenceRef+ ")"
Time ::= "(" "bt" TimeField+ ")"
Plan ::= "(" "plan" PlanStep+ ")"
```

### **S-Form Examples**

**Example 1: Basic Intent**
```
(ensure
  (ent plix://db/table/aimos.public.users#rev@h_98fa)
  (use plix://tool/mcp/pg.migrate#rev@h_2a10)
  (with (version "2025_11_11_01") (script.ref plix://blob/sql/ddl/users_v3#rev@h_abcd))
  (pre (= schema_intact h_prev))
  (post (= schema_fingerprint h_next))
  (tests unique_email (rowcount_stable <= 0))
  (evidence schema_before schema_after)
  (bt now))
```

**Example 2: With Logical Constraints**
```
(ensure
  (ent plix://db/schema/aimos.public)
  (act migrate)
  (pre (and (= schema_intact h_prev) (<= rowcount_stable 0)))
  (post (= schema_fingerprint h_next))
  (tests unique_email))
```

**Example 3: With Quantified Constraints**
```
(ensure
  (ent plix://db/table/users)
  (act migrate)
  (pre (forall row in users (unique_email row)))
  (post (= schema_fingerprint h_next)))
```

---

## 🔄 **ROUND-TRIP CONVERSION RULES**

### **Conversion Rules**

**1. Human-PLIX → Canonical JSON:**
- Parse indentation-based structure
- Resolve tags via registry
- Normalize constraint expressions
- Convert plan blocks to arrays

**2. Canonical JSON → Human-PLIX:**
- Generate indentation-based structure
- Format tags with proper spacing
- Expand constraint expressions
- Format plan blocks with proper indentation

**3. Human-PLIX ↔ S-form:**
- Convert indentation to parentheses
- Preserve tag references
- Maintain constraint semantics
- Preserve plan structure

**4. Canonical JSON ↔ S-form:**
- Convert JSON objects to S-expressions
- Preserve all fields
- Maintain type information
- Preserve bitemporal fields

### **Round-Trip Invariants**

**Invariant 1: Semantic Preservation**
- All three forms must have identical semantics
- Constraints must evaluate to same values
- Plan steps must execute in same order
- Evidence requirements must be identical

**Invariant 2: Tag Resolution**
- Tags must resolve to same entities across forms
- Tag references must be preserved
- Revision hashes must be maintained

**Invariant 3: Bitemporal Fields**
- `tx_time` and `valid_time` must be preserved
- Time values must be identical across forms

**Invariant 4: Error Handling**
- Error types must map correctly
- Error actions must be preserved
- Error configurations must be identical

---

## 🔨 **PARSER REQUIREMENTS**

### **Parser Architecture**

**1. Lexical Analysis:**
- Tokenize Human-PLIX input
- Handle indentation-based structure
- Support optional delimiters (`{}` blocks)
- Recognize tags, identifiers, operators

**2. Syntax Analysis:**
- Parse tokens into AST
- Handle indentation hierarchy
- Support both indentation and delimiter syntax
- Validate grammar rules

**3. Semantic Analysis:**
- Resolve tags via registry
- Validate constraint expressions
- Check type compatibility
- Verify plan dependencies

**4. Code Generation:**
- Generate Canonical JSON
- Generate S-form
- Preserve all semantic information
- Maintain round-trip capability

### **Parser Edge Cases**

**1. Dangling References:**
- Detect unresolved tags
- Report missing tag definitions
- Provide suggestions for similar tags

**2. Malformed URNs:**
- Validate tag URN format
- Check namespace/path syntax
- Verify revision hash format

**3. Circular Dependencies:**
- Detect circular plan dependencies
- Report dependency cycles
- Suggest dependency fixes

**4. Indentation Ambiguity:**
- Handle mixed indentation (tabs/spaces)
- Support optional delimiters for clarity
- Provide clear error messages

**5. Constraint Parsing:**
- Handle nested logical operators
- Parse quantified constraints correctly
- Validate temporal constraint syntax

### **Parser Implementation Requirements**

**1. Error Reporting:**
- Clear error messages with line numbers
- Suggestions for fixing errors
- Context-aware error recovery

**2. Performance:**
- Fast parsing (<100ms for typical contracts)
- Incremental parsing support
- Caching of parsed results

**3. Extensibility:**
- Support for grammar evolution (GGPs)
- Plugin system for custom constraints
- Extensible error taxonomy

**4. Testing:**
- Unit tests for each grammar rule
- Round-trip conversion tests
- Edge case tests (dangling refs, malformed URNs)
- Performance benchmarks

---

## 📝 **EXAMPLES**

### **Example 1: Human-PLIX (Enhanced)**

```
ensure ent:plix://db/table/aimos.public.users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  with:
    version: "2025_11_11_01"
    script.ref: plix://blob/sql/ddl/users_v3#rev@h_abcd
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
    con:forall_rows unique_email
    con:eventually_true(room_reserved, within_ms=5000)
  post:
    con:schema_fingerprint == h_next
  tests:
    tst:unique_email passes
    tst:rowcount_stable <= 0
  evidence:
    w:pg.schema_fingerprint_before
    w:pg.schema_fingerprint_after
  bt:
    tx_time: now()
  plan [
    step validate_preconditions
      on_error: constraint.violated -> fail
    step reserve_room
      retry 3 backoff exponential(100ms, 2s) jitter
      on_error: net.timeout -> retry with retry(3, 100ms, 2s)
      on_error: policy.denied -> escalate(admin)
      compensate release_room
  ]
```

### **Example 2: Canonical JSON (Enhanced)**

```json
{
  "speech": "ensure",
  "entity": "plix://db/table/aimos.public.users#rev@h_98fa",
  "action": {
    "capability": "plix://tool/mcp/pg.migrate#rev@h_2a10"
  },
  "with": {
    "version": "2025_11_11_01",
    "script.ref": "plix://blob/sql/ddl/users_v3#rev@h_abcd"
  },
  "pre": [
    {
      "type": "and",
      "left": {"expr": "schema_intact", "op": "==", "value": "h_prev"},
      "right": {"expr": "rowcount_stable", "op": "<=", "value": 0}
    },
    {
      "quantifier": "forall",
      "variable": "row",
      "constraint": {"expr": "unique_email", "op": "==", "value": true}
    },
    {
      "type": "eventually",
      "constraint": {"expr": "room_reserved", "op": "==", "value": true},
      "duration": "5000ms"
    }
  ],
  "post": [
    {"expr": "schema_fingerprint", "op": "==", "value": "h_next"}
  ],
  "tests": [
    {"test": "unique_email"},
    {"test": "rowcount_stable", "op": "<=", "value": 0}
  ],
  "evidence": [
    "plix://witness/schema_before",
    "plix://witness/schema_after"
  ],
  "bt": {
    "tx_time": "2025-01-27T12:00:00Z"
  },
  "plan": [
    {
      "step": "validate_preconditions",
      "errors": [
        {"error": "constraint.violated", "action": "fail"}
      ]
    },
    {
      "step": "reserve_room",
      "retry": {
        "max": 3,
        "backoff": "exponential",
        "min_delay": "100ms",
        "max_delay": "2s",
        "jitter": true
      },
      "errors": [
        {"error": "net.timeout", "action": "retry", "config": {"max": 3, "min_delay": "100ms", "max_delay": "2s"}},
        {"error": "policy.denied", "action": "escalate", "config": {"target": "admin"}}
      ],
      "compensate": "release_room"
    }
  ]
}
```

### **Example 3: S-Form (Enhanced)**

```
(ensure
  (ent plix://db/table/aimos.public.users#rev@h_98fa)
  (use plix://tool/mcp/pg.migrate#rev@h_2a10)
  (with (version "2025_11_11_01") (script.ref plix://blob/sql/ddl/users_v3#rev@h_abcd))
  (pre 
    (and (= schema_intact h_prev) (<= rowcount_stable 0))
    (forall row (unique_email row))
    (eventually (= room_reserved true) 5000ms))
  (post (= schema_fingerprint h_next))
  (tests unique_email (rowcount_stable <= 0))
  (evidence schema_before schema_after)
  (bt now)
  (plan
    (step validate_preconditions
      (on_error constraint.violated fail))
    (step reserve_room
      (retry 3 exponential 100ms 2s jitter)
      (on_error net.timeout retry (retry 3 100ms 2s))
      (on_error policy.denied escalate admin)
      (compensate release_room))))
```

---

## 🎯 **IMPLEMENTATION CHECKLIST**

### **Phase 1 Tasks**

- [x] **Grammar Specification** - EBNF grammar defined
- [x] **Enhanced Constraints** - Logical operators, quantifiers, temporal operators added
- [x] **Error Taxonomy** - Complete error type system defined
- [x] **Canonical JSON Schema** - JSON Schema v2020-12 defined
- [x] **S-Form Syntax** - S-expression syntax specified
- [x] **Round-Trip Rules** - Conversion invariants documented
- [ ] **Parser Implementation** - Human-PLIX parser (indentation-based)
- [ ] **Parser Delimiters** - Optional `{}` block support
- [ ] **Edge Case Handling** - Dangling refs, malformed URNs, circular deps
- [ ] **Round-Trip Tests** - Conversion tests for all three forms
- [ ] **Performance Tests** - Parser benchmarks

---

**Status:** ✅ **GRAMMAR SPECIFICATION COMPLETE**  
**Next:** Parser Implementation  
**Version:** 2.0.0 (Enhanced with External AI Feedback)

