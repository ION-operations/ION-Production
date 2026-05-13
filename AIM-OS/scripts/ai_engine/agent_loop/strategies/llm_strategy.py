"""
Strategy: LLM Research (Default)

Uses the Gemini CLI to have an LLM agent analyze the task and
build context by reasoning about what the worker needs. This is
the original Phase 1 approach — the Context Researcher agent.

The LLM reads MCP state, chat history, and project context,
then synthesizes a structured ContextPack.
"""

import time
import logging
from typing import Optional

from . import ContextStrategy, register_strategy

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

logger = logging.getLogger('ai_engine.agent_loop.strategies.llm')


@register_strategy
class LLMResearchStrategy(ContextStrategy):
    """LLM-based context research using Gemini CLI.

    The original 3-phase loop approach — an LLM agent reasons
    about the task and builds context through analysis.
    """

    name = 'llm_research'
    description = 'LLM analyzes task + calls MCP to build context (original default)'

    def __init__(self, workspace_root: str = '', **kwargs):
        super().__init__(workspace_root, **kwargs)
        self._provider = None

    def _get_provider(self):
        if self._provider is None:
            try:
                from providers.gemini_cli_provider import GeminiCLIProvider
            except ImportError:
                from scripts.ai_engine.providers.gemini_cli_provider import GeminiCLIProvider
            self._provider = GeminiCLIProvider(
                working_directory=self.workspace_root,
            )
        return self._provider

    def build_context(
        self,
        task: str,
        handoff: Optional[Handoff] = None,
        **kwargs,
    ) -> ContextPack:
        """Build context by having an LLM research the task."""
        from phases import run_context_researcher

        start = time.time()
        mcp_access = kwargs.get('mcp_access', True)
        timeout = kwargs.get('timeout', 60)

        pack = run_context_researcher(
            provider=self._get_provider(),
            task=task,
            mcp_access=mcp_access,
            timeout=timeout,
            previous_handoff=handoff,
        )

        self._metrics = {
            'build_time_ms': (time.time() - start) * 1000,
            'tokens_used': pack.tokens_used,
            'method': 'llm_research',
        }

        return pack
