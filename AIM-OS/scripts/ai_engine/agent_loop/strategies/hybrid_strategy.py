"""
Strategy: Hybrid (Multi-Source Fusion)

Runs multiple context strategies in parallel, deduplicates results,
and assembles a fused ContextPack with the best context from all sources.

This is the most comprehensive strategy — it combines LLM research,
ContextPackBuilder pipeline, and HHNI retrieval into a single pack.
"""

import time
import logging
from typing import Optional, List, Dict, Any

from . import ContextStrategy, register_strategy, get_strategy

import os
import sys

_AGENT_LOOP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AI_ENGINE_DIR = os.path.dirname(_AGENT_LOOP_DIR)

for p in [_AI_ENGINE_DIR, _AGENT_LOOP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from ..models import ContextPack, Handoff
except ImportError:
    from models import ContextPack, Handoff

logger = logging.getLogger('ai_engine.agent_loop.strategies.hybrid')


@register_strategy
class HybridStrategy(ContextStrategy):
    """Multi-source fusion strategy.

    Runs multiple sub-strategies, merges their results, and 
    deduplicates to produce the richest possible context. Each
    sub-strategy contributes different types of context:
    - pack_builder: files, git diffs, DaemonRAG analysis
    - hhni_direct: semantic retrieval, CMC memories
    """

    name = 'hybrid'
    description = 'Multi-source fusion: PackBuilder + HHNI + deduplication'

    def __init__(self, workspace_root: str = '', **kwargs):
        super().__init__(workspace_root, **kwargs)
        self._sub_strategies = kwargs.get('sub_strategies', ['pack_builder', 'hhni_direct'])
        self._loaded_strategies: Dict[str, ContextStrategy] = {}

    def _load_sub_strategies(self):
        """Lazy-load sub-strategies."""
        for name in self._sub_strategies:
            if name not in self._loaded_strategies:
                try:
                    self._loaded_strategies[name] = get_strategy(
                        name, workspace_root=self.workspace_root,
                    )
                    logger.info(f'[Hybrid] Loaded sub-strategy: {name}')
                except Exception as e:
                    logger.warning(f'[Hybrid] Failed to load {name}: {e}')

    def build_context(
        self,
        task: str,
        handoff: Optional[Handoff] = None,
        **kwargs,
    ) -> ContextPack:
        """Build context by fusing results from multiple strategies."""
        start = time.time()
        self._load_sub_strategies()

        # Run each sub-strategy
        sub_packs: List[tuple] = []  # (name, ContextPack)
        sub_metrics: Dict[str, Any] = {}

        for name, strategy in self._loaded_strategies.items():
            try:
                t0 = time.time()
                pack = strategy.build_context(task, handoff, **kwargs)
                elapsed = (time.time() - t0) * 1000
                sub_packs.append((name, pack))
                sub_metrics[name] = {
                    'time_ms': elapsed,
                    'tokens': pack.tokens_used,
                    'success': True,
                }
                logger.info(f'[Hybrid] {name}: {elapsed:.0f}ms, {pack.tokens_used} tokens')
            except Exception as e:
                logger.warning(f'[Hybrid] {name} failed: {e}')
                sub_metrics[name] = {'success': False, 'error': str(e)}

        # Fuse results
        fused = self._fuse_packs(task, sub_packs, handoff)

        total_elapsed = (time.time() - start) * 1000
        fused.build_time_ms = total_elapsed

        self._metrics = {
            'build_time_ms': total_elapsed,
            'tokens_used': fused.tokens_used,
            'sub_strategies': sub_metrics,
            'sources_fused': len(sub_packs),
            'method': 'hybrid',
        }

        logger.info(
            f'[HybridStrategy] Fused {len(sub_packs)} sources, '
            f'{fused.tokens_used} tokens, {total_elapsed:.0f}ms'
        )

        return fused

    def _fuse_packs(
        self,
        task: str,
        sub_packs: List[tuple],
        handoff: Optional[Handoff],
    ) -> ContextPack:
        """Merge multiple ContextPacks with deduplication."""
        # Collect all fields with deduplication
        all_project_state = []
        all_files = []
        all_research = []
        all_instructions = []
        seen_files = set()
        seen_content_hashes = set()

        for name, pack in sub_packs:
            # Project state
            if pack.project_state:
                h = hash(pack.project_state[:100])
                if h not in seen_content_hashes:
                    seen_content_hashes.add(h)
                    all_project_state.append(f"[{name}]\n{pack.project_state}")

            # Files (deduplicate)
            for f in pack.files_to_examine:
                if f not in seen_files:
                    seen_files.add(f)
                    all_files.append(f)

            # Research notes
            if pack.research_notes:
                h = hash(pack.research_notes[:100])
                if h not in seen_content_hashes:
                    seen_content_hashes.add(h)
                    all_research.append(f"[{name}] {pack.research_notes}")

            # Instructions
            if pack.instructions:
                all_instructions.append(f"[{name}] {pack.instructions}")

        # Merge relevant history (prefer most detailed)
        relevant_history = ''
        if handoff:
            relevant_history = handoff.to_prompt()
        else:
            for _, pack in sub_packs:
                if pack.relevant_history and len(pack.relevant_history) > len(relevant_history):
                    relevant_history = pack.relevant_history

        total_tokens = sum(p.tokens_used for _, p in sub_packs)

        return ContextPack(
            task_summary=task,
            relevant_history=relevant_history,
            project_state='\n\n'.join(all_project_state),
            instructions='\n'.join(all_instructions) if all_instructions else f'Execute: {task}',
            files_to_examine=all_files[:20],
            research_notes='\n\n'.join(all_research),
            tokens_used=total_tokens,
        )

    def status(self) -> dict:
        base = super().status()
        base['sub_strategies'] = list(self._loaded_strategies.keys())
        base['configured'] = self._sub_strategies
        return base
