"""
FAISS Index Wrapper - Vector storage and similarity search
"""

import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class FAISSIndex:
    """Wrapper for FAISS vector index with metadata"""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS index
        
        Args:
            dimension: Vector dimension (384 for all-MiniLM-L6-v2)
        """
        self.dimension = dimension
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self._create_index()
    
    def _create_index(self):
        """Create new FAISS index"""
        # Use IndexFlatL2 for exact search (L2 distance)
        self.index = faiss.IndexFlatL2(self.dimension)
    
    def add(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Add vectors to index with metadata
        
        Args:
            vectors: numpy array of shape (n, dimension)
            metadata: List of metadata dicts (one per vector)
        """
        if vectors.shape[0] != len(metadata):
            raise ValueError("Number of vectors must match metadata length")
        
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} != {self.dimension}")
        
        # Ensure float32
        vectors = vectors.astype(np.float32)
        
        # Add to index
        self.index.add(vectors)
        
        # Store metadata
        self.metadata.extend(metadata)
    
    def search(self, query_vector: np.ndarray, k: int = 20) -> tuple:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector (shape: (1, dimension) or (dimension,))
            k: Number of results to return
            
        Returns:
            (distances, indices, metadata)
            - distances: numpy array of shape (1, k)
            - indices: numpy array of shape (1, k)
            - metadata: List of k metadata dicts
        """
        # Reshape if needed
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Ensure float32
        query_vector = query_vector.astype(np.float32)
        
        # Search
        distances, indices = self.index.search(query_vector, min(k, len(self.metadata)))
        
        # Get metadata for results
        result_metadata = [
            self.metadata[idx] for idx in indices[0] if idx < len(self.metadata)
        ]
        
        return distances, indices, result_metadata
    
    def save(self, index_path: str, metadata_path: str):
        """
        Save index and metadata to disk
        
        Args:
            index_path: Path to save FAISS index (.faiss file)
            metadata_path: Path to save metadata (.json file)
        """
        # Create directory if needed
        os.makedirs(Path(index_path).parent, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata as JSON
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
    
    def load(self, index_path: str, metadata_path: str):
        """
        Load index and metadata from disk
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
        """
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found: {index_path}")
        
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
    
    def size(self) -> int:
        """Return number of vectors in index"""
        return self.index.ntotal if self.index else 0
    
    def clear(self):
        """Clear index and metadata"""
        self._create_index()
        self.metadata = []

