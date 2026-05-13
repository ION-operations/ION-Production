"""
Unit Tests: CodeChunker
"""

import pytest
import tempfile
import os
from pathlib import Path
from icip_search import CodeChunker, CodeChunk


@pytest.fixture
def chunker():
    return CodeChunker()


@pytest.fixture
def sample_python_file(tmp_path):
    """Create sample Python file for testing"""
    file_path = tmp_path / "sample.py"
    content = '''
def add(a, b):
    """Add two numbers"""
    return a + b

class Calculator:
    def multiply(self, a, b):
        """Multiply two numbers"""
        return a * b
    
    def divide(self, a, b):
        """Divide two numbers"""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
'''
    file_path.write_text(content)
    return str(file_path)


def test_chunk_python_file(chunker, sample_python_file):
    """Test chunking Python file"""
    chunks = chunker.chunk_file(sample_python_file, 'py')
    
    # Should extract: add function, Calculator class, multiply method, divide method
    assert len(chunks) >= 2  # At least function and class
    
    # Check function chunk
    func_chunks = [c for c in chunks if c.type == 'function']
    assert len(func_chunks) > 0
    assert any(c.name == 'add' for c in func_chunks)
    
    # Check class chunk
    class_chunks = [c for c in chunks if c.type == 'class']
    assert len(class_chunks) > 0
    assert any(c.name == 'Calculator' for c in class_chunks)
    
    # Verify chunk properties
    first_chunk = chunks[0]
    assert first_chunk.file == sample_python_file
    assert first_chunk.start_line > 0
    assert first_chunk.end_line >= first_chunk.start_line
    assert first_chunk.code != ""
    assert first_chunk.language == 'python'


def test_chunk_invalid_file(chunker, tmp_path):
    """Test chunking invalid Python file"""
    file_path = tmp_path / "invalid.py"
    file_path.write_text("this is not valid python code %%%")
    
    # Should handle error and return fallback chunk
    chunks = chunker.chunk_file(str(file_path), 'py')
    
    # Fallback should return whole file as one chunk
    assert len(chunks) == 1
    assert chunks[0].type == 'file'


def test_chunk_empty_file(chunker, tmp_path):
    """Test chunking empty file"""
    file_path = tmp_path / "empty.py"
    file_path.write_text("")
    
    chunks = chunker.chunk_file(str(file_path), 'py')
    assert len(chunks) == 0 or chunks[0].code == ""


def test_chunk_codebase(chunker, tmp_path):
    """Test chunking entire codebase"""
    # Create mini codebase
    (tmp_path / "file1.py").write_text("def func1(): pass")
    (tmp_path / "file2.py").write_text("def func2(): pass")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.py").write_text("def func3(): pass")
    
    chunks = chunker.chunk_codebase(str(tmp_path))
    
    # Should find all 3 functions
    assert len(chunks) >= 3
    func_names = {c.name for c in chunks if c.type == 'function'}
    assert 'func1' in func_names
    assert 'func2' in func_names
    assert 'func3' in func_names


def test_context_extraction(chunker, sample_python_file):
    """Test that context is extracted"""
    chunks = chunker.chunk_file(sample_python_file, 'py')
    
    # Chunks should have context
    assert any(c.context is not None for c in chunks)

