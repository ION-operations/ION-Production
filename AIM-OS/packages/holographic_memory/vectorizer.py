"""Vectorization layer for converting AIM-OS data to high-dimensional vectors.

Converts structured AIM-OS data (PLIx intents, entities, relationships, memory atoms)
into high-dimensional vectors suitable for holographic encoding.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Optional

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


class BaseVectorizer:
    """Base class for vectorizers."""
    
    def __init__(self, dimension: int = 10000, normalize: bool = True):
        """Initialize vectorizer.
        
        Args:
            dimension: Target vector dimension
            normalize: Whether to normalize output vectors
        """
        self.dimension = dimension
        self.normalize = normalize
    
    def _normalize(self, vector: NDArray[np.float64]) -> NDArray[np.float64]:
        """Normalize vector to unit length."""
        if self.normalize:
            norm = np.linalg.norm(vector)
            if norm > 1e-10:
                return vector / norm
        return vector
    
    def _hash_to_vector(self, data: str, seed: Optional[int] = None) -> NDArray[np.float64]:
        """Convert hash to deterministic high-dimensional vector.
        
        Args:
            data: String data to hash
            seed: Optional seed for reproducibility
            
        Returns:
            High-dimensional vector
        """
        # Create hash
        hash_obj = hashlib.sha256(data.encode())
        if seed is not None:
            hash_obj.update(str(seed).encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to vector (deterministic)
        vector = np.zeros(self.dimension, dtype=np.float64)
        for i in range(min(len(hash_bytes), self.dimension)):
            vector[i] = (hash_bytes[i] - 128) / 128.0  # Normalize to [-1, 1]
        
        # Fill remaining dimensions with deterministic pattern
        for i in range(len(hash_bytes), self.dimension):
            vector[i] = np.sin(i * 0.1) * 0.5  # Deterministic pattern
        
        return self._normalize(vector)


class PLIxVectorizer(BaseVectorizer):
    """Vectorizer for PLIx intents."""
    
    def vectorize(self, plix_intent: Dict[str, Any]) -> NDArray[np.float64]:
        """Convert PLIx intent to high-dimensional vector.
        
        Args:
            plix_intent: PLIx intent dictionary with keys like 'goal', 'process', etc.
            
        Returns:
            High-dimensional vector representing the PLIx intent
        """
        # Extract key components
        goal = str(plix_intent.get("goal", ""))
        process = str(plix_intent.get("process", ""))
        constraint = str(plix_intent.get("constraint", ""))
        effect = str(plix_intent.get("effect", ""))
        
        # Combine into single string
        combined = f"{goal}|{process}|{constraint}|{effect}"
        
        # Hash to vector
        vector = self._hash_to_vector(combined)
        
        logger.debug(f"Vectorized PLIx intent: {len(combined)} chars -> {self.dimension}D vector")
        
        return vector


class EntityVectorizer(BaseVectorizer):
    """Vectorizer for SEG entities."""
    
    def vectorize(self, entity: Dict[str, Any]) -> NDArray[np.float64]:
        """Convert SEG entity to high-dimensional vector.
        
        Args:
            entity: Entity dictionary with keys like 'id', 'type', 'name', 'attributes'
            
        Returns:
            High-dimensional vector representing the entity
        """
        # Extract key components
        entity_id = str(entity.get("id", ""))
        entity_type = str(entity.get("type", ""))
        name = str(entity.get("name", ""))
        attributes = str(entity.get("attributes", ""))
        
        # Combine into single string
        combined = f"{entity_id}|{entity_type}|{name}|{attributes}"
        
        # Hash to vector
        vector = self._hash_to_vector(combined)
        
        logger.debug(f"Vectorized entity: {entity_id} -> {self.dimension}D vector")
        
        return vector


class RelationshipVectorizer(BaseVectorizer):
    """Vectorizer for SEG relationships."""
    
    def vectorize(self, relationship: Dict[str, Any]) -> NDArray[np.float64]:
        """Convert SEG relationship to high-dimensional vector.
        
        Args:
            relationship: Relationship dictionary with keys like 'source_id', 'target_id', 'type'
            
        Returns:
            High-dimensional vector representing the relationship
        """
        # Extract key components
        source_id = str(relationship.get("source_id", ""))
        target_id = str(relationship.get("target_id", ""))
        relation_type = str(relationship.get("relation_type", ""))
        confidence = str(relationship.get("confidence", ""))
        
        # Combine into single string
        combined = f"{source_id}|{target_id}|{relation_type}|{confidence}"
        
        # Hash to vector
        vector = self._hash_to_vector(combined)
        
        logger.debug(f"Vectorized relationship: {source_id}->{target_id} -> {self.dimension}D vector")
        
        return vector


class MemoryAtomVectorizer(BaseVectorizer):
    """Vectorizer for CMC memory atoms."""
    
    def vectorize(self, atom: Dict[str, Any]) -> NDArray[np.float64]:
        """Convert CMC memory atom to high-dimensional vector.
        
        Args:
            atom: Atom dictionary with keys like 'id', 'modality', 'content', 'tags'
            
        Returns:
            High-dimensional vector representing the memory atom
        """
        # Extract key components
        atom_id = str(atom.get("id", ""))
        modality = str(atom.get("modality", ""))
        content = str(atom.get("content", {}).get("inline", ""))
        tags = str(atom.get("tags", []))
        
        # Combine into single string
        combined = f"{atom_id}|{modality}|{content[:500]}|{tags}"  # Limit content length
        
        # Hash to vector
        vector = self._hash_to_vector(combined)
        
        logger.debug(f"Vectorized memory atom: {atom_id} -> {self.dimension}D vector")
        
        return vector

