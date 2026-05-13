# HHNI → CMC Integration Plan
**Date:** 2025-11-03  
**Author:** Aether (Autonomous Operation)  
**Status:** 📋 **PLAN CREATED**  
**Purpose:** Integrate HHNI indexes with CMC for persistent storage  

---

## 🎯 **INTEGRATION GOAL**

Persist HHNI indexes (315 files, 658,307 nodes) to CMC for:
- **Long-term storage** (survives restarts)
- **Bitemporal tracking** (version history)
- **Full provenance** (who/what/when indexed)
- **Cross-system access** (other systems can query)

---

## 📊 **CURRENT STATE**

### **HHNI Indexes Created:**
- **Idea Files:** 71 files → 117,008 nodes
- **Organized Files:** 244 files → 541,299 nodes
- **Total:** 315 files → 658,307 nodes

### **Index Files:**
- `knowledge_architecture/AETHER_MEMORY/investigations/HHNI_IDEA_INDEX.json`
- `knowledge_architecture/AETHER_MEMORY/investigations/HHNI_IDEA_INDEX_SUMMARY.json`
- `HHNI_FLOATING_FILES_INDEX.json`
- `HHNI_FLOATING_FILES_INDEX_SUMMARY.json`

---

## 🏗️ **INTEGRATION APPROACH**

### **Option 1: Store Index Metadata in CMC**
- Store summary data (file counts, node counts, indexing dates)
- Keep full index JSON files on disk
- Store references to disk files in CMC

**Pros:** Simple, fast, preserves existing structure  
**Cons:** Full index not in CMC, harder to query semantically

### **Option 2: Store Individual Nodes in CMC**
- Each of 658,307 nodes becomes a CMC atom
- Full hierarchical structure preserved
- Complete bitemporal tracking

**Pros:** Full CMC integration, bitemporal tracking, semantic querying  
**Cons:** 658,307 atoms to create, slower initial load

### **Option 3: Store Documents + Node Summaries**
- Store each document (315 files) as CMC atom
- Store node summaries (counts, metadata) per document
- Keep full node structure in HHNI index files

**Pros:** Balanced approach, good provenance, manageable scale  
**Cons:** Still need to query HHNI for full node details

---

## 🎯 **RECOMMENDED APPROACH: Hybrid**

### **Phase 1: Store Index Metadata (Quick Win)**
1. Store index summaries in CMC
   - Total files indexed
   - Total nodes created
   - Indexing timestamp
   - File paths indexed
2. Store document metadata per file
   - File path
   - Node count
   - Indexing date
   - Metadata (frontmatter, systems, tags)

**Result:** Full provenance in CMC, quick to implement

### **Phase 2: Store Node Hierarchies (Future Enhancement)**
1. Store root nodes for each document
2. Store key nodes (sections, important paragraphs)
3. Keep full node structure in HHNI for performance

**Result:** Balance between CMC integration and performance

---

## 📋 **IMPLEMENTATION STEPS**

### **Step 1: Create CMC Storage Script**
- Read HHNI index JSON files
- Extract metadata and summaries
- Store in CMC using `store_memory` MCP tool
- Include agent identity metadata

### **Step 2: Store Index Summaries**
- Store overall index statistics
- Store per-directory summaries
- Store per-category summaries

### **Step 3: Store Document Metadata**
- For each indexed file, store:
  - File path
  - Node count
  - Indexing metadata
  - Systems referenced
  - Tags
  - Frontmatter data

### **Step 4: Create Query Interface**
- Query CMC for indexed files
- Query CMC for index statistics
- Link to HHNI for semantic search

### **Step 5: Test & Validate**
- Verify all metadata stored correctly
- Test querying capabilities
- Validate bitemporal tracking

---

## 🔧 **TECHNICAL DETAILS**

### **CMC Storage Format:**
```python
{
    "content": "HHNI Index Summary",
    "metadata": {
        "index_type": "idea_files" | "organized_files",
        "total_files": 71,
        "total_nodes": 117008,
        "indexed_at": "2025-11-03T...",
        "files": [...],
        "agent": "aether"
    },
    "tags": {
        "type": "hhni_index",
        "index_type": "idea_files",
        "agent": "aether"
    }
}
```

### **MCP Tool Usage:**
- Use `mcp_lucid-mcp_store_memory` to store index metadata
- Include agent identity (`agent_name: "aether"`)
- Tag appropriately for retrieval

---

## 🚀 **NEXT STEPS**

1. **Create CMC storage script** (`scripts/store_hhni_indexes_to_cmc.py`)
2. **Store index summaries** (overall statistics)
3. **Store document metadata** (per-file information)
4. **Create query interface** (retrieve via CMC)
5. **Test semantic search** (verify HHNI search works)

---

**Status:** 📋 **PLAN CREATED**  
**Next:** Implement CMC storage script  
**Priority:** High (completes 98% → 100%)  
**Confidence:** 0.85 (High - Clear plan, straightforward implementation)
