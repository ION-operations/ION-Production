"""
AIM-OS AI Engine — VIF Safety Gates

Implements Sev's safety framework:
    - Confidence gates: block execution below threshold
    - Red zone gating: require human approval for dangerous actions
    - Two-phase commit: propose → verify → apply
    - Escalation protocol: notify human when uncertain

Integrates with VIF (Verifiable Intelligence Framework) via MCP.
"""

import time
import logging
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger('ai_engine.vif_gates')


# ── Gate Types ────────────────────────────────────────────

class GateVerdict(str, Enum):
    PASS = 'pass'
    BLOCK = 'block'
    ESCALATE = 'escalate'
    REVIEW = 'review'


@dataclass
class GateResult:
    """Result of a VIF gate check."""
    verdict: str = GateVerdict.PASS
    reason: str = ''
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    requires_human: bool = False
    escalation_reason: str = ''

    @property
    def passed(self) -> bool:
        return self.verdict == GateVerdict.PASS


# ── Confidence Gate ──────────────────────────────────────

class ConfidenceGate:
    """
    Blocks execution when confidence is below threshold.
    
    Thresholds (Sev's design):
        - Standard actions: 0.3 minimum
        - File modifications: 0.5 minimum
        - Destructive actions: 0.7 minimum
        - System mutations: 0.9 minimum (+ human approval)
    """

    THRESHOLDS = {
        'read': 0.1,             # Almost always allowed
        'standard': 0.3,         # General actions
        'file_write': 0.5,       # File modifications
        'file_create': 0.4,      # New files
        'command': 0.5,          # Running commands
        'destructive': 0.7,      # Delete operations
        'system_mutate': 0.9,    # MCP/orchestration changes
    }

    def check(
        self,
        confidence: float,
        action_type: str = 'standard',
        evidence: Optional[List[str]] = None,
        override_threshold: Optional[float] = None,
    ) -> GateResult:
        """
        Check if confidence meets the threshold for an action.
        """
        threshold = override_threshold or self.THRESHOLDS.get(
            action_type, self.THRESHOLDS['standard']
        )

        if confidence >= threshold:
            return GateResult(
                verdict=GateVerdict.PASS,
                confidence=confidence,
                evidence=evidence or [],
                reason=f'Confidence {confidence:.2f} >= threshold {threshold:.2f}',
            )
        elif confidence >= threshold * 0.7:
            return GateResult(
                verdict=GateVerdict.REVIEW,
                confidence=confidence,
                evidence=evidence or [],
                reason=f'Confidence {confidence:.2f} near threshold {threshold:.2f} — review recommended',
                requires_human=False,
            )
        else:
            return GateResult(
                verdict=GateVerdict.BLOCK,
                confidence=confidence,
                evidence=evidence or [],
                reason=f'Confidence {confidence:.2f} < threshold {threshold:.2f} — BLOCKED',
                requires_human=action_type in ('destructive', 'system_mutate'),
                escalation_reason=f'Low confidence ({confidence:.2f}) for {action_type} action',
            )


# ── Red Zone Gate ────────────────────────────────────────

class RedZoneGate:
    """
    Blocks actions that require explicit human capability tokens.
    
    Red zone actions (Sev's design):
        - Mutating MCP/orchestration configuration
        - Deleting memory atoms
        - Deleting files
        - Running dangerous commands
    """

    RED_ZONE_ACTIONS = {
        'mcp:mutate_orchestration',
        'memory:delete',
        'file:delete',
        'command:dangerous',
    }

    def check(
        self,
        action: str,
        has_human_token: bool = False,
        evidence: Optional[List[str]] = None,
    ) -> GateResult:
        """Check if an action requires human approval."""
        if action not in self.RED_ZONE_ACTIONS:
            return GateResult(
                verdict=GateVerdict.PASS,
                reason=f'Action "{action}" is not in red zone',
                evidence=evidence or [],
            )

        if has_human_token:
            return GateResult(
                verdict=GateVerdict.PASS,
                reason=f'Red zone action "{action}" approved with human token',
                evidence=evidence or [],
            )

        return GateResult(
            verdict=GateVerdict.ESCALATE,
            reason=f'RED ZONE: "{action}" requires human approval',
            requires_human=True,
            escalation_reason=(
                f'Action "{action}" is in the RED ZONE. '
                f'This action requires explicit human approval before execution. '
                f'Evidence: {evidence or "none"}'
            ),
            evidence=evidence or [],
        )


# ── Two-Phase Commit Gate ────────────────────────────────

@dataclass
class ProposedAction:
    """An action in the propose phase of two-phase commit."""
    action_id: str
    action_type: str
    description: str
    target: str  # file path, memory atom, etc.
    content: str = ''  # proposed change content
    confidence: float = 0.0
    risks: List[str] = field(default_factory=list)
    proposed_at: float = field(default_factory=time.time)
    verified: bool = False
    approved: bool = False


class TwoPhaseCommitGate:
    """
    Implements propose → verify → apply pattern.
    
    Risky actions must be PROPOSED first, then VERIFIED
    (by auditor or human), then APPLIED.
    """

    def __init__(self):
        self._proposals: Dict[str, ProposedAction] = {}

    def propose(
        self,
        action_type: str,
        description: str,
        target: str,
        content: str = '',
        confidence: float = 0.0,
        risks: Optional[List[str]] = None,
    ) -> ProposedAction:
        """Phase 1: Propose an action for review."""
        import uuid
        action_id = f'action_{uuid.uuid4().hex[:8]}'

        proposal = ProposedAction(
            action_id=action_id,
            action_type=action_type,
            description=description,
            target=target,
            content=content,
            confidence=confidence,
            risks=risks or [],
        )

        self._proposals[action_id] = proposal

        logger.info(
            f'[2PC] Proposed: {action_type} on {target} '
            f'(confidence={confidence:.2f}, risks={len(risks or [])})'
        )

        return proposal

    def verify(
        self,
        action_id: str,
        approved: bool = True,
        reason: str = '',
    ) -> GateResult:
        """Phase 2: Verify (approve or reject) a proposed action."""
        proposal = self._proposals.get(action_id)
        if not proposal:
            return GateResult(
                verdict=GateVerdict.BLOCK,
                reason=f'Unknown action_id: {action_id}',
            )

        proposal.verified = True
        proposal.approved = approved

        if approved:
            return GateResult(
                verdict=GateVerdict.PASS,
                reason=f'Action {action_id} APPROVED: {reason}',
                confidence=proposal.confidence,
            )
        else:
            return GateResult(
                verdict=GateVerdict.BLOCK,
                reason=f'Action {action_id} REJECTED: {reason}',
                confidence=proposal.confidence,
            )

    def can_apply(self, action_id: str) -> bool:
        """Phase 3: Check if an action can be applied."""
        proposal = self._proposals.get(action_id)
        return proposal is not None and proposal.verified and proposal.approved

    def get_pending(self) -> List[ProposedAction]:
        """Get all proposals awaiting verification."""
        return [p for p in self._proposals.values() if not p.verified]


# ── Unified VIF Gate ─────────────────────────────────────

class VIFGate:
    """
    Unified safety gate combining all VIF checks.
    
    Usage:
        gate = VIFGate()
        result = gate.check(action='file:write', confidence=0.8)
        if result.passed:
            # proceed
        elif result.requires_human:
            # escalate
    """

    def __init__(self):
        self.confidence_gate = ConfidenceGate()
        self.red_zone_gate = RedZoneGate()
        self.two_phase_gate = TwoPhaseCommitGate()
        self._gate_log: List[Dict] = []

    def check(
        self,
        action: str,
        confidence: float = 0.5,
        evidence: Optional[List[str]] = None,
        has_human_token: bool = False,
    ) -> GateResult:
        """
        Run all safety gates on an action.
        Returns the most restrictive result.
        """
        evidence = evidence or []

        # Check red zone first (most restrictive)
        red_result = self.red_zone_gate.check(action, has_human_token, evidence)
        if not red_result.passed:
            self._log_gate('red_zone', action, red_result)
            return red_result

        # Then confidence gate
        # Map action to action_type for threshold lookup
        action_type = self._action_to_type(action)
        conf_result = self.confidence_gate.check(confidence, action_type, evidence)
        self._log_gate('confidence', action, conf_result)
        return conf_result

    def propose_risky_action(
        self,
        action_type: str,
        description: str,
        target: str,
        **kwargs,
    ) -> ProposedAction:
        """Propose a risky action for two-phase commit."""
        return self.two_phase_gate.propose(
            action_type=action_type,
            description=description,
            target=target,
            **kwargs,
        )

    def _action_to_type(self, action: str) -> str:
        """Map an action string to a threshold type."""
        mappings = {
            'file:read': 'read',
            'file:write': 'file_write',
            'file:create': 'file_create',
            'file:delete': 'destructive',
            'command:run': 'command',
            'command:dangerous': 'destructive',
            'memory:read': 'read',
            'memory:write': 'standard',
            'memory:delete': 'destructive',
            'mcp:read': 'read',
            'mcp:write': 'standard',
            'mcp:mutate_orchestration': 'system_mutate',
        }
        return mappings.get(action, 'standard')

    def _log_gate(self, gate_name: str, action: str, result: GateResult):
        """Log a gate check for audit trail."""
        self._gate_log.append({
            'gate': gate_name,
            'action': action,
            'verdict': result.verdict,
            'confidence': result.confidence,
            'timestamp': time.time(),
        })
        # Keep last 500 entries
        if len(self._gate_log) > 500:
            self._gate_log = self._gate_log[-500:]

    def get_audit_log(self, limit: int = 20) -> List[Dict]:
        """Get recent gate check audit log."""
        return self._gate_log[-limit:]

    def status(self) -> dict:
        return {
            'total_checks': len(self._gate_log),
            'pending_proposals': len(self.two_phase_gate.get_pending()),
            'recent_blocks': sum(
                1 for e in self._gate_log[-50:]
                if e['verdict'] in (GateVerdict.BLOCK, GateVerdict.ESCALATE)
            ),
        }
