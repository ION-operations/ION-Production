"""
AIM-OS AI Engine — Swarm Contracts

The data contracts that define communication between the Orchestrator
and Worker agents in the Gemini CLI swarm.

Design by Sev (GPT-5.2 Thinking):
    "Workers get a JobPacket, return a ResultPacket. Always."

JobPacket: Everything a worker needs to execute its task.
ResultPacket: Everything the orchestrator needs to merge results.

These are IMMUTABLE contracts — workers cannot modify their own
JobPacket, and the orchestrator validates every ResultPacket.
"""

import time
import uuid
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum


# ── Enums ─────────────────────────────────────────────────

class WorkerRole(str, Enum):
    """Worker specialisation roles."""
    CODER = 'coder'
    ARCHITECT = 'architect'
    AUDITOR = 'auditor'
    RESEARCHER = 'researcher'
    INDEXER = 'indexer'
    TESTER = 'tester'


class JobStatus(str, Enum):
    """Lifecycle states for a job."""
    CREATED = 'created'
    ASSIGNED = 'assigned'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    TIMEOUT = 'timeout'
    CANCELLED = 'cancelled'
    QUARANTINED = 'quarantined'


class JobPriority(str, Enum):
    CRITICAL = 'critical'
    HIGH = 'high'
    STANDARD = 'standard'
    LOW = 'low'


class RiskLevel(str, Enum):
    NONE = 'none'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


# ── Capability Tokens ────────────────────────────────────

class CapabilityToken(str, Enum):
    """
    Capability-based security tokens (Sev's design).
    Permissions enforced at MCP layer, not just in prompts.
    """
    FILE_READ = 'file:read'
    FILE_WRITE = 'file:write'
    FILE_CREATE = 'file:create'
    FILE_DELETE = 'file:delete'
    COMMAND_RUN = 'command:run'
    COMMAND_DANGEROUS = 'command:dangerous'
    MCP_READ = 'mcp:read'
    MCP_WRITE = 'mcp:write'
    MCP_MUTATE_ORCHESTRATION = 'mcp:mutate_orchestration'  # RED ZONE
    MEMORY_READ = 'memory:read'
    MEMORY_WRITE = 'memory:write'
    MEMORY_DELETE = 'memory:delete'                        # RED ZONE
    COMMS_SEND = 'comms:send'
    COMMS_BROADCAST = 'comms:broadcast'
    LLM_CALL = 'llm:call'
    LLM_DEEP_THINK = 'llm:deep_think'
    HUMAN_ESCALATE = 'human:escalate'


# Red zone: these capabilities require explicit human approval
RED_ZONE_CAPABILITIES: Set[CapabilityToken] = {
    CapabilityToken.MCP_MUTATE_ORCHESTRATION,
    CapabilityToken.MEMORY_DELETE,
    CapabilityToken.FILE_DELETE,
    CapabilityToken.COMMAND_DANGEROUS,
}

# Default capability sets per role
ROLE_CAPABILITIES: Dict[WorkerRole, Set[CapabilityToken]] = {
    WorkerRole.CODER: {
        CapabilityToken.FILE_READ, CapabilityToken.FILE_WRITE,
        CapabilityToken.FILE_CREATE, CapabilityToken.COMMAND_RUN,
        CapabilityToken.MCP_READ, CapabilityToken.MEMORY_READ,
        CapabilityToken.COMMS_SEND, CapabilityToken.LLM_CALL,
    },
    WorkerRole.ARCHITECT: {
        CapabilityToken.FILE_READ, CapabilityToken.MCP_READ,
        CapabilityToken.MEMORY_READ, CapabilityToken.MEMORY_WRITE,
        CapabilityToken.COMMS_SEND, CapabilityToken.LLM_CALL,
        CapabilityToken.LLM_DEEP_THINK,
    },
    WorkerRole.AUDITOR: {
        CapabilityToken.FILE_READ, CapabilityToken.COMMAND_RUN,
        CapabilityToken.MCP_READ, CapabilityToken.MEMORY_READ,
        CapabilityToken.MEMORY_WRITE, CapabilityToken.COMMS_SEND,
        CapabilityToken.LLM_CALL,
    },
    WorkerRole.RESEARCHER: {
        CapabilityToken.FILE_READ, CapabilityToken.MCP_READ,
        CapabilityToken.MEMORY_READ, CapabilityToken.MEMORY_WRITE,
        CapabilityToken.COMMS_SEND, CapabilityToken.LLM_CALL,
        CapabilityToken.LLM_DEEP_THINK,
    },
    WorkerRole.INDEXER: {
        CapabilityToken.FILE_READ, CapabilityToken.MEMORY_READ,
        CapabilityToken.MEMORY_WRITE, CapabilityToken.LLM_CALL,
    },
    WorkerRole.TESTER: {
        CapabilityToken.FILE_READ, CapabilityToken.COMMAND_RUN,
        CapabilityToken.MCP_READ, CapabilityToken.COMMS_SEND,
        CapabilityToken.LLM_CALL,
    },
}


# ── Output Contract ──────────────────────────────────────

@dataclass
class OutputContract:
    """
    Defines what the worker MUST return.
    Enforced by the orchestrator during ResultPacket validation.
    """
    required_fields: List[str] = field(default_factory=lambda: [
        'summary', 'confidence',
    ])
    expected_artifacts: List[str] = field(default_factory=list)  # e.g., ['modified_file', 'test_results']
    max_output_tokens: int = 8000
    require_citations: bool = True
    require_confidence: bool = True
    require_risks: bool = False


# ── JobPacket ────────────────────────────────────────────

@dataclass
class JobPacket:
    """
    Everything a worker needs to execute its task.
    Immutable once created — workers cannot modify their own packet.
    
    Designed by Sev:
    "Workers get a JobPacket {job_id, role, allowed_tools,
     allowed_paths, forbidden_paths, max_tokens/budget,
     context_pack_ref, output_contract}."
    """
    # Identity
    job_id: str = field(default_factory=lambda: f'job_{uuid.uuid4().hex[:12]}')
    parent_job_id: str = ''          # If this is a sub-task
    instance_id: str = field(default_factory=lambda: f'inst_{uuid.uuid4().hex[:8]}')
    holder_id: str = ''              # Identity lock for MCP comms

    # Role & Task
    role: str = WorkerRole.CODER
    task_description: str = ''
    task_type: str = 'standard'      # Maps to model routing

    # Genome overlay
    genome_base: str = ''            # Base genome content
    role_overlay: str = ''           # Role-specific system prompt overlay
    task_overlay: str = ''           # Task-specific constraints/focus

    # Capabilities (enforced at MCP layer)
    capabilities: List[str] = field(default_factory=list)
    allowed_tools: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=list)
    forbidden_paths: List[str] = field(default_factory=list)

    # Budget
    max_tokens: int = 32000
    max_steps: int = 15
    ttl_seconds: int = 300           # Time-to-live
    heartbeat_interval: int = 30     # Seconds between heartbeats

    # Context
    context_pack_ref: str = ''       # Reference to ContextPack
    context_inline: str = ''         # Inline context (for small jobs)
    include_files: List[str] = field(default_factory=list)

    # Output expectations
    output_contract: Optional[OutputContract] = None
    priority: str = JobPriority.STANDARD

    # Metadata
    created_at: float = field(default_factory=time.time)
    created_by: str = 'orchestrator'
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d['output_contract'] = asdict(self.output_contract) if self.output_contract else None
        return d

    def to_system_prompt(self) -> str:
        """Assemble the full system prompt from genome layers."""
        parts = []
        if self.genome_base:
            parts.append(self.genome_base)
        if self.role_overlay:
            parts.append(f"\n## Role Override\n{self.role_overlay}")
        if self.task_overlay:
            parts.append(f"\n## Task Scope\n{self.task_overlay}")

        # Capability statement
        cap_list = ', '.join(self.capabilities) if self.capabilities else 'standard'
        parts.append(f"\n## Capabilities\nYou have: {cap_list}")

        # Path constraints
        if self.allowed_paths:
            parts.append(f"\n## Allowed Paths\n" + '\n'.join(f'- `{p}`' for p in self.allowed_paths))
        if self.forbidden_paths:
            parts.append(f"\n## FORBIDDEN Paths (DO NOT ACCESS)\n" + '\n'.join(f'- `{p}`' for p in self.forbidden_paths))

        # Output contract
        if self.output_contract:
            parts.append(
                f"\n## Output Requirements\n"
                f"Required fields: {', '.join(self.output_contract.required_fields)}\n"
                f"Max output: {self.output_contract.max_output_tokens} tokens\n"
                f"Citations required: {self.output_contract.require_citations}"
            )

        return '\n'.join(parts)


# ── ResultPacket ─────────────────────────────────────────

@dataclass
class ResultPacket:
    """
    Everything the orchestrator needs to merge results.
    Returned by every worker upon completion.
    
    Designed by Sev:
    "Workers return a ResultPacket {job_id, artifacts,
     citations(paths), confidence, risks, next_actions, logs_ref}."
    """
    # Identity
    job_id: str = ''
    instance_id: str = ''

    # Status
    status: str = JobStatus.COMPLETED
    exit_code: int = 0

    # Core output
    summary: str = ''               # Natural language summary of work done
    content: str = ''               # Full response content

    # Artifacts
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    # Each artifact: {'type': 'file_edit'|'analysis'|'plan', 'path': ..., 'content': ...}

    # Provenance
    citations: List[str] = field(default_factory=list)   # File paths referenced
    evidence: List[str] = field(default_factory=list)     # Evidence for claims

    # Quality
    confidence: float = 0.0
    risks: List[Dict[str, str]] = field(default_factory=list)
    # Each risk: {'level': 'low'|'medium'|'high', 'description': ...}

    # Next steps
    next_actions: List[str] = field(default_factory=list)
    requires_human: bool = False
    escalation_reason: str = ''

    # Metrics
    tokens_used: int = 0
    latency_ms: float = 0.0
    steps_executed: int = 0
    model_used: str = ''

    # Trace
    logs_ref: str = ''               # Reference to full logs in CMC
    error: str = ''

    # Metadata
    completed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def succeeded(self) -> bool:
        return self.status == JobStatus.COMPLETED and self.exit_code == 0

    def validate_against_contract(self, contract: OutputContract) -> List[str]:
        """Validate this result against the job's output contract."""
        violations = []

        if contract.require_confidence and self.confidence <= 0:
            violations.append('Missing confidence score')

        if contract.require_citations and not self.citations:
            violations.append('Missing citations (file references)')

        for req_field in contract.required_fields:
            if not getattr(self, req_field, None):
                violations.append(f'Missing required field: {req_field}')

        for expected in contract.expected_artifacts:
            found = any(a.get('type') == expected for a in self.artifacts)
            if not found:
                violations.append(f'Missing expected artifact: {expected}')

        return violations


# ── Swarm Task ───────────────────────────────────────────

@dataclass
class SwarmTask:
    """
    A high-level task that gets decomposed into JobPackets.
    Tracks the overall swarm execution.
    """
    task_id: str = field(default_factory=lambda: f'swarm_{uuid.uuid4().hex[:12]}')
    description: str = ''
    jobs: List[JobPacket] = field(default_factory=list)
    results: Dict[str, ResultPacket] = field(default_factory=dict)  # job_id -> result
    status: str = JobStatus.CREATED
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    merged_output: str = ''

    @property
    def all_completed(self) -> bool:
        return all(
            job.job_id in self.results
            for job in self.jobs
        )

    @property
    def any_failed(self) -> bool:
        return any(
            not r.succeeded for r in self.results.values()
        )

    def to_dict(self) -> dict:
        return {
            'task_id': self.task_id,
            'description': self.description[:200],
            'status': self.status,
            'total_jobs': len(self.jobs),
            'completed_jobs': len(self.results),
            'failed_jobs': sum(1 for r in self.results.values() if not r.succeeded),
            'created_at': self.created_at,
            'completed_at': self.completed_at,
        }
