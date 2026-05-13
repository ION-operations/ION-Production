"""
Prompt Chain Data Models
Complete implementation from T3 Detailed documentation

This module implements the complete data model for Prompt Chains,
enabling executable workflow graphs with meta-orchestration.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
import json


# === ENUMERATIONS ===

class ChainType(str, Enum):
    """Chain classification"""
    META = "meta"                    # Orchestrates other chains
    ATOMIC = "atomic"                # Single-purpose operation
    COMPOSITE = "composite"          # Composition of chains
    ADAPTIVE = "adaptive"            # Self-modifying


class ChainPriority(str, Enum):
    """Chain priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NodeType(str, Enum):
    """Node operation types"""
    SYSTEM_CALL = "system_call"      # Call AIM-OS system
    DECISION = "decision"            # Conditional branching
    GATE = "gate"                    # Quality enforcement
    BRANCH = "branch"                # Parallel execution
    MERGE = "merge"                  # Combine results


class ConditionType(str, Enum):
    """Edge condition types"""
    CONFIDENCE = "confidence"        # VIF confidence check
    QUALITY = "quality"              # SDF-CVF quality check
    RESULT = "result"                # Operation result check
    CUSTOM = "custom"                # Custom expression


# === QUALITY GATE ===

@dataclass
class QualityGate:
    """
    Quality enforcement gate (SDF-CVF)
    
    Enforces quality standards before proceeding.
    """
    gate_type: str                   # "quartet_parity" | "test_coverage" | "custom"
    threshold: float                 # Minimum passing score (0.0-1.0)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate gate against context"""
        if self.gate_type == "quartet_parity":
            parity = context.get("quartet_parity", 0.0)
            return parity >= self.threshold
        elif self.gate_type == "test_coverage":
            coverage = context.get("test_coverage", 0.0)
            return coverage >= self.threshold
        else:
            # Custom gate - evaluate parameters
            return True  # Placeholder
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'gate_type': self.gate_type,
            'threshold': self.threshold,
            'parameters': self.parameters
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> QualityGate:
        """Deserialize from dictionary"""
        return QualityGate(
            gate_type=data['gate_type'],
            threshold=data['threshold'],
            parameters=data.get('parameters', {})
        )


# === CHAIN NODE ===

@dataclass
class ChainNode:
    """
    Single operation in a chain
    
    Explicitly declares which AIM-OS system it uses,
    enabling complete traceability and integration.
    """
    
    # === IDENTITY ===
    node_id: str                     # Unique within chain
    name: str                        # Human-readable
    description: str                 # What this does
    
    # === OPERATION ===
    operation_type: NodeType
    
    # === SYSTEM INTEGRATION (Explicit!) ===
    system: Optional[str] = None     # "CMC" | "HHNI" | "VIF" | "APOE" | "SEG" | "SDF-CVF"
    operation: Optional[str] = None  # System operation name
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # === PROMPT (For AI operations) ===
    prompt: Optional[str] = None     # Natural language prompt
    
    # === QUALITY ===
    confidence_threshold: float = 0.70
    quality_gate: Optional[QualityGate] = None
    
    # === EXECUTION ===
    execution_required: bool = True
    timeout_seconds: Optional[float] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'node_id': self.node_id,
            'name': self.name,
            'description': self.description,
            'operation_type': self.operation_type.value,
            'system': self.system,
            'operation': self.operation,
            'parameters': self.parameters,
            'prompt': self.prompt,
            'confidence_threshold': self.confidence_threshold,
            'quality_gate': self.quality_gate.to_dict() if self.quality_gate else None,
            'execution_required': self.execution_required,
            'timeout_seconds': self.timeout_seconds,
            'retry_count': self.retry_count
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ChainNode:
        """Deserialize from dictionary"""
        return ChainNode(
            node_id=data['node_id'],
            name=data['name'],
            description=data['description'],
            operation_type=NodeType(data['operation_type']),
            system=data.get('system'),
            operation=data.get('operation'),
            parameters=data.get('parameters', {}),
            prompt=data.get('prompt'),
            confidence_threshold=data.get('confidence_threshold', 0.70),
            quality_gate=QualityGate.from_dict(data['quality_gate']) if data.get('quality_gate') else None,
            execution_required=data.get('execution_required', True),
            timeout_seconds=data.get('timeout_seconds'),
            retry_count=data.get('retry_count', 0)
        )


# === CHAIN EDGE ===

@dataclass
class ChainEdge:
    """
    Transition between nodes with conditional logic
    
    Enables dynamic routing based on runtime conditions.
    """
    
    # === IDENTITY ===
    edge_id: str
    from_node_id: str
    to_node_id: str
    
    # === CONDITION (Optional) ===
    condition_type: Optional[ConditionType] = None
    condition_expression: Optional[str] = None  # Python expression
    
    # === METADATA ===
    label: str = ""
    weight: float = 1.0
    
    def evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """Evaluate edge condition against context"""
        if self.condition_type is None:
            return True  # Always take unconditional edges
        
        if self.condition_type == ConditionType.CONFIDENCE:
            # Parse expression like "confidence > 0.70"
            confidence = context.get('confidence', 0.0)
            return eval(self.condition_expression, {'confidence': confidence})
        
        elif self.condition_type == ConditionType.QUALITY:
            # Parse expression like "quartet_parity >= 0.90"
            quality = context.get('quartet_parity', 0.0)
            return eval(self.condition_expression, {'quartet_parity': quality})
        
        elif self.condition_type == ConditionType.RESULT:
            # Parse expression like "status == 'success'"
            result = context.get('result', {})
            return eval(self.condition_expression, result)
        
        elif self.condition_type == ConditionType.CUSTOM:
            # Custom Python expression
            return eval(self.condition_expression, context)
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'edge_id': self.edge_id,
            'from_node_id': self.from_node_id,
            'to_node_id': self.to_node_id,
            'condition_type': self.condition_type.value if self.condition_type else None,
            'condition_expression': self.condition_expression,
            'label': self.label,
            'weight': self.weight
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ChainEdge:
        """Deserialize from dictionary"""
        return ChainEdge(
            edge_id=data['edge_id'],
            from_node_id=data['from_node_id'],
            to_node_id=data['to_node_id'],
            condition_type=ConditionType(data['condition_type']) if data.get('condition_type') else None,
            condition_expression=data.get('condition_expression'),
            label=data.get('label', ''),
            weight=data.get('weight', 1.0)
        )


# === PROMPT CHAIN ===

@dataclass
class PromptChain:
    """
    Executable workflow graph for AI operations
    
    Complete chain definition with nodes, edges, and system integration.
    Implements meta-orchestration (chains orchestrating chains).
    """
    
    # === IDENTITY ===
    chain_id: str
    name: str
    description: str
    version: str = "1.0.0"
    
    # === CLASSIFICATION ===
    chain_type: ChainType = ChainType.ATOMIC
    tier: int = 1
    priority: ChainPriority = ChainPriority.MEDIUM
    
    # === STRUCTURE ===
    nodes: List[ChainNode] = field(default_factory=list)
    edges: List[ChainEdge] = field(default_factory=list)
    start_node_id: str = ""
    end_node_ids: List[str] = field(default_factory=list)
    
    # === INTEGRATION (Bidirectional with Goals) ===
    goal_id: Optional[str] = None
    parent_chain_id: Optional[str] = None
    sub_chain_ids: List[str] = field(default_factory=list)
    
    # === TIMELINE INTEGRATION (Bidirectional) ===
    # Added for Timeline-Chain bidirectional graph (Nov 5, 2025)
    timeline_entry_ids: List[str] = field(default_factory=list)  # Timeline entries produced
    execution_history: List[str] = field(default_factory=list)   # ExecutionRecord IDs
    
    # === METADATA ===
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "aether"
    
    # === PROVENANCE ===
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration: float = 0.0
    
    def get_node(self, node_id: str) -> Optional[ChainNode]:
        """Get node by ID"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_outgoing_edges(self, node_id: str) -> List[ChainEdge]:
        """Get all edges leaving a node"""
        return [edge for edge in self.edges if edge.from_node_id == node_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage"""
        return {
            'chain_id': self.chain_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'chain_type': self.chain_type.value,
            'tier': self.tier,
            'priority': self.priority.value,
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
            'start_node_id': self.start_node_id,
            'end_node_ids': self.end_node_ids,
            'goal_id': self.goal_id,
            'parent_chain_id': self.parent_chain_id,
            'sub_chain_ids': self.sub_chain_ids,
            'timeline_entry_ids': self.timeline_entry_ids,
            'execution_history': self.execution_history,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'average_duration': self.average_duration
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> PromptChain:
        """Deserialize from dictionary"""
        return PromptChain(
            chain_id=data['chain_id'],
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0.0'),
            chain_type=ChainType(data['chain_type']),
            tier=data.get('tier', 1),
            priority=ChainPriority(data['priority']),
            nodes=[ChainNode.from_dict(n) for n in data['nodes']],
            edges=[ChainEdge.from_dict(e) for e in data['edges']],
            start_node_id=data['start_node_id'],
            end_node_ids=data['end_node_ids'],
            goal_id=data.get('goal_id'),
            parent_chain_id=data.get('parent_chain_id'),
            sub_chain_ids=data.get('sub_chain_ids', []),
            timeline_entry_ids=data.get('timeline_entry_ids', []),
            execution_history=data.get('execution_history', []),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data.get('updated_at'), str) else data.get('updated_at', datetime.now()),
            created_by=data.get('created_by', 'aether'),
            execution_count=data.get('execution_count', 0),
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0),
            average_duration=data.get('average_duration', 0.0)
        )

