# Subsystem Inventory & Mapping Plan

**Purpose:** Comprehensive inventory of all subsystems and mapping to main systems  
**Date:** 2025-01-27  
**Status:** PLANNING  
**Author:** Aether (with Braden's insight)  
**Related Systems:** All AIM-OS Systems, Documentation Standards, System Hierarchy

---

## 🎯 **BRADEN'S CRITICAL CONCERN**

**Braden's Statement:**
> "we also have so many sub systems and even systems not yet made into or integrated into other T0+ docs /system maps etc. so we will first I think have to go over all the like 50-80 sub systems we have ..hmm im trying to think how we do this. I think we had already mapped the sub systems to the main systems? I wonder if we tagged them within the main systems or how it was done or ensured they were noted in the larger branches of the system above etc? lets look into this"

**Core Challenge:**
- **91 system directories** found in `knowledge_architecture/systems/`
- **Many subsystems** (50-80) not integrated into T0+ docs/system maps
- **Need to verify** how subsystems are currently mapped
- **Need to ensure** all subsystems are properly tagged/noted in main systems

---

## 📊 **CURRENT STATE ANALYSIS**

### **System Count:**
- **91 system directories** in `knowledge_architecture/systems/`
- **8-9 main systems** (CMC, SEG, HHNI, VIF, SDF-CVF, APOE, CAS, TCS, IIS)
- **~80-83 subsystems** (remaining directories)

### **Current Mapping Pattern (From CMC Example):**

**System Map Structure:**
- `internalNodes` - Lists components (e.g., `atomManager`, `snapshotEngine`, `storageManager`)
- Components are listed as `internalNodes` with `kind: "core.component"`, `"storage.component"`, etc.
- **No explicit "subsystem" designation** - components are just internal nodes

**Component Organization:**
- Components have their own directories: `components/{component_name}/`
- Components have README.md, L1-L2 docs (sometimes)
- **Components are NOT explicitly mapped as subsystems** in system maps

**T0+ Documentation:**
- T2_architecture.md has "Components" section
- Lists components but doesn't explicitly map them as subsystems
- Components referenced but not systematically integrated

---

## 🔍 **INVESTIGATION NEEDED**

### **Questions to Answer:**

1. **How are subsystems currently mapped?**
   - Are they in `internalNodes` in system maps?
   - Are they in a separate `subsystems` section?
   - Are they just listed in T0+ docs?
   - Are they in system indexes?

2. **Which systems have subsystems?**
   - CMC has: atoms, pipelines, snapshots, storage (4 components)
   - What about other main systems?
   - How many subsystems per main system?

3. **Which subsystems are NOT mapped?**
   - Which subsystems exist but aren't in system maps?
   - Which subsystems exist but aren't in T0+ docs?
   - Which subsystems exist but aren't in system indexes?

4. **What's the relationship between "systems" and "subsystems"?**
   - Are some "systems" actually subsystems of main systems?
   - How do we distinguish between standalone systems and subsystems?
   - What's the hierarchy?

---

## 📋 **INVENTORY PLAN**

### **Phase 1: Complete System Inventory**

**Step 1: List All Systems**
- Get complete list of all 91 system directories
- Categorize: Main systems vs Subsystems vs Standalone systems
- Identify which systems belong to which main system

**Step 2: Check Current Mapping**
- For each system, check:
  - Does it have system.map.lucid.json5?
  - Does it have system.index.lucid.json5?
  - Is it listed in a main system's map/index?
  - Is it referenced in T0+ docs?

**Step 3: Identify Gaps**
- List systems not in any main system map
- List systems not in any main system index
- List systems not in any T0+ docs
- List systems that should be subsystems but aren't mapped

---

### **Phase 2: Subsystem Classification**

**Classification Criteria:**
1. **Main System:** Core system (CMC, SEG, HHNI, VIF, SDF-CVF, APOE, CAS, TCS, IIS)
2. **Subsystem:** Component of main system (e.g., CMC's atoms, pipelines, snapshots, storage)
3. **Standalone System:** Independent system (e.g., daemon_rag_system, lucid_mcp_integration)
4. **Infrastructure System:** Layer 5 system (conditional system maps)
5. **Application System:** Layer 6 system (no system maps required)

**Classification Process:**
1. Review each of 91 systems
2. Determine classification (main, subsystem, standalone, infrastructure, application)
3. If subsystem, identify parent main system
4. Document classification

---

### **Phase 3: Mapping Verification**

**For Each Main System:**
1. **Check System Map:**
   - Are all subsystems listed in `internalNodes`?
   - Are subsystems explicitly marked as subsystems?
   - Are relationships documented?

2. **Check System Index:**
   - Are all subsystems listed?
   - Are subsystems cross-referenced?
   - Are relationships documented?

3. **Check T0+ Docs:**
   - Are all subsystems mentioned in T2_architecture.md?
   - Are subsystems documented in T3_detailed.md?
   - Are subsystems referenced in T4_complete.md?

4. **Check Component Directories:**
   - Do subsystems have their own directories?
   - Do subsystems have README.md?
   - Do subsystems have L0-L4 docs (if needed)?

---

### **Phase 4: Gap Identification**

**Missing Mappings:**
- List subsystems not in system maps
- List subsystems not in system indexes
- List subsystems not in T0+ docs
- List subsystems without proper documentation

**Incorrect Classifications:**
- List systems classified as standalone but should be subsystems
- List subsystems classified as main systems
- List systems in wrong layer

**Missing Documentation:**
- List subsystems without README.md
- List subsystems without L0-L4 docs (if needed)
- List subsystems without integration docs

---

## 🎯 **MAPPING STRATEGY**

### **Option 1: Components as Internal Nodes (Current Pattern)**

**Current Approach:**
- Components listed as `internalNodes` in system maps
- Components have `kind: "core.component"`, `"storage.component"`, etc.
- Components referenced in T0+ docs but not explicitly as "subsystems"

**Pros:**
- Simple structure
- Already in place for some systems
- Easy to maintain

**Cons:**
- No explicit "subsystem" designation
- Hard to distinguish subsystems from simple components
- No clear hierarchy

---

### **Option 2: Explicit Subsystem Section (Recommended)**

**Proposed Approach:**
- Add `subsystems` section to system maps
- List subsystems explicitly with parent relationship
- Document subsystem relationships

**System Map Structure:**
```json5
{
  "systemId": "cmc.contextMemoryCore",
  "internalNodes": [...],  // Simple components
  "subsystems": [           // NEW: Explicit subsystems
    {
      "id": "atoms",
      "name": "Atom Management Subsystem",
      "type": "subsystem",
      "parent": "cmc",
      "status": "production",
      "documentation": {
        "L0": "components/atoms/L1_overview.md",
        "L1": "components/atoms/L1_overview.md",
        "L2": "components/atoms/L2_architecture.md",
        "README": "components/atoms/README.md"
      },
      "relationships": {
        "parent": "cmc",
        "children": [],
        "siblings": ["pipelines", "snapshots", "storage"],
        "external": []
      }
    },
    ...
  ]
}
```

**Pros:**
- Explicit subsystem designation
- Clear hierarchy
- Easy to identify subsystems
- Better organization

**Cons:**
- Requires updating all system maps
- More complex structure

---

### **Option 3: Hybrid Approach (Recommended)**

**Proposed Approach:**
- Keep `internalNodes` for simple components
- Add `subsystems` section for complex components that meet subsystem criteria
- Use subsystem creation criteria to determine which components are subsystems

**System Map Structure:**
```json5
{
  "systemId": "cmc.contextMemoryCore",
  "internalNodes": [
    // Simple components (don't meet subsystem criteria)
    {
      "id": "atomManager",
      "kind": "core.component",
      ...
    }
  ],
  "subsystems": [
    // Complex components (meet subsystem criteria)
    {
      "id": "atoms",
      "type": "subsystem",
      "meetsCriteria": ["complexity", "independence"],
      ...
    }
  ]
}
```

**Pros:**
- Best of both worlds
- Clear distinction between components and subsystems
- Flexible structure
- Aligns with subsystem creation criteria

**Cons:**
- Requires careful classification
- More complex structure

---

## 📊 **INVENTORY PROCESS**

### **Step 1: Create Complete System List**

**Process:**
1. List all 91 system directories
2. For each, determine:
   - Is it a main system? (CMC, SEG, HHNI, VIF, SDF-CVF, APOE, CAS, TCS, IIS)
   - Is it a subsystem? (component of main system)
   - Is it standalone? (independent system)
   - Is it infrastructure? (Layer 5)
   - Is it application? (Layer 6)

**Deliverable:** `COMPLETE_SYSTEM_INVENTORY.md`

---

### **Step 2: Check Current Mapping Status**

**For Each System:**
1. **System Map Check:**
   - Does system.map.lucid.json5 exist?
   - Is system listed in any main system's map?
   - Is system listed as `internalNode` or `subsystem`?

2. **System Index Check:**
   - Does system.index.lucid.json5 exist?
   - Is system listed in any main system's index?
   - Is system cross-referenced?

3. **T0+ Docs Check:**
   - Is system mentioned in T2_architecture.md?
   - Is system documented in T3_detailed.md?
   - Is system referenced in T4_complete.md?

4. **Component Directory Check:**
   - Does system have component directory?
   - Does system have README.md?
   - Does system have L0-L4 docs?

**Deliverable:** `SYSTEM_MAPPING_STATUS.md`

---

### **Step 3: Identify Gaps**

**Gap Categories:**
1. **Missing System Maps:** Systems without system.map.lucid.json5
2. **Missing System Indexes:** Systems without system.index.lucid.json5
3. **Missing T0+ References:** Systems not in T0+ docs
4. **Missing Component Docs:** Systems without README.md or L0-L4 docs
5. **Missing Parent Mapping:** Subsystems not mapped to main systems
6. **Missing Cross-Connections:** Subsystems without relationship documentation

**Deliverable:** `SUBSYSTEM_MAPPING_GAPS.md`

---

### **Step 4: Create Mapping Plan**

**For Each Gap:**
1. Identify what's missing
2. Determine where it should be mapped
3. Create mapping plan
4. Prioritize (critical, high, medium, low)

**Deliverable:** `SUBSYSTEM_MAPPING_PLAN.md`

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Inventory (Immediate)**
1. Create complete system list (91 systems)
2. Classify each system (main, subsystem, standalone, infrastructure, application)
3. Check current mapping status
4. Identify gaps

### **Phase 2: Mapping Strategy (After Inventory)**
1. Decide on mapping approach (Option 1, 2, or 3)
2. Create mapping templates
3. Create mapping process
4. Create validation checklist

### **Phase 3: Mapping Implementation (After Consolidation)**
1. Update system maps with subsystems
2. Update system indexes with subsystems
3. Update T0+ docs with subsystems
4. Create/update subsystem documentation
5. Verify all mappings

---

**Status:** Inventory & Mapping Plan Created ✅  
**Confidence:** High (0.85) - Clear process, addresses Braden's concerns  
**Next:** Create complete system inventory (91 systems), check current mapping status

---

