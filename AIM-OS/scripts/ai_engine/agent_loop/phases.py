"""
AIM-OS AI Engine — 3-Phase Agent Loop: Phase Implementations

Each phase is a specialized agent invocation via Gemini CLI:
    Phase 1 (Context Researcher) — Builds optimal context for worker
    Phase 2 (Worker) — Executes with clean, pre-built context
    Phase 3 (Closeout) — Documents, prepares handoff
"""

import json
import time
import logging
from typing import Optional

try:
    from .models import (
        ContextPack, WorkResult, Handoff, LoopConfig, PhaseType,
    )
    from .diagnostics import PhaseMetrics
except ImportError:
    from models import (
        ContextPack, WorkResult, Handoff, LoopConfig, PhaseType,
    )
    from diagnostics import PhaseMetrics

logger = logging.getLogger('ai_engine.agent_loop.phases')


# ══════════════════════════════════════════════════════════
# SYSTEM PROMPTS — The personality of each phase agent
# ══════════════════════════════════════════════════════════

CONTEXT_RESEARCHER_SYSTEM = """You are the CONTEXT RESEARCHER — Phase 1 of the AIM-OS 3-Phase Agent Loop.

YOUR ROLE: Build the perfect context package for the Worker agent who will execute the task.
The Worker will receive ONLY what you produce — they have no access to history, MCP, or project state.

YOUR PROCESS:
1. Analyze the task and any handoff from the previous iteration
2. If MCP tools are available, use them to check messages, recent context, and project state
3. Research relevant files, docs, and past work
4. Synthesize everything into a structured ContextPack

OUTPUT FORMAT — You MUST output valid JSON with this exact structure:
```json
{
    "task_summary": "Clear description of what needs to be done",
    "instructions": "Step-by-step instructions for the Worker agent",
    "relevant_history": "Key context from past work (if any)",
    "project_state": "Current state of relevant systems/files",
    "files_to_examine": ["file1.py", "file2.py"],
    "constraints": ["constraint1", "constraint2"],
    "references": ["relevant doc or link"]
}
```

CRITICAL RULES:
- Be THOROUGH but CONCISE — the worker's context window is precious
- Focus on ACTIONABLE information, not background noise
- Include specific file paths if relevant
- Your output quality directly determines the worker's effectiveness
"""

WORKER_SYSTEM = """You are the WORKER — Phase 2 of the AIM-OS 3-Phase Agent Loop.

YOUR ROLE: Execute the task using the pre-built context provided to you.
You have been given carefully researched context — trust it and focus on execution.

YOUR PROCESS:
1. Read the context pack provided
2. Execute the task as instructed
3. Report your results in structured format

OUTPUT FORMAT — You MUST output valid JSON with this exact structure:
```json
{
    "success": true,
    "output": "Your main work output / analysis / code / etc",
    "files_modified": [],
    "files_created": [],
    "decisions_made": ["decision1"],
    "issues_encountered": ["issue1"],
    "suggested_next_steps": ["step1"]
}
```

CRITICAL RULES:
- Focus purely on EXECUTION — context research is already done
- Be precise and thorough in your work
- Document every decision you make
- Report any issues honestly — the Closeout agent needs accurate data
"""

CLOSEOUT_SYSTEM = """You are the CLOSEOUT AGENT — Phase 3 of the AIM-OS 3-Phase Agent Loop.

YOUR ROLE: Document what happened, assess quality, and prepare a handoff for the next iteration.

YOUR PROCESS:
1. Review the worker's output and assess its quality
2. Summarize what was accomplished
3. Identify open issues and next priorities
4. Score the quality of the context that was provided to the worker
5. Determine if the overall task is complete or needs more iterations

OUTPUT FORMAT — You MUST output valid JSON with this exact structure:
```json
{
    "task_complete": false,
    "iteration_summary": "What was accomplished this iteration",
    "cumulative_progress": "Overall progress across all iterations",
    "open_issues": ["issue1"],
    "next_priorities": ["priority1"],
    "quality_score": 0.8,
    "context_quality_score": 0.9
}
```

SCORING GUIDE:
- quality_score: 0.0 = total failure, 0.5 = partial, 0.8 = good, 1.0 = perfect
- context_quality_score: Rate how useful the context pack was for the worker
- task_complete: Set true ONLY if the task is fully resolved

CRITICAL RULES:
- Be HONEST in your quality assessments
- Focus on what's needed for the NEXT iteration
- Keep cumulative_progress updated with ALL progress so far
"""


# ══════════════════════════════════════════════════════════
# PHASE EXECUTORS
# ══════════════════════════════════════════════════════════

def _parse_json_from_response(text: str) -> dict:
    """Extract JSON from an LLM response that may contain markdown fences."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ``` fences
    import re
    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding first { ... } block
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start >= 0 and brace_end > brace_start:
        try:
            return json.loads(text[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    # Give up — return raw text wrapped
    return {'output': text, '_parse_failed': True}


def run_context_researcher(
    provider,
    task: str,
    handoff: Optional[Handoff],
    config: LoopConfig,
    iteration: int,
) -> tuple[ContextPack, PhaseMetrics]:
    """Phase 1: Build context for the worker.

    Args:
        provider: GeminiCLIProvider instance
        task: The original task
        handoff: Previous iteration's handoff (None for first iteration)
        config: Loop configuration
        iteration: Current iteration number

    Returns:
        (ContextPack, PhaseMetrics) tuple
    """
    start = time.time()

    # Build the prompt
    prompt_parts = [f"## Task\n{task}"]

    if handoff and handoff.iteration > 0:
        prompt_parts.append(handoff.to_prompt())

    depth_instructions = {
        'shallow': "Keep your research brief — just summarize the key points.",
        'medium': "Do a thorough analysis of the task and available context.",
        'deep': "Do an exhaustive deep-dive: check all MCP tools, analyze file structures, review all relevant history.",
    }
    prompt_parts.append(
        f"\n## Research Depth: {config.context_depth.upper()}\n"
        f"{depth_instructions.get(config.context_depth, depth_instructions['medium'])}"
    )

    prompt = '\n\n'.join(prompt_parts)

    # Choose MCP access
    mcp_servers = ['ai-engine'] if config.context_mcp_access else None

    # Call Gemini CLI
    model = config.model_per_phase.get('context', 'auto')
    timeout = config.timeout_per_phase.get('context', 60)

    logger.info(f'[Phase 1] Context Research iter={iteration} depth={config.context_depth}')

    response = provider.complete(
        prompt=prompt,
        system=CONTEXT_RESEARCHER_SYSTEM,
        model=model if model != 'auto' else '',
        timeout=timeout,
        mcp_servers=mcp_servers,
    )

    elapsed = (time.time() - start) * 1000

    # Parse response into ContextPack
    if response.success:
        data = _parse_json_from_response(response.content)
        context_pack = ContextPack(
            task_summary=data.get('task_summary', task),
            relevant_history=data.get('relevant_history', ''),
            project_state=data.get('project_state', ''),
            instructions=data.get('instructions', ''),
            files_to_examine=data.get('files_to_examine', []),
            constraints=data.get('constraints', []),
            references=data.get('references', []),
            research_notes=data.get('research_notes', ''),
            tokens_used=response.tokens_in + response.tokens_out,
            build_time_ms=elapsed,
        )
    else:
        # Fallback: pass raw task as context
        context_pack = ContextPack(
            task_summary=task,
            instructions="Execute the task as described.",
            build_time_ms=elapsed,
        )

    metrics = PhaseMetrics(
        phase=PhaseType.CONTEXT,
        iteration=iteration,
        latency_ms=elapsed,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        model_used=response.model or model,
        success=response.success,
        error=response.error if not response.success else '',
    )

    logger.info(f'[Phase 1] Done in {elapsed:.0f}ms — context has {len(context_pack.to_prompt())} chars')
    return context_pack, metrics


def run_worker(
    provider,
    context_pack: ContextPack,
    config: LoopConfig,
    iteration: int,
) -> tuple[WorkResult, PhaseMetrics]:
    """Phase 2: Execute the task with pre-built context.

    Args:
        provider: GeminiCLIProvider instance
        context_pack: Pre-built context from Phase 1
        config: Loop configuration
        iteration: Current iteration number

    Returns:
        (WorkResult, PhaseMetrics) tuple
    """
    start = time.time()

    # The worker's prompt IS the context pack
    prompt = context_pack.to_prompt()

    # MCP access for worker (usually disabled — the key innovation)
    mcp_servers = ['ai-engine'] if config.worker_mcp_access else None

    model = config.model_per_phase.get('worker', 'auto')
    timeout = config.timeout_per_phase.get('worker', 120)

    logger.info(f'[Phase 2] Worker iter={iteration} mcp={"yes" if mcp_servers else "no"}')

    response = provider.complete(
        prompt=prompt,
        system=WORKER_SYSTEM,
        model=model if model != 'auto' else '',
        timeout=timeout,
        mcp_servers=mcp_servers,
    )

    elapsed = (time.time() - start) * 1000

    if response.success:
        data = _parse_json_from_response(response.content)
        work_result = WorkResult(
            success=data.get('success', True),
            output=data.get('output', response.content),
            files_modified=data.get('files_modified', []),
            files_created=data.get('files_created', []),
            decisions_made=data.get('decisions_made', []),
            issues_encountered=data.get('issues_encountered', []),
            suggested_next_steps=data.get('suggested_next_steps', []),
            raw_response=response.content,
            tokens_used=response.tokens_in + response.tokens_out,
            work_time_ms=elapsed,
            model_used=response.model or model,
        )
    else:
        work_result = WorkResult(
            success=False,
            output=f"Worker failed: {response.error}",
            issues_encountered=[response.error],
            raw_response=response.content,
            work_time_ms=elapsed,
        )

    metrics = PhaseMetrics(
        phase=PhaseType.WORKER,
        iteration=iteration,
        latency_ms=elapsed,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        model_used=response.model or model,
        success=response.success,
        error=response.error if not response.success else '',
    )

    logger.info(f'[Phase 2] Done in {elapsed:.0f}ms — success={work_result.success}')
    return work_result, metrics


def run_closeout(
    provider,
    task: str,
    context_pack: ContextPack,
    work_result: WorkResult,
    previous_handoff: Optional[Handoff],
    config: LoopConfig,
    iteration: int,
) -> tuple[Handoff, PhaseMetrics]:
    """Phase 3: Document, assess quality, prepare handoff.

    Args:
        provider: GeminiCLIProvider instance
        task: The original task
        context_pack: What context was provided to the worker
        work_result: What the worker produced
        previous_handoff: Previous iteration's handoff
        config: Loop configuration
        iteration: Current iteration number

    Returns:
        (Handoff, PhaseMetrics) tuple
    """
    start = time.time()

    # Build closeout prompt with all the data
    prompt_parts = [
        f"# Original Task\n{task}",
        f"# Iteration: {iteration}",
        f"\n# Context That Was Provided to Worker\n{json.dumps(context_pack.to_dict(), indent=2)[:2000]}",
        f"\n# Worker's Output\n{json.dumps(work_result.to_dict(), indent=2)[:3000]}",
    ]

    if previous_handoff:
        prompt_parts.append(
            f"\n# Previous Cumulative Progress\n{previous_handoff.cumulative_progress}"
        )

    prompt = '\n'.join(prompt_parts)

    mcp_servers = ['ai-engine'] if config.closeout_mcp_access else None
    model = config.model_per_phase.get('closeout', 'auto')
    timeout = config.timeout_per_phase.get('closeout', 60)

    logger.info(f'[Phase 3] Closeout iter={iteration}')

    response = provider.complete(
        prompt=prompt,
        system=CLOSEOUT_SYSTEM,
        model=model if model != 'auto' else '',
        timeout=timeout,
        mcp_servers=mcp_servers,
    )

    elapsed = (time.time() - start) * 1000

    if response.success:
        data = _parse_json_from_response(response.content)
        handoff = Handoff(
            task=task,
            task_complete=data.get('task_complete', False),
            iteration_summary=data.get('iteration_summary', ''),
            cumulative_progress=data.get('cumulative_progress', ''),
            open_issues=data.get('open_issues', []),
            next_priorities=data.get('next_priorities', []),
            quality_score=float(data.get('quality_score', 0.5)),
            context_quality_score=float(data.get('context_quality_score', 0.5)),
            iteration=iteration,
            closeout_time_ms=elapsed,
            tokens_used=response.tokens_in + response.tokens_out,
        )
    else:
        handoff = Handoff(
            task=task,
            task_complete=False,
            iteration_summary=f"Closeout failed: {response.error}",
            iteration=iteration,
            closeout_time_ms=elapsed,
        )

    metrics = PhaseMetrics(
        phase=PhaseType.CLOSEOUT,
        iteration=iteration,
        latency_ms=elapsed,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        model_used=response.model or model,
        success=response.success,
        output_quality=handoff.quality_score,
        context_quality=handoff.context_quality_score,
        error=response.error if not response.success else '',
    )

    logger.info(
        f'[Phase 3] Done in {elapsed:.0f}ms — '
        f'complete={handoff.task_complete} quality={handoff.quality_score:.0%}'
    )
    return handoff, metrics
