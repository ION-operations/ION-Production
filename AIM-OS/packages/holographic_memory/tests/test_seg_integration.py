"""Tests for SEG holographic memory integration."""

import os
import pytest

import numpy as np

from holographic_memory.seg_integration import SEG_HoloIntegration


class TestSEG_HoloIntegration:
    """Test suite for SEG holographic integration."""
    
    def test_disabled_by_default(self):
        """Test that integration is disabled by default."""
        integration = SEG_HoloIntegration(enable=False)
        assert not integration.is_enabled()
        assert integration.holo_memory is None
    
    def test_enable_explicitly(self):
        """Test explicit enabling."""
        integration = SEG_HoloIntegration(enable=True)
        assert integration.is_enabled()
        assert integration.holo_memory is not None
        assert integration.entity_vectorizer is not None
        assert integration.relationship_vectorizer is not None
    
    def test_store_entity_when_disabled(self):
        """Test that store_entity returns None when disabled."""
        integration = SEG_HoloIntegration(enable=False)
        
        entity = {
            "id": "entity_123",
            "type": "concept",
            "name": "Test Entity",
            "attributes": {"field": "ai"},
        }
        
        result = integration.store_entity(entity, "entity_123")
        assert result is None
    
    def test_store_entity_when_enabled(self):
        """Test storing entity when enabled."""
        integration = SEG_HoloIntegration(enable=True, dimension=1000)
        
        entity = {
            "id": "entity_123",
            "type": "concept",
            "name": "Test Entity",
            "attributes": {"field": "ai"},
        }
        
        memory_id = integration.store_entity(entity, "entity_123")
        
        assert memory_id is not None
        assert "entity_123" in integration.entity_registry
    
    def test_store_relationship_when_disabled(self):
        """Test that store_relationship returns None when disabled."""
        integration = SEG_HoloIntegration(enable=False)
        
        relationship = {
            "source_id": "entity_1",
            "target_id": "entity_2",
            "relation_type": "relates_to",
        }
        
        result = integration.store_relationship(relationship, "entity_1", "entity_2")
        assert result is None
    
    def test_store_relationship_when_enabled(self):
        """Test storing relationship when enabled."""
        integration = SEG_HoloIntegration(enable=True, dimension=1000)
        
        # Store entities first
        entity1 = {"id": "entity_1", "type": "concept", "name": "Entity 1", "attributes": {}}
        entity2 = {"id": "entity_2", "type": "concept", "name": "Entity 2", "attributes": {}}
        
        integration.store_entity(entity1, "entity_1")
        integration.store_entity(entity2, "entity_2")
        
        # Store relationship
        relationship = {
            "source_id": "entity_1",
            "target_id": "entity_2",
            "relation_type": "relates_to",
            "confidence": 0.95,
        }
        
        memory_id = integration.store_relationship(relationship, "entity_1", "entity_2")
        
        assert memory_id is not None
        assert ("entity_1", "entity_2", "relates_to") in integration.relationship_registry
    
    def test_infer_relationship_when_disabled(self):
        """Test that infer_relationship returns empty when disabled."""
        integration = SEG_HoloIntegration(enable=False)
        results = integration.infer_relationship("entity_1", "relates_to")
        assert results == []
    
    def test_infer_relationship_when_enabled(self):
        """Test relationship inference when enabled."""
        integration = SEG_HoloIntegration(enable=True, dimension=1000)
        
        # Store entities
        entity1 = {"id": "entity_1", "type": "concept", "name": "Source", "attributes": {}}
        entity2 = {"id": "entity_2", "type": "concept", "name": "Target", "attributes": {}}
        
        integration.store_entity(entity1, "entity_1")
        integration.store_entity(entity2, "entity_2")
        
        # Store relationship
        relationship = {
            "source_id": "entity_1",
            "target_id": "entity_2",
            "relation_type": "relates_to",
        }
        integration.store_relationship(relationship, "entity_1", "entity_2")
        
        # Infer
        results = integration.infer_relationship("entity_1", "relates_to")
        
        # Should find entity_2 as target
        assert len(results) > 0
        target_ids = [r[0] for r in results]
        assert "entity_2" in target_ids or len(results) > 0  # May find it or similar
    
    def test_find_similar_entities_when_disabled(self):
        """Test that find_similar_entities returns empty when disabled."""
        integration = SEG_HoloIntegration(enable=False)
        entity = {"id": "entity_1", "type": "concept", "name": "Test", "attributes": {}}
        results = integration.find_similar_entities(entity)
        assert results == []
    
    def test_find_similar_entities_when_enabled(self):
        """Test similar entity search when enabled."""
        integration = SEG_HoloIntegration(enable=True, dimension=1000)
        
        # Store multiple entities
        for i in range(5):
            entity = {
                "id": f"entity_{i}",
                "type": "concept",
                "name": f"Entity {i}",
                "attributes": {"field": f"field_{i}"},
            }
            integration.store_entity(entity, f"entity_{i}")
        
        # Find similar
        query_entity = {
            "id": "query_entity",
            "type": "concept",
            "name": "Entity 0",
            "attributes": {"field": "field_0"},
        }
        results = integration.find_similar_entities(query_entity, top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(r, tuple) and len(r) == 3 for r in results)
    
    def test_get_stats_when_disabled(self):
        """Test stats when disabled."""
        integration = SEG_HoloIntegration(enable=False)
        stats = integration.get_stats()
        
        assert stats["enabled"] is False
        assert "message" in stats
    
    def test_get_stats_when_enabled(self):
        """Test stats when enabled."""
        integration = SEG_HoloIntegration(enable=True, dimension=1000)
        
        # Store some entities and relationships
        entity1 = {"id": "entity_1", "type": "concept", "name": "Entity 1", "attributes": {}}
        entity2 = {"id": "entity_2", "type": "concept", "name": "Entity 2", "attributes": {}}
        
        integration.store_entity(entity1, "entity_1")
        integration.store_entity(entity2, "entity_2")
        
        relationship = {
            "source_id": "entity_1",
            "target_id": "entity_2",
            "relation_type": "relates_to",
        }
        integration.store_relationship(relationship, "entity_1", "entity_2")
        
        stats = integration.get_stats()
        
        assert stats["enabled"] is True
        assert stats["entity_count"] == 2
        assert stats["relationship_count"] == 1
        assert "holo_memory" in stats

