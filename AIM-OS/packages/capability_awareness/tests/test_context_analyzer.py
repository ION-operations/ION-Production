"""Tests for Context Analyzer component"""

import pytest
from datetime import datetime, timezone

from capability_awareness.context_analyzer import ContextAnalyzer
from capability_awareness.models import ContextAnalysis


class TestContextAnalyzer:
    """Test Context Analyzer functionality"""
    
    def test_analyze_context_basic(self):
        """Test basic context analysis"""
        analyzer = ContextAnalyzer()
        
        context_input = {
            "user_input": "I need to document a new system",
            "current_task": "documentation",
            "system_state": {"quality": "good"},
            "recent_activities": []
        }
        
        analysis = analyzer.analyze_context(context_input)
        
        assert analysis is not None
        assert isinstance(analysis, ContextAnalysis)
        assert analysis.confidence >= 0.0
        assert analysis.confidence <= 1.0
        assert isinstance(analysis.capability_hints, list)
    
    def test_analyze_situation(self):
        """Test situation analysis"""
        analyzer = ContextAnalyzer()
        
        situation = analyzer._analyze_situation(
            user_input="I need help",
            current_task="testing",
            agent_state="active"
        )
        
        assert situation is not None
        assert isinstance(situation, str)
        assert len(situation) > 0
    
    def test_analyze_user_intent(self):
        """Test user intent analysis"""
        analyzer = ContextAnalyzer()
        
        context_input = {
            "user_input": "I need documentation",
            "quality_expectations": "high"
        }
        
        user_intent = analyzer._analyze_user_intent(
            user_input="I need documentation",
            context_input=context_input
        )
        
        assert user_intent is not None
        assert isinstance(user_intent, str)
        assert len(user_intent) > 0
    
    def test_extract_capability_hints(self):
        """Test capability hints extraction"""
        analyzer = ContextAnalyzer()
        
        situation = "high complexity task"
        user_intent = "need documentation"
        system_state = {"quality": "good"}
        temporal_context = {"recent_patterns": []}
        
        hints = analyzer._extract_capability_hints(
            situation, user_intent, system_state, temporal_context
        )
        
        assert isinstance(hints, list)
        assert len(hints) >= 0
    
    def test_query_context_history(self):
        """Test context history querying"""
        analyzer = ContextAnalyzer()
        
        # Create some context analyses
        context_input1 = {
            "user_input": "test1",
            "current_task": "task1",
            "system_state": {},
            "recent_activities": []
        }
        context_input2 = {
            "user_input": "test2",
            "current_task": "task2",
            "system_state": {},
            "recent_activities": []
        }
        
        analysis1 = analyzer.analyze_context(context_input1)
        analysis2 = analyzer.analyze_context(context_input2)
        
        # Query history (access directly from analyzer)
        history = analyzer.analysis_history
        
        assert isinstance(history, list)
        assert len(history) >= 2
        assert analysis1 in history
        assert analysis2 in history

