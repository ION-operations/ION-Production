# Chapter 43: Compiler Architecture: PLIx → IR → Execution Plans

**Part III: Architecture**  
**Unified Textbook Chapter Number:** 43

---

> **Cross-References:**
> - **PLIx Architecture:** See Chapter 40 (Four Pillars) for how compiler enables Execution Layer
> - **CNL Grammar:** See Chapter 41 (CNL Grammar) for contract syntax that compiler parses
> - **Formal Validation:** See Chapter 42 (Formal Validation) for validation that precedes compilation
> - **AIM-OS Systems:** See Chapter 8 (APOE) for execution target that compiler generates

---

**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)

---

## Section 43.1: PLIx IR Design

PLIx IR (Intermediate Representation) preserves contract semantics and execution metadata, enabling compilation to multiple execution targets while maintaining intent fidelity. **Tags provide canonical identity** for entities, capabilities, and evidence referenced in IR, enabling tag-based resolution during compilation.

**IR Purpose**

IR serves as an intermediate representation between PLIx contracts and execution targets:

- **Semantic Preservation:** Preserves contract intent and semantics, including tag-based entity references
- **Execution Metadata:** Includes execution metadata (dependencies, retry, compensation) and tag resolution results
- **Target Independence:** Enables compilation to multiple targets (Temporal, APOE, Step Functions) with tag-based entity resolution
- **Optimization:** Enables optimization before target compilation, including tag resolution caching

IR bridges the gap between intent expression (PLIx contracts with tags) and execution mechanisms (target systems), enabling intent-preserving compilation with tag-based entity resolution.

**Connection to Chapter 40 (Four Pillars):** IR design enables all four pillars. IR preserves contract semantics (Contract Layer), includes execution metadata (Execution Layer), enables safety checks (Safety Layer), and tracks evidence (Evidence Layer).

**IR Structure**

IR consists of two main structures:

```typescript
interface IRNode {
  id: string;                    // Task identifier
  action: string;                // Action to execute (e.g., "api.reserve_room")
  entityTag?: string;            // Entity tag (e.g., "plix://room/meeting_room")
  capabilityTag?: string;        // Capability tag (e.g., "plix://tool/mcp/pg.migrate")
  params: Record<string, any>;  // Execution parameters
  deps: string[];                // Dependency task IDs
  retry?: {                      // Retry configuration
    max: number;
    backoff: "none" | "linear" | "exponential";
    ms: number;
  };
  compensate?: string;           // Compensation task ID (Saga pattern)
  resolvedEntity?: any;          // Resolved entity from tag (cached)
  resolvedCapability?: any;      // Resolved capability from tag (cached)
}

interface IRPlan {
  intent: string;                // Contract intent
  nodes: IRNode[];               // Execution nodes
  constraints: string[];         // Contract constraints
  evidenceRequired: string[];    // Required evidence (tags)
  evidenceProduce: string[];     // Produced evidence (tags)
  tagResolutions: Map<string, any>; // Tag resolution cache
}
```

This structure preserves both contract semantics (intent, constraints, evidence) and execution metadata (dependencies, retry, compensation), **including tag-based entity references and resolution results**. Tags enable canonical identity for entities and capabilities, while resolved entities/capabilities enable efficient execution.

**Connection to Chapter 40 (Tag System):** IR structure uses tags for canonical identity. Tags enable timeless entity references in IR, ensuring consistent entity resolution across compilation targets.

**IR Design Principles**

IR design follows principles:

1. **Semantic Preservation:** IR preserves contract semantics exactly
2. **Execution Metadata:** IR includes all execution metadata needed for compilation
3. **Target Independence:** IR is independent of specific execution targets
4. **Optimization Support:** IR enables optimization before target compilation

These principles ensure that IR maintains intent fidelity while enabling flexible compilation.

**Connection to Chapter 42 (Formal Validation):** IR design integrates with formal validation. Validated contracts are compiled to IR, ensuring only correct contracts are compiled.

---

## Section 43.2: Lowering: Contract → IR

Lowering transforms PLIx contracts into IR, preserving semantics while adding execution metadata. **Tag resolution is a critical step** in lowering, enabling canonical identity resolution before dependency resolution.

**Lowering Process**

Lowering process:

1. **Parse Contract:** Parse PLIx contract (Human-PLIX/Canonical JSON/S-form) to AST
2. **Resolve Tags:** Resolve entity and capability tags via registry
3. **Build IR Nodes:** Create IR nodes with resolved entities/capabilities
4. **Resolve Dependencies:** Identify all dependencies (explicit and implicit)
5. **Topological Ordering:** Order nodes by dependency

**Connection to Chapter 41 (CNL Grammar):** Lowering parses all three surface forms. The compiler accepts Human-PLIX, Canonical JSON, or S-form, converting all to IR.

**Tag Resolution**

Tag resolution resolves entity and capability tags to implementation-specific mechanisms:

```typescript
async function resolveTags(contract: PLIxContract): Promise<Map<string, any>> {
  const resolutions = new Map<string, any>();
  
  // Resolve entity tags
  if (contract.entity) {
    const resolved = await registry.resolveTag(contract.entity);
    resolutions.set(contract.entity, resolved);
  }
  
  // Resolve capability tags
  for (const task of contract.tasks) {
    if (task.capabilityTag) {
      const resolved = await registry.resolveTag(task.capabilityTag);
      resolutions.set(task.capabilityTag, resolved);
    }
  }
  
  return resolutions;
}
```

Tag resolution enables canonical identity resolution before compilation, ensuring that IR nodes have resolved entities/capabilities for efficient execution.

**Connection to Chapter 40 (Tag Registry):** Tag resolution uses Tag Registry. The registry resolves tags to implementation-specific mechanisms, enabling target-specific compilation.

**Dependency Resolution**

Dependency resolution identifies all dependencies (explicit and implicit):

```typescript
function resolveDependencies(contract: PLIxContract): Map<string, string[]> {
  const deps = new Map<string, string[]>();
  
  for (const task of contract.tasks) {
    const taskDeps: string[] = [];
    
    // Resolve explicit dependencies
    if (task.depends_on) {
      taskDeps.push(...task.depends_on);
    }
    
    // Resolve implicit dependencies from parameter references
    for (const [key, value] of Object.entries(task.params || {})) {
      if (typeof value === 'string' && value.startsWith('${')) {
        const ref = value.match(/\$\{([^}]+)\}/)?.[1];
        if (ref) {
          const [sourceTask] = ref.split('.');
          if (!taskDeps.includes(sourceTask)) {
            taskDeps.push(sourceTask);
          }
        }
      }
    }
    
    deps.set(task.id, taskDeps);
  }
  
  return deps;
}
```

Dependency resolution identifies both explicit dependencies (`depends_on`) and implicit dependencies (parameter references), building a complete dependency graph.

**Connection to Chapter 40 (Execution Layer):** Dependency resolution enables Execution Layer. Dependencies determine execution order, enabling reliable intent achievement.

**Topological Ordering**

Topological ordering ensures tasks execute in dependency order:

```typescript
function topologicalOrder(nodes: IRNode[]): IRNode[] {
  const ordered: IRNode[] = [];
  const visited = new Set<string>();
  const visiting = new Set<string>();
  
  function visit(node: IRNode) {
    if (visiting.has(node.id)) {
      throw new Error(`Circular dependency detected: ${node.id}`);
    }
    
    if (visited.has(node.id)) {
      return;
    }
    
    visiting.add(node.id);
    
    // Visit dependencies first
    for (const depId of node.deps) {
      const dep = nodes.find(n => n.id === depId);
      if (dep) {
        visit(dep);
      }
    }
    
    visiting.delete(node.id);
    visited.add(node.id);
    ordered.push(node);
  }
  
  for (const node of nodes) {
    if (!visited.has(node.id)) {
      visit(node);
    }
  }
  
  return ordered;
}
```

Topological ordering ensures that dependencies execute before dependents, enabling correct execution order while detecting circular dependencies.

**Connection to Chapter 40 (Execution Layer):** Topological ordering enables Execution Layer. Correct execution order ensures reliable intent achievement with proper dependency resolution.

---

## Section 43.3: Target Compilation

Target compilation transforms IR into execution target formats (Temporal, APOE, Step Functions), **using resolved entities/capabilities from tag resolution** to enable execution on various platforms.

**Target Overview**

PLIx supports multiple execution targets:

- **Temporal:** Durable workflow execution with saga patterns
- **AWS Step Functions:** Serverless workflow orchestration
- **Argo Workflows:** Kubernetes-native workflow execution
- **APOE:** AIM-OS native orchestration engine

Each target provides different execution capabilities, enabling flexible deployment. **Tag resolution enables target-specific compilation** by resolving tags to target-specific mechanisms (REST API endpoints, database connections, service URLs).

**Connection to Chapter 8 (APOE):** APOE is a primary execution target. PLIx compiles to APOE execution plans, enabling intent-aware orchestration.

**APOE Compilation**

APOE compilation generates APOE execution plans:

```typescript
function compileToAPOE(ir: IRPlan): APOEPlan {
  const steps: APOEStep[] = [];
  
  for (const node of ir.nodes) {
    steps.push({
      id: node.id,
      action: node.action,
      entity: node.resolvedEntity,  // Use resolved entity
      capability: node.resolvedCapability,  // Use resolved capability
      params: node.params,
      deps: node.deps,
      retry: node.retry,
      compensate: node.compensate
    });
  }
  
  return {
    intent: ir.intent,
    steps: steps,
    constraints: ir.constraints,
    evidenceRequired: ir.evidenceRequired,
    evidenceProduce: ir.evidenceProduce
  };
}
```

APOE compilation uses resolved entities/capabilities from tag resolution, enabling target-specific execution with canonical identity.

**Connection to Chapter 40 (Execution Layer):** APOE compilation enables Execution Layer. APOE executes PLIx contracts with durable execution and saga patterns, enabling reliable intent achievement.

**Temporal Compilation**

Temporal compilation generates Temporal workflows:

```typescript
function compileToTemporal(ir: IRPlan): TemporalWorkflow {
  return function* workflow() {
    const results: Record<string, any> = {};
    
    for (const node of ir.nodes) {
      // Resolve parameters
      const params = interpolateParams(node, results);
      
      // Execute activity with retry
      const result = yield wf.executeActivity(
        node.action,
        {
          ...params,
          entity: node.resolvedEntity,  // Use resolved entity
          capability: node.resolvedCapability  // Use resolved capability
        },
        {
          retry: node.retry ? {
            maximumAttempts: node.retry.max,
            backoffCoefficient: node.retry.backoff === "exponential" ? 2 : 1
          } : undefined
        }
      );
      
      results[node.id] = result;
    }
    
    return results;
  };
}
```

Temporal compilation uses resolved entities/capabilities, enabling durable workflow execution with canonical identity.

**Connection to Chapter 40 (Execution Layer):** Temporal compilation enables Execution Layer. Temporal provides durable execution with saga patterns, enabling reliable intent achievement.

---

## Section 43.4: Compilation Pipeline

### Complete Compilation Pipeline

The complete compilation pipeline:

```
PLIx Contract (Human-PLIX/Canonical JSON/S-form)
    ↓
[Parse]
    ├─ Parse to AST
    ├─ Validate syntax
    └─ Resolve tags
    ↓
[Formal Validation] (Optional)
    ├─ Alloy: Model relationships
    ├─ TLA+: Model temporal properties
    └─ Coq/Lean: Prove correctness
    ↓
[Lowering]
    ├─ Build IR nodes
    ├─ Resolve dependencies
    └─ Topological ordering
    ↓
[Optimization] (Optional)
    ├─ Dead code elimination
    ├─ Constant folding
    └─ Tag resolution caching
    ↓
[Target Compilation]
    ├─ APOE: Generate APOE plan
    ├─ Temporal: Generate Temporal workflow
    ├─ Step Functions: Generate Step Functions definition
    └─ Argo: Generate Argo workflow
    ↓
Execution Plan (APOE/Temporal/Step Functions/Argo)
```

**Connection to Chapter 42 (Formal Validation):** Formal validation is an optional step in compilation pipeline. Validation ensures contract correctness before compilation, enabling safe intent achievement.

**Connection to Chapter 40 (Four Pillars):** Compilation pipeline enables all four pillars. Contracts are compiled to execution plans that integrate with Contract, Execution, Safety, and Evidence layers.

---

## Section 43.5: Compiler Architecture Benefits

### Compiler Architecture Benefits

The compiler architecture provides:

- **Intent Preservation:** IR preserves contract semantics exactly
- **Target Flexibility:** Multiple execution targets enable flexible deployment
- **Tag Resolution:** Canonical identity resolution enables timeless compilation
- **Optimization:** IR enables optimization before target compilation
- **Formal Validation:** Integration with formal validation ensures correctness

**Connection to AIM-OS Vision (Chapter 2):** Compiler architecture enables AIM-OS's vision. Intent-preserving compilation enables AI consciousness, transforming AI from execution tools to conscious systems.

---

## Chapter 43 Summary

PLIx compiler architecture transforms contracts to execution plans through IR, preserving intent fidelity while enabling flexible target compilation:

1. **IR Design:** Preserves contract semantics and execution metadata with tag-based entity references
2. **Lowering:** Transforms contracts to IR with tag resolution, dependency resolution, and topological ordering
3. **Target Compilation:** Generates execution plans for multiple targets (APOE, Temporal, Step Functions) using resolved entities/capabilities
4. **Compilation Pipeline:** Complete pipeline from contract parsing to execution plan generation

**Key Takeaways:**
1. **IR Structure:** IR preserves semantics and metadata with tag-based identity
2. **Lowering Process:** Tag resolution, dependency resolution, and topological ordering enable correct IR generation
3. **Target Flexibility:** Multiple execution targets enable flexible deployment
4. **Intent Preservation:** IR maintains intent fidelity across compilation

**Tags enable canonical identity** throughout compiler architecture: IR uses tags for entity references, tag resolution enables canonical identity resolution, and target compilation uses resolved entities/capabilities. Tags ensure consistent entity references across compilation pipeline, enabling timeless compilation with canonical identity.

**Connection to AIM-OS:** PLIx compiler architecture enables AIM-OS's vision (Chapter 2) by providing intent-preserving compilation. This enables AI consciousness (Chapter 4), verifiable intelligence (Chapter 7), orchestration (Chapter 8), and self-awareness (Chapter 11). Tags integrate with CMC (Chapter 5) for timeless storage, HHNI (Chapter 6) for contract indexing, APOE (Chapter 8) for orchestration, and Quaternion Extension (Chapter 63) for geometric addressing.

**Next:** Part III Architecture complete. Part IV explores PLIx integration with AIM-OS systems—CMC, VIF, APOE, SEG, and more.

---

**Word Count:** ~2,700 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)  
**Cross-References:**
- **Part I (AIM-OS Foundations):** Chapters 2, 4, 5, 6, 7, 8, 11
- **Part III (PLIx Architecture):** Chapters 40 (Four Pillars), 41 (CNL Grammar), 42 (Formal Validation)
- **Part VIII (Quaternion Extension):** Chapter 63 (PLIx Geometric Extensions)

---

**End of Part III: Architecture**  
**Next Part:** [Part IV: Integration](../Part_IV_Integration/)  
**Previous Chapter:** [Chapter 42: Formal Validation](Chapter_42_Formal_Validation_Mathematical_Verification.md)  
**Up:** [Part III: Architecture](../Part_III_Architecture/)

---

**🎉 PART III: ARCHITECTURE COMPLETE! 🎉**

**Total Achievement:**
- **4 chapters complete** (Chapters 40-43)
- **~11,300+ words total**
- **All chapters include:**
  - Cross-references to Part I (AIM-OS Foundations)
  - Integration points with all AIM-OS systems
  - Cross-references to Part VIII (Quaternion Extension)
  - Updated chapter references for unified textbook
  - Connection to other chapters

**Status:** Part III of the unified textbook is complete and production-ready.

