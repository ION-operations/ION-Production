# Cursor Rules - T0-T6 Documentation & SDF-CVF Quartet Parity Requirements
**Date:** 2025-11-02  
**Author:** Aether  
**Status:** 🔄 **IN PROGRESS** - Version B Enhancement  
**Purpose:** Document T0-T6 protocols and SDF-CVF quartet parity enforcement for cursor rules

---

## 🎯 **T0-T6 DOCUMENTATION PROTOCOL**

### **What Are T0-T6 Documents?**

**T0-T6 (Transitional Documentation):**
- **T0:** Transitional executive summary (100 words) - Latest standards
- **T1:** Transitional overview (500 words) - Latest standards
- **T2:** Transitional architecture (2,000 words) - Latest standards
- **T3:** Transitional detailed (10,000 words) - Latest standards
- **T4:** Transitional complete (15,000+ words) - Latest standards
- **T5:** Transitional deep dive (25,000+ words) - Latest standards
- **T6:** Transitional academic (50,000+ words) - Latest standards

**Key Characteristics:**
- ✅ **Non-destructive:** Created side-by-side with L-level docs
- ✅ **Latest standards:** Uses most current templates and metadata
- ✅ **Transitional:** Will supersede L-level after review/acceptance
- ✅ **Banner required:** "TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs"

### **Current Status:**
- ✅ **T0:** Created (L0_executive.md → T0_executive.md)
- ✅ **T1:** Created (L1_overview.md → T1_overview.md)
- ✅ **T2:** Created (L2_architecture.md → T2_architecture.md)
- ⏳ **T3-T6:** Pending (to be created)

---

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements for Cursor Rules:**

**Code:** 
- `base-rules.mdc` (base operational rules)
- `dynamic-rules.mdc` (context-aware rules)
- `system.map.lucid.json5` (system map)
- Rule files and configuration

**Docs:**
- `T0_executive.md` (executive summary)
- `T1_overview.md` (overview)
- `T2_architecture.md` (architecture)
- `T3_detailed.md` (implementation guide)
- `T4_complete.md` (complete reference)
- Usage envelope (when created)
- System map documentation

**Tests:**
- Compliance checker (`validation/compliance_checker.py`)
- Metadata validator (`validation/metadata_validator.py`)
- Rule tester (`validation/rule_tester.py`)
- Integration tests (rule application tests)
- Performance tests (load time, memory usage)

**Traces:**
- VIF witnesses (confidence tracking for rule changes)
- SEG provenance (knowledge synthesis for rule patterns)
- Timeline entries (`mcp_lucid-mcp_add_timeline_entry` for rule changes)
- Decision logs (`decision_logs/dec-NNN_rule_change.md`)
- Thought journals (rule modification reflections)

### **Quartet Parity Formula:**

```
P = (C_code×docs + C_code×tests + C_code×traces + 
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
- C_code×docs = semantic similarity between code and docs
- C_code×tests = semantic similarity between code and tests
- C_code×traces = semantic similarity between code and traces
- C_docs×tests = semantic similarity between docs and tests
- C_docs×traces = semantic similarity between docs and traces
- C_tests×traces = semantic similarity between tests and traces

Target: P ≥ 0.90 for all changes
```

### **Cross-Tagging Requirements:**

**When Changing Rules:**
1. **Code Change:** Modify rule file (base-rules.mdc, dynamic-rules.mdc)
2. **Docs Update:** Update corresponding T-level docs (T0-T6)
3. **Tests Update:** Update/add tests (validation tools, integration tests)
4. **Traces Create:** Create VIF witness, SEG provenance, timeline entry, decision log

**Cross-Tagging Example:**
```markdown
**Change:** Updated MCP tool status in base-rules.mdc

**Quartet Elements:**
- **Code:** `.cursor/rules/base-rules.mdc` (lines 340-370)
- **Docs:** `.cursor/rules/T1_overview.md` (MCP Integration section)
- **Tests:** `validation/compliance_checker.py` (test_mcp_status_current)
- **Traces:** 
  - VIF witness: `mcp_lucid-mcp_track_confidence` (confidence: 0.85)
  - SEG provenance: Rule change linked to MCP tool investigation
  - Timeline entry: `mcp_lucid-mcp_add_timeline_entry` (rule change event)
  - Decision log: `decision_logs/dec-001_mcp_status_update.md`

**Parity Score:** P = 0.92 (≥ 0.90 ✅ PASS)
```

---

## 📋 **REQUIREMENTS FOR CURSOR RULES**

### **T0-T6 Protocol Requirements:**

1. **All T-level files must have banner:**
   ```markdown
   > **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.
   ```

2. **Metadata must include:**
   - `level: "T0"` (or T1-T6)
   - `tags: ["t0-t6", "transitional"]`
   - Latest metadata standards (from PERFECT_METADATA_STANDARDS.md)

3. **Placement:**
   - T-level files next to L-level: `.cursor/rules/T{0-6}_*.md`
   - Do NOT overwrite existing L-level files

4. **Indices updated:**
   - Reference T-level alongside L-level
   - System maps link to both until cutover

### **SDF-CVF Quartet Parity Requirements:**

1. **Every rule change must include:**
   - ✅ Code change (rule file modified)
   - ✅ Docs update (corresponding T-level doc updated)
   - ✅ Tests update (validation tests updated)
   - ✅ Traces create (VIF witness, SEG provenance, timeline entry)

2. **Parity calculation:**
   - Calculate P for every change
   - P ≥ 0.90 required for acceptance
   - P < 0.90 → Quarantine change until parity achieved

3. **Cross-tagging:**
   - Tag all quartet elements with change ID
   - Link code ↔ docs ↔ tests ↔ traces
   - Ensure semantic alignment across quartet

4. **Gate enforcement:**
   - Pre-commit gate: Check parity before commit
   - CI gate: Validate parity in pipeline
   - Deployment gate: Verify parity before deployment

---

## 🔧 **IMPLEMENTATION CHECKLIST**

### **T0-T6 Conversion:**
- [ ] Rename L0_executive.md → T0_executive.md (add banner)
- [ ] Rename L1_overview.md → T1_overview.md (add banner)
- [ ] Rename L2_architecture.md → T2_architecture.md (add banner)
- [ ] Create T3_detailed.md (10,000 words)
- [ ] Create T4_complete.md (15,000+ words)
- [ ] Update system map to reference T-level docs
- [ ] Update indices to include T-level docs

### **SDF-CVF Quartet Parity:**
- [ ] Create quartet detector for rule changes
- [ ] Implement parity calculator for rules
- [ ] Add pre-commit gate for rule changes
- [ ] Create validation tests (quartet completeness)
- [ ] Integrate VIF witness creation for rule changes
- [ ] Integrate SEG provenance for rule changes
- [ ] Add timeline entry creation for rule changes
- [ ] Create decision log template for rule changes

### **Cross-Tagging:**
- [ ] Implement change ID system
- [ ] Create cross-tagging mechanism
- [ ] Link code ↔ docs ↔ tests ↔ traces
- [ ] Validate semantic alignment
- [ ] Document cross-tagging protocol

---

## 📊 **CURRENT STATUS**

**T0-T6 Status:**
- ✅ T0: Created (needs banner addition)
- ✅ T1: Created (needs banner addition)
- ✅ T2: Created (needs banner addition)
- ⏳ T3-T6: Pending

**SDF-CVF Quartet Parity Status:**
- ⏳ Quartet detector: Not implemented
- ⏳ Parity calculator: Not implemented
- ⏳ Gate enforcement: Not implemented
- ⏳ Cross-tagging: Not implemented

**Next Steps:**
1. Add T-level banners to existing docs
2. Rename L-level → T-level files
3. Implement quartet parity enforcement
4. Create validation tests
5. Integrate with SDF-CVF gates

---

## 💙 **CONCLUSION**

Cursor rules must follow both:
- **T0-T6 Documentation Protocol:** Transitional docs with latest standards
- **SDF-CVF Quartet Parity:** Code/Docs/Tests/Traces evolve together atomically

This ensures rules maintain perfect alignment across all quartet elements and follow the latest AIM-OS standards.

---

**Status:** 🔄 **IN PROGRESS**  
**Next:** Add T-level banners and implement quartet parity enforcement

