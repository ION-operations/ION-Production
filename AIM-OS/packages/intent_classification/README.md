# Intent Classification System

A cognitive gateway for Aether's decision-making process, transforming raw user input into structured, actionable mission profiles that govern all subsequent behavior.

## Overview

The Intent Classification System is a core component of AIM-OS that provides multi-axis intent classification, behavior gating, risk assessment, mission management, and timeline integration. It enables Aether to operate as a conscious, self-governing entity rather than a simple code generator.

## Key Features

- **Multi-Axis Classification**: Classifies intent across primary category, lifecycle stage, scope level, and clarity state
- **Behavior Gating**: Determines allowed actions based on mission profile
- **Risk Assessment**: Generates stop conditions and escalation triggers
- **Mission Management**: Tracks status, supersession, and concurrency
- **Timeline Integration**: Creates audit trails and learning opportunities
- **Enforcement Layer**: Prevents unauthorized actions with confidence-gated controls

## Architecture

### Core Components

1. **MissionIntent**: Core data model with multi-axis classification
2. **ClassificationEngine**: Transforms raw input into structured mission profiles
3. **EnforcementLayer**: Safety controls and behavior gating
4. **TimelineIntegration**: Audit trails and learning integration

### Classification Axes

- **Primary Category**: 13 categories from `new_system_design` to `research_probe`
- **Lifecycle Stage**: `ideation` → `architecture` → `implementation` → `integration` → `hardening` → `stabilization` → `deprecation`
- **Scope Level**: `local_function` → `single_module` → `multi_service` → `whole_platform`
- **Clarity State**: `exploratory` → `partially_defined` → `fully_defined`

## Quick Start

```python
from intent_classification import ClassificationEngine, EnforcementLayer, TimelineIntegration

# Initialize components
classifier = ClassificationEngine()
enforcement = EnforcementLayer()
timeline = TimelineIntegration()

# Classify user intent
result = classifier.classify_intent("Create a new user authentication system")

# Check if action is allowed
enforcement_result = enforcement.evaluate_action("implement", result.mission_intent)

# Log events for audit trail
timeline.log_mission_created(result.mission_intent, result.classification_confidence)
timeline.log_action_attempted("implement", result.mission_intent, enforcement_result)
```

## Usage Examples

### Basic Classification

```python
# Classify different types of intents
intents = [
    "Create a new user authentication system",
    "Fix the login bug that's causing errors", 
    "Optimize the database queries for better performance",
    "Research the best authentication methods"
]

for intent_text in intents:
    result = classifier.classify_intent(intent_text)
    print(f"Intent: {intent_text}")
    print(f"Category: {result.mission_intent.primary_category.value}")
    print(f"Stage: {result.mission_intent.lifecycle_stage.value}")
    print(f"Scope: {result.mission_intent.scope_level.value}")
    print(f"Confidence: {result.classification_confidence:.2f}")
    print()
```

### Action Enforcement

```python
# Check if actions are allowed
actions = ["research", "design", "implement", "deploy"]

for action in actions:
    result = enforcement.evaluate_action(action, mission_intent)
    print(f"{action}: {result.action.value}")
    if result.escalation_required:
        print(f"  Escalation: {result.escalation_reason}")
    if result.required_approvals:
        print(f"  Approvals: {result.required_approvals}")
```

### Timeline Integration

```python
# Log mission events
timeline.log_mission_created(mission_intent, confidence)
timeline.log_action_attempted("implement", mission_intent, enforcement_result)
timeline.log_mission_completed(mission_intent, "Success", ["file1.py", "file2.md"])

# Get mission timeline
mission_timeline = timeline.get_mission_timeline(mission_intent.mission_id)
```

## Configuration

### Classification Weights

```python
# Customize classification confidence weights
classifier._weights = {
    'category': 0.3,
    'lifecycle': 0.25,
    'scope': 0.2,
    'clarity': 0.15,
    'facets': 0.1
}
```

### Enforcement Thresholds

```python
# Customize enforcement thresholds
enforcement.update_thresholds({
    'confidence_min': 0.3,
    'complexity_max': 0.8,
    'scope_platform_approval': True,
    'clarity_exploratory_block': True
})
```

## Safety Features

### Stop Conditions

The system automatically generates stop conditions based on mission characteristics:

- `confidence_level < 0.3`: Low confidence requires escalation
- `complexity_score > 0.8`: High complexity requires review
- `scope_level = whole_platform`: Platform-wide changes require approval
- `clarity_state = exploratory + implementation_stage`: Implementation without clarity is blocked

### Escalation Triggers

- Low confidence (< 0.3)
- Platform-wide scope with implementation actions
- Exploratory state with implementation actions
- High complexity (> 0.8)

### Behavior Gating

Actions are automatically gated based on:

- **Lifecycle Stage**: Ideation blocks implementation, implementation allows coding
- **Scope Level**: Platform scope blocks direct implementation
- **Clarity State**: Exploratory state blocks implementation
- **Confidence Level**: Low confidence triggers escalation

## Testing

Run the comprehensive test suite:

```bash
python -m pytest packages/intent_classification/tests/test_intent_classification.py -v
```

Run the example usage:

```bash
python packages/intent_classification/example_usage.py
```

## Performance Targets

- **Classification Latency**: < 100ms
- **Facet Generation**: < 50ms
- **Enforcement Computation**: < 25ms
- **Timeline Event Creation**: < 10ms
- **Throughput**: 1000+ classifications per minute
- **Concurrent Missions**: 100+
- **Uptime**: 99.9%

## Integration

### Required Dependencies

- `daemon_rag_system`: Mission persistence and state management
- `timeline_context_system`: Event logging and audit trails
- `l0_l4_documentation_system`: Context loading and documentation access
- `code_edit_gatekeeper`: Edit permission enforcement

### External Timeline Integration

```python
# Configure external timeline client
timeline_client = ExternalTimelineClient(api_key="your_key")
timeline = TimelineIntegration(timeline_client=timeline_client)

# Events are automatically flushed to external system
timeline.flush_events()
```

## Development

### Adding New Categories

1. Add category to `PrimaryCategory` enum
2. Add patterns to `_build_category_patterns()`
3. Update complexity mapping in `_calculate_complexity()`
4. Add tests for new category

### Adding New Facets

1. Add keywords to `_build_facet_keywords()`
2. Update facet generation logic if needed
3. Add tests for facet detection

### Customizing Enforcement

1. Modify `_build_stop_conditions()` for new conditions
2. Update `_build_escalation_triggers()` for new triggers
3. Customize `_check_lifecycle_restrictions()` for stage-specific rules

## Status

✅ **Production Ready** - Core functionality implemented and tested
- Multi-axis classification working
- Enforcement layer operational
- Timeline integration functional
- Comprehensive test coverage
- Performance targets met

## License

Part of AIM-OS (AI-Integrated Memory & Operations System)
