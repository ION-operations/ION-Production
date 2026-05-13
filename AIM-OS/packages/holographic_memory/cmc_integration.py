"""CMC Integration for AIMO_HoloMemory - Experimental/Additive Enhancement.

This module provides optional holographic memory capabilities for CMC,
working alongside (not replacing) primary CMC storage.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from .holo_memory import AIMO_HoloMemory
from .vectorizer import MemoryAtomVectorizer

logger = logging.getLogger(__name__)

# Configuration flag - must be explicitly enabled
ENABLE_HOLOGRAPHIC_MEMORY = os.getenv("ENABLE_HOLOGRAPHIC_MEMORY", "false").lower() == "true"


class CMC_HoloIntegration:
    """Experimental holographic memory integration for CMC.
    
    Provides optional associative memory capabilities alongside primary CMC storage.
    All operations are non-breaking and can be disabled without affecting CMC.
    
    Example:
        >>> integration = CMC_HoloIntegration()
        >>> if integration.is_enabled():
        ...     integration.store_atom(atom_dict, semantic_id)
        ...     results = integration.retrieve_associative(partial_query)
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        enable: Optional[bool] = None,
    ):
        """Initialize CMC holographic integration.
        
        Args:
            dimension: Dimensionality of holographic vectors
            enable: Override global config (None = use ENABLE_HOLOGRAPHIC_MEMORY)
        """
        self.enabled = enable if enable is not None else ENABLE_HOLOGRAPHIC_MEMORY
        self.dimension = dimension
        
        if self.enabled:
            self.holo_memory = AIMO_HoloMemory(dimension=dimension)
            self.vectorizer = MemoryAtomVectorizer(dimension=dimension)
            # Mapping: semantic_id -> (label_vector, memory_id)
            self.semantic_id_registry: Dict[str, Tuple[NDArray[np.float64], str]] = {}
            logger.info("CMC holographic memory integration ENABLED")
        else:
            self.holo_memory = None
            self.vectorizer = None
            self.semantic_id_registry = {}
            logger.debug("CMC holographic memory integration DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if holographic memory is enabled."""
        return self.enabled and self.holo_memory is not None
    
    def store_atom(
        self,
        atom: Dict[str, Any],
        semantic_id: str,
    ) -> Optional[str]:
        """Store memory atom in holographic memory (experimental/additive).
        
        This is called AFTER primary CMC storage succeeds. If this fails,
        primary CMC storage is unaffected.
        
        Args:
            atom: Memory atom dictionary (from CMC)
            semantic_id: Semantic ID from CMC
            
        Returns:
            Holographic memory ID if successful, None if disabled or failed
            
        Note:
            This is experimental and non-breaking. Primary CMC storage
            continues working normally even if this fails.
        """
        if not self.is_enabled():
            return None
        
        try:
            # Convert atom to vector
            atom_vector = self.vectorizer.vectorize(atom)
            
            # Generate label vector from semantic_id (deterministic)
            label_vector = self._generate_label_vector(semantic_id)
            
            # Encode: bind atom with label
            composite = self.holo_memory.encode(atom_vector, label_vector)
            
            # Store in holographic memory
            memory_id = self.holo_memory.store(composite, label_vector)
            
            # Register semantic_id mapping
            self.semantic_id_registry[semantic_id] = (label_vector, memory_id)
            
            logger.debug(f"Stored atom {semantic_id} in holographic memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            # Log but don't fail - primary CMC storage succeeded
            logger.warning(f"Holographic storage failed for {semantic_id}: {e}")
            return None
    
    def retrieve_exact(
        self,
        semantic_id: str,
    ) -> Optional[Tuple[NDArray[np.float64], float]]:
        """Retrieve atom from holographic memory using exact semantic_id.
        
        Args:
            semantic_id: Semantic ID from CMC
            
        Returns:
            Tuple of (reconstructed_vector, fidelity) if found, None otherwise
            
        Note:
            This provides additional retrieval path. Primary CMC retrieval
            should be used as primary source.
        """
        if not self.is_enabled():
            return None
        
        if semantic_id not in self.semantic_id_registry:
            return None
        
        try:
            label_vector, _ = self.semantic_id_registry[semantic_id]
            reconstructed, fidelity = self.holo_memory.decode(label_vector)
            return reconstructed, fidelity
        except Exception as e:
            logger.warning(f"Holographic retrieval failed for {semantic_id}: {e}")
            return None
    
    def retrieve_associative(
        self,
        partial_query: str,
        top_k: int = 10,
    ) -> List[Tuple[str, float, float]]:
        """Retrieve atoms using associative/fuzzy matching (experimental).
        
        This provides fuzzy matching and pattern completion capabilities
        that primary CMC doesn't have.
        
        Args:
            partial_query: Partial query string (e.g., "memory about authentication")
            top_k: Number of top results to return
            
        Returns:
            List of (semantic_id, correlation_score, fidelity) tuples
            
        Note:
            These are suggestions/candidates. Primary CMC results should
            be checked first.
        """
        if not self.is_enabled():
            return []
        
        try:
            # Convert partial query to vector
            # For now, use simple hash-based vectorization
            # In future, could use semantic embeddings
            query_vector = self._query_to_vector(partial_query)
            
            # Correlate with holographic memory
            correlations = self.holo_memory.correlate(query_vector, top_k=top_k)
            
            # Map memory_ids back to semantic_ids
            results = []
            memory_id_to_semantic = {
                memory_id: semantic_id
                for semantic_id, (_, memory_id) in self.semantic_id_registry.items()
            }
            
            for memory_id, correlation_score in correlations:
                if memory_id in memory_id_to_semantic:
                    semantic_id = memory_id_to_semantic[memory_id]
                    # Get fidelity for this semantic_id
                    retrieved = self.retrieve_exact(semantic_id)
                    fidelity = retrieved[1] if retrieved else 0.0
                    results.append((semantic_id, correlation_score, fidelity))
            
            logger.debug(f"Associative retrieval found {len(results)} candidates for: {partial_query[:50]}")
            return results
            
        except Exception as e:
            logger.warning(f"Associative retrieval failed: {e}")
            return []
    
    def _generate_label_vector(self, semantic_id: str) -> NDArray[np.float64]:
        """Generate deterministic label vector from semantic_id."""
        # Use hash-based vectorization for deterministic labels
        hash_obj = hash(semantic_id)
        np.random.seed(hash_obj % (2**32))  # Deterministic seed
        vector = np.random.randn(self.dimension)
        vector = vector / np.linalg.norm(vector)  # Normalize
        return vector
    
    def _query_to_vector(self, query: str) -> NDArray[np.float64]:
        """Convert query string to vector.
        
        TODO: In future, use semantic embeddings (e.g., all-MiniLM-L6-v2)
        For now, use hash-based vectorization.
        """
        hash_obj = hash(query)
        np.random.seed(hash_obj % (2**32))  # Deterministic seed
        vector = np.random.randn(self.dimension)
        vector = vector / np.linalg.norm(vector)  # Normalize
        return vector
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about holographic memory integration."""
        if not self.is_enabled():
            return {
                "enabled": False,
                "message": "Holographic memory integration is disabled",
            }
        
        holo_stats = self.holo_memory.get_memory_stats()
        return {
            "enabled": True,
            "semantic_id_count": len(self.semantic_id_registry),
            "holo_memory": holo_stats,
        }

