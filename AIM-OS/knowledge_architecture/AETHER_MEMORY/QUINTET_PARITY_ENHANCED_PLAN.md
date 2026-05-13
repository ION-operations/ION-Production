---
id: "quintet_parity_enhanced_plan"
system: "sdfcvf"
component: "quintet_parity"
level: "T2"
type: "enhanced_plan"
title: "SDF-CVF Quintet Parity - Enhanced Plan with Surgical Improvements"
description: "2,000-word enhanced implementation plan incorporating AST-based coverage, composite metrics, callgraph verification, JSON-LD records, and anti-gaming checks"
audience: "developers, implementers"
confidence_threshold: 0.90
token_cost: 2000
word_count: 2000
created: "2025-11-03T23:55:00Z"
updated: "2025-11-03T23:55:00Z"
author: "aether"
status: "enhanced_plan"
tags: ["sdfcvf", "quintet-parity", "nl-tags", "enhanced", "surgical-improvements"]
dependencies: ["QUINTET_PARITY_IMPLEMENTATION_PLAN.md"]
related_docs: ["NL_TAGS_ALL_IDEAS_CONSOLIDATED.md"]
version: "v2.0.0"
---

# SDF-CVF Quintet Parity - Enhanced Plan

**Date:** 2025-11-03  
**Purpose:** Enhanced implementation plan with surgical improvements from external review  
**Status:** ✅ **ENHANCED PLAN READY** - Airtight, fast, unfakeable

---

## 🎯 **SURGICAL ENHANCEMENTS (15 Improvements)**

### **Enhancement 1: AST-Based Coverage** (Precise, Not Heuristic)

**Replace:** `content.count('def ')` heuristic

**With:** Multi-language AST symbol extraction

**Python Implementation:**
```python
import ast
from pathlib import Path
from typing import List, Tuple

def extract_python_symbols(file_path: str) -> List[Tuple[str, str, int]]:
    """Extract all function/class symbols from Python file"""
    src = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    symbols = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            
            # Build signature
            if hasattr(node, "args"):
                args = ",".join([arg.arg for arg in node.args.args])
                sig = f"{name}({args})"
            else:
                sig = name
            
            lineno = getattr(node, "lineno", 0)
            symbols.append(("py", sig, lineno))
    
    return symbols
```

**TypeScript/JavaScript:**
```python
# Use TypeScript compiler API via subprocess
import subprocess
import json

def extract_ts_symbols(file_path: str) -> List[Tuple[str, str, int]]:
    """Extract symbols from TS/JS file"""
    # Use tsc --listFiles or ts-node with compiler API
    result = subprocess.run(
        ["node", "scripts/extract_ts_symbols.js", file_path],
        capture_output=True,
        text=True
    )
    symbols_json = json.loads(result.stdout)
    return [(s["lang"], s["sig"], s["line"]) for s in symbols_json]
```

**Benefit:** Exact coverage calculation, maps tags to concrete symbols

---

### **Enhancement 2: Composite code↔tags Metric** (Explainable)

**Current:** Single cosine similarity

**Enhanced:** Weighted decomposition with sub-scores

**Formula:**
```
sim(code,tags) = 0.4·sim_sig + 0.3·sim_name + 0.2·sim_doc + 0.1·spec_ok

Where:
  sim_sig:  Jaccard(AST_signature, tag.syntax_ref) or 1.0 if exact match
  sim_name: cosine(symbol_name_embedding, tag.canonical_id_tokens)
  sim_doc:  cosine(docstring_embedding, tag.description_embedding)
  spec_ok:  1.0 if SPEC validator executed successfully, else 0.0
```

**Implementation:**
```python
def calculate_code_tags_similarity(code_symbol, nl_tag) -> Dict[str, float]:
    """Calculate composite code↔tags similarity"""
    # 1. Signature similarity (structural)
    sim_sig = jaccard_similarity(
        normalize_signature(code_symbol.sig),
        normalize_signature(nl_tag.syntax_ref)
    )
    
    # 2. Name similarity (semantic)
    sim_name = cosine_similarity(
        embed(code_symbol.name),
        embed(nl_tag.canonical_id)
    )
    
    # 3. Documentation similarity (semantic)
    sim_doc = cosine_similarity(
        embed(code_symbol.docstring or ""),
        embed(nl_tag.description)
    )
    
    # 4. Spec compliance (validation)
    spec_ok = 1.0 if validate_spec(nl_tag) else 0.0
    
    # Composite score
    composite = 0.4 * sim_sig + 0.3 * sim_name + 0.2 * sim_doc + 0.1 * spec_ok
    
    return {
        "composite": composite,
        "sim_sig": sim_sig,
        "sim_name": sim_name,
        "sim_doc": sim_doc,
        "spec_ok": spec_ok
    }
```

**Benefit:** Diagnostic - shows WHAT to fix (signature? docs? spec?)

---

### **Enhancement 3: Callgraph Verification for CONNECT Tags**

**Current:** Text-based connection validation

**Enhanced:** Actual callgraph + contract graph verification

**Implementation:**
```python
class CallgraphValidator:
    """Validate CONNECT tags against actual callgraph"""
    
    def build_callgraph(self, code_files: List[str]) -> nx.DiGraph:
        """Build callgraph from code files"""
        graph = nx.DiGraph()
        
        for file in code_files:
            # Parse AST
            tree = ast.parse(Path(file).read_text())
            
            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = f"{Path(file).stem}.{node.name}"
                    graph.add_node(func_name)
                    
                    # Extract calls
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                target = child.func.id
                                graph.add_edge(func_name, target)
        
        return graph
    
    def validate_connect_tag(self, tag: NLTag, callgraph: nx.DiGraph) -> bool:
        """Validate CONNECT tag against callgraph"""
        # Extract SOURCE → TARGET from tag
        if "→" in tag.description:
            source, target = tag.description.split("→")
            source = source.strip()
            target = target.strip()
            
            # Check if edge exists in callgraph OR contract graph
            if callgraph.has_edge(source, target):
                return True
            
            # Check contract graph (OpenAPI, gRPC, etc.)
            if self.contract_graph.has_edge(source, target):
                return True
            
            return False
        
        return True  # Not a CONNECT tag or no edge specified
```

**Benefit:** CONNECT tags verified against actual code structure

---

### **Enhancement 4: JSON-LD Tag Records with Hashes**

**Current:** Tags as simple data structures

**Enhanced:** First-class JSON-LD records with bitemporal tracking

**Schema:**
```json
{
  "@context": "https://aim.os/schema/nl-tag.json",
  "id": "tag:VIF-WITNESS-001",
  "type": "NLTag",
  "canon": "VIF-WITNESS-001",
  "kind": "NL_TAG",
  "desc": "Create VIF witness envelope with provenance",
  "sig": "create_witness(...) -> VIFWitness",
  "artifact": "packages/vif/witness.py#L45-L78",
  "contentHash": "blake3:a1b2c3d...",
  "fileHash": "blake3:e4f5g6h...",
  "dependsOn": ["VIF-PROVENANCE-001", "CMC-STORE-001"],
  "connects": [{"src": "create_witness", "tgt": "cmc.store_atom"}],
  "validTime": {"from": "2025-11-03T23:52:00Z"},
  "systemTime": {"recorded": "2025-11-03T23:53:11Z"},
  "provenance": {
    "commit": "a1b2c3d",
    "author": "aether",
    "tool": "nl-tags@0.3.0"
  }
}
```

**Drift Detection:**
```python
if tag.contentHash != current_content_hash and tag.text_unchanged:
    # Content changed but tag didn't update
    fail("Silent drift detected - tag out of sync with code")
```

**Benefit:** Bitemporal tracking prevents drift, content hashes ensure integrity

---

### **Enhancement 5: Cached & Incremental Embeddings**

**Current:** Recompute all embeddings every time

**Enhanced:** Cache + incremental computation

**Implementation:**
```python
class EmbeddingCache:
    """Cache embeddings by content hash"""
    
    def __init__(self, cmc_store):
        self.cache = {}  # In-memory
        self.cmc = cmc_store  # Persistent in CMC
        self.model_version = "text-embedding-3-large@20251103"
    
    def get_or_compute(self, content: str) -> np.ndarray:
        """Get cached embedding or compute and cache"""
        # Hash content
        content_hash = hashlib.blake3(content.encode()).hexdigest()
        cache_key = f"{self.model_version}:{content_hash}"
        
        # Check memory cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Check CMC
        cached_embedding = self.cmc.get_embedding(cache_key)
        if cached_embedding:
            self.cache[cache_key] = cached_embedding
            return cached_embedding
        
        # Compute
        embedding = self.embedding_service.embed(content)
        
        # Cache in memory and CMC
        self.cache[cache_key] = embedding
        self.cmc.store_embedding(cache_key, embedding)
        
        return embedding
```

**Incremental Parity:**
```python
def calculate_parity_incremental(self, diff: GitDiff, prev_result: QuintetParityResult) -> QuintetParityResult:
    """Calculate parity only for changed elements"""
    # Identify what changed
    changed_code = diff.modified_files
    changed_docs = diff.modified_docs
    # etc.
    
    # Reuse cached similarities for unchanged pairs
    similarities = prev_result.similarities.copy()
    
    # Recompute only affected pairs
    if changed_code or changed_tags:
        similarities["code_tags"] = self._compute_similarity(code, tags)
    
    if changed_docs or changed_tags:
        similarities["docs_tags"] = self._compute_similarity(docs, tags)
    
    # etc.
    
    return QuintetParityResult(similarities=similarities)
```

**Benefit:** <300ms pre-commit performance

---

### **Enhancement 6: Anti-Gaming Checks**

**Boilerplate Detection:**
```python
def detect_boilerplate(tags: List[NLTag]) -> List[str]:
    """Detect boilerplate tag descriptions"""
    desc_counts = {}
    for tag in tags:
        desc_counts[tag.description] = desc_counts.get(tag.description, 0) + 1
    
    # Find descriptions repeated > K times
    boilerplate = [desc for desc, count in desc_counts.items() if count > 5]
    
    return boilerplate
```

**SPEC Execution Proof:**
```python
def validate_spec_with_proof(tag: NLTag) -> Tuple[bool, Dict]:
    """Validate SPEC tag with execution proof"""
    if not tag.kind == "NL_TAG_SPEC":
        return True, {}
    
    # Execute validator
    result = execute_validator(tag.validation_method, tag.spec_file)
    
    # Require proof
    if not result.get("ok"):
        return False, {"error": "Validator failed"}
    
    if not result.get("input_hash") or not result.get("schema_hash"):
        return False, {"error": "Missing proof hashes"}
    
    return True, result
```

**Duplicate ID Check:**
```python
def validate_unique_canonical_ids(tags: List[NLTag]) -> List[str]:
    """Ensure canonical IDs are globally unique"""
    seen_ids = {}
    duplicates = []
    
    for tag in tags:
        if tag.canonical_id in seen_ids:
            duplicates.append(f"Duplicate ID {tag.canonical_id} in {tag.file_path} and {seen_ids[tag.canonical_id]}")
        else:
            seen_ids[tag.canonical_id] = tag.file_path
    
    return duplicates
```

**Benefit:** Prevents gaming, ensures integrity

---

### **Enhancement 7: Diagnostic Parity Report**

**Enhanced Output:**
```
================================================================================
Quintet Parity Analysis Report
================================================================================

Pair          Score   Status  Notes
code↔docs     0.93    ✅      Well aligned
code↔tests    0.88    ⚠️      Missing test names for 2 symbols
code↔traces   0.90    ✅      Complete traceability
code↔tags     0.81    ❌      Low - See breakdown below
docs↔tests    0.86    ✅      Good alignment
docs↔traces   0.89    ✅      Complete
tests↔traces  0.84    ✅      Adequate
docs↔tags     0.78    ⚠️      Stale section headers in docs
tests↔tags    0.80    ⚠️      Boilerplate tag descriptions detected
traces↔tags   0.83    ✅      Adequate

Overall: P_quintet = 0.872  ❌ BELOW 0.90

code↔tags Breakdown:
  sim_sig:  0.75  ❌  Mismatched signatures in 3 functions:
    - VIF-WITNESS-001: Expected 'create_witness(...)' found 'create_witness_envelope(...)'
    - CMC-STORE-001: Expected 'store_atom(atom)' found 'store_atom(atom: Atom) -> str'
  sim_name: 0.89  ✅  Good name alignment
  sim_doc:  0.82  ✅  Adequate documentation alignment
  spec_ok:  0.80  ⚠️  2 SPEC tags missing execution proof

Issues:
  1. Fix signature mismatches (3 tags)
  2. Update stale doc headers (2 sections)
  3. Replace boilerplate descriptions (4 tags)
  4. Add SPEC execution proofs (2 validators)

================================================================================
```

**Benefit:** Self-evident failures, fast to fix

---

### **Enhancement 8: Per-Directory Policy Profiles**

**Configuration:** `nl_tags.yml` in each directory

```yaml
# packages/vif/nl_tags.yml
policy:
  public_required: [NL_TAG, NL_TAG_SPEC]  # Public API needs specs
  cross_system_required: [NL_TAG_CONNECT]  # Integrations need connections
  
thresholds:
  public_coverage: 0.95   # 95% of public functions
  internal_coverage: 0.75  # 75% of internal functions
  code_tags_min: 0.85     # Code-tags alignment
  
weights:
  code_tags:
    sig: 0.4   # Signature match most important
    name: 0.3  # Name alignment
    doc: 0.2   # Documentation alignment
    spec: 0.1  # Spec compliance
```

**Policy Resolution:** Closest `nl_tags.yml` wins, else merge upward

**Benefit:** System-specific requirements, flexible enforcement

---

### **Enhancement 9: Fast Pre-Commit (<300ms)**

**Performance Targets:**
- Tag parsing: < 50ms (staged files only)
- Embedding: < 100ms (incremental, cached)
- Parity calculation: < 100ms (incremental)
- Gate checks: < 50ms
- **Total: < 300ms P95**

**Optimization:**
```python
class FastQuintetAnalyzer:
    """Optimized quintet analyzer for pre-commit"""
    
    def __init__(self):
        self.embedding_cache = EmbeddingCache()
        self.prev_parity = None  # Cache previous result
    
    def analyze_staged_diff(self, diff: GitDiff) -> QuintetParityResult:
        """Fast analysis of staged diff only"""
        # Extract only changed files
        changed_files = diff.staged_files
        
        # Parse tags only from changed files
        tags = self._parse_tags_fast(changed_files)
        
        # Incremental parity calculation
        if self.prev_parity:
            result = self._calculate_parity_incremental(diff, self.prev_parity)
        else:
            result = self._calculate_parity_full(diff)
        
        self.prev_parity = result
        return result
```

**Fallback:** If > 300ms locally, emit advisory pass but enforce in CI

**Benefit:** Fast enough for muscle memory, doesn't slow development

---

### **Enhancement 10: Callgraph Verification**

**For NL_TAG_CONNECT validation:**
```python
class CallgraphBuilder:
    """Build callgraph for CONNECT validation"""
    
    def build_python_callgraph(self, files: List[str]) -> nx.DiGraph:
        """Build callgraph from Python files"""
        graph = nx.DiGraph()
        
        for file in files:
            tree = ast.parse(Path(file).read_text())
            module_name = Path(file).stem
            
            # Add nodes (functions)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = f"{module_name}.{node.name}"
                    graph.add_node(func_name)
                    
                    # Add edges (calls)
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                target = f"{child.func.value.id}.{child.func.attr}"
                                graph.add_edge(func_name, target)
        
        return graph
    
    def validate_connect_tag(self, tag: NLTag, callgraph: nx.DiGraph) -> bool:
        """Validate CONNECT tag has actual edge"""
        if tag.kind != "NL_TAG_CONNECT":
            return True
        
        # Parse SOURCE → TARGET
        if "→" in tag.description:
            source, target = tag.description.split("→")
            
            # Check callgraph
            if callgraph.has_edge(source.strip(), target.strip()):
                return True
        
        return False
```

**Benefit:** CONNECT tags must reflect actual code structure

---

### **Enhancement 11-15: Additional Improvements**

**11. JSON-LD Emission:** All tags stored as JSON-LD in CMC (enables querying)

**12. Bitemporal Tag Tracking:** Tags have transaction_time and valid_time (evolution tracking)

**13. Anti-Gaming:** Boilerplate detection, duplicate IDs, SPEC proof requirements

**14. CLI Tools:** Fast, focused commands for common operations

**15. Per-File Performance Budget:** Timeout if analysis takes > 500ms, advisory pass

---

## 🔄 **INTEGRATION WITH TCS BITEMPORAL TIMELINE**

### **The Timeline Design Connection**

**User mentioned:** Bitemporal timeline showing past memories, current state, future plans

**This is TCS (Timeline Context System)!**

**How NL Tags Integrate with TCS Timeline:**

**Past (Memories):**
```python
# Query: "Show me all NL_TAG changes in the last week"
tags_history = tcs.query_timeline(
    entity_type="nl_tag",
    time_range=(week_ago, now),
    include_evolution=True
)

# Result: Timeline of how tags evolved
# - VIF-WITNESS-001 created (Nov 1)
# - VIF-WITNESS-001 description updated (Nov 2)
# - VIF-WITNESS-001 dependency added (Nov 3)
```

**Present (Current State):**
```python
# Current tags as timeline nodes
current_tags = tcs.get_current_state(entity_type="nl_tag")

# Shows:
# - All active NL tags
# - Their current descriptions
# - Current connections (CONNECT)
# - Current compliance (SPEC)
```

**Future (Plans & Goals):**
```python
# Planned tags for upcoming features
planned_tags = tcs.query_future_timeline(
    entity_type="nl_tag",
    time_range=(now, month_from_now)
)

# Result: Timeline of planned tags
# - VIF-CAL-002: Planned for week 2 (new calibration method)
# - CMC-SNAPSHOT-005: Planned for week 3 (snapshot optimization)
```

**Complete Integration:**
```python
# TCS tracks NL tag evolution bitemporally
class TCSNLTagIntegration:
    def track_tag_creation(self, tag: NLTag):
        """Track tag creation in timeline"""
        tcs.add_timeline_entry(
            entity=tag,
            entity_type="nl_tag",
            operation="created",
            transaction_time=now(),
            valid_time_from=tag.valid_from
        )
    
    def track_tag_update(self, tag: NLTag, changes: Dict):
        """Track tag updates in timeline"""
        tcs.add_timeline_entry(
            entity=tag,
            entity_type="nl_tag",
            operation="updated",
            changes=changes,
            transaction_time=now(),
            valid_time_from=now()  # New version valid from now
        )
    
    def query_tag_evolution(self, tag_id: str) -> Timeline:
        """Query complete evolution of a tag"""
        return tcs.query_timeline(
            entity_id=tag_id,
            entity_type="nl_tag",
            include_all_versions=True
        )
```

**Benefit:** Complete tag evolution history, enables "what changed and when?"

---

## 📊 **ENHANCED IMPLEMENTATION PLAN**

### **Phase 1: Quintet Parity Core (Enhanced)** (10-13 hours)

**Tasks:**
1. QuintetDetector with AST-based symbol extraction (3-4 hours)
2. QuintetParityCalculator with composite metrics (3-4 hours)
3. NLTagGate with all enhancements (2-3 hours)
4. CallgraphBuilder for CONNECT validation (1-2 hours)
5. Testing (1 hour)

### **Phase 2: Pre-Commit + Caching** (3-4 hours)

**Tasks:**
1. Fast pre-commit hook (<300ms) (2 hours)
2. Embedding cache implementation (1-2 hours)

### **Phase 3: VIF Tagging + JSON-LD** (20-28 hours)

**Tasks:**
1. Tag all VIF functions (10-14 hours)
2. JSON-LD emission for all tags (2-3 hours)
3. TCS timeline integration (2-3 hours)
4. Validate quintet parity (1-2 hours)
5. Documentation (1-2 hours)
6. Performance optimization (2-3 hours)

### **Phases 4-6: Unchanged** (58-85 hours)

**Total Enhanced:** 91-130 hours (slightly more for robustness)

---

## 🎯 **ENHANCED SUCCESS CRITERIA**

**Performance:**
- [ ] Pre-commit < 300ms P95
- [ ] Full analysis < 5 seconds
- [ ] Embedding cache hit rate > 80%

**Quality:**
- [ ] AST-based coverage (not heuristic)
- [ ] Composite code↔tags metric
- [ ] Callgraph CONNECT validation
- [ ] JSON-LD tag records in CMC/TCS
- [ ] Anti-gaming checks active

**Integration:**
- [ ] TCS timeline tracks tag evolution
- [ ] Bitemporal queries on tag history
- [ ] Future tags for planned features

---

## 💡 **RECOMMENDATIONS FROM EXTERNAL REVIEW**

**Adopt Immediately:**
1. ✅ AST-based coverage (precise)
2. ✅ Composite code↔tags metric (diagnostic)
3. ✅ Cached embeddings (fast)
4. ✅ Diagnostic report format (clear)
5. ✅ Per-directory policies (flexible)

**Adopt in Phase 2:**
6. ✅ Callgraph verification (robust)
7. ✅ JSON-LD records (complete)
8. ✅ Anti-gaming checks (integrity)

**Consider for Future:**
9. ⚠️ CLI tools (nice-to-have)
10. ⚠️ Auto-fix scaffolding (helpful but can be manual)

---

**Status:** ✅ **ENHANCED PLAN READY** - Incorporates all surgical improvements  
**Time:** 91-130 hours total (10-13 hours for enhanced quintet parity core)  
**Next:** Proceed with Phase 1 (enhanced quintet parity implementation)?

