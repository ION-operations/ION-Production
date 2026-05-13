"""
Embedding Generator for MCP RAG Proxy

Generates high-quality embeddings for MCP tools using sentence-transformers.
Integrates with existing HHNI embedding infrastructure for consistency.

Author: Solo
Date: 2025-10-30
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Try to use HHNI's embedding utilities for consistency
try:
    from hhni.embeddings import encode_text, encode_texts, get_model
    USE_HHNI_EMBEDDINGS = True
except ImportError:
    USE_HHNI_EMBEDDINGS = False

logger = logging.getLogger(__name__)

# Use same model as HHNI for consistency
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@dataclass
class ToolEmbeddingInput:
    """Input for generating tool embeddings"""
    tool_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    context_keywords: List[str]
    usage_examples: Optional[List[str]] = None
    related_tools: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    consciousness_relevance: float = 0.5


class EmbeddingGenerator:
    """Generate embeddings for MCP tools using sentence-transformers"""
    
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialize embedding generator
        
        Args:
            model_name: Sentence-transformer model name (default: all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load embedding model"""
        if USE_HHNI_EMBEDDINGS:
            # Use HHNI's cached model for consistency
            try:
                self.model = get_model()
                logger.info(f"Using HHNI embedding model: {MODEL_NAME}")
                return
            except Exception as e:
                logger.warning(f"Failed to use HHNI embeddings, falling back to direct load: {e}")
        
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"Model loaded: {self.model_name} (dim={self.model.get_sentence_embedding_dimension()})")
    
    def build_embedding_text(self, tool: ToolEmbeddingInput) -> str:
        """Build comprehensive text for embedding
        
        Combines tool metadata into a single text string optimized for semantic search.
        Uses weighted composition to emphasize important fields.
        
        Args:
            tool: Tool embedding input
            
        Returns:
            Combined text string for embedding
        """
        # Build weighted text parts
        parts = []
        
        # Name (2× weight - most important)
        parts.extend([f"Tool: {tool.name}"] * 2)
        
        # Description (1× weight)
        parts.append(f"Description: {tool.description}")
        
        # Tags (1× weight)
        if tool.tags:
            parts.append(f"Tags: {', '.join(tool.tags)}")
        
        # Context keywords (1× weight)
        if tool.context_keywords:
            parts.append(f"Context: {', '.join(tool.context_keywords)}")
        
        # Usage examples (1.5× weight - highly relevant)
        if tool.usage_examples:
            for example in tool.usage_examples[:3]:  # Limit to top 3
                parts.append(f"Example: {example}")
        
        # Category (1× weight)
        parts.append(f"Category: {tool.category}")
        
        # Related tools (0.5× weight)
        if tool.related_tools:
            parts.append(f"Related: {', '.join(tool.related_tools[:5])}")  # Limit to top 5
        
        # Dependencies (0.5× weight)
        if tool.dependencies:
            parts.append(f"Dependencies: {', '.join(tool.dependencies)}")
        
        return "\n".join(parts)
    
    def generate_embedding(self, tool: ToolEmbeddingInput) -> np.ndarray:
        """Generate embedding vector for a tool
        
        Args:
            tool: Tool embedding input
            
        Returns:
            Embedding vector (numpy array)
        """
        text = self.build_embedding_text(tool)
        
        if USE_HHNI_EMBEDDINGS:
            # Use HHNI's encoding function
            embedding = encode_text(text)
            return np.array(embedding)
        else:
            # Use direct model encoding
            embedding = self.model.encode(text, show_progress_bar=False)
            return embedding
    
    def generate_embeddings_batch(
        self, 
        tools: List[ToolEmbeddingInput],
        batch_size: int = 32
    ) -> List[np.ndarray]:
        """Generate embeddings for multiple tools in batches
        
        Args:
            tools: List of tool embedding inputs
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        texts = [self.build_embedding_text(tool) for tool in tools]
        
        if USE_HHNI_EMBEDDINGS:
            # Use HHNI's batch encoding
            embeddings = encode_texts(texts)
            return [np.array(emb) for emb in embeddings]
        else:
            # Use direct model batch encoding
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False
            )
            return [emb for emb in embeddings]
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension
        
        Returns:
            Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return EMBEDDING_DIM


def extract_tool_metadata_from_json(
    metadata_path: str = "tools_metadata.json"
) -> List[ToolEmbeddingInput]:
    """Extract tool metadata from JSON file
    
    Args:
        metadata_path: Path to tools_metadata.json
        
    Returns:
        List of ToolEmbeddingInput objects
    """
    import json
    from pathlib import Path
    
    path = Path(metadata_path)
    if not path.exists():
        logger.warning(f"Metadata file not found: {metadata_path}")
        return []
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    tools = []
    for tool_id, tool_data in data.items():
        tool = ToolEmbeddingInput(
            tool_id=tool_id,
            name=tool_data.get('name', tool_id),
            description=tool_data.get('description', ''),
            category=tool_data.get('category', 'unknown'),
            tags=tool_data.get('tags', []),
            context_keywords=tool_data.get('context_keywords', []),
            usage_examples=tool_data.get('usage_examples'),
            related_tools=tool_data.get('related_tools'),
            dependencies=tool_data.get('dependencies', []),
            consciousness_relevance=tool_data.get('consciousness_relevance', 0.5)
        )
        tools.append(tool)
    
    logger.info(f"Extracted {len(tools)} tools from {metadata_path}")
    return tools

