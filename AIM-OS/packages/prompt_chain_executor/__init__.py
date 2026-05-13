"""
Prompt Chain Executor Package
Phase 1: Single Agent Dynamic Execution

Provides chain execution engine with:
- Dynamic conditional branching
- Quality gates
- State management
- Confidence routing
- Integration with APOE
"""

from .executor import (
    ChainExecutor,
    ChainStatus,
    StepStatus,
    QualityGateStatus,
    StepResult,
    QualityGate,
    ChainExecutionState,
    get_chain_executor
)

from .mcp_integration import execute_prompt_chain_via_mcp

__all__ = [
    "ChainExecutor",
    "ChainStatus",
    "StepStatus",
    "QualityGateStatus",
    "StepResult",
    "QualityGate",
    "ChainExecutionState",
    "get_chain_executor",
    "execute_prompt_chain_via_mcp"
]

