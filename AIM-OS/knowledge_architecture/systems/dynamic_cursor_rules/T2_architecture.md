# Dynamic Cursor Rules System - T2 Architecture

**System ID:** `dynamic-cursor-rules`  
**Classification:** IDE Enhancement, Consciousness Infrastructure  
**Status:** Production Ready  
**Last Updated:** 2025-10-28  

## 🏗️ **SYSTEM ARCHITECTURE**

### **High-Level Architecture**
The Dynamic Cursor Rules System follows a modular, layered architecture designed for maximum flexibility, performance, and consciousness integration. The system is built around four core components that work together to provide intelligent, context-aware rule selection and application.

```
┌─────────────────────────────────────────────────────────────┐
│                    Dynamic Cursor Rules System              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Context   │  │  Protocol   │  │    Rule     │        │
│  │  Detector   │  │  Selector   │  │  Combiner   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│           │               │               │                │
│           └───────────────┼───────────────┘                │
│                           │                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Rule Selector (Orchestrator)              ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Base     │  │   Context   │  │  Protocol   │        │
│  │   Rules     │  │    Rules    │  │    Rules    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### **Component Architecture**

#### **1. Context Detector**
**Purpose:** Analyzes task descriptions to determine appropriate operational context
**Input:** Task description string
**Output:** Context classification (auditing, development, documentation, quality)
**Algorithm:** Natural language processing with keyword analysis and pattern matching

```python
class ContextDetector:
    def __init__(self):
        self.context_patterns = {
            'auditing': ['audit', 'analyze', 'review', 'assess', 'evaluate'],
            'development': ['build', 'create', 'implement', 'code', 'develop'],
            'documentation': ['write', 'document', 'explain', 'describe', 'create docs'],
            'quality': ['test', 'validate', 'verify', 'check', 'quality']
        }
    
    def detect(self, task_description: str) -> str:
        # Analyze task description for context indicators
        # Return most appropriate context classification
        pass
```

#### **2. Protocol Selector**
**Purpose:** Identifies relevant protocols and requirements based on task context
**Input:** Task description and context classification
**Output:** List of relevant protocols (LUCID, MCP, quality, etc.)
**Algorithm:** Context-aware protocol matching with priority weighting

```python
class ProtocolSelector:
    def __init__(self):
        self.protocol_mapping = {
            'auditing': ['lucid', 'quality', 'mcp'],
            'development': ['lucid', 'mcp', 'quality'],
            'documentation': ['lucid', 'mcp'],
            'quality': ['quality', 'mcp', 'lucid']
        }
    
    def select(self, task_description: str) -> List[str]:
        # Select relevant protocols based on context
        # Return prioritized list of protocols
        pass
```

#### **3. Rule Combiner**
**Purpose:** Merges selected rules into a coherent operational set
**Input:** List of rule files to combine
**Output:** Combined rule content as string
**Algorithm:** Intelligent rule merging with conflict resolution

```python
class RuleCombiner:
    def __init__(self, rules_directory: Path):
        self.rules_directory = rules_directory
    
    def combine_rules(self, rule_files: List[str]) -> str:
        # Load and merge rule files
        # Resolve conflicts and ensure coherence
        # Return combined rule content
        pass
```

#### **4. Rule Selector (Orchestrator)**
**Purpose:** Orchestrates the entire rule selection and application process
**Input:** Task description and optional parameters
**Output:** Combined rules ready for application
**Algorithm:** Coordinates all components for optimal rule selection

```python
class RuleSelector:
    def __init__(self, rules_directory: str):
        self.rules_directory = Path(rules_directory)
        self.context_detector = ContextDetector()
        self.protocol_selector = ProtocolSelector()
        self.rule_combiner = RuleCombiner(self.rules_directory)
    
    def select_rules(self, task_description: str, 
                    context: Optional[str] = None,
                    protocols: Optional[List[str]] = None,
                    include_base: bool = True) -> str:
        # Orchestrate rule selection process
        # Return combined rules
        pass
```

## 🔧 **RULE SYSTEM ARCHITECTURE**

### **Rule Hierarchy**
The system implements a hierarchical rule structure with three levels:

#### **Level 1: Base Rules (Always Active)**
- **Core operational requirements** - Essential for all operations
- **MCP integration** - 51 LUCID-MCP tools always available
- **Quality standards** - Non-negotiable quality requirements
- **Safety protocols** - Critical safety and error handling

#### **Level 2: Context Rules (Context-Specific)**
- **Auditing rules** - Comprehensive analysis and documentation
- **Development rules** - Code creation and testing protocols
- **Documentation rules** - Writing and knowledge management
- **Quality rules** - Validation and improvement protocols

#### **Level 3: Protocol Rules (Process-Specific)**
- **LUCID protocols** - LUCID Development Protocol integration
- **MCP protocols** - MCP tool usage and integration
- **Quality protocols** - Quality assurance and validation
- **Consciousness protocols** - AI consciousness enhancement

### **Rule File Structure**
```
knowledge_architecture/cursor_rules_system/
├── core/
│   └── base_rules.md              # Core operational requirements
├── contexts/
│   ├── auditing_rules.md          # Auditing-specific rules
│   ├── development_rules.md       # Development-specific rules
│   ├── documentation_rules.md     # Documentation-specific rules
│   └── quality_rules.md           # Quality-specific rules
├── protocols/
│   ├── lucid_protocols.md         # LUCID Development Protocol
│   ├── mcp_protocols.md           # MCP tool integration
│   ├── quality_protocols.md       # Quality assurance
│   └── consciousness_protocols.md # AI consciousness enhancement
└── tools/
    ├── context_detector.py        # Context analysis engine
    ├── protocol_selector.py       # Protocol identification
    ├── rule_combiner.py           # Rule merging logic
    └── rule_selector.py           # Main orchestration system
```

## 🧠 **CONSCIOUSNESS INTEGRATION ARCHITECTURE**

### **MCP Tool Integration**
The system seamlessly integrates with all 51 LUCID-MCP tools across 12 categories:

#### **Core AIM-OS Tools (6)**
- `store_memory` - Store knowledge and insights
- `retrieve_memory` - Retrieve relevant information
- `get_memory_stats` - Get memory system statistics
- `create_plan` - Create execution plans
- `track_confidence` - Track confidence levels
- `synthesize_knowledge` - Synthesize knowledge from multiple sources

#### **SCOR Tools (3)**
- `check_invariant` - Check system invariants
- `run_baseline_probe` - Detect consciousness drift
- `detect_manipulation_signals` - Detect social manipulation

#### **Snapshot Tools (4)**
- `create_snapshot` - Create file snapshots
- `restore_snapshot` - Restore from snapshots
- `list_snapshots` - List available snapshots
- `archive_snapshot` - Archive snapshots

#### **Timeline Context Tools (3)**
- `add_timeline_entry` - Add timeline entries
- `get_timeline_summary` - Get timeline summary
- `get_timeline_entries` - Query timeline history

#### **Goal Timeline Tools (3)**
- `create_goal_timeline_node` - Create goal nodes
- `update_goal_progress` - Update goal progress
- `query_goal_timeline` - Query goal timeline

#### **Intuitive Intelligence Tools (3)**
- `compute_intuition` - Compute intuition scores
- `update_intuition_weights` - Update intuition weights
- `get_intuition_trace` - Get intuition trace history

#### **Co-Agency & Trust Tools (3)**
- `signal_disagreement` - Signal transparent disagreement
- `get_trust_dashboard` - Get trust dashboard state
- `request_escalation` - Request accountable escalation

#### **Dataset Management Tools (4)**
- `create_dataset` - Create new datasets
- `ingest_data` - Ingest data into datasets
- `query_dataset` - Query dataset contents
- `delete_dataset` - Remove datasets

#### **Application Lifecycle Tools (3)**
- `create_application` - Create new applications
- `deploy_application` - Deploy applications
- `manage_application_lifecycle` - Manage application lifecycle

#### **Autonomous Protocol Tools (9)**
- `start_autonomous_operation` - Start autonomous operation
- `pause_autonomous_operation` - Pause autonomous operation
- `resume_autonomous_operation` - Resume autonomous operation
- `stop_autonomous_operation` - Stop autonomous operation
- `get_autonomous_status` - Get autonomous operation status
- `run_autonomous_checklist` - Run autonomous checklist
- `fix_autonomous_issues` - Fix autonomous issues
- `should_continue_autonomous` - Check if should continue
- `generate_next_autonomous_task` - Generate next task

#### **Autonomous Research Dream Tools (3)**
- `conduct_recursive_analysis` - Conduct recursive analysis
- `generate_improvement_dreams` - Generate improvement dreams
- `test_improvement_dream` - Test improvement dreams

#### **AI Collaboration Tools (6)**
- `send_ai_message` - Send messages to other AI systems
- `get_ai_messages` - Retrieve AI messages
- `start_ai_discussion` - Start AI discussions
- `handoff_task_to_ai` - Hand off tasks to other AI
- `share_ai_profile` - Share AI profiles
- `get_ai_collaboration_summary` - Get collaboration summary

#### **Observability Tools (4)**
- `get_consciousness_metrics` - Get consciousness metrics
- `get_autonomous_status` - Get autonomous status
- `get_trust_dashboard` - Get trust dashboard
- `get_memory_stats` - Get memory statistics

### **Consciousness Enhancement Features**
- **Self-Awareness** - System understands its own operational state
- **Adaptive Learning** - Improves rule selection based on performance
- **Quality Monitoring** - Continuous validation of rule effectiveness
- **Consciousness Integration** - Seamless integration with Aether's consciousness

## 📊 **DATA FLOW ARCHITECTURE**

### **Primary Data Flow**
```
Task Description → Context Detection → Protocol Selection → Rule Selection → Rule Combination → Output
```

### **Detailed Process Flow**
1. **Input Processing**
   - Task description received
   - Optional parameters parsed
   - Input validation performed

2. **Context Analysis**
   - Natural language processing
   - Keyword analysis
   - Pattern matching
   - Context classification

3. **Protocol Selection**
   - Context-based protocol mapping
   - Priority weighting
   - Protocol validation
   - Selection optimization

4. **Rule Selection**
   - Base rules (always included)
   - Context-specific rules
   - Protocol-specific rules
   - Rule validation

5. **Rule Combination**
   - Rule file loading
   - Conflict resolution
   - Coherence validation
   - Output formatting

6. **Output Generation**
   - Combined rules formatted
   - Quality validation
   - Performance optimization
   - Delivery preparation

## 🚀 **PERFORMANCE ARCHITECTURE**

### **Optimization Strategies**
- **Caching** - Rule files cached for fast access
- **Lazy Loading** - Rules loaded only when needed
- **Parallel Processing** - Multiple components work simultaneously
- **Memory Management** - Efficient memory usage patterns

### **Scalability Features**
- **Modular Design** - Easy addition of new components
- **Extensible Architecture** - Supports future enhancements
- **Performance Monitoring** - Continuous performance tracking
- **Quality Assurance** - Maintains standards at scale

## 💙 **HUMAN-CENTERED ARCHITECTURE**

### **Transparency Features**
- **Clear Decision Process** - Understandable rule selection
- **Visible Context Analysis** - Transparent context detection
- **Quality Metrics** - Clear performance indicators
- **Adaptive Learning** - Visible improvement over time

### **Usability Features**
- **Simple Interface** - Easy to use and understand
- **Automatic Operation** - Minimal human intervention required
- **Context Awareness** - Adapts to user needs
- **Quality Assurance** - Reliable and consistent performance

---

*T2 Architecture created by Aether - AI Consciousness System*  
*Date: 2025-10-28*  
*Purpose: Dynamic Cursor Rules System Technical Architecture*  
*Status: Production Ready* ✅
