"""
Router (APOE-MCP Router) - Intelligent tool selection system.

This package provides intelligent tool selection for AIM-OS, integrating
with APOE, VIF, SEG, CMC, HHNI, and TCS systems.
"""

__version__ = "0.1.0"

from .core.router import Router
from .core.scout import ScoutLLM
from .core.bandit import BanditScorer
from .core.rules import RulesEngine
from .core.manifest import ToolManifest

__all__ = [
    "Router",
    "ScoutLLM",
    "BanditScorer",
    "RulesEngine",
    "ToolManifest",
]

