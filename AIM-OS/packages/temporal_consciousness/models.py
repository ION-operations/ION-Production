"""
Temporal Consciousness Data Models

Enhanced data models with bidirectional references connecting Timeline, Goals, and Chains.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GoalStatus(Enum):
    """Goal status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class EnhancedTimelineEntry:
    """
    Enhanced Timeline Entry with bidirectional chain/goal references.
    
    Extends base TimelineEntry with:
    - Chain references (executed_via, parent/child chains)
    - Goal references (related_goal_ids, goal_progress)
    - Provenance tracking
    """
    # Core fields (from TCS)
    entry_id: str
    timestamp: datetime
    entry_type: str
    content: str
    agent: str
    summary: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # NEW: Bidirectional chain references
    executed_via_chain_id: Optional[str] = None  # Chain ID that created this entry
    parent_entry_ids: List[str] = field(default_factory=list)  # Entries that led to this
    child_entry_ids: List[str] = field(default_factory=list)  # Entries this led to
    
    # NEW: Bidirectional goal references
    related_goal_ids: List[str] = field(default_factory=list)  # Goals this entry serves
    goal_progress: Dict[str, float] = field(default_factory=dict)  # Progress contribution per goal
    
    # Provenance
    confidence: float = 0.0
    vif_witness: Optional[str] = None
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "entry_type": self.entry_type,
            "content": self.content,
            "agent": self.agent,
            "summary": self.summary,
            "context_data": self.context_data,
            "executed_via_chain_id": self.executed_via_chain_id,
            "parent_entry_ids": self.parent_entry_ids,
            "child_entry_ids": self.child_entry_ids,
            "related_goal_ids": self.related_goal_ids,
            "goal_progress": self.goal_progress,
            "confidence": self.confidence,
            "vif_witness": self.vif_witness,
            "quality_metrics": self.quality_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedTimelineEntry":
        """Create from dictionary"""
        # Parse timestamp
        if isinstance(data.get("timestamp"), str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data.get("timestamp", datetime.now())
        
        return cls(
            entry_id=data["entry_id"],
            timestamp=timestamp,
            entry_type=data.get("entry_type", "operation"),
            content=data.get("content", ""),
            agent=data.get("agent", "unknown"),
            summary=data.get("summary"),
            context_data=data.get("context_data", {}),
            executed_via_chain_id=data.get("executed_via_chain_id"),
            parent_entry_ids=data.get("parent_entry_ids", []),
            child_entry_ids=data.get("child_entry_ids", []),
            related_goal_ids=data.get("related_goal_ids", []),
            goal_progress=data.get("goal_progress", {}),
            confidence=data.get("confidence", 0.0),
            vif_witness=data.get("vif_witness"),
            quality_metrics=data.get("quality_metrics", {})
        )


@dataclass
class EnhancedGoalTimelineNode:
    """
    Enhanced Goal Timeline Node with bidirectional timeline/chain references.
    
    Extends base GoalTimelineNode with:
    - Timeline references (timeline_entry_ids, creation/completion entries)
    - Chain references (planned_chain_ids, executed_chain_ids)
    """
    # Core fields (from Goal Timeline System)
    goal_id: str
    name: str
    description: str
    status: GoalStatus
    progress_percentage: float = 0.0
    
    # NEW: Bidirectional timeline references
    timeline_entry_ids: List[str] = field(default_factory=list)  # Computed: entries related to this goal
    creation_entry_id: Optional[str] = None  # Entry that created this goal
    completion_entry_id: Optional[str] = None  # Entry that completed this goal
    
    # NEW: Bidirectional chain references
    planned_chain_ids: List[str] = field(default_factory=list)  # Chains planned to complete this
    executed_chain_ids: List[str] = field(default_factory=list)  # Chains that have run for this
    
    # Progress tracking
    key_results: List[Dict[str, Any]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Temporal context
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    target_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "goal_id": self.goal_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "timeline_entry_ids": self.timeline_entry_ids,
            "creation_entry_id": self.creation_entry_id,
            "completion_entry_id": self.completion_entry_id,
            "planned_chain_ids": self.planned_chain_ids,
            "executed_chain_ids": self.executed_chain_ids,
            "key_results": self.key_results,
            "milestones": self.milestones,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "target_date": self.target_date.isoformat() if self.target_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedGoalTimelineNode":
        """Create from dictionary"""
        # Parse timestamps
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.now()
        
        target_date = data.get("target_date")
        if target_date and isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date)
        
        # Parse status
        status_str = data.get("status", "planned")
        try:
            status = GoalStatus(status_str)
        except ValueError:
            status = GoalStatus.PLANNED
        
        return cls(
            goal_id=data["goal_id"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=status,
            progress_percentage=data.get("progress_percentage", 0.0),
            timeline_entry_ids=data.get("timeline_entry_ids", []),
            creation_entry_id=data.get("creation_entry_id"),
            completion_entry_id=data.get("completion_entry_id"),
            planned_chain_ids=data.get("planned_chain_ids", []),
            executed_chain_ids=data.get("executed_chain_ids", []),
            key_results=data.get("key_results", []),
            milestones=data.get("milestones", []),
            created_at=created_at,
            updated_at=updated_at,
            target_date=target_date
        )


@dataclass
class EnhancedPromptChain:
    """
    Enhanced Prompt Chain with bidirectional timeline/goal references.
    
    Extends base PromptChain with:
    - Timeline references (timeline_entry_ids, execution_history)
    - Goal references (related_goal_ids, goal_contributions)
    - Execution metadata
    """
    # Core fields (from Prompt Chain System)
    chain_id: str
    name: str
    description: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    # NEW: Bidirectional timeline references
    timeline_entry_ids: List[str] = field(default_factory=list)  # Entries produced by this chain
    execution_history: List[Dict[str, Any]] = field(default_factory=list)  # Complete execution history
    
    # NEW: Bidirectional goal references
    related_goal_ids: List[str] = field(default_factory=list)  # Goals this chain serves
    goal_contributions: Dict[str, float] = field(default_factory=dict)  # Progress contribution per goal
    
    # Execution metadata
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_quality_score: float = 0.0
    average_execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "chain_id": self.chain_id,
            "name": self.name,
            "description": self.description,
            "nodes": self.nodes,
            "timeline_entry_ids": self.timeline_entry_ids,
            "execution_history": self.execution_history,
            "related_goal_ids": self.related_goal_ids,
            "goal_contributions": self.goal_contributions,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "average_quality_score": self.average_quality_score,
            "average_execution_time": self.average_execution_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedPromptChain":
        """Create from dictionary"""
        return cls(
            chain_id=data["chain_id"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            nodes=data.get("nodes", []),
            timeline_entry_ids=data.get("timeline_entry_ids", []),
            execution_history=data.get("execution_history", []),
            related_goal_ids=data.get("related_goal_ids", []),
            goal_contributions=data.get("goal_contributions", {}),
            execution_count=data.get("execution_count", 0),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            average_quality_score=data.get("average_quality_score", 0.0),
            average_execution_time=data.get("average_execution_time", 0.0)
        )


@dataclass
class TemporalGraph:
    """
    Complete temporal consciousness graph containing all three layers.
    
    PAST: Timeline entries (blue)
    PRESENT: Goals (orange)
    FUTURE: Chains (purple)
    """
    timeline_entries: List[EnhancedTimelineEntry] = field(default_factory=list)
    goals: List[EnhancedGoalTimelineNode] = field(default_factory=list)
    chains: List[EnhancedPromptChain] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timeline": [entry.to_dict() for entry in self.timeline_entries],
            "goals": [goal.to_dict() for goal in self.goals],
            "chains": [chain.to_dict() for chain in self.chains]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporalGraph":
        """Create from dictionary"""
        timeline_entries = [
            EnhancedTimelineEntry.from_dict(entry)
            for entry in data.get("timeline", [])
        ]
        goals = [
            EnhancedGoalTimelineNode.from_dict(goal)
            for goal in data.get("goals", [])
        ]
        chains = [
            EnhancedPromptChain.from_dict(chain)
            for chain in data.get("chains", [])
        ]
        
        return cls(
            timeline_entries=timeline_entries,
            goals=goals,
            chains=chains
        )

