"""
Tests for Specialist Registry
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.specialist_registry import SpecialistRegistry, Specialist


class TestSpecialist:
    """Tests for Specialist class."""
    
    def test_create_specialist(self):
        """Test creating a specialist."""
        specialist = Specialist(
            id='test-specialist',
            name='Test Specialist',
            domain=['Test'],
            description='Test specialist'
        )
        assert specialist.id == 'test-specialist'
        assert specialist.name == 'Test Specialist'
        assert specialist.domain == ['Test']
    
    def test_specialist_validation(self):
        """Test specialist validation."""
        # Missing ID
        with pytest.raises(ValueError):
            Specialist(id='', name='Test', domain=['Test'], description='Test')
        
        # Missing name
        with pytest.raises(ValueError):
            Specialist(id='test', name='', domain=['Test'], description='Test')
        
        # Missing domain
        with pytest.raises(ValueError):
            Specialist(id='test', name='Test', domain=[], description='Test')
        
        # Invalid relevance factors (don't sum to 1.0)
        with pytest.raises(ValueError):
            Specialist(
                id='test',
                name='Test',
                domain=['Test'],
                description='Test',
                relevance_factors={
                    'domain_match': 0.50,
                    'data_connections': 0.50,
                    'system_connections': 0.20,
                    'pattern_recognition': 0.10,
                    'complexity': 0.05
                }
            )
        
        # Invalid activation thresholds (not in order)
        with pytest.raises(ValueError):
            Specialist(
                id='test',
                name='Test',
                domain=['Test'],
                description='Test',
                activation_thresholds={
                    'ownership': 0.60,
                    'activation': 0.70,
                    'consultation': 0.90
                }
            )
    
    def test_specialist_to_dict(self):
        """Test converting specialist to dictionary."""
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['Test'],
            description='Test'
        )
        data = specialist.to_dict()
        assert data['id'] == 'test'
        assert data['name'] == 'Test'
        assert isinstance(data['created_at'], str)
    
    def test_specialist_from_dict(self):
        """Test creating specialist from dictionary."""
        data = {
            'id': 'test',
            'name': 'Test',
            'domain': ['Test'],
            'description': 'Test',
            'connections': {'systems': [], 'data': [], 'patterns': []},
            'relevance_factors': {
                'domain_match': 0.40,
                'data_connections': 0.25,
                'system_connections': 0.20,
                'pattern_recognition': 0.10,
                'complexity': 0.05
            },
            'activation_thresholds': {
                'ownership': 0.90,
                'activation': 0.70,
                'consultation': 0.60
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        specialist = Specialist.from_dict(data)
        assert specialist.id == 'test'
        assert specialist.name == 'Test'


class TestSpecialistRegistry:
    """Tests for SpecialistRegistry class."""
    
    def test_register_specialist(self):
        """Test registering a specialist."""
        registry = SpecialistRegistry()
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['Test'],
            description='Test'
        )
        registry.register(specialist)
        assert registry.count() == 1
    
    def test_get_specialist(self):
        """Test getting a specialist."""
        registry = SpecialistRegistry()
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['Test'],
            description='Test'
        )
        registry.register(specialist)
        retrieved = registry.get('test')
        assert retrieved is not None
        assert retrieved.id == 'test'
    
    def test_get_nonexistent_specialist(self):
        """Test getting nonexistent specialist."""
        registry = SpecialistRegistry()
        assert registry.get('nonexistent') is None
    
    def test_find_by_domain(self):
        """Test finding specialists by domain."""
        registry = SpecialistRegistry()
        
        specialist1 = Specialist(
            id='ui',
            name='UI Specialist',
            domain=['UI', 'UX'],
            description='UI specialist'
        )
        specialist2 = Specialist(
            id='lex',
            name='Lex',
            domain=['Language'],
            description='Language specialist'
        )
        
        registry.register(specialist1)
        registry.register(specialist2)
        
        ui_specialists = registry.find_by_domain('UI')
        assert len(ui_specialists) == 1
        assert ui_specialists[0].id == 'ui'
        
        language_specialists = registry.find_by_domain('Language')
        assert len(language_specialists) == 1
        assert language_specialists[0].id == 'lex'
    
    def test_find_by_system(self):
        """Test finding specialists by system."""
        registry = SpecialistRegistry()
        
        specialist = Specialist(
            id='ui',
            name='UI Specialist',
            domain=['UI'],
            description='UI specialist',
            connections={'systems': ['React', 'Vue'], 'data': [], 'patterns': []}
        )
        registry.register(specialist)
        
        react_specialists = registry.find_by_system('React')
        assert len(react_specialists) == 1
        assert react_specialists[0].id == 'ui'
    
    def test_duplicate_registration(self):
        """Test registering duplicate specialist."""
        registry = SpecialistRegistry()
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['Test'],
            description='Test'
        )
        registry.register(specialist)
        
        with pytest.raises(ValueError):
            registry.register(specialist)
    
    def test_update_specialist(self):
        """Test updating a specialist."""
        registry = SpecialistRegistry()
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['Test'],
            description='Test'
        )
        registry.register(specialist)
        
        updated = Specialist(
            id='test',
            name='Updated Test',
            domain=['Test', 'Updated'],
            description='Updated'
        )
        registry.update(updated)
        
        retrieved = registry.get('test')
        assert retrieved.name == 'Updated Test'
        assert 'Updated' in retrieved.domain
    
    def test_remove_specialist(self):
        """Test removing a specialist."""
        registry = SpecialistRegistry()
        specialist = Specialist(
            id='test',
            name='Test',
            domain=['Test'],
            description='Test'
        )
        registry.register(specialist)
        assert registry.count() == 1
        
        registry.remove('test')
        assert registry.count() == 0
        assert registry.get('test') is None
    
    def test_get_all_specialists(self):
        """Test getting all specialists."""
        registry = SpecialistRegistry()
        
        specialist1 = Specialist(
            id='test1',
            name='Test 1',
            domain=['Test'],
            description='Test'
        )
        specialist2 = Specialist(
            id='test2',
            name='Test 2',
            domain=['Test'],
            description='Test'
        )
        
        registry.register(specialist1)
        registry.register(specialist2)
        
        all_specialists = registry.get_all()
        assert len(all_specialists) == 2

