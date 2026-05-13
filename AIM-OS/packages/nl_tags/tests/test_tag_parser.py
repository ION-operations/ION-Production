"""Tests for NL Tag Parser"""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.nl_tags.tag_parser import NLTagParser
from packages.nl_tags.models import NLTag


class TestNLTagParser:
    """Test NL tag parser"""
    
    def test_detect_language_python(self):
        """Test Python language detection"""
        parser = NLTagParser()
        assert parser.detect_language("test.py") == "python"
        assert parser.detect_language("packages/vif/witness.py") == "python"
    
    def test_detect_language_typescript(self):
        """Test TypeScript language detection"""
        parser = NLTagParser()
        assert parser.detect_language("test.ts") == "typescript"
        assert parser.detect_language("test.tsx") == "typescript"
    
    def test_detect_language_javascript(self):
        """Test JavaScript language detection"""
        parser = NLTagParser()
        assert parser.detect_language("test.js") == "javascript"
        assert parser.detect_language("test.jsx") == "javascript"
    
    def test_extract_python_tag(self):
        """Test extracting Python NL tag"""
        parser = NLTagParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""# NL: Validates user authentication token
def validate_token(token: str) -> bool:
    return len(token) > 0
""")
            file_path = f.name
        
        try:
            tags = parser.parse_file(file_path)
            assert len(tags) == 1
            assert tags[0].tag_text == "Validates user authentication token"
            assert tags[0].language == "python"
            assert tags[0].line_start == 1
        finally:
            os.unlink(file_path)
    
    def test_extract_typescript_tag(self):
        """Test extracting TypeScript NL tag"""
        parser = NLTagParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write("""// NL: Fetches user data from API
async function fetchUser(id: string): Promise<User> {
    return await api.get(`/users/${id}`);
}
""")
            file_path = f.name
        
        try:
            tags = parser.parse_file(file_path)
            assert len(tags) == 1
            assert tags[0].tag_text == "Fetches user data from API"
            assert tags[0].language == "typescript"
            assert tags[0].line_start == 1
        finally:
            os.unlink(file_path)
    
    def test_extract_multiple_tags(self):
        """Test extracting multiple tags from file"""
        parser = NLTagParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""# NL: Validates user input
def validate_input(data: dict) -> bool:
    return True

# NL: Processes payment transaction
def process_payment(amount: float) -> str:
    return "success"
""")
            file_path = f.name
        
        try:
            tags = parser.parse_file(file_path)
            assert len(tags) == 2
            assert tags[0].tag_text == "Validates user input"
            assert tags[1].tag_text == "Processes payment transaction"
        finally:
            os.unlink(file_path)
    
    def test_extract_code_block(self):
        """Test code block extraction"""
        parser = NLTagParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""# NL: Validates user authentication token
def validate_token(token: str) -> bool:
    if not token:
        return False
    return len(token) > 10
""")
            file_path = f.name
        
        try:
            tags = parser.parse_file(file_path)
            assert len(tags) == 1
            assert tags[0].code_block is not None
            assert "def validate_token" in tags[0].code_block
        finally:
            os.unlink(file_path)
    
    def test_file_not_found(self):
        """Test handling of non-existent file"""
        parser = NLTagParser()
        tags = parser.parse_file("nonexistent.py")
        assert tags == []

