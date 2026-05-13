# HHNI Indexing Analysis

**Date:** 2025-01-27  
**Status:** 🔍 **ANALYSIS COMPLETE** - Solution identified  
**Agent:** Aether

---

## 🎯 **CURRENT STATUS**

**HHNI Status:**
- `index_nodes: 0` - No nodes indexed
- `cmc_atoms_total: 1000` - 1000 atoms in CMC
- `cmc_atoms_hhni_tagged: 0` - No atoms have `hhni_index` tag
- `index_available: false` - Index not available
- `retriever_available: true` - Retriever is available but has nothing to retrieve

---

## 🔍 **ROOT CAUSE ANALYSIS**

### **Problem 1: Wrong Indexing Method**

The MCP server's `store_memory` tool and `_build_hhni_index()` method use:
- `HierarchicalIndex.index_document()` - Simple in-memory index (not real HHNI)

But the real HHNI system requires:
- `build_hhni_for_atom()` - Creates proper HHNI nodes with DGraph/Qdrant
- DGraph client for graph storage
- Qdrant client for vector embeddings
- Creates hierarchical nodes (doc → paragraph → sentence)

### **Problem 2: No Atoms Tagged**

The `_build_hhni_index()` method only indexes atoms with `hhni_index` tag:
```python
hhni_atoms = [a for a in atoms if 'hhni_index' in getattr(a, 'tags', {})]
```

But **0 atoms** have this tag, so nothing gets indexed.

### **Problem 3: Missing Integration**

The MCP server doesn't use `MemoryStore.create_atom_with_hhni()` which properly builds HHNI nodes. It uses `create_atom()` and then tries to index with the wrong method.

---

## ✅ **SOLUTION**

### **Option 1: Create Batch Indexing Tool (Recommended)**

Create a new MCP tool `index_atoms_in_hhni` that:
1. Gets DGraph/Qdrant clients from MemoryStore
2. Iterates through CMC atoms (or filtered subset)
3. Calls `build_hhni_for_atom()` for each atom
4. Returns indexing statistics

**Implementation:**
```python
def index_atoms_in_hhni(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Index existing CMC atoms into HHNI using proper build_hhni_for_atom()"""
    if not self.memory:
        return {"success": False, "error": "Memory store not initialized"}
    
    try:
        # Get HHNI clients from MemoryStore
        dgraph_client, qdrant_client = self.memory._get_hhni_clients()
        
        # Import build function
        from hhni.indexer import build_hhni_for_atom
        
        # Get atoms to index
        limit = arguments.get("limit", 100)
        filter_tag = arguments.get("filter_tag")  # Optional: only index atoms with this tag
        
        atoms = list(self.memory.list_atoms(limit=limit))
        if filter_tag:
            atoms = [a for a in atoms if filter_tag in getattr(a, 'tags', {})]
        
        # Index each atom
        indexed_count = 0
        failed_count = 0
        total_nodes = 0
        
        for atom in atoms:
            try:
                nodes = build_hhni_for_atom(
                    atom=atom,
                    dgraph_client=dgraph_client,
                    qdrant_client=qdrant_client,
                    correlation_id=f"mcp_index_{atom.id}"
                )
                indexed_count += 1
                total_nodes += len(nodes)
            except Exception as e:
                log(f"Failed to index atom {atom.id}: {e}")
                failed_count += 1
        
        return {
            "success": True,
            "atoms_indexed": indexed_count,
            "atoms_failed": failed_count,
            "total_nodes_created": total_nodes,
            "message": f"Indexed {indexed_count} atoms, created {total_nodes} HHNI nodes"
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to index atoms: {str(e)}"}
```

### **Option 2: Update store_memory to Use create_atom_with_hhni**

Modify `store_memory` to use `create_atom_with_hhni()` when a tag indicates HHNI indexing:
- Check for `hhni_index: true` or `priority >= 0.6` tag
- Use `create_atom_with_hhni(build_hhni=True)` instead of `create_atom()`

**Pros:** Automatic indexing for new atoms  
**Cons:** Doesn't help existing atoms

### **Option 3: Add hhni_index Tag to Important Atoms**

Create a tool to add `hhni_index: true` tag to atoms that should be indexed, then let `_build_hhni_index()` handle it (but still need to fix the indexing method).

---

## 📊 **RECOMMENDED APPROACH**

**Phase 1: Create Batch Indexing Tool**
- Add `index_atoms_in_hhni` MCP tool
- Use proper `build_hhni_for_atom()` method
- Index existing atoms in batches

**Phase 2: Update store_memory**
- Use `create_atom_with_hhni()` for new atoms when appropriate
- Check for `hhni_index` or `priority >= 0.6` tags

**Phase 3: Update _build_hhni_index**
- Replace `HierarchicalIndex.index_document()` with proper `build_hhni_for_atom()`
- Or remove it if batch indexing tool handles everything

---

## 🎯 **IMMEDIATE NEXT STEPS**

1. **Create `index_atoms_in_hhni` tool** - Batch index existing atoms
2. **Test with small batch** - Index 10-20 atoms first
3. **Verify HHNI status** - Check that nodes appear
4. **Update store_memory** - Use proper HHNI indexing for new atoms

---

## 📝 **NOTES**

- The real HHNI system uses DGraph for graph structure and Qdrant for vector embeddings
- `build_hhni_for_atom()` creates hierarchical nodes: doc → paragraph → sentence
- Each level has embeddings stored in Qdrant
- The simple `HierarchicalIndex` is just an in-memory fallback, not the real system

---

**Status:** ✅ **Analysis complete - ready for implementation**  
**Confidence:** 0.90 (high - clear solution identified)  
**Next:** Implement `index_atoms_in_hhni` tool

---

*Created by Aether*  
*2025-01-27*

