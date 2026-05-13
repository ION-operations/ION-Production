# Chapter 7: Enhanced Constraint Language

**Part:** II - Architecture  
**Chapter:** 7  
**Target Word Count:** 3,500-4,000 words (enhanced from 3,000-3,500)  
**Status:** ✅ **COMPLETE** (v2.0 Enhanced)  
**Priority:** ⚠️ **HIGH** - Essential for expressiveness

---

## Introduction

In Chapter 6, we explored the three surface forms of PLIx—Human-PLIX, Canonical JSON, and S-form. We saw how constraints are expressed in each form, but we haven't yet explored the full power of PLIx constraints.

PLIx provides an **enhanced constraint language** that goes far beyond simple comparisons. It includes:

1. **Basic Constraints:** Simple comparisons (`==`, `!=`, `<=`, `>=`, `<`, `>`)
2. **Logical Constraints:** Composition with `AND`, `OR`, `NOT`
3. **Quantified Constraints:** Universal (`FORALL`) and existential (`EXISTS`) quantifiers
4. **Temporal Constraints:** Time-based conditions (`EVENTUALLY`, `ALWAYS`, `WITHIN`)

This chapter explores each constraint type, shows how to compose them, and explains how constraints are evaluated. By the end, you'll be able to express complex intent requirements with precision and clarity.

---

## Section 7.1: Basic Constraints (Review)

### Simple Comparisons

Basic constraints express simple comparisons between values. They form the foundation of PLIx constraint language.

**Comparison Operators:**
- `==` - Equality
- `!=` - Inequality
- `<=` - Less than or equal
- `>=` - Greater than or equal
- `<` - Less than
- `>` - Greater than

### Basic Constraint Syntax

**Human-PLIX:**
```plix
Entity: plix://room/meeting_room  # Canonical entity identity

pre:
  con:room_available == true
  con:user_authenticated == true
  con:duration <= 4h
  con:capacity >= 5
```

**Canonical JSON:**
```json
{
  "entity": "plix://room/meeting_room",  # Canonical entity identity
  "pre": [
    {"type": "basic", "expr": "room_available", "op": "==", "value": true},
    {"type": "basic", "expr": "user_authenticated", "op": "==", "value": true},
    {"type": "basic", "expr": "duration", "op": "<=", "value": "4h"},
    {"type": "basic", "expr": "capacity", "op": ">=", "value": 5}
  ]
}
```

**S-form:**
```
(entity plix://room/meeting_room  # Canonical entity identity
 (pre
  (= room_available true)
  (= user_authenticated true)
  (<= duration 4h)
  (>= capacity 5)))
```

### Basic Constraint Examples

**Example 1: Room Booking Preconditions (with entity tag)**
```plix
Entity: plix://room/meeting_room  # Canonical entity identity

pre:
  con:room_available == true
  con:user_authenticated == true
  con:duration <= 4h
```

**Example 2: Database Migration Preconditions**
```plix
pre:
  con:schema_intact == h_prev
  con:rowcount_stable <= 0
```

**Example 3: User Authentication Preconditions**
```plix
pre:
  con:user_exists == true
  con:credentials_valid == true
```

### When to Use Basic Constraints

**Use Basic Constraints When:**
- Expressing simple conditions (equality, comparison)
- Checking single values (boolean, number, string)
- Validating simple properties (availability, authentication)

**Don't Use Basic Constraints When:**
- Expressing complex conditions (use logical constraints)
- Checking collections (use quantified constraints)
- Expressing time-based conditions (use temporal constraints)

---

## Section 7.2: Logical Constraints (NEW)

### Logical Operators

Logical constraints enable composition of multiple constraints using logical operators:

- `AND` - Both constraints must be true
- `OR` - At least one constraint must be true
- `NOT` - Constraint must be false

### Logical Constraint Syntax

**Human-PLIX:**
```plix
Entity: plix://schema/database_schema  # Canonical entity identity

pre:
  con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
  con:(room_available == true) OR (waitlist_enabled == true)
  con:NOT (maintenance_mode == true)
```

**Canonical JSON:**
```json
{
  "entity": "plix://schema/database_schema",  # Canonical entity identity
  "pre": [
    {
      "type": "logical",
      "operator": "and",
      "left": {"type": "basic", "expr": "schema_intact", "op": "==", "value": "h_prev"},
      "right": {"type": "basic", "expr": "rowcount_stable", "op": "<=", "value": 0}
    },
    {
      "type": "logical",
      "operator": "or",
      "left": {"type": "basic", "expr": "room_available", "op": "==", "value": true},
      "right": {"type": "basic", "expr": "waitlist_enabled", "op": "==", "value": true}
    },
    {
      "type": "logical",
      "operator": "not",
      "left": {"type": "basic", "expr": "maintenance_mode", "op": "==", "value": true}
    }
  ]
}
```

**S-form:**
```
(entity plix://schema/database_schema  # Canonical entity identity
 (pre
  (and (= schema_intact h_prev) (<= rowcount_stable 0))
  (or (= room_available true) (= waitlist_enabled true))
  (not (= maintenance_mode true))))
```

### Logical Constraint Examples

**Example 1: AND - Both Conditions Required (for specific entity)**
```plix
Entity: plix://schema/database_schema  # Canonical entity identity

pre:
  con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
```
**Meaning:** For this specific schema entity, schema must be intact AND row count must be stable.

**Example 2: OR - Either Condition Acceptable (for specific entity)**
```plix
Entity: plix://room/meeting_room  # Canonical entity identity

pre:
  con:(room_available == true) OR (waitlist_enabled == true)
```
**Meaning:** For this specific room entity, room must be available OR waitlist must be enabled.

**Example 3: NOT - Condition Must Be False**
```plix
pre:
  con:NOT (maintenance_mode == true)
```
**Meaning:** Maintenance mode must NOT be enabled.

**Example 4: Nested Logical Operators**
```plix
pre:
  con:((a == 1) AND (b == 2)) OR ((c == 3) AND (d == 4))
```
**Meaning:** Either (a==1 AND b==2) OR (c==3 AND d==4).

### Logical Constraint Evaluation

**AND Evaluation:**
- Both operands must be true
- Short-circuit: If left is false, right is not evaluated
- Returns true only if both are true

**OR Evaluation:**
- At least one operand must be true
- Short-circuit: If left is true, right is not evaluated
- Returns true if either is true

**NOT Evaluation:**
- Operand must be false
- Returns true if operand is false
- Returns false if operand is true

### When to Use Logical Constraints

**Use Logical Constraints When:**
- Expressing complex conditions (multiple requirements)
- Combining multiple constraints (AND, OR)
- Negating conditions (NOT)

**Don't Use Logical Constraints When:**
- Expressing simple conditions (use basic constraints)
- Checking collections (use quantified constraints)
- Expressing time-based conditions (use temporal constraints)

---

## Section 7.3: Quantified Constraints (NEW)

### Quantifiers

Quantified constraints enable expressing conditions over collections:

- `FORALL` - Universal quantifier (all items must satisfy)
- `EXISTS` - Existential quantifier (at least one item must satisfy)

### Quantified Constraint Syntax

**Human-PLIX:**
```plix
Entity: plix://data/user_table  # Canonical entity identity

pre:
  con:forall_rows unique_email
  con:exists_room (capacity >= 10)
```

**Canonical JSON:**
```json
{
  "entity": "plix://data/user_table",  # Canonical entity identity
  "pre": [
    {
      "type": "quantified",
      "quantifier": "forall",
      "variable": "row",
      "domain": "rows",
      "entity_tag": "plix://data/user_table",  # Entity tag for domain
      "predicate": {
        "type": "basic",
        "expr": "unique_email",
        "op": "==",
        "value": true
      }
    },
    {
      "type": "quantified",
      "quantifier": "exists",
      "variable": "room",
      "domain": "rooms",
      "entity_tag": "plix://room/meeting_room",  # Entity tag for domain
      "predicate": {
        "type": "basic",
        "expr": "capacity",
        "op": ">=",
        "value": 10
      }
    }
  ]
}
```

**S-form:**
```
(entity plix://data/user_table  # Canonical entity identity
 (pre
  (forall row rows (unique_email row))
  (exists room rooms (>= capacity 10))))
```

### Quantified Constraint Examples

**Example 1: FORALL - All Rows Must Have Unique Email (for specific entity)**
```plix
Entity: plix://data/user_table  # Canonical entity identity

pre:
  con:forall_rows unique_email
```
**Meaning:** For this specific user table entity, for all rows in the collection, each row must have a unique email.

**Example 2: EXISTS - At Least One Room Has Capacity >= 10 (for specific entity)**
```plix
Entity: plix://room/meeting_room  # Canonical entity identity

pre:
  con:exists_room (capacity >= 10)
```
**Meaning:** For this specific room entity collection, there exists at least one room with capacity >= 10.

**Example 3: FORALL with Complex Predicate**
```plix
pre:
  con:forall_users (authenticated == true) AND (permissions_valid == true)
```
**Meaning:** For all users, each user must be authenticated AND have valid permissions.

**Example 4: EXISTS with Complex Predicate**
```plix
pre:
  con:exists_room (available == true) AND (capacity >= 5)
```
**Meaning:** There exists at least one room that is available AND has capacity >= 5.

### Quantified Constraint Evaluation

**FORALL Evaluation:**
- Iterates over all items in collection
- Applies predicate to each item
- Returns true only if ALL items satisfy predicate
- Returns false if ANY item fails predicate

**EXISTS Evaluation:**
- Iterates over all items in collection
- Applies predicate to each item
- Returns true if ANY item satisfies predicate
- Returns false only if ALL items fail predicate

### When to Use Quantified Constraints

**Use Quantified Constraints When:**
- Checking collections (all items, some items)
- Expressing database constraints (unique, foreign keys)
- Validating array/list properties

**Don't Use Quantified Constraints When:**
- Expressing simple conditions (use basic constraints)
- Expressing logical composition (use logical constraints)
- Expressing time-based conditions (use temporal constraints)

---

## Section 7.4: Temporal Constraints (NEW)

### Temporal Operators

Temporal constraints enable expressing time-based conditions:

- `EVENTUALLY` - Constraint will eventually be true
- `ALWAYS` - Constraint must always be true
- `WITHIN` - Constraint must be true within duration
- `AFTER` - Constraint must be true after duration
- `BEFORE` - Constraint must be true before duration

### Temporal Constraint Syntax

**Human-PLIX:**
```plix
Entity: plix://payment/transaction  # Canonical entity identity

pre:
  con:eventually_true(condition, within_ms=5000)
  con:always_true(schema_intact)
  con:within_timeout(response_received, timeout=30s)
```

**Canonical JSON:**
```json
{
  "entity": "plix://payment/transaction",  # Canonical entity identity
  "pre": [
    {
      "type": "temporal",
      "operator": "eventually",
      "entity_tag": "plix://payment/transaction",  # Entity tag
      "constraint": {"type": "basic", "expr": "condition", "op": "==", "value": true},
      "duration": "5000ms"
    },
    {
      "type": "temporal",
      "operator": "always",
      "entity_tag": "plix://schema/database_schema",  # Entity tag
      "constraint": {"type": "basic", "expr": "schema_intact", "op": "==", "value": true}
    },
    {
      "type": "temporal",
      "operator": "within",
      "entity_tag": "plix://payment/transaction",  # Entity tag
      "constraint": {"type": "basic", "expr": "response_received", "op": "==", "value": true},
      "timeout": "30s"
    }
  ]
}
```

**S-form:**
```
(entity plix://payment/transaction  # Canonical entity identity
 (pre
  (eventually (= condition true) 5000ms)
  (always (= schema_intact true))
  (within (= response_received true) 30s)))
```

### Temporal Constraint Examples

**Example 1: EVENTUALLY - Condition Will Eventually Be True (for specific entity)**
```plix
Entity: plix://payment/transaction  # Canonical entity identity

pre:
  con:eventually_true(payment_received, within_ms=5000)
```
**Meaning:** For this specific payment transaction entity, payment will eventually be received within 5 seconds.

**Example 2: ALWAYS - Condition Must Always Be True (for specific entity)**
```plix
Entity: plix://schema/database_schema  # Canonical entity identity

pre:
  con:always_true(schema_intact)
```
**Meaning:** For this specific schema entity, schema must always be intact (throughout execution).

**Example 3: WITHIN - Condition Must Be True Within Duration**
```plix
pre:
  con:within_timeout(response_received, timeout=30s)
```
**Meaning:** Response must be received within 30 seconds.

**Example 4: AFTER - Condition Must Be True After Duration**
```plix
post:
  con:after_delay(confirmation_sent, delay=1s)
```
**Meaning:** Confirmation must be sent after 1 second delay.

**Example 5: BEFORE - Condition Must Be True Before Duration**
```plix
pre:
  con:before_deadline(approval_received, deadline=24h)
```
**Meaning:** Approval must be received before 24-hour deadline.

### Temporal Constraint Evaluation

**EVENTUALLY Evaluation:**
- Monitors constraint over time
- Returns true if constraint becomes true within duration
- Returns false if duration expires without constraint being true

**ALWAYS Evaluation:**
- Monitors constraint continuously
- Returns true only if constraint is true at all times
- Returns false if constraint becomes false at any time

**WITHIN Evaluation:**
- Monitors constraint with timeout
- Returns true if constraint is true within timeout
- Returns false if timeout expires without constraint being true

**AFTER Evaluation:**
- Waits for duration, then checks constraint
- Returns true if constraint is true after duration
- Returns false if constraint is false after duration

**BEFORE Evaluation:**
- Checks constraint before deadline
- Returns true if constraint is true before deadline
- Returns false if deadline passes without constraint being true

### When to Use Temporal Constraints

**Use Temporal Constraints When:**
- Expressing time-based conditions (timeouts, deadlines)
- Expressing eventual consistency (eventually true)
- Expressing invariant conditions (always true)

**Don't Use Temporal Constraints When:**
- Expressing simple conditions (use basic constraints)
- Expressing logical composition (use logical constraints)
- Checking collections (use quantified constraints)

---

## Section 7.5: Constraint Composition

### Combining Constraint Types

Constraints can be composed to express complex requirements. You can combine:

- **Basic + Logical:** `(a == 1) AND (b == 2)`
- **Logical + Quantified:** `(forall_rows unique_email) AND (rowcount_stable <= 0)`
- **Quantified + Temporal:** `eventually_true(forall_rows unique_email, within_ms=5000)`
- **All Types:** Complex nested compositions

### Composition Examples

**Example 1: Basic + Logical**
```plix
pre:
  con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
```
**Composition:** Two basic constraints combined with AND.

**Example 2: Logical + Quantified**
```plix
pre:
  con:(forall_rows unique_email) AND (rowcount_stable <= 0)
```
**Composition:** Quantified constraint combined with basic constraint using AND.

**Example 3: Quantified + Temporal**
```plix
pre:
  con:eventually_true(forall_rows unique_email, within_ms=5000)
```
**Composition:** Quantified constraint wrapped in temporal constraint.

**Example 4: Complex Nested Composition**
```plix
pre:
  con:((schema_intact == h_prev) AND (rowcount_stable <= 0)) AND (forall_rows unique_email)
```
**Composition:** Multiple constraint types nested and combined.

### Composition Best Practices

**1. Use Parentheses for Clarity**
```plix
# Good: Clear precedence
con:((a == 1) AND (b == 2)) OR ((c == 3) AND (d == 4))

# Bad: Ambiguous precedence
con:a == 1 AND b == 2 OR c == 3 AND d == 4
```

**2. Group Related Constraints**
```plix
# Good: Grouped by concern
pre:
  con:(schema_intact == h_prev) AND (rowcount_stable <= 0)  # Schema constraints
  con:forall_rows unique_email                              # Data constraints
```

**3. Use Quantified Constraints for Collections**
```plix
# Good: Quantified constraint
con:forall_rows unique_email

# Bad: Manual iteration (not expressible in PLIx)
# (Would require plan steps, not constraints)
```

**4. Use Temporal Constraints for Time-Based Conditions**
```plix
# Good: Temporal constraint
con:eventually_true(payment_received, within_ms=5000)

# Bad: Plan step timeout (less declarative)
# (Would require plan step with timeout, not constraint)
```

---

## Section 7.6: Constraint Evaluation

### Evaluation Process

Constraints are evaluated in a specific order:

1. **Parse Constraints:** Parse constraint expressions into constraint objects
2. **Resolve Context:** Resolve variable values from execution context
3. **Evaluate Constraints:** Evaluate each constraint based on its type
4. **Combine Results:** Combine results using logical operators
5. **Return Result:** Return true if all constraints pass, false otherwise

### Evaluation Context

Constraints are evaluated against an **execution context** that provides:

- **Variable Values:** Current values of variables (`room_available`, `user_authenticated`) **for specific entities**
- **Entity State:** Current state of entities (`schema_intact`, `rowcount_stable`) **identified via entity tags**
- **Temporal State:** Current time and temporal state (for temporal constraints) **per entity via tags**
- **Collection State:** Current state of collections (for quantified constraints) **identified via entity tags**
- **Entity Tags:** Canonical entity identity **for filtering and querying entity-specific state** ⭐ NEW

### Evaluation Examples

**Example 1: Basic Constraint Evaluation (for specific entity)**
```plix
Entity: plix://room/meeting_room  # Canonical entity identity

pre:
  con:room_available == true
```
**Context:** `{entity_tag: "plix://room/meeting_room", room_available: true}`  
**Evaluation:** `true == true` → `true` (for this specific entity)  
**Result:** ✅ Pass

**Example 2: Logical Constraint Evaluation (for specific entity)**
```plix
Entity: plix://schema/database_schema  # Canonical entity identity

pre:
  con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
```
**Context:** `{entity_tag: "plix://schema/database_schema", schema_intact: "h_prev", rowcount_stable: 0}`  
**Evaluation:**
- Left: `"h_prev" == "h_prev"` → `true` (for this specific schema entity)
- Right: `0 <= 0` → `true` (for this specific schema entity)
- AND: `true AND true` → `true`  
**Result:** ✅ Pass

**Example 3: Quantified Constraint Evaluation (for specific entity)**
```plix
Entity: plix://data/user_table  # Canonical entity identity

pre:
  con:forall_rows unique_email
```
**Context:** `{entity_tag: "plix://data/user_table", rows: [{email: "a@example.com"}, {email: "b@example.com"}]}`  
**Evaluation:**
- Row 1: `unique_email({email: "a@example.com"}, entity_tag="plix://data/user_table")` → `true`
- Row 2: `unique_email({email: "b@example.com"}, entity_tag="plix://data/user_table")` → `true`
- FORALL: `true AND true` → `true` (for this specific user table entity)  
**Result:** ✅ Pass

**Example 4: Temporal Constraint Evaluation (for specific entity)**
```plix
Entity: plix://payment/transaction  # Canonical entity identity

pre:
  con:eventually_true(payment_received, within_ms=5000)
```
**Context:** `{entity_tag: "plix://payment/transaction", payment_received: false, start_time: 0ms, current_time: 3000ms}`  
**Evaluation:**
- Monitor: `payment_received` becomes `true` at `3500ms` (for this specific payment entity)
- Within duration: `3500ms < 5000ms` → `true`
- EVENTUALLY: `true` (for this specific payment entity)  
**Result:** ✅ Pass

### Constraint Failure Handling

When constraints fail, PLIx provides:

1. **Error Reporting:** Detailed error messages indicating which constraint failed
2. **Error Codes:** Standard error codes (`CON_001`, `CON_002`, `CON_003`)
3. **Error Actions:** Configurable error handling (retry, compensate, fail, escalate)

**Example: Constraint Failure (for specific entity)**
```plix
Entity: plix://room/meeting_room  # Canonical entity identity

pre:
  con:room_available == true
```
**Context:** `{entity_tag: "plix://room/meeting_room", room_available: false}`  
**Evaluation:** `false == true` → `false` (for this specific room entity)  
**Result:** ❌ Fail  
**Error:** `CON_001: Constraint violated for entity plix://room/meeting_room: room_available == true`  
**Action:** Fail (as configured in error handling)

### Evaluation Best Practices

**1. Provide Clear Context (with entity tags)**
- Ensure all variables are available in context **for specific entities**
- Resolve tags before evaluation **to get entity-specific state**
- Provide temporal state for temporal constraints **per entity via tags**
- Include entity tags in context **for entity-aware constraint evaluation** ⭐ NEW

**2. Handle Constraint Failures**
- Configure error handling for constraint violations
- Provide helpful error messages
- Use appropriate error actions (retry, compensate, fail)

**3. Optimize Constraint Evaluation**
- Evaluate simple constraints first (short-circuit)
- Cache constraint results when possible
- Use quantified constraints efficiently (avoid nested loops)

---

## Chapter 7 Summary

PLIx provides an enhanced constraint language **with tag-based canonical identity** that enables powerful intent expression:

1. **Basic Constraints:** Simple comparisons (`==`, `!=`, `<=`, `>=`, `<`, `>`) **for specific entities**
2. **Logical Constraints:** Composition with `AND`, `OR`, `NOT` **with entity-aware evaluation**
3. **Quantified Constraints:** Universal (`FORALL`) and existential (`EXISTS`) quantifiers **for entity collections**
4. **Temporal Constraints:** Time-based conditions (`EVENTUALLY`, `ALWAYS`, `WITHIN`) **per entity via tags**

**Key Takeaways:**
1. **Constraint Types:** Four types enable different expressiveness **with entity-aware evaluation**
2. **Composition:** Constraints can be combined for complex requirements **for specific entities**
3. **Evaluation:** Constraints are evaluated against execution context **with entity tags for entity-specific state**
4. **Failure Handling:** Constraint failures trigger configurable error actions **with entity-aware error reporting**
5. **Best Practices:** Use appropriate constraint types for different scenarios **with entity tags for clarity**

**Tags enable canonical identity** throughout constraint language: constraints are evaluated **for specific entities via tags** (`entity="plix://room/meeting_room"`), constraint context includes entity tags **for entity-specific state resolution**, quantified constraints operate **on entity collections via tags**, temporal constraints monitor **per entity via tags**, and constraint failures report **entity tags for debugging**. Tags enable unambiguous entity references that survive technology changes, enabling enhanced constraint language with canonical identity—constraints express requirements **for which entities**, evaluate **for specific entities**, and report failures **with entity context**.

**Next:** Chapter 8 explores formal validation using Alloy, TLA+, and invariant verification to ensure constraint correctness **with tag-based entity references**.

---

**Word Count:** ~3,800 words (enhanced from ~3,300)  
**Status:** ✅ **COMPLETE** (v2.0 Enhanced)  
**Cross-References:**
- Chapter 5 (Part I): Tag System (tag format and canonical identity)
- Chapter 6: Three Surface Forms (constraint syntax in each form with tags)
- Chapter 10: Error Taxonomy (constraint violation errors with entity tags)
- Chapter 15: Tag Registry (tag resolution for constraint evaluation)
