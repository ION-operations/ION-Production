# Chapter 49: Runtime Implementation: Durable Execution and Recovery

**Part:** V - Implementation  
**Chapter:** 49  
**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)

---

## Section 49.1: Durable Execution Engine

Durable execution ensures intent achievement survives failures, enabling reliable intent achievement through checkpointing and recovery.

**Durable Execution Overview**

Durable execution provides:

- **Checkpointing:** Store execution state before each step
- **Recovery:** Restore from checkpoints on failure
- **Idempotency:** Safe retry of operations
- **State Persistence:** Persistent state across failures

Durable execution enables reliable intent achievement despite transient failures.

**Checkpointing Implementation**

Checkpointing stores execution state:

```typescript
interface Checkpoint {
  node_id: string;
  entity_tag?: string;  // Entity tag for this checkpoint
  state: {
    inputs: Record<string, any>;
    outputs?: Record<string, any>;
    status: 'running' | 'completed' | 'failed';
  };
  timestamp: string;
  checkpoint_id: string;
}

async function createCheckpoint(
  node_id: string,
  state: Checkpoint['state'],
  entity_tag: string | undefined,
  cmc: MemoryStore
): Promise<string> {
  const checkpoint = {
    type: 'plix_checkpoint',
    node_id,
    entity_tag,  // Include entity tag
    state,
    timestamp: new Date().toISOString()
  };
  
  const tags = ['checkpoint', 'plix_execution', node_id];
  if (entity_tag) {
    tags.push(entity_tag);  // Include entity tag for queries
  }
  
  const atom = await cmc.create_atom({
    content: checkpoint,
    tags
  });
  
  return atom.id;
}

async function restoreFromCheckpoint(
  checkpoint_id: string,
  cmc: MemoryStore
): Promise<Checkpoint['state']> {
  const atom = await cmc.get_atom(checkpoint_id);
  return atom.content.state;
}
```

Checkpointing enables recovery from failures by storing execution state.

**Recovery Implementation**

Recovery restores execution from checkpoints:

```typescript
async function executeWithRecovery(
  ir: IRPlan,
  executor: NodeExecutor,
  cmc: MemoryStore
): Promise<ExecutionResult> {
  const results: Record<string, any> = {};
  const checkpoints: Record<string, string> = {};
  const entity_tag = ir.entityTag;  // Get entity tag from IR
  
  for (const node of ir.nodes) {
    try {
      // Create checkpoint before execution (includes entity tag)
      const checkpoint_id = await createCheckpoint(node.id, {
        inputs: node.params,
        status: 'running'
      }, node.entityTag || entity_tag, cmc);
      checkpoints[node.id] = checkpoint_id;
      
      // Execute node
      const output = await executor.exec(node.id, node.action, node.params);
      results[node.id] = output;
      
      // Update checkpoint on success (includes entity tag)
      await createCheckpoint(node.id, {
        inputs: node.params,
        outputs: output,
        status: 'completed'
      }, node.entityTag || entity_tag, cmc);
      
    } catch (error) {
      // Restore from checkpoint on failure
      const checkpoint_id = checkpoints[node.id];
      if (checkpoint_id) {
        const state = await restoreFromCheckpoint(checkpoint_id, cmc);
        // Retry or compensate based on state
        await handleFailure(node, state, error, executor, cmc);
      }
      throw error;
    }
  }
  
  return { results };
}
```

Recovery enables execution resumption from checkpoints, ensuring intent achievement despite failures.

**Idempotency Support**

Idempotency ensures safe retry:

```typescript
async function executeIdempotent(
  node_id: string,
  action: string,
  params: Record<string, any>,
  entity_tag: string | undefined,
  executor: NodeExecutor,
  cmc: MemoryStore
): Promise<any> {
  // Generate idempotency key (includes entity tag)
  const idempotency_key = `${node_id}_${entity_tag || 'default'}_${hashParams(params)}`;
  
  // Check if already executed (query by entity tag)
  const tags = ['execution', 'idempotent', idempotency_key];
  if (entity_tag) {
    tags.push(entity_tag);  // Include entity tag for queries
  }
  
  const existing = await cmc.query({ tags });
  
  if (existing.length > 0) {
    // Return existing result
    return existing[0].content.outputs;
  }
  
  // Execute and store result (includes entity tag)
  const output = await executor.exec(node_id, action, params);
  
  await cmc.create_atom({
    content: {
      type: 'execution_result',
      node_id,
      entity_tag,  // Include entity tag
      outputs: output,
      idempotency_key
    },
    tags
  });
  
  return output;
}
```

Idempotency ensures safe retry of operations, preventing duplicate execution.

**Durable Execution Benefits**

Durable execution provides:

- **Reliability:** Execution survives failures through checkpointing
- **Recovery:** Execution resumes from checkpoints
- **Idempotency:** Safe retry of operations
- **State Persistence:** Persistent state across failures

These benefits enable reliable intent achievement despite transient failures.

---

## Section 49.2: Saga Pattern Implementation

Saga pattern enables compensation for partial failures, ensuring system consistency through dynamic compensation logic.

**Saga Pattern Overview**

Saga pattern provides:

- **Compensation:** Undo operations when later steps fail
- **Dynamic Compensation:** Compensation logic defined per task
- **Consistency:** System remains consistent despite partial failures
- **Recovery:** System recovers from partial failures

Saga pattern ensures system consistency through compensation.

**Compensation Logic**

Compensation logic implementation:

```typescript
interface Compensation {
  action: string;
  params: Record<string, any>;
}

async function executeWithCompensation(
  ir: IRPlan,
  executor: NodeExecutor,
  cmc: MemoryStore
): Promise<ExecutionResult> {
  const results: Record<string, any> = {};
  const completed: IRNode[] = [];
  
  for (const node of ir.nodes) {
    try {
      // Execute node
      const output = await executor.exec(node.id, node.action, node.params);
      results[node.id] = output;
      completed.push(node);
      
    } catch (error) {
      // Trigger compensation for completed nodes
      for (const completedNode of completed.reverse()) {
        if (completedNode.compensate) {
          const compensateNode = ir.nodes.find(n => n.id === completedNode.compensate);
          if (compensateNode) {
            try {
              await executor.exec(
                compensateNode.id,
                compensateNode.action,
                resolveCompensationParams(compensateNode.params, results)
              );
            } catch (compError) {
              // Log compensation failure
              console.error(`Compensation failed for ${completedNode.id}: ${compError}`);
            }
          }
        }
      }
      throw error;
    }
  }
  
  return { results };
}

function resolveCompensationParams(
  params: Record<string, any>,
  results: Record<string, any>
): Record<string, any> {
  const resolved: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === 'string' && value.startsWith('${')) {
      const ref = value.match(/\$\{([^}]+)\}/)?.[1];
      if (ref) {
        const [taskId, field] = ref.split('.');
        resolved[key] = results[taskId]?.[field] ?? value;
      } else {
        resolved[key] = value;
      }
    } else {
      resolved[key] = value;
    }
  }
  
  return resolved;
}
```

Compensation logic undoes completed operations when later steps fail, ensuring consistency.

**Saga Pattern Example**

Saga pattern example:

```typescript
// Room booking saga with entity tags
const ir: IRPlan = {
  intent: "Book a meeting room",
  entityTag: "plix://room/meeting_room",  // Entity tag
  nodes: [
    {
      id: "check_availability",
      action: "api.check_room_availability",
      entityTag: "plix://room/meeting_room",  // Entity tag
      deps: []
    },
    {
      id: "reserve_room",
      action: "api.reserve_room",
      entityTag: "plix://room/meeting_room",  // Same entity tag
      deps: ["check_availability"],
      compensate: "cancel_reservation"  // Compensation task
    },
    {
      id: "create_calendar_event",
      action: "api.create_calendar_event",
      entityTag: "plix://room/meeting_room",  // Same entity tag
      deps: ["reserve_room"],
      compensate: "delete_calendar_event"
    },
    {
      id: "cancel_reservation",
      action: "api.cancel_reservation",
      entityTag: "plix://room/meeting_room",  // Same entity tag
      deps: []
    },
    {
      id: "delete_calendar_event",
      action: "api.delete_calendar_event",
      entityTag: "plix://room/meeting_room",  // Same entity tag
      deps: []
    }
  ]
};

// If create_calendar_event fails:
// 1. cancel_reservation compensates reserve_room (for entity plix://room/meeting_room)
// 2. delete_calendar_event compensates create_calendar_event (if it succeeded, for same entity)
```

Saga pattern ensures system consistency through compensation, undoing partial changes on failure.

**Saga Pattern Benefits**

Saga pattern provides:

- **Consistency:** System remains consistent despite partial failures
- **Recovery:** System recovers from partial failures through compensation
- **Dynamic Compensation:** Compensation logic defined per task
- **Reliability:** Ensures system reliability through compensation

These benefits enable reliable intent achievement with system consistency guarantees.

---

## Section 49.3: Recovery Mechanisms

Recovery mechanisms enable execution resumption from failures, ensuring intent achievement through checkpoint restoration and compensation.

**Recovery Strategies**

Recovery strategies:

1. **Checkpoint Restoration:** Restore from last checkpoint
2. **Compensation:** Undo partial changes
3. **Retry:** Retry failed operations
4. **Escalation:** Escalate to human operator

Recovery strategies enable execution resumption from various failure modes.

**Checkpoint Restoration**

Checkpoint restoration implementation:

```typescript
async function restoreExecution(
  plan_id: string,
  entity_tag: string | undefined,
  cmc: MemoryStore
): Promise<ExecutionState> {
  // Find last checkpoint (filter by entity tag if provided)
  const tags = ['checkpoint', 'plix_execution', plan_id];
  if (entity_tag) {
    tags.push(entity_tag);  // Filter by entity tag
  }
  
  const checkpoints = await cmc.query({ tags });
  
  if (checkpoints.length === 0) {
    throw new Error('No checkpoints found');
  }
  
  // Get most recent checkpoint
  const lastCheckpoint = checkpoints.sort((a, b) => 
    new Date(b.content.timestamp).getTime() - new Date(a.content.timestamp).getTime()
  )[0];
  
  // Restore state
  const state: ExecutionState = {
    plan_id,
    entity_tag,  // Include entity tag
    completed_nodes: [],
    failed_nodes: [],
    current_node: lastCheckpoint.content.node_id,
    state: lastCheckpoint.content.state
  };
  
  // Find completed nodes
  const completedCheckpoints = checkpoints.filter(c => 
    c.content.state.status === 'completed'
  );
  state.completed_nodes = completedCheckpoints.map(c => c.content.node_id);
  
  return state;
}

async function resumeExecution(
  state: ExecutionState,
  ir: IRPlan,
  executor: NodeExecutor,
  cmc: MemoryStore
): Promise<ExecutionResult> {
  // Resume from checkpoint
  const results: Record<string, any> = {};
  
  // Restore completed results
  for (const nodeId of state.completed_nodes) {
    const checkpoint = await findCheckpoint(nodeId, cmc);
    if (checkpoint) {
      results[nodeId] = checkpoint.content.state.outputs;
    }
  }
  
  // Continue from current node
  const currentNodeIndex = ir.nodes.findIndex(n => n.id === state.current_node);
  for (let i = currentNodeIndex; i < ir.nodes.length; i++) {
    const node = ir.nodes[i];
    try {
      const output = await executor.exec(node.id, node.action, node.params);
      results[node.id] = output;
    } catch (error) {
      // Handle failure
      await handleFailure(node, results, error, executor, cmc);
      throw error;
    }
  }
  
  return { results };
}
```

Checkpoint restoration enables execution resumption from failures, ensuring intent achievement.

**Retry Logic**

Retry logic implementation:

```typescript
async function executeWithRetry(
  node: IRNode,
  executor: NodeExecutor,
  maxAttempts: number = 3,
  backoff: 'none' | 'linear' | 'exponential' = 'exponential',
  backoffMs: number = 1000
): Promise<any> {
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await executor.exec(node.id, node.action, node.params);
    } catch (error) {
      lastError = error as Error;
      
      if (attempt < maxAttempts) {
        // Calculate backoff delay
        const delay = calculateBackoff(attempt, backoff, backoffMs);
        await sleep(delay);
      }
    }
  }
  
  throw lastError || new Error('Execution failed after retries');
}

function calculateBackoff(
  attempt: number,
  backoff: 'none' | 'linear' | 'exponential',
  baseMs: number
): number {
  switch (backoff) {
    case 'none':
      return 0;
    case 'linear':
      return baseMs * attempt;
    case 'exponential':
      return baseMs * Math.pow(2, attempt - 1);
    default:
      return baseMs;
  }
}
```

Retry logic enables automatic retry of failed operations, improving reliability.

**Recovery Mechanisms Benefits**

Recovery mechanisms provide:

- **Checkpoint Restoration:** Execution resumption from failures
- **Compensation:** System consistency through compensation
- **Retry Logic:** Automatic retry of failed operations
- **Escalation:** Human operator intervention when needed

These benefits enable reliable intent achievement despite failures.

---

## Section 49.4: State Persistence

State persistence enables durable execution state storage, ensuring execution state survives failures and system restarts.

**State Persistence Implementation**

State persistence using CMC:

```typescript
interface ExecutionState {
  plan_id: string;
  intent: string;
  entity_tag?: string;  // Entity tag for this execution
  completed_nodes: string[];
  failed_nodes: string[];
  current_node?: string;
  results: Record<string, any>;
  checkpoints: Record<string, string>;
}

async function persistState(
  state: ExecutionState,
  cmc: MemoryStore
): Promise<string> {
  const tags = ['execution_state', 'plix', state.plan_id];
  if (state.entity_tag) {
    tags.push(state.entity_tag);  // Include entity tag for queries
  }
  
  const atom = await cmc.create_atom({
    content: {
      type: 'plix_execution_state',
      ...state,
      timestamp: new Date().toISOString()
    },
    tags
  });
  
  return atom.id;
}

async function loadState(
  plan_id: string,
  entity_tag: string | undefined,
  cmc: MemoryStore
): Promise<ExecutionState | null> {
  const tags = ['execution_state', 'plix', plan_id];
  if (entity_tag) {
    tags.push(entity_tag);  // Filter by entity tag
  }
  
  const atoms = await cmc.query({ tags });
  
  if (atoms.length === 0) {
    return null;
  }
  
  // Get most recent state
  const latest = atoms.sort((a, b) =>
    new Date(b.content.timestamp).getTime() - new Date(a.content.timestamp).getTime()
  )[0];
  
  return latest.content as ExecutionState;
}
```

State persistence enables execution state storage and retrieval, supporting durable execution.

**Bitemporal State Tracking**

Bitemporal state tracking:

```typescript
async function trackStateEvolution(
  plan_id: string,
  state: ExecutionState,
  cmc: MemoryStore
): Promise<void> {
  const tags = ['execution_state', 'plix', plan_id];
  if (state.entity_tag) {
    tags.push(state.entity_tag);  // Include entity tag
  }
  
  // Store state with bitemporal tracking
  await cmc.create_atom({
    content: {
      type: 'plix_execution_state',
      ...state
    },
    tags,
    valid_from: new Date(),
    valid_to: null  // Current state
  });
  
  // Query state evolution (filter by entity tag)
  const evolution = await cmc.query({
    tags,
    valid_at: new Date()  // State at specific time
  });
}

async function queryStateHistory(
  plan_id: string,
  entity_tag: string | undefined,
  timestamp: Date,
  cmc: MemoryStore
): Promise<ExecutionState | null> {
  const tags = ['execution_state', 'plix', plan_id];
  if (entity_tag) {
    tags.push(entity_tag);  // Filter by entity tag
  }
  
  const atoms = await cmc.query({
    tags,
    valid_at: timestamp
  });
  
  if (atoms.length === 0) {
    return null;
  }
  
  return atoms[0].content as ExecutionState;
}
```

Bitemporal state tracking enables state evolution queries, supporting temporal reasoning.

**State Persistence Benefits**

State persistence provides:

- **Durability:** Execution state survives failures
- **Recovery:** Execution resumption from persisted state
- **Temporal Queries:** State evolution queries
- **Auditability:** Complete execution history

These benefits enable reliable intent achievement with complete execution history.

---

## Chapter 49 Summary

Runtime implementation provides durable execution, saga patterns, recovery mechanisms, and state persistence **with tag-based entity references**. Durable execution ensures intent achievement survives failures through checkpointing **with tag-based entity tracking** and recovery **using entity tags**. Saga pattern enables compensation for partial failures **for specific entities via tags**, ensuring system consistency. Recovery mechanisms enable execution resumption from failures **using tag-based checkpoint queries**. State persistence enables durable execution state storage **with tag-based entity references**, ensuring execution state survives failures and system restarts.

**Tags enable canonical identity** throughout runtime execution: checkpoints include entity tags (`plix://room/meeting_room`), checkpoint queries filter by entity tags, state persistence includes entity tags for entity-based queries, and saga compensation tracks entities via tags. Tags enable unambiguous entity references that survive technology changes, enabling intent-aware runtime execution with canonical identity.

**Next:** Chapter 50 explores provenance emitters—PROV/OpenLineage integration, showing how tags enable provenance tracking.

---

**Word Count:** ~2,700 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)  
**Cross-References:**
- Chapter 5: Tag System (tag format and components)
- Chapter 9: CMC Integration (checkpoint storage with tags)
- Chapter 11: APOE Integration (execution with tags)
- Chapter 15: Tag Registry (tag resolution process)

