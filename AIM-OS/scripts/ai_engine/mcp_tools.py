"""
AIM-OS AI Engine — MCP Tools v2

Exposes the unified AI Engine as MCP tools so that any agent
(and the engine itself) can use it programmatically.

v2 upgrades:
    - Uses unified AIEngine facade instead of individual subsystems
    - Adds swarm tools (ai_engine_swarm, ai_engine_workers)
    - Adds context tools (ai_engine_context, ai_engine_tools)
    - Adds learning tools (ai_engine_learn, ai_engine_insights)
    - Adds registry/session tools
    - 14 tools total (up from 6)

Tools:
    ai_engine_execute    — Full 7-layer engine pipeline (flagship tool)
    ai_engine_ask        — Quick LLM prompt via Gemini CLI
    ai_engine_code       — Run coding agent on a task
    ai_engine_plan       — Run planning agent for analysis
    ai_engine_audit      — Run audit agent for code review
    ai_engine_swarm      — Swarm execution (decompose → workers → merge)
    ai_engine_context    — Build a ContextPack for a task
    ai_engine_tools      — Get tool recommendations for a task type
    ai_engine_learn      — Feed an execution outcome to the learner
    ai_engine_insights   — Get learning insights and model recommendations
    ai_engine_agents     — List registered agents and their capabilities
    ai_engine_sessions   — Session management (create, list, complete)
    ai_engine_status     — Full engine health report (all subsystems)
    ai_engine_index      — Index workspace for context engine
"""

import os
import sys
import json
import time
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger('ai_engine.mcp_tools')

# ── Lazy Engine Singleton ────────────────────────────────

_engine = None
_workspace = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')


def _get_engine():
    """Get or create the singleton AIEngine instance."""
    global _engine
    if _engine is None:
        from ai_engine.engine import AIEngine, EngineConfig
        config = EngineConfig(
            workspace_root=os.path.abspath(_workspace),
            use_daemon_rag=True,
            enable_learning=True,
            enable_traces=True,
            enable_vif=True,
        )
        _engine = AIEngine(config)
    return _engine


# ══════════════════════════════════════════════════════════
# FLAGSHIP TOOLS
# ══════════════════════════════════════════════════════════

def ai_engine_execute(
    task: str,
    active_file: str = '',
    include_files: str = '',
    agent_id: str = '',
    model: str = 'auto',
) -> dict:
    """
    Execute a task through the full 7-layer AI Engine pipeline.

    Pipeline: Context→Agent Selection→Genome→VIF Gate→LLM→Trace→Learn

    Args:
        task: What to do (e.g., "Fix the auth bug in auth.py")
        active_file: Currently active file for context
        include_files: Comma-separated additional file paths
        agent_id: Force specific agent (coder_v1, architect_v1, etc.)
        model: Model override ('auto' for intelligent routing)

    Returns:
        EngineResult with output, confidence, model used, trace ID
    """
    engine = _get_engine()
    files = [f.strip() for f in include_files.split(',') if f.strip()] if include_files else None

    result = engine.execute(
        task=task,
        active_file=active_file,
        include_files=files,
        agent_id=agent_id,
        model=model,
    )
    return {
        'success': result.success,
        'output': result.output[:4000],
        'confidence': result.confidence,
        'model_used': result.model_used,
        'agent_used': result.agent_used,
        'trace_id': result.trace_id,
        'time_ms': round(result.time_ms, 1),
        'learnings': result.learnings,
        'errors': result.errors,
    }


def ai_engine_ask(
    prompt: str,
    system: str = '',
    model: str = '',
    task_type: str = 'standard',
) -> dict:
    """
    Quick LLM prompt via Gemini CLI (unlimited, $0 cost).
    Bypasses the full engine pipeline for fast queries.

    Args:
        prompt: The question or instruction
        system: Optional system instruction
        model: Model name or empty for auto-selection
        task_type: fast|standard|deep-think|code-edit|planning

    Returns:
        Response with content, model used, latency
    """
    engine = _get_engine()
    response = engine.router.complete(
        prompt=prompt,
        system=system,
        model=model,
        task_type=task_type,
    )
    return response.to_dict() if hasattr(response, 'to_dict') else {'content': str(response)}


def ai_engine_code(
    task: str,
    active_file: str = '',
    include_files: str = '',
) -> dict:
    """
    Run the Coding Agent on a task.
    Uses the engine pipeline with auto-selected coder agent.

    Args:
        task: What to code (e.g., "Add error handling to auth.py")
        active_file: Currently active file path
        include_files: Comma-separated file paths for context
    """
    return ai_engine_execute(task=task, active_file=active_file,
                             include_files=include_files, agent_id='coder_v1')


def ai_engine_plan(question: str, context: str = '') -> dict:
    """
    Run the Planning Agent for architectural analysis.

    Args:
        question: What to plan/analyse
        context: Additional context (constraints, current state)
    """
    task = f"{question}\n\nContext:\n{context}" if context else question
    return ai_engine_execute(task=task, agent_id='architect_v1')


def ai_engine_audit(target: str, focus: str = 'general') -> dict:
    """
    Run the Audit Agent for code review.

    Args:
        target: File path, code snippet, or task description to audit
        focus: general|security|performance|self-improvement
    """
    task = f"Audit with focus on {focus}:\n\n{target}"
    return ai_engine_execute(task=task, agent_id='auditor_v1')


# ══════════════════════════════════════════════════════════
# SWARM TOOLS
# ══════════════════════════════════════════════════════════

def ai_engine_swarm(
    task: str,
    workers: int = 3,
) -> dict:
    """
    Execute a complex task using the swarm orchestrator.
    Decomposes task → assigns to specialized workers → merges results.

    Args:
        task: Complex task description
        workers: Number of parallel workers (default: 3)
    """
    engine = _get_engine()
    result = engine.swarm_execute(task=task, workers=workers)
    return {
        'success': result.success,
        'output': result.output[:4000],
        'time_ms': round(result.time_ms, 1),
        'errors': result.errors,
    }


# ══════════════════════════════════════════════════════════
# CONTEXT & INTELLIGENCE TOOLS
# ══════════════════════════════════════════════════════════

def ai_engine_context(
    task: str,
    active_file: str = '',
    max_tokens: int = 0,
) -> dict:
    """
    Build a ContextPack for a task (Evidence→Retrieval→Budgeting→Pack).
    Shows what context the engine would gather without executing.

    Args:
        task: Task description
        active_file: Primary file for context
        max_tokens: Token budget (0 = auto based on task type)
    """
    engine = _get_engine()
    pack = engine.context_builder.build_for_task(
        task=task,
        active_file=active_file,
        max_tokens=max_tokens,
    )
    return pack.to_dict()


def ai_engine_tools(task_type: str = 'coding') -> dict:
    """
    Get MCP tool recommendations for a task type.
    Uses DaemonRAG's ToolSelectionEngine when available.

    Args:
        task_type: coding|debugging|planning|review|research
    """
    engine = _get_engine()
    advice = engine.tool_advisor.advise(task_type=task_type)
    return {
        'recommended': [{'tool': r.tool_id, 'score': r.score} for r in advice.recommended_tools],
        'total': advice.total_tools,
        'strategy': advice.strategy,
        'source': advice.source,
    }


def ai_engine_learn(
    task_type: str,
    agent_name: str,
    model_used: str,
    success: bool,
    confidence: float = 0.5,
    time_ms: float = 0.0,
) -> dict:
    """
    Feed an execution outcome to the learning system.
    Updates model preferences and identifies failure patterns.

    Args:
        task_type: Type of task completed
        agent_name: Agent that executed the task
        model_used: LLM model used
        success: Whether the task succeeded
        confidence: Confidence score (0-1)
        time_ms: Execution time in milliseconds
    """
    from ai_engine.traces.execution_trace import ExecutionTrace, TraceOutcome
    engine = _get_engine()

    trace = ExecutionTrace(
        task_type=task_type,
        agent_name=agent_name,
        model_used=model_used,
        outcome=TraceOutcome.SUCCESS if success else TraceOutcome.FAILURE,
        confidence=confidence,
        total_time_ms=time_ms,
    )

    insights = engine.learner.learn_from_trace(trace)
    return {
        'insights': [{'type': i.insight_type, 'description': i.description} for i in insights],
        'model_stats': engine.learner.get_model_stats(),
    }


def ai_engine_insights(limit: int = 10) -> dict:
    """
    Get learning insights and model performance recommendations.

    Args:
        limit: Max insights to return (default: 10)
    """
    engine = _get_engine()
    insights = engine.learner.get_insights(limit)
    recommended = engine.learner.recommend_model('coding')

    return {
        'insights': [{'type': i.insight_type, 'description': i.description, 'confidence': i.confidence}
                     for i in insights],
        'recommended_model_for_coding': recommended,
        'model_stats': engine.learner.get_model_stats(),
        'status': engine.learner.status(),
    }


# ══════════════════════════════════════════════════════════
# REGISTRY & SESSION TOOLS
# ══════════════════════════════════════════════════════════

def ai_engine_agents() -> dict:
    """List all registered agents and their capabilities."""
    engine = _get_engine()
    agents = engine.registry.list_all()
    return {
        'agents': [
            {
                'id': a.agent_id,
                'name': a.name,
                'role': a.role,
                'task_types': a.task_types,
                'model_preference': a.model_preference,
                'capabilities': [c.name for c in a.capabilities],
                'status': a.status,
                'total_tasks': a.total_tasks,
                'success_rate': round(a.success_rate, 3),
            }
            for a in agents
        ],
        'total': len(agents),
    }


def ai_engine_sessions(action: str = 'list', session_id: str = '', agent_id: str = '') -> dict:
    """
    Session management for Gemini CLI workers.

    Args:
        action: list|create|complete|status
        session_id: Session ID (for complete action)
        agent_id: Agent ID (for create action)
    """
    engine = _get_engine()
    mgr = engine.sessions

    if action == 'create':
        session = mgr.create(agent_id=agent_id)
        mgr.activate(session.session_id)
        return {'session_id': session.session_id, 'state': session.state}
    elif action == 'complete' and session_id:
        mgr.complete(session_id)
        return {'completed': session_id}
    elif action == 'status':
        return mgr.status()
    else:  # list
        active = mgr.get_active()
        return {
            'active_sessions': [
                {'id': s.session_id, 'agent': s.agent_id, 'state': s.state}
                for s in active
            ],
            'status': mgr.status(),
        }


# ══════════════════════════════════════════════════════════
# STATUS & SYSTEM TOOLS
# ══════════════════════════════════════════════════════════

def ai_engine_status() -> dict:
    """
    Full AI Engine health report.
    Shows all subsystem status: registry, genome, sessions,
    traces, learner, VIF, router.
    """
    engine = _get_engine()
    status = engine.status()
    status['version'] = '1.0.0'
    status['tools_registered'] = len(AI_ENGINE_TOOLS)
    return status


def ai_engine_index(workspace_root: str = '', force: bool = True) -> dict:
    """
    Index or re-index workspace for the Context Engine.

    Args:
        workspace_root: Root directory (default: current workspace)
        force: Force re-index even if recently indexed
    """
    engine = _get_engine()
    return engine.context_builder.status()


# ══════════════════════════════════════════════════════════
# TOOL REGISTRY
# ══════════════════════════════════════════════════════════

AI_ENGINE_TOOLS = {
    # Flagship
    'ai_engine_execute': ai_engine_execute,
    'ai_engine_ask': ai_engine_ask,
    'ai_engine_code': ai_engine_code,
    'ai_engine_plan': ai_engine_plan,
    'ai_engine_audit': ai_engine_audit,
    # Swarm
    'ai_engine_swarm': ai_engine_swarm,
    # Context & Intelligence
    'ai_engine_context': ai_engine_context,
    'ai_engine_tools': ai_engine_tools,
    'ai_engine_learn': ai_engine_learn,
    'ai_engine_insights': ai_engine_insights,
    # Registry & Sessions
    'ai_engine_agents': ai_engine_agents,
    'ai_engine_sessions': ai_engine_sessions,
    # System
    'ai_engine_status': ai_engine_status,
    'ai_engine_index': ai_engine_index,
}


def register_ai_engine_tools(mcp_server):
    """
    Register all AI Engine tools with an MCP server.

    Usage:
        from ai_engine.mcp_tools import register_ai_engine_tools
        register_ai_engine_tools(my_mcp_server)
    """
    for name, func in AI_ENGINE_TOOLS.items():
        mcp_server.tool(name)(func)
    return {
        'registered': len(AI_ENGINE_TOOLS),
        'tools': list(AI_ENGINE_TOOLS.keys()),
    }
