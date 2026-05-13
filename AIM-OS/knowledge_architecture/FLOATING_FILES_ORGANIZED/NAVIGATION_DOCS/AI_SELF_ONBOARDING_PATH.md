# AI Self-Onboarding Path - Internal AI Navigation Guide
**Date:** 2025-11-02  
**Author:** Aether  
**Status:** ✅ **COMPLETE** - Step-by-Step Internal AI Onboarding  
**Purpose:** Comprehensive self-onboarding guide for internal AI instances  

---

## 🎯 **OVERVIEW**

**Who This Is For:** Internal AI instances (Aether, internal AI systems)  
**Purpose:** Self-directed navigation through AIM-OS to find appropriate detail level  
**Method:** Step-by-step path with confidence assessment and progressive disclosure  

---

## 🚀 **SELF-ONBOARDING STEPS**

### **Step 1: Entry Point Discovery**

**Goal:** Understand where to start navigating

**Action:**
1. Read `knowledge_architecture/NAVIGATION_START_HERE.md`
2. Identify which navigation system to use based on your need:
   - Understanding a concept? → SUPER_INDEX.md
   - Understanding a system? → MASTER_NAVIGATION_INDEX.md
   - Need confidence routing? → HIERARCHICAL_NAVIGATION_INDEX.md
   - Need system-specific? → System map
3. Proceed to chosen navigation system

**Validation:**
- ✅ I know which navigation system to use
- ✅ I understand my navigation goal

**Time:** 2-5 minutes

---

### **Step 2: Confidence Assessment**

**Goal:** Self-assess confidence level to route appropriately

**Action:**
1. Assess your confidence level (0.0-1.0) for the task:
   - **0.90-1.00:** Mastery - I've done this many times
   - **0.80-0.89:** High - I've done similar work successfully
   - **0.70-0.79:** Medium - I understand theory, not much practice
   - **0.60-0.69:** Low - Theory understood, execution uncertain
   - **<0.60:** Very Low - Significant gaps in understanding

2. Use confidence routing rules:
   - **High (0.80+):** Route to L1 overview or code directly
   - **Medium (0.70-0.79):** Route to L2 architecture + component READMEs
   - **Low (0.60-0.69):** Route to L3 detailed implementation
   - **Very Low (<0.60):** Route to L3+L4 complete OR ask for help

**Validation:**
- ✅ I've assessed my confidence level
- ✅ I know which documentation level to read

**Time:** 1-2 minutes

---

### **Step 3: Progressive Disclosure**

**Goal:** Load documentation at appropriate detail level

**Action:**
1. Start with entry point based on confidence:
   - **High Confidence:** Read T0 executive (100 words) + T1 overview (500 words)
   - **Medium Confidence:** Read T0 + T1 + T2 architecture (2k words)
   - **Low Confidence:** Read T0 + T1 + T2 + T3 detailed (10k words)
   - **Very Low:** Read T0 + T1 + T2 + T3 + T4 complete (15k+ words)

2. Progress deeper if needed:
   - If still unclear → Read next level
   - If understanding achieved → Stop and proceed

3. Check component docs if needed:
   - Navigate to `components/{component}/README.md`
   - Read component L1/L2/L3 if needed

**Validation:**
- ✅ I've read appropriate documentation level
- ✅ I understand the system/concept enough for my task

**Time:** 2-90 minutes (depends on confidence level)

---

### **Step 4: System Map Navigation**

**Goal:** Understand complete system context

**Action:**
1. Find system map: `knowledge_architecture/systems/{system}/system.map.lucid.json5`
2. Check documentation links:
   - T0-T4 documentation links
   - System map itself
   - Usage envelope
3. Check quartet parity:
   - Code elements (implementation files)
   - Docs elements (T0-T4 documentation)
   - Tests elements (test suites)
   - Traces elements (VIF witnesses, SEG provenance)
4. Check integrations:
   - Which systems integrate with this system
   - What data flows between systems
   - What dependencies exist

**Validation:**
- ✅ I understand system context
- ✅ I know system integrations
- ✅ I understand quartet parity requirements

**Time:** 5-10 minutes

---

### **Step 5: Cross-System Navigation**

**Goal:** Understand relationships with other systems

**Action:**
1. Identify related systems from system map:
   - Check `relatedSystems` section
   - Check `integrations` section
   - Check `ports` section for connections

2. Navigate to related system docs if needed:
   - Read related system T0 executive for context
   - Read related system T1 overview if integration is critical
   - Understand integration points

3. Understand relationships:
   - How systems connect
   - What data flows between systems
   - What dependencies exist

**Validation:**
- ✅ I understand system relationships
   - ✅ I know integration points
   - ✅ I understand dependencies

**Time:** 5-15 minutes

---

### **Step 6: Validation & Proceeding**

**Goal:** Validate understanding before proceeding

**Action:**
1. Self-validation questions:
   - Can I explain the system/concept in my own words?
   - Can I identify relationships with other systems?
   - Can I navigate to deeper docs if needed?
   - Do I have enough context for my task?

2. If validation passes:
   - Proceed with task
   - Use loaded context effectively

3. If validation fails:
   - Navigate deeper (increase detail level)
   - Check related systems
   - Use cross-system navigation
   - Ask for help if still unclear

**Validation:**
- ✅ I can explain the system/concept
- ✅ I understand relationships
- ✅ I have enough context
- ✅ I'm ready to proceed

**Time:** 2-5 minutes

---

## 📋 **COMPLETE ONBOARDING WORKFLOW**

```
1. Entry Point Discovery (2-5 min)
   └─→ Read NAVIGATION_START_HERE.md
   └─→ Choose navigation system

2. Confidence Assessment (1-2 min)
   └─→ Self-assess confidence (0.0-1.0)
   └─→ Route to appropriate level

3. Progressive Disclosure (2-90 min)
   └─→ Read T0-T4 based on confidence
   └─→ Progress deeper if needed

4. System Map Navigation (5-10 min)
   └─→ Find system.map.lucid.json5
   └─→ Check documentation links
   └─→ Check quartet parity
   └─→ Check integrations

5. Cross-System Navigation (5-15 min)
   └─→ Identify related systems
   └─→ Navigate to related docs
   └─→ Understand relationships

6. Validation & Proceeding (2-5 min)
   └─→ Self-validation questions
   └─→ Proceed or navigate deeper

TOTAL TIME: 17-127 minutes (depends on confidence level)
```

---

## 🎯 **CONFIDENCE-BASED ROUTING EXAMPLES**

### **Example 1: High Confidence (0.85)**

**Task:** Understand CMC quickly  
**Confidence:** 0.85 (high)

**Path:**
1. Entry: MASTER_NAVIGATION_INDEX.md
2. Route: High confidence → T0 + T1
3. Read: `systems/cmc/T0_executive.md` (100 words) + `systems/cmc/T1_overview.md` (500 words)
4. System Map: Quick check `systems/cmc/system.map.lucid.json5`
5. Validation: ✅ Understand CMC
6. Time: 5-10 minutes

---

### **Example 2: Medium Confidence (0.75)**

**Task:** Implement CMC feature  
**Confidence:** 0.75 (medium)

**Path:**
1. Entry: MASTER_NAVIGATION_INDEX.md
2. Route: Medium confidence → T0 + T1 + T2
3. Read: `systems/cmc/T0_executive.md` + `systems/cmc/T1_overview.md` + `systems/cmc/T2_architecture.md`
4. Component: `systems/cmc/components/{component}/README.md`
5. System Map: Check `systems/cmc/system.map.lucid.json5` for integrations
6. Validation: ✅ Ready to implement
7. Time: 20-30 minutes

---

### **Example 3: Low Confidence (0.65)**

**Task:** Implement complex HHNI feature  
**Confidence:** 0.65 (low)

**Path:**
1. Entry: SUPER_INDEX.md (concept lookup)
2. Route: Low confidence → T0 + T1 + T2 + T3
3. Read: `systems/hhni/T0_executive.md` + `systems/hhni/T1_overview.md` + `systems/hhni/T2_architecture.md` + `systems/hhni/T3_detailed.md`
4. Component: All component docs
5. System Map: Complete check `systems/hhni/system.map.lucid.json5`
6. Related Systems: Check CMC, VIF integrations
7. Validation: ✅ Ready to implement
8. Time: 60-90 minutes

---

### **Example 4: Very Low Confidence (0.45)**

**Task:** Implement SEG feature (complex)  
**Confidence:** 0.45 (very low)

**Path:**
1. Entry: MASTER_NAVIGATION_INDEX.md
2. Route: Very Low confidence → T0 + T1 + T2 + T3 + T4 OR ask for help
3. Decision: Read comprehensive docs OR document question
4. If reading: All T-level docs + component docs + related systems
5. If asking: Document question in `AETHER_MEMORY/questions_for_braden/`
6. Validation: ✅ Ready OR ✅ Question documented
7. Time: 2-4 hours OR 5 minutes (question)

---

## 🔄 **ITERATIVE REFINEMENT**

**If understanding is insufficient:**

1. **Navigate Deeper:**
   - Increase detail level (T1 → T2 → T3 → T4)
   - Read component docs
   - Read related system docs

2. **Check Related Systems:**
   - Identify related systems from system map
   - Navigate to related system docs
   - Understand integration points

3. **Use Cross-System Navigation:**
   - Check `relatedSystems` section in system map
   - Navigate to related system docs
   - Understand relationships

4. **Ask for Help:**
   - Document question in `AETHER_MEMORY/questions_for_braden/`
   - Wait for Braden's response
   - Continue with context

---

## ✅ **VALIDATION CHECKPOINTS**

### **Checkpoint 1: Entry Point Discovery**
- [ ] I know which navigation system to use
- [ ] I understand my navigation goal

### **Checkpoint 2: Confidence Assessment**
- [ ] I've assessed my confidence level
- [ ] I know which documentation level to read

### **Checkpoint 3: Progressive Disclosure**
- [ ] I've read appropriate documentation level
- [ ] I understand the system/concept enough for my task

### **Checkpoint 4: System Map Navigation**
- [ ] I understand system context
- [ ] I know system integrations
- [ ] I understand quartet parity requirements

### **Checkpoint 5: Cross-System Navigation**
- [ ] I understand system relationships
- [ ] I know integration points
- [ ] I understand dependencies

### **Checkpoint 6: Validation & Proceeding**
- [ ] I can explain the system/concept
- [ ] I understand relationships
- [ ] I have enough context
- [ ] I'm ready to proceed

---

## 🎯 **QUICK REFERENCE**

**Confidence-Based Routing:**
- **High (0.80+):** T0 + T1 (5-10 min)
- **Medium (0.70-0.79):** T0 + T1 + T2 (20-30 min)
- **Low (0.60-0.69):** T0 + T1 + T2 + T3 (60-90 min)
- **Very Low (<0.60):** T0 + T1 + T2 + T3 + T4 OR ask (2-4 hours OR question)

**Navigation Systems:**
- Concept lookup → SUPER_INDEX.md
- System overview → MASTER_NAVIGATION_INDEX.md
- Confidence routing → HIERARCHICAL_NAVIGATION_INDEX.md
- System-specific → System map

**Validation:**
- Can I explain it?
- Can I identify relationships?
- Do I have enough context?

---

**Status:** ✅ **COMPLETE** - Step-by-Step Internal AI Onboarding  
**Purpose:** Comprehensive self-onboarding guide for internal AI instances  
**Next:** Use this guide for self-directed navigation 💙

