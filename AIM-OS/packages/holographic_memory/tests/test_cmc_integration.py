"""Tests for CMC holographic memory integration."""

import os
import pytest

import numpy as np

from holographic_memory.cmc_integration import CMC_HoloIntegration, ENABLE_HOLOGRAPHIC_MEMORY


class TestCMC_HoloIntegration:
    """Test suite for CMC holographic integration."""
    
    def test_disabled_by_default(self):
        """Test that integration is disabled by default."""
        # Temporarily disable if env var is set
        original = os.environ.get("ENABLE_HOLOGRAPHIC_MEMORY")
        if original:
            del os.environ["ENABLE_HOLOGRAPHIC_MEMORY"]
        
        try:
            integration = CMC_HoloIntegration(enable=False)
            assert not integration.is_enabled()
            assert integration.holo_memory is None
        finally:
            if original:
                os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = original
    
    def test_enable_explicitly(self):
        """Test explicit enabling."""
        integration = CMC_HoloIntegration(enable=True)
        assert integration.is_enabled()
        assert integration.holo_memory is not None
        assert integration.vectorizer is not None
    
    def test_store_atom_when_disabled(self):
        """Test that store_atom returns None when disabled."""
        integration = CMC_HoloIntegration(enable=False)
        
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Test content"},
            "tags": [],
        }
        
        result = integration.store_atom(atom, "semantic_123")
        assert result is None
    
    def test_store_atom_when_enabled(self):
        """Test storing atom when enabled."""
        integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Test content"},
            "tags": [{"key": "topic", "value": "test"}],
        }
        
        memory_id = integration.store_atom(atom, "semantic_123")
        
        assert memory_id is not None
        assert "semantic_123" in integration.semantic_id_registry
    
    def test_retrieve_exact_when_disabled(self):
        """Test that retrieve_exact returns None when disabled."""
        integration = CMC_HoloIntegration(enable=False)
        result = integration.retrieve_exact("semantic_123")
        assert result is None
    
    def test_retrieve_exact_when_enabled(self):
        """Test exact retrieval when enabled."""
        integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Test content"},
            "tags": [],
        }
        
        # Store first
        integration.store_atom(atom, "semantic_123")
        
        # Retrieve
        result = integration.retrieve_exact("semantic_123")
        
        assert result is not None
        reconstructed, fidelity = result
        assert reconstructed.shape == (1000,)
        assert 0.0 <= fidelity <= 1.0
    
    def test_retrieve_associative_when_disabled(self):
        """Test that associative retrieval returns empty when disabled."""
        integration = CMC_HoloIntegration(enable=False)
        results = integration.retrieve_associative("test query")
        assert results == []
    
    def test_retrieve_associative_when_enabled(self):
        """Test associative retrieval when enabled."""
        integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        # Store multiple atoms
        for i in range(5):
            atom = {
                "id": f"atom_{i}",
                "modality": "text",
                "content": {"inline": f"Content {i}"},
                "tags": [{"key": "topic", "value": f"topic_{i}"}],
            }
            integration.store_atom(atom, f"semantic_{i}")
        
        # Retrieve associatively
        results = integration.retrieve_associative("content", top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(r, tuple) and len(r) == 3 for r in results)
        assert all(isinstance(score, float) for _, score, _ in results)
    
    def test_get_stats_when_disabled(self):
        """Test stats when disabled."""
        integration = CMC_HoloIntegration(enable=False)
        stats = integration.get_stats()
        
        assert stats["enabled"] is False
        assert "message" in stats
    
    def test_get_stats_when_enabled(self):
        """Test stats when enabled."""
        integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        # Store some atoms
        for i in range(3):
            atom = {
                "id": f"atom_{i}",
                "modality": "text",
                "content": {"inline": f"Content {i}"},
                "tags": [],
            }
            integration.store_atom(atom, f"semantic_{i}")
        
        stats = integration.get_stats()
        
        assert stats["enabled"] is True
        assert stats["semantic_id_count"] == 3
        assert "holo_memory" in stats

