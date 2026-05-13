"""
Semantic Search Engine - Main orchestrator for ICIP semantic search
"""

import os
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

from .code_chunker import CodeChunker, CodeChunk
from .code_embedder import CodeEmbedder
from .faiss_index import FAISSIndex


@dataclass
class CodeSearchResult:
    """Result from semantic search"""
    file: str
    line: int
    code: str
    context: Optional[str]
    language: str
    type: str
    name: str
    relevance: float  # 0-1
    confidence: float  # 0-1 (normalized within results)
    distance: float  # Raw FAISS distance


class SemanticEngine:
    """Main semantic search engine for code"""
    
    def __init__(
        self,
        codebase_path: str,
        index_dir: Optional[str] = None
    ):
        """
        Initialize semantic search engine
        
        Args:
            codebase_path: Path to codebase root
            index_dir: Directory for index files (default: {codebase}/.icip/)
        """
        self.codebase_path = codebase_path
        self.index_dir = index_dir or os.path.join(codebase_path, '.icip')
        
        # Components
        self.chunker = CodeChunker()
        self.embedder = CodeEmbedder()
        self.index = FAISSIndex(dimension=self.embedder.dimension)
        
        # Paths
        self.index_path = os.path.join(self.index_dir, 'index.faiss')
        self.metadata_path = os.path.join(self.index_dir, 'metadata.json')
        self.chunks_path = os.path.join(self.index_dir, 'chunks.json')
        self.hash_cache_path = os.path.join(self.index_dir, 'hash_cache.json')
        
        # Cache
        self.chunks: List[CodeChunk] = []
        self.hash_cache: dict = {}
        
        # Try to load existing index
        self._try_load_index()
    
    def _try_load_index(self):
        """Try to load existing index"""
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            try:
                self.index.load(self.index_path, self.metadata_path)
                
                # Load chunks
                with open(self.chunks_path, 'r', encoding='utf-8') as f:
                    chunks_data = json.load(f)
                    self.chunks = [
                        CodeChunk(**chunk_data) for chunk_data in chunks_data
                    ]
                
                # Load hash cache
                if os.path.exists(self.hash_cache_path):
                    with open(self.hash_cache_path, 'r') as f:
                        self.hash_cache = json.load(f)
                
                print(f"[ICIP] Loaded existing index with {len(self.chunks)} chunks")
            except Exception as e:
                print(f"[ICIP] Failed to load index: {e}. Will rebuild.")
                self.chunks = []
                self.hash_cache = {}
    
    def index_codebase(
        self,
        languages: Optional[List[str]] = None,
        force_rebuild: bool = False
    ):
        """
        Index entire codebase
        
        Args:
            languages: Languages to index (default: ['py'])
            force_rebuild: Rebuild even if index exists
        """
        if not force_rebuild and self.index.size() > 0:
            print(f"[ICIP] Index already exists ({self.index.size()} chunks). Use force_rebuild=True to rebuild.")
            return
        
        print(f"[ICIP] Indexing codebase: {self.codebase_path}")
        
        # Extract code chunks
        print("[ICIP] Extracting code chunks...")
        self.chunks = self.chunker.chunk_codebase(self.codebase_path, languages)
        print(f"[ICIP] Extracted {len(self.chunks)} code chunks")
        
        if not self.chunks:
            print("[ICIP] No code chunks found!")
            return
        
        # Generate embeddings
        print("[ICIP] Generating embeddings...")
        codes = [chunk.code for chunk in self.chunks]
        embeddings = self.embedder.embed_batch(codes)
        print(f"[ICIP] Generated {len(embeddings)} embeddings")
        
        # Create metadata
        metadata = [self._chunk_to_metadata(chunk) for chunk in self.chunks]
        
        # Add to FAISS index
        print("[ICIP] Building FAISS index...")
        self.index.add(embeddings, metadata)
        print(f"[ICIP] Index built with {self.index.size()} vectors")
        
        # Save index
        self._save_index()
        print(f"[ICIP] Index saved to {self.index_dir}")
    
    def search(
        self,
        query: str,
        k: int = 20,
        include_context: bool = True
    ) -> List[CodeSearchResult]:
        """
        Semantic search for code
        
        Args:
            query: Natural language or code query
            k: Number of results
            include_context: Include surrounding context
            
        Returns:
            List of CodeSearchResult, ranked by relevance
        """
        if not query or not query.strip():
            return []
        
        # Ensure index exists
        if self.index.size() == 0:
            print("[ICIP] No index found. Indexing codebase...")
            self.index_codebase()
        
        if self.index.size() == 0:
            print("[ICIP] Index is still empty after indexing!")
            return []
        
        # Embed query
        query_vector = self.embedder.embed_query(query)
        
        # Search FAISS
        distances, indices, metadata_list = self.index.search(query_vector, k)
        
        # Build results
        results = []
        for i, (distance, idx, metadata) in enumerate(zip(distances[0], indices[0], metadata_list)):
            # Find corresponding chunk
            chunk = self.chunks[idx]
            
            # Calculate relevance (convert distance to similarity)
            # L2 distance → relevance: smaller distance = higher relevance
            relevance = 1.0 / (1.0 + distance)
            
            result = CodeSearchResult(
                file=chunk.file,
                line=chunk.start_line,
                code=chunk.code,
                context=chunk.context if include_context else None,
                language=chunk.language,
                type=chunk.type,
                name=chunk.name,
                relevance=relevance,
                confidence=0.0,  # Will normalize below
                distance=float(distance)
            )
            results.append(result)
        
        # Normalize confidence (relative within results)
        if results:
            max_rel = results[0].relevance
            min_rel = results[-1].relevance
            rel_range = max(max_rel - min_rel, 1e-6)
            
            for result in results:
                result.confidence = (result.relevance - min_rel) / rel_range
        
        return results
    
    def _chunk_to_metadata(self, chunk: CodeChunk) -> dict:
        """Convert chunk to metadata dict"""
        return {
            'file': chunk.file,
            'start_line': chunk.start_line,
            'end_line': chunk.end_line,
            'language': chunk.language,
            'type': chunk.type,
            'name': chunk.name,
        }
    
    def _save_index(self):
        """Save index, chunks, and hash cache to disk"""
        os.makedirs(self.index_dir, exist_ok=True)
        
        # Save FAISS index
        self.index.save(self.index_path, self.metadata_path)
        
        # Save chunks
        with open(self.chunks_path, 'w', encoding='utf-8') as f:
            chunks_data = [asdict(chunk) for chunk in self.chunks]
            json.dump(chunks_data, f, indent=2)
        
        # Save hash cache
        with open(self.hash_cache_path, 'w') as f:
            json.dump(self.hash_cache, f, indent=2)
    
    def get_stats(self) -> dict:
        """Get index statistics"""
        return {
            'total_chunks': len(self.chunks),
            'index_size': self.index.size(),
            'languages': list(set(chunk.language for chunk in self.chunks)),
            'types': list(set(chunk.type for chunk in self.chunks)),
            'dimension': self.dimension,
        }

