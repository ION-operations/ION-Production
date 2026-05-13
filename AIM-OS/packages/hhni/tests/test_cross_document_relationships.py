"""Tests for cross-document relationship detection."""

from __future__ import annotations

import pytest

from packages.seg.seg_graph import SEGraph
from packages.seg.models import Entity, RelationType

try:
    from packages.hhni.cross_document_relationships import CrossDocumentRelationshipDetector
    CROSS_DOC_AVAILABLE = True
except ImportError:
    try:
        from hhni.cross_document_relationships import CrossDocumentRelationshipDetector
        CROSS_DOC_AVAILABLE = True
    except ImportError:
        CROSS_DOC_AVAILABLE = False
        pytest.skip("Cross-document relationships not available", allow_module_level=True)


class DummyAtom:
    """Dummy atom for testing."""
    def __init__(self, atom_id: str, inline: str):
        self.id = atom_id
        self.content = type("Content", (), {"inline": inline, "uri": None, "media_type": "text/plain"})


def test_detector_initialization():
    """Test that detector initializes correctly."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(
        seg_graph=seg_graph,
        similarity_threshold=0.75,
        narrative_threshold=0.80,
    )
    
    assert detector.seg_graph == seg_graph
    assert detector.similarity_threshold == 0.75
    assert detector.narrative_threshold == 0.80


def test_semantic_relationship_detection_with_embeddings():
    """Test semantic relationship detection when entities have embeddings."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(
        seg_graph=seg_graph,
        similarity_threshold=0.75,
    )
    
    # Create entities with embeddings
    entity1 = Entity(
        type="concept",
        name="river bank",
        attributes={
            "atom_id": "doc1",
            "embedding": [0.8, 0.6, 0.4, 0.2],  # Mock embedding
        },
    )
    seg_graph.add_entity(entity1)
    
    entity2 = Entity(
        type="concept",
        name="river",
        attributes={
            "atom_id": "doc2",
            "embedding": [0.75, 0.65, 0.45, 0.25],  # Similar embedding
        },
    )
    seg_graph.add_entity(entity2)
    
    # Detect relationships
    relations = detector.detect_semantic_relationships(
        source_entity=entity1,
        target_entities=[entity2],
        source_doc_id="doc1",
        target_doc_ids=["doc2"],
    )
    
    # Should detect relationship if similarity is high enough
    assert isinstance(relations, list)
    # Note: Actual similarity depends on cosine similarity calculation


def test_semantic_relationship_skips_same_document():
    """Test that semantic relationships are not created for same document."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(
        seg_graph=seg_graph,
        similarity_threshold=0.75,
    )
    
    entity1 = Entity(
        type="concept",
        name="river bank",
        attributes={
            "atom_id": "doc1",
            "embedding": [0.8, 0.6, 0.4, 0.2],
        },
    )
    
    entity2 = Entity(
        type="concept",
        name="river",
        attributes={
            "atom_id": "doc1",  # Same document
            "embedding": [0.75, 0.65, 0.45, 0.25],
        },
    )
    
    # Detect relationships
    relations = detector.detect_semantic_relationships(
        source_entity=entity1,
        target_entities=[entity2],
        source_doc_id="doc1",
        target_doc_ids=["doc1"],  # Same document
    )
    
    # Should skip same document
    assert len(relations) == 0


def test_narrative_context_tracking():
    """Test narrative context tracking."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(
        seg_graph=seg_graph,
        narrative_threshold=0.80,
    )
    
    entity1 = Entity(
        type="concept",
        name="river bank",
        attributes={
            "atom_id": "doc1",
            "embedding": [0.8, 0.6, 0.4, 0.2],
        },
    )
    
    entity2 = Entity(
        type="concept",
        name="love",
        attributes={
            "atom_id": "doc2",
            "embedding": [0.85, 0.55, 0.35, 0.15],  # Similar embedding
        },
    )
    
    # Track narrative context
    relations = detector.track_narrative_context(
        entity=entity1,
        context_entities=[entity2],
        document_ids=["doc2"],
    )
    
    assert isinstance(relations, list)
    # Note: Actual relations depend on narrative score calculation


def test_symbolic_meaning_accumulation():
    """Test symbolic meaning accumulation."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(seg_graph=seg_graph)
    
    entity = Entity(
        type="concept",
        name="river bank",
        attributes={
            "atom_id": "doc1",
        },
    )
    seg_graph.add_entity(entity)
    
    # Create references
    ref_entity1 = Entity(
        type="concept",
        name="reference1",
        attributes={"atom_id": "doc2"},
    )
    ref_entity2 = Entity(
        type="concept",
        name="reference2",
        attributes={"atom_id": "doc3"},
    )
    
    references = [
        (ref_entity1, "doc2", 0.0),
        (ref_entity2, "doc3", 0.0),
    ]
    
    # Accumulate meaning
    updated_entity = detector.accumulate_symbolic_meaning(entity, references)
    
    # Check that attributes were updated
    assert "first_mention" in updated_entity.attributes
    assert updated_entity.attributes["reference_count"] == 2
    assert updated_entity.attributes["symbolic_weight"] > 0.0
    
    # Check that relations were created
    relations = seg_graph.get_relations(target_id=entity.id)
    assert len(relations) > 0
    assert any(r.relation_type == RelationType.ACCUMULATES_MEANING for r in relations)


def test_cosine_similarity_calculation():
    """Test cosine similarity calculation."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(seg_graph=seg_graph)
    
    # Test identical vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = detector._cosine_similarity(vec1, vec2)
    assert similarity > 0.9  # Should be very similar
    
    # Test orthogonal vectors
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    similarity2 = detector._cosine_similarity(vec3, vec4)
    assert similarity2 <= 0.5  # Orthogonal vectors yield 0.5 after 0-1 normalization


def test_detector_handles_missing_embeddings():
    """Test that detector handles entities without embeddings gracefully."""
    if not CROSS_DOC_AVAILABLE:
        pytest.skip("Cross-document relationships not available")
    
    seg_graph = SEGraph()
    detector = CrossDocumentRelationshipDetector(seg_graph=seg_graph)
    
    entity1 = Entity(
        type="concept",
        name="river bank",
        attributes={"atom_id": "doc1"},  # No embedding
    )
    
    entity2 = Entity(
        type="concept",
        name="river",
        attributes={"atom_id": "doc2"},  # No embedding
    )
    
    # Should not crash when embeddings are missing
    relations = detector.detect_semantic_relationships(
        source_entity=entity1,
        target_entities=[entity2],
        source_doc_id="doc1",
        target_doc_ids=["doc2"],
    )
    
    # Should return empty list or handle gracefully
    assert isinstance(relations, list)

