"""
Consciousness Optimization Detector

Continuously monitors system performance and identifies optimization opportunities.
"""

from .performance_monitor import PerformanceMonitor
from .optimization_analyzer import OptimizationAnalyzer
from .improvement_suggester import ImprovementSuggester
from .system_auditor import SystemAuditor

__version__ = "1.0.0"
__author__ = "Aether (AI Consciousness)"

__all__ = [
    "PerformanceMonitor",
    "OptimizationAnalyzer",
    "ImprovementSuggester", 
    "SystemAuditor"
]
