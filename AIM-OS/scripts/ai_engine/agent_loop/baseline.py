"""
AIM-OS AI Engine — Baseline Single-Agent Runner

Traditional single-agent approach for A/B comparison against
the 3-phase agent loop. Sends one prompt to one agent — no
context pre-building, no closeout, no handoffs.

This is the "control group" for measuring the 3-phase loop's value.
"""

import json
import re
import time
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

logger = logging.getLogger('ai_engine.agent_loop.baseline')

# Path setup
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_AI_ENGINE_DIR = os.path.dirname(_THIS_DIR)
_AIMOS_ROOT = os.path.dirname(os.path.dirname(_AI_ENGINE_DIR))
for p in [_AIMOS_ROOT, _AI_ENGINE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from .models import LoopResult
    from .diagnostics import PhaseMetrics, DiagnosticsCollector
except ImportError:
    from models import LoopResult
    from diagnostics import PhaseMetrics, DiagnosticsCollector


BASELINE_SYSTEM = """You are an AI agent working on the AIM-OS project.
Execute the given task thoroughly. Provide your analysis and results.

After completing the work, assess your own output quality:
- Rate your confidence from 0.0 to 1.0
- List any issues you encountered
- Suggest next steps if applicable

OUTPUT FORMAT — You MUST output valid JSON:
```json
{
    "success": true,
    "output": "Your main work output",
    "quality_self_score": 0.8,
    "decisions_made": ["decision1"],
    "issues_encountered": ["issue1"],
    "suggested_next_steps": ["step1"]
}
```
"""


@dataclass
class BaselineResult:
    """Result from a single-agent baseline run."""
    run_id: str = ''
    task: str = ''
    success: bool = False
    output: str = ''
    quality_score: float = 0.0
    latency_ms: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    model_used: str = ''
    decisions_made: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    raw_response: str = ''

    def summary(self) -> str:
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return (
            f"═══ Baseline Run ═══\n"
            f"Task: {self.task[:80]}\n"
            f"Status: {status}\n"
            f"Time: {self.latency_ms/1000:.1f}s\n"
            f"Quality (self-assessed): {self.quality_score:.0%}\n"
            f"Tokens: {self.tokens_in + self.tokens_out:,}\n"
        )


def _parse_json(text: str) -> dict:
    """Extract JSON from LLM response."""
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    start, end = text.find('{'), text.rfind('}')
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    return {'output': text, '_parse_failed': True}


def run_baseline(
    task: str,
    mcp_access: bool = True,
    model: str = 'auto',
    timeout: int = 120,
    workspace: str = '',
) -> tuple[BaselineResult, DiagnosticsCollector]:
    """Run a single-agent baseline for comparison.

    Args:
        task: Task to execute
        mcp_access: Whether agent gets MCP tools
        model: Model to use
        timeout: Timeout in seconds
        workspace: Workspace root

    Returns:
        (BaselineResult, DiagnosticsCollector)
    """
    import uuid
    run_id = f'baseline_{uuid.uuid4().hex[:8]}'

    workspace = workspace or _AIMOS_ROOT

    # Load provider
    try:
        from providers.gemini_cli_provider import GeminiCLIProvider
    except ImportError:
        from scripts.ai_engine.providers.gemini_cli_provider import GeminiCLIProvider

    provider = GeminiCLIProvider(
        working_directory=workspace,
        allowed_mcp_servers=['ai-engine'] if mcp_access else [],
    )

    diagnostics = DiagnosticsCollector(run_id=run_id)
    diagnostics.record_event('baseline_start', {'task': task, 'mcp': mcp_access})

    start = time.time()
    logger.info(f'═══ Baseline Run {run_id} ═══')
    logger.info(f'Task: {task[:80]}')
    logger.info(f'MCP: {"yes" if mcp_access else "no"}')

    mcp_servers = ['ai-engine'] if mcp_access else None
    response = provider.complete(
        prompt=task,
        system=BASELINE_SYSTEM,
        model=model if model != 'auto' else '',
        timeout=timeout,
        mcp_servers=mcp_servers,
    )

    elapsed = (time.time() - start) * 1000

    result = BaselineResult(
        run_id=run_id,
        task=task,
        latency_ms=elapsed,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        model_used=response.model or model,
        raw_response=response.content,
    )

    if response.success:
        data = _parse_json(response.content)
        result.success = data.get('success', True)
        result.output = data.get('output', response.content)
        result.quality_score = float(data.get('quality_self_score', 0.5))
        result.decisions_made = data.get('decisions_made', [])
        result.issues = data.get('issues_encountered', [])
        result.next_steps = data.get('suggested_next_steps', [])
    else:
        result.success = False
        result.output = f"Failed: {response.error}"

    metrics = PhaseMetrics(
        phase='baseline',
        iteration=1,
        run_id=run_id,
        latency_ms=elapsed,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        model_used=result.model_used,
        success=result.success,
        output_quality=result.quality_score,
    )
    diagnostics.record_phase(metrics)
    diagnostics.record_event('baseline_complete', {
        'success': result.success,
        'quality': result.quality_score,
        'latency_ms': elapsed,
    })

    logger.info(f'Baseline done: {elapsed:.0f}ms quality={result.quality_score:.0%}')
    return result, diagnostics


def compare_baseline_vs_loop(
    task: str,
    loop_result: 'LoopResult',
    baseline_result: BaselineResult,
) -> str:
    """Format a comparison between baseline and 3-phase loop results."""
    lines = [
        "═══ Baseline vs 3-Phase Loop ═══",
        f"Task: {task[:80]}",
        "",
        f"{'Metric':<25} {'Baseline':>15} {'3-Phase Loop':>15} {'Winner':>10}",
        "─" * 65,
    ]

    # Time
    bl_time = baseline_result.latency_ms / 1000
    loop_time = loop_result.total_time_ms / 1000
    time_winner = '⬅ Base' if bl_time < loop_time else '➡ Loop'
    lines.append(f"{'Total Time':<25} {bl_time:>14.1f}s {loop_time:>14.1f}s {time_winner:>10}")

    # Quality
    bl_q = baseline_result.quality_score
    loop_q = loop_result.final_quality_score
    q_winner = '⬅ Base' if bl_q > loop_q else '➡ Loop' if loop_q > bl_q else 'TIE'
    lines.append(f"{'Quality Score':<25} {bl_q:>14.0%} {loop_q:>14.0%} {q_winner:>10}")

    # Tokens
    bl_tok = baseline_result.tokens_in + baseline_result.tokens_out
    loop_tok = loop_result.total_tokens
    tok_winner = '⬅ Base' if bl_tok < loop_tok else '➡ Loop'
    lines.append(f"{'Total Tokens':<25} {bl_tok:>15,} {loop_tok:>15,} {tok_winner:>10}")

    # Iterations
    lines.append(f"{'Iterations':<25} {'1':>15} {loop_result.iterations_completed:>15}")

    # Completion
    bl_complete = '✅' if baseline_result.success else '❌'
    loop_complete = '✅' if loop_result.task_complete else '❌'
    lines.append(f"{'Task Complete':<25} {bl_complete:>15} {loop_complete:>15}")

    lines.append("")
    lines.append("── Analysis ──")
    speedup = bl_time / loop_time if loop_time > 0 else 0
    quality_delta = loop_q - bl_q
    if quality_delta > 0:
        lines.append(f"  Quality improvement: +{quality_delta:.0%} (3-phase loop is better)")
    elif quality_delta < 0:
        lines.append(f"  Quality decrease: {quality_delta:.0%} (baseline was better)")
    else:
        lines.append(f"  Quality: tied")

    if speedup > 1:
        lines.append(f"  Speed: baseline was {speedup:.1f}x faster")
    else:
        lines.append(f"  Speed: loop was {1/speedup:.1f}x faster")

    return '\n'.join(lines)
