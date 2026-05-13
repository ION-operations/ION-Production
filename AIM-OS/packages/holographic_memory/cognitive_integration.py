"""Cognitive Component Integration for AIMO_HoloMemory - Experimental/Additive Enhancement.

This module provides optional holographic memory capabilities for cognitive components
(VIF, APOE, SIS, CAS), working alongside (not replacing) primary operations.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from .holo_memory import AIMO_HoloMemory
from .vectorizer import PLIxVectorizer, MemoryAtomVectorizer

logger = logging.getLogger(__name__)

# Configuration flag - must be explicitly enabled
ENABLE_HOLOGRAPHIC_MEMORY = os.getenv("ENABLE_HOLOGRAPHIC_MEMORY", "false").lower() == "true"


class VIF_HoloIntegration:
    """Experimental holographic memory integration for VIF.
    
    Provides optional confidence scoring based on reconstruction fidelity
    from holographic memory. Works alongside primary VIF confidence calculation.
    
    Example:
        >>> integration = VIF_HoloIntegration()
        >>> if integration.is_enabled():
        ...     confidence = integration.compute_confidence_from_reconstruction(
        ...         plix_intent, semantic_id
        ...     )
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        enable: Optional[bool] = None,
        cmc_integration: Optional[Any] = None,  # CMC_HoloIntegration
    ):
        """Initialize VIF holographic integration.
        
        Args:
            dimension: Dimensionality of holographic vectors
            enable: Override global config (None = use ENABLE_HOLOGRAPHIC_MEMORY)
            cmc_integration: Optional CMC integration for accessing stored atoms
        """
        self.enabled = enable if enable is not None else ENABLE_HOLOGRAPHIC_MEMORY
        self.dimension = dimension
        self.cmc_integration = cmc_integration
        
        if self.enabled:
            self.vectorizer = PLIxVectorizer(dimension=dimension)
            logger.info("VIF holographic memory integration ENABLED")
        else:
            self.vectorizer = None
            logger.debug("VIF holographic memory integration DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if holographic memory is enabled."""
        return self.enabled and self.vectorizer is not None
    
    def compute_confidence_from_reconstruction(
        self,
        plix_intent: Dict[str, Any],
        semantic_id: Optional[str] = None,
    ) -> Optional[float]:
        """Compute confidence score from holographic reconstruction fidelity (experimental).
        
        High-fidelity reconstruction → Higher confidence
        Low-fidelity/ambiguous reconstruction → Lower confidence
        
        Args:
            plix_intent: PLIx intent dictionary
            semantic_id: Optional semantic ID for exact lookup
            
        Returns:
            Confidence score (0.0-1.0) if enabled and successful, None otherwise
            
        Note:
            This provides additional confidence signal. Primary VIF confidence
            calculation should be used as primary source.
        """
        if not self.is_enabled():
            return None
        
        if self.cmc_integration is None or not self.cmc_integration.is_enabled():
            return None
        
        try:
            # Convert PLIx intent to vector
            intent_vector = self.vectorizer.vectorize(plix_intent)
            
            # Try to retrieve from holographic memory
            if semantic_id:
                result = self.cmc_integration.retrieve_exact(semantic_id)
                if result:
                    _, fidelity = result
                    # Use fidelity as additional confidence signal
                    # High fidelity (0.8-1.0) → High confidence
                    # Low fidelity (<0.5) → Low confidence
                    confidence = min(1.0, max(0.0, fidelity * 1.2))  # Scale slightly
                    logger.debug(f"Holographic confidence for {semantic_id}: {confidence:.3f} (fidelity: {fidelity:.3f})")
                    return confidence
            
            # If no exact match, try associative retrieval
            suggestions = self.cmc_integration.retrieve_associative(
                str(plix_intent.get("goal", "")), top_k=1
            )
            if suggestions:
                _, correlation, fidelity = suggestions[0]
                # Combine correlation and fidelity
                confidence = (correlation + fidelity) / 2.0
                logger.debug(f"Holographic confidence from association: {confidence:.3f}")
                return confidence
            
            return None
            
        except Exception as e:
            logger.warning(f"Holographic confidence calculation failed: {e}")
            return None


class APOE_HoloIntegration:
    """Experimental holographic memory integration for APOE.
    
    Provides optional associative plan retrieval from holographic encodings.
    Works alongside primary APOE plan generation.
    
    Example:
        >>> integration = APOE_HoloIntegration()
        >>> if integration.is_enabled():
        ...     plans = integration.retrieve_associative_plans(plix_intent)
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        enable: Optional[bool] = None,
        cmc_integration: Optional[Any] = None,  # CMC_HoloIntegration
    ):
        """Initialize APOE holographic integration.
        
        Args:
            dimension: Dimensionality of holographic vectors
            enable: Override global config (None = use ENABLE_HOLOGRAPHIC_MEMORY)
            cmc_integration: Optional CMC integration for accessing stored plans
        """
        self.enabled = enable if enable is not None else ENABLE_HOLOGRAPHIC_MEMORY
        self.dimension = dimension
        self.cmc_integration = cmc_integration
        
        if self.enabled:
            self.vectorizer = PLIxVectorizer(dimension=dimension)
            logger.info("APOE holographic memory integration ENABLED")
        else:
            self.vectorizer = None
            logger.debug("APOE holographic memory integration DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if holographic memory is enabled."""
        return self.enabled and self.vectorizer is not None
    
    def retrieve_associative_plans(
        self,
        plix_intent: Dict[str, Any],
        top_k: int = 5,
    ) -> List[Tuple[str, float, float]]:
        """Retrieve execution plans associatively from holographic memory (experimental).
        
        Provides plan suggestions based on holographic similarity to past successful plans.
        
        Args:
            plix_intent: PLIx intent dictionary
            top_k: Number of top plans to return
            
        Returns:
            List of (plan_id, correlation_score, fidelity) tuples (suggestions)
            
        Note:
            These are suggestions/candidates. Primary APOE plan generation
            should be used as primary source.
        """
        if not self.is_enabled():
            return []
        
        if self.cmc_integration is None or not self.cmc_integration.is_enabled():
            return []
        
        try:
            # Convert PLIx intent to vector
            intent_vector = self.vectorizer.vectorize(plix_intent)
            
            # Retrieve associatively
            # In full implementation, would search for plans specifically
            # For now, use general associative retrieval
            goal_str = str(plix_intent.get("goal", ""))
            suggestions = self.cmc_integration.retrieve_associative(goal_str, top_k=top_k)
            
            # Filter for plans (in full impl, would check atom tags/type)
            plan_suggestions = []
            for semantic_id, correlation, fidelity in suggestions:
                # In full implementation, would verify this is actually a plan
                # For now, return all suggestions as potential plans
                plan_suggestions.append((semantic_id, correlation, fidelity))
            
            logger.debug(f"Retrieved {len(plan_suggestions)} associative plan suggestions")
            return plan_suggestions
            
        except Exception as e:
            logger.warning(f"Associative plan retrieval failed: {e}")
            return []


class SIS_HoloIntegration:
    """Experimental holographic memory integration for SIS.
    
    Provides optional association reinforcement/weakening based on success/failure.
    Works alongside primary SIS learning mechanisms.
    
    Example:
        >>> integration = SIS_HoloIntegration()
        >>> if integration.is_enabled():
        ...     integration.reinforce_association(pattern_id, success=True)
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        enable: Optional[bool] = None,
        cmc_integration: Optional[Any] = None,  # CMC_HoloIntegration
    ):
        """Initialize SIS holographic integration.
        
        Args:
            dimension: Dimensionality of holographic vectors
            enable: Override global config (None = use ENABLE_HOLOGRAPHIC_MEMORY)
            cmc_integration: Optional CMC integration for accessing stored patterns
        """
        self.enabled = enable if enable is not None else ENABLE_HOLOGRAPHIC_MEMORY
        self.dimension = dimension
        self.cmc_integration = cmc_integration
        
        if self.enabled:
            logger.info("SIS holographic memory integration ENABLED")
        else:
            logger.debug("SIS holographic memory integration DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if holographic memory is enabled."""
        return self.enabled and self.cmc_integration is not None and self.cmc_integration.is_enabled()
    
    def reinforce_association(
        self,
        pattern_id: str,
        success: bool = True,
        strength: float = 0.1,
    ) -> bool:
        """Reinforce or weaken association in holographic memory (experimental).
        
        Successful patterns are reinforced (re-bound with increased weight).
        Failed patterns are de-emphasized.
        
        Args:
            pattern_id: Pattern identifier (e.g., semantic_id)
            success: True to reinforce, False to weaken
            strength: Reinforcement/weakening strength (0.0-1.0)
            
        Returns:
            True if successful, False if disabled or failed
            
        Note:
            This provides additional learning mechanism. Primary SIS learning
            should be used as primary mechanism.
        """
        if not self.is_enabled():
            return False
        
        try:
            # Retrieve current pattern
            result = self.cmc_integration.retrieve_exact(pattern_id)
            if not result:
                logger.warning(f"Pattern {pattern_id} not found in holographic memory")
                return False
            
            reconstructed, current_fidelity = result
            
            # Adjust based on success/failure
            if success:
                # Reinforce: increase weight (re-store with higher magnitude)
                reinforced = reconstructed * (1.0 + strength)
                reinforced = reinforced / np.linalg.norm(reinforced)  # Renormalize
                # In full implementation, would update in holographic memory
                logger.debug(f"Reinforced association for {pattern_id} (strength: {strength})")
            else:
                # Weaken: decrease weight
                weakened = reconstructed * (1.0 - strength)
                weakened = weakened / np.linalg.norm(weakened)  # Renormalize
                # In full implementation, would update in holographic memory
                logger.debug(f"Weakened association for {pattern_id} (strength: {strength})")
            
            return True
            
        except Exception as e:
            logger.warning(f"Association reinforcement failed for {pattern_id}: {e}")
            return False


class CAS_HoloIntegration:
    """Experimental holographic memory integration for CAS.
    
    Provides optional meta-cognition insights from holographic memory state.
    Works alongside primary CAS meta-cognitive analysis.
    
    Example:
        >>> integration = CAS_HoloIntegration()
        >>> if integration.is_enabled():
        ...     insights = integration.analyze_holographic_state()
    """
    
    def __init__(
        self,
        dimension: int = 10000,
        enable: Optional[bool] = None,
        cmc_integration: Optional[Any] = None,  # CMC_HoloIntegration
        seg_integration: Optional[Any] = None,  # SEG_HoloIntegration
    ):
        """Initialize CAS holographic integration.
        
        Args:
            dimension: Dimensionality of holographic vectors
            enable: Override global config (None = use ENABLE_HOLOGRAPHIC_MEMORY)
            cmc_integration: Optional CMC integration for memory state
            seg_integration: Optional SEG integration for graph state
        """
        self.enabled = enable if enable is not None else ENABLE_HOLOGRAPHIC_MEMORY
        self.dimension = dimension
        self.cmc_integration = cmc_integration
        self.seg_integration = seg_integration
        
        if self.enabled:
            logger.info("CAS holographic memory integration ENABLED")
        else:
            logger.debug("CAS holographic memory integration DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if holographic memory is enabled."""
        return self.enabled and (
            (self.cmc_integration is not None and self.cmc_integration.is_enabled()) or
            (self.seg_integration is not None and self.seg_integration.is_enabled())
        )
    
    def analyze_holographic_state(self) -> Dict[str, Any]:
        """Analyze holographic memory state for meta-cognition (experimental).
        
        Provides insights about:
        - Memory density and activity
        - Areas of ambiguity (multiple strong reconstructions)
        - Correlation clusters
        - Overall coherence
        
        Returns:
            Dictionary with meta-cognitive insights
            
        Note:
            This provides additional meta-cognitive signal. Primary CAS
            analysis should be used as primary source.
        """
        if not self.is_enabled():
            return {
                "enabled": False,
                "message": "Holographic memory integration is disabled",
            }
        
        insights = {
            "enabled": True,
            "memory_density": 0.0,
            "ambiguity_areas": [],
            "correlation_clusters": [],
            "coherence_score": 0.0,
        }
        
        try:
            # Get statistics from integrations
            if self.cmc_integration:
                cmc_stats = self.cmc_integration.get_stats()
                if cmc_stats.get("enabled"):
                    holo_stats = cmc_stats.get("holo_memory", {})
                    memory_count = holo_stats.get("memory_count", 0)
                    memory_array_norm = holo_stats.get("memory_array_norm", 0.0)
                    
                    # Compute density (normalized by dimension)
                    insights["memory_density"] = memory_array_norm / (self.dimension * memory_count) if memory_count > 0 else 0.0
                    insights["memory_count"] = memory_count
            
            if self.seg_integration:
                seg_stats = self.seg_integration.get_stats()
                if seg_stats.get("enabled"):
                    insights["entity_count"] = seg_stats.get("entity_count", 0)
                    insights["relationship_count"] = seg_stats.get("relationship_count", 0)
            
            # Compute coherence (simplified - in full impl would analyze correlations)
            insights["coherence_score"] = min(1.0, insights.get("memory_density", 0.0) * 2.0)
            
            logger.debug(f"Holographic state analysis: {insights}")
            return insights
            
        except Exception as e:
            logger.warning(f"Holographic state analysis failed: {e}")
            return {
                "enabled": True,
                "error": str(e),
            }
    
    def detect_ambiguity(
        self,
        query: str,
        threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Detect ambiguity in holographic memory (experimental).
        
        Multiple strong reconstructions for a query indicate ambiguity/confusion.
        
        Args:
            query: Query string
            threshold: Correlation threshold for considering a match "strong"
            
        Returns:
            Dictionary with ambiguity detection results
            
        Note:
            This provides additional ambiguity signal. Primary CAS ambiguity
            detection should be used as primary source.
        """
        if not self.is_enabled() or self.cmc_integration is None:
            return {
                "ambiguous": False,
                "strong_matches": 0,
            }
        
        try:
            # Retrieve associatively
            suggestions = self.cmc_integration.retrieve_associative(query, top_k=10)
            
            # Count strong matches (correlation above threshold)
            strong_matches = [s for s in suggestions if s[1] >= threshold]
            
            # Ambiguity: multiple strong matches
            ambiguous = len(strong_matches) > 1
            
            result = {
                "ambiguous": ambiguous,
                "strong_matches": len(strong_matches),
                "top_correlations": [s[1] for s in strong_matches[:3]],
            }
            
            if ambiguous:
                logger.debug(f"Ambiguity detected: {len(strong_matches)} strong matches for query: {query[:50]}")
            
            return result
            
        except Exception as e:
            logger.warning(f"Ambiguity detection failed: {e}")
            return {
                "ambiguous": False,
                "error": str(e),
            }

