"""
Vector Index for MCP RAG Proxy

Manages FAISS index for fast similarity search of MCP tool embeddings.

Author: Solo
Date: 2025-10-30
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

try:
    from .embedding_generator import ToolEmbeddingInput, EmbeddingGenerator
except ImportError:
    from embedding_generator import ToolEmbeddingInput, EmbeddingGenerator

logger = logging.getLogger(__name__)


class VectorIndex:
    """FAISS-based vector index for MCP tool embeddings"""
    
    def __init__(
        self,
        embedding_dim: int = 384,
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None
    ):
        """Initialize vector index
        
        Args:
            embedding_dim: Embedding dimension (384 for all-MiniLM-L6-v2)
            index_path: Path to save/load FAISS index (optional)
            metadata_path: Path to save/load tool metadata (optional)
        """
        self.embedding_dim = embedding_dim
        self.index_path = Path(index_path) if index_path else Path("tool_embeddings.faiss")
        self.metadata_path = Path(metadata_path) if metadata_path else Path("tool_metadata.pkl")
        
        self.index: Optional[faiss.Index] = None
        self.tool_metadata: List[ToolEmbeddingInput] = []
        self.tool_id_map: Dict[int, str] = {}  # FAISS index ID -> tool_id
        
        if not FAISS_AVAILABLE:
            logger.warning(
                "FAISS not available. Install with: pip install faiss-cpu"
            )
    
    def build_index(
        self,
        tools: List[ToolEmbeddingInput],
        embeddings: Optional[List[np.ndarray]] = None,
        generator: Optional[EmbeddingGenerator] = None
    ):
        """Build FAISS index from tool embeddings
        
        Args:
            tools: List of tool metadata
            embeddings: Pre-computed embeddings (optional)
            generator: EmbeddingGenerator instance (optional, for generating embeddings)
        """
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available. Install with: pip install faiss-cpu")
        
        if embeddings is None:
            if generator is None:
                generator = EmbeddingGenerator()
            logger.info(f"Generating embeddings for {len(tools)} tools...")
            embeddings = generator.generate_embeddings_batch(tools)
        
        # Ensure embeddings are numpy arrays
        embeddings_array = np.array([emb.flatten() for emb in embeddings]).astype('float32')
        
        # Normalize embeddings for cosine similarity (more accurate than L2)
        faiss.normalize_L2(embeddings_array)
        
        # Build FAISS index (IndexFlatIP for inner product = cosine similarity)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings_array)
        
        # Store metadata
        self.tool_metadata = tools
        self.tool_id_map = {i: tool.tool_id for i, tool in enumerate(tools)}
        
        logger.info(f"Built FAISS index with {self.index.ntotal} tools")
    
    def save(self):
        """Save index and metadata to disk"""
        if self.index is None:
            logger.warning("No index to save")
            return
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        logger.info(f"Saved FAISS index to {self.index_path}")
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'tools': self.tool_metadata,
                'tool_id_map': self.tool_id_map,
                'embedding_dim': self.embedding_dim
            }, f)
        logger.info(f"Saved metadata to {self.metadata_path}")
    
    def load(self) -> bool:
        """Load index and metadata from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS not available")
            return False
        
        if not self.index_path.exists():
            logger.warning(f"Index file not found: {self.index_path}")
            return False
        
        if not self.metadata_path.exists():
            logger.warning(f"Metadata file not found: {self.metadata_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            logger.info(f"Loaded FAISS index from {self.index_path} ({self.index.ntotal} tools)")
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.tool_metadata = data['tools']
                self.tool_id_map = data['tool_id_map']
                self.embedding_dim = data.get('embedding_dim', self.embedding_dim)
            logger.info(f"Loaded metadata from {self.metadata_path}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """Search for similar tools
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (tool_id, similarity_score) tuples, sorted by similarity
        """
        if self.index is None:
            logger.error("Index not built or loaded")
            return []
        
        # Normalize query embedding
        query_array = query_embedding.flatten().astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_array)
        
        # Search
        similarities, indices = self.index.search(query_array, k)
        
        # Format results
        results = []
        for idx, sim in zip(indices[0], similarities[0]):
            if idx >= 0 and sim >= threshold:
                tool_id = self.tool_id_map.get(idx, f"unknown_{idx}")
                results.append((tool_id, float(sim)))
        
        return results
    
    def get_tool_by_id(self, tool_id: str) -> Optional[ToolEmbeddingInput]:
        """Get tool metadata by tool ID
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            ToolEmbeddingInput or None if not found
        """
        for tool in self.tool_metadata:
            if tool.tool_id == tool_id:
                return tool
        return None
    
    def get_all_tools(self) -> List[ToolEmbeddingInput]:
        """Get all tool metadata
        
        Returns:
            List of all tools
        """
        return self.tool_metadata
    
    def size(self) -> int:
        """Get number of tools in index
        
        Returns:
            Number of tools
        """
        if self.index:
            return self.index.ntotal
        return len(self.tool_metadata)

