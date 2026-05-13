"""
Adaptive Executor -- Proposal Lifecycle Manager

Closes the loop: proposals go from PENDING -> APPROVED -> EXECUTING -> COMPLETED.

State Machine:
    PENDING --> APPROVED --> EXECUTING --> COMPLETED
       |           |           |
       v           v           v
    REJECTED    FAILED      FAILED

Usage:
    from packages.adaptive_system.adaptive_executor import ProposalExecutor
    executor = ProposalExecutor(proposals_dir)
    
    # Review pending
    pending = executor.list_pending()
    
    # Approve and execute
    executor.approve("decay_refresh_20260314.json", approved_by="gemini-cli")
    executor.execute("decay_refresh_20260314.json")
    
    # Or batch
    executor.auto_approve_and_execute()
    
    # Record outcome
    executor.record_outcome("decay_refresh_20260314.json", "effective")
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------
# Proposal States
# ---------------------------------------------------------------

class ProposalState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class ProposalOutcome(Enum):
    EFFECTIVE = "effective"         # Fixed the issue
    NOISE = "noise"                 # Correct but unnecessary
    FALSE_POSITIVE = "false_positive"  # Signal was wrong
    REJECTED = "rejected"           # Human rejected
    UNKNOWN = "unknown"             # Not yet evaluated


# ---------------------------------------------------------------
# Enhanced Proposal
# ---------------------------------------------------------------

@dataclass
class Proposal:
    """Full lifecycle proposal with state tracking."""
    # Identity
    proposal_id: str               # Filename stem
    response_type: str             # e.g., "decay_refresh", "test_unit"
    description: str
    
    # Origin
    system_name: str = ""          # Which adaptive system generated it
    signal_data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    # Approval
    state: str = "pending"
    required_approval: str = "auto"
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Execution
    execution_command: Optional[str] = None
    target_path: Optional[str] = None
    content: Any = None            # Generated content (test stubs, docs, etc.)
    executed_at: Optional[str] = None
    execution_output: Optional[str] = None
    execution_duration: float = 0.0
    
    # Feedback
    outcome: str = "unknown"
    outcome_score: float = 0.0     # 0-1 quality
    outcome_notes: str = ""
    outcome_recorded_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Proposal':
        # Filter to known fields only
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)
    
    @classmethod
    def from_file(cls, path: Path) -> 'Proposal':
        """Load a proposal from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("proposal_id", path.stem)
        return cls.from_dict(data)
    
    def save(self, path: Path):
        """Save proposal to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )


# ---------------------------------------------------------------
# Proposal Executor
# ---------------------------------------------------------------

class ProposalExecutor:
    """
    Manages the full proposal lifecycle.
    
    Directory layout:
        proposals/
            pending/      <- new proposals land here
            approved/     <- approved, awaiting execution
            completed/    <- successfully executed
            failed/       <- execution failed
            rejected/     <- human rejected
    """
    
    SUBDIRS = ["pending", "approved", "completed", "failed", "rejected"]
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        for subdir in self.SUBDIRS:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def _dir(self, state: str) -> Path:
        return self.base_dir / state
    
    def _move(self, proposal: Proposal, from_state: str, to_state: str) -> Path:
        """Move a proposal file between state directories."""
        src = self._dir(from_state) / f"{proposal.proposal_id}.json"
        dst = self._dir(to_state) / f"{proposal.proposal_id}.json"
        proposal.state = to_state
        proposal.save(dst)
        if src.exists() and src != dst:
            src.unlink()
        return dst
    
    # ── Ingestion ──
    
    def ingest_legacy_proposals(self) -> int:
        """
        Migrate legacy flat proposals (from v3.0) into the pending/ directory.
        Legacy format: {response_type, description, target_path, required_approval, created_at}
        """
        legacy_dir = self.base_dir
        count = 0
        for f in legacy_dir.glob("*.json"):
            if f.parent.name in self.SUBDIRS:
                continue  # Already in a state dir
            
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            
            proposal = Proposal(
                proposal_id=f.stem,
                response_type=data.get("response_type", "unknown"),
                description=data.get("description", f.stem),
                required_approval=data.get("required_approval", "auto"),
                created_at=data.get("created_at", ""),
                target_path=data.get("target_path"),
                state="pending",
            )
            
            proposal.save(self._dir("pending") / f"{proposal.proposal_id}.json")
            f.unlink()
            count += 1
        
        return count
    
    # ── Queries ──
    
    def list_proposals(self, state: Optional[str] = None) -> List[Proposal]:
        """List proposals, optionally filtered by state."""
        results = []
        states = [state] if state else self.SUBDIRS
        for s in states:
            d = self._dir(s)
            for f in sorted(d.glob("*.json")):
                try:
                    results.append(Proposal.from_file(f))
                except (json.JSONDecodeError, OSError):
                    pass
        return results
    
    def list_pending(self) -> List[Proposal]:
        return self.list_proposals("pending")
    
    def list_approved(self) -> List[Proposal]:
        return self.list_proposals("approved")
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Find a proposal by ID across all states."""
        for s in self.SUBDIRS:
            path = self._dir(s) / f"{proposal_id}.json"
            if path.exists():
                return Proposal.from_file(path)
        return None
    
    def get_state(self, proposal_id: str) -> Optional[str]:
        """Get the current state of a proposal."""
        for s in self.SUBDIRS:
            if (self._dir(s) / f"{proposal_id}.json").exists():
                return s
        return None
    
    # ── State Transitions ──
    
    def approve(self, proposal_id: str, approved_by: str = "auto") -> Proposal:
        """Move proposal from pending -> approved."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        current_state = self.get_state(proposal_id)
        if current_state != "pending":
            raise ValueError(f"Cannot approve: proposal is '{current_state}', not 'pending'")
        
        proposal.approved_by = approved_by
        proposal.approved_at = datetime.now().isoformat()
        self._move(proposal, "pending", "approved")
        return proposal
    
    def reject(self, proposal_id: str, reason: str = "", rejected_by: str = "human") -> Proposal:
        """Move proposal from pending -> rejected."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        current_state = self.get_state(proposal_id)
        if current_state not in ("pending", "approved"):
            raise ValueError(f"Cannot reject: proposal is '{current_state}'")
        
        proposal.rejection_reason = reason or f"Rejected by {rejected_by}"
        proposal.outcome = "rejected"
        self._move(proposal, current_state, "rejected")
        return proposal
    
    def execute(self, proposal_id: str) -> Proposal:
        """Execute an approved proposal."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        current_state = self.get_state(proposal_id)
        if current_state != "approved":
            raise ValueError(f"Cannot execute: proposal is '{current_state}', not 'approved'")
        
        # Move to executing
        proposal.state = "executing"
        proposal.executed_at = datetime.now().isoformat()
        
        start = time.time()
        try:
            result = self._run_proposal(proposal)
            proposal.execution_duration = time.time() - start
            proposal.execution_output = result.get("output", "")[:2000]
            
            if result.get("success"):
                self._move(proposal, "approved", "completed")
            else:
                proposal.execution_output = result.get("error", "Unknown error")
                self._move(proposal, "approved", "failed")
        except Exception as e:
            proposal.execution_duration = time.time() - start
            proposal.execution_output = str(e)
            self._move(proposal, "approved", "failed")
        
        return proposal
    
    def _run_proposal(self, proposal: Proposal) -> dict:
        """Execute the actual work for a proposal."""
        cmd = proposal.execution_command
        
        if not cmd:
            # Generate command from response_type
            cmd = self._generate_command(proposal)
        
        if not cmd:
            return {
                "success": True,
                "output": f"Proposal '{proposal.response_type}' recorded (no executable command)",
            }
        
        # Execute via subprocess
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(Path.cwd()),
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout[:2000],
                "error": result.stderr[:1000] if result.returncode != 0 else "",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout (300s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_command(self, proposal: Proposal) -> Optional[str]:
        """Generate an execution command from the proposal type."""
        rt = proposal.response_type
        desc = proposal.description
        
        # Map response types to genome_assembler spawn commands
        SPAWN_MAP = {
            "decay_refresh": ("agent-knowledge-auditor", "Refresh stale KI"),
            "decay_rebuild": ("agent-knowledge-auditor", "Full KI rebuild"),
            "test_full_suite": ("agent-qa-lead", "Generate full test suite"),
            "test_unit": ("agent-unit-test", "Generate unit tests"),
            "drift_refactor": ("codex", "Refactor architectural violation"),
            "security_endpoint_scan": ("agent-security", "Endpoint security scan"),
            "security_full_audit": ("agent-security", "Full security audit"),
            "security_dep_audit": ("agent-security", "Dependency audit"),
            "doc_enrich": ("agent-docs", "Enrich documentation"),
            "research_depth_T3": ("agent-research-strategist", "Deep research"),
            "research_depth_T4": ("agent-research-strategist", "Full deep research protocol"),
        }
        
        if rt in SPAWN_MAP:
            agent, base_task = SPAWN_MAP[rt]
            task = f"{base_task}: {desc}"
            return (
                f"python scripts/ai_engine/genome_assembler.py spawn {agent} "
                f"--task \"{task}\""
            )
        
        return None
    
    # ── Batch Operations ──
    
    def auto_approve_all(self) -> List[Proposal]:
        """Approve all pending proposals that are AUTO level."""
        approved = []
        for p in self.list_pending():
            if p.required_approval == "auto":
                self.approve(p.proposal_id, approved_by="auto")
                approved.append(p)
        return approved
    
    def execute_all_approved(self) -> List[Proposal]:
        """Execute all approved proposals."""
        executed = []
        for p in self.list_approved():
            result = self.execute(p.proposal_id)
            executed.append(result)
        return executed
    
    def auto_approve_and_execute(self) -> Tuple[int, int, int]:
        """Auto-approve AUTO-level proposals and execute them.
        
        Returns:
            (approved_count, executed_count, failed_count)
        """
        approved = self.auto_approve_all()
        executed = 0
        failed = 0
        
        for p in approved:
            result = self.execute(p.proposal_id)
            if result.state == "completed":
                executed += 1
            else:
                failed += 1
        
        return len(approved), executed, failed
    
    # ── Feedback ──
    
    def record_outcome(
        self, 
        proposal_id: str, 
        outcome: str,
        score: float = 0.0,
        notes: str = "",
    ) -> Proposal:
        """Record the outcome of an executed proposal."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        proposal.outcome = outcome
        proposal.outcome_score = score
        proposal.outcome_notes = notes
        proposal.outcome_recorded_at = datetime.now().isoformat()
        
        # Save in place
        current_state = self.get_state(proposal_id)
        path = self._dir(current_state) / f"{proposal_id}.json"
        proposal.save(path)
        
        return proposal
    
    # ── Stats ──
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proposal lifecycle statistics."""
        stats = {}
        for state in self.SUBDIRS:
            proposals = self.list_proposals(state)
            stats[state] = len(proposals)
        
        # Outcome breakdown for completed
        completed = self.list_proposals("completed")
        outcomes = {}
        for p in completed:
            outcomes[p.outcome] = outcomes.get(p.outcome, 0) + 1
        stats["outcomes"] = outcomes
        
        # Effectiveness rate
        total_evaluated = sum(1 for p in completed if p.outcome != "unknown")
        effective = sum(1 for p in completed if p.outcome == "effective")
        stats["effectiveness_rate"] = effective / max(1, total_evaluated)
        
        return stats
