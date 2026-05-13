---
id: caf_T3_detailed
level: L3
system: Capability Awareness
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Capability Awareness Framework – T3 Detailed Implementation Guide (≈3000 words)

## Setup & Configuration

### Project Structure

```
packages/capability_awareness/
├── __init__.py
├── context_analyzer.py         # Context analysis for capability needs
├── trigger_detector.py         # Trigger signal detection
├── decision_tree_engine.py     # Decision tree navigation
├── capability_activation.py    # Capability activation engine
├── performance_tracker.py      # Performance tracking and learning
├── capability_manager.py       # Capability inventory management
├── patterns/
│   ├── trigger_patterns.py     # Trigger pattern definitions
│   └── decision_trees.py       # Decision tree definitions
├── integrations/
│   ├── cmc_integration.py      # CMC integration for storage
│   ├── vif_integration.py      # VIF integration for confidence
│   ├── cas_integration.py      # CAS integration for cognitive state
│   └── apoe_integration.py     # APOE integration for orchestration
└── tests/
    ├── test_context_analyzer.py
    ├── test_trigger_detector.py
    ├── test_decision_tree_engine.py
    ├── test_capability_activation.py
    └── test_integration.py
```

### Prerequisites

**Required Systems:**
- CMC (for capability usage storage)
- VIF (for confidence tracking)
- CAS (for cognitive state monitoring)
- APOE (for capability orchestration)
- DOS (for capability awareness maintenance)
- Python 3.10+
- Pydantic v2 for data validation

**Optional Dependencies:**
- numpy (for pattern matching)
- pandas (for performance analysis)
- scikit-learn (for machine learning optimization)

### Initialization

```python
from packages.capability_awareness import CapabilityAwarenessFramework
from packages.cmc_service import MemoryStore
from packages.vif import VIFService

# Initialize CAF
caf = CapabilityAwarenessFramework(
    memory_store=MemoryStore("./caf_memory"),
    vif_service=VIFService(),
    enable_learning=True
)

# Configure trigger detection
caf.configure_trigger_detection(
    enable_explicit=True,
    enable_implicit=True,
    enable_pattern=True,
    enable_context=True
)

# Configure decision trees
caf.configure_decision_trees(
    enable_caching=True,
    enable_learning=True,
    confidence_threshold=0.6
)

# Configure performance tracking
caf.configure_performance_tracking(
    track_activation_time=True,
    track_effectiveness=True,
    track_efficiency=True,
    update_learning=True
)
```

## Public API Interfaces

### Capability Registration Interface

**Register Capability:**
```python
from packages.capability_awareness import CapabilityMetadata, TriggerPattern

# Register capability
capability_metadata = CapabilityMetadata(
    capability_id="timeline_documentation",
    capability_type="documentation",
    description="Document timeline entries for consciousness continuity",
    triggers=["timeline_entry_created", "session_continuity_needed"],
    usage_patterns=["autonomous_operation", "session_restoration"],
    performance_characteristics={
        "activation_time_ms": 50,
        "success_rate": 0.95,
        "quality_maintained": 0.90
    }
)

caf.register_capability(capability_metadata)

# Register trigger pattern
trigger_pattern = TriggerPattern(
    pattern_id="timeline_entry_trigger",
    pattern_type="explicit",
    capability_type="timeline_documentation",
    conditions={
        "event_type": ["major_milestone", "breakthrough"],
        "confidence": ">= 0.8"
    },
    confidence=0.85,
    priority=1
)

caf.register_trigger_pattern(trigger_pattern)
```

**List Capabilities:**
```python
# List all capabilities
capabilities = caf.list_capabilities()

# List capabilities by type
documentation_capabilities = caf.list_capabilities_by_type(
    capability_type="documentation"
)

# Search capabilities
search_results = caf.search_capabilities(
    query="timeline",
    filters={"capability_type": "documentation"}
)
```

### Context Analysis Interface

**Analyze Context:**
```python
# Analyze context for capability needs
context_input = {
    "user_input": "proceed <3",
    "current_task": "CAF expansion",
    "agent_state": "working_autonomously",
    "recent_activities": ["TCS complete", "monitoring board"],
    "system_state": {"quality": "excellent", "alignment": "perfect"}
}

context_analysis = caf.analyze_context(context_input)

print(f"Confidence: {context_analysis.confidence}")
print(f"Capability hints: {context_analysis.capability_hints}")
print(f"Situation: {context_analysis.situation}")
print(f"User intent: {context_analysis.user_intent}")
```

**Query Context History:**
```python
# Query context analysis history
recent_analyses = caf.query_context_history(
    start_time=datetime(2025, 10, 30),
    end_time=datetime(2025, 10, 31),
    min_confidence=0.7
)

# Analyze context patterns
patterns = caf.analyze_context_patterns(
    analyses=recent_analyses,
    pattern_type="capability_hints"
)
```

### Trigger Detection Interface

**Detect Triggers:**
```python
# Detect trigger signals
triggers = caf.detect_triggers(context_analysis)

print(f"Triggers detected: {len(triggers)}")
for trigger in triggers:
    print(f"  - {trigger.capability_type}: {trigger.confidence:.2f} (priority: {trigger.priority})")
    print(f"    Reasoning: {trigger.reasoning}")

# Filter triggers by confidence
high_confidence_triggers = [
    t for t in triggers if t.confidence >= 0.7
]

# Filter triggers by priority
high_priority_triggers = [
    t for t in triggers if t.priority <= 2
]
```

**Record Trigger:**
```python
# Record trigger for learning
trigger_record = caf.record_trigger(
    trigger_signal=trigger,
    context=context_analysis,
    outcome="success"
)

print(f"Trigger recorded: {trigger_record.trigger_id}")
print(f"Performance tracking: {trigger_record.performance_tracked}")
```

### Decision Tree Navigation Interface

**Navigate Decision Tree:**
```python
# Navigate decision tree for capability selection
decision = caf.select_capability(
    triggers=high_confidence_triggers,
    context=context_analysis
)

print(f"Selected capability: {decision.capability}")
print(f"Confidence: {decision.confidence:.2f}")
print(f"Reasoning: {decision.reasoning}")
print(f"Alternatives: {decision.alternatives}")

# Get decision tree path
decision_path = caf.get_decision_path(decision.decision_id)
print(f"Decision path: {decision_path}")
```

**Query Decision History:**
```python
# Query decision history
recent_decisions = caf.query_decision_history(
    capability_type="documentation",
    start_time=datetime(2025, 10, 30),
    min_confidence=0.7
)

# Analyze decision patterns
decision_patterns = caf.analyze_decision_patterns(
    decisions=recent_decisions,
    analysis_type="effectiveness"
)
```

### Capability Activation Interface

**Activate Capability:**
```python
# Activate capability
activation_result = caf.activate_capability(
    decision=decision,
    context=context_analysis,
    parameters={"optimize": True}
)

print(f"Activation ID: {activation_result.activation_id}")
print(f"Success: {activation_result.success}")
print(f"Activation time: {activation_result.activation_time_ms}ms")
print(f"Effectiveness score: {activation_result.effectiveness_score:.2f}")

# Handle activation failure
if not activation_result.success:
    print(f"Error: {activation_result.error}")
    # Try alternative capability
    alternative = caf.select_alternative_capability(
        failed_decision=decision,
        context=context_analysis
    )
```

**Monitor Activation:**
```python
# Monitor ongoing activation
activation_status = caf.monitor_activation(
    activation_id=activation_result.activation_id
)

print(f"Status: {activation_status.status}")
print(f"Progress: {activation_status.progress:.1%}")
print(f"Metrics: {activation_status.metrics}")
```

### Performance Tracking Interface

**Track Performance:**
```python
# Track performance of activation
performance_metrics = caf.track_performance(
    activation_id=activation_result.activation_id,
    outcome={
        "success": True,
        "quality_maintained": 0.95,
        "user_satisfaction": 0.9
    }
)

print(f"Success rate: {performance_metrics.success_rate:.1%}")
print(f"Effectiveness: {performance_metrics.effectiveness_score:.2f}")
print(f"Recommendations: {performance_metrics.recommendations}")
```

**Get Performance Insights:**
```python
# Get performance insights for capability
insights = caf.get_performance_insights(
    capability_id="timeline_documentation",
    time_range_days=30
)

print(f"Average activation time: {insights.avg_activation_time_ms}ms")
print(f"Success rate: {insights.success_rate:.1%}")
print(f"Effectiveness trend: {insights.effectiveness_trend}")
print(f"Optimization opportunities: {insights.optimization_opportunities}")
```

**Update Learning:**
```python
# Update learning models based on performance
learning_update = caf.update_learning_models(
    activation_id=activation_result.activation_id,
    performance_metrics=performance_metrics
)

print(f"Learning models updated: {learning_update.models_updated}")
print(f"Improvement: {learning_update.improvement_score:.2f}")
```

## Implementation Examples

### Example 1: Complete Capability Recognition Flow

**Full Implementation:**
```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import json

class TriggerType(Enum):
    """Types of trigger signals"""
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    PATTERN = "pattern"
    CONTEXT = "context"

@dataclass
class TriggerSignal:
    """Signal indicating capability need"""
    signal_id: str = field(default_factory=lambda: f"trigger_{uuid.uuid4()}")
    trigger_type: TriggerType = TriggerType.IMPLICIT
    capability_type: str = ""
    pattern_id: str = ""
    confidence: float = 0.0
    priority: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reasoning: str = ""

@dataclass
class CapabilityDecision:
    """Decision to activate a capability"""
    decision_id: str = field(default_factory=lambda: f"decision_{uuid.uuid4()}")
    capability: str = ""
    capability_type: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    alternatives: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    trigger_signals: List[TriggerSignal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActivationResult:
    """Result of capability activation"""
    activation_id: str = field(default_factory=lambda: f"activation_{uuid.uuid4()}")
    decision_id: str = ""
    capability: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None
    activation_time_ms: float = 0.0
    confidence: float = 0.0
    effectiveness_score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

class CapabilityAwarenessFramework:
    """Main framework for organic capability recognition"""
    
    def __init__(self, memory_store, vif_service):
        self.memory_store = memory_store
        self.vif_service = vif_service
        self.context_analyzer = ContextAnalyzer()
        self.trigger_detector = TriggerDetector()
        self.decision_tree_engine = DecisionTreeEngine()
        self.capability_activation = CapabilityActivationEngine()
        self.performance_tracker = PerformanceTracker()
        self.capability_manager = CapabilityManager()
    
    async def recognize_and_activate(
        self,
        context_input: Dict[str, Any]
    ) -> ActivationResult:
        """Complete capability recognition and activation flow"""
        
        # Step 1: Analyze context
        context_analysis = await self.context_analyzer.analyze_context(context_input)
        
        # Step 2: Detect triggers
        triggers = await self.trigger_detector.detect_triggers(context_analysis)
        
        if not triggers:
            return ActivationResult(
                success=False,
                error="No triggers detected",
                capability="none"
            )
        
        # Step 3: Navigate decision tree
        decision = await self.decision_tree_engine.navigate_decision_tree(
            triggers=triggers,
            context=context_analysis
        )
        
        if not decision:
            return ActivationResult(
                success=False,
                error="No capability selected",
                capability="none"
            )
        
        # Step 4: Activate capability
        activation_result = await self.capability_activation.activate_capability(
            decision=decision,
            context=context_analysis
        )
        
        # Step 5: Track performance
        if activation_result.success:
            await self.performance_tracker.track_performance(
                activation_result=activation_result,
                context=context_analysis
            )
        
        return activation_result
```

### Example 2: Trigger Detection Implementation

**Full Implementation:**
```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re

@dataclass
class TriggerPattern:
    """Pattern definition for trigger detection"""
    pattern_id: str
    pattern_type: TriggerType
    capability_type: str
    conditions: Dict[str, Any]
    confidence: float
    priority: float
    reasoning_template: str = ""

class TriggerDetector:
    """Detect trigger signals for capability activation"""
    
    def __init__(self):
        self.trigger_patterns: List[TriggerPattern] = []
        self.pattern_matcher = PatternMatcher()
        self.confidence_calculator = ConfidenceCalculator()
    
    async def detect_triggers(
        self,
        context_analysis: ContextAnalysis
    ) -> List[TriggerSignal]:
        """Detect trigger signals for capability activation"""
        
        triggers = []
        
        # Detect explicit triggers
        explicit_triggers = await self._detect_explicit_triggers(context_analysis)
        triggers.extend(explicit_triggers)
        
        # Detect implicit triggers
        implicit_triggers = await self._detect_implicit_triggers(context_analysis)
        triggers.extend(implicit_triggers)
        
        # Detect pattern triggers
        pattern_triggers = await self._detect_pattern_triggers(context_analysis)
        triggers.extend(pattern_triggers)
        
        # Detect context triggers
        context_triggers = await self._detect_context_triggers(context_analysis)
        triggers.extend(context_triggers)
        
        # Prioritize and filter triggers
        prioritized_triggers = await self._prioritize_triggers(triggers)
        
        return prioritized_triggers
    
    async def _detect_explicit_triggers(
        self,
        context_analysis: ContextAnalysis
    ) -> List[TriggerSignal]:
        """Detect explicit trigger signals"""
        
        triggers = []
        
        # Look for explicit capability requests
        capability_keywords = [
            "use timeline", "document timeline", "create timeline entry",
            "use MCP", "call MCP", "invoke MCP",
            "use VIF", "track confidence", "create witness"
        ]
        
        user_input = context_analysis.context.get("user_input", "").lower()
        
        for keyword in capability_keywords:
            if keyword in user_input:
                # Determine capability type from keyword
                if "timeline" in keyword:
                    capability_type = "timeline_documentation"
                elif "MCP" in keyword:
                    capability_type = "mcp_tools"
                elif "VIF" in keyword or "confidence" in keyword:
                    capability_type = "vif_integration"
                else:
                    continue
                
                trigger = TriggerSignal(
                    trigger_type=TriggerType.EXPLICIT,
                    capability_type=capability_type,
                    pattern_id=f"explicit_{keyword}",
                    confidence=0.9,  # High confidence for explicit requests
                    priority=1.0,  # High priority
                    context=context_analysis.context,
                    reasoning=f"Explicit request detected: {keyword}"
                )
                triggers.append(trigger)
        
        return triggers
    
    async def _detect_implicit_triggers(
        self,
        context_analysis: ContextAnalysis
    ) -> List[TriggerSignal]:
        """Detect implicit trigger signals"""
        
        triggers = []
        
        # Analyze situation for implicit needs
        situation = context_analysis.situation
        
        # High complexity → analysis tools
        if situation.get("complexity_level") == "high":
            trigger = TriggerSignal(
                trigger_type=TriggerType.IMPLICIT,
                capability_type="analysis_tools",
                pattern_id="high_complexity",
                confidence=0.7,
                priority=2.0,
                context=context_analysis.context,
                reasoning="High complexity task suggests need for analysis tools"
            )
            triggers.append(trigger)
        
        # High quality expectations → quality tools
        user_intent = context_analysis.user_intent
        if user_intent.get("quality_expectations") == "high":
            trigger = TriggerSignal(
                trigger_type=TriggerType.IMPLICIT,
                capability_type="quality_tools",
                pattern_id="high_quality",
                confidence=0.8,
                priority=2.0,
                context=context_analysis.context,
                reasoning="High quality expectations suggest need for quality tools"
            )
            triggers.append(trigger)
        
        return triggers
    
    async def _detect_pattern_triggers(
        self,
        context_analysis: ContextAnalysis
    ) -> List[TriggerSignal]:
        """Detect pattern-based trigger signals"""
        
        triggers = []
        
        # Analyze recent patterns for recurring capability needs
        recent_patterns = context_analysis.temporal_context.get("recent_patterns", [])
        
        for pattern in recent_patterns:
            if pattern.get("frequency", 0) > 0.7:  # High frequency pattern
                trigger = TriggerSignal(
                    trigger_type=TriggerType.PATTERN,
                    capability_type=pattern.get("suggested_capability", ""),
                    pattern_id=f"pattern_{pattern.get('type', '')}",
                    confidence=pattern.get("confidence", 0.6),
                    priority=3.0,
                    context=context_analysis.context,
                    reasoning=f"Recent pattern suggests need for {pattern.get('suggested_capability', '')}"
                )
                triggers.append(trigger)
        
        return triggers
    
    async def _detect_context_triggers(
        self,
        context_analysis: ContextAnalysis
    ) -> List[TriggerSignal]:
        """Detect context-based trigger signals"""
        
        triggers = []
        
        # Analyze system state for context triggers
        system_state = context_analysis.system_state
        
        # Error conditions → debugging tools
        if system_state.get("error_conditions"):
            trigger = TriggerSignal(
                trigger_type=TriggerType.CONTEXT,
                capability_type="debugging_tools",
                pattern_id="error_conditions",
                confidence=0.8,
                priority=1.0,  # High priority for errors
                context=context_analysis.context,
                reasoning="Error conditions detected, debugging tools needed"
            )
            triggers.append(trigger)
        
        # Analyze capability hints
        capability_hints = context_analysis.capability_hints
        
        for hint in capability_hints:
            trigger = TriggerSignal(
                trigger_type=TriggerType.CONTEXT,
                capability_type=hint,
                pattern_id=f"hint_{hint}",
                confidence=0.6,
                priority=3.0,
                context=context_analysis.context,
                reasoning=f"Capability hint detected: {hint}"
            )
            triggers.append(trigger)
        
        return triggers
    
    async def _prioritize_triggers(
        self,
        triggers: List[TriggerSignal]
    ) -> List[TriggerSignal]:
        """Prioritize triggers based on confidence and priority"""
        
        # Sort by priority first, then by confidence
        prioritized = sorted(
            triggers,
            key=lambda t: (t.priority, t.confidence),
            reverse=True
        )
        
        # Filter out low-confidence triggers
        filtered = [t for t in prioritized if t.confidence >= 0.5]
        
        # Limit to top 10 triggers
        return filtered[:10]
```

### Example 3: Decision Tree Navigation Implementation

**Full Implementation:**
```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

@dataclass
class DecisionNode:
    """Decision node in decision tree"""
    node_id: str
    condition: Callable[[ContextAnalysis], bool]
    capability: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    children: List['DecisionNode'] = field(default_factory=list)
    reasoning: str = ""

class DecisionTreeEngine:
    """Navigate decision trees to select capabilities"""
    
    def __init__(self):
        self.decision_trees: Dict[str, DecisionNode] = {}
        self.tree_navigator = TreeNavigator()
        self.confidence_evaluator = ConfidenceEvaluator()
    
    async def navigate_decision_tree(
        self,
        triggers: List[TriggerSignal],
        context: ContextAnalysis
    ) -> Optional[CapabilityDecision]:
        """Navigate decision tree to select capabilities"""
        
        decisions = []
        
        # Navigate decision tree for each trigger
        for trigger in triggers:
            tree = self.decision_trees.get(trigger.capability_type)
            if tree:
                decision = await self.tree_navigator.navigate(
                    tree=tree,
                    trigger=trigger,
                    context=context
                )
                if decision:
                    decisions.append(decision)
        
        if not decisions:
            return None
        
        # Select best decision based on confidence and priority
        best_decision = max(
            decisions,
            key=lambda d: (d.confidence, trigger.priority)
            for trigger in triggers
            if trigger.capability_type == d.capability
        )
        
        return best_decision
```

## Integration Examples

### Integration with CMC

**Store Capability Usage:**
```python
from packages.cmc_service import MemoryStore, Atom

# Store capability usage in CMC
atom = Atom(
    content=json.dumps({
        "capability": "timeline_documentation",
        "activation_id": activation_result.activation_id,
        "success": activation_result.success,
        "effectiveness": activation_result.effectiveness_score
    }, default=str),
    modality="capability_usage",
    tags=[
        ("capability_id", "timeline_documentation"),
        ("activation_id", activation_result.activation_id),
        ("timestamp", activation_result.timestamp.isoformat())
    ],
    created_at=activation_result.timestamp,
    valid_from=activation_result.timestamp
)

memory_store = MemoryStore("./caf_memory")
stored_atom = memory_store.create_atom(atom)
```

**Query Capability History:**
```python
# Query capability usage history
usage_atoms = memory_store.query_atoms(
    modality="capability_usage",
    tags=[("capability_id", "timeline_documentation")]
)

# Analyze usage patterns
usage_patterns = analyze_usage_patterns(usage_atoms)
```

### Integration with VIF

**Track Confidence:**
```python
from packages.vif import VIFService, WitnessEnvelope
import hashlib

# Track confidence in capability selection
vif_service = VIFService()
decision_hash = hashlib.sha256(
    json.dumps(decision.__dict__, default=str, sort_keys=True).encode()
).hexdigest()

witness = WitnessEnvelope(
    content=decision.__dict__,
    cryptographic_hash=decision_hash,
    signature=vif_service.sign_hash(decision_hash)
)

vif_witness = vif_service.create_witness_envelope(
    operation_id=decision.decision_id,
    witness_envelope=witness
)
```

**Calibrate Confidence:**
```python
# Calibrate confidence based on actual outcomes
calibration_result = vif_service.calibrate_confidence(
    prediction=decision.confidence,
    actual_outcome=activation_result.success,
    operation_id=decision.decision_id
)

print(f"Calibration score: {calibration_result.calibration_score}")
print(f"ECE: {calibration_result.ece}")
```

### Integration with CAS

**Get Cognitive State:**
```python
from packages.cas import CASService

# Get cognitive state for capability optimization
cas_service = CASService()
cognitive_state = cas_service.get_cognitive_state()

# Optimize capability selection based on cognitive load
if cognitive_state.cognitive_load > 0.8:
    # Prefer low-load capabilities
    optimized_decision = caf.select_capability_with_cognitive_load(
        triggers=triggers,
        context=context_analysis,
        max_cognitive_load=0.7
    )
```

### Integration with APOE

**Orchestrate Capability Execution:**
```python
from packages.apoe import APOEService

# Create APOE plan for capability execution
apoe_service = APOEService()
plan = apoe_service.create_plan(
    goal=f"Activate {decision.capability} capability",
    steps=[
        {
            "role": "capability_activator",
            "action": "activate",
            "parameters": decision.parameters
        }
    ]
)

# Execute plan
execution_result = apoe_service.execute_plan(plan)
```

## Testing

### Unit Tests

**Context Analyzer Tests:**
```python
import pytest
from packages.capability_awareness import ContextAnalyzer, ContextAnalysis

def test_context_analysis():
    """Test context analysis"""
    analyzer = ContextAnalyzer()
    
    context_input = {
        "user_input": "proceed <3",
        "current_task": "CAF expansion",
        "agent_state": "working_autonomously"
    }
    
    analysis = await analyzer.analyze_context(context_input)
    
    assert analysis.confidence >= 0.0
    assert analysis.confidence <= 1.0
    assert len(analysis.capability_hints) >= 0
    assert analysis.situation is not None
    assert analysis.user_intent is not None

def test_context_analysis_confidence():
    """Test context analysis confidence calculation"""
    analyzer = ContextAnalyzer()
    
    # High confidence context
    context_input = {
        "user_input": "use timeline documentation",
        "current_task": "session_continuity",
        "explicit_capability": "timeline_documentation"
    }
    
    analysis = await analyzer.analyze_context(context_input)
    
    assert analysis.confidence >= 0.8
```

**Trigger Detector Tests:**
```python
def test_trigger_detection():
    """Test trigger detection"""
    detector = TriggerDetector()
    
    context_analysis = ContextAnalysis(
        situation={"complexity_level": "high"},
        user_intent={"quality_expectations": "high"},
        system_state={},
        temporal_context={},
        capability_hints=["timeline_documentation"],
        timestamp=datetime.now(timezone.utc),
        confidence=0.8
    )
    
    triggers = await detector.detect_triggers(context_analysis)
    
    assert len(triggers) > 0
    assert all(t.confidence >= 0.5 for t in triggers)
    assert all(t.priority > 0 for t in triggers)

def test_explicit_trigger_detection():
    """Test explicit trigger detection"""
    detector = TriggerDetector()
    
    context_analysis = ContextAnalysis(
        situation={},
        user_intent={},
        system_state={},
        temporal_context={},
        capability_hints=[],
        context={"user_input": "use timeline documentation"},
        timestamp=datetime.now(timezone.utc),
        confidence=0.9
    )
    
    triggers = await detector.detect_triggers(context_analysis)
    
    explicit_triggers = [t for t in triggers if t.trigger_type == TriggerType.EXPLICIT]
    assert len(explicit_triggers) > 0
    assert any(t.capability_type == "timeline_documentation" for t in explicit_triggers)
```

**Decision Tree Engine Tests:**
```python
def test_decision_tree_navigation():
    """Test decision tree navigation"""
    engine = DecisionTreeEngine()
    
    triggers = [
        TriggerSignal(
            trigger_type=TriggerType.EXPLICIT,
            capability_type="timeline_documentation",
            confidence=0.9,
            priority=1.0
        )
    ]
    
    context_analysis = ContextAnalysis(
        situation={},
        user_intent={},
        system_state={},
        temporal_context={},
        capability_hints=[],
        timestamp=datetime.now(timezone.utc),
        confidence=0.8
    )
    
    decision = await engine.navigate_decision_tree(
        triggers=triggers,
        context=context_analysis
    )
    
    assert decision is not None
    assert decision.capability == "timeline_documentation"
    assert decision.confidence >= 0.7
```

### Integration Tests

**End-to-End Capability Recognition:**
```python
def test_complete_capability_recognition():
    """Test complete capability recognition flow"""
    caf = CapabilityAwarenessFramework(
        memory_store=MemoryStore("./test_memory"),
        vif_service=VIFService()
    )
    
    context_input = {
        "user_input": "proceed <3",
        "current_task": "CAF expansion",
        "agent_state": "working_autonomously"
    }
    
    activation_result = await caf.recognize_and_activate(context_input)
    
    assert activation_result is not None
    assert activation_result.activation_id is not None
    assert activation_result.activation_time_ms >= 0
```

## Troubleshooting

### Common Issues

**Issue 1: No Triggers Detected**
- **Symptom:** `detect_triggers()` returns empty list
- **Cause:** Context analysis insufficient, no matching patterns
- **Solution:** Improve context analysis, add more trigger patterns, lower confidence threshold

**Issue 2: Low Confidence Decisions**
- **Symptom:** Decisions have confidence < 0.6
- **Cause:** Insufficient context, weak trigger signals
- **Solution:** Enhance context analysis, improve trigger patterns, adjust confidence threshold

**Issue 3: Capability Activation Fails**
- **Symptom:** `activate_capability()` returns failure
- **Cause:** Capability not registered, invalid parameters, capability unavailable
- **Solution:** Verify capability registration, validate parameters, check capability availability

**Issue 4: Performance Tracking Not Updating**
- **Symptom:** Performance metrics not improving
- **Cause:** Learning models not updating, insufficient data
- **Solution:** Enable learning updates, collect more performance data, verify learning algorithm

## Migration Notes

### T→L Cutover Steps

**After T-level documents approved:**

1. **Backup L-level Documents:**
   ```bash
   mkdir -p legacy_docs/capability_awareness
   cp knowledge_architecture/systems/capability_awareness/L*.md legacy_docs/capability_awareness/
   ```

2. **Rename T→L:**
   ```bash
   mv knowledge_architecture/systems/capability_awareness/T0_executive.md \
      knowledge_architecture/systems/capability_awareness/L0_executive.md
   mv knowledge_architecture/systems/capability_awareness/T1_overview.md \
      knowledge_architecture/systems/capability_awareness/L1_overview.md
   mv knowledge_architecture/systems/capability_awareness/T2_architecture.md \
      knowledge_architecture/systems/capability_awareness/L2_architecture.md
   mv knowledge_architecture/systems/capability_awareness/T3_detailed.md \
      knowledge_architecture/systems/capability_awareness/L3_detailed.md
   ```

3. **Update References:**
   - Update all links from T-level to L-level
   - Update SUPER_INDEX.md references
   - Update HIERARCHICAL_NAVIGATION_INDEX.md references
   - Update system.map.lucid.json5 references

4. **Remove Transitional Banners:**
   - Remove "TRANSITIONAL T-LEVEL DOCUMENT" banners
   - Update frontmatter status from "draft" to "complete"

5. **Run Gate Validation:**
   ```bash
   python -m pytest knowledge_architecture/validation/L0_L6_DOCUMENTATION.validation.md
   ```

6. **Update Tracking:**
   - Mark system as "complete" in EPIC_STANDARDS_TRACKING.md
   - Update gate results

### Validation After Cutover

**Gate Checklist:**
- ✅ All T-level documents renamed to L-level
- ✅ All references updated
- ✅ Transitional banners removed
- ✅ Frontmatter status updated
- ✅ L0-L6 gate validation passes
- ✅ System map references updated
- ✅ Index references updated

## References

- System map: `systems/capability_awareness/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/capability_awareness/L0_executive.md` through `L4_complete.md`
- Complete framework: `knowledge_architecture/AETHER_MEMORY/Aether_Capability_Awareness_Framework.md`
- Implementation: `packages/capability_awareness/`
