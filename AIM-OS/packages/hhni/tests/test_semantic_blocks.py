"""Tests for semantic block organization."""

from __future__ import annotations

import pytest

from packages.hhni.models import HHNINode
from packages.hhni.semantic_blocks import (
    SemanticBlock,
    BlockType,
    create_block_id,
    validate_block,
    BlockRelationship,
)

try:
    from packages.seg.seg_graph import SEGraph
    from packages.hhni.semantic_block_organizer import SemanticBlockOrganizer
    BLOCK_ORGANIZER_AVAILABLE = True
except ImportError:
    try:
        from seg import SEGraph
        from hhni.semantic_block_organizer import SemanticBlockOrganizer
        BLOCK_ORGANIZER_AVAILABLE = True
    except ImportError:
        BLOCK_ORGANIZER_AVAILABLE = False
        pytest.skip("Semantic block organizer not available", allow_module_level=True)


def test_create_block_id():
    """Test block ID creation."""
    block_id = create_block_id("thematic", "atom_123", 0)
    assert block_id.startswith("block_")
    assert "thematic" in block_id
    assert "atom_123" in block_id


def test_validate_block_valid():
    """Test block validation with valid block."""
    block = SemanticBlock(
        id="block_123",
        block_type=BlockType.THEMATIC,
        content_ids=["node_1", "node_2"],
        centroid_embedding=[0.5, 0.3, 0.2],
    )
    
    assert validate_block(block) is True


def test_validate_block_invalid_type():
    """Test block validation with invalid type."""
    block = SemanticBlock(
        id="block_123",
        block_type="invalid_type",
        content_ids=["node_1"],
        centroid_embedding=[0.5, 0.3, 0.2],
    )
    
    assert validate_block(block) is False


def test_validate_block_empty_content():
    """Test block validation with empty content."""
    block = SemanticBlock(
        id="block_123",
        block_type=BlockType.THEMATIC,
        content_ids=[],
        centroid_embedding=[0.5, 0.3, 0.2],
    )
    
    assert validate_block(block) is False


def test_block_organizer_initialization():
    """Test that block organizer initializes correctly."""
    if not BLOCK_ORGANIZER_AVAILABLE:
        pytest.skip("Semantic block organizer not available")
    
    seg_graph = SEGraph()
    organizer = SemanticBlockOrganizer(
        seg_graph=seg_graph,
        cluster_threshold=0.80,
        max_block_size=10,
        min_block_size=2,
    )
    
    assert organizer.seg_graph == seg_graph
    assert organizer.cluster_threshold == 0.80
    assert organizer.max_block_size == 10
    assert organizer.min_block_size == 2


def test_organize_into_blocks_empty():
    """Test organizing empty node list."""
    if not BLOCK_ORGANIZER_AVAILABLE:
        pytest.skip("Semantic block organizer not available")
    
    seg_graph = SEGraph()
    organizer = SemanticBlockOrganizer(seg_graph=seg_graph)
    
    blocks = organizer.organize_into_blocks([], "atom_123")
    
    assert blocks == []


def test_organize_into_blocks_insufficient_nodes():
    """Test organizing with insufficient nodes."""
    if not BLOCK_ORGANIZER_AVAILABLE:
        pytest.skip("Semantic block organizer not available")
    
    seg_graph = SEGraph()
    organizer = SemanticBlockOrganizer(seg_graph=seg_graph, min_block_size=2)
    
    # Create single node
    node = HHNINode(
        id="node_1",
        level=4,
        path="doc.para.sent",
        content_hash="hash1",
        text="Test sentence",
    )
    
    blocks = organizer.organize_into_blocks([node], "atom_123")
    
    # Should return empty (not enough nodes)
    assert len(blocks) == 0


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    if not BLOCK_ORGANIZER_AVAILABLE:
        pytest.skip("Semantic block organizer not available")
    
    seg_graph = SEGraph()
    organizer = SemanticBlockOrganizer(seg_graph=seg_graph)
    
    # Test identical vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = organizer._cosine_similarity(vec1, vec2)
    assert similarity > 0.9  # Should be very similar
    
    # Test orthogonal vectors
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    similarity2 = organizer._cosine_similarity(vec3, vec4)
    assert similarity2 <= 0.5  # Orthogonal vectors yield 0.5 after 0-1 normalization


def test_block_relationship():
    """Test block relationship model."""
    relationship = BlockRelationship(
        source_block_id="block_1",
        target_block_id="block_2",
        relationship_type="semantic",
        similarity=0.85,
        confidence=0.90,
    )
    
    assert relationship.source_block_id == "block_1"
    assert relationship.target_block_id == "block_2"
    assert relationship.similarity == 0.85
    assert relationship.confidence == 0.90

