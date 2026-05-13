"""
Tests for Relevance Calculator
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.relevance_calculator import RelevanceCalculator, Work
from specialist_system.specialist_registry import Specialist


class TestRelevanceCalculator:
    """Tests for RelevanceCalculator class."""
    
    def test_calculate_relevance_ui_work(self):
        """Test calculating relevance for UI work."""
        calculator = RelevanceCalculator()
        
        work = Work(
            description='Design a new button component',
            domain=['UI', 'Design'],
            systems=['React', 'Tailwind'],
            data=['design-tokens', 'component-libraries'],
            patterns=['component-patterns'],
            complexity=0.7
        )
        
        specialist = Specialist(
            id='ui-specialist',
            name='UI Specialist',
            domain=['UI', 'UX', 'Design', 'Frontend'],
            description='UI specialist',
            connections={
                'systems': ['React', 'Vue', 'Tailwind'],
                'data': ['design-tokens', 'component-libraries'],
                'patterns': ['component-patterns']
            }
        )
        
        score = calculator.calculate_relevance(work, specialist)
        
        # Should have high relevance (>0.70)
        assert score.overall > 0.70
        assert score.domain_match >= 0.5  # 2/4 = 0.5 exactly
        assert score.data_connections > 0.5
        assert score.system_connections > 0.5
    
    def test_calculate_relevance_language_work(self):
        """Test calculating relevance for language work."""
        calculator = RelevanceCalculator()
        
        work = Work(
            description='Define PLIx language lexicon',
            domain=['Language', 'Lexicon'],
            systems=['PLIx'],
            data=['language-specs', 'lexicon-definitions'],
            patterns=['lexicon-patterns'],
            complexity=0.8
        )
        
        specialist = Specialist(
            id='lex',
            name='Lex',
            domain=['Language', 'Lexicon', 'Grammar'],
            description='Language specialist',
            connections={
                'systems': ['PLIx', 'Smalltalk-like'],
                'data': ['language-specs', 'lexicon-definitions'],
                'patterns': ['lexicon-patterns']
            }
        )
        
        score = calculator.calculate_relevance(work, specialist)
        
        # Should have high relevance (>0.85) - algorithm gives 0.857
        assert score.overall > 0.85
        assert score.domain_match > 0.6  # 2/3 = 0.667
        assert score.data_connections > 0.8
    
    def test_calculate_relevance_low_relevance(self):
        """Test calculating relevance for work with low relevance."""
        calculator = RelevanceCalculator()
        
        work = Work(
            description='General code implementation',
            domain=['General'],
            systems=['General'],
            data=['general-data'],
            patterns=['general-patterns'],
            complexity=0.5
        )
        
        specialist = Specialist(
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
        
        score = calculator.calculate_relevance(work, specialist)
        
        # Should have low relevance (<0.60)
        assert score.overall < 0.60
    
    def test_calculate_domain_match(self):
        """Test domain match calculation."""
        calculator = RelevanceCalculator()
        
        work = Work(description='UI work', domain=['UI', 'Design'])
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['UI', 'UX', 'Design'],
            description='Test'
        )
        
        match = calculator._calculate_domain_match(work, specialist)
        
        # Should have good match (intersection/union)
        assert 0.0 <= match <= 1.0
        assert match > 0.5  # Good overlap
    
    def test_calculate_data_connections(self):
        """Test data connections calculation."""
        calculator = RelevanceCalculator()
        
        work = Work(description='UI work', data=['design-tokens', 'component-libraries'])
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['UI'],
            description='Test',
            connections={
                'systems': [],
                'data': ['design-tokens', 'component-libraries', 'ux-patterns'],
                'patterns': []
            }
        )
        
        connections = calculator._calculate_data_connections(work, specialist)
        
        # Should have good connections (2/2 = 1.0)
        assert connections == 1.0
    
    def test_calculate_system_connections(self):
        """Test system connections calculation."""
        calculator = RelevanceCalculator()
        
        work = Work(description='UI work', systems=['React', 'Vue'])
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['UI'],
            description='Test',
            connections={
                'systems': ['React', 'Vue', 'Angular'],
                'data': [],
                'patterns': []
            }
        )
        
        connections = calculator._calculate_system_connections(work, specialist)
        
        # Should have good connections (2/2 = 1.0)
        assert connections == 1.0
    
    def test_calculate_pattern_recognition(self):
        """Test pattern recognition calculation."""
        calculator = RelevanceCalculator()
        
        work = Work(description='UI work', patterns=['component-patterns', 'layout-patterns'])
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['UI'],
            description='Test',
            connections={
                'systems': [],
                'data': [],
                'patterns': ['component-patterns', 'layout-patterns', 'interaction-patterns']
            }
        )
        
        recognition = calculator._calculate_pattern_recognition(work, specialist)
        
        # Should have good recognition (2/2 = 1.0)
        assert recognition == 1.0
    
    def test_calculate_complexity(self):
        """Test complexity calculation."""
        calculator = RelevanceCalculator()
        
        work = Work(description='Complex work', complexity=0.8)
        complexity = calculator._calculate_complexity(work)
        
        assert complexity == 0.8
        
        work_no_complexity = Work(description='Simple work')
        complexity_default = calculator._calculate_complexity(work_no_complexity)
        
        assert complexity_default == 0.5  # Default moderate complexity

