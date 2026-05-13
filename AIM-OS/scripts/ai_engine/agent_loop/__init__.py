"""
AIM-OS AI Engine — 3-Phase Agent Loop

Recursive agent execution loop where context management is fully
separated from task execution:

    Phase 1: Context Researcher — builds optimal context
    Phase 2: Worker — executes with clean, pre-built context
    Phase 3: Closeout — documents, prepares handoff

Usage:
    from scripts.ai_engine.agent_loop.models import LoopConfig
    from scripts.ai_engine.agent_loop.orchestrator import LoopOrchestrator
    
    orchestrator = LoopOrchestrator(LoopConfig(strategy='standard'))
    result = orchestrator.run("Audit the registry module", max_iterations=3)
    print(result.summary())
"""

# Lazy-export — avoid triggering heavy import chains at module level
from .models import (
    LoopConfig, ContextPack, WorkResult, Handoff,
    LoopResult, PhaseType, StrategyType,
)
from .diagnostics import PhaseMetrics, DiagnosticsCollector

# LoopOrchestrator is NOT imported at module level to avoid
# triggering GeminiCLIProvider's heavy import chain.
# Import it directly when needed:
#   from scripts.ai_engine.agent_loop.orchestrator import LoopOrchestrator

__all__ = [
    'LoopConfig', 'LoopResult',
    'ContextPack', 'WorkResult', 'Handoff',
    'PhaseMetrics', 'DiagnosticsCollector',
    'PhaseType', 'StrategyType',
]
