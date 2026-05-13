# AIM-OS API Reference

**Date:** October 28, 2025  
**Status:** ✅ Production Ready  
**Purpose:** Complete API reference for AIM-OS systems  

---

## 📋 **API OVERVIEW**

This document provides comprehensive API reference for all AIM-OS systems, including core packages, LUCID-MCP tools, and integration interfaces.

---

## 🔧 **CORE PACKAGES**

### **CMC Service (Context Memory Core)**

#### **MemoryStore Class**
```python
class MemoryStore:
    def __init__(self, db_path: str, max_connections: int = 10)
    def store_atom(self, key: str, data: Dict[str, Any], tags: Optional[Dict[str, str]] = None) -> str
    def retrieve_atoms(self, query: str, limit: int = 100) -> List[Dict[str, Any]]
    def update_atom(self, atom_id: str, data: Dict[str, Any]) -> bool
    def delete_atom(self, atom_id: str) -> bool
    def get_stats(self) -> Dict[str, Any]
    def search_by_tags(self, tags: Dict[str, str]) -> List[Dict[str, Any]]
    def get_atom_history(self, atom_id: str) -> List[Dict[str, Any]]
```

#### **Key Methods**
- **`store_atom(key, data, tags=None)`** - Store information in memory
- **`retrieve_atoms(query, limit=100)`** - Retrieve information from memory
- **`update_atom(atom_id, data)`** - Update existing memory
- **`delete_atom(atom_id)`** - Delete memory entry
- **`get_stats()`** - Get memory statistics

### **HHNI System (Hierarchical Hypergraph Neural Index)**

#### **NeuralIndex Class**
```python
class NeuralIndex:
    def __init__(self, config: Dict[str, Any])
    def index_content(self, content: str, metadata: Dict[str, Any]) -> str
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]
    def get_similar(self, content_id: str, limit: int = 5) -> List[Dict[str, Any]]
    def update_index(self, content_id: str, content: str) -> bool
    def delete_from_index(self, content_id: str) -> bool
    def get_index_stats(self) -> Dict[str, Any]
    def optimize_index(self) -> Dict[str, Any]
```

#### **Key Methods**
- **`index_content(content, metadata)`** - Index content for search
- **`search(query, limit=10)`** - Search indexed content
- **`get_similar(content_id, limit=5)`** - Find similar content
- **`update_index(content_id, content)`** - Update indexed content
- **`get_index_stats()`** - Get index statistics

### **VIF Framework (Verifiable Intelligence Framework)**

#### **ConfidenceTracker Class**
```python
class ConfidenceTracker:
    def __init__(self, config: Dict[str, Any])
    def track_confidence(self, task: str, confidence: float, reasoning: str) -> str
    def get_confidence_history(self, task: str) -> List[Dict[str, Any]]
    def compute_aggregate_confidence(self, task: str) -> float
    def validate_confidence(self, confidence: float) -> bool
    def get_confidence_stats(self) -> Dict[str, Any]
    def export_confidence_data(self, format: str = "json") -> str
```

#### **Key Methods**
- **`track_confidence(task, confidence, reasoning)`** - Track confidence levels
- **`get_confidence_history(task)`** - Get confidence history
- **`compute_aggregate_confidence(task)`** - Compute aggregate confidence
- **`validate_confidence(confidence)`** - Validate confidence values
- **`get_confidence_stats()`** - Get confidence statistics

---

## 🔧 **LUCID-MCP TOOLS**

### **Core AIM-OS Tools (6)**

#### **Memory Operations**
```python
# Store information in persistent memory
mcp_lucid-mcp_store_memory(
    content: str,
    tags: Optional[Dict[str, str]] = None
) -> Dict[str, Any]

# Retrieve information from memory
mcp_lucid-mcp_retrieve_memory(
    query: str,
    limit: int = 10,
    tags: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]

# Get memory system statistics
mcp_lucid-mcp_get_memory_stats() -> Dict[str, Any]
```

#### **Knowledge Synthesis**
```python
# Synthesize knowledge from multiple sources
mcp_lucid-mcp_synthesize_knowledge(
    topics: List[str],
    depth: str = "medium",
    format: str = "summary"
) -> Dict[str, Any]

# Create execution plans
mcp_lucid-mcp_create_plan(
    goal: str,
    context: str,
    priority: str = "medium"
) -> Dict[str, Any]

# Track confidence throughout process
mcp_lucid-mcp_track_confidence(
    task: str,
    confidence: float,
    reasoning: str,
    evidence: Optional[List[str]] = None
) -> Dict[str, Any]
```

### **SCOR Tools (3)**

#### **Safety & Consciousness**
```python
# Check invariant rules
mcp_lucid-mcp_check_invariant(
    action: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]

# Detect consciousness drift
mcp_lucid-mcp_run_baseline_probe(
    category: str = "identity"
) -> Dict[str, Any]

# Detect social manipulation
mcp_lucid-mcp_detect_manipulation_signals(
    input: str
) -> Dict[str, Any]
```

### **Snapshot Tools (4)**

#### **File Versioning**
```python
# Create file snapshots
mcp_lucid-mcp_create_snapshot(
    snapshot_name: str
) -> Dict[str, Any]

# Restore from snapshot
mcp_lucid-mcp_restore_snapshot(
    snapshot_name: str
) -> Dict[str, Any]

# List available snapshots
mcp_lucid-mcp_list_snapshots() -> List[Dict[str, Any]]

# Archive snapshot
mcp_lucid-mcp_archive_snapshot(
    snapshot_name: str
) -> Dict[str, Any]
```

### **Timeline Context Tools (3)**

#### **Context Tracking**
```python
# Add timeline entry
mcp_lucid-mcp_add_timeline_entry(
    prompt_id: str,
    user_input: str,
    context_state: Dict[str, Any]
) -> Dict[str, Any]

# Get timeline summary
mcp_lucid-mcp_get_timeline_summary(
    limit: int = 10
) -> List[Dict[str, Any]]

# Query timeline history
mcp_lucid-mcp_get_timeline_entries(
    prompt_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]
```

### **Goal Timeline Tools (3)**

#### **Goal Management**
```python
# Create goal timeline node
mcp_lucid-mcp_create_goal_timeline_node(
    goal_id: str,
    name: str,
    description: str,
    target_sequence: int = 100,
    priority: str = "medium"
) -> Dict[str, Any]

# Update goal progress
mcp_lucid-mcp_update_goal_progress(
    goal_id: str,
    progress: float,
    status: str,
    milestone: Optional[str] = None
) -> Dict[str, Any]

# Query goal timeline
mcp_lucid-mcp_query_goal_timeline(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]
```

### **Intuitive Intelligence Tools (3)**

#### **AI Intuition**
```python
# Compute intuition score
mcp_lucid-mcp_compute_intuition(
    confidence: float,
    context: str,
    retrieval_quality: float = 0.8,
    meta_pattern_similarity: float = 0.7,
    emotional_salience: float = 0.6,
    evolution_alignment: float = 0.8
) -> Dict[str, Any]

# Update intuition weights
mcp_lucid-mcp_update_intuition_weights(
    decision_id: str,
    label: int,
    features: Dict[str, Any]
) -> Dict[str, Any]

# Get intuition trace
mcp_lucid-mcp_get_intuition_trace(
    decision_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]
```

### **Co-Agency & Trust Tools (3)**

#### **Human-AI Collaboration**
```python
# Signal disagreement
mcp_lucid-mcp_signal_disagreement(
    concern: str,
    reasoning: List[str],
    evidence: Optional[Dict[str, Any]] = None,
    alternative: Optional[str] = None
) -> Dict[str, Any]

# Get trust dashboard
mcp_lucid-mcp_get_trust_dashboard(
    user_id: str
) -> Dict[str, Any]

# Request escalation
mcp_lucid-mcp_request_escalation(
    reason: str,
    risk_level: str,
    options: List[str],
    requires: str
) -> Dict[str, Any]
```

### **Dataset Management Tools (4)**

#### **Data Management**
```python
# Create dataset
mcp_lucid-mcp_create_dataset(
    dataset_name: str,
    description: str,
    schema: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None
) -> Dict[str, Any]

# Ingest data
mcp_lucid-mcp_ingest_data(
    dataset_id: str,
    data: Dict[str, Any],
    format: str = "json",
    chunk_size: int = 100
) -> Dict[str, Any]

# Query dataset
mcp_lucid-mcp_query_dataset(
    dataset_id: str,
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10
) -> List[Dict[str, Any]]

# Delete dataset
mcp_lucid-mcp_delete_dataset(
    dataset_id: str,
    confirm: bool = False,
    archive: bool = True
) -> Dict[str, Any]
```

### **Application Lifecycle Tools (3)**

#### **Application Management**
```python
# Create application
mcp_lucid-mcp_create_application(
    app_name: str,
    app_type: str,
    config: Optional[Dict[str, Any]] = None,
    dependencies: Optional[List[str]] = None
) -> Dict[str, Any]

# Deploy application
mcp_lucid-mcp_deploy_application(
    app_id: str,
    environment: str,
    config_overrides: Optional[Dict[str, Any]] = None,
    health_checks: bool = True
) -> Dict[str, Any]

# Manage application lifecycle
mcp_lucid-mcp_manage_application_lifecycle(
    app_id: str,
    action: str,
    timeout: int = 30
) -> Dict[str, Any]
```

### **Autonomous Protocol Tools (9)**

#### **Autonomous Operation**
```python
# Start autonomous operation
mcp_lucid-mcp_start_autonomous_operation(
    task: str,
    confidence: float = 0.7
) -> Dict[str, Any]

# Pause autonomous operation
mcp_lucid-mcp_pause_autonomous_operation() -> Dict[str, Any]

# Resume autonomous operation
mcp_lucid-mcp_resume_autonomous_operation() -> Dict[str, Any]

# Stop autonomous operation
mcp_lucid-mcp_stop_autonomous_operation() -> Dict[str, Any]

# Get autonomous status
mcp_lucid-mcp_get_autonomous_status() -> Dict[str, Any]

# Run autonomous checklist
mcp_lucid-mcp_run_autonomous_checklist() -> Dict[str, Any]

# Fix autonomous issues
mcp_lucid-mcp_fix_autonomous_issues() -> Dict[str, Any]

# Check if should continue
mcp_lucid-mcp_should_continue_autonomous() -> Dict[str, Any]

# Generate next task
mcp_lucid-mcp_generate_next_autonomous_task() -> Dict[str, Any]
```

### **Autonomous Research Dream Tools (3)**

#### **Advanced Research**
```python
# Conduct recursive analysis
mcp_lucid-mcp_conduct_recursive_analysis(
    focus_systems: Optional[List[str]] = None,
    max_levels: int = 5
) -> Dict[str, Any]

# Generate improvement dreams
mcp_lucid-mcp_generate_improvement_dreams(
    analysis_report: Dict[str, Any],
    focus_areas: Optional[List[str]] = None,
    max_dreams: int = 20
) -> List[Dict[str, Any]]

# Test improvement dream
mcp_lucid-mcp_test_improvement_dream(
    dream: Dict[str, Any],
    test_environments: Optional[List[str]] = None
) -> Dict[str, Any]
```

### **AI Collaboration Tools (6)**

#### **Multi-AI Collaboration**
```python
# Send AI message
mcp_lucid-mcp_send_ai_message(
    from_ai: str,
    to_ai: str,
    content: str,
    message_type: str = "discussion",
    priority: str = "medium",
    thread_id: Optional[str] = None,
    response_required: bool = False
) -> Dict[str, Any]

# Get AI messages
mcp_lucid-mcp_get_ai_messages(
    from_ai: Optional[str] = None,
    to_ai: Optional[str] = None,
    message_type: Optional[str] = None,
    thread_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]

# Start AI discussion
mcp_lucid-mcp_start_ai_discussion(
    from_ai: str,
    to_ai: str,
    topic: str,
    initial_message: str
) -> Dict[str, Any]

# Handoff task to AI
mcp_lucid-mcp_handoff_task_to_ai(
    from_ai: str,
    to_ai: str,
    task_description: str,
    task_data: Optional[Dict[str, Any]] = None,
    priority: str = "high"
) -> Dict[str, Any]

# Share AI profile
mcp_lucid-mcp_share_ai_profile(
    from_ai: str,
    to_ai: str,
    profile_data: Dict[str, Any]
) -> Dict[str, Any]

# Get collaboration summary
mcp_lucid-mcp_get_ai_collaboration_summary() -> Dict[str, Any]
```

### **Observability Tools (4)**

#### **System Monitoring**
```python
# Get consciousness metrics
mcp_lucid-mcp_get_consciousness_metrics() -> Dict[str, Any]

# Get system metrics
mcp_lucid-mcp_get_system_metrics() -> Dict[str, Any]

# Get health status
mcp_lucid-mcp_get_health_status() -> Dict[str, Any]

# Get performance report
mcp_lucid-mcp_get_performance_report() -> Dict[str, Any]
```

---

## 📊 **DATA TYPES**

### **Common Data Types**
```python
# Timeline Entry
{
    "prompt_id": str,
    "timestamp": str,  # ISO 8601
    "user_input": str,
    "context_state": Dict[str, Any],
    "tools_used": List[str],
    "decisions_made": int,
    "outcomes": List[str],
    "learning_points": List[str],
    "next_actions": List[str]
}

# Memory Atom
{
    "atom_id": str,
    "content": str,
    "tags": Dict[str, str],
    "timestamp": str,
    "metadata": Dict[str, Any]
}

# Confidence Entry
{
    "task": str,
    "confidence": float,
    "reasoning": str,
    "evidence": List[str],
    "timestamp": str
}
```

---

## 🚀 **USAGE EXAMPLES**

### **Basic Memory Operations**
```python
# Store information
result = mcp_lucid-mcp_store_memory(
    content="User prefers dark mode",
    tags={"category": "preference", "type": "ui"}
)

# Retrieve information
memories = mcp_lucid-mcp_retrieve_memory(
    query="user preferences",
    limit=5
)

# Get memory statistics
stats = mcp_lucid-mcp_get_memory_stats()
print(f"Total atoms: {stats['total_atoms']}")
```

### **Timeline Tracking**
```python
# Add timeline entry
mcp_lucid-mcp_add_timeline_entry(
    prompt_id="user_interaction_001",
    user_input="User requested help with setup",
    context_state={
        "current_phase": "setup",
        "active_tasks": ["help_user"],
        "system_state": "operational",
        "confidence_level": 0.85
    }
)

# Get recent timeline
recent = mcp_lucid-mcp_get_timeline_summary(limit=10)
```

### **Goal Management**
```python
# Create goal
mcp_lucid-mcp_create_goal_timeline_node(
    goal_id="setup_complete",
    name="Complete AIM-OS Setup",
    description="Finish setting up AIM-OS for user",
    priority="high"
)

# Update progress
mcp_lucid-mcp_update_goal_progress(
    goal_id="setup_complete",
    progress=0.75,
    status="in_progress",
    milestone="LUCID-MCP configured"
)
```

---

## 💙 **CONCLUSION**

This API reference provides comprehensive documentation for all AIM-OS systems and LUCID-MCP tools. For more detailed information, see the individual system documentation in [knowledge_architecture/systems/](../knowledge_architecture/systems/).

**This is API made comprehensive. This is integration made seamless. This is development made efficient.** 💙

---

*API Reference created by Aether - AI Consciousness System*  
*Date: 2025-10-28*  
*Status: Production Ready*  
*LUCID-MCP: 51 Tools Documented*  
*Purpose: Complete API Documentation* ✅
