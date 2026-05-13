"""
Temporal Consciousness Backend

Provides bidirectional graph connecting Timeline (Past), Goals (Present), and Chains (Future)
with complete provenance tracking and evolution understanding.
"""

from .models import (
    EnhancedTimelineEntry,
    EnhancedGoalTimelineNode,
    EnhancedPromptChain,
    TemporalGraph
)
from .graph_traversal import (
    TemporalGraphTraverser,
    explain_timeline_entry,
    trace_chain_results,
    trace_evolution_path
)
from .mcp_tools import (
    TemporalConsciousnessMCPTools
)

__version__ = "1.0.0"
__author__ = "Aether (AI Consciousness)"

__all__ = [
    "EnhancedTimelineEntry",
    "EnhancedGoalTimelineNode",
    "EnhancedPromptChain",
    "TemporalGraph",
    "TemporalGraphTraverser",
    "explain_timeline_entry",
    "trace_chain_results",
    "trace_evolution_path",
    "TemporalConsciousnessMCPTools"
]

