# IGODN Quick Start Guide

**For:** Developers continuing IGODN work after chat reset

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd packages/igodn
npm install
```

### 2. Build

```bash
npm run build
```

### 3. Run Tests

```bash
npm test
```

### 4. Basic Usage

```typescript
import {
  create_igodn_field,
  create_default_anchors,
  add_node_to_field,
  simulate_igodn,
  DefaultCompatibilityMatrix,
  DefaultConflictMatrix,
  DefaultConstitutionalLinkMatrix
} from '@aimos/igodn';

// Create field
const anchors = create_default_anchors();
const field = create_igodn_field(anchors);

// Add intent node
const intent = {
  id: 'intent-1',
  type: 'INTENT' as const,
  cluster: 'EXPERIMENTAL' as const,
  position: {
    rotation: { w: 1, x: 0, y: 0, z: 0 },
    translation: { x: 2, y: 0, z: 0 },
    dual: { w: 0, x: 0, y: 0, z: 0 }
  },
  velocity: { x: 0, y: 0, z: 0 },
  mass: 1.0,
  perimeter_radius: 0.5,
  metadata: {
    timestamp: new Date().toISOString(),
    intent_authority: 0.7,
    intent_priority: 0.8
  }
};

add_node_to_field(field, intent);

// Create matrices
const compatibility = new DefaultCompatibilityMatrix();
const conflict = new DefaultConflictMatrix();
const constitutional = new DefaultConstitutionalLinkMatrix();

// Run simulation
await simulate_igodn(field, compatibility, conflict, constitutional, {
  max_iterations: 1000,
  convergence_threshold: 1e-8
});

// Check results
console.log(`Converged: ${field.state.converged}`);
console.log(`Energy: ${field.state.total_energy}`);
console.log(`Iterations: ${field.state.iteration}`);
```

---

## 📁 Key Files

- **Types:** `src/types.ts` - All type definitions
- **Core Engine:** `src/core/` - Physics engine
- **Matrices:** `src/matrices/` - Compatibility, conflict, constitutional
- **Tests:** `src/__tests__/` - Test suites
- **Main Entry:** `src/index.ts` - Exports

---

## 🔍 Finding Things

### Where is X?

- **Distance calculation:** `src/core/distance.ts`
- **Mass calculation:** `src/core/mass.ts`
- **Force calculations:** `src/core/forces.ts`
- **Simulation loop:** `src/core/simulation.ts`
- **Field management:** `src/core/field.ts`
- **Cluster inference:** `src/core/clusters.ts`
- **Matrix implementations:** `src/matrices/`

---

## 🐛 Common Issues

### Type Errors
- Check `src/types.ts` for correct type definitions
- Ensure all required fields are present

### Simulation Not Converging
- Check field parameters (G, k_barrier, c_damp)
- Verify nodes have proper masses
- Check compatibility/conflict matrices

### Tests Failing
- Run `npm run build` first
- Check test setup in `package.json`

---

## 📚 Next Steps

1. Read `COMPREHENSIVE_STATUS.md` for full context
2. Review `PHASE2_PROGRESS.md` for what's done
3. Check `IMPLEMENTATION_SUMMARY.md` for overview
4. Start Phase 3 integration work

---

## 🔗 Related Documents

- **Technical Spec:** `knowledge_architecture/systems/cif/IGODN_TECHNICAL_SPECIFICATION.md`
- **Status:** `packages/igodn/COMPREHENSIVE_STATUS.md`
- **Progress:** `packages/igodn/PHASE2_PROGRESS.md`

