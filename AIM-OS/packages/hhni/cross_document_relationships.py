"""Cross-document relationship detection and tracking.

Detects semantic relationships across documents to enable narrative context
and symbolic meaning accumulation.
"""

from __future__ import annotations

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import logging

from packages.seg.seg_graph import SEGraph
from packages.seg.models import Entity, Relation, RelationType

logger = logging.getLogger(__name__)


class CrossDocumentRelationshipDetector:
    """Detects and tracks semantic relationships across documents.
    
    Enables:
    - Semantic similarity detection (embedding-based)
    - Narrative context tracking (story-level relationships)
    - Symbolic meaning accumulation (meaning over time)
    """
    
    def __init__(
        self,
        seg_graph: SEGraph,
        similarity_threshold: float = 0.75,
        narrative_threshold: float = 0.80,
    ):
        """Initialize cross-document relationship detector.
        
        Args:
            seg_graph: SEG graph to add relations to
            similarity_threshold: Minimum similarity for semantic relationships (0-1)
            narrative_threshold: Minimum confidence for narrative context (0-1)
        """
        self.seg_graph = seg_graph
        self.similarity_threshold = similarity_threshold
        self.narrative_threshold = narrative_threshold
    
    def detect_semantic_relationships(
        self,
        source_entity: Entity,
        target_entities: List[Entity],
        source_doc_id: str,
        target_doc_ids: List[str],
    ) -> List[Relation]:
        """Detect semantic relationships between entities across documents.
        
        Args:
            source_entity: Source entity (from document A)
            target_entities: Candidate target entities (from document B, C, etc.)
            source_doc_id: Source document ID
            target_doc_ids: Target document IDs (one per target entity)
            
        Returns:
            List of detected relations
        """
        relations = []
        
        try:
            # Get embeddings for similarity comparison
            source_embedding = self._get_entity_embedding(source_entity)
            
            for target_entity, target_doc_id in zip(target_entities, target_doc_ids):
                # Skip if same document
                if target_doc_id == source_doc_id:
                    continue
                
                # Get target embedding
                target_embedding = self._get_entity_embedding(target_entity)
                
                if source_embedding is None or target_embedding is None:
                    continue
                
                # Compute semantic similarity
                similarity = self._cosine_similarity(source_embedding, target_embedding)
                
                if similarity >= self.similarity_threshold:
                    # Create semantically related relation
                    relation = Relation(
                        source_id=source_entity.id,
                        target_id=target_entity.id,
                        relation_type=RelationType.SEMANTICALLY_RELATED,
                        confidence=similarity,
                        attributes={
                            "source_doc": source_doc_id,
                            "target_doc": target_doc_id,
                            "similarity_score": similarity,
                            "detection_method": "embedding_similarity",
                        },
                        tags=["cross_document", "semantic"],
                        source=f"cross_doc_detector:{source_doc_id}",
                    )
                    relations.append(relation)
        
        except Exception as exc:
            logger.warning(
                "cross_doc.semantic.detection.failed",
                extra={
                    "source_entity": source_entity.id,
                    "error": str(exc),
                },
            )
        
        return relations
    
    def track_narrative_context(
        self,
        entity: Entity,
        context_entities: List[Entity],
        document_ids: List[str],
    ) -> List[Relation]:
        """Track narrative context relationships.
        
        Example: "river bank" → "love" (narrative context from story)
        
        Args:
            entity: Entity to find narrative context for
            context_entities: Candidate context entities
            document_ids: Document IDs for context entities
            
        Returns:
            List of narrative context relations
        """
        relations = []
        
        try:
            # Check for narrative patterns
            # This is a simplified implementation - could be enhanced with LLM analysis
            for context_entity, doc_id in zip(context_entities, document_ids):
                # Check if entities are in narrative context
                # (e.g., same document, similar themes, co-occurrence patterns)
                narrative_score = self._compute_narrative_score(entity, context_entity, doc_id)
                
                if narrative_score >= self.narrative_threshold:
                    relation = Relation(
                        source_id=entity.id,
                        target_id=context_entity.id,
                        relation_type=RelationType.NARRATIVE_CONTEXT,
                        confidence=narrative_score,
                        attributes={
                            "context_doc": doc_id,
                            "narrative_score": narrative_score,
                            "context_type": "symbolic",  # Could be: symbolic, thematic, motif
                        },
                        tags=["cross_document", "narrative"],
                        source="cross_doc_detector:narrative",
                    )
                    relations.append(relation)
        
        except Exception as exc:
            logger.warning(
                "cross_doc.narrative.detection.failed",
                extra={
                    "entity": entity.id,
                    "error": str(exc),
                },
            )
        
        return relations
    
    def accumulate_symbolic_meaning(
        self,
        entity: Entity,
        references: List[Tuple[Entity, str, float]],  # (entity, doc_id, timestamp)
    ) -> Entity:
        """Accumulate symbolic meaning over time.
        
        Example: "river bank" first mentioned → later references accumulate meaning
        
        Args:
            entity: Entity to accumulate meaning for
            references: List of (referencing_entity, doc_id, timestamp) tuples
            
        Returns:
            Updated entity with accumulated meaning
        """
        try:
            # Track first mention
            if "first_mention" not in entity.attributes:
                entity.attributes["first_mention"] = datetime.now(timezone.utc).isoformat()
                entity.attributes["reference_count"] = 0
                entity.attributes["symbolic_weight"] = 0.0
            
            # Update reference count
            entity.attributes["reference_count"] = entity.attributes.get("reference_count", 0) + len(references)
            
            # Accumulate symbolic weight (increases with references)
            base_weight = 0.3
            weight_increment = 0.1
            entity.attributes["symbolic_weight"] = min(
                1.0,
                base_weight + (entity.attributes["reference_count"] * weight_increment)
            )
            
            # Create accumulates_meaning relations
            for ref_entity, doc_id, timestamp in references:
                # Ensure reference entity exists in SEG before creating relation
                if self.seg_graph.get_entity(ref_entity.id) is None:
                    try:
                        self.seg_graph.add_entity(ref_entity)
                    except Exception:
                        # If adding fails, skip relation creation for this reference
                        continue
                relation = Relation(
                    source_id=ref_entity.id,
                    target_id=entity.id,
                    relation_type=RelationType.ACCUMULATES_MEANING,
                    confidence=entity.attributes["symbolic_weight"],
                    attributes={
                        "reference_doc": doc_id,
                        "timestamp": timestamp,
                        "accumulated_weight": entity.attributes["symbolic_weight"],
                    },
                    tags=["cross_document", "symbolic", "accumulation"],
                    source="cross_doc_detector:accumulation",
                )
                self.seg_graph.add_relation(relation)
        
        except Exception as exc:
            logger.warning(
                "cross_doc.accumulation.failed",
                extra={
                    "entity": entity.id,
                    "error": str(exc),
                },
            )
        
        return entity
    
    def _get_entity_embedding(self, entity: Entity) -> Optional[List[float]]:
        """Get embedding for entity.
        
        Tries to get embedding from entity attributes, or computes from name/type.
        
        Args:
            entity: Entity to get embedding for
            
        Returns:
            Embedding vector or None
        """
        # Try to get existing embedding from attributes
        if "embedding" in entity.attributes:
            embedding = entity.attributes["embedding"]
            if isinstance(embedding, list) and len(embedding) > 0:
                return embedding
        
        # Try to get from name embedding
        if "name_embedding" in entity.attributes:
            embedding = entity.attributes["name_embedding"]
            if isinstance(embedding, list) and len(embedding) > 0:
                return embedding
        
        # For now, return None (would need to compute embedding)
        # In production, this would use sentence-transformers or similar
        return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        if len(vec1) != len(vec2):
            return 0.0
        
        # Compute dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Compute magnitudes
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        
        # Cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return (similarity + 1.0) / 2.0
    
    def _compute_narrative_score(
        self,
        entity: Entity,
        context_entity: Entity,
        doc_id: str,
    ) -> float:
        """Compute narrative context score between two entities.
        
        Simplified implementation - could be enhanced with:
        - LLM-based narrative analysis
        - Co-occurrence patterns
        - Thematic similarity
        - Document structure analysis
        
        Args:
            entity: Source entity
            context_entity: Context entity
            doc_id: Document ID
            
        Returns:
            Narrative score (0-1)
        """
        # Simplified: use semantic similarity as proxy for narrative context
        # In production, this would use more sophisticated narrative analysis
        source_embedding = self._get_entity_embedding(entity)
        context_embedding = self._get_entity_embedding(context_entity)
        
        if source_embedding is None or context_embedding is None:
            return 0.0
        
        similarity = self._cosine_similarity(source_embedding, context_embedding)
        
        # Boost score if entities are in same document (narrative context)
        if entity.attributes.get("atom_id") == context_entity.attributes.get("atom_id"):
            similarity = min(1.0, similarity * 1.2)
        
        return similarity

