# Chapter 44: CMC Integration: Intent-Aware Memory

**Part IV: Integration**  
**Unified Textbook Chapter Number:** 44

---

> **Cross-References:**
> - **AIM-OS Foundations:** See Chapter 5 (Memory That Never Forgets - CMC) for CMC architecture
> - **PLIx Architecture:** See Chapter 40 (The Four Pillars) for how CMC integrates with the Evidence Layer
> - **PLIx Foundations:** See Chapter 37 (Intent vs Execution) for how CMC stores intent separately from execution
> - **Tag System:** See Chapter 5 (Tag System) for how entity tags enable canonical identity in CMC

---

**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)

---

## Section 44.1: Before PLIx: Fact Storage

Before PLIx, CMC (Context Memory Core) stores facts, events, and states—execution artifacts that record what happened, not what was intended.

**CMC's Original Purpose**

CMC was designed to store:

- **Facts:** Immutable facts about the world
- **Events:** Things that happened at specific times
- **States:** System states at specific points in time
- **Atoms:** Fundamental units of memory with bitemporal tracking

CMC's strength lies in its bitemporal versioning: it tracks both when facts were recorded (transaction time) and when they were valid (valid time), enabling temporal queries like "what was known at time T?"

**Fact Storage Example**

Before PLIx, CMC stores execution artifacts:

```python
# Store execution fact
atom = cmc.create_atom({
    content: {
        "action": "book_room",
        "result": "success",
        "room_id": "A101",
        "timestamp": "2025-12-01T10:00:00Z"
    },
    tags: ["execution", "room_booking"]
})

# Query: What happened?
facts = cmc.query({
    tags: ["execution", "room_booking"],
    valid_at: "2025-12-01T10:00:00Z"
})
# Returns: Execution facts, not intent
```

CMC stores what happened (execution facts) but not what was intended (intent contracts). This limits CMC's ability to reason about purpose and verify intent achievement.

**Limitations of Fact Storage**

Fact storage has limitations:

- **No Intent Awareness:** CMC doesn't know what was intended, only what happened
- **No Intent Queries:** Can't query "what was the intent behind this action?"
- **No Intent Verification:** Can't verify "did this outcome satisfy the intent?"
- **No Intent Lineage:** Can't trace outcomes back to intents

These limitations prevent CMC from supporting intent-driven reasoning, verification, and learning.

**Bitemporal Versioning**

CMC's bitemporal versioning enables temporal queries:

```python
# Bitemporal query: What was known at time T?
facts = cmc.query({
    valid_at: "2025-12-01T09:00:00Z",  # Valid time
    transaction_at: "2025-12-01T10:00:00Z"  # Transaction time
})

# Returns: Facts that were valid at 09:00 and recorded by 10:00
```

Bitemporal versioning enables temporal reasoning, but without intent awareness, CMC can't reason about intent evolution or intent-outcome relationships.

**Before PLIx Summary**

Before PLIx, CMC is execution-focused:
- Stores what happened (facts, events, states)
- Enables temporal queries (what was known when)
- Lacks intent awareness (no intent storage or queries)
- Lacks intent verification (can't verify intent achievement)

This execution focus limits CMC's ability to support intent-driven systems.

---

## Section 44.2: After PLIx: Intent Memory

After PLIx, CMC stores intent contracts, plans, and evidence—intent artifacts that record what was intended, enabling intent-aware memory and reasoning.

**Intent-Aware Storage**

With PLIx, CMC stores intent contracts:

```python
# Store PLIx contract with tags
contract = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room",  # Entity tag
    contract={
        "pre": ["room_available == true"],
        "post": ["room_reserved == true"]
    }
)

atom = cmc.create_atom({
    content: {
        "type": "plix_contract",
        "contract": contract,
        "intent": contract.intent,
        "entity_tag": contract.entity,  # Store entity tag
        "resolved_entity": resolveTag(contract.entity)  # Resolved entity (cached)
    },
    tags: ["intent", "plix_contract", "room_booking", contract.entity]  # Include entity tag
})

# Query: What was intended?
intents = cmc.query({
    tags: ["intent", "plix_contract"],
    valid_at: "2025-12-01T10:00:00Z"
})
# Returns: Intent contracts, not just execution facts
```

CMC now stores what was intended (intent contracts) **with tag-based entity references**, enabling intent-aware memory with canonical identity. Tags enable unambiguous entity references (`plix://room/meeting_room`), while resolved entities enable efficient queries.

**Intent Queries**

With PLIx, CMC enables intent queries:

```python
# Query: What intents targeted this entity?
intents = cmc.query({
    tags: ["intent", "plix_contract", "plix://room/meeting_room"],  # Query by entity tag
    content_filter: {
        "contract.post": {"$contains": "room_reserved == true"}
    }
})
# Returns: All intents that intended to reserve the meeting room (identified by tag)

# Query: What was the intent behind this action?
intent = cmc.query({
    tags: ["intent", "plix_contract"],
    content_filter: {
        "execution.action": "book_room",
        "entity_tag": "plix://room/meeting_room"  # Filter by entity tag
    }
})
# Returns: Intent contract that led to this action for this entity
```

Intent queries enable reasoning about purpose: we can query what was intended **for specific entities via tags**, trace outcomes to intents, and understand the relationship between intent and execution. Tags enable entity-based intent discovery.

**Intent Versioning**

With PLIx, CMC enables intent versioning:

```python
# Store intent version 1
contract_v1 = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room"  # Entity tag
)
atom_v1 = cmc.create_atom({
    content: {
        "type": "plix_contract",
        "contract": contract_v1,
        "version": 1,
        "entity_tag": contract_v1.entity  # Store entity tag
    },
    tags: ["intent", "plix_contract", contract_v1.entity]  # Include entity tag
})

# Store intent version 2 (evolved)
contract_v2 = PLIxContract(
    intent="Book a meeting room with catering",
    entity="plix://room/meeting_room"  # Same entity tag
)
atom_v2 = cmc.create_atom({
    content: {
        "type": "plix_contract",
        "contract": contract_v2,
        "version": 2,
        "entity_tag": contract_v2.entity  # Same entity tag
    },
    tags: ["intent", "plix_contract", contract_v2.entity],  # Same entity tag
    parent_atom_id: atom_v1.id  # Link to version 1
})

# Query: How did intent evolve for this entity?
evolution = cmc.query_lineage(atom_v2.id)
# Returns: Intent evolution chain (v1 → v2) for entity plix://room/meeting_room
```

Intent versioning enables temporal reasoning about intent evolution: we can trace how intent evolved over time **for specific entities via tags**, understand intent refinement, and reason about intent-outcome relationships across versions. Tags enable entity-based intent evolution tracking.

**Intent-Outcome Mapping**

With PLIx, CMC enables intent-outcome mapping:

```python
# Store intent
intent_atom = cmc.create_atom({
    content: {"type": "plix_contract", "contract": contract},
    tags: ["intent"]
})

# Store outcome
outcome_atom = cmc.create_atom({
    content: {"type": "execution_result", "room_reserved": True},
    tags: ["outcome"],
    parent_atom_id: intent_atom.id  # Link to intent
})

# Query: Did outcome satisfy intent?
verification = verifyIntent(intent_atom.content.contract, outcome_atom.content)
# Returns: True if postconditions satisfied
```

Intent-outcome mapping enables verification: we can check if outcomes satisfied intents, measure intent achievement rates, and learn from intent-outcome relationships.

**After PLIx Summary**

After PLIx, CMC is intent-aware:
- Stores what was intended (intent contracts, plans, evidence)
- Enables intent queries (what was intended, what intents led to outcomes)
- Supports intent versioning (tracks intent evolution)
- Enables intent-outcome mapping (verifies intent achievement)

This intent awareness transforms CMC from execution-focused memory to intent-aware memory, enabling intent-driven reasoning, verification, and learning.

---

## Section 44.3: Transformation Details

The transformation from fact storage to intent memory involves storing PLIx contracts as CMC atoms, enabling intent queries, versioning, and checkpoint integration.

**PLIx Contract → CMC Atom**

PLIx contracts store as CMC atoms **with tag-based entity references**:

```python
def storePLIxContract(contract: PLIxContract, cmc: MemoryStore) -> str:
    """Store PLIx contract as CMC atom with tag resolution"""
    # Resolve entity tag
    entity_tag = contract.entity or contract.entityTag
    resolved_entity = resolveTag(entity_tag) if entity_tag else None
    
    # Resolve capability tags
    capability_tags = [task.capabilityTag for task in contract.tasks if hasattr(task, 'capabilityTag')]
    resolved_capabilities = {tag: resolveTag(tag) for tag in capability_tags if tag}
    
    atom = cmc.create_atom({
        content: {
            "type": "plix_contract",
            "intent": contract.intent,
            "contract": contract.to_dict(),
            "tasks": [task.to_dict() for task in contract.tasks],
            "constraints": contract.constraints,
            "evidence": contract.evidence,
            "entity_tag": entity_tag,  # Store entity tag
            "resolved_entity": resolved_entity,  # Store resolved entity
            "capability_tags": capability_tags,  # Store capability tags
            "resolved_capabilities": resolved_capabilities  # Store resolved capabilities
        },
        tags: [
            "intent", 
            "plix_contract", 
            contract.intent,
            entity_tag  # Include entity tag for queries
        ] + capability_tags,  # Include capability tags
        metadata: {
            "created_at": datetime.now(),
            "contract_version": contract.version
        }
    })
    return atom.id
```

This transformation preserves contract semantics **with tag-based entity references**, enabling CMC's bitemporal versioning and query capabilities. Tags enable canonical identity for entities and capabilities, while resolved entities/capabilities enable efficient queries.

**Intent Metadata**

Intent metadata enables intent queries:

```python
def addIntentMetadata(atom: Atom, contract: PLIxContract):
    """Add intent metadata to atom with tag information"""
    entity_tag = contract.entity or contract.entityTag
    resolved_entity = resolveTag(entity_tag) if entity_tag else None
    
    atom.metadata.update({
        "intent": contract.intent,
        "intent_type": classifyIntent(contract.intent),
        "intent_domain": extractDomain(contract.intent),
        "intent_confidence": calculateConfidence(contract),
        "entity_tag": entity_tag,  # Entity tag
        "entity_type": resolved_entity.get("type") if resolved_entity else None,  # Entity type from resolution
        "entity_location": resolved_entity.get("location") if resolved_entity else None  # Entity location from resolution
    })
```

Intent metadata enables intent classification, domain extraction, confidence tracking, **and tag-based entity discovery**, supporting intent queries and reasoning. Tags enable entity-based intent discovery.

**Intent Lineage**

Intent lineage tracks intent evolution:

```python
def trackIntentLineage(contract: PLIxContract, parent_atom_id: str, cmc: MemoryStore):
    """Track intent lineage with tag-based entity references"""
    entity_tag = contract.entity or contract.entityTag
    
    atom = cmc.create_atom({
        content: {
            "type": "plix_contract",
            "contract": contract,
            "entity_tag": entity_tag  # Store entity tag
        },
        tags: ["intent", "plix_contract", entity_tag],  # Include entity tag
        parent_atom_id: parent_atom_id  # Link to parent intent
    })
    
    # Query lineage for this entity
    lineage = cmc.query_lineage(atom.id)
    # Returns: Chain of intent evolution for entity plix://room/meeting_room
```

Intent lineage enables temporal reasoning about intent evolution, enabling queries like "how did this intent evolve **for this entity**?" and "what intents led to this outcome **for this entity**?". Tags enable entity-based intent lineage tracking.

**Checkpoint Integration**

Checkpoint integration enables durable execution:

```python
def createCheckpoint(node_id: str, state: dict, entity_tag: str, cmc: MemoryStore) -> str:
    """Create execution checkpoint with entity tag"""
    checkpoint_atom = cmc.create_atom({
        content: {
            "type": "plix_checkpoint",
            "node_id": node_id,
            "state": state,
            "timestamp": datetime.now(),
            "entity_tag": entity_tag  # Store entity tag
        },
        tags: ["checkpoint", "plix_execution", node_id, entity_tag]  # Include entity tag
    })
    return checkpoint_atom.id

def restoreFromCheckpoint(checkpoint_id: str, cmc: MemoryStore) -> dict:
    """Restore state from checkpoint"""
    checkpoint = cmc.get_atom(checkpoint_id)
    return checkpoint.content["state"]
```

Checkpoint integration enables durable execution: CMC stores execution state **with tag-based entity references**, enabling recovery from failures and resuming execution from checkpoints. Tags enable entity-based checkpoint queries.

**Transformation Benefits**

The transformation provides:

- **Intent Storage:** CMC stores intent contracts, enabling intent-aware memory
- **Intent Queries:** CMC enables intent queries, enabling intent-driven reasoning
- **Intent Versioning:** CMC tracks intent evolution, enabling temporal reasoning
- **Checkpoint Integration:** CMC stores execution state, enabling durable execution

These benefits transform CMC from execution-focused memory to intent-aware memory, enabling intent-driven systems.

---

## Section 44.4: Implementation Examples

Implementation examples demonstrate PLIx contract storage, intent queries, intent versioning, and checkpoint creation in CMC.

**Example 1: Store PLIx Contract**

```python
# PLIx contract with entity tag
contract = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room",  # Entity tag
    contract={
        "pre": ["room_available == true"],
        "post": ["room_reserved == true"]
    },
    tasks=[
        Task(
            id="check_availability", 
            action="api.check_room_availability",
            entityTag="plix://room/meeting_room"  # Entity tag
        ),
        Task(
            id="reserve_room", 
            action="api.reserve_room", 
            depends_on=["check_availability"],
            entityTag="plix://room/meeting_room"  # Same entity tag
        )
    ]
)

# Store in CMC
atom_id = storePLIxContract(contract, cmc)
print(f"Stored contract: {atom_id}")

# Query intent by entity tag
intent_atoms = cmc.query({
    tags: ["intent", "plix_contract", "plix://room/meeting_room"],  # Query by entity tag
    content_filter: {"intent": "Book a meeting room"}
})
print(f"Found {len(intent_atoms)} intent contracts for entity plix://room/meeting_room")
```

This example demonstrates storing PLIx contracts in CMC and querying them by intent.

**Example 2: Intent Queries**

```python
# Query: What intents intended to reserve this entity?
intents = cmc.query({
    tags: ["intent", "plix_contract", "plix://room/meeting_room"],  # Query by entity tag
    content_filter: {
        "contract.post": {"$contains": "room_reserved == true"}
    }
})

# Query: What was the intent behind this execution for this entity?
execution_atom = cmc.get_atom(execution_atom_id)
intent_atom = cmc.query({
    tags: ["intent", "plix_contract", execution_atom.content["entity_tag"]],  # Query by entity tag
    content_filter: {
        "execution.action": execution_atom.content["action"]
    }
})[0]

print(f"Intent: {intent_atom.content['intent']}")
print(f"Entity: {intent_atom.content['entity_tag']}")  # Entity tag
print(f"Contract: {intent_atom.content['contract']}")
```

This example demonstrates intent queries: finding intents by postconditions and tracing execution to intent.

**Example 3: Intent Versioning**

```python
# Store intent version 1 with entity tag
contract_v1 = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room"  # Entity tag
)
atom_v1 = storePLIxContract(contract_v1, cmc)

# Store intent version 2 (evolved) with same entity tag
contract_v2 = PLIxContract(
    intent="Book a meeting room with catering",
    entity="plix://room/meeting_room"  # Same entity tag
)
atom_v2 = cmc.create_atom({
    content: {
        "type": "plix_contract",
        "contract": contract_v2,
        "entity_tag": contract_v2.entity  # Same entity tag
    },
    tags: ["intent", "plix_contract", contract_v2.entity],  # Same entity tag
    parent_atom_id: atom_v1  # Link to version 1
})

# Query intent evolution for this entity
lineage = cmc.query_lineage(atom_v2)
print(f"Intent evolution for plix://room/meeting_room: {[atom.content['intent'] for atom in lineage]}")
```

This example demonstrates intent versioning: storing evolved intents and querying intent evolution.

**Example 4: Checkpoint Creation**

```python
# Create checkpoint before execution with entity tag
checkpoint_id = createCheckpoint("reserve_room", {
    "inputs": {"room_id": "A101", "date": "2025-12-01"},
    "status": "running",
    "entity_tag": "plix://room/meeting_room"  # Entity tag
}, "plix://room/meeting_room", cmc)

try:
    # Execute task
    result = executeTask("reserve_room", {"room_id": "A101"})
    
    # Update checkpoint on success
    cmc.create_atom({
        content: {
            "type": "plix_checkpoint",
            "node_id": "reserve_room",
            "state": {
                "inputs": {...}, 
                "outputs": result, 
                "status": "completed",
                "entity_tag": "plix://room/meeting_room"  # Entity tag
            }
        },
        tags: ["checkpoint", "plix_execution", "plix://room/meeting_room"],  # Include entity tag
        parent_atom_id: checkpoint_id
    })
except Exception as e:
    # Restore from checkpoint on failure
    state = restoreFromCheckpoint(checkpoint_id, cmc)
    print(f"Restored state for plix://room/meeting_room: {state}")
    raise e
```

This example demonstrates checkpoint creation: storing execution state, updating on success, and restoring on failure.

**Implementation Benefits**

Implementation examples demonstrate:

- **Contract Storage:** Storing PLIx contracts as CMC atoms
- **Intent Queries:** Querying intents by postconditions and execution
- **Intent Versioning:** Tracking intent evolution
- **Checkpoint Integration:** Enabling durable execution

These examples show how CMC transforms from fact storage to intent-aware memory, enabling intent-driven systems.

---

## Chapter 44 Summary

CMC transforms from fact storage to intent-aware memory through PLIx integration. Before PLIx, CMC stores execution facts but lacks intent awareness. After PLIx, CMC stores intent contracts **with tag-based entity references**, enables intent queries **by entity tags**, supports intent versioning **with tag-based lineage**, and integrates checkpoints **with tag-based entity tracking** for durable execution.

**Tags enable canonical identity** throughout CMC integration: intent contracts reference entities via tags (`plix://room/meeting_room`), intent queries filter by entity tags, intent lineage tracks evolution by entity tags, and checkpoints include entity tags for entity-based recovery. Tags enable unambiguous entity references that survive technology changes, enabling intent-aware memory with canonical identity.

This transformation enables intent-driven reasoning, verification, and learning, making CMC a foundation for intent-aware systems. Tags provide the identity foundation that makes this transformation possible.

**Next:** Chapter 45 explores VIF integration—how VIF transforms from execution verification to intent verification, showing how tags enable intent verification.

---

**Word Count:** ~2,800 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)  
**Cross-References:**
> - **AIM-OS Foundations:** Chapter 5 (Memory That Never Forgets - CMC)
> - **PLIx Architecture:** Chapter 40 (The Four Pillars)
> - **PLIx Foundations:** Chapter 37 (Intent vs Execution)
> - **Tag System:** Chapter 5 (Tag System)

