"""Semantic block models for pre-organized content.

Semantic blocks represent pre-computed clusters of related content,
enabling retrieval of organized blocks instead of isolated chunks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class SemanticBlock(BaseModel):
    """A pre-organized semantic block containing related content.
    
    Semantic blocks are created at index time to enable retrieval
    of pre-organized content instead of isolated chunks.
    """
    
    id: str = Field(..., description="Unique block identifier")
    block_type: str = Field(..., description="Type of block: thematic, narrative, conceptual, morphological")
    content_ids: List[str] = Field(default_factory=list, description="HHNI node IDs or CMC atom IDs in this block")
    relationships: Dict[str, float] = Field(default_factory=dict, description="Relationship strengths to other blocks (block_id -> similarity)")
    centroid_embedding: Optional[List[float]] = Field(None, description="Block centroid embedding for similarity calculation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Block creation timestamp")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional block metadata")
    
    # Provenance
    atom_id: Optional[str] = Field(None, description="Source CMC atom ID")
    document_id: Optional[str] = Field(None, description="Source document ID")
    
    # Statistics
    node_count: int = Field(0, description="Number of nodes in this block")
    avg_similarity: float = Field(0.0, description="Average similarity within block")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "block_abc123",
                "block_type": "thematic",
                "content_ids": ["node_1", "node_2", "node_3"],
                "relationships": {"block_xyz789": 0.85},
                "centroid_embedding": [0.5, 0.3, 0.2, 0.1],
                "created_at": "2025-01-27T12:00:00Z",
                "attributes": {"theme": "river", "context": "narrative"},
                "atom_id": "atom_123",
                "document_id": "doc_1",
                "node_count": 3,
                "avg_similarity": 0.88,
            }
        }
    }


class BlockType:
    """Block type constants."""
    THEMATIC = "thematic"  # Content with same theme/topic
    NARRATIVE = "narrative"  # Content with narrative context
    CONCEPTUAL = "conceptual"  # Content with same concept
    MORPHOLOGICAL = "morphological"  # Content with morphological relationships
    CROSS_DOCUMENT = "cross_document"  # Content across documents (Phase 2)
    MIXED = "mixed"  # Mixed types


class BlockRelationship(BaseModel):
    """Relationship between two semantic blocks."""
    
    source_block_id: str = Field(..., description="Source block ID")
    target_block_id: str = Field(..., description="Target block ID")
    relationship_type: str = Field(..., description="Type of relationship: semantic, narrative, morphological, etc.")
    similarity: float = Field(..., description="Similarity score (0-1)")
    confidence: float = Field(1.0, description="Confidence in relationship (0-1)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional relationship metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "source_block_id": "block_abc123",
                "target_block_id": "block_xyz789",
                "relationship_type": "semantic",
                "similarity": 0.85,
                "confidence": 0.90,
                "attributes": {"cross_document": True},
                "created_at": "2025-01-27T12:00:00Z",
            }
        }
    }


def create_block_id(block_type: str, atom_id: str, index: int) -> str:
    """Create a unique block ID.
    
    Args:
        block_type: Type of block
        atom_id: Source atom ID
        index: Block index within document
        
    Returns:
        Unique block ID
    """
    return f"block_{block_type}_{atom_id}_{index}"


def validate_block(block: SemanticBlock) -> bool:
    """Validate a semantic block.
    
    Args:
        block: Block to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not block.id:
        return False
    
    if not block.block_type:
        return False
    
    if block.block_type not in [
        BlockType.THEMATIC,
        BlockType.NARRATIVE,
        BlockType.CONCEPTUAL,
        BlockType.MORPHOLOGICAL,
        BlockType.CROSS_DOCUMENT,
        BlockType.MIXED,
    ]:
        return False
    
    if len(block.content_ids) == 0:
        return False
    
    if block.centroid_embedding and len(block.centroid_embedding) == 0:
        return False
    
    return True

