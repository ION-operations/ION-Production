# Chapter 8: Compiler Architecture: PLIx → IR → Execution Plans

**Part:** II - Architecture  
**Chapter:** 8  
**Target Word Count:** 2,500-3,000 words (enhanced from 2,000-2,500)  
**Status:** ✅ **COMPLETE** (v2.0 Enhanced)

---

## Section 8.1: PLIx IR Design

PLIx IR (Intermediate Representation) preserves contract semantics and execution metadata, enabling compilation to multiple execution targets while maintaining intent fidelity. **Tags provide canonical identity** for entities, capabilities, and evidence referenced in IR, enabling tag-based resolution during compilation.

**IR Purpose**

IR serves as an intermediate representation between PLIx contracts and execution targets:

- **Semantic Preservation:** Preserves contract intent and semantics, including tag-based entity references
- **Execution Metadata:** Includes execution metadata (dependencies, retry, compensation) and tag resolution results
- **Target Independence:** Enables compilation to multiple targets (Temporal, APOE, Step Functions) with tag-based entity resolution
- **Optimization:** Enables optimization before target compilation, including tag resolution caching

IR bridges the gap between intent expression (PLIx contracts with tags) and execution mechanisms (target systems), enabling intent-preserving compilation with tag-based entity resolution.

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

**IR Design Principles**

IR design follows principles:

1. **Semantic Preservation:** IR preserves contract semantics exactly
2. **Execution Metadata:** IR includes all execution metadata needed for compilation
3. **Target Independence:** IR is independent of specific execution targets
4. **Optimization Support:** IR enables optimization before target compilation

These principles ensure that IR maintains intent fidelity while enabling flexible compilation.

**IR Example**

Example IR for room booking contract:

```typescript
const irPlan: IRPlan = {
  intent: "Book a meeting room",
  nodes: [
    {
      id: "check_availability",
      action: "api.check_room_availability",
      entityTag: "plix://room/meeting_room",  // Entity tag
      params: {
        date: "2025-12-01",
        duration: 2
      },
      deps: [],
      retry: {
        max: 3,
        backoff: "exponential",
        ms: 1000
      },
      resolvedEntity: {  // Resolved entity (cached)
        type: "database_table",
        location: "postgresql://db/rooms",
        schema: "public.rooms"
      }
    },
    {
      id: "reserve_room",
      action: "api.reserve_room",
      entityTag: "plix://room/meeting_room",  // Same entity tag
      params: {
        room_id: "${check_availability.room_id}",
        duration: 2
      },
      deps: ["check_availability"],
      compensate: "cancel_reservation",
      resolvedEntity: {  // Same resolved entity (reused from cache)
        type: "database_table",
        location: "postgresql://db/rooms",
        schema: "public.rooms"
      }
    },
    {
      id: "cancel_reservation",
      action: "api.cancel_reservation",
      entityTag: "plix://room/meeting_room",  // Same entity tag
      params: {
        reservation_id: "${reserve_room.res_id}"
      },
      deps: [],
      resolvedEntity: {  // Same resolved entity (reused from cache)
        type: "database_table",
        location: "postgresql://db/rooms",
        schema: "public.rooms"
      }
    }
  ],
  constraints: [
    "duration <= 4h",
    "calendar_conflicts == none"
  ],
  evidenceRequired: ["plix://witness/calendar.open_slots"],  // Evidence tags
  evidenceProduce: ["plix://witness/reservation.record"],     // Evidence tags
  tagResolutions: new Map([  // Tag resolution cache
    ["plix://room/meeting_room", {
      type: "database_table",
      location: "postgresql://db/rooms",
      schema: "public.rooms"
    }]
  ])
};
```

This IR preserves the contract's intent, execution steps, dependencies, retry logic, compensation, **and tag-based entity references with resolution results**. Tags enable canonical identity (`plix://room/meeting_room`), while resolved entities enable efficient execution. Tag resolution cache enables reuse across nodes.

**IR Benefits**

IR design provides:

- **Semantic Preservation:** Maintains contract semantics through compilation
- **Execution Metadata:** Includes all metadata needed for execution
- **Target Flexibility:** Enables compilation to multiple targets
- **Optimization Support:** Enables optimization before compilation

These benefits enable intent-preserving compilation, ensuring that execution achieves the intended goals.

---

## Section 8.2: Lowering Process

Lowering transforms PLIx contracts into IR, resolving dependencies, interpolating parameters, and ordering tasks topologically.

**Lowering Overview**

Lowering process:

```
PLIx Contract
  ↓
Dependency Resolution
  ↓
Parameter Interpolation
  ↓
Topological Ordering
  ↓
IR Plan
```

This process transforms contracts into executable IR while preserving semantics.

**Tag Resolution Benefits**

Tag resolution provides:

- **Canonical Identity:** Tags provide unique, unambiguous entity references
- **Multi-Source Resolution:** Resolves tags via Registry → HHNI → SEG → CMC
- **Resolution Caching:** Caches resolved entities/capabilities for reuse
- **Target Independence:** Resolved entities enable target-specific compilation

These benefits enable efficient tag resolution during lowering, ensuring that entity references are resolved before dependency resolution.

**Dependency Resolution**

Dependency resolution builds dependency graph:

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

**Parameter Interpolation**

Parameter interpolation resolves parameter references:

```typescript
function interpolateParams(
  task: Task,
  results: Record<string, any>
): Record<string, any> {
  const interpolated: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(task.params || {})) {
    if (typeof value === 'string' && value.includes('${')) {
      // Resolve parameter reference: ${task.field}
      const interpolatedValue = value.replace(/\$\{([^}]+)\}/g, (match, ref) => {
        const [taskId, field] = ref.split('.');
        return results[taskId]?.[field] ?? match;
      });
      interpolated[key] = interpolatedValue;
    } else {
      interpolated[key] = value;
    }
  }
  
  return interpolated;
}
```

Parameter interpolation resolves `${task.field}` references to actual values from previous task results, enabling dynamic parameter passing.

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

**Lowering Implementation**

Complete lowering implementation:

```typescript
async function lowerToIR(contract: PLIxContract): Promise<IRPlan> {
  // Resolve tags first
  const tagResolutions = await resolveTags(contract);
  
  // Build IR nodes with resolved entities/capabilities
  const nodes: IRNode[] = contract.tasks.map(task => ({
    id: task.id,
    action: task.action,
    entityTag: task.entityTag,
    capabilityTag: task.capabilityTag,
    params: task.params || {},
    deps: task.depends_on || [],
    retry: task.retry ? {
      max: task.retry.max_attempts || 0,
      backoff: task.retry.backoff || "none",
      ms: task.retry.backoff_ms || 0
    } : undefined,
    compensate: task.compensate,
    resolvedEntity: task.entityTag ? tagResolutions.get(task.entityTag) : undefined,
    resolvedCapability: task.capabilityTag ? tagResolutions.get(task.capabilityTag) : undefined
  }));
  
  // Resolve dependencies
  const deps = resolveDependencies(contract);
  for (const node of nodes) {
    node.deps = deps.get(node.id) || [];
  }
  
  // Topological ordering
  const ordered = topologicalOrder(nodes);
  
  return {
    intent: contract.intent,
    nodes: ordered,
    constraints: contract.constraints || [],
    evidenceRequired: contract.evidence?.required || [],
    evidenceProduce: contract.evidence?.produce || [],
    tagResolutions  // Include tag resolution cache
  };
}
```

This implementation performs complete lowering: **resolving tags**, building IR nodes with resolved entities/capabilities, resolving dependencies, and ordering topologically. Tag resolution enables canonical identity resolution before dependency resolution.

**Lowering Benefits**

Lowering process provides:

- **Tag Resolution:** Resolves entity and capability tags to implementation-specific mechanisms
- **Dependency Resolution:** Identifies all dependencies (explicit and implicit)
- **Parameter Interpolation:** Resolves parameter references dynamically
- **Topological Ordering:** Ensures correct execution order
- **Circular Detection:** Detects circular dependencies

These benefits enable correct IR generation with tag-based entity resolution, ensuring that execution follows dependency order, resolves parameters correctly, **and uses resolved entities/capabilities from tag resolution**.

---

## Section 8.3: Target Compilation

Target compilation transforms IR into execution target formats (Temporal, Step Functions, Argo), **using resolved entities/capabilities from tag resolution** to enable execution on various platforms.

**Target Overview**

PLIx supports multiple execution targets:

- **Temporal:** Durable workflow execution with saga patterns
- **AWS Step Functions:** Serverless workflow orchestration
- **Argo Workflows:** Kubernetes-native workflow execution
- **APOE:** AIM-OS native orchestration engine

Each target provides different execution capabilities, enabling flexible deployment. **Tag resolution enables target-specific compilation** by resolving tags to target-specific mechanisms (REST API endpoints, database connections, service URLs).

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
        { args: params },
        {
          retry: {
            maximumAttempts: node.retry?.max || 1,
            backoffCoefficient: node.retry?.backoff === "exponential" ? 2 : 1,
            initialInterval: node.retry?.ms || 1000
          }
        }
      );
      
      results[node.id] = result;
      
      // Handle compensation on failure
      if (node.compensate) {
        try {
          // Continue execution
        } catch (error) {
          // Trigger compensation
          const compensateNode = ir.nodes.find(n => n.id === node.compensate);
          if (compensateNode) {
            yield wf.executeActivity(compensateNode.action, {
              args: interpolateParams(compensateNode, results)
            });
          }
          throw error;
        }
      }
    }
    
    return results;
  };
}
```

Temporal compilation generates workflows with durable execution, retry logic, and saga compensation, enabling reliable intent achievement.

**Step Functions Compilation**

Step Functions compilation generates Step Functions definitions:

```typescript
function compileToStepFunctions(ir: IRPlan): StepFunctionsDefinition {
  const states: Record<string, any> = {};
  
  for (const node of ir.nodes) {
    states[node.id] = {
      Type: "Task",
      Resource: `arn:aws:states:::lambda:invoke`,
      Parameters: {
        FunctionName: node.action,
        Payload: {
          ...node.params
        }
      },
      Retry: node.retry ? [{
        ErrorEquals: ["States.ALL"],
        MaxAttempts: node.retry.max,
        BackoffRate: node.retry.backoff === "exponential" ? 2 : 1,
        IntervalSeconds: node.retry.ms / 1000
      }] : undefined,
      Catch: node.compensate ? [{
        ErrorEquals: ["States.ALL"],
        Next: node.compensate,
        ResultPath: "$.error"
      }] : undefined,
      Next: getNextNode(node, ir.nodes)
    };
  }
  
  return {
    Comment: ir.intent,
    StartAt: ir.nodes[0].id,
    States: states
  };
}
```

Step Functions compilation generates serverless workflows with retry and error handling, enabling scalable intent achievement.

**Argo Compilation**

Argo compilation generates Argo Workflow definitions:

```yaml
# Generated Argo Workflow
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: book-meeting-room-
spec:
  entrypoint: book-meeting-room
  templates:
  - name: book-meeting-room
    steps:
    - - name: check-availability
        template: check-availability
    - - name: reserve-room
        template: reserve-room
        arguments:
          parameters:
          - name: room-id
            value: "{{steps.check-availability.outputs.result.room_id}}"
  
  - name: check-availability
    container:
      image: api-executor:latest
      command: [api.check_room_availability]
      args: ["--date", "2025-12-01", "--duration", "2h"]
  
  - name: reserve-room
    container:
      image: api-executor:latest
      command: [api.reserve_room]
      args: ["--room-id", "{{inputs.parameters.room-id}}"]
```

Argo compilation generates Kubernetes-native workflows, enabling containerized intent achievement.

**Target Compilation Benefits**

Target compilation provides:

- **Target Flexibility:** Enables compilation to multiple execution targets
- **Platform Optimization:** Optimizes for each target's capabilities
- **Deployment Flexibility:** Enables deployment on various platforms
- **Intent Preservation:** Maintains intent semantics across targets

These benefits enable flexible deployment while preserving intent fidelity.

---

## Section 8.4: APOE Integration

APOE integration compiles PLIx IR into APOE ExecutionPlans, enabling intent-aware orchestration within AIM-OS.

**APOE Overview**

APOE (Atomic Provenance Orchestration Engine) provides:

- **Plan Execution:** Executes ExecutionPlans with role-based orchestration
- **Budget Management:** Manages execution budgets and gates
- **Provenance Tracking:** Tracks execution provenance
- **Multi-Agent Coordination:** Coordinates multiple agents

APOE integration enables PLIx contracts to execute within AIM-OS, leveraging existing orchestration capabilities.

**IR → APOE Compilation**

IR to APOE compilation **uses resolved entities/capabilities from tag resolution**:

```typescript
function compileToAPOE(ir: IRPlan): ExecutionPlan {
  const steps: ExecutionStep[] = ir.nodes.map(node => {
    // Use resolved entity/capability from tag resolution
    const entity = node.resolvedEntity || {};
    const capability = node.resolvedCapability || {};
    
    return {
      id: node.id,
      role: extractRole(node.action, capability),  // Extract role from action/capability
      description: `${node.action}: ${ir.intent}`,  // Human-readable description
      inputs: {
        ...node.params,
        entity: entity,  // Include resolved entity
        capability: capability  // Include resolved capability
      },
      outputs: {},
      dependencies: node.deps.map(depId => ({
        step_id: depId,
        output_field: "result"
      }))
    };
  });
  
  const roles: Record<string, RoleDefinition> = {};
  for (const step of steps) {
    if (!roles[step.role]) {
      roles[step.role] = {
        description: `Execute ${step.role} actions`,
        capabilities: [step.role]
      };
    }
  }
  
  return {
    steps,
    roles,
    budget: {
      max_cost: 1000,
      max_time: 300000  // 5 minutes
    },
    gates: [
      {
        type: "confidence",
        threshold: 0.70,
        check: async (step) => {
          const confidence = await vif.get_confidence(step.role, step.inputs);
          return confidence >= 0.70;
        }
      }
    ]
  };
}

function extractRole(action: string, capability?: any): string {
  // Use capability tag resolution if available
  if (capability?.role) {
    return capability.role;
  }
  // Extract role from action: "api.reserve_room" → "api"
  return action.split('.')[0];
}
```

This compilation transforms IR into APOE ExecutionPlans, **using resolved entities/capabilities from tag resolution** to map IR nodes to APOE steps, dependencies to APOE dependencies, and adding APOE-specific metadata (budgets, gates). Tag resolution enables target-specific compilation by resolving tags to APOE-specific mechanisms.

**Role Mapping**

Role mapping assigns IR actions to APOE roles:

```typescript
const roleMapping: Record<string, string> = {
  "api": "api_executor",
  "db": "database_executor",
  "ai": "ai_agent",
  "router": "router_agent"
};

function mapRole(action: string): string {
  const [namespace] = action.split('.');
  return roleMapping[namespace] || "default_executor";
}
```

Role mapping enables APOE to route tasks to appropriate executors, leveraging APOE's role-based orchestration.

**Budget and Gate Mapping**

Budget and gate mapping:

```typescript
function mapBudgetsAndGates(ir: IRPlan): {
  budget: Budget;
  gates: Gate[];
} {
  return {
    budget: {
      max_cost: calculateCost(ir.nodes),
      max_time: calculateTime(ir.nodes),
      max_tokens: calculateTokens(ir.nodes)
    },
    gates: [
      {
        type: "confidence",
        threshold: PLIX_DEFAULTS.confidence.global_minimum,
        check: async (step) => {
          const confidence = await vif.get_confidence(step.role, step.inputs);
          return confidence >= PLIX_DEFAULTS.confidence.global_minimum;
        }
      },
      {
        type: "policy",
        check: async (step) => {
          const policy = compileConstraintsToPolicy(ir.constraints);
          return await evaluatePolicy(policy, step.inputs);
        }
      }
    ]
  };
}
```

Budget and gate mapping enables APOE to enforce PLIx constraints (confidence thresholds, policy rules) during execution.

**APOE Execution**

APOE execution with PLIx contracts:

```typescript
async function executePLIxContract(contract: PLIxContract) {
  // Compile to IR (includes tag resolution)
  const ir = await lowerToIR(contract);
  
  // Compile to APOE (uses resolved entities/capabilities)
  const apoePlan = compileToAPOE(ir);
  
  // Execute via APOE
  const executor = new PlanExecutor();
  const result = await executor.execute(apoePlan);
  
  // Verify intent achievement (uses tag-based entity references)
  const verification = await verifyIntent(contract, result);
  
  return {
    result,
    verification
  };
}
```

APOE execution enables PLIx contracts to execute within AIM-OS, leveraging APOE's orchestration capabilities while maintaining intent fidelity. **Tag resolution enables target-specific compilation** by resolving tags to APOE-specific mechanisms, while resolved entities/capabilities enable efficient execution.

**APOE Integration Benefits**

APOE integration provides:

- **Native Integration:** Leverages existing AIM-OS orchestration
- **Intent Awareness:** Enables intent-aware execution
- **Provenance Tracking:** Tracks execution provenance
- **Multi-Agent Coordination:** Coordinates multiple agents

These benefits enable seamless PLIx execution within AIM-OS, leveraging existing infrastructure while adding intent-awareness.

---

## Chapter 8 Summary

Compiler architecture transforms PLIx contracts into executable plans through IR design, lowering process, target compilation, and APOE integration. IR preserves contract semantics and execution metadata, **including tag-based entity references and resolution results**. Lowering resolves tags, resolves dependencies, and orders tasks topologically. Target compilation generates execution code for various platforms, **using resolved entities/capabilities from tag resolution**. APOE integration enables native AIM-OS execution, **leveraging tag resolution for target-specific compilation**.

**Tags enable canonical identity** throughout the compilation process: IR preserves tag-based entity references, lowering resolves tags to implementation-specific mechanisms, and target compilation uses resolved entities/capabilities for efficient execution. Tag resolution enables intent-preserving compilation with canonical identity, ensuring that execution achieves intended goals while maintaining flexibility across execution targets.

**Next:** Part II Architecture complete. Part III explores AIM-OS integration—CMC, VIF, APOE, and SEG transformations, showing how tags enable integration.

---

**Word Count:** ~2,800 words (enhanced from ~2,300)  
**Status:** ✅ **COMPLETE** (v2.0 Enhanced)  
**Cross-References:**
- Chapter 5: Tag System (tag format and components)
- Chapter 15: Tag Registry (tag resolution process)
- Chapter 20: PLIX-to-AIP Compiler (complete compiler implementation)

