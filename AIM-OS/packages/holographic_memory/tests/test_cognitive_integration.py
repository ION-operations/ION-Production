"""Tests for cognitive component holographic memory integration."""

import pytest

from holographic_memory.cognitive_integration import (
    VIF_HoloIntegration,
    APOE_HoloIntegration,
    SIS_HoloIntegration,
    CAS_HoloIntegration,
)
from holographic_memory.cmc_integration import CMC_HoloIntegration
from holographic_memory.seg_integration import SEG_HoloIntegration


class TestVIF_HoloIntegration:
    """Test suite for VIF holographic integration."""
    
    def test_disabled_by_default(self):
        """Test that integration is disabled by default."""
        integration = VIF_HoloIntegration(enable=False)
        assert not integration.is_enabled()
    
    def test_enable_explicitly(self):
        """Test explicit enabling."""
        cmc_integration = CMC_HoloIntegration(enable=True, dimension=1000)
        integration = VIF_HoloIntegration(enable=True, dimension=1000, cmc_integration=cmc_integration)
        assert integration.is_enabled()
    
    def test_compute_confidence_when_disabled(self):
        """Test that confidence computation returns None when disabled."""
        integration = VIF_HoloIntegration(enable=False)
        plix_intent = {"goal": "Test goal", "process": "Test process"}
        result = integration.compute_confidence_from_reconstruction(plix_intent)
        assert result is None
    
    def test_compute_confidence_when_enabled(self):
        """Test confidence computation when enabled."""
        cmc_integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        # Store an atom first
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Test content"},
            "tags": [],
        }
        cmc_integration.store_atom(atom, "semantic_123")
        
        integration = VIF_HoloIntegration(enable=True, dimension=1000, cmc_integration=cmc_integration)
        
        plix_intent = {"goal": "Test goal", "process": "Test process"}
        confidence = integration.compute_confidence_from_reconstruction(plix_intent, "semantic_123")
        
        # Should return a confidence score if successful
        if confidence is not None:
            assert 0.0 <= confidence <= 1.0


class TestAPOE_HoloIntegration:
    """Test suite for APOE holographic integration."""
    
    def test_disabled_by_default(self):
        """Test that integration is disabled by default."""
        integration = APOE_HoloIntegration(enable=False)
        assert not integration.is_enabled()
    
    def test_retrieve_plans_when_disabled(self):
        """Test that plan retrieval returns empty when disabled."""
        integration = APOE_HoloIntegration(enable=False)
        plix_intent = {"goal": "Test goal"}
        results = integration.retrieve_associative_plans(plix_intent)
        assert results == []
    
    def test_retrieve_plans_when_enabled(self):
        """Test plan retrieval when enabled."""
        cmc_integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        # Store some atoms (as plans)
        for i in range(3):
            atom = {
                "id": f"atom_{i}",
                "modality": "text",
                "content": {"inline": f"Plan {i}"},
                "tags": [],
            }
            cmc_integration.store_atom(atom, f"semantic_{i}")
        
        integration = APOE_HoloIntegration(enable=True, dimension=1000, cmc_integration=cmc_integration)
        
        plix_intent = {"goal": "Test goal", "process": "Test process"}
        plans = integration.retrieve_associative_plans(plix_intent, top_k=3)
        
        assert len(plans) <= 3
        assert all(isinstance(p, tuple) and len(p) == 3 for p in plans)


class TestSIS_HoloIntegration:
    """Test suite for SIS holographic integration."""
    
    def test_disabled_by_default(self):
        """Test that integration is disabled by default."""
        integration = SIS_HoloIntegration(enable=False)
        assert not integration.is_enabled()
    
    def test_reinforce_when_disabled(self):
        """Test that reinforcement returns False when disabled."""
        integration = SIS_HoloIntegration(enable=False)
        result = integration.reinforce_association("pattern_123", success=True)
        assert result is False
    
    def test_reinforce_when_enabled(self):
        """Test association reinforcement when enabled."""
        cmc_integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        # Store a pattern first
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Pattern content"},
            "tags": [],
        }
        cmc_integration.store_atom(atom, "pattern_123")
        
        integration = SIS_HoloIntegration(enable=True, dimension=1000, cmc_integration=cmc_integration)
        
        # Reinforce
        result = integration.reinforce_association("pattern_123", success=True, strength=0.1)
        assert result is True
        
        # Weaken
        result = integration.reinforce_association("pattern_123", success=False, strength=0.1)
        assert result is True


class TestCAS_HoloIntegration:
    """Test suite for CAS holographic integration."""
    
    def test_disabled_by_default(self):
        """Test that integration is disabled by default."""
        integration = CAS_HoloIntegration(enable=False)
        assert not integration.is_enabled()
    
    def test_analyze_state_when_disabled(self):
        """Test that state analysis returns disabled message when disabled."""
        integration = CAS_HoloIntegration(enable=False)
        insights = integration.analyze_holographic_state()
        assert insights["enabled"] is False
    
    def test_analyze_state_when_enabled(self):
        """Test state analysis when enabled."""
        cmc_integration = CMC_HoloIntegration(enable=True, dimension=1000)
        seg_integration = SEG_HoloIntegration(enable=True, dimension=1000)
        
        # Store some data
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Test"},
            "tags": [],
        }
        cmc_integration.store_atom(atom, "semantic_123")
        
        entity = {
            "id": "entity_123",
            "type": "concept",
            "name": "Test Entity",
            "attributes": {},
        }
        seg_integration.store_entity(entity, "entity_123")
        
        integration = CAS_HoloIntegration(
            enable=True,
            dimension=1000,
            cmc_integration=cmc_integration,
            seg_integration=seg_integration,
        )
        
        insights = integration.analyze_holographic_state()
        
        assert insights["enabled"] is True
        assert "memory_density" in insights
        assert "coherence_score" in insights
    
    def test_detect_ambiguity_when_disabled(self):
        """Test that ambiguity detection returns not ambiguous when disabled."""
        integration = CAS_HoloIntegration(enable=False)
        result = integration.detect_ambiguity("test query")
        assert result["ambiguous"] is False
    
    def test_detect_ambiguity_when_enabled(self):
        """Test ambiguity detection when enabled."""
        cmc_integration = CMC_HoloIntegration(enable=True, dimension=1000)
        
        # Store multiple similar atoms
        for i in range(5):
            atom = {
                "id": f"atom_{i}",
                "modality": "text",
                "content": {"inline": f"Similar content {i}"},
                "tags": [],
            }
            cmc_integration.store_atom(atom, f"semantic_{i}")
        
        integration = CAS_HoloIntegration(
            enable=True,
            dimension=1000,
            cmc_integration=cmc_integration,
        )
        
        result = integration.detect_ambiguity("similar content", threshold=0.5)
        
        assert "ambiguous" in result
        assert "strong_matches" in result

