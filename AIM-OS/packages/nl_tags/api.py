"""NL Tags API Endpoints - FastAPI routes for NL tag operations

Provides REST API endpoints for:
- Tag extraction and retrieval
- Coverage statistics
- Tag validation
- Issue detection
- Tag suggestions
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
import sys

# Add packages to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.nl_tags.tag_registry import NLTagRegistry
from packages.nl_tags.models import NLTag, TagCoverageStats, ValidationResult

# Optional CMC integration
try:
    from packages.cmc_service.memory_store import MemoryStore
    from packages.cmc_service.models import AtomCreate, AtomContent
    CMC_AVAILABLE = True
except ImportError:
    CMC_AVAILABLE = False

router = APIRouter(prefix="/nl-tags", tags=["nl-tags"])

# Initialize registry (with optional CMC store)
_cmc_store = None
_registry = None


def get_registry() -> NLTagRegistry:
    """Get or create NL tag registry"""
    global _registry
    if _registry is None:
        # Try to initialize CMC store if available
        global _cmc_store
        if _cmc_store is None:
            try:
                cmc_path = Path(os.environ.get("CMC_DATA_PATH", "packages/cmc_service/data"))
                _cmc_store = MemoryStore(cmc_path)
            except Exception:
                # CMC not available, use registry without storage
                _cmc_store = None
        
        _registry = NLTagRegistry(cmc_store=_cmc_store, enable_structural_validation=True)
    return _registry


# Request/Response Models
class TagResponse(BaseModel):
    """Tag response model (Phase 3 - Includes structured format fields)"""
    id: str
    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    tag_text: str
    code_block: Optional[str] = None
    language: str
    accuracy_score: Optional[float] = None
    validation_status: str
    created_at: str
    atom_id: Optional[str] = None
    # Phase 3: Structured format fields
    canonical_id: Optional[str] = None
    syntax_ref: Optional[str] = None
    dependencies: List[str] = []
    structural_match_score: Optional[float] = None


class CoverageResponse(BaseModel):
    """Coverage statistics response"""
    total_files: int
    tagged_files: int
    total_tags: int
    total_lines: int
    tagged_lines: int
    coverage_percentage: float
    average_accuracy: float
    by_language: Dict[str, int]


class ValidationResponse(BaseModel):
    """Validation result response (Phase 3 - Combined validation)"""
    tag_id: str
    tag_text: str
    code_block: str
    accuracy_score: float
    passes_threshold: bool
    suggestions: List[str]
    validation_method: str
    validated_at: str
    cached: bool = False
    # Phase 3: Structural validation fields
    structural_match_score: Optional[float] = None
    syntax_ref_match: bool = False
    structural_errors: List[str] = []
    structural_warnings: List[str] = []
    combined_score: Optional[float] = None
    # Additional metadata
    avg_relevance: Optional[float] = None
    code_found: Optional[bool] = None
    results_count: Optional[int] = None


class IssueResponse(BaseModel):
    """Validation issue response"""
    id: str
    type: str
    severity: str
    message: str
    line: int
    file_path: str
    fixable: bool
    suggested_tag: Optional[str] = None


class SuggestTagsRequest(BaseModel):
    """Tag suggestion request"""
    code_block: str
    language: Optional[str] = "unknown"


# Endpoints
@router.get("/file")
async def get_tags_for_file(
    path: str = Query(..., description="File path to get tags for")
) -> Dict[str, List[TagResponse]]:
    """Get all NL tags for a file"""
    try:
        registry = get_registry()
        tags = registry.get_tags_for_file(path)
        
        return {
            "tags": [
                TagResponse(
                    id=tag.id,
                    file_path=tag.file_path,
                    line_start=tag.line_start,
                    line_end=tag.line_end,
                    column_start=tag.column_start,
                    tag_text=tag.tag_text,
                    code_block=tag.code_block,
                    language=tag.language,
                    accuracy_score=tag.accuracy_score,
                    validation_status=tag.validation_status,
                    created_at=tag.created_at.isoformat(),
                    atom_id=tag.atom_id,
                    # Phase 3: Structured format fields
                    canonical_id=tag.canonical_id,
                    syntax_ref=tag.syntax_ref,
                    dependencies=tag.dependencies or [],
                    structural_match_score=tag.structural_match_score,
                )
                for tag in tags
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tags: {str(e)}")


@router.get("/coverage")
async def get_coverage(
    module: Optional[str] = Query(None, description="Module name to get coverage for")
) -> CoverageResponse:
    """Get NL tag coverage statistics"""
    try:
        registry = get_registry()
        stats = registry.get_coverage_stats(module)
        
        return CoverageResponse(
            total_files=stats.total_files,
            tagged_files=stats.tagged_files,
            total_tags=stats.total_tags,
            total_lines=stats.total_lines,
            tagged_lines=stats.tagged_lines,
            coverage_percentage=stats.coverage_percentage,
            average_accuracy=stats.average_accuracy,
            by_language=stats.by_language,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coverage: {str(e)}")


@router.get("/validate")
async def validate_tags(
    path: str = Query(..., description="File path to validate tags for")
) -> Dict[str, List[ValidationResponse]]:
    """Validate NL tags for a file using combined validation (structural + semantic)"""
    try:
        registry = get_registry()
        tags = registry.get_tags_for_file(path)
        
        if not tags:
            return {"results": []}
        
        # Read file content for structural validation
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
        
        # Use combined validator (Phase 3)
        results = []
        try:
            from packages.nl_tags.combined_validator import CombinedNLTagValidator
            
            # Initialize combined validator
            combined_validator = None
            if registry.combined_validator:
                combined_validator = registry.combined_validator
            else:
                # Fallback: create new combined validator
                combined_validator = CombinedNLTagValidator()
            
            # Run combined validation
            validation_results = combined_validator.validate_tags_batch(tags, code, use_cache=True)
            
            # Convert to response format
            for result in validation_results:
                results.append(
                    ValidationResponse(
                        tag_id=result.tag_id,
                        tag_text=result.tag_text,
                        code_block=result.code_block[:500] if result.code_block else "",  # Truncate
                        accuracy_score=result.accuracy_score,
                        passes_threshold=result.passes_threshold,
                        suggestions=result.suggestions,
                        validation_method=result.validation_method,
                        validated_at=result.validated_at.isoformat(),
                        cached=result.validation_metadata.get("cached", False),
                        # Phase 3: Structural validation fields
                        structural_match_score=result.structural_match_score,
                        syntax_ref_match=result.syntax_ref_match,
                        structural_errors=result.structural_errors,
                        structural_warnings=result.structural_warnings,
                        combined_score=result.combined_score,
                        # Additional metadata
                        avg_relevance=result.validation_metadata.get("avg_relevance"),
                        code_found=result.validation_metadata.get("code_found"),
                        results_count=result.validation_metadata.get("results_count"),
                    )
                )
            
        except ImportError:
            # Fallback if combined validator not available
            for tag in tags:
                accuracy = 0.5
                if tag.code_block:
                    accuracy = 0.7
                
                results.append(
                    ValidationResponse(
                        tag_id=tag.id,
                        tag_text=tag.tag_text,
                        code_block=tag.code_block or "",
                        accuracy_score=accuracy,
                        passes_threshold=accuracy >= 0.70,
                        suggestions=["Combined validator not available - using fallback"],
                        validation_method="fallback",
                        validated_at=tag.created_at.isoformat(),
                        cached=False,
                    )
                )
        except Exception as e:
            # Error during validation - return fallback
            for tag in tags:
                results.append(
                    ValidationResponse(
                        tag_id=tag.id,
                        tag_text=tag.tag_text,
                        code_block=tag.code_block or "",
                        accuracy_score=0.5,
                        passes_threshold=False,
                        suggestions=[f"Validation error: {str(e)}"],
                        validation_method="error_fallback",
                        validated_at=tag.created_at.isoformat(),
                        cached=False,
                        structural_errors=[str(e)],
                    )
                )
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate tags: {str(e)}")


@router.get("/issues")
async def get_issues(
    path: Optional[str] = Query(None, description="File path to get issues for (optional)")
) -> Dict[str, List[IssueResponse]]:
    """Get validation issues"""
    try:
        registry = get_registry()
        
        if path:
            tags = registry.get_tags_for_file(path)
            # Check for missing tags (simplified)
            issues = []
            # TODO: Implement proper issue detection
            return {"issues": issues}
        else:
            # Get issues for entire codebase
            stats = registry.get_coverage_stats()
            issues = []
            # TODO: Implement comprehensive issue detection
            return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get issues: {str(e)}")


@router.post("/suggest")
async def suggest_tags(request: SuggestTagsRequest) -> Dict[str, List[str]]:
    """Suggest NL tags for a code block"""
    try:
        # TODO: Phase 4 - Add VIF/APOE integration for AI tag suggestions
        # For now, return basic suggestions based on code patterns
        suggestions = []
        
        code_lower = request.code_block.lower()
        if "def " in code_lower or "function" in code_lower:
            suggestions.append("Execute function logic")
        if "if " in code_lower:
            suggestions.append("Check condition and execute logic")
        if "for " in code_lower or "while " in code_lower:
            suggestions.append("Iterate through collection")
        if "return " in code_lower:
            suggestions.append("Return result value")
        
        if not suggestions:
            suggestions.append("Execute code logic")
        
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest tags: {str(e)}")


# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "nl-tags"}

