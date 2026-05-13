# Section 3: Syntax (Grammar)

**Status:** ✅ **EXTRACTED FROM GRAMMAR_SPECIFICATION_V2.md**  
**Source:** `knowledge_architecture/systems/plix/GRAMMAR_SPECIFICATION_V2.md`  
**Last Updated:** 2025-01-27

---

## **3.1 EBNF Grammar**

### **Core Grammar (EBNF)**

**Top-Level Structure:**
```
Specification ::= SpeechAct EntityClause ActionClause [WithClause] [PreClause] [PostClause] [TestsClause] [EvidenceClause] [TimeClause] [PlanClause]
```

**Speech Acts:**
```
SpeechAct ::= "ask" | "assert" | "plan" | "ensure" | "measure" | "decide" | "retract"
```

**Entity Clause:**
```
EntityClause ::= "ent:" Tag
```

**Action Clause:**
```
ActionClause ::= "act:" Identifier | "using" "cap:" Tag
```

**With Clause (Parameters):**
```
WithClause ::= "with:" WithField+
WithField ::= Key ":" (Scalar | TagRef)
TagRef ::= Tag | Key "." "ref" ":" Tag
```

**Preconditions:**
```
PreClause ::= "pre:" Constraint+
Constraint ::= ConstraintExpr | LogicalConstraint | QuantifiedConstraint | TemporalConstraint
ConstraintExpr ::= Identifier ComparisonOp (Scalar | Identifier | Tag)
ComparisonOp ::= "==" | "!=" | "<=" | ">=" | "<" | ">"
LogicalConstraint ::= ConstraintExpr ("and" | "or" | "not") ConstraintExpr
QuantifiedConstraint ::= ("forall" | "exists") Identifier ":" ConstraintExpr
TemporalConstraint ::= ("eventually" | "always" | "within") "(" ConstraintExpr "," Duration ")"
```

**Postconditions:**
```
PostClause ::= "post:" Constraint+
```

**Tests:**
```
TestsClause ::= "tests:" TestSpec+
TestSpec ::= "tst:" Identifier [TestBound]
TestBound ::= ComparisonOp Scalar
```

**Evidence:**
```
EvidenceClause ::= "evidence:" EvidenceRef+
EvidenceRef ::= "w:" Identifier | Tag
```

**Time (Bitemporal):**
```
TimeClause ::= "bt:" "tx_time:" Scalar ["valid_time:" Scalar]
```

**Plan Block:**
```
PlanClause ::= "plan" "[" PlanStep+ "]"
PlanStep ::= "step" Identifier [RetrySpec] [FallbackSpec] [CompensationSpec]
RetrySpec ::= "retry" Integer "backoff" ("linear" | "exponential" | "fixed") "(" Duration "," Duration ")" ["jitter"]
FallbackSpec ::= "fallback" Identifier
CompensationSpec ::= "compensate" Identifier
```

**Tags:**
```
Tag ::= "plix://" Namespace "/" Path ["#rev@" Hash]
Namespace ::= Identifier ("." Identifier)*
Path ::= Identifier ("/" Identifier)*
Hash ::= HexString
```

**Primitives:**
```
Identifier ::= Letter (Letter | Digit | "_" | "." | "/")*
Scalar ::= String | Number | Boolean
String ::= '"' StringChar* '"'
Number ::= Integer | Float
Boolean ::= "true" | "false"
Duration ::= Integer ("ms" | "s" | "m" | "h" | "d")
HexString ::= ("0".."9" | "a".."f" | "A".."F")+
Key ::= Identifier
```

**Error Handling:**
```
ErrorClause ::= "on_error:" ErrorType "->" ErrorAction
ErrorType ::= "net.timeout" | "policy.denied" | "constraint.violated" | "contract.precondition_failed" | "contract.postcondition_failed" | "proof.missing" | "auth.insufficient" | "resource.exceeded"
ErrorAction ::= "retry" | "compensate" | "fail" | "escalate" | "fallback" Identifier
```

### **Grammar Enhancements**

**1. Logical Operators:**
- Added `and`, `or`, `not` to `LogicalConstraint`
- Enables composition: `con:schema_intact AND rowcount_stable`

**2. Quantifiers:**
- Added `forall` and `exists` to `QuantifiedConstraint`
- Enables: `con:forall_rows unique_email`

**3. Temporal Operators:**
- Added `eventually`, `always`, `within` to `TemporalConstraint`
- Enables: `con:eventually_true(condition, within_ms)`

**4. Error Taxonomy:**
- Added `ErrorClause` with typed `ErrorType`
- Enables declarative error handling: `on_error: net.timeout -> retry`

**5. Optional Delimiters:**
- Human-PLIX supports optional `{}` blocks for deep nesting
- Parser handles both indentation-based and delimiter-based syntax

---

## **3.2 Surface Forms**

### **Human-PLIX (Indentation-Based)**

**Syntax:**
- Indentation-based structure (similar to YAML/Python)
- Optional delimiters (`{}`) for deep nesting
- Human-readable, developer-friendly

**Example:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  with:
    version: "2025_11_11_01"
    script.ref: plix://blob/sql/ddl/users_v3#rev@h_abcd
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
    con:forall_rows unique_email
  post:
    con:schema_fingerprint == h_next
  tests:
    tst:unique_email passes
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
      compensate release_room
  ]
```

### **Canonical JSON (Machine-Executable)**

**Syntax:**
- JSON format (JSON Schema Draft 2020-12)
- Machine-executable, AIP-compilable
- Validated via JSON Schema

**Example:**
```json
{
  "speech": "ensure",
  "entity": "plix://db/table/users#rev@h_98fa",
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
    }
  ],
  "post": [
    {"expr": "schema_fingerprint", "op": "==", "value": "h_next"}
  ],
  "tests": [
    {"test": "unique_email"}
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
    }
  ]
}
```

**Schema Location:**
- `packages/plix/schema/plix.canonical.schema.json`
- JSON Schema Draft 2020-12
- Validates Canonical JSON form

### **S-Form (Minimal, Diff-Friendly)**

**Syntax:**
- S-expression format (Lisp-like)
- Minimal, diff-friendly for version control
- Preserves all semantic information

**Example:**
```
(ensure
  (ent plix://db/table/users#rev@h_98fa)
  (use plix://tool/mcp/pg.migrate#rev@h_2a10)
  (with (version "2025_11_11_01") (script.ref plix://blob/sql/ddl/users_v3#rev@h_abcd))
  (pre 
    (and (= schema_intact h_prev) (<= rowcount_stable 0))
    (forall row (unique_email row)))
  (post (= schema_fingerprint h_next))
  (tests unique_email)
  (evidence schema_before schema_after)
  (bt now)
  (plan
    (step validate_preconditions
      (on_error constraint.violated fail))
    (step reserve_room
      (retry 3 exponential 100ms 2s jitter)
      (on_error net.timeout retry (retry 3 100ms 2s))
      (compensate release_room))))
```

---

## **3.3 Parser Edge Cases**

### **1. Dangling References**

**Problem:**
- Plan steps reference non-existent steps
- Tags reference non-existent entities

**Detection:**
- Parser validates all step dependencies
- Parser validates all tag references
- Reports missing references with suggestions

**Example:**
```plix
plan [
  step step1
  step step2
    depends_on: [step3]  # ERROR: step3 doesn't exist
]
```

### **2. Malformed URNs**

**Problem:**
- Invalid tag format
- Missing namespace or path
- Invalid revision hash

**Detection:**
- Parser validates tag URN format
- Checks namespace/path syntax
- Verifies revision hash format

**Example:**
```plix
ent:plix://invalid tag  # ERROR: Invalid tag format
ent:plix://db           # ERROR: Missing path
ent:plix://db/table/users#rev@invalid_hash  # ERROR: Invalid hash format
```

### **3. Circular Dependencies**

**Problem:**
- Plan steps form dependency cycles
- Circular tag references

**Detection:**
- Parser detects circular plan dependencies
- Reports dependency cycles
- Suggests dependency fixes

**Example:**
```plix
plan [
  step step1
    depends_on: [step2]
  step step2
    depends_on: [step1]  # ERROR: Circular dependency
]
```

### **4. Indentation Ambiguity**

**Problem:**
- Mixed indentation (tabs/spaces)
- Ambiguous indentation levels

**Solution:**
- Parser normalizes indentation
- Supports optional delimiters (`{}`) for clarity
- Provides clear error messages

**Example:**
```plix
pre:
  con:a == 1
    con:b == 2  # ERROR: Ambiguous indentation
```

**Fixed with delimiters:**
```plix
pre: {
  con:a == 1
  con:b == 2
}
```

### **5. Constraint Parsing**

**Problem:**
- Nested logical operators
- Quantified constraint syntax
- Temporal constraint validation

**Solution:**
- Parser handles nested logical operators
- Validates quantified constraint syntax
- Validates temporal constraint syntax

**Example:**
```plix
pre:
  con:(a == 1) AND ((b == 2) OR (c == 3))  # Nested logical operators
  con:forall_rows (unique_email AND valid_format)  # Quantified with nested logical
  con:eventually_true(condition, within_ms=5000)  # Temporal constraint
```

---

## **3.4 Round-Trip Conversion Rules**

### **Conversion Invariants**

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

### **Conversion Process**

**Human-PLIX → Canonical JSON:**
1. Parse indentation-based structure
2. Resolve tags via registry
3. Normalize constraint expressions
4. Convert plan blocks to arrays

**Canonical JSON → Human-PLIX:**
1. Generate indentation-based structure
2. Format tags with proper spacing
3. Expand constraint expressions
4. Format plan blocks with proper indentation

**Human-PLIX ↔ S-form:**
1. Convert indentation to parentheses
2. Preserve tag references
3. Maintain constraint semantics
4. Preserve plan structure

**Canonical JSON ↔ S-form:**
1. Convert JSON objects to S-expressions
2. Preserve all fields
3. Maintain type information
4. Preserve bitemporal fields

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 4: Semantics](./04_semantics.md)

