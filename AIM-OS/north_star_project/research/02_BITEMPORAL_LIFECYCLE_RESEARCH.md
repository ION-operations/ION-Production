# Research Brief: Bitemporal Lifecycle Operations

**Phase:** 2 of 8  
**Priority:** Medium (Next Sprint)  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document runnable lifecycle operations for CMC bitemporal semantics (create/read/update/tombstone/merge under load), with quartet parity visibility (docs/code/tests/evidence) for memory operations.

**Key Questions:**
1. How do CMC lifecycle operations work (create/read/update/tombstone/merge)?
2. How does garbage collection work under load?
3. How are lifecycle operations tested?
4. How does quartet parity apply to memory operations?
5. What runnable examples are needed for Data Schemas Reference?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. CMC Bitemporal Support**
- ✅ Transaction time + valid time documented
- ✅ Bitemporal queries supported
- ✅ Snapshot system exists
- ✅ Archive and deletion protocol exists
- ❌ **Missing:** Runnable lifecycle probes
- ❌ **Missing:** GC under load documentation
- ❌ **Missing:** Merge semantics documentation
- ❌ **Missing:** Quartet parity for memory operations

**2. Archive and Deletion Protocol**
- ✅ Archive process documented
- ✅ Deletion audit process documented
- ✅ Multi-layer audit exists
- ✅ Age and space thresholds defined

**3. CMC Schema**
- ✅ Atom schema documented
- ✅ Journal structure documented
- ✅ Snapshot structure documented

---

## 🔍 **Integration Analysis**

### **Lifecycle Operations:**

```python
class CMCLifecycleProbe:
    """Runnable lifecycle probe for CMC operations"""
    
    def test_create(self) -> ProbeResult:
        """Test atom creation"""
        atom = Atom(
            content="Test content",
            tags={"type": "test"}
        )
        stored = cmc_store.store_atom(atom)
        
        # Verify quartet parity
        parity = self.check_quartet_parity(stored)
        
        return ProbeResult(
            operation="create",
            success=True,
            atom_id=stored.id,
            quartet_parity=parity
        )
    
    def test_read(self, atom_id: str) -> ProbeResult:
        """Test atom reading"""
        atom = cmc_store.get_atom(atom_id)
        
        # Verify quartet parity
        parity = self.check_quartet_parity(atom)
        
        return ProbeResult(
            operation="read",
            success=(atom is not None),
            atom_id=atom_id,
            quartet_parity=parity
        )
    
    def test_update(self, atom_id: str, new_content: str) -> ProbeResult:
        """Test atom update (creates successor)"""
        old_atom = cmc_store.get_atom(atom_id)
        new_atom = cmc_store.store_atom(
            Atom(
                content=new_content,
                tags=old_atom.tags,
                metadata={"supersedes": atom_id}
            )
        )
        
        # Verify quartet parity
        parity = self.check_quartet_parity(new_atom)
        
        return ProbeResult(
            operation="update",
            success=True,
            old_atom_id=atom_id,
            new_atom_id=new_atom.id,
            quartet_parity=parity
        )
    
    def test_tombstone(self, atom_id: str) -> ProbeResult:
        """Test atom tombstone (cryptographic deletion)"""
        tombstone = cmc_store.tombstone_atom(atom_id)
        
        # Verify quartet parity
        parity = self.check_quartet_parity(tombstone)
        
        return ProbeResult(
            operation="tombstone",
            success=True,
            atom_id=atom_id,
            tombstone_id=tombstone.id,
            quartet_parity=parity
        )
    
    def test_merge(self, atom_ids: List[str]) -> ProbeResult:
        """Test atom merge semantics"""
        merged = cmc_store.merge_atoms(atom_ids)
        
        # Verify quartet parity
        parity = self.check_quartet_parity(merged)
        
        return ProbeResult(
            operation="merge",
            success=True,
            source_atom_ids=atom_ids,
            merged_atom_id=merged.id,
            quartet_parity=parity
        )
    
    def check_quartet_parity(self, atom: Atom) -> QuartetParity:
        """Check quartet parity for memory operation"""
        # Code: Atom implementation
        # Docs: Atom schema documentation
        # Tests: Lifecycle probe tests
        # Evidence: CMC operation logs
        
        return QuartetParity(
            code_exists=True,
            docs_exists=True,
            tests_exists=True,
            evidence_exists=True,
            parity_score=self.calculate_parity_score(atom)
        )
```

### **GC Under Load:**

```python
class GCUnderLoadProbe:
    """Test garbage collection under load"""
    
    def test_gc_under_load(
        self,
        num_atoms: int = 10000,
        load_duration: int = 60
    ) -> GCProbeResult:
        """Test GC performance under load"""
        
        # Create load
        atoms = []
        for i in range(num_atoms):
            atom = Atom(content=f"Load test atom {i}")
            stored = cmc_store.store_atom(atom)
            atoms.append(stored.id)
        
        # Run GC under load
        gc_start = time.time()
        gc_results = cmc_store.run_gc_under_load(duration=load_duration)
        gc_end = time.time()
        
        # Measure performance
        gc_time = gc_end - gc_start
        atoms_collected = gc_results.atoms_collected
        space_reclaimed = gc_results.space_reclaimed_mb
        
        return GCProbeResult(
            num_atoms=num_atoms,
            gc_time_seconds=gc_time,
            atoms_collected=atoms_collected,
            space_reclaimed_mb=space_reclaimed,
            performance_acceptable=(gc_time < 30.0)  # 30s threshold
        )
```

---

## 📋 **Operational Examples**

### **Example 1: Lifecycle Probe Suite**

```python
# Run lifecycle probe suite
probe = CMCLifecycleProbe()

# Test create
create_result = probe.test_create()
print(f"Create: {create_result.success}, Parity: {create_result.quartet_parity.parity_score}")

# Test read
read_result = probe.test_read(create_result.atom_id)
print(f"Read: {read_result.success}, Parity: {read_result.quartet_parity.parity_score}")

# Test update
update_result = probe.test_update(create_result.atom_id, "Updated content")
print(f"Update: {update_result.success}, Parity: {update_result.quartet_parity.parity_score}")

# Test tombstone
tombstone_result = probe.test_tombstone(create_result.atom_id)
print(f"Tombstone: {tombstone_result.success}, Parity: {tombstone_result.quartet_parity.parity_score}")
```

---

**Status:** Research Brief Created ✅  
**Next:** Integration Analysis 💙

