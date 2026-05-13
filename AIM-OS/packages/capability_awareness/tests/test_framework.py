"""Tests for main CAF framework"""

import pytest

from capability_awareness.framework import CapabilityAwarenessFramework
from capability_awareness.models import CapabilityMetadata


class TestCapabilityAwarenessFramework:
    """Test main CAF framework"""
    
    def test_framework_initialization(self):
        """Test framework initialization"""
        caf = CapabilityAwarenessFramework()
        
        assert caf is not None
        assert caf.context_analyzer is not None
        assert caf.trigger_detector is not None
        assert caf.decision_tree_engine is not None
        assert caf.capability_activation is not None
        assert caf.performance_tracker is not None
        assert caf.capability_manager is not None
    
    def test_recognize_and_activate(self):
        """Test complete recognition and activation flow"""
        caf = CapabilityAwarenessFramework()
        
        context_input = {
            "user_input": "I need to document a system",
            "current_task": "documentation",
            "system_state": {},
            "recent_activities": []
        }
        
        result = caf.recognize_and_activate(context_input)
        
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'capability')
    
    def test_list_capabilities(self):
        """Test capability listing"""
        caf = CapabilityAwarenessFramework()
        
        capabilities = caf.list_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
    
    def test_search_capabilities(self):
        """Test capability search"""
        caf = CapabilityAwarenessFramework()
        
        results = caf.search_capabilities("documentation")
        
        assert isinstance(results, list)
    
    def test_register_capability(self):
        """Test capability registration"""
        caf = CapabilityAwarenessFramework()
        
        metadata = CapabilityMetadata(
            capability_id="test_capability",
            capability_type="test",
            description="Test capability"
        )
        
        caf.register_capability(metadata)
        
        capability = caf.capability_manager.get_capability("test_capability")
        assert capability is not None
        assert capability.capability_id == "test_capability"

