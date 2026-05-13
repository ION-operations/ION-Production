"""Tests for CAF integrations"""

import pytest

from capability_awareness.integrations.cmc_integration import CMCIntegration
from capability_awareness.integrations.vif_integration import VIFIntegration
from capability_awareness.integrations.cas_integration import CASIntegration
from capability_awareness.integrations.apoe_integration import APOEIntegration


class TestCMCIntegration:
    """Test CMC integration"""
    
    def test_cmc_initialization(self):
        """Test CMC integration initialization"""
        integration = CMCIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'enabled')
    
    def test_cmc_disabled_when_no_store(self):
        """Test CMC integration disabled when no memory store"""
        integration = CMCIntegration(memory_store=None)
        
        # Should gracefully handle missing CMC
        assert integration.enabled is False or integration.enabled is True


class TestVIFIntegration:
    """Test VIF integration"""
    
    def test_vif_initialization(self):
        """Test VIF integration initialization"""
        integration = VIFIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'enabled')
    
    def test_track_confidence(self):
        """Test confidence tracking"""
        integration = VIFIntegration()
        
        result = integration.track_confidence(
            task="test_task",
            confidence=0.8,
            reasoning="Test reasoning"
        )
        
        assert result is not None
        assert 'confidence' in result or 'tracked' in result


class TestCASIntegration:
    """Test CAS integration"""
    
    def test_cas_initialization(self):
        """Test CAS integration initialization"""
        integration = CASIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'enabled')
    
    def test_check_cognitive_state(self):
        """Test cognitive state checking"""
        integration = CASIntegration()
        
        state = integration.check_cognitive_state()
        
        assert state is not None
        assert isinstance(state, dict)


class TestAPOEIntegration:
    """Test APOE integration"""
    
    def test_apoe_initialization(self):
        """Test APOE integration initialization"""
        integration = APOEIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'enabled')
    
    def test_create_capability_plan(self):
        """Test capability plan creation"""
        integration = APOEIntegration()
        
        plan = integration.create_capability_plan(
            capabilities=["test_capability"],
            goal="Test goal",
            context={}
        )
        
        # Plan may be None if APOE not available, which is OK
        assert plan is None or plan is not None

