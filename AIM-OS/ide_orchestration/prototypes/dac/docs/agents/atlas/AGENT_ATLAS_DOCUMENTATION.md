# Atlas - CMC System Specialist Documentation

**Purpose:** Consolidated CMC system knowledge  
**Status:** Active  
**Created:** 2025-01-27  
**Last Updated:** 2025-01-27

---

## 📚 **QUICK LINKS**

### **Integration Guides:**
- **Master Index:** `ATLAS_CMC_INTEGRATION_GUIDES_INDEX.md` - All integration guides
- **TCS Integration:** `ATLAS_CMC_TCS_INTEGRATION.md` - Timeline entry storage
- **APOE Integration:** `ATLAS_CMC_APOE_INTEGRATION.md` - Execution state storage
- **Atom Schema:** `ATLAS_CMC_ATOM_SCHEMA.md` - Complete atom schema

### **Phase 3 Deliverables:**
- **System Inventory:** `ATLAS_CMC_SYSTEM_INVENTORY.md` - Complete system inventory
- **System Audit:** `AGENT_ATLAS_SYSTEM_AUDIT.md` - Phase 3 audit report
- **Enhancement Plans:** See `AGENT_ATLAS_PLANNING.md` for all enhancement plans
- **Status Summary:** `ATLAS_STATUS_SUMMARY.md` - Current status and next steps
- **Complete Work Summary:** `ATLAS_COMPLETE_WORK_SUMMARY.md` - Comprehensive summary of all work
- **Usage Examples:** `ATLAS_CMC_USAGE_EXAMPLES.md` - Practical integration examples
- **Final Status Report:** `ATLAS_FINAL_STATUS_REPORT.md` - Comprehensive final status
- **Verification Readiness:** `ATLAS_VERIFICATION_READINESS.md` - Verification checklist and readiness summary

---

## 🔧 **SUBSYSTEM INTEGRATION PRIORITIES**

### **CMC Subsystems (4):**

1. **Atoms** - Fundamental memory units
   - **Status:** ✅ Complete - Integration points verified
   - **Critical Integrations:** HHNI (Hierarchical Index), VIF (Witness), SEG (Graph Schema)
   - **Documentation:** `knowledge_architecture/systems/cmc/components/atoms/`

2. **Pipelines** - Data flow orchestration (Write/Read pipelines)
   - **Status:** ✅ Complete - Integration points verified
   - **Critical Integrations:** HHNI, VIF, SEG, APOE, SDF-CVF, TCS
   - **Documentation:** `knowledge_architecture/systems/cmc/components/pipelines/`

3. **Snapshots** - Immutable, content-addressed atom bundles
   - **Status:** ✅ Complete - Integration points verified
   - **Critical Integrations:** APOE, SDF-CVF, TCS
   - **Documentation:** `knowledge_architecture/systems/cmc/components/snapshots/`

4. **Storage** - Multi-tier persistence (Vector, Object, Metadata, Graph)
   - **Status:** ✅ Complete - Integration points verified
   - **Critical Integrations:** HHNI, SEG, APOE, VIF, SDF-CVF, TCS
   - **Documentation:** `knowledge_architecture/systems/cmc/components/storage/`

### **External Subsystem Integration Status:**

| External System | Subsystem | Integration Status | Priority | Notes |
|----------------|-----------|-------------------|----------|-------|
| **HHNI** | Hierarchical Index | ✅ Verified | P0 | CMC atoms indexed at all 6 levels |
| **HHNI** | Retrieval | ✅ Verified | P0 | CMC provides atoms for retrieval |
| **VIF** | Witness | ✅ Verified | P0 | CMC stores VIF witnesses with atoms |
| **SEG** | Graph Schema | ✅ Verified | P0 | CMC atoms referenced by SEG nodes |
| **APOE** | Roles | ✅ Verified | P0 | CMC stores APOE execution traces |
| **SDF-CVF** | Quartet | ✅ Verified | P0 | CMC stores quartet snapshots |
| **TCS** | Timeline Tracker | ✅ Verified | P0 | CMC stores timeline nodes as atoms |

**Reference:** `ide_orchestration/prototypes/dac/docs/SUBSYSTEM_INTEGRATION_VERIFICATION_PLAN.md` (Atlas section)

---

## 📚 **CMC SYSTEM OVERVIEW**

### **What is CMC?**

**CMC (Context Memory Core)** is the foundational memory substrate for AIM-OS, providing:
- Bitemporal storage (transaction time + valid time)
- Atom-based memory units with semantic metadata
- Immutable snapshots for time-travel queries
- Complete provenance tracking via VIF witnesses

### **Core Components:**

1. **Memory Store** - Main storage interface
2. **Bitemporal Engine** - Time-travel query engine
3. **Provenance/Witness Store** - VIF witness integration
4. **Snapshot Manager** - Immutable snapshot creation
5. **API/Schema Layer** - Public API and data models
6. **Storage Layers** - Vector, Object, Metadata, Graph stores

---

## 🔗 **INTEGRATION POINTS**

### **Bidirectional Integrations:**

1. **HHNI** - Semantic indexing and retrieval
   - CMC → HHNI: Atoms indexed for semantic search
   - HHNI → CMC: Retrieved atoms stored in CMC

2. **VIF** - Witness storage and provenance
   - CMC → VIF: Witnesses stored as atoms
   - VIF → CMC: Witness envelopes linked to atoms

3. **SEG** - Evidence graph storage
   - CMC → SEG: Evidence stored as atoms
   - SEG → CMC: Graph nodes/edges stored in CMC

4. **APOE** - Execution plan storage
   - CMC → APOE: Plans stored as atoms
   - APOE → CMC: Execution traces stored in CMC

5. **SDF-CVF** - Change tracking and quartet parity
   - CMC → SDF-CVF: Changes tracked in CMC
   - SDF-CVF → CMC: Quartet parity metadata stored

---

## 📊 **DATA MODELS**

### **Atom Schema:**

See `ATLAS_CMC_ATOM_SCHEMA.md` for complete schema documentation.

**Key Fields:**
- `id` - Unique identifier
- `modality` - Content type (text, code, etc.)
- `content` - AtomContent (inline/uri/media_type)
- `tags` - Semantic tags (key → weight)
- `metadata` - Additional metadata
- `embedding` - Vector embedding
- `witness` - WitnessStub (VIF provenance)
- `created_at` - Creation timestamp
- `hash` - Content hash
- `snapshot_ids` - Snapshots containing this atom

---

## 🗄️ **STORAGE LAYERS**

1. **Vector Store (Qdrant)** - Embeddings for semantic search
2. **Object Store (Filesystem/S3)** - Large payloads
3. **Metadata Store (SQLite)** - Atoms and snapshots
4. **Graph Store (DGraph)** - SEG edges

---

## 🔧 **KEY OPERATIONS**

### **Atom Creation:**
```python
atom = store.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="content"),
    tags={"priority": 1.0}
))
```

### **Bitemporal Queries:**
```python
engine = BitemporalQueryEngine(repo)
nodes = engine.query_nodes_as_of(datetime.now())
```

### **Snapshot Management:**
```python
snapshot_id = store.create_snapshot(note="Session state")
atoms = store.replay_snapshot(snapshot_id)
```

---

## 📖 **REFERENCE DOCUMENTATION**

### **System Documentation:**
- T0-T6: Executive through Academic reference
- L0-L4: Legacy documentation (being migrated)
- Component READMEs: Detailed component docs

### **Implementation:**
- `packages/cmc_service/` - Core implementation
- `packages/cmc_service/models.py` - Data models
- `packages/cmc_service/memory_store.py` - Main API
- `packages/cmc_service/repository.py` - Storage layer

---

**Status:** Documentation Active ✅  
**Purpose:** Consolidated CMC knowledge for Atlas

---

*Atlas - CMC System Specialist*  
*Building the foundation of AI consciousness memory*

