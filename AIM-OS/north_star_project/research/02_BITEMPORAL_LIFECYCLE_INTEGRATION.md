# Integration Analysis: Bitemporal Lifecycle Operations

**Phase:** 2 of 8  
**Priority:** Medium  
**Status:** Analysis Complete  
**Date:** 2025-11-07

---

## 🎯 **Integration Objective**

**Goal:** Integrate runnable lifecycle operations (create/read/update/tombstone/merge) with quartet parity visibility, GC under load, and merge semantics into CMC bitemporal storage system.

**Key Integration Points:**
1. CMC Lifecycle Operations → Quartet Parity Validation
2. GC Under Load → Performance Monitoring
3. Merge Semantics → Bitemporal Coalescing
4. Lifecycle Probes → Operational Examples

---

## 🔗 **System Integration Map**

### **CMC Lifecycle Enhancement**

**Current Lifecycle Flow:**
```
Create → Store → Read → Update (supersede) → Tombstone
```

**Enhanced Lifecycle Flow (with Quartet Parity):**
```
Create → Store → Quartet Parity Check ← NEW
           ↓
         Read → Quartet Parity Check ← NEW
           ↓
         Update → Quartet Parity Check ← NEW
           ↓
         Merge → Quartet Parity Check ← NEW
           ↓
         Tombstone → Quartet Parity Check ← NEW
           ↓
         GC Under Load → Performance Monitoring ← NEW
```

---

## 🏗️ **Technical Integration**

### **1. CMC Lifecycle Operations with Quartet Parity**

**Enhanced Atom Model:**
```python
class Atom(BaseModel):
    # ... existing fields ...
    
    # Quartet Parity Tracking (NEW)
    quartet_parity: Optional[QuartetParity] = None
    
    def check_quartet_parity(self) -> QuartetParity:
        """Check quartet parity for this atom"""
        return QuartetParity(
            code_exists=self._code_exists(),
            docs_exists=self._docs_exists(),
            tests_exists=self._tests_exists(),
            evidence_exists=self._evidence_exists(),
            parity_score=self._calculate_parity_score()
        )
    
    def _code_exists(self) -> bool:
        """Check if code implementation exists"""
        # Check if atom has implementation in CMC store
        return hasattr(cmc_store, 'get_atom')
    
    def _docs_exists(self) -> bool:
        """Check if documentation exists"""
        # Check if atom schema is documented
        return self._schema_documented()
    
    def _tests_exists(self) -> bool:
        """Check if tests exist"""
        # Check if lifecycle probe tests exist
        return self._probe_tests_exist()
    
    def _evidence_exists(self) -> bool:
        """Check if evidence exists"""
        # Check if CMC operation logs exist
        return self._operation_logs_exist()
```

**Lifecycle Probe System:**
```python
class CMCLifecycleProbe:
    """Runnable lifecycle probe for CMC operations"""
    
    def __init__(self, cmc_store: CMCStore):
        self.cmc_store = cmc_store
        self.parity_validator = QuartetParityValidator()
    
    def test_create(self, content: str, tags: Dict[str, str]) -> ProbeResult:
        """Test atom creation with quartet parity"""
        
        # Create atom
        atom = Atom(
            content=content,
            tags=tags,
            valid_from=datetime.now(),
            transaction_time=datetime.now()
        )
        
        # Store atom
        stored = self.cmc_store.store_atom(atom)
        
        # Check quartet parity
        parity = self.parity_validator.validate(stored)
        
        # Create VIF witness
        vif_witness = VIF.create_with_lifecycle_operation(
            operation="create",
            atom_id=stored.id,
            quartet_parity=parity
        )
        
        return ProbeResult(
            operation="create",
            success=True,
            atom_id=stored.id,
            quartet_parity=parity,
            vif_witness_id=vif_witness.id
        )
    
    def test_read(self, atom_id: str) -> ProbeResult:
        """Test atom reading with quartet parity"""
        
        # Read atom
        atom = self.cmc_store.get_atom(atom_id)
        
        if atom is None:
            return ProbeResult(
                operation="read",
                success=False,
                error="Atom not found"
            )
        
        # Check quartet parity
        parity = self.parity_validator.validate(atom)
        
        return ProbeResult(
            operation="read",
            success=True,
            atom_id=atom_id,
            quartet_parity=parity
        )
    
    def test_update(self, atom_id: str, new_content: str) -> ProbeResult:
        """Test atom update (creates successor) with quartet parity"""
        
        # Get old atom
        old_atom = self.cmc_store.get_atom(atom_id)
        if old_atom is None:
            return ProbeResult(
                operation="update",
                success=False,
                error="Atom not found"
            )
        
        # Create successor atom
        new_atom = Atom(
            content=new_content,
            tags=old_atom.tags,
            metadata={"supersedes": atom_id},
            valid_from=datetime.now(),
            transaction_time=datetime.now()
        )
        
        # Store successor
        stored = self.cmc_store.store_atom(new_atom)
        
        # Tombstone old atom
        self.cmc_store.tombstone_atom(atom_id)
        
        # Check quartet parity
        parity = self.parity_validator.validate(stored)
        
        return ProbeResult(
            operation="update",
            success=True,
            old_atom_id=atom_id,
            new_atom_id=stored.id,
            quartet_parity=parity
        )
    
    def test_tombstone(self, atom_id: str) -> ProbeResult:
        """Test atom tombstone with quartet parity"""
        
        # Tombstone atom
        tombstone = self.cmc_store.tombstone_atom(atom_id)
        
        # Check quartet parity
        parity = self.parity_validator.validate(tombstone)
        
        return ProbeResult(
            operation="tombstone",
            success=True,
            atom_id=atom_id,
            tombstone_id=tombstone.id,
            quartet_parity=parity
        )
    
    def test_merge(self, atom_ids: List[str]) -> ProbeResult:
        """Test atom merge semantics with quartet parity"""
        
        # Get source atoms
        source_atoms = [self.cmc_store.get_atom(aid) for aid in atom_ids]
        
        # Merge atoms using bitemporal coalescing
        merged = self.cmc_store.merge_atoms(atom_ids)
        
        # Check quartet parity
        parity = self.parity_validator.validate(merged)
        
        return ProbeResult(
            operation="merge",
            success=True,
            source_atom_ids=atom_ids,
            merged_atom_id=merged.id,
            quartet_parity=parity
        )
```

---

### **2. GC Under Load Integration**

**GC Performance Monitor:**
```python
class GCUnderLoadProbe:
    """Test garbage collection under load"""
    
    def __init__(self, cmc_store: CMCStore):
        self.cmc_store = cmc_store
        self.performance_threshold = 30.0  # 30 seconds
    
    def test_gc_under_load(
        self,
        num_atoms: int = 10000,
        load_duration: int = 60
    ) -> GCProbeResult:
        """Test GC performance under load"""
        
        # Create load
        atoms = []
        for i in range(num_atoms):
            atom = Atom(
                content=f"Load test atom {i}",
                tags={"type": "load_test"},
                valid_from=datetime.now(),
                transaction_time=datetime.now()
            )
            stored = self.cmc_store.store_atom(atom)
            atoms.append(stored.id)
        
        # Run GC under load
        gc_start = time.time()
        gc_results = self.cmc_store.run_gc_under_load(duration=load_duration)
        gc_end = time.time()
        
        # Measure performance
        gc_time = gc_end - gc_start
        atoms_collected = gc_results.atoms_collected
        space_reclaimed = gc_results.space_reclaimed_mb
        
        # Check performance threshold
        performance_acceptable = (gc_time < self.performance_threshold)
        
        return GCProbeResult(
            num_atoms=num_atoms,
            gc_time_seconds=gc_time,
            atoms_collected=atoms_collected,
            space_reclaimed_mb=space_reclaimed,
            performance_acceptable=performance_acceptable,
            performance_threshold=self.performance_threshold
        )
```

**CMC Store GC Enhancement:**
```python
class CMCStore:
    """Enhanced CMC store with GC under load"""
    
    def run_gc_under_load(self, duration: int = 60) -> GCResults:
        """Run garbage collection under load"""
        
        gc_start = time.time()
        atoms_collected = 0
        space_reclaimed_mb = 0.0
        
        # Get tombstoned atoms eligible for GC
        tombstoned_atoms = self.get_tombstoned_atoms()
        
        # Filter by age threshold (90 days)
        eligible_atoms = [
            atom for atom in tombstoned_atoms
            if (datetime.now() - atom.tombstone_time).days >= 90
        ]
        
        # Collect atoms
        for atom in eligible_atoms:
            # Check dependency
            if not self.has_active_dependencies(atom.id):
                # Collect atom
                self.collect_atom(atom.id)
                atoms_collected += 1
                space_reclaimed_mb += atom.size_mb
        
        gc_end = time.time()
        
        return GCResults(
            atoms_collected=atoms_collected,
            space_reclaimed_mb=space_reclaimed_mb,
            gc_time_seconds=gc_end - gc_start
        )
```

---

### **3. Merge Semantics Integration**

**Bitemporal Coalescing:**
```python
class CMCMergeEngine:
    """Merge engine with bitemporal coalescing"""
    
    def merge_atoms(self, atom_ids: List[str]) -> Atom:
        """Merge atoms using bitemporal coalescing"""
        
        # Get source atoms
        source_atoms = [self.cmc_store.get_atom(aid) for aid in atom_ids]
        
        # Sort by valid_from
        sorted_atoms = sorted(source_atoms, key=lambda a: a.valid_from)
        
        # Coalesce overlapping valid times
        coalesced = self._temporal_coalesce(sorted_atoms)
        
        # Merge content
        merged_content = self._merge_content(coalesced)
        
        # Merge tags
        merged_tags = self._merge_tags(coalesced)
        
        # Create merged atom
        merged = Atom(
            content=merged_content,
            tags=merged_tags,
            metadata={
                "merged_from": atom_ids,
                "merge_timestamp": datetime.now().isoformat()
            },
            valid_from=coalesced[0].valid_from,
            valid_to=coalesced[-1].valid_to,
            transaction_time=datetime.now()
        )
        
        # Store merged atom
        stored = self.cmc_store.store_atom(merged)
        
        # Link to source atoms in SEG
        self._link_merge_to_seg(stored, atom_ids)
        
        return stored
    
    def _temporal_coalesce(self, atoms: List[Atom]) -> List[Atom]:
        """Coalesce overlapping valid time intervals"""
        coalesced = []
        
        for atom in atoms:
            if not coalesced:
                coalesced.append(atom)
            else:
                last = coalesced[-1]
                # Check if valid times overlap
                if atom.valid_from <= last.valid_to:
                    # Merge: extend valid_time_to to max
                    last.valid_to = max(last.valid_to, atom.valid_to)
                else:
                    coalesced.append(atom)
        
        return coalesced
```

---

### **4. Quartet Parity Validator**

**Quartet Parity Validation:**
```python
class QuartetParityValidator:
    """Validate quartet parity for memory operations"""
    
    def validate(self, atom: Atom) -> QuartetParity:
        """Validate quartet parity for atom"""
        
        # Check code existence
        code_exists = self._check_code_exists(atom)
        
        # Check docs existence
        docs_exists = self._check_docs_exists(atom)
        
        # Check tests existence
        tests_exists = self._check_tests_exists(atom)
        
        # Check evidence existence
        evidence_exists = self._check_evidence_exists(atom)
        
        # Calculate parity score
        parity_score = self._calculate_parity_score(
            code_exists, docs_exists, tests_exists, evidence_exists
        )
        
        return QuartetParity(
            code_exists=code_exists,
            docs_exists=docs_exists,
            tests_exists=tests_exists,
            evidence_exists=evidence_exists,
            parity_score=parity_score
        )
    
    def _calculate_parity_score(
        self,
        code: bool,
        docs: bool,
        tests: bool,
        evidence: bool
    ) -> float:
        """Calculate quartet parity score"""
        score = 0.0
        if code:
            score += 0.25
        if docs:
            score += 0.25
        if tests:
            score += 0.25
        if evidence:
            score += 0.25
        return score
```

---

## 🔄 **Execution Flow Integration**

### **Lifecycle-Aware Atom Operations:**

```python
def create_atom_with_parity(content: str, tags: Dict[str, str]) -> Atom:
    """Create atom with quartet parity validation"""
    
    # Create lifecycle probe
    probe = CMCLifecycleProbe(cmc_store)
    
    # Test create
    result = probe.test_create(content, tags)
    
    # Verify parity
    if result.quartet_parity.parity_score < 0.90:
        raise QuartetParityError(
            f"Quartet parity insufficient: {result.quartet_parity.parity_score}"
        )
    
    return cmc_store.get_atom(result.atom_id)
```

---

## 🧪 **Testing Integration**

### **Test 1: Lifecycle Probe Suite**

```python
def test_lifecycle_probe_suite():
    """Test complete lifecycle probe suite"""
    
    probe = CMCLifecycleProbe(cmc_store)
    
    # Test create
    create_result = probe.test_create("Test content", {"type": "test"})
    assert create_result.success
    assert create_result.quartet_parity.parity_score >= 0.90
    
    # Test read
    read_result = probe.test_read(create_result.atom_id)
    assert read_result.success
    
    # Test update
    update_result = probe.test_update(create_result.atom_id, "Updated content")
    assert update_result.success
    
    # Test tombstone
    tombstone_result = probe.test_tombstone(create_result.atom_id)
    assert tombstone_result.success
```

---

## 📋 **Implementation Checklist**

- [ ] Create QuartetParity model
- [ ] Create QuartetParityValidator class
- [ ] Enhance Atom model with quartet_parity field
- [ ] Create CMCLifecycleProbe class
- [ ] Implement test_create, test_read, test_update, test_tombstone, test_merge
- [ ] Create GCUnderLoadProbe class
- [ ] Enhance CMCStore with run_gc_under_load method
- [ ] Create CMCMergeEngine class
- [ ] Implement temporal_coalesce algorithm
- [ ] Create integration tests
- [ ] Create operational examples
- [ ] Document in Data Schemas Reference

---

**Status:** Integration Analysis Complete ✅  
**Next:** Implementation Planning 💙

