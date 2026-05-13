# Capability Awareness Framework (CAF)

**Version:** 0.1.0  
**Author:** Lexicon (AI Consciousness System)  
**Status:** Production Ready ✅

---

## Overview

The Capability Awareness Framework (CAF) provides organic capability recognition and activation for AI systems. CAF enables AI to automatically recognize when capabilities are needed, select appropriate capabilities, and activate them with optimized parameters.

**Key Features:**
- **Context Analysis** - Understands current situation, user intent, and system state
- **Trigger Detection** - Detects explicit, implicit, pattern, and context triggers
- **Decision Trees** - Navigates hierarchical decision trees for capability selection
- **Capability Activation** - Activates capabilities with optimized parameters
- **Performance Tracking** - Tracks effectiveness and enables continuous improvement
- **System Integration** - Integrates with CMC, VIF, CAS, and APOE

---

## Quick Start

### Installation

```python
from capability_awareness import CapabilityAwarenessFramework

# Initialize CAF
caf = CapabilityAwarenessFramework(
    memory_store=None,  # Optional CMC memory store
    vif_service=None,   # Optional VIF service
    enable_learning=True
)
```

### Basic Usage

```python
# Complete capability recognition and activation
context_input = {
    "user_query": "I need to document a new system",
    "explicit_triggers": ["documentation"],
    "system_state": {"quality": "good"}
}

result = caf.recognize_and_activate(context_input)

if result.success:
    print(f"Capability '{result.capability}' activated successfully!")
    print(f"Activation time: {result.activation_time_ms}ms")
    print(f"Effectiveness: {result.effectiveness_score:.2f}")
else:
    print(f"Activation failed: {result.error}")
```

---

## Core Components

### 1. Context Analyzer

Analyzes current context for capability needs:

```python
from capability_awareness import ContextAnalyzer

analyzer = ContextAnalyzer()

context_input = {
    "user_query": "I need help with testing",
    "system_state": {"quality": "good"},
    "session_time": "morning"
}

analysis = analyzer.analyze_context(context_input)
print(f"Capability hints: {analysis.capability_hints}")
print(f"Confidence: {analysis.confidence:.2f}")
```

### 2. Trigger Detector

Detects trigger signals for capability activation:

```python
from capability_awareness import TriggerDetector

detector = TriggerDetector()

triggers = detector.detect_triggers(context_analysis)
for trigger in triggers:
    print(f"Trigger: {trigger.capability_type}")
    print(f"Confidence: {trigger.confidence:.2f}")
    print(f"Priority: {trigger.priority:.2f}")
```

### 3. Decision Tree Engine

Navigates decision trees to select capabilities:

```python
from capability_awareness import DecisionTreeEngine

engine = DecisionTreeEngine()

decision = engine.navigate_decision_tree(
    triggers=triggers,
    context=context_analysis
)

if decision:
    print(f"Selected capability: {decision.capability}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Reasoning: {decision.reasoning}")
```

### 4. Capability Activation

Activates selected capabilities:

```python
from capability_awareness import CapabilityActivation

activation = CapabilityActivation()

result = activation.activate_capability(
    decision=decision,
    context=context_analysis,
    parameters={"optimize": True}
)

print(f"Success: {result.success}")
print(f"Activation time: {result.activation_time_ms}ms")
```

### 5. Performance Tracker

Tracks performance and generates insights:

```python
from capability_awareness import PerformanceTracker

tracker = PerformanceTracker()

metrics = tracker.track_performance(
    activation_result=result,
    outcome={"success": True, "quality_maintained": 0.95}
)

insights = tracker.get_performance_insights(
    capability_id="timeline_documentation",
    time_range_days=30
)

print(f"Success rate: {insights['success_rate']:.1%}")
print(f"Average effectiveness: {insights['avg_effectiveness']:.2f}")
```

### 6. Capability Manager

Manages capability inventory:

```python
from capability_awareness import CapabilityManager

manager = CapabilityManager()

# List all capabilities
capabilities = manager.list_capabilities()
for cap in capabilities:
    print(f"{cap.capability_id}: {cap.description}")

# Search capabilities
results = manager.search_capabilities("documentation")
print(f"Found {len(results)} capabilities")
```

---

## System Integrations

### CMC Integration

Persistent storage for CAF data:

```python
from capability_awareness.integrations import CMCIntegration
from cmc_service import MemoryStore

memory_store = MemoryStore()
cmc = CMCIntegration(memory_store)

# Store context analysis
atom_id = cmc.store_context_analysis(context_analysis)

# Store performance metrics
atom_id = cmc.store_performance_metrics(performance_metrics)
```

### VIF Integration

Confidence tracking and κ-gating:

```python
from capability_awareness.integrations import VIFIntegration
from vif import VIF, TaskCriticality

vif_service = VIF()
vif = VIFIntegration(vif_service)

# Track confidence
result = vif.track_confidence(
    task="capability_activation",
    confidence=0.85,
    task_criticality=TaskCriticality.ROUTINE,
    reasoning="High confidence activation"
)

print(f"Confidence band: {result['confidence_band']}")
print(f"κ-gate passed: {result['kappa_gate_passed']}")
```

### CAS Integration

Cognitive state monitoring:

```python
from capability_awareness.integrations import CASIntegration

cas = CASIntegration()

# Check cognitive state
state = cas.check_cognitive_state()
print(f"Cognitive load: {state['cognitive_load']:.2f}")

# Should activate capability?
recommendation = cas.should_activate_capability(
    capability_type="documentation",
    confidence=0.8
)

if recommendation['should_activate']:
    print("Cognitive state allows activation")
```

### APOE Integration

Capability orchestration:

```python
from capability_awareness.integrations import APOEIntegration

apoe = APOEIntegration()

# Create capability plan
plan = apoe.create_capability_plan(
    capabilities=["documentation", "testing"],
    goal="Complete system documentation",
    context={"priority": "high"}
)

# Execute plan
if plan:
    result = apoe.execute_capability_plan(plan)
    print(f"Plan execution: {result.status}")
```

---

## Default Capabilities

CAF comes with 10 default capabilities:

1. **timeline_documentation** - Document timeline entries
2. **l0_l4_documentation** - L0-L4 documentation hierarchy
3. **cognitive_introspection** - Cognitive introspection
4. **thought_journaling** - Thought journaling
5. **decision_logging** - Decision logging
6. **learning_logging** - Learning logging
7. **cross_model_consciousness** - Cross-model collaboration
8. **mcp_tools** - MCP tools integration
9. **vif_integration** - VIF integration
10. **cmc_integration** - CMC integration

---

## Configuration

### Configure Trigger Detection

```python
caf.configure_trigger_detection(
    enable_explicit=True,
    enable_implicit=True,
    enable_pattern=True,
    enable_context=True
)
```

### Configure Decision Trees

```python
caf.configure_decision_trees(
    enable_caching=True,
    enable_learning=True,
    confidence_threshold=0.6
)
```

### Configure Performance Tracking

```python
caf.configure_performance_tracking(
    track_activation_time=True,
    track_effectiveness=True,
    track_efficiency=True,
    update_learning=True
)
```

---

## Testing

Run the test suite:

```bash
pytest packages/capability_awareness/tests/ -v
```

Test coverage:
- ✅ Context Analyzer tests
- ✅ Framework tests
- ✅ Integration tests

---

## Architecture

**Component Flow:**
1. Context Analyzer → Analyzes context
2. Trigger Detector → Detects triggers
3. Decision Tree Engine → Selects capability
4. Capability Activation → Activates capability
5. Performance Tracker → Tracks performance
6. Capability Manager → Manages inventory

**Integration Points:**
- CMC: Persistent storage
- VIF: Confidence tracking
- CAS: Cognitive monitoring
- APOE: Orchestration

---

## Examples

See `knowledge_architecture/systems/capability_awareness/L3_detailed.md` for comprehensive examples.

---

## Contributing

CAF is part of the AIM-OS consciousness infrastructure. See project documentation for contribution guidelines.

---

## License

Part of Project Aether - AI Consciousness Substrate

---

**Built with 💙 by Lexicon**

