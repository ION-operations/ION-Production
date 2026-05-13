# Nova - NL Tag Implementation Plan for SDF-CVF

**Purpose:** Plan for adding NL tags to all public functions in `packages/sdfcvf/`  
**Created:** 2025-01-27  
**Status:** Planning Complete, Implementation In Progress  
**Agent:** Nova (SDF-CVF System Specialist)  
**Priority:** P0 (CRITICAL) - SDF-CVF violates its own quintet parity principles

---

## 📋 **EXECUTIVE SUMMARY**

**Current Status:** 0 NL tags found in `packages/sdfcvf/`  
**Target:** 95%+ public functions, 75%+ internal functions  
**Estimated Tags Needed:** 40-60 tags  
**Estimated Effort:** 2-3 days  
**Criticality:** CRITICAL - SDF-CVF cannot validate its own code quality using its own principles

---

## 🎯 **OBJECTIVES**

1. Add NL tags to all public API functions (exported in `__init__.py`)
2. Add NL tags to all public classes and their methods
3. Add NL tags to key internal functions (target 75%+ coverage)
4. Ensure quintet parity P ≥ 0.90 for SDF-CVF code itself
5. Validate tags with callgraph (CONNECT tag validation)

---

## 📚 **NL TAG FORMAT**

### **Primary Tag (NL_TAG) - REQUIRED**
```
# NL_TAG: SDFCVF-{CATEGORY}-{NNN} | {description} | {signature} | [{dependencies}]
```

### **Tag Categories for SDF-CVF:**
- **QUARTET** - Quartet detection and classification
- **PARITY** - Parity calculation
- **GATE** - Quality gate enforcement
- **BLAST** - Blast radius calculation
- **DORA** - DORA metrics tracking
- **QUINTET** - Quintet parity extension
- **CALLGRAPH** - Callgraph building and validation
- **CONFIG** - Configuration management
- **MODEL** - Data models, enums, dataclasses
- **UTIL** - Utility functions
- **CONNECT** - Cross-system integration tags
- **DESIGN** - Design intent tags
- **SPEC** - Specification/validation tags

---

## 📊 **FUNCTIONS TO TAG**

### **Core Public API (High Priority):**

#### **1. quartet.py:**
- [ ] `class Quartet` - Data model (MODEL)
- [ ] `class QuartetDetector` - Quartet detection (QUARTET)
- [ ] `class FileClassification` - Enum (MODEL)
- [ ] `def extract_module_name()` - Utility (UTIL)

**Public Methods:**
- [ ] `QuartetDetector.classify_file()` - File classification (QUARTET)
- [ ] `QuartetDetector.detect_from_changes()` - Detect quartet from file changes (QUARTET)
- [ ] `QuartetDetector.detect_from_git_diff()` - Detect from Git diff (QUARTET)
- [ ] `Quartet.is_complete()` - Completeness check (QUARTET)

#### **2. parity.py:**
- [ ] `class ParityResult` - Result data model (MODEL)
- [ ] `class ParityCalculator` - Parity calculation (PARITY)
- [ ] `def calculate_parity()` - Standalone parity calculation (PARITY)
- [ ] `def weighted_parity()` - Weighted parity calculation (PARITY)

**Public Methods:**
- [ ] `ParityCalculator.calculate()` - Calculate parity for quartet (PARITY)

#### **3. gates.py:**
- [ ] `class ParityGate` - Gate enforcement (GATE)
- [ ] `class GateConfig` - Gate configuration (MODEL)
- [ ] `class GateResult` - Gate result (MODEL)
- [ ] `class GateType` - Enum (MODEL)
- [ ] `def create_pre_commit_gate()` - Factory function (GATE)
- [ ] `def create_deployment_gate()` - Factory function (GATE)
- [ ] `def create_pr_gate()` - Factory function (GATE)

**Public Methods:**
- [ ] `ParityGate.check()` - Check gate (GATE)

#### **4. blast_radius.py:**
- [ ] `class DependencyAnalyzer` - Dependency analysis (BLAST)
- [ ] `class BlastRadiusResult` - Result model (MODEL)
- [ ] `def analyze_blast_radius()` - Standalone analysis (BLAST)

**Public Methods:**
- [ ] `DependencyAnalyzer.analyze()` - Analyze dependencies (BLAST)

#### **5. dora.py:**
- [ ] `class DORAMetricsCollector` - Metrics collection (DORA)
- [ ] `class DORAMetrics` - Metrics model (MODEL)
- [ ] `class ParityDORACorrelator` - Correlation analysis (DORA)
- [ ] `class CorrelationAnalysis` - Analysis result (MODEL)
- [ ] `def initialize_dora_db()` - Database initialization (DORA)
- [ ] `def report_dora_metrics()` - Metrics reporting (DORA)

**Public Methods:**
- [ ] `DORAMetricsCollector.record_deployment()` - Record deployment (DORA)
- [ ] `DORAMetricsCollector.record_incident()` - Record incident (DORA)
- [ ] `DORAMetricsCollector.get_metrics()` - Get metrics (DORA)
- [ ] `ParityDORACorrelator.correlate()` - Correlate parity with DORA (DORA)

#### **6. quintet.py:**
- [ ] `class Quintet` - Quintet data model (MODEL)
- [ ] `class QuintetDetector` - Quintet detection (QUINTET)
- [ ] `class QuintetParityCalculator` - Quintet parity calculation (QUINTET)
- [ ] `class ASTSymbolExtractor` - Symbol extraction (QUINTET)
- [ ] `class NLTagGate` - NL tag gate (GATE)

#### **7. callgraph.py:**
- [ ] `class Callgraph` - Callgraph model (MODEL)
- [ ] `class CallEdge` - Edge model (MODEL)
- [ ] `class CallgraphBuilder` - Builder (CALLGRAPH)
- [ ] `class CONNECTTagValidator` - CONNECT validation (CALLGRAPH)
- [ ] `class CONNECTValidationResult` - Validation result (MODEL)

#### **8. config.py:**
- [ ] `class SDFCVFConfig` - Main config model (MODEL)
- [ ] `class CoverageConfig` - Coverage config (MODEL)
- [ ] `class ConfigLoader` - Config loader (CONFIG)
- [ ] `def get_config()` - Get config singleton (CONFIG)
- [ ] `def reload_config()` - Reload config (CONFIG)

---

## 🔄 **IMPLEMENTATION STRATEGY**

### **Phase 1: Core Public API (Priority 1)**
**Target:** All functions exported in `__init__.py`
- Tag all 32 exported symbols
- Focus on public-facing API
- Ensure CONNECT tags for integrations

**Estimated:** 32 tags, 1 day

### **Phase 2: Key Internal Functions (Priority 2)**
**Target:** 75%+ of internal functions
- Tag helper methods and utilities
- Tag important internal logic
- Focus on functions that enable quintet parity

**Estimated:** 15-20 tags, 0.5 days

### **Phase 3: Integration Tags (Priority 3)**
**Target:** All cross-system integrations
- Add NL_TAG_CONNECT for CMC, VIF, SEG, APOE, HHNI integrations
- Validate with callgraph builder
- Document integration patterns

**Estimated:** 10-15 CONNECT tags, 0.5 days

### **Phase 4: Design Intent Tags (Priority 4)**
**Target:** Architectural decisions
- Add NL_TAG_INTENT for key design decisions
- Link to ADRs and design docs
- Document rationale

**Estimated:** 5-10 INTENT tags, 0.5 days

### **Phase 5: Validation Tags (Priority 5)**
**Target:** All validations
- Add NL_TAG_SPEC for schema validations
- Add NL_TAG_SPEC for contract enforcement
- Link to schema files

**Estimated:** 5-10 SPEC tags, 0.5 days

---

## 📝 **TAG TEMPLATES**

### **Quartet Detection Tags:**
```python
# NL_TAG: SDFCVF-QUARTET-001 | Classify file into quartet category | classify_file(filepath: str) -> FileClassification | []
# NL_TAG: SDFCVF-QUARTET-002 | Detect quartet from file changes | detect_from_changes(files: List[str]) -> Quartet | []
```

### **Parity Calculation Tags:**
```python
# NL_TAG: SDFCVF-PARITY-001 | Calculate quartet parity score | calculate(quartet: Quartet) -> ParityResult | [SDFCVF-QUARTET-001]
```

### **Gate Enforcement Tags:**
```python
# NL_TAG: SDFCVF-GATE-001 | Check parity gate | check(quartet: Quartet, result: ParityResult) -> GateResult | [SDFCVF-PARITY-001]
```

### **Integration Tags:**
```python
# NL_TAG_CONNECT: SDFCVF-CMC-001 | Store quartet parity results in CMC | calculate → store_atom | [SDFCVF-PARITY-001, CMC-STORE-001]
```

### **Design Intent Tags:**
```python
# NL_TAG_INTENT: SDFCVF-DESIGN-001 | Quartet parity prevents drift | Enforce atomic evolution | [ADR-QUARTET-PARITY]
```

---

## ✅ **VALIDATION CRITERIA**

1. **Coverage:** 95%+ public functions tagged
2. **Coverage:** 75%+ internal functions tagged
3. **Quality:** Quintet parity P ≥ 0.90 for SDF-CVF code
4. **Validation:** All CONNECT tags validated with callgraph
5. **Documentation:** Tag catalog updated with all tags
6. **Testing:** Tags validated with quintet parity calculator

---

## 🚀 **NEXT STEPS**

1. ✅ Create implementation plan (this document)
2. ⏳ Start Phase 1: Tag core public API functions
3. ⏳ Begin with `quartet.py` (establish pattern)
4. ⏳ Continue with `parity.py`, `gates.py`, etc.
5. ⏳ Validate tags with quintet parity calculator
6. ⏳ Update NL_TAG_CATALOG.md
7. ⏳ Run quintet parity on SDF-CVF code itself
8. ⏳ Ensure P ≥ 0.90

---

**Status:** Planning Complete, Ready to Begin Implementation  
**Confidence:** High (0.90) - Clear plan, well-defined format, examples available  
**Next:** Begin tagging `quartet.py` core functions

