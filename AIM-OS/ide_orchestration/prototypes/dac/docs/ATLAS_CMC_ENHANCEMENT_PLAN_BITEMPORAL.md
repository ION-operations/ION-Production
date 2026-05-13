# Atlas - CMC Bitemporal Native Support Enhancement Plan

**Agent:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Planning  
**Enhancement:** High Priority #1 - Bitemporal Native Support  
**Estimated Effort:** 2-3 days

---

## 📋 **EXECUTIVE SUMMARY**

**Current State:** Bitemporal time stored in metadata, not native CMC API  
**Target State:** Native `valid_from`/`valid_to` fields in Atom model  
**Impact:** Enables native bitemporal queries without metadata parsing  
**Priority:** High

---

## 🔍 **CURRENT STATE ANALYSIS**

### **What Exists:**

1. **Repository Bitemporal Support:**
   - `mpd_nodes` table has: `tt_start`, `tt_end`, `vt_start`, `vt_end` fields
   - `mpd_edges` table has: `tt_start`, `tt_end`, `vt_start`, `vt_end` fields
   - Indexes created on `tt_start` for both tables
   - **Location:** `repository.py:109-129`

2. **Bitemporal Query Engine:**
   - `BitemporalQueryEngine` class exists
   - Queries work on MPD nodes/edges, not directly on atoms
   - **Location:** `bitemporal_queries.py`

3. **CrossModelAtom Support:**
   - `CrossModelAtom` class has `valid_from` and `valid_to` fields
   - **Location:** `cross_model_atoms.py:366-367`

4. **MCP Tool Support:**
   - `store_memory` tool accepts `valid_from`/`valid_to` parameters
   - Stores bitemporal info in metadata
   - **Location:** `lucid_mcp_server.py:1907-1952`

### **What's Missing:**

1. **Atom Model:**
   - No `valid_from`/`valid_to` fields in `Atom` class
   - No `transaction_time` field (uses `created_at` instead)
   - **Location:** `models.py:105-141`

2. **Repository Atom Storage:**
   - `atoms` table doesn't have bitemporal fields
   - Only `created_at` timestamp exists
   - **Location:** `repository.py:38-50`

3. **API Integration:**
   - `create_atom()` doesn't accept bitemporal parameters
   - No native bitemporal query methods on atoms

---

## 🎯 **ENHANCEMENT DESIGN**

### **Step 1: Update Atom Model**

**File:** `packages/cmc_service/models.py`

**Changes:**
```python
@dataclass
class Atom(AtomCreate):
    id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str = ""
    witness: WitnessStub = field(default_factory=WitnessStub)
    snapshot_ids: List[str] = field(default_factory=list)
    
    # NEW: Bitemporal fields
    transaction_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
```

**Rationale:**
- `transaction_time` = when atom was recorded (currently `created_at`)
- `valid_from` = when atom became valid in reality (defaults to `transaction_time`)
- `valid_to` = when atom stopped being valid (None = open-ended)

### **Step 2: Update Repository Schema**

**File:** `packages/cmc_service/repository.py`

**Changes:**
```python
CREATE TABLE IF NOT EXISTS atoms (
    id TEXT PRIMARY KEY,
    modality TEXT NOT NULL,
    inline TEXT,
    uri TEXT,
    media_type TEXT NOT NULL,
    hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    transaction_time TEXT NOT NULL,  # NEW
    valid_from TEXT,                  # NEW
    valid_to TEXT,                     # NEW
    metadata TEXT,
    witness TEXT,
    embedding BLOB
)

CREATE INDEX IF NOT EXISTS idx_atoms_transaction_time ON atoms(transaction_time)
CREATE INDEX IF NOT EXISTS idx_atoms_valid_from ON atoms(valid_from)
CREATE INDEX IF NOT EXISTS idx_atoms_valid_to ON atoms(valid_to)
```

**Migration:**
- Add migration script to populate `transaction_time` from `created_at`
- Set `valid_from` = `created_at` for existing atoms
- Set `valid_to` = NULL for existing atoms (open-ended)

### **Step 3: Update MemoryStore API**

**File:** `packages/cmc_service/memory_store.py`

**Changes:**
```python
def create_atom(
    self,
    payload: AtomCreate,
    *,
    correlation_id: Optional[str] = None,
    transaction_time: Optional[datetime] = None,  # NEW
    valid_from: Optional[datetime] = None,         # NEW
    valid_to: Optional[datetime] = None,            # NEW
) -> Atom:
    """Create atom with native bitemporal support"""
    # Set defaults
    if transaction_time is None:
        transaction_time = datetime.now(timezone.utc)
    if valid_from is None:
        valid_from = transaction_time
    
    # Create atom with bitemporal fields
    atom = Atom(
        ...,
        transaction_time=transaction_time,
        valid_from=valid_from,
        valid_to=valid_to,
    )
```

### **Step 4: Add Bitemporal Query Methods**

**File:** `packages/cmc_service/memory_store.py`

**New Methods:**
```python
def query_atoms_as_of(
    self,
    as_of_time: datetime,
    *,
    use_transaction_time: bool = False,
    tag: Optional[str] = None,
    limit: int = 100,
) -> List[Atom]:
    """Query atoms as they existed at a specific point in time"""
    
def query_atoms_in_range(
    self,
    start_time: datetime,
    end_time: datetime,
    *,
    use_transaction_time: bool = False,
    tag: Optional[str] = None,
) -> List[Atom]:
    """Query atoms valid during a time range"""
```

### **Step 5: Update MCP Tool**

**File:** `lucid_mcp_server.py`

**Changes:**
- Update `store_memory` to use native bitemporal fields instead of metadata
- Remove metadata bitemporal storage
- Use native API fields directly

---

## 📊 **IMPACT ANALYSIS**

### **Breaking Changes:**
- ⚠️ Atom model schema change (requires migration)
- ⚠️ Repository schema change (requires migration)
- ⚠️ API signature change (backward compatible with defaults)

### **Benefits:**
- ✅ Native bitemporal queries without metadata parsing
- ✅ Better performance (indexed queries)
- ✅ Cleaner API (no metadata workarounds)
- ✅ Type safety (datetime fields vs string metadata)

### **Risks:**
- ⚠️ Migration complexity (existing atoms need bitemporal values)
- ⚠️ Test updates required (all atom creation tests)
- ⚠️ Documentation updates required

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests:**
1. Atom creation with bitemporal fields
2. Atom creation without bitemporal fields (defaults)
3. Bitemporal query correctness
4. Migration script validation

### **Integration Tests:**
1. End-to-end bitemporal workflow
2. MCP tool integration
3. Repository migration
4. Query performance

### **Migration Tests:**
1. Existing atoms get correct bitemporal values
2. No data loss during migration
3. Backward compatibility maintained

---

## 📝 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Model Updates**
- [ ] Add bitemporal fields to Atom model
- [ ] Update AtomCreate to accept bitemporal parameters
- [ ] Update to_record/from_record methods
- [ ] Add validation (valid_from <= valid_to)

### **Phase 2: Repository Updates**
- [ ] Add bitemporal columns to atoms table
- [ ] Create indexes on bitemporal fields
- [ ] Update save/load methods
- [ ] Create migration script

### **Phase 3: API Updates**
- [ ] Update MemoryStore.create_atom() signature
- [ ] Add bitemporal query methods
- [ ] Update existing code to use new fields
- [ ] Maintain backward compatibility

### **Phase 4: Integration Updates**
- [ ] Update MCP tool (store_memory)
- [ ] Update BitemporalQueryEngine to work with atoms
- [ ] Update cross-model atoms integration
- [ ] Update documentation

### **Phase 5: Testing & Validation**
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test migration script
- [ ] Performance testing
- [ ] Validate backward compatibility

---

## 🚀 **ESTIMATED TIMELINE**

**Day 1:**
- Model updates (2-3 hours)
- Repository schema updates (2-3 hours)
- Migration script (1-2 hours)

**Day 2:**
- API updates (3-4 hours)
- Query methods implementation (2-3 hours)
- MCP tool updates (1-2 hours)

**Day 3:**
- Testing (4-5 hours)
- Documentation updates (2-3 hours)
- Validation and cleanup (1-2 hours)

**Total:** 2-3 days (16-24 hours)

---

## 🔗 **RELATED ENHANCEMENTS**

This enhancement enables:
1. **Native Bitemporal Queries:** Direct queries without metadata parsing
2. **Better Performance:** Indexed queries on bitemporal fields
3. **Type Safety:** Datetime fields vs string metadata
4. **Cleaner API:** No workarounds needed

**Dependencies:**
- None (can be implemented independently)

**Blocks:**
- None (doesn't block other enhancements)

---

## 📚 **REFERENCES**

- **Current Implementation:** `packages/cmc_service/models.py`, `repository.py`
- **Bitemporal Queries:** `packages/cmc_service/bitemporal_queries.py`
- **MCP Integration:** `lucid_mcp_server.py:1895-2083`
- **Documentation:** `knowledge_architecture/systems/cmc/T2_architecture.md` (bitemporal section)

---

**Status:** Planning Complete ✅  
**Next:** Begin implementation when approved  
**Confidence:** High (0.85) - clear design, low risk

---

*Created by Atlas (CMC System Specialist)*  
*Date: 2025-01-27*  
*Version: 1.0*

