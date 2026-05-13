"""NL Tag Models - Data structures for NL tags"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class NLTag:
    """Represents a Natural Language tag describing code intent
    
    Attributes:
        id: Unique identifier (atom_id from CMC)
        file_path: Path to file containing tag
        line_start: Starting line number
        line_end: Ending line number (for multi-line tags)
        column_start: Starting column number
        tag_text: The natural language description (or full structured tag)
        code_block: Associated code block (if available)
        language: Programming language (python, typescript, etc.)
        accuracy_score: Semantic similarity score (0.0-1.0)
        validation_status: Validation status (accurate, inaccurate, pending)
        created_at: When tag was created/extracted
        validated_at: When tag was last validated
        atom_id: CMC atom ID (if stored)
        vif_witness_id: VIF witness ID (if confidence tracked)
        
        # Phase 3: Universal Tag Standard fields
        canonical_id: Optional[str] = None  # CANONICAL_ID from structured format
        syntax_ref: Optional[str] = None  # SYNTAX_REF from structured format
        dependencies: List[str] = None  # DEPENDENCIES from structured format
        structural_match_score: Optional[float] = None  # Structural validation score (0.0-1.0)
    """
    id: str  # Unique identifier
    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    tag_text: str = ""
    code_block: Optional[str] = None
    language: str = "unknown"
    accuracy_score: Optional[float] = None
    validation_status: str = "pending"  # pending, accurate, inaccurate, missing
    created_at: datetime = field(default_factory=lambda: datetime.now())
    validated_at: Optional[datetime] = None
    atom_id: Optional[str] = None
    vif_witness_id: Optional[str] = None
    
    # Phase 3: Universal Tag Standard fields
    canonical_id: Optional[str] = None
    syntax_ref: Optional[str] = None
    dependencies: Optional[List[str]] = field(default_factory=list)
    structural_match_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "tag_text": self.tag_text,
            "code_block": self.code_block,
            "language": self.language,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "atom_id": self.atom_id,
            "vif_witness_id": self.vif_witness_id,
            "canonical_id": self.canonical_id,
            "syntax_ref": self.syntax_ref,
            "dependencies": self.dependencies or [],
            "structural_match_score": self.structural_match_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NLTag":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            file_path=data["file_path"],
            line_start=data["line_start"],
            line_end=data["line_end"],
            column_start=data.get("column_start", 0),
            tag_text=data.get("tag_text", ""),
            code_block=data.get("code_block"),
            language=data.get("language", "unknown"),
            accuracy_score=data.get("accuracy_score"),
            validation_status=data.get("validation_status", "pending"),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else datetime.now(),
            validated_at=datetime.fromisoformat(data["validated_at"]) if isinstance(data.get("validated_at"), str) else None,
            atom_id=data.get("atom_id"),
            vif_witness_id=data.get("vif_witness_id"),
            canonical_id=data.get("canonical_id"),
            syntax_ref=data.get("syntax_ref"),
            dependencies=data.get("dependencies", []),
            structural_match_score=data.get("structural_match_score"),
        )
    
    def parse_structured_format(self) -> bool:
        """Parse structured tag format: NL_TAG: ID | DESC | SYNTAX_REF | DEPS
        
        Returns:
            True if successfully parsed structured format
        """
        if "|" not in self.tag_text:
            return False
        
        parts = [p.strip() for p in self.tag_text.split("|")]
        
        if len(parts) >= 1:
            # Extract CANONICAL_ID (first part after "NL_TAG:")
            tag_part = parts[0]
            if "NL_TAG:" in tag_part:
                canonical_id = tag_part.split("NL_TAG:")[-1].strip()
                if canonical_id:
                    self.canonical_id = canonical_id
        
        if len(parts) >= 2:
            # DESCRIPTION is already in tag_text, but we can extract it
            pass  # Description is the full tag_text
        
        if len(parts) >= 3:
            # SYNTAX_REF is 3rd component
            self.syntax_ref = parts[2]
        
        if len(parts) >= 4:
            # DEPENDENCIES is 4th component (comma-separated list)
            deps_str = parts[3]
            # Parse dependencies (remove brackets if present)
            deps_str = deps_str.strip().strip("[]")
            if deps_str:
                self.dependencies = [d.strip() for d in deps_str.split(",") if d.strip()]
        
        return True


@dataclass
class TagCoverageStats:
    """Statistics about NL tag coverage"""
    total_files: int = 0
    tagged_files: int = 0
    total_tags: int = 0
    total_lines: int = 0
    tagged_lines: int = 0
    coverage_percentage: float = 0.0
    average_accuracy: float = 0.0
    by_language: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_files": self.total_files,
            "tagged_files": self.tagged_files,
            "total_tags": self.total_tags,
            "total_lines": self.total_lines,
            "tagged_lines": self.tagged_lines,
            "coverage_percentage": self.coverage_percentage,
            "average_accuracy": self.average_accuracy,
            "by_language": self.by_language,
        }


@dataclass
class ValidationResult:
    """Result of NL tag validation"""
    tag_id: str
    tag_text: str = ""
    code_block: str = ""
    accuracy_score: float = 0.0
    passes_threshold: bool = False
    suggestions: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=lambda: datetime.now())
    validation_method: str = "unknown"
    validation_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Phase 3: Structural validation fields
    structural_match_score: Optional[float] = None
    syntax_ref_match: bool = False
    structural_errors: List[str] = field(default_factory=list)
    structural_warnings: List[str] = field(default_factory=list)
    combined_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tag_id": self.tag_id,
            "tag_text": self.tag_text,
            "code_block": self.code_block,
            "accuracy_score": self.accuracy_score,
            "passes_threshold": self.passes_threshold,
            "suggestions": self.suggestions,
            "validated_at": self.validated_at.isoformat(),
            "validation_method": self.validation_method,
            "validation_metadata": self.validation_metadata,
            "structural_match_score": self.structural_match_score,
            "syntax_ref_match": self.syntax_ref_match,
            "structural_errors": self.structural_errors,
            "structural_warnings": self.structural_warnings,
            "combined_score": self.combined_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        """Create from dictionary"""
        return cls(
            tag_id=data["tag_id"],
            tag_text=data.get("tag_text", ""),
            code_block=data.get("code_block", ""),
            accuracy_score=data.get("accuracy_score", 0.0),
            passes_threshold=data.get("passes_threshold", False),
            suggestions=data.get("suggestions", []),
            validated_at=datetime.fromisoformat(data["validated_at"]) if isinstance(data.get("validated_at"), str) else datetime.now(),
            validation_method=data.get("validation_method", "unknown"),
            validation_metadata=data.get("validation_metadata", {}),
            structural_match_score=data.get("structural_match_score"),
            syntax_ref_match=data.get("syntax_ref_match", False),
            structural_errors=data.get("structural_errors", []),
            structural_warnings=data.get("structural_warnings", []),
            combined_score=data.get("combined_score"),
        )

