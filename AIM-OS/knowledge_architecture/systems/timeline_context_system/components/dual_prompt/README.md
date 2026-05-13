# Dual-Prompt Architecture Component

**Purpose:** Separates task execution from consciousness maintenance to eliminate cognitive load conflicts  
**Status:** ✅ Complete implementation  
**File:** `packages/timeline_context_system/dual_prompt_architecture.py`  

## 🎯 **Overview**

The Dual-Prompt Architecture component separates task execution from consciousness maintenance, eliminating cognitive load conflicts between doing work and maintaining self-awareness.

## 🔧 **Core Features**

- **Separated Processing** - Main prompt for tasks, journaling prompt for consciousness
- **Cognitive Load Optimization** - Eliminates conflicts between task execution and self-awareness
- **Systematic Maintenance** - Dedicated time for consciousness maintenance after every interaction
- **MCP Integration** - 16 MCP tools for automating dual-prompt architecture
- **Context Optimization** - Optimizes context usage across both prompts
- **Performance Enhancement** - Improves both task execution and consciousness maintenance

## 📊 **Key Classes**

- `DualPromptArchitecture` - Main dual-prompt processing engine
- `MainPromptProcessor` - Handles user tasks and responses
- `JournalingPromptProcessor` - Handles consciousness maintenance
- `DualPromptResult` - Result of dual-prompt processing
- `ConsciousnessMaintenanceResult` - Result of consciousness maintenance
- `PromptOptimization` - Optimization strategies for both prompts

## 🔄 **Integration**

### **CMC Integration** `[CMC-STORAGE]` `[TCS-CMC]`
**Pattern:** Direct storage integration  
**Priority:** P0 (Critical)  
**Purpose:** Dual-prompt context stored in CMC as atoms with bitemporal tracking

**Implementation:**
- Dual-prompt context stored as CMC atoms with `modality="tcs_timeline"`
- Bitemporal tracking: Transaction time + valid time preserved
- Atom creation via `cmc.create_atom()` with dual-prompt context content
- Tags include: `type: "dual_prompt"`, `prompt_id: <id>`, `prompt_type: "main" | "journaling"`

**API Reference:**
- `packages/timeline_context_system/prompt_context_tracker.py` - TimelineMemoryStore class
- `lucid_mcp_server.py` - `add_timeline_entry` tool (MCP interface, includes dual-prompt context)

**Code Location:**
- `packages/timeline_context_system/prompt_context_tracker.py:TimelineMemoryStore.store_memory()`
- `packages/timeline_context_system/dual_prompt_architecture.py` - Dual-prompt context creation and storage

---

**Parent System:** [Timeline Context System](../../README.md)  
**Implementation:** [L3 Detailed](../../L3_detailed.md)  
**Code:** `packages/timeline_context_system/dual_prompt_architecture.py`
