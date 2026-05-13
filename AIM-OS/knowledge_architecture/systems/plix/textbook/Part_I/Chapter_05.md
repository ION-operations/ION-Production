# Chapter 5: The Tag System: Canonical Identity

**Part:** I - Foundations  
**Chapter:** 5  
**Target Word Count:** 3,000-3,500 words  
**Status:** ✅ **COMPLETE**  
**Priority:** ⚠️ **CRITICAL** - Foundational for all subsequent chapters

---

## Introduction

In the previous chapters, we explored the fundamental concepts of pure language, intent-execution separation, meaning and trust, and AI consciousness. We saw how PLIx enables these transformative capabilities, but we haven't yet examined the foundational mechanism that makes it all possible: **the tag system**.

Tags are the canonical identity system for PLIx. They provide a way to uniquely identify entities, capabilities, and evidence across time, space, and systems. Without tags, PLIx contracts would be ambiguous, intent would be unclear, and verification would be impossible.

This chapter introduces the tag system—the foundation upon which all PLIx capabilities are built. We'll explore the tag format, understand tag components, examine tag types, learn how tags are resolved, and see why tags enable the transformative capabilities we've discussed.

---

## Section 5.1: Tag Format: The URN Scheme

### The Problem: Ambiguous Identity

Consider a simple intent: "book a meeting room." Without tags, this intent is ambiguous. Which room? Which booking system? Which calendar? The intent lacks identity—it cannot be uniquely identified, verified, or tracked.

Traditional systems solve this with namespaces, IDs, or paths, but these are fragile. A database table might be renamed, a tool might be deprecated, a witness might be lost. Identity becomes ambiguous, intent becomes unclear, and verification becomes impossible.

**Tags solve this problem by providing canonical identity—a unique, immutable identifier that survives changes, migrations, and evolution.**

### The URN Scheme

PLIx tags use a URN (Uniform Resource Name) scheme inspired by web standards but designed for intent expression:

```
plix://{namespace}/{path}#rev@{hash}
```

**Components:**
- **`plix://`** - Protocol identifier (always `plix://`)
- **`{namespace}`** - Entity category (e.g., `db`, `tool`, `witness`)
- **`{path}`** - Hierarchical path within namespace (e.g., `table/users`, `mcp/pg.migrate`)
- **`#rev@`** - Revision separator (optional)
- **`{hash}`** - Content hash for verification (optional)

### Why URN Scheme Matters

The URN scheme provides several critical benefits:

1. **Canonical Identity:** Every tag is unique and unambiguous
2. **Hierarchical Organization:** Namespace and path provide natural organization
3. **Version Control:** Revision and hash enable versioning and verification
4. **System Independence:** Tags work across systems, databases, and tools
5. **Timelessness:** Tags survive technology changes and migrations

### Tag Format Examples

**Entity Tags:**
```
plix://db/table/users#rev@h_98fa
plix://blob/sql/ddl/users_v3#rev@h_abcd
plix://room/meeting_room
```

**Capability Tags:**
```
plix://tool/mcp/pg.migrate#rev@h_2a10
plix://service/api/room_reservation#rev@h_3b20
plix://capability/auth/authenticate
```

**Evidence Tags:**
```
plix://witness/schema_before
plix://witness/schema_after
plix://evidence/migration_complete
```

Each tag uniquely identifies an entity, capability, or evidence, enabling unambiguous intent expression and verification.

---

## Section 5.2: Tag Components Explained

### Namespace: Entity Category

The namespace categorizes the tag's purpose and domain. Common namespaces include:

- **`db`** - Database entities (tables, schemas, views)
- **`tool`** - Tool capabilities (MCP tools, APIs, CLIs)
- **`witness`** - Evidence witnesses (VIF witnesses, proofs)
- **`blob`** - Blob storage (SQL scripts, configuration files)
- **`service`** - Service capabilities (APIs, microservices)
- **`room`** - Domain entities (meeting rooms, resources)
- **`auth`** - Authentication entities (users, sessions)

**Namespace Examples:**
```
plix://db/table/users          # Database table
plix://tool/mcp/pg.migrate     # MCP tool
plix://witness/schema_before   # VIF witness
```

Namespaces provide natural organization and enable namespace-based queries and filtering.

### Path: Hierarchical Organization

The path provides hierarchical organization within the namespace. Paths use forward slashes (`/`) to create hierarchies:

```
plix://db/table/users                    # Database table
plix://db/schema/public                  # Database schema
plix://tool/mcp/pg.migrate              # MCP tool
plix://tool/mcp/pg.query                # Another MCP tool
plix://witness/schema_before            # Witness
plix://witness/schema_after             # Another witness
```

Paths enable:
- **Hierarchical Organization:** Natural grouping of related tags
- **Path-Based Queries:** Query by path pattern (e.g., `plix://db/table/*`)
- **Namespace Scoping:** Organize tags within namespaces

### Revision: Optional Version Identifier

The revision identifier enables versioning and tracking changes:

```
plix://db/table/users#rev@h_98fa
plix://db/table/users#rev@h_99fb
```

Revisions enable:
- **Version Tracking:** Track changes to entities
- **Version Queries:** Query specific versions
- **Change History:** Track evolution over time

### Hash: Optional Content Verification

The hash provides content verification and integrity checking:

```
plix://db/table/users#rev@h_98fa
plix://blob/sql/ddl/users_v3#rev@h_abcd
```

Hashes enable:
- **Content Verification:** Verify tag content hasn't changed
- **Integrity Checking:** Detect tampering or corruption
- **Deterministic Identity:** Same content → same hash → same tag

### Complete Tag Examples

**Database Migration Tag:**
```
plix://db/table/users#rev@h_98fa
```
- **Namespace:** `db` (database entity)
- **Path:** `table/users` (users table)
- **Revision:** `h_98fa` (specific version)
- **Purpose:** Uniquely identifies the users table at a specific version

**Tool Capability Tag:**
```
plix://tool/mcp/pg.migrate#rev@h_2a10
```
- **Namespace:** `tool` (tool capability)
- **Path:** `mcp/pg.migrate` (PostgreSQL migrate tool via MCP)
- **Revision:** `h_2a10` (specific version)
- **Purpose:** Uniquely identifies the PostgreSQL migrate tool capability

**Evidence Witness Tag:**
```
plix://witness/schema_before
```
- **Namespace:** `witness` (evidence witness)
- **Path:** `schema_before` (schema state before operation)
- **Revision:** None (current version)
- **Purpose:** Uniquely identifies a witness of schema state

---

## Section 5.3: Tag Types: Entity, Capability, Evidence

PLIx tags serve three primary purposes, corresponding to three tag types:

### Entity Tags: What We're Acting On

Entity tags identify the entities we're acting on—the "what" of intent:

```
plix://db/table/users
plix://room/meeting_room
plix://blob/sql/ddl/users_v3
```

**Entity Tag Characteristics:**
- Identify **what** we're acting on
- Represent **domain entities** (tables, rooms, files)
- Used in **entity clauses** (`ent:`)
- Enable **entity-based queries** and **entity tracking**

**Entity Tag Example:**
```plix
ensure ent:plix://db/table/users
  act:migrate
  ...
```

This tag identifies the `users` table as the entity we're migrating.

### Capability Tags: What We're Using

Capability tags identify the capabilities we're using—the "how" of intent:

```
plix://tool/mcp/pg.migrate
plix://service/api/room_reservation
plix://capability/auth/authenticate
```

**Capability Tag Characteristics:**
- Identify **what** we're using to achieve intent
- Represent **tool capabilities** (MCP tools, APIs, services)
- Used in **capability clauses** (`cap:`)
- Enable **capability-based routing** and **capability discovery**

**Capability Tag Example:**
```plix
ensure ent:plix://db/table/users
  act:migrate using cap:plix://tool/mcp/pg.migrate
  ...
```

This tag identifies the PostgreSQL migrate tool as the capability we're using.

### Evidence Tags: What We're Proving

Evidence tags identify the evidence we're producing—the "proof" of intent achievement:

```
plix://witness/schema_before
plix://witness/schema_after
plix://evidence/migration_complete
```

**Evidence Tag Characteristics:**
- Identify **what** we're proving
- Represent **evidence witnesses** (VIF witnesses, proofs)
- Used in **evidence clauses** (`evidence:`)
- Enable **evidence tracking** and **verification**

**Evidence Tag Example:**
```plix
ensure ent:plix://db/table/users
  act:migrate
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
  ...
```

These tags identify the witnesses we're producing to prove migration success.

### When to Use Each Tag Type

**Use Entity Tags When:**
- Identifying the entity you're acting on
- Expressing "what" you're modifying
- Tracking entity state changes

**Use Capability Tags When:**
- Identifying the tool/service you're using
- Expressing "how" you're achieving intent
- Routing to specific capabilities

**Use Evidence Tags When:**
- Identifying evidence you're producing
- Expressing "proof" of intent achievement
- Tracking verification witnesses

---

## Section 5.4: Tag Resolution: Multi-Source Lookup

Tags are not just identifiers—they must be **resolved** to their actual definitions. Tag resolution is the process of looking up a tag and retrieving its definition, metadata, and associated data.

### The Resolution Problem

When we see a tag like `plix://db/table/users`, we need to know:
- What is this entity? (definition)
- Where is it stored? (location)
- What are its properties? (metadata)
- Who created it? (provenance)

Tag resolution answers these questions by looking up the tag across multiple sources.

### Multi-Source Resolution

PLIx uses a **multi-source resolution strategy** that queries multiple systems in priority order:

**Resolution Priority:**
1. **Registry Cache** (fastest) - In-memory cache of recently resolved tags
2. **Tag Registry** (authoritative) - Primary source, cached, authoritative
3. **HHNI** (semantic search) - Semantic search for entity/action lookups
4. **SEG** (evidence/lineage) - Evidence/lineage resolution
5. **CMC** (general lookup) - General atom lookups

**Why Multi-Source?**

Different sources serve different purposes:
- **Registry:** Fast, authoritative, cached
- **HHNI:** Semantic search when exact match not found
- **SEG:** Evidence and lineage tracking
- **CMC:** General storage and retrieval

Multi-source resolution ensures tags can be resolved even if one source is unavailable or incomplete.

### Resolution Process

**Step 1: Check Cache**
```
Tag: plix://db/table/users
Cache Hit? → Yes → Return cached definition
Cache Miss? → Continue to Step 2
```

**Step 2: Query Tag Registry**
```
Tag: plix://db/table/users
Registry Query → Found → Cache and return
Not Found? → Continue to Step 3
```

**Step 3: Query HHNI (Semantic Search)**
```
Tag: plix://db/table/users
HHNI Query → Found → Cache and return
Not Found? → Continue to Step 4
```

**Step 4: Query SEG (Evidence/Lineage)**
```
Tag: plix://db/table/users
SEG Query → Found → Cache and return
Not Found? → Continue to Step 5
```

**Step 5: Query CMC (General Lookup)**
```
Tag: plix://db/table/users
CMC Query → Found → Cache and return
Not Found? → Resolution failed
```

### Resolution Examples

**Example 1: Registry Cache Hit**
```
Tag: plix://db/table/users
Resolution: Cache Hit (0.1ms)
Result: { definition: "users table", location: "postgres://db/users", ... }
```

**Example 2: Registry Resolution**
```
Tag: plix://db/table/users
Resolution: Registry Query (5ms)
Result: { definition: "users table", location: "postgres://db/users", ... }
Cache: Updated with result
```

**Example 3: HHNI Semantic Search**
```
Tag: plix://db/table/users
Resolution: Registry Miss → HHNI Query (50ms)
Result: { definition: "users table", similarity: 0.95, ... }
Cache: Updated with result
```

**Example 4: Multi-Source Fallback**
```
Tag: plix://db/table/users
Resolution: Registry Miss → HHNI Miss → SEG Found (100ms)
Result: { definition: "users table", lineage: [...], ... }
Cache: Updated with result
```

### Resolution Best Practices

**1. Cache Aggressively**
- Cache resolved tags to avoid repeated lookups
- Invalidate cache on tag updates
- Use cache for frequently accessed tags

**2. Handle Resolution Failures**
- Check all sources before failing
- Provide helpful error messages
- Suggest similar tags if exact match not found

**3. Optimize Resolution Order**
- Check cache first (fastest)
- Query registry second (authoritative)
- Use semantic search as fallback (slower but comprehensive)

---

## Section 5.5: Tag Identity: Why Tags Matter

Tags are not just identifiers—they enable the transformative capabilities we've discussed throughout this book. Let's explore why tags matter.

### Tags Enable Separation

**Without Tags:**
```python
# Ambiguous: Which users table? Which database?
def migrate_users_table():
    db.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
```

**With Tags:**
```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate
  ...
```

Tags enable **canonical identity**—unambiguous identification that survives changes, migrations, and evolution.

### Tags Enable Timelessness

**Without Tags:**
- Entity identity tied to implementation (database name, table name)
- Identity breaks when implementation changes
- Intent becomes ambiguous

**With Tags:**
- Entity identity independent of implementation
- Identity survives technology changes
- Intent remains clear

**Example:**
```
plix://db/table/users#rev@h_98fa
```

This tag identifies the users table regardless of:
- Database name (PostgreSQL, MySQL, MongoDB)
- Table name (users, user_table, user_accounts)
- Technology stack (REST, GraphQL, gRPC)

### Tags Enable Verifiability

**Without Tags:**
- Evidence cannot be uniquely identified
- Verification is ambiguous
- Trust is impossible

**With Tags:**
- Evidence uniquely identified via tags
- Verification is unambiguous
- Trust is verifiable

**Example:**
```plix
evidence:
  w:plix://witness/schema_before
  w:plix://witness/schema_after
```

These tags uniquely identify the witnesses, enabling unambiguous verification.

### Tags Enable Consciousness

**Without Tags:**
- AI systems cannot identify their own intent
- Self-awareness is impossible
- Consciousness is blocked

**With Tags:**
- AI systems can identify intent via tags
- Self-awareness becomes possible
- Consciousness is enabled

**Example:**
```plix
ensure ent:plix://db/table/users
  act:migrate
  ...
```

The AI system knows:
- **What** it's acting on (`plix://db/table/users`)
- **How** it's achieving intent (`cap:plix://tool/mcp/pg.migrate`)
- **What** it's proving (`w:plix://witness/schema_before`)

This self-awareness enables AI consciousness.

---

## Section 5.6: Tag Examples: Real-World Usage

Let's examine complete PLIx contracts that demonstrate tag usage in real-world scenarios.

### Example 1: Database Migration

```plix
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  with:
    version: "2025_11_11_01"
    script.ref: plix://blob/sql/ddl/users_v3#rev@h_abcd
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
  post:
    con:schema_fingerprint == h_next
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
  bt:
    tx_time: now()
```

**Tag Analysis:**
- **Entity Tag:** `plix://db/table/users#rev@h_98fa` - Identifies the users table
- **Capability Tag:** `plix://tool/mcp/pg.migrate#rev@h_2a10` - Identifies the migrate tool
- **Blob Tag:** `plix://blob/sql/ddl/users_v3#rev@h_abcd` - Identifies the migration script
- **Evidence Tags:** `plix://witness/schema_before`, `plix://witness/schema_after` - Identify witnesses

### Example 2: Room Booking

```plix
ensure ent:plix://room/meeting_room
  act:book
  with:
    date: "2025-12-01"
    duration: "2h"
    user_id: "user123"
  pre:
    con:room_available == true
    con:user_authenticated == true
  post:
    con:room_reserved == true
    con:calendar_event_created == true
  evidence:
    w:plix://witness/reservation_record
    w:plix://witness/calendar_event_id
  bt:
    tx_time: now()
```

**Tag Analysis:**
- **Entity Tag:** `plix://room/meeting_room` - Identifies the meeting room
- **Evidence Tags:** `plix://witness/reservation_record`, `plix://witness/calendar_event_id` - Identify witnesses

### Example 3: User Authentication

```plix
ensure ent:plix://auth/user_session
  act:authenticate
  with:
    user_id: "user123"
    credentials: "${hashed_password}"
  pre:
    con:user_exists == true
    con:credentials_valid == true
  post:
    con:session_created == true
    con:token_issued == true
  evidence:
    w:plix://witness/authentication_witness
  bt:
    tx_time: now()
```

**Tag Analysis:**
- **Entity Tag:** `plix://auth/user_session` - Identifies the user session
- **Evidence Tag:** `plix://witness/authentication_witness` - Identifies authentication witness

---

## Chapter 5 Summary

Tags are the foundation of PLIx—the canonical identity system that enables pure language, intent-execution separation, timelessness, verifiability, and AI consciousness.

**Key Takeaways:**
1. **Tag Format:** `plix://namespace/path#rev@hash` provides canonical identity
2. **Tag Components:** Namespace, path, revision, and hash serve distinct purposes
3. **Tag Types:** Entity, capability, and evidence tags serve different roles
4. **Tag Resolution:** Multi-source lookup ensures tags can always be resolved
5. **Tag Identity:** Tags enable separation, timelessness, verifiability, and consciousness

**Next:** Chapter 6 explores the three surface forms of PLIx—Human-PLIX, Canonical JSON, and S-form—and how tags are used in each form.

---

**Word Count:** ~3,200 words  
**Status:** ✅ **COMPLETE**  
**Cross-References:**
- Chapter 6: Three Surface Forms (tag usage in each form)
- Chapter 15: Tag Registry (lifecycle management)
- Spec Section 2.1: Tag System

