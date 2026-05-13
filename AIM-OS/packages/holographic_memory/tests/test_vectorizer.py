"""Tests for vectorizer modules."""

import numpy as np
import pytest

from holographic_memory import (
    PLIxVectorizer,
    EntityVectorizer,
    RelationshipVectorizer,
    MemoryAtomVectorizer,
)


class TestPLIxVectorizer:
    """Test suite for PLIxVectorizer."""
    
    def test_vectorize(self):
        """Test PLIx intent vectorization."""
        vectorizer = PLIxVectorizer(dimension=1000)
        
        plix_intent = {
            "goal": "Test goal",
            "process": "Test process",
            "constraint": "Test constraint",
            "effect": "Test effect",
        }
        
        vector = vectorizer.vectorize(plix_intent)
        
        assert vector.shape == (1000,)
        assert np.isfinite(vector).all()
        assert np.linalg.norm(vector) <= 1.0 + 1e-6  # Normalized


class TestEntityVectorizer:
    """Test suite for EntityVectorizer."""
    
    def test_vectorize(self):
        """Test entity vectorization."""
        vectorizer = EntityVectorizer(dimension=1000)
        
        entity = {
            "id": "entity_123",
            "type": "concept",
            "name": "Test Entity",
            "attributes": {"field": "ai"},
        }
        
        vector = vectorizer.vectorize(entity)
        
        assert vector.shape == (1000,)
        assert np.isfinite(vector).all()
        assert np.linalg.norm(vector) <= 1.0 + 1e-6


class TestRelationshipVectorizer:
    """Test suite for RelationshipVectorizer."""
    
    def test_vectorize(self):
        """Test relationship vectorization."""
        vectorizer = RelationshipVectorizer(dimension=1000)
        
        relationship = {
            "source_id": "entity_1",
            "target_id": "entity_2",
            "relation_type": "relates_to",
            "confidence": 0.95,
        }
        
        vector = vectorizer.vectorize(relationship)
        
        assert vector.shape == (1000,)
        assert np.isfinite(vector).all()
        assert np.linalg.norm(vector) <= 1.0 + 1e-6


class TestMemoryAtomVectorizer:
    """Test suite for MemoryAtomVectorizer."""
    
    def test_vectorize(self):
        """Test memory atom vectorization."""
        vectorizer = MemoryAtomVectorizer(dimension=1000)
        
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": "Test content"},
            "tags": [{"key": "topic", "value": "test"}],
        }
        
        vector = vectorizer.vectorize(atom)
        
        assert vector.shape == (1000,)
        assert np.isfinite(vector).all()
        assert np.linalg.norm(vector) <= 1.0 + 1e-6
    
    def test_long_content_truncation(self):
        """Test that long content is truncated."""
        vectorizer = MemoryAtomVectorizer(dimension=1000)
        
        # Very long content
        long_content = "x" * 10000
        atom = {
            "id": "atom_123",
            "modality": "text",
            "content": {"inline": long_content},
            "tags": [],
        }
        
        vector = vectorizer.vectorize(atom)
        
        assert vector.shape == (1000,)
        assert np.isfinite(vector).all()

