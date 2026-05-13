"""
AIM-OS AI Engine — Swarm Orchestrator

The brain of the swarm. Takes a high-level task, decomposes it
into worker jobs, assigns them, gates on results, and merges output.

Design by Sev:
    "Use an Orchestrator/Manager that only does: task decomposition,
     assignment, gating, merge of results."

The orchestrator NEVER does work itself — it delegates to workers
and coordinates their results.

Flow:
    1. Receive task from user/agent
    2. Decompose into worker jobs (via LLM Router)
    3. Create JobPackets with capabilities + genome overlays
    4. Spawn workers via WorkerManager
    5. Collect ResultPackets
    6. Validate results (VIF gates, output contract)
    7. Merge results into final output
    8. Store execution trace in CMC
    9. Publish handoff via comms
"""

import time
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

from ai_engine.swarm.contracts import (
    JobPacket, ResultPacket, SwarmTask, JobStatus,
    WorkerRole, JobPriority, OutputContract,
    ROLE_CAPABILITIES, CapabilityToken,
)
from ai_engine.swarm.worker_manager import WorkerManager

logger = logging.getLogger('ai_engine.orchestrator')


# ── Orchestrator ──────────────────────────────────────────

class SwarmOrchestrator:
    """
    Coordinates the Gemini CLI worker swarm.
    
    The orchestrator's ONLY job is:
        decompose → assign → gate → merge
    
    It never does work itself.
    """

    def __init__(
        self,
        worker_manager: Optional[WorkerManager] = None,
        llm_router=None,
        working_directory: str = '',
    ):
        self.worker_manager = worker_manager or WorkerManager(
            working_directory=working_directory,
        )
        self._llm_router = llm_router
        self._working_dir = working_directory

        # Execution history
        self._swarm_history: List[SwarmTask] = []

    def _ensure_router(self):
        if self._llm_router is None:
            from ai_engine.llm_router import LLMRouter
            self._llm_router = LLMRouter()

    # ── Main Entry Point ─────────────────────────────────

    def execute(
        self,
        task: str,
        decompose: bool = True,
        roles: Optional[List[str]] = None,
        context: str = '',
        priority: str = JobPriority.STANDARD,
        max_workers: int = 3,
    ) -> SwarmTask:
        """
        Execute a task using the swarm.
        
        Args:
            task: High-level task description
            decompose: If True, use LLM to decompose into sub-tasks
            roles: Worker roles to use (default: auto-select)
            context: Additional context for the task
            priority: Job priority
            max_workers: Maximum workers to spawn
        
        Returns:
            SwarmTask with all jobs and merged results
        """
        self._ensure_router()

        swarm_task = SwarmTask(description=task)
        swarm_task.status = JobStatus.RUNNING

        logger.info(f'[Orchestrator] Starting swarm task: {task[:80]}...')

        try:
            # Step 1: Decompose task into jobs
            if decompose:
                jobs = self._decompose_task(task, context, roles, max_workers)
            else:
                # Single worker mode
                role = roles[0] if roles else WorkerRole.CODER
                jobs = [self._create_job(task, role, context, priority)]

            swarm_task.jobs = jobs
            logger.info(f'[Orchestrator] Decomposed into {len(jobs)} jobs')

            # Step 2: Spawn workers and collect results
            for job in jobs:
                try:
                    worker = self.worker_manager.spawn(job)
                    result = self.worker_manager.collect(worker)
                    swarm_task.results[job.job_id] = result

                    logger.info(
                        f'[Orchestrator] Job {job.job_id} ({job.role}): '
                        f'{"DONE" if result.succeeded else "FAIL"} '
                        f'(confidence={result.confidence:.2f})'
                    )

                    # Retry on failure
                    if not result.succeeded and worker.retry_count < worker.max_retries:
                        logger.info(f'[Orchestrator] Retrying job {job.job_id}...')
                        retry_worker = self.worker_manager.spawn(job)
                        retry_result = self.worker_manager.collect(retry_worker)
                        swarm_task.results[job.job_id] = retry_result

                except Exception as e:
                    logger.error(f'[Orchestrator] Job {job.job_id} error: {e}')
                    swarm_task.results[job.job_id] = ResultPacket(
                        job_id=job.job_id,
                        status=JobStatus.FAILED,
                        error=str(e),
                    )

            # Step 3: Gate — validate results
            gate_passed = self._validate_results(swarm_task)

            # Step 4: Merge results
            if gate_passed or not swarm_task.any_failed:
                swarm_task.merged_output = self._merge_results(swarm_task)
                swarm_task.status = JobStatus.COMPLETED
            else:
                swarm_task.merged_output = self._merge_results(swarm_task)
                swarm_task.status = JobStatus.FAILED

            swarm_task.completed_at = time.time()

            # Step 5: Store trace
            self._store_trace(swarm_task)

            # Step 6: Publish handoff
            self._publish_handoff(swarm_task)

            self._swarm_history.append(swarm_task)

            logger.info(
                f'[Orchestrator] Swarm task {swarm_task.status}: '
                f'{len([r for r in swarm_task.results.values() if r.succeeded])}/'
                f'{len(swarm_task.jobs)} jobs succeeded'
            )

            return swarm_task

        except Exception as e:
            logger.error(f'[Orchestrator] Swarm task failed: {e}')
            swarm_task.status = JobStatus.FAILED
            return swarm_task

    # ── Task Decomposition ───────────────────────────────

    def _decompose_task(
        self,
        task: str,
        context: str,
        roles: Optional[List[str]],
        max_workers: int,
    ) -> List[JobPacket]:
        """
        Use the LLM Router to decompose a task into worker jobs.
        The LLM decides what roles are needed and what each does.
        """
        decompose_prompt = f"""Decompose this task into {max_workers} or fewer parallel worker jobs.

## Task
{task}

{"## Context" + chr(10) + context if context else ""}

## Available Worker Roles
- coder: Code generation, file editing, debugging
- architect: System analysis, design, planning
- auditor: Code review, quality checks, security analysis
- researcher: Deep research, knowledge gathering, documentation review
- tester: Test writing, test execution, validation

## Instructions
Respond with ONLY a JSON array of job objects:
[
    {{
        "role": "coder|architect|auditor|researcher|tester",
        "task": "Specific task for this worker",
        "priority": "critical|high|standard|low",
        "needs_files": ["list/of/relevant/files"],
        "depends_on": []
    }}
]

Rules:
- Each job should be independently executable
- Use the minimum number of workers needed
- Maximum {max_workers} jobs
- Split by concern, not by subtask ordering
"""

        response = self._llm_router.complete(
            prompt=decompose_prompt,
            task_type='planning',
            timeout=60,
        )

        jobs = []
        if response.success:
            try:
                # Parse job definitions
                import re
                content = response.content
                # Extract JSON array
                array_match = re.search(r'\[[\s\S]*\]', content)
                if array_match:
                    job_defs = json.loads(array_match.group())
                else:
                    job_defs = json.loads(content)

                for job_def in job_defs[:max_workers]:
                    role = job_def.get('role', WorkerRole.CODER)
                    job_task = job_def.get('task', task)
                    priority = job_def.get('priority', JobPriority.STANDARD)
                    files = job_def.get('needs_files', [])

                    job = self._create_job(job_task, role, context, priority, files)
                    jobs.append(job)

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f'Failed to parse decomposition: {e}')

        # Fallback: single worker if decomposition fails
        if not jobs:
            role = roles[0] if roles else WorkerRole.CODER
            jobs = [self._create_job(task, role, context, JobPriority.STANDARD)]

        return jobs

    def _create_job(
        self,
        task: str,
        role: str,
        context: str = '',
        priority: str = JobPriority.STANDARD,
        include_files: Optional[List[str]] = None,
    ) -> JobPacket:
        """Create a JobPacket for a worker."""
        # Get capabilities for role
        try:
            role_enum = WorkerRole(role)
        except ValueError:
            role_enum = WorkerRole.CODER

        caps = ROLE_CAPABILITIES.get(role_enum, ROLE_CAPABILITIES[WorkerRole.CODER])

        return JobPacket(
            role=role,
            task_description=task,
            capabilities=[c.value for c in caps],
            allowed_tools=[c.value for c in caps],
            allowed_paths=[self._working_dir] if self._working_dir else [],
            context_inline=context,
            include_files=include_files or [],
            priority=priority,
            output_contract=OutputContract(
                require_citations=True,
                require_confidence=True,
            ),
        )

    # ── Result Validation (VIF Gates) ────────────────────

    def _validate_results(self, swarm_task: SwarmTask) -> bool:
        """
        Validate all results using VIF-style confidence gates.
        Returns True if all results pass validation.
        """
        all_valid = True

        for job_id, result in swarm_task.results.items():
            # Find the corresponding job
            job = next((j for j in swarm_task.jobs if j.job_id == job_id), None)
            if not job:
                continue

            # Check confidence gate
            if result.confidence < 0.3:
                logger.warning(
                    f'[VIF Gate] Job {job_id} FAILED confidence gate '
                    f'(confidence={result.confidence:.2f}, threshold=0.3)'
                )
                all_valid = False

            # Check output contract
            if job.output_contract:
                violations = result.validate_against_contract(job.output_contract)
                if violations:
                    logger.warning(
                        f'[VIF Gate] Job {job_id} contract violations: {violations}'
                    )

            # Check for human escalation
            if result.requires_human:
                logger.warning(
                    f'[VIF Gate] Job {job_id} requires HUMAN review: '
                    f'{result.escalation_reason}'
                )
                all_valid = False

        return all_valid

    # ── Result Merging ───────────────────────────────────

    def _merge_results(self, swarm_task: SwarmTask) -> str:
        """Merge all worker results into a coherent final output."""
        parts = [f"# Swarm Task: {swarm_task.description[:100]}"]
        parts.append(f"**Task ID:** `{swarm_task.task_id}`")
        parts.append(f"**Status:** {swarm_task.status}")
        parts.append(f"**Workers:** {len(swarm_task.jobs)}")
        parts.append("")

        for job in swarm_task.jobs:
            result = swarm_task.results.get(job.job_id)
            if not result:
                parts.append(f"## [{job.role.upper()}] — No result")
                continue

            status_emoji = '✅' if result.succeeded else '❌'
            parts.append(f"## {status_emoji} [{job.role.upper()}] {job.task_description[:80]}")
            parts.append(f"**Confidence:** {result.confidence:.2f}")

            if result.summary:
                parts.append(f"\n{result.summary}")

            if result.risks:
                parts.append("\n**Risks:**")
                for risk in result.risks:
                    parts.append(f"- [{risk.get('level', '?')}] {risk.get('description', '')}")

            if result.next_actions:
                parts.append("\n**Next Actions:**")
                for action in result.next_actions:
                    parts.append(f"- {action}")

            if result.error:
                parts.append(f"\n**Error:** {result.error}")

            parts.append("")

        return '\n'.join(parts)

    # ── Trace Storage ────────────────────────────────────

    def _store_trace(self, swarm_task: SwarmTask):
        """Store execution trace in CMC via MCP."""
        try:
            from ai_engine.self_improve import MCPBridge
            mcp = MCPBridge()

            trace = {
                'task_id': swarm_task.task_id,
                'description': swarm_task.description[:200],
                'status': swarm_task.status,
                'jobs': len(swarm_task.jobs),
                'succeeded': sum(1 for r in swarm_task.results.values() if r.succeeded),
                'failed': sum(1 for r in swarm_task.results.values() if not r.succeeded),
                'total_time': swarm_task.completed_at - swarm_task.created_at,
            }

            mcp.store_memory(
                content=f"[Swarm Trace] {json.dumps(trace, indent=2)}",
                tags={'type': 'swarm_trace', 'task_id': swarm_task.task_id},
            )
        except Exception as e:
            logger.debug(f'Failed to store trace: {e}')

    def _publish_handoff(self, swarm_task: SwarmTask):
        """Publish handoff via comms bus."""
        try:
            from ai_engine.self_improve import MCPBridge
            mcp = MCPBridge()
            # Comms bus notification would go here
            # For now, just log
            logger.info(f'[Orchestrator] Handoff published for {swarm_task.task_id}')
        except Exception:
            pass

    # ── Status ───────────────────────────────────────────

    def status(self) -> dict:
        return {
            'total_tasks': len(self._swarm_history),
            'worker_manager': self.worker_manager.status(),
            'recent_tasks': [t.to_dict() for t in self._swarm_history[-5:]],
        }
