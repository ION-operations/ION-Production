# Section 8: Appendices/Reference Sections

**Status:** ✅ **POPULATED WITH REFERENCE TABLES**  
**Source:** Lexicon Table, Test Suites, External AI Feedback  
**Last Updated:** 2025-01-27

---

## **8.1 Complete Lexicon**

**See:** [Complete Lexicon Table](../lexicon/lexicon_table.md) for exhaustive reference.

**Summary:**
- **Tag Prefixes:** 6 (`ent:`, `cap:`, `act:`, `con:`, `test:`, `ev:`)
- **Operators:** 11 (comparison: `==`, `!=`, `<=`, `>=`, `<`, `>`; logical: `AND`, `OR`, `NOT`; quantifiers: `FORALL`, `EXISTS`)
- **Keywords:** 11 (`intent`, `ent:`, `act:`, `using`, `with:`, `pre:`, `post:`, `tests:`, `evidence:`, `bt:`, `plan`)
- **Speech Acts:** 7 (`ask`, `assert`, `plan`, `ensure`, `measure`, `decide`, `retract`)
- **Types:** 6 (`Entity`, `Action`, `Capability<In, Out>`, `Constraint`, `Test`, `Evidence`)

**Total Entries:** 41

**Auto-Generation:**
- Lexicon table is auto-generated from Phase 3 Registry + Phase 1 Parser
- Regenerate via: `npm run generate:lexicon`
- Source: `packages/plix/spec/scripts/generate_lexicon.ts`

---

## **8.2 Language Comparison Matrix**

**See:** [External AI Feedback Synthesis](../../knowledge_architecture/systems/plix/EXTERNAL_AI_FEEDBACK_SYNTHESIS.md#language-comparison-matrix) for complete comparison.

**Summary:**
- **20 PLIX constructs** mapped to nearest analogs in other languages
- **Languages compared:** PL/I, Datomic, RDF, Hoare Logic, TLA+, Alloy, Prolog, SQL, GraphQL, OpenAPI, JSON Schema, YAML, TOML, Gherkin, Cucumber, Rego, Terraform, Ansible, Puppet, Chef

**Key Comparisons:**
- **Tags:** Similar to RDF URIs, Datomic entity IDs
- **Contracts:** Similar to Hoare Logic pre/postconditions
- **Bitemporal:** Similar to Datomic bitemporal model
- **Constraints:** Similar to TLA+ invariants, Alloy predicates
- **Tests:** Similar to Gherkin/Cucumber scenarios

---

## **8.3 Keyword Index**

**Auto-Generated from Phase 1 Parser**

**Keywords by Category:**

**Tag Prefixes:**
- `ent:` - Entity identity
- `cap:` - Capability reference
- `act:` - Action identifier
- `con:` - Constraint expression
- `test:` - Test specification
- `ev:` - Evidence reference

**Operators:**
- Comparison: `==`, `!=`, `<=`, `>=`, `<`, `>`
- Logical: `AND`, `OR`, `NOT`
- Quantifiers: `FORALL`, `EXISTS`

**Speech Acts:**
- `ask` - Query intent
- `assert` - Assertion intent
- `plan` - Planning intent
- `ensure` - Guaranteed execution
- `measure` - Measurement intent
- `decide` - Decision intent
- `retract` - Retraction intent

**Plan Keywords:**
- `step` - Plan step
- `retry` - Retry specification
- `backoff` - Backoff strategy
- `compensate` - Compensation action
- `fallback` - Fallback step
- `on_error` - Error handling clause

**Time Keywords:**
- `tx_time` - Transaction time
- `valid_time` - Valid time
- `now()` - Current time function

---

## **8.4 Complete Tag Registry**

**Auto-Generated from Phase 3 Registry**

**Tag Registry Structure:**
- **Namespace:** Entity category (e.g., `db`, `tool`, `witness`)
- **Path:** Hierarchical path within namespace (e.g., `table/users`, `mcp/pg.migrate`)
- **Revision:** Optional revision identifier
- **Hash:** Optional content hash for verification

**Tag Examples:**

**Database Entities:**
- `plix://db/table/users#rev@h_98fa`
- `plix://db/schema/public#rev@h_abcd`
- `plix://db/view/active_users#rev@h_1234`

**Tool Capabilities:**
- `plix://tool/mcp/pg.migrate#rev@h_2a10`
- `plix://tool/api/room_reservation#rev@h_3b20`
- `plix://tool/cli/deploy#rev@h_4c30`

**Evidence/Witnesses:**
- `plix://witness/schema_before`
- `plix://witness/schema_after`
- `plix://evidence/migration_provenance`

**Registry Query API:**
```typescript
// Query by namespace
const tags = await registry.queryTags({ namespace: 'db' });

// Query by authority tier
const tierATags = await registry.queryTags({ authorityTier: 'A' });

// Query by date range
const recentTags = await registry.queryTags({
  dateRange: {
    from: '2025-01-01T00:00:00Z',
    to: '2025-01-27T23:59:59Z'
  }
});
```

---

## **8.5 Error Code Reference**

**Complete Error Taxonomy:**

**Network Errors:**
- `NET_001` - Network timeout
- `NET_002` - Network unavailable
- `NET_003` - Network refused

**Policy Errors:**
- `POL_001` - Policy denied
- `POL_002` - Policy violation
- `POL_003` - Policy unauthorized

**Constraint Errors:**
- `CON_001` - Constraint violated
- `CON_002` - Constraint unmet
- `CON_003` - Constraint invalid

**Contract Errors:**
- `CTR_001` - Contract precondition failed
- `CTR_002` - Contract postcondition failed
- `CTR_003` - Contract invariant broken
- `CTR_004` - Contract compensation failed
- `CTR_005` - Contract invalid structure

**Proof Errors:**
- `PRF_001` - Proof unverifiable
- `PRF_002` - Proof insufficient evidence
- `PRF_003` - Proof contradicted

**Authentication Errors:**
- `AUT_001` - Authentication failed
- `AUT_002` - Authentication expired
- `AUT_003` - Authentication permission denied

**Resource Errors:**
- `RES_001` - Resource unavailable
- `RES_002` - Resource exhausted
- `RES_003` - Resource locked

**Execution Errors:**
- `EXE_001` - Execution failed
- `EXE_002` - Execution step failed
- `EXE_003` - Execution timeout
- `EXE_004` - Execution cancelled
- `EXE_005` - Execution dependency failed
- `EXE_006` - Execution fallback failed

**See:** [Error Taxonomy](../sections/03_syntax.md#error-taxonomy) for complete details.

---

## **8.6 Bibliography**

**Core References:**

**PL/I Language Reference:**
- IBM PL/I Language Reference Manual
- PL/I Language Design Principles

**Datomic Papers:**
- "Datomic: A Functional Database" (Rich Hickey)
- Bitemporal Model Documentation

**RDF Specifications:**
- W3C RDF 1.1 Concepts and Abstract Syntax
- RDF Schema 1.1

**Hoare Logic:**
- "An Axiomatic Basis for Computer Programming" (C.A.R. Hoare)
- Design by Contract (Bertrand Meyer)

**TLA+ and Alloy:**
- "Specifying Systems" (Leslie Lamport)
- "Software Abstractions" (Daniel Jackson)

**Formal Methods:**
- "Introduction to Formal Methods" (Various)
- Model Checking and Verification

**AIM-OS Documentation:**
- North Star Document
- CMC Bitemporal Model
- VIF Witness System
- APOE Execution Engine
- SEG Evidence Graph

---

## **8.7 Version Compatibility Matrix**

| PLIX Language Version | Spec Version | Status | Notes |
|----------------------|--------------|--------|-------|
| v1.0 | v1.0 | ✅ Current | Initial release |
| v0.x | N/A | ⚠️ Pre-spec | Pre-specification versions |

**Compatibility Policy:**
- PLIX language version and spec version align semantically
- Breaking changes (major version) require GGP approval
- Additions (minor version) tracked via GGPs
- Clarifications (patch version) documented in change log

**Migration Guide:**
- v0.x → v1.0: See [Migration Guide](../MIGRATION_GUIDE.md) (if exists)
- Future versions: Tracked via GGPs

---

## **8.8 Glossary**

**Key Terms:**

**PLIX:** Protocol Language for Integration & Explanation - A typed, tag-centric protocol language for expressing deterministic intent.

**Tag:** Canonical identity reference in format `plix://namespace/path#rev@hash`.

**Intent:** What we want to achieve, separate from how we achieve it.

**Contract:** Preconditions and postconditions expressing intent requirements.

**Bitemporal:** Tracking both transaction time (`tx_time`) and valid time (`valid_time`).

**Authority Tier:** System for authorizing operations (S, A, B, C).

**GGP:** Grammar Growth Proposal - Algorithmic proposal for language evolution.

**AIP:** Application Integration Protocol - Protocol for integrating apps with AIM-OS.

**VIF:** Verifiable Intelligence Framework - System for intent verification and witness generation.

**APOE:** Atomic Provenance Orchestration Engine - System for intent achievement and execution planning.

**SEG:** Shared Evidence Graph - System for intent lineage and evidence tracking.

**HHNI:** Hierarchical Hypergraph Neural Index - System for tag resolution and semantic search.

**SCOR:** Sanity Core: Self-Consistency, Oversight, and Resilience - AI consciousness immune system.

**CMC:** Context Memory Core - Intent-aware memory system with bitemporal versioning.

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 9: Conformance and Testing](./09_conformance.md)

