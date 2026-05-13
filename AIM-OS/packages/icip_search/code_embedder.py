"""
Code Embedder - Generate embeddings for code

Uses sentence-transformers (same as HHNI) for consistency.
"""

import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer


class CodeEmbedder:
    """Generates embeddings for code using sentence-transformers"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedder
        
        Args:
            model_name: sentence-transformers model name
                       Default: 'all-MiniLM-L6-v2' (384d, same as HHNI)
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.dimension = 384 if 'MiniLM-L6' in model_name else 768
    
    def _ensure_model_loaded(self):
        """Lazy load model on first use"""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
    
    def embed(self, code: str) -> np.ndarray:
        """
        Generate embedding for single code snippet
        
        Args:
            code: Code string to embed
            
        Returns:
            numpy array of shape (384,) or (768,) depending on model
        """
        self._ensure_model_loaded()
        
        if not code or not code.strip():
            # Return zero vector for empty code
            return np.zeros(self.dimension, dtype=np.float32)
        
        # Generate embedding
        embedding = self.model.encode(code, convert_to_numpy=True)
        
        return embedding.astype(np.float32)
    
    def embed_batch(self, codes: List[str]) -> np.ndarray:
        """
        Generate embeddings for batch of code snippets
        
        Args:
            codes: List of code strings
            
        Returns:
            numpy array of shape (n, 384) or (n, 768)
        """
        self._ensure_model_loaded()
        
        if not codes:
            return np.zeros((0, self.dimension), dtype=np.float32)
        
        # Handle empty strings
        codes = [code if code and code.strip() else " " for code in codes]
        
        # Batch encode (more efficient)
        embeddings = self.model.encode(
            codes,
            convert_to_numpy=True,
            show_progress_bar=len(codes) > 100  # Show progress for large batches
        )
        
        return embeddings.astype(np.float32)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for search query
        
        Alias for embed() but makes usage clearer
        """
        return self.embed(query)

