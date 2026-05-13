"""
AIM-OS AI Engine — 3-Phase Agent Loop Orchestrator

The main loop controller that manages the 3-phase cycle:
    Phase 1: Context Researcher → ContextPack
    Phase 2: Worker → WorkResult
    Phase 3: Closeout → Handoff → (recurse)

Supports dynamic strategy configuration and full diagnostics.
"""

import os
import sys
import time
import logging
from typing import Optional

try:
    from .models import (
        LoopConfig, ContextPack, WorkResult, Handoff,
        LoopResult, StrategyType,
    )
    from .diagnostics import DiagnosticsCollector
    from .phases import run_context_researcher, run_worker, run_closeout
except ImportError:
    from models import (
        LoopConfig, ContextPack, WorkResult, Handoff,
        LoopResult, StrategyType,
    )
    from diagnostics import DiagnosticsCollector
    from phases import run_context_researcher, run_worker, run_closeout

logger = logging.getLogger('ai_engine.agent_loop.orchestrator')


class LoopOrchestrator:
    """Runs the 3-phase agent loop with full diagnostics.

    Usage:
        config = LoopConfig.from_strategy('standard')
        orchestrator = LoopOrchestrator(config)
        result = orchestrator.run("Audit the registry module", max_iterations=3)
        print(result.summary())
        print(orchestrator.diagnostics.format_report())
    """

    def __init__(self, config: Optional[LoopConfig] = None):
        self.config = config or LoopConfig()
        self.diagnostics = DiagnosticsCollector()
        self._provider = None
        self._iteration = 0

    @property
    def provider(self):
        """Lazy-load GeminiCLIProvider."""
        if self._provider is None:
            # Add engine paths
            aim_root = self.config.workspace_root or os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if aim_root not in sys.path:
                sys.path.insert(0, aim_root)

            try:
                from scripts.ai_engine.providers.gemini_cli_provider import GeminiCLIProvider
            except ImportError:
                try:
                    from ai_engine.providers.gemini_cli_provider import GeminiCLIProvider
                except ImportError:
                    from providers.gemini_cli_provider import GeminiCLIProvider

            self._provider = GeminiCLIProvider(
                working_directory=aim_root,
                allowed_mcp_servers=['ai-engine'],
            )
            logger.info(f'GeminiCLIProvider initialized (workspace: {aim_root})')

        return self._provider

    def run(
        self,
        task: str,
        max_iterations: Optional[int] = None,
    ) -> LoopResult:
        """Execute the full 3-phase loop.

        Args:
            task: The task to execute
            max_iterations: Override config's max_iterations

        Returns:
            LoopResult with all data and diagnostics
        """
        iterations = max_iterations or self.config.max_iterations
        run_start = time.time()

        # Initialize result
        result = LoopResult(
            task=task,
            strategy=self.config.strategy,
        )
        self.diagnostics = DiagnosticsCollector(run_id=result.run_id)
        self.diagnostics.record_event('loop_start', {
            'task': task,
            'strategy': self.config.strategy,
            'max_iterations': iterations,
        })

        logger.info(f'═══ Starting 3-Phase Loop ═══')
        logger.info(f'Task: {task[:80]}')
        logger.info(f'Strategy: {self.config.strategy}')
        logger.info(f'Max iterations: {iterations}')

        handoff = Handoff(task=task)

        for i in range(1, iterations + 1):
            self._iteration = i
            logger.info(f'\n──── Iteration {i}/{iterations} ────')
            self.diagnostics.record_event('iteration_start', {'iteration': i})

            try:
                # ── Phase 1: Context Research ──
                context_pack, ctx_metrics = run_context_researcher(
                    provider=self.provider,
                    task=task,
                    handoff=handoff if i > 1 else None,
                    config=self.config,
                    iteration=i,
                )
                self.diagnostics.record_phase(ctx_metrics)
                result.context_packs.append(context_pack)

                # ── Phase 2: Worker Execution ──
                work_result, work_metrics = run_worker(
                    provider=self.provider,
                    context_pack=context_pack,
                    config=self.config,
                    iteration=i,
                )
                self.diagnostics.record_phase(work_metrics)
                result.work_results.append(work_result)

                # ── Phase 3: Closeout & Handoff ──
                handoff, close_metrics = run_closeout(
                    provider=self.provider,
                    task=task,
                    context_pack=context_pack,
                    work_result=work_result,
                    previous_handoff=handoff if i > 1 else None,
                    config=self.config,
                    iteration=i,
                )
                self.diagnostics.record_phase(close_metrics)
                result.handoffs.append(handoff)

                # Update result quality from closeout assessment
                result.final_quality_score = handoff.quality_score

                self.diagnostics.record_event('iteration_complete', {
                    'iteration': i,
                    'quality': handoff.quality_score,
                    'context_quality': handoff.context_quality_score,
                    'task_complete': handoff.task_complete,
                })

                logger.info(
                    f'Iteration {i} complete — '
                    f'quality={handoff.quality_score:.0%} '
                    f'complete={handoff.task_complete}'
                )

                if handoff.task_complete:
                    logger.info(f'✅ Task marked complete at iteration {i}')
                    break

            except Exception as e:
                logger.error(f'Iteration {i} failed: {e}')
                self.diagnostics.record_event('iteration_error', {
                    'iteration': i,
                    'error': str(e),
                })
                # Create a failure handoff so the loop can continue
                handoff = Handoff(
                    task=task,
                    iteration_summary=f"Iteration {i} failed: {e}",
                    open_issues=[str(e)],
                    iteration=i,
                )
                result.handoffs.append(handoff)

        # Finalize result
        result.iterations_completed = self._iteration
        result.task_complete = handoff.task_complete
        result.total_time_ms = (time.time() - run_start) * 1000
        result.total_tokens = sum(
            p.tokens_in + p.tokens_out
            for p in self.diagnostics._phases
        )
        if result.work_results:
            result.final_output = result.work_results[-1].output

        self.diagnostics.record_event('loop_complete', {
            'iterations': result.iterations_completed,
            'total_time_ms': result.total_time_ms,
            'task_complete': result.task_complete,
        })

        logger.info(f'\n═══ Loop Complete ═══')
        logger.info(result.summary())

        return result

    def run_comparison(
        self,
        task: str,
        strategies: list[str] = None,
        max_iterations: int = 2,
    ) -> str:
        """Run the same task with multiple strategies and compare results.

        Args:
            task: Task to test
            strategies: List of strategy names to compare
            max_iterations: Iterations per strategy

        Returns:
            Formatted comparison report
        """
        strategies = strategies or ['standard', 'minimal', 'deep_research']
        collectors = []
        results = []

        for strategy in strategies:
            logger.info(f'\n═══ Testing Strategy: {strategy} ═══')
            self.config = LoopConfig.from_strategy(strategy)

            result = self.run(task, max_iterations=max_iterations)
            results.append(result)
            collectors.append(self.diagnostics)

        # Build comparison
        comparison = DiagnosticsCollector.compare_runs(collectors)

        # Add per-strategy details
        lines = [comparison, ""]
        for result, strategy in zip(results, strategies):
            lines.append(f"\n── {strategy} ──")
            lines.append(f"  Completed: {'✅' if result.task_complete else '❌'}")
            lines.append(f"  Iterations: {result.iterations_completed}")
            lines.append(f"  Time: {result.total_time_ms/1000:.1f}s")
            lines.append(f"  Tokens: {result.total_tokens:,}")
            lines.append(f"  Quality: {result.final_quality_score:.0%}")

        return '\n'.join(lines)
