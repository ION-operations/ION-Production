# PLIx - Programmatic-Linguistic Interface

**Status:** 🚀 **ACTIVE** - Research & Implementation Phase  
**Version:** 0.1.0  
**Purpose:** Typed intent/contract layer bridging NL intents to executable multi-agent/tool plans

---

## Overview

PLIx is a **typed intent/contract layer** that bridges natural language intents and executable multi-agent/tool plans. It provides:

- **Human-legible yet machine-strict** intent contracts with pre/post conditions
- **Durable, recoverable** execution graphs with retries/compensations
- **Evidence chains** linking every claim/step to artifacts, sources, diffs, tests
- **Confidence/quality gates** enforced across tools/agents
- **Bitemporal memory** integration for auditability

---

## Core Components

### Models
- **Schema** (`src/models/schema.ts`) - PLIx v1 JSON Schema and TypeScript types
- **Research** (`src/models/research.ts`) - Research data extraction forms and comparison matrix types

### Compiler
- **Compiler** (`src/compiler.ts`) - NL → PLIx compilation (stub implementation)

### Comparison Matrix
- **Comparison Matrix** (`src/comparison-matrix.ts`) - System for managing research findings
- **Initial Data** (`src/data/initial-matrix.ts`) - Populated comparison matrix from research

### Interop Adapters
- **Interop Adapters** (`src/interop-adapters.ts`) - Compile PLIx to Temporal, OPA, PROV, PDDL

### Benchmarks
- **Benchmarks** (`src/benchmarks.ts`) - IDE task suite for evaluating PLIx vs baseline

---

## Usage

### Compile NL Intent to PLIx

```typescript
import { PLIxCompiler } from '@aimos/plix';

const intent = await PLIxCompiler.compileIntent(
  'Add remember me checkbox to login form while maintaining test coverage',
  {
    entities: ['LoginForm', 'TestSuite'],
    scope: 'frontend',
    risk: 0.3,
  }
);

const validation = PLIxCompiler.validateIntent(intent);
console.log(validation); // { valid: true, errors: [], warnings: [...] }
```

### Compile to Temporal

```typescript
import { PLIxToTemporalAdapter } from '@aimos/plix';

const workflow = PLIxToTemporalAdapter.compile(intent);
console.log(workflow); // Temporal workflow definition
```

### Run Benchmarks

```typescript
import { PLIxBenchmarkRunner, IDE_TASK_SUITE } from '@aimos/plix';

const results = await PLIxBenchmarkRunner.runSuite(true); // Use PLIx
const baseline = await PLIxBenchmarkRunner.runSuite(false); // Baseline

const comparison = PLIxBenchmarkRunner.compareResults(baseline, results);
console.log(comparison); // Improvement metrics
```

---

## Research Status

- ✅ Research protocol defined
- ✅ Comparison matrix populated (13 systems analyzed)
- ✅ PLIx v1 schema complete
- ⏳ Compiler stub implementation (in progress)
- ⏳ Interop adapters (stub implementations)
- ⏳ IDE integration (planned)

---

## Integration with AIM-OS

- **CMC:** Store PLIx contracts/plans as atoms
- **HHNI:** Index by intent, contract, plan structure
- **SEG:** Evidence chains as graph edges
- **VIF:** Confidence gates as witnesses
- **APOE:** Plan execution orchestration
- **TCS:** Bitemporal timeline for auditability

---

## Documentation

- **T0 Executive:** `knowledge_architecture/systems/plix/T0_executive.md`
- **T1 Overview:** `knowledge_architecture/systems/plix/T1_overview.md`
- **Research Protocol:** `knowledge_architecture/systems/plix/PLIX_DEEP_RESEARCH_PROTOCOL.md`
- **Research Findings:** `knowledge_architecture/systems/plix/RESEARCH_FINDINGS.md`

---

## Development

```bash
# Build
npm run build

# Type check
npm run type-check

# Test
npm test

# Lint
npm run lint
```

---

**Next Steps:** Complete compiler stub, implement interop adapters, build IDE integration

