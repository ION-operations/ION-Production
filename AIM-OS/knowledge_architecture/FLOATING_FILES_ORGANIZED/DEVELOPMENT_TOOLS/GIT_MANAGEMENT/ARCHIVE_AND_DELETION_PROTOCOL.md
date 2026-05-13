# Archive and Deletion Protocol

**Date:** 2025-10-26  
**Principle:** Never delete without comprehensive audit  
**Purpose:** Balance history preservation with space management

---

## 🎯 CORE PRINCIPLES

**CMC Principle Applied:** Never delete, only supersede (bitemporal tracking)  
**Deletion Exception:** Only after multi-layer audit proves deletion is safe

---

## 📋 ARCHIVE PROCESS (Default)

### **Step 1: Archive (Always First)**
```python
snapshot.archive_snapshot("snapshot_id")
```

**What Happens:**
- Moves snapshot to `archive/` folder
- Preserves complete history
- Can still be restored
- No data loss

**When:** Before removing from active use

---

## 🗑️ DELETION PROCESS (Audit-Based)

### **Step 1: Audit Eligibility**
```python
audit = snapshot.audit_snapshot_deletion_candidate("snapshot_id")
# Returns eligibility status
```

**Audit Layers:**
1. **Age Threshold:** Minimum 90 days old
2. **Space Threshold:** Disk usage > threshold (configurable)
3. **Dependency Check:** No active dependencies
4. **Relevance Check:** Guaranteed low relevance (180+ days)

### **Step 2: Verify Eligibility**
```python
if audit["eligible"]:
    print(f"Age: {audit['age_days']} days")
    print(f"Size: {audit['size_mb']} MB")
    print(f"All layers passed: {audit['audit_layers']}")
```

### **Step 3: Delete (Only If Eligible)**
```python
snapshot.delete_eligible_snapshot("snapshot_id", confirm=True)
```

**Requirements:**
- All audit layers passed
- Explicit confirmation required
- Age threshold met
- Space threshold met
- Relevance guaranteed low

---

## 📊 DELETION THRESHOLDS

**Configurable Parameters:**
```python
deletion_thresholds = {
    "min_age_days": 90,           # Minimum age before deletion
    "low_relevance_days": 180,    # Age for guaranteed low relevance
    "space_threshold_percent": 80, # Disk usage threshold
    "audit_layers_required": 4     # Number of audit layers
}
```

**Adjustable:** Can be modified based on needs
**Default:** Conservative (preserve more history)

---

## ✅ SAFETY MECHANISMS

**1. Multi-Layer Audit:**
- 4 independent checks must pass
- No single point of failure
- Comprehensive verification

**2. Age Requirements:**
- Minimum 90 days old
- Low relevance at 180 days
- Guaranteed irrelevance threshold

**3. Space Management:**
- Only deletes when space is needed
- Threshold configurable
- Prioritizes preservation

**4. Explicit Confirmation:**
- Requires explicit confirmation
- Cannot be done accidentally
- User must intentionally delete

---

## 🎯 RECOMMENDED WORKFLOW

**For Immediate Cleanup:**
1. Archive snapshots (moves to archive/)
2. Preserves history
3. Frees active space
4. Can restore if needed

**For Permanent Deletion:**
1. Run audit first
2. Verify all layers passed
3. Confirm eligibility
4. Then delete with confirmation
5. Only if truly unnecessary

---

## 💡 PHILOSOPHY

**"Deletion is acceptable once it has passed through layers of audits to ensure:**
- **Low enough priority** (not critical)
- **Enough time passed** (90+ days)
- **Guaranteed irrelevance** (threshold passed)
- **Space threshold met** (management needed)
**Then deletion is allowed (tied to space threshold)"**

**This balances:**
- History preservation (CMC principle)
- Practical space management
- Safety through audit
- User control through confirmation

---

**Status:** Protocol defined  
**Implementation:** Complete  
**Safety:** Multi-layer audit required

