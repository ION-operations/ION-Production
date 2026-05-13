"""NL Tag Combined Validator - Phase 3

Orchestrates both structural and semantic validation, merging results
into a unified validation response.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import sys

# Add packages to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .models import NLTag, ValidationResult
from .structural_validator import StructuralValidator, StructuralValidationResult
from .semantic_validator import NLTagSemanticValidator


class CombinedNLTagValidator:
    """Combined validator that runs both structural and semantic validation"""
    
    def __init__(
        self,
        structural_validator: Optional[StructuralValidator] = None,
        semantic_validator: Optional[NLTagSemanticValidator] = None
    ):
        """Initialize combined validator
        
        Args:
            structural_validator: Structural validator instance (optional)
            semantic_validator: Semantic validator instance (optional)
        """
        self.structural_validator = structural_validator or StructuralValidator()
        
        # Semantic validator is optional (HHNI may not be available)
        self.semantic_validator = semantic_validator
        
        if semantic_validator is None:
            try:
                self.semantic_validator = NLTagSemanticValidator()
            except (ImportError, Exception):
                self.semantic_validator = None
    
    def validate_tag(self, tag: NLTag, code: str, use_cache: bool = True) -> ValidationResult:
        """Validate a single tag using both structural and semantic validation
        
        Args:
            tag: NL tag to validate
            code: Source code string for structural validation
            use_cache: Whether to use cached semantic results (default: True)
            
        Returns:
            Combined ValidationResult with both structural and semantic scores
        """
        # Initialize result
        result = ValidationResult(
            tag_id=tag.id,
            tag_text=tag.tag_text,
            code_block=tag.code_block or "",
            validated_at=datetime.now(),
        )
        
        # Phase 1: Structural validation (if SYNTAX_REF exists)
        structural_result = None
        if tag.syntax_ref:
            try:
                structural_result = self.structural_validator.validate_syntax_ref(tag, code)
                result.structural_match_score = structural_result.match_score
                result.syntax_ref_match = structural_result.matches
                result.structural_errors = structural_result.errors
                result.structural_warnings = structural_result.warnings
                
                # Update tag with structural score
                tag.structural_match_score = structural_result.match_score
            except Exception as e:
                result.structural_errors = [f"Structural validation error: {str(e)}"]
                result.structural_match_score = 0.0
                result.syntax_ref_match = False
        else:
            # No SYNTAX_REF - can't do structural validation
            result.structural_warnings = ["No SYNTAX_REF specified - structural validation skipped"]
        
        # Phase 2: Semantic validation (always run)
        semantic_result = None
        if self.semantic_validator:
            try:
                semantic_dict = self.semantic_validator.validate_tag(tag, use_cache=use_cache)
                
                result.accuracy_score = semantic_dict.get("accuracy_score", 0.0)
                result.passes_threshold = semantic_dict.get("passes_threshold", False)
                result.suggestions = semantic_dict.get("suggestions", [])
                result.validation_method = semantic_dict.get("validation_method", "hhni_semantic")
                result.validation_metadata = {
                    "avg_relevance": semantic_dict.get("avg_relevance"),
                    "code_found": semantic_dict.get("code_found"),
                    "results_count": semantic_dict.get("results_count"),
                    "cached": semantic_dict.get("cached", False),
                }
                
                semantic_result = semantic_dict
            except Exception as e:
                # Semantic validation failed - use fallback
                result.accuracy_score = 0.5
                result.passes_threshold = False
                result.suggestions = [f"Semantic validation error: {str(e)}"]
                result.validation_method = "error_fallback"
        else:
            # HHNI not available - use simple fallback
            result.accuracy_score = 0.5 if tag.code_block else 0.0
            result.passes_threshold = False
            result.suggestions = ["Semantic validation (HHNI) not available"]
            result.validation_method = "fallback"
        
        # Phase 3: Calculate combined score
        result.combined_score = self._calculate_combined_score(
            structural_result=structural_result,
            semantic_score=result.accuracy_score,
            structural_score=result.structural_match_score
        )
        
        # Phase 4: Determine overall pass/fail
        # Pass if: structural match >= 0.95 OR (semantic >= 0.70 AND no structural errors)
        if result.structural_match_score is not None:
            if result.structural_match_score >= 0.95:
                result.passes_threshold = True
            elif result.structural_match_score >= 0.70 and result.accuracy_score >= 0.70:
                result.passes_threshold = True
            elif len(result.structural_errors) > 0:
                result.passes_threshold = False
            else:
                result.passes_threshold = result.accuracy_score >= 0.70
        else:
            # No structural validation - use semantic only
            result.passes_threshold = result.accuracy_score >= 0.70
        
        return result
    
    def validate_tags_batch(
        self,
        tags: List[NLTag],
        code: str,
        use_cache: bool = True
    ) -> List[ValidationResult]:
        """Validate multiple tags efficiently
        
        Args:
            tags: List of NL tags to validate
            code: Source code string for structural validation
            use_cache: Whether to use cached semantic results (default: True)
            
        Returns:
            List of combined ValidationResult objects
        """
        results = []
        
        for tag in tags:
            result = self.validate_tag(tag, code, use_cache=use_cache)
            
            # Update tag with validation results
            tag.accuracy_score = result.accuracy_score
            tag.structural_match_score = result.structural_match_score
            tag.validated_at = result.validated_at
            tag.validation_status = "accurate" if result.passes_threshold else "inaccurate"
            
            results.append(result)
        
        return results
    
    def _calculate_combined_score(
        self,
        structural_result: Optional[StructuralValidationResult],
        semantic_score: float,
        structural_score: Optional[float]
    ) -> float:
        """Calculate combined validation score from structural and semantic
        
        Priority Logic:
        - If structural match >= 0.95: High confidence (use structural score)
        - If structural match < 0.95 but exists: Mixed (structural * 0.3 + semantic * 0.7)
        - If no structural validation: Use semantic only
        
        Args:
            structural_result: Structural validation result (optional)
            semantic_score: Semantic validation score (0.0-1.0)
            structural_score: Structural match score (optional)
            
        Returns:
            Combined score (0.0-1.0)
        """
        if structural_score is not None:
            if structural_score >= 0.95:
                # Perfect structural match - high confidence
                return structural_score
            elif structural_score > 0.0:
                # Structural validation exists but didn't pass perfectly
                # Weight: structural 30%, semantic 70%
                return (structural_score * 0.3) + (semantic_score * 0.7)
            else:
                # Structural validation failed - use semantic as primary
                return semantic_score * 0.7  # Penalize for structural failure
        else:
            # No structural validation - use semantic only
            return semantic_score
    
    def validate_tag_dict(self, tag: NLTag, code: str, use_cache: bool = True) -> Dict[str, Any]:
        """Validate tag and return as dictionary (for API/MCP compatibility)
        
        Args:
            tag: NL tag to validate
            code: Source code string
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary representation of validation result
        """
        result = self.validate_tag(tag, code, use_cache=use_cache)
        return result.to_dict()

