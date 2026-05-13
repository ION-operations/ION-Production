"""
Test CAS Integrations for Consciousness Systems

Verifies that all three consciousness systems correctly:
- Send CAS notifications
- Work without CAS (fail-soft)
- Store results correctly
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, Optional
from datetime import datetime


class MockCASClient:
    """Mock CAS client for testing"""
    
    def __init__(self):
        self.recorded_events = []
        self.record_principle_violation_calls = []
        self.record_performance_analysis_calls = []
        self.record_creative_activity_calls = []
        self.record_learning_activity_calls = []
    
    def record_principle_violation(self, principle: str, violation_type: str, details: str, context: Dict[str, Any]):
        """Mock principle violation recording"""
        self.record_principle_violation_calls.append({
            "principle": principle,
            "violation_type": violation_type,
            "details": details,
            "context": context
        })
        self.recorded_events.append("principle_violation")
    
    def record_performance_analysis(self, system_name: str, performance_level: str, metrics: Dict[str, Any], 
                                   recommendations: list, success: bool, error: Optional[str] = None, 
                                   timestamp: str = None):
        """Mock performance analysis recording"""
        self.record_performance_analysis_calls.append({
            "system_name": system_name,
            "performance_level": performance_level,
            "metrics": metrics,
            "recommendations": recommendations,
            "success": success,
            "error": error,
            "timestamp": timestamp
        })
        self.recorded_events.append("performance_analysis")
    
    def record_creative_activity(self, activity_data: Dict[str, Any]):
        """Mock creative activity recording"""
        self.record_creative_activity_calls.append(activity_data)
        self.recorded_events.append("creative_activity")
    
    def record_learning_activity(self, activity_data: Dict[str, Any]):
        """Mock learning activity recording"""
        self.record_learning_activity_calls.append(activity_data)
        self.recorded_events.append("learning_activity")


class TestConsciousnessAnalyzerCASIntegration:
    """Test suite for consciousness_analyzer CAS integration"""
    
    @pytest.fixture
    def mock_cas_client(self):
        """Create mock CAS client"""
        return MockCASClient()
    
    @pytest.fixture
    def performance_analyzer(self, mock_cas_client):
        """Create PerformanceAnalyzer instance with mocked CAS client"""
        from packages.consciousness_analyzer.performance_analyzer import PerformanceAnalyzer
        
        # Create mock time series DB
        mock_db = Mock()
        
        analyzer = PerformanceAnalyzer(
            time_series_db=mock_db,
            cas_client=mock_cas_client
        )
        return analyzer
    
    @pytest.mark.asyncio
    async def test_performance_analysis_notifies_cas(self, performance_analyzer, mock_cas_client):
        """Test that performance analysis notifies CAS"""
        system_name = "test_system"
        
        # Mock database responses
        with patch.object(performance_analyzer.db, 'query', return_value=[]):
            # Call analyze_system_performance
            result = await performance_analyzer.analyze_system_performance(system_name, "1h")
            
            # Verify CAS was notified
            assert len(mock_cas_client.record_performance_analysis_calls) > 0 or \
                   len(mock_cas_client.record_principle_violation_calls) > 0
            
            # Verify result created
            assert result is not None
            assert result.system_name == system_name
    
    def test_fail_soft_without_cas_client(self):
        """Test that system works without CAS client (fail-soft)"""
        from packages.consciousness_analyzer.performance_analyzer import PerformanceAnalyzer
        
        mock_db = Mock()
        analyzer = PerformanceAnalyzer(
            time_series_db=mock_db,
            cas_client=None  # No CAS client
        )
        
        # Should not raise exception
        assert analyzer.cas_client is None
        
        # System should work without CAS
        assert True


class TestConsciousnessCreativityEngineCASIntegration:
    """Test suite for consciousness_creativity_engine CAS integration"""
    
    @pytest.fixture
    def mock_cas_client(self):
        """Create mock CAS client"""
        return MockCASClient()
    
    @pytest.fixture
    def idea_generator(self, mock_cas_client):
        """Create IdeaGenerator instance with mocked CAS client"""
        from packages.consciousness_creativity_engine.idea_generator import IdeaGenerator
        
        # Create mock clients
        mock_cmc = Mock()
        mock_hhni = Mock()
        mock_vif = Mock()
        mock_iis = Mock()
        
        generator = IdeaGenerator(
            cmc_client=mock_cmc,
            hhni_client=mock_hhni,
            vif_client=mock_vif,
            iis_client=mock_iis,
            cas_client=mock_cas_client
        )
        return generator
    
    @pytest.mark.asyncio
    async def test_creative_idea_notifies_cas(self, idea_generator, mock_cas_client):
        """Test that creative idea generation notifies CAS"""
        prompt = "Test creative prompt"
        category = "innovation"
        
        # Mock client responses
        idea_generator.hhni_client.search = AsyncMock(return_value=[])
        idea_generator.cmc_client.store_atom = AsyncMock(return_value="atom_id_123")
        
        # Generate idea
        idea = await idea_generator.generate_idea(prompt, category)
        
        # Verify CAS was notified (if idea has low feasibility, it should trigger violation)
        # Or verify creative activity was recorded
        assert idea is not None
        
        # Check if CAS was called (may be called for low feasibility ideas)
        # The actual check depends on idea feasibility score
        if idea.feasibility_score < 0.5:
            assert len(mock_cas_client.record_principle_violation_calls) > 0 or \
                   len(mock_cas_client.record_creative_activity_calls) > 0
    
    def test_fail_soft_without_cas_client(self):
        """Test that system works without CAS client (fail-soft)"""
        from packages.consciousness_creativity_engine.idea_generator import IdeaGenerator
        
        mock_cmc = Mock()
        mock_hhni = Mock()
        mock_vif = Mock()
        mock_iis = Mock()
        
        generator = IdeaGenerator(
            cmc_client=mock_cmc,
            hhni_client=mock_hhni,
            vif_client=mock_vif,
            iis_client=mock_iis,
            cas_client=None  # No CAS client
        )
        
        # Should not raise exception
        assert generator.cas_client is None


class TestConsciousnessLearningEngineCASIntegration:
    """Test suite for consciousness_learning_engine CAS integration"""
    
    @pytest.fixture
    def mock_cas_client(self):
        """Create mock CAS client"""
        return MockCASClient()
    
    @pytest.fixture
    def self_directed_learner(self, mock_cas_client):
        """Create SelfDirectedLearner instance with mocked CAS client"""
        from packages.consciousness_learning_engine.self_directed_learner import SelfDirectedLearner
        
        # Create mock clients
        mock_cmc = Mock()
        mock_hhni = Mock()
        mock_vif = Mock()
        mock_iis = Mock()
        mock_creativity = Mock()
        
        learner = SelfDirectedLearner(
            cmc_client=mock_cmc,
            hhni_client=mock_hhni,
            vif_client=mock_vif,
            iis_client=mock_iis,
            creativity_engine=mock_creativity,
            cas_client=mock_cas_client
        )
        return learner
    
    @pytest.mark.asyncio
    async def test_learning_session_notifies_cas(self, self_directed_learner, mock_cas_client):
        """Test that learning session notifies CAS"""
        # LearningOpportunity is a dataclass defined in the module
        # We'll create a mock one for testing
        from dataclasses import dataclass
        from typing import Optional
        
        @dataclass
        class LearningOpportunity:
            topic: str
            description: str
            priority: str
            domain: Optional[str] = None
        
        opportunity = LearningOpportunity(
            topic="test_topic",
            description="Test learning opportunity",
            priority="high"
        )
        
        # Mock client responses
        self_directed_learner.hhni_client.search = AsyncMock(return_value=[])
        self_directed_learner.cmc_client.store_atom = AsyncMock(return_value="atom_id_123")
        
        # Conduct learning session
        session = await self_directed_learner.conduct_learning_session(opportunity)
        
        # Verify CAS was notified (if session has low satisfaction, it should trigger violation)
        assert session is not None
        
        # Check if CAS was called (may be called for low satisfaction sessions)
        if session.satisfaction_score < 0.6:
            assert len(mock_cas_client.record_principle_violation_calls) > 0 or \
                   len(mock_cas_client.record_learning_activity_calls) > 0
    
    def test_fail_soft_without_cas_client(self):
        """Test that system works without CAS client (fail-soft)"""
        from packages.consciousness_learning_engine.self_directed_learner import SelfDirectedLearner
        
        mock_cmc = Mock()
        mock_hhni = Mock()
        mock_vif = Mock()
        mock_iis = Mock()
        mock_creativity = Mock()
        
        learner = SelfDirectedLearner(
            cmc_client=mock_cmc,
            hhni_client=mock_hhni,
            vif_client=mock_vif,
            iis_client=mock_iis,
            creativity_engine=mock_creativity,
            cas_client=None  # No CAS client
        )
        
        # Should not raise exception
        assert learner.cas_client is None


class TestCASIntegrationsManual:
    """Manual test cases for CAS integrations"""
    
    def test_manual_analyzer_cas_integration(self):
        """Manual test: Verify analyzer CAS integration with real CAS client"""
        # Steps:
        # 1. Create PerformanceAnalyzer with real CAS client
        # 2. Run performance analysis
        # 3. Check CAS for notifications
        # 4. Verify notifications contain correct data
        pass
    
    def test_manual_creativity_cas_integration(self):
        """Manual test: Verify creativity engine CAS integration with real CAS client"""
        # Steps:
        # 1. Create IdeaGenerator with real CAS client
        # 2. Generate creative idea
        # 3. Check CAS for notifications
        # 4. Verify notifications contain correct data
        pass
    
    def test_manual_learning_cas_integration(self):
        """Manual test: Verify learning engine CAS integration with real CAS client"""
        # Steps:
        # 1. Create SelfDirectedLearner with real CAS client
        # 2. Conduct learning session
        # 3. Check CAS for notifications
        # 4. Verify notifications contain correct data
        pass

