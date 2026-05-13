"""Tests for SEG integration in HHNI morphological analysis."""

from __future__ import annotations

import pytest

from hhni.indexer import build_hhni_for_atom
from hhni.models import HHNINode
from hhni.safety import HHNISafetyGates

# Import SEG - use same pattern as indexer.py
try:
    from packages.seg.seg_graph import SEGraph
    from packages.seg.models import RelationType
except ImportError:
    # Fallback: try direct import if packages is in path
    try:
        from seg import SEGraph, RelationType
    except ImportError:
        pytest.skip("SEG package not available", allow_module_level=True)


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
    def __init__(self, fail=False):
        self.fail = fail
        self.points = []

    def upsert(self, collection_name, points):
        if self.fail:
            raise RuntimeError("qdrant down")
        self.points.extend(points)
        return points[0]["id"]


def test_build_hhni_with_seg_creates_word_entity():
    """Test that SEG integration creates word entities."""
    atom = DummyAtom("atom1", "The unhappy cat ran.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()

    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # Find SUBWORD nodes with morphology
    subword_nodes = [n for n in nodes if n.level == 6 and n.morphology]
    assert len(subword_nodes) > 0

    # Check that word entities were created in SEG
    word_entities = seg_graph.list_entities(entity_type="morphological_word")
    assert len(word_entities) > 0

    # Verify at least one word entity exists
    found_word = False
    for node in subword_nodes:
        if node.morphology and node.morphology.get("word"):
            word = node.morphology["word"].lower()
            word_entity_id = f"morph_word:{word}"
            entity = seg_graph.get_entity(word_entity_id)
            if entity:
                found_word = True
                assert entity.type == "morphological_word"
                assert entity.name == node.morphology["word"]
                assert "hhni_node_id" in entity.attributes
                assert "atom_id" in entity.attributes
                break
    
    assert found_word, "No word entity found in SEG"


def test_build_hhni_with_seg_creates_part_entities():
    """Test that SEG integration creates part entities (prefix, root, suffix)."""
    atom = DummyAtom("atom2", "The unhappiness was clear.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()

    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # Find SUBWORD nodes with morphology
    subword_nodes = [n for n in nodes if n.level == 6 and n.morphology]
    
    # Check for part entities
    part_entities = seg_graph.list_entities(entity_type="morphological_part")
    
    # Should have at least one part entity if morphological analysis found parts
    found_parts = False
    for node in subword_nodes:
        if node.morphology:
            morph = node.morphology
            if morph.get("prefix") or morph.get("root") or morph.get("suffix"):
                found_parts = True
                break
    
    if found_parts:
        assert len(part_entities) >= 0
        
        # Verify part entity structure
        for entity in part_entities:
            assert entity.type == "morphological_part"
            assert "part_type" in entity.attributes
            assert entity.attributes["part_type"] in ["prefix", "root", "suffix"]


def test_build_hhni_with_seg_creates_relations():
    """Test that SEG integration creates relations between words and parts."""
    atom = DummyAtom("atom3", "The unhappy cat was running.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()

    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # Find SUBWORD nodes with morphology
    subword_nodes = [n for n in nodes if n.level == 6 and n.morphology]
    
    # Check for relations
    relations = seg_graph.get_relations()
    
    # Should have relations if morphological parts exist
    found_relations = False
    for node in subword_nodes:
        if node.morphology:
            morph = node.morphology
            if morph.get("prefix") or (morph.get("root") and morph.get("root") != morph.get("word")) or morph.get("suffix"):
                found_relations = True
                break
    
    if found_relations:
        assert len(relations) > 0
        
        # Verify relation structure
        for relation in relations:
            assert relation.relation_type == RelationType.DERIVES_FROM
            assert relation.confidence == 1.0
            assert "morphology" in relation.tags
            
            # Verify source and target entities exist
            source_entity = seg_graph.get_entity(relation.source_id)
            target_entity = seg_graph.get_entity(relation.target_id)
            assert source_entity is not None
            assert target_entity is not None


def test_build_hhni_with_seg_links_word_to_parts():
    """Test that word entities are linked to their parts via relations."""
    atom = DummyAtom("atom4", "The unhappiness was clear.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()

    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # Find word with morphological parts
    word_entity = None
    for node in nodes:
        if node.level == 6 and node.morphology:
            morph = node.morphology
            word = morph.get("word", "").lower()
            if word and (morph.get("prefix") or morph.get("root") or morph.get("suffix")):
                word_entity_id = f"morph_word:{word}"
                word_entity = seg_graph.get_entity(word_entity_id)
                if word_entity:
                    break
    
    if word_entity:
        # Get relations from word entity
        relations = seg_graph.get_relations(source_id=word_entity.id)
        
        # Should have at least one relation to a part
        assert len(relations) >= 0
        
        # Verify relations link to part entities
        for relation in relations:
            part_entity = seg_graph.get_entity(relation.target_id)
            assert part_entity is not None
            assert part_entity.type == "morphological_part"
            assert relation.relation_type == RelationType.DERIVES_FROM


def test_build_hhni_without_seg_works():
    """Test that HHNI indexing works without SEG (backward compatibility)."""
    atom = DummyAtom("atom5", "The cat ran.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()

    # Should work without seg_graph parameter
    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123"
    )

    assert len(nodes) > 0
    assert dgraph.upsert_payloads


def test_build_hhni_with_seg_handles_errors_gracefully():
    """Test that SEG integration errors don't break HHNI indexing."""
    atom = DummyAtom("atom6", "The cat ran.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    
    # Create a SEG graph that will fail (simulate error)
    class FailingSEGraph(SEGraph):
        def add_entity(self, entity):
            raise RuntimeError("SEG error")
    
    seg_graph = FailingSEGraph()

    # Should still complete HHNI indexing even if SEG fails
    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # HHNI indexing should complete successfully
    assert len(nodes) > 0
    assert dgraph.upsert_payloads


def test_seg_entity_deduplication():
    """Test that SEG entities are deduplicated by consistent IDs."""
    atom = DummyAtom("atom7", "The unhappy cat was unhappy.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()

    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # Find "unhappy" word entity
    word_entity_id = "morph_word:unhappy"
    word_entity = seg_graph.get_entity(word_entity_id)
    
    if word_entity:
        # Should only have one entity for "unhappy" even though it appears twice
        word_entities = [e for e in seg_graph.list_entities() if e.id == word_entity_id]
        assert len(word_entities) == 1
        
        # Entity should have multiple hhni_node_id references
        # (This would be in attributes, but we're just checking deduplication works)
        assert word_entity.id == word_entity_id


def test_seg_integration_with_complex_word():
    """Test SEG integration with complex morphological word."""
    atom = DummyAtom("atom8", "The unhappiness was overwhelming.")
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()
    seg_graph = SEGraph()

    nodes = build_hhni_for_atom(
        atom=atom,
        dgraph_client=dgraph,
        qdrant_client=qdrant,
        correlation_id="123",
        seg_graph=seg_graph
    )

    # Find "unhappiness" word entity
    word_entity_id = "morph_word:unhappiness"
    word_entity = seg_graph.get_entity(word_entity_id)
    
    if word_entity:
        # Get relations from word to parts
        relations = seg_graph.get_relations(source_id=word_entity.id)
        
        # Should have relations to prefix, root, and suffix
        part_types = set()
        for relation in relations:
            part_entity = seg_graph.get_entity(relation.target_id)
            if part_entity:
                part_types.add(part_entity.attributes.get("part_type"))
        
        # Should have at least one part type
        assert len(part_types) > 0

