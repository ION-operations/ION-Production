# Subsystem Hierarchy Enhancement Plan

**Purpose:** Add explicit subsystem hierarchy to system maps and enhance hierarchy documentation  
**Date:** 2025-01-27  
**Status:** IMPLEMENTATION  
**Author:** Aether  
**Related Systems:** All AIM-OS Systems, Documentation Standards, System Hierarchy

---

## 🎯 **OBJECTIVE**

**Braden's Requirement:**
> "yes we need it it have heirarchy in sytem maps, i thought we had mapped them . what are all the system maps we have and indexs? and super index what else? i thought we had hierchy mapped out, but if not or need imrpved this is important."

**Goal:**
- Add explicit `subsystems` section to all system maps
- Show subsystem → main system hierarchy clearly
- Enhance HIERARCHICAL_NAVIGATION_INDEX.md with subsystem hierarchy
- Verify all subsystems are properly mapped

---

## 📊 **SUBSYSTEM INVENTORY BY MAIN SYSTEM**

### **1. CMC (Context Memory Core) - Layer 1**

**Subsystems Identified:**
1. **Atoms** - `components/atoms/` (has L1-L2 docs, README, fields/)
2. **Pipelines** - `components/pipelines/` (has L1-L2 docs, README)
3. **Snapshots** - `components/snapshots/` (has L1-L2 docs, README)
4. **Storage** - `components/storage/` (has L1-L2 docs, README)

**Status:** ✅ All 4 subsystems have documentation

---

### **2. HHNI (Hierarchical Hypergraph Neural Index) - Layer 2**

**Subsystems Identified:**
1. **DVNS Physics** - `components/dvns/` (check if exists)
2. **Morphological Analysis** - `components/morphological_analysis/` (check if exists)
3. **Semantic Block Organizer** - (check if exists)
4. **Cross-Document Relationship Detector** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **3. VIF (Verifiable Intelligence Framework) - Layer 2**

**Subsystems Identified:**
1. **Confidence Tracker** - (check if exists)
2. **Witness Manager** - (check if exists)
3. **Provenance Engine** - (check if exists)
4. **Validation Engine** - (check if exists)
5. **κ-Gating Module** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **4. SEG (Shared Evidence Graph) - Layer 1**

**Subsystems Identified:**
1. **Graph Engine** - (check if exists)
2. **Contradiction Detector** - (check if exists)
3. **Synthesis Engine** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **5. APOE (AI-Powered Orchestration Engine) - Layer 3**

**Subsystems Identified:**
1. **ACL Compiler** - (check if exists)
2. **DAG Executor** - (check if exists)
3. **Role Dispatcher** - (check if exists)
4. **Gate Manager** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **6. SDF-CVF (Atomic Evolution Framework) - Layer 2**

**Subsystems Identified:**
1. **Quartet Parity** - (check if exists)
2. **Quality Gates** - (check if exists)
3. **Blast Radius** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **7. CAS (Cognitive Analysis System) - Layer 4**

**Subsystems Identified:**
1. **Meta-Cognitive Monitor** - (check if exists)
2. **Failure Detector** - (check if exists)
3. **Self-Correction** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **8. TCS (Timeline Context System) - Layer 4**

**Subsystems Identified:**
1. **Timeline Tracker** - (check if exists)
2. **Consciousness Journaling** - (check if exists)
3. **Context Management** - (check if exists)
4. **Dual-Prompt** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

### **9. IIS (Intuitive Intelligence System) - Layer 4**

**Subsystems Identified:**
1. **Intuition Calculator** - (check if exists)
2. **Feature Extractor** - (check if exists)
3. **Learning Engine** - (check if exists)
4. **Calibration Tracker** - (check if exists)

**Status:** ⏳ Need to verify which components are subsystems

---

## 🏗️ **ENHANCEMENT PROCESS**

### **Phase 1: Complete Subsystem Inventory**

**For Each Main System:**
1. List all components in `components/` directory
2. Check which components meet subsystem criteria:
   - Complexity threshold (500+ lines OR 3+ sub-components OR 5+ integrations)
   - Independence threshold (can be understood independently, clear boundaries, own API)
   - Relationship threshold (relationships to other systems/subsystems)
   - Evolution threshold (expected to grow, needs maintenance, can be reused)
3. Classify: Subsystem vs Simple Component
4. Document classification

**Deliverable:** `COMPLETE_SUBSYSTEM_INVENTORY.md`

---

### **Phase 2: Add Subsystems Section to System Maps**

**For Each Main System:**
1. Read current system.map.lucid.json5
2. Identify all subsystems (from Phase 1)
3. Add `subsystems` array with:
   - Subsystem ID
   - Subsystem name
   - Type: "subsystem"
   - Parent: main system ID
   - Status
   - Documentation paths
   - Relationships (parent, children, siblings, external)
4. Keep `internalNodes` for simple components
5. Update system map

**Deliverable:** Updated system.map.lucid.json5 for all 9 core systems

---

### **Phase 3: Enhance HIERARCHICAL_NAVIGATION_INDEX.md**

**Enhancement:**
1. Add "Subsystems" section under each main system
2. List all subsystems with links to documentation
3. Show subsystem → main system relationships
4. Link to subsystem documentation (L0-L4, README)

**Deliverable:** Enhanced HIERARCHICAL_NAVIGATION_INDEX.md

---

### **Phase 4: Update System Indexes**

**For Each Main System:**
1. Read current system.index.lucid.json5
2. Add subsystem entries to `internalNodes` or new `subsystems` section
3. Add cross-references for subsystems
4. Update relationships section

**Deliverable:** Updated system.index.lucid.json5 for all 9 core systems

---

### **Phase 5: Verify All Mappings**

**Verification Checklist:**
- [ ] All subsystems listed in system maps
- [ ] All subsystems listed in system indexes
- [ ] All subsystems mentioned in T0+ docs
- [ ] All subsystems have proper documentation
- [ ] All parent-child relationships documented
- [ ] All cross-connections documented

**Deliverable:** `SUBSYSTEM_MAPPING_VERIFICATION_REPORT.md`

---

## 🚀 **IMPLEMENTATION ORDER**

### **Step 1: CMC (Example/Reference)**
- Complete subsystem inventory
- Add subsystems section to system map
- Enhance HIERARCHICAL_NAVIGATION_INDEX.md
- Update system index
- Verify mappings

**Why First:** CMC has clear subsystem structure (atoms, pipelines, snapshots, storage), good reference for others

---

### **Step 2: Remaining Core Systems (HHNI, VIF, SEG, APOE, SDF-CVF, CAS, TCS, IIS)**
- Complete subsystem inventory for each
- Add subsystems section to system maps
- Update system indexes
- Verify mappings

---

### **Step 3: Enhance HIERARCHICAL_NAVIGATION_INDEX.md**
- Add subsystem sections for all main systems
- Show complete hierarchy
- Link to all documentation

---

### **Step 4: Final Verification**
- Verify all subsystems mapped
- Verify all hierarchies correct
- Verify all cross-references accurate

---

**Status:** Enhancement Plan Created ✅  
**Confidence:** High (0.90) - Clear process, systematic approach  
**Next:** Begin Phase 1 - Complete subsystem inventory for CMC (example/reference)

---

