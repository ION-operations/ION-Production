# SEG Holographic Memory Integration Guide

**Status:** Experimental/Additive Enhancement  
**Version:** 0.1.0

## Overview

This guide explains how to use the experimental holographic memory integration with SEG. This is an **optional, additive enhancement** that works alongside (not replacing) primary SEG storage.

## Configuration

### Enable Holographic Memory

Set environment variable:
```bash
export ENABLE_HOLOGRAPHIC_MEMORY=true
```

Or in Python:
```python
import os
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"
```

**Default:** Disabled (`false`) - core SEG works unchanged

## Usage

### Basic Integration

```python
from holographic_memory.seg_integration import SEG_HoloIntegration

# Initialize integration
integration = SEG_HoloIntegration()

# Check if enabled
if integration.is_enabled():
    # Store entity (called AFTER primary SEG storage)
    entity = {
        "id": "entity_123",
        "type": "concept",
        "name": "Machine Learning",
        "attributes": {"field": "ai"}
    }
    memory_id = integration.store_entity(entity, "entity_123")
    
    # Store relationship (entities must be stored first)
    relationship = {
        "source_id": "entity_123",
        "target_id": "entity_456",
        "relation_type": "relates_to",
        "confidence": 0.95
    }
    rel_memory_id = integration.store_relationship(
        relationship, "entity_123", "entity_456"
    )
    
    # Infer relationship (find target from source + type)
    suggestions = integration.infer_relationship("entity_123", "relates_to")
    for target_id, correlation, fidelity in suggestions:
        print(f"Found target: {target_id} (correlation: {correlation:.3f})")
    
    # Find similar entities
    similar = integration.find_similar_entities(entity, top_k=5)
    for entity_id, correlation, fidelity in similar:
        print(f"Similar: {entity_id} (correlation: {correlation:.3f})")
```

### Integration with SEG Graph

```python
from seg import SEGraph, Entity, Relation, RelationType
from holographic_memory.seg_integration import SEG_HoloIntegration

# Initialize SEG (primary storage)
seg = SEGraph()

# Initialize holographic integration (experimental)
holo_integration = SEG_HoloIntegration()

# Create entity in SEG (primary)
entity = Entity(
    type="concept",
    name="Neural Networks",
    attributes={"field": "ai"}
)
entity = seg.add_entity(entity)

# Additionally store in holographic memory (if enabled)
if holo_integration.is_enabled():
    entity_dict = entity.model_dump()
    holo_integration.store_entity(entity_dict, entity.id)

# Create relationship in SEG (primary)
relation = Relation(
    source_id=entity.id,
    target_id=target_entity.id,
    relation_type=RelationType.RELATES_TO,
    confidence=0.95
)
relation = seg.add_relation(relation)

# Additionally store in holographic memory (if enabled)
if holo_integration.is_enabled():
    relation_dict = relation.model_dump()
    holo_integration.store_relationship(
        relation_dict, relation.source_id, relation.target_id
    )
```

### Relationship Inference Pattern

```python
# Primary relationship lookup from SEG
relations = seg.get_relations(source_id="entity_123", relation_type=RelationType.RELATES_TO)

# Additional associative inference (if enabled)
if holo_integration.is_enabled():
    # Infer target entities from source + relationship type
    suggestions = holo_integration.infer_relationship("entity_123", "relates_to")
    
    # Combine results
    results = {
        "primary": relations,  # From SEG
        "holographic_suggestions": suggestions,  # From holographic memory
        "source": "seg+holo" if suggestions else "seg"
    }
```

## Key Features

### 1. Relationship Inference

Infer target entities from source entity + relationship type:
```python
# Given: entity_123 and "relates_to" relationship type
# Find: What entities does entity_123 relate to?
targets = integration.infer_relationship("entity_123", "relates_to")
```

### 2. Similar Entity Search

Find entities similar to a given entity:
```python
query_entity = {
    "type": "concept",
    "name": "Deep Learning",
    "attributes": {"field": "ai"}
}
similar = integration.find_similar_entities(query_entity, top_k=10)
```

### 3. Composite Relationship Storage

Relationships stored as bound composite: `(Entity_A) * (Relationship) * (Entity_B)`
- Enables relationship inference
- Preserves graph structure in holographic encoding
- Allows pattern matching

## Key Points

1. **Non-Breaking:** Primary SEG operations unchanged
2. **Opt-In:** Must be explicitly enabled
3. **Additive:** Provides additional capabilities, not replacements
4. **Graceful Degradation:** Errors don't affect primary SEG
5. **Experimental:** Can be disabled/removed without impact
6. **Order Matters:** Entities must be stored before relationships

## Statistics

```python
stats = holo_integration.get_stats()
print(stats)
# {
#     "enabled": True,
#     "entity_count": 42,
#     "relationship_count": 15,
#     "holo_memory": {
#         "dimension": 10000,
#         "memory_count": 57,
#         ...
#     }
# }
```

## Error Handling

All holographic operations are wrapped in try/except:
- Errors are logged but don't affect primary SEG
- Failed holographic storage → SEG storage still succeeds
- Failed holographic inference → SEG queries still work

## Future Enhancements

- Better entity-to-memory_id mapping for similarity search
- Graph pattern matching via complex query vectors
- Integration with HHNI for improved retrieval
- Performance optimizations

---

**Remember:** This is experimental. Core SEG continues working normally when disabled.

