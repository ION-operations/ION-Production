"""Tests for AIMO_HoloMemory core module."""

import numpy as np
import pytest

from holographic_memory import AIMO_HoloMemory


class TestAIMOHoloMemory:
    """Test suite for AIMO_HoloMemory."""
    
    def test_initialization(self):
        """Test memory initialization."""
        memory = AIMO_HoloMemory(dimension=1000, normalize=True)
        assert memory.dimension == 1000
        assert memory.normalize is True
        assert memory.memory_array is None
        assert len(memory.memory_registry) == 0
    
    def test_encode_decode(self):
        """Test encoding and decoding operations."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        # Create test vectors
        data_vector = np.random.randn(1000)
        label_vector = np.random.randn(1000)
        
        # Normalize
        data_vector = data_vector / np.linalg.norm(data_vector)
        label_vector = label_vector / np.linalg.norm(label_vector)
        
        # Encode
        composite = memory.encode(data_vector, label_vector)
        
        assert composite.shape == (1000,)
        assert np.isfinite(composite).all()
        
        # Store
        memory_id = memory.store(composite, label_vector)
        assert memory_id is not None
        
        # Decode
        reconstructed, fidelity = memory.decode(label_vector)
        
        assert reconstructed.shape == (1000,)
        assert 0.0 <= fidelity <= 1.0
        assert np.isfinite(reconstructed).all()
    
    def test_store_retrieve(self):
        """Test storing and retrieving memories."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        # Create and store multiple memories
        memory_ids = []
        for i in range(5):
            data_vector = np.random.randn(1000)
            label_vector = np.random.randn(1000)
            data_vector = data_vector / np.linalg.norm(data_vector)
            label_vector = label_vector / np.linalg.norm(label_vector)
            
            composite = memory.encode(data_vector, label_vector)
            memory_id = memory.store(composite, label_vector)
            memory_ids.append(memory_id)
        
        # Verify all stored
        assert len(memory.memory_registry) == 5
        assert len(memory_ids) == 5
        
        # Retrieve one
        label_vector = memory.memory_registry[memory_ids[0]]
        reconstructed, fidelity = memory.decode(label_vector)
        
        assert reconstructed.shape == (1000,)
        assert fidelity >= 0.0
    
    def test_correlate(self):
        """Test correlation operation."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        # Store multiple memories
        query_vector = None
        for i in range(10):
            data_vector = np.random.randn(1000)
            label_vector = np.random.randn(1000)
            data_vector = data_vector / np.linalg.norm(data_vector)
            label_vector = label_vector / np.linalg.norm(label_vector)
            
            if i == 5:
                query_vector = data_vector.copy()
            
            composite = memory.encode(data_vector, label_vector)
            memory.store(composite, label_vector)
        
        # Correlate
        results = memory.correlate(query_vector, top_k=5)
        
        assert len(results) == 5
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
        assert all(isinstance(score, float) and -1.0 <= score <= 1.0 for _, score in results)
    
    def test_update(self):
        """Test update operation."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        # Store initial memory
        data_vector = np.random.randn(1000)
        label_vector = np.random.randn(1000)
        data_vector = data_vector / np.linalg.norm(data_vector)
        label_vector = label_vector / np.linalg.norm(label_vector)
        
        composite = memory.encode(data_vector, label_vector)
        memory_id = memory.store(composite, label_vector)
        
        # Update
        new_data_vector = np.random.randn(1000)
        new_data_vector = new_data_vector / np.linalg.norm(new_data_vector)
        new_composite = memory.encode(new_data_vector, label_vector)
        
        memory.update(new_composite, label_vector)
        
        # Verify update
        assert memory_id in memory.memory_registry
    
    def test_get_memory_stats(self):
        """Test memory statistics."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        # Store some memories
        for i in range(3):
            data_vector = np.random.randn(1000)
            label_vector = np.random.randn(1000)
            data_vector = data_vector / np.linalg.norm(data_vector)
            label_vector = label_vector / np.linalg.norm(label_vector)
            
            composite = memory.encode(data_vector, label_vector)
            memory.store(composite, label_vector)
        
        stats = memory.get_memory_stats()
        
        assert stats["dimension"] == 1000
        assert stats["memory_count"] == 3
        assert stats["normalize"] is True
        assert stats["memory_array_norm"] >= 0.0
    
    def test_dimension_mismatch_error(self):
        """Test error handling for dimension mismatches."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        # Wrong dimension
        wrong_vector = np.random.randn(500)
        
        with pytest.raises(ValueError):
            memory.encode(wrong_vector, np.random.randn(1000))
        
        with pytest.raises(ValueError):
            memory.decode(wrong_vector)
    
    def test_empty_memory_error(self):
        """Test error handling for empty memory."""
        memory = AIMO_HoloMemory(dimension=1000)
        
        query_vector = np.random.randn(1000)
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        with pytest.raises(RuntimeError):
            memory.decode(query_vector)
        
        with pytest.raises(RuntimeError):
            memory.correlate(query_vector)

