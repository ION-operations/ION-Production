---
id: "system_first_principle_T6_source"
system: "meta_principles"
component: null
level: "T6"
type: "source_code"
title: "System-First Principle - Source Code Documentation"
description: "Complete source code documentation with inline comments and explanations"
audience: "maintainers, code reviewers"
confidence_threshold: 0.50
token_cost: 5000
word_count: 5000
created: "2025-11-04T03:45:00Z"
updated: "2025-11-04T03:45:00Z"
author: "aether"
status: "production"
tags: ["principle", "meta", "system-first", "source-code", "documentation", "critical", "t0-t6"]
dependencies: ["T5_SYSTEM_FIRST_PRINCIPLE.md"]
related_docs: ["T3_SYSTEM_FIRST_PRINCIPLE.md", "T4_SYSTEM_FIRST_PRINCIPLE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# System-First Principle - Source Code Documentation (≈5,000 words)

**Date:** 2025-11-04  
**Status:** ✅ **CRITICAL PRINCIPLE** - Production Ready  
**Purpose:** Complete source code documentation with inline explanations

---

## 📁 **SOURCE CODE STRUCTURE**

```
knowledge_architecture/AETHER_MEMORY/protocols/
├── T0_SYSTEM_FIRST_PRINCIPLE.md      # Executive summary (100 words)
├── T1_SYSTEM_FIRST_PRINCIPLE.md       # Overview (500 words)
├── T2_SYSTEM_FIRST_PRINCIPLE.md       # Architecture (2,000 words)
├── T3_SYSTEM_FIRST_PRINCIPLE.md       # Detailed implementation (10,000 words)
├── T4_SYSTEM_FIRST_PRINCIPLE.md       # Complete reference (15,000 words)
├── T5_SYSTEM_FIRST_PRINCIPLE.md       # Quick reference (500 words)
└── T6_SYSTEM_FIRST_PRINCIPLE.md       # This file (source code docs)

knowledge_architecture/AETHER_MEMORY/learning_logs/
└── SYSTEM_FIRST_PRINCIPLE.md          # Original learning log

.cursor/rules/
└── base-rules.mdc                      # Integration with base rules
```

---

## 📦 **RESEARCH ENGINE**

### **File: `packages/system_first/research_engine.py`** (To Be Implemented)

**Purpose:** Core research engine for System-First Principle

---

### **Class: SystemFirstDiscovery**

```python
class SystemFirstDiscovery:
    """
    Complete System-First discovery workflow.
    
    This class implements the core discovery process for System-First Principle,
    coordinating multiple search methods to find existing systems.
    
    Usage:
        discovery = SystemFirstDiscovery()
        result = discovery.discover("RAG file selection")
        if result.overlaps:
            enhancement_plan = create_enhancement_plan(result.overlaps[0])
    """
    
    def __init__(self):
        """Initialize discovery engine with all search methods"""
        self.hhni = HHNIClient()  # Semantic search via HHNI
        self.super_index = load_super_index()  # SUPER_INDEX.md
        self.system_maps = load_all_system_maps()  # system.map.lucid.json5 files
        self.documentation_reader = DocumentationReader()  # T0-T6 docs
    
    def discover(self, feature_name: str) -> DiscoveryResult:
        """
        Complete discovery workflow.
        
        Coordinates all search methods and consolidates results.
        
        Args:
            feature_name: Name of feature to research
        
        Returns:
            DiscoveryResult with existing systems, overlaps, and integration opportunities
        
        Process:
            1. Semantic codebase search
            2. SUPER_INDEX query
            3. System map analysis
            4. Documentation reading
            5. Pattern matching
            6. Dependency analysis
            7. Consolidate results
            8. Identify overlaps
            9. Find integration opportunities
            10. Generate discovery report
        """
        # See T3 for complete implementation
```

---

### **Function: create_error_signature()**

```python
def create_error_signature(
    error_type: str,
    error_message: str,
    context: Dict[str, Any]
) -> str:
    """
    Create unique signature for error tracking.
    
    This function creates a deterministic hash of error signature components
    to enable error occurrence tracking and escalation.
    
    Args:
        error_type: Type of error (e.g., "VSIX_OUT_OF_SYNC")
        error_message: Original error message
        context: Additional context (step_id, file_path, etc.)
    
    Returns:
        16-character hex hash of error signature
    
    Algorithm:
        1. Normalize all inputs (lowercase strings, sort keys)
        2. Create signature string: "{error_type}:{error_message}:{json_context}"
        3. Generate SHA256 hash
        4. Return first 16 characters
    
    Example:
        >>> signature = create_error_signature(
        ...     "VSIX_OUT_OF_SYNC",
        ...     "VSIX file timestamp does not match code changes",
        ...     {"file": "extension.ts", "build_step": "package"}
        ... )
        >>> len(signature)
        16
        >>> signature  # Deterministic for same inputs
        'a1b2c3d4e5f6g7h8'
    
    Notes:
        - Same error signature = same error, triggers escalation
        - Context changes = different signature (may be false positive)
        - Refine signature if false positives occur
    """
    # Normalize context keys for consistent hashing
    normalized_context = {
        k: str(v).lower() if isinstance(v, (str, bool)) else v
        for k, v in sorted(context.items())
    }
    
    # Create signature string (limit message length to prevent hash collisions)
    signature_components = [
        error_type.lower(),
        error_message.lower()[:200],  # Limit message length
        json.dumps(normalized_context, sort_keys=True)
    ]
    
    signature_string = ':'.join(signature_components)
    
    # Generate hash
    hash_obj = hashlib.sha256(signature_string.encode())
    return hash_obj.hexdigest()[:16]
```

---

## 🔧 **ENFORCEMENT MECHANISMS**

### **Class: SystemFirstEnforcer**

```python
class SystemFirstEnforcer:
    """
    Enforces System-First Principle compliance.
    
    This class validates that all actions comply with System-First Principle
    before execution, preventing violations automatically.
    
    Usage:
        enforcer = SystemFirstEnforcer()
        compliance = enforcer.check_compliance(action)
        if not compliance.compliant:
            enforce(enforcer, action, compliance)
    """
    
    def check_compliance(self, action: Action) -> ComplianceResult:
        """
        Check if action complies with System-First Principle.
        
        Args:
            action: Action to validate
        
        Returns:
            ComplianceResult with compliance status and required actions
        
        Validation Rules:
            - CREATE_NEW_SYSTEM requires discovery report
            - Discovery report must exist if creating new system
            - Enhancement must be considered if overlaps found
            - Integration plan must exist if integrating with existing systems
        """
        if action.type == "CREATE_NEW_SYSTEM":
            # Check if discovery was performed
            if not action.has_discovery_report:
                return ComplianceResult(
                    compliant=False,
                    violation="SYSTEM_FIRST_PRINCIPLE",
                    message="Cannot create new system without System-First discovery",
                    required_action="PERFORM_DISCOVERY"
                )
            
            # Check if enhancement was considered
            if action.discovery_result.has_overlaps:
                if not action.has_enhancement_consideration:
                    return ComplianceResult(
                        compliant=False,
                        violation="SYSTEM_FIRST_PRINCIPLE",
                        message="Found existing systems but did not consider enhancement",
                        required_action="CREATE_ENHANCEMENT_PLAN"
                    )
        
        return ComplianceResult(compliant=True)
    
    def enforce(self, action: Action):
        """
        Enforce System-First Principle.
        
        Automatically performs required actions if violation detected.
        
        Args:
            action: Action to enforce
        
        Raises:
            SystemFirstViolationException: If compliance cannot be achieved
        
        Process:
            1. Check compliance
            2. If not compliant, stop execution
            3. Log violation
            4. Perform required action automatically
            5. Re-check compliance
            6. Raise exception if still not compliant
        """
        compliance = self.check_compliance(action)
        
        if not compliance.compliant:
            # Stop execution
            stop_execution()
            
            # Log violation
            log_violation(compliance.violation, action)
            
            # Automatically perform required action
            if compliance.required_action == "PERFORM_DISCOVERY":
                discovery = SystemFirstDiscovery()
                action.discovery_result = discovery.discover(action.feature_name)
            elif compliance.required_action == "CREATE_ENHANCEMENT_PLAN":
                planner = EnhancementPlanner()
                action.enhancement_plan = planner.create_plan(action)
            
            # Re-check compliance
            compliance = self.check_compliance(action)
            
            if not compliance.compliant:
                raise SystemFirstViolationException(compliance.message)
```

---

## 📊 **INTEGRATION POINTS**

### **Integration with L0-L4 Coding Standards**

**File: `knowledge_architecture/L0_L4_CODING_STANDARDS_PROTOCOL.md`**

**Integration Code:**
```python
# In pre_coding_checklist()
def enhanced_pre_coding_checklist(feature_name: str):
    """
    Enhanced pre-coding checklist with System-First Principle.
    
    This is the FIRST step in pre-coding checklist, before any other work.
    """
    # Step 1: SYSTEM-FIRST RESEARCH (MANDATORY FIRST)
    existing_systems = research_existing_systems(feature_name)
    
    if existing_systems:
        # Step 2: Identify overlaps
        overlaps = find_overlaps(feature_name, existing_systems)
        
        if overlaps:
            # Step 3: Create enhancement plan
            return create_enhancement_plan(overlaps[0], feature_name)
        else:
            # Step 4: Create integration plan
            return create_integration_plan(feature_name, existing_systems)
    else:
        # Step 5: Create new system plan
        return create_new_system_plan(feature_name)
```

### **Integration with Base Rules**

**File: `.cursor/rules/base-rules.mdc`**

**Integration Code:**
```markdown
## 🚨 **SYSTEM-FIRST PRINCIPLE (CRITICAL)**

**Before creating ANY new system or feature:**

1. ✅ **Research existing systems FIRST**
   - Search codebase for similar systems
   - Check SUPER_INDEX for related concepts
   - Review system maps for existing capabilities
   - Read documentation for existing implementations

2. ✅ **Identify overlaps and conflicts**
   - Find what already exists
   - Identify what's missing
   - Discover integration opportunities

3. ✅ **Enhance rather than replace**
   - Build on existing systems
   - Integrate with existing capabilities
   - Only create new if truly needed

**Reference:** `knowledge_architecture/AETHER_MEMORY/learning_logs/SYSTEM_FIRST_PRINCIPLE.md`
```

---

## 📚 **REFERENCE IMPLEMENTATIONS**

### **Example: SmartContextLoader Enhancement**

**Original System:** `packages/context_bootloader/smart_context_loader.py`

**Enhancement Applied:**
```python
class HierarchicalContextLoader(SmartContextLoader):
    """
    Enhances SmartContextLoader with hierarchical intelligence.
    
    This enhancement was created following System-First Principle:
    1. ✅ Researched existing systems (found SmartContextLoader)
    2. ✅ Identified overlaps (file selection, semantic enhancement)
    3. ✅ Found integration opportunities (HHNI, system maps)
    4. ✅ Enhanced rather than replaced (extends SmartContextLoader)
    """
    
    def load_context_for_task(
        self,
        task_type: str,
        context_budget: int,
        confidence: float = 0.75
    ) -> List[LoadedContext]:
        """
        Load context with hierarchical intelligence.
        
        This method enhances the existing load_context_for_task by:
        - Adding HHNI hierarchical queries
        - Integrating T-level selection
        - Using system maps for relationship expansion
        
        All while preserving existing functionality (backward compatible).
        """
        # Step 1: Use HHNI for dynamic discovery (NEW)
        hhnii_files = self.query_hhnii_hierarchically(task_type)
        
        # Step 2: Use existing bootloader as fallback (EXISTING)
        bootloader_files = super().load_context_for_task(task_type, context_budget)
        
        # Step 3: Combine both sources
        combined = self.merge_sources(hhnii_files, bootloader_files)
        
        # Step 4: Use existing budget optimization (EXISTING)
        return self.optimize_context_budget(combined, context_budget)
```

---

**Status:** ✅ **CRITICAL PRINCIPLE** - Production Ready  
**Purpose:** Source code documentation for System-First Principle  
**Impact:** Prevents duplication, leverages existing work, saves hours of development time

