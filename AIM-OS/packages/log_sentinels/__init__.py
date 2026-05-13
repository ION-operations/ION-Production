"""
Log-Sentinels (Hybrid) - Comprehensive log analysis system.

This package provides hybrid cloud/local log analysis for AIM-OS,
integrating with Router, SEG, VIF, CMC, and TCS systems.
"""

__version__ = "0.1.0"

from .core.pipeline import LogSentinelsPipeline
from .core.collectors import LogCollector, BrowserConsoleCollector, TerminalCollector, BackendAPICollector
from .core.normalizer import LogNormalizer
from .core.template_miner import LogTemplateMiner
from .core.windower import Windower
from .core.scout import ScoutAdapter
from .core.forensics import ForensicsAdapter
from .core.router_policy import RouterPolicy

__all__ = [
    "LogSentinelsPipeline",
    "LogCollector",
    "BrowserConsoleCollector",
    "TerminalCollector",
    "BackendAPICollector",
    "LogNormalizer",
    "LogTemplateMiner",
    "Windower",
    "ScoutAdapter",
    "ForensicsAdapter",
    "RouterPolicy",
]

