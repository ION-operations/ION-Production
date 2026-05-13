"""
AIM-OS AI Engine v1.0

A self-improving, multi-agent AI system powered by unlimited Gemini CLI,
deeply integrated with all AIM-OS subsystems.

Architecture (7 layers):
    L1  LLM Router         — providers/*, llm_router
    L2  Context Engine      — context/*, context_engine
    L3  Agent Runtime       — agents/*, agent_runtime, registry, genome_loader
    L4  Self-Improvement    — learning/*, traces/*, self_improve
    L5  Swarm               — swarm/*
    L6  Safety              — safety/*
    L7  Session             — session_manager

Usage:
    from ai_engine.engine import AIEngine
    engine = AIEngine(workspace_root='...')
    result = engine.execute("Fix the auth bug")
"""

__version__ = '1.0.0'

# Convenience imports
from ai_engine.engine import AIEngine, EngineConfig, EngineResult
