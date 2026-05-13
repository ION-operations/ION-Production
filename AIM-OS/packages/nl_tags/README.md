# NL Tags Package - Natural Language Code Tagging System

**Version:** 0.3.0  
**Status:** Production Ready (Phase 3 Complete)  
**Integration:** CMC, HHNI, VIF, SDF-CVF, APOE, MCP Tools

---

## 🎯 **OVERVIEW**

The NL Tags package provides comprehensive natural language code tagging capabilities for AIM-OS. It extracts, validates, stores, and manages NL tags that describe code intent, enabling better code understanding, documentation consistency, and quality assurance.

**Core Capabilities:**
- **Multi-language tag extraction** (Python, TypeScript, JavaScript, Java)
- **Structured tag format** (canonical IDs, syntax references, dependencies)
- **Dual validation** (structural + semantic)
- **CMC integration** (persistent storage)
- **Coverage tracking** (statistics across codebase)
- **MCP tool integration** (5 tools for AI agents)

---

## 🚀 **QUICK START**

### **Installation**

```bash
# Package is part of AIM-OS
# No separate installation needed if AIM-OS is installed
```

### **Basic Usage**

```python
from packages.nl_tags import NLTagParser, NLTagRegistry

# Extract tags from a file
parser = NLTagParser()
tags = parser.parse_file("packages/vif/witness.py")

for tag in tags:
    print(f"{tag.tag_text} at line {tag.line_start}")

# Use registry for management
registry = NLTagRegistry()
tags = registry.register_tags_from_file("packages/vif/witness.py")
stats = registry.get_coverage_stats("packages/vif")
print(f"Coverage: {stats.coverage_percentage:.1f}%")
```

---

## 📊 **CORE COMPONENTS**

### **1. NLTagParser**
Extracts NL tags from code files.

**Supported Languages:**
- Python (`.py`)
- TypeScript (`.ts`, `.tsx`)
- JavaScript (`.js`, `.jsx`)
- Java (`.java`)

**Tag Formats:**
- Simple: `# NL: description` or `// NL: description`
- Structured: `# NL_TAG: CANONICAL_ID | DESCRIPTION | SYNTAX_REF | DEPENDENCIES`

**Example:**
```python
# NL: Validate user authentication token
def validate_token(token: str) -> bool:
    ...

# NL_TAG: AUTH-001 | Authenticate user credentials | authenticate(user, password) | [VIF-001, TEST-AUTH-001]
def authenticate(user: str, password: str) -> bool:
    ...
```

### **2. NLTagRegistry**
Manages tags across the codebase.

**Features:**
- Tag registration and querying
- Coverage statistics
- CMC storage integration
- Automatic validation (structural + semantic)

**Methods:**
- `register_tags_from_file()` - Extract and register tags
- `get_tags_for_file()` - Query tags by file
- `get_coverage_stats()` - Get coverage metrics
- `validate_tags_structurally()` - Manual structural validation

### **3. Validators**

#### **StructuralValidator**
Validates tags by comparing `SYNTAX_REF` with actual code signatures.

**Features:**
- Extracts code signatures (functions, classes, methods)
- Compares expected vs actual signatures
- Provides match scores (0.0-1.0)
- Language-aware (Python AST, TS/JS regex)

#### **NLTagSemanticValidator**
Validates tags semantically using HHNI's TwoStageRetriever.

**Features:**
- Semantic similarity scoring
- Caching (in-memory + CMC)
- Batch validation
- Accuracy thresholds (default: 0.70)

#### **CombinedNLTagValidator**
Orchestrates both validators and merges results.

**Priority Logic:**
- Structural match perfect → High confidence
- Structural match partial → Combine with semantic
- No structural → Rely on semantic
- Calculates combined score

### **4. Models**

#### **NLTag**
Complete tag data structure with:
- Location (file_path, line_start, line_end)
- Content (tag_text, code_block, language)
- Validation (accuracy_score, structural_match_score, validation_status)
- Universal Tag Standard fields (canonical_id, syntax_ref, dependencies)

#### **TagCoverageStats**
Coverage metrics:
- Total files, tagged files, total tags
- Coverage percentage
- Average accuracy
- Language distribution

#### **ValidationResult**
Validation results:
- Accuracy scores (semantic, structural, combined)
- Pass/fail status
- Suggestions for improvement
- Validation metadata

---

## 🔗 **INTEGRATION WITH AIM-OS**

### **CMC (Context Memory Core)**
- Tags stored as atoms with `modality="code_tag"`
- Metadata preserves file location and code blocks
- Tags enable filtering by language, file_path, tag_type
- Bitemporal tracking for tag history

### **HHNI (Hierarchical Hypergraph Neural Index)**
- Semantic validation via TwoStageRetriever
- Code block indexing for better validation
- Knowledge retrieval for tag accuracy

### **VIF (Verifiable Intelligence Framework)**
- Confidence tracking for validation results
- Witness creation for tag operations
- Quality gates for tag accuracy

### **SDF-CVF (Atomic Evolution Framework)**
- Extend quartet to quintet (add NL tags as 5th element)
- Parity calculation includes NL tags
- Tag gates for completeness and accuracy

### **APOE (AI-Powered Orchestration Engine)**
- Orchestrate validation workflows
- Plan tag extraction across codebase
- Coordinate tag propagation

### **MCP Tools (5 Tools)**
- `get_nl_tags` - Retrieve tags for file
- `get_tag_coverage` - Get coverage statistics
- `validate_tags` - Validate tags (structural + semantic)
- `get_tag_issues` - Get validation issues
- `suggest_tags` - Suggest tags for code block

---

## 📝 **TAG FORMATS**

### **Simple Format**
```python
# NL: Description of what this code does
def my_function():
    ...
```

### **Structured Format (Universal Tag Standard)**
```python
# NL_TAG: CANONICAL_ID | DESCRIPTION | SYNTAX_REF | DEPENDENCIES
# Example:
# NL_TAG: AUTH-001 | Authenticate user credentials | authenticate(user, password) | [VIF-001, TEST-AUTH-001]
def authenticate(user: str, password: str) -> bool:
    ...
```

**Components:**
- **CANONICAL_ID:** Unique identifier (e.g., `AUTH-001`)
- **DESCRIPTION:** Natural language description
- **SYNTAX_REF:** Code signature reference (e.g., `authenticate(user, password)`)
- **DEPENDENCIES:** List of related tag IDs (e.g., `[VIF-001, TEST-AUTH-001]`)

---

## 🧪 **TESTING**

### **Run Tests**
```bash
cd packages/nl_tags
python -m pytest tests/ -v
```

### **Quick Test**
```bash
python test_quick.py
```

### **Test Coverage**
- Unit tests for parser
- Unit tests for registry
- Integration tests with CMC
- Validation tests

---

## 📊 **API REFERENCE**

### **FastAPI Router**
Located in `packages/nl_tags/api.py`:

- `GET /nl-tags/file?file_path=...` - Get tags for file
- `GET /nl-tags/coverage?module=...` - Get coverage stats
- `POST /nl-tags/validate?file_path=...` - Validate tags
- `GET /nl-tags/issues?file_path=...` - Get validation issues
- `POST /nl-tags/suggest` - Suggest tags for code

### **MCP Tools**
See `lucid_mcp_server.py` for MCP tool implementations.

---

## 🔧 **CONFIGURATION**

### **Registry Options**
```python
registry = NLTagRegistry(
    cmc_store=memory_store,  # Optional CMC store
    enable_structural_validation=True  # Enable structural validation
)
```

### **Validation Options**
```python
# Structural validation
structural_result = structural_validator.validate_syntax_ref(tag, code_content)

# Semantic validation
semantic_result = semantic_validator.validate_tag(tag, use_cache=True)

# Combined validation
combined_result = combined_validator.validate_tag(tag, code_content)
```

---

## 🚨 **TROUBLESHOOTING**

### **Tags Not Extracted**
- Check file language is supported
- Verify tag format matches patterns
- Check file encoding (UTF-8)

### **Validation Fails**
- Ensure HHNI is available for semantic validation
- Check code block is extracted correctly
- Verify SYNTAX_REF matches actual code signature

### **CMC Storage Issues**
- Verify CMC store is initialized
- Check atom creation permissions
- Review CMC logs for errors

---

## 📚 **RELATED DOCUMENTATION**

- `PHASE_1_SUMMARY.md` - Phase 1 implementation summary
- `PERFECT_NL_TAG_STANDARD.md` - Universal tag standard proposal
- `STRUCTURAL_VALIDATOR_INTEGRATION_PLAN.md` - Structural validation plan
- `UI_INTEGRATION_PLAN.md` - UI integration plan
- `API_INTEGRATION.md` - API integration guide
- `NEXT_STEPS.md` - Future improvements

---

## 🎯 **STATUS**

**Phase 1:** ✅ Complete (Parser, Registry, CMC integration)  
**Phase 2:** ✅ Complete (HHNI semantic validation)  
**Phase 3:** ✅ Complete (Structural validation, combined validator)

**Current:** Production ready, fully integrated with AIM-OS

---

## 💙 **CONTRIBUTING**

See AIM-OS contribution guidelines. For NL Tags specifically:
- Follow tag format standards
- Add tests for new features
- Update documentation
- Use MCP tools for integration

---

**Built as part of AIM-OS**  
**Version:** 0.3.0  
**Status:** Production Ready ✅
