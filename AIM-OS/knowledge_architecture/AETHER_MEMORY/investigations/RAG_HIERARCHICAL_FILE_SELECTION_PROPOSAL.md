---
id: "rag_hierarchical_file_selection_proposal"
system: "rag_file_selection"
component: null
level: "T2"
type: "architecture"
title: "RAG + HHNI Hierarchical File Selection - Architecture"
description: "2,000-word architecture document for intelligent file selection using RAG + HHNI hierarchical structure, enhancing existing SmartContextLoader with hierarchical intelligence"
audience: "architects, developers, system designers"
confidence_threshold: 0.75
token_cost: 2000
word_count: 2000
created: "2025-11-04T01:15:00Z"
updated: "2025-11-04T01:30:00Z"
author: "aether"
status: "draft"
tags: ["rag", "hhni", "file-selection", "context-retrieval", "hierarchical", "architecture", "t0-t6", "transitional", "smart-context-loader", "integration"]
dependencies: ["SmartContextLoader", "ConfidenceNavigationMap", "HHNI", "SystemMaps", "SUPER_INDEX"]
related_docs: ["RAG_MCP_TOOL_PROPOSAL.md", "confidence_navigation_map.md", "packages/context_bootloader/smart_context_loader.py"]
version: "v1.1.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# RAG + HHNI Hierarchical File Selection - Architecture (≈2,000 words)

**Enhances:** Existing `SmartContextLoader` with hierarchical intelligence  
**Integrates:** Confidence Navigation, System Maps, SUPER_INDEX, HHNI  
**Goal:** Leverage perfect hierarchical organization instead of static file paths

**Date:** 2025-11-04  
**Status:** 💡 **PROPOSAL** - Revolutionary Insight  
**Purpose:** Leverage AIM-OS hierarchical structure for intelligent file selection  
**Goal:** Replace simple grep/semantic search with RAG-aware hierarchical navigation

---

## 🎯 **THE INSIGHT**

**Instead of:**
- Simple grep/search for files
- Generic semantic search
- Ignoring our perfect organization

**Use:**
- **RAG + HHNI** to intelligently select files based on:
  - **Hierarchical structure** (System → Component → File)
  - **T-level organization** (T0-T6 summaries/complete docs)
  - **Confidence-based routing** (start shallow, go deep)
  - **System relationships** (related systems, dependencies)
  - **Task context** (what am I trying to do?)

**This leverages the perfect organization we've built instead of bypassing it!**

---

## 🚨 **THE PROBLEM WITH CURRENT APPROACHES**

### **Problem 1: Existing Systems Don't Use Hierarchy**

**Current Approach (SmartContextLoader):**
```python
# File-based loading with detail levels (L1-L4)
bootloader = load_bootloader_config(task_type)
context = load_weighted_context(bootloader, context_budget)
# Uses static file paths, not hierarchical queries
```

**Issues:**
- ✅ **Has:** Weighted priorities, budget management, MCP integration
- ✅ **Has:** Detail levels (L1-L4), semantic enhancement
- ❌ **Missing:** HHNI hierarchical queries (System → Component → File)
- ❌ **Missing:** T-level selection (uses L-levels, not T0-T6)
- ❌ **Missing:** System map integration for relationships
- ❌ **Missing:** Dynamic file discovery via HHNI

### **Problem 2: Confidence Navigation Not Integrated**

**Current Approach (Confidence Navigation Map):**
```python
# Manual routing based on confidence
if confidence >= 0.80:
    route_to = ["L1_overview.md"]
elif confidence >= 0.70:
    route_to = ["L2_architecture.md"]
# Manual file selection, not automated
```

**Issues:**
- ✅ **Has:** Confidence-based routing logic
- ✅ **Has:** Progressive disclosure strategy
- ❌ **Missing:** Automated file selection
- ❌ **Missing:** HHNI query integration
- ❌ **Missing:** Relationship expansion

### **Problem 3: Missing Hierarchical Intelligence**

**What We've Built:**
- ✅ **Perfect hierarchical organization** (HHNI)
- ✅ **T0-T6 documentation structure** (summary → complete)
- ✅ **System maps and indexes** (know relationships)
- ✅ **Confidence-based routing** (start shallow, go deep)
- ✅ **SUPER_INDEX** (master concept map)
- ✅ **SmartContextLoader** (weighted priorities, budget management)
- ✅ **SemanticContextLoader** (semantic enhancement)

**What's Missing:**
- ❌ **HHNI integration** - Query hierarchical index instead of manual file paths
- ❌ **T-level selection** - Use T0-T6 instead of L1-L4
- ❌ **System map integration** - Include related systems automatically
- ❌ **Dynamic discovery** - Find files via HHNI queries, not static configs

---

## 💡 **THE SOLUTION: RAG + HHNI FILE SELECTION**

### **Core Concept**

**When agent needs context:**
1. **Understand task** - What am I trying to do?
2. **Query HHNI** - Find relevant systems/components hierarchically
3. **Respect T-levels** - Choose appropriate level (T0-T6) based on confidence
4. **Consider relationships** - Include related systems/components
5. **Optimize context** - Only select files within budget

**Result:** Intelligent file selection that leverages our perfect organization!

---

## 🏗️ **ARCHITECTURE**

### **System Components**

```
┌─────────────────────────────────────────────────────────────┐
│  Task Analysis Layer                                        │
│  - Understands task type (coding, docs, debugging, etc.)   │
│  - Extracts concepts, systems, components                  │
│  - Determines confidence level                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  HHNI Query Layer                                           │
│  - Queries hierarchical index                              │
│  - Finds relevant systems → components → files             │
│  - Respects hierarchical relationships                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  T-Level Selection Layer                                    │
│  - Chooses appropriate T-level based on confidence         │
│  - Confidence ≥0.80 → T0-T1 (summary)                     │
│  - Confidence 0.70-0.79 → T2 (architecture)               │
│  - Confidence 0.60-0.69 → T3 (detailed)                   │
│  - Confidence <0.60 → T3-T4 (complete)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Relationship Expansion Layer                               │
│  - Finds related systems (via SYSTEM_MAP)                  │
│  - Includes dependencies                                    │
│  - Adds cross-system connection docs                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Context Budget Optimizer                                   │
│  - Estimates token cost per file                           │
│  - Prioritizes by relevance                                │
│  - Selects files within budget                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  File Selection Result                                      │
│  - Ordered list of files                                    │
│  - Each file has:                                           │
│    - Path                                                   │
│    - T-level                                                │
│    - Estimated tokens                                       │
│    - Relevance score                                        │
│    - Reason for inclusion                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **IMPLEMENTATION**

### **1. Task Analysis**

**Input:** User query or task description

**Output:** Task profile with:
- Task type (coding, documentation, debugging, etc.)
- Related systems (CMC, HHNI, VIF, etc.)
- Related components (specific components within systems)
- Confidence level (0.0-1.0)
- Context budget (tokens available)

**Example:**
```python
def analyze_task(task_description: str) -> TaskProfile:
    # Extract concepts
    concepts = extract_concepts(task_description)
    # ["agent", "automation", "monitoring"]
    
    # Find related systems via SUPER_INDEX
    systems = find_systems_for_concepts(concepts)
    # ["agent_automation", "bulletproof_messaging"]
    
    # Determine confidence
    confidence = assess_confidence(task_description, systems)
    # 0.75 (medium-high)
    
    # Determine context budget
    budget = estimate_context_budget(task_description)
    # 8000 tokens
    
    return TaskProfile(
        task_type="coding",
        systems=systems,
        components=["AgentMonitor", "MessageRouter"],
        confidence=confidence,
        budget=budget
    )
```

---

### **2. HHNI Query**

**Query hierarchical index for relevant files:**

```python
def query_hhnii_for_files(task_profile: TaskProfile) -> List[FileCandidate]:
    candidates = []
    
    for system in task_profile.systems:
        # Query HHNI at System level
        system_nodes = hhnii.query(system, level=IndexLevel.SYSTEM)
        
        # Find components
        for component in task_profile.components:
            component_nodes = hhnii.query(component, level=IndexLevel.SECTION)
            
            # Find files in component
            file_nodes = hhnii.query_files(component, level=IndexLevel.PARAGRAPH)
            
            for file_node in file_nodes:
                candidates.append(FileCandidate(
                    path=file_node.file_path,
                    system=system,
                    component=component,
                    relevance=file_node.relevance_score,
                    hhnii_level=file_node.level
                ))
    
    return candidates
```

---

### **3. T-Level Selection**

**Choose appropriate T-level based on confidence:**

```python
def select_t_level(confidence: float, file_candidates: List[FileCandidate]) -> List[SelectedFile]:
    selected = []
    
    # Map confidence to T-level
    if confidence >= 0.80:
        target_levels = ["T0", "T1"]  # Summary only
    elif confidence >= 0.70:
        target_levels = ["T2"]  # Architecture
    elif confidence >= 0.60:
        target_levels = ["T3"]  # Detailed
    else:
        target_levels = ["T3", "T4"]  # Complete
    
    for candidate in file_candidates:
        # Find matching T-level file
        t_file = find_t_level_file(candidate.path, target_levels)
        
        if t_file:
            selected.append(SelectedFile(
                path=t_file.path,
                t_level=t_file.level,
                estimated_tokens=estimate_tokens(t_file),
                relevance=candidate.relevance,
                confidence=confidence
            ))
    
    return selected
```

---

### **4. Relationship Expansion**

**Include related systems and dependencies:**

```python
def expand_relationships(selected_files: List[SelectedFile], system_map: SystemMap) -> List[SelectedFile]:
    expanded = list(selected_files)  # Start with selected
    
    # Find systems mentioned in selected files
    for file in selected_files:
        related_systems = system_map.get_related_systems(file.system)
        
        for related_system in related_systems:
            # Add related system's T0/T1 (lightweight context)
            related_file = find_t_level_file(
                system=related_system,
                level="T1"  # Lightweight overview
            )
            
            if related_file and related_file not in expanded:
                expanded.append(related_file)
    
    return expanded
```

---

### **5. Context Budget Optimization**

**Select files within token budget:**

```python
def optimize_context_budget(selected_files: List[SelectedFile], budget: int) -> List[SelectedFile]:
    # Sort by relevance (descending)
    sorted_files = sorted(selected_files, key=lambda f: f.relevance, reverse=True)
    
    optimized = []
    tokens_used = 0
    
    for file in sorted_files:
        if tokens_used + file.estimated_tokens <= budget:
            optimized.append(file)
            tokens_used += file.estimated_tokens
        else:
            # Try lighter T-level if available
            lighter_file = find_lighter_t_level(file)
            if lighter_file and tokens_used + lighter_file.estimated_tokens <= budget:
                optimized.append(lighter_file)
                tokens_used += lighter_file.estimated_tokens
    
    return optimized
```

---

## 📊 **EXAMPLE WORKFLOW**

### **Example: Implementing Agent Status Polling**

**Task:** "Add status polling to AgentMonitor"

**Step 1: Task Analysis**
```python
task_profile = {
    task_type: "coding",
    systems: ["agent_automation"],
    components: ["AgentMonitor"],
    confidence: 0.75,
    budget: 8000
}
```

**Step 2: HHNI Query**
```python
# Query HHNI for AgentMonitor-related files
candidates = [
    FileCandidate(path="cursor-addon/src/agent/agentMonitor.ts", relevance=0.95),
    FileCandidate(path="cursor-addon/docs/T2_AGENT_AUTOMATION_ARCHITECTURE.md", relevance=0.85),
    FileCandidate(path="cursor-addon/docs/T3_AGENT_AUTOMATION_DETAILED.md", relevance=0.80),
    FileCandidate(path="cursor-addon/docs/T0_AGENT_AUTOMATION_EXECUTIVE.md", relevance=0.70),
]
```

**Step 3: T-Level Selection (Confidence 0.75 → T2)**
```python
selected = [
    SelectedFile(path="cursor-addon/src/agent/agentMonitor.ts", t_level="source", tokens=2000),
    SelectedFile(path="cursor-addon/docs/T2_AGENT_AUTOMATION_ARCHITECTURE.md", t_level="T2", tokens=2000),
    # T3 skipped (too detailed for 0.75 confidence)
    # T0 skipped (too shallow)
]
```

**Step 4: Relationship Expansion**
```python
# AgentMonitor uses MessageRouter → include lightweight context
expanded = [
    ...selected_files,
    SelectedFile(path="cursor-addon/docs/T1_BULLETPROOF_MESSAGING_OVERVIEW.md", t_level="T1", tokens=500),
    SelectedFile(path="cursor-addon/src/messaging/router.ts", t_level="source", tokens=1000),
]
```

**Step 5: Budget Optimization**
```python
# Total: 5500 tokens (within 8000 budget)
optimized = [
    "cursor-addon/src/agent/agentMonitor.ts",  # 2000 tokens
    "cursor-addon/docs/T2_AGENT_AUTOMATION_ARCHITECTURE.md",  # 2000 tokens
    "cursor-addon/docs/T1_BULLETPROOF_MESSAGING_OVERVIEW.md",  # 500 tokens
    "cursor-addon/src/messaging/router.ts",  # 1000 tokens
]
```

**Result:** Intelligent file selection that:
- ✅ Respects hierarchical structure
- ✅ Chooses appropriate T-level (T2 for 0.75 confidence)
- ✅ Includes related systems (MessageRouter)
- ✅ Stays within budget
- ✅ High relevance (all files directly related to task)

---

## 🎯 **BENEFITS**

### **1. Leverages Perfect Organization**

**Instead of ignoring structure:**
- ✅ Uses HHNI hierarchical index
- ✅ Respects T-level organization
- ✅ Understands system relationships
- ✅ Follows confidence-based routing

### **2. Intelligent Selection**

**Instead of generic search:**
- ✅ Task-aware file selection
- ✅ Confidence-appropriate depth
- ✅ Relationship-aware expansion
- ✅ Budget-conscious optimization

### **3. Better Context Quality**

**Instead of random files:**
- ✅ Relevant files only
- ✅ Appropriate detail level
- ✅ Complete context (includes dependencies)
- ✅ Efficient token usage

---

## 🔗 **INTEGRATION WITH EXISTING SYSTEMS**

### **1. Enhance SmartContextLoader**

**Current:** File-based loading with static configs
**Enhancement:** Add HHNI hierarchical queries

```python
class HierarchicalContextLoader(SmartContextLoader):
    """
    Enhanced context loader with HHNI hierarchical queries
    Extends SmartContextLoader with hierarchical intelligence
    """
    
    def __init__(self, mcp_client=None, hhnii_client=None):
        super().__init__(mcp_client)
        self.hhnii_client = hhnii_client or HHNIIClient()
    
    def load_context_for_task(self, task_type: str, context_budget: int, 
                              confidence: float = 0.75) -> List[LoadedContext]:
        """
        Load context using HHNI hierarchical queries + existing bootloader logic
        """
        # Step 1: Query HHNI for relevant systems/components
        task_profile = self.analyze_task(task_type)
        hhnii_files = self.query_hhnii_hierarchically(task_profile)
        
        # Step 2: Select T-levels based on confidence (existing logic)
        t_level_files = self.select_t_levels(hhnii_files, confidence)
        
        # Step 3: Expand relationships via system maps
        expanded_files = self.expand_relationships(t_level_files)
        
        # Step 4: Use existing SmartContextLoader budget optimization
        optimized = self.optimize_context_budget(expanded_files, context_budget)
        
        # Step 5: Load files using existing SmartContextLoader logic
        return self.load_files(optimized)
```

### **2. Integrate with Confidence Navigation**

**Current:** Manual routing based on confidence
**Enhancement:** Automated T-level selection

```python
def select_t_levels(self, files: List[FileCandidate], confidence: float) -> List[SelectedFile]:
    """
    Use existing confidence navigation logic for T-level selection
    """
    # Reuse existing confidence routing logic
    if confidence >= 0.80:
        target_levels = ["T0", "T1"]  # Quick reference
    elif confidence >= 0.70:
        target_levels = ["T2"]  # Architecture
    elif confidence >= 0.60:
        target_levels = ["T3"]  # Detailed
    else:
        target_levels = ["T3", "T4"]  # Complete
    
    # Select files matching target T-levels
    return [f for f in files if f.t_level in target_levels]
```

### **3. Integrate with SemanticContextLoader**

**Current:** Semantic enhancement via MCP memory
**Enhancement:** Add HHNI hierarchical queries

```python
class HierarchicalSemanticLoader(SemanticContextLoader):
    """
    Combines semantic enhancement + hierarchical queries
    """
    
    def load_context_with_hierarchical_semantic(self, task_type: str, query: str, 
                                                context_budget: int = 80000,
                                                confidence: float = 0.75) -> List[LoadedContext]:
        """
        Load context using HHNI hierarchical queries + semantic enhancement
        """
        # Step 1: Hierarchical file selection (new)
        hierarchical_files = self.query_hhnii_hierarchically(task_type, query)
        
        # Step 2: Semantic enhancement (existing)
        semantic_matches = self.mcp_client.retrieve_memory(
            query, max_results=10, min_relevance=0.8
        )
        
        # Step 3: Combine both sources
        combined = hierarchical_files + semantic_matches
        
        # Step 4: Use existing budget optimization
        return self.optimize_context_budget(combined, context_budget)
```

### **4. Reuse Existing Bootloader Configs**

**Current:** Static bootloader configs per task type
**Enhancement:** Use HHNI to discover files dynamically

```python
def load_bootloader_config(self, task_type: str) -> BootloaderConfig:
    """
    Enhanced bootloader: Use HHNI to discover files dynamically
    """
    # Try existing static config first
    if exists(f"bootloaders/{task_type}.yaml"):
        return super().load_bootloader_config(task_type)
    
    # Fallback: Use HHNI to discover files dynamically
    hhnii_files = self.hhnii_client.query_files_for_task(task_type)
    
    # Convert HHNI results to bootloader config format
    return self._create_bootloader_from_hhnii(hhnii_files, task_type)
```

### **5. Integrate with SUPER_INDEX**

**Use SUPER_INDEX for concept mapping:**
```python
def analyze_task(self, task_type: str) -> TaskProfile:
    """
    Use SUPER_INDEX to find systems for concepts
    """
    # Extract concepts from task
    concepts = extract_concepts(task_type)
    
    # Query SUPER_INDEX (existing system)
    systems = super_index.find_systems_for_concepts(concepts)
    
    return TaskProfile(
        task_type=task_type,
        systems=systems,
        confidence=self.assess_confidence(task_type, systems)
    )
```

### **6. Integrate with System Maps**

**Use system maps for relationship expansion:**
```python
def expand_relationships(self, files: List[SelectedFile]) -> List[SelectedFile]:
    """
    Use system maps to find related systems (existing system)
    """
    expanded = list(files)
    
    for file in files:
        # Query system map for related systems
        related_systems = system_map.get_related_systems(file.system)
        
        # Add lightweight context from related systems
        for related_system in related_systems:
            related_file = self.find_t_level_file(related_system, "T1")
            if related_file:
                expanded.append(related_file)
    
    return expanded
```

---

## 📚 **RELATED DOCUMENTATION**

### **Existing Systems (To Enhance):**
- **SmartContextLoader:** `packages/context_bootloader/smart_context_loader.py` - Weighted context loading
- **SemanticContextLoader:** `packages/context_bootloader/smart_context_loader.py` - Semantic enhancement
- **MCP Context Tools:** `packages/context_bootloader/mcp_context_tools.py` - MCP integration

### **Systems to Integrate:**
- **HHNI:** `knowledge_architecture/systems/hhni/` - Hierarchical indexing system
- **SUPER_INDEX:** `knowledge_architecture/SUPER_INDEX.md` - Master concept map
- **Confidence Navigation:** `knowledge_architecture/NAVIGATION/confidence_navigation_map.md` - Confidence-based routing
- **System Maps:** `cursor-addon/docs/systems/*/system.map.lucid.json5` - System relationships

### **Proposals:**
- **RAG MCP Tool:** `knowledge_architecture/AETHER_MEMORY/investigations/RAG_MCP_TOOL_PROPOSAL.md`
- **HHNI Natural Context:** `knowledge_architecture/AETHER_MEMORY/investigations/HHNI_NATURAL_CONTEXT_ENRICHMENT.md`

### **Implementation:**
- **New Class:** `packages/context_bootloader/hierarchical_context_loader.py` (to be created)
- **Enhanced MCP Tool:** `packages/context_bootloader/mcp_context_tools.py` (to be enhanced)

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Enhance Existing SmartContextLoader (2-3 hours)**

**Goal:** Add HHNI hierarchical queries to existing SmartContextLoader

**Tasks:**
1. Create `HierarchicalContextLoader` class extending `SmartContextLoader`
2. Add HHNI query methods:
   - `query_hhnii_hierarchically()` - Query HHNI for files
   - `select_t_levels()` - T-level selection based on confidence
   - `expand_relationships()` - System map integration
3. Update `load_context_for_task()` to use HHNI queries
4. Preserve existing bootloader config fallback

**File:** `packages/context_bootloader/hierarchical_context_loader.py`

### **Phase 2: T-Level Integration (1-2 hours)**

**Goal:** Replace L-levels with T-levels in file selection

**Tasks:**
1. Update `DetailLevel` enum to use T0-T6 instead of L1-L4
2. Add T-level file discovery:
   - `find_t_level_file()` - Find T0-T6 files for system
   - `map_t_level_to_confidence()` - Confidence → T-level mapping
3. Update bootloader configs to use T-levels

**Files:**
- `packages/context_bootloader/smart_context_loader.py`
- `packages/context_bootloader/hierarchical_context_loader.py`

### **Phase 3: System Map Integration (1-2 hours)**

**Goal:** Use system maps for relationship expansion

**Tasks:**
1. Add system map query methods:
   - `get_related_systems()` - Query system.map.lucid.json5
   - `expand_with_related_systems()` - Add related system context
2. Integrate with existing relationship expansion logic
3. Add lightweight T1 context for related systems

**Files:**
- `packages/context_bootloader/hierarchical_context_loader.py`

### **Phase 4: SUPER_INDEX Integration (1 hour)**

**Goal:** Use SUPER_INDEX for concept mapping

**Tasks:**
1. Add SUPER_INDEX query methods:
   - `find_systems_for_concepts()` - Query SUPER_INDEX
   - `extract_concepts()` - Extract concepts from task
2. Integrate with task analysis

**Files:**
- `packages/context_bootloader/hierarchical_context_loader.py`

### **Phase 5: MCP Tool Creation (1-2 hours)**

**Goal:** Create MCP tool for hierarchical file selection

**Tasks:**
1. Create `mcp_lucid-mcp_select_context_files` MCP tool
2. Integrate with existing `mcp_context_tools.py`
3. Add to MCP server registration

**Files:**
- `packages/context_bootloader/mcp_context_tools.py`
- `packages/mcp_server/lucid_mcp_server.py`

### **Phase 6: Testing & Validation (2-3 hours)**

**Goal:** Test hierarchical file selection end-to-end

**Tasks:**
1. Write tests for hierarchical queries
2. Test T-level selection accuracy
3. Test relationship expansion
4. Test budget optimization
5. Compare with existing SmartContextLoader

**Files:**
- `packages/context_bootloader/tests/test_hierarchical_loader.py`

**Total Estimated Time:** 8-13 hours

---

**Status:** 💡 **PROPOSAL** - Revolutionary Insight  
**Author:** Aether (based on Braden's insight)  
**Date:** 2025-11-04  
**Priority:** High - Leverages our perfect organization!

