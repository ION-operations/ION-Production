"""
Tests for Activation Mechanisms
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.activation_mechanisms import ActivationMechanisms
from specialist_system.specialist_registry import Specialist
from specialist_system.relevance_calculator import Work, RelevanceScore
from specialist_system.activation_system import ActivationResult


class TestActivationMechanisms:
    """Tests for ActivationMechanisms class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mechanisms = ActivationMechanisms()
        
        # Create test specialist
        self.specialist = Specialist(
            id='ui-specialist',
            name='UI Specialist',
            domain=['UI', 'UX', 'Design'],
            description='UI specialist',
            connections={
                'systems': ['React', 'Vue'],
                'data': ['design-tokens'],
                'patterns': ['component-patterns']
            }
        )
        
        # Create test work
        self.work = Work(
            description='Design a button component',
            domain=['UI', 'Design'],
            systems=['React'],
            data=['design-tokens'],
            patterns=['component-patterns'],
            complexity=0.7
        )
        
        # Create test relevance score
        self.high_relevance = RelevanceScore(
            overall=0.95,
            domain_match=1.0,
            data_connections=1.0,
            system_connections=1.0,
            pattern_recognition=1.0,
            complexity=0.7,
            factors={}
        )
        
        self.medium_relevance = RelevanceScore(
            overall=0.75,
            domain_match=0.8,
            data_connections=0.7,
            system_connections=0.8,
            pattern_recognition=0.6,
            complexity=0.7,
            factors={}
        )
        
        self.low_relevance = RelevanceScore(
            overall=0.65,
            domain_match=0.6,
            data_connections=0.5,
            system_connections=0.6,
            pattern_recognition=0.5,
            complexity=0.5,
            factors={}
        )
    
    def test_show_consultation_warning(self):
        """Test consultation warning mechanism."""
        result = self.mechanisms.show_consultation_warning(
            self.work,
            self.specialist,
            self.low_relevance
        )
        
        assert result['type'] == 'consultation'
        assert result['level'] == 1
        assert 'UI Specialist' in result['message']
        assert result['specialist_id'] == 'ui-specialist'
        assert result['action'] == 'suggest_consultation'
        assert result['relevance'] == 0.65
    
    def test_activate_specialist(self):
        """Test activation mechanism."""
        result = self.mechanisms.activate_specialist(
            self.work,
            self.specialist,
            self.medium_relevance
        )
        
        assert result['type'] == 'activation'
        assert result['level'] == 2
        assert 'Activating' in result['message']
        assert result['specialist_id'] == 'ui-specialist'
        assert result['action'] == 'activate'
        assert result['relevance'] == 0.75
    
    def test_assign_ownership(self):
        """Test ownership assignment mechanism."""
        result = self.mechanisms.assign_ownership(
            self.work,
            self.specialist,
            self.high_relevance
        )
        
        assert result['type'] == 'ownership'
        assert result['level'] == 3
        assert 'taking ownership' in result['message']
        assert result['specialist_id'] == 'ui-specialist'
        assert result['action'] == 'take_ownership'
        assert result['relevance'] == 0.95
    
    def test_handle_activation_result_ownership(self):
        """Test handling activation result with ownership."""
        activation_result = ActivationResult()
        activation_result.ownership = [self.specialist]
        activation_result.scores = {
            'ui-specialist': self.high_relevance
        }
        
        mechanisms = self.mechanisms.handle_activation_result(
            self.work,
            activation_result
        )
        
        assert len(mechanisms) == 1
        assert mechanisms[0]['type'] == 'ownership'
        assert mechanisms[0]['level'] == 3
    
    def test_handle_activation_result_activation(self):
        """Test handling activation result with activation."""
        activation_result = ActivationResult()
        activation_result.activation = [self.specialist]
        activation_result.scores = {
            'ui-specialist': self.medium_relevance
        }
        
        mechanisms = self.mechanisms.handle_activation_result(
            self.work,
            activation_result
        )
        
        assert len(mechanisms) == 1
        assert mechanisms[0]['type'] == 'activation'
        assert mechanisms[0]['level'] == 2
    
    def test_handle_activation_result_consultation(self):
        """Test handling activation result with consultation."""
        activation_result = ActivationResult()
        activation_result.consultation = [self.specialist]
        activation_result.scores = {
            'ui-specialist': self.low_relevance
        }
        
        mechanisms = self.mechanisms.handle_activation_result(
            self.work,
            activation_result
        )
        
        assert len(mechanisms) == 1
        assert mechanisms[0]['type'] == 'consultation'
        assert mechanisms[0]['level'] == 1
    
    def test_handle_activation_result_multiple(self):
        """Test handling activation result with multiple levels."""
        # Create multiple specialists
        specialist2 = Specialist(
            id='lex',
            name='Lex',
            domain=['Language'],
            description='Language specialist'
        )
        
        activation_result = ActivationResult()
        activation_result.ownership = [self.specialist]
        activation_result.activation = [specialist2]
        activation_result.scores = {
            'ui-specialist': self.high_relevance,
            'lex': self.medium_relevance
        }
        
        mechanisms = self.mechanisms.handle_activation_result(
            self.work,
            activation_result
        )
        
        assert len(mechanisms) == 2
        # Should be sorted by level (highest first)
        assert mechanisms[0]['level'] == 3  # Ownership
        assert mechanisms[1]['level'] == 2  # Activation
    
    def test_get_primary_activation(self):
        """Test getting primary activation."""
        # Mechanisms can be in any order - method should find highest
        mechanisms = [
            {'type': 'consultation', 'level': 1},
            {'type': 'activation', 'level': 2},
            {'type': 'ownership', 'level': 3}  # Highest priority (should be returned)
        ]
        
        primary = self.mechanisms.get_primary_activation(mechanisms)
        
        assert primary is not None
        assert primary['level'] == 3  # Highest priority
        assert primary['type'] == 'ownership'
    
    def test_get_primary_activation_empty(self):
        """Test getting primary activation from empty list."""
        primary = self.mechanisms.get_primary_activation([])
        
        assert primary is None
    
    def test_format_activation_summary(self):
        """Test formatting activation summary."""
        mechanisms = [
            {
                'type': 'ownership',
                'level': 3,
                'specialist_name': 'UI Specialist'
            },
            {
                'type': 'activation',
                'level': 2,
                'specialist_name': 'Lex'
            },
            {
                'type': 'consultation',
                'level': 1,
                'specialist_name': 'Codex'
            }
        ]
        
        summary = self.mechanisms.format_activation_summary(mechanisms)
        
        assert 'Ownership: UI Specialist' in summary
        assert 'Activated: Lex' in summary
        assert 'Consultation: Codex' in summary
    
    def test_format_activation_summary_empty(self):
        """Test formatting empty activation summary."""
        summary = self.mechanisms.format_activation_summary([])
        
        assert summary == "No specialist activation needed."

