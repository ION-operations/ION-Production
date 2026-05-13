"""
Unit Tests: SemanticEngine
"""

import pytest
import tempfile
import os
from pathlib import Path
from icip_search import SemanticEngine


@pytest.fixture
def test_codebase(tmp_path):
    """Create test codebase"""
    # Create Python files
    (tmp_path / "auth.py").write_text('''
def authenticate(username, password):
    """Authenticate user with credentials"""
    return verify_credentials(username, password)

def login(user):
    """Log in user"""
    return create_session(user)
''')
    
    (tmp_path / "math.py").write_text('''
def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b
''')
    
    return str(tmp_path)


@pytest.fixture
def engine(test_codebase):
    """Create semantic engine"""
    return SemanticEngine(test_codebase)


def test_engine_initialization(test_codebase):
    """Test engine initializes correctly"""
    engine = SemanticEngine(test_codebase)
    
    assert engine.codebase_path == test_codebase
    assert engine.chunker is not None
    assert engine.embedder is not None
    assert engine.index is not None


def test_index_codebase(engine):
    """Test indexing codebase"""
    # Index
    engine.index_codebase(languages=['py'])
    
    # Should have indexed functions
    assert engine.index.size() > 0
    assert len(engine.chunks) > 0
    
    # Should have found our functions
    chunk_names = {c.name for c in engine.chunks}
    assert 'authenticate' in chunk_names
    assert 'login' in chunk_names
    assert 'add' in chunk_names


def test_semantic_search_finds_relevant_code(engine):
    """Test that semantic search finds relevant code"""
    # Index first
    engine.index_codebase(languages=['py'])
    
    # Search for authentication
    results = engine.search("user authentication", k=5)
    
    # Should find authentication-related functions
    assert len(results) > 0
    result_names = {r.name for r in results}
    assert 'authenticate' in result_names or 'login' in result_names


def test_semantic_search_synonym_matching(engine):
    """Test that semantic search handles synonyms"""
    engine.index_codebase(languages=['py'])
    
    # Search for "login" should find "authenticate"
    results = engine.search("login functionality", k=10)
    
    # Should find auth-related code
    assert len(results) > 0
    result_code = ' '.join([r.code for r in results])
    assert 'authenticate' in result_code or 'login' in result_code


def test_search_returns_relevance_scores(engine):
    """Test that results have relevance scores"""
    engine.index_codebase(languages=['py'])
    
    results = engine.search("math operations", k=5)
    
    assert len(results) > 0
    
    # All results should have scores
    for result in results:
        assert 0 <= result.relevance <= 1
        assert 0 <= result.confidence <= 1
        assert result.distance >= 0
    
    # Results should be sorted by relevance (descending)
    relevances = [r.relevance for r in results]
    assert relevances == sorted(relevances, reverse=True)


def test_search_confidence_normalization(engine):
    """Test that confidence is normalized within results"""
    engine.index_codebase(languages=['py'])
    
    results = engine.search("functions", k=5)
    
    if len(results) > 1:
        # First result should have highest confidence
        assert results[0].confidence == 1.0
        
        # Last result should have lowest
        assert results[-1].confidence < results[0].confidence


def test_search_empty_query(engine):
    """Test search with empty query"""
    engine.index_codebase(languages=['py'])
    
    results = engine.search("", k=10)
    assert len(results) == 0


def test_search_no_index(test_codebase):
    """Test search auto-indexes if needed"""
    engine = SemanticEngine(test_codebase)
    
    # Search without explicit indexing
    results = engine.search("functions", k=5)
    
    # Should have auto-indexed
    assert engine.index.size() > 0
    assert len(results) > 0


def test_index_persistence(test_codebase):
    """Test that index persists across engine instances"""
    # Create engine and index
    engine1 = SemanticEngine(test_codebase)
    engine1.index_codebase(languages=['py'])
    size1 = engine1.index.size()
    
    # Create new engine (should load existing index)
    engine2 = SemanticEngine(test_codebase)
    size2 = engine2.index.size()
    
    # Should have same size
    assert size1 == size2
    assert size2 > 0


def test_get_stats(engine):
    """Test getting index statistics"""
    engine.index_codebase(languages=['py'])
    
    stats = engine.get_stats()
    
    assert 'total_chunks' in stats
    assert 'index_size' in stats
    assert 'languages' in stats
    assert 'types' in stats
    assert 'dimension' in stats
    
    assert stats['total_chunks'] > 0
    assert stats['dimension'] == 384
    assert 'python' in stats['languages']

