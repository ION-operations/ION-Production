# Chapter 15: Tag Registry: Lifecycle and Governance

**Part:** III - Integration  
**Chapter:** 15  
**Target Word Count:** 3,000-3,500 words  
**Status:** ✅ **COMPLETE**  
**Priority:** ⚠️ **CRITICAL** - Essential for tag lifecycle management

---

## Introduction

In Chapter 5, we explored the tag system—the canonical identity mechanism that enables PLIx. We saw how tags provide unique, unambiguous identifiers for entities, capabilities, and evidence. But tags don't exist in isolation—they must be **registered**, **resolved**, **queried**, and **governed**.

The **Tag Registry** is the system that manages the complete lifecycle of PLIx tags. It provides:

1. **Tag Registration:** Registering new tags with authority tiers
2. **Tag Resolution:** Multi-source lookup with caching
3. **Tag Queries:** Querying tags by namespace, path, tier, date range
4. **Rename Governance:** Controlled tag renaming with dependent tracking
5. **Authority Tier System:** Tier-based authorization for tag operations

This chapter explores the Tag Registry system—how tags are registered, resolved, queried, renamed, and governed. By the end, you'll understand the complete tag lifecycle and how to use the registry effectively.

---

## Section 15.1: Tag Registration Process

### Registering New Tags

Tags must be registered before they can be used in PLIx contracts. Registration creates a **TagDefinition** that stores:

- **Tag:** Full tag string (`plix://namespace/path#rev@hash`)
- **Resolved Data:** Entity/action/capability data
- **Authority Tier:** Required tier for operations (S, A, B, C)
- **Metadata:** Additional tag metadata
- **Timestamps:** Created/updated timestamps
- **Created By:** Agent/user ID who created the tag

### Registration Process

**Step 1: Parse Tag**
- Extract namespace, path, revision, hash
- Validate tag format
- Check for duplicate tags

**Step 2: Validate Authority**
- Verify authority tier is sufficient
- Check if tag requires higher tier
- Validate creator permissions

**Step 3: Create TagDefinition**
- Create tag definition object
- Set timestamps (created, updated)
- Store resolved data and metadata

**Step 4: Store Tag**
- Store in memory (Map)
- Cache for fast resolution
- Persist to CMC (if available)

### Registration Examples

**Example 1: Register Database Table Tag**
```typescript
const registry = new PLIXTagRegistry({ cmcClient });

const tagDefinition = await registry.registerTag(
  'plix://db/table/users#rev@h_98fa',
  {
    type: 'database_table',
    schema: 'public',
    name: 'users',
    columns: ['id', 'email', 'name']
  },
  'A',  // Authority tier A
  'agent-aether',
  {
    description: 'Users table in public schema',
    version: 'v3.0'
  }
);
```

**Example 2: Register Tool Capability Tag**
```typescript
const tagDefinition = await registry.registerTag(
  'plix://tool/mcp/pg.migrate#rev@h_2a10',
  {
    type: 'mcp_tool',
    tool: 'pg.migrate',
    input: { version: 'string', script: 'tag' },
    output: { hash: 'string' }
  },
  'B',  // Authority tier B
  'agent-aether',
  {
    description: 'PostgreSQL migration tool via MCP',
    version: '1.0.0'
  }
);
```

**Example 3: Register Evidence Witness Tag**
```typescript
const tagDefinition = await registry.registerTag(
  'plix://witness/schema_before',
  {
    type: 'vif_witness',
    witness_type: 'schema_fingerprint',
    fingerprint: 'h_98fa'
  },
  'C',  // Authority tier C
  'agent-aether',
  {
    description: 'Schema fingerprint witness before migration'
  }
);
```

### Authority Tier Requirements

**Tier S (Supreme):**
- System-critical operations
- Highest authority required
- Rarely used

**Tier A (Authoritative):**
- Important operations
- High authority required
- Common for production tags

**Tier B (Basic):**
- Standard operations
- Medium authority required
- Common for development tags

**Tier C (Common):**
- Routine operations
- Low authority required
- Common for temporary tags

### Registration Best Practices

**1. Use Appropriate Authority Tiers**
```typescript
// Good: Production database table → Tier A
await registry.registerTag('plix://db/table/users', ..., 'A', ...);

// Good: Development tool → Tier B
await registry.registerTag('plix://tool/dev/test', ..., 'B', ...);

// Good: Temporary witness → Tier C
await registry.registerTag('plix://witness/temp', ..., 'C', ...);
```

**2. Provide Complete Metadata**
```typescript
// Good: Complete metadata
await registry.registerTag(tag, resolved, tier, creator, {
  description: 'Clear description',
  version: '1.0.0',
  owner: 'team-name',
  documentation: 'https://docs.example.com'
});
```

**3. Validate Tag Format**
```typescript
// Good: Valid tag format
'plix://db/table/users#rev@h_98fa'

// Bad: Invalid tag format
'db/table/users'  // Missing plix:// prefix
'plix://db'       // Missing path
```

---

## Section 15.2: Tag Resolution: Multi-Source Lookup

### Resolution Process

Tag resolution follows a **multi-source lookup strategy** with priority order:

**Resolution Priority:**
1. **Registry Cache** (fastest) - In-memory cache
2. **Tag Registry** (authoritative) - Primary source
3. **HHNI** (semantic search) - Fallback semantic search
4. **SEG** (evidence/lineage) - Evidence resolution
5. **CMC** (general lookup) - General storage lookup

### Cache-First Resolution

**Step 1: Check Cache**
```typescript
if (cache.has(tag)) {
  stats.cacheHits++;
  return cache.get(tag);
}
```

**Step 2: Check Registry**
```typescript
if (tags.has(tag)) {
  const definition = tags.get(tag);
  cache.set(tag, definition);  // Cache for next time
  return definition;
}
```

**Step 3: Check Rename**
```typescript
const rename = renames.get(tag);
if (rename && rename.status === 'completed') {
  return resolveTag(rename.toTag);  // Resolve renamed tag
}
```

**Step 4: Query CMC**
```typescript
const cmcResult = await queryCMC(tag);
if (cmcResult) {
  tags.set(tag, cmcResult);
  cache.set(tag, cmcResult);
  return cmcResult;
}
```

### Resolution Examples

**Example 1: Cache Hit**
```typescript
// First resolution: Cache miss → Registry query → Cache
const tag1 = await registry.resolveTag('plix://db/table/users');
// Resolution time: 5ms (registry query)

// Second resolution: Cache hit
const tag2 = await registry.resolveTag('plix://db/table/users');
// Resolution time: 0.1ms (cache hit)
```

**Example 2: Rename Resolution**
```typescript
// Original tag
const original = await registry.resolveTag('plix://db/table/users_old');
// Returns: TagDefinition for 'plix://db/table/users_old'

// After rename to 'plix://db/table/users'
const renamed = await registry.resolveTag('plix://db/table/users_old');
// Returns: TagDefinition for 'plix://db/table/users' (redirected)
```

**Example 3: CMC Fallback**
```typescript
// Tag not in registry, query CMC
const tag = await registry.resolveTag('plix://db/table/users');
// Resolution: Registry miss → CMC query → Cache
// Returns: TagDefinition from CMC (if found)
```

### Cache Management

**Cache Statistics:**
```typescript
const stats = registry.getStats();
console.log('Cache hit rate:', stats.cacheHitRate);
// Example: 0.85 (85% cache hit rate)
```

**Cache Invalidation:**
```typescript
// Clear cache (e.g., after tag updates)
registry.clearCache();
```

**Cache Best Practices:**
- Cache aggressively (fast resolution)
- Invalidate on tag updates
- Monitor cache hit rate (target: >80%)

---

## Section 15.3: Tag Queries

### Query Capabilities

The Tag Registry provides powerful query capabilities:

- **By Namespace:** Query all tags in a namespace
- **By Path Pattern:** Query tags matching path pattern
- **By Authority Tier:** Query tags by authority tier
- **By Date Range:** Query tags created/updated in date range
- **Pagination:** Limit and offset for large result sets

### Query Examples

**Example 1: Query by Namespace**
```typescript
const dbTags = await registry.queryTags({
  namespace: 'db',
  limit: 100
});
// Returns: All tags in 'db' namespace
```

**Example 2: Query by Path Pattern**
```typescript
const userTables = await registry.queryTags({
  namespace: 'db',
  pathPattern: 'table/users.*',
  limit: 50
});
// Returns: All tags matching 'table/users.*' pattern
```

**Example 3: Query by Authority Tier**
```typescript
const tierATags = await registry.queryTags({
  authorityTier: 'A',
  limit: 100
});
// Returns: All tags with authority tier A
```

**Example 4: Query by Date Range**
```typescript
const recentTags = await registry.queryTags({
  dateRange: {
    from: '2025-01-01T00:00:00Z',
    to: '2025-01-31T23:59:59Z'
  },
  limit: 100
});
// Returns: All tags created in January 2025
```

**Example 5: Complex Query**
```typescript
const results = await registry.queryTags({
  namespace: 'db',
  pathPattern: 'table/.*',
  authorityTier: 'A',
  dateRange: {
    from: '2025-01-01T00:00:00Z',
    to: '2025-01-31T23:59:59Z'
  },
  limit: 50,
  offset: 0
});
// Returns: Database table tags with tier A created in January 2025
```

### Query Best Practices

**1. Use Specific Queries**
```typescript
// Good: Specific namespace query
await registry.queryTags({ namespace: 'db', limit: 100 });

// Bad: Query all tags (inefficient)
await registry.queryTags({ limit: 10000 });
```

**2. Use Pagination**
```typescript
// Good: Paginated query
await registry.queryTags({ namespace: 'db', limit: 100, offset: 0 });

// Bad: Query all tags at once (memory intensive)
await registry.queryTags({ namespace: 'db' });
```

**3. Combine Filters**
```typescript
// Good: Combined filters
await registry.queryTags({
  namespace: 'db',
  authorityTier: 'A',
  limit: 100
});
```

---

## Section 15.4: Rename Governance Workflow

### The Rename Problem

Tags provide canonical identity, but sometimes tags need to be renamed:
- Namespace reorganization
- Path restructuring
- Naming convention changes
- Deprecation and migration

**The Challenge:** Renaming a tag breaks all references to it. How do we rename tags safely?

### Rename Governance Process

The Tag Registry provides **governed rename workflow**:

**Step 1: Authority Tier Validation**
- Verify requester has sufficient authority tier
- Check if tag requires higher tier
- Validate rename permissions

**Step 2: Dependent Tracking**
- Find all tags that reference the renamed tag
- Identify dependent contracts
- Track dependent systems

**Step 3: Dependent Acknowledgment**
- Notify dependents of rename
- Require dependents to acknowledge
- Track acknowledgment status

**Step 4: Rename Completion**
- Complete rename after all dependents acknowledge
- Create redirect from old tag to new tag
- Update all dependent references

### Rename Workflow Example

**Step 1: Initiate Rename**
```typescript
const rename = await registry.renameTag(
  'plix://db/table/users_old',  // From tag
  'plix://db/table/users',      // To tag
  'A',                           // Authority tier
  'agent-aether',                // Renamed by
  'Standardizing naming convention'  // Reason
);
// Status: 'pending'
// Dependents: ['plix://contract/migration_v1', 'plix://contract/migration_v2']
```

**Step 2: Dependent Acknowledgment**
```typescript
// Dependent 1 acknowledges
await registry.acknowledgeRename(
  'plix://db/table/users_old',
  'plix://contract/migration_v1',
  'agent-aether'
);

// Dependent 2 acknowledges
await registry.acknowledgeRename(
  'plix://db/table/users_old',
  'plix://contract/migration_v2',
  'agent-aether'
);
// Status: 'acknowledged' → 'completed'
```

**Step 3: Rename Completion**
```typescript
// Rename is now completed
// Old tag redirects to new tag
const resolved = await registry.resolveTag('plix://db/table/users_old');
// Returns: TagDefinition for 'plix://db/table/users' (redirected)
```

### Rename Status Tracking

**Status Values:**
- **`pending`** - Rename initiated, waiting for acknowledgments
- **`acknowledged`** - All dependents acknowledged, completing rename
- **`completed`** - Rename completed, redirect active
- **`rejected`** - Rename rejected (insufficient authority, conflicts)

**Rename History:**
```typescript
const history = registry.getRenameHistory('plix://db/table/users');
// Returns: Array of TagRename objects showing rename history
```

### Rename Best Practices

**1. Provide Clear Reasons**
```typescript
// Good: Clear reason
await registry.renameTag(fromTag, toTag, tier, creator, 
  'Standardizing naming convention across all database tables');

// Bad: No reason
await registry.renameTag(fromTag, toTag, tier, creator);
```

**2. Track Dependents**
```typescript
// Good: Check dependents before rename
const dependents = await registry.getDependents(fromTag);
console.log('Dependents:', dependents);
// Notify dependents before rename
```

**3. Use Appropriate Authority Tiers**
```typescript
// Good: Sufficient authority tier
await registry.renameTag(fromTag, toTag, 'A', creator, reason);

// Bad: Insufficient authority tier
await registry.renameTag(fromTag, toTag, 'C', creator, reason);
// Error: Insufficient authority tier
```

---

## Section 15.5: Authority Tier System

### Tier Definitions

**Tier S (Supreme):**
- Highest authority
- System-critical operations
- Rarely used
- Examples: Core system tags, critical infrastructure

**Tier A (Authoritative):**
- High authority
- Important operations
- Common for production
- Examples: Production database tables, production tools

**Tier B (Basic):**
- Medium authority
- Standard operations
- Common for development
- Examples: Development tools, test data

**Tier C (Common):**
- Low authority
- Routine operations
- Common for temporary
- Examples: Temporary witnesses, test tags

### Tier Validation

**Authority Check:**
```typescript
function hasAuthority(provided: AuthorityTier, required: AuthorityTier): boolean {
  const tiers: AuthorityTier[] = ['C', 'B', 'A', 'S'];
  const providedIndex = tiers.indexOf(provided);
  const requiredIndex = tiers.indexOf(required);
  return providedIndex >= requiredIndex;
}
```

**Examples:**
- Provided: `'A'`, Required: `'B'` → ✅ Authorized (A ≥ B)
- Provided: `'B'`, Required: `'A'` → ❌ Insufficient (B < A)
- Provided: `'S'`, Required: `'A'` → ✅ Authorized (S ≥ A)

### Tier-Based Operations

**Tag Registration:**
- Tags require appropriate authority tier
- Higher-tier tags require higher-tier registration
- Tier determines who can modify/rename tags

**Tag Rename:**
- Rename requires sufficient authority tier
- Must have tier ≥ tag's authority tier
- Higher-tier renames require more approvals

**Tag Queries:**
- Can query by authority tier
- Filter results by tier
- Statistics by tier

### Tier Examples

**Example 1: Register Tier A Tag**
```typescript
await registry.registerTag(
  'plix://db/table/users',
  { type: 'database_table', ... },
  'A',  // Authority tier A
  'agent-aether'
);
// Requires: Tier A or higher to modify/rename
```

**Example 2: Rename Tier A Tag**
```typescript
// Requires: Tier A or higher
await registry.renameTag(
  'plix://db/table/users_old',
  'plix://db/table/users',
  'A',  // Must be A or higher
  'agent-aether',
  'Standardizing naming'
);
```

**Example 3: Query by Tier**
```typescript
const tierATags = await registry.queryTags({
  authorityTier: 'A',
  limit: 100
});
// Returns: All tags with authority tier A
```

---

## Section 15.6: Tag Lifecycle Examples

### Complete Lifecycle: Registration → Usage → Rename → Deprecation

**Phase 1: Registration**
```typescript
// Register new tag
const tag = await registry.registerTag(
  'plix://db/table/users_v1',
  { type: 'database_table', schema: 'public', name: 'users_v1' },
  'A',
  'agent-aether',
  { version: '1.0.0' }
);
// Status: Registered, ready for use
```

**Phase 2: Usage**
```typescript
// Use tag in PLIx contract
const contract = {
  entity: 'plix://db/table/users_v1',
  action: 'migrate',
  ...
};

// Resolve tag
const resolved = await registry.resolveTag('plix://db/table/users_v1');
// Returns: TagDefinition with resolved data
```

**Phase 3: Rename**
```typescript
// Rename tag (standardizing naming)
const rename = await registry.renameTag(
  'plix://db/table/users_v1',
  'plix://db/table/users',
  'A',
  'agent-aether',
  'Standardizing naming convention'
);

// Dependents acknowledge
await registry.acknowledgeRename('plix://db/table/users_v1', 
  'plix://contract/migration_v1', 'agent-aether');

// Rename completes
// Status: 'completed'
```

**Phase 4: Deprecation**
```typescript
// Query rename history
const history = registry.getRenameHistory('plix://db/table/users');
// Returns: History showing rename from users_v1 → users

// Old tag still resolves (redirects to new tag)
const oldTag = await registry.resolveTag('plix://db/table/users_v1');
// Returns: TagDefinition for 'plix://db/table/users' (redirected)
```

### Real-World Scenarios

**Scenario 1: Database Schema Evolution**
```typescript
// Register initial schema
await registry.registerTag('plix://db/schema/v1', {...}, 'A', ...);

// Schema evolves → Register new version
await registry.registerTag('plix://db/schema/v2', {...}, 'A', ...);

// Rename old schema (deprecation)
await registry.renameTag('plix://db/schema/v1', 'plix://db/schema/v1_deprecated', 
  'A', ..., 'Deprecated in favor of v2');
```

**Scenario 2: Tool Capability Migration**
```typescript
// Register old tool
await registry.registerTag('plix://tool/mcp/pg.migrate_v1', {...}, 'B', ...);

// Register new tool
await registry.registerTag('plix://tool/mcp/pg.migrate_v2', {...}, 'B', ...);

// Rename old tool (migration)
await registry.renameTag('plix://tool/mcp/pg.migrate_v1', 
  'plix://tool/mcp/pg.migrate_v1_deprecated', 'B', ..., 
  'Migrated to v2, use v2 instead');
```

**Scenario 3: Namespace Reorganization**
```typescript
// Register tags in old namespace
await registry.registerTag('plix://old/db/users', {...}, 'A', ...);
await registry.registerTag('plix://old/db/posts', {...}, 'A', ...);

// Reorganize namespace
await registry.renameTag('plix://old/db/users', 'plix://db/table/users', 
  'A', ..., 'Namespace reorganization');
await registry.renameTag('plix://old/db/posts', 'plix://db/table/posts', 
  'A', ..., 'Namespace reorganization');
```

---

## Chapter 15 Summary

The Tag Registry manages the complete lifecycle of PLIx tags:

1. **Tag Registration:** Register tags with authority tiers and metadata
2. **Tag Resolution:** Multi-source lookup with caching and rename handling
3. **Tag Queries:** Query tags by namespace, path, tier, date range
4. **Rename Governance:** Controlled renaming with dependent tracking
5. **Authority Tier System:** Tier-based authorization for operations

**Key Takeaways:**
1. **Registration:** Tags must be registered before use, with appropriate authority tiers
2. **Resolution:** Multi-source lookup ensures tags can always be resolved
3. **Queries:** Powerful query capabilities enable tag discovery and filtering
4. **Rename Governance:** Controlled renaming prevents breaking changes
5. **Authority Tiers:** Tier-based authorization ensures proper governance

**Next:** Chapter 16 explores PLIX parser implementation—how to parse Human-PLIX, Canonical JSON, and S-form into executable contracts.

---

**Word Count:** ~3,200 words  
**Status:** ✅ **COMPLETE**  
**Cross-References:**
- Chapter 5: Tag System (foundation)
- Chapter 20: PLIX-to-AIP Compiler (tag resolution in compiler)
- Spec Section 2.1: Tag System
- Spec Section 7.3: Registry API

