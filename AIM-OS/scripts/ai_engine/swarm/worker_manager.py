"""
AIM-OS AI Engine — Worker Manager

Manages Gemini CLI worker process lifecycle.
Design by Sev: "Ephemeral workers with strict TTL + heartbeat."

Responsibilities:
    - Spawn Gemini CLI subprocesses with JobPacket parameters
    - Monitor heartbeat (worker liveness)
    - Enforce TTL (kill workers that exceed time budget)
    - Collect ResultPackets from stdout (JSON)
    - Handle failure: timeout → retry, repeated failure → quarantine
    - Track all workers in a registry for orchestrator access
"""

import os
import time
import json
import asyncio
import logging
import subprocess
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ai_engine.swarm.contracts import (
    JobPacket, ResultPacket, JobStatus, WorkerRole,
    CapabilityToken, RED_ZONE_CAPABILITIES,
)

logger = logging.getLogger('ai_engine.worker_manager')


# ── Worker Process State ──────────────────────────────────

@dataclass
class WorkerProcess:
    """Tracks a single Gemini CLI worker process."""
    job: JobPacket
    process: Optional[subprocess.Popen] = None
    async_process: Optional[asyncio.subprocess.Process] = None
    pid: int = 0
    status: str = JobStatus.CREATED
    started_at: float = 0.0
    last_heartbeat: float = 0.0
    retry_count: int = 0
    max_retries: int = 2
    stdout_buffer: str = ''
    stderr_buffer: str = ''

    @property
    def elapsed_seconds(self) -> float:
        if self.started_at == 0:
            return 0
        return time.time() - self.started_at

    @property
    def is_expired(self) -> bool:
        return self.elapsed_seconds > self.job.ttl_seconds

    @property
    def heartbeat_stale(self) -> bool:
        if self.last_heartbeat == 0:
            return self.elapsed_seconds > self.job.heartbeat_interval * 2
        return (time.time() - self.last_heartbeat) > self.job.heartbeat_interval * 3


# ── Worker Manager ────────────────────────────────────────

class WorkerManager:
    """
    Manages the lifecycle of Gemini CLI worker processes.
    
    The orchestrator calls:
        worker = manager.spawn(job_packet)
        result = manager.collect(worker)
        
    The manager handles:
        - Building CLI commands from JobPackets
        - Subprocess creation and monitoring
        - TTL enforcement (auto-kill expired workers)
        - Heartbeat tracking
        - Retry logic on failure
        - ResultPacket parsing from stdout
    """

    def __init__(
        self,
        gemini_cli_path: str = 'gemini',
        working_directory: str = '',
        max_concurrent_workers: int = 5,
        sandbox_policy: str = 'allow-read-write',
    ):
        self.cli_path = gemini_cli_path
        self.working_directory = working_directory or os.getcwd()
        self.max_concurrent = max_concurrent_workers
        self.sandbox_policy = sandbox_policy

        # Worker registry
        self._workers: Dict[str, WorkerProcess] = {}
        self._quarantine: Dict[str, int] = {}  # job_id -> failure count
        self._history: List[Dict] = []

    # ── Spawn ────────────────────────────────────────────

    def spawn(self, job: JobPacket) -> WorkerProcess:
        """
        Spawn a new Gemini CLI worker process for a job.
        
        Validates capabilities, builds the CLI command, and
        starts the subprocess. Returns the WorkerProcess handle.
        """
        # Check concurrency limit
        active = sum(1 for w in self._workers.values() if w.status == JobStatus.RUNNING)
        if active >= self.max_concurrent:
            raise RuntimeError(
                f'Max concurrent workers ({self.max_concurrent}) reached. '
                f'Wait for a worker to complete.'
            )

        # Check quarantine
        if self._quarantine.get(job.job_id, 0) >= 3:
            raise RuntimeError(f'Job {job.job_id} is quarantined (3+ failures)')

        # Validate no RED ZONE capabilities without human approval
        for cap in job.capabilities:
            try:
                cap_token = CapabilityToken(cap)
                if cap_token in RED_ZONE_CAPABILITIES:
                    raise PermissionError(
                        f'RED ZONE capability "{cap}" requires explicit human approval. '
                        f'Use two-phase commit via safety/vif_gates.'
                    )
            except ValueError:
                pass

        # Build CLI command
        cmd = self._build_worker_command(job)

        # Start subprocess
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                cwd=self.working_directory,
            )

            worker = WorkerProcess(
                job=job,
                process=process,
                pid=process.pid,
                status=JobStatus.RUNNING,
                started_at=time.time(),
                last_heartbeat=time.time(),
            )

            self._workers[job.job_id] = worker

            logger.info(
                f'[WorkerManager] Spawned worker {job.job_id} '
                f'(role={job.role}, pid={process.pid}, ttl={job.ttl_seconds}s)'
            )

            return worker

        except FileNotFoundError:
            raise RuntimeError(
                f'Gemini CLI not found at "{self.cli_path}". '
                f'Install: npm install -g @google/gemini-cli'
            )
        except Exception as e:
            logger.error(f'Failed to spawn worker: {e}')
            raise

    # ── Collect ──────────────────────────────────────────

    def collect(
        self,
        worker: WorkerProcess,
        timeout: Optional[int] = None,
    ) -> ResultPacket:
        """
        Wait for a worker to complete and return its ResultPacket.
        Enforces TTL. Parses JSON output from stdout.
        """
        timeout = timeout or worker.job.ttl_seconds

        try:
            stdout, stderr = worker.process.communicate(timeout=timeout)
            exit_code = worker.process.returncode

            worker.stdout_buffer = stdout
            worker.stderr_buffer = stderr

            elapsed = (time.time() - worker.started_at) * 1000

            if exit_code == 0:
                # Parse ResultPacket from stdout JSON
                result = self._parse_result(stdout, worker.job)
                result.latency_ms = elapsed
                result.exit_code = exit_code
                worker.status = JobStatus.COMPLETED

                logger.info(
                    f'[WorkerManager] Worker {worker.job.job_id} completed '
                    f'({elapsed:.0f}ms, confidence={result.confidence:.2f})'
                )
            else:
                result = ResultPacket(
                    job_id=worker.job.job_id,
                    instance_id=worker.job.instance_id,
                    status=JobStatus.FAILED,
                    exit_code=exit_code,
                    error=stderr[:2000] if stderr else f'Exit code {exit_code}',
                    latency_ms=elapsed,
                )
                worker.status = JobStatus.FAILED
                self._quarantine[worker.job.job_id] = self._quarantine.get(worker.job.job_id, 0) + 1

                logger.warning(
                    f'[WorkerManager] Worker {worker.job.job_id} failed '
                    f'(exit={exit_code}, quarantine={self._quarantine.get(worker.job.job_id, 0)})'
                )

            # Store in history
            self._history.append({
                'job_id': worker.job.job_id,
                'role': worker.job.role,
                'status': worker.status,
                'elapsed_ms': elapsed,
                'exit_code': exit_code,
            })

            return result

        except subprocess.TimeoutExpired:
            # TTL exceeded — kill the worker
            worker.process.kill()
            worker.process.wait(timeout=5)
            worker.status = JobStatus.TIMEOUT

            self._quarantine[worker.job.job_id] = self._quarantine.get(worker.job.job_id, 0) + 1

            logger.warning(
                f'[WorkerManager] Worker {worker.job.job_id} TIMED OUT '
                f'after {timeout}s — killed (pid={worker.pid})'
            )

            return ResultPacket(
                job_id=worker.job.job_id,
                instance_id=worker.job.instance_id,
                status=JobStatus.TIMEOUT,
                error=f'Worker timed out after {timeout}s (TTL exceeded)',
                latency_ms=timeout * 1000,
            )

    # ── Async Spawn/Collect ──────────────────────────────

    async def spawn_async(self, job: JobPacket) -> WorkerProcess:
        """Async version of spawn using asyncio subprocess."""
        active = sum(1 for w in self._workers.values() if w.status == JobStatus.RUNNING)
        if active >= self.max_concurrent:
            raise RuntimeError(f'Max concurrent workers ({self.max_concurrent}) reached')

        cmd = self._build_worker_command(job)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_directory,
        )

        worker = WorkerProcess(
            job=job,
            async_process=process,
            pid=process.pid,
            status=JobStatus.RUNNING,
            started_at=time.time(),
            last_heartbeat=time.time(),
        )

        self._workers[job.job_id] = worker
        return worker

    async def collect_async(
        self,
        worker: WorkerProcess,
        timeout: Optional[int] = None,
    ) -> ResultPacket:
        """Async version of collect."""
        timeout = timeout or worker.job.ttl_seconds

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                worker.async_process.communicate(),
                timeout=timeout,
            )

            stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ''
            stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ''
            exit_code = worker.async_process.returncode
            elapsed = (time.time() - worker.started_at) * 1000

            if exit_code == 0:
                result = self._parse_result(stdout, worker.job)
                result.latency_ms = elapsed
                worker.status = JobStatus.COMPLETED
            else:
                result = ResultPacket(
                    job_id=worker.job.job_id,
                    instance_id=worker.job.instance_id,
                    status=JobStatus.FAILED,
                    exit_code=exit_code,
                    error=stderr[:2000],
                    latency_ms=elapsed,
                )
                worker.status = JobStatus.FAILED

            return result

        except asyncio.TimeoutError:
            worker.async_process.kill()
            worker.status = JobStatus.TIMEOUT
            return ResultPacket(
                job_id=worker.job.job_id,
                instance_id=worker.job.instance_id,
                status=JobStatus.TIMEOUT,
                error=f'Worker timed out after {timeout}s',
                latency_ms=timeout * 1000,
            )

    # ── Management ───────────────────────────────────────

    def kill_worker(self, job_id: str):
        """Force-kill a worker process (poison pill)."""
        worker = self._workers.get(job_id)
        if worker:
            if worker.process and worker.process.poll() is None:
                worker.process.kill()
            if worker.async_process and worker.async_process.returncode is None:
                worker.async_process.kill()
            worker.status = JobStatus.CANCELLED
            logger.info(f'[WorkerManager] Killed worker {job_id}')

    def kill_all(self):
        """Kill all running workers."""
        for job_id, worker in self._workers.items():
            if worker.status == JobStatus.RUNNING:
                self.kill_worker(job_id)

    def check_health(self) -> Dict[str, Any]:
        """Check health of all workers. Kill expired ones."""
        expired = []
        stale = []
        active = []

        for job_id, worker in self._workers.items():
            if worker.status != JobStatus.RUNNING:
                continue

            if worker.is_expired:
                expired.append(job_id)
                self.kill_worker(job_id)
                worker.status = JobStatus.TIMEOUT
            elif worker.heartbeat_stale:
                stale.append(job_id)
            else:
                active.append(job_id)

        return {
            'active': len(active),
            'expired_killed': len(expired),
            'stale_heartbeat': len(stale),
            'total_registered': len(self._workers),
            'quarantined': dict(self._quarantine),
        }

    def status(self) -> dict:
        """Full manager status."""
        return {
            'cli_path': self.cli_path,
            'max_concurrent': self.max_concurrent,
            'active_workers': sum(1 for w in self._workers.values() if w.status == JobStatus.RUNNING),
            'total_spawned': len(self._history),
            'quarantine': dict(self._quarantine),
            'recent_history': self._history[-10:],
        }

    # ── Internal ─────────────────────────────────────────

    def _build_worker_command(self, job: JobPacket) -> List[str]:
        """Build the Gemini CLI command for a worker."""
        # Assemble the full prompt: system (from genome layers) + task + output instructions
        system_prompt = job.to_system_prompt()

        # Build the task prompt with output format requirements
        task_prompt = f"""{system_prompt}

---

## Task
{job.task_description}

## Required Output Format
Respond with ONLY a valid JSON object containing:
{{
    "summary": "What you did and found",
    "content": "Your full response",
    "artifacts": [{{"type": "analysis|file_edit|plan", "path": "...", "content": "..."}}],
    "citations": ["file/paths/referenced"],
    "evidence": ["evidence for claims"],
    "confidence": 0.0-1.0,
    "risks": [{{"level": "low|medium|high", "description": "..."}}],
    "next_actions": ["suggested follow-ups"],
    "requires_human": false,
    "escalation_reason": ""
}}
"""

        # Add inline context if provided
        if job.context_inline:
            task_prompt += f"\n## Context\n{job.context_inline}\n"

        cmd = [self.cli_path, '-p', task_prompt, '--output-format', 'json']

        # Sandbox
        cmd.extend(['--sandbox', self.sandbox_policy])

        # Include directories
        for path in job.allowed_paths:
            if os.path.isdir(path):
                cmd.extend(['--include-directories', path])

        return cmd

    def _parse_result(self, stdout: str, job: JobPacket) -> ResultPacket:
        """Parse a ResultPacket from worker stdout."""
        result = ResultPacket(
            job_id=job.job_id,
            instance_id=job.instance_id,
        )

        if not stdout.strip():
            result.status = JobStatus.FAILED
            result.error = 'Empty output from worker'
            return result

        # Try to parse JSON
        try:
            data = json.loads(stdout.strip())
        except json.JSONDecodeError:
            # Try extracting JSON from text
            import re
            json_match = re.search(r'\{[\s\S]*\}', stdout)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}

        if not data:
            # Fallback: treat raw output as content
            result.content = stdout.strip()
            result.summary = stdout.strip()[:200]
            result.confidence = 0.3  # Low confidence for unparsed output
            result.status = JobStatus.COMPLETED
            return result

        # Map JSON fields to ResultPacket
        # Handle Gemini CLI JSON wrapper (may nest under 'response')
        if 'response' in data and isinstance(data['response'], dict):
            data = data['response']

        result.summary = data.get('summary', '')
        result.content = data.get('content', data.get('text', ''))
        result.artifacts = data.get('artifacts', [])
        result.citations = data.get('citations', [])
        result.evidence = data.get('evidence', [])
        result.confidence = float(data.get('confidence', 0.5))
        result.risks = data.get('risks', [])
        result.next_actions = data.get('next_actions', [])
        result.requires_human = data.get('requires_human', False)
        result.escalation_reason = data.get('escalation_reason', '')
        result.status = JobStatus.COMPLETED

        # Validate against output contract
        if job.output_contract:
            violations = result.validate_against_contract(job.output_contract)
            if violations:
                logger.warning(
                    f'Worker {job.job_id} output contract violations: {violations}'
                )

        return result
