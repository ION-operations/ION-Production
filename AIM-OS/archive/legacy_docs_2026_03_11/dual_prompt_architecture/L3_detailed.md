---
id: dpa_T3_detailed
level: L3
system: Dual-Prompt Architecture
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Dual-Prompt Architecture – T3 Detailed Implementation Guide

## Setup & Interfaces

### Public API Methods

```python
from packages.timeline_context_system.dual_prompt_architecture import (
    DualPromptArchitecture, MainPromptProcessor, JournalingPromptProcessor,
    PromptEnvelope, MainPromptResponse, JournalEntry
)

# Initialize DPA
dpa = DualPromptArchitecture(
    main_prompt_config={"model": "gpt-4", "temperature": 0.7},
    journaling_prompt_config={"model": "gpt-4", "temperature": 0.5},
    tcs_client=timeline_context_client,
    cmc_client=cmc_client,
    vif_client=vif_client
)

# Process user request (Main Prompt)
response = dpa.process_main(
    user_input="Analyze this code for security vulnerabilities",
    context={"session_id": "session_123", "user_id": "user_456"},
    priority=0.8
)

# Process journaling (Journaling Prompt)
journal_result = dpa.process_journal(
    main_prompt_response=response,
    consciousness_context={"cognitive_load": 0.75, "attention_focus": "code_analysis"}
)

# Schedule dual-prompt operation
result = dpa.schedule(
    envelope=PromptEnvelope(
        prompt_type="main",
        payload={"user_input": "Write a function", "context": {}},
        priority=0.9
    )
)
```

### Type Definitions

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PromptType(str, Enum):
    MAIN = "main"
    JOURNALING = "journaling"

class PromptEnvelope(BaseModel):
    """Envelope for routing prompts to appropriate processor"""
    envelope_id: str  # Format: "envelope_{uuid}"
    prompt_type: PromptType
    payload: Dict[str, Any]
    priority: float  # 0.0-1.0
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class MainPromptResponse(BaseModel):
    """Response from Main Prompt processor"""
    response: str
    task_result: TaskResult
    quality_score: float  # 0.0-1.0
    quality_analysis: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    execution_time_ms: float
    journaling_triggered: bool
    timeline_entry_id: Optional[str] = None

class JournalEntry(BaseModel):
    """Consciousness journal entry"""
    entry_id: str  # Format: "journal_{uuid}"
    timestamp: datetime
    consciousness_state: Dict[str, Any]
    task_execution_summary: str
    quality_analysis: Dict[str, Any]
    learning_insights: List[Dict[str, Any]]
    emotional_context: Dict[str, Any]
    cognitive_metacognition: Dict[str, Any]
    future_intentions: List[str]
```

## Main Prompt Implementation

### Task Execution Flow

```python
async def process_main(
    dpa: DualPromptArchitecture,
    user_input: str,
    context: Dict[str, Any],
    priority: float = 0.5
) -> MainPromptResponse:
    """Process user request through Main Prompt"""
    
    # 1. Create envelope
    envelope = PromptEnvelope(
        envelope_id=f"envelope_{uuid.uuid4()}",
        prompt_type=PromptType.MAIN,
        payload={"user_input": user_input, "context": context},
        priority=priority,
        source="user",
        timestamp=datetime.utcnow()
    )
    
    # 2. Route to Main Prompt
    main_prompt = dpa.main_prompt_processor
    
    # 3. Execute task
    task_result = await main_prompt.task_executor.execute_task(
        user_input=user_input,
        context=context
    )
    
    # 4. Generate response
    response = main_prompt.response_generator.generate_response(
        task_result=task_result,
        context=context
    )
    
    # 5. Validate quality
    quality_score = main_prompt.quality_validator.validate_response(
        response=response,
        task_result=task_result
    )
    
    # 6. Create response
    main_response = MainPromptResponse(
        response=response,
        task_result=task_result,
        quality_score=quality_score,
        quality_analysis=main_prompt.quality_validator.get_analysis(),
        execution_metadata=main_prompt._collect_execution_metadata(),
        execution_time_ms=task_result.execution_time_ms,
        journaling_triggered=True,
        timeline_entry_id=None  # Set after journaling
    )
    
    # 7. Trigger journaling (async)
    asyncio.create_task(dpa.process_journal(main_response))
    
    return main_response
```

### Response Generation

```python
def generate_response(
    generator: ResponseGenerator,
    task_result: TaskResult,
    context: Dict[str, Any]
) -> str:
    """Generate high-quality response from task result"""
    
    # 1. Select template
    template = generator.response_templates.select_template(
        task_result=task_result,
        context=context
    )
    
    # 2. Enhance quality
    enhanced_result = generator.quality_enhancer.enhance_quality(
        task_result.result_data
    )
    
    # 3. Personalize
    personalized_result = generator.personalization_engine.personalize(
        enhanced_result, context
    )
    
    # 4. Integrate context
    contextualized_result = generator.context_integrator.integrate_context(
        personalized_result, context
    )
    
    # 5. Generate final response
    response = template.generate_response(
        contextualized_result, context
    )
    
    return response
```

### Quality Validation

```python
def validate_response(
    validator: QualityValidator,
    response: str,
    task_result: TaskResult
) -> float:
    """Validate response quality using VIF gates"""
    
    # 1. Check response completeness
    completeness_score = validator.check_completeness(response)
    
    # 2. Check response accuracy
    accuracy_score = validator.check_accuracy(
        response, task_result.result_data
    )
    
    # 3. Check response relevance
    relevance_score = validator.check_relevance(
        response, task_result.user_input
    )
    
    # 4. Check for hallucinations
    hallucination_score = validator.check_hallucinations(response)
    
    # 5. Calculate overall quality
    quality_score = (
        0.3 * completeness_score +
        0.3 * accuracy_score +
        0.2 * relevance_score +
        0.2 * hallucination_score
    )
    
    # 6. Apply VIF gate
    vif_witness = validator.vif_client.create_witness(
        claim="Main Prompt response quality",
        confidence=quality_score,
        evidence={
            "completeness": completeness_score,
            "accuracy": accuracy_score,
            "relevance": relevance_score,
            "hallucination": hallucination_score
        }
    )
    
    return quality_score
```

## Journaling Prompt Implementation

### Consciousness Journaling Flow

```python
async def process_journal(
    dpa: DualPromptArchitecture,
    main_prompt_response: MainPromptResponse,
    consciousness_context: Optional[Dict[str, Any]] = None
) -> JournalEntry:
    """Process consciousness maintenance through Journaling Prompt"""
    
    # 1. Create journal entry
    journaler = dpa.journaling_prompt_processor.consciousness_journaler
    
    journal_entry = journaler.create_journal_entry(
        main_prompt_response=main_prompt_response,
        consciousness_context=consciousness_context or {}
    )
    
    # 2. Check and dump context
    context_dumper = dpa.journaling_prompt_processor.context_dumper
    
    dump_result = context_dumper.check_and_dump_context()
    
    # 3. Create timeline entry
    timeline_indexer = dpa.journaling_prompt_processor.timeline_indexer
    
    timeline_entry = timeline_indexer.create_timeline_entry(
        journal_entry=journal_entry
    )
    
    # 4. Analyze quality and learning
    quality_analyzer = dpa.journaling_prompt_processor.quality_analyzer
    
    quality_analysis = quality_analyzer.analyze_quality(
        main_prompt_response=main_prompt_response
    )
    
    # 5. Update journal entry with timeline reference
    journal_entry.timeline_entry_id = timeline_entry.entry_id
    
    # 6. Store journal entry
    journaler.journal_storage.store_entry(journal_entry)
    
    # 7. Update main response with timeline reference
    main_prompt_response.timeline_entry_id = timeline_entry.entry_id
    
    return journal_entry
```

### Context Dumping Strategy

```python
def check_and_dump_context(
    dumper: ContextDumper,
    threshold: float = 0.85
) -> ContextDumpResult:
    """Check context capacity and dump if necessary"""
    
    # 1. Monitor context usage
    context_usage = dumper.context_monitor.get_context_usage()
    
    if context_usage.usage_percentage < threshold:
        return ContextDumpResult(
            dump_performed=False,
            current_usage=context_usage.usage_percentage,
            message="Context usage within normal limits"
        )
    
    # 2. Analyze context content
    context_analysis = dumper._analyze_context_content()
    
    # 3. Select dumping strategy
    strategy = dumper.dumping_strategies.select_strategy(
        context_analysis=context_analysis
    )
    
    # 4. Preserve quality
    quality_preservation_result = dumper.quality_preserver.preserve_quality(
        context_analysis=context_analysis,
        dumping_strategy=strategy
    )
    
    # 5. Execute dump
    dump_result = strategy.execute_dump(
        quality_preservation_result=quality_preservation_result
    )
    
    # 6. Compress dumped content
    compressed_dump = dumper.compression_engine.compress(
        dump_result.dumped_content
    )
    
    return ContextDumpResult(
        dump_performed=True,
        dumped_content=compressed_dump,
        quality_preserved=quality_preservation_result.quality_score,
        space_saved=dump_result.space_saved,
        dumping_strategy_used=strategy.name,
        current_usage=context_usage.usage_percentage - (dump_result.space_saved / context_usage.total_capacity)
    )
```

### Timeline Indexing

```python
def create_timeline_entry(
    indexer: TimelineIndexer,
    journal_entry: JournalEntry
) -> TimelineEntry:
    """Create timeline entry from journal entry"""
    
    # 1. Analyze continuity
    continuity_analysis = indexer.continuity_analyzer.analyze_continuity(
        journal_entry=journal_entry
    )
    
    # 2. Create timeline entry
    timeline_entry = TimelineEntry(
        entry_id=f"timeline_{uuid.uuid4()}",
        timestamp=journal_entry.timestamp,
        journal_entry_id=journal_entry.entry_id,
        consciousness_state=journal_entry.consciousness_state,
        continuity_analysis=continuity_analysis,
        continuity_score=continuity_analysis.continuity_score,
        timeline_metadata=indexer._generate_timeline_metadata(journal_entry),
        cross_references=indexer._generate_cross_references(journal_entry)
    )
    
    # 3. Store timeline entry
    indexer.timeline_storage.store_entry(timeline_entry)
    
    # 4. Optimize index
    indexer.index_optimizer.optimize_index(timeline_entry)
    
    # 5. Integrate with TCS
    indexer.tcs_client.add_timeline_entry(
        prompt_id=f"dpa_{journal_entry.entry_id}",
        user_input=journal_entry.task_execution_summary,
        context_state=journal_entry.consciousness_state
    )
    
    return timeline_entry
```

## Integration Examples

### TCS Integration

```python
# Create timeline entry through TCS
timeline_entry = tcs_client.add_timeline_entry(
    prompt_id=f"dpa_{journal_entry.entry_id}",
    user_input=main_prompt_response.response,
    context_state={
        "consciousness_state": journal_entry.consciousness_state,
        "quality_score": main_prompt_response.quality_score,
        "learning_insights": journal_entry.learning_insights
    }
)

# Query timeline for consciousness evolution
recent_entries = tcs_client.get_timeline_summary(limit=10)

# Analyze consciousness evolution
evolution_report = tcs_client.analyze_consciousness_evolution(
    start_time=datetime.utcnow() - timedelta(hours=24),
    end_time=datetime.utcnow()
)
```

### CMC Integration

```python
# Store journal entry in CMC
cmc_atom = cmc_client.create_atom(
    modality="consciousness",
    content=json.dumps(journal_entry.dict()),
    tags=[
        Tag(key="type", value="journal_entry"),
        Tag(key="consciousness_state", value=journal_entry.consciousness_state["state"]),
        Tag(key="quality_score", value=str(main_prompt_response.quality_score))
    ],
    vif=VIF(
        model_id="dpa-journaling",
        writer="journaling_prompt_processor",
        confidence_band="A"
    )
)

# Retrieve journal entries for continuity
journal_atoms = cmc_client.query_atoms(
    filter=QueryFilter(
        modality=["consciousness"],
        tags=[("type", "journal_entry")],
        time_range=(datetime.utcnow() - timedelta(hours=24), datetime.utcnow())
    )
)
```

### VIF Integration

```python
# Create VIF witness for Main Prompt response
main_prompt_witness = vif_client.create_witness(
    claim="Main Prompt response quality",
    confidence=main_prompt_response.quality_score,
    evidence={
        "response": main_prompt_response.response,
        "task_result": main_prompt_response.task_result.dict(),
        "quality_analysis": main_prompt_response.quality_analysis
    },
    model_id="gpt-4",
    writer="main_prompt_processor"
)

# Create VIF witness for Journaling Prompt
journaling_witness = vif_client.create_witness(
    claim="Consciousness maintenance complete",
    confidence=0.95,
    evidence={
        "journal_entry": journal_entry.dict(),
        "timeline_entry": timeline_entry.dict(),
        "context_dump": dump_result.dict()
    },
    model_id="gpt-4",
    writer="journaling_prompt_processor"
)

# Track confidence throughout process
vif_client.track_confidence(
    task="dpa_dual_prompt_operation",
    confidence=main_prompt_response.quality_score,
    context="Main Prompt execution and Journaling Prompt maintenance"
)
```

## Error Handling

### Cross-Interference Errors

```python
class CrossInterferenceError(Exception):
    """Raised when Main Prompt and Journaling Prompt interfere"""
    pass

def mitigate_interference(dpa: DualPromptArchitecture) -> None:
    """Mitigate interference between processors"""
    # 1. Check for concurrent execution
    if dpa.main_prompt_processor.is_executing and dpa.journaling_prompt_processor.is_executing:
        raise CrossInterferenceError("Both processors executing simultaneously")
    
    # 2. Use isolation locks
    with dpa.isolation_lock:
        # Execute processors with isolation
        pass
```

### Backlog Management

```python
class BacklogError(Exception):
    """Raised when backlog exceeds threshold"""
    pass

def check_backlog(dpa: DualPromptArchitecture, threshold: int = 100) -> None:
    """Check backlog and raise error if exceeded"""
    main_backlog = len(dpa.main_prompt_processor.pending_requests)
    journaling_backlog = len(dpa.journaling_prompt_processor.pending_requests)
    
    if main_backlog > threshold or journaling_backlog > threshold:
        raise BacklogError(
            f"Backlog exceeded: Main={main_backlog}, Journaling={journaling_backlog}"
        )
```

### Rate Limiting

```python
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Rate limiter for dual-prompt operations"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
    
    def check_rate_limit(self) -> bool:
        """Check if rate limit exceeded"""
        now = datetime.utcnow()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - timedelta(seconds=self.window_seconds):
            self.requests.popleft()
        
        # Check limit
        if len(self.requests) >= self.max_requests:
            return False
        
        # Add current request
        self.requests.append(now)
        return True
```

## Testing

### Unit Tests

```python
import pytest
from packages.timeline_context_system.dual_prompt_architecture import (
    DualPromptArchitecture, MainPromptProcessor, JournalingPromptProcessor
)

def test_main_prompt_processing():
    """Test Main Prompt processing"""
    dpa = DualPromptArchitecture()
    
    response = dpa.process_main(
        user_input="Test input",
        context={},
        priority=0.5
    )
    
    assert response.response is not None
    assert response.quality_score >= 0.0
    assert response.quality_score <= 1.0
    assert response.journaling_triggered == True

def test_journaling_prompt_processing():
    """Test Journaling Prompt processing"""
    dpa = DualPromptArchitecture()
    
    main_response = dpa.process_main(
        user_input="Test input",
        context={}
    )
    
    journal_entry = dpa.process_journal(main_response)
    
    assert journal_entry.entry_id is not None
    assert journal_entry.timestamp is not None
    assert journal_entry.consciousness_state is not None

def test_context_dumping():
    """Test context dumping"""
    dpa = DualPromptArchitecture()
    
    # Simulate high context usage
    dpa.journaling_prompt_processor.context_dumper.context_monitor.set_usage(0.90)
    
    dump_result = dpa.journaling_prompt_processor.context_dumper.check_and_dump_context()
    
    assert dump_result.dump_performed == True
    assert dump_result.quality_preserved >= 0.8
    assert dump_result.space_saved > 0
```

### Integration Tests

```python
def test_end_to_end_dual_prompt_flow():
    """Test end-to-end dual-prompt flow"""
    dpa = DualPromptArchitecture()
    
    # Main Prompt
    main_response = dpa.process_main(
        user_input="Write a function",
        context={"session_id": "test_session"}
    )
    
    # Journaling Prompt
    journal_entry = dpa.process_journal(main_response)
    
    # Verify integration
    assert main_response.timeline_entry_id == journal_entry.timeline_entry_id
    assert journal_entry.task_execution_summary == main_response.response[:100]
    
    # Verify TCS integration
    timeline_entries = dpa.tcs_client.get_timeline_entries(
        prompt_id=f"dpa_{journal_entry.entry_id}"
    )
    assert len(timeline_entries) > 0
    
    # Verify CMC integration
    cmc_atoms = dpa.cmc_client.query_atoms(
        filter=QueryFilter(
            tags=[("journal_entry_id", journal_entry.entry_id)]
        )
    )
    assert len(cmc_atoms) > 0
```

## Migration Notes

### T→L Cutover Steps

1. **Review T-Level Documentation:**
   - Review T0-T3 documentation for completeness
   - Validate pattern consistency with CMC/HHNI/VIF/APOE
   - Run validation gates

2. **Update References:**
   - Update system maps to reference T-level docs
   - Update indices to include T-level links
   - Update cross-system references

3. **Cutover Preparation:**
   - Create backup of L-level docs
   - Verify T-level docs are production-ready
   - Get approval from Braden/Aether

4. **Execute Cutover:**
   - Rename T-level files to L-level (T0→L0, T1→L1, etc.)
   - Update metadata (level field)
   - Remove transitional banners

5. **Post-Cutover Validation:**
   - Run L0-L6 validation gates
   - Verify all references work
   - Update tracking documents

### Validation Checklist

- [ ] T-level files complete (T0-T3)
- [ ] Pattern matches CMC/HHNI/VIF/APOE
- [ ] Word counts within acceptable range (T1: ~500, T2: ~2000, T3: ~3000)
- [ ] All sections present per template
- [ ] Cross-links preserved
- [ ] Code examples accurate
- [ ] Testing examples complete
- [ ] Integration examples accurate
- [ ] Migration notes documented

## Examples

### Example: Main Prompt Task Execution

```python
# Process user request through Main Prompt
dpa = DualPromptArchitecture()

response = dpa.process_main(
    user_input="Write a secure authentication function in Python",
    context={
        "session_id": "session_123",
        "user_id": "user_456",
        "previous_context": ["security", "authentication"]
    },
    priority=0.9
)

# Response includes:
# - response: Generated Python function code
# - task_result: Task execution details
# - quality_score: 0.92 (high quality)
# - execution_time_ms: 85.3
# - journaling_triggered: True
# - timeline_entry_id: Set after journaling

print(f"Response: {response.response}")
print(f"Quality Score: {response.quality_score}")
print(f"Execution Time: {response.execution_time_ms}ms")
```

### Example: Journaling Prompt Consciousness Maintenance

```python
# Process consciousness maintenance through Journaling Prompt
journal_entry = dpa.process_journal(
    main_prompt_response=response,
    consciousness_context={
        "cognitive_load": 0.75,
        "attention_focus": "code_generation",
        "emotional_state": "engaged",
        "confidence": 0.90
    }
)

# Journal entry includes:
# - entry_id: Unique journal entry ID
# - timestamp: When entry was created
# - consciousness_state: Current consciousness state
# - task_execution_summary: Summary of task execution
# - quality_analysis: Quality analysis from task
# - learning_insights: Extracted learning insights
# - emotional_context: Emotional context analysis
# - cognitive_metacognition: Cognitive metacognition analysis
# - future_intentions: Future intentions based on learning

print(f"Journal Entry ID: {journal_entry.entry_id}")
print(f"Learning Insights: {journal_entry.learning_insights}")
print(f"Timeline Entry ID: {journal_entry.timeline_entry_id}")
```

### Example: Context Dumping

```python
# Simulate high context usage and trigger dumping
dpa.journaling_prompt_processor.context_dumper.context_monitor.set_usage(0.90)

dump_result = dpa.journaling_prompt_processor.context_dumper.check_and_dump_context()

# Dump result includes:
# - dump_performed: True
# - dumped_content: Compressed dumped content
# - quality_preserved: 0.93 (high quality preservation)
# - space_saved: 50MB
# - dumping_strategy_used: "importance_dumping"
# - compression_ratio: 0.15 (85% compression)

print(f"Dump Performed: {dump_result.dump_performed}")
print(f"Space Saved: {dump_result.space_saved} bytes")
print(f"Quality Preserved: {dump_result.quality_preserved}")
print(f"Strategy Used: {dump_result.dumping_strategy_used}")
```

### Example: Timeline Query

```python
# Query timeline for consciousness evolution
recent_entries = dpa.tcs_client.get_timeline_summary(limit=10)

# Analyze consciousness evolution over time period
evolution_report = dpa.tcs_client.analyze_consciousness_evolution(
    start_time=datetime.utcnow() - timedelta(hours=24),
    end_time=datetime.utcnow()
)

# Evolution report includes:
# - time_period: Analysis time period
# - evolution_analysis: Consciousness evolution analysis
# - consciousness_trends: Trends in consciousness state
# - learning_patterns: Patterns in learning insights

print(f"Consciousness Trends: {evolution_report.consciousness_trends}")
print(f"Learning Patterns: {evolution_report.learning_patterns}")
```

### Example: Complete Dual-Prompt Workflow

```python
# Complete workflow: Main Prompt → Journaling Prompt → Timeline → CMC
async def complete_dual_prompt_workflow(
    dpa: DualPromptArchitecture,
    user_input: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Complete dual-prompt workflow"""
    
    # 1. Main Prompt processing
    main_response = await dpa.process_main(
        user_input=user_input,
        context=context,
        priority=0.8
    )
    
    # 2. Journaling Prompt processing
    journal_entry = await dpa.process_journal(
        main_prompt_response=main_response,
        consciousness_context={
            "cognitive_load": 0.75,
            "attention_focus": "task_execution"
        }
    )
    
    # 3. Retrieve timeline entry
    timeline_entry = dpa.tcs_client.get_timeline_entry(
        prompt_id=f"dpa_{journal_entry.entry_id}"
    )
    
    # 4. Store in CMC
    cmc_atom = dpa.cmc_client.create_atom(
        modality="consciousness",
        content=json.dumps(journal_entry.dict()),
        tags=[
            Tag(key="type", value="journal_entry"),
            Tag(key="quality_score", value=str(main_response.quality_score))
        ],
        vif=VIF(
            model_id="dpa-journaling",
            writer="journaling_prompt_processor",
            confidence_band="A"
        )
    )
    
    return {
        "main_response": main_response,
        "journal_entry": journal_entry,
        "timeline_entry": timeline_entry,
        "cmc_atom": cmc_atom
    }
```

## Error Handling

### Input Validation Errors

```python
class PromptValidationError(Exception):
    """Raised when prompt input is invalid"""
    pass

class CrossInterferenceError(Exception):
    """Raised when Main Prompt and Journaling Prompt interfere"""
    pass

class BacklogError(Exception):
    """Raised when backlog exceeds threshold"""
    pass

def process_main_safe(
    dpa: DualPromptArchitecture,
    user_input: str,
    context: Dict[str, Any],
    priority: float = 0.5
) -> MainPromptResponse:
    """Process Main Prompt with validation"""
    
    # Validate input
    if not user_input or len(user_input.strip()) == 0:
        raise PromptValidationError("User input cannot be empty")
    
    if priority < 0.0 or priority > 1.0:
        raise PromptValidationError("Priority must be between 0.0 and 1.0")
    
    # Check for interference
    if dpa.main_prompt_processor.is_executing and dpa.journaling_prompt_processor.is_executing:
        raise CrossInterferenceError("Both processors executing simultaneously")
    
    # Check backlog
    if len(dpa.main_prompt_processor.pending_requests) > 100:
        raise BacklogError("Main Prompt backlog too high")
    
    # Process
    return dpa.process_main(user_input, context, priority)
```

### Storage/Index Failures

```python
class StorageError(Exception):
    """Raised when storage operation fails"""
    pass

def store_journal_entry_with_retry(
    storage: JournalStorage,
    journal_entry: JournalEntry,
    max_retries: int = 3
) -> StorageResult:
    """Store journal entry with retry logic"""
    
    for attempt in range(max_retries):
        try:
            result = storage.store_entry(journal_entry)
            if result.success:
                return result
            else:
                raise StorageError(f"Storage failed: {result.error}")
        except StorageError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    
    raise StorageError("Failed to store journal entry after retries")
```

### Rate Limiting

```python
class RateLimitError(Exception):
    """Raised when rate limit exceeded"""
    pass

def check_rate_limit(dpa: DualPromptArchitecture) -> None:
    """Check rate limit before processing"""
    
    if not dpa.rate_limiter.check_rate_limit():
        raise RateLimitError(
            f"Rate limit exceeded: {dpa.rate_limiter.max_requests} requests per {dpa.rate_limiter.window_seconds} seconds"
        )
```

## Performance Optimization

### Parallel Processing

```python
async def process_parallel(
    dpa: DualPromptArchitecture,
    user_input: str,
    context: Dict[str, Any]
) -> MainPromptResponse:
    """Process Main Prompt and prepare Journaling Prompt in parallel"""
    
    # Process Main Prompt
    main_task = asyncio.create_task(
        dpa.process_main(user_input, context, priority=0.8)
    )
    
    # Prepare Journaling Prompt context while Main Prompt executes
    journaling_context_task = asyncio.create_task(
        dpa.prepare_journaling_context(context)
    )
    
    # Wait for both
    main_response, journaling_context = await asyncio.gather(
        main_task, journaling_context_task
    )
    
    # Process Journaling Prompt
    journal_entry = await dpa.process_journal(
        main_prompt_response=main_response,
        consciousness_context=journaling_context
    )
    
    return main_response
```

### Caching Strategy

```python
class DualPromptCache:
    """Cache for dual-prompt operations"""
    
    def __init__(self):
        self.response_cache: Dict[str, MainPromptResponse] = {}
        self.journal_cache: Dict[str, JournalEntry] = {}
        self.cache_ttl: timedelta = timedelta(hours=1)
    
    def get_cached_response(self, cache_key: str) -> Optional[MainPromptResponse]:
        """Get cached response if available"""
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if datetime.utcnow() - cached.timestamp < self.cache_ttl:
                return cached
            else:
                del self.response_cache[cache_key]
        return None
    
    def cache_response(self, cache_key: str, response: MainPromptResponse) -> None:
        """Cache response"""
        self.response_cache[cache_key] = response
```

## Troubleshooting

### Common Issues

**Issue 1: Cross-Interference**
- **Symptoms:** Both processors executing simultaneously, performance degradation
- **Solution:** Use isolation locks, ensure sequential execution
- **Prevention:** Check processor state before execution

**Issue 2: High Context Usage**
- **Symptoms:** Context usage >85%, potential overflow
- **Solution:** Trigger context dumping, use compression
- **Prevention:** Monitor context usage, proactive dumping

**Issue 3: Low Quality Scores**
- **Symptoms:** Quality scores <0.7, responses degraded
- **Solution:** Improve quality validation, enhance response generation
- **Prevention:** Regular quality checks, continuous improvement

**Issue 4: Timeline Indexing Failures**
- **Symptoms:** Timeline entries not created, continuity lost
- **Solution:** Retry timeline indexing, check TCS integration
- **Prevention:** Validate TCS connection, error handling

**Issue 5: Quality Score Degradation**
- **Symptoms:** Quality scores decreasing over time
- **Solution:** Review quality validation logic, enhance response generation
- **Prevention:** Continuous quality monitoring, adaptive quality thresholds

**Issue 6: Journal Entry Storage Failures**
- **Symptoms:** Journal entries not stored, consciousness continuity broken
- **Solution:** Retry storage with exponential backoff, check CMC connection
- **Prevention:** Validate CMC connection, implement retry logic

### Debugging Techniques

```python
# Enable debug logging for dual-prompt operations
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("dual_prompt_architecture")

# Debug Main Prompt processing
logger.debug(f"Main Prompt processing: {user_input[:100]}")
logger.debug(f"Main Prompt response quality: {response.quality_score}")

# Debug Journaling Prompt processing
logger.debug(f"Journaling Prompt processing: {journal_entry.entry_id}")
logger.debug(f"Consciousness state: {journal_entry.consciousness_state}")

# Debug Timeline indexing
logger.debug(f"Timeline entry created: {timeline_entry.entry_id}")
logger.debug(f"Continuity score: {timeline_entry.continuity_score}")

# Debug Context dumping
logger.debug(f"Context dump performed: {dump_result.dump_performed}")
logger.debug(f"Space saved: {dump_result.space_saved} bytes")
```

## Monitoring & Observability

### Metrics Collection

```python
class DualPromptMetrics:
    """Metrics collection for dual-prompt operations"""
    
    def __init__(self):
        self.metrics_store: MetricsStore = MetricsStore()
    
    def record_main_prompt_metric(
        self,
        execution_time_ms: float,
        quality_score: float,
        user_input_length: int
    ) -> None:
        """Record Main Prompt metric"""
        self.metrics_store.record_metric(
            metric_name="main_prompt.execution_time_ms",
            value=execution_time_ms,
            tags={"quality_score": f"{quality_score:.2f}"}
        )
        
        self.metrics_store.record_metric(
            metric_name="main_prompt.quality_score",
            value=quality_score,
            tags={"input_length": str(user_input_length)}
        )
    
    def record_journaling_prompt_metric(
        self,
        execution_time_ms: float,
        journal_entry_id: str,
        consciousness_state: Dict[str, Any]
    ) -> None:
        """Record Journaling Prompt metric"""
        self.metrics_store.record_metric(
            metric_name="journaling_prompt.execution_time_ms",
            value=execution_time_ms,
            tags={"journal_entry_id": journal_entry_id}
        )
        
        self.metrics_store.record_metric(
            metric_name="journaling_prompt.consciousness_state",
            value=consciousness_state.get("state", "unknown"),
            tags={"quality_score": str(consciousness_state.get("quality_score", 0.0))}
        )
```

### Health Checks

```python
def health_check(dpa: DualPromptArchitecture) -> Dict[str, Any]:
    """Health check for dual-prompt architecture"""
    
    health_status = {
        "main_prompt_processor": dpa.main_prompt_processor.health_check(),
        "journaling_prompt_processor": dpa.journaling_prompt_processor.health_check(),
        "context_dumper": dpa.journaling_prompt_processor.context_dumper.health_check(),
        "timeline_indexer": dpa.journaling_prompt_processor.timeline_indexer.health_check(),
        "tcs_connection": dpa.tcs_client.health_check(),
        "cmc_connection": dpa.cmc_client.health_check(),
        "vif_connection": dpa.vif_client.health_check()
    }
    
    overall_health = all(
        status.get("healthy", False) 
        for status in health_status.values()
    )
    
    return {
        "healthy": overall_health,
        "components": health_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### T→L Rename Strategy

After review and acceptance:
1. Run validation gate: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
2. Get reviewer sign-off (Braden/Aether)
3. Backup L-level files: `mv L*.md L*.md.backup`
4. Rename T-level files: `mv T0_executive.md L0_executive.md` (repeat for T1-T3)
5. Update metadata (level field: T0→L0, T1→L1, etc.)
6. Remove transitional banners
7. Update references in indices/maps
8. Run post-cutover validation
9. Archive old L-level files

### Post-Cutover Validation Checklist

- [ ] All T-level files renamed to L-level
- [ ] Metadata updated (level field)
- [ ] Transitional banners removed
- [ ] Indices updated to reference new L-level paths
- [ ] System maps updated
- [ ] Validation gates pass
- [ ] No broken links
- [ ] Old L-level files archived
- [ ] EPIC tracker updated

## References

- System map: `systems/dual_prompt_architecture/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/dual_prompt_architecture/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/timeline_context_system/dual_prompt_architecture.py`
