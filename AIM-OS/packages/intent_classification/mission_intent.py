"""
Mission Intent Data Models

Core data structures for the Intent Classification System, defining the multi-axis
classification model that transforms raw user input into structured mission profiles.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class PrimaryCategory(Enum):
    """Primary mission categories for intent classification."""
    
    NEW_SYSTEM_DESIGN = "new_system_design"
    EXISTING_SYSTEM_ENHANCEMENT = "existing_system_enhancement"
    BUG_FIX = "bug_fix"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    RESEARCH_PROBE = "research_probe"
    ANALYSIS = "analysis"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    INVESTIGATION = "investigation"


class LifecycleStage(Enum):
    """Mission lifecycle stages from ideation to deprecation."""
    
    IDEATION = "ideation"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    INTEGRATION = "integration"
    HARDENING = "hardening"
    STABILIZATION = "stabilization"
    DEPRECATION = "deprecation"


class ScopeLevel(Enum):
    """Scope levels from local function to whole platform."""
    
    LOCAL_FUNCTION = "local_function"
    SINGLE_MODULE = "single_module"
    MULTI_SERVICE = "multi_service"
    WHOLE_PLATFORM = "whole_platform"


class ClarityState(Enum):
    """Clarity states from exploratory to fully defined."""
    
    EXPLORATORY = "exploratory"
    PARTIALLY_DEFINED = "partially_defined"
    FULLY_DEFINED = "fully_defined"


class MissionStatus(Enum):
    """Mission status tracking."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"
    BLOCKED = "blocked"


@dataclass
class MissionIntent:
    """
    Core mission profile with multi-axis classification.
    
    This is the primary data structure that captures all aspects of a mission
    intent, enabling behavior gating, risk assessment, and mission management.
    """
    
    # Core identification
    mission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_intent: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Multi-axis classification
    primary_category: PrimaryCategory = PrimaryCategory.INVESTIGATION
    lifecycle_stage: LifecycleStage = LifecycleStage.IDEATION
    scope_level: ScopeLevel = ScopeLevel.LOCAL_FUNCTION
    clarity_state: ClarityState = ClarityState.EXPLORATORY
    
    # Contextual information
    facets: List[str] = field(default_factory=list)
    confidence_level: float = 0.0
    complexity_score: float = 0.0
    
    # Behavior control
    allowed_actions: Set[str] = field(default_factory=set)
    blocked_actions: Set[str] = field(default_factory=set)
    required_approvals: List[str] = field(default_factory=list)
    
    # Mission management
    mission_status: MissionStatus = MissionStatus.ACTIVE
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    
    # Risk assessment
    risk_level: str = "low"  # low, medium, high, critical
    stop_conditions: List[str] = field(default_factory=list)
    blast_radius: str = "local"  # local, module, service, platform
    
    # Context and memory
    related_missions: List[str] = field(default_factory=list)
    parent_mission: Optional[str] = None
    child_missions: List[str] = field(default_factory=list)
    
    # Metadata
    tags: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize the mission intent after initialization."""
        self._validate_confidence()
        self._validate_complexity()
        self._normalize_facets()
    
    def _validate_confidence(self) -> None:
        """Validate confidence level is within valid range."""
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValueError(f"Confidence level must be between 0.0 and 1.0, got {self.confidence_level}")
    
    def _validate_complexity(self) -> None:
        """Validate complexity score is within valid range."""
        if not 0.0 <= self.complexity_score <= 1.0:
            raise ValueError(f"Complexity score must be between 0.0 and 1.0, got {self.complexity_score}")
    
    def _normalize_facets(self) -> None:
        """Normalize facets to lowercase and remove duplicates."""
        self.facets = list(set(facet.lower().strip() for facet in self.facets if facet.strip()))
    
    def add_facet(self, facet: str) -> None:
        """Add a facet to the mission intent."""
        normalized_facet = facet.lower().strip()
        if normalized_facet and normalized_facet not in self.facets:
            self.facets.append(normalized_facet)
    
    def remove_facet(self, facet: str) -> None:
        """Remove a facet from the mission intent."""
        normalized_facet = facet.lower().strip()
        if normalized_facet in self.facets:
            self.facets.remove(normalized_facet)
    
    def add_allowed_action(self, action: str) -> None:
        """Add an allowed action."""
        self.allowed_actions.add(action)
    
    def add_blocked_action(self, action: str) -> None:
        """Add a blocked action."""
        self.blocked_actions.add(action)
        # Remove from allowed actions if present
        self.allowed_actions.discard(action)
    
    def is_action_allowed(self, action: str) -> bool:
        """Check if an action is allowed for this mission."""
        return action in self.allowed_actions and action not in self.blocked_actions
    
    def requires_escalation(self) -> bool:
        """Check if this mission requires escalation."""
        return (
            self.escalation_required or
            self.confidence_level < 0.3 or
            (self.scope_level == ScopeLevel.WHOLE_PLATFORM and self.lifecycle_stage in [LifecycleStage.IMPLEMENTATION, LifecycleStage.INTEGRATION]) or
            (self.clarity_state == ClarityState.EXPLORATORY and self.lifecycle_stage in [LifecycleStage.IMPLEMENTATION, LifecycleStage.INTEGRATION]) or
            self.complexity_score > 0.8
        )
    
    def get_escalation_reason(self) -> Optional[str]:
        """Get the reason for escalation if required."""
        if not self.requires_escalation():
            return None
        
        if self.escalation_reason:
            return self.escalation_reason
        
        if self.confidence_level < 0.3:
            return f"Low confidence level: {self.confidence_level}"
        
        if self.scope_level == ScopeLevel.WHOLE_PLATFORM and self.lifecycle_stage in [LifecycleStage.IMPLEMENTATION, LifecycleStage.INTEGRATION]:
            return "Platform-wide scope with implementation/integration stage"
        
        if self.clarity_state == ClarityState.EXPLORATORY and self.lifecycle_stage in [LifecycleStage.IMPLEMENTATION, LifecycleStage.INTEGRATION]:
            return "Exploratory state with implementation/integration stage"
        
        if self.complexity_score > 0.8:
            return f"High complexity score: {self.complexity_score}"
        
        return "Unknown escalation reason"
    
    def update_status(self, new_status: MissionStatus, reason: Optional[str] = None) -> None:
        """Update mission status with optional reason."""
        self.mission_status = new_status
        self.updated_at = datetime.utcnow()
        if reason:
            self.notes.append(f"Status changed to {new_status.value}: {reason}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mission intent to dictionary for serialization."""
        return {
            "mission_id": self.mission_id,
            "raw_intent": self.raw_intent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "primary_category": self.primary_category.value,
            "lifecycle_stage": self.lifecycle_stage.value,
            "scope_level": self.scope_level.value,
            "clarity_state": self.clarity_state.value,
            "facets": self.facets,
            "confidence_level": self.confidence_level,
            "complexity_score": self.complexity_score,
            "allowed_actions": list(self.allowed_actions),
            "blocked_actions": list(self.blocked_actions),
            "required_approvals": self.required_approvals,
            "mission_status": self.mission_status.value,
            "escalation_required": self.escalation_required,
            "escalation_reason": self.escalation_reason,
            "risk_level": self.risk_level,
            "stop_conditions": self.stop_conditions,
            "blast_radius": self.blast_radius,
            "related_missions": self.related_missions,
            "parent_mission": self.parent_mission,
            "child_missions": self.child_missions,
            "tags": self.tags,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MissionIntent:
        """Create mission intent from dictionary."""
        # Convert enum values back to enum instances
        data["primary_category"] = PrimaryCategory(data["primary_category"])
        data["lifecycle_stage"] = LifecycleStage(data["lifecycle_stage"])
        data["scope_level"] = ScopeLevel(data["scope_level"])
        data["clarity_state"] = ClarityState(data["clarity_state"])
        data["mission_status"] = MissionStatus(data["mission_status"])
        
        # Convert sets back from lists
        data["allowed_actions"] = set(data["allowed_actions"])
        data["blocked_actions"] = set(data["blocked_actions"])
        
        # Convert datetime strings back to datetime objects
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return cls(**data)
