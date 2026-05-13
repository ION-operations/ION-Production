# PLIx Quaternion Extension: Phase 1 Implementation Plan

**Status:** 🔄 Ready for Implementation  
**Created:** 2025-01-27  
**Phase:** Foundation (Weeks 1-4)  
**Purpose:** Detailed implementation plan for Phase 1 foundation work

---

## Overview

Phase 1 establishes the foundational components:
1. Quaternion math library with determinism guarantees
2. Spatial indexing (Morton4D + S³ binning) with quantum numbers
3. Basic syscalls (`place`, `move`, `sense`, `emit`) with quantum context and selection rules

---

## Week 1-2: Quaternion Math Library

### File Structure
```
packages/quaternion-math/
├── src/
│   ├── quat.rs              # QQuat implementation
│   ├── dual_quat.rs         # DualQuat implementation
│   ├── double_quat.rs       # DoubleQuat implementation
│   ├── canonical.rs         # Sign canonicalization
│   └── lib.rs               # Public API
├── tests/
│   ├── quat_tests.rs
│   ├── dual_quat_tests.rs
│   ├── double_quat_tests.rs
│   └── canonical_tests.rs
└── Cargo.toml
```

### Core Requirements

**QQuat:**
- `q0, q1, q2, q3: f64` components
- Hamilton product (non-commutative)
- Conjugate, norm, normalize
- SLERP interpolation
- Sign canonicalization (determinism)

**DualQuat:**
- Rotation (QQuat) + translation (vec3)
- Composition (screw motion)
- Transform point
- Inverse

**DoubleQuat:**
- Left/right SU(2) rotors
- 4D rotations
- SO(4) ≅ SU(2)×SU(2) structure

**Determinism:**
- Sign canonicalization: always choose q or -q consistently
- Fixed operation ordering
- No floating-point non-associativity issues

### Test Requirements
- 100% coverage for all operations
- Deterministic replay tests
- Numerical stability tests
- Edge case tests (zero, identity, etc.)

---

## Week 3: Spatial Indexing + Quantum Numbers

### File Structure
```
packages/spatial-index/
├── src/
│   ├── morton4d.rs          # Morton4D encoding/decoding
│   ├── s3_binning.rs         # S³ binning (Hopf factorization)
│   ├── qaddr.rs              # Quantum Kernel Address
│   ├── selection_rules.rs   # Selection rule validation
│   └── lib.rs
├── tests/
│   ├── morton4d_tests.rs
│   ├── s3_binning_tests.rs
│   ├── qaddr_tests.rs
│   └── selection_rules_tests.rs
└── Cargo.toml
```

### Core Requirements

**Morton4D:**
- Encode (x, y, z, τ) → uint64
- Decode uint64 → (x, y, z, τ)
- Range queries
- Deterministic ordering

**S³ Binning:**
- Hopf factorization: S³ → S² × S¹
- Icosahedral tessellation (or optimal scheme)
- Orientation bin → uint16
- Cone queries

**QAddr:**
```rust
pub struct QAddr {
    pub n: i16,           // Principal shell
    pub l: i16,           // Capability class
    pub m: i32,           // Orientation channel
    pub s: i16,           // Chirality mode
    pub morton4d: u64,    // Spacetime index
    pub s3bin: u16,       // Orientation bin
}

impl QAddr {
    pub fn composite_key(&self) -> u64 {
        (self.morton4d << 16) | (self.s3bin as u64)
    }
}
```

**Selection Rules:**
- Validate Δn ∈ {0,±1}
- Validate Δℓ ∈ {0,±1}
- Validate Δm ∈ {0,±1}
- Validate Δs (guarded boundaries only)
- Return SelectionResult with reason

### Test Requirements
- Morton4D round-trip tests
- S³ binning consistency tests
- Selection rule validation tests
- Edge case tests (boundary conditions)

---

## Week 4: Basic Syscalls with Quantum Context

### File Structure
```
packages/kernel-syscalls/
├── src/
│   ├── place.rs             # place syscall
│   ├── move.rs              # move syscall
│   ├── sense.rs             # sense syscall
│   ├── emit.rs              # emit syscall
│   ├── syscall_common.rs    # Common syscall logic
│   └── lib.rs
├── tests/
│   ├── place_tests.rs
│   ├── move_tests.rs
│   ├── sense_tests.rs
│   └── emit_tests.rs
└── Cargo.toml
```

### Core Requirements

**place(entity, pose, attrs):**
- Accept QAddr context
- Validate selection rules (Δn, Δℓ, Δm, Δs)
- Check Pauli exclusion (no double-occupancy)
- Generate CMSE ResidueMask
- Create VIF witness
- Store in CMC with bitemporal timestamps
- Update spatial index
- Return entity_id

**move(id, Δpose):**
- Accept QAddr context
- Validate selection rules
- Compute screw motion (dual quaternion composition)
- Update Morton4D/S³ bin
- Generate VIF motion proof
- Update CMC atom
- Update spatial index
- Return new pose

**sense(region, filters):**
- Accept QAddr context (observer's quantum numbers)
- Validate visibility (observer's n,ℓ permits)
- Query spatial index (Morton4D + S³ cone)
- Filter by quantum numbers
- Order by (spacetime proximity, energy proximity)
- Return List<Entity>

**emit(event, effect):**
- Accept QAddr context
- Validate selection rules
- Splat κ/λ/ρ fields at pose
- Generate VIF witness
- Store bitemporal fact
- Record ResidueMask
- Return emission_id

### Test Requirements
- Syscall unit tests
- Selection rule violation tests
- Pauli exclusion tests
- Integration tests
- Deterministic replay tests

---

## Implementation Checklist

### Week 1-2: Quaternion Math
- [ ] Create `packages/quaternion-math/` structure
- [ ] Implement QQuat with all operations
- [ ] Implement DualQuat with screw motion
- [ ] Implement DoubleQuat for 4D rotations
- [ ] Implement sign canonicalization
- [ ] Write comprehensive tests
- [ ] Document API

### Week 3: Spatial Indexing + Quantum Numbers
- [ ] Create `packages/spatial-index/` structure
- [ ] Implement Morton4D encoding/decoding
- [ ] Implement S³ binning algorithm
- [ ] Implement QAddr structure
- [ ] Implement selection rule validation
- [ ] Write comprehensive tests
- [ ] Document API

### Week 4: Basic Syscalls
- [ ] Create `packages/kernel-syscalls/` structure
- [ ] Implement `place` syscall
- [ ] Implement `move` syscall
- [ ] Implement `sense` syscall
- [ ] Implement `emit` syscall
- [ ] Integrate with CMC, VIF, CMSE
- [ ] Write comprehensive tests
- [ ] Document API

---

## Success Criteria

**Week 1-2:**
- ✅ All quaternion operations deterministic and tested
- ✅ Sign canonicalization working correctly
- ✅ SLERP interpolation smooth and stable

**Week 3:**
- ✅ Morton4D encoding/decoding correct
- ✅ S³ binning algorithm working
- ✅ Selection rules validated correctly
- ✅ QAddr structure complete

**Week 4:**
- ✅ All four syscalls implemented
- ✅ Selection rules enforced
- ✅ Pauli exclusion working
- ✅ Integration with CMC/VIF/CMSE working
- ✅ Deterministic replay verified

---

**Status:** ✅ Phase 1 plan complete  
**Next Action:** Begin Week 1-2 implementation (Quaternion Math Library)

