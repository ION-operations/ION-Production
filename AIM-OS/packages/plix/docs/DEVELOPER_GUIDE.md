# PLIx Developer Guide

**Version:** 1.0.0  
**Date:** 2025-01-27  
**Audience:** Developers extending or contributing to PLIx

---

## 🎯 **Overview**

This guide covers PLIx internals, architecture, and how to extend the system.

---

## 📐 **Architecture Overview**

### **Pipeline Stages**

```
Human-PLIx Text
    ↓
[Parser] → AST
    ↓
[Type Checker] → Annotated AST (Γ ⊢ t : T ! ε ▷ φ)
    ↓
[Effect Checker] → Validated AST
    ↓
[Compiler] → AIP Graph + APOE Plan
    ↓
[Backends] → TLA+ / Alloy / OPA / IRPlan
    ↓
[Runtime] → Execution + Evidence
    ↓
[Verifier] → Cryptographic Verification
```

### **Module Structure**

```
packages/plix/src/
├── parser/           # Human-PLIx → AST
├── semantics/        # Type system, effects, subdistribution
├── compiler/         # AST → AIP/APOE
├── backends/         # Target format generation
├── pipeline/         # End-to-end orchestration
├── runtime/          # Execution engines
└── models/           # Type definitions
```

---

## 🔧 **Core Components**

### **1. Parser (`parser/index.ts`)**

**Responsibility:** Convert Human-PLIx text to structured AST

**Key Features:**
- Indentation-based syntax
- Dual syntax support (Core-PLIx formal + Human-PLIx simplified)
- Tag resolution
- Dependency validation

**Extending the Parser:**

```typescript
// Add new token type
type TokenType = 'speech' | 'entity' | ... | 'your_new_type';

// Add recognition in tokenizeLine
if (line.trim().startsWith('your_keyword')) {
  tokens.push({
    type: 'your_new_type',
    value: 'your_keyword',
    line: lineNum,
    column: indent,
    indent
  });
}

// Add parsing in parseTokens
case 'your_new_type':
  // Your parsing logic
  break;
```

### **2. Semantics Module (`semantics/`)**

**Subdistribution Monad (`subdistribution.ts`):**
- Probabilistic retry/fallback semantics
- Monad operations: `unit`, `bind`, `map`, `fail`, `choice`
- Plan semantics: `⟦plan⟧: State → Dist(State)`

**Annotated Typing (`annotated-typing.ts`):**
- Type judgment: `Γ ⊢ t : T ! ε ▷ φ`
- Effect rows: `{io?, net?, db?, compensable?, idempotent?}`
- Confidence lattice: `[0,1]` with ⊔ and ⊓

**Effect System (`effect-system.ts`):**
- Effect checking
- Capability gating
- Policy engine

**Extending the Type System:**

```typescript
// Add new effect type
export interface EffectRow {
  io?: boolean;
  net?: boolean;
  db?: boolean;
  your_effect?: boolean;  // Add here
}

// Add inference rule
static inferFromName(name: string): EffectRow {
  const effects: EffectRow = {};
  const lower = name.toLowerCase();
  
  if (lower.includes('your_pattern')) {
    effects.your_effect = true;
  }
  
  return effects;
}
```

### **3. Compiler (`compiler/`)**

**AIP Compiler (`aip-compiler.ts`):**
- Converts Intent → AIP Graph
- Tag resolution (HHNI/SEG/CMC cascade)
- APOE plan generation
- VIF witness requirements

**Quaternion Compiler (`quaternion-compiler.ts`):**
- Geometric operations → syscalls
- QAddr resolution
- Hamiltonian cost calculation

**Extending the Compiler:**

```typescript
// Add custom compilation target
async compileToCustomTarget(intent: PLIxIntent): Promise<CustomOutput> {
  const aipGraph = await this.compileToAIPGraph(intent);
  
  // Transform graph to your format
  const customOutput = this.transformToCustom(aipGraph);
  
  return customOutput;
}
```

### **4. Backends (`backends/`)**

**TLA+ Backend (`tlaplus-backend.ts`):**
- Contract → TLA+ invariants
- Plan → TLA+ actions
- Generates TLA+ module for model checking

**Alloy Backend (`alloy-backend.ts`):**
- Entity → Alloy signatures
- Contract → Alloy facts
- Plan → Alloy predicates

**OPA Backend (`opa-backend.ts`):**
- Contract → OPA rules
- Effects → Capability checks
- Runtime policy enforcement

**IRPlan Backend (`irplan-backend.ts`):**
- Primary execution backend
- APOE-compatible format
- Dependency tracking

**Creating a New Backend:**

```typescript
export class MyBackend {
  compile(intent: PLIxIntent): MyFormat {
    // Extract components
    const contract = intent.contract;
    const plan = intent.plan;
    
    // Transform to your format
    return this.transform(contract, plan);
  }
  
  serialize(output: MyFormat): string {
    // Convert to text
    return JSON.stringify(output);
  }
}
```

---

## 🧪 **Testing**

### **Test Structure**

```
__tests__/
├── unit/            # Unit tests (individual functions)
├── integration/     # Integration tests (module interactions)
└── e2e/            # End-to-end tests (full pipeline)
```

### **Writing Tests**

```typescript
import { PLIXParser } from '../parser';

describe('MyFeature', () => {
  test('should handle basic case', () => {
    const parser = new PLIXParser();
    const result = parser.parse(plixText);
    
    expect(result.errors).toHaveLength(0);
    expect(result.intent).toBeDefined();
  });
});
```

### **Golden Example Pattern**

Always test against the golden example (meeting-room reservation):

```typescript
test('should pass golden example', () => {
  const result = backend.compile(goldenExample);
  expect(validate(result)).toBe(true);
});
```

---

## 🔗 **Integration Points**

### **AIM-OS Integration**

**CMC (Context Memory Core):**
```typescript
import { CMCStorageClient } from '../runtime/cmc-storage-client';

const cmc = new CMCStorageClient('http://localhost:5000');
await cmc.storeEntity(entityId, qaddr, metadata);
```

**HHNI (Hierarchical Hypergraph Neural Index):**
```typescript
import { HHNIClient } from '../compiler/hhni-client';

const hhni = new HHNIHTTPClient('http://localhost:5001');
const qaddr = await hhni.resolveTagToQAddr(tag);
```

**SEG (Shared Evidence Graph):**
```typescript
import { SEGClient } from '../compiler/seg-client';

const seg = new SEGHTTPClient('http://localhost:5002');
await seg.trackSyscall(syscallId, entityId, operation, qaddr);
```

**VIF (Verifiable Immutable Facts):**
```typescript
// VIF witnesses automatically generated during compilation
const witnesses = compiler.generateWitnessRequirements(intent);
```

---

## 📚 **Advanced Topics**

### **Subdistribution Monad**

Model probabilistic execution formally:

```typescript
import { Dist, Retry, Fallback } from '../semantics/subdistribution';

// Create distribution
const action = (state: State) => Dist.unit(newState);

// Add retry
const retryAction = Retry.retry(action, 3, 0.8);

// Add fallback
const fallbackAction = Fallback.fallback(primary, alternative, 0.7);

// Compute plan semantics
const planSemantics = Plan.computePlanSemantics(steps, dependencies);
```

### **Effect Row System**

Enforce capability-based security:

```typescript
import { EffectChecker, PolicyEngine } from '../semantics/effect-system';

// Register context capabilities
effectChecker.registerContext('sandbox', { io: true });

// Check action
const result = effectChecker.checkAction('sandbox', { io: true, net: true });
// result.allowed = false (net not allowed)
```

### **Annotated Typing**

Type check with effects and confidence:

```typescript
import { AnnotatedTypeChecker, TypingContext } from '../semantics/annotated-typing';

const checker = new AnnotatedTypeChecker();
const context = new TypingContext();

const judgment = checker.check(context, term);
// judgment: Γ ⊢ t : T ! ε ▷ φ
```

---

## 🌟 **Contributing**

### **Code Style**

- **TypeScript strict mode**
- **Comprehensive type annotations**
- **JSDoc comments for public APIs**
- **Functional style preferred**
- **Immutable data structures**

### **Commit Messages**

```
[Component] Brief description

Details:
- What changed
- Why it changed
- Any breaking changes

Tests: Added/Modified X tests
Docs: Updated/Added documentation
```

### **Pull Request Process**

1. Fork repository
2. Create feature branch
3. Write tests first (TDD)
4. Implement feature
5. Run full test suite
6. Update documentation
7. Submit PR with description

### **Testing Requirements**

- **All tests must pass**
- **New code must have >90% coverage**
- **Include edge cases**
- **Golden example must pass**

---

## 📖 **Further Reading**

- [Core-PLIx Semantics](../../knowledge_architecture/systems/plix/research/formal_semantics/core_semantics_v01_final.md)
- [Grammar Specification](../../knowledge_architecture/systems/plix/GRAMMAR_SPECIFICATION_V2.md)
- [Pipeline Specification](../../knowledge_architecture/systems/plix/research/compilation_pipeline/pipeline_specification.md)

---

**Questions?** See [Troubleshooting](#troubleshooting) or open an issue.

**Happy hacking!** 🔥

