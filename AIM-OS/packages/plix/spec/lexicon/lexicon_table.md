# PLIX Complete Lexicon

**Status:** ✅ **AUTO-GENERATED**  
**Version:** 1.0.0  
**Date:** 2025-01-27  
**Source:** Phase 3 Registry + Phase 1 Parser

---

## 📚 **COMPLETE LEXICON TABLE**

| Category | Prefix/Keyword/Operator/Type | Description | Constraints | Example |
|----------|-------------------------------|-------------|-------------|----------|
| Tag Prefix | `ent:` | Entity identity - Canonical entity reference | Must resolve via registry to Entity type | `ent:plix://db/table/users#rev@h_98fa` |
| Tag Prefix | `cap:` | Capability reference - Tool or service capability | Must resolve via registry to Capability type | `cap:plix://tool/mcp/pg.migrate#rev@h_2a10` |
| Tag Prefix | `act:` | Action identifier - Action to perform | Must be defined in action registry | `act:migrate` |
| Tag Prefix | `con:` | Constraint expression - Pre/post condition | Must be evaluable to boolean | `con:schema_intact == h_prev` |
| Tag Prefix | `test:` | Test specification - Test to execute | Must be executable test | `test:unique_email` |
| Tag Prefix | `ev:` | Evidence reference - Witness or evidence | Must resolve via registry to Evidence type | `ev:plix://witness/schema_before` |
| Operator | `==` | Equality comparison | Binary, works with scalars/identifiers | `con:a == b` |
| Operator | `!=` | Inequality comparison | Binary, works with scalars/identifiers | `con:a != b` |
| Operator | `<=` | Less than or equal comparison | Binary, numeric comparison | `con:a <= 10` |
| Operator | `>=` | Greater than or equal comparison | Binary, numeric comparison | `con:a >= 10` |
| Operator | `<` | Less than comparison | Binary, numeric comparison | `con:a < 10` |
| Operator | `>` | Greater than comparison | Binary, numeric comparison | `con:a > 10` |
| Operator | `AND` | Logical AND | Binary, logical operation | `con:(a == 1) AND (b == 2)` |
| Operator | `OR` | Logical OR | Binary, logical operation | `con:(a == 1) OR (b == 2)` |
| Operator | `NOT` | Logical NOT | Unary, logical operation | `con:NOT (a == 1)` |
| Operator | `FORALL` | Universal quantifier | Quantified, requires variable and domain | `con:FORALL row IN users (unique_email)` |
| Operator | `EXISTS` | Existential quantifier | Quantified, requires variable and domain | `con:EXISTS room IN rooms (capacity >= 10)` |
| Keyword | `intent` | Intent declaration - Top-level intent type | Required, must be speech act | `intent: ensure` |
| Keyword | `ent:` | Entity clause - Entity being acted upon | Required, must be valid tag | `ent:plix://db/table/users` |
| Keyword | `act:` | Action clause - Action to perform | Required (or using cap:) | `act:migrate` |
| Keyword | `using` | Capability clause - Use capability instead of action | Optional, requires cap: tag | `using cap:plix://tool/mcp/pg.migrate` |
| Keyword | `with:` | Parameters - Input parameters for action | Optional, key-value pairs | `with: version: "v2.0"` |
| Keyword | `pre:` | Preconditions - Conditions that must hold before execution | Optional, array of constraints | `pre: con:schema_intact == h_prev` |
| Keyword | `post:` | Postconditions - Conditions that must hold after execution | Optional, array of constraints | `post: con:schema_fingerprint == h_next` |
| Keyword | `tests:` | Test specifications - Tests to execute | Optional, array of test specs | `tests: test:unique_email` |
| Keyword | `evidence:` | Evidence requirements - Evidence/witnesses to collect | Optional, array of evidence refs | `evidence: ev:schema_before` |
| Keyword | `bt:` | Bitemporal fields - Transaction and valid time | Optional, tx_time required if present | `bt: tx_time: now()` |
| Keyword | `plan` | Plan block - Execution plan with steps | Optional, array of plan steps | `plan [ step validate ]` |
| Speech Act | `ask` | Query intent - Request information | Requires Entity, Action | `ask ent:users act:query` |
| Speech Act | `assert` | Assertion intent - Assert a fact | Requires Entity, Post | `assert ent:users post: con:valid == true` |
| Speech Act | `plan` | Planning intent - Create execution plan | Requires Entity, Action, Plan | `plan ent:users act:migrate plan [ ... ]` |
| Speech Act | `ensure` | Guaranteed execution - Ensure conditions hold | Requires Entity, Action, Pre, Post, Tests | `ensure ent:users act:migrate pre: ... post: ... tests: ...` |
| Speech Act | `measure` | Measurement intent - Measure entity properties | Requires Entity, Tests | `measure ent:users tests: test:performance` |
| Speech Act | `decide` | Decision intent - Make a decision | Requires Entity, Pre, Post | `decide ent:users pre: ... post: ...` |
| Speech Act | `retract` | Retraction intent - Retract a previous assertion | Requires Entity | `retract ent:users` |
| Type | `Entity` | Tagged entity reference | Must resolve via registry | `plix://db/table/users#rev@h_98fa` |
| Type | `Action` | Action identifier | Must be defined | `migrate` |
| Type | `Capability<In, Out>` | Callable capability with input/output types | Must resolve to tool | `plix://tool/mcp/pg.migrate<Version:String, Script:Tag> -> Hash` |
| Type | `Constraint` | Constraint expression | Must be evaluable to boolean | `schema_intact == h_prev` |
| Type | `Test` | Test specification | Must be executable | `unique_email` |
| Type | `Evidence` | Evidence reference | Must resolve to witness | `plix://witness/schema_before` |

---

## 📋 **CATEGORIES**

### **Tag Prefixes (6 entries)**
Tags that identify entities, capabilities, actions, constraints, tests, and evidence.

**Usage:**
- `ent:` - Entity references (required in intent)
- `cap:` - Capability references (used with `using` keyword)
- `act:` - Action identifiers (required in intent)
- `con:` - Constraint expressions (used in `pre:` and `post:`)
- `test:` - Test specifications (used in `tests:`)
- `ev:` - Evidence references (used in `evidence:`)

### **Operators (11 entries)**
Comparison and logical operators for constraint expressions.

**Comparison Operators:**
- `==`, `!=`, `<=`, `>=`, `<`, `>` - Binary comparison operators

**Logical Operators:**
- `AND`, `OR`, `NOT` - Logical operations

**Quantifiers:**
- `FORALL`, `EXISTS` - Quantified constraints

### **Keywords (11 entries)**
Language keywords for intent structure and clauses.

**Required Keywords:**
- `intent` - Intent declaration (top-level)
- `ent:` - Entity clause (required)
- `act:` or `using cap:` - Action/capability clause (required)

**Optional Keywords:**
- `with:` - Parameters
- `pre:` - Preconditions
- `post:` - Postconditions
- `tests:` - Test specifications
- `evidence:` - Evidence requirements
- `bt:` - Bitemporal fields
- `plan` - Plan block

### **Speech Acts (7 entries)**
Top-level intent types that determine execution semantics.

**Query Types:**
- `ask` - Query information
- `measure` - Measure properties

**Assertion Types:**
- `assert` - Assert a fact
- `retract` - Retract assertion

**Execution Types:**
- `plan` - Create execution plan
- `ensure` - Guaranteed execution (requires pre/post/tests)
- `decide` - Make a decision

### **Types (6 entries)**
Type system for PLIX entities and expressions.

**Core Types:**
- `Entity` - Tagged entity references
- `Action` - Action identifiers
- `Capability<In, Out>` - Typed capabilities
- `Constraint` - Constraint expressions
- `Test` - Test specifications
- `Evidence` - Evidence references

---

## 🔍 **SEARCHABLE INDEX**

### **By Category**
- [Tag Prefixes](#tag-prefixes-6-entries) (6)
- [Operators](#operators-11-entries) (11)
- [Keywords](#keywords-11-entries) (11)
- [Speech Acts](#speech-acts-7-entries) (7)
- [Types](#types-6-entries) (6)

### **By Usage**
- **Required:** `intent`, `ent:`, `act:` or `using cap:`
- **Optional:** `with:`, `pre:`, `post:`, `tests:`, `evidence:`, `bt:`, `plan`
- **Constraints:** `con:` with operators (`==`, `!=`, `<=`, `>=`, `<`, `>`, `AND`, `OR`, `NOT`, `FORALL`, `EXISTS`)
- **Tests:** `test:` specifications
- **Evidence:** `ev:` references

---

## 📝 **NOTES**

**Auto-Generation:**
- This lexicon is auto-generated from Phase 3 Registry and Phase 1 Parser
- To regenerate, run: `npm run generate:lexicon`
- Source code: `packages/plix/spec/scripts/generate_lexicon.ts`

**Extensibility:**
- New tags can be registered via Phase 3 Registry
- New operators can be added via GGP proposals (Phase 4)
- New speech acts can be added via GGP proposals (Phase 4)

**Versioning:**
- Lexicon version aligns with PLIX language version
- Changes tracked via GGPs (Grammar Growth Proposals)
- See [Section 5: Evolution Framework](../PLIX_LANGUAGE_SPECIFICATION.md#section-5-layer-model-and-extensions)

---

**Last Generated:** 2025-01-27  
**Total Entries:** 41  
**Status:** ✅ **COMPLETE**

