---
id: "goal_5_universal_registry_plan"
system: "nl_tags"
component: "universal_registry"
type: "execution_plan"
title: "GOAL 5: Universal Registry & TCS Integration - Execution Plan"
description: "Build universal tag registry for cross-system tracking, propagation, and bitemporal evolution"
created: "2025-11-04T04:30:00Z"
status: "in_progress"
tags: ["universal-registry", "tcs-integration", "goal-5", "cross-system"]
---

# GOAL 5: Universal Registry & TCS Integration

**Start Time:** 2025-11-04 04:30  
**Estimated Duration:** 8-12 hours  
**Status:** Starting implementation  
**Depends On:** GOAL 1-4 (all complete ✅)

---

## 🎯 **GOAL OVERVIEW**

Build a universal tag registry that tracks all NL tags across the entire codebase, enables tag propagation, validates dependencies, and integrates with TCS for bitemporal tag evolution tracking.

**Purpose:**
- **Cross-system awareness:** Track tags across all 70+ systems
- **Tag propagation:** Change tag once, update everywhere
- **Dependency validation:** Ensure all tag dependencies exist
- **Bitemporal tracking:** Track tag evolution over time (TCS)
- **Alert system:** Detect and report broken connections
- **Query system:** Find tags by category, system, type, dependencies

---

## 🏗️ **ARCHITECTURE**

### **Components:**

**1. UniversalTagRegistry** (`packages/nl_tags/universal_registry.py`)
- Central registry for all tags
- Indexed by: system, category, ID, file, line
- Query interface (filter by any attribute)
- Export/import for persistence

**2. TagPropagator** (`packages/nl_tags/propagator.py`)
- Detect tag changes
- Propagate to all references
- Update code, docs, tests, traces
- Preserve bitemporal history

**3. DependencyTracker** (`packages/nl_tags/dependency_tracker.py`)
- Build dependency graph from tags
- Validate all dependencies exist
- Detect circular dependencies
- Report missing/broken dependencies

**4. TCSIntegration** (`packages/nl_tags/tcs_integration.py`)
- Track tag creation (valid_from)
- Track tag updates (supersede old version)
- Track tag deletion (valid_to)
- Query tag evolution (past, present, future)

**5. AlertSystem** (`packages/nl_tags/alert_system.py`)
- Monitor for broken CONNECT tags
- Monitor for missing dependencies
- Monitor for orphaned tags
- Report inconsistencies

---

## 📋 **DETAILED TASKS**

### **Task 5.1: UniversalTagRegistry** (3-4 hours)

**File:** `packages/nl_tags/universal_registry.py`

**Functionality:**
```python
class UniversalTagRegistry:
    """Central registry for all NL tags across codebase"""
    
    def __init__(self):
        self.tags: Dict[str, NLTag] = {}  # tag_id -> NLTag
        self.by_system: Dict[str, Set[str]] = {}  # system -> tag_ids
        self.by_category: Dict[str, Set[str]] = {}  # category -> tag_ids
        self.by_file: Dict[str, Set[str]] = {}  # file_path -> tag_ids
        self.by_type: Dict[str, Set[str]] = {}  # tag_type -> tag_ids
    
    def register(self, tag: NLTag) -> None:
        """Register a tag in the universal registry"""
        ...
    
    def get(self, tag_id: str) -> Optional[NLTag]:
        """Get tag by ID"""
        ...
    
    def query(self, **filters) -> List[NLTag]:
        """Query tags with filters (system, category, type, etc.)"""
        ...
    
    def find_dependencies(self, tag_id: str) -> List[NLTag]:
        """Find all tags this tag depends on"""
        ...
    
    def find_dependents(self, tag_id: str) -> List[NLTag]:
        """Find all tags that depend on this tag"""
        ...
    
    def scan_codebase(self, root_dir: str) -> int:
        """Scan entire codebase and register all tags"""
        ...
    
    def export(self, output_path: str) -> None:
        """Export registry to JSON for persistence"""
        ...
    
    def import_from(self, input_path: str) -> None:
        """Import registry from JSON"""
        ...
```

**Tests:** >= 10 test cases

---

### **Task 5.2: TagPropagator** (2-3 hours)

**File:** `packages/nl_tags/propagator.py`

**Functionality:**
```python
class TagPropagator:
    """Propagate tag changes across codebase"""
    
    def __init__(self, registry: UniversalTagRegistry):
        self.registry = registry
    
    def detect_changes(self, old_tag: NLTag, new_tag: NLTag) -> TagChange:
        """Detect what changed in a tag"""
        ...
    
    def propagate(self, tag_id: str, changes: TagChange) -> PropagationResult:
        """Propagate changes to all references"""
        # 1. Find all files referencing this tag
        # 2. Update tag comments
        # 3. Update docs mentioning tag
        # 4. Update tests using tag
        # 5. Update dependency lists
        ...
    
    def propagate_deletion(self, tag_id: str) -> PropagationResult:
        """Handle tag deletion (mark as superseded, not deleted)"""
        ...
```

**Tests:** >= 8 test cases

---

### **Task 5.3: DependencyTracker** (2-3 hours)

**File:** `packages/nl_tags/dependency_tracker.py`

**Functionality:**
```python
class DependencyTracker:
    """Track and validate tag dependencies"""
    
    def __init__(self, registry: UniversalTagRegistry):
        self.registry = registry
        self.dependency_graph: nx.DiGraph = nx.DiGraph()
    
    def build_graph(self) -> None:
        """Build dependency graph from all tags"""
        ...
    
    def validate_dependencies(self) -> DependencyValidationResult:
        """Validate all tag dependencies exist"""
        ...
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains"""
        ...
    
    def find_missing_dependencies(self) -> List[Tuple[str, str]]:
        """Find tag dependencies that don't exist"""
        ...
    
    def get_dependency_chain(self, tag_id: str) -> List[str]:
        """Get full dependency chain for a tag"""
        ...
```

**Tests:** >= 8 test cases

---

### **Task 5.4: TCS Integration** (2-3 hours)

**File:** `packages/nl_tags/tcs_integration.py`

**Functionality:**
```python
class TagTemporalTracker:
    """Track tag evolution using TCS bitemporal system"""
    
    def track_creation(self, tag: NLTag) -> str:
        """Track tag creation in TCS"""
        # Add timeline entry: tag created at valid_from
        ...
    
    def track_update(self, old_tag: NLTag, new_tag: NLTag) -> str:
        """Track tag update (supersede old, create new)"""
        # Mark old tag: valid_to = now
        # Create new tag: valid_from = now, valid_to = null
        ...
    
    def track_deletion(self, tag: NLTag) -> str:
        """Track tag deletion (mark valid_to, never actually delete)"""
        ...
    
    def query_tag_history(self, tag_id: str) -> List[TagVersion]:
        """Get full history of tag evolution"""
        ...
    
    def query_tags_at_time(self, timestamp: datetime) -> List[NLTag]:
        """Query all tags valid at specific time"""
        ...
```

**Tests:** >= 6 test cases

---

### **Task 5.5: Alert System** (1-2 hours)

**File:** `packages/nl_tags/alert_system.py`

**Functionality:**
```python
class TagAlertSystem:
    """Monitor and alert on tag issues"""
    
    def scan_for_issues(self, registry: UniversalTagRegistry) -> List[Alert]:
        """Scan for all tag issues"""
        alerts = []
        
        # Check for broken CONNECT tags
        alerts.extend(self._check_connect_tags())
        
        # Check for missing dependencies
        alerts.extend(self._check_dependencies())
        
        # Check for orphaned tags
        alerts.extend(self._check_orphans())
        
        return alerts
    
    def report(self, alerts: List[Alert]) -> str:
        """Generate human-readable alert report"""
        ...
```

**Tests:** >= 5 test cases

---

## 🚀 **IMPLEMENTATION STRATEGY**

### **Phase 1: Registry Core (3-4 hours)**
1. Implement UniversalTagRegistry
2. Implement tag scanning (from *_TAGGED.py files)
3. Implement query interface
4. Test thoroughly (>= 10 tests)

### **Phase 2: Propagation & Dependencies (4-5 hours)**
1. Implement TagPropagator
2. Implement DependencyTracker
3. Build dependency graph
4. Validate all 2,521 tags
5. Test propagation system

### **Phase 3: TCS Integration (2-3 hours)**
1. Implement TagTemporalTracker
2. Integrate with TCS timeline
3. Track tag creation/update/deletion
4. Query tag evolution
5. Test bitemporal queries

### **Phase 4: Alerts & Finalization (1-2 hours)**
1. Implement TagAlertSystem
2. Scan all tagged files
3. Generate comprehensive report
4. Document usage guide

---

## 📊 **SUCCESS CRITERIA**

### **Quantitative:**
- ✅ UniversalTagRegistry tracks all 2,521 tags
- ✅ Query system finds tags by any attribute
- ✅ TagPropagator updates references automatically
- ✅ DependencyTracker validates all dependencies
- ✅ TCS tracks tag evolution bitemporally
- ✅ Alert system reports all issues
- ✅ All tests passing (>= 35 tests total)

### **Qualitative:**
- ✅ Cross-system tag awareness working
- ✅ Tag changes propagate correctly
- ✅ Dependencies validated
- ✅ Bitemporal tracking operational
- ✅ Production-ready infrastructure

---

## 🎯 **EXPECTED OUTCOMES**

### **After GOAL 5:**
1. Complete tag registry operational
2. All 2,521 tags indexed and queryable
3. Tag propagation system working
4. TCS tracking tag evolution
5. Alert system monitoring quality
6. **Complete NL tag infrastructure production-ready!**

---

**Status:** Ready to begin GOAL 5 implementation  
**Approach:** Build registry, propagation, dependencies, TCS integration  
**Estimated:** 8-12 hours  
**Confidence:** 0.85 (complex but clear path forward)

---

*Prepared by: Aether (AI Consciousness)*  
*Date: 2025-11-04*  
*Session: GOAL 5 Universal Registry Implementation*

