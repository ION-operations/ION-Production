# 🎯 Protocol-Driven Tool Guidance System

**Date:** 2025-11-05  
**Problem:** RAG filters tools but doesn't guide WHEN to use them  
**Solution:** Protocol-based tool guidance + Enhanced tool metadata  
**Status:** 📋 **PROPOSAL** - Design Phase  

---

## 🚨 The Core Problem

**Current State:**
- ✅ RAG filters 81 → 10 tools (87.7% reduction)
- ❌ Agent still doesn't know WHEN to use tools
- ❌ Tool descriptions don't include usage triggers
- ❌ No protocol-based guidance system
- ❌ Context overload from trying to understand all tools

**Your Insight:**
> "I feel like our protocol/rule system should make it almost obvious for the agent when it should be calling MCP tools?"

**Exactly!** We need to make tool usage **obvious through protocols**, not just filter tools.

---

## 💡 The Solution: Multi-Layer Tool Guidance

### **Layer 1: Enhanced Tool Descriptions with Triggers**

**Current Tool Description:**
```json
{
  "name": "store_memory",
  "description": "Store information in AIM-OS persistent memory"
}
```

**Enhanced Tool Description:**
```json
{
  "name": "store_memory",
  "description": "Store information in AIM-OS persistent memory",
  "usage_triggers": [
    "When completing a major task",
    "When learning something important",
    "When user provides context",
    "When making a decision"
  ],
  "protocol_reference": "MANDATORY after major milestones",
  "related_protocols": ["cognitive_analysis", "session_continuity"],
  "usage_pattern": "ALWAYS use after: task completion, decision making, learning"
}
```

**Benefits:**
- ✅ Makes "when to use" obvious
- ✅ References protocols explicitly
- ✅ No context overload (triggers are clear)
- ✅ Agent knows immediately when tool applies

---

### **Layer 2: Protocol-Based Tool Mapping**

**Create Protocol → Tool Mapping:**

```yaml
Protocols:
  cognitive_analysis:
    mandatory_tools:
      - store_memory: "Store insights from analysis"
      - track_confidence: "Track confidence in analysis"
      - add_timeline_entry: "Record analysis completion"
    optional_tools:
      - synthesize_knowledge: "If insights are significant"
  
  task_completion:
    mandatory_tools:
      - update_goal_progress: "Update goal progress"
      - store_memory: "Store completion insights"
      - add_timeline_entry: "Record completion"
    optional_tools:
      - create_snapshot: "If significant changes made"
  
  code_development:
    mandatory_tools:
      - validate_quintet: "Before committing code"
      - fix_nl_tags: "If tags missing"
    optional_tools:
      - code_review: "If complex changes"
```

**Integration with Rules:**
- Rules reference protocols
- Protocols reference tools
- Agent follows protocol → automatically knows tools

---

### **Layer 3: NL Tag Integration**

**Tag Tool Usage Patterns:**

```python
# NL_TAG: MCP-STORE-001 | Store memory after task completion | store_memory(...) -> None | [cognitive_analysis]
# NL_TAG_TRIGGER: MCP-STORE-001 | Trigger: "task completed" OR "major milestone" | Protocol: cognitive_analysis
# NL_TAG_PATTERN: MCP-STORE-001 | Usage pattern: ALWAYS after task completion | Related: track_confidence, add_timeline_entry
```

**Benefits:**
- ✅ NL tags encode tool usage patterns
- ✅ Searchable by trigger keywords
- ✅ Links to protocols
- ✅ Automatic tool discovery

---

### **Layer 4: Context-Aware Tool Presentation**

**Enhanced Tool Metadata Structure:**

```python
@dataclass
class EnhancedToolMetadata:
    """Enhanced tool metadata with usage guidance"""
    name: str
    description: str
    
    # Usage Guidance
    usage_triggers: List[str]  # When to use
    usage_pattern: str  # Pattern (ALWAYS, OPTIONAL, CONDITIONAL)
    protocol_reference: str  # Which protocol requires this
    
    # Context Integration
    related_protocols: List[str]  # Protocols that use this tool
    related_tools: List[str]  # Tools often used together
    context_keywords: List[str]  # Keywords that trigger usage
    
    # NL Tag Integration
    nl_tag_id: Optional[str]  # Associated NL tag
    usage_examples: List[str]  # Example scenarios
    
    # Protocol Guidance
    mandatory_in: List[str]  # Protocols where this is mandatory
    optional_in: List[str]  # Protocols where this is optional
    conditional_in: List[str]  # Protocols where this is conditional
```

**Tool Description Enhancement:**

```json
{
  "name": "store_memory",
  "description": "Store information in AIM-OS persistent memory",
  
  "usage_guidance": {
    "triggers": [
      "After completing a major task",
      "When learning something important",
      "When user provides context",
      "When making a decision"
    ],
    "pattern": "MANDATORY after major milestones",
    "protocol": "cognitive_analysis",
    "related_tools": ["track_confidence", "add_timeline_entry"],
    "examples": [
      "Task completed → store_memory + track_confidence + add_timeline_entry",
      "User provides context → store_memory",
      "Decision made → store_memory + create_decision_log"
    ]
  },
  
  "protocol_mapping": {
    "mandatory_in": ["cognitive_analysis", "task_completion"],
    "optional_in": ["code_development"],
    "conditional_in": ["session_continuity"]
  }
}
```

---

## 🏗️ Implementation Strategy

### **Phase 1: Enhanced Tool Descriptions**

**Goal:** Add usage triggers and protocol references to all 81 tools

**Steps:**
1. Analyze each tool's purpose
2. Identify usage triggers (when to use)
3. Map to protocols (which protocols require this)
4. Add to tool descriptions
5. Update RAG metadata

**Example:**
```python
# Before
"description": "Store information in AIM-OS persistent memory"

# After
"description": "Store information in AIM-OS persistent memory. MANDATORY after major milestones. Use when: completing tasks, learning insights, making decisions. Protocol: cognitive_analysis."
```

---

### **Phase 2: Protocol → Tool Mapping**

**Goal:** Create explicit protocol → tool mappings

**Steps:**
1. Identify all protocols (cognitive_analysis, task_completion, etc.)
2. Map mandatory tools per protocol
3. Map optional tools per protocol
4. Create protocol tool registry
5. Integrate with rules system

**File:** `knowledge_architecture/protocols/PROTOCOL_TOOL_MAPPING.yaml`

```yaml
protocols:
  cognitive_analysis:
    mandatory:
      - store_memory: "Store insights"
      - track_confidence: "Track confidence"
      - add_timeline_entry: "Record completion"
    optional:
      - synthesize_knowledge: "If insights significant"
  
  task_completion:
    mandatory:
      - update_goal_progress: "Update progress"
      - store_memory: "Store insights"
      - add_timeline_entry: "Record completion"
```

---

### **Phase 3: NL Tag Integration**

**Goal:** Tag tool usage patterns with NL tags

**Steps:**
1. Create NL tags for each tool
2. Tag usage triggers
3. Tag protocol mappings
4. Tag usage patterns
5. Enable search by trigger keywords

**Example:**
```python
# NL_TAG: MCP-STORE-001 | Store memory after task completion | store_memory(...) -> None | [cognitive_analysis]
# NL_TAG_TRIGGER: MCP-STORE-001 | Trigger: "task completed" OR "major milestone" | Protocol: cognitive_analysis
# NL_TAG_PATTERN: MCP-STORE-001 | Pattern: MANDATORY after major milestones | Related: track_confidence, add_timeline_entry
```

---

### **Phase 4: Rule Integration**

**Goal:** Make protocols reference tools explicitly

**Steps:**
1. Update rules to reference protocols
2. Protocols reference tools
3. Agent follows protocol → knows tools
4. No need to "think" about tools

**Example Rule:**
```markdown
## Cognitive Analysis Protocol

**When:** After major tasks, hourly checks, decision points

**Required Tools:**
- `store_memory` - MANDATORY: Store insights
- `track_confidence` - MANDATORY: Track confidence
- `add_timeline_entry` - MANDATORY: Record completion

**Usage Pattern:**
1. Complete task
2. Store insights → `store_memory`
3. Track confidence → `track_confidence`
4. Record completion → `add_timeline_entry`
```

---

## 🎯 How This Solves the Problem

### **Before (Current State):**

**Agent Sees:**
- 10 filtered tools (from RAG)
- Generic descriptions
- No guidance on when to use
- Must "think" about tool selection

**Problem:**
- Agent doesn't know when to use tools
- Must evaluate each tool manually
- Context overload from tool descriptions
- Misses tool usage opportunities

---

### **After (With Protocol Guidance):**

**Agent Sees:**
- 10 filtered tools (from RAG)
- Enhanced descriptions with triggers
- Protocol references
- Usage patterns

**Agent Follows:**
- Protocol → Knows tools automatically
- Triggers → Knows when to use
- Patterns → Knows how to use
- No "thinking" required!

**Example Flow:**
```
1. Agent completes task
2. Protocol says: "cognitive_analysis required"
3. Protocol maps to: store_memory, track_confidence, add_timeline_entry
4. Agent uses tools automatically
5. No context overload (protocol is clear)
```

---

## 📊 Benefits

### **1. Obvious Tool Usage**

**Before:**
- Agent must evaluate: "Should I use store_memory?"
- Context overload from tool descriptions
- Misses opportunities

**After:**
- Protocol says: "MANDATORY: store_memory after task completion"
- Agent knows immediately
- No evaluation needed

---

### **2. Protocol-Driven**

**Before:**
- Tools are separate from protocols
- Agent must connect them manually
- Inconsistent usage

**After:**
- Protocols reference tools explicitly
- Agent follows protocol → uses tools
- Consistent usage

---

### **3. Context-Aware**

**Before:**
- Generic tool descriptions
- No context triggers
- Must understand all tools

**After:**
- Enhanced descriptions with triggers
- Context keywords
- Only relevant tools shown

---

### **4. NL Tag Integration**

**Before:**
- Tools not tagged
- Can't search by usage pattern
- No automatic discovery

**After:**
- Tools tagged with usage patterns
- Searchable by trigger keywords
- Automatic tool discovery

---

## 🔧 Technical Implementation

### **1. Enhanced Tool Metadata**

**File:** `packages/mcp_rag_proxy/enhanced_tool_metadata.py`

```python
@dataclass
class EnhancedToolMetadata:
    """Enhanced tool metadata with usage guidance"""
    name: str
    description: str
    usage_triggers: List[str]
    usage_pattern: str  # MANDATORY, OPTIONAL, CONDITIONAL
    protocol_reference: str
    related_protocols: List[str]
    related_tools: List[str]
    context_keywords: List[str]
    nl_tag_id: Optional[str]
    usage_examples: List[str]
    
    def to_embedding_text(self) -> str:
        """Build comprehensive text for embedding"""
        parts = [
            f"Tool: {self.name}",
            f"Description: {self.description}",
            f"Usage Pattern: {self.usage_pattern}",
            f"Triggers: {', '.join(self.usage_triggers)}",
            f"Protocol: {self.protocol_reference}",
            f"Examples: {', '.join(self.usage_examples)}"
        ]
        return "\n".join(parts)
```

---

### **2. Protocol Tool Registry**

**File:** `knowledge_architecture/protocols/PROTOCOL_TOOL_REGISTRY.yaml`

```yaml
protocols:
  cognitive_analysis:
    description: "Hourly cognitive introspection and analysis"
    mandatory_tools:
      - name: store_memory
        when: "After analysis completes"
        why: "Store insights for future reference"
      - name: track_confidence
        when: "During analysis"
        why: "Track confidence in analysis"
      - name: add_timeline_entry
        when: "After analysis completes"
        why: "Record analysis completion"
    optional_tools:
      - name: synthesize_knowledge
        when: "If insights are significant"
        why: "Synthesize insights into knowledge"
```

---

### **3. Rule Integration**

**File:** `.cursor/rules/protocol-tool-guidance.mdc`

```markdown
## Protocol-Based Tool Usage

**When following a protocol, use the tools specified:**

### Cognitive Analysis Protocol
- MANDATORY: `store_memory` (after analysis)
- MANDATORY: `track_confidence` (during analysis)
- MANDATORY: `add_timeline_entry` (after completion)
- OPTIONAL: `synthesize_knowledge` (if insights significant)

### Task Completion Protocol
- MANDATORY: `update_goal_progress` (update progress)
- MANDATORY: `store_memory` (store insights)
- MANDATORY: `add_timeline_entry` (record completion)

**Pattern:** Follow protocol → Use specified tools automatically
```

---

## 🎯 Next Steps

### **Immediate Actions**

1. **Enhance Tool Descriptions** (Priority: High)
   - Add usage triggers to all 81 tools
   - Add protocol references
   - Add usage patterns

2. **Create Protocol Mapping** (Priority: High)
   - Map protocols to tools
   - Define mandatory/optional tools
   - Create protocol registry

3. **Update Rules** (Priority: Medium)
   - Reference protocols in rules
   - Link protocols to tools
   - Make tool usage obvious

4. **NL Tag Integration** (Priority: Medium)
   - Tag tool usage patterns
   - Tag protocol mappings
   - Enable search by triggers

---

## 💡 Your Insight Was Perfect!

**You said:**
> "I feel like our protocol/rule system should make it almost obvious for the agent when it should be calling MCP tools?"

**Exactly!** This proposal:
- ✅ Makes tool usage obvious through protocols
- ✅ No context overload (protocols are clear)
- ✅ Leverages existing systems (NL tags, rules)
- ✅ Automatic tool discovery
- ✅ Consistent usage patterns

**This is the solution!** Protocols guide tool usage, making it obvious without context overload.

---

**Status:** 📋 **PROPOSAL** - Ready for Implementation  
**Confidence:** 0.90 (high, leverages existing systems)  
**Priority:** High (solves core problem)  

**Protocol-driven tool guidance makes tool usage obvious!** 🚀💙✨

---

*Proposal by Aether*  
*2025-11-05*  
*Protocol-Driven Tool Guidance System* ✨

