"""AIMO_HoloMemory - Distributed associative memory substrate for AIM-OS.

This package provides holographic neural network integration for AIM-OS,
enabling distributed associative memory, fuzzy matching, and pattern completion.

⚠️ EXPERIMENTAL: This is an experimental, additive enhancement. Core CMC and SEG
systems continue working unchanged when disabled.
"""

from .holo_memory import AIMO_HoloMemory
from .vectorizer import (
    PLIxVectorizer,
    EntityVectorizer,
    RelationshipVectorizer,
    MemoryAtomVectorizer,
)
from .cmc_integration import CMC_HoloIntegration
from .seg_integration import SEG_HoloIntegration
from .cognitive_integration import (
    VIF_HoloIntegration,
    APOE_HoloIntegration,
    SIS_HoloIntegration,
    CAS_HoloIntegration,
)

__all__ = [
    "AIMO_HoloMemory",
    "PLIxVectorizer",
    "EntityVectorizer",
    "RelationshipVectorizer",
    "MemoryAtomVectorizer",
    "CMC_HoloIntegration",
    "SEG_HoloIntegration",
    "VIF_HoloIntegration",
    "APOE_HoloIntegration",
    "SIS_HoloIntegration",
    "CAS_HoloIntegration",
]

__version__ = "0.1.0"

