"""
Unit Tests: FAISSIndex
"""

import pytest
import numpy as np
import tempfile
import os
from icip_search import FAISSIndex


@pytest.fixture
def index():
    return FAISSIndex(dimension=384)


@pytest.fixture
def sample_vectors():
    """Generate sample vectors"""
    np.random.seed(42)
    return np.random.rand(10, 384).astype(np.float32)


@pytest.fixture
def sample_metadata():
    """Generate sample metadata"""
    return [
        {'file': f'file{i}.py', 'line': i * 10, 'name': f'func{i}'}
        for i in range(10)
    ]


def test_add_vectors(index, sample_vectors, sample_metadata):
    """Test adding vectors to index"""
    index.add(sample_vectors, sample_metadata)
    
    assert index.size() == 10
    assert len(index.metadata) == 10


def test_search(index, sample_vectors, sample_metadata):
    """Test vector search"""
    # Add vectors
    index.add(sample_vectors, sample_metadata)
    
    # Search for first vector (should be closest to itself)
    query_vector = sample_vectors[0:1]
    distances, indices, metadata = index.search(query_vector, k=3)
    
    # First result should be the query itself (distance ~0)
    assert indices[0][0] == 0
    assert distances[0][0] < 0.01  # Very small distance
    
    # Should return 3 results
    assert len(indices[0]) == 3
    assert len(metadata) == 3


def test_search_returns_metadata(index, sample_vectors, sample_metadata):
    """Test that search returns correct metadata"""
    index.add(sample_vectors, sample_metadata)
    
    query_vector = sample_vectors[0:1]
    distances, indices, metadata = index.search(query_vector, k=1)
    
    # Metadata should match
    assert metadata[0]['file'] == 'file0.py'
    assert metadata[0]['name'] == 'func0'


def test_save_and_load(index, sample_vectors, sample_metadata, tmp_path):
    """Test saving and loading index"""
    # Add vectors
    index.add(sample_vectors, sample_metadata)
    
    # Save
    index_path = tmp_path / "test.faiss"
    metadata_path = tmp_path / "test_metadata.json"
    index.save(str(index_path), str(metadata_path))
    
    # Create new index and load
    index2 = FAISSIndex(dimension=384)
    index2.load(str(index_path), str(metadata_path))
    
    # Verify loaded correctly
    assert index2.size() == 10
    assert len(index2.metadata) == 10
    assert index2.metadata[0]['file'] == 'file0.py'
    
    # Verify search works on loaded index
    query_vector = sample_vectors[0:1]
    distances, indices, metadata = index2.search(query_vector, k=1)
    assert indices[0][0] == 0


def test_clear(index, sample_vectors, sample_metadata):
    """Test clearing index"""
    index.add(sample_vectors, sample_metadata)
    assert index.size() == 10
    
    index.clear()
    assert index.size() == 0
    assert len(index.metadata) == 0


def test_add_validates_dimensions(index):
    """Test that add validates vector dimensions"""
    wrong_dim = np.random.rand(5, 128).astype(np.float32)  # Wrong dimension
    metadata = [{}] * 5
    
    with pytest.raises(ValueError, match="Vector dimension"):
        index.add(wrong_dim, metadata)


def test_add_validates_metadata_length(index):
    """Test that add validates metadata length"""
    vectors = np.random.rand(5, 384).astype(np.float32)
    metadata = [{}] * 3  # Wrong length
    
    with pytest.raises(ValueError, match="metadata length"):
        index.add(vectors, metadata)

