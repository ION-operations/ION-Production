"""
ICIP Search - Semantic Code Search Package

Provides 3-tier code search:
- Tier 1: Literal (grep-based)
- Tier 2: Structural (AST-based)
- Tier 3: Semantic (embedding-based)

This implementation focuses on Tier 3 (semantic) using:
- sentence-transformers for embeddings (all-MiniLM-L6-v2, 384d)
- FAISS for vector search
- Python AST for code chunking
"""

from .semantic_engine import SemanticEngine, CodeSearchResult
from .code_embedder import CodeEmbedder
from .code_chunker import CodeChunker, CodeChunk
from .faiss_index import FAISSIndex

__all__ = [
    'SemanticEngine',
    'CodeSearchResult',
    'CodeEmbedder',
    'CodeChunker',
    'CodeChunk',
    'FAISSIndex',
]

__version__ = '0.1.0'

