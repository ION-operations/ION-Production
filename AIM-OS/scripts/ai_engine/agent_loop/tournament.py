"""
AIM-OS Context Lab — Tournament Runner

Head-to-head strategy comparison system. Runs multiple strategies
against the same task(s) and produces ranked results with detailed
diagnostics and quality scores.

Features:
    - Single task tournament (quick A/B test)
    - Task suite tournament (statistical significance)
    - Leaderboard tracking across runs
    - Export to JSON for JOC dashboard consumption
"""

import time
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENT_LOOP_DIR = _THIS_DIR

for p in [_AGENT_LOOP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

logger = logging.getLogger('ai_engine.agent_loop.tournament')


@dataclass
class StrategyResult:
    """Result of running a single strategy on a single task."""
    strategy_name: str = ''
    task: str = ''

    # Timing
    build_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # Quality scores
    quality_overall: float = 0.0
    quality_coverage: float = 0.0
    quality_specificity: float = 0.0
    quality_freshness: float = 0.0
    quality_token_efficiency: float = 0.0
    quality_diversity: float = 0.0

    # Context stats
    tokens_used: int = 0
    files_found: int = 0
    sources_used: int = 0

    # Strategy metrics
    strategy_metrics: Dict[str, Any] = field(default_factory=dict)

    # Result
    success: bool = True
    error: str = ''

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class TournamentResult:
    """Results of a full tournament across strategies."""
    tournament_id: str = ''
    tasks: List[str] = field(default_factory=list)
    strategies: List[str] = field(default_factory=list)
    results: List[StrategyResult] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    total_time_ms: float = 0.0

    def leaderboard(self) -> List[Dict[str, Any]]:
        """Compute ranked leaderboard from results."""
        scores: Dict[str, List[float]] = {}
        times: Dict[str, List[float]] = {}

        for r in self.results:
            if r.success:
                scores.setdefault(r.strategy_name, []).append(r.quality_overall)
                times.setdefault(r.strategy_name, []).append(r.build_time_ms)

        board = []
        for name in scores:
            avg_score = sum(scores[name]) / len(scores[name])
            avg_time = sum(times[name]) / len(times[name])
            board.append({
                'rank': 0,  # Set below
                'strategy': name,
                'avg_quality': round(avg_score, 3),
                'avg_time_ms': round(avg_time, 1),
                'tasks_run': len(scores[name]),
                'tasks_passed': sum(1 for s in scores[name] if s > 0.5),
            })

        board.sort(key=lambda x: x['avg_quality'], reverse=True)
        for i, entry in enumerate(board):
            entry['rank'] = i + 1

        return board

    def format_report(self) -> str:
        """Format a human-readable tournament report."""
        lines = [
            '╔══════════════════════════════════════════════╗',
            '║      CONTEXT LAB — TOURNAMENT RESULTS       ║',
            '╚══════════════════════════════════════════════╝',
            '',
        ]

        board = self.leaderboard()
        if board:
            lines.append(f"{'Rank':<6}{'Strategy':<18}{'Quality':>10}{'Time(ms)':>10}{'Tasks':>8}")
            lines.append('─' * 52)
            for entry in board:
                medal = ['🥇', '🥈', '🥉'][entry['rank'] - 1] if entry['rank'] <= 3 else '  '
                lines.append(
                    f"{medal} {entry['rank']:<3}"
                    f"{entry['strategy']:<18}"
                    f"{entry['avg_quality']:>9.1%}"
                    f"{entry['avg_time_ms']:>10.0f}"
                    f"{entry['tasks_run']:>8}"
                )
        else:
            lines.append('  No results to display')

        lines.append('')
        lines.append(f"Total time: {self.total_time_ms / 1000:.1f}s")
        lines.append(f"Tasks: {len(self.tasks)}, Strategies: {len(self.strategies)}")

        # Per-task breakdown
        if len(self.tasks) > 1:
            lines.append('')
            lines.append('── Per-Task Breakdown ──')
            for task in self.tasks:
                task_results = [r for r in self.results if r.task == task and r.success]
                if task_results:
                    lines.append(f'\nTask: "{task[:60]}"')
                    for r in sorted(task_results, key=lambda x: x.quality_overall, reverse=True):
                        lines.append(f'  {r.strategy_name:<16} {r.quality_overall:>8.1%}  ({r.build_time_ms:.0f}ms)')

        return '\n'.join(lines)

    def to_dict(self) -> dict:
        return {
            'tournament_id': self.tournament_id,
            'tasks': self.tasks,
            'strategies': self.strategies,
            'leaderboard': self.leaderboard(),
            'total_time_ms': self.total_time_ms,
            'result_count': len(self.results),
            'results': [r.to_dict() for r in self.results],
        }


def run_tournament(
    tasks: List[str],
    strategy_names: List[str],
    workspace_root: str = '',
    verbose: bool = False,
) -> TournamentResult:
    """Run a full tournament — every strategy against every task.

    Args:
        tasks: List of task descriptions to test
        strategy_names: List of strategy names to compete
        workspace_root: Working directory for strategies
        verbose: Print progress

    Returns:
        TournamentResult with leaderboard and per-task results
    """
    import uuid

    # Lazy imports to avoid circular deps
    from strategies import get_strategy
    from quality import score_context_pack

    tournament = TournamentResult(
        tournament_id=f'tournament_{uuid.uuid4().hex[:8]}',
        tasks=tasks,
        strategies=strategy_names,
    )

    total_runs = len(tasks) * len(strategy_names)
    run_count = 0

    if verbose:
        print(f'\n🏟️  Starting tournament: {len(strategy_names)} strategies × {len(tasks)} tasks = {total_runs} runs\n')

    for task in tasks:
        for strategy_name in strategy_names:
            run_count += 1
            result = StrategyResult(strategy_name=strategy_name, task=task)

            try:
                if verbose:
                    print(f'  [{run_count}/{total_runs}] {strategy_name} × "{task[:40]}..."', end='', flush=True)

                strategy = get_strategy(strategy_name, workspace_root=workspace_root)

                start = time.time()
                pack = strategy.build_context(task)
                elapsed = (time.time() - start) * 1000

                # Score the context quality
                quality = score_context_pack(pack, task)

                # Fill result
                result.build_time_ms = elapsed
                result.total_time_ms = elapsed
                result.quality_overall = quality.overall
                result.quality_coverage = quality.coverage
                result.quality_specificity = quality.specificity
                result.quality_freshness = quality.freshness
                result.quality_token_efficiency = quality.token_efficiency
                result.quality_diversity = quality.diversity
                result.tokens_used = getattr(pack, 'tokens_used', 0) or getattr(pack, 'total_tokens', 0)
                result.files_found = len(getattr(pack, 'files_to_examine', []))
                result.sources_used = len(quality.details.get('active_sources', {}))
                result.strategy_metrics = strategy.metrics
                result.success = True

                if verbose:
                    print(f'  → {quality.overall:.1%} ({elapsed:.0f}ms)')

            except Exception as e:
                result.success = False
                result.error = str(e)
                logger.warning(f'Strategy {strategy_name} failed on task: {e}')
                if verbose:
                    print(f'  → FAILED: {e}')

            tournament.results.append(result)

    tournament.completed_at = time.time()
    tournament.total_time_ms = (tournament.completed_at - tournament.started_at) * 1000

    if verbose:
        print(f'\n{tournament.format_report()}')

    return tournament


def save_tournament(result: TournamentResult, output_dir: str = '') -> str:
    """Save tournament results to a JSON file."""
    if not output_dir:
        output_dir = os.path.join(_THIS_DIR, 'tournament_results')
    os.makedirs(output_dir, exist_ok=True)

    filename = f'{result.tournament_id}.json'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2, default=str)

    logger.info(f'Tournament saved to {filepath}')
    return filepath
