"""
HHNI Lite — torch-free HHNI wrapper for the MCP server.

Uses a sys.meta_path hook (TorchBlocker) to intercept all torch.*
and sentence_transformers.* imports, returning empty stub modules.
This prevents the torch initialization hang on this Windows stack
while allowing HHNI to load and operate using fallback embeddings.

Verified: Import ~10s, index ~2s, retriever <250ms.

Usage:
    from packages.hhni_lite import (
        HierarchicalIndex, TwoStageRetriever, RetrievalConfig,
        build_hhni_index_from_atoms, create_retriever,
    )
"""

from __future__ import annotations

import sys
import types


class _TorchBlocker:
    """
    sys.meta_path hook that intercepts torch and sentence_transformers
    imports, returning empty stub modules to prevent the hang.
    
    Must be installed BEFORE any HHNI import.
    """
    _BLOCKED = ('torch', 'sentence_transformers')
    
    def find_module(self, fullname, path=None):
        for b in self._BLOCKED:
            if fullname == b or fullname.startswith(b + '.'):
                return self
        return None
    
    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = types.ModuleType(fullname)
        mod.__path__ = []
        mod.__loader__ = self
        mod.__spec__ = None
        sys.modules[fullname] = mod
        return mod


# Install the blocker BEFORE any HHNI import
# Only if torch isn't already successfully loaded
if 'torch' not in sys.modules:
    sys.meta_path.insert(0, _TorchBlocker())


# Now safe to import HHNI — embeddings.py will get stub torch/sentence_transformers
from packages.hhni import (  # noqa: E402
    HierarchicalIndex,
    IndexLevel,
    IndexNode,
    TwoStageRetriever,
    RetrievalConfig,
    RetrievalResult,
)


def build_hhni_index_from_atoms(atoms: list, max_atoms: int = 500) -> HierarchicalIndex:
    """Build an HHNI index from CMC atoms using fallback embeddings."""
    index = HierarchicalIndex()
    indexed = 0
    for atom in atoms:
        if indexed >= max_atoms:
            break
        try:
            content = getattr(atom, 'content', None) or getattr(atom, 'data', '')
            if not content or not isinstance(content, str) or len(content) < 10:
                continue
            atom_id = str(
                getattr(atom, 'id', None)
                or getattr(atom, 'atom_id', f'a{indexed}')
            )
            index.index_document(
                content=content[:2000],
                doc_id=atom_id,
                metadata={"source": "cmc"},
            )
            indexed += 1
        except Exception:
            continue
    return index


def create_retriever(
    index: HierarchicalIndex,
    token_budget: int = 4000,
    coarse_k: int = 100,
    min_relevance: float = 0.3,
    dvns_iterations: int = 50,
) -> TwoStageRetriever:
    """Create a TwoStageRetriever with sensible defaults."""
    config = RetrievalConfig(
        token_budget=token_budget,
        coarse_k=coarse_k,
        min_relevance=min_relevance,
        dvns_iterations=dvns_iterations,
        enable_conflict_resolution=True,
        enable_compression=True,
    )
    return TwoStageRetriever(hierarchical_index=index, config=config)


__all__ = [
    "HierarchicalIndex", "IndexLevel", "IndexNode",
    "TwoStageRetriever", "RetrievalConfig", "RetrievalResult",
    "build_hhni_index_from_atoms", "create_retriever",
]
