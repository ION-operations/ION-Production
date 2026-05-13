"""
HHNI (Hierarchical Hypergraph Neural Index) → SEG (Shared Evidence Graph) Integration

Enables bidirectional integration between HHNI semantic search and SEG evidence nodes.

This integration enables:
- Evidence synthesis via HHNI semantic search
- Context retrieval for evidence nodes
- Evidence indexing for HHNI search
"""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any, Literal, Tuple

from .models import Evidence
from .seg_graph import SEGraph

try:
    from hhni.retrieval import TwoStageRetriever, RetrievalResult
    from hhni.hierarchical_index import HierarchicalIndex
    from hhni.semantic_search import SemanticSearchEngine, SearchResult
    HHNI_AVAILABLE = True
except ImportError:
    HHNI_AVAILABLE = False
    # Type stubs for when HHNI is not available
    TwoStageRetriever = None  # type: ignore
    RetrievalResult = None  # type: ignore
    HierarchicalIndex = None  # type: ignore
    SemanticSearchEngine = None  # type: ignore
    SearchResult = None  # type: ignore


IntegrationMode = Literal["strict", "auto", "fallback", "mocked"]
_VALID_INTEGRATION_MODES = {"strict", "auto", "fallback", "mocked"}
_DEFAULT_INTEGRATION_MODE = os.getenv("AIMOS_SEG_HHNI_MODE", "strict")


def _resolve_integration_mode(integration_mode: Optional[IntegrationMode]) -> str:
    mode = (integration_mode or _DEFAULT_INTEGRATION_MODE).strip().lower()
    if mode not in _VALID_INTEGRATION_MODES:
        valid = ", ".join(sorted(_VALID_INTEGRATION_MODES))
        raise ValueError(f"Invalid integration_mode '{mode}'. Expected one of: {valid}")
    return mode


def _ensure_hhni_enabled(integration_mode: Optional[IntegrationMode]) -> None:
    mode = _resolve_integration_mode(integration_mode)
    if mode == "strict":
        raise ImportError("HHNI integration is disabled in strict mode.")
    if mode in {"auto", "fallback"} and not HHNI_AVAILABLE:
        raise ImportError("HHNI service not available. Install hhni package or use mocked mode.")


def _coerce_graph_and_retriever(
    graph_or_retriever: Any,
    maybe_retriever: Any,
) -> Tuple[Optional[SEGraph], Any]:
    # Legacy call form: synthesize_evidence(query, graph, hhni_retriever)
    if isinstance(graph_or_retriever, SEGraph):
        return graph_or_retriever, maybe_retriever
    # Current form: synthesize_evidence(query, hhni_retriever, graph)
    if isinstance(maybe_retriever, SEGraph):
        return maybe_retriever, graph_or_retriever
    # Retriever-only fallback
    return None, graph_or_retriever


def synthesize_evidence(
    query: str,
    graph_or_retriever: Any,
    hhni_retriever: Optional[TwoStageRetriever] = None,
    top_k: int = 5,
    integration_mode: Optional[IntegrationMode] = None,
) -> List[Evidence]:
    """
    Synthesize evidence using HHNI semantic search.
    
    Args:
        query: Search query string
        hhni_retriever: HHNI TwoStageRetriever instance
        graph: Optional SEG graph instance (to convert search results to evidence)
        top_k: Number of top results to return
    
    Returns:
        List of Evidence nodes matching the query
    
    Raises:
        ImportError: If HHNI is not available
        ValueError: If query is invalid
    """
    _ensure_hhni_enabled(integration_mode)
    
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    graph, retriever = _coerce_graph_and_retriever(graph_or_retriever, hhni_retriever)
    if retriever is None or not hasattr(retriever, "retrieve"):
        raise ValueError("HHNI retriever with a 'retrieve' method is required")
    
    # Perform HHNI retrieval
    retrieval_result = retriever.retrieve(query, token_budget=None)
    selected_items = getattr(retrieval_result, "selected", None)
    if selected_items is None:
        selected_items = getattr(retrieval_result, "selected_items", [])
    
    # Convert retrieval results to evidence nodes
    evidence_list = []
    for result in selected_items[:top_k]:
        # Create evidence from search result
        evidence = Evidence(
            content=result.node.content if hasattr(result.node, "content") else str(result.node),
            source=f"hhni.search:{result.node.id if hasattr(result.node, 'id') else 'unknown'}",
            evidence_type="synthesized",
            confidence=result.score if hasattr(result, "score") else 0.8,
            reliability=result.confidence if hasattr(result, "confidence") else 0.8,
            tags=["hhni", "synthesized", "search"],
            metadata={
                "hhni_node_id": result.node.id if hasattr(result.node, "id") else None,
                "hhni_score": result.score if hasattr(result, "score") else None,
                "hhni_confidence": result.confidence if hasattr(result, "confidence") else None,
                "query": query,
            }
        )
        
        # Add to graph if provided
        if graph:
            evidence = graph.add_evidence(evidence)
        
        evidence_list.append(evidence)
    
    return evidence_list


def get_synthesis_context(
    evidence_ids: List[str],
    graph_or_retriever: Any,
    hhni_retriever: Optional[TwoStageRetriever] = None,
    integration_mode: Optional[IntegrationMode] = None,
) -> Dict[str, Any]:
    """
    Get synthesis context for evidence nodes using HHNI.
    
    Args:
        evidence_ids: List of SEG evidence IDs
        graph: SEG graph instance
        hhni_retriever: Optional HHNI retriever (for additional context)
    
    Returns:
        Dictionary with synthesis context
    
    Raises:
        ValueError: If evidence not found
    """
    _ensure_hhni_enabled(integration_mode)

    graph, retriever = _coerce_graph_and_retriever(graph_or_retriever, hhni_retriever)
    if graph is None:
        raise ValueError("SEG graph is required to build synthesis context")

    # Get evidence from graph
    evidence_list = []
    for evidence_id in evidence_ids:
        evidence = graph.get_evidence(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found in graph")
        evidence_list.append(evidence)
    
    # Build synthesis context
    context = {
        "evidence_count": len(evidence_list),
        "evidence_ids": evidence_ids,
        "sources": [e.source for e in evidence_list],
        "confidence_scores": [e.confidence for e in evidence_list],
        "average_confidence": sum(e.confidence for e in evidence_list) / len(evidence_list) if evidence_list else 0.0,
        "tags": list(set(tag for e in evidence_list for tag in e.tags)),
        "metadata": {
            "evidence_types": list(set(e.evidence_type for e in evidence_list)),
            "reliability_scores": [e.reliability for e in evidence_list],
        }
    }
    
    # If HHNI retriever provided, enhance with semantic search
    if retriever and hasattr(retriever, "retrieve"):
        # Create query from evidence content
        query = " ".join(e.content[:100] for e in evidence_list[:3])  # Use first 3 evidence snippets
        try:
            retrieval_result = retriever.retrieve(query, token_budget=500)
            selected_items = getattr(retrieval_result, "selected", None)
            if selected_items is None:
                selected_items = getattr(retrieval_result, "selected_items", [])
            context["hhni_enhancement"] = {
                "query": query,
                "retrieved_count": len(selected_items),
                "average_relevance": retrieval_result.average_relevance if hasattr(retrieval_result, "average_relevance") else 0.0,
            }
        except Exception:
            # If HHNI fails, continue without enhancement
            pass
    
    return context


def index_evidence_for_hhni(
    evidence: Evidence,
    hhni_index: HierarchicalIndex,
    integration_mode: Optional[IntegrationMode] = None,
) -> None:
    """
    Index SEG evidence node in HHNI for semantic search.
    
    Args:
        evidence: SEG Evidence node to index
        hhni_index: HHNI HierarchicalIndex instance
    
    Raises:
        ImportError: If HHNI is not available
        ValueError: If evidence is invalid
    """
    _ensure_hhni_enabled(integration_mode)
    
    if not evidence:
        raise ValueError("Evidence cannot be None")
    if hhni_index is None:
        raise ValueError("HHNI index cannot be None")
    
    # Create index node from evidence
    # Note: This depends on HHNI's index API
    # For now, we'll create a basic index entry
    try:
        # HHNI indexing would typically be done via build_hhni_for_atom or similar
        # This is a placeholder that shows the integration pattern
        # Actual implementation would depend on HHNI's indexing API
        
        # If HHNI has an add_node method:
        if hasattr(hhni_index, "add_node"):
            hhni_index.add_node(
                content=evidence.content,
                summary=evidence.content[:200],  # First 200 chars as summary
                metadata={
                    "seg_evidence_id": evidence.id,
                    "source": evidence.source,
                    "evidence_type": evidence.evidence_type,
                    "confidence": evidence.confidence,
                }
            )
        else:
            # If no direct add_node, log that indexing would happen via CMC
            # (HHNI typically indexes CMC atoms, so evidence should be stored in CMC first)
            pass
    except Exception as e:
        # If indexing fails, log but don't raise (non-critical)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to index evidence {evidence.id} in HHNI: {e}")

