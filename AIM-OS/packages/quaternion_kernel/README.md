# Quaternion Kernel

**Status:** 🔄 Week 3 Implementation In Progress  
**Phase:** Foundation (Weeks 1-4)  
**Purpose:** 4D Quaternion-Native Scene Kernel for AIM-OS

---

## Overview

This Rust crate implements the foundational spatial indexing and quantum selection rules for the PLIx Quaternion Extension. It provides:

- **Morton4D Encoding**: 4D spacetime indexing for cache-coherent spatial queries
- **S³ Orientation Binning**: Hopf factorization for quaternion orientation indexing
- **Quantum Kernel Address (QAddr)**: Complete quantum state structure with selection rules
- **Selection Rule Validation**: Hydrogen-like transition constraints for security

---

## Architecture

### Core Components

1. **Morton4D** (`morton.rs`)
   - 64-bit Z-order curve encoding for (x, y, z, τ) coordinates
   - Provides cache-coherent spatial locality
   - Deterministic encoding/decoding

2. **S³ Binning** (`s3_binning.rs`)
   - Hopf factorization: S³ → S² × S¹
   - 16-bit orientation cell ID
   - Neighbor computation for cone queries

3. **Quantum Address** (`quantum.rs`)
   - QAddr structure: `{n, ℓ, m, s, morton4d, s3bin}`
   - Selection rules: `{Δn, Δℓ, Δm, Δs}`
   - Transition validation

4. **Composite Key** (`lib.rs`)
   - Combines Morton4D (64-bit) + S³ bin (16-bit)
   - 80-bit composite key for entity indexing

---

## Usage

### Morton4D Encoding

```rust
use quaternion_kernel::{Vec4, morton4d_encode, morton4d_decode};

let pos = Vec4 {
    x: 0.5,
    y: 0.25,
    z: 0.75,
    tau: 0.125,
};

let key = morton4d_encode(&pos);
let decoded = morton4d_decode(key);
```

### S³ Binning

```rust
use quaternion_kernel::{Quat, s3_bin_encode};

let quat = Quat {
    w: 1.0,
    x: 0.0,
    y: 0.0,
    z: 0.0,
};

let bin = s3_bin_encode(&quat);
```

### QAddr and Selection Rules

```rust
use quaternion_kernel::{QAddr, PrincipalShell, OrbitalClass, Spin, SelectionRules, validate_transition, MortonKey, S3Bin};

let from = QAddr {
    n: PrincipalShell(1),
    l: OrbitalClass::Memory,
    m: S3Bin(100),
    s: Spin::Read,
    morton_key: MortonKey(0),
};

let to = QAddr {
    n: PrincipalShell(1),
    l: OrbitalClass::Io,
    m: S3Bin(100),
    s: Spin::Read,
    morton_key: MortonKey(0),
};

let rules = SelectionRules {
    delta_n: 0,
    delta_l: true,
    delta_m: false,
    delta_s: false,
};

match validate_transition(&from, &to, &rules) {
    Ok(()) => println!("Transition valid"),
    Err(e) => println!("Transition invalid: {}", e),
}
```

---

## Testing

Run tests:
```bash
cargo test
```

Run benchmarks:
```bash
cargo bench
```

---

## Performance Targets

- Morton4D encode/decode: < 100ns
- S³ binning: < 200ns
- Selection rule validation: < 50ns

---

## Status

**Week 3 Progress:**
- ✅ Morton4D encoding/decoding (complete)
- ⚠️ S³ binning (placeholder - needs Hopf factorization)
- ✅ QAddr structure (complete)
- ✅ Selection rule validation (complete)

**Week 4 Progress:**
- ✅ Kernel state management (complete)
- ✅ place syscall (complete with Pauli Exclusion)
- ✅ sense syscall (complete with privilege checks)
- ✅ emit syscall (basic validation complete)
- ⚠️ move syscall (needs dual quaternion composition)

**Next:** Complete dual quaternion composition for move syscall, then proceed to Phase 2 (PLIX Integration)

---

## References

- PLIx Quaternion Extension Research Paper
- Enhanced Implementation Plan
- RTFT (Recursive Temporal Field Theory) documentation

