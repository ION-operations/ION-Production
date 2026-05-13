"""
AIM-OS AI Engine — Enhanced Worker

The intelligence layer that transforms raw Gemini CLI workers
into context-aware, memory-equipped, quality-scored agents.

Wraps the basic GeminiCLIProvider + WorkerManager pipeline with:
    1. Pre-exec:  ContextPack assembly (workspace search, git diffs, symbols)
    2. Pre-exec:  CMC memory retrieval (institutional knowledge)
    3. Post-exec: Quality scoring via quality.py
    4. Post-exec: CMC result storage (learning for future workers)
    5. Comms:     Inter-agent message bus integration
    6. Meta:      Evolution metrics feeding into Context Lab

Design principle (Braden):
    "Build yourself a team you are truly proud of and can trust."

This is that team.
"""

import os
import sys
import json
import time
import uuid
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger('ai_engine.enhanced_worker')

# Ensure imports work
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

WORKSPACE = os.path.join(SCRIPT_DIR, '..', '..')


# ── Enhanced Result ──────────────────────────────────────

@dataclass
class EnhancedResult:
    """Result from an enhanced worker — includes context and quality metadata."""
    # Core
    worker_id: str = ''
    role: str = ''
    task: str = ''
    content: str = ''
    success: bool = False
    error: str = ''

    # Timing
    latency_ms: float = 0.0
    context_build_ms: float = 0.0
    llm_ms: float = 0.0
    scoring_ms: float = 0.0

    # Context
    context_tokens: int = 0
    context_sources: List[str] = field(default_factory=list)
    memory_items_retrieved: int = 0

    # Quality
    quality_score: float = 0.0
    quality_breakdown: Dict[str, float] = field(default_factory=dict)

    # Meta
    model: str = ''
    genome_tokens: int = 0
    stored_to_cmc: bool = False
    evolution_reported: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ── Enhanced Worker ──────────────────────────────────────

class EnhancedWorker:
    """
    A Gemini CLI worker wrapped with AIM-OS intelligence:
    
    Before execution:
        - Builds a ContextPack (workspace files, symbols, git diffs)
        - Retrieves relevant CMC memories
        - Assembles a genome-based system prompt
    
    After execution:
        - Scores output quality (completeness, confidence, usefulness)
        - Stores result summary in CMC for future workers
        - Reports metrics to evolution engine
        - Publishes status to comms bus
    """

    def __init__(
        self,
        workspace_root: str = '',
        role: str = 'researcher',
        model: str = '',
        timeout: int = 120,
        enable_context: bool = True,
        enable_structural_context: bool = False,
        enable_atlas: bool = True,
        enable_memory: bool = True,
        enable_scoring: bool = True,
        enable_comms: bool = True,
        enable_evolution: bool = True,
        max_context_tokens: int = 16000,
    ):
        self.workspace_root = workspace_root or WORKSPACE
        self.role = role
        self.model = model
        self.timeout = timeout
        self.enable_context = enable_context
        self.enable_structural_context = enable_structural_context
        self.enable_atlas = enable_atlas
        self.enable_memory = enable_memory
        self.enable_scoring = enable_scoring
        self.enable_comms = enable_comms
        self.enable_evolution = enable_evolution
        self.max_context_tokens = max_context_tokens

        # Lazy-loaded components
        self._provider = None
        self._genome_loader = None
        self._context_builder = None
        self._context_mapper = None
        self._quality_scorer = None
        self._atlas = None
        self._mcp_bridge = None
        self._worker_id = f'ew_{uuid.uuid4().hex[:8]}'

    # ── Lazy Component Access ─────────────────────────────

    @property
    def provider(self):
        if self._provider is None:
            from providers.gemini_cli_provider import GeminiCLIProvider
            self._provider = GeminiCLIProvider(
                working_directory=self.workspace_root,
            )
        return self._provider

    @property
    def genome_loader(self):
        if self._genome_loader is None:
            from genome_loader import GenomeLoader
            self._genome_loader = GenomeLoader(workspace_root=self.workspace_root)
        return self._genome_loader

    @property
    def context_builder(self):
        if self._context_builder is None:
            try:
                from context.context_pack import ContextPackBuilder
                self._context_builder = ContextPackBuilder(
                    workspace_root=self.workspace_root,
                )
            except Exception as e:
                logger.warning(f'ContextPackBuilder unavailable: {e}')
        return self._context_builder

    @property
    def context_mapper(self):
        if self._context_mapper is None:
            try:
                from context_mapper import ContextMapper
                self._context_mapper = ContextMapper(
                    workspace_root=self.workspace_root,
                )
            except Exception as e:
                logger.warning(f'ContextMapper unavailable: {e}')
        return self._context_mapper

    @property
    def atlas(self):
        if self._atlas is None:
            try:
                from atlas_agent import Atlas
                self._atlas = Atlas(workspace_root=self.workspace_root)
                # Try loading from disk first (instant), fall back to fresh index
                if not self._atlas.load():
                    self._atlas.index()
            except Exception as e:
                logger.warning(f'Atlas unavailable: {e}')
        return self._atlas

    @property
    def quality_scorer(self):
        if self._quality_scorer is None:
            try:
                from agent_loop.quality import score_context_pack
                self._quality_scorer = score_context_pack
            except Exception as e:
                logger.warning(f'Quality scorer unavailable: {e}')
        return self._quality_scorer

    # ── Core Execution ────────────────────────────────────

    def execute(
        self,
        task: str,
        active_file: str = '',
        include_files: Optional[List[str]] = None,
        extra_context: str = '',
        task_constraints: str = '',
    ) -> EnhancedResult:
        """
        Execute a task with full AIM-OS intelligence.
        
        Pipeline:
            1. Build genome system prompt
            2. Gather context (files, symbols, git diffs)
            3. Retrieve relevant memories from CMC
            4. Assemble enhanced prompt
            5. Execute via Gemini CLI
            6. Score output quality
            7. Store results to CMC
            8. Report to evolution engine
            9. Publish to comms bus
        
        Args:
            task: What to do
            active_file: Currently focused file
            include_files: Additional files for context
            extra_context: Manual context to prepend
            task_constraints: Constraints/guardrails for the task
        
        Returns:
            EnhancedResult with content, quality metrics, and metadata
        """
        start_time = time.monotonic()
        result = EnhancedResult(
            worker_id=self._worker_id,
            role=self.role,
            task=task,
        )

        # ── Step 1: Build Genome ──────────────────────────
        genome = self.genome_loader.build_genome(
            role=self.role,
            task=task,
            task_constraints=task_constraints,
            instance_id=self._worker_id,
        )
        system_prompt = genome.to_system_prompt()
        result.genome_tokens = genome.total_tokens

        # ── Step 1b: Atlas Big Picture ────────────────────
        atlas_context = ''
        if self.enable_atlas and self.atlas:
            try:
                atlas_context = self.atlas.build_context_package(
                    task=task,
                    include_summary=True,
                    max_modules=3,
                )
                logger.info(
                    f'[{self._worker_id}] Atlas: {len(atlas_context)} chars big-picture context'
                )
            except Exception as e:
                logger.warning(f'[{self._worker_id}] Atlas context failed: {e}')

        # ── Step 2: Build Context Pack ────────────────────
        context_content = ''
        if self.enable_context and self.context_builder:
            ctx_start = time.monotonic()
            try:
                context_pack = self.context_builder.build_for_task(
                    task=task,
                    active_file=active_file,
                    include_files=include_files,
                    max_tokens=self.max_context_tokens,
                )
                context_content = context_pack.get_content()
                result.context_tokens = context_pack.total_tokens
                result.context_sources = [
                    e.source for e in context_pack.evidence
                ]
                result.context_build_ms = (time.monotonic() - ctx_start) * 1000
                logger.info(
                    f'[{self._worker_id}] Context: {result.context_tokens} tokens '
                    f'from {len(result.context_sources)} sources '
                    f'({result.context_build_ms:.0f}ms)'
                )
            except Exception as e:
                logger.warning(f'[{self._worker_id}] Context build failed: {e}')

        # ── Step 2b: Structural Context (AST Envelope) ────
        structural_content = ''
        if self.enable_structural_context and active_file and self.context_mapper:
            try:
                envelope = self.context_mapper.build_envelope(
                    target_path=active_file,
                    budget_chars=self.max_context_tokens * 4,
                )
                structural_content = envelope.to_string()
                stats = envelope.stats
                logger.info(
                    f'[{self._worker_id}] Structural: {stats["contract_count"]} contracts '
                    f'from {stats["dependency_count"]} deps '
                    f'({stats["estimated_tokens"]} tokens)'
                )
            except Exception as e:
                logger.warning(f'[{self._worker_id}] Structural context failed: {e}')

        # ── Step 3: Retrieve CMC Memories ─────────────────
        memory_content = ''
        if self.enable_memory:
            try:
                memory_content = self._retrieve_memories(task)
                if memory_content:
                    result.memory_items_retrieved = memory_content.count('---')
                    logger.info(
                        f'[{self._worker_id}] Retrieved {result.memory_items_retrieved} '
                        f'memory items from CMC'
                    )
            except BaseException as e:
                logger.debug(f'[{self._worker_id}] Memory retrieval skipped: {e}')

        # ── Step 4: Assemble Enhanced Prompt ──────────────
        prompt_parts = []
        if atlas_context:
            prompt_parts.append(f"## Big Picture (Atlas)\n{atlas_context}")
        if structural_content:
            prompt_parts.append(f"## Structural Context (AST Contracts)\n{structural_content}")
        if extra_context:
            prompt_parts.append(f"## Additional Context\n{extra_context}")
        if context_content:
            prompt_parts.append(f"## Workspace Context\n{context_content}")
        if memory_content:
            prompt_parts.append(f"## Institutional Memory\n{memory_content}")
        prompt_parts.append(f"## Task\n{task}")
        prompt_parts.append(
            "\n## Output Requirements\n"
            "Respond with structured, actionable output. Include:\n"
            "- A clear summary of findings\n"
            "- Confidence level (0-1) in your analysis\n"
            "- Any risks or concerns identified\n"
            "- Specific recommendations"
        )

        full_prompt = '\n\n'.join(prompt_parts)

        # ── Step 5: Execute via Gemini CLI ────────────────
        llm_start = time.monotonic()
        response = self.provider.complete(
            prompt=full_prompt,
            system=system_prompt,
            model=self.model,
            timeout=self.timeout,
        )
        result.llm_ms = (time.monotonic() - llm_start) * 1000
        result.content = response.content
        result.success = response.success
        result.error = response.error
        result.model = response.model

        if not response.success:
            result.latency_ms = (time.monotonic() - start_time) * 1000
            logger.error(f'[{self._worker_id}] Execution failed: {response.error}')
            return result

        # ── Step 6: Score Quality ─────────────────────────
        if self.enable_scoring and self.quality_scorer:
            score_start = time.monotonic()
            try:
                score = self.quality_scorer.score(
                    task=task,
                    output=response.content,
                )
                result.quality_score = score.get('overall', 0.0)
                result.quality_breakdown = score
                result.scoring_ms = (time.monotonic() - score_start) * 1000
                logger.info(
                    f'[{self._worker_id}] Quality: {result.quality_score:.2f} '
                    f'({result.scoring_ms:.0f}ms)'
                )
            except Exception as e:
                logger.warning(f'[{self._worker_id}] Scoring failed: {e}')

        # ── Step 7: Store to CMC ──────────────────────────
        if self.enable_memory and result.success:
            try:
                self._store_result_to_cmc(task, result)
                result.stored_to_cmc = True
            except Exception as e:
                logger.warning(f'[{self._worker_id}] CMC storage failed: {e}')

        # ── Step 8: Report to Evolution ───────────────────
        if self.enable_evolution and result.success:
            try:
                self._report_to_evolution(task, result)
                result.evolution_reported = True
            except Exception as e:
                logger.warning(f'[{self._worker_id}] Evolution report failed: {e}')

        # ── Step 9: Publish to Comms ──────────────────────
        if self.enable_comms and result.success:
            try:
                self._publish_status(task, result)
            except Exception as e:
                logger.warning(f'[{self._worker_id}] Comms publish failed: {e}')

        result.latency_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            f'[{self._worker_id}] Complete: {result.latency_ms:.0f}ms total '
            f'(ctx={result.context_build_ms:.0f}ms, llm={result.llm_ms:.0f}ms, '
            f'score={result.scoring_ms:.0f}ms)'
        )

        return result

    # ── Memory Integration ────────────────────────────────

    def _retrieve_memories(self, task: str) -> str:
        """Retrieve relevant memories from CMC via MCP HTTP bridge."""
        try:
            import requests
            resp = requests.post(
                'http://localhost:5001/mcp/execute',
                json={
                    'tool': 'retrieve_memory',
                    'arguments': {'query': task, 'limit': 5},
                },
                timeout=2,  # fast fail if MCP is down
            )
            if resp.status_code == 200:
                data = resp.json()
                memories = data.get('result', {}).get('memories', [])
                if memories:
                    parts = []
                    for m in memories[:5]:
                        content = m.get('content', '')
                        if content:
                            parts.append(f"---\n{content}")
                    return '\n'.join(parts)
        except BaseException:
            pass  # MCP not running — totally fine

        return ''

    def _store_result_to_cmc(self, task: str, result: 'EnhancedResult'):
        """Store result summary in CMC for institutional memory."""
        summary = (
            f"Worker {result.worker_id} ({result.role}) completed task: {task[:100]}\n"
            f"Quality: {result.quality_score:.2f}, Latency: {result.latency_ms:.0f}ms\n"
            f"Context: {result.context_tokens} tokens from {len(result.context_sources)} sources\n"
            f"Summary: {result.content[:300]}"
        )
        try:
            import requests
            requests.post(
                'http://localhost:5001/mcp/execute',
                json={
                    'tool': 'store_memory',
                    'arguments': {
                        'content': summary,
                        'tags': {
                            'type': 'worker_result',
                            'role': result.role,
                            'worker_id': result.worker_id,
                            'quality': str(round(result.quality_score, 2)),
                        },
                    },
                },
                timeout=5,
            )
        except Exception:
            pass

    # ── Evolution Reporting ───────────────────────────────

    def _report_to_evolution(self, task: str, result: 'EnhancedResult'):
        """Report execution metrics to the evolution engine."""
        try:
            import requests
            requests.post(
                'http://localhost:5001/mcp/execute',
                json={
                    'tool': 'ai_engine_learn',
                    'arguments': {
                        'task_type': self.role,
                        'agent_name': f'gemini_cli_{self.role}',
                        'model_used': result.model or 'auto',
                        'success': result.success,
                        'confidence': result.quality_score,
                        'time_ms': result.llm_ms,
                    },
                },
                timeout=5,
            )
        except Exception:
            pass

    # ── Comms Bus ─────────────────────────────────────────

    def _publish_status(self, task: str, result: 'EnhancedResult'):
        """Publish status update to the AI comms bus."""
        try:
            import requests
            requests.post(
                'http://localhost:5001/mcp/execute',
                json={
                    'tool': 'send_ai_message',
                    'arguments': {
                        'from_ai': f'GeminiCLI-{self.role}-{self._worker_id[:8]}',
                        'to_ai': 'Opus',
                        'content': (
                            f"Task completed: {task[:80]}... "
                            f"Quality: {result.quality_score:.2f}, "
                            f"Time: {result.latency_ms:.0f}ms"
                        ),
                        'message_type': 'status_update',
                    },
                },
                timeout=5,
            )
        except Exception:
            pass

    # ── Status ────────────────────────────────────────────

    def status(self) -> dict:
        return {
            'worker_id': self._worker_id,
            'role': self.role,
            'model': self.model or 'auto',
            'features': {
                'atlas': self.enable_atlas,
                'context': self.enable_context,
                'structural_context': self.enable_structural_context,
                'memory': self.enable_memory,
                'scoring': self.enable_scoring,
                'comms': self.enable_comms,
                'evolution': self.enable_evolution,
            },
            'provider_available': self.provider.is_available if self._provider else 'not_checked',
            'atlas_available': self._atlas is not None and self._atlas._indexed,
            'context_builder': self.context_builder is not None,
            'quality_scorer': self.quality_scorer is not None,
        }


# ── Enhanced Swarm ────────────────────────────────────────

class EnhancedSwarm:
    """
    Multi-agent swarm using EnhancedWorkers.
    
    Spawns N workers in parallel, each with full AIM-OS intelligence,
    then merges their results into a unified output.
    
    Usage:
        swarm = EnhancedSwarm(workspace_root='/path/to/AIM-OS')
        result = swarm.execute(
            task='Audit the CMC subsystem',
            roles=['researcher', 'auditor', 'architect'],
        )
    """

    def __init__(
        self,
        workspace_root: str = '',
        max_workers: int = 5,
        timeout_per_worker: int = 120,
        enable_context: bool = True,
        enable_memory: bool = True,
        enable_scoring: bool = True,
    ):
        self.workspace_root = workspace_root or WORKSPACE
        self.max_workers = max_workers
        self.timeout = timeout_per_worker
        self.enable_context = enable_context
        self.enable_memory = enable_memory
        self.enable_scoring = enable_scoring

    def execute(
        self,
        task: str,
        roles: Optional[List[str]] = None,
        active_file: str = '',
        extra_context: str = '',
    ) -> Dict[str, Any]:
        """
        Execute a task with multiple enhanced workers.
        
        Args:
            task: High-level task description
            roles: Worker roles to use (default: ['researcher', 'auditor'])
            active_file: Focused file for context
            extra_context: Additional manual context
        
        Returns:
            Dict with merged results, individual worker outputs, and stats
        """
        roles = roles or ['researcher', 'auditor']
        roles = roles[:self.max_workers]

        swarm_id = f'swarm_{uuid.uuid4().hex[:8]}'
        start_time = time.monotonic()

        logger.info(
            f'[{swarm_id}] Starting enhanced swarm: {len(roles)} workers '
            f'for task: {task[:60]}...'
        )

        # Create and execute workers sequentially
        # (parallel subprocess spawning on Windows can be fragile)
        worker_results: List[EnhancedResult] = []

        for i, role in enumerate(roles):
            logger.info(f'[{swarm_id}] Spawning worker {i+1}/{len(roles)}: {role}')
            worker = EnhancedWorker(
                workspace_root=self.workspace_root,
                role=role,
                timeout=self.timeout,
                enable_context=self.enable_context,
                enable_memory=self.enable_memory,
                enable_scoring=self.enable_scoring,
            )
            result = worker.execute(
                task=task,
                active_file=active_file,
                extra_context=extra_context,
            )
            worker_results.append(result)

        # Merge results
        total_time = (time.monotonic() - start_time) * 1000
        successful = [r for r in worker_results if r.success]
        failed = [r for r in worker_results if not r.success]

        # Build merged output
        merged_parts = []
        for r in successful:
            merged_parts.append(
                f"## {r.role.title()} Agent [{r.worker_id}]\n"
                f"**Quality:** {r.quality_score:.2f} | "
                f"**Time:** {r.llm_ms:.0f}ms | "
                f"**Context:** {r.context_tokens} tokens\n\n"
                f"{r.content}\n"
            )

        merged_output = '\n---\n\n'.join(merged_parts)

        # Compute aggregate stats
        avg_quality = (
            sum(r.quality_score for r in successful) / len(successful)
            if successful else 0.0
        )

        summary = {
            'swarm_id': swarm_id,
            'task': task,
            'total_time_ms': total_time,
            'workers': len(roles),
            'succeeded': len(successful),
            'failed': len(failed),
            'avg_quality': avg_quality,
            'merged_output': merged_output,
            'individual_results': [r.to_dict() for r in worker_results],
        }

        logger.info(
            f'[{swarm_id}] Complete: {len(successful)}/{len(roles)} succeeded, '
            f'avg quality={avg_quality:.2f}, total={total_time:.0f}ms'
        )

        return summary


# ── CLI Test ──────────────────────────────────────────────

def _test():
    """Quick smoke test of an enhanced worker."""
    print("═" * 60)
    print("  Enhanced Worker — Smoke Test")
    print("═" * 60)

    worker = EnhancedWorker(
        workspace_root=WORKSPACE,
        role='researcher',
        timeout=60,
        enable_context=True,
        enable_memory=True,
        enable_scoring=False,  # Quality scorer may not exist yet
        enable_comms=False,    # MCP bridge may not be running
        enable_evolution=False,
    )

    print(f"\n  Worker ID: {worker._worker_id}")
    print(f"  Role:      {worker.role}")
    print(f"  Status:    {json.dumps(worker.status(), indent=2)}")

    print(f"\n  Executing task...")
    result = worker.execute(
        task='List the Python files in scripts/ai_engine/ and briefly describe what each one does.',
        active_file='scripts/ai_engine/__init__.py',
    )

    print(f"\n  Success:     {result.success}")
    print(f"  Total time:  {result.latency_ms:.0f}ms")
    print(f"  Context:     {result.context_tokens} tokens, {result.context_build_ms:.0f}ms")
    print(f"  LLM:         {result.llm_ms:.0f}ms")
    print(f"  Genome:      ~{result.genome_tokens} tokens")
    print(f"  Memory:      {result.memory_items_retrieved} items retrieved")
    print(f"  Quality:     {result.quality_score:.2f}")
    print(f"  Content:     {result.content[:300]}...")

    if result.error:
        print(f"  Error:       {result.error}")

    return result


if __name__ == '__main__':
    _test()
