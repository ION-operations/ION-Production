"""
AIM-OS AI Engine — 3-Phase Agent Loop Diagnostics

Comprehensive metrics collection, comparison, and reporting
for measuring the effectiveness of different loop strategies.
"""

import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger('ai_engine.agent_loop.diagnostics')


@dataclass
class PhaseMetrics:
    """Metrics for a single phase execution."""
    phase: str              # 'context', 'worker', 'closeout'
    iteration: int
    run_id: str = ''

    # Performance
    latency_ms: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    model_used: str = ''

    # Quality (assessed by closeout agent)
    success: bool = True
    output_quality: float = 0.0    # 0-1
    context_quality: float = 0.0   # 0-1, how useful was the context?

    # Errors
    error: str = ''
    retries: int = 0

    timestamp: float = field(default_factory=time.time)


class DiagnosticsCollector:
    """Collects, stores, and compares loop execution metrics.

    Usage:
        dc = DiagnosticsCollector(run_id='run_abc123')
        dc.record_phase(PhaseMetrics(phase='context', iteration=1, ...))
        dc.record_phase(PhaseMetrics(phase='worker', iteration=1, ...))
        dc.record_phase(PhaseMetrics(phase='closeout', iteration=1, ...))
        print(dc.get_run_summary())
    """

    def __init__(self, run_id: str = ''):
        self.run_id = run_id
        self._phases: List[PhaseMetrics] = []
        self._start_time = time.time()
        self._events: List[Dict[str, Any]] = []

    def record_phase(self, metrics: PhaseMetrics) -> None:
        """Record metrics for a completed phase."""
        metrics.run_id = self.run_id
        self._phases.append(metrics)
        logger.info(
            f'[Diagnostics] {metrics.phase} iter={metrics.iteration} '
            f'{metrics.latency_ms:.0f}ms tokens={metrics.tokens_in + metrics.tokens_out} '
            f'quality={metrics.output_quality:.1%}'
        )

    def record_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Record a custom event (handoff, error, strategy switch, etc)."""
        self._events.append({
            'type': event_type,
            'timestamp': time.time(),
            'data': data or {},
        })

    def get_iteration_report(self, iteration: int) -> Dict[str, Any]:
        """Get detailed metrics for a specific iteration."""
        phases = [p for p in self._phases if p.iteration == iteration]
        if not phases:
            return {'iteration': iteration, 'status': 'not found'}

        total_latency = sum(p.latency_ms for p in phases)
        total_tokens = sum(p.tokens_in + p.tokens_out for p in phases)

        return {
            'iteration': iteration,
            'phases': {p.phase: asdict(p) for p in phases},
            'total_latency_ms': total_latency,
            'total_tokens': total_tokens,
            'all_succeeded': all(p.success for p in phases),
            'avg_quality': sum(p.output_quality for p in phases) / len(phases) if phases else 0,
        }

    def get_run_summary(self) -> Dict[str, Any]:
        """Get summary for the entire run."""
        if not self._phases:
            return {'status': 'no data'}

        total_time = (time.time() - self._start_time) * 1000
        iterations = max(p.iteration for p in self._phases) if self._phases else 0

        # Aggregate by phase type
        phase_aggregates = {}
        for phase_type in ['context', 'worker', 'closeout']:
            phase_data = [p for p in self._phases if p.phase == phase_type]
            if phase_data:
                phase_aggregates[phase_type] = {
                    'count': len(phase_data),
                    'avg_latency_ms': sum(p.latency_ms for p in phase_data) / len(phase_data),
                    'total_tokens': sum(p.tokens_in + p.tokens_out for p in phase_data),
                    'avg_quality': sum(p.output_quality for p in phase_data) / len(phase_data),
                    'success_rate': sum(1 for p in phase_data if p.success) / len(phase_data),
                    'errors': [p.error for p in phase_data if p.error],
                }

        return {
            'run_id': self.run_id,
            'iterations': iterations,
            'total_time_ms': total_time,
            'total_tokens': sum(p.tokens_in + p.tokens_out for p in self._phases),
            'total_phases': len(self._phases),
            'all_succeeded': all(p.success for p in self._phases),
            'phase_aggregates': phase_aggregates,
            'events': len(self._events),
        }

    def get_phase_timeline(self) -> List[Dict[str, Any]]:
        """Get chronological timeline of all phase executions."""
        return [
            {
                'phase': p.phase,
                'iteration': p.iteration,
                'latency_ms': p.latency_ms,
                'tokens': p.tokens_in + p.tokens_out,
                'quality': p.output_quality,
                'success': p.success,
                'model': p.model_used,
            }
            for p in sorted(self._phases, key=lambda x: x.timestamp)
        ]

    def format_report(self) -> str:
        """Format a human-readable diagnostics report."""
        summary = self.get_run_summary()
        if summary.get('status') == 'no data':
            return "No diagnostics data collected."

        lines = [
            f"═══ Diagnostics Report: {self.run_id} ═══",
            f"Iterations: {summary['iterations']}",
            f"Total Time: {summary['total_time_ms']/1000:.1f}s",
            f"Total Tokens: {summary['total_tokens']:,}",
            f"All Succeeded: {'✅' if summary['all_succeeded'] else '❌'}",
            "",
            "── Per-Phase Averages ──",
        ]

        for phase, agg in summary.get('phase_aggregates', {}).items():
            lines.append(
                f"  {phase:>10}: {agg['avg_latency_ms']:.0f}ms avg | "
                f"{agg['total_tokens']:,} tokens | "
                f"{agg['avg_quality']:.0%} quality | "
                f"{agg['success_rate']:.0%} success"
            )

        lines.append("")
        lines.append("── Phase Timeline ──")
        for entry in self.get_phase_timeline():
            status = '✅' if entry['success'] else '❌'
            lines.append(
                f"  {status} iter {entry['iteration']} {entry['phase']:>10} "
                f"{entry['latency_ms']:.0f}ms {entry['tokens']:,}tok "
                f"q={entry['quality']:.0%}"
            )

        return '\n'.join(lines)

    def save_to_file(self, path: str) -> None:
        """Save diagnostics to a JSON file."""
        data = {
            'summary': self.get_run_summary(),
            'timeline': self.get_phase_timeline(),
            'events': self._events,
            'raw_phases': [asdict(p) for p in self._phases],
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f'Diagnostics saved to {path}')

    @staticmethod
    def compare_runs(runs: List['DiagnosticsCollector']) -> str:
        """Compare multiple runs side-by-side."""
        if not runs:
            return "No runs to compare."

        lines = ["═══ Strategy Comparison ═══", ""]
        header = f"{'Run ID':>20} | {'Strategy':>14} | {'Iters':>5} | {'Time':>8} | {'Tokens':>8} | {'Quality':>8}"
        lines.append(header)
        lines.append("─" * len(header))

        for run in runs:
            s = run.get_run_summary()
            phases = s.get('phase_aggregates', {})
            avg_q = sum(
                p.get('avg_quality', 0) for p in phases.values()
            ) / max(len(phases), 1)

            lines.append(
                f"{run.run_id:>20} | "
                f"{'?':>14} | "
                f"{s.get('iterations', 0):>5} | "
                f"{s.get('total_time_ms', 0)/1000:>7.1f}s | "
                f"{s.get('total_tokens', 0):>8,} | "
                f"{avg_q:>7.0%}"
            )

        return '\n'.join(lines)
