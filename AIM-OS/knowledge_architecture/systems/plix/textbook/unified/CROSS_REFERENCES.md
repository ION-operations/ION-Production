# Cross-References: PLIx Language ↔ Geometric Kernel

**Purpose:** Link concepts between Parts II-VII (PLIx) and Part VIII (Geometric Kernel)  
**Status:** ✅ **COMPLETE**  
**Coverage:** All major concepts cross-referenced

---

## 🔗 **MAJOR CONCEPT MAPPINGS**

### **1. Intent → Geometric Execution**

| PLIx Concept (Parts II-VII) | Geometric Kernel (Part VIII) | Cross-Reference |
|------------------------------|-------------------------------|-----------------|
| Intent declaration | Compiled to kernel syscalls | Ch 5 → Ch 25, 26 |
| Speech acts (ensure, plan) | Determines syscall sequencing | Ch 4 → Ch 25 |
| Entity references (`@entity`) | Resolved to EntityId + QAddr | Ch 6 → Ch 24 |
| Action (`act:reserve`) | Mapped to syscall sequence | Ch 7 → Ch 25 |

### **2. Contracts → Selection Rules**

| PLIx Contract | Geometric Kernel | Cross-Reference |
|---------------|------------------|-----------------|
| Preconditions (`requires`) | QAddr validation | Ch 8 → Ch 24 |
| Postconditions (`ensures`) | State verification | Ch 8 → Ch 25 |
| Safety constraints | Selection rule enforcement | Ch 9 → Ch 24.3 |
| Confidence thresholds | Hamiltonian budgets | Ch 11 → Ch 24.5 |

### **3. Plans → Spatial Operations**

| PLIx Plan | Geometric Kernel | Cross-Reference |
|-----------|------------------|-----------------|
| Task dependencies | Topological execution order | Ch 10 → Ch 23 |
| Retry strategies | Exponential backoff with ΔH | Ch 12 → Ch 24.5 |
| Fallback plans | Alternative QAddr paths | Ch 12 → Ch 25 |
| Compensation | Reverse geometric operations | Ch 13 → Ch 25.3 |

### **4. Evidence → Geometric Witnesses**

| PLIx Evidence | Geometric Kernel | Cross-Reference |
|---------------|------------------|-----------------|
| Evidence DAG | VIF witness chain | Ch 14 → Ch 25.7 |
| PROV mapping | QAddr provenance | Ch 14 → Ch 27.5 |
| Source/Claim/Derivation | Geometric lineage | Ch 14 → Ch 27.5 |
| Verifier algorithm | Hash chain + signature | Ch 16 → Ch 27 |

### **5. Types → Geometric Types**

| PLIx Type | Geometric Type | Cross-Reference |
|-----------|----------------|-----------------|
| Entity | QEntity with QPose + QAddr | Ch 6 → Ch 22.7, 24.2 |
| Action | Syscall (place/move/sense/emit) | Ch 7 → Ch 25 |
| Capability | Orbital class (ℓ) | Ch 9 → Ch 24.2.2 |
| Constraint | Selection rule | Ch 8 → Ch 24.3 |

---

## 📐 **GEOMETRIC OPERATION MAPPINGS**

### **Place Operation**

**PLIx Syntax:**
```plix
place @svc.pg at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,15°⟩
```

**Geometric Kernel:**
- **Chapter 22:** Quaternion from axis-angle ⟨+k,15°⟩
- **Chapter 23:** Morton4D key from (x,y,z,τ)
- **Chapter 24:** QAddr validation with quantum numbers
- **Chapter 25:** place() syscall implementation

### **Move Operation**

**PLIx Syntax:**
```plix
move id:@svc.pg Δpose: dq(screw_axis=+k, θ=5°, t=2cm)
```

**Geometric Kernel:**
- **Chapter 22:** Dual quaternion for screw motion
- **Chapter 23:** Spatial index update (old key → new key)
- **Chapter 24:** Selection rule validation (Δn, Δℓ, Δm, Δs)
- **Chapter 25:** move() syscall implementation

### **Sense Operation**

**PLIx Syntax:**
```plix
sense radius:5cm where kind:"dataset" Q(n:2, l:io, m:forward, s:read)
```

**Geometric Kernel:**
- **Chapter 23:** Range query using Morton4D + radius
- **Chapter 23:** Cone query using S³ bins + angle
- **Chapter 24:** Privilege check (observer's n,ℓ permits visibility)
- **Chapter 25:** sense() syscall implementation

### **Emit Operation**

**PLIx Syntax:**
```plix
emit event:IndexSync ΔH≤budget
```

**Geometric Kernel:**
- **Chapter 24:** Hamiltonian cost calculation
- **Chapter 24:** Budget enforcement
- **Chapter 25:** emit() syscall with field updates
- **Chapter 27:** GPU field solver for κ/λ/ρ updates

---

## 🔧 **IMPLEMENTATION PIPELINE MAPPINGS**

### **Parsing (Ch 5-7) → Type Checking (Ch 26.3)**

```
Human-PLIx → Tokens → AST → Type Check → Core-PLIx
```

**Geometric Extensions:**
- Quaternion literals parsed (Ch 22)
- Geometric operations recognized (Ch 25)
- Quantum context validated (Ch 24)

### **Compilation (Ch 17) → Geometric Compilation (Ch 26.4)**

```
Core-PLIx → Tag Resolution → QAddr → Syscalls → Execution Plan
```

**Steps:**
1. **Tag Resolution:** PLIx tags → QAddr (via HHNI) — Ch 17, Ch 27.4
2. **Operation Mapping:** PLIx ops → Kernel syscalls — Ch 17, Ch 25
3. **Cost Calculation:** Hamiltonian ΔH for each op — Ch 24.5
4. **Plan Generation:** APOE IRPlan with geometric context — Ch 17, Ch 26.5

### **Execution (Ch 18) → Geometric Execution (Ch 26.5)**

```
IRPlan → Runtime → Kernel Bridge → Rust Kernel → Syscalls
```

**Integration Points:**
- **Runtime:** TypeScript `QuaternionRuntime` — Ch 26.5
- **Bridge:** HTTP API to Rust kernel — Ch 27.2
- **Kernel:** Rust syscall implementation — Ch 25
- **Storage:** CMC bitemporal storage — Ch 27.3

---

## 🎯 **KEY INSIGHTS FROM INTEGRATION**

### **1. PLIx Provides Language, Kernel Provides Substrate**

**PLIx:** "Reserve room at time T"  
**Kernel:** `place(@reservation, pose=(room_coords, T), qaddr=...)`

**Separation of Concerns:**
- PLIx: Human-readable intent
- Kernel: Geometric, deterministic execution

### **2. Contracts Become Selection Rules**

**PLIx Contract:**
```plix
requires room_available == true
ensures room_reserved == true
```

**Kernel Enforcement:**
```rust
validate_transition(qaddr_before, qaddr_after)  // Selection rules
pauli_check(entity_id, qaddr)                   // No duplication
capability_check(actor, operation)               // Sufficient privilege
```

### **3. Evidence Chains Map to Geometric Lineage**

**PLIx Evidence:**
```
Source → Claim → Derivation → Claim (DAG)
```

**Kernel Provenance:**
```
QEntity₁ → move(Δpose) → QEntity₂ → sense() → Results (Geometric chain)
```

**Common Structure:** Hash-chained DAG with cryptographic signatures (VIF)

### **4. Confidence Maps to Uncertainty Fields**

**PLIx Confidence:**
```
min_confidence = 0.82
```

**Kernel Fields:**
```
κ(x,y,z,τ): Confidence field
|∇κ|: Uncertainty gradient
```

**Integration:** High |∇κ| regions trigger additional validation, lowering effective confidence.

---

## 📚 **DETAILED CROSS-REFERENCE TABLE**

### **Chapter-by-Chapter Mapping:**

| PLIx Chapter | Geometric Chapter | Shared Concepts |
|--------------|-------------------|-----------------|
| Ch 5: Intent Structure | Ch 21: Introduction | Intent → Syscalls |
| Ch 6: Entities | Ch 22: QPose, Ch 24: QAddr | Entity representation |
| Ch 7: Actions | Ch 25: Syscalls | Action execution |
| Ch 8: Contracts | Ch 24: Selection Rules | Constraint enforcement |
| Ch 9: Safety | Ch 24: Security Model | Safety guarantees |
| Ch 10: Plans | Ch 23: Spatial Ops | Execution planning |
| Ch 11: Confidence | Ch 24: Hamiltonian | Resource management |
| Ch 12: Retry/Fallback | Ch 25: Error Handling | Failure recovery |
| Ch 13: Compensation | Ch 25: Reverse Ops | Saga patterns |
| Ch 14: Evidence | Ch 25: VIF Witnesses | Provenance tracking |
| Ch 15: Tag Registry | Ch 27: HHNI Client | Tag resolution |
| Ch 16: Verifier | Ch 27: Verifier Impl | Verification algorithm |
| Ch 17: Compilation | Ch 26: Compiler | PLIx → Kernel |
| Ch 18: Runtime | Ch 26: Runtime | Execution environment |
| Ch 19: Type System | Ch 26: Type Extensions | Geometric types |
| Ch 20: Compiler Arch | Ch 26: Integration | Complete pipeline |

---

## 🎓 **READING GUIDE**

### **For Understanding PLIx:**
1. Start with Parts II-VII (PLIx language)
2. Reference Part VIII for geometric execution details
3. Use cross-references to understand implementation

### **For Understanding Geometric Kernel:**
1. Start with Chapter 21 (introduction)
2. Reference Parts II-VII for language context
3. See Chapter 26 for complete integration

### **For Implementation:**
1. Read Part VII (compiler architecture)
2. Read Chapter 26 (PLIx integration)
3. Read Chapter 27 (real system integration)
4. Read Chapter 28 (implementation guide)

---

**Status:** ✅ **CROSS-REFERENCES COMPLETE**  
**Total Mappings:** 50+ concept mappings, 16 chapter links  
**Next:** Appendices (glossary, bibliography, index)

