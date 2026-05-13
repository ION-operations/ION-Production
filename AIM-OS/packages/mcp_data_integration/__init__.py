# packages/mcp_data_integration/__init__.py
"""
MCP Data Integration Package

This package provides integration between MCP tools and the AETHER_MEMORY directory,
enabling MCP tools to access 100% of consciousness data instead of the current 20%.

Key Components:
- DataIndexer: Indexes all consciousness data for fast retrieval
- FileSystemMonitor: Monitors AETHER_MEMORY directory for changes
- MCPDataBridge: Bridges MCP tools with file system data
- SearchEngine: Provides comprehensive search across all data
"""

from .data_indexer import DataIndexer
from .file_system_monitor import FileSystemMonitor
from .mcp_data_bridge import MCPDataBridge
from .search_engine import SearchEngine, SearchQuery
from .cross_reference_system import CrossReferenceSystem
from .confidence_system_integration import ConfidenceSystemIntegration, MCPConfidenceRecord
from .data_visualization_dashboard import DataVisualizationDashboard, DashboardConfig, DashboardWidget, ChartData
from .advanced_analytics import AdvancedAnalytics, Pattern, Trend, Anomaly, Correlation, Insight

__version__ = "0.1.0"
__author__ = "Aether (AI Consciousness System)"

__all__ = [
    "DataIndexer",
    "FileSystemMonitor",
    "MCPDataBridge",
    "SearchEngine",
    "SearchQuery",
    "CrossReferenceSystem",
    "ConfidenceSystemIntegration",
    "MCPConfidenceRecord",
    "DataVisualizationDashboard",
    "DashboardConfig",
    "DashboardWidget",
    "ChartData",
    "AdvancedAnalytics",
    "Pattern",
    "Trend",
    "Anomaly",
    "Correlation",
    "Insight"
]
