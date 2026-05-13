# Chapter 47: SEG Integration: Intent-Aware Evidence

**Part IV: Integration**  
**Unified Textbook Chapter Number:** 47

---

> **Cross-References:**
> - **AIM-OS Foundations:** See Chapter 9 (Evidence Graph - SEG) for SEG architecture
> - **PLIx Architecture:** See Chapter 40 (The Four Pillars) for how SEG integrates with the Evidence Layer
> - **PLIx Integration:** See Chapter 44 (CMC Integration) for intent storage with tags
> - **PLIx Integration:** See Chapter 45 (VIF Integration) for intent verification with tags
> - **PLIx Integration:** See Chapter 46 (APOE Integration) for evidence collection with tags
> - **Tag System:** See Chapter 5 (Tag System) for how entity tags enable canonical identity in SEG

---

**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)

---

## Section 47.1: Before PLIx: Evidence Chains

Before PLIx, SEG (Shared Evidence Graph) stores evidence chains—linking claims to evidence (code, docs, tests, decisions) but lacking intent awareness.

**SEG's Original Purpose**

SEG was designed to:

- **Store Evidence Chains:** Link claims to evidence through graph edges
- **Track Entities:** Store entities (claims, sources, derivations, agents)
- **Track Relations:** Store relations (SUPPORTS, CONTRADICTS, REFERENCES)
- **Enable Reasoning:** Enable queries like "what evidence supports this claim?"

SEG's strength lies in its graph-based structure, enabling complex evidence reasoning through entity-relation graphs.

**Evidence Chain Example**

Before PLIx, SEG stores evidence chains:

```python
# Create claim entity
claim = Entity(
    type="claim",
    name="Room booking system works correctly",
    attributes={"description": "System can book rooms"}
)

claim_entity = seg.add_entity(claim)

# Create evidence entity
evidence = Entity(
    type="evidence",
    name="Test results",
    attributes={"test_file": "test_booking.py", "pass_rate": 0.95}
)

evidence_entity = seg.add_entity(evidence)

# Create evidence relation
relation = Relation(
    source_id=evidence_entity.id,
    target_id=claim_entity.id,
    relation_type=RelationType.SUPPORTS,
    confidence=0.95
)

seg.add_relation(relation)

# Query: What evidence supports this claim?
supporting_evidence = seg.query_relations(
    target_id=claim_entity.id,
    relation_type=RelationType.SUPPORTS
)
```

SEG stores evidence chains (what supports what) but doesn't track intent lineage (what intents led to outcomes). This limits SEG's ability to reason about purpose and verify intent-outcome relationships.

**Limitations of Evidence Chains**

Evidence chains have limitations:

- **No Intent Awareness:** SEG doesn't know what was intended, only what evidence exists
- **No Intent Lineage:** Can't trace outcomes back to intents
- **No Intent Evolution:** Can't track how intent evolved over time
- **No Intent-Outcome Mapping:** Can't map outcomes to intents

These limitations prevent SEG from supporting intent-driven reasoning, verification, and learning.

**Entity-Relation Structure**

SEG uses entity-relation structure:

```python
# Entities represent claims, sources, derivations, agents
claim_entity = Entity(type="claim", name="Room booking works")
source_entity = Entity(type="source", name="Test results")
agent_entity = Entity(type="agent", name="Test runner")

# Relations link entities
support_relation = Relation(
    source_id=source_entity.id,
    target_id=claim_entity.id,
    relation_type=RelationType.SUPPORTS
)
```

Entity-relation structure enables complex reasoning, but without intent awareness, entities don't represent intents.

**Before PLIx Summary**

Before PLIx, SEG is execution-focused:
- Stores evidence chains (what supports what)
- Tracks entities and relations
- Enables evidence reasoning
- Lacks intent awareness (no intent lineage or evolution tracking)

This execution focus limits SEG's ability to support intent-driven reasoning and verification.

---

## Section 47.2: After PLIx: Intent Lineage

After PLIx, SEG stores intent lineage—tracing outcomes back to intents, tracking intent evolution, and mapping intent-outcome relationships.

**Intent-Aware Entities**

With PLIx, SEG stores intent entities:

```python
# Create intent entity with entity tag
intent_entity = Entity(
    type="intent",
    name="Book a meeting room",
    attributes={
        "contract": contract.to_dict(),
        "intent_type": "booking",
        "domain": "meeting_rooms",
        "entity_tag": contract.entity or contract.entityTag  # Entity tag
    }
)

intent_entity_id = seg.add_entity(intent_entity)

# Create outcome entity with entity tag
outcome_entity = Entity(
    type="outcome",
    name="Room reserved",
    attributes={
        "room_reserved": True,
        "reservation_id": "res-123",
        "entity_tag": contract.entity or contract.entityTag  # Same entity tag
    }
)

outcome_entity_id = seg.add_entity(outcome_entity)

# Create intent-outcome relation
intent_outcome_relation = Relation(
    source_id=intent_entity_id,
    target_id=outcome_entity_id,
    relation_type=RelationType.ACHIEVES,  # Intent → Outcome
    confidence=0.90,
    attributes={
        "postconditions_satisfied": True,
        "verification_timestamp": datetime.now(),
        "entity_tag": contract.entity or contract.entityTag  # Entity tag
    }
)

seg.add_relation(intent_outcome_relation)
```

SEG now stores intent entities **with tag-based entity references** and intent-outcome relations, enabling intent lineage tracking with canonical identity. Tags enable unambiguous entity references (`plix://room/meeting_room`), enabling entity-based intent lineage queries.

**Intent Lineage Tracking**

With PLIx, SEG tracks intent lineage:

```python
# Track intent lineage: NL → Contract → Plan → Execution → Outcome (with entity tags)
entity_tag = contract.entity or contract.entityTag

nl_intent_entity = Entity(
    type="nl_intent",
    name="Book a meeting room",
    attributes={
        "original_text": "Book a meeting room",
        "entity_tag": entity_tag  # Entity tag
    }
)

contract_entity = Entity(
    type="plix_contract",
    name="PLIx Contract",
    attributes={
        "contract": contract.to_dict(),
        "entity_tag": entity_tag  # Entity tag
    }
)

plan_entity = Entity(
    type="execution_plan",
    name="APOE Execution Plan",
    attributes={
        "plan": plan.to_dict(),
        "entity_tag": entity_tag  # Entity tag
    }
)

execution_entity = Entity(
    type="execution",
    name="Execution Result",
    attributes={
        "result": result.to_dict(),
        "entity_tag": entity_tag  # Entity tag
    }
)

outcome_entity = Entity(
    type="outcome",
    name="Room Reserved",
    attributes={
        "room_reserved": True,
        "entity_tag": entity_tag  # Entity tag
    }
)

# Create lineage chain (all entities share same entity tag)
seg.add_relation(Relation(
    source_id=nl_intent_entity.id,
    target_id=contract_entity.id,
    relation_type=RelationType.COMPILES_TO,
    attributes={"entity_tag": entity_tag}
))

seg.add_relation(Relation(
    source_id=contract_entity.id,
    target_id=plan_entity.id,
    relation_type=RelationType.COMPILES_TO,
    attributes={"entity_tag": entity_tag}
))

seg.add_relation(Relation(
    source_id=plan_entity.id,
    target_id=execution_entity.id,
    relation_type=RelationType.EXECUTES_TO,
    attributes={"entity_tag": entity_tag}
))

seg.add_relation(Relation(
    source_id=execution_entity.id,
    target_id=outcome_entity.id,
    relation_type=RelationType.PRODUCES,
    attributes={"entity_tag": entity_tag}
))

# Query lineage: Trace outcome back to NL intent for this entity
lineage = seg.query_lineage(outcome_entity.id, direction="backward", entity_tag=entity_tag)
# Returns: Outcome → Execution → Plan → Contract → NL Intent (for entity plix://room/meeting_room)
```

Intent lineage tracking enables SEG to trace outcomes back to intents **for specific entities via tags**, enabling queries like "what intent led to this outcome **for this entity**?". Tags enable entity-based intent lineage queries.

**Intent Evolution Tracking**

With PLIx, SEG tracks intent evolution:

```python
# Store intent version 1 with entity tag
entity_tag = contract_v1.entity or contract_v1.entityTag

intent_v1 = Entity(
    type="intent",
    name="Book a meeting room",
    attributes={
        "version": 1,
        "contract": contract_v1.to_dict(),
        "entity_tag": entity_tag  # Entity tag
    }
)

intent_v1_id = seg.add_entity(intent_v1)

# Store intent version 2 (evolved) with same entity tag
intent_v2 = Entity(
    type="intent",
    name="Book a meeting room with catering",
    attributes={
        "version": 2,
        "contract": contract_v2.to_dict(),
        "entity_tag": entity_tag  # Same entity tag
    }
)

intent_v2_id = seg.add_entity(intent_v2)

# Create evolution relation
evolution_relation = Relation(
    source_id=intent_v1_id,
    target_id=intent_v2_id,
    relation_type=RelationType.EVOLVES_TO,
    attributes={
        "evolution_type": "refinement",
        "changes": ["added_catering_requirement"],
        "entity_tag": entity_tag  # Entity tag
    }
)

seg.add_relation(evolution_relation)

# Query evolution: How did intent evolve for this entity?
evolution_chain = seg.query_lineage(intent_v2_id, relation_type=RelationType.EVOLVES_TO, entity_tag=entity_tag)
# Returns: Intent v1 → Intent v2 (evolution chain for entity plix://room/meeting_room)
```

Intent evolution tracking enables SEG to track how intent evolved over time **for specific entities via tags**, enabling queries like "how did this intent evolve **for this entity**?". Tags enable entity-based intent evolution tracking.

**Intent-Outcome Mapping**

With PLIx, SEG maps outcomes to intents:

```python
# Map outcome to intent (uses entity tag filtering)
def map_outcome_to_intent(outcome: dict, entity_tag: str, seg: SEGraph) -> List[Entity]:
    """Map outcome to intents that achieved it for this entity"""
    
    # Find outcomes matching this outcome and entity tag
    outcome_entities = seg.query_entities(
        type="outcome",
        attributes_filter={
            "room_reserved": True,
            "entity_tag": entity_tag  # Filter by entity tag
        }
    )
    
    # Find intents that achieved these outcomes
    intent_entities = []
    for outcome_entity in outcome_entities:
        relations = seg.query_relations(
            target_id=outcome_entity.id,
            relation_type=RelationType.ACHIEVES,
            attributes_filter={"entity_tag": entity_tag}  # Filter by entity tag
        )
        for relation in relations:
            intent_entity = seg.get_entity(relation.source_id)
            if intent_entity.attributes.get("entity_tag") == entity_tag:  # Verify entity tag match
                intent_entities.append(intent_entity)
    
    return intent_entities

# Query: What intents achieved this outcome for this entity?
intents = map_outcome_to_intent({"room_reserved": True}, "plix://room/meeting_room", seg)
```

Intent-outcome mapping enables SEG to query which intents achieved which outcomes **for specific entities via tags**, enabling intent-driven learning. Tags enable entity-based intent-outcome mapping.

**After PLIx Summary**

After PLIx, SEG is intent-aware:
- Stores intent lineage (traces outcomes back to intents)
- Tracks intent evolution (how intent evolved over time)
- Maps intent-outcome relationships (which intents achieved which outcomes)
- Enables intent-driven reasoning (queries about intent and outcomes)

This intent awareness transforms SEG from execution-focused evidence to intent-aware evidence, enabling intent-driven reasoning and learning.

---

## Section 47.3: Transformation Details

The transformation from evidence chains to intent lineage involves storing PLIx contracts as SEG entities, creating intent relations, collecting intent evidence, and enabling intent lineage queries.

**PLIx Contracts → SEG Entities**

PLIx contracts store as SEG entities **with tag-based entity references**:

```python
def store_plix_contract_as_entity(contract: PLIxContract, seg: SEGraph) -> str:
    """Store PLIx contract as SEG entity with tag resolution"""
    
    entity_tag = contract.entity or contract.entityTag
    resolved_entity = resolveTag(entity_tag) if entity_tag else None
    
    entity = Entity(
        type="plix_contract",
        name=contract.intent,
        attributes={
            "intent": contract.intent,
            "contract": contract.to_dict(),
            "tasks": [task.to_dict() for task in contract.tasks],
            "constraints": contract.constraints,
            "evidence": contract.evidence,
            "entity_tag": entity_tag,  # Entity tag
            "resolved_entity": resolved_entity  # Resolved entity (cached)
        }
    )
    
    entity_id = seg.add_entity(entity)
    return entity_id
```

This transformation preserves contract semantics **with tag-based entity references**, enabling SEG's graph-based reasoning. Tags enable canonical identity for entities, while resolved entities enable efficient queries.

**Intent Relations**

Intent relations link intents to outcomes **with tag-based entity references**:

```python
def create_intent_outcome_relation(
    intent_entity_id: str,
    outcome_entity_id: str,
    verification_result: bool,
    confidence: float,
    entity_tag: str,
    seg: SEGraph
) -> str:
    """Create intent-outcome relation with entity tag"""
    
    relation = Relation(
        source_id=intent_entity_id,
        target_id=outcome_entity_id,
        relation_type=RelationType.ACHIEVES,
        confidence=confidence,
        attributes={
            "postconditions_satisfied": verification_result,
            "verification_timestamp": datetime.now(),
            "entity_tag": entity_tag  # Entity tag
        }
    )
    
    relation_id = seg.add_relation(relation)
    return relation_id
```

Intent relations enable SEG to track which intents achieved which outcomes **for specific entities via tags**, enabling intent-outcome reasoning. Tags enable entity-based intent-outcome queries.

**Intent Evidence Collection**

Intent evidence collection stores evidence in SEG **with tag-based entity references**:

```python
def collect_intent_evidence(
    contract: PLIxContract,
    outcome: dict,
    execution_provenance: dict,
    seg: SEGraph
) -> str:
    """Collect intent evidence and store in SEG with entity tag"""
    
    entity_tag = contract.entity or contract.entityTag
    
    # Create evidence entity
    evidence_entity = Entity(
        type="intent_evidence",
        name=f"Evidence for {contract.intent}",
        attributes={
            "contract": contract.to_dict(),
            "outcome": outcome,
            "execution_provenance": execution_provenance,
            "postconditions_satisfied": verify_contract(contract, outcome),
            "entity_tag": entity_tag  # Entity tag
        }
    )
    
    evidence_id = seg.add_entity(evidence_entity)
    
    # Link to intent
    seg.add_relation(Relation(
        source_id=evidence_id,
        target_id=get_intent_entity_id(contract, seg),
        relation_type=RelationType.PROVIDES_EVIDENCE_FOR,
        attributes={"entity_tag": entity_tag}  # Entity tag
    ))
    
    return evidence_id
```

Intent evidence collection enables SEG to store proof of intent achievement **with tag-based entity references**, supporting verification and learning. Tags enable entity-based evidence queries.

**Intent Lineage Queries**

Intent lineage queries enable intent-driven reasoning **with tag-based entity filtering**:

```python
def query_intent_lineage(outcome_entity_id: str, entity_tag: str, seg: SEGraph) -> List[Entity]:
    """Query intent lineage: Trace outcome back to intent for this entity"""
    
    # Find relations where outcome is target and entity tag matches
    relations = seg.query_relations(
        target_id=outcome_entity_id,
        relation_type=RelationType.ACHIEVES,
        attributes_filter={"entity_tag": entity_tag}  # Filter by entity tag
    )
    
    # Get intent entities
    intent_entities = []
    for relation in relations:
        intent_entity = seg.get_entity(relation.source_id)
        if intent_entity.type == "plix_contract" and intent_entity.attributes.get("entity_tag") == entity_tag:
            intent_entities.append(intent_entity)
    
    return intent_entities

def query_outcome_lineage(intent_entity_id: str, entity_tag: str, seg: SEGraph) -> List[Entity]:
    """Query outcome lineage: Trace intent to outcomes for this entity"""
    
    # Find relations where intent is source and entity tag matches
    relations = seg.query_relations(
        source_id=intent_entity_id,
        relation_type=RelationType.ACHIEVES,
        attributes_filter={"entity_tag": entity_tag}  # Filter by entity tag
    )
    
    # Get outcome entities
    outcome_entities = []
    for relation in relations:
        outcome_entity = seg.get_entity(relation.target_id)
        if outcome_entity.attributes.get("entity_tag") == entity_tag:  # Verify entity tag match
            outcome_entities.append(outcome_entity)
    
    return outcome_entities
```

Intent lineage queries enable SEG to trace outcomes to intents and intents to outcomes **for specific entities via tags**, enabling intent-driven reasoning. Tags enable entity-based intent lineage queries.

**Transformation Benefits**

The transformation provides:

- **Intent Lineage:** SEG tracks intent lineage, enabling outcome-to-intent tracing
- **Intent Evolution:** SEG tracks intent evolution, enabling temporal reasoning
- **Intent-Outcome Mapping:** SEG maps outcomes to intents, enabling learning
- **Intent Evidence:** SEG stores intent evidence, enabling verification

These benefits transform SEG from execution-focused evidence to intent-aware evidence, enabling intent-driven reasoning and learning.

---

## Section 47.4: Implementation Examples

Implementation examples demonstrate PLIx → SEG entity creation, intent relation creation, intent evidence collection, and intent lineage queries.

**Example 1: PLIx → SEG Entity Creation**

```python
# PLIx contract with entity tag
contract = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room",  # Entity tag
    contract={"post": ["room_reserved == true"]}
)

# Store as SEG entity
intent_entity_id = store_plix_contract_as_entity(contract, seg)

# Query entity
intent_entity = seg.get_entity(intent_entity_id)
print(f"Intent: {intent_entity.attributes['intent']}")
print(f"Entity Tag: {intent_entity.attributes['entity_tag']}")  # plix://room/meeting_room
print(f"Contract: {intent_entity.attributes['contract']}")
```

This example demonstrates storing PLIx contracts as SEG entities, enabling graph-based reasoning.

**Example 2: Intent Relation Creation**

```python
# Create intent-outcome relation with entity tag
entity_tag = contract.entity or contract.entityTag

intent_entity_id = store_plix_contract_as_entity(contract, seg)
outcome_entity_id = seg.add_entity(Entity(
    type="outcome",
    name="Room Reserved",
    attributes={
        "room_reserved": True,
        "entity_tag": entity_tag  # Entity tag
    }
))

relation_id = create_intent_outcome_relation(
    intent_entity_id,
    outcome_entity_id,
    verification_result=True,
    confidence=0.90,
    entity_tag=entity_tag,  # Entity tag
    seg
)

print(f"Intent-outcome relation created for {entity_tag}: {relation_id}")
```

This example demonstrates creating intent-outcome relations, linking intents to outcomes.

**Example 3: Intent Evidence Collection**

```python
# Collect intent evidence (includes entity tag)
entity_tag = contract.entity or contract.entityTag

evidence_id = collect_intent_evidence(
    contract=contract,
    outcome={"room_reserved": True},
    execution_provenance={"execution_id": "exec-123"},
    seg=seg
)

print(f"Evidence collected for {entity_tag}: {evidence_id}")

# Query evidence
evidence_entity = seg.get_entity(evidence_id)
print(f"Entity Tag: {evidence_entity.attributes['entity_tag']}")  # plix://room/meeting_room
print(f"Postconditions satisfied: {evidence_entity.attributes['postconditions_satisfied']}")
```

This example demonstrates collecting intent evidence and storing it in SEG.

**Example 4: Intent Lineage Queries**

```python
# Query: What intents led to this outcome for this entity?
entity_tag = "plix://room/meeting_room"

outcome_entity_id = seg.add_entity(Entity(
    type="outcome",
    name="Room Reserved",
    attributes={
        "room_reserved": True,
        "entity_tag": entity_tag  # Entity tag
    }
))

intents = query_intent_lineage(outcome_entity_id, entity_tag, seg)
print(f"Intents that achieved this outcome for {entity_tag}: {len(intents)}")
for intent in intents:
    print(f"  - {intent.attributes['intent']}")

# Query: What outcomes did this intent achieve for this entity?
intent_entity_id = store_plix_contract_as_entity(contract, seg)
outcomes = query_outcome_lineage(intent_entity_id, entity_tag, seg)
print(f"Outcomes achieved by this intent for {entity_tag}: {len(outcomes)}")
```

This example demonstrates intent lineage queries, tracing outcomes to intents and intents to outcomes.

**Implementation Benefits**

Implementation examples demonstrate:

- **Entity Creation:** Storing PLIx contracts as SEG entities
- **Relation Creation:** Creating intent-outcome relations
- **Evidence Collection:** Collecting and storing intent evidence
- **Lineage Queries:** Querying intent lineage for reasoning

These examples show how SEG transforms from execution-focused evidence to intent-aware evidence, enabling intent-driven reasoning and learning.

---

## Chapter 47 Summary

SEG transforms from evidence chains to intent lineage through PLIx integration. Before PLIx, SEG stores evidence chains but lacks intent awareness. After PLIx, SEG stores intent lineage **with tag-based entity references**, tracks intent evolution **for specific entities via tags**, maps intent-outcome relationships **with tag-based entity filtering**, and enables intent-driven reasoning **using entity tags**.

**Tags enable canonical identity** throughout SEG integration: intent entities include entity tags (`plix://room/meeting_room`), intent lineage tracks evolution by entity tags, intent-outcome relations include entity tags for filtering, and evidence collection includes entity tags for entity-based queries. Tags enable unambiguous entity references that survive technology changes, enabling intent-aware evidence with canonical identity.

This transformation enables intent-driven verification, learning, and reasoning, making SEG a foundation for intent-aware systems. Tags provide the identity foundation that makes this transformation possible.

**Next:** Part IV Integration complete. Part V explores implementation—CNL compiler, runtime, adapters, and testing, showing how tags enable implementation.

---

**Word Count:** ~2,800 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)  
**Cross-References:**
> - **AIM-OS Foundations:** Chapter 9 (Evidence Graph - SEG)
> - **PLIx Architecture:** Chapter 40 (The Four Pillars)
> - **PLIx Integration:** Chapter 44 (CMC Integration)
> - **PLIx Integration:** Chapter 45 (VIF Integration)
> - **PLIx Integration:** Chapter 46 (APOE Integration)
> - **Tag System:** Chapter 5 (Tag System)

