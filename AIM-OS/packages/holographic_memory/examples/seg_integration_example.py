"""SEG integration example for holographic memory.

Demonstrates using holographic memory with SEG as an experimental enhancement.
"""

import os

# Enable holographic memory
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"

from holographic_memory import SEG_HoloIntegration
from seg import SEGraph, Entity, Relation, RelationType


def main():
    """Demonstrate SEG holographic integration."""
    
    print("=== SEG Holographic Memory Integration ===\n")
    
    # Initialize SEG (primary storage)
    print("1. Initializing SEG (primary storage)...")
    seg = SEGraph()
    print("   SEG initialized\n")
    
    # Initialize holographic integration (experimental)
    print("2. Initializing holographic integration...")
    holo = SEG_HoloIntegration(dimension=1000)  # Smaller for demo
    print(f"   Holographic memory enabled: {holo.is_enabled()}\n")
    
    if not holo.is_enabled():
        print("   ⚠️  Holographic memory is disabled. Set ENABLE_HOLOGRAPHIC_MEMORY=true")
        return
    
    # Create entities in SEG (primary)
    print("3. Creating entities in SEG...")
    entities = []
    for name in ["Machine Learning", "Deep Learning", "Neural Networks"]:
        entity = Entity(
            type="concept",
            name=name,
            attributes={"field": "ai"}
        )
        entity = seg.add_entity(entity)
        entities.append(entity)
        print(f"   Created entity: {entity.name} ({entity.id[:12]}...)")
    
    print()
    
    # Store entities in holographic memory (experimental)
    print("4. Storing entities in holographic memory (experimental)...")
    for entity in entities:
        entity_dict = entity.model_dump()
        holo_id = holo.store_entity(entity_dict, entity.id)
        if holo_id:
            print(f"   Stored {entity.name} in holographic memory: {holo_id[:8]}...")
    
    print()
    
    # Create relationships in SEG (primary)
    print("5. Creating relationships in SEG...")
    relation1 = Relation(
        source_id=entities[0].id,  # Machine Learning
        target_id=entities[1].id,  # Deep Learning
        relation_type=RelationType.RELATES_TO,
        confidence=0.95
    )
    relation1 = seg.add_relation(relation1)
    print(f"   Created relation: {entities[0].name} -> {entities[1].name}")
    
    relation2 = Relation(
        source_id=entities[1].id,  # Deep Learning
        target_id=entities[2].id,  # Neural Networks
        relation_type=RelationType.RELATES_TO,
        confidence=0.90
    )
    relation2 = seg.add_relation(relation2)
    print(f"   Created relation: {entities[1].name} -> {entities[2].name}")
    
    print()
    
    # Store relationships in holographic memory (experimental)
    print("6. Storing relationships in holographic memory (experimental)...")
    for relation in [relation1, relation2]:
        relation_dict = relation.model_dump()
        holo_id = holo.store_relationship(
            relation_dict, relation.source_id, relation.target_id
        )
        if holo_id:
            print(f"   Stored relationship in holographic memory: {holo_id[:8]}...")
    
    print()
    
    # Relationship inference
    print("7. Relationship inference (experimental)...")
    targets = holo.infer_relationship(entities[0].id, "relates_to")
    print(f"   Inferred {len(targets)} target entities for '{entities[0].name}':")
    for target_id, correlation, fidelity in targets:
        # Find entity name
        target_entity = next((e for e in entities if e.id == target_id), None)
        name = target_entity.name if target_entity else target_id[:12]
        print(f"     {name} (correlation: {correlation:.3f}, fidelity: {fidelity:.3f})")
    
    print()
    
    # Similar entity search
    print("8. Similar entity search (experimental)...")
    query_entity = {
        "type": "concept",
        "name": "Artificial Intelligence",
        "attributes": {"field": "ai"}
    }
    similar = holo.find_similar_entities(query_entity, top_k=3)
    print(f"   Found {len(similar)} similar entities:")
    for entity_id, correlation, fidelity in similar:
        print(f"     {entity_id} (correlation: {correlation:.3f}, fidelity: {fidelity:.3f})")
    
    print()
    
    # Statistics
    print("9. Integration statistics...")
    stats = holo.get_stats()
    print(f"   Enabled: {stats['enabled']}")
    if stats['enabled']:
        print(f"   Entity count: {stats['entity_count']}")
        print(f"   Relationship count: {stats['relationship_count']}")
        holo_stats = stats.get('holo_memory', {})
        print(f"   Holographic memory count: {holo_stats.get('memory_count', 0)}")
    
    print("\n=== Demo Complete ===")
    print("\nNote: Primary SEG storage succeeded regardless of holographic results.")


if __name__ == "__main__":
    main()

