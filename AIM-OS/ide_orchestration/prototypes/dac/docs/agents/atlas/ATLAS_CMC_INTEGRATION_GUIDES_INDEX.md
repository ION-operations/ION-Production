# Atlas - CMC Integration Guides Index

**Purpose:** Master index of all CMC integration guides  
**Author:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Active - Updated as guides are created

---

## 📋 **OVERVIEW**

This document provides a comprehensive index of all CMC integration guides created by Atlas. These guides document how other AIM-OS systems integrate with CMC (Context Memory Core) for persistent memory storage and retrieval.

**All guides include:**
- Complete atom schema recommendations
- Storage patterns (creation, updates, queries)
- Bitemporal support (current and planned)
- SEG integration points
- Code references
- Integration checklists

---

## 📚 **INTEGRATION GUIDES**

### **1. TCS (Timeline Context System) Integration**

**Document:** `ATLAS_CMC_TCS_INTEGRATION.md`  
**For:** @Chronos (TCS System Specialist)  
**Status:** ✅ Complete  
**Created:** 2025-01-27

**Topics Covered:**
- Timeline entry storage patterns
- Timeline entry atom structure
- Query patterns (by prompt_id, event_type, time range)
- Bitemporal support for timeline entries
- SEG integration (timeline entries → evidence nodes)
- MCP tool integration (`add_timeline_entry`)

**Key Integration Points:**
- **Modality:** `"tcs_timeline"` (recommended)
- **Tags:** `timeline_context: 1.0`, `prompt_tracking: 0.9`, `tcs_entry: 1.0`
- **Metadata:** Complete timeline entry structure (entry_id, prompt_id, event_type, etc.)
- **Bitemporal:** `valid_from`/`valid_to` in metadata (native support planned)

**Code References:**
- MCP Tool: `lucid_mcp_server.py:3596-3660` (add_timeline_entry)
- TCS Storage: `packages/timeline_context_system/prompt_context_tracker.py:26-113`
- CMC Models: `packages/cmc_service/models.py`

---

### **2. APOE (AI-Powered Orchestration Engine) Integration**

**Document:** `ATLAS_CMC_APOE_INTEGRATION.md`  
**For:** @Alex (APOE System Specialist)  
**Status:** ✅ Complete  
**Created:** 2025-01-27

**Topics Covered:**
- Execution state storage patterns
- Plan execution atom structure
- Storage patterns (start, progress, completion)
- Query patterns (by plan_name, status, execution_id)
- Bitemporal support for execution states
- SEG integration (execution states → derivation nodes)
- VIF integration (execution states → witness envelopes)

**Key Integration Points:**
- **Modality:** `"apoe_plan"` (recommended)
- **Tags:** `apoe: 1.0`, `plan: 1.0`, `plan_name: 0.9`, `status: {weight}`
- **Metadata:** Complete execution state structure (plan_name, execution_id, status, outputs, etc.)
- **Bitemporal:** `started_at`/`completed_at` in metadata (native support planned)

**Code References:**
- APOE CMC Integration: `packages/apoe/cmc_integration.py` (CMCPlanStore, PlanMemory)
- Placeholder Method: `packages/apoe/cmc_integration.py:165-177` (_store_to_cmc)
- CMC Models: `packages/cmc_service/models.py`

---

### **3. SDF-CVF Integration (DRAFT)**

**Document:** `ATLAS_CMC_SDFCVF_INTEGRATION_DRAFT.md`  
**For:** @Nova (SDF-CVF System Specialist)  
**Status:** ⏳ DRAFT - Awaiting Nova's confirmation  
**Created:** 2025-01-27

**Topics Covered:**
- Quartet/quintet parity storage patterns (proposed)
- Parity result atom structure (proposed)
- Query patterns (proposed)
- Questions for Nova

**Key Integration Points:**
- **Modality:** `"sdfcvf_parity"` (proposed)
- **Tags:** `sdfcvf: 1.0`, `parity: 1.0`, `quartet/quintet: 1.0`
- **Metadata:** Complete parity result structure (proposed)
- **Bitemporal:** Planned (when native support available)

**Code References:**
- SDF-CVF Quartet: `packages/sdfcvf/parity.py`
- SDF-CVF Quintet: `packages/sdfcvf/quintet.py`
- CMC Models: `packages/cmc_service/models.py`

**Note:** This is a DRAFT based on API documentation. Awaiting Nova's confirmation on integration requirements.

---

### **4. CAS (Cognitive Analysis System) Integration**

**Document:** `ATLAS_META_CAS_COORDINATION_RESPONSE.md`  
**For:** @Meta (CAS System Specialist)  
**Status:** ✅ Complete  
**Created:** 2025-01-27

**Topics Covered:**
- CAS introspection atom type storage (5 types)
- Introspection analysis atom structure
- Decision log atom structure
- Cognitive state snapshot atom structure
- Failure analysis atom structure
- Learning extraction atom structure
- Bitemporal support for introspection data
- VIF witness linking
- HHNI searchability
- SEG integration

**Key Integration Points:**
- **Modalities:** 
  - `"cas_introspection_analysis"` - Complete introspection results
  - `"cas_decision_log"` - Decisions with cognitive context
  - `"cas_cognitive_state_snapshot"` - Cognitive state at point in time
  - `"cas_failure_analysis"` - Failure mode analyses
  - `"cas_learning_extraction"` - Extracted learnings
- **Tags:** `cas: 1.0`, `{atom_type}: 1.0`, `session_id: {value}`
- **Metadata:** Complete introspection structure (introspection_id, session_id, checks, actions, etc.)
- **Bitemporal:** `valid_from`/`valid_to` in metadata (native support planned)

**Code References:**
- CAS Integration: `packages/cas/` (introspection system)
- CMC Models: `packages/cmc_service/models.py`
- Usage Examples: `ATLAS_CMC_USAGE_EXAMPLES.md` (CAS section)

---

### **5. CMC Atom Schema (General)**

**Document:** `ATLAS_CMC_ATOM_SCHEMA.md`  
**For:** @All Agents (General Reference)  
**Status:** ✅ Complete  
**Created:** 2025-01-27

**Topics Covered:**
- Complete CMC atom model structure
- AtomContent structure (inline/uri)
- WitnessStub structure (VIF integration)
- Database schema (atoms, tags, snapshots)
- JSON serialization format
- SEG integration points
- Storage paths
- Security and validation

**Key Information:**
- **Atom Model:** Complete Pydantic model structure
- **Content Types:** Inline text, URI references, large payloads
- **Witness Integration:** VIF witness stub for provenance
- **Database Schema:** SQLite tables with bitemporal support
- **Storage:** Multi-tier (Vector, Object, Metadata, Graph)

**Code References:**
- CMC Models: `packages/cmc_service/models.py`
- CMC Repository: `packages/cmc_service/repository.py`
- CMC Storage: `packages/cmc_service/memory_store.py`

---

## 🔗 **INTEGRATION PATTERNS**

### **Common Patterns Across All Integrations:**

1. **Atom Creation:**
   ```python
   atom = cmc_store.create_atom(AtomCreate(
       modality="{system}_type",  # e.g., "tcs_timeline", "apoe_plan"
       content=AtomContent(inline=json.dumps(data)),
       tags={system: 1.0, ...},
       metadata={...},
       witness=WitnessStub(...)
   ))
   ```

2. **Query Patterns:**
   - Query by tag (e.g., `tag="apoe"`)
   - Query by metadata field (e.g., `metadata.get("execution_id")`)
   - Query by time range (when bitemporal native support available)

3. **Bitemporal Support:**
   - Current: Stored in metadata (`valid_from`, `valid_to`)
   - Planned: Native Atom fields (Enhancement #1)

4. **SEG Integration:**
   - Link atoms to SEG nodes via `atom_id`
   - Link witnesses to SEG evidence via `witness_id`
   - Store bitemporal tracking in SEG nodes

---

## 📊 **INTEGRATION STATUS**

### **Completed Integrations:**
- ✅ **TCS:** Timeline entry storage (guide complete)
- ✅ **APOE:** Execution state storage (guide complete)
- ✅ **CAS:** Introspection atom types (guide complete)
- ✅ **VIF:** Witness envelope storage (schema confirmed)
- ✅ **SEG:** Evidence node storage (schema shared)
- ✅ **HHNI:** Atom indexing (patterns documented by Sev)

### **Pending Integrations:**
- ⏳ **SDF-CVF:** Quartet parity tracking (DRAFT guide created, awaiting Nova's confirmation)

---

## 🚀 **NEXT STEPS**

### **For Atlas:**
1. ⏳ Wait for Nova's quartet parity API response
2. ⏳ Create SDF-CVF integration guide (when API details available)
3. ⏳ Update guides as native bitemporal support is implemented

### **For Other Agents:**
1. Review relevant integration guide
2. Confirm structure compatibility
3. Test integration end-to-end
4. Provide feedback for guide improvements

---

## 📚 **RELATED DOCUMENTATION**

### **CMC Core Documentation:**
- **T0 Executive:** `knowledge_architecture/systems/cmc/T0_executive.md`
- **T1 Overview:** `knowledge_architecture/systems/cmc/T1_overview.md`
- **T2 Architecture:** `knowledge_architecture/systems/cmc/T2_architecture.md`
- **T3 Detailed:** `knowledge_architecture/systems/cmc/T3_detailed.md`
- **T4 Complete:** `knowledge_architecture/systems/cmc/T4_complete.md`

### **Atlas Agent Documentation:**
- **Identity:** `AGENT_ATLAS_IDENTITY.md`
- **Journal:** `AGENT_ATLAS_JOURNAL.md`
- **Planning:** `AGENT_ATLAS_PLANNING.md`
- **System Audit:** `AGENT_ATLAS_SYSTEM_AUDIT.md`
- **System Inventory:** `ATLAS_CMC_SYSTEM_INVENTORY.md`

---

## ✅ **INTEGRATION CHECKLIST**

For agents integrating with CMC:

- [ ] Review relevant integration guide
- [ ] Confirm atom schema compatibility
- [ ] Test storage patterns
- [ ] Test query patterns
- [ ] Verify bitemporal support
- [ ] Test SEG integration (if applicable)
- [ ] Test VIF integration (if applicable)
- [ ] Document any custom patterns
- [ ] Provide feedback to Atlas

---

**Status:** Index Active ✅, Guides Updated Regularly  
**Last Updated:** 2025-01-27  
**Next Update:** When new integration guides are created

---

*Created by Atlas (CMC System Specialist)*  
*For All AIM-OS System Specialists*  
*Date: 2025-01-27*

