"""
Execution Record Data Models
Tracks complete execution history for prompt chains

Implements bidirectional connection between chains and timeline entries.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class NodeExecutionResult:
    """Result of executing a single node"""
    node_id: str
    success: bool
    output: Any
    confidence: float = 0.0
    duration: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'node_id': self.node_id,
            'success': self.success,
            'output': self.output,
            'confidence': self.confidence,
            'duration': self.duration,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ChainExecutionResult:
    """Result of executing an entire chain"""
    chain_id: str
    execution_id: str
    success: bool
    output: Any
    nodes_executed: List[NodeExecutionResult]
    total_duration: float
    confidence: float
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'chain_id': self.chain_id,
            'execution_id': self.execution_id,
            'success': self.success,
            'output': self.output,
            'nodes_executed': [n.to_dict() for n in self.nodes_executed],
            'total_duration': self.total_duration,
            'confidence': self.confidence,
            'error': self.error,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class NodeExecution:
    """
    Individual node execution record
    
    Tracks complete execution history for a single chain node,
    including timeline entries created by this node.
    """
    node_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # "running" | "completed" | "failed" | "aborted"
    
    # Timeline Connection (Bidirectional)
    timeline_entry_ids: List[str] = field(default_factory=list)  # Timeline entries created by this node
    
    # Results
    output: Any = None
    quality_score: float = 0.0
    confidence_score: float = 0.0
    
    # Provenance
    input_data: Dict[str, Any] = field(default_factory=dict)
    system_calls: List[Dict[str, Any]] = field(default_factory=list)  # MCP calls, API calls, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'node_id': self.node_id,
            'execution_id': self.execution_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'timeline_entry_ids': self.timeline_entry_ids,
            'output': self.output,
            'quality_score': self.quality_score,
            'confidence_score': self.confidence_score,
            'input_data': self.input_data,
            'system_calls': self.system_calls
        }


@dataclass
class ExecutionRecord:
    """
    Complete execution record for a chain
    
    Tracks all executions, node results, timeline connections,
    and quality metrics for complete provenance.
    """
    execution_id: str
    chain_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # "running" | "completed" | "failed" | "aborted"
    
    # Timeline Connections (Bidirectional)
    timeline_entry_ids: List[str] = field(default_factory=list)  # Timeline entries created during execution
    node_executions: List[NodeExecution] = field(default_factory=list)  # Individual node executions
    
    # Quality Metrics
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    alignment_score: float = 0.0  # Alignment with goals
    
    # Provenance
    executed_by: str = "aether"  # Agent/system that executed
    context_snapshot: Dict[str, Any] = field(default_factory=dict)  # Context at execution time
    
    # Goal Integration
    goal_id: Optional[str] = None  # Goal this execution served
    
    def add_timeline_entry(self, entry_id: str):
        """Add timeline entry produced during execution"""
        if entry_id not in self.timeline_entry_ids:
            self.timeline_entry_ids.append(entry_id)
    
    def add_node_execution(self, node_execution: NodeExecution):
        """Add node execution record"""
        self.node_executions.append(node_execution)
        # Also add any timeline entries from this node
        for entry_id in node_execution.timeline_entry_ids:
            self.add_timeline_entry(entry_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'execution_id': self.execution_id,
            'chain_id': self.chain_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'timeline_entry_ids': self.timeline_entry_ids,
            'node_executions': [n.to_dict() for n in self.node_executions],
            'quality_metrics': self.quality_metrics,
            'confidence_scores': self.confidence_scores,
            'alignment_score': self.alignment_score,
            'executed_by': self.executed_by,
            'context_snapshot': self.context_snapshot,
            'goal_id': self.goal_id
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ExecutionRecord:
        """Deserialize from dictionary"""
        return ExecutionRecord(
            execution_id=data['execution_id'],
            chain_id=data['chain_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            status=data.get('status', 'running'),
            timeline_entry_ids=data.get('timeline_entry_ids', []),
            node_executions=[],  # Would need separate deserialization
            quality_metrics=data.get('quality_metrics', {}),
            confidence_scores=data.get('confidence_scores', {}),
            alignment_score=data.get('alignment_score', 0.0),
            executed_by=data.get('executed_by', 'aether'),
            context_snapshot=data.get('context_snapshot', {}),
            goal_id=data.get('goal_id')
        )

