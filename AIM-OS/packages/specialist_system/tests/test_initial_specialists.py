"""
Tests for Initial Specialist Registration
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.specialist_registry import SpecialistRegistry
from specialist_system.initial_specialists import register_initial_specialists, get_initial_specialists


class TestInitialSpecialists:
    """Tests for initial specialist registration."""
    
    def test_register_initial_specialists(self):
        """Test registering initial specialists."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        # Should have 5 specialists (4 original + math specialist)
        assert registry.count() == 5
        
        # Check each specialist exists
        assert registry.get('ui-specialist') is not None
        assert registry.get('lex') is not None
        assert registry.get('codex') is not None
        assert registry.get('solo') is not None
        assert registry.get('math-specialist') is not None
    
    def test_ui_specialist_registration(self):
        """Test UI Specialist registration."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        ui_specialist = registry.get('ui-specialist')
        assert ui_specialist is not None
        assert ui_specialist.name == 'UI Specialist'
        assert 'UI' in ui_specialist.domain
        assert 'React' in ui_specialist.connections['systems']
    
    def test_lex_registration(self):
        """Test Lex registration."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        lex = registry.get('lex')
        assert lex is not None
        assert lex.name == 'Lex'
        assert 'Language' in lex.domain
        assert 'PLIx' in lex.connections['systems']
    
    def test_codex_registration(self):
        """Test Codex registration."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        codex = registry.get('codex')
        assert codex is not None
        assert codex.name == 'Codex'
        assert 'Chat' in codex.domain
    
    def test_solo_registration(self):
        """Test Solo registration."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        solo = registry.get('solo')
        assert solo is not None
        assert solo.name == 'Solo'
        assert 'Backend Integration' in solo.domain
        assert 'REST' in solo.connections['systems']
    
    def test_find_by_domain(self):
        """Test finding specialists by domain."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        ui_specialists = registry.find_by_domain('UI')
        assert len(ui_specialists) == 1
        assert ui_specialists[0].id == 'ui-specialist'
        
        language_specialists = registry.find_by_domain('Language')
        assert len(language_specialists) == 1
        assert language_specialists[0].id == 'lex'
    
    def test_find_by_system(self):
        """Test finding specialists by system."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        react_specialists = registry.find_by_system('React')
        assert len(react_specialists) == 1
        assert react_specialists[0].id == 'ui-specialist'
        
        plix_specialists = registry.find_by_system('PLIx')
        assert len(plix_specialists) == 1
        assert plix_specialists[0].id == 'lex'
    
    def test_get_initial_specialists(self):
        """Test get_initial_specialists function."""
        specialists = get_initial_specialists()
        
        assert len(specialists) == 5
        specialist_ids = [s.id for s in specialists]
        assert 'ui-specialist' in specialist_ids
        assert 'lex' in specialist_ids
        assert 'codex' in specialist_ids
        assert 'solo' in specialist_ids
        assert 'math-specialist' in specialist_ids
    
    def test_math_specialist_registration(self):
        """Test Math Specialist registration."""
        registry = SpecialistRegistry()
        register_initial_specialists(registry)
        
        math_specialist = registry.get('math-specialist')
        assert math_specialist is not None
        assert math_specialist.name == 'Math Specialist'
        assert 'Mathematics' in math_specialist.domain
        assert 'Matplotlib' in math_specialist.connections['systems']
        assert 'NumPy' in math_specialist.connections['systems']

