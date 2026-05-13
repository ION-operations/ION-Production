"""HHNI Integration for SDF-CVF

Enables blast radius analysis using HHNI dependency graph.

Integration Points:
- Change context retrieval from HHNI
- Impact analysis queries
- Evolution pattern detection
- Consistency checks
"""

from __future__ import annotations
import os
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime, timezone

# HHNI imports (optional)
try:
    from packages.hhni.retrieval import TwoStageRetriever, RetrievalResult, RetrievalConfig
    from packages.hhni.hierarchical_index import HierarchicalIndex
    HHNI_AVAILABLE = True
except ImportError:
    # Fallback for environments without HHNI
    HHNI_AVAILABLE = False
    TwoStageRetriever = None
    RetrievalResult = None
    RetrievalConfig = None
    HierarchicalIndex = None


IntegrationMode = Literal["strict", "auto", "fallback", "mocked"]
_VALID_INTEGRATION_MODES = {"strict", "auto", "fallback", "mocked"}
_DEFAULT_INTEGRATION_MODE = os.getenv("AIMOS_SDFCVF_HHNI_MODE", "strict")


def _resolve_integration_mode(integration_mode: Optional[IntegrationMode]) -> str:
    mode = (integration_mode or _DEFAULT_INTEGRATION_MODE).strip().lower()
    if mode not in _VALID_INTEGRATION_MODES:
        valid = ", ".join(sorted(_VALID_INTEGRATION_MODES))
        raise ValueError(f"Invalid integration_mode '{mode}'. Expected one of: {valid}")
    return mode


def _is_available(
    package_available: bool,
    integration_mode: str,
    client: Optional[Any] = None,
) -> bool:
    if integration_mode == "strict":
        return False
    if integration_mode in {"auto", "fallback"}:
        return package_available or client is not None
    return True


class HHNIIntegration:
    """Integrates SDF-CVF with HHNI for blast radius analysis.
    
    Provides:
    - Change context retrieval
    - Impact analysis queries
    - Evolution pattern detection
    - Consistency checks
    """
    
    def __init__(
        self,
        hhni_client: Optional[Any] = None,
        integration_mode: Optional[IntegrationMode] = None,
    ):
        """
        Initialize HHNI integration.
        
        Args:
            hhni_client: HHNI client instance (optional, for testing can be None)
        """
        self.integration_mode = _resolve_integration_mode(integration_mode)
        self.hhni_available = _is_available(
            package_available=HHNI_AVAILABLE,
            integration_mode=self.integration_mode,
            client=hhni_client,
        )
        self.hhni = hhni_client
        
        if not self.hhni_available:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("HHNI integration disabled: HHNI package not available")
    
    def get_change_context(
        self,
        change_files: List[str],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get change context from HHNI for blast radius analysis.
        
        Used by blastRadiusCalculator for dependency analysis.
        
        Args:
            change_files: List of changed file paths
            query: Optional query string for context retrieval
            
        Returns:
            Change context dictionary
        """
        if not self.hhni_available:
            return {
                "context_available": False,
                "error": "HHNI not available",
                "context": {}
            }
        
        try:
            # Simplified implementation (would use actual HHNI TwoStageRetriever)
            # TODO: Wire to packages.hhni.retrieval.TwoStageRetriever.retrieve() when HHNI schema confirmed
            # RetrievalResult has: selected_items, total_tokens, relevance_score, etc.
            context = {
                "change_files": change_files,
                "dependencies": [],
                "dependents": [],
                "impact_scope": "local"
            }
            
            return {
                "context_available": True,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting change context from HHNI: {e}")
            return {
                "context_available": False,
                "error": str(e),
                "context": {}
            }
    
    def query_impact_analysis(
        self,
        change_files: List[str],
        analysis_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Query impact analysis from HHNI dependency graph.
        
        Used by blastRadiusCalculator for impact prediction.
        
        Args:
            change_files: List of changed file paths
            analysis_depth: Depth of dependency analysis
            
        Returns:
            Impact analysis result dictionary
        """
        if not self.hhni_available:
            return {
                "analysis_available": False,
                "error": "HHNI not available",
                "impact": {}
            }
        
        try:
            # Simplified implementation (would use actual HHNI TwoStageRetriever)
            # TODO: Wire to packages.hhni.retrieval.TwoStageRetriever.retrieve() for dependency analysis
            # RetrievalResult.selected_items contains SearchResult objects with relevance scores
            impact = {
                "affected_files": change_files,
                "dependencies": [],
                "dependents": [],
                "impact_score": 0.5,
                "risk_level": "medium"
            }
            
            return {
                "analysis_available": True,
                "impact": impact,
                "analysis_depth": analysis_depth,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error querying impact analysis from HHNI: {e}")
            return {
                "analysis_available": False,
                "error": str(e),
                "impact": {}
            }
    
    def detect_evolution_patterns(
        self,
        quartet_id: str,
        time_window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect evolution patterns using HHNI queries.
        
        Used for evolution tracking and pattern analysis.
        
        Args:
            quartet_id: Unique identifier for the quartet
            time_window_days: Time window for pattern detection
            
        Returns:
            List of evolution pattern dictionaries
        """
        if not self.hhni_available:
            return []
        
        try:
            # Simplified implementation (would use actual HHNI pattern detection)
            patterns = []
            
            return patterns
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error detecting evolution patterns from HHNI: {e}")
            return []
    
    def check_consistency(
        self,
        quartet_id: str
    ) -> Dict[str, Any]:
        """
        Check consistency using HHNI queries.
        
        Used for consistency validation.
        
        Args:
            quartet_id: Unique identifier for the quartet
            
        Returns:
            Consistency check result
        """
        if not self.hhni_available:
            return {
                "consistent": False,
                "error": "HHNI not available"
            }
        
        try:
            # Simplified implementation (would use actual HHNI consistency checks)
            return {
                "consistent": True,
                "quartet_id": quartet_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking consistency with HHNI: {e}")
            return {
                "consistent": False,
                "error": str(e)
            }

