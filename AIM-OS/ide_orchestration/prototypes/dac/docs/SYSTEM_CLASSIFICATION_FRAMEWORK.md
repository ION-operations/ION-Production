# SYSTEM CLASSIFICATION FRAMEWORK - How to Categorize AIM-OS Systems

**Date:** 2025-11-18
**Status:** Framework Ready
**Purpose:** Define how to classify all AIM-OS systems and packages

---

## 🎯 **CLASSIFICATION GOALS**

**We need to determine for each system/package:**
1. Is it a core system?
2. Is it an enhancement to an existing system?
3. Is it a sub-layer of an existing system?
4. Is it a new major system?
5. Is it an integration system?
6. Is it a utility system?

**This classification will:**
- Create clear system hierarchy
- Show relationships between systems
- Guide documentation priorities
- Inform integration decisions
- Help determine what needs to be core vs enhancement

---

## 📊 **CLASSIFICATION LEVELS**

### **1. CORE SYSTEMS (7 Systems)**

**Definition:** Foundation systems that are essential for AIM-OS operation and used by all other systems.

**Current Core Systems:**
1. **CMC** (Context Memory Core) - Bitemporal storage
2. **HHNI** (Hierarchical Hypergraph Neural Index) - Semantic retrieval
3. **VIF** (Verifiable Intelligence Framework) - Verification & confidence
4. **APOE** (AI-Powered Orchestration Engine) - Planning & execution
5. **SEG** (Semantic Episodic Graphs) - Knowledge synthesis
6. **CAS** (Cognitive Analysis System) - Meta-cognition
7. **TCS** (Timeline Context System) - Temporal consciousness

**Criteria for Core System:**
- ✅ Used by multiple other systems
- ✅ Provides fundamental capability
- ✅ Essential for AIM-OS operation
- ✅ Has extensive integration points
- ✅ Well-documented and tested

**Action:** Core systems are already identified. Verify completeness and document all enhancements/sub-layers.

---

### **2. ENHANCEMENT SYSTEMS**

**Definition:** Systems that enhance existing core systems with additional capabilities.

**Examples:**
- `holographic_memory` → Enhances CMC (memory capabilities)
- `deepsearch` → Enhances HHNI (search capabilities)
- `nl_tags` → Enhances SDF-CVF (quintet parity)
- `scor` → Enhances CAS (safety capabilities)

**Criteria for Enhancement:**
- ✅ Extends functionality of core system
- ✅ Can be used independently or with core system
- ✅ Adds new capabilities without replacing core
- ✅ Has clear relationship to core system

**Classification Questions:**
1. Which core system does this enhance?
2. What new capabilities does it add?
3. Can it work independently?
4. Is it optional or required?

**Action:** Classify as enhancement, document relationship to core system, update system maps.

---

### **3. SUB-LAYER SYSTEMS**

**Definition:** Systems that are sub-components or specialized layers within a core system.

**Examples:**
- `context_bootloader` → Sub-layer of TCS (context loading)
- `apoe_runner` → Sub-layer of APOE (execution engine)
- `prompt_chain_executor` → Sub-layer of prompt_chains (execution engine)

**Criteria for Sub-Layer:**
- ✅ Part of a larger system
- ✅ Specialized functionality within parent
- ✅ Not typically used independently
- ✅ Clear parent-child relationship

**Classification Questions:**
1. Which system is the parent?
2. What specialized function does it provide?
3. Is it always used with parent?
4. Can it be separated?

**Action:** Classify as sub-layer, document parent system, update system hierarchy.

---

### **4. NEW MAJOR SYSTEMS**

**Definition:** Major new systems that may become core systems or remain separate.

**Current New Major Systems:**
- **PLIx** - Programming language
- **Quaternion Kernel** - Geometric kernel
- **IGODN** - Intent geometry
- **LLM API Integration** - API service registry

**Criteria for New Major:**
- ✅ Significant new capability
- ✅ May become core system
- ✅ Has own documentation and structure
- ✅ May integrate with multiple core systems

**Classification Questions:**
1. Should this become a core system?
2. What core systems does it integrate with?
3. Is it foundational or specialized?
4. What is its relationship to existing core?

**Action:** Classify as new major, determine if should be core, document integration points.

---

### **5. INTEGRATION SYSTEMS**

**Definition:** Systems that integrate AIM-OS with external systems or provide integration layers.

**Examples:**
- **MCP Integration** - MCP server, MCP tools
- **IDE Integration** - Cursor extension, Electron app, DAC v2 IDE
- **LLM API Integration** - API service registry
- **Mobile Integration** - Mobile app, SDK

**Criteria for Integration:**
- ✅ Connects AIM-OS to external systems
- ✅ Provides integration layer
- ✅ May have own UI or interface
- ✅ Not core functionality but important

**Classification Questions:**
1. What does it integrate with?
2. Is it required or optional?
3. What core systems does it use?
4. Is it a separate layer or embedded?

**Action:** Classify as integration, document integration points, update system maps.

---

### **6. UTILITY SYSTEMS**

**Definition:** Utility packages, test systems, and supporting infrastructure.

**Examples:**
- `integration_tests` - Test utilities
- `schemas` - Schema definitions
- `unified` - Unified utilities
- `doc_builder` - Documentation builder

**Criteria for Utility:**
- ✅ Supporting infrastructure
- ✅ Not a core capability
- ✅ May be used by multiple systems
- ✅ Minimal documentation needed

**Classification Questions:**
1. What is its purpose?
2. Which systems use it?
3. Is it required or optional?
4. What level of documentation needed?

**Action:** Classify as utility, minimal documentation (T0-T1 may be sufficient).

---

## 🔍 **CLASSIFICATION PROCESS**

### **Step 1: Analyze System/Package**

**Questions to Answer:**
1. What does this system/package do?
2. Which systems does it depend on?
3. Which systems depend on it?
4. What is its primary purpose?
5. Is it foundational or specialized?

### **Step 2: Check Relationships**

**Check:**
- Integration files (does it integrate with core systems?)
- Import statements (what does it import from?)
- Documentation references (what systems does it mention?)
- Usage patterns (where is it used?)

### **Step 3: Apply Classification**

**Decision Tree:**
```
Is it used by multiple systems and foundational?
  → YES: Core System (verify against 7 core systems)
  → NO: Continue

Does it enhance a core system?
  → YES: Enhancement System
  → NO: Continue

Is it a sub-component of a larger system?
  → YES: Sub-Layer System
  → NO: Continue

Is it a major new capability?
  → YES: New Major System
  → NO: Continue

Does it integrate with external systems?
  → YES: Integration System
  → NO: Continue

Is it utility/supporting infrastructure?
  → YES: Utility System
  → NO: Re-evaluate
```

### **Step 4: Document Classification**

**Document:**
- Classification level
- Parent system (if sub-layer or enhancement)
- Relationships to other systems
- Integration points
- Rationale for classification

---

## 📋 **SPECIFIC CLASSIFICATION EXAMPLES**

### **Example 1: `holographic_memory`**

**Analysis:**
- Enhances CMC with holographic memory capabilities
- Used with CMC, not independently
- Adds new memory capabilities

**Classification:** Enhancement System (enhances CMC)

**Action:** Document as enhancement to CMC, update CMC system map

---

### **Example 2: `apoe_runner`**

**Analysis:**
- Executes APOE plans
- Part of APOE system
- Specialized execution engine

**Classification:** Sub-Layer System (sub-layer of APOE)

**Action:** Document as sub-layer of APOE, update APOE system map

---

### **Example 3: `PLIx`**

**Analysis:**
- Major new programming language
- Integrates with multiple systems
- Significant new capability

**Classification:** New Major System (may become core)

**Action:** Document as new major, determine if should be core, document integration

---

### **Example 4: `MCP Integration`**

**Analysis:**
- Integrates AIM-OS with Cursor IDE
- Provides integration layer
- Not core functionality

**Classification:** Integration System

**Action:** Document as integration, document integration points

---

### **Example 5: `integration_tests`**

**Analysis:**
- Test utilities
- Supporting infrastructure
- Not a core capability

**Classification:** Utility System

**Action:** Minimal documentation (T0-T1 sufficient)

---

## 🎯 **CLASSIFICATION PRIORITIES**

### **High Priority (Classify First):**
1. Systems that might be core (need to decide)
2. Enhancements to core systems (need to document relationships)
3. Sub-layers of core systems (need to document hierarchy)

### **Medium Priority:**
4. New major systems (need to determine if core)
5. Integration systems (need to document integration points)

### **Low Priority:**
6. Utility systems (minimal classification needed)

---

## 📊 **CLASSIFICATION OUTPUT**

**For each system/package, document:**
1. **Classification Level:** Core / Enhancement / Sub-Layer / New Major / Integration / Utility
2. **Parent System:** (if enhancement or sub-layer)
3. **Relationships:** Which systems it relates to
4. **Integration Points:** How it integrates with other systems
5. **Rationale:** Why this classification

**Update:**
- System maps with classifications
- System hierarchy diagrams
- Integration maps
- Documentation structure

---

## 🚀 **NEXT STEPS**

1. **Specialists Classify Their Systems:**
   - Each specialist classifies their assigned systems
   - Uses this framework
   - Documents rationale

2. **Review Classifications:**
   - Aether reviews all classifications
   - Team resolves conflicts
   - Final classifications determined

3. **Update System Maps:**
   - Update all system maps with classifications
   - Create system hierarchy
   - Document relationships

4. **Document Missing Systems:**
   - Classify systems from docs that don't have packages
   - Determine if packages needed
   - Document implementation gaps

---

**Status:** Framework Ready

**See:** `TEAM_CONSOLIDATION_ASSIGNMENTS.md` for specialist assignments

