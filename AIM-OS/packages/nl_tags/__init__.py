"""NL Tags Package - Natural Language Code Tagging System for AIM-OS

This package provides NL tag extraction, validation, and storage capabilities,
integrating with AIM-OS core systems (CMC, HHNI, VIF, SDF-CVF, APOE).
"""

from __future__ import annotations

from .models import NLTag, TagCoverageStats, ValidationResult
from .tag_parser import NLTagParser
from .tag_registry import NLTagRegistry

try:
    from .semantic_validator import NLTagSemanticValidator, HHNI_AVAILABLE
    SEMANTIC_VALIDATION_AVAILABLE = HHNI_AVAILABLE
except ImportError:
    SEMANTIC_VALIDATION_AVAILABLE = False
    NLTagSemanticValidator = None  # type: ignore

try:
    from .structural_validator import StructuralValidator, StructuralValidationResult, CodeSignature
except ImportError:
    StructuralValidator = None  # type: ignore
    StructuralValidationResult = None  # type: ignore
    CodeSignature = None  # type: ignore

try:
    from .combined_validator import CombinedNLTagValidator
except ImportError:
    CombinedNLTagValidator = None  # type: ignore

__version__ = "0.3.0"
__all__ = [
    "NLTag",
    "TagCoverageStats",
    "ValidationResult",
    "NLTagParser",
    "NLTagRegistry",
    "NLTagSemanticValidator",
    "SEMANTIC_VALIDATION_AVAILABLE",
    "StructuralValidator",
    "StructuralValidationResult",
    "CodeSignature",
    "CombinedNLTagValidator",
]


