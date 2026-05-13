# Phase 3: Integration Roadmap

**Status:** Ready to Begin  
**Estimated Time:** 20-30 hours  
**Dependencies:** CIF, PCE, VIF, HHNI, Quaternion Kernel packages

---

## Overview

Phase 3 integrates IGODN with AIM-OS systems:
1. CIF Integration (utterance → nodes)
2. PCE Integration (field → contract decisions)
3. VIF Integration (converged state → witness)
4. Quaternion Kernel Integration (real SO(3) distance)
5. HHNI Integration (semantic distances)

---

## 1. CIF Integration (6-8 hours) 🚧 Started

**Status:** Structure created, needs implementation

**Files:**
- ✅ `src/integration/cif_types.ts` - Types defined
- ✅ `src/integration/cif_converter.ts` - Structure created
- ⏳ `src/__tests__/cif_integration.test.ts` - Needs tests

**Tasks:**
- [ ] Find/check CIF package structure
- [ ] Implement real CIF utterance parsing
- [ ] Implement HHNI-based semantic positioning
- [ ] Implement anchor-based positioning
- [ ] Add comprehensive tests

**Dependencies:**
- CIF package (need to locate)
- HHNI package (`@aimos/hhni`)

---

## 2. PCE Integration (6-8 hours)

**Status:** Not started

**Files to Create:**
- `src/integration/pce_interpreter.ts`
- `src/integration/pce_types.ts`
- `src/__tests__/pce_integration.test.ts`

**Tasks:**
- [ ] Create `IGODNToPCEInterpreter` class
- [ ] Implement `compute_intent_scores()` (from spec)
- [ ] Generate reinforcement decisions
- [ ] Generate conflict decisions
- [ ] Generate new doctrine decisions
- [ ] Convert to PLIx contract format
- [ ] Add tests

**Key Function (from spec):**
```typescript
private compute_intent_scores(
  intent_node: IGODNNode,
  field: IGODNField
): { reinforcement_score: number; conflict_score: number; novelty_score: number }
```

**Dependencies:**
- PLIx package (`@aimos/plix`)
- PCE system structure

---

## 3. VIF Integration (2-3 hours)

**Status:** Hook ready in simulation

**Files to Create:**
- `src/integration/vif_witness.ts`
- `src/__tests__/vif_integration.test.ts`

**Tasks:**
- [ ] Create `seal_vif_witness()` function
- [ ] Integrate with VIF package
- [ ] Map nodes to QAddrs
- [ ] Create VIF witness
- [ ] Store in CMC with bitemporal tracking
- [ ] Add tests

**Dependencies:**
- VIF package (`@aimos/vif`)
- CMC service
- Quaternion kernel (for QAddr mapping)

---

## 4. Quaternion Kernel Integration (4-6 hours)

**Status:** Placeholders ready

**Files to Update:**
- `src/utils/quaternions.ts`

**Tasks:**
- [ ] Find quaternion kernel package
- [ ] Import quaternion functions
- [ ] Replace `quaternion_geodesic_distance()` placeholder
- [ ] Replace `dual_quat_to_position()` placeholder
- [ ] Replace `get_hopf_fiber()` placeholder
- [ ] Test SO(3)-invariant distance
- [ ] Verify screw-motion trajectories

**Dependencies:**
- Quaternion kernel package

---

## 5. HHNI Integration (3-4 hours)

**Status:** Fallback in place

**Files to Update:**
- `src/core/distance.ts` (semantic distance)
- `src/integration/hhni_integration.ts` (new)

**Tasks:**
- [ ] Integrate HHNI client
- [ ] Use HHNI for semantic distance
- [ ] Create concept nodes from HHNI
- [ ] Add tests

**Dependencies:**
- HHNI package (`@aimos/hhni`)

---

## Testing Strategy

1. **Unit Tests:** Each integration module independently
2. **Integration Tests:** End-to-end with real AIM-OS data
3. **Performance Tests:** Large fields (1000+ nodes)
4. **Validation Tests:** Compare with expected behavior

---

## Success Criteria

Phase 3 complete when:
- [ ] CIF utterances convert to IGODN nodes
- [ ] IGODN field interpreted for PCE decisions
- [ ] Converged states sealed as VIF witnesses
- [ ] Quaternion kernel provides real distances
- [ ] HHNI provides semantic distances
- [ ] All integration tests passing

---

## Order of Implementation

**Recommended Order:**
1. CIF Integration (most straightforward, needed first)
2. HHNI Integration (needed for CIF semantic positioning)
3. PCE Integration (uses field state)
4. VIF Integration (uses converged state)
5. Quaternion Kernel (enhances all distance calculations)

---

## Notes

- Start with CIF integration (structure already created)
- Check package locations before starting each integration
- Test incrementally as each integration completes
- Update `COMPREHENSIVE_STATUS.md` after each milestone

