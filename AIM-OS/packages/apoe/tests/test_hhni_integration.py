"""Tests for APOE HHNI Integration

Tests Retriever role integration with HHNI for budget-aware context retrieval.
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch

from apoe import ACLParser, PlanExecutor, StepStatus, Budget, RoleType
from apoe.models import Step
from apoe.retriever_role import RetrieverRole
from apoe.role_dispatcher import RoleDispatcher


class TestHHNIIntegration:
    """Test HHNI integration functionality."""
    
    @pytest.fixture
    def mock_hierarchical_index(self):
        """Create mock HierarchicalIndex."""
        index = Mock()
        index.retrieve = Mock(return_value={
            "context": [
                {"content": "Test context 1", "relevance": 0.95},
                {"content": "Test context 2", "relevance": 0.90}
            ],
            "total_tokens": 1000,
            "relevance_scores": [0.95, 0.90],
            "modality": "code",
            "k": 2,
            "dvns_enabled": True
        })
        return index
    
    @patch('apoe.retriever_role.HHNI_AVAILABLE', True)
    def test_retriever_role_init_with_hhni(self, mock_hierarchical_index):
        """Test RetrieverRole initialization with HHNI."""
        retriever = RetrieverRole(hierarchical_index=mock_hierarchical_index)
        
        assert retriever.index == mock_hierarchical_index
        assert retriever.hhni_available is True
    
    def test_retriever_role_init_without_hhni(self):
        """Test RetrieverRole initialization without HHNI."""
        retriever = RetrieverRole(hierarchical_index=None)
        
        assert retriever.index is None
        assert retriever.hhni_available is False
    
    def test_retriever_role_execute_with_budget(self, mock_hierarchical_index):
        """Test RetrieverRole execution with budget constraints."""
        retriever = RetrieverRole(hierarchical_index=mock_hierarchical_index)
        
        budget = Budget(tokens_limit=2000, time_limit_seconds=10.0)
        
        inputs = {
            "query": "Test query",
            "k": 10,
            "modality": "code",
            "enable_dvns": True
        }
        
        result = retriever.execute(inputs=inputs, budget=budget)
        
        assert result is not None
        assert "context" in result
        assert "total_tokens" in result
        assert result["total_tokens"] <= budget.tokens_limit
    
    def test_retriever_role_multi_resolution_context(self, mock_hierarchical_index):
        """Test RetrieverRole multi-resolution context retrieval."""
        retriever = RetrieverRole(hierarchical_index=mock_hierarchical_index)
        
        budget = Budget(tokens_limit=5000, time_limit_seconds=30.0)
        
        inputs = {
            "query": "Test query",
            "k": 20,
            "modality": "code",
            "enable_dvns": True,
            "multi_resolution": True
        }
        
        result = retriever.execute(inputs=inputs, budget=budget)
        
        assert result is not None
        assert "context" in result
        assert len(result["context"]) > 0
    
    def test_role_dispatcher_dispatch_retriever(self, mock_hierarchical_index):
        """Test RoleDispatcher dispatching Retriever role with HHNI."""
        dispatcher = RoleDispatcher(enable_hhni=True)
        dispatcher.retriever_role = RetrieverRole(hierarchical_index=mock_hierarchical_index)
        
        step = Step(
            id="step_001",
            name="retrieve_context",
            role=RoleType.RETRIEVER,
            description="Retrieve context",
            budget=Budget(tokens_limit=2000, time_limit_seconds=10.0)
        )
        
        inputs = {
            "query": "Test query",
            "k": 10
        }
        
        result = dispatcher.dispatch_retriever(
            step=step,
            inputs=inputs,
            budget=step.budget
        )
        
        assert result is not None
        assert "context" in result
        assert "total_tokens" in result
    
    def test_retriever_role_budget_exceeded(self, mock_hierarchical_index):
        """Test RetrieverRole handling budget exceeded."""
        retriever = RetrieverRole(hierarchical_index=mock_hierarchical_index)
        
        budget = Budget(tokens_limit=2000, time_limit_seconds=10.0)
        
        inputs = {
            "query": "Test query",
            "k": 100
        }
        
        result = retriever.execute(inputs=inputs, budget=budget)
        
        # Should handle budget constraints (retriever should respect budget)
        assert result is not None
        assert "context" in result
        assert "total_tokens" in result
    
    def test_retriever_role_without_hhni_fallback(self):
        """Test RetrieverRole fallback when HHNI unavailable."""
        retriever = RetrieverRole(hierarchical_index=None)
        
        budget = Budget(tokens_limit=2000, time_limit_seconds=10.0)
        
        inputs = {
            "query": "Test query",
            "k": 10
        }
        
        result = retriever.execute(inputs=inputs, budget=budget)
        
        # Should return empty result or error when HHNI unavailable
        assert result is not None
        assert "error" in result or result.get("context") == []

