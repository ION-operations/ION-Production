"""
AIM-OS AI Engine — 3-Phase Agent Loop Data Models

All data structures for the loop pipeline:
    LoopConfig — dynamic configuration for strategy testing
    ContextPack — Phase 1 output (worker's pre-built context)
    WorkResult — Phase 2 output (what the worker accomplished)
    Handoff — Phase 3 output (input for next iteration)
    LoopResult — final result of a complete loop run
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PhaseType(str, Enum):
    CONTEXT = 'context'
    WORKER = 'worker'
    CLOSEOUT = 'closeout'


class StrategyType(str, Enum):
    STANDARD = 'standard'
    DEEP_RESEARCH = 'deep_research'
    MINIMAL = 'minimal'
    FULL_MCP = 'full_mcp'
    CUSTOM = 'custom'


# ══════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════

@dataclass
class LoopConfig:
    """Dynamic configuration for testing different agent loop strategies.

    Switch between strategies to A/B test different approaches:
        standard     — MCP context + history → no-MCP worker → MCP closeout
        deep_research — full indexing + analysis → extended worker → full docs
        minimal      — brief summary only → minimal worker → lightweight handoff
        full_mcp     — MCP everywhere (like traditional IDE agents)
    """
    strategy: str = StrategyType.STANDARD
    max_iterations: int = 5

    # Per-phase MCP access
    context_mcp_access: bool = True
    worker_mcp_access: bool = False       # Key insight: worker stays clean
    closeout_mcp_access: bool = True

    # Context depth control
    context_depth: str = 'medium'         # 'shallow', 'medium', 'deep'

    # Model selection per phase (allows testing different models)
    model_per_phase: Dict[str, str] = field(default_factory=lambda: {
        'context': 'auto',
        'worker': 'auto',
        'closeout': 'auto',
    })

    # Timeout per phase (seconds)
    timeout_per_phase: Dict[str, int] = field(default_factory=lambda: {
        'context': 60,
        'worker': 120,
        'closeout': 60,
    })

    # Working directory
    workspace_root: str = ''

    # Verbose logging
    verbose: bool = False

    @classmethod
    def from_strategy(cls, strategy: str, **overrides) -> 'LoopConfig':
        """Create config from a named strategy with optional overrides."""
        presets = {
            'standard': {},
            'deep_research': {
                'context_depth': 'deep',
                'timeout_per_phase': {'context': 120, 'worker': 180, 'closeout': 90},
            },
            'minimal': {
                'context_depth': 'shallow',
                'context_mcp_access': False,
                'closeout_mcp_access': False,
                'timeout_per_phase': {'context': 30, 'worker': 90, 'closeout': 30},
            },
            'full_mcp': {
                'worker_mcp_access': True,
            },
        }
        preset = presets.get(strategy, {})
        preset.update(overrides)
        return cls(strategy=strategy, **preset)


# ══════════════════════════════════════════════════════════
# PHASE DATA MODELS
# ══════════════════════════════════════════════════════════

@dataclass
class ContextPack:
    """Output of Phase 1 — the worker's pre-built context.

    The Context Researcher agent produces this by analyzing MCP state,
    chat history, project state, and the current task. The worker
    receives ONLY this — no raw history, no MCP access.
    """
    task_summary: str = ''
    relevant_history: str = ''
    project_state: str = ''
    instructions: str = ''
    files_to_examine: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

    # Metadata
    research_notes: str = ''
    tokens_used: int = 0
    build_time_ms: float = 0.0

    def to_prompt(self) -> str:
        """Serialize into a prompt for the worker agent."""
        sections = []

        if self.task_summary:
            sections.append(f"# Task\n{self.task_summary}")

        if self.instructions:
            sections.append(f"## Instructions\n{self.instructions}")

        if self.relevant_history:
            sections.append(f"## Context from Previous Work\n{self.relevant_history}")

        if self.project_state:
            sections.append(f"## Current Project State\n{self.project_state}")

        if self.files_to_examine:
            files_list = '\n'.join(f'- `{f}`' for f in self.files_to_examine)
            sections.append(f"## Key Files\n{files_list}")

        if self.constraints:
            constraints_list = '\n'.join(f'- {c}' for c in self.constraints)
            sections.append(f"## Constraints\n{constraints_list}")

        if self.references:
            refs_list = '\n'.join(f'- {r}' for r in self.references)
            sections.append(f"## References\n{refs_list}")

        return '\n\n'.join(sections)

    def to_dict(self) -> dict:
        return {
            'task_summary': self.task_summary,
            'relevant_history': self.relevant_history,
            'project_state': self.project_state,
            'instructions': self.instructions,
            'files_to_examine': self.files_to_examine,
            'constraints': self.constraints,
            'references': self.references,
            'tokens_used': self.tokens_used,
            'build_time_ms': self.build_time_ms,
        }


@dataclass
class WorkResult:
    """Output of Phase 2 — what the worker accomplished."""
    success: bool = False
    output: str = ''
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)
    issues_encountered: List[str] = field(default_factory=list)
    suggested_next_steps: List[str] = field(default_factory=list)

    # Raw output from the LLM
    raw_response: str = ''
    tokens_used: int = 0
    work_time_ms: float = 0.0
    model_used: str = ''

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'output': self.output[:1000],  # Truncate for handoff
            'files_modified': self.files_modified,
            'files_created': self.files_created,
            'decisions_made': self.decisions_made,
            'issues_encountered': self.issues_encountered,
            'suggested_next_steps': self.suggested_next_steps,
            'tokens_used': self.tokens_used,
            'work_time_ms': self.work_time_ms,
            'model_used': self.model_used,
        }


@dataclass
class Handoff:
    """Output of Phase 3 — input for the next iteration's Phase 1.

    This is the bridge between iterations. The Closeout agent
    produces it, and the next Context Researcher reads it.
    """
    task: str = ''
    task_complete: bool = False
    iteration_summary: str = ''
    cumulative_progress: str = ''
    open_issues: List[str] = field(default_factory=list)
    next_priorities: List[str] = field(default_factory=list)
    quality_score: float = 0.0         # 0-1, assessed by closeout
    context_quality_score: float = 0.0  # How good was the context pack?

    # Metadata
    iteration: int = 0
    closeout_time_ms: float = 0.0
    tokens_used: int = 0

    def to_dict(self) -> dict:
        return {
            'task': self.task,
            'task_complete': self.task_complete,
            'iteration': self.iteration,
            'iteration_summary': self.iteration_summary,
            'cumulative_progress': self.cumulative_progress,
            'open_issues': self.open_issues,
            'next_priorities': self.next_priorities,
            'quality_score': self.quality_score,
            'context_quality_score': self.context_quality_score,
        }

    def to_prompt(self) -> str:
        """Serialize into a prompt for the next Context Researcher."""
        parts = [f"# Handoff from Iteration {self.iteration}"]

        if self.cumulative_progress:
            parts.append(f"## Progress So Far\n{self.cumulative_progress}")

        if self.iteration_summary:
            parts.append(f"## Last Iteration Summary\n{self.iteration_summary}")

        if self.open_issues:
            issues = '\n'.join(f'- {i}' for i in self.open_issues)
            parts.append(f"## Open Issues\n{issues}")

        if self.next_priorities:
            priorities = '\n'.join(f'{i+1}. {p}' for i, p in enumerate(self.next_priorities))
            parts.append(f"## Next Priorities\n{priorities}")

        parts.append(f"\n**Quality:** {self.quality_score:.1%} | **Context Quality:** {self.context_quality_score:.1%}")

        return '\n\n'.join(parts)


# ══════════════════════════════════════════════════════════
# LOOP RESULT
# ══════════════════════════════════════════════════════════

@dataclass
class LoopResult:
    """Final result of a complete loop run."""
    run_id: str = field(default_factory=lambda: f'run_{uuid.uuid4().hex[:8]}')
    task: str = ''
    strategy: str = ''
    iterations_completed: int = 0
    task_complete: bool = False
    total_time_ms: float = 0.0
    total_tokens: int = 0

    # Per-iteration data
    context_packs: List[ContextPack] = field(default_factory=list)
    work_results: List[WorkResult] = field(default_factory=list)
    handoffs: List[Handoff] = field(default_factory=list)

    # Final state
    final_output: str = ''
    final_quality_score: float = 0.0

    def summary(self) -> str:
        """Human-readable summary."""
        status = "✅ COMPLETE" if self.task_complete else "🔄 INCOMPLETE"
        return (
            f"═══ Loop Run {self.run_id} ═══\n"
            f"Task: {self.task[:80]}\n"
            f"Strategy: {self.strategy}\n"
            f"Status: {status}\n"
            f"Iterations: {self.iterations_completed}\n"
            f"Total Time: {self.total_time_ms/1000:.1f}s\n"
            f"Total Tokens: {self.total_tokens:,}\n"
            f"Quality: {self.final_quality_score:.1%}\n"
        )
