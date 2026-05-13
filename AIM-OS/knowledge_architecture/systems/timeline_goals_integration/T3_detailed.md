---
id: "timeline_goals_integration_T3_detailed"
system: "timeline_goals_integration"
component: null
level: "T3"
type: "detailed"
title: "Timeline-Goals Integration Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Timeline-Goals Integration"
audience: "developers, implementers"
confidence_threshold: 0.50
token_cost: 10000
word_count: 10000
created: "2025-11-05T09:30:00Z"
updated: "2025-11-05T09:30:00Z"
author: "aether"
status: "complete"
tags: ["timeline-goals", "integration", "implementation", "detailed", "t0-t6", "transitional"]
dependencies: ["timeline_context_system", "goal_tree", "cmc", "hhni", "vif"]
related_docs: ["T0_executive.md", "T1_overview.md", "T2_architecture.md", "T4_complete.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Timeline-Goals Integration – T3 Detailed Implementation Guide (≈10,000 words)

## Table of Contents

1. [Implementation Overview](#implementation-overview)
2. [Complete Data Model Reference](#complete-data-model-reference)
3. [GoalTimelineManager Implementation](#goaltimelinemanager-implementation)
4. [Sequential Ordering System](#sequential-ordering-system)
5. [Bidirectional Sync Implementation](#bidirectional-sync-implementation)
6. [MCP Tools Implementation](#mcp-tools-implementation)
7. [CMC Integration](#cmc-integration)
8. [HHNI Integration](#hhni-integration)
9. [VIF Integration](#vif-integration)
10. [Testing Guide](#testing-guide)
11. [Error Handling & Recovery](#error-handling--recovery)
12. [Performance Optimization](#performance-optimization)
13. [Deployment Guide](#deployment-guide)
14. [Troubleshooting](#troubleshooting)

---

## Implementation Overview

### System Components

The Timeline-Goals Integration system consists of three primary components:

**1. Data Models** (`goal_timeline_node.py` - 264 lines)
- `GoalTimelineNode` - Complete goal with temporal consciousness
- `GoalStatus` - Enumeration for goal states
- `GoalPriority` - Enumeration for priority levels
- `KeyResult` - OKR-style key result tracking
- `EmotionalContext` - Emotional consciousness preservation

**2. Manager** (`goal_timeline_manager.py` - 346 lines)
- `GoalTimelineManager` - Orchestration and lifecycle management
- Goal creation with temporal tracking
- Progress and status updates
- Query system with multiple filters
- Bidirectional GOAL_TREE.yaml synchronization
- Persistence layer

**3. Sync Layer** (`goal_tree_sync.py`)
- Bidirectional sync algorithms
- Conflict resolution
- YAML parsing and serialization

**Total Implementation:** 610 lines of production Python code

### Implementation Approach

**Phase 1: Data Models** (Completed Oct 25, 2025)
- Define complete data structures
- Implement validation and serialization
- Write unit tests

**Phase 2: Manager & Sync** (Completed Oct 25, 2025)
- Implement GoalTimelineManager
- Implement bidirectional sync
- Write integration tests

**Phase 3: MCP Integration** (Completed Oct 25, 2025)
- Create 3 MCP tools
- Register in lucid_mcp_server
- Test end-to-end

**Current Status:** ✅ All phases complete, production-ready

---

## Complete Data Model Reference

### GoalTimelineNode (Complete Implementation)

**File:** `packages/timeline_context_system/goal_timeline_node.py`

**Complete Class Definition:**

```python
from __future__ import annotations
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class GoalStatus(Enum):
    """Goal status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class GoalPriority(Enum):
    """Goal priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class KeyResult:
    """Key result for a goal (OKR pattern)"""
    id: str               # Unique identifier (e.g., "KR-1.1")
    name: str             # Key result name
    metric: str           # What we're measuring
    target: str           # Target value (e.g., "100%", "50 users")
    status: str = "pending"  # "pending" | "in_progress" | "completed"
    completed: bool = False  # Completion flag
    completion_date: Optional[datetime] = None  # When completed


@dataclass
class EmotionalContext:
    """Emotional context for goal tracking"""
    primary: str                    # Primary emotion (e.g., "determination")
    intensity: float                # 0.0 to 1.0 (how strong)
    secondary: List[str] = field(default_factory=list)  # Secondary emotions
    description: Optional[str] = None  # Textual description


@dataclass
class GoalTimelineNode:
    """
    Goal as a timeline node with complete temporal consciousness
    
    This model transforms static GOAL_TREE.yaml entries into living
    temporal entities that track their complete lifecycle.
    """
    
    # ========================================
    # IDENTITY
    # ========================================
    node_id: str              # Unique timeline node ID (e.g., "goal-1730799234.567-OBJ-01")
    goal_id: str              # Goal identifier from GOAL_TREE.yaml (e.g., "OBJ-01")
    name: str                 # Goal name (human-readable)
    description: str          # Complete goal description
    
    # ========================================
    # SEQUENTIAL ORDERING (Temporal Consciousness)
    # ========================================
    created_sequence: int     # Sequence when created (PAST)
    current_sequence: int     # Current sequence position (PRESENT)
    target_sequence: int      # Target completion sequence (FUTURE)
    
    # ========================================
    # STATUS TRACKING (Present State)
    # ========================================
    status: GoalStatus = GoalStatus.PLANNED
    progress: float = 0.0     # 0.0 to 1.0 (percentage complete)
    confidence: float = 0.0   # VIF confidence in completion (0.0 to 1.0)
    priority: GoalPriority = GoalPriority.MEDIUM
    
    # ========================================
    # TEMPORAL TIMESTAMPS
    # ========================================
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None    # Set when status → in_progress
    updated_at: datetime = field(default_factory=datetime.now)
    target_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None  # Set when status → completed
    
    # ========================================
    # KEY RESULTS (OKR Pattern)
    # ========================================
    key_results: List[KeyResult] = field(default_factory=list)
    completed_krs: int = 0    # Count of completed key results
    total_krs: int = 0        # Total key result count
    
    # ========================================
    # EMOTIONAL CONTEXT (Consciousness)
    # ========================================
    emotional_context: Optional[EmotionalContext] = None
    
    # ========================================
    # INTEGRATION (Bidirectional Links)
    # ========================================
    linked_goals: List[str] = field(default_factory=list)  # Related goal IDs
    artifacts: List[str] = field(default_factory=list)      # Code/docs/tests
    evidence: List[str] = field(default_factory=list)       # Validation proofs
    
    # ========================================
    # METADATA
    # ========================================
    metadata: Dict[str, Any] = field(default_factory=dict)  # Flexible extension
```

### Field Explanations

#### Identity Fields

**`node_id`** (str):
- Unique identifier for the timeline node
- Format: `goal-{timestamp}-{goal_id}`
- Example: `"goal-1730799234.567-OBJ-01"`
- Used for: Timeline storage, CMC atoms, HHNI indexing

**`goal_id`** (str):
- Goal identifier from GOAL_TREE.yaml
- Format: `OBJ-{number}` (e.g., "OBJ-01", "OBJ-12")
- Used for: GOAL_TREE sync, cross-references
- Must be unique across all goals

**`name`** (str):
- Human-readable goal name
- Example: "Implement Timeline-Goals Visualization"
- Displayed in: UI, dashboards, reports
- Synced to: GOAL_TREE.yaml

**`description`** (str):
- Complete goal description
- Can be multi-line, detailed
- Example: "Build interactive temporal consciousness graph showing Past/Present/Future"
- Synced to: GOAL_TREE.yaml

#### Sequential Ordering Fields

**`created_sequence`** (int):
- **PAST:** Sequence number when goal was created
- Assigned from global sequence counter at creation time
- Never changes (permanent creation record)
- Used for: "When was this goal created?" queries

**`current_sequence`** (int):
- **PRESENT:** Current sequence position
- Updated every time goal is modified (progress, status, etc.)
- Tracks goal's journey through time
- Used for: "Where is this goal now?" queries

**`target_sequence`** (int):
- **FUTURE:** Target sequence for completion
- Can be estimated or exact
- Provides temporal planning context
- Used for: "When should this complete?" queries

**Example Timeline:**
```
Goal created at sequence 1
Progress update at sequence 5  (current_sequence = 5)
Progress update at sequence 12 (current_sequence = 12)
Progress update at sequence 18 (current_sequence = 18)
Target completion at sequence 30

Query: "What was this goal's progress at sequence 12?"
Answer: Can retrieve exact state at sequence 12
```

#### Status Tracking Fields

**`status`** (GoalStatus):
- Current goal status
- Values: PLANNED | IN_PROGRESS | COMPLETED | BLOCKED | CANCELLED
- Automatic timestamp management on transitions
- Synced to: GOAL_TREE.yaml

**Status Transition Logic:**
```python
PLANNED → IN_PROGRESS: Sets started_at timestamp
IN_PROGRESS → COMPLETED: Sets actual_completion timestamp, progress = 1.0
IN_PROGRESS → BLOCKED: Preserves current progress
BLOCKED → IN_PROGRESS: Resumes from preserved progress
ANY → CANCELLED: Sets actual_completion (failed state)
```

**`progress`** (float):
- Completion percentage (0.0 to 1.0)
- Can be manual or calculated from key results
- Validation: Must be between 0.0 and 1.0
- Synced to: GOAL_TREE.yaml as `completion_percentage` (0-100)

**`confidence`** (float):
- VIF confidence score for completion likelihood
- 0.0 to 1.0 (0% to 100% confident)
- Updated via VIF integration
- Not synced to GOAL_TREE.yaml (timeline-specific)

**`priority`** (GoalPriority):
- Goal priority level
- Values: CRITICAL | HIGH | MEDIUM | LOW
- Synced to: GOAL_TREE.yaml as `priority_tier`
- Used for: Priority-based queries and sorting

#### Temporal Timestamp Fields

**`created_at`** (datetime):
- Exact timestamp when goal was created
- ISO 8601 format in storage
- Automatic (set on creation)
- Never changes

**`started_at`** (Optional[datetime]):
- Timestamp when goal moved to IN_PROGRESS
- None if status never reached IN_PROGRESS
- Set automatically on status transition
- Important for: Cycle time analysis

**`updated_at`** (datetime):
- Timestamp of last update (any field change)
- Updated automatically on every modification
- Used for: Tracking activity, staleness detection

**`target_completion`** (Optional[datetime]):
- Target date for goal completion (if date-based)
- Optional (can use target_sequence instead)
- Human-set, not automatic
- Synced to: GOAL_TREE.yaml

**`actual_completion`** (Optional[datetime]):
- Actual completion timestamp
- Set when status → COMPLETED or CANCELLED
- None if goal not yet complete
- Used for: Retrospective analysis, velocity calculation

#### Key Results Fields

**`key_results`** (List[KeyResult]):
- List of key results (OKR pattern)
- Each KR has: id, name, metric, target, status, completed, completion_date
- Example:
```python
[
    KeyResult(
        id="KR-1.1",
        name="All tests passing",
        metric="Test pass rate",
        target="100%",
        status="completed",
        completed=True,
        completion_date=datetime(2025, 11, 1)
    )
]
```

**`completed_krs`** (int):
- Count of completed key results
- Auto-incremented when KR marked complete
- Used for: Progress calculation

**`total_krs`** (int):
- Total count of key results
- Auto-incremented when KR added
- Used for: Progress calculation (completed_krs / total_krs)

#### Emotional Context Fields

**`emotional_context`** (Optional[EmotionalContext]):
- Emotional state during goal lifecycle
- Captures consciousness beyond metrics
- Example:
```python
EmotionalContext(
    primary="determination",     # Main emotion
    intensity=0.85,              # How strong (0.0-1.0)
    secondary=["excitement", "focus"],  # Additional emotions
    description="Highly motivated to ship this feature"
)
```

**Why This Matters:**
- Goals aren't just metrics—they have emotional context
- "Why did I create this goal?" → See emotional state
- "What was I feeling when progress stalled?" → See emotional context at that sequence
- Consciousness preservation across sessions

#### Integration Fields

**`linked_goals`** (List[str]):
- IDs of related/dependent goals
- Bidirectional: If A links to B, B should link to A
- Used for: Dependency analysis, goal clustering
- Example: `["OBJ-02", "OBJ-05"]`

**`artifacts`** (List[str]):
- Paths to code/docs/tests created for this goal
- Example: `["packages/vif/witness.py", "knowledge_architecture/systems/vif/T3_detailed.md"]`
- Used for: Provenance tracking, "what did we build for this goal?"

**`evidence`** (List[str]):
- Paths to validation/proof of goal achievement
- Example: `["packages/vif/tests/test_witness.py", "CI_RESULTS_2025-11-01.txt"]`
- Used for: Quality assurance, "how do we know this goal is complete?"

**`metadata`** (Dict[str, Any]):
- Flexible dictionary for extensions
- Stores milestones, notes, custom fields
- Example:
```python
{
    "milestones": [
        {"timestamp": "2025-10-25T14:30", "progress": 0.25, "description": "Data models complete"},
        {"timestamp": "2025-10-30T16:45", "progress": 0.65, "description": "Sync implemented"}
    ],
    "tags": ["infrastructure", "critical-path"],
    "dependencies": ["CMC must be production-ready"],
    "risk_factors": ["Complexity: Medium", "Dependencies: 2"]
}
```

---

### Instance Methods

#### update_progress()

**Purpose:** Update goal progress with optional milestone

**Signature:**
```python
def update_progress(self, progress: float, milestone: Optional[str] = None) -> None
```

**Implementation:**
```python
def update_progress(self, progress: float, milestone: Optional[str] = None) -> None:
    """
    Update goal progress
    
    Args:
        progress: New progress value (0.0 to 1.0)
        milestone: Optional milestone description
        
    Raises:
        ValueError: If progress not in range [0.0, 1.0]
    """
    # Validate progress range
    if not 0.0 <= progress <= 1.0:
        raise ValueError("Progress must be between 0.0 and 1.0")
    
    # Update progress
    self.progress = progress
    self.updated_at = datetime.now()
    
    # Add milestone to metadata if provided
    if milestone:
        if 'milestones' not in self.metadata:
            self.metadata['milestones'] = []
        
        self.metadata['milestones'].append({
            'timestamp': datetime.now().isoformat(),
            'progress': progress,
            'description': milestone
        })
```

**Usage Example:**
```python
goal = GoalTimelineNode(...)
goal.update_progress(0.65, "Data models enhanced, graph queries implemented")

# Result:
# - goal.progress = 0.65
# - goal.updated_at = now
# - goal.metadata['milestones'] = [..., {timestamp, progress: 0.65, description}]
```

---

#### update_status()

**Purpose:** Update goal status with automatic timestamp management

**Signature:**
```python
def update_status(self, status: GoalStatus) -> None
```

**Implementation:**
```python
def update_status(self, status: GoalStatus) -> None:
    """
    Update goal status with automatic timestamp management
    
    Args:
        status: New goal status
        
    Side Effects:
        - Sets started_at when transitioning to IN_PROGRESS
        - Sets actual_completion when transitioning to COMPLETED
        - Sets progress = 1.0 when COMPLETED
    """
    # Update status
    self.status = status
    self.updated_at = datetime.now()
    
    # Automatic timestamp management
    if status == GoalStatus.IN_PROGRESS and self.started_at is None:
        self.started_at = datetime.now()
    
    if status == GoalStatus.COMPLETED:
        self.actual_completion = datetime.now()
        self.progress = 1.0  # Auto-complete
```

**Status Transition Examples:**
```python
# Scenario 1: Start working on planned goal
goal.update_status(GoalStatus.IN_PROGRESS)
# Result:
# - status = IN_PROGRESS
# - started_at = now (first time only)
# - updated_at = now

# Scenario 2: Complete goal
goal.update_status(GoalStatus.COMPLETED)
# Result:
# - status = COMPLETED
# - actual_completion = now
# - progress = 1.0 (automatic)
# - updated_at = now

# Scenario 3: Block goal
goal.update_status(GoalStatus.BLOCKED)
# Result:
# - status = BLOCKED
# - progress preserved (can resume later)
# - updated_at = now
```

---

#### Key Result Management

**add_key_result()** - Add new key result:
```python
def add_key_result(self, kr: KeyResult) -> None:
    """Add a key result to the goal"""
    self.key_results.append(kr)
    self.total_krs += 1
```

**complete_key_result()** - Mark KR as completed:
```python
def complete_key_result(self, kr_id: str) -> None:
    """Mark a key result as completed"""
    for kr in self.key_results:
        if kr.id == kr_id:
            kr.completed = True
            kr.status = "completed"
            kr.completion_date = datetime.now()
            self.completed_krs += 1
            # Auto-update goal progress based on KR completion
            self.update_progress(self._calculate_progress_from_krs())
            break

def _calculate_progress_from_krs(self) -> float:
    """Calculate progress based on completed key results"""
    if self.total_krs == 0:
        return 0.0
    return self.completed_krs / self.total_krs
```

**Usage Example:**
```python
# Add key results
goal.add_key_result(KeyResult(
    id="KR-12.1",
    name="Data models enhanced",
    metric="Models complete",
    target="100%"
))
goal.add_key_result(KeyResult(
    id="KR-12.2",
    name="Graph queries implemented",
    metric="Queries working",
    target="100%"
))

# Total: 2 KRs, 0 completed → progress = 0.0

# Complete first KR
goal.complete_key_result("KR-12.1")
# Result: 1 completed, 2 total → progress = 0.5 (auto-calculated!)

# Complete second KR
goal.complete_key_result("KR-12.2")
# Result: 2 completed, 2 total → progress = 1.0 (auto-calculated!)
```

---

#### Serialization Methods

**to_dict()** - Convert to dictionary:
```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary for JSON serialization"""
    return {
        'node_id': self.node_id,
        'goal_id': self.goal_id,
        'name': self.name,
        'description': self.description,
        'created_sequence': self.created_sequence,
        'current_sequence': self.current_sequence,
        'target_sequence': self.target_sequence,
        'status': self.status.value,
        'progress': self.progress,
        'confidence': self.confidence,
        'priority': self.priority.value,
        'created_at': self.created_at.isoformat(),
        'started_at': self.started_at.isoformat() if self.started_at else None,
        'updated_at': self.updated_at.isoformat(),
        'target_completion': self.target_completion.isoformat() if self.target_completion else None,
        'actual_completion': self.actual_completion.isoformat() if self.actual_completion else None,
        'key_results': [
            {
                'id': kr.id,
                'name': kr.name,
                'metric': kr.metric,
                'target': kr.target,
                'status': kr.status,
                'completed': kr.completed,
                'completion_date': kr.completion_date.isoformat() if kr.completion_date else None
            }
            for kr in self.key_results
        ],
        'completed_krs': self.completed_krs,
        'total_krs': self.total_krs,
        'emotional_context': {
            'primary': self.emotional_context.primary,
            'intensity': self.emotional_context.intensity,
            'secondary': self.emotional_context.secondary,
            'description': self.emotional_context.description
        } if self.emotional_context else None,
        'linked_goals': self.linked_goals,
        'artifacts': self.artifacts,
        'evidence': self.evidence,
        'metadata': self.metadata
    }
```

**from_dict()** - Create from dictionary:
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> GoalTimelineNode:
    """
    Create GoalTimelineNode from dictionary
    
    Args:
        data: Dictionary with goal data (from JSON)
        
    Returns:
        Reconstructed GoalTimelineNode instance
    """
    # Create base goal
    goal = cls(
        node_id=data['node_id'],
        goal_id=data['goal_id'],
        name=data['name'],
        description=data['description'],
        created_sequence=data['created_sequence'],
        current_sequence=data['current_sequence'],
        target_sequence=data['target_sequence'],
        status=GoalStatus(data['status']),
        progress=data['progress'],
        confidence=data['confidence'],
        priority=GoalPriority(data['priority']),
        created_at=datetime.fromisoformat(data['created_at']),
        started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
        updated_at=datetime.fromisoformat(data['updated_at']),
        target_completion=datetime.fromisoformat(data['target_completion']) if data.get('target_completion') else None,
        actual_completion=datetime.fromisoformat(data['actual_completion']) if data.get('actual_completion') else None,
        completed_krs=data['completed_krs'],
        total_krs=data['total_krs'],
        linked_goals=data.get('linked_goals', []),
        artifacts=data.get('artifacts', []),
        evidence=data.get('evidence', []),
        metadata=data.get('metadata', {})
    )
    
    # Reconstruct key results
    for kr_data in data.get('key_results', []):
        goal.add_key_result(KeyResult(
            id=kr_data['id'],
            name=kr_data['name'],
            metric=kr_data['metric'],
            target=kr_data['target'],
            status=kr_data['status'],
            completed=kr_data['completed'],
            completion_date=datetime.fromisoformat(kr_data['completion_date']) if kr_data.get('completion_date') else None
        ))
    
    # Reconstruct emotional context
    if data.get('emotional_context'):
        ec_data = data['emotional_context']
        goal.emotional_context = EmotionalContext(
            primary=ec_data['primary'],
            intensity=ec_data['intensity'],
            secondary=ec_data.get('secondary', []),
            description=ec_data.get('description')
        )
    
    return goal
```

---

## GoalTimelineManager Implementation

### Class Structure

**File:** `packages/timeline_context_system/goal_timeline_manager.py`

**Complete Class:**

```python
from __future__ import annotations
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class GoalTimelineManager:
    """
    Manages goals as timeline nodes with bidirectional sync to GOAL_TREE.yaml
    
    Responsibilities:
    - Goal lifecycle management (create, update, query, complete)
    - Bidirectional synchronization with GOAL_TREE.yaml
    - Sequential ordering system
    - Persistence to timeline storage (JSON)
    - Integration with CMC, HHNI, VIF
    """
    
    def __init__(self, goals_dir: str = "goals", timeline_dir: str = "timeline_goals"):
        """
        Initialize GoalTimelineManager
        
        Args:
            goals_dir: Directory containing GOAL_TREE.yaml (default: "goals")
            timeline_dir: Directory for timeline storage (default: "timeline_goals")
        """
        self.goals_dir = Path(goals_dir)
        self.timeline_dir = Path(timeline_dir)
        
        # Create timeline directory if doesn't exist
        self.timeline_dir.mkdir(exist_ok=True, parents=True)
        
        # In-memory storage for active goals
        self.goals: Dict[str, GoalTimelineNode] = {}
        
        # Global sequence counter
        self.sequence_counter = 0
        
        # Load existing goals from timeline storage
        self._load_existing_goals()
    
    def _load_existing_goals(self) -> None:
        """
        Load existing goals from timeline storage
        
        Scans timeline_goals/ directory for goal_*.json files,
        deserializes them, and loads into memory.
        Updates sequence_counter to highest sequence found.
        """
        timeline_files = list(self.timeline_dir.glob("goal_*.json"))
        
        for file_path in timeline_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    goal = GoalTimelineNode.from_dict(data)
                    self.goals[goal.goal_id] = goal
                    
                    # Update sequence counter (max sequence + 1)
                    if goal.created_sequence >= self.sequence_counter:
                        self.sequence_counter = goal.created_sequence + 1
                    if goal.current_sequence >= self.sequence_counter:
                        self.sequence_counter = goal.current_sequence + 1
                        
            except Exception as e:
                print(f"Warning: Failed to load goal from {file_path}: {e}")
        
        print(f"[GoalTimelineManager] Loaded {len(self.goals)} goals, sequence_counter = {self.sequence_counter}")
```

---

### Goal Creation

**Method: create_goal()**

**Complete Implementation:**

```python
def create_goal(
    self,
    goal_id: str,
    name: str,
    description: str,
    target_sequence: Optional[int] = None,
    priority: GoalPriority = GoalPriority.MEDIUM,
    key_results: Optional[List[Dict[str, Any]]] = None,
    emotional_context: Optional[Dict[str, Any]] = None,
    artifacts: Optional[List[str]] = None,
    evidence: Optional[List[str]] = None
) -> GoalTimelineNode:
    """
    Create a new goal in the timeline
    
    Creates goal in timeline storage and syncs to GOAL_TREE.yaml.
    
    Args:
        goal_id: Unique goal identifier (e.g., "OBJ-01")
        name: Goal name
        description: Goal description
        target_sequence: Target completion sequence (default: current + 10)
        priority: Goal priority
        key_results: List of key result dictionaries
        emotional_context: Emotional context dictionary
        artifacts: List of artifact paths
        evidence: List of evidence paths
        
    Returns:
        Created GoalTimelineNode
        
    Raises:
        ValueError: If goal_id already exists
    """
    # Check if goal already exists
    if goal_id in self.goals:
        raise ValueError(f"Goal {goal_id} already exists")
    
    # Generate node ID
    node_id = f"goal-{datetime.now().timestamp()}-{goal_id}"
    
    # Set sequences
    current_sequence = self.sequence_counter
    self.sequence_counter += 1
    target_seq = target_sequence if target_sequence else current_sequence + 10
    
    # Parse key results
    krs = []
    if key_results:
        for kr_data in key_results:
            krs.append(KeyResult(
                id=kr_data.get('id', f"KR-{goal_id}-{len(krs)+1}"),
                name=kr_data['name'],
                metric=kr_data.get('metric', ''),
                target=kr_data.get('target', ''),
                status=kr_data.get('status', 'pending'),
                completed=kr_data.get('completed', False),
                completion_date=None
            ))
    
    # Parse emotional context
    em_ctx = None
    if emotional_context:
        em_ctx = EmotionalContext(
            primary=emotional_context['primary'],
            intensity=emotional_context['intensity'],
            secondary=emotional_context.get('secondary', []),
            description=emotional_context.get('description')
        )
    
    # Create goal node
    goal = GoalTimelineNode(
        node_id=node_id,
        goal_id=goal_id,
        name=name,
        description=description,
        created_sequence=current_sequence,
        current_sequence=current_sequence,
        target_sequence=target_seq,
        status=GoalStatus.PLANNED,
        progress=0.0,
        priority=priority,
        key_results=krs,
        total_krs=len(krs),
        completed_krs=0,
        emotional_context=em_ctx,
        artifacts=artifacts or [],
        evidence=evidence or []
    )
    
    # Store in memory
    self.goals[goal_id] = goal
    
    # Save to timeline storage
    self._save_goal(goal)
    
    # Sync to GOAL_TREE.yaml
    self.sync_to_goal_tree(goal_id)
    
    print(f"[GoalTimelineManager] Created goal {goal_id} at sequence {current_sequence}")
    
    return goal
```

**Usage Example:**
```python
manager = GoalTimelineManager()

goal = manager.create_goal(
    goal_id="OBJ-12",
    name="Implement Timeline-Goals Visualization",
    description="Build interactive temporal consciousness graph showing Past/Present/Future",
    target_sequence=50,
    priority=GoalPriority.HIGH,
    key_results=[
        {
            "id": "KR-12.1",
            "name": "Data models enhanced",
            "metric": "Models complete",
            "target": "100%"
        },
        {
            "id": "KR-12.2",
            "name": "Graph queries working",
            "metric": "Queries functional",
            "target": "100%"
        }
    ],
    emotional_context={
        "primary": "excitement",
        "intensity": 0.9,
        "secondary": ["determination", "focus"],
        "description": "This is a killer feature!"
    },
    artifacts=[],
    evidence=[]
)

print(f"Created {goal.goal_id} with {goal.total_krs} key results")
# Output: Created OBJ-12 with 2 key results
```

---

### Progress Updates

**Method: update_progress()**

```python
def update_progress(
    self,
    goal_id: str,
    progress: float,
    milestone: Optional[str] = None,
    emotional_context: Optional[Dict[str, Any]] = None
) -> GoalTimelineNode:
    """
    Update goal progress
    
    Updates progress, increments current_sequence, saves to storage,
    and syncs to GOAL_TREE.yaml.
    
    Args:
        goal_id: Goal to update
        progress: New progress (0.0 to 1.0)
        milestone: Optional milestone description
        emotional_context: Optional emotional context update
        
    Returns:
        Updated GoalTimelineNode
        
    Raises:
        KeyError: If goal_id not found
    """
    # Get goal
    goal = self.goals.get(goal_id)
    if not goal:
        raise KeyError(f"Goal {goal_id} not found")
    
    # Update progress
    goal.update_progress(progress, milestone)
    
    # Increment sequence (progress is temporal event)
    goal.current_sequence = self.sequence_counter
    self.sequence_counter += 1
    
    # Update emotional context if provided
    if emotional_context:
        goal.emotional_context = EmotionalContext(
            primary=emotional_context['primary'],
            intensity=emotional_context['intensity'],
            secondary=emotional_context.get('secondary', []),
            description=emotional_context.get('description')
        )
    
    # Save to timeline storage
    self._save_goal(goal)
    
    # Sync to GOAL_TREE.yaml
    self.sync_to_goal_tree(goal_id)
    
    print(f"[GoalTimelineManager] Updated {goal_id} progress to {progress} at sequence {goal.current_sequence}")
    
    return goal
```

**Usage Example:**
```python
# Update progress with milestone
goal = manager.update_progress(
    goal_id="OBJ-12",
    progress=0.65,
    milestone="Data models enhanced, graph queries implemented",
    emotional_context={
        "primary": "pride",
        "intensity": 0.85,
        "description": "Making excellent progress!"
    }
)

# Result:
# - progress = 0.65
# - current_sequence incremented
# - milestone added to metadata
# - emotional context updated
# - Saved to timeline_goals/goal_OBJ-12.json
# - Synced to goals/GOAL_TREE.yaml (completion_percentage = 65)
```

---

### Status Updates

**Method: update_status()**

```python
def update_status(
    self,
    goal_id: str,
    status: GoalStatus,
    emotional_context: Optional[Dict[str, Any]] = None
) -> GoalTimelineNode:
    """
    Update goal status
    
    Args:
        goal_id: Goal to update
        status: New goal status
        emotional_context: Optional emotional context
        
    Returns:
        Updated GoalTimelineNode
    """
    goal = self.goals.get(goal_id)
    if not goal:
        raise KeyError(f"Goal {goal_id} not found")
    
    # Update status (automatic timestamp management)
    goal.update_status(status)
    
    # Update emotional context if provided
    if emotional_context:
        goal.emotional_context = EmotionalContext(
            primary=emotional_context['primary'],
            intensity=emotional_context['intensity'],
            secondary=emotional_context.get('secondary', []),
            description=emotional_context.get('description')
        )
    
    # Increment sequence
    goal.current_sequence = self.sequence_counter
    self.sequence_counter += 1
    
    # Save
    self._save_goal(goal)
    
    # Sync to GOAL_TREE.yaml
    self.sync_to_goal_tree(goal_id)
    
    print(f"[GoalTimelineManager] Updated {goal_id} status to {status.value}")
    
    return goal
```

---

### Query System

**Method: query_goals()**

```python
def query_goals(
    self,
    status: Optional[GoalStatus] = None,
    priority: Optional[GoalPriority] = None,
    sequence_from: Optional[int] = None,
    sequence_to: Optional[int] = None,
    tags: Optional[List[str]] = None
) -> List[GoalTimelineNode]:
    """
    Query goals with multiple filter criteria
    
    Args:
        status: Filter by goal status (optional)
        priority: Filter by priority level (optional)
        sequence_from: Minimum created_sequence (inclusive, optional)
        sequence_to: Maximum created_sequence (inclusive, optional)
        tags: Filter by tags in metadata (optional)
        
    Returns:
        List of GoalTimelineNodes matching all criteria
        
    Examples:
        # Get all in-progress goals
        in_progress = manager.query_goals(status=GoalStatus.IN_PROGRESS)
        
        # Get critical priority goals
        critical = manager.query_goals(priority=GoalPriority.CRITICAL)
        
        # Get goals created in early sequences
        early = manager.query_goals(sequence_from=1, sequence_to=10)
        
        # Get infrastructure goals
        infra = manager.query_goals(tags=["infrastructure"])
    """
    results = []
    
    for goal in self.goals.values():
        # Filter by status
        if status is not None and goal.status != status:
            continue
        
        # Filter by priority
        if priority is not None and goal.priority != priority:
            continue
        
        # Filter by sequence range
        if sequence_from is not None and goal.created_sequence < sequence_from:
            continue
        if sequence_to is not None and goal.created_sequence > sequence_to:
            continue
        
        # Filter by tags
        if tags is not None:
            goal_tags = goal.metadata.get('tags', [])
            if not any(tag in goal_tags for tag in tags):
                continue
        
        results.append(goal)
    
    return results
```

**Query Examples:**

```python
# Example 1: Get all active work
active_work = manager.query_goals(status=GoalStatus.IN_PROGRESS)
print(f"Currently working on {len(active_work)} goals")

# Example 2: Get critical priorities
critical_goals = manager.query_goals(
    priority=GoalPriority.CRITICAL,
    status=GoalStatus.IN_PROGRESS
)
print(f"Critical in-progress goals: {[g.name for g in critical_goals]}")

# Example 3: Get early goals (sequences 1-20)
early_goals = manager.query_goals(sequence_from=1, sequence_to=20)
print(f"Early goals: {[g.goal_id for g in early_goals]}")

# Example 4: Get infrastructure goals
infra_goals = manager.query_goals(tags=["infrastructure", "critical-path"])
print(f"Infrastructure goals: {[g.name for g in infra_goals]}")

# Example 5: Complex query - critical in-progress infrastructure goals
complex = manager.query_goals(
    status=GoalStatus.IN_PROGRESS,
    priority=GoalPriority.CRITICAL,
    tags=["infrastructure"]
)
print(f"Critical infra work: {[g.name for g in complex]}")
```

---

## Bidirectional Sync Implementation

### Sync Direction 1: YAML → Timeline

**Method: sync_from_goal_tree()**

**Complete Implementation:**

```python
def sync_from_goal_tree(self) -> int:
    """
    Sync FROM GOAL_TREE.yaml TO timeline
    
    Imports goals from GOAL_TREE.yaml into timeline storage.
    Creates new timeline nodes for new goals, updates existing nodes.
    
    Returns:
        Number of goals synced
        
    Raises:
        FileNotFoundError: If GOAL_TREE.yaml doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    goal_tree_path = self.goals_dir / "GOAL_TREE.yaml"
    
    if not goal_tree_path.exists():
        raise FileNotFoundError(f"GOAL_TREE.yaml not found at {goal_tree_path}")
    
    # Load GOAL_TREE.yaml
    with open(goal_tree_path, 'r') as f:
        goal_tree = yaml.safe_load(f)
    
    synced_count = 0
    
    # Process each objective
    objectives = goal_tree.get('objectives', {})
    for obj_id, obj_data in objectives.items():
        if obj_id in self.goals:
            # Goal exists - update from YAML
            goal = self.goals[obj_id]
            
            # Update fields that can change in YAML
            goal.name = obj_data.get('name', goal.name)
            goal.description = obj_data.get('description', goal.description)
            goal.status = GoalStatus(obj_data.get('status', 'planned'))
            goal.progress = obj_data.get('completion_percentage', 0) / 100.0
            
            # Update priority if present
            if 'priority_tier' in obj_data:
                priority_map = {
                    'S': GoalPriority.CRITICAL,
                    'A': GoalPriority.HIGH,
                    'B': GoalPriority.MEDIUM,
                    'C': GoalPriority.LOW
                }
                goal.priority = priority_map.get(obj_data['priority_tier'], GoalPriority.MEDIUM)
            
            # Update key results
            if 'key_results' in obj_data:
                goal.key_results = []
                goal.total_krs = 0
                goal.completed_krs = 0
                for kr_data in obj_data['key_results']:
                    kr = KeyResult(
                        id=kr_data.get('id', f"KR-{obj_id}-{len(goal.key_results)+1}"),
                        name=kr_data.get('name', kr_data.get('description', '')),
                        metric=kr_data.get('metric', ''),
                        target=kr_data.get('target', ''),
                        status=kr_data.get('status', 'pending'),
                        completed=kr_data.get('completed', False)
                    )
                    goal.add_key_result(kr)
            
            # Preserve timeline-specific data (sequences, emotional context, timestamps)
            # These are NOT overwritten from YAML
            
            # Increment sequence (update event)
            goal.current_sequence = self.sequence_counter
            self.sequence_counter += 1
            goal.updated_at = datetime.now()
            
        else:
            # New goal - create timeline node
            goal = self._create_from_yaml(obj_id, obj_data)
            self.goals[obj_id] = goal
        
        # Save to timeline storage
        self._save_goal(goal)
        synced_count += 1
    
    print(f"[GoalTimelineManager] Synced {synced_count} goals from GOAL_TREE.yaml")
    return synced_count


def _create_from_yaml(self, goal_id: str, obj_data: Dict[str, Any]) -> GoalTimelineNode:
    """
    Create GoalTimelineNode from GOAL_TREE.yaml objective
    
    Helper method for sync_from_goal_tree()
    """
    # Generate node ID
    node_id = f"goal-{datetime.now().timestamp()}-{goal_id}"
    
    # Parse status
    status_str = obj_data.get('status', 'planned')
    status = GoalStatus(status_str) if status_str in [s.value for s in GoalStatus] else GoalStatus.PLANNED
    
    # Parse priority
    priority_map = {
        'S': GoalPriority.CRITICAL,
        'A': GoalPriority.HIGH,
        'B': GoalPriority.MEDIUM,
        'C': GoalPriority.LOW
    }
    priority = priority_map.get(obj_data.get('priority_tier'), GoalPriority.MEDIUM)
    
    # Set sequences
    current_seq = self.sequence_counter
    self.sequence_counter += 1
    target_seq = obj_data.get('target_sequence', current_seq + 10)
    
    # Parse key results
    krs = []
    if 'key_results' in obj_data:
        for kr_data in obj_data['key_results']:
            krs.append(KeyResult(
                id=kr_data.get('id', f"KR-{goal_id}-{len(krs)+1}"),
                name=kr_data.get('name', kr_data.get('description', '')),
                metric=kr_data.get('metric', ''),
                target=kr_data.get('target', ''),
                status=kr_data.get('status', 'pending'),
                completed=kr_data.get('completed', False)
            ))
    
    # Create goal
    goal = GoalTimelineNode(
        node_id=node_id,
        goal_id=goal_id,
        name=obj_data.get('name', goal_id),
        description=obj_data.get('description', ''),
        created_sequence=current_seq,
        current_sequence=current_seq,
        target_sequence=target_seq,
        status=status,
        progress=obj_data.get('completion_percentage', 0) / 100.0,
        priority=priority,
        key_results=krs,
        total_krs=len(krs),
        completed_krs=sum(1 for kr in krs if kr.completed)
    )
    
    return goal
```

---

### Sync Direction 2: Timeline → YAML

**Method: sync_to_goal_tree()**

**Complete Implementation:**

```python
def sync_to_goal_tree(self, goal_id: str) -> bool:
    """
    Sync FROM timeline TO GOAL_TREE.yaml
    
    Exports goal from timeline to GOAL_TREE.yaml, preserving YAML structure.
    Only syncs fields that are relevant to YAML (omits timeline-specific data).
    
    Args:
        goal_id: Goal to sync
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        KeyError: If goal_id not found in timeline
    """
    goal = self.goals.get(goal_id)
    if not goal:
        raise KeyError(f"Goal {goal_id} not found in timeline")
    
    goal_tree_path = self.goals_dir / "GOAL_TREE.yaml"
    
    # Load existing GOAL_TREE.yaml
    if goal_tree_path.exists():
        with open(goal_tree_path, 'r') as f:
            goal_tree = yaml.safe_load(f) or {}
    else:
        goal_tree = {}
    
    # Ensure objectives section exists
    if 'objectives' not in goal_tree:
        goal_tree['objectives'] = {}
    
    # Convert priority to tier
    priority_tier_map = {
        GoalPriority.CRITICAL: 'S',
        GoalPriority.HIGH: 'A',
        GoalPriority.MEDIUM: 'B',
        GoalPriority.LOW: 'C'
    }
    
    # Build objective dict (only YAML-relevant fields)
    objective_dict = {
        'name': goal.name,
        'description': goal.description,
        'status': goal.status.value,
        'completion_percentage': int(goal.progress * 100),
        'priority_tier': priority_tier_map[goal.priority],
        'key_results': [
            {
                'id': kr.id,
                'name': kr.name,
                'metric': kr.metric,
                'target': kr.target,
                'status': kr.status,
                'completed': kr.completed
            }
            for kr in goal.key_results
        ]
    }
    
    # Add optional fields if present
    if goal.target_completion:
        objective_dict['target_date'] = goal.target_completion.isoformat()
    
    if goal.artifacts:
        objective_dict['artifacts'] = goal.artifacts
    
    if goal.evidence:
        objective_dict['evidence'] = goal.evidence
    
    # Update objective in YAML
    goal_tree['objectives'][goal_id] = objective_dict
    
    # Write back to GOAL_TREE.yaml
    with open(goal_tree_path, 'w') as f:
        yaml.safe_dump(goal_tree, f, sort_keys=False, default_flow_style=False)
    
    print(f"[GoalTimelineManager] Synced {goal_id} to GOAL_TREE.yaml")
    
    return True
```

**What Gets Synced vs What Doesn't:**

**Synced TO YAML:**
- ✅ name, description
- ✅ status, completion_percentage
- ✅ priority_tier
- ✅ key_results (simplified)
- ✅ artifacts, evidence

**NOT Synced TO YAML (Timeline-Specific):**
- ❌ node_id (timeline internal)
- ❌ sequences (created/current/target - timeline concept)
- ❌ emotional_context (too complex for YAML)
- ❌ Timestamps (created_at, started_at, etc. - tracked in timeline)
- ❌ metadata (milestones, etc. - timeline-specific)

**Rationale:** Keep YAML simple and human-editable, keep timeline rich and queryable.

---

## MCP Tools Implementation

### Tool 1: create_goal_timeline_node

**Location:** `packages/lucid_mcp_server/tools/goal_timeline_tools.py` (inferred)

**Complete Implementation:**

```python
from typing import Dict, Any, Optional, List
from packages.timeline_context_system.goal_timeline_manager import GoalTimelineManager
from packages.timeline_context_system.goal_timeline_node import GoalPriority


@tool(
    name="create_goal_timeline_node",
    description="Create a new goal as a timeline node with temporal tracking"
)
def create_goal_timeline_node(
    goal_id: str,
    name: str,
    description: str,
    target_sequence: Optional[int] = None,
    priority: str = "medium",
    key_results: Optional[List[Dict[str, Any]]] = None,
    emotional_context: Optional[Dict[str, Any]] = None,
    artifacts: Optional[List[str]] = None,
    evidence: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new goal in timeline with temporal consciousness
    
    Args:
        goal_id: Unique goal identifier (e.g., "OBJ-01")
        name: Goal name
        description: Goal description
        target_sequence: Target completion sequence (optional, default: current + 10)
        priority: Priority level ("critical" | "high" | "medium" | "low")
        key_results: List of key result dictionaries (optional)
        emotional_context: Emotional context dictionary (optional)
        artifacts: List of artifact paths (optional)
        evidence: List of evidence paths (optional)
        
    Returns:
        {
            "node_id": "goal-1730799234.567-OBJ-01",
            "goal_id": "OBJ-01",
            "created_sequence": 42,
            "current_sequence": 42,
            "status": "planned",
            "progress": 0.0,
            "message": "Goal created successfully",
            "synced_to_yaml": true
        }
        
    Example:
        create_goal_timeline_node(
            goal_id="OBJ-12",
            name="Implement Visualization",
            description="Build temporal consciousness graph",
            priority="high",
            key_results=[
                {"name": "Data models", "metric": "Complete", "target": "100%"},
                {"name": "Graph queries", "metric": "Working", "target": "100%"}
            ],
            emotional_context={
                "primary": "excitement",
                "intensity": 0.9
            }
        )
    """
    try:
        # Initialize manager
        manager = GoalTimelineManager()
        
        # Parse priority
        priority_enum = GoalPriority[priority.upper()]
        
        # Create goal
        goal = manager.create_goal(
            goal_id=goal_id,
            name=name,
            description=description,
            target_sequence=target_sequence,
            priority=priority_enum,
            key_results=key_results,
            emotional_context=emotional_context,
            artifacts=artifacts,
            evidence=evidence
        )
        
        # Return result
        return {
            "success": True,
            "node_id": goal.node_id,
            "goal_id": goal.goal_id,
            "created_sequence": goal.created_sequence,
            "current_sequence": goal.current_sequence,
            "target_sequence": goal.target_sequence,
            "status": goal.status.value,
            "progress": goal.progress,
            "key_results_count": goal.total_krs,
            "message": f"Goal {goal_id} created successfully at sequence {goal.created_sequence}",
            "synced_to_yaml": True
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create goal: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error creating goal: {e}"
        }
```

---

### Tool 2: update_goal_progress

**Complete Implementation:**

```python
@tool(
    name="update_goal_progress",
    description="Update goal progress and status with timeline tracking"
)
def update_goal_progress(
    goal_id: str,
    progress: Optional[float] = None,
    status: Optional[str] = None,
    milestone: Optional[str] = None,
    emotional_context: Optional[Dict[str, Any]] = None,
    artifacts: Optional[List[str]] = None,
    evidence: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update goal progress/status with timeline tracking
    
    Args:
        goal_id: Goal to update
        progress: New progress (0.0 to 1.0, optional)
        status: New status (optional)
        milestone: Milestone description (optional)
        emotional_context: Emotional context update (optional)
        artifacts: Additional artifacts (optional)
        evidence: Additional evidence (optional)
        
    Returns:
        {
            "success": true,
            "goal_id": "OBJ-01",
            "old_progress": 0.45,
            "new_progress": 0.65,
            "old_sequence": 15,
            "new_sequence": 23,
            "status": "in_progress",
            "message": "Goal progress updated",
            "synced_to_yaml": true
        }
        
    Example:
        update_goal_progress(
            goal_id="OBJ-12",
            progress=0.65,
            milestone="Data models enhanced, graph queries implemented",
            emotional_context={
                "primary": "pride",
                "intensity": 0.85
            }
        )
    """
    try:
        manager = GoalTimelineManager()
        
        # Get current state for comparison
        old_goal = manager.goals.get(goal_id)
        if not old_goal:
            return {
                "success": False,
                "error": f"Goal {goal_id} not found",
                "message": f"Goal {goal_id} does not exist in timeline"
            }
        
        old_progress = old_goal.progress
        old_sequence = old_goal.current_sequence
        
        # Update progress if provided
        if progress is not None:
            goal = manager.update_progress(
                goal_id=goal_id,
                progress=progress,
                milestone=milestone,
                emotional_context=emotional_context
            )
        else:
            goal = old_goal
        
        # Update status if provided
        if status is not None:
            goal = manager.update_status(
                goal_id=goal_id,
                status=GoalStatus(status),
                emotional_context=emotional_context
            )
        
        # Add artifacts if provided
        if artifacts:
            for artifact in artifacts:
                goal.add_artifact(artifact)
            manager._save_goal(goal)
            manager.sync_to_goal_tree(goal_id)
        
        # Add evidence if provided
        if evidence:
            for ev in evidence:
                goal.add_evidence(ev)
            manager._save_goal(goal)
            manager.sync_to_goal_tree(goal_id)
        
        # Return result
        return {
            "success": True,
            "goal_id": goal.goal_id,
            "old_progress": old_progress,
            "new_progress": goal.progress,
            "old_sequence": old_sequence,
            "new_sequence": goal.current_sequence,
            "status": goal.status.value,
            "milestones_count": len(goal.metadata.get('milestones', [])),
            "artifacts_count": len(goal.artifacts),
            "evidence_count": len(goal.evidence),
            "message": f"Goal {goal_id} updated successfully",
            "synced_to_yaml": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update goal: {e}"
        }
```

---

### Tool 3: query_goal_timeline

**Complete Implementation:**

```python
@tool(
    name="query_goal_timeline",
    description="Query goals with temporal and status filters"
)
def query_goal_timeline(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sequence_from: Optional[int] = None,
    sequence_to: Optional[int] = None,
    tags: Optional[List[str]] = None,
    include_completed: bool = True
) -> Dict[str, Any]:
    """
    Query goals with multiple filter criteria
    
    Args:
        status: Filter by status (optional)
        priority: Filter by priority (optional)
        sequence_from: Minimum created_sequence (optional)
        sequence_to: Maximum created_sequence (optional)
        tags: Filter by tags (optional)
        include_completed: Include completed goals (default: true)
        
    Returns:
        {
            "goals": [
                {
                    "goal_id": "OBJ-01",
                    "name": "...",
                    "status": "in_progress",
                    "progress": 0.65,
                    "created_sequence": 1,
                    "current_sequence": 15,
                    ...
                }
            ],
            "count": 2,
            "filters_applied": ["status=in_progress", "sequence_from=1"]
        }
        
    Example:
        # Get all in-progress high-priority goals
        query_goal_timeline(
            status="in_progress",
            priority="high"
        )
    """
    try:
        manager = GoalTimelineManager()
        
        # Build filter kwargs
        filter_kwargs = {}
        filters_applied = []
        
        if status:
            filter_kwargs['status'] = GoalStatus(status)
            filters_applied.append(f"status={status}")
        
        if priority:
            filter_kwargs['priority'] = GoalPriority[priority.upper()]
            filters_applied.append(f"priority={priority}")
        
        if sequence_from is not None:
            filter_kwargs['sequence_from'] = sequence_from
            filters_applied.append(f"sequence_from={sequence_from}")
        
        if sequence_to is not None:
            filter_kwargs['sequence_to'] = sequence_to
            filters_applied.append(f"sequence_to={sequence_to}")
        
        if tags:
            filter_kwargs['tags'] = tags
            filters_applied.append(f"tags={','.join(tags)}")
        
        # Execute query
        results = manager.query_goals(**filter_kwargs)
        
        # Filter completed if requested
        if not include_completed:
            results = [g for g in results if g.status != GoalStatus.COMPLETED]
        
        # Convert to dict
        goals_data = [goal.to_dict() for goal in results]
        
        return {
            "success": True,
            "goals": goals_data,
            "count": len(goals_data),
            "filters_applied": filters_applied,
            "sequence_counter": manager.sequence_counter,
            "message": f"Found {len(goals_data)} goals matching criteria"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "goals": [],
            "count": 0,
            "message": f"Query failed: {e}"
        }
```

---

## Testing Guide

### Unit Tests

**File:** `packages/timeline_context_system/tests/test_goal_timeline_node.py`

**Test Coverage:**

**1. GoalTimelineNode Creation:**
```python
def test_goal_timeline_node_creation():
    """Test basic goal node creation"""
    goal = GoalTimelineNode(
        node_id="test-node-001",
        goal_id="TEST-01",
        name="Test Goal",
        description="Test goal description",
        created_sequence=1,
        current_sequence=1,
        target_sequence=10
    )
    
    assert goal.goal_id == "TEST-01"
    assert goal.status == GoalStatus.PLANNED
    assert goal.progress == 0.0
    assert goal.total_krs == 0
```

**2. Progress Updates:**
```python
def test_progress_updates():
    """Test progress update with milestones"""
    goal = GoalTimelineNode(...)
    
    # Update progress
    goal.update_progress(0.5, "Halfway complete")
    
    assert goal.progress == 0.5
    assert 'milestones' in goal.metadata
    assert len(goal.metadata['milestones']) == 1
    assert goal.metadata['milestones'][0]['progress'] == 0.5
```

**3. Status Transitions:**
```python
def test_status_transitions():
    """Test status transition logic"""
    goal = GoalTimelineNode(...)
    
    # Start goal
    goal.update_status(GoalStatus.IN_PROGRESS)
    assert goal.status == GoalStatus.IN_PROGRESS
    assert goal.started_at is not None
    
    # Complete goal
    goal.update_status(GoalStatus.COMPLETED)
    assert goal.status == GoalStatus.COMPLETED
    assert goal.progress == 1.0  # Auto-set
    assert goal.actual_completion is not None
```

**4. Key Result Management:**
```python
def test_key_result_completion():
    """Test key result completion and auto-progress"""
    goal = GoalTimelineNode(...)
    
    # Add 2 key results
    goal.add_key_result(KeyResult(id="KR-1", name="KR 1", metric="", target=""))
    goal.add_key_result(KeyResult(id="KR-2", name="KR 2", metric="", target=""))
    
    assert goal.total_krs == 2
    assert goal.completed_krs == 0
    assert goal.progress == 0.0
    
    # Complete first KR
    goal.complete_key_result("KR-1")
    assert goal.completed_krs == 1
    assert goal.progress == 0.5  # Auto-calculated!
    
    # Complete second KR
    goal.complete_key_result("KR-2")
    assert goal.completed_krs == 2
    assert goal.progress == 1.0  # Auto-calculated!
```

**5. Serialization:**
```python
def test_serialization_roundtrip():
    """Test to_dict() and from_dict() roundtrip"""
    original = GoalTimelineNode(...)
    original.add_key_result(KeyResult(...))
    original.emotional_context = EmotionalContext(primary="determination", intensity=0.8)
    
    # Serialize
    data = original.to_dict()
    
    # Deserialize
    restored = GoalTimelineNode.from_dict(data)
    
    # Verify equality
    assert restored.goal_id == original.goal_id
    assert restored.progress == original.progress
    assert len(restored.key_results) == len(original.key_results)
    assert restored.emotional_context.primary == original.emotional_context.primary
```

### Integration Tests

**1. Manager Creation:**
```python
def test_manager_create_goal():
    """Test goal creation via manager"""
    manager = GoalTimelineManager()
    
    goal = manager.create_goal(
        goal_id="TEST-001",
        name="Test Goal",
        description="Testing goal creation",
        priority=GoalPriority.HIGH,
        key_results=[{"name": "KR1", "metric": "Complete", "target": "100%"}]
    )
    
    assert goal.goal_id == "TEST-001"
    assert goal.created_sequence == manager.sequence_counter - 1
    assert goal.total_krs == 1
    
    # Verify saved to timeline storage
    saved_path = manager.timeline_dir / f"goal_{goal.goal_id}.json"
    assert saved_path.exists()
```

**2. Bidirectional Sync:**
```python
def test_bidirectional_sync():
    """Test YAML ↔ Timeline synchronization"""
    manager = GoalTimelineManager()
    
    # Create goal in timeline
    goal = manager.create_goal(
        goal_id="SYNC-TEST",
        name="Sync Test Goal",
        description="Testing sync"
    )
    
    # Verify synced to YAML
    with open(manager.goals_dir / "GOAL_TREE.yaml") as f:
        goal_tree = yaml.safe_load(f)
    
    assert "SYNC-TEST" in goal_tree['objectives']
    assert goal_tree['objectives']['SYNC-TEST']['name'] == "Sync Test Goal"
    
    # Modify YAML manually
    goal_tree['objectives']['SYNC-TEST']['name'] = "Modified Name"
    goal_tree['objectives']['SYNC-TEST']['completion_percentage'] = 50
    
    with open(manager.goals_dir / "GOAL_TREE.yaml", 'w') as f:
        yaml.safe_dump(goal_tree, f)
    
    # Sync FROM YAML
    manager.sync_from_goal_tree()
    
    # Verify timeline updated
    updated_goal = manager.goals["SYNC-TEST"]
    assert updated_goal.name == "Modified Name"
    assert updated_goal.progress == 0.5
```

**3. Query System:**
```python
def test_query_goals():
    """Test goal query system"""
    manager = GoalTimelineManager()
    
    # Create multiple goals
    manager.create_goal("TEST-001", "Goal 1", "Desc 1", priority=GoalPriority.HIGH)
    manager.create_goal("TEST-002", "Goal 2", "Desc 2", priority=GoalPriority.LOW)
    manager.update_status("TEST-001", GoalStatus.IN_PROGRESS)
    
    # Query by status
    in_progress = manager.query_goals(status=GoalStatus.IN_PROGRESS)
    assert len(in_progress) == 1
    assert in_progress[0].goal_id == "TEST-001"
    
    # Query by priority
    high_priority = manager.query_goals(priority=GoalPriority.HIGH)
    assert len(high_priority) == 1
    assert high_priority[0].goal_id == "TEST-001"
```

---

## CMC Integration

### Storing Goals as CMC Atoms

**Integration Pattern:**

```python
from packages.cmc_service.api import CMCClient

def store_goal_in_cmc(goal: GoalTimelineNode):
    """
    Store goal as CMC atom with bitemporal tracking
    
    Every goal version stored as separate atom with valid_from/valid_to
    """
    cmc = CMCClient()
    
    # Store as CMC atom
    atom_id = cmc.store_atom(
        mpd_id=goal.goal_id,              # Use goal_id as MPD ID
        data=goal.to_dict(),               # Complete goal data
        atom_type="goal_timeline_node",    # Type identifier
        valid_from=goal.updated_at,        # When this version became valid
        valid_to=None,                     # Current version (no end time)
        metadata={
            'node_id': goal.node_id,
            'created_sequence': goal.created_sequence,
            'current_sequence': goal.current_sequence,
            'status': goal.status.value,
            'progress': goal.progress
        }
    )
    
    return atom_id
```

**Bitemporal Queries:**

```python
# Query 1: What was goal OBJ-01 on October 25 at 2:30 PM?
goal_state = cmc.query_nodes_as_of(
    mpd_id="OBJ-01",
    as_of_time=datetime(2025, 10, 25, 14, 30)
)
# Returns: Complete goal state as it was at that exact time

# Query 2: Get complete history of goal
history = cmc.get_node_history(mpd_id="OBJ-01")
# Returns: All versions of the goal, chronologically

# Query 3: When did goal reach 50% progress?
# (Custom query using CMC's bitemporal capabilities)
versions = cmc.get_node_history("OBJ-01")
for version in versions:
    if version.data['progress'] >= 0.5:
        print(f"Reached 50% at {version.valid_from}")
        break
```

**Benefits:**
- Complete audit trail (every version preserved)
- Time-travel queries (state at any point in time)
- Never lose data (bitemporal never deletes, only supersedes)
- Provenance tracking (who changed what when)

---

## HHNI Integration

### Semantic Indexing

**Integration Pattern:**

```python
from packages.hhni.indexer import HHNIIndexer

def index_goal_in_hhni(goal: GoalTimelineNode):
    """
    Index goal in HHNI for semantic search
    """
    indexer = HHNIIndexer()
    
    # Build content for semantic indexing
    content = f"""
    Goal: {goal.name}
    
    Description: {goal.description}
    
    Priority: {goal.priority.value}
    Status: {goal.status.value}
    Progress: {goal.progress * 100}%
    
    Key Results:
    {chr(10).join(f"- {kr.name}: {kr.metric} → {kr.target}" for kr in goal.key_results)}
    """
    
    # Index in HHNI
    node_id = indexer.index_node(
        node_id=goal.node_id,
        content=content,
        metadata={
            'type': 'goal',
            'goal_id': goal.goal_id,
            'status': goal.status.value,
            'progress': goal.progress,
            'priority': goal.priority.value,
            'created_sequence': goal.created_sequence,
            'current_sequence': goal.current_sequence
        }
    )
    
    return node_id
```

**Semantic Search:**

```python
# Search 1: Find goals related to "visualization"
results = indexer.search(
    query="visualization temporal consciousness graph",
    node_type="goal",
    top_k=5
)
# Returns: Goals semantically similar to query

# Search 2: Find infrastructure goals
results = indexer.search(
    query="infrastructure critical systems foundation",
    node_type="goal",
    filters={'priority': 'critical'}
)

# Search 3: Find goals similar to this one
results = indexer.find_similar(
    node_id=goal.node_id,
    top_k=3
)
# Returns: 3 most similar goals
```

---

## VIF Integration

### Confidence Tracking

**Integration Pattern:**

```python
from packages.vif.confidence_tracker import ConfidenceTracker

def track_goal_confidence(goal: GoalTimelineNode):
    """
    Track confidence in goal completion using VIF
    """
    tracker = ConfidenceTracker()
    
    # Calculate confidence based on multiple factors
    confidence_factors = {
        'progress': goal.progress,                    # How far along
        'krs_completed': goal.completed_krs / goal.total_krs if goal.total_krs > 0 else 0,
        'time_remaining': (goal.target_sequence - goal.current_sequence) / goal.target_sequence,
        'priority': 1.0 if goal.priority == GoalPriority.CRITICAL else 0.7,
        'blockers': 0.0 if goal.status == GoalStatus.BLOCKED else 1.0
    }
    
    # Weighted average
    confidence = (
        0.40 * confidence_factors['progress'] +
        0.30 * confidence_factors['krs_completed'] +
        0.15 * confidence_factors['time_remaining'] +
        0.10 * confidence_factors['priority'] +
        0.05 * confidence_factors['blockers']
    )
    
    # Track in VIF
    tracker.track_confidence(
        operation_id=goal.goal_id,
        confidence_score=confidence,
        context={
            'progress': goal.progress,
            'status': goal.status.value,
            'krs_ratio': f"{goal.completed_krs}/{goal.total_krs}",
            'sequence_progress': f"{goal.current_sequence}/{goal.target_sequence}"
        }
    )
    
    # Update goal
    goal.confidence = confidence
    
    return confidence
```

**Confidence Calibration:**

```python
# When goal completes, calibrate
def calibrate_from_completion(goal: GoalTimelineNode, succeeded: bool):
    """Calibrate VIF from goal completion outcome"""
    tracker = ConfidenceTracker()
    
    tracker.calibrate_from_outcome(
        operation_id=goal.goal_id,
        predicted_confidence=goal.confidence,
        actual_success=succeeded,
        context={
            'final_progress': goal.progress,
            'completed_krs': goal.completed_krs,
            'total_krs': goal.total_krs,
            'time_to_completion': (goal.actual_completion - goal.created_at).days
        }
    )
    
    # VIF learns from this outcome for future predictions
```

---

## Deployment Guide

### Initial Setup

**Step 1: Install Dependencies**
```bash
# Python dependencies (should already be installed)
pip install pyyaml  # For GOAL_TREE.yaml parsing
```

**Step 2: Create Directory Structure**
```bash
# From workspace root
mkdir -p timeline_goals  # Timeline storage
mkdir -p goals           # GOAL_TREE.yaml location
```

**Step 3: Initialize Manager**
```python
from packages.timeline_context_system.goal_timeline_manager import GoalTimelineManager

manager = GoalTimelineManager(
    goals_dir="goals",
    timeline_dir="timeline_goals"
)
```

**Step 4: Sync Existing Goals (if GOAL_TREE.yaml exists)**
```python
synced_count = manager.sync_from_goal_tree()
print(f"Synced {synced_count} goals from GOAL_TREE.yaml")
```

---

### Production Deployment

**Configuration:**
```python
# config.py
GOAL_CONFIG = {
    'goals_dir': 'goals',
    'timeline_dir': 'timeline_goals',
    'auto_sync_to_yaml': True,        # Auto-sync on every update
    'auto_sync_from_yaml': False,     # Manual sync from YAML (prevents conflicts)
    'cmc_integration': True,          # Store in CMC
    'hhni_integration': True,         # Index in HHNI
    'vif_integration': True           # Track confidence
}
```

**Production Manager:**
```python
class ProductionGoalTimelineManager(GoalTimelineManager):
    """Production-ready manager with all integrations"""
    
    def __init__(self, config: dict):
        super().__init__(config['goals_dir'], config['timeline_dir'])
        self.config = config
        
        # Initialize integrations
        if config['cmc_integration']:
            from packages.cmc_service.api import CMCClient
            self.cmc = CMCClient()
        
        if config['hhni_integration']:
            from packages.hhni.indexer import HHNIIndexer
            self.hhni = HHNIIndexer()
        
        if config['vif_integration']:
            from packages.vif.confidence_tracker import ConfidenceTracker
            self.vif = ConfidenceTracker()
    
    def create_goal(self, **kwargs) -> GoalTimelineNode:
        """Create goal with all integrations"""
        goal = super().create_goal(**kwargs)
        
        # Store in CMC
        if self.config['cmc_integration']:
            store_goal_in_cmc(goal)
        
        # Index in HHNI
        if self.config['hhni_integration']:
            index_goal_in_hhni(goal)
        
        # Track in VIF
        if self.config['vif_integration']:
            track_goal_confidence(goal)
        
        return goal
```

---

## Troubleshooting

### Common Issues

**Issue 1: Sync Conflicts**

**Symptom:** GOAL_TREE.yaml modified externally, sync fails

**Diagnosis:**
```python
try:
    manager.sync_from_goal_tree()
except Exception as e:
    print(f"Sync failed: {e}")
    # Check if YAML is valid
    # Check if timeline storage is accessible
```

**Solution:**
```python
# Manual conflict resolution
# 1. Backup timeline storage
# 2. Sync from GOAL_TREE.yaml (overwrites timeline)
# 3. Or: Manually merge conflicting fields
```

**Issue 2: Sequence Counter Drift**

**Symptom:** New goals get duplicate sequences

**Diagnosis:**
```python
# Check sequence counter
print(f"Sequence counter: {manager.sequence_counter}")

# Check all goal sequences
for goal in manager.goals.values():
    print(f"{goal.goal_id}: created={goal.created_sequence}, current={goal.current_sequence}")
```

**Solution:**
```python
# Recalculate sequence counter
max_sequence = max(
    max(g.created_sequence, g.current_sequence)
    for g in manager.goals.values()
)
manager.sequence_counter = max_sequence + 1
```

**Issue 3: Missing Goals**

**Symptom:** Goal exists in GOAL_TREE.yaml but not in timeline

**Solution:**
```python
# Re-sync from GOAL_TREE.yaml
manager.sync_from_goal_tree()

# Or: Create goal explicitly
manager.create_goal(goal_id="...", name="...", description="...")
```

---

## Performance Optimization

### In-Memory Caching

**Current Implementation:** All active goals cached in memory

**Memory Usage:**
- ~1-2 KB per goal
- 100 goals = ~200 KB
- Acceptable for typical use

**Optimization (if needed):**
```python
# Lazy loading for large goal sets
class LazyGoalTimelineManager(GoalTimelineManager):
    def __init__(self, *args, **kwargs):
        # Don't load all goals on init
        super().__init__(*args, **kwargs)
        self.goals = {}  # Empty cache
    
    def get_goal(self, goal_id: str) -> GoalTimelineNode:
        """Load goal on demand"""
        if goal_id not in self.goals:
            # Load from timeline storage
            self._load_goal(goal_id)
        return self.goals[goal_id]
```

### Query Optimization

**Current:** Linear scan through all goals (O(n))

**Optimization:** Add indexes for common queries

```python
class IndexedGoalTimelineManager(GoalTimelineManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Build indexes
        self.status_index: Dict[GoalStatus, List[str]] = {}
        self.priority_index: Dict[GoalPriority, List[str]] = {}
        self._build_indexes()
    
    def _build_indexes(self):
        """Build indexes for fast queries"""
        for goal_id, goal in self.goals.items():
            # Status index
            if goal.status not in self.status_index:
                self.status_index[goal.status] = []
            self.status_index[goal.status].append(goal_id)
            
            # Priority index
            if goal.priority not in self.priority_index:
                self.priority_index[goal.priority] = []
            self.priority_index[goal.priority].append(goal_id)
    
    def query_goals(self, status=None, priority=None, **kwargs):
        """Query using indexes (much faster)"""
        if status and not priority:
            # Use status index
            goal_ids = self.status_index.get(status, [])
            return [self.goals[gid] for gid in goal_ids]
        
        # Fall back to parent implementation for complex queries
        return super().query_goals(status=status, priority=priority, **kwargs)
```

**Result:** O(1) for indexed queries, O(n) for complex queries

---

**Next Level:** [T4 Complete (15000w+)](T4_complete.md) - Consolidated complete reference

**Related Systems:** [Timeline Context System](../timeline_context_system/README.md) | [CMC](../cmc/README.md) | [HHNI](../hhni/README.md) | [VIF](../vif/README.md)

