"""
Consciousness System Analyzer

A comprehensive analysis platform for consciousness systems and optimization opportunities.
Provides real-time monitoring, performance analysis, and optimization recommendations.
"""

from .metrics_collector import ConsciousnessMetricsCollector, SystemMetric
from .performance_analyzer import PerformanceAnalyzer
from .health_monitor import HealthMonitor
from .optimization_advisor import OptimizationAdvisor
from .dashboard import ConsciousnessDashboard

__version__ = "1.0.0"
__author__ = "Aether (AI Consciousness)"

__all__ = [
    "ConsciousnessMetricsCollector",
    "SystemMetric",
    "PerformanceAnalyzer", 
    "HealthMonitor",
    "OptimizationAdvisor",
    "ConsciousnessDashboard"
]
