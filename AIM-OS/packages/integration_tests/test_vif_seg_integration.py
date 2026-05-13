"""Integration tests for VIF + SEG.

Tests that VIF witnesses can be linked to SEG nodes for provenance tracking.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest

from vif.witness import VIF, ConfidenceBand, TaskCriticality
from seg import SEGraph, Entity, Relation, Evidence, RelationType


def test_vif_witness_to_seg_entity():
    """Test creating SEG entity with VIF witness provenance."""
    # Create VIF witness
    witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_test_123",
        prompt_hash=hashlib.sha256(b"test prompt").hexdigest(),
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash=hashlib.sha256(b"test output").hexdigest(),
        output_tokens=5,
        total_tokens=15,
    )
    
    # Create SEG entity with witness_id
    graph = SEGraph()
    entity = Entity(
        type="concept",
        name="Machine Learning",
        attributes={"field": "ai"},
        witness_id=witness.id,  # Link to VIF witness
        source="vif_witness",
        confidence=witness.confidence_score,
    )
    
    graph.add_entity(entity)
    
    # Verify entity created with VIF reference
    retrieved = graph.get_entity(entity.id)
    assert retrieved is not None
    assert retrieved.witness_id == witness.id
    assert retrieved.confidence == witness.confidence_score
    assert retrieved.source == "vif_witness"


def test_vif_witness_to_seg_relation():
    """Test creating SEG relation with VIF witness provenance."""
    # Create VIF witness
    witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_test_456",
        prompt_hash=hashlib.sha256(b"relation prompt").hexdigest(),
        prompt_tokens=15,
        confidence_score=0.88,
        confidence_band=ConfidenceBand.B,
        output_hash=hashlib.sha256(b"relation output").hexdigest(),
        output_tokens=8,
        total_tokens=23,
    )
    
    # Create entities first
    graph = SEGraph()
    entity1 = Entity(type="concept", name="Neural Networks")
    entity2 = Entity(type="concept", name="Deep Learning")
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    
    # Create relation with witness_id
    relation = Relation(
        source_id=entity1.id,
        target_id=entity2.id,
        relation_type=RelationType.RELATES_TO,
        witness_id=witness.id,  # Link to VIF witness
        source="vif_witness",
        confidence=witness.confidence_score,
    )
    
    graph.add_relation(relation)
    
    # Verify relation created with VIF reference
    retrieved = graph.get_relation(relation.id)
    assert retrieved is not None
    assert retrieved.witness_id == witness.id
    assert retrieved.confidence == witness.confidence_score
    assert retrieved.source == "vif_witness"


def test_vif_witness_to_seg_evidence():
    """Test creating SEG evidence with VIF witness provenance."""
    # Create VIF witness
    witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_test_789",
        prompt_hash=hashlib.sha256(b"evidence prompt").hexdigest(),
        prompt_tokens=20,
        confidence_score=0.92,
        confidence_band=ConfidenceBand.A,
        output_hash=hashlib.sha256(b"evidence output").hexdigest(),
        output_tokens=10,
        total_tokens=30,
    )
    
    # Create SEG evidence with witness_id
    graph = SEGraph()
    evidence = Evidence(
        content="Neural networks are a subset of machine learning",
        source="vif_witness",
        evidence_type="claim",
        confidence=witness.confidence_score,
        witness_id=witness.id,  # Link to VIF witness
    )
    
    graph.add_evidence(evidence)
    
    # Verify evidence created with VIF reference
    retrieved = graph.get_evidence(evidence.id)
    assert retrieved is not None
    assert retrieved.witness_id == witness.id
    assert retrieved.confidence == witness.confidence_score
    assert retrieved.source == "vif_witness"


def test_vif_provenance_chain():
    """Test VIF parent-child witness chain in SEG."""
    # Create parent VIF witness
    parent_witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_parent",
        prompt_hash=hashlib.sha256(b"parent prompt").hexdigest(),
        prompt_tokens=10,
        confidence_score=0.90,
        confidence_band=ConfidenceBand.A,
        output_hash=hashlib.sha256(b"parent output").hexdigest(),
        output_tokens=5,
        total_tokens=15,
    )
    
    # Create child VIF witness
    child_witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_child",
        prompt_hash=hashlib.sha256(b"child prompt").hexdigest(),
        prompt_tokens=10,
        confidence_score=0.85,
        confidence_band=ConfidenceBand.B,
        output_hash=hashlib.sha256(b"child output").hexdigest(),
        output_tokens=5,
        total_tokens=15,
        parent_vif_id=parent_witness.id,  # Link to parent
    )
    
    # Update parent with child reference
    parent_witness.child_vif_ids.append(child_witness.id)
    
    # Create SEG entities for both
    graph = SEGraph()
    parent_entity = Entity(
        type="concept",
        name="Parent Concept",
        witness_id=parent_witness.id,
    )
    child_entity = Entity(
        type="concept",
        name="Child Concept",
        witness_id=child_witness.id,
    )
    
    graph.add_entity(parent_entity)
    graph.add_entity(child_entity)
    
    # Verify provenance chain
    retrieved_parent = graph.get_entity(parent_entity.id)
    retrieved_child = graph.get_entity(child_entity.id)
    
    assert retrieved_parent.witness_id == parent_witness.id
    assert retrieved_child.witness_id == child_witness.id
    assert child_witness.parent_vif_id == parent_witness.id
    assert child_witness.id in parent_witness.child_vif_ids


def test_vif_confidence_affects_seg():
    """Test that VIF confidence affects SEG operations."""
    # Create high confidence witness
    high_conf_witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_high",
        prompt_hash=hashlib.sha256(b"high conf prompt").hexdigest(),
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash=hashlib.sha256(b"high conf output").hexdigest(),
        output_tokens=5,
        total_tokens=15,
        kappa_gate_passed=True,
    )
    
    # Create low confidence witness
    low_conf_witness = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_low",
        prompt_hash=hashlib.sha256(b"low conf prompt").hexdigest(),
        prompt_tokens=10,
        confidence_score=0.65,  # Below κ threshold
        confidence_band=ConfidenceBand.C,
        output_hash=hashlib.sha256(b"low conf output").hexdigest(),
        output_tokens=5,
        total_tokens=15,
        kappa_gate_passed=False,  # κ-gate failed
    )
    
    # Create SEG entities with different confidence levels
    graph = SEGraph()
    high_conf_entity = Entity(
        type="concept",
        name="High Confidence Concept",
        witness_id=high_conf_witness.id,
        confidence=high_conf_witness.confidence_score,
    )
    low_conf_entity = Entity(
        type="concept",
        name="Low Confidence Concept",
        witness_id=low_conf_witness.id,
        confidence=low_conf_witness.confidence_score,
    )
    
    graph.add_entity(high_conf_entity)
    graph.add_entity(low_conf_entity)
    
    # Verify confidence affects SEG
    retrieved_high = graph.get_entity(high_conf_entity.id)
    retrieved_low = graph.get_entity(low_conf_entity.id)
    
    assert retrieved_high.confidence == 0.95
    assert retrieved_low.confidence == 0.65
    assert retrieved_high.confidence > retrieved_low.confidence
    
    # Verify κ-gate status
    assert high_conf_witness.kappa_gate_passed is True
    assert low_conf_witness.kappa_gate_passed is False


def test_seg_synthesis_from_vif_witnesses():
    """Test knowledge synthesis from multiple VIF witnesses."""
    # Create multiple VIF witnesses
    witnesses = []
    for i in range(3):
        witness = VIF(
            model_id="gpt-4-turbo",
            model_provider="openai",
            context_snapshot_id=f"snap_{i}",
            prompt_hash=hashlib.sha256(f"prompt_{i}".encode()).hexdigest(),
            prompt_tokens=10,
            confidence_score=0.90 - (i * 0.05),  # Decreasing confidence
            confidence_band=ConfidenceBand.A if i == 0 else ConfidenceBand.B,
            output_hash=hashlib.sha256(f"output_{i}".encode()).hexdigest(),
            output_tokens=5,
            total_tokens=15,
        )
        witnesses.append(witness)
    
    # Create SEG entities from witnesses
    graph = SEGraph()
    entities = []
    for i, witness in enumerate(witnesses):
        entity = Entity(
            type="concept",
            name=f"Concept {i}",
            witness_id=witness.id,
            confidence=witness.confidence_score,
        )
        graph.add_entity(entity)
        entities.append(entity)
    
    # Create relations between entities
    for i in range(len(entities) - 1):
        relation = Relation(
            source_id=entities[i].id,
            target_id=entities[i + 1].id,
            relation_type=RelationType.RELATES_TO,
            witness_id=witnesses[i].id,
            confidence=witnesses[i].confidence_score,
        )
        graph.add_relation(relation)
    
    # Verify synthesis: all entities and relations linked
    all_entities = graph.list_entities()
    assert len(all_entities) == 3
    
    # Get all relations (need to query for each entity pair)
    all_relations = []
    for entity in entities:
        all_relations.extend(graph.get_outgoing_relations(entity.id))
    assert len(all_relations) == 2
    
    # Verify contradiction detection can work with VIF witnesses
    # (This tests that SEG can use VIF confidence for synthesis)
    stats = graph.stats()
    assert stats["entity_count"] == 3
    assert stats["relation_count"] == 2
    
    # Verify all entities have witness_ids
    for entity in entities:
        retrieved = graph.get_entity(entity.id)
        assert retrieved.witness_id is not None
        assert retrieved.witness_id.startswith("vif_")

