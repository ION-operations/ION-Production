---
id: sdfcvf_T3_detailed
level: L3
system: SDF-CVF
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# SDF‑CVF – T3 Detailed Implementation Guide

## Setup & Installation

### Dependencies

```bash
# Core dependencies
pip install gitpython>=3.1.0        # Git integration
pip install ast>=0.10                # AST parsing
pip install sentence-transformers>=2.2.0  # Embeddings
pip install numpy>=1.24.0             # Similarity calculations
pip install pyyaml>=6.0              # Configuration

# CI/CD integration
pip install github3.py>=3.0          # GitHub API
pip install pygit2>=1.11             # Git operations
```

### Installation

```bash
# Install SDF-CVF
pip install sdfcvf

# Configure pre-commit hook
sdfcvf install-hooks

# Verify installation
sdfcvf --version
```

## Public API Interfaces

### Core Operations

```python
from packages.sdfcvf import SDFCVF, ParityResult, BlastRadius

# Initialize SDF-CVF
sdfcvf = SDFCVF(
    embedding_service=SentenceTransformerEmbeddingService(),
    threshold=0.90
)

# Detect quartet from Git diff
change = sdfcvf.detect_quartet(diff=git_diff)

# Calculate parity
result = sdfcvf.calculate_parity(change)

# Check gate
gate_result = sdfcvf.enforce_gate(change, gate_type="pre_commit")

# Analyze blast radius
blast_radius = sdfcvf.analyze_blast_radius(change)
```

### Quartet Detection

```python
# Detect quartet from Git diff
change = sdfcvf.detect_quartet(diff=git_diff)

# Detect quartet from PR
change = sdfcvf.detect_quartet_from_pr(pr_number=123)

# Detect quartet from commit
change = sdfcvf.detect_quartet_from_commit(commit_hash="abc123")

# Check completeness
completeness = sdfcvf.check_completeness(change)
if not completeness.complete:
    print(f"Missing elements: {completeness.missing}")
```

### Parity Calculation

```python
# Calculate parity for change
result = sdfcvf.calculate_parity(change)

# Access results
print(f"Parity Score: {result.parity_score}")
print(f"Status: {result.status}")
print(f"Misaligned Pairs: {result.misaligned_pairs}")

# Individual pair scores
print(f"Code↔Docs: {result.code_docs_score}")
print(f"Code↔Tests: {result.code_tests_score}")
print(f"Code↔Traces: {result.code_traces_score}")
```

### Gate Enforcement

```python
# Pre-commit gate
gate_result = sdfcvf.enforce_gate(change, gate_type="pre_commit")
if gate_result.status == "FAIL":
    print(f"Gate failed: {gate_result.message}")
    sys.exit(1)

# CI gate
gate_result = sdfcvf.enforce_gate(change, gate_type="ci")
if gate_result.status == "FAIL":
    github.create_check_run(status="failure", conclusion="Parity gate failed")

# Deployment gate
gate_result = sdfcvf.enforce_gate(change, gate_type="deployment")
if gate_result.status == "FAIL":
    raise DeploymentBlocked(f"Parity {gate_result.parity_score} < 0.90")
```

### Blast Radius Analysis

```python
# Analyze change impact
blast_radius = sdfcvf.analyze_blast_radius(change)

print(f"Total files affected: {blast_radius.total_affected}")
print(f"Direct changes: {len(blast_radius.direct_files)}")
print(f"Dependencies: {len(blast_radius.dependencies)}")
print(f"Related docs: {len(blast_radius.docs)}")
print(f"Related tests: {len(blast_radius.tests)}")
print(f"Estimated effort: {blast_radius.estimated_effort} lines")
```

### Auto-Remediation

```python
# Get remediation suggestions
suggestions = sdfcvf.suggest_remediation(change, parity_result)

for suggestion in suggestions:
    print(f"Type: {suggestion.type}")
    print(f"Element: {suggestion.element}")
    print(f"Suggestion: {suggestion.suggestion}")
    if suggestion.template:
        print(f"Template: {suggestion.template}")
```

## Implementation Details

### Quartet Detection Implementation

```python
class QuartetDetector:
    """Detect quartet elements from Git changes"""
    
    def detect_from_git_diff(self, diff: str) -> Change:
        """Extract quartet from Git diff"""
        files = self._parse_diff_files(diff)
        
        code_files = [f for f in files if self._is_code_file(f)]
        doc_files = [f for f in files if self._is_doc_file(f)]
        test_files = [f for f in files if self._is_test_file(f)]
        trace_files = self._find_related_traces(files)
        
        return Change(
            code_files=code_files,
            doc_files=doc_files,
            test_files=test_files,
            trace_files=trace_files
        )
    
    def _parse_diff_files(self, diff: str) -> List[str]:
        """Parse files from Git diff"""
        files = []
        for line in diff.split('\n'):
            if line.startswith('diff --git'):
                # Extract file paths
                parts = line.split()
                if len(parts) >= 3:
                    file_path = parts[2].lstrip('b/')
                    files.append(file_path)
        return files
    
    def _is_code_file(self, path: str) -> bool:
        """Check if file is code"""
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs'}
        return any(path.endswith(ext) for ext in code_extensions)
    
    def _is_doc_file(self, path: str) -> bool:
        """Check if file is documentation"""
        doc_extensions = {'.md', '.rst', '.txt'}
        doc_patterns = ['README', 'docs/', 'documentation/']
        return (any(path.endswith(ext) for ext in doc_extensions) or
                any(pattern in path for pattern in doc_patterns))
    
    def _is_test_file(self, path: str) -> bool:
        """Check if file is test"""
        test_patterns = ['test_', '_test.', 'spec.', '.test.']
        return any(pattern in path for pattern in test_patterns)
    
    def _find_related_traces(self, files: List[str]) -> List[str]:
        """Find VIF witnesses and SEG nodes related to changes"""
        traces = []
        
        # Query VIF for witnesses related to changed files
        for file_path in files:
            vif_witnesses = self.vif_client.query_witnesses(
                filter={"file_path": file_path}
            )
            traces.extend([w.id for w in vif_witnesses])
        
        # Query SEG for nodes related to changed code
        for file_path in files:
            seg_nodes = self.seg_client.query_nodes(
                filter={"source": file_path}
            )
            traces.extend([n.id for n in seg_nodes])
        
        return traces
```

### Parity Calculation Implementation

```python
class ParityCalculator:
    """Calculate quartet parity score"""
    
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
    
    def calculate(self, change: Change) -> ParityResult:
        """Calculate parity for change"""
        
        # Extract text from quartet elements
        code_text = self._extract_code_text(change.code_files)
        docs_text = self._extract_docs_text(change.doc_files)
        tests_text = self._extract_test_text(change.test_files)
        traces_text = self._extract_trace_text(change.trace_files)
        
        # Generate embeddings
        embeddings = {
            "code": self.embedding_service.embed(code_text),
            "docs": self.embedding_service.embed(docs_text),
            "tests": self.embedding_service.embed(tests_text),
            "traces": self.embedding_service.embed(traces_text)
        }
        
        # Calculate all 6 pairwise similarities
        pairs = [
            ("code", "docs"),
            ("code", "tests"),
            ("code", "traces"),
            ("docs", "tests"),
            ("docs", "traces"),
            ("tests", "traces")
        ]
        
        pair_scores = {}
        similarities = []
        
        for a, b in pairs:
            sim = cosine_similarity(
                [embeddings[a]],
                [embeddings[b]]
            )[0, 0]
            similarities.append(sim)
            pair_scores[f"{a}×{b}"] = sim
        
        # Average = parity score
        parity = sum(similarities) / len(similarities)
        
        # Find misaligned pairs
        misaligned = [
            pair for pair, score in pair_scores.items()
            if score < 0.80
        ]
        
        return ParityResult(
            parity_score=parity,
            threshold=0.90,
            status="PASS" if parity >= 0.90 else "FAIL",
            pair_scores=pair_scores,
            misaligned_pairs=misaligned,
            code_docs_score=pair_scores["code×docs"],
            code_tests_score=pair_scores["code×tests"],
            code_traces_score=pair_scores["code×traces"],
            docs_tests_score=pair_scores["docs×tests"],
            docs_traces_score=pair_scores["docs×traces"],
            tests_traces_score=pair_scores["tests×traces"]
        )
    
    def _extract_code_text(self, code_files: List[str]) -> str:
        """Extract meaningful code text"""
        texts = []
        for file_path in code_files:
            try:
                with open(file_path, 'r') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                
                # Extract function/class signatures + docstrings
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        sig = f"def {node.name}({self._format_args(node.args)})"
                        docstring = ast.get_docstring(node) or ""
                        texts.append(f"{sig}\n{docstring}")
                    elif isinstance(node, ast.ClassDef):
                        sig = f"class {node.name}"
                        docstring = ast.get_docstring(node) or ""
                        texts.append(f"{sig}\n{docstring}")
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        return "\n\n".join(texts)
    
    def _extract_docs_text(self, doc_files: List[str]) -> str:
        """Extract documentation text"""
        texts = []
        for file_path in doc_files:
            try:
                with open(file_path, 'r') as f:
                    text = f.read()
                    texts.append(text)
            except Exception as e:
                continue
        return "\n\n".join(texts)
    
    def _extract_test_text(self, test_files: List[str]) -> str:
        """Extract test text"""
        texts = []
        for file_path in test_files:
            try:
                with open(file_path, 'r') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                
                # Extract test function names + assertions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        texts.append(node.name.replace('_', ' '))
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assert):
                                texts.append(ast.unparse(child.test))
            except Exception as e:
                continue
        return "\n\n".join(texts)
    
    def _extract_trace_text(self, trace_files: List[str]) -> str:
        """Extract execution trace text"""
        texts = []
        
        # VIF witnesses
        vif_witnesses = self._load_vif_witnesses(trace_files)
        for vif in vif_witnesses:
            texts.append(f"Model: {vif.model_id}, Confidence: {vif.confidence_band}")
        
        # SEG provenance
        seg_nodes = self._load_seg_nodes(trace_files)
        for node in seg_nodes:
            if node.type == "derivation":
                texts.append(node.reasoning)
        
        return "\n\n".join(texts)
    
    def _format_args(self, args: ast.arguments) -> str:
        """Format function arguments"""
        arg_names = [arg.arg for arg in args.args]
        return ", ".join(arg_names)
```

### Pre-Commit Hook Implementation

```python
#!/usr/bin/env python3
"""Git pre-commit hook for SDF-CVF parity checking"""

import sys
import subprocess
from packages.sdfcvf import SDFCVF

def main():
    """Run pre-commit gate"""
    # Get staged files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error: Could not get staged files")
        sys.exit(1)
    
    staged_files = result.stdout.strip().split('\n')
    if not staged_files or staged_files == ['']:
        print("No files staged for commit")
        sys.exit(0)
    
    # Get diff
    diff_result = subprocess.run(
        ['git', 'diff', '--cached'],
        capture_output=True,
        text=True
    )
    diff = diff_result.stdout
    
    # Initialize SDF-CVF
    sdfcvf = SDFCVF()
    
    # Detect quartet
    change = sdfcvf.detect_quartet(diff=diff)
    
    # Check completeness
    completeness = sdfcvf.check_completeness(change)
    if not completeness.complete:
        print(f"❌ Pre-commit gate FAILED")
        print(f"Missing quartet elements: {', '.join(completeness.missing)}")
        print(f"\nPlease add:")
        for missing in completeness.missing:
            print(f"  - {missing}")
        sys.exit(1)
    
    # Calculate parity
    parity = sdfcvf.calculate_parity(change)
    
    # Check gate
    if parity.status == "FAIL":
        print(f"❌ Pre-commit gate FAILED")
        print(f"Parity score: {parity.parity_score:.2f} < threshold 0.90")
        print(f"\nMisaligned pairs:")
        for pair in parity.misaligned_pairs:
            print(f"  - {pair}: {parity.pair_scores[pair]:.2f}")
        
        # Get remediation suggestions
        suggestions = sdfcvf.suggest_remediation(change, parity)
        if suggestions:
            print(f"\nSuggestions:")
            for suggestion in suggestions:
                print(f"  → {suggestion.suggestion}")
        
        sys.exit(1)
    
    print(f"✅ Pre-commit gate PASSED (P={parity.parity_score:.2f})")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### CI Gate Implementation

```python
# GitHub Actions workflow
# .github/workflows/parity-check.yml

name: Quartet Parity Check

on:
  pull_request:
    branches: [main]

jobs:
  parity-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install sdfcvf
      
      - name: Check parity
        run: |
          python -m sdfcvf.ci_gate --pr ${{ github.event.pull_request.number }}
```

```python
# CI gate script
# packages/sdfcvf/ci_gate.py

import sys
import argparse
from packages.sdfcvf import SDFCVF
from packages.sdfcvf.github import GitHubClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', type=int, required=True)
    args = parser.parse_args()
    
    # Initialize
    sdfcvf = SDFCVF()
    github = GitHubClient()
    
    # Get PR changes
    pr_files = github.get_pr_files(args.pr)
    
    # Detect quartet
    change = sdfcvf.detect_quartet_from_pr(args.pr)
    
    # Validate
    completeness = sdfcvf.check_completeness(change)
    if not completeness.complete:
        github.create_check_run(
            status="failure",
            conclusion="Incomplete quartet",
            output={
                "title": "Quartet Parity Check",
                "summary": f"Missing elements: {', '.join(completeness.missing)}"
            }
        )
        sys.exit(1)
    
    # Calculate parity
    parity = sdfcvf.calculate_parity(change)
    
    if parity.status == "FAIL":
        github.create_check_run(
            status="failure",
            conclusion="Low parity",
            output={
                "title": "Quartet Parity Check",
                "summary": f"Parity {parity.parity_score:.2f} < threshold 0.90",
                "text": "\n".join(parity.misaligned_pairs)
            }
        )
        sys.exit(1)
    
    # Pass
    github.create_check_run(
        status="success",
        conclusion="Parity gate passed",
        output={
            "title": "Quartet Parity Check",
            "summary": f"P={parity.parity_score:.2f} >= 0.90"
        }
    )
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Blast Radius Analysis Implementation

```python
class BlastRadiusAnalyzer:
    """Calculate change impact"""
    
    def analyze(self, change: Change) -> BlastRadius:
        """Analyze blast radius for change"""
        
        # Direct changes
        direct_files = change.code_files + change.doc_files + change.test_files
        
        # Find dependencies
        dependencies = []
        for code_file in change.code_files:
            deps = self._find_dependencies(code_file)
            dependencies.extend(deps)
        
        # Find related documentation
        docs = []
        for code_file in change.code_files:
            related_docs = self._find_mentioning_docs(code_file)
            docs.extend(related_docs)
        
        # Find related tests
        tests = []
        for code_file in change.code_files:
            covering_tests = self._find_covering_tests(code_file)
            tests.extend(covering_tests)
        
        # Find related traces
        traces = change.trace_files
        
        # Calculate totals
        all_affected = set(direct_files + dependencies + docs + tests + traces)
        total_affected = len(all_affected)
        
        # Estimate effort
        estimated_effort = self._estimate_effort(all_affected)
        
        return BlastRadius(
            direct_files=direct_files,
            dependencies=list(set(dependencies)),
            docs=list(set(docs)),
            tests=list(set(tests)),
            traces=list(set(traces)),
            total_affected=total_affected,
            estimated_effort=estimated_effort,
            breakdown={
                "code": len(change.code_files),
                "docs": len(docs),
                "tests": len(tests),
                "traces": len(traces)
            }
        )
    
    def _find_dependencies(self, file_path: str) -> List[str]:
        """Find files that import or reference this file"""
        dependencies = []
        
        # Parse imports
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Resolve import to file path
                        dep_file = self._resolve_import(alias.name)
                        if dep_file:
                            dependencies.append(dep_file)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep_file = self._resolve_import(node.module)
                        if dep_file:
                            dependencies.append(dep_file)
        except Exception:
            pass
        
        return dependencies
    
    def _find_mentioning_docs(self, file_path: str) -> List[str]:
        """Find documentation that mentions this file"""
        docs = []
        
        # Search all doc files for references
        for doc_file in self._find_all_doc_files():
            try:
                with open(doc_file, 'r') as f:
                    content = f.read()
                    if file_path in content or self._extract_module_name(file_path) in content:
                        docs.append(doc_file)
            except Exception:
                continue
        
        return docs
    
    def _find_covering_tests(self, file_path: str) -> List[str]:
        """Find tests that cover this file"""
        tests = []
        
        # Use coverage data if available
        # Otherwise, search for test files that import the module
        module_name = self._extract_module_name(file_path)
        
        for test_file in self._find_all_test_files():
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    if module_name in content:
                        tests.append(test_file)
            except Exception:
                continue
        
        return tests
    
    def _estimate_effort(self, files: List[str]) -> int:
        """Estimate lines of code to update"""
        total_lines = 0
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    lines = len(f.readlines())
                    total_lines += lines
            except Exception:
                continue
        return total_lines
```

### Auto-Remediation Implementation

```python
class AutoRemediationEngine:
    """Generate remediation suggestions"""
    
    def suggest(self, change: Change, parity: ParityResult) -> List[RemediationSuggestion]:
        """Generate suggestions for low-parity change"""
        suggestions = []
        
        # Check completeness
        completeness = QuartetCompleteness.check(change)
        if not completeness.complete:
            for missing in completeness.missing:
                suggestions.append(self._suggest_missing_element(missing, change))
        
        # Check misalignments
        for pair in parity.misaligned_pairs:
            suggestions.append(self._suggest_alignment_improvement(pair, parity))
        
        return suggestions
    
    def _suggest_missing_element(self, element: str, change: Change) -> RemediationSuggestion:
        """Suggest adding missing quartet element"""
        if element == "docs":
            return RemediationSuggestion(
                type="missing_element",
                element="docs",
                suggestion="Add documentation for changed code",
                template=self._get_doc_template(change.code_files),
                examples=self._get_doc_examples()
            )
        elif element == "tests":
            return RemediationSuggestion(
                type="missing_element",
                element="tests",
                suggestion="Add tests for changed code",
                template=self._get_test_template(change.code_files),
                examples=self._get_test_examples()
            )
        elif element == "traces":
            return RemediationSuggestion(
                type="missing_element",
                element="traces",
                suggestion="Add VIF witnesses or SEG nodes for this change",
                template=self._get_trace_template(change.code_files),
                examples=self._get_trace_examples()
            )
    
    def _suggest_alignment_improvement(self, pair: str, parity: ParityResult) -> RemediationSuggestion:
        """Suggest improving alignment between pair"""
        elements = pair.split('×')
        element_a, element_b = elements[0], elements[1]
        
        score = parity.pair_scores[pair]
        
        return RemediationSuggestion(
            type="misalignment",
            element=pair,
            suggestion=f"Improve alignment between {element_a} and {element_b} (current: {score:.2f})",
            template=None,
            examples=self._get_alignment_examples(element_a, element_b)
        )
```

## Configuration

### Configuration File

```yaml
# .sdfcvf.yaml

# Parity threshold
threshold: 0.90

# Embedding service
embedding:
  service: sentence_transformers
  model: all-MiniLM-L6-v2

# Gate configuration
gates:
  pre_commit:
    enabled: true
    threshold: 0.90
  ci:
    enabled: true
    threshold: 0.90
  deployment:
    enabled: true
    threshold: 0.90

# Blast radius
blast_radius:
  max_dependency_depth: 10
  include_transitive_deps: true

# Auto-remediation
remediation:
  enabled: true
  suggest_templates: true
```

### Environment-Specific Configuration

```yaml
# Development: Lower threshold
threshold: 0.85

# Production: Strict threshold
threshold: 0.95
```

## Error Handling

### Missing Artifacts

```python
try:
    change = sdfcvf.detect_quartet(diff=diff)
except MissingArtifactError as e:
    print(f"Missing artifact: {e.artifact}")
    print(f"Please add: {e.suggestion}")
```

### Stale Traces

```python
try:
    parity = sdfcvf.calculate_parity(change)
except StaleTraceError as e:
    print(f"Stale traces detected: {e.trace_files}")
    print("Please regenerate traces for this change")
```

### Invalid Configuration

```python
try:
    sdfcvf = SDFCVF(config_file=".sdfcvf.yaml")
except InvalidConfigError as e:
    print(f"Configuration error: {e.message}")
    print(f"Fix: {e.suggestion}")
```

## Examples

### CLI Usage

```bash
# Check parity for current changes
sdfcvf check

# Check parity for specific commit
sdfcvf check --commit abc123

# Check parity for PR
sdfcvf check --pr 123

# Analyze blast radius
sdfcvf blast-radius --commit abc123

# Get remediation suggestions
sdfcvf suggest --commit abc123
```

### API Usage

```python
from packages.sdfcvf import SDFCVF

# Initialize
sdfcvf = SDFCVF()

# Check parity
result = sdfcvf.check_parity(commit_hash="abc123")

# Analyze impact
blast_radius = sdfcvf.analyze_blast_radius(commit_hash="abc123")

# Get suggestions
suggestions = sdfcvf.suggest_remediation(commit_hash="abc123")
```

## Testing

### Unit Tests

```python
import pytest
from packages.sdfcvf import SDFCVF, Change

def test_parity_calculation():
    """Test parity calculation"""
    sdfcvf = SDFCVF()
    
    change = Change(
        code_files=["test_code.py"],
        doc_files=["test_docs.md"],
        test_files=["test_tests.py"],
        trace_files=["trace_1.json"]
    )
    
    result = sdfcvf.calculate_parity(change)
    
    assert 0.0 <= result.parity_score <= 1.0
    assert result.status in ["PASS", "FAIL"]

def test_quartet_detection():
    """Test quartet detection"""
    sdfcvf = SDFCVF()
    
    diff = """
    diff --git a/code.py b/code.py
    +def new_function():
    +    pass
    diff --git a/docs.md b/docs.md
    +# New Function
    """
    
    change = sdfcvf.detect_quartet(diff=diff)
    
    assert len(change.code_files) > 0
    assert len(change.doc_files) > 0

def test_gate_enforcement():
    """Test gate enforcement"""
    sdfcvf = SDFCVF()
    
    change = Change(...)  # High-parity change
    
    result = sdfcvf.enforce_gate(change, gate_type="pre_commit")
    
    assert result.status == "PASS"
```

### Integration Tests

```python
def test_pre_commit_hook():
    """Test pre-commit hook integration"""
    # Set up test repository
    # Stage changes
    # Run hook
    # Verify result
    pass

def test_ci_gate():
    """Test CI gate integration"""
    # Mock GitHub API
    # Create test PR
    # Run CI gate
    # Verify check run created
    pass
```

## Troubleshooting

### Common Issues

**Issue: Parity calculation slow**
```python
# Cause: Large files or many files
# Solution: Optimize embedding generation

# Use faster embedding model
sdfcvf = SDFCVF(
    embedding_service=SentenceTransformerEmbeddingService(
        model="all-MiniLM-L6-v2"  # Faster, smaller model
    )
)

# Or cache embeddings
sdfcvf.enable_embedding_cache()
```

**Issue: False positives (code/docs align but fail)**
```python
# Cause: Embedding model doesn't capture semantic similarity
# Solution: Use better model or adjust threshold

# Use better model
sdfcvf = SDFCVF(
    embedding_service=SentenceTransformerEmbeddingService(
        model="all-mpnet-base-v2"  # Better quality
    )
)

# Or lower threshold temporarily
sdfcvf.configure(threshold=0.85)
```

**Issue: Missing traces detected**
```python
# Cause: VIF/SEG not integrated
# Solution: Ensure VIF/SEG integration

# Configure trace sources
sdfcvf.configure(
    trace_sources=["vif", "seg"]
)

# Or disable trace requirement temporarily
sdfcvf.configure(
    require_traces=False
)
```

## Migration Notes

### T→L Cutover Steps

1. **Validate T-level documentation** against gate checklist
2. **Review with stakeholders** for accuracy and completeness
3. **Update L-level docs** with T-level content (preserve T-level for history)
4. **Update navigation indexes** to reference L-level instead of T-level
5. **Run validation gates** to ensure compliance
6. **Archive T-level** in historical_versions/

### Validation Checklist

- [ ] All interfaces documented with examples
- [ ] All configuration options explained
- [ ] Error handling covered
- [ ] Tests provided
- [ ] Troubleshooting guide included
- [ ] Migration steps documented

## References

- **System Map:** `knowledge_architecture/systems/sdfcvf/system.map.lucid.json5`
- **L-Level Docs:** `knowledge_architecture/systems/sdfcvf/L{0-4}_*.md`
- **Gate Validation:** `coordination/epic_standards_overhaul/artifacts/gate_checks/SDFCVF_T0_T6_GATE_RESULTS.md`
- **Templates:** `knowledge_architecture/TEMPLATES_LIBRARY/T3_DETAILED_TEMPLATE.md`
- **Code:** `packages/sdfcvf/`
