"""NL Tag Registry - Manage NL tags across codebase

Provides querying, coverage tracking, and tag management capabilities.
Integrates with CMC for storage and retrieval.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Set, Any
from pathlib import Path
from datetime import datetime

from .models import NLTag, TagCoverageStats
from .tag_parser import NLTagParser
from .combined_validator import CombinedNLTagValidator
from .structural_validator import StructuralValidator
from .semantic_validator import NLTagSemanticValidator


class NLTagRegistry:
    """Registry for managing NL tags across codebase"""
    
    def __init__(self, cmc_store=None, enable_structural_validation: bool = True):
        """Initialize registry
        
        Args:
            cmc_store: CMC MemoryStore instance (optional, for storage)
            enable_structural_validation: Whether to run structural validation (default: True)
        """
        self.cmc_store = cmc_store
        self.parser = NLTagParser()
        self._tags_cache: Dict[str, List[NLTag]] = {}
        self.enable_structural_validation = enable_structural_validation
        
        # Initialize validators (optional)
        self.structural_validator = None
        self.semantic_validator = None
        self.combined_validator = None
        
        if enable_structural_validation:
            try:
                from .structural_validator import StructuralValidator
                self.structural_validator = StructuralValidator()
            except ImportError:
                pass
        
        try:
            from .semantic_validator import NLTagSemanticValidator
            self.semantic_validator = NLTagSemanticValidator(cmc_store=cmc_store) if cmc_store else None
        except ImportError:
            pass
        
        # Initialize combined validator if both are available
        if self.structural_validator or self.semantic_validator:
            try:
                from .combined_validator import CombinedNLTagValidator
                self.combined_validator = CombinedNLTagValidator(
                    structural_validator=self.structural_validator,
                    semantic_validator=self.semantic_validator
                )
            except ImportError:
                pass
    
    def register_tags_from_file(self, file_path: str, validate: bool = True) -> List[NLTag]:
        """Extract and register tags from a file
        
        Args:
            file_path: Path to code file
            validate: Whether to run validation (default: True)
            
        Returns:
            List of extracted tags
        """
        tags = self.parser.parse_file(file_path)
        
        # Run validation if enabled
        if validate and self.combined_validator:
            try:
                # Read file content for structural validation
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Run combined validation
                validation_results = self.combined_validator.validate_tags_batch(tags, code)
                
                # Update tags with validation results
                for result in validation_results:
                    tag = next((t for t in tags if t.id == result.tag_id), None)
                    if tag:
                        tag.accuracy_score = result.accuracy_score
                        tag.structural_match_score = result.structural_match_score
                        tag.validated_at = result.validated_at
                        tag.validation_status = "accurate" if result.passes_threshold else "inaccurate"
            except Exception as e:
                # Validation failed, but continue with tag registration
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Validation failed for {file_path}: {e}")
        
        # Cache tags
        self._tags_cache[file_path] = tags
        
        # Store in CMC if available
        if self.cmc_store:
            for tag in tags:
                self._store_tag_in_cmc(tag)
        
        return tags
    
    def get_tags_for_file(self, file_path: str) -> List[NLTag]:
        """Get all tags for a file
        
        Args:
            file_path: Path to file
            
        Returns:
            List of tags for file
        """
        # Check cache first
        if file_path in self._tags_cache:
            return self._tags_cache[file_path]
        
        # Try to load from CMC
        if self.cmc_store:
            tags = self._load_tags_from_cmc(file_path)
            if tags:
                self._tags_cache[file_path] = tags
                return tags
        
        # Parse file if not cached
        return self.register_tags_from_file(file_path)
    
    def validate_tags_structurally(self, file_path: str) -> List[Dict[str, Any]]:
        """Validate tags structurally for a file
        
        Args:
            file_path: Path to file
            
        Returns:
            List of structural validation results
        """
        if not self.structural_validator:
            return []
        
        tags = self.get_tags_for_file(file_path)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            results = []
            for tag in tags:
                if tag.syntax_ref:
                    structural_result = self.structural_validator.validate_syntax_ref(tag, code)
                    
                    # Update tag with structural score
                    tag.structural_match_score = structural_result.match_score
                    
                    results.append({
                        "tag_id": tag.id,
                        "matches": structural_result.matches,
                        "match_score": structural_result.match_score,
                        "expected_signature": structural_result.expected_signature,
                        "actual_signature": structural_result.actual_signature,
                        "errors": structural_result.errors,
                        "warnings": structural_result.warnings,
                    })
            
            return results
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Structural validation failed for {file_path}: {e}")
            return []
    
    def update_tag_validation(self, tag_id: str, validation_result: Dict[str, Any]) -> bool:
        """Update tag with validation result
        
        Args:
            tag_id: Tag ID to update
            validation_result: Validation result dictionary
            
        Returns:
            True if updated successfully
        """
        # Find tag in cache
        for file_path, tags in self._tags_cache.items():
            for tag in tags:
                if tag.id == tag_id:
                    # Update tag with validation result
                    tag.accuracy_score = validation_result.get("accuracy_score")
                    tag.validation_status = "accurate" if validation_result.get("passes_threshold") else "inaccurate"
                    if validation_result.get("validated_at"):
                        from datetime import datetime
                        tag.validated_at = datetime.fromisoformat(validation_result["validated_at"]) if isinstance(validation_result["validated_at"], str) else datetime.now()
                    
                    # Update in CMC if available
                    if self.cmc_store:
                        self._store_tag_in_cmc(tag)
                    
                    return True
        
        return False
    
    def get_tags_for_module(self, module: str) -> List[NLTag]:
        """Get all tags for a module/system
        
        Args:
            module: Module name (e.g., 'vif', 'cmc')
            
        Returns:
            List of tags for module
        """
        tags = []
        
        # Find all files in module
        module_paths = self._find_module_files(module)
        
        for file_path in module_paths:
            tags.extend(self.get_tags_for_file(file_path))
        
        return tags
    
    def get_coverage_stats(self, codebase_path: Optional[str] = None) -> TagCoverageStats:
        """Calculate NL tag coverage statistics
        
        Args:
            codebase_path: Root path of codebase (optional)
            
        Returns:
            TagCoverageStats with coverage metrics
        """
        stats = TagCoverageStats()
        
        # Find all code files
        code_files = self._find_code_files(codebase_path)
        stats.total_files = len(code_files)
        
        tagged_files = 0
        total_tags = 0
        total_lines = 0
        tagged_lines = 0
        language_counts: Dict[str, int] = {}
        
        for file_path in code_files:
            tags = self.get_tags_for_file(file_path)
            
            if tags:
                tagged_files += 1
                total_tags += len(tags)
                tagged_lines += len(set(tag.line_start for tag in tags))
                
                # Count by language
                for tag in tags:
                    language_counts[tag.language] = language_counts.get(tag.language, 0) + 1
            
            # Count total lines (approximate)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        stats.tagged_files = tagged_files
        stats.total_tags = total_tags
        stats.total_lines = total_lines
        stats.tagged_lines = tagged_lines
        stats.coverage_percentage = (tagged_lines / total_lines * 100) if total_lines > 0 else 0.0
        stats.by_language = language_counts
        
        return stats
    
    def _store_tag_in_cmc(self, tag: NLTag) -> Optional[str]:
        """Store tag in CMC as atom
        
        Args:
            tag: Tag to store
            
        Returns:
            Atom ID if stored successfully
        """
        if not self.cmc_store:
            return None
        
        try:
            from packages.cmc_service.models import AtomCreate, AtomContent
            
            # Create atom with NL tag content
            atom_create = AtomCreate(
                modality="code_tag",
                content=AtomContent(
                    inline=tag.tag_text,
                    media_type="text/plain"
                ),
                tags={
                    "file_path": tag.file_path,
                    "line_number": float(tag.line_start),
                    "language": tag.language,
                    "tag_type": "nl_tag",
                },
                metadata={
                    "file_path": tag.file_path,
                    "line_start": tag.line_start,
                    "line_end": tag.line_end,
                    "column_start": tag.column_start,
                    "code_block": tag.code_block or "",
                    "language": tag.language,
                    "tag_id": tag.id,
                }
            )
            
            # Store atom
            atom = self.cmc_store.create_atom(atom_create)
            tag.atom_id = atom.id
            return atom.id
        except Exception as e:
            # Log error but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error storing tag in CMC: {e}", exc_info=True)
            return None
    
    def _load_tags_from_cmc(self, file_path: str) -> List[NLTag]:
        """Load tags from CMC for a file
        
        Args:
            file_path: Path to file
            
        Returns:
            List of tags loaded from CMC
        """
        if not self.cmc_store:
            return []
        
        try:
            # Query CMC for tags with matching file_path tag
            # Note: This queries by tag key, not tag value
            # We need to filter by metadata instead
            atoms = list(self.cmc_store.list_atoms(tag="tag_type", limit=1000))
            
            tags = []
            for atom in atoms:
                # Filter by file_path in metadata
                if atom.metadata.get("file_path") == file_path and atom.modality == "code_tag":
                    tag = NLTag(
                        id=atom.metadata.get("tag_id", atom.id),
                        file_path=file_path,
                        line_start=int(atom.metadata.get("line_start", 0)),
                        line_end=int(atom.metadata.get("line_end", atom.metadata.get("line_start", 0))),
                        column_start=int(atom.metadata.get("column_start", 0)),
                        tag_text=atom.content.inline or "",
                        code_block=atom.metadata.get("code_block"),
                        language=atom.metadata.get("language", "unknown"),
                        atom_id=atom.id,
                        created_at=atom.created_at,
                    )
                    tags.append(tag)
            
            return tags
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading tags from CMC: {e}", exc_info=True)
            return []
    
    def _find_module_files(self, module: str) -> List[str]:
        """Find all files in a module
        
        Args:
            module: Module name
            
        Returns:
            List of file paths
        """
        files = []
        
        # Look in packages/{module}/
        module_path = Path(f"packages/{module}")
        if module_path.exists():
            for file_path in module_path.rglob("*.py"):
                if not file_path.name.startswith('test_') and 'tests' not in file_path.parts:
                    files.append(str(file_path))
        
        return files
    
    def _find_code_files(self, root_path: Optional[str] = None) -> List[str]:
        """Find all code files in codebase
        
        Args:
            root_path: Root path to search (defaults to packages/)
            
        Returns:
            List of code file paths
        """
        if root_path is None:
            root_path = "packages"
        
        root = Path(root_path)
        if not root.exists():
            return []
        
        code_extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.java'}
        files = []
        
        for file_path in root.rglob("*"):
            if file_path.suffix in code_extensions:
                # Skip test files and node_modules
                if 'test_' not in file_path.name and 'node_modules' not in file_path.parts:
                    files.append(str(file_path))
        
        return files

