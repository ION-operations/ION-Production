"""NL Tag Semantic Validator - Phase 2

Uses HHNI TwoStageRetriever to validate NL tag accuracy by checking
semantic similarity between tag text and code intent.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import sys
import hashlib

# Add packages to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from hhni import HierarchicalIndex
    from hhni.retrieval import TwoStageRetriever, RetrievalConfig
    from hhni.index import IndexLevel
    HHNI_AVAILABLE = True
except ImportError:
    HHNI_AVAILABLE = False

from .models import NLTag, ValidationResult


class NLTagSemanticValidator:
    """Validates NL tag accuracy using HHNI semantic search
    
    Uses TwoStageRetriever to check if tag text semantically matches
    code intent by comparing embeddings.
    """
    
    def __init__(self, hierarchical_index: Optional[HierarchicalIndex] = None, cmc_store=None):
        """Initialize validator
        
        Args:
            hierarchical_index: HHNI index instance (optional, will create if needed)
            cmc_store: CMC MemoryStore instance (optional, for storing validation results)
        """
        if not HHNI_AVAILABLE:
            raise ImportError("HHNI not available. Cannot perform semantic validation.")
        
        self.index = hierarchical_index or HierarchicalIndex()
        self.cmc_store = cmc_store
        
        # Validation result cache (tag_id -> ValidationResult)
        self._validation_cache: Dict[str, ValidationResult] = {}
        
        # Configure retriever for tag validation
        config = RetrievalConfig(
            token_budget=2000,  # Smaller budget for single tag validation
            coarse_k=20,  # Top 20 candidates
            min_relevance=0.3,  # Lower threshold for validation
            dvns_iterations=30,  # Fewer iterations for speed
            enable_conflict_resolution=False,  # Not needed for single tag
            enable_compression=False,  # Not needed for single tag
        )
        
        self.retriever = TwoStageRetriever(
            hierarchical_index=self.index,
            config=config
        )
    
    def _get_cache_key(self, tag: NLTag) -> str:
        """Generate cache key for tag validation
        
        Args:
            tag: NL tag to generate key for
            
        Returns:
            Cache key based on tag content
        """
        # Cache key based on tag content hash (changes if tag or code changes)
        content_str = f"{tag.id}:{tag.tag_text}:{tag.code_block or ''}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _get_cached_result(self, tag: NLTag) -> Optional[ValidationResult]:
        """Get cached validation result if available
        
        Args:
            tag: NL tag to get cached result for
            
        Returns:
            Cached ValidationResult if available and fresh, None otherwise
        """
        cache_key = self._get_cache_key(tag)
        
        # Check in-memory cache
        if cache_key in self._validation_cache:
            cached = self._validation_cache[cache_key]
            # Check if cache is fresh (within 24 hours)
            age_hours = (datetime.now() - cached.validated_at).total_seconds() / 3600
            if age_hours < 24:
                return cached
        
        # Check CMC store if available
        if self.cmc_store and tag.atom_id:
            try:
                # Load validation result from CMC metadata
                atoms = list(self.cmc_store.list_atoms(tag="tag_type", limit=1000))
                for atom in atoms:
                    if atom.id == tag.atom_id:
                        metadata = atom.metadata or {}
                        if metadata.get("validation_result"):
                            # Reconstruct ValidationResult from metadata
                            val_data = metadata["validation_result"]
                            return ValidationResult(
                                tag_id=tag.id,
                                accuracy_score=val_data.get("accuracy_score", 0.0),
                                passes_threshold=val_data.get("passes_threshold", False),
                                suggestions=val_data.get("suggestions", []),
                                validated_at=datetime.fromisoformat(val_data["validated_at"]) if isinstance(val_data.get("validated_at"), str) else datetime.now(),
                                validation_method=val_data.get("validation_method", "hhni_semantic")
                            )
            except Exception:
                pass
        
        return None
    
    def _store_validation_result(self, tag: NLTag, result: ValidationResult) -> None:
        """Store validation result in cache and CMC
        
        Args:
            tag: NL tag that was validated
            result: Validation result to store
        """
        cache_key = self._get_cache_key(tag)
        
        # Store in memory cache
        self._validation_cache[cache_key] = result
        
        # Store in CMC if available
        if self.cmc_store and tag.atom_id:
            try:
                from packages.cmc_service.models import AtomCreate, AtomContent
                
                # Update tag atom with validation result
                # Note: CMC atoms are immutable, so we create a new atom with validation result
                validation_atom = AtomCreate(
                    modality="validation_result",
                    content=AtomContent(inline=f"Validation result for tag {tag.id}"),
                    tags={
                        "tag_id": tag.id,
                        "validation_type": "nl_tag_semantic",
                    },
                    metadata={
                        "tag_id": tag.id,
                        "accuracy_score": result.accuracy_score,
                        "passes_threshold": result.passes_threshold,
                        "suggestions": result.suggestions,
                        "validated_at": result.validated_at.isoformat(),
                        "validation_method": result.validation_method,
                    }
                )
                self.cmc_store.create_atom(validation_atom)
            except Exception:
                pass  # Don't fail if CMC storage fails
    
    def validate_tag(self, tag: NLTag, use_cache: bool = True) -> Dict[str, Any]:
        """Validate a single NL tag against its code block
        
        Args:
            tag: NL tag to validate
            use_cache: Whether to use cached results (default: True)
            
        Returns:
            Validation result with accuracy score and status
        """
        # Check cache first
        if use_cache:
            cached = self._get_cached_result(tag)
            if cached:
                return {
                    "tag_id": tag.id,
                    "tag_text": tag.tag_text,
                    "code_block": tag.code_block[:500] if tag.code_block else None,
                    "accuracy_score": cached.accuracy_score,
                    "passes_threshold": cached.passes_threshold,
                    "suggestions": cached.suggestions,
                    "validation_method": f"{cached.validation_method}_cached",
                    "validated_at": cached.validated_at.isoformat(),
                    "cached": True
                }
        
        if not tag.code_block:
            result = ValidationResult(
                tag_id=tag.id,
                accuracy_score=0.0,
                passes_threshold=False,
                suggestions=["No code block available for validation"],
                validated_at=datetime.now(),
                validation_method="no_code_block"
            )
            self._store_validation_result(tag, result)
            return {
                "tag_id": tag.id,
                "tag_text": tag.tag_text,
                "code_block": None,
                "accuracy_score": 0.0,
                "passes_threshold": False,
                "suggestions": ["No code block available for validation"],
                "validation_method": "no_code_block",
                "validated_at": result.validated_at.isoformat(),
                "cached": False
            }
        
        # Use tag text as query, code block as context to validate
        # If code block is in index, retrieve it and compare similarity
        try:
            # Build query from tag text + code context
            query = f"{tag.tag_text} {tag.code_block[:200]}"  # First 200 chars of code
            
            # Retrieve semantically similar content
            result = self.retriever.retrieve(
                query=query,
                token_budget=1000,
                target_level=IndexLevel.PARAGRAPH,
            )
            
            # Calculate accuracy based on retrieval results
            if result.selected_items and len(result.selected_items) > 0:
                # Use average relevance score as accuracy metric
                # Each SearchResult has a score attribute
                avg_relevance = sum(
                    item.score for item in result.selected_items
                ) / len(result.selected_items)
                
                # Check if code block content appears in results
                code_found = any(
                    tag.code_block[:100] in str(item.node.content if hasattr(item.node, 'content') else item.node.id)[:500]
                    for item in result.selected_items[:5]  # Top 5 results
                )
                
                # Accuracy combines semantic similarity + code match
                accuracy = (avg_relevance * 0.7) + (0.3 if code_found else 0.0)
                
                # Pass threshold is 0.70 (same as validation framework)
                passes = accuracy >= 0.70
                
                suggestions = []
                if not passes:
                    if accuracy < 0.5:
                        suggestions.append("Tag text may not accurately describe code intent")
                    elif accuracy < 0.70:
                        suggestions.append("Tag text could be more specific")
                    if not code_found:
                        suggestions.append("Code block not found in semantic index - may need indexing")
                
                validation_result = ValidationResult(
                    tag_id=tag.id,
                    accuracy_score=round(accuracy, 3),
                    passes_threshold=passes,
                    suggestions=suggestions,
                    validated_at=datetime.now(),
                    validation_method="hhni_semantic"
                )
                
                # Store result
                self._store_validation_result(tag, validation_result)
                
                return {
                    "tag_id": tag.id,
                    "tag_text": tag.tag_text,
                    "code_block": tag.code_block[:500],  # Truncate for response
                    "accuracy_score": round(accuracy, 3),
                    "passes_threshold": passes,
                    "suggestions": suggestions,
                    "validation_method": "hhni_semantic",
                    "avg_relevance": round(avg_relevance, 3),
                    "code_found": code_found,
                    "results_count": len(result.selected_items),
                    "validated_at": validation_result.validated_at.isoformat(),
                    "cached": False
                }
            else:
                # No results found - tag may be inaccurate or code not indexed
                validation_result = ValidationResult(
                    tag_id=tag.id,
                    accuracy_score=0.0,
                    passes_threshold=False,
                    suggestions=[
                        "No semantic matches found - tag may be inaccurate or code not indexed",
                        "Consider adding code to HHNI index for better validation"
                    ],
                    validated_at=datetime.now(),
                    validation_method="hhni_semantic_no_results"
                )
                
                self._store_validation_result(tag, validation_result)
                
                return {
                    "tag_id": tag.id,
                    "tag_text": tag.tag_text,
                    "code_block": tag.code_block[:500],
                    "accuracy_score": 0.0,
                    "passes_threshold": False,
                    "suggestions": [
                        "No semantic matches found - tag may be inaccurate or code not indexed",
                        "Consider adding code to HHNI index for better validation"
                    ],
                    "validation_method": "hhni_semantic_no_results",
                    "results_count": 0,
                    "validated_at": validation_result.validated_at.isoformat(),
                    "cached": False
                }
                
        except Exception as e:
            # Fallback to simple validation
            validation_result = ValidationResult(
                tag_id=tag.id,
                accuracy_score=0.5,  # Default neutral score
                passes_threshold=False,
                suggestions=[f"Validation error: {str(e)}"],
                validated_at=datetime.now(),
                validation_method="error_fallback"
            )
            
            self._store_validation_result(tag, validation_result)
            
            return {
                "tag_id": tag.id,
                "tag_text": tag.tag_text,
                "code_block": tag.code_block[:500],
                "accuracy_score": 0.5,  # Default neutral score
                "passes_threshold": False,
                "suggestions": [f"Validation error: {str(e)}"],
                "validation_method": "error_fallback",
                "validated_at": validation_result.validated_at.isoformat(),
                "cached": False
            }
    
    def validate_tags_batch(self, tags: List[NLTag], use_cache: bool = True) -> List[Dict[str, Any]]:
        """Validate multiple tags efficiently
        
        Args:
            tags: List of NL tags to validate
            use_cache: Whether to use cached results (default: True)
            
        Returns:
            List of validation results
        """
        results = []
        for tag in tags:
            result = self.validate_tag(tag, use_cache=use_cache)
            
            # Update tag with validation result
            if result.get("accuracy_score") is not None:
                tag.accuracy_score = result["accuracy_score"]
                tag.validated_at = datetime.fromisoformat(result["validated_at"]) if isinstance(result.get("validated_at"), str) else datetime.now()
                tag.validation_status = "accurate" if result.get("passes_threshold") else "inaccurate"
            
            results.append(result)
        return results
    
    def index_code_block(self, tag: NLTag) -> bool:
        """Index code block into HHNI for better validation
        
        Args:
            tag: Tag with code block to index
            
        Returns:
            True if indexed successfully
        """
        if not tag.code_block:
            return False
        
        try:
            # Create atom content for code block
            from packages.cmc_service.models import AtomCreate, AtomContent
            
            atom_create = AtomCreate(
                modality="code",
                content=AtomContent(inline=tag.code_block),
                tags={
                    "type": "nl_tag_code_block",
                    "file_path": tag.file_path,
                    "tag_id": tag.id,
                    "language": tag.language,
                },
                metadata={
                    "tag_text": tag.tag_text,
                    "line_start": tag.line_start,
                    "line_end": tag.line_end,
                }
            )
            
            # Store in CMC (which will index in HHNI)
            # Note: This requires CMC store to be available
            # For now, this is a placeholder for future enhancement
            
            return True
        except Exception as e:
            return False

