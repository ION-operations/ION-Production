"""
Unit Tests: CodeEmbedder
"""

import pytest
import numpy as np
from icip_search import CodeEmbedder


@pytest.fixture
def embedder():
    return CodeEmbedder()


def test_embed_single_code(embedder):
    """Test embedding single code snippet"""
    code = "def add(a, b): return a + b"
    
    embedding = embedder.embed(code)
    
    # Check shape and type
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)  # all-MiniLM-L6-v2 is 384d
    assert embedding.dtype == np.float32
    
    # Check non-zero
    assert np.any(embedding != 0)


def test_embed_empty_code(embedder):
    """Test embedding empty string"""
    embedding = embedder.embed("")
    
    # Should return zero vector
    assert embedding.shape == (384,)
    assert np.all(embedding == 0)


def test_embed_batch(embedder):
    """Test batch embedding"""
    codes = [
        "def add(a, b): return a + b",
        "def subtract(a, b): return a - b",
        "class Calculator: pass",
    ]
    
    embeddings = embedder.embed_batch(codes)
    
    # Check shape
    assert embeddings.shape == (3, 384)
    assert embeddings.dtype == np.float32
    
    # Each embedding should be different
    assert not np.array_equal(embeddings[0], embeddings[1])
    assert not np.array_equal(embeddings[0], embeddings[2])


def test_embed_batch_empty(embedder):
    """Test batch embedding with empty list"""
    embeddings = embedder.embed_batch([])
    
    assert embeddings.shape == (0, 384)


def test_semantic_similarity(embedder):
    """Test that similar code has similar embeddings"""
    code1 = "def add(a, b): return a + b"
    code2 = "def sum_numbers(x, y): return x + y"  # Similar function
    code3 = "class Dog: pass"  # Completely different
    
    emb1 = embedder.embed(code1)
    emb2 = embedder.embed(code2)
    emb3 = embedder.embed(code3)
    
    # Calculate cosine similarity
    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_1_2 = cosine_sim(emb1, emb2)
    sim_1_3 = cosine_sim(emb1, emb3)
    
    # Similar code should have higher similarity
    assert sim_1_2 > sim_1_3
    assert sim_1_2 > 0.7  # Should be quite similar


def test_model_lazy_loading(embedder):
    """Test that model loads lazily"""
    # Model should be None initially
    assert embedder.model is None
    
    # After first embed, model should be loaded
    embedder.embed("test")
    assert embedder.model is not None


def test_embed_query_alias(embedder):
    """Test embed_query is alias for embed"""
    query = "authentication functions"
    
    emb1 = embedder.embed(query)
    emb2 = embedder.embed_query(query)
    
    assert np.array_equal(emb1, emb2)

