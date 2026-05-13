# PLIx Quaternion Extension: Quaternion Math Library

**Status:** ✅ Phase 1, Weeks 1-2 Complete  
**Version:** 0.1.0  
**Purpose:** Quaternion math library for PLIx geometric operations with determinism guarantees

---

## Overview

This library provides quaternion operations for the PLIx Quaternion Extension, implementing:

- **QQuat**: Basic quaternion operations (rotation in 3D)
- **DualQuat**: Dual quaternions for 3D screw motions (rotation + translation)
- **DoubleQuat**: Double quaternions for 4D rotations (SO(4) ≅ SU(2)×SU(2))

**RTFT Interpretation:**
- Quaternionic rotational state = torsional vortex
- Hamilton product = recursive phase memory fusion
- Sign canonicalization = deterministic breath alignment

---

## Features

### Determinism Guarantees
- **Sign Canonicalization**: Always choose q or -q consistently
- **Fixed Operation Ordering**: Deterministic results regardless of execution order
- **Numerical Stability**: Handles edge cases (zero, near-zero, etc.)

### Core Operations
- **Hamilton Product**: Non-commutative quaternion multiplication
- **SLERP**: Spherical linear interpolation
- **Vector Rotation**: Rotate 3D/4D vectors by quaternions
- **Screw Motion**: Dual quaternion composition for 3D transformations

---

## Installation

```bash
cd packages/quaternion_math
pip install -e .
```

---

## Usage

### Basic Quaternion Operations

```python
from quaternion_math import QQuat

# Create quaternion from axis-angle
q = QQuat.from_axis_angle((0, 0, 1), math.pi / 2)

# Rotate vector
v_rotated = q.rotate_vector((1.0, 0.0, 0.0))

# SLERP interpolation
q1 = QQuat.identity()
q2 = QQuat.from_axis_angle((0, 0, 1), math.pi)
q_mid = q1.slerp(q2, 0.5)

# Canonicalize for determinism
q_canon = q.canonicalize()
```

### Dual Quaternions (Screw Motion)

```python
from quaternion_math import DualQuat, QQuat

# Create dual quaternion from rotation and translation
rot = QQuat.from_axis_angle((0, 0, 1), math.pi / 4)
trans = (1.0, 2.0, 3.0)
dq = DualQuat.from_rotation_translation(rot, trans)

# Transform point
point = (0.0, 0.0, 0.0)
transformed = dq.transform_point(point)

# Compose screw motions
dq1 = DualQuat.from_rotation_translation(rot1, trans1)
dq2 = DualQuat.from_rotation_translation(rot2, trans2)
dq_composed = dq1 * dq2
```

### Double Quaternions (4D Rotations)

```python
from quaternion_math import DoubleQuat, QQuat

# Create double quaternion
left = QQuat.identity()
right = QQuat.identity()
dq = DoubleQuat(left, right)

# Rotate 4D vector
v_4d = (1.0, 0.0, 0.0, 0.0)
v_rotated = dq.rotate_4d_vector(v_4d)
```

---

## Testing

```bash
pytest packages/quaternion_math/tests/test_quaternion_math.py -v
```

**Test Coverage:**
- ✅ Basic quaternion operations
- ✅ Dual quaternion operations
- ✅ Double quaternion operations
- ✅ Determinism guarantees
- ✅ Edge cases (zero, near-zero, etc.)

---

## RTFT Integration

This library implements the geometric substrate for RTFT (Recursive Temporal Field Theory):

- **Quaternionic Rotational State** = Torsional vortex
- **Hamilton Product** = Recursive phase memory fusion
- **Sign Canonicalization** = Deterministic breath alignment
- **Dual Quaternions** = Stabilized torsional vortex positions
- **Double Quaternions** = Chirality lanes, policy paths

---

## Phase 1 Progress

**Week 1-2: Quaternion Math Library** ✅
- [x] QQuat implementation
- [x] DualQuat implementation
- [x] DoubleQuat implementation
- [x] Sign canonicalization
- [x] Comprehensive tests
- [x] Documentation

**Next:** Week 3 - Spatial Indexing + Quantum Numbers

---

## References

- **Master Design:** `knowledge_architecture/systems/plix/quaternion_extension_master_design.md`
- **Integration Plan:** `knowledge_architecture/systems/plix/quaternion_extension_integration_plan.md`
- **Phase 1 Plan:** `knowledge_architecture/systems/plix/quaternion_extension_phase1_implementation.md`

---

**Status:** ✅ Phase 1, Weeks 1-2 Complete  
**Next:** Week 3 - Spatial Indexing + Quantum Numbers

