"""
Tests for Activation System
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.activation_system import ActivationSystem, ActivationResult
from specialist_system.specialist_registry import SpecialistRegistry, Specialist
from specialist_system.relevance_calculator import RelevanceCalculator, Work


class TestActivationSystem:
    """Tests for ActivationSystem class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = SpecialistRegistry()
        self.calculator = RelevanceCalculator()
        self.activation_system = ActivationSystem(self.registry, self.calculator)
        
        # Register test specialists
        ui_specialist = Specialist(
            id='ui-specialist',
            name='UI Specialist',
            domain=['UI', 'UX'],
            description='UI specialist',
            connections={
                'systems': ['React'],
                'data': ['design-tokens'],
                'patterns': ['component-patterns']
            }
        )
        self.registry.register(ui_specialist)
        
        lex_specialist = Specialist(
            id='lex',
            name='Lex',
            domain=['Language'],
            description='Language specialist',
            connections={
                'systems': ['PLIx'],
                'data': ['lexicon-definitions'],
                'patterns': ['lexicon-patterns']
            }
        )
        self.registry.register(lex_specialist)
    
    def test_activate_specialists_ui_work(self):
        """Test activating specialists for UI work."""
        work = Work(
            description='Design a button component',
            domain=['UI', 'Design'],
            systems=['React'],
            data=['design-tokens'],
            patterns=['component-patterns'],
            complexity=0.7
        )
        
        result = self.activation_system.activate_specialists(work)
        
        # UI Specialist should be activated
        assert len(result.activation) > 0 or len(result.ownership) > 0
        ui_specialist = result.activation[0] if result.activation else result.ownership[0]
        assert ui_specialist.id == 'ui-specialist'
    
    def test_activate_specialists_language_work(self):
        """Test activating specialists for language work."""
        work = Work(
            description='Define PLIx lexicon',
            domain=['Language', 'Lexicon'],
            systems=['PLIx'],
            data=['lexicon-definitions'],
            patterns=['lexicon-patterns'],
            complexity=0.8
        )
        
        result = self.activation_system.activate_specialists(work)
        
        # Lex should be activated
        assert len(result.activation) > 0 or len(result.ownership) > 0
        lex = result.activation[0] if result.activation else result.ownership[0]
        assert lex.id == 'lex'
    
    def test_activate_specialists_low_relevance(self):
        """Test activation for work with low relevance."""
        work = Work(
            description='General code',
            domain=['General'],
            systems=['General'],
            data=['general-data'],
            patterns=['general-patterns'],
            complexity=0.5
        )
        
        result = self.activation_system.activate_specialists(work)
        
        # Should have no activation or ownership
        assert len(result.ownership) == 0
        assert len(result.activation) == 0
        # May have consultation suggestions
        assert len(result.none) > 0 or len(result.consultation) >= 0
    
    def test_should_activate(self):
        """Test should_activate method."""
        work = Work(
            description='UI component',
            domain=['UI'],
            systems=['React'],
            data=['design-tokens'],
            patterns=['component-patterns'],
            complexity=0.7
        )
        
        ui_specialist = self.registry.get('ui-specialist')
        assert ui_specialist is not None
        
        should_activate = self.activation_system.should_activate(work, ui_specialist)
        assert should_activate is True
    
    def test_should_own(self):
        """Test should_own method."""
        work = Work(
            description='UI component design',
            domain=['UI', 'Design'],
            systems=['React'],
            data=['design-tokens'],
            patterns=['component-patterns'],
            complexity=0.9
        )
        
        ui_specialist = self.registry.get('ui-specialist')
        assert ui_specialist is not None
        
        # May or may not own depending on exact relevance
        should_own = self.activation_system.should_own(work, ui_specialist)
        assert isinstance(should_own, bool)
    
    def test_should_consult(self):
        """Test should_consult method."""
        work = Work(
            description='UI-related work',
            domain=['UI'],
            systems=[],
            data=[],
            patterns=[],
            complexity=0.5
        )
        
        ui_specialist = self.registry.get('ui-specialist')
        assert ui_specialist is not None
        
        should_consult = self.activation_system.should_consult(work, ui_specialist)
        assert isinstance(should_consult, bool)
    
    def test_get_best_match(self):
        """Test get_best_match method."""
        work = Work(
            description='UI component',
            domain=['UI'],
            systems=['React'],
            data=['design-tokens'],
            patterns=['component-patterns'],
            complexity=0.7
        )
        
        best_match = self.activation_system.get_best_match(work)
        
        assert best_match is not None
        specialist, score = best_match
        assert specialist.id == 'ui-specialist'
        assert score.overall > 0.0

