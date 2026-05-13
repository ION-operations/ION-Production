# AI Chat System Enhancement: Significance Scoring & Typed Relationships

**Created:** 2025-01-27  
**Status:** Design Analysis - Integration Assessment  
**Purpose:** Document current system and analyze proposed enhancement for significance scoring, typed relationships, and deterministic retrieval

---

## 📋 **TABLE OF CONTENTS**

1. [Current System Architecture](#current-system-architecture)
2. [Proposed Enhancement](#proposed-enhancement)
3. [Integration Analysis](#integration-analysis)
4. [Migration Strategy](#migration-strategy)
5. [Implementation Plan](#implementation-plan)

---

## 🏗️ **CURRENT SYSTEM ARCHITECTURE**

### **1. Message Structure**

The current `ChatMessage` interface includes:

```typescript
interface ChatMessage {
  id: string
  timestamp: Date
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
  agent_id?: string
  confidence?: number
  
  // Work Attribution
  work_references?: {
    files?: Array<{ path: string; operation: string; lines?: number[] }>
    cmc_atoms?: string[]
    vif_witnesses?: string[]
    goals?: string[]
    timeline_entries?: string[]
    git_commits?: string[]
  }
  
  // Evidence & Confidence
  evidence_trail?: {
    cmc_atom_id?: string
    vif_witness_id?: string
    supporting_files?: string[]
  }
  
  // Goal Alignment
  goal_alignment?: {
    objective?: string
    key_result?: string
    progress?: number
  }
  
  // Communication Context
  message_type?: 'discussion' | 'task_handoff' | 'problem_solving' | 'status_update' | 'urgent'
  thread_id?: string
  
  // Tool Calls
  tool_calls?: ToolCall[]
  
  // Cross-Channel Collaboration
  connected_channel?: string
  ping_context?: { from_channel: string; reason: string }
  
  metadata?: Record<string, any>
}
```

### **2. Current Features**

**✅ Implemented:**
- Discord-style channel organization (UI, Backend, Frontend, Infrastructure)
- Expandable sections (Researching, Documenting, Building, Debugging)
- Work references display (files, CMC atoms, goals, timeline entries)
- Evidence trail visualization
- Goal alignment display
- Tool call display (MCP tools with status, arguments, results)
- Cross-channel collaboration (ping/connect/disconnect)
- Expandable message details (compact by default, expand for full details)
- Collapsible sidebar (icon-only view)

**❌ Not Yet Implemented:**
- Significance scoring
- Typed relationships between messages
- Deterministic retrieval based on structured queries
- Context usage tracking (tokens, agents, reasons)
- Heatmap visualization
- Context overrides (pins, forced levels, priority)

### **3. Current Storage**

- **State Management:** React `useState` (in-memory, per-session)
- **Persistence:** None (mock data only)
- **Retrieval:** Simple array filtering by channel
- **Context Selection:** Not implemented (all messages shown)

### **4. Current Limitations**

1. **No Significance Scoring:** All messages treated equally
2. **No Relationship Tracking:** Messages don't reference each other structurally
3. **No Context Budget:** No token limits or selective retrieval
4. **No Usage Tracking:** Can't see which messages are most valuable
5. **No Deterministic Retrieval:** No structured query system
6. **No Overrides:** Can't pin, prioritize, or force levels

---

## 🚀 **PROPOSED ENHANCEMENT**

### **1. Summary Atom Structure**

Transform messages into **first-class structured objects** with precomputed significance and relationships:

```typescript
type SummaryAtom = {
  id: string                     // ULID/hash (from message.id)
  level: "micro"|"meso"|"macro" // Granularity level
  
  // Message metadata
  title: string                  // Canonical, terse title
  turn: [number, number]         // Turn range covered [t0, t1]
  recap: string                  // Natural-language recap (from message.content)
  updatedAt: string              // ISO timestamp
  
  // Structured claims (extracted from message)
  claims: Array<{
    id: string
    text: string
    kind: "decision"|"fact"|"hypothesis"|"task"
    objects: string[]            // Symbols/files/APIs (from work_references)
    evidence: string[]           // SEG ids (from evidence_trail)
    quality: {
      conf: number               // From message.confidence
      tests?: number             // From work_references (test files)
      gates?: string[]           // From VIF witnesses
    }
  }>
  
  // Significance (precomputed!)
  sig: {
    score: number                // Bounded [0,1] composite score
    breakdown: {
      usage: number              // Opens, clicks, references, agent-loads
      impact: number             // Tests added, bugs fixed, perf gain
      novelty: number            // New symbols/edges introduced
      recency: number            // Exponential decay
      pins: number               // User pins (0 or 1)
    }
    halfLifeDays: number         // Decay control
  }
  
  // Typed relations to other atoms
  rel: Array<{
    to: string                   // Other atom id
    type: "supports"|"contradicts"|"depends_on"|"alternative_to"|"duplicates"|"resolves"
    strength: number             // [0,1] cosine similarity × confidence
    objects?: string[]           // Overlapping symbols
  }>
}
```

### **2. Significance Scoring Formula**

**Fixed formula with learnable weights:**

```typescript
sig.score = σ(
  0.40 * usage        // Opens, clicks, pins, references, agent-loads
+ 0.25 * impact       // Tests added, bugs fixed, perf gain, $$ saved
+ 0.20 * novelty      // New symbols/edges introduced
+ 0.10 * recency      // Exponential decay with halfLifeDays
+ 0.05 * pins         // User pin or governance mark
)
```

**Where:**
- **usage**: Normalized log counts (from message views, agent references)
- **impact**: From VIF/SEG (test deltas, incident resolved, from `work_references`)
- **novelty**: Jaccard distance of symbols vs. prior atoms (from `work_references.files`)
- **recency**: `exp(-Δt/τ)` where τ = `halfLifeDays`
- **pins**: 1.0 if pinned else 0 (user override)

### **3. Relationship Typing**

**At write-time, extract relationships:**

1. **Extract symbols** from `work_references.files`, `work_references.cmc_atoms`
2. **Compare to neighbors** (last K atoms in same channel/domain)
3. **Assign edges** based on patterns:
   - Same symbols + opposite polarity → `contradicts`
   - Same goal + different approach → `alternative_to`
   - References as justification → `supports`
   - Code change unblocks task → `resolves`
   - Shared pre-reqs → `depends_on`
   - High text+symbol overlap → `duplicates`

**Edge strength** = cosine(similarity) × confidence

### **4. Deterministic Retrieval**

**Query plan from user prompt:**

```typescript
type Need = {
  kind: "decision"|"fact"|"task"
  objects: string[]
  mustInclude?: string[]
}

function assemble(query: string, needs: Need[], budget: Tokens) {
  const qSymbols = hhni.extractSymbols(query)
  const seed = hhni.lookup(qSymbols, query, {k:128})  // Vector + symbolic
  
  const scored = seed.map(a => ({
    atom: a,
    score:
      0.45 * a.sig.score +
      0.25 * similarity(a, qSymbols) +
      0.15 * relationBoost(a, needs) +
      0.10 * recency(a) +
      0.05 * pinBoost(a)
  }))
  
  const picked = diversify(scored, {
    by: "rel.type|objects",
    minKinds: needs.map(n => n.kind)
  })
  
  return packToBudget(picked, budget, {
    prefer: ["micro","meso"],
    includeRawForPins: true
  })
}
```

**Features:**
- **relationBoost**: + if atom `supports/depends_on` requested objects; − if `contradicts` (unless reviewing contradictions)
- **diversify**: Ensure coverage of **kinds** (`decision/fact/task`) and **objects**; avoid duplicates
- **packToBudget**: Greedy pack; favor micro/meso, then pull **raw** only for pins

### **5. Context Usage Tracking**

**Track which atoms are used by which agents:**

```typescript
type ContextUse = {
  agent: "coding"|"planning"|`tool:${string}`
  level: "macro"|"meso"|"micro"|"raw"
  tokens: number
  reasons: Array<"recency"|"semantic"|"symbolic"|"pin"|"dependency">
  score: number  // Per-agent selection score
}

type MessageContextInfo = {
  id: string
  turn: number
  included: boolean               // Included in ANY agent's pack this turn
  totalTokensInPack: number      // Sum across agents
  significance: number            // Precomputed sig.score
  relations: Array<{
    to: string
    type: "supports"|"depends_on"|"contradicts"
    strength: number
  }>
  uses: ContextUse[]
}
```

### **6. Context Overrides**

**User/agent overrides (persist in CMC):**

```typescript
type ContextOverride = {
  id: string
  pinned?: boolean
  forcedLevel?: "macro"|"meso"|"micro"|"raw"
  priority?: number  // -1..+1 (salience delta)
  ttlTurns?: number  // Optional decay window
}
```

**Scoring with overrides:**

```typescript
function finalScore(base: number, o?: ContextOverride) {
  const pinBoost = o?.pinned ? 0.08 : 0.0
  const prioBoost = clamp(o?.priority ?? 0, -1, 1) * 0.10
  return clamp01(base + pinBoost + prioBoost)
}
```

### **7. Heatmap UI Components**

**Three views:**

1. **Inline Heat Badge** (on each message bubble)
   - Shows inclusion, tokens, current level, quick actions
   - Pin, promote, force level, adjust priority

2. **Chat Heatmap Panel** (grid/timeline + brush adjust)
   - Shows conversation as scrollable grid (x: turn, y: agent/level)
   - Each cell colored by inclusion strength
   - Brush-select multiple bubbles, apply priority/pin

3. **Context Ledger** (bottom drawer)
   - Budget bar: `Total 12k • Used 9.4k • Free 2.6k`
   - Sortable table: item, level, tokens, agent, reasons, score
   - Batch actions: demote, unpin, clear priorities

---

## 🔗 **INTEGRATION ANALYSIS**

### **1. Message → SummaryAtom Mapping**

**Current message fields map directly:**

| Current Field | SummaryAtom Field | Notes |
|--------------|-------------------|-------|
| `id` | `id` | Direct mapping |
| `timestamp` | `updatedAt`, `turn` | Convert to ISO, calculate turn range |
| `content` | `recap` | Use as natural-language recap |
| `confidence` | `claims[].quality.conf` | Extract from message |
| `work_references.files` | `claims[].objects` | Extract file paths |
| `work_references.cmc_atoms` | `claims[].evidence` | Map to SEG ids |
| `work_references.goals` | `claims[].objects` | Include goal IDs |
| `evidence_trail.cmc_atom_id` | `claims[].evidence` | Direct mapping |
| `goal_alignment.objective` | `claims[].kind="task"` | Classify as task |
| `tool_calls` | `sig.breakdown.usage` | Count tool calls as usage |

**New fields to compute:**
- `level`: Determine from message length, complexity, scope
- `claims`: Extract structured claims from `content` + `work_references`
- `sig`: Compute from usage, impact, novelty, recency, pins
- `rel`: Compute by comparing to other messages in same channel

### **2. Significance Scoring Integration**

**Data sources from current system:**

1. **Usage** (0.40 weight):
   - Message views (track in UI)
   - Agent references (from `agent_id` in messages)
   - Tool calls (from `tool_calls` array)
   - Cross-channel connections (from `connected_channel`)

2. **Impact** (0.25 weight):
   - Tests added (from `work_references.files` with test files)
   - Bugs fixed (from `work_references` with bug-related files)
   - Performance gains (from `work_references` with perf-related files)
   - Goal progress (from `goal_alignment.progress`)

3. **Novelty** (0.20 weight):
   - New symbols (from `work_references.files` not seen before)
   - New edges (from `rel` array)
   - New CMC atoms (from `work_references.cmc_atoms`)

4. **Recency** (0.10 weight):
   - Exponential decay from `timestamp`
   - Configurable `halfLifeDays` (default: 30 days)

5. **Pins** (0.05 weight):
   - User override (new feature)

### **3. Relationship Extraction**

**From current message structure:**

1. **Extract symbols:**
   - File paths from `work_references.files`
   - CMC atom IDs from `work_references.cmc_atoms`
   - Goal IDs from `work_references.goals`
   - Function/API names from `work_references` (if parsed)

2. **Compare to neighbors:**
   - Same channel messages (from channel organization)
   - Same thread messages (from `thread_id`)
   - Connected channel messages (from `connected_channel`)

3. **Assign relationship types:**
   - **supports**: Same goal, same approach, references as justification
   - **contradicts**: Same symbols, opposite decisions (from `message_type`)
   - **depends_on**: References same files/atoms, earlier timestamp
   - **alternative_to**: Same goal, different approach
   - **resolves**: Code change unblocks task (from `work_references.files`)
   - **duplicates**: High text+symbol overlap

### **4. Deterministic Retrieval Integration**

**Query needs from current system:**

1. **Agent context** (from `agent_id`):
   - Filter by agent's recent work
   - Prioritize agent's own messages
   - Include agent's dependencies

2. **Channel context** (from channel organization):
   - Filter by channel (UI, Backend, Frontend, Infrastructure)
   - Filter by section (Researching, Documenting, Building, Debugging)

3. **Goal context** (from `goal_alignment`):
   - Filter by objective/key result
   - Prioritize messages with goal alignment

4. **Thread context** (from `thread_id`):
   - Include thread messages
   - Prioritize thread root

### **5. Context Usage Tracking Integration**

**Track usage from current system:**

1. **Agent usage** (from `agent_id`):
   - Track which agents reference which messages
   - Count tool calls per agent
   - Track agent loads (when agent opens channel)

2. **Token usage**:
   - Calculate tokens from `content` length
   - Track per-agent token usage
   - Track per-level token usage (micro/meso/macro/raw)

3. **Inclusion reasons**:
   - **recency**: Message is recent
   - **semantic**: Semantic similarity to query
   - **symbolic**: Symbol overlap with query
   - **pin**: User pinned message
   - **dependency**: Message is dependency of selected message

### **6. UI Integration Points**

**Current UI components can be enhanced:**

1. **Message Display** (`AIChatManagement.tsx`):
   - Add `MessageContextBadge` component
   - Show heat badge on each message
   - Add pin/priority controls

2. **Channel Sidebar**:
   - Show heat indicators on channels
   - Show context usage per channel

3. **Right Panel**:
   - Add "Context Heatmap" tab
   - Show grid visualization
   - Add brush selection

4. **Bottom Panel**:
   - Add "Context Ledger" tab
   - Show budget, tokens, reasons
   - Add batch actions

---

## 🔄 **MIGRATION STRATEGY**

### **Phase 1: Data Model Enhancement (Non-Breaking)**

**Goal:** Add new fields to existing `ChatMessage` without breaking current UI

1. **Extend `ChatMessage` interface:**
   ```typescript
   interface ChatMessage {
     // ... existing fields ...
     
     // New fields (optional for backward compatibility)
     summary_atom?: SummaryAtom
     context_info?: MessageContextInfo
     override?: ContextOverride
   }
   ```

2. **Add significance computation:**
   - Compute `sig` from existing message data
   - Store in `summary_atom.sig`
   - Update on message view/agent reference

3. **Add relationship extraction:**
   - Compute `rel` by comparing messages
   - Store in `summary_atom.rel`
   - Update when new messages added

### **Phase 2: Retrieval System (Backend)**

**Goal:** Implement deterministic retrieval without changing UI

1. **Create `assemble()` function:**
   - Accept query, needs, budget
   - Return selected atom IDs
   - Log selection reasons

2. **Add context usage tracking:**
   - Track which messages are selected
   - Store in `MessageContextInfo`
   - Update on each retrieval

3. **Add override system:**
   - Store `ContextOverride` in CMC
   - Apply overrides in `assemble()`
   - Persist across sessions

### **Phase 3: UI Components (Progressive Enhancement)**

**Goal:** Add heatmap UI without breaking existing features

1. **Add `MessageContextBadge`:**
   - Show on each message (optional, can be hidden)
   - Display inclusion, tokens, level
   - Add pin/priority controls

2. **Add `ChatHeatmapPanel`:**
   - New tab in right panel
   - Show grid visualization
   - Add brush selection

3. **Add `ContextLedger`:**
   - New tab in bottom panel
   - Show budget, tokens, reasons
   - Add batch actions

### **Phase 4: Integration (Full System)**

**Goal:** Connect retrieval system to UI

1. **Wire retrieval to message display:**
   - Use `assemble()` to select messages
   - Show only selected messages (with option to show all)
   - Highlight selected messages

2. **Wire overrides to retrieval:**
   - Apply user overrides in `assemble()`
   - Update UI on override change
   - Persist overrides in CMC

3. **Wire heatmap to retrieval:**
   - Show selection in heatmap
   - Allow brush selection to set overrides
   - Update retrieval on override change

---

## 📋 **IMPLEMENTATION PLAN**

### **Step 1: Data Model (Week 1)**

- [ ] Define `SummaryAtom` type
- [ ] Define `MessageContextInfo` type
- [ ] Define `ContextOverride` type
- [ ] Extend `ChatMessage` interface
- [ ] Create migration function: `messageToSummaryAtom()`

### **Step 2: Significance Scoring (Week 1-2)**

- [ ] Implement `computeSignificance()` function
- [ ] Track usage metrics (views, references, tool calls)
- [ ] Compute impact from work references
- [ ] Compute novelty from symbol overlap
- [ ] Implement recency decay
- [ ] Add pin tracking

### **Step 3: Relationship Extraction (Week 2)**

- [ ] Implement `extractSymbols()` function
- [ ] Implement `compareMessages()` function
- [ ] Implement `assignRelationships()` function
- [ ] Compute relationship strength
- [ ] Store relationships in `SummaryAtom.rel`

### **Step 4: Deterministic Retrieval (Week 2-3)**

- [ ] Implement `assemble()` function
- [ ] Implement `diversify()` function
- [ ] Implement `packToBudget()` function
- [ ] Add query parsing (extract needs)
- [ ] Add HHNI integration (symbol extraction)

### **Step 5: Context Usage Tracking (Week 3)**

- [ ] Implement `ContextUse` tracking
- [ ] Track per-agent usage
- [ ] Track per-level usage
- [ ] Track inclusion reasons
- [ ] Store in `MessageContextInfo`

### **Step 6: Override System (Week 3-4)**

- [ ] Implement `ContextOverride` storage (CMC)
- [ ] Implement `applyOverride()` function
- [ ] Implement `finalScore()` function
- [ ] Add override persistence
- [ ] Add override TTL

### **Step 7: UI Components (Week 4-5)**

- [ ] Create `MessageContextBadge` component
- [ ] Create `ChatHeatmapPanel` component
- [ ] Create `ContextLedger` component
- [ ] Add heatmap visualization (canvas)
- [ ] Add brush selection

### **Step 8: Integration (Week 5-6)**

- [ ] Wire retrieval to message display
- [ ] Wire overrides to retrieval
- [ ] Wire heatmap to retrieval
- [ ] Add UI controls (pin, priority, level)
- [ ] Add batch actions

### **Step 9: Testing (Week 6)**

- [ ] Test significance scoring accuracy
- [ ] Test relationship extraction
- [ ] Test deterministic retrieval
- [ ] Test override system
- [ ] Test UI components
- [ ] Test integration

### **Step 10: Documentation (Week 6)**

- [ ] Document API
- [ ] Document UI components
- [ ] Document migration process
- [ ] Document usage patterns

---

## ✅ **COMPATIBILITY ASSESSMENT**

### **✅ Fully Compatible**

1. **Message Structure:** Can extend without breaking existing UI
2. **Channel Organization:** Works with existing channel system
3. **Work References:** Can feed into significance scoring
4. **Evidence Trails:** Can inform relationships
5. **Tool Calls:** Can contribute to usage metrics
6. **Goal Alignment:** Can inform impact scoring

### **⚠️ Requires Migration**

1. **Storage:** Need to migrate from in-memory to CMC persistence
2. **Retrieval:** Need to replace simple filtering with `assemble()`
3. **UI:** Need to add new components (backward compatible)

### **❌ Potential Conflicts**

1. **Message Display:** Current "show all messages" vs. "show selected messages"
   - **Solution:** Add toggle "Show All" / "Show Selected"

2. **Cross-Channel Collaboration:** Current `connected_channel` vs. relationship system
   - **Solution:** Use `connected_channel` to inform `rel` extraction

3. **Thread System:** Current `thread_id` vs. relationship system
   - **Solution:** Use `thread_id` to inform `rel` extraction (thread = `depends_on`)

---

## 🎯 **RECOMMENDATIONS**

### **1. Start with Data Model**

Begin by extending `ChatMessage` with optional `summary_atom` field. This allows gradual migration without breaking existing code.

### **2. Implement Significance Scoring First**

Significance scoring provides immediate value (highlighting important messages) without requiring full retrieval system.

### **3. Add UI Components Progressively**

Add `MessageContextBadge` first (shows value immediately), then `ContextLedger` (shows system working), then `ChatHeatmapPanel` (advanced visualization).

### **4. Keep Backward Compatibility**

Always support "show all messages" mode. Make retrieval optional, not required.

### **5. Test with Real Data**

Use actual message history to test significance scoring and relationship extraction. Mock data may not reveal edge cases.

---

## 📊 **SUCCESS METRICS**

1. **Significance Accuracy:** High-sig messages are actually important (user validation)
2. **Relationship Accuracy:** Extracted relationships match user expectations
3. **Retrieval Quality:** Selected messages cover query needs (coverage test)
4. **Token Efficiency:** Retrieval uses <80% of budget while covering needs
5. **UI Usability:** Users can understand and control context selection
6. **Performance:** Retrieval completes in <100ms for typical queries

---

## 🔗 **RELATED DOCUMENTS**

- `AGENT_CHAT_SYSTEM_DESIGN.md` - Current system design
- `ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx` - Current implementation
- CMC documentation - For persistence
- HHNI documentation - For symbol extraction
- VIF documentation - For evidence trails

---

**Status:** Design Analysis Complete - Ready for Implementation Decision  
**Priority:** HIGH - Significant enhancement to agent collaboration  
**Next Steps:** Review with team, decide on implementation approach, begin Phase 1

