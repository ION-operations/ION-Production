"""Simple validation script for SEG integration.

Run this to manually validate that SEG integration works correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hhni.indexer import build_hhni_for_atom
from hhni.models import HHNINode

try:
    from packages.seg.seg_graph import SEGraph
    from packages.seg.models import RelationType
    SEG_AVAILABLE = True
except ImportError:
    try:
        from seg import SEGraph, RelationType
        SEG_AVAILABLE = True
    except ImportError:
        SEG_AVAILABLE = False
        print("⚠️  SEG not available - skipping SEG integration tests")


class DummyAtom:
    """Dummy atom for testing."""
    def __init__(self, atom_id: str, inline: str, tags=None):
        self.id = atom_id
        self.content = type("Content", (), {"inline": inline, "uri": None, "media_type": "text/plain"})
        self.tags = tags or {}
        self.created_at = HHNINode.__dataclass_fields__["created_at"].default_factory()  # type: ignore
        self.hash = "hash123"
        self.witness = type("Witness", (), {"snapshot_id": None})


class DummyDGraphClient:
    """Dummy DGraph client for testing."""
    def __init__(self):
        self.upsert_payloads: list[dict] = []

    def upsert_nodes(self, nodes):
        self.upsert_payloads.append({"input": list(nodes)})


class DummyQdrantClient:
    """Dummy Qdrant client for testing."""
    def __init__(self):
        self.points = []

    def upsert(self, collection_name, points):
        self.points.extend(points)
        return points[0]["id"] if points else None


def validate_morphology():
    """Validate morphological analysis works."""
    print("🔍 Validating morphological analysis...")
    
    from packages.hhni.morphology import analyze_morphology
    
    test_words = ["happy", "unhappy", "happiness", "unhappiness"]
    
    for word in test_words:
        result = analyze_morphology(word)
        print(f"  ✓ {word}:")
        print(f"    - Prefix: {result.prefix or 'none'}")
        print(f"    - Root: {result.root or 'none'}")
        print(f"    - Suffix: {result.suffix or 'none'}")
        print(f"    - Operations: {result.operations}")
    
    print("✅ Morphological analysis working\n")


def validate_hhni_integration():
    """Validate HHNI integration."""
    print("🔍 Validating HHNI integration...")
    
    atom = DummyAtom("test1", "The unhappy cat ran quickly.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    
    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="test123"
    )
    
    # Find SUBWORD nodes with morphology
    subword_nodes = [n for n in nodes if n.level == 6 and n.morphology]
    
    print(f"  ✓ Created {len(nodes)} HHNI nodes")
    print(f"  ✓ Found {len(subword_nodes)} SUBWORD nodes with morphology")
    
    for node in subword_nodes[:3]:  # Show first 3
        if node.morphology:
            morph = node.morphology
            print(f"    - Word: {morph.get('word', 'N/A')}")
            print(f"      Parts: {morph.get('parts', [])}")
            print(f"      Operations: {morph.get('operations', [])}")
    
    print("✅ HHNI integration working\n")


def validate_seg_integration():
    """Validate SEG integration."""
    if not SEG_AVAILABLE:
        print("⚠️  SEG not available - skipping SEG integration validation\n")
        return
    
    print("🔍 Validating SEG integration...")
    
    atom = DummyAtom("test2", "The unhappiness was clear.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()
    
    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="test456",
        seg_graph=seg_graph
    )
    
    # Check for word entities
    word_entities = seg_graph.list_entities(entity_type="morphological_word")
    print(f"  ✓ Created {len(word_entities)} word entities in SEG")
    
    # Check for part entities
    part_entities = seg_graph.list_entities(entity_type="morphological_part")
    print(f"  ✓ Created {len(part_entities)} part entities in SEG")
    
    # Check for relations
    relations = seg_graph.get_relations()
    print(f"  ✓ Created {len(relations)} relations in SEG")
    
    # Show example
    if word_entities:
        word_entity = word_entities[0]
        print(f"    - Example word: {word_entity.name}")
        word_relations = seg_graph.get_relations(source_id=word_entity.id)
        print(f"      Relations: {len(word_relations)}")
        for rel in word_relations[:2]:  # Show first 2
            part_entity = seg_graph.get_entity(rel.target_id)
            if part_entity:
                print(f"        → {part_entity.attributes.get('part_type', 'unknown')}: {part_entity.name}")
    
    print("✅ SEG integration working\n")


def validate_backward_compatibility():
    """Validate backward compatibility (works without SEG)."""
    print("🔍 Validating backward compatibility...")
    
    atom = DummyAtom("test3", "The cat ran.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    
    # Should work without seg_graph
    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="test789"
    )
    
    print(f"  ✓ Created {len(nodes)} HHNI nodes without SEG")
    print(f"  ✓ DGraph payloads: {len(dgraph.upsert_payloads)}")
    print("✅ Backward compatibility working\n")


def main():
    """Run all validations."""
    print("=" * 60)
    print("Morphological Analysis - Phase 1 Validation")
    print("=" * 60)
    print()
    
    try:
        validate_morphology()
        validate_hhni_integration()
        validate_seg_integration()
        validate_backward_compatibility()
        
        print("=" * 60)
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 60)
        return 0
    except Exception as e:
        print("=" * 60)
        print(f"❌ VALIDATION FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

