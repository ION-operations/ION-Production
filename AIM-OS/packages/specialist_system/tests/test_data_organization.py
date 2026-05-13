"""
Tests for Data Organization System
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.data_organization import DataOrganizer, DataItem, SpecialistData


class TestDataOrganizer:
    """Tests for DataOrganizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.organizer = DataOrganizer()
    
    def test_organize_data(self):
        """Test organizing data."""
        data = [
            {'id': '1', 'type': 'primary', 'content': 'Primary data'},
            {'id': '2', 'type': 'connected', 'content': 'Connected data'},
            {'id': '3', 'type': 'extended', 'content': 'Extended data'}
        ]
        
        specialist_data = self.organizer.organize_data('test-specialist', data)
        
        assert specialist_data.specialist_id == 'test-specialist'
        assert len(specialist_data.primary_data) == 1
        assert len(specialist_data.connected_data) == 1
        assert len(specialist_data.extended_data) == 1
    
    def test_get_primary_data(self):
        """Test getting primary data."""
        data = [
            {'id': '1', 'type': 'primary', 'content': 'Primary'},
            {'id': '2', 'type': 'connected', 'content': 'Connected'}
        ]
        
        specialist_data = self.organizer.organize_data('test', data)
        primary = self.organizer.get_primary_data(specialist_data)
        
        assert len(primary) == 1
        assert primary[0].type == 'primary'
    
    def test_tag_data(self):
        """Test tagging data."""
        data = {'content': 'Test data'}
        
        tagged = self.organizer.tag_data(
            data,
            'test-specialist',
            domain=['UI'],
            systems=['React'],
            relevance=0.85
        )
        
        assert 'tags' in tagged
        assert tagged['tags']['specialist'] == 'test-specialist'
        assert tagged['tags']['domain'] == ['UI']
        assert tagged['tags']['systems'] == ['React']
        assert tagged['tags']['relevance'] == 0.85

