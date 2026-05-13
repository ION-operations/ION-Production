"""
Tests for VIF → SEG integration.

Tests the bidirectional integration between VIF witnesses and SEG entities/relations/evidence.
"""

import pytest
from seg.vif_integration import (
    create_vif_witness,
    attach_witness_to_entity,
    attach_witness_to_relation,
    attach_witness_to_evidence,
    get_witness_provenance,
)
from seg.models import Entity, Relation, Evidence, RelationType
from seg.seg_graph import SEGraph


def test_create_vif_witness_basic():
    """Test basic VIF witness creation expects ImportError when VIF missing."""
    entity = Entity(name="test_entity", type="test", confidence=0.9)

    # Expect ImportError when VIF is not available
    with pytest.raises(ImportError):
        _ = create_vif_witness(
            entity=entity,
            cmc_store=None,  # VIF not available → raises before use
            model_id="test_model",
            model_provider="test_provider",
            context_snapshot_id="snapshot_123",
        )


def test_attach_witness_to_entity():
    """Attach witness to entity without requiring VIF service."""
    graph = SEGraph()

    entity = Entity(name="test_entity", type="test", confidence=0.9)
    entity = graph.add_entity(entity)

    witness_id = "witness_test123"

    # Attach should not require VIF; verify update in graph
    attach_witness_to_entity(entity.id, witness_id, graph)
    assert graph.get_entity(entity.id).witness_id == witness_id


def test_attach_witness_to_relation():
    """Attach witness to relation without requiring VIF service."""
    graph = SEGraph()

    source_entity = graph.add_entity(Entity(name="source", type="test"))
    target_entity = graph.add_entity(Entity(name="target", type="test"))

    relation = Relation(
        source_id=source_entity.id,
        target_id=target_entity.id,
        relation_type=RelationType.RELATES_TO,
        confidence=0.9,
    )
    relation = graph.add_relation(relation)

    witness_id = "witness_test123"

    # Attach should not require VIF; verify update in graph
    attach_witness_to_relation(relation.id, witness_id, graph)
    assert graph.get_relation(relation.id).witness_id == witness_id


def test_attach_witness_to_evidence():
    """Attach witness to evidence without requiring VIF service."""
    graph = SEGraph()

    evidence = graph.add_evidence(
        Evidence(content="Test evidence", source="test.source", evidence_type="test", confidence=0.9)
    )

    witness_id = "witness_test123"

    # Attach should not require VIF; verify update in graph
    attach_witness_to_evidence(evidence.id, witness_id, graph)
    assert graph.get_evidence(evidence.id).witness_id == witness_id


def test_get_witness_provenance():
    """get_witness_provenance should raise ImportError when VIF missing."""
    graph = SEGraph()
    entity = graph.add_entity(Entity(name="e1", type="test"))

    with pytest.raises(ImportError):
        _ = get_witness_provenance(entity.id, cmc_store=None, graph=graph)


def test_vif_integration_with_graph():
    """Basic sanity: entities can be added and retrieved; not VIF-dependent."""
    graph = SEGraph()

    entity = Entity(name="test_entity", type="test", confidence=0.9)
    entity = graph.add_entity(entity)

    # Verify entity is in graph
    stored_entity = graph.get_entity(entity.id)
    assert stored_entity is not None
    assert stored_entity.name == "test_entity"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

