"""
Strategy: ContextPackBuilder (4-Stage Pipeline)

Uses the existing AIM-OS ContextPackBuilder which has the deepest
integration with AIM-OS context systems:
    1. Evidence: gather raw context from all sources (files, editor, git)
    2. Retrieval: semantic search via HHNI + CMC memory retrieval
    3. Budgeting: select minimal slices within token budget
    4. Pack: assemble final ContextPack

This is Sev's original unified context strategy built into the
AI Engine's context/ module.
"""

import time
import logging
from typing import Optional

from . import ContextStrategy, register_strategy

import os
import sys

_AGENT_LOOP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AI_ENGINE_DIR = os.path.dirname(_AGENT_LOOP_DIR)
_SCRIPTS_DIR = os.path.dirname(_AI_ENGINE_DIR)
_AIMOS_ROOT = os.path.dirname(_SCRIPTS_DIR)

for p in [_AIMOS_ROOT, _AI_ENGINE_DIR, _AGENT_LOOP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from ..models import ContextPack as LoopContextPack, Handoff
except ImportError:
    from models import ContextPack as LoopContextPack, Handoff

logger = logging.getLogger('ai_engine.agent_loop.strategies.pack_builder')


@register_strategy
class PackBuilderStrategy(ContextStrategy):
    """ContextPackBuilder-based strategy using the 4-stage pipeline.

    Wraps the existing ContextPackBuilder (context/context_pack.py)
    as a Phase 1 strategy and converts its output to the agent loop's
    ContextPack format.
    """

    name = 'pack_builder'
    description = 'ContextPackBuilder 4-stage pipeline (Evidence→Retrieval→Budget→Pack)'

    def __init__(self, workspace_root: str = '', **kwargs):
        super().__init__(workspace_root, **kwargs)
        self._builder = None
        self._use_daemon_rag = kwargs.get('use_daemon_rag', True)

    def _get_builder(self):
        """Lazy-load the ContextPackBuilder."""
        if self._builder is None:
            try:
                from context.context_pack import ContextPackBuilder
            except ImportError:
                try:
                    from ai_engine.context.context_pack import ContextPackBuilder
                except ImportError:
                    from scripts.ai_engine.context.context_pack import ContextPackBuilder

            self._builder = ContextPackBuilder(
                workspace_root=self.workspace_root,
                use_daemon_rag=self._use_daemon_rag,
            )
            logger.info('[PackBuilderStrategy] ContextPackBuilder loaded')
        return self._builder

    def build_context(
        self,
        task: str,
        handoff: Optional[Handoff] = None,
        **kwargs,
    ) -> LoopContextPack:
        """Build context using the 4-stage ContextPackBuilder pipeline."""
        start = time.time()
        builder = self._get_builder()

        # Enrich task with handoff context if available
        enriched_task = task
        if handoff:
            enriched_task = (
                f"{task}\n\n"
                f"Previous iteration context:\n"
                f"- Progress: {handoff.cumulative_progress}\n"
                f"- Open issues: {', '.join(handoff.open_issues)}\n"
                f"- Priorities: {', '.join(handoff.next_priorities)}"
            )

        # Build using the 4-stage pipeline
        active_file = kwargs.get('active_file', '')
        include_files = kwargs.get('include_files', None)
        max_tokens = kwargs.get('max_tokens', 0)

        engine_pack = builder.build_for_task(
            task=enriched_task,
            active_file=active_file,
            include_files=include_files,
            max_tokens=max_tokens,
        )

        # Convert ContextPackBuilder output → agent loop ContextPack
        loop_pack = self._convert_pack(engine_pack, task, handoff)

        elapsed = (time.time() - start) * 1000
        loop_pack.build_time_ms = elapsed

        self._metrics = {
            'build_time_ms': elapsed,
            'tokens_used': loop_pack.tokens_used,
            'evidence_count': len(engine_pack.evidence),
            'evidence_types': list(set(e.type for e in engine_pack.evidence)),
            'token_utilization': engine_pack.token_utilization,
            'profile_source': engine_pack.profile.classification_source if engine_pack.profile else 'none',
            'method': 'pack_builder',
        }

        logger.info(
            f'[PackBuilderStrategy] Built context: {len(engine_pack.evidence)} items, '
            f'{engine_pack.total_tokens} tokens, {elapsed:.0f}ms'
        )

        return loop_pack

    def _convert_pack(self, engine_pack, task: str, handoff: Optional[Handoff]) -> LoopContextPack:
        """Convert ContextPackBuilder output to agent loop ContextPack."""
        # Extract different evidence types into structured fields
        project_state_parts = []
        files_to_examine = []
        research_notes_parts = []
        instructions_parts = []

        for item in engine_pack.evidence:
            etype = item.type if isinstance(item.type, str) else item.type.value

            if etype in ('file_content', 'file_summary'):
                files_to_examine.append(item.source)
                project_state_parts.append(f"[{etype}] {item.source}:\n{item.content[:1000]}")
            elif etype == 'cmc_memory':
                research_notes_parts.append(f"[Memory] {item.content}")
            elif etype == 'search_result':
                research_notes_parts.append(f"[Search] {item.content}")
            elif etype == 'git_diff':
                project_state_parts.append(f"[Recent Changes]\n{item.content}")
            elif etype == 'daemon_rag_context':
                instructions_parts.append(f"[Task Analysis]\n{item.content}")
            elif etype == 'editor_state':
                project_state_parts.append(f"[Editor State]\n{item.content}")
            else:
                research_notes_parts.append(f"[{etype}] {item.content[:500]}")

        # Build profile-based instructions
        if engine_pack.profile:
            p = engine_pack.profile
            instructions_parts.insert(0,
                f"Task type: {p.task_type} | Complexity: {p.complexity} | "
                f"Intent: {p.intent} | Keywords: {', '.join(p.keywords)}"
            )

        # Assemble the loop ContextPack
        relevant_history = ''
        if handoff:
            relevant_history = handoff.to_prompt()

        return LoopContextPack(
            task_summary=task,
            relevant_history=relevant_history,
            project_state='\n\n'.join(project_state_parts) if project_state_parts else '',
            instructions='\n'.join(instructions_parts) if instructions_parts else '',
            files_to_examine=files_to_examine,
            research_notes='\n'.join(research_notes_parts) if research_notes_parts else '',
            tokens_used=engine_pack.total_tokens,
        )

    def status(self) -> dict:
        base = super().status()
        if self._builder:
            base['builder_status'] = self._builder.status()
        return base
