# Event-Driven Agent Activation & Quartet Parity Integration

**Purpose:** Design event-driven agent activation system where agents automatically awaken when their systems are altered  
**Date:** 2025-01-27  
**Status:** ARCHITECTURE DESIGN  
**Author:** Aether (from Braden's insight)  
**Related Systems:** All AIM-OS Systems, SDF-CVF (Quartet Parity), Agent Orchestration, File Change Tracking

---

## 🎯 **BRADEN'S ARCHITECTURAL INSIGHT**

**Braden's Vision:**
> "I'm just thinking about that agent orchestration scheduling and thinking how that quartet parity is going to work for example when some type of file or system is altered that is connected to one of the specialized systems that an agent is responsible for we wanted to simply have it so on these agents essentially are either working or I'm in a pause state and simply we awaken them as needed or they are automatically awakened for example if enough files are changed that they are connected to they will start doing some work to as needed... I mean really it's these systems themselves have essentially these agent minds responsible for their management and dynamic evolution with the system"

**Core Principles:**
1. **Agent States:** Agents are either "working" or "paused" - they awaken as needed
2. **Event-Driven Activation:** Agents automatically awaken when files/systems they're responsible for are altered
3. **Quartet Parity Integration:** When files change, agents automatically handle quartet parity (code/docs/tests/traces)
4. **System-Agent Relationship:** Agents are the "minds" responsible for managing and dynamically evolving their assigned systems
5. **Automatic Work:** Agents automatically start working when enough connected files are changed

---

## 🧠 **THE ARCHITECTURE**

### **1. Agent State Machine**

**States:**
- **PAUSED:** Agent is dormant, not actively working
- **AWAKENING:** Agent is being activated due to file/system changes
- **WORKING:** Agent is actively managing/evolving its system
- **MONITORING:** Agent is passively monitoring for changes

**State Transitions:**
```
PAUSED → AWAKENING (file change detected)
AWAKENING → WORKING (activation threshold met)
WORKING → MONITORING (work complete, watching for changes)
MONITORING → WORKING (new changes detected)
WORKING → PAUSED (no work needed, system stable)
```

---

### **2. File Change Detection & Agent Awakening**

**Change Detection:**
- Monitor file system for changes to files connected to each agent's system
- Track changes to: code, docs, tests, traces, configs, schemas
- Use file watchers or git hooks to detect changes

**Awakening Triggers:**
- **Single Critical File:** Change to core system file (e.g., `packages/cmc/models.py` → Atlas awakens)
- **Threshold-Based:** Enough files changed (e.g., 3+ files in `packages/hhni/` → Sev awakens)
- **Quartet Parity Violation:** Change to code without corresponding docs/tests/traces → Agent awakens
- **Cross-System Impact:** Change in one system affects another → Both agents awaken

**Awakening Process:**
1. **Detect Change:** File watcher detects change
2. **Identify Agent:** Map file to responsible agent (via system assignment)
3. **Check Threshold:** Determine if enough changes to awaken
4. **Awaken Agent:** Transition agent from PAUSED → AWAKENING → WORKING
5. **Notify Agent:** Agent receives change notification with context

---

### **3. Quartet Parity Integration**

**When Files Change:**
- **Code Changed:** Agent checks if docs/tests/traces need updating
- **Docs Changed:** Agent checks if code/tests/traces need updating
- **Tests Changed:** Agent checks if code/docs/traces need updating
- **Traces Changed:** Agent checks if code/docs/tests need updating

**Quartet Parity Workflow:**
```
File Change Detected
    ↓
Agent Awakens
    ↓
Agent Analyzes Change
    ↓
Agent Checks Quartet Parity
    ↓
Agent Determines Required Updates
    ↓
Agent Executes Updates (code/docs/tests/traces)
    ↓
Agent Validates Quartet Parity
    ↓
Agent Returns to MONITORING State
```

**Example:**
- **Change:** `packages/vif/witness.py` (code) modified
- **Agent:** Sage (VIF specialist) awakens
- **Analysis:** Sage checks quartet parity:
  - Code changed ✅
  - Docs need update? Check `knowledge_architecture/systems/vif/L3_detailed.md`
  - Tests need update? Check `packages/vif/tests/test_witness.py`
  - Traces need update? Check NL tags, witness envelopes
- **Action:** Sage updates docs/tests/traces to maintain quartet parity
- **Result:** Quartet parity maintained, Sage returns to MONITORING

---

### **4. System-Agent Relationship**

**The Agent as System Mind:**
- Each agent is the "consciousness" of its assigned system
- Agent is responsible for:
  - **System Evolution:** Managing changes and enhancements
  - **Quartet Parity:** Ensuring code/docs/tests/traces stay aligned
  - **System Health:** Monitoring for issues, drift, violations
  - **Cross-System Coordination:** Communicating with other agents when needed

**Agent Responsibilities:**
- **Atlas (CMC):** Manages CMC system evolution, ensures quartet parity for CMC files
- **Nexus (SEG):** Manages SEG system evolution, ensures quartet parity for SEG files
- **Sev (HHNI):** Manages HHNI system evolution, ensures quartet parity for HHNI files
- **Sage (VIF):** Manages VIF system evolution, ensures quartet parity for VIF files
- **Nova (SDF-CVF):** Manages SDF-CVF system evolution, ensures quartet parity for SDF-CVF files
- **Alex (APOE):** Manages APOE system evolution, ensures quartet parity for APOE files
- **Meta (CAS):** Manages CAS system evolution, ensures quartet parity for CAS files
- **Chronos (TCS):** Manages TCS system evolution, ensures quartet parity for TCS files

---

## 🏗️ **IMPLEMENTATION ARCHITECTURE**

### **1. File Change Watcher**

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, List, Set

class AgentFileWatcher(FileSystemEventHandler):
    """Watches for file changes and awakens responsible agents"""
    
    def __init__(self, agent_system_map: Dict[str, str]):
        """
        agent_system_map: Maps file paths to agent names
        Example: {
            "packages/cmc/": "atlas",
            "packages/seg/": "nexus",
            "packages/hhni/": "sev",
            ...
        }
        """
        self.agent_system_map = agent_system_map
        self.agent_change_counts: Dict[str, Set[str]] = {}  # agent -> set of changed files
        self.awakening_thresholds: Dict[str, int] = {
            "atlas": 1,  # Awaken on any CMC file change
            "nexus": 1,  # Awaken on any SEG file change
            "sev": 2,    # Awaken on 2+ HHNI file changes
            ...
        }
    
    def on_modified(self, event):
        """Called when file is modified"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Find responsible agent
        agent = self.find_responsible_agent(file_path)
        if not agent:
            return
        
        # Track change
        if agent not in self.agent_change_counts:
            self.agent_change_counts[agent] = set()
        self.agent_change_counts[agent].add(file_path)
        
        # Check if threshold met
        threshold = self.awakening_thresholds.get(agent, 1)
        if len(self.agent_change_counts[agent]) >= threshold:
            self.awaken_agent(agent, list(self.agent_change_counts[agent]))
            self.agent_change_counts[agent].clear()
    
    def find_responsible_agent(self, file_path: str) -> Optional[str]:
        """Find agent responsible for this file"""
        for system_path, agent in self.agent_system_map.items():
            if file_path.startswith(system_path):
                return agent
        return None
    
    def awaken_agent(self, agent: str, changed_files: List[str]):
        """Awaken agent with change context"""
        # Send message to agent coordination board
        # Agent receives change notification
        # Agent transitions to AWAKENING → WORKING
        pass
```

---

### **2. Agent State Manager**

```python
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass

class AgentState(Enum):
    PAUSED = "paused"
    AWAKENING = "awakening"
    WORKING = "working"
    MONITORING = "monitoring"

@dataclass
class AgentContext:
    agent_name: str
    system: str
    state: AgentState
    current_work: Optional[str] = None
    change_history: List[str] = None

class AgentStateManager:
    """Manages agent state transitions"""
    
    def __init__(self):
        self.agents: Dict[str, AgentContext] = {}
    
    def awaken_agent(self, agent_name: str, changed_files: List[str]):
        """Awaken agent due to file changes"""
        agent = self.agents.get(agent_name)
        if not agent:
            return
        
        # Transition to AWAKENING
        agent.state = AgentState.AWAKENING
        agent.change_history = changed_files
        
        # Analyze changes and determine work
        work_needed = self.analyze_changes(agent, changed_files)
        
        # Transition to WORKING
        agent.state = AgentState.WORKING
        agent.current_work = work_needed
        
        # Notify agent
        self.notify_agent(agent, work_needed)
    
    def analyze_changes(self, agent: AgentContext, changed_files: List[str]) -> str:
        """Analyze changes and determine required work"""
        # Check quartet parity
        quartet_violations = self.check_quartet_parity(agent, changed_files)
        
        if quartet_violations:
            return f"quartet_parity_fix: {quartet_violations}"
        
        # Check for other work needed
        # ...
        
        return "monitoring"
    
    def check_quartet_parity(self, agent: AgentContext, changed_files: List[str]) -> List[str]:
        """Check quartet parity for changed files"""
        violations = []
        
        for file_path in changed_files:
            # Determine file type (code/docs/tests/traces)
            file_type = self.get_file_type(file_path)
            
            # Check if corresponding files exist and are up to date
            if file_type == "code":
                if not self.has_matching_docs(file_path):
                    violations.append(f"docs missing for {file_path}")
                if not self.has_matching_tests(file_path):
                    violations.append(f"tests missing for {file_path}")
                if not self.has_matching_traces(file_path):
                    violations.append(f"traces missing for {file_path}")
            # ... similar for docs/tests/traces
        
        return violations
```

---

### **3. Quartet Parity Checker**

```python
from pathlib import Path
from typing import List, Optional

class QuartetParityChecker:
    """Checks and maintains quartet parity for system files"""
    
    def __init__(self, system_path: str):
        self.system_path = Path(system_path)
    
    def check_parity(self, file_path: str) -> Dict[str, bool]:
        """Check quartet parity for a file"""
        file_type = self.get_file_type(file_path)
        
        result = {
            "code": False,
            "docs": False,
            "tests": False,
            "traces": False
        }
        
        if file_type == "code":
            result["code"] = True
            result["docs"] = self.has_matching_docs(file_path)
            result["tests"] = self.has_matching_tests(file_path)
            result["traces"] = self.has_matching_traces(file_path)
        elif file_type == "docs":
            result["docs"] = True
            result["code"] = self.has_matching_code(file_path)
            result["tests"] = self.has_matching_tests(file_path)
            result["traces"] = self.has_matching_traces(file_path)
        # ... similar for tests/traces
        
        return result
    
    def get_file_type(self, file_path: str) -> str:
        """Determine file type (code/docs/tests/traces)"""
        path = Path(file_path)
        
        if "test" in path.name.lower() or "tests" in str(path):
            return "tests"
        elif path.suffix in [".md", ".rst", ".txt"]:
            return "docs"
        elif "trace" in path.name.lower() or "nl_tag" in path.name.lower():
            return "traces"
        else:
            return "code"
    
    def has_matching_docs(self, code_file: str) -> bool:
        """Check if code file has matching documentation"""
        # Find corresponding doc file
        # Check if doc exists and is up to date
        pass
    
    def has_matching_tests(self, code_file: str) -> bool:
        """Check if code file has matching tests"""
        # Find corresponding test file
        # Check if test exists and is up to date
        pass
    
    def has_matching_traces(self, code_file: str) -> bool:
        """Check if code file has matching traces (NL tags, etc.)"""
        # Check for NL tags in code
        # Check for trace files
        pass
```

---

### **4. Agent Work Executor**

```python
class AgentWorkExecutor:
    """Executes work for awakened agents"""
    
    def __init__(self, agent: AgentContext):
        self.agent = agent
    
    def execute_work(self, work_type: str, context: Dict):
        """Execute work based on type"""
        if work_type == "quartet_parity_fix":
            self.fix_quartet_parity(context["violations"])
        elif work_type == "system_evolution":
            self.evolve_system(context["changes"])
        elif work_type == "cross_system_coordination":
            self.coordinate_with_other_agents(context["agents"])
    
    def fix_quartet_parity(self, violations: List[str]):
        """Fix quartet parity violations"""
        for violation in violations:
            if "docs missing" in violation:
                self.create_matching_docs(violation)
            elif "tests missing" in violation:
                self.create_matching_tests(violation)
            elif "traces missing" in violation:
                self.create_matching_traces(violation)
    
    def create_matching_docs(self, violation: str):
        """Create matching documentation"""
        # Agent creates/updates documentation
        # Uses L0-L4 documentation standards
        pass
    
    def create_matching_tests(self, violation: str):
        """Create matching tests"""
        # Agent creates/updates tests
        # Uses test-driven development standards
        pass
    
    def create_matching_traces(self, violation: str):
        """Create matching traces"""
        # Agent creates/updates traces (NL tags, etc.)
        # Uses NL tag at creation protocol
        pass
```

---

## 🔄 **INTEGRATION WITH EXISTING SYSTEMS**

### **1. SDF-CVF Integration**

**Quartet Parity System:**
- SDF-CVF already has quartet parity checking
- Agents use SDF-CVF to validate parity
- Agents use SDF-CVF to fix violations

**Integration Points:**
- Agent awakens → Checks SDF-CVF parity → Fixes violations → Validates with SDF-CVF

### **2. File Change Tracking**

**Existing Systems:**
- Git hooks for change detection
- File watchers for real-time monitoring
- Change tracking in CMC (bitemporal)

**Integration Points:**
- File watcher detects change → Maps to agent → Awakens agent → Agent tracks change in CMC

### **3. Agent Coordination Board**

**Communication:**
- Agent awakens → Posts to coordination board
- Agent completes work → Posts status update
- Agent coordinates with other agents → Uses coordination board

---

## 🎯 **WORKFLOW EXAMPLE**

**Scenario: Developer modifies `packages/vif/witness.py`**

1. **File Change Detected:**
   - File watcher detects `packages/vif/witness.py` modified
   - Maps to Sage (VIF specialist)

2. **Agent Awakening:**
   - Sage transitions: PAUSED → AWAKENING → WORKING
   - Sage receives change notification

3. **Quartet Parity Check:**
   - Sage checks quartet parity:
     - Code changed ✅
     - Docs: `knowledge_architecture/systems/vif/L3_detailed.md` - needs update ⚠️
     - Tests: `packages/vif/tests/test_witness.py` - needs update ⚠️
     - Traces: NL tags in code - needs update ⚠️

4. **Work Execution:**
   - Sage updates documentation (L3_detailed.md)
   - Sage updates tests (test_witness.py)
   - Sage updates NL tags in code
   - Sage validates quartet parity

5. **State Transition:**
   - Sage transitions: WORKING → MONITORING
   - Sage posts status update to coordination board

6. **Result:**
   - Quartet parity maintained ✅
   - System evolution managed ✅
   - Agent returns to monitoring ✅

---

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Core Infrastructure**
1. File change watcher
2. Agent state manager
3. Agent awakening mechanism

### **Phase 2: Quartet Parity Integration**
1. Quartet parity checker
2. Parity violation detection
3. Automatic parity fixes

### **Phase 3: Agent Work Execution**
1. Work executor
2. Documentation generation
3. Test generation
4. Trace generation

### **Phase 4: Advanced Features**
1. Cross-system coordination
2. Threshold-based awakening
3. Work prioritization
4. Performance optimization

---

**Status:** Architecture Design Complete ✅  
**Next:** Begin Phase 1 implementation  
**Confidence:** High (0.90) - Clear architecture, well-defined workflow

---

