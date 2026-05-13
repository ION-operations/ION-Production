# Section 2: Core Concepts and Ontology

**Status:** ✅ **EXTRACTED FROM TEXTBOOK + PHASE 3 REGISTRY**  
**Source:** PLIX Textbook Part II: Architecture (Chapters 5-8) + Phase 3 Registry Implementation  
**Last Updated:** 2025-01-27

---

## **2.1 Tag System**

### **Tag Format**

```
plix://{namespace}/{path}#rev@{hash}
```

**Components:**
- **Namespace:** Entity category (e.g., `db`, `tool`, `witness`)
- **Path:** Hierarchical path within namespace (e.g., `table/users`, `mcp/pg.migrate`)
- **Revision:** Optional revision identifier
- **Hash:** Optional content hash for verification

### **Tag Examples**

**Entity Tags:**
- `plix://db/table/users#rev@h_98fa` - Database table entity
- `plix://blob/sql/ddl/users_v3#rev@h_abcd` - SQL script blob

**Capability Tags:**
- `plix://tool/mcp/pg.migrate#rev@h_2a10` - Tool capability
- `plix://service/api/room_reservation#rev@h_3b20` - Service capability

**Evidence Tags:**
- `plix://witness/schema_before` - Witness before operation
- `plix://witness/schema_after` - Witness after operation

### **Tag Resolution**

**Multi-Source Resolution:**
1. **Tag Registry (Phase 3):** Primary source, cached, authoritative
2. **HHNI:** Semantic search for entity/action lookups
3. **SEG:** Evidence/lineage resolution
4. **CMC:** General atom lookups

**Resolution Priority:**
1. Registry cache (fastest)
2. Tag Registry (authoritative)
3. HHNI (semantic search)
4. SEG (evidence/lineage)
5. CMC (general lookup)

### **Tag Rename Governance**

**Rename Process:**
1. Authority tier validation (must have sufficient tier)
2. Dependent tracking (find tags that reference renamed tag)
3. Dependent acknowledgment (require dependents to acknowledge)
4. Rename completion (after all dependents acknowledge)

**See:** [Phase 3 Registry Implementation](../../../PHASE3_IMPLEMENTATION_SUMMARY.md) for details.

---

## **2.2 Bitemporal Model**

### **Transaction Time (`tx_time`)**

**Definition:**
- When the fact was recorded in the system
- Immutable, append-only timeline
- Used for audit trails and provenance

**Usage:**
- Audit queries: "What did we know at time T?"
- Provenance tracking: "When was this fact recorded?"
- Timeline reconstruction: "What was the system state at time T?"

### **Valid Time (`valid_time`)**

**Definition:**
- When the fact is/was valid in the real world
- Can be updated (bitemporal versioning)
- Used for temporal queries

**Usage:**
- Temporal queries: "What was valid at time T?"
- Historical queries: "What was valid from T1 to T2?"
- Time-travel queries: "What was valid when we recorded it?"

### **Bitemporal Example**

```plix
bt:
  tx_time: 2025-01-27T12:00:00Z
  valid_time: 2024-01-01T00:00:00Z/2024-12-31T23:59:59Z
```

**Query Examples:**
- Query at transaction time: "What did we know at 2025-01-27?"
- Query at valid time: "What was valid in 2024?"
- Query both: "What did we know was valid in 2024 when we recorded it?"

### **Bitemporal Rules**

**Rule 1: Transaction Time Immutability**
- `tx_time` is set at intent creation and never changes
- Enables append-only audit trail
- Prevents retroactive modifications

**Rule 2: Valid Time Mutability**
- `valid_time` can be updated (bitemporal versioning)
- Old versions preserved (bitemporal history)
- Enables "what was valid when" queries

**Rule 3: Temporal Consistency**
- Valid time must be consistent with transaction time
- Cannot have valid time before transaction time
- Temporal queries respect both times

---

## **2.3 Authority Tiers**

### **Tier System**

**Tier Definitions:**
- **S (Supreme):** Highest authority, system-critical operations
- **A (Authoritative):** High authority, important operations
- **B (Basic):** Medium authority, standard operations
- **C (Common):** Low authority, routine operations

### **Tier Usage**

**Tag Registration:**
- Tags require appropriate authority tier
- Higher-tier tags require higher-tier registration
- Tier determines who can modify/rename tags

**GGP Proposals:**
- GGP proposals require tier-based quorum
- Higher-tier proposals require more approvals
- Tier determines proposal acceptance threshold

**Operations:**
- Operations validate tier before execution
- Insufficient tier → escalation or rejection
- Tier determines operation authorization

### **Tier Validation**

**Authority Check:**
```typescript
function hasAuthority(provided: AuthorityTier, required: AuthorityTier): boolean {
  const tiers: AuthorityTier[] = ['C', 'B', 'A', 'S'];
  const providedIndex = tiers.indexOf(provided);
  const requiredIndex = tiers.indexOf(required);
  return providedIndex >= requiredIndex;
}
```

**Example:**
- Provided: `'A'`, Required: `'B'` → ✅ Authorized (A ≥ B)
- Provided: `'B'`, Required: `'A'` → ❌ Insufficient (B < A)

---

## **2.4 Complete Lexicon**

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

## **2.5 Core Ontology**

### **Entity Types**

**Database Entities:**
- `plix://db/table/{name}` - Database tables
- `plix://db/schema/{name}` - Database schemas
- `plix://db/view/{name}` - Database views

**Tool Capabilities:**
- `plix://tool/mcp/{name}` - MCP tool capabilities
- `plix://tool/api/{name}` - API tool capabilities
- `plix://tool/cli/{name}` - CLI tool capabilities

**Evidence/Witnesses:**
- `plix://witness/{name}` - VIF witnesses
- `plix://evidence/{name}` - SEG evidence nodes

### **Action Types**

**CRUD Operations:**
- `create` - Create entity
- `read` - Read entity
- `update` - Update entity
- `delete` - Delete entity

**Execution Operations:**
- `migrate` - Database migration
- `deploy` - Application deployment
- `validate` - Validation operation
- `test` - Test execution

### **Capability Types**

**Typed Capabilities:**
- `Capability<In, Out>` - Generic capability with input/output types
- `Capability<Version:String, Script:Tag> -> Hash` - Specific capability signature

**Capability Examples:**
- `plix://tool/mcp/pg.migrate<Version:String, Script:Tag> -> Hash`
- `plix://service/api/room_reservation<Date:String, Duration:Number> -> ReservationId`

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 3: Syntax (Grammar)](./03_syntax.md)

