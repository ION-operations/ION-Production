"""APOE Core Data Models

Base types for APOE orchestration system.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# NL_TAG: VIF-MODEL-001 | The 8 specialized AI agent roles. | class RoleType | []
class RoleType(str, Enum):
    """The 8 specialized AI agent roles."""
    PLANNER = "planner"
    RETRIEVER = "retriever"
    REASONER = "reasoner"
    VERIFIER = "verifier"
    BUILDER = "builder"
    CRITIC = "critic"
    OPERATOR = "operator"
    WITNESS = "witness"


# NL_TAG: VIF-MODEL-002 | Execution status for steps. | class StepStatus | []
class StepStatus(str, Enum):
    """Execution status for steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ABSTAINED = "abstained"  # κ-gate triggered


# NL_TAG: VIF-MODEL-003 | Resource budget for operations. | class Budget | []
class Budget(BaseModel):
    """Resource budget for operations."""
    tokens_limit: int = 10000
    tokens_consumed: int = 0
    time_limit_seconds: float = 300.0
    time_elapsed_seconds: float = 0.0
    tools_limit: int = 10
    tools_consumed: int = 0
    
    def check_tokens(self, cost: int) -> bool:
        """Check if tokens available."""
        return self.tokens_consumed + cost <= self.tokens_limit
    
    def consume_tokens(self, cost: int) -> bool:
        """Consume tokens from budget."""
        if self.check_tokens(cost):
            self.tokens_consumed += cost
            return True
        return False
    
    def check_time(self, duration: float) -> bool:
        """Check if time available."""
        return self.time_elapsed_seconds + duration <= self.time_limit_seconds
    
    def consume_time(self, duration: float) -> bool:
        """Consume time from budget."""
        if self.check_time(duration):
            self.time_elapsed_seconds += duration
            return True
        return False
    
    def remaining_tokens(self) -> int:
        """Get remaining token budget."""
        return self.tokens_limit - self.tokens_consumed
    
    def remaining_time(self) -> float:
        """Get remaining time budget."""
        return self.time_limit_seconds - self.time_elapsed_seconds


# NL_TAG: VIF-MODEL-004 | Quality gate that must pass before proceeding. | class Gate | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: gate | Gate | [ADR-TBD]
class Gate(BaseModel):
    """Quality gate that must pass before proceeding."""
    id: str
    name: str
    gate_type: str  # "quality" | "budget" | "confidence" | "custom"
    condition: str  # e.g., "output.confidence >= 0.95"
    on_fail: Optional[str] = "abort"  # "abort" | "retry" | "skip" | "escalate"
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate gate condition against context.
        
        Args:
            context: Variables available for condition evaluation
            
        Returns:
            True if gate passes, False if fails
        """
        try:
            # Simple eval-based gate (production would use safer evaluation)
            return eval(self.condition, {"__builtins__": {}}, context)
        except Exception:
            # On error, fail safe (gate fails)
            return False


# NL_TAG: VIF-MODEL-005 | Single step in execution plan. | class Step | []
class Step(BaseModel):
    # NL_TAG: VIF-MODEL-006 | Check if tokens available. | check_tokens(self, cost) | []
    # NL_TAG_SPEC: VIF-SPEC-001 | Validates check_tokens specification | check_tokens | [spec_file_TBD]
    def check_tokens(self, cost: int) -> bool:
        """Check if tokens available."""
        return self.tokens_consumed + cost <= self.tokens_limit
    
    # NL_TAG: VIF-MODEL-007 | Consume tokens from budget. | consume_tokens(self, cost) | []
    def consume_tokens(self, cost: int) -> bool:
        """Consume tokens from budget."""
        if self.check_tokens(cost):
            self.tokens_consumed += cost
            return True
        return False
    
    # NL_TAG: VIF-MODEL-008 | Check if time available. | check_time(self, duration) | []
    # NL_TAG_SPEC: VIF-SPEC-002 | Validates check_time specification | check_time | [spec_file_TBD]
    def check_time(self, duration: float) -> bool:
        """Check if time available."""
        return self.time_elapsed_seconds + duration <= self.time_limit_seconds
    
    # NL_TAG: VIF-MODEL-009 | Consume time from budget. | consume_time(self, duration) | []
    def consume_time(self, duration: float) -> bool:
        """Consume time from budget."""
        if self.check_time(duration):
            self.time_elapsed_seconds += duration
            return True
        return False
    
    # NL_TAG: VIF-MODEL-010 | Get remaining token budget. | remaining_tokens(self) | []
    def remaining_tokens(self) -> int:
        """Get remaining token budget."""
        return self.tokens_limit - self.tokens_consumed
    
    # NL_TAG: VIF-MODEL-011 | Get remaining time budget. | remaining_time(self) | []
    def remaining_time(self) -> float:
        """Get remaining time budget."""
        return self.time_limit_seconds - self.time_elapsed_seconds


class Gate(BaseModel):
    """Quality gate that must pass before proceeding."""
    id: str
    name: str
    gate_type: str  # "quality" | "budget" | "confidence" | "custom"
    condition: str  # e.g., "output.confidence >= 0.95"
    on_fail: Optional[str] = "abort"  # "abort" | "retry" | "skip" | "escalate"
    
    # NL_TAG: VIF-MODEL-012 | Evaluate gate condition against context. | evaluate(self, context) | []
    # NL_TAG_INTENT: VIF-INTENT-002 | Design decision: gate | evaluate | [ADR-TBD]
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate gate condition against context.
        
        Args:
            context: Variables available for condition evaluation
            
        Returns:
            True if gate passes, False if fails
        """
        try:
            # Simple eval-based gate (production would use safer evaluation)
            return eval(self.condition, {"__builtins__": {}}, context)
        except Exception:
            # On error, fail safe (gate fails)
            return False


class Step(BaseModel):
    """Single step in execution plan."""
    id: str
    name: str
    role: RoleType
    role_name: Optional[str] = None  # Name of role from ASSIGN (e.g., "validator")
    description: Optional[str] = None
    budget: Optional[Budget] = None
    gates: List[Gate] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    
    # Execution results
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # NL_TAG: VIF-MODEL-013 | Calculate execution duration in seconds. | duration(self) | []
    def duration(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

