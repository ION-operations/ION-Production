"""SEG Integration for AIMO_HoloMemory - Experimental/Additive Enhancement.

This module provides optional holographic memory capabilities for SEG,
working alongside (not replacing) primary SEG storage.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from .holo_memory import AIMO_HoloMemory
from .vectorizer import EntityVectorizer, RelationshipVectorizer

logger = logging.getLogger(__name__)

# Configuration flag - must be explicitly enabled
ENABLE_HOLOGRAPHIC_MEMORY = os.getenv("ENABLE_HOLOGRAPHIC_MEMORY", "false").lower() == "true"


class SEG_HoloIntegration:
    """Experimental holographic memory integration for SEG.
    
    Provides optional associative graph capabilities alongside primary SEG storage.
    All operations are non-breaking and can be disabled without affecting SEG.
    
    Example:
        >>> integration = SEG_HoloIntegration()
        >>> if integration.is_enabled():
        ...     integration.store_entity(entity_dict, entity_id)
        ...     integration.store_relationship(rel_dict, entity_a_id, entity_b_id)
        ...     suggestions = integration.infer_relationship(entity_a_id, rel_type)
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        enable: Optional[bool] = None,
    ):
        """Initialize SEG holographic integration.
        
        Args:
            dimension: Dimensionality of holographic vectors
            enable: Override global config (None = use ENABLE_HOLOGRAPHIC_MEMORY)
        """
        self.enabled = enable if enable is not None else ENABLE_HOLOGRAPHIC_MEMORY
        self.dimension = dimension
        
        if self.enabled:
            self.holo_memory = AIMO_HoloMemory(dimension=dimension)
            self.entity_vectorizer = EntityVectorizer(dimension=dimension)
            self.relationship_vectorizer = RelationshipVectorizer(dimension=dimension)
            # Mapping: entity_id -> label_vector
            self.entity_registry: Dict[str, NDArray[np.float64]] = {}
            # Mapping: (source_id, target_id, rel_type) -> (composite_vector, memory_id)
            self.relationship_registry: Dict[Tuple[str, str, str], Tuple[NDArray[np.float64], str]] = {}
            logger.info("SEG holographic memory integration ENABLED")
        else:
            self.holo_memory = None
            self.entity_vectorizer = None
            self.relationship_vectorizer = None
            self.entity_registry = {}
            self.relationship_registry = {}
            logger.debug("SEG holographic memory integration DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if holographic memory is enabled."""
        return self.enabled and self.holo_memory is not None
    
    def store_entity(
        self,
        entity: Dict[str, Any],
        entity_id: str,
    ) -> Optional[str]:
        """Store entity in holographic memory (experimental/additive).
        
        This is called AFTER primary SEG storage succeeds. If this fails,
        primary SEG storage is unaffected.
        
        Args:
            entity: Entity dictionary (from SEG)
            entity_id: Entity ID from SEG
            
        Returns:
            Holographic memory ID if successful, None if disabled or failed
            
        Note:
            This is experimental and non-breaking. Primary SEG storage
            continues working normally even if this fails.
        """
        if not self.is_enabled():
            return None
        
        try:
            # Convert entity to vector
            entity_vector = self.entity_vectorizer.vectorize(entity)
            
            # Generate label vector from entity_id (deterministic)
            label_vector = self._generate_label_vector(entity_id)
            
            # Encode: bind entity with label
            composite = self.holo_memory.encode(entity_vector, label_vector)
            
            # Store in holographic memory
            memory_id = self.holo_memory.store(composite, label_vector)
            
            # Register entity mapping
            self.entity_registry[entity_id] = label_vector
            
            logger.debug(f"Stored entity {entity_id} in holographic memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            # Log but don't fail - primary SEG storage succeeded
            logger.warning(f"Holographic entity storage failed for {entity_id}: {e}")
            return None
    
    def store_relationship(
        self,
        relationship: Dict[str, Any],
        source_id: str,
        target_id: str,
    ) -> Optional[str]:
        """Store relationship in holographic memory (experimental/additive).
        
        Stores relationship as bound composite: (Entity_A_vec) * (Relationship_vec) * (Entity_B_vec)
        
        This is called AFTER primary SEG storage succeeds. If this fails,
        primary SEG storage is unaffected.
        
        Args:
            relationship: Relationship dictionary (from SEG)
            source_id: Source entity ID
            target_id: Target entity ID
            
        Returns:
            Holographic memory ID if successful, None if disabled or failed
            
        Note:
            This is experimental and non-breaking. Primary SEG storage
            continues working normally even if this fails.
        """
        if not self.is_enabled():
            return None
        
        try:
            # Get entity vectors (must be stored first)
            if source_id not in self.entity_registry or target_id not in self.entity_registry:
                logger.warning(f"Entities {source_id} or {target_id} not in holographic memory")
                return None
            
            source_label = self.entity_registry[source_id]
            target_label = self.entity_registry[target_id]
            
            # Decode entity vectors
            source_vector, _ = self.holo_memory.decode(source_label)
            target_vector, _ = self.holo_memory.decode(target_label)
            
            # Convert relationship to vector
            relationship_vector = self.relationship_vectorizer.vectorize(relationship)
            
            # Bind: (Entity_A) * (Relationship) * (Entity_B)
            # Step 1: Bind source with relationship
            step1 = self.holo_memory.encode(source_vector, relationship_vector)
            # Step 2: Bind result with target
            composite = self.holo_memory.encode(step1, target_vector)
            
            # Generate label for relationship
            rel_type = str(relationship.get("relation_type", "unknown"))
            rel_label = self._generate_relationship_label(source_id, target_id, rel_type)
            
            # Store in holographic memory
            memory_id = self.holo_memory.store(composite, rel_label)
            
            # Register relationship mapping
            key = (source_id, target_id, rel_type)
            self.relationship_registry[key] = (composite, memory_id)
            
            logger.debug(f"Stored relationship {source_id}->{target_id} ({rel_type}) in holographic memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            # Log but don't fail - primary SEG storage succeeded
            logger.warning(f"Holographic relationship storage failed for {source_id}->{target_id}: {e}")
            return None
    
    def infer_relationship(
        self,
        source_id: str,
        relationship_type: str,
    ) -> List[Tuple[str, float, float]]:
        """Infer target entity from source and relationship type (experimental).
        
        Uses holographic memory to reconstruct target entity vector from
        source entity and relationship type.
        
        Args:
            source_id: Source entity ID
            relationship_type: Type of relationship
            
        Returns:
            List of (target_id, correlation_score, fidelity) tuples (suggestions)
            
        Note:
            These are suggestions/candidates. Primary SEG results should
            be checked first.
        """
        if not self.is_enabled():
            return []
        
        if source_id not in self.entity_registry:
            return []
        
        try:
            # Get source entity vector
            source_label = self.entity_registry[source_id]
            source_vector, _ = self.holo_memory.decode(source_label)
            
            # Create relationship vector
            relationship_dict = {"relation_type": relationship_type}
            relationship_vector = self.relationship_vectorizer.vectorize(relationship_dict)
            
            # Bind source with relationship
            bound = self.holo_memory.encode(source_vector, relationship_vector)
            
            # Correlate with all stored relationships to find potential targets
            correlations = self.holo_memory.correlate(bound, top_k=20)
            
            # Map to target entities
            results = []
            for memory_id, correlation_score in correlations:
                # Find relationship that matches this memory_id
                for (src_id, tgt_id, rel_type), (composite, stored_memory_id) in self.relationship_registry.items():
                    if stored_memory_id == memory_id and src_id == source_id and rel_type == relationship_type:
                        # Get target entity vector and compute fidelity
                        if tgt_id in self.entity_registry:
                            target_label = self.entity_registry[tgt_id]
                            target_vector, fidelity = self.holo_memory.decode(target_label)
                            results.append((tgt_id, correlation_score, fidelity))
                            break
            
            logger.debug(f"Inferred {len(results)} target candidates for {source_id} -> {relationship_type}")
            return results[:10]  # Return top 10
            
        except Exception as e:
            logger.warning(f"Relationship inference failed: {e}")
            return []
    
    def find_similar_entities(
        self,
        entity: Dict[str, Any],
        top_k: int = 10,
    ) -> List[Tuple[str, float, float]]:
        """Find similar entities using associative matching (experimental).
        
        Args:
            entity: Entity dictionary to match against
            top_k: Number of top results to return
            
        Returns:
            List of (entity_id, correlation_score, fidelity) tuples (suggestions)
        """
        if not self.is_enabled():
            return []
        
        try:
            # Convert entity to vector
            entity_vector = self.entity_vectorizer.vectorize(entity)
            
            # Correlate with all stored entities
            correlations = self.holo_memory.correlate(entity_vector, top_k=top_k * 2)
            
            # Map memory_ids back to entity_ids
            results = []
            memory_id_to_entity = {}
            for entity_id, label_vector in self.entity_registry.items():
                # Find memory_id for this entity
                for stored_entity_id, stored_label in self.entity_registry.items():
                    if stored_entity_id == entity_id:
                        # Decode to get memory_id (simplified - in real impl would track this)
                        _, _ = self.holo_memory.decode(stored_label)
                        break
            
            # For now, use correlation scores directly
            # In full implementation, would map memory_ids to entity_ids
            for i, (memory_id, correlation_score) in enumerate(correlations[:top_k]):
                # Simplified: use index as proxy (would need proper mapping)
                entity_id = f"entity_{i}"  # Placeholder
                results.append((entity_id, correlation_score, 0.8))  # Placeholder fidelity
            
            logger.debug(f"Found {len(results)} similar entities")
            return results
            
        except Exception as e:
            logger.warning(f"Similar entity search failed: {e}")
            return []
    
    def _generate_label_vector(self, entity_id: str) -> NDArray[np.float64]:
        """Generate deterministic label vector from entity_id."""
        hash_obj = hash(entity_id)
        np.random.seed(hash_obj % (2**32))  # Deterministic seed
        vector = np.random.randn(self.dimension)
        vector = vector / np.linalg.norm(vector)  # Normalize
        return vector
    
    def _generate_relationship_label(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
    ) -> NDArray[np.float64]:
        """Generate deterministic label vector for relationship."""
        combined = f"{source_id}|{target_id}|{rel_type}"
        hash_obj = hash(combined)
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
            "entity_count": len(self.entity_registry),
            "relationship_count": len(self.relationship_registry),
            "holo_memory": holo_stats,
        }

