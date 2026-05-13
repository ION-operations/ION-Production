"""Retriever Role Implementation with HHNI Integration

Provides intelligent context retrieval using HHNI (Hierarchical Hypergraph Neural Index)
with budget-aware queries and multi-resolution context support.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import logging

from .models import Budget, RoleType

logger = logging.getLogger(__name__)

# HHNI imports (optional)
try:
    from packages.hhni.retrieval import TwoStageRetriever, RetrievalConfig, RetrievalResult
    from packages.hhni.hierarchical_index import HierarchicalIndex, IndexLevel
    from packages.hhni.semantic_search import EmbeddingProvider
    HHNI_AVAILABLE = True
except ImportError:
    HHNI_AVAILABLE = False
    TwoStageRetriever = None
    RetrievalConfig = None
    RetrievalResult = None
    HierarchicalIndex = None
    IndexLevel = None
    EmbeddingProvider = None


class RetrieverRole:
    """Retriever role using HHNI for context retrieval.
    
    Provides:
    - Budget-aware queries (respects APOE token budgets)
    - Multi-resolution context support
    - DVNS physics for relevance optimization
    - Conflict resolution and compression
    """
    
    def __init__(self, hierarchical_index: Optional[HierarchicalIndex] = None):
        """
        Initialize Retriever role.
        
        Args:
            hierarchical_index: HHNI index instance (optional, will create if needed)
        """
        self.index = hierarchical_index
        self.hhni_available = HHNI_AVAILABLE and hierarchical_index is not None
        self._passthrough_mode = False

        if self.hhni_available and hierarchical_index is not None:
            is_real_hhni_index = (
                HierarchicalIndex is not None and
                isinstance(hierarchical_index, HierarchicalIndex)
            )
            # Some tests inject a simple mock retriever with a `retrieve()` contract.
            if hasattr(hierarchical_index, "retrieve") and not is_real_hhni_index:
                self.retriever = hierarchical_index
                self._passthrough_mode = True
            else:
                config = RetrievalConfig(
                    coarse_k=100,
                    min_relevance=0.3,
                    token_budget=4000,  # Default budget
                    enable_conflict_resolution=True,
                    enable_compression=True,
                )
                self.retriever = TwoStageRetriever(
                    hierarchical_index=hierarchical_index,
                    config=config
                )
        else:
            self.retriever = None
            if not self.hhni_available:
                logger.warning("HHNI not available - Retriever role will use fallback")
    
    def execute(
        self,
        inputs: Dict[str, Any],
        budget: Optional[Budget] = None
    ) -> Dict[str, Any]:
        """Execute retrieval with HHNI.
        
        Args:
            inputs: Retrieval inputs containing:
                - query: Search query string
                - modality: Content type ("code", "docs", "data", etc.)
                - k: Number of results (default: 100)
                - enable_dvns: Enable DVNS physics (default: True)
                - resolution_levels: Multi-resolution levels (optional)
            budget: APOE budget constraints
            
        Returns:
            Dictionary with:
                - context: Retrieved context items
                - total_tokens: Token count
                - relevance_scores: Relevance scores
                - retrieval_witness: VIF witness for retrieval (if available)
                - modality: Content modality
                - k: Number of results
                - dvns_enabled: Whether DVNS was used
        """
        # Extract query
        query = inputs.get("query", "")
        if not query:
            return {
                "context": [],
                "total_tokens": 0,
                "error": "No query provided",
                "relevance_scores": [],
                "modality": inputs.get("modality", "code"),
                "k": 0,
                "dvns_enabled": False
            }
        
        # Check if multi-resolution requested
        resolution_levels = inputs.get("resolution_levels")
        if resolution_levels:
            return self._execute_multi_resolution(inputs, budget)
        
        # Extract budget constraints
        token_budget = budget.tokens_limit if budget else 2000  # Default 2k tokens
        time_budget = budget.time_limit_seconds if budget else 30  # Default 30s
        
        # Extract query constraints
        modality = inputs.get("modality", "code")  # "code", "docs", "data", etc.
        k = inputs.get("k", 100)  # Number of results
        enable_dvns = inputs.get("enable_dvns", True)  # Enable DVNS physics
        
        # Use HHNI if available
        if self.hhni_available and self.retriever:
            try:
                if self._passthrough_mode:
                    raw_result = self.retriever.retrieve(
                        query=query,
                        k=k,
                        modality=modality,
                        enable_dvns=enable_dvns
                    )
                    if isinstance(raw_result, dict):
                        total_tokens = min(raw_result.get("total_tokens", 0), token_budget)
                        return {
                            "context": raw_result.get("context", []),
                            "total_tokens": total_tokens,
                            "relevance_scores": raw_result.get("relevance_scores", []),
                            "retrieval_witness": raw_result.get("retrieval_witness", {}),
                            "modality": raw_result.get("modality", modality),
                            "k": raw_result.get("k", len(raw_result.get("context", []))),
                            "dvns_enabled": raw_result.get("dvns_enabled", enable_dvns),
                            "metrics": raw_result.get("metrics", {})
                        }

                # Determine target level from modality
                target_level = self._modality_to_level(modality)
                
                # Update retriever config with budget
                self.retriever.config.token_budget = token_budget
                self.retriever.config.coarse_k = k
                
                # Query HHNI with budget constraints
                result: RetrievalResult = self.retriever.retrieve(
                    query=query,
                    token_budget=token_budget,
                    target_level=target_level,
                    provider=EmbeddingProvider.LOCAL  # Can be made configurable
                )
                
                # Extract context items (RetrievalResult uses selected_items)
                context_items = [
                    {
                        "id": item.node.id,
                        "content": item.node.content,
                        "level": item.node.level.value if hasattr(item.node.level, 'value') else str(item.node.level),
                        "relevance": item.score,
                        "metadata": item.node.metadata if hasattr(item.node, 'metadata') else {}
                    }
                    for item in result.selected_items
                ]
                
                return {
                    "context": context_items,
                    "total_tokens": result.total_tokens,
                    "relevance_scores": [item.score for item in result.selected_items],
                    "retrieval_witness": result.audit_trail if hasattr(result, 'audit_trail') else {},
                    "modality": modality,
                    "k": len(context_items),
                    "dvns_enabled": enable_dvns,
                    "metrics": {
                        "coarse_time_ms": result.coarse_time_ms if hasattr(result, 'coarse_time_ms') else 0,
                        "dvns_time_ms": result.dvns_time_ms if hasattr(result, 'dvns_time_ms') else 0,
                        "relevance_score": result.relevance_score if hasattr(result, 'relevance_score') else 0.0,
                        "efficiency": result.efficiency if hasattr(result, 'efficiency') else 0.0,
                        "budget_utilization": result.total_tokens / token_budget if token_budget > 0 else 0
                    }
                }
            except Exception as e:
                logger.error(f"HHNI retrieval failed: {e}", exc_info=True)
                return {
                    "context": [],
                    "total_tokens": 0,
                    "error": str(e),
                    "relevance_scores": [],
                    "modality": modality,
                    "k": 0,
                    "dvns_enabled": enable_dvns
                }
        else:
            # Fallback: return empty result
            logger.warning("HHNI not available - returning empty retrieval result")
            return {
                "context": [],
                "total_tokens": 0,
                "error": "HHNI not available",
                "relevance_scores": [],
                "modality": modality,
                "k": 0,
                "dvns_enabled": False
            }
    
    def _execute_multi_resolution(
        self,
        inputs: Dict[str, Any],
        budget: Optional[Budget] = None
    ) -> Dict[str, Any]:
        """Execute retrieval with multi-resolution context.
        
        Args:
            inputs: Retrieval inputs with resolution_levels
            budget: APOE budget constraints
            
        Returns:
            Dictionary with multi-resolution results
        """
        if not self.hhni_available or not self.retriever:
            return {
                "multi_resolution": {},
                "total_tokens": 0,
                "resolution_levels": inputs.get("resolution_levels", []),
                "error": "HHNI not available"
            }
        
        query = inputs.get("query", "")
        resolution_levels = inputs.get("resolution_levels", ["system", "section", "paragraph"])
        token_budget = budget.tokens_limit if budget else 2000
        modality = inputs.get("modality", "code")
        
        # Query HHNI at multiple resolutions
        results = {}
        budget_per_level = token_budget // len(resolution_levels) if resolution_levels else token_budget
        
        for level_name in resolution_levels:
            try:
                # Map level name to IndexLevel
                target_level = self._name_to_level(level_name)
                
                # Update config for this level
                self.retriever.config.token_budget = budget_per_level
                self.retriever.config.coarse_k = 50  # Fewer results per level
                
                # Query at this resolution
                result: RetrievalResult = self.retriever.retrieve(
                    query=query,
                    token_budget=budget_per_level,
                    target_level=target_level,
                    provider=EmbeddingProvider.LOCAL
                )
                
                # Extract items (RetrievalResult uses selected_items)
                context_items = [
                    {
                        "id": item.node.id,
                        "content": item.node.content,
                        "level": item.node.level.value if hasattr(item.node.level, 'value') else str(item.node.level),
                        "relevance": item.score,
                        "metadata": item.node.metadata if hasattr(item.node, 'metadata') else {}
                    }
                    for item in result.selected_items
                ]
                
                results[level_name] = {
                    "items": context_items,
                    "tokens": result.total_tokens,
                    "scores": [item.score for item in result.selected_items],
                    "count": len(context_items)
                }
            except Exception as e:
                logger.warning(f"Multi-resolution retrieval failed for level {level_name}: {e}")
                results[level_name] = {
                    "items": [],
                    "tokens": 0,
                    "scores": [],
                    "count": 0,
                    "error": str(e)
                }
        
        return {
            "multi_resolution": results,
            "total_tokens": sum(r.get("tokens", 0) for r in results.values()),
            "resolution_levels": resolution_levels,
            "modality": modality
        }
    
    def _modality_to_level(self, modality: str) -> IndexLevel:
        """Map modality to HHNI index level.
        
        Args:
            modality: Content modality ("code", "docs", "data", etc.)
            
        Returns:
            IndexLevel
        """
        if not self.hhni_available:
            return None
        
        # Map modalities to appropriate levels
        modality_level_map = {
            "code": IndexLevel.PARAGRAPH,  # Code functions/classes
            "docs": IndexLevel.SECTION,     # Documentation sections
            "data": IndexLevel.PARAGRAPH,   # Data entries
            "text": IndexLevel.PARAGRAPH,   # General text
        }
        return modality_level_map.get(modality.lower(), IndexLevel.PARAGRAPH)
    
    def _name_to_level(self, level_name: str) -> IndexLevel:
        """Map level name to IndexLevel enum.
        
        Args:
            level_name: Level name ("system", "section", "paragraph", "sentence")
            
        Returns:
            IndexLevel
        """
        if not self.hhni_available:
            return None
        
        name_map = {
            "system": IndexLevel.SYSTEM,
            "section": IndexLevel.SECTION,
            "paragraph": IndexLevel.PARAGRAPH,
            "sentence": IndexLevel.SENTENCE,
        }
        return name_map.get(level_name.lower(), IndexLevel.PARAGRAPH)

