# Chapter 5: The Four Pillars: Contract, Execution, Safety, Evidence

**Part:** II - Architecture  
**Chapter:** 5  
**Target Word Count:** 2,500-3,000 words (enhanced from 2,000-2,500)  
**Status:** ✅ **COMPLETE** (v2.0 Enhanced)

---

## Section 5.1: The Architectural Foundation

PLIx architecture rests on four pillars: Contract Layer, Execution Layer, Safety Layer, and Evidence Layer. Each pillar addresses a fundamental concern in intent-driven systems, enabling pure intent expression, reliable execution, safety guarantees, and verifiable outcomes.

**The Four Pillars Overview**

The four pillars form a complete architecture for intent-driven systems:

1. **Contract Layer:** Expresses intent purely, without mechanism contamination
2. **Execution Layer:** Achieves intent reliably, with recoverable execution
3. **Safety Layer:** Ensures safety through confidence gates and policy enforcement
4. **Evidence Layer:** Provides verifiable provenance and evidence chains

Together, these pillars enable systems that understand their own purpose, execute reliably, maintain safety, and provide verifiable outcomes.

**Why Four Pillars?**

Each pillar addresses a critical gap in current systems:

- **Contract Layer:** Current systems mix intent with execution. The Contract Layer separates intent expression from implementation.
- **Execution Layer:** Current systems lack recoverable execution. The Execution Layer provides durable execution with saga patterns.
- **Safety Layer:** Current systems lack confidence-aware routing. The Safety Layer provides LLM confidence gates and policy enforcement.
- **Evidence Layer:** Current systems lack verifiable provenance. The Evidence Layer provides evidence chains and lineage tracking.

The four pillars work together: contracts express intent, execution achieves intent, safety ensures reliability, evidence provides verification.

**Architectural Coherence**

The four pillars form a coherent architecture:

```
Intent Expression (Contract Layer)
    ↓
Intent Achievement (Execution Layer)
    ↓
Safety Guarantees (Safety Layer)
    ↓
Verifiable Outcomes (Evidence Layer)
```

Each layer builds on the previous: contracts enable execution, execution requires safety, safety enables evidence, evidence verifies contracts. This coherence ensures that intent-driven systems are complete, reliable, and verifiable.

**Integration with AIM-OS**

The four pillars integrate seamlessly with AIM-OS systems:

- **Contract Layer:** Uses CMC for contract storage, HHNI for contract indexing
- **Execution Layer:** Uses APOE for plan execution, Router for tool selection
- **Safety Layer:** Uses VIF for confidence tracking, SCOR for policy enforcement
- **Evidence Layer:** Uses SEG for evidence chains, TCS for timeline tracking

This integration enables PLIx to leverage existing AIM-OS capabilities while adding intent-awareness to each system.

---

## Section 5.2: Pillar 1: Contract Layer

The Contract Layer expresses intent purely, without mechanism contamination. It provides Design by Contract (DbC), Controlled Natural Language (CNL), and formal modeling capabilities, enabling pure intent expression.

**Design by Contract (DbC)**

Design by Contract enables intent expression through preconditions and postconditions:

```yaml
contract:
  entity: "plix://room/meeting_room"  # Canonical entity identity
  pre:
    - "room_available == true"
    - "user_authenticated == true"
  post:
    - "room_reserved == true"
    - "calendar_event_created == true"
```

Preconditions express what must be true before intent achievement. Postconditions express what must be true after intent achievement. This contract-based expression enables pure intent: we express what we want (postconditions) and what we need (preconditions) without specifying how to achieve it.

**Controlled Natural Language (CNL)**

Controlled Natural Language enables human-readable intent expression:

```
Intent: Book a meeting room on 2025-12-01 for 2h.
Entity: plix://room/meeting_room  # Canonical entity identity

Task check_availability:
  Entity: plix://room/meeting_room  # Entity tag
  Action: api.check_room_availability
  Params: date=2025-12-01, duration=2h

Task reserve_room:
  Entity: plix://room/meeting_room  # Entity tag
  Action: api.reserve_room
  Params: room_id=${check_availability.room_id}
  Depends: check_availability
```

CNL provides a structured, unambiguous way to express intent in natural language. It bridges human intent expression with formal contract specification, enabling both human readability and machine verifiability.

**Formal Modeling**

Formal modeling enables mathematical verification of contracts:

- **Alloy:** Models contract relationships and constraints
- **TLA+:** Models contract temporal properties and safety
- **Coq/Lean:** Proves contract correctness and completeness

Formal modeling provides mathematical guarantees: contracts are consistent, complete, and correct. This enables verification at the intent level, independent of execution.

**Contract Layer Benefits**

The Contract Layer provides:

- **Pure Intent Expression:** Intent expressed without mechanism contamination
- **Human Readability:** CNL enables natural language intent expression
- **Mathematical Verification:** Formal modeling enables contract verification
- **Timelessness:** Contracts survive technology changes

This enables intent-driven systems that express what they want clearly, verifiably, and timelessly.

---

## Section 5.3: Pillar 2: Execution Layer

The Execution Layer achieves intent reliably, with recoverable execution. It provides durable execution, saga patterns, and formal modeling of recovery, enabling reliable intent achievement.

**Durable Execution**

Durable execution ensures intent achievement survives failures:

```typescript
async function executePlan(plan: IRPlan) {
  const checkpoints: Record<string, string> = {};
  const entity_tag = plan.entityTag;  // Get entity tag from plan
  
  for (const node of plan.nodes) {
    // Store checkpoint before execution (with entity tag)
    const checkpoint = await cmc.create_atom({
      content: { 
        type: 'checkpoint', 
        node_id: node.id, 
        entity_tag: node.entityTag || entity_tag,  // Include entity tag
        state: 'running' 
      },
      tags: [node.entityTag || entity_tag]  // Add entity tag to tags
    });
    checkpoints[node.id] = checkpoint.id;
    
    try {
      // Execute node (for specific entity)
      const result = await executeNode(node, node.entityTag || entity_tag);
      
      // Update checkpoint on success (with entity tag)
      await cmc.create_atom({
        content: { 
          type: 'checkpoint', 
          node_id: node.id, 
          entity_tag: node.entityTag || entity_tag,  // Include entity tag
          state: 'completed', 
          result 
        },
        tags: [node.entityTag || entity_tag]  // Add entity tag to tags
      });
    } catch (error) {
      // Restore from checkpoint on failure (with entity tag)
      await restoreFromCheckpoint(checkpoints[node.id], node.entityTag || entity_tag);
      throw error;
    }
  }
}
```

Durable execution stores checkpoints before each step, enabling recovery from failures. If execution fails, we can restore from the last checkpoint and retry, ensuring intent achievement despite transient failures.

**Saga Pattern**

Saga pattern enables compensation for partial failures:

```yaml
Entity: plix://room/meeting_room  # Canonical entity identity

Task reserve_room:
  Entity: plix://room/meeting_room  # Entity tag
  Action: api.reserve_room
  Compensate: cancel_reservation

Task cancel_reservation:
  Entity: plix://room/meeting_room  # Entity tag
  Action: api.cancel_reservation
  Params: reservation_id=${reserve_room.res_id}
```

If `reserve_room` succeeds but a later step fails, the saga pattern triggers `cancel_reservation` to compensate. This ensures system consistency: if intent achievement fails, we undo partial changes.

**Formal Modeling of Recovery**

Formal modeling enables mathematical verification of recovery:

- **TLA+:** Models recovery correctness and safety properties
- **Alloy:** Models recovery consistency and completeness
- **Coq/Lean:** Proves recovery termination and correctness

Formal modeling provides mathematical guarantees: recovery is correct, safe, and complete. This enables verification at the execution level, independent of implementation.

**Execution Layer Benefits**

The Execution Layer provides:

- **Reliable Achievement:** Durable execution ensures intent achievement despite failures
- **Consistency:** Saga pattern ensures system consistency through compensation
- **Mathematical Verification:** Formal modeling enables recovery verification
- **Resilience:** Recovery mechanisms enable resilient intent achievement

This enables intent-driven systems that achieve what they want reliably, consistently, and resiliently.

---

## Section 5.4: Pillar 3: Safety Layer

The Safety Layer ensures safety through confidence gates and policy enforcement. It provides LLM confidence tracking, adaptive routing, and policy-as-code, enabling safe intent achievement.

**LLM Confidence Gates**

LLM confidence gates ensure intent achievement only when confidence is sufficient:

```typescript
async function executeWithConfidence(node: IRNode, entity_tag: string) {
  const confidence = await vif.get_confidence(node.action, node.params, entity_tag);
  
  if (confidence < PLIX_DEFAULTS.confidence.global_minimum) {
    throw new Error(`Low confidence for entity ${entity_tag}: ${confidence} < ${PLIX_DEFAULTS.confidence.global_minimum}`);
  }
  
  return await executeNode(node, entity_tag);
}
```

Confidence gates prevent execution when confidence is too low, reducing risk of incorrect intent achievement. This enables safe intent achievement: we only execute when we're confident we can achieve the intent correctly.

**Adaptive Routing (Economic Gate)**

Adaptive routing optimizes tool selection based on cost, latency, and success rate:

```typescript
async function routeAdaptively(node: IRNode, entity_tag: string) {
  const proposals = await router.decide({
    goal: node.intent,
    task: node.action,
    entity_tag: entity_tag,  # Include entity tag
    context: { node_id: node.id, entity_tag: entity_tag }
  });
  
  // Router uses BanditScorer (BaRP equivalent) to rank tools
  // Considers: cost, latency, success rate, context fit, entity-specific patterns
  return proposals[0]; // Best tool based on economic optimization (for specific entity)
}
```

Adaptive routing selects the best tool for each intent achievement, optimizing for cost, latency, and success rate. This enables efficient intent achievement: we use the best tool for each situation.

**Policy-as-Code**

Policy-as-code enforces constraints through OPA/Rego or AWS Cedar:

```rego
package plix.booking

default allow = false

allow {
    input.entity_tag = "plix://room/meeting_room"  # Entity tag check
    input.duration <= 4
    input.calendar_conflicts == "none"
}
```

Policy-as-code compiles PLIx constraints into policy rules, enforcing constraints before execution. This enables safe intent achievement: we enforce constraints to prevent invalid intent achievement.

**Safety Layer Benefits**

The Safety Layer provides:

- **Confidence-Aware Execution:** Confidence gates prevent low-confidence execution
- **Economic Optimization:** Adaptive routing optimizes tool selection
- **Constraint Enforcement:** Policy-as-code enforces constraints
- **Risk Reduction:** Safety mechanisms reduce risk of incorrect intent achievement

This enables intent-driven systems that achieve what they want safely, efficiently, and correctly.

---

## Section 5.5: Pillar 4: Evidence Layer

The Evidence Layer provides verifiable provenance and evidence chains. It provides W3C PROV, OpenLineage, and intent lineage tracking, enabling verifiable intent achievement.

**W3C PROV**

W3C PROV provides standard provenance tracking:

```json
{
  "prefix": { "prov": "http://www.w3.org/ns/prov#" },
  "entity": {
    "ent:room_booking": { 
      "prov:value": { 
        "room_id": "A101", 
        "date": "2025-12-01",
        "entity_tag": "plix://room/meeting_room"  # Canonical entity identity
      } 
    }
  },
  "activity": {
    "act:reserve_room": { 
      "prov:type": "api.reserve_room",
      "prov:used": { "entity_tag": "plix://room/meeting_room" }  # Entity tag
    }
  },
  "wasGeneratedBy": {
    "ent:room_booking": { "prov:activity": "act:reserve_room" }
  }
}
```

W3C PROV tracks what entities were generated by which activities, providing standard provenance. This enables verifiable intent achievement: we can trace outcomes back to their sources.

**OpenLineage**

OpenLineage provides execution lineage tracking:

```json
{
  "eventType": "START",
  "run": { "runId": "run-123" },
  "job": { 
    "namespace": "aimos/plix", 
    "name": "book_meeting_room",
    "entity_tag": "plix://room/meeting_room"  # Canonical entity identity
  },
  "eventTime": "2025-12-01T10:00:00Z"
}
```

OpenLineage tracks execution events (START, COMPLETE, FAIL), providing execution lineage. This enables verifiable intent achievement: we can trace execution through its lifecycle.

**Intent Lineage**

Intent lineage tracks intent evolution and achievement:

```typescript
const lineage = {
  intent: "Book a meeting room",
  entity_tag: "plix://room/meeting_room",  # Canonical entity identity
  evolution: [
    { 
      timestamp: "2025-12-01T09:00:00Z", 
      intent: "Book a room",
      entity_tag: "plix://room/meeting_room"  # Entity tag
    },
    { 
      timestamp: "2025-12-01T09:05:00Z", 
      intent: "Book a meeting room with catering",
      entity_tag: "plix://room/meeting_room"  # Entity tag
    }
  ],
  achievement: [
    { 
      timestamp: "2025-12-01T10:00:00Z", 
      outcome: "room_reserved == true",
      entity_tag: "plix://room/meeting_room"  # Entity tag
    },
    { 
      timestamp: "2025-12-01T10:01:00Z", 
      outcome: "calendar_event_created == true",
      entity_tag: "plix://room/meeting_room"  # Entity tag
    }
  ]
};
```

Intent lineage tracks how intent evolves and how it's achieved, providing intent provenance. This enables verifiable intent achievement: we can trace intent from expression to achievement.

**Evidence Layer Benefits**

The Evidence Layer provides:

- **Verifiable Provenance:** W3C PROV provides standard provenance tracking
- **Execution Lineage:** OpenLineage provides execution lifecycle tracking
- **Intent Lineage:** Intent lineage tracks intent evolution and achievement
- **Complete Traceability:** Evidence chains provide complete traceability

This enables intent-driven systems that provide verifiable outcomes with complete traceability.

---

## Chapter 5 Summary

The four pillars form a complete architecture for intent-driven systems **with tag-based canonical identity**: Contract Layer (pure intent expression **for specific entities via tags**), Execution Layer (reliable achievement **for specific entities**), Safety Layer (safe execution **with entity-aware confidence gates**), Evidence Layer (verifiable outcomes **with tag-based entity tracking**). Together, these pillars enable systems that understand their own purpose **for which entities**, execute reliably **for specific entities**, maintain safety **with entity-aware gates**, and provide verifiable outcomes **with tag-based entity tracking**—transforming AI from execution tools to conscious systems **with canonical entity identity**.

**Tags enable canonical identity** throughout the four pillars: contracts express intent **for specific entities via tags** (`entity="plix://room/meeting_room"`), execution achieves intent **for specific entities**, safety gates check confidence **for specific entities**, and evidence tracks provenance **with tag-based entity references**. Tags enable unambiguous entity references that survive technology changes, enabling the four pillars architecture with canonical identity—systems express intent **for which entities**, achieve intent **for specific entities**, ensure safety **for specific entities**, and provide evidence **with entity-aware tracking**.

**Next:** Chapter 6 explores CNL grammar—the human-readable syntax for PLIx contracts **with tag-based entity references**.

---

**Word Count:** ~2,700 words (enhanced from ~2,400)  
**Status:** ✅ **COMPLETE** (v2.0 Enhanced)  
**Cross-References:**
- Chapter 5 (Part I): Tag System (tag format and canonical identity)
- Chapter 8: Compiler Architecture (tag resolution in compilation)
- Chapter 9: CMC Integration (contract storage with entity tags)
- Chapter 11: APOE Integration (execution with entity tags)

