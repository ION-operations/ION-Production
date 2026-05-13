"""Semantic block organizer for pre-organized content.

Organizes content into semantic blocks at index time to enable
retrieval of pre-organized blocks instead of isolated chunks.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

from .models import HHNINode
from .semantic_blocks import SemanticBlock, BlockType, create_block_id, validate_block
from .embeddings import encode_text, encode_texts
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from packages.seg.seg_graph import SEGraph

logger = logging.getLogger(__name__)


class SemanticBlockOrganizer:
    """Organizes content into semantic blocks during indexing.
    
    Clusters related content at index time to enable retrieval
    of pre-organized blocks instead of isolated chunks.
    """
    
    def __init__(
        self,
        seg_graph: "SEGraph",
        cluster_threshold: float = 0.80,
        max_block_size: int = 10,
        min_block_size: int = 2,
    ):
        """Initialize semantic block organizer.
        
        Args:
            seg_graph: SEG graph for relationship tracking
            cluster_threshold: Minimum similarity for clustering (0-1)
            max_block_size: Maximum nodes per block
            min_block_size: Minimum nodes per block
        """
        self.seg_graph = seg_graph
        self.cluster_threshold = cluster_threshold
        self.max_block_size = max_block_size
        self.min_block_size = min_block_size
    
    def organize_into_blocks(
        self,
        nodes: List[HHNINode],
        atom_id: str,
    ) -> List[SemanticBlock]:
        """Organize nodes into semantic blocks.
        
        Args:
            nodes: HHNI nodes to organize
            atom_id: CMC atom ID for provenance
            
        Returns:
            List of semantic blocks
        """
        if not nodes:
            return []
        
        try:
            # Filter to nodes with text content (sentence/word level)
            content_nodes = [
                n for n in nodes
                if n.text and n.level >= 4  # Sentence level and below
            ]
            
            if len(content_nodes) < self.min_block_size:
                # Not enough nodes to form blocks
                return []
            
            # Compute embeddings for all nodes
            node_embeddings = self._compute_node_embeddings(content_nodes)
            
            # Cluster nodes by semantic similarity
            clusters = self._cluster_nodes(content_nodes, node_embeddings)
            
            # Form blocks from clusters
            blocks = []
            for idx, cluster in enumerate(clusters):
                if len(cluster) < self.min_block_size:
                    continue
                
                block = self._form_block(
                    cluster_nodes=cluster,
                    node_embeddings=node_embeddings,
                    block_type=self._infer_block_type(cluster),
                    atom_id=atom_id,
                    block_index=idx,
                )
                
                if validate_block(block):
                    blocks.append(block)
            
            return blocks
        
        except Exception as exc:
            logger.warning(
                "hhni.block.organization.failed",
                extra={
                    "atom_id": atom_id,
                    "node_count": len(nodes),
                    "error": str(exc),
                },
            )
            return []
    
    def pre_compute_relationships(
        self,
        blocks: List[SemanticBlock],
    ) -> Dict[str, Dict[str, float]]:
        """Pre-compute relationships between blocks.
        
        Args:
            blocks: Semantic blocks to compute relationships for
            
        Returns:
            Dictionary mapping block_id → {other_block_id: similarity}
        """
        relationships = {}
        
        try:
            for i, block1 in enumerate(blocks):
                if block1.centroid_embedding is None:
                    continue
                
                block_relations = {}
                
                for j, block2 in enumerate(blocks):
                    if i == j or block2.centroid_embedding is None:
                        continue
                    
                    # Compute similarity between block centroids
                    similarity = self._cosine_similarity(
                        block1.centroid_embedding,
                        block2.centroid_embedding,
                    )
                    
                    if similarity >= self.cluster_threshold:
                        block_relations[block2.id] = similarity
                        
                        # Update block relationships
                        block1.relationships[block2.id] = similarity
                        block2.relationships[block1.id] = similarity
                
                relationships[block1.id] = block_relations
        
        except Exception as exc:
            logger.warning(
                "hhni.block.relationships.failed",
                extra={
                    "block_count": len(blocks),
                    "error": str(exc),
                },
            )
        
        return relationships
    
    def _compute_node_embeddings(
        self,
        nodes: List[HHNINode],
    ) -> Dict[str, List[float]]:
        """Compute embeddings for nodes.
        
        Args:
            nodes: Nodes to compute embeddings for
            
        Returns:
            Dictionary mapping node_id -> embedding
        """
        embeddings = {}
        
        try:
            # Get texts for all nodes
            texts = [n.text for n in nodes if n.text]
            
            if not texts:
                return embeddings
            
            # Compute embeddings in batch
            text_embeddings = encode_texts(texts)
            
            # Map back to nodes
            text_idx = 0
            for node in nodes:
                if node.text:
                    embeddings[node.id] = text_embeddings[text_idx]
                    text_idx += 1
        
        except Exception as exc:
            logger.warning(
                "hhni.block.embeddings.failed",
                extra={
                    "node_count": len(nodes),
                    "error": str(exc),
                },
            )
        
        return embeddings
    
    def _cluster_nodes(
        self,
        nodes: List[HHNINode],
        embeddings: Dict[str, List[float]],
    ) -> List[List[HHNINode]]:
        """Cluster nodes by semantic similarity.
        
        Uses hierarchical clustering with similarity threshold.
        
        Args:
            nodes: Nodes to cluster
            embeddings: Node embeddings
            
        Returns:
            List of clusters (each cluster is a list of nodes)
        """
        if not nodes or not embeddings:
            return []
        
        # Simple clustering: group nodes by similarity
        clusters = []
        unassigned = nodes.copy()
        
        while unassigned:
            # Start new cluster with first unassigned node
            cluster = [unassigned.pop(0)]
            cluster_embedding = embeddings.get(cluster[0].id)
            
            if cluster_embedding is None:
                continue
            
            # Find similar nodes
            remaining = []
            for node in unassigned:
                node_embedding = embeddings.get(node.id)
                if node_embedding is None:
                    remaining.append(node)
                    continue
                
                similarity = self._cosine_similarity(cluster_embedding, node_embedding)
                
                if similarity >= self.cluster_threshold and len(cluster) < self.max_block_size:
                    cluster.append(node)
                else:
                    remaining.append(node)
            
            if len(cluster) >= self.min_block_size:
                clusters.append(cluster)
            
            unassigned = remaining
        
        return clusters
    
    def _form_block(
        self,
        cluster_nodes: List[HHNINode],
        node_embeddings: Dict[str, List[float]],
        block_type: str,
        atom_id: str,
        block_index: int,
    ) -> SemanticBlock:
        """Form a semantic block from a cluster of nodes.
        
        Args:
            cluster_nodes: Nodes in the cluster
            node_embeddings: Node embeddings
            block_type: Type of block
            atom_id: Source atom ID
            block_index: Block index within document
            
        Returns:
            Semantic block
        """
        # Compute block centroid (average of node embeddings)
        centroid_embedding = None
        node_emb_list = [
            node_embeddings.get(node.id)
            for node in cluster_nodes
            if node_embeddings.get(node.id) is not None
        ]
        
        if node_emb_list:
            # Average embeddings
            centroid_embedding = [
                sum(emb[i] for emb in node_emb_list) / len(node_emb_list)
                for i in range(len(node_emb_list[0]))
            ]
        
        # Compute average similarity within block
        avg_similarity = 0.0
        if len(node_emb_list) > 1:
            similarities = []
            for i in range(len(node_emb_list)):
                for j in range(i + 1, len(node_emb_list)):
                    sim = self._cosine_similarity(node_emb_list[i], node_emb_list[j])
                    similarities.append(sim)
            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
        
        # Create block
        block = SemanticBlock(
            id=create_block_id(block_type, atom_id, block_index),
            block_type=block_type,
            content_ids=[node.id for node in cluster_nodes],
            centroid_embedding=centroid_embedding,
            atom_id=atom_id,
            document_id=atom_id,  # Using atom_id as document_id for now
            node_count=len(cluster_nodes),
            avg_similarity=avg_similarity,
            attributes={
                "cluster_size": len(cluster_nodes),
                "created_from": "hhni_indexing",
            },
        )
        
        return block
    
    def _infer_block_type(self, nodes: List[HHNINode]) -> str:
        """Infer block type from nodes.
        
        Args:
            nodes: Nodes in the block
            
        Returns:
            Block type
        """
        # Check for morphological relationships (Phase 1)
        has_morphology = any(
            node.morphology is not None
            for node in nodes
        )
        
        if has_morphology:
            return BlockType.MORPHOLOGICAL
        
        # Check for narrative context (Phase 2)
        # This is simplified - could be enhanced with SEG queries
        if len(nodes) > 3:
            return BlockType.THEMATIC
        
        return BlockType.CONCEPTUAL
    
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

