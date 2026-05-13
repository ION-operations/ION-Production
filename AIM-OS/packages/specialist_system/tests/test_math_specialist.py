"""
Tests for Math Specialist
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.specialist_registry import SpecialistRegistry
from specialist_system.initial_specialists import register_initial_specialists
from specialist_system.work_detector import WorkDetector
from specialist_system.relevance_calculator import RelevanceCalculator
from specialist_system.activation_system import ActivationSystem


class TestMathSpecialist:
    """Tests for Math Specialist."""
    
    def test_math_specialist_registration(self):
        """Test Math Specialist is registered."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        math_specialist = registry.get('math-specialist')
        assert math_specialist is not None
        assert math_specialist.name == 'Math Specialist'
        assert 'Mathematics' in math_specialist.domain
        assert 'Matplotlib' in math_specialist.connections['systems']
        assert 'NumPy' in math_specialist.connections['systems']
    
    def test_math_work_detection(self):
        """Test detecting math work from message."""
        detector = WorkDetector()
        message = "Create a plot showing the relationship between x and y using matplotlib"
        
        work = detector.detect_work(message)
        
        assert work.description == message
        assert 'Mathematics' in work.domain
        assert 'Matplotlib' in work.systems
    
    def test_math_specialist_activation(self):
        """Test Math Specialist activation for math work."""
        registry = SpecialistRegistry()
        calculator = RelevanceCalculator()
        activation_system = ActivationSystem(registry, calculator)
        register_initial_specialists(registry)
        
        from specialist_system.relevance_calculator import Work
        
        work = Work(
            description='Solve the equation x^2 + 2x + 1 = 0',
            domain=['Mathematics'],
            systems=['SymPy'],
            data=['equations'],
            patterns=['mathematical-patterns'],
            complexity=0.6
        )
        
        result = activation_system.activate_specialists(work)
        
        # Math specialist should be activated or consulted
        all_specialists = result.ownership + result.activation + result.consultation
        math_specialist_ids = [s.id for s in all_specialists]
        assert 'math-specialist' in math_specialist_ids
    
    def test_math_equation_work(self):
        """Test detecting equation work."""
        detector = WorkDetector()
        message = "Solve the equation x^2 + 5x + 6 = 0"
        
        work = detector.detect_work(message)
        
        assert 'Mathematics' in work.domain
        assert 'SymPy' in work.systems or len(work.systems) > 0
    
    def test_math_statistics_work(self):
        """Test detecting statistics work."""
        detector = WorkDetector()
        message = "Calculate the mean and standard deviation of this dataset using numpy"
        
        work = detector.detect_work(message)
        
        assert 'Mathematics' in work.domain
        assert 'NumPy' in work.systems

