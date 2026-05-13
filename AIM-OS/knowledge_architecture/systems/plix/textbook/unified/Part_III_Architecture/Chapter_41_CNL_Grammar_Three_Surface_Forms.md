# Chapter 41: CNL Grammar: Three Surface Forms

**Part III: Architecture**  
**Unified Textbook Chapter Number:** 41

---

> **Cross-References:**
> - **PLIx Foundations:** See Chapter 40 (Four Pillars) for how CNL grammar enables Contract Layer
> - **Tag System:** See Chapter 40 (Tag System) for tag usage in each form
> - **Enhanced Constraints:** See Chapter 42 (Formal Validation) for constraint syntax
> - **Compiler Architecture:** See Chapter 43 (Compiler Architecture) for parsing all three forms
> - **Quaternion Extension:** See Chapter 63 (PLIx Geometric Extensions) for geometric addressing in CNL

---

**Target Word Count:** 3,000-3,500 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)

---

## Introduction

In Chapter 40, we explored the four pillars of PLIx architecture—Contract, Execution, Safety, and Evidence. The Contract Layer uses Controlled Natural Language (CNL) to express intent contracts. Now we turn to the grammar itself: how do we express PLIx contracts?

PLIx provides **three surface forms**—three different ways to express the same intent contract. Each form serves a different purpose:

1. **Human-PLIX:** Indentation-based, human-readable syntax for development
2. **Canonical JSON:** Machine-executable JSON format for tooling and APIs
3. **S-form:** Minimal, diff-friendly S-expression format for version control

All three forms express the **same semantics**—they are different representations of the same intent contract. This chapter explores each form, shows when to use which form, and explains how to convert between them.

**Connection to Chapter 40 (Four Pillars):** CNL grammar enables the Contract Layer pillar. All three surface forms express contracts that integrate with the four pillars architecture, enabling pure intent expression, reliable execution, safety guarantees, and verifiable outcomes.

---

## Section 41.1: Human-PLIX: Indentation-Based Syntax

### The Human-Readable Form

Human-PLIX is designed for **human readability**—it's the form developers write when creating PLIx contracts. It uses indentation-based structure (similar to YAML or Python) to create a natural, readable syntax.

### Syntax Characteristics

**Indentation-Based Structure:**
- Uses indentation (spaces or tabs) to indicate nesting
- Similar to YAML or Python syntax
- Natural, readable format

**Optional Delimiters:**
- Supports optional `{}` delimiters for deep nesting
- Helps avoid indentation ambiguity
- Provides clarity in complex contracts

**Natural Language Keywords:**
- Uses keywords like `ensure`, `ent:`, `act:`, `pre:`, `post:`
- Human-readable and intuitive
- Easy to learn and use

### Complete Human-PLIX Example

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
    con:migration_logged == true
  tests:
    tst:unique_email passes
    tst:rowcount_stable <= 0
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
  bt:
    tx_time: now()
  plan [
    step validate_preconditions
      on_error: constraint.violated -> fail
    step execute_migration
      retry 3 backoff exponential(100ms, 2s) jitter
      on_error: net.timeout -> retry with retry(3, 100ms, 2s)
      on_error: execution.failed -> compensate rollback_migration
      compensate rollback_migration
  ]
```

**Key Features:**
- **Speech Act:** `ensure` (ensures intent achievement)
- **Entity:** `ent:plix://db/table/users#rev@h_98fa` (users table with tag-based canonical identity)
- **Action:** `act:migrate` using capability `cap:plix://tool/mcp/pg.migrate#rev@h_2a10`
- **Parameters:** `with:` clause with version and script reference
- **Preconditions:** `pre:` clause with logical AND and quantified constraints
- **Postconditions:** `post:` clause with schema fingerprint and logging
- **Tests:** `tests:` clause with test specifications
- **Evidence:** `evidence:` clause with witness tags
- **Bitemporal:** `bt:` clause with transaction time
- **Plan:** `plan []` block with steps, error handling, retry, and compensation

**Connection to Chapter 40 (Tag System):** Human-PLIX uses tags (`plix://db/table/users#rev@h_98fa`) for canonical entity identity. Tags enable timeless intent expression independent of implementation.

### When to Use Human-PLIX

**Use Human-PLIX When:**
- Writing new contracts (most readable)
- Learning PLIx (easiest to understand)
- Reviewing contracts (human-friendly)
- Documenting intent (natural language)

**Don't Use Human-PLIX When:**
- Building tooling (use Canonical JSON)
- Version control diffs (use S-form)
- API integration (use Canonical JSON)
- Machine processing (use Canonical JSON)

---

## Section 41.2: Canonical JSON: Machine-Executable Format

### The Machine-Executable Form

Canonical JSON is designed for **machine processing**—it's the form tools, APIs, and compilers use. It uses standard JSON format (JSON Schema Draft 2020-12) to provide a machine-executable, validated representation.

### Syntax Characteristics

**JSON Format:**
- Standard JSON (RFC 8259)
- Validated via JSON Schema Draft 2020-12
- Machine-executable and parseable

**Structured Representation:**
- All PLIx concepts mapped to JSON structures
- Arrays for lists (preconditions, postconditions, steps)
- Objects for complex structures (constraints, steps, errors)

**Schema Validation:**
- Validated via `packages/plix/schema/plix.canonical.schema.json`
- Ensures correctness and completeness
- Enables tooling and API integration

### Complete Canonical JSON Example

```json
{
  "speech": "ensure",
  "entity": "plix://db/table/users#rev@h_98fa",
  "action": {
    "type": "capability",
    "capability": "plix://tool/mcp/pg.migrate#rev@h_2a10"
  },
  "with": {
    "version": "2025_11_11_01",
    "script.ref": "plix://blob/sql/ddl/users_v3#rev@h_abcd"
  },
  "pre": [
    {
      "type": "logical",
      "operator": "and",
      "operands": [
        {
          "type": "basic",
          "expr": "schema_intact",
          "op": "==",
          "value": "h_prev"
        },
        {
          "type": "basic",
          "expr": "rowcount_stable",
          "op": "<=",
          "value": 0
        }
      ]
    },
    {
      "type": "quantified",
      "quantifier": "forall",
      "variable": "row",
      "collection": "rows",
      "predicate": {
        "type": "basic",
        "expr": "unique_email",
        "op": "==",
        "value": true
      }
    }
  ],
  "post": [
    {
      "type": "basic",
      "expr": "schema_fingerprint",
      "op": "==",
      "value": "h_next"
    },
    {
      "type": "basic",
      "expr": "migration_logged",
      "op": "==",
      "value": true
    }
  ],
  "tests": [
    {
      "test": "unique_email",
      "bound": {
        "op": "==",
        "value": true
      }
    },
    {
      "test": "rowcount_stable",
      "bound": {
        "op": "<=",
        "value": 0
      }
    }
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
        {
          "on": "constraint.violated",
          "action": "fail"
        }
      ]
    },
    {
      "step": "execute_migration",
      "retry": {
        "max": 3,
        "backoff": "exponential",
        "min_delay": "100ms",
        "max_delay": "2s",
        "jitter": true
      },
      "errors": [
        {
          "on": "net.timeout",
          "action": "retry"
        },
        {
          "on": "execution.failed",
          "action": "compensate",
          "target_step": "rollback_migration"
        }
      ],
      "compensate": "rollback_migration"
    }
  ]
}
```

**Key Features:**
- **Speech Act:** `"speech": "ensure"`
- **Entity:** `"entity": "plix://db/table/users#rev@h_98fa"` (tag-based canonical identity)
- **Action:** `"action": { "type": "capability", "capability": "..." }`
- **Parameters:** `"with": { ... }` object
- **Preconditions:** `"pre": [ ... ]` array of constraint objects
- **Postconditions:** `"post": [ ... ]` array of constraint objects
- **Tests:** `"tests": [ ... ]` array of test objects
- **Evidence:** `"evidence": [ ... ]` array of tag strings
- **Bitemporal:** `"bt": { "tx_time": "..." }` object
- **Plan:** `"plan": [ ... ]` array of step objects

**Connection to Chapter 43 (Compiler Architecture):** Canonical JSON is the primary format for compiler input. The compiler parses Canonical JSON and generates execution plans, enabling intent-preserving compilation.

### When to Use Canonical JSON

**Use Canonical JSON When:**
- Building tooling (parsers, compilers, validators)
- API integration (REST APIs, GraphQL)
- Machine processing (automation, scripts)
- Storage and serialization (databases, files)

**Don't Use Canonical JSON When:**
- Writing contracts manually (use Human-PLIX)
- Version control diffs (use S-form)
- Human review (use Human-PLIX)

---

## Section 41.3: S-Form: Minimal, Diff-Friendly Format

### The Minimal Form

S-form is designed for **version control**—it's the form that produces clean, readable diffs. It uses S-expression format (Lisp-like) to provide a minimal, diff-friendly representation.

### Syntax Characteristics

**S-Expression Format:**
- Lisp-like syntax with parentheses
- Minimal representation
- Preserves all semantic information

**Diff-Friendly:**
- One line per concept (when possible)
- Minimal changes produce minimal diffs
- Easy to review in version control

**Complete Semantics:**
- Preserves all PLIx concepts
- No information loss
- Round-trip convertible

### Complete S-Form Example

```
(ensure
  (ent plix://db/table/users#rev@h_98fa)
  (use plix://tool/mcp/pg.migrate#rev@h_2a10)
  (with (version "2025_11_11_01") (script.ref plix://blob/sql/ddl/users_v3#rev@h_abcd))
  (pre 
    (and (= schema_intact h_prev) (<= rowcount_stable 0))
    (forall row rows (unique_email row)))
  (post (= schema_fingerprint h_next) (= migration_logged true))
  (tests unique_email rowcount_stable)
  (evidence plix://witness/schema_before plix://witness/schema_after)
  (bt (tx_time now))
  (plan
    (step validate_preconditions
      (on_error constraint.violated fail))
    (step execute_migration
      (retry 3 exponential 100ms 2s jitter)
      (on_error net.timeout retry)
      (on_error execution.failed compensate rollback_migration)
      (compensate rollback_migration))))
```

**Key Features:**
- **Speech Act:** `(ensure ...)`
- **Entity:** `(ent plix://db/table/users#rev@h_98fa)` (tag-based canonical identity)
- **Action:** `(use plix://tool/mcp/pg.migrate#rev@h_2a10)`
- **Parameters:** `(with ...)`
- **Preconditions:** `(pre ...)` with nested S-expressions
- **Postconditions:** `(post ...)`
- **Tests:** `(tests ...)`
- **Evidence:** `(evidence ...)`
- **Bitemporal:** `(bt ...)`
- **Plan:** `(plan ...)` with nested step S-expressions

**Connection to CMC (Chapter 5):** S-form integrates with CMC by storing contracts in minimal format. CMC preserves S-form contracts with bitemporal tracking, enabling version control with clean diffs.

### When to Use S-Form

**Use S-Form When:**
- Version control (clean diffs)
- Minimal representation (smallest file size)
- Machine processing (simple parsing)
- Storage efficiency (compact format)

**Don't Use S-Form When:**
- Writing contracts manually (use Human-PLIX)
- Human readability (use Human-PLIX)
- API integration (use Canonical JSON)

---

## Section 41.4: When to Use Which Form

### Decision Tree

**Question 1: Who is the primary audience?**
- **Human developers** → Use Human-PLIX
- **Machines/tools** → Use Canonical JSON
- **Version control** → Use S-form

**Question 2: What is the primary use case?**
- **Writing contracts** → Use Human-PLIX
- **Tooling/APIs** → Use Canonical JSON
- **Diffs/storage** → Use S-form

**Question 3: What is the context?**
- **Development** → Use Human-PLIX
- **Production** → Use Canonical JSON
- **Version control** → Use S-form

### Form Comparison

| Feature | Human-PLIX | Canonical JSON | S-Form |
|---------|-----------|----------------|--------|
| **Readability** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Poor | ⭐⭐⭐ Good |
| **Writability** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Poor | ⭐⭐⭐ Good |
| **Machine Processing** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Diff Quality** | ⭐⭐ Poor | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Tooling Support** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Storage Size** | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |

### Best Practices

**Development Workflow:**
1. **Write** contracts in Human-PLIX (readable, writable)
2. **Convert** to Canonical JSON for tooling (validation, compilation)
3. **Store** in S-form for version control (clean diffs)

**API Integration:**
- **Accept** Human-PLIX or Canonical JSON (developer choice)
- **Process** in Canonical JSON (machine-executable)
- **Return** Canonical JSON (standardized)

**Version Control:**
- **Commit** S-form (clean diffs)
- **Review** Human-PLIX (readable)
- **Validate** Canonical JSON (correctness)

---

## Section 41.5: Round-Trip Conversion

### Conversion Invariants

All three forms must have **identical semantics**—they are different representations of the same intent contract. Conversion between forms must preserve:

1. **Semantic Preservation:** All three forms must have identical semantics
2. **Tag Resolution:** Tags must resolve to same entities across forms
3. **Bitemporal Fields:** `tx_time` and `valid_time` must be preserved
4. **Error Handling:** Error types and actions must be preserved

**Connection to Chapter 40 (Tag System):** Round-trip conversion preserves tag-based canonical identity. Tags enable consistent entity references across all three forms, ensuring semantic preservation.

### Conversion Process

**Human-PLIX → Canonical JSON:**
1. Parse indentation-based structure
2. Resolve tags via registry
3. Normalize constraint expressions
4. Convert plan blocks to arrays
5. Validate via JSON Schema

**Canonical JSON → Human-PLIX:**
1. Generate indentation-based structure
2. Format tags with proper spacing
3. Expand constraint expressions
4. Format plan blocks with proper indentation
5. Preserve all semantic information

**Human-PLIX ↔ S-form:**
1. Convert indentation to parentheses
2. Preserve tag references
3. Maintain constraint semantics
4. Preserve plan structure
5. Ensure round-trip compatibility

**Canonical JSON ↔ S-form:**
1. Convert JSON objects to S-expressions
2. Preserve all fields
3. Maintain type information
4. Preserve bitemporal fields
5. Ensure semantic equivalence

**Connection to Chapter 43 (Compiler Architecture):** Round-trip conversion is essential for compiler architecture. The compiler must preserve semantics when converting between forms, enabling intent-preserving compilation.

---

## Section 41.6: Grammar Specification (EBNF)

### Complete EBNF Grammar

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

**Error Handling:**
```
ErrorClause ::= "on_error:" ErrorType "->" ErrorAction
ErrorType ::= "net.timeout" | "policy.denied" | "constraint.violated" | "contract.precondition_failed" | "contract.postcondition_failed" | "proof.missing" | "auth.insufficient" | "resource.exceeded"
ErrorAction ::= "retry" | "compensate" | "fail" | "escalate" | "fallback" Identifier
```

### Grammar Enhancements

**1. Logical Operators:**
- Added `and`, `or`, `not` to `LogicalConstraint`
- Enables composition: `con:(a == b) AND (c <= d)`

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

**Connection to Chapter 42 (Formal Validation):** EBNF grammar enables formal validation. All three surface forms must conform to the grammar, enabling mathematical verification of contract correctness.

---

## Chapter 41 Summary

PLIx provides three surface forms—three different ways to express the same intent contract. Each form serves a different purpose:

1. **Human-PLIX:** Indentation-based, human-readable syntax for development
2. **Canonical JSON:** Machine-executable JSON format for tooling and APIs
3. **S-form:** Minimal, diff-friendly S-expression format for version control

**Key Takeaways:**
1. **Three Forms:** Human-PLIX, Canonical JSON, and S-form express the same semantics
2. **When to Use:** Choose form based on audience, use case, and context
3. **Round-Trip Conversion:** All forms are convertible with semantic preservation
4. **Grammar Specification:** Complete EBNF grammar defines all three forms
5. **Grammar Enhancements:** Logical, quantified, and temporal constraints extend expressiveness

**Tags enable canonical identity** throughout all three forms: Human-PLIX uses tags (`ent:plix://db/table/users#rev@h_98fa`), Canonical JSON stores tags as strings (`"entity": "plix://db/table/users#rev@h_98fa"`), and S-form preserves tags (`(ent plix://db/table/users#rev@h_98fa)`). Tags ensure consistent entity references across all forms, enabling timeless intent expression.

**Connection to AIM-OS:** PLIx CNL grammar enables AIM-OS's vision (Chapter 2) by providing multiple surface forms for intent expression. This enables AI consciousness (Chapter 4), verifiable intelligence (Chapter 7), orchestration (Chapter 8), and self-awareness (Chapter 11). Tags integrate with CMC (Chapter 5) for timeless storage, HHNI (Chapter 6) for contract indexing, and Quaternion Extension (Chapter 63) for geometric addressing.

**Next:** Chapter 42 explores formal validation—mathematical verification of contract correctness using Alloy, TLA+, and Coq/Lean.

---

**Word Count:** ~3,400 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)  
**Cross-References:**
- **Part I (AIM-OS Foundations):** Chapters 2, 4, 5, 6, 7, 8, 11
- **Part III (PLIx Architecture):** Chapters 40 (Four Pillars), 42 (Formal Validation), 43 (Compiler Architecture)
- **Part VIII (Quaternion Extension):** Chapter 63 (PLIx Geometric Extensions)

---

**Next Chapter:** [Chapter 42: Formal Validation: Mathematical Verification](Chapter_42_Formal_Validation_Mathematical_Verification.md)  
**Previous Chapter:** [Chapter 40: The Four Pillars](Chapter_40_The_Four_Pillars_Contract_Execution_Safety_Evidence.md)  
**Up:** [Part III: Architecture](../Part_III_Architecture/)

