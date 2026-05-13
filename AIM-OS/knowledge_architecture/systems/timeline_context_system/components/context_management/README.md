# Context Management Component

**Purpose:** Adaptive context management with multiple dump strategies for optimal token usage  
**Status:** ✅ Complete implementation  
**File:** `packages/timeline_context_system/adaptive_context_dumping.py`  

## 🎯 **Overview**

The Context Management component provides adaptive context management with multiple dump strategies, balancing context preservation with token costs through intelligent summarization and compression.

## 🔧 **Core Features**

- **Adaptive Context Management** - Monitors context capacity and manages token usage
- **Multiple Dump Strategies** - From full context preservation to perfect summaries
- **Strategic Compression** - Up to 93% space savings while preserving quality
- **Context Quality Metrics** - Measures preservation, compression, and reconstruction accuracy
- **Automatic Management** - Monitors context capacity and dumps before limits
- **Cost Optimization** - Balances context preservation with token costs

## 📊 **Key Classes**

- `AdaptiveContextManager` - Main context management engine
- `DumpStrategy` - Different strategies for context dumping
- `CompressedContext` - Compressed context with quality metrics
- `ContextStatus` - Current context capacity and usage status
- `ContextQualityMetrics` - Quality assessment for context operations
- `DumpResult` - Result of context dumping operations

## 🔄 **Integration**

### **CMC Integration** `[CMC-STORAGE]` `[TCS-CMC]`
**Pattern:** Direct storage integration  
**Priority:** P0 (Critical)  
**Purpose:** Context snapshots stored in CMC as atoms with bitemporal tracking

**Implementation:**
- Context snapshots stored as CMC atoms with `modality="tcs_timeline"`
- Bitemporal tracking: Transaction time + valid time preserved
- Atom creation via `cmc.create_atom()` with context snapshot content
- Tags include: `type: "context_snapshot"`, `prompt_id: <id>`, `dump_strategy: <strategy>`

**API Reference:**
- `packages/timeline_context_system/prompt_context_tracker.py` - TimelineMemoryStore class
- `lucid_mcp_server.py` - `add_timeline_entry` tool (MCP interface, includes context snapshots)

**Code Location:**
- `packages/timeline_context_system/prompt_context_tracker.py:TimelineMemoryStore.store_memory()`
- `packages/timeline_context_system/adaptive_context_dumping.py` - Context snapshot creation and storage

---

### **HHNI Integration** `[HHNI-QUERY]` `[TCS-HHNI]`
**Pattern:** Indirect retrieval integration (via CMC)  
**Priority:** P0 (Critical)  
**Purpose:** Temporal context retrieval uses HHNI retrieval subsystem for efficient context queries

**Implementation:**
- **Indirect via CMC:** TCS emits `tcs_timeline` atoms to CMC, HHNI polls and indexes automatically
- HHNI's CMC→HHNI poller (at-least-once, idempotent) detects these atoms and indexes them
- HHNI retrieval then leverages temporal metadata during context selection
- Temporal queries use HHNI's hierarchical index for efficient context retrieval

**Data Flow:**
- TCS context snapshots → CMC atoms (`tcs_timeline`) → HHNI poller → HHNI hierarchical index
- Temporal context queries → HHNI retrieval → Context snapshots with temporal metadata
- Frequently accessed context nodes become available through standard HHNI scoring

**API Reference:**
- MCP Tools: `mcp_lucid-mcp_get_timeline_entries`, `mcp_lucid-mcp_get_timeline_summary`
- HHNI Integration: Indirect via CMC atoms with `modality="tcs_timeline"`

**Documentation:**
- `knowledge_architecture/systems/timeline_context_system/T2_architecture.md` - Integration with HHNI section

---

**Parent System:** [Timeline Context System](../../README.md)  
**Implementation:** [L3 Detailed](../../L3_detailed.md)  
**Code:** `packages/timeline_context_system/adaptive_context_dumping.py`
