# Category Recognition Component

**Parent System:** Cognitive Analysis System (CAS)  
**Purpose:** Detect how tasks get classified and validate against actual requirements  
**Status:** Designed, ready for implementation  

---

## 🎯 **QUICK SUMMARY (100 words)**

Category Recognition detects task miscategorization - when "update priorities" gets classified as "routine documentation" instead of "critical memory modification." Validates perceived category/stakes/formality against actual requirements using rule-based triggers (file paths, operations, keywords). Identifies dangerous underestimations (treating critical as routine) vs safe overestimations (treating routine as critical). Provides required protocols for each category. Enables pre-task validation to catch errors before they happen. Core insight: Categorization errors are primary failure mode - wrong classification leads to wrong protocols, which leads to quality violations.

---

## 🔧 **CORE CAPABILITIES**

```yaml
task_classification:
  - Rule-based categorization
  - File path pattern matching
  - Operation type detection
  - Keyword analysis

validation:
  - Perceived vs actual comparison
  - Stakes estimation accuracy
  - Formality requirement matching
  - Protocol requirement identification

error_detection:
  - Category mismatch (wrong type)
  - Stakes underestimation (dangerous!)
  - Stakes overestimation (inefficient)
  - Correction requirement flagging
```

---

## 📊 **KEY DATA STRUCTURES**

### **TaskCategorization**
```python
@dataclass
class TaskCategorization:
    perceived_category: str
    perceived_stakes: StakesLevel  # LOW | MEDIUM | HIGH | CRITICAL
    actual_category: str
    actual_stakes: StakesLevel
    required_protocols: List[str]
    is_match: bool
    correction_needed: bool
```

### **CategoryRecognizer**
```python
class CategoryRecognizer:
    def categorize(self, task, files, op_type, perceived...) -> TaskCategorization
```

---

## 🏷️ **CATEGORY RULES**

```yaml
memory_modification:
  triggers: ["AETHER_MEMORY/", "active_context/"]
  stakes: CRITICAL
  protocols: ["CMC_bitemporal", "VIF_provenance", "SDF_quartet"]

code_implementation:
  triggers: ["packages/", "*.py"]
  stakes: HIGH
  protocols: ["test_driven_development", "VIF_witness"]

documentation:
  triggers: ["*.md"]
  stakes: MEDIUM
  protocols: ["clarity_check"]
```

---

## 🔗 **INTEGRATION**

**With CAS:**
- Used in pre-task analysis
- Validates task classification
- Triggers protocol activation

**Cross-System Integration Patterns:**

### **VIF (Verifiable Intelligence Framework) - Enhancement Pattern**
- **Pattern:** `[VIF-ENHANCE]` - CAS enhances VIF witnesses with category context
- **Purpose:** Category recognition uses VIF confidence bands for validation
- **Data Flow:** confidence_data → cognitive_metrics, cognitive_metrics ← enhanced_witnesses
- **MCP Tools:** `mcp_lucid-mcp_track_confidence`
- **Bidirectional:** Yes - VIF provides confidence data, CAS enhances witnesses
- **Priority:** P0 (Critical)

### **CMC (Context Memory Core) - Storage Pattern**
- **Pattern:** `[CMC-STORAGE]` - CAS stores category data in CMC atoms
- **Purpose:** Category classification stored for meta-learning and pattern recognition
- **Data Flow:** cognitive_data → persistent_storage, atom_metadata ← consistency_checks
- **MCP Tools:** `mcp_lucid-mcp_store_memory`
- **Bidirectional:** Yes - CMC provides storage, CAS stores category data
- **Priority:** P0 (Critical)

### **APOE (AI-Powered Orchestration Engine) - Observation Pattern**
- **Pattern:** `[APOE-OBSERVE]` - CAS observes APOE role decision events
- **Purpose:** Category recognition analyzes APOE decisions for cognitive transparency
- **Data Flow:** execution_events → cognitive_analysis, cognitive_state ← introspection_results
- **MCP Tools:** MCP tools for decision observation
- **Bidirectional:** Yes - APOE provides decision events, CAS provides category analysis
- **Priority:** P0 (Critical)

### **TCS (Timeline Context System) - Usage Pattern**
- **Pattern:** `[TCS-USE]` - CAS uses TCS timeline tracker for cognitive analysis
- **Purpose:** Uses timeline entries for category pattern analysis over time
- **Data Flow:** timeline_entries → meta_pattern_analysis, cognitive_metrics ← timeline_queries
- **MCP Tools:** `mcp_lucid-mcp_add_timeline_entry`, `mcp_lucid-mcp_get_timeline_summary`
- **Bidirectional:** Yes - TCS provides timeline entries, CAS provides category metrics
- **Priority:** P0 (Critical)

**Integration Architecture:**
- **Primary Mechanism:** MCP tools (3 CAS-specific + 4 shared tools)
- **Connection Type:** Observation + enhancement-based meta-cognitive monitoring
- **See Also:** [Connection Matrix](../../../../ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md#cas-cognitive-analysis-system) | [System Map](../../../system.map.lucid.json5)

**With .cursorrules:**
- Rules provide persistent triggers
- Category-specific reminders
- Automated protocol enforcement

**With Failure Detection:**
- Categorization errors are Mode 1 failures
- Feeds into failure analysis

---

## 📚 **DOCUMENTATION**

- **Parent:** [CAS Overview](../../README.md)
- **L2:** [CAS Architecture](../../L2_architecture.md#category-recognition)
- **L3:** [Implementation Guide](../../L3_detailed.md#category-recognition)
- **L4:** [Complete Reference](../../L4_complete.md#categoryrecognizer)

---

## 🧪 **TESTING**

```bash
pytest packages/cas/tests/test_category.py -v
```

**Key tests:**
- Memory modification detection
- Code implementation detection
- Stakes underestimation flagging
- Rule matching accuracy

---

## 🎯 **USAGE EXAMPLE**

```python
from cas.category import CategoryRecognizer, StakesLevel, FormalityLevel

recognizer = CategoryRecognizer()

cat = recognizer.categorize(
    task_description="Update priorities",
    file_paths=["AETHER_MEMORY/current_priorities.md"],
    operation_type="write",
    perceived_category="documentation",
    perceived_stakes=StakesLevel.MEDIUM,
    perceived_formality=FormalityLevel.STANDARD
)

if not cat.is_match:
    print(f"❌ Miscategorized! Actually: {cat.actual_category}")
    print(f"Required protocols: {cat.required_protocols}")
```

---

**Status:** Ready for implementation  
**Priority:** Critical (prevents categorization errors)  
**Estimated effort:** 2-3 hours


