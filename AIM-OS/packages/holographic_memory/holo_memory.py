"""AIMO_HoloMemory - Core holographic memory implementation.

Implements distributed associative memory using holographic reduced representations (HRR)
principles for AIM-OS integration.
"""

from __future__ import annotations

import logging
import uuid
from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


class AIMO_HoloMemory:
    """Distributed associative memory substrate using holographic principles.
    
    Encodes structured data as high-dimensional vectors distributed across
    the entire memory array, enabling associative recall, fuzzy matching,
    and pattern completion.
    
    Example:
        >>> memory = AIMO_HoloMemory(dimension=10000)
        >>> data_vec = np.random.randn(10000)
        >>> label_vec = np.random.randn(10000)
        >>> memory_id = memory.store(memory.encode(data_vec, label_vec))
        >>> reconstructed, fidelity = memory.decode(label_vec)
        >>> print(f"Reconstruction fidelity: {fidelity:.3f}")
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        normalize: bool = True,
        sparse_threshold: float = 1e-6,
    ):
        """Initialize holographic memory.
        
        Args:
            dimension: Dimensionality of holographic vectors (default: 10000)
            normalize: Whether to normalize vectors (default: True)
            sparse_threshold: Threshold for sparse storage (default: 1e-6)
        """
        self.dimension = dimension
        self.normalize = normalize
        self.sparse_threshold = sparse_threshold
        
        # Holographic memory array (distributed storage)
        self.memory_array: Optional[NDArray[np.float64]] = None
        
        # Memory ID to label vector mapping
        self.memory_registry: Dict[str, NDArray[np.float64]] = {}
        
        # Label vector to memory ID mapping (for exact lookups)
        self.label_to_id: Dict[bytes, str] = {}
        
        logger.info(f"Initialized AIMO_HoloMemory (dim={dimension}, normalize={normalize})")
    
    def encode(
        self,
        data_vector: NDArray[np.float64],
        label_vector: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Bind structured data with semantic ID using circular convolution.
        
        The binding operation distributes the data across the entire memory
        array, where each part contains information about the whole.
        
        Args:
            data_vector: High-dimensional vector representing the data
            label_vector: High-dimensional vector representing the semantic ID/label
            
        Returns:
            Composite vector encoding the bound data and label
            
        Raises:
            ValueError: If vectors have incorrect dimensions
        """
        if data_vector.shape != (self.dimension,) or label_vector.shape != (self.dimension,):
            raise ValueError(
                f"Vectors must have dimension {self.dimension}, "
                f"got {data_vector.shape} and {label_vector.shape}"
            )
        
        # Normalize if requested
        if self.normalize:
            data_vector = data_vector / (np.linalg.norm(data_vector) + 1e-10)
            label_vector = label_vector / (np.linalg.norm(label_vector) + 1e-10)
        
        # Circular convolution (HRR binding operation)
        # This is equivalent to FFT-based circular convolution
        data_fft = np.fft.fft(data_vector)
        label_fft = np.fft.fft(label_vector)
        composite_fft = data_fft * label_fft
        composite = np.fft.ifft(composite_fft).real
        
        # Normalize composite
        if self.normalize:
            composite = composite / (np.linalg.norm(composite) + 1e-10)
        
        return composite
    
    def decode(
        self,
        query_vector: NDArray[np.float64],
    ) -> Tuple[NDArray[np.float64], float]:
        """Reconstruct original data given label or content vector.
        
        Uses circular correlation (inverse of circular convolution) to
        unbind the data from the holographic memory.
        
        Args:
            query_vector: Label vector or partial content vector for query
            
        Returns:
            Tuple of (reconstructed_data, fidelity_score)
            - reconstructed_data: Best reconstruction attempt
            - fidelity_score: Quality of reconstruction (0.0-1.0)
            
        Raises:
            ValueError: If query vector has incorrect dimension
            RuntimeError: If memory array is empty
        """
        if query_vector.shape != (self.dimension,):
            raise ValueError(
                f"Query vector must have dimension {self.dimension}, "
                f"got {query_vector.shape}"
            )
        
        if self.memory_array is None:
            raise RuntimeError("Memory array is empty - nothing to decode")
        
        # Normalize query
        if self.normalize:
            query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        
        # Circular correlation (unbinding operation)
        query_fft = np.fft.fft(query_vector)
        memory_fft = np.fft.fft(self.memory_array)
        
        # Unbind: divide by query (inverse of binding)
        reconstructed_fft = memory_fft / (query_fft + 1e-10)
        reconstructed = np.fft.ifft(reconstructed_fft).real
        
        # Normalize
        if self.normalize:
            reconstructed = reconstructed / (np.linalg.norm(reconstructed) + 1e-10)
        
        # Compute fidelity (cosine similarity with expected structure)
        # For now, use magnitude as proxy (higher = better reconstruction)
        fidelity = min(1.0, np.linalg.norm(reconstructed) / np.sqrt(self.dimension))
        
        return reconstructed, fidelity
    
    def store(
        self,
        composite_vector: NDArray[np.float64],
        label_vector: Optional[NDArray[np.float64]] = None,
    ) -> str:
        """Add encoded vector to holographic memory array.
        
        The composite vector is added to the distributed memory array,
        where it becomes part of the holographic substrate.
        
        Args:
            composite_vector: Encoded composite vector (from encode())
            label_vector: Optional label vector for exact lookup
            
        Returns:
            Memory ID (unique identifier for this memory)
            
        Raises:
            ValueError: If composite vector has incorrect dimension
        """
        if composite_vector.shape != (self.dimension,):
            raise ValueError(
                f"Composite vector must have dimension {self.dimension}, "
                f"got {composite_vector.shape}"
            )
        
        # Generate unique memory ID
        memory_id = str(uuid.uuid4())
        
        # Initialize memory array if empty
        if self.memory_array is None:
            self.memory_array = np.zeros(self.dimension, dtype=np.float64)
        
        # Add to distributed memory (superposition)
        self.memory_array = self.memory_array + composite_vector
        
        # Store label vector for exact lookup if provided
        if label_vector is not None:
            if label_vector.shape != (self.dimension,):
                raise ValueError(
                    f"Label vector must have dimension {self.dimension}, "
                    f"got {label_vector.shape}"
                )
            self.memory_registry[memory_id] = label_vector.copy()
            # Create hash for fast lookup
            label_hash = hash(label_vector.tobytes())
            self.label_to_id[label_hash] = memory_id
        
        logger.debug(f"Stored memory {memory_id} in holographic array")
        
        return memory_id
    
    def update(
        self,
        modified_vector: NDArray[np.float64],
        label_vector: NDArray[np.float64],
    ) -> None:
        """Modify existing entries in holographic memory.
        
        Note: In holographic memory, "updates" are typically done by
        storing a new version and using the label to retrieve the latest.
        This method provides a way to adjust the memory array directly.
        
        Args:
            modified_vector: New composite vector
            label_vector: Label vector identifying the memory to update
            
        Raises:
            ValueError: If vectors have incorrect dimensions
            KeyError: If label vector not found in registry
        """
        if modified_vector.shape != (self.dimension,) or label_vector.shape != (self.dimension,):
            raise ValueError(
                f"Vectors must have dimension {self.dimension}, "
                f"got {modified_vector.shape} and {label_vector.shape}"
            )
        
        # Find memory ID from label
        label_hash = hash(label_vector.tobytes())
        if label_hash not in self.label_to_id:
            raise KeyError("Label vector not found in memory registry")
        
        memory_id = self.label_to_id[label_hash]
        
        # Decode old version to subtract it
        old_composite, _ = self.decode(label_vector)
        
        # Subtract old, add new
        if self.memory_array is not None:
            self.memory_array = self.memory_array - old_composite + modified_vector
        
        # Update registry
        self.memory_registry[memory_id] = label_vector.copy()
        
        logger.debug(f"Updated memory {memory_id} in holographic array")
    
    def correlate(
        self,
        query_vector: NDArray[np.float64],
        top_k: int = 10,
    ) -> List[Tuple[str, float]]:
        """Return highly correlated vectors from memory.
        
        Computes correlation between query vector and all stored memories,
        returning the top-k most similar entries.
        
        Args:
            query_vector: Query vector for correlation
            top_k: Number of top results to return
            
        Returns:
            List of (memory_id, correlation_score) tuples, sorted by score descending
            
        Raises:
            ValueError: If query vector has incorrect dimension
            RuntimeError: If memory array is empty
        """
        if query_vector.shape != (self.dimension,):
            raise ValueError(
                f"Query vector must have dimension {self.dimension}, "
                f"got {query_vector.shape}"
            )
        
        if self.memory_array is None or len(self.memory_registry) == 0:
            raise RuntimeError("Memory array is empty - nothing to correlate")
        
        # Normalize query
        if self.normalize:
            query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        
        # Compute correlations with all stored memories
        correlations = []
        for memory_id, label_vector in self.memory_registry.items():
            # Decode using label to get stored data
            reconstructed, fidelity = self.decode(label_vector)
            
            # Compute cosine similarity (correlation)
            correlation = np.dot(query_vector, reconstructed) / (
                np.linalg.norm(query_vector) * np.linalg.norm(reconstructed) + 1e-10
            )
            
            # Weight by fidelity
            weighted_correlation = correlation * fidelity
            
            correlations.append((memory_id, float(weighted_correlation)))
        
        # Sort by correlation (descending) and return top-k
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        return correlations[:top_k]
    
    def get_memory_stats(self) -> Dict[str, any]:
        """Get statistics about the holographic memory.
        
        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "dimension": self.dimension,
            "memory_count": len(self.memory_registry),
            "memory_array_norm": float(np.linalg.norm(self.memory_array)) if self.memory_array is not None else 0.0,
            "normalize": self.normalize,
        }
        
        return stats

