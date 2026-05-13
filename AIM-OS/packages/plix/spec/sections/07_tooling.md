# Section 7: Tooling and Implementation

**Status:** ✅ **EXTRACTED FROM PHASE 1-4 DOCSTRINGS**  
**Source:** Phase 1-4 Implementation Files  
**Last Updated:** 2025-01-27

---

## **7.1 Parser API**

### **PLIXParser Class**

**Constructor:**
```typescript
constructor(options?: ParseOptions)
```

**Options:**
- `allowDelimiters?: boolean` - Support optional delimiters (`{}`) for deep nesting (default: `true`)
- `strict?: boolean` - Strict mode - fail on unknown constructs (default: `false`)
- `tagRegistry?: Map<string, any>` - Tag registry for resolving tags

**Methods:**

#### **`parse(text: string): ParseResult`**

Parse Human-PLIX text into PLIxIntent.

**Parameters:**
- `text: string` - Human-PLIX text (or S-form if starts with `(`)

**Returns:**
- `ParseResult`:
  - `intent: PLIxIntent | null` - Parsed PLIX intent
  - `errors: ParseError[]` - Parse errors
  - `warnings: ParseError[]` - Warnings (non-fatal issues)

**Example:**
```typescript
const parser = new PLIXParser();
const result = parser.parse(`
ensure ent:plix://db/table/users
  act:create
  pre:
    con:user_not_exists == true
  post:
    con:user_created == true
`);

if (result.intent) {
  console.log('Parsed intent:', result.intent.intent);
} else {
  console.error('Parse errors:', result.errors);
}
```

#### **`validateTag(tag: string): boolean`**

Validate PLIX tag format.

**Parameters:**
- `tag: string` - Tag to validate (format: `plix://namespace/path#rev@hash`)

**Returns:**
- `boolean` - True if tag format is valid

**Example:**
```typescript
parser.validateTag('plix://db/table/users#rev@h_98fa'); // true
parser.validateTag('http://example.com/tag'); // false
```

#### **`detectDanglingReferences(intent: PLIxIntent): string[]`**

Detect dangling references in plan (steps that reference non-existent steps).

**Parameters:**
- `intent: PLIxIntent` - Intent to check

**Returns:**
- `string[]` - Array of error messages for dangling references

**Example:**
```typescript
const errors = parser.detectDanglingReferences(intent);
if (errors.length > 0) {
  console.error('Dangling references:', errors);
}
```

#### **`checkCircularDependencies(intent: PLIxIntent): boolean`**

Check for circular dependencies in plan dependency graph.

**Parameters:**
- `intent: PLIxIntent` - Intent to check

**Returns:**
- `boolean` - True if circular dependencies detected

**Example:**
```typescript
if (parser.checkCircularDependencies(intent)) {
  console.error('Circular dependencies detected!');
}
```

### **RoundTripConverter Class**

**Methods:**

#### **`jsonToHuman(intent: PLIxIntent): string`**

Convert Canonical JSON-PLIX to Human-PLIX format.

**Parameters:**
- `intent: PLIxIntent` - Canonical JSON intent

**Returns:**
- `string` - Human-PLIX formatted string

**Example:**
```typescript
const human = RoundTripConverter.jsonToHuman(intent);
console.log(human);
```

#### **`jsonToSForm(intent: PLIxIntent): string`**

Convert Canonical JSON-PLIX to S-form format.

**Parameters:**
- `intent: PLIxIntent` - Canonical JSON intent

**Returns:**
- `string` - S-form formatted string

**Example:**
```typescript
const sform = RoundTripConverter.jsonToSForm(intent);
console.log(sform);
```

#### **`sFormToJSON(sForm: string): PLIxIntent`**

Convert S-form to Canonical JSON-PLIX.

**Parameters:**
- `sForm: string` - S-form string

**Returns:**
- `PLIxIntent` - Canonical JSON intent

**Example:**
```typescript
const intent = RoundTripConverter.sFormToJSON('(intent "Book room" ...)');
```

---

## **7.2 Compiler API**

### **PLIXToAIPCompiler Class**

**Constructor:**
```typescript
constructor(options?: {
  hhniClient?: any;
  segClient?: any;
  cmcClient?: any;
  tagRegistry?: PLIXTagRegistry;
})
```

**Methods:**

#### **`compileToAIPGraph(intent: PLIxIntent): Promise<AIPGraph>`**

Compile PLIX intent to AIP graph structure.

**Parameters:**
- `intent: PLIxIntent` - PLIX intent to compile

**Returns:**
- `Promise<AIPGraph>`:
  - `nodes: AIPGraphNode[]` - Graph nodes (entity, action, capability, constraint, test, evidence)
  - `edges: AIPGraphEdge[]` - Graph edges (depends_on, compensates, requires, produces, validates)
  - `metadata?: Record<string, any>` - Compilation metadata

**Example:**
```typescript
const compiler = new PLIXToAIPCompiler({ tagRegistry });
const graph = await compiler.compileToAIPGraph(intent);
console.log('AIP Graph nodes:', graph.nodes.length);
console.log('AIP Graph edges:', graph.edges.length);
```

#### **`resolveTag(tag: string): Promise<TagResolutionResult>`**

Resolve tag via Tag Registry (preferred) or HHNI/SEG/CMC.

**Parameters:**
- `tag: string` - Tag to resolve

**Returns:**
- `Promise<TagResolutionResult>`:
  - `tag: string` - Original tag
  - `resolved: any | null` - Resolved entity/action/capability
  - `source: 'hhni' | 'seg' | 'cmc' | 'cache' | 'not_found'` - Resolution source
  - `confidence: number` - Resolution confidence (0-1)
  - `metadata?: Record<string, any>` - Resolution metadata

**Resolution Priority:**
1. Cache (fastest)
2. Tag Registry (authoritative)
3. HHNI (semantic search)
4. SEG (evidence/lineage)
5. CMC (general lookup)

**Example:**
```typescript
const result = await compiler.resolveTag('plix://db/table/users');
if (result.resolved) {
  console.log('Resolved:', result.resolved);
  console.log('Source:', result.source);
  console.log('Confidence:', result.confidence);
}
```

#### **`compileToAPOE(intent: PLIxIntent): Promise<APOECompilationResult>`**

Compile PLIX plan to APOE execution plan format.

**Parameters:**
- `intent: PLIxIntent` - PLIX intent with plan steps

**Returns:**
- `Promise<APOECompilationResult>`:
  - `plan: any` - APOE ExecutionPlan structure
  - `witnessRequirements: VIFWitnessRequirement[]` - VIF witness requirements
  - `resolvedTags: Map<string, any>` - Resolved tags map
  - `errors: string[]` - Compilation errors
  - `warnings: string[]` - Compilation warnings

**Example:**
```typescript
const result = await compiler.compileToAPOE(intent);
if (result.errors.length === 0) {
  console.log('APOE Plan:', result.plan);
  console.log('Witness Requirements:', result.witnessRequirements);
} else {
  console.error('Compilation errors:', result.errors);
}
```

#### **`generateWitnessRequirements(intent: PLIxIntent): VIFWitnessRequirement[]`**

Generate VIF witness requirements for intent execution.

**Parameters:**
- `intent: PLIxIntent` - PLIX intent

**Returns:**
- `VIFWitnessRequirement[]`:
  - `operation: string` - Operation identifier
  - `stepId?: string` - Step ID (if step-level)
  - `requiredConfidence: number` - Required confidence threshold
  - `evidenceTypes: string[]` - Required evidence types
  - `metadata?: Record<string, any>` - Witness metadata

**Example:**
```typescript
const requirements = compiler.generateWitnessRequirements(intent);
for (const req of requirements) {
  console.log(`Operation ${req.operation} requires confidence >= ${req.requiredConfidence}`);
}
```

---

## **7.3 Registry API**

### **PLIXTagRegistry Class**

**Constructor:**
```typescript
constructor(options?: {
  cmcClient?: any;
})
```

**Methods:**

#### **`registerTag(tag: string, resolved: any, authorityTier: AuthorityTier, createdBy: string, metadata?: Record<string, any>): Promise<TagDefinition>`**

Register a new tag in the registry.

**Parameters:**
- `tag: string` - Full tag (format: `plix://namespace/path#rev@hash`)
- `resolved: any` - Resolved entity/action/capability data
- `authorityTier: AuthorityTier` - Authority tier required for operations (`'S' | 'A' | 'B' | 'C'`)
- `createdBy: string` - Creator identifier (agent/user ID)
- `metadata?: Record<string, any>` - Optional metadata

**Returns:**
- `Promise<TagDefinition>` - Registered tag definition

**Example:**
```typescript
const registry = new PLIXTagRegistry({ cmcClient });
const definition = await registry.registerTag(
  'plix://db/table/users#rev@h_98fa',
  { type: 'table', schema: 'public' },
  'A',
  'agent-123'
);
console.log('Registered tag:', definition.tag);
```

#### **`resolveTag(tag: string): Promise<TagDefinition | null>`**

Resolve a tag (with caching and rename handling).

**Parameters:**
- `tag: string` - Tag to resolve

**Returns:**
- `Promise<TagDefinition | null>` - Tag definition or null if not found

**Resolution Process:**
1. Check cache first
2. Check for rename (resolve renamed tag)
3. Check memory store
4. Try CMC if available

**Example:**
```typescript
const definition = await registry.resolveTag('plix://db/table/users');
if (definition) {
  console.log('Resolved:', definition.resolved);
  console.log('Authority tier:', definition.authorityTier);
}
```

#### **`queryTags(query: TagQuery): Promise<TagDefinition[]>`**

Query tags by criteria.

**Parameters:**
- `query: TagQuery`:
  - `namespace?: string` - Filter by namespace
  - `pathPattern?: string` - Filter by path pattern (regex)
  - `revision?: string` - Filter by revision
  - `authorityTier?: AuthorityTier` - Filter by authority tier
  - `dateRange?: { from: string, to: string }` - Filter by date range
  - `limit?: number` - Limit results (default: 100)
  - `offset?: number` - Offset for pagination (default: 0)

**Returns:**
- `Promise<TagDefinition[]>` - Matching tag definitions

**Example:**
```typescript
const tags = await registry.queryTags({
  namespace: 'db',
  authorityTier: 'A',
  limit: 10
});
console.log(`Found ${tags.length} tags`);
```

#### **`renameTag(fromTag: string, toTag: string, authorityTier: AuthorityTier, renamedBy: string, reason?: string): Promise<TagRename>`**

Rename a tag (with governance).

**Parameters:**
- `fromTag: string` - Original tag
- `toTag: string` - New tag
- `authorityTier: AuthorityTier` - Authority tier of renamer
- `renamedBy: string` - Renamer identifier
- `reason?: string` - Reason for rename

**Returns:**
- `Promise<TagRename>` - Rename record

**Governance:**
- Verifies tag exists
- Validates authority tier is sufficient
- Finds dependents (tags that reference this tag)
- Creates rename record with pending status
- Requires all dependents to acknowledge before completion

**Example:**
```typescript
const rename = await registry.renameTag(
  'plix://db/table/users',
  'plix://db/table/users_v2',
  'A',
  'agent-123',
  'Schema migration to v2'
);
console.log('Rename status:', rename.status);
console.log('Dependents:', rename.dependents);
```

#### **`getDependents(tag: string): Promise<string[]>`**

Get tags that depend on a given tag.

**Parameters:**
- `tag: string` - Tag to check

**Returns:**
- `Promise<string[]>` - Array of dependent tag identifiers

**Example:**
```typescript
const dependents = await registry.getDependents('plix://db/table/users');
console.log(`Tag has ${dependents.length} dependents`);
```

#### **`acknowledgeRename(fromTag: string, dependentTag: string, acknowledgedBy: string): Promise<void>`**

Acknowledge a tag rename by a dependent.

**Parameters:**
- `fromTag: string` - Original tag (from rename)
- `dependentTag: string` - Dependent tag identifier
- `acknowledgedBy: string` - Acknowledger identifier

**Example:**
```typescript
await registry.acknowledgeRename(
  'plix://db/table/users',
  'plix://app/schema/users',
  'agent-456'
);
```

#### **`getRenameHistory(tag: string): Promise<TagRename[]>`**

Get rename history for a tag.

**Parameters:**
- `tag: string` - Tag to check

**Returns:**
- `Promise<TagRename[]>` - Array of rename records

**Example:**
```typescript
const history = await registry.getRenameHistory('plix://db/table/users_v2');
console.log(`Tag has ${history.length} rename records`);
```

#### **`getAuthorityTierStats(): Promise<Record<AuthorityTier, number>>`**

Get statistics on tags by authority tier.

**Returns:**
- `Promise<Record<AuthorityTier, number>>` - Count of tags per tier

**Example:**
```typescript
const stats = await registry.getAuthorityTierStats();
console.log('Tags by tier:', stats);
// { S: 5, A: 20, B: 50, C: 100 }
```

#### **`getCacheStats(): { hits: number, misses: number, hitRate: number }`**

Get cache statistics.

**Returns:**
- `{ hits: number, misses: number, hitRate: number }` - Cache statistics

**Example:**
```typescript
const stats = registry.getCacheStats();
console.log(`Cache hit rate: ${(stats.hitRate * 100).toFixed(2)}%`);
```

---

## **7.4 Evolution Framework API**

### **PLIXGGPSystem Class**

**Constructor:**
```typescript
constructor(options?: {
  cmcClient?: any;
  timelineClient?: any;
})
```

**Methods:**

#### **`minePatterns(traces: PLIxIntent[]): Promise<PatternMiningResult>`**

Mine grammar patterns from historical PLIX traces.

**Parameters:**
- `traces: PLIxIntent[]` - Historical PLIX intent traces

**Returns:**
- `Promise<PatternMiningResult>`:
  - `patterns: GrammarPattern[]` - Discovered patterns
  - `confidence: number` - Overall confidence score (0-1)
  - `recommendations: string[]` - Recommendations for GGP proposals
  - `metadata?: Record<string, any>` - Mining metadata

**Pattern Mining:**
- Extracts constraint patterns (operators, types)
- Extracts plan step patterns (retry, compensation, errors, dependencies)
- Calculates frequency and confidence
- Only includes patterns seen in ≥10% of traces

**Example:**
```typescript
const ggpSystem = new PLIXGGPSystem();
const result = await ggpSystem.minePatterns(historicalTraces);
console.log(`Discovered ${result.patterns.length} patterns`);
console.log('Recommendations:', result.recommendations);
```

#### **`defineGGP(pattern: GrammarPattern, rationale: { problem: string, solution: string, benefits: string[], risks: string[] }, deprecationProof: DeprecationProof, authorityQuorum: { tier: AuthorityTier, required: number }, createdBy: string): Promise<GGPProposal>`**

Define a new GGP proposal.

**Parameters:**
- `pattern: GrammarPattern` - Proposed grammar pattern
- `rationale: { problem, solution, benefits, risks }` - Proposal rationale
- `deprecationProof: DeprecationProof` - Deprecation proof with conformance tests
- `authorityQuorum: { tier, required }` - Authority quorum requirements
- `createdBy: string` - Creator identifier

**Returns:**
- `Promise<GGPProposal>` - GGP proposal record

**Example:**
```typescript
const proposal = await ggpSystem.defineGGP(
  pattern,
  {
    problem: 'Current constraint syntax is verbose',
    solution: 'Add shorthand syntax for common constraints',
    benefits: ['Reduced verbosity', 'Improved readability'],
    risks: ['Breaking changes', 'Migration effort']
  },
  deprecationProof,
  { tier: 'A', required: 3 },
  'agent-123'
);
console.log('GGP Proposal ID:', proposal.id);
```

#### **`validateDeprecationProof(proof: DeprecationProof): Promise<{ valid: boolean, errors: string[] }>`**

Validate deprecation proof using conformance tests.

**Parameters:**
- `proof: DeprecationProof` - Deprecation proof to validate

**Returns:**
- `Promise<{ valid: boolean, errors: string[] }>` - Validation result

**Validation:**
- Runs conformance test suite
- Checks backward compatibility
- Validates migration guide
- Returns validation status

**Example:**
```typescript
const validation = await ggpSystem.validateDeprecationProof(deprecationProof);
if (validation.valid) {
  console.log('Deprecation proof validated');
} else {
  console.error('Validation errors:', validation.errors);
}
```

#### **`approveGGP(ggpId: string, authority: string, tier: AuthorityTier, comment?: string): Promise<GGPProposal>`**

Approve a GGP proposal (requires authority quorum).

**Parameters:**
- `ggpId: string` - GGP proposal ID
- `authority: string` - Approver identifier
- `tier: AuthorityTier` - Approver authority tier
- `comment?: string` - Optional approval comment

**Returns:**
- `Promise<GGPProposal>` - Updated GGP proposal

**Approval Process:**
- Validates approver has sufficient tier
- Adds approval to quorum
- Checks if quorum is met
- If quorum met, updates status to 'approved' and integrates with AIM-OS governance

**Example:**
```typescript
const updated = await ggpSystem.approveGGP(
  'GGP-001',
  'agent-456',
  'A',
  'Looks good, approved'
);
console.log('Approval status:', updated.status);
console.log('Approvals:', updated.authorityQuorum.approvals);
```

#### **`getGGPStatus(ggpId: string): Promise<GGPStatus>`**

Get status of a GGP proposal.

**Parameters:**
- `ggpId: string` - GGP proposal ID

**Returns:**
- `Promise<GGPStatus>` - Status (`'draft' | 'proposed' | 'review' | 'approved' | 'rejected' | 'deprecated'`)

**Example:**
```typescript
const status = await ggpSystem.getGGPStatus('GGP-001');
console.log('GGP Status:', status);
```

#### **`getApprovedGGPs(): Promise<GGPProposal[]>`**

Get list of approved GGP proposals.

**Returns:**
- `Promise<GGPProposal[]>` - Array of approved GGP proposals

**Example:**
```typescript
const approved = await ggpSystem.getApprovedGGPs();
console.log(`Found ${approved.length} approved GGPs`);
```

---

## **7.5 Security Notes**

### **Tag Resolution Security**

**Authority Tier Validation:**
- Tag resolution validates authority tier before returning sensitive data
- Higher-tier tags require higher-tier authorization
- Insufficient tier → escalation or rejection

**Cache Security:**
- Tag cache is in-memory only (not persisted)
- Cache entries expire after TTL (configurable)
- Sensitive data not cached

### **GGP Approval Security**

**Authority Quorum:**
- GGP proposals require tier-based quorum
- Higher-tier proposals require more approvals
- Quorum prevents single-authority abuse

**Deprecation Proof Validation:**
- Deprecation proofs must pass conformance tests
- Backward compatibility checks prevent breaking changes
- Migration guides ensure smooth transitions

### **Input Validation**

**Parser Security:**
- Parser validates all input before processing
- Malformed input rejected with clear error messages
- No code injection vulnerabilities (parser is pure)

**Compiler Security:**
- Compiler validates all tags before resolution
- Unresolved tags fail compilation (no fallback to unsafe execution)
- Witness requirements ensure verifiable execution

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 8: Appendices/Reference Sections](./08_appendices.md)

