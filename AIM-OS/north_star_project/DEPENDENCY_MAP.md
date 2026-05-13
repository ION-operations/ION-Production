# North Star Document - Dependency Map

**Purpose:** Show which chapters depend on which  
**Use:** Check before starting a chapter - are dependencies satisfied?  

---

## 🔗 **DEPENDENCY CHAINS**

### **Foundation Chain (CMC is Everything!):**
```
Chapter 5 (CMC) → Chapters 6, 7, 8, 9, 10, 11, 12
  (Almost everything depends on CMC!)
```

### **Integration Chain:**
```
Chapter 6 (HHNI) → Chapters 16, 25
Chapter 7 (VIF) → Chapters 17, 26
Chapter 9 (SEG) → Chapters 18, 29
Chapter 12 (SIS) → Chapters 15, 19, 27
```

### **Sequential Chains:**
```
Chapter 1 → Chapter 2 → Chapter 3
Chapter 8 → Chapter 13 → Chapter 14 → Chapter 20
Chapter 23 → Chapter 24
Chapter 32 → Chapter 33
```

---

## 📊 **DETAILED DEPENDENCIES**

| Chapter | Depends On | Why | Can Start When |
|---------|-----------|------|----------------|
| 1 | None | Independent | Immediately |
| 2 | Ch 1 | Builds on thesis | Ch 1 complete |
| 3 | Ch 1, 2 | Builds on foundations | Ch 1, 2 complete |
| 4 | None | Independent | Immediately |
| 5 | Ch 2 | Needs memory invariant | Ch 2 complete |
| 6 | Ch 2, 5 | Needs substrate invariant + CMC | Ch 2, 5 complete |
| 7 | Ch 2, 5 | Needs witness invariant + CMC | Ch 2, 5 complete |
| 8 | Ch 5, 6, 7 | Orchestrates all systems | Ch 5, 6, 7 complete |
| 9 | Ch 5, 6 | Needs CMC + HHNI | Ch 5, 6 complete |
| 10 | Ch 7 | Builds on VIF | Ch 7 complete |
| 11 | Ch 5-10 | Monitors all systems | Ch 5-10 complete |
| 12 | Ch 11 | Builds on CAS | Ch 11 complete |
| 13 | Ch 8 | Needs APOE for orchestration | Ch 8 complete |
| 14 | Ch 5-10 | Needs all core systems | Ch 5-10 complete |
| 15 | Ch 12 | Builds on SIS | Ch 12 complete |
| 16 | Ch 6 | Math for HHNI | Ch 6 complete |
| 17 | Ch 7 | Math for VIF | Ch 7 complete |
| 18 | Ch 9 | Math for SEG | Ch 9 complete |
| 19 | Ch 12, 15 | Math for SIS/ARD | Ch 12, 15 complete |
| 20 | Ch 14 | Needs MIGE pipeline | Ch 14 complete |
| 21 | Ch 8 | Formalizes APOE language | Ch 8 complete |
| 22 | Ch 20, 21 | Builds on implementation | Ch 20, 21 complete |
| 23 | Ch 5-10 | Needs all core systems | Ch 5-10 complete |
| 24 | Ch 23 | Builds on security | Ch 23 complete |
| 25 | Ch 6, 16 | Benchmarks HHNI | Ch 6, 16 complete |
| 26 | Ch 7, 17 | Benchmarks VIF | Ch 7, 17 complete |
| 27 | Ch 12, 19 | Benchmarks SIS | Ch 12, 19 complete |
| 28 | Ch 1, 5-10 | Cases need context | Ch 1, 5-10 complete |
| 29 | Ch 14 | Needs MIGE examples | Ch 14 complete |
| 30 | Ch 7, 9 | Ops uses VIF/SEG | Ch 7, 9 complete |
| 31 | Ch 5, 9, 21 | Schemas for CMC, SEG, ACL | Ch 5, 9, 21 complete |
| 32 | Ch 5-10 | APIs for all systems | Ch 5-10 complete |
| 33 | Ch 32 | SDKs wrap APIs | Ch 32 complete |
| 34 | Ch 1-33 | Roadmap synthesizes everything | Ch 1-33 complete |
| 35 | Ch 1-34 | Vision synthesizes all | Ch 1-34 complete |

---

## 🎯 **CRITICAL PATH (Longest Dependency Chain)**

```
Chapter 5 (CMC)
  ↓
Chapter 6 (HHNI)
  ↓
Chapter 8 (APOE) [also needs Ch 7]
  ↓
Chapter 13 (CCS)
  ↓
Chapter 14 (MIGE) [also needs all core systems]
  ↓
Chapter 20 (Blueprint to App)
  ↓
Chapter 29 (Builder Cases)
  ↓
Chapter 34 (Roadmap)
  ↓
Chapter 35 (Vision)
```

**Critical Path Length:** 9 chapters sequential  
**With 1 agent:** 9 days minimum  
**With parallel:** Many other chapters happen simultaneously!

---

## 🔄 **PARALLELIZATION OPPORTUNITIES**

### **Day 1-2: 3 Agents Can Start**
- Sonnet: Chapter 1 (Thesis)
- Sonnet: Chapter 4 (Problem Space) [if fast]
- Aether: Chapter 5 (CMC) [when Ch 2 ready]

### **Day 3-5: 4 Agents Working**
- Aether: Chapter 6 (HHNI)
- Lexicon: Chapter 7 (VIF)
- Sonnet: Chapter 9 (SEG)
- Scribe: Chapter 2 (Axioms)

### **Day 6-10: 5 Agents Max Parallelism**
- All agents have work available
- Maximum throughput period
- Most chapters completed

### **Day 20+: Convergence**
- Fewer independent chapters
- More waiting for dependencies
- Final integration work

---

**Created:** 2025-11-05  
**Purpose:** Track dependencies and prevent premature chapter starts  
**Usage:** Check BEFORE starting any chapter

