"""Tests for NL Tag Registry"""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.nl_tags.tag_registry import NLTagRegistry
from packages.nl_tags.models import NLTag, TagCoverageStats


class TestNLTagRegistry:
    """Test NL tag registry"""
    
    def test_register_tags_from_file(self):
        """Test registering tags from file"""
        registry = NLTagRegistry()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""# NL: Validates user input
def validate_input(data: dict) -> bool:
    return True
""")
            file_path = f.name
        
        try:
            tags = registry.register_tags_from_file(file_path)
            assert len(tags) == 1
            assert file_path in registry._tags_cache
        finally:
            os.unlink(file_path)
    
    def test_get_tags_for_file(self):
        """Test retrieving tags for file"""
        registry = NLTagRegistry()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""# NL: Test function
def test_function():
    pass
""")
            file_path = f.name
        
        try:
            tags = registry.get_tags_for_file(file_path)
            assert len(tags) == 1
            assert tags[0].tag_text == "Test function"
        finally:
            os.unlink(file_path)
    
    def test_get_coverage_stats(self):
        """Test coverage statistics calculation"""
        registry = NLTagRegistry()
        
        # Create temporary files
        files = []
        try:
            # File with tag
            f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            f1.write("""# NL: Function with tag
def tagged_function():
    pass
""")
            f1.close()
            files.append(f1.name)
            
            # File without tag
            f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            f2.write("""def untagged_function():
    pass
""")
            f2.close()
            files.append(f2.name)
            
            # Register tags
            for file_path in files:
                registry.register_tags_from_file(file_path)
            
            # Calculate stats (using temp directory as root)
            stats = registry.get_coverage_stats()
            
            assert stats.total_files >= 2
            assert stats.total_tags >= 1
            assert stats.coverage_percentage >= 0.0
            
        finally:
            # Cleanup
            for file_path in files:
                os.unlink(file_path)

