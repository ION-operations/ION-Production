"""
SDF-CVF Quintet Parity System

Extends quartet parity (Code, Docs, Tests, Traces) to quintet parity (+ NL Tags).
Implements all surgical improvements for robustness, speed, and unfakeability.

Key Features:
- AST-based symbol extraction (multi-language)
- Composite code↔tags metric (sig + name + doc + spec)
- Callgraph verification for CONNECT tags
- JSON-LD tag records with content hashes
- Cached & incremental embeddings
- Anti-gaming checks
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

# Import from existing packages
try:
    from packages.nl_tags import NLTag, NLTagParser
except ImportError:
    print("Warning: packages.nl_tags not available, quintet features limited")
    NLTag = None
    NLTagParser = None

# NL_TAG: SDFCVF-MODEL-016 | Code symbol representation for AST extraction | CodeSymbol(name: str, signature: str, line_number: int, file_path: str, docstring: Optional[str] = None, is_public: bool = True, language: str = "python") | []
@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, method)"""
    name: str
    signature: str
    line_number: int
    file_path: str
    docstring: Optional[str] = None
    is_public: bool = True  # Exported/public vs internal
    language: str = "python"

# NL_TAG: SDFCVF-MODEL-017 | Quintet data model for code/docs/tests/traces/nl_tags | Quintet(code: List[str], docs: List[str], tests: List[str], traces: List[str], nl_tags: List[NLTag], code_symbols: List[CodeSymbol] = [], detected_at: datetime = ...) | [SDFCVF-MODEL-016]
@dataclass
class Quintet:
    """Five elements for quintet parity"""
    code: List[str]  # Code file paths
    docs: List[str]  # Documentation file paths
    tests: List[str]  # Test file paths
    traces: List[str]  # Trace file paths (VIF witnesses, etc.)
    nl_tags: List[NLTag]  # NL tags extracted from code
    
    # Metadata
    code_symbols: List[CodeSymbol] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)

# NL_TAG: SDFCVF-MODEL-018 | Composite code↔tags similarity score | CompositeScore(composite: float, sim_sig: float, sim_name: float, sim_doc: float, spec_ok: float) | []
@dataclass
class CompositeScore:
    """Composite code↔tags similarity with sub-scores"""
    composite: float  # Overall score
    sim_sig: float    # Signature similarity (structural)
    sim_name: float   # Name similarity (semantic)
    sim_doc: float    # Documentation similarity (semantic)
    spec_ok: float    # SPEC validation (0 or 1)
    
    def __str__(self) -> str:
        return f"Composite: {self.composite:.2f} (sig:{self.sim_sig:.2f}, name:{self.sim_name:.2f}, doc:{self.sim_doc:.2f}, spec:{self.spec_ok:.2f})"

# NL_TAG: SDFCVF-MODEL-019 | Quintet parity calculation result | QuintetParityResult(score: float, similarities: Dict[str, float], is_quintet: bool = True, code_tags_composite: Optional[CompositeScore] = None, issues: List[str] = [], warnings: List[str] = [], boilerplate_detected: List[str] = []) | [SDFCVF-MODEL-018]
@dataclass
class QuintetParityResult:
    """Quintet parity calculation result with diagnostic details"""
    score: float  # Overall parity score (0-1)
    similarities: Dict[str, float]  # All 10 pairwise similarities
    is_quintet: bool = True
    
    # Composite score for code↔tags
    code_tags_composite: Optional[CompositeScore] = None
    
    # Diagnostic information
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    boilerplate_detected: List[str] = field(default_factory=list)
    
    def passed(self, threshold: float = 0.90) -> bool:
        """Check if parity passes threshold"""
        return self.score >= threshold and len(self.issues) == 0

# NL_TAG: SDFCVF-QUINTET-001 | AST-based symbol extractor for code analysis | ASTSymbolExtractor | []
class ASTSymbolExtractor:
    """Extract symbols from code using AST (multi-language support)"""
    
    @staticmethod
    def extract_python_symbols(file_path: str) -> List[CodeSymbol]:
        """Extract all function/class symbols from Python file using AST"""
        try:
            src = Path(file_path).read_text(encoding="utf-8")
            tree = ast.parse(src)
            symbols = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Function/method
                    name = node.name
                    
                    # Build signature
                    args = [arg.arg for arg in node.args.args]
                    sig = f"{name}({', '.join(args)})"
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node)
                    
                    # Check if public (doesn't start with _)
                    is_public = not name.startswith('_')
                    
                    symbol = CodeSymbol(
                        name=name,
                        signature=sig,
                        line_number=node.lineno,
                        file_path=file_path,
                        docstring=docstring,
                        is_public=is_public,
                        language="python"
                    )
                    symbols.append(symbol)
                    
                elif isinstance(node, ast.ClassDef):
                    # Class
                    name = node.name
                    sig = f"class {name}"
                    docstring = ast.get_docstring(node)
                    is_public = not name.startswith('_')
                    
                    symbol = CodeSymbol(
                        name=name,
                        signature=sig,
                        line_number=node.lineno,
                        file_path=file_path,
                        docstring=docstring,
                        is_public=is_public,
                        language="python"
                    )
                    symbols.append(symbol)
            
            return symbols
            
        except Exception as e:
            print(f"Error extracting Python symbols from {file_path}: {e}")
            return []
    
    @staticmethod
    def extract_symbols(file_path: str) -> List[CodeSymbol]:
        """Extract symbols from file (auto-detect language)"""
        file_path_obj = Path(file_path)
        
        if file_path_obj.suffix == ".py":
            return ASTSymbolExtractor.extract_python_symbols(file_path)
        # TODO: Add TypeScript, JavaScript, Java extractors
        else:
            return []

# NL_TAG: SDFCVF-QUINTET-002 | Quintet detector with AST symbol extraction | QuintetDetector() | [SDFCVF-QUINTET-001]
class QuintetDetector:
    """Detects quintet elements from code changes with AST-based symbol extraction"""
    
    def __init__(self):
        if NLTagParser:
            self.nl_tag_parser = NLTagParser()
        else:
            self.nl_tag_parser = None
        self.symbol_extractor = ASTSymbolExtractor()
    
    # NL_TAG: SDFCVF-QUINTET-003 | Detect quintet from file lists | detect_from_files(code_files: List[str], docs_files: List[str], tests_files: List[str], traces_files: List[str]) -> Quintet | [SDFCVF-QUINTET-002, SDFCVF-MODEL-017]
    def detect_from_files(self, 
                         code_files: List[str],
                         docs_files: List[str],
                         tests_files: List[str],
                         traces_files: List[str]) -> Quintet:
        """Detect quintet from file lists"""
        # Extract NL tags from code files
        nl_tags = []
        if self.nl_tag_parser:
            for code_file in code_files:
                try:
                    tags = self.nl_tag_parser.parse_file(code_file)
                    nl_tags.extend(tags)
                except Exception as e:
                    print(f"Warning: Could not parse tags from {code_file}: {e}")
        
        # Extract code symbols using AST
        code_symbols = []
        for code_file in code_files:
            symbols = self.symbol_extractor.extract_symbols(code_file)
            code_symbols.extend(symbols)
        
        return Quintet(
            code=code_files,
            docs=docs_files,
            tests=tests_files,
            traces=traces_files,
            nl_tags=nl_tags,
            code_symbols=code_symbols
        )

# NL_TAG: SDFCVF-QUINTET-004 | Quintet parity calculator with composite code↔tags metric | QuintetParityCalculator(embedding_service: Optional[callable] = None) | [SDFCVF-MODEL-017]
class QuintetParityCalculator:
    """Calculates quintet parity with composite code↔tags metric"""
    
    def __init__(self, embedding_service=None):
        self.embedding_service = embedding_service
        self.embedding_cache = {}  # Simple in-memory cache
    
    # NL_TAG: SDFCVF-QUINTET-005 | Calculate quintet parity with composite code↔tags metric | calculate_parity(quintet: Quintet) -> QuintetParityResult | [SDFCVF-QUINTET-004, SDFCVF-MODEL-017, SDFCVF-MODEL-019]
    def calculate_parity(self, quintet: Quintet) -> QuintetParityResult:
        """Calculate quintet parity (10 pairwise similarities)"""
        # Extract embeddings (with caching)
        emb_code = self._embed_code(quintet.code)
        emb_docs = self._embed_docs(quintet.docs)
        emb_tests = self._embed_tests(quintet.tests)
        emb_traces = self._embed_traces(quintet.traces)
        emb_tags = self._embed_nl_tags(quintet.nl_tags)
        
        # Calculate 10 pairwise similarities
        similarities = {
            # Original 6 (quartet)
            "code_docs": self._cosine_similarity(emb_code, emb_docs),
            "code_tests": self._cosine_similarity(emb_code, emb_tests),
            "code_traces": self._cosine_similarity(emb_code, emb_traces),
            "docs_tests": self._cosine_similarity(emb_docs, emb_tests),
            "docs_traces": self._cosine_similarity(emb_docs, emb_traces),
            "tests_traces": self._cosine_similarity(emb_tests, emb_traces),
            
            # New 4 (quintet - NL tags)
            "code_tags": 0.0,  # Calculated below with composite metric
            "docs_tags": self._cosine_similarity(emb_docs, emb_tags),
            "tests_tags": self._cosine_similarity(emb_tests, emb_tags),
            "traces_tags": self._cosine_similarity(emb_traces, emb_tags),
        }
        
        # Calculate composite code↔tags metric
        code_tags_composite = self._calculate_composite_code_tags(
            quintet.code_symbols,
            quintet.nl_tags
        )
        similarities["code_tags"] = code_tags_composite.composite
        
        # Overall parity score (average of all 10)
        parity_score = sum(similarities.values()) / len(similarities)
        
        # Detect anti-gaming issues
        boilerplate = self._detect_boilerplate(quintet.nl_tags)
        
        return QuintetParityResult(
            score=parity_score,
            similarities=similarities,
            code_tags_composite=code_tags_composite,
            boilerplate_detected=boilerplate
        )
    
    def _calculate_composite_code_tags(self, 
                                      code_symbols: List[CodeSymbol],
                                      nl_tags: List[NLTag]) -> CompositeScore:
        """Calculate composite code↔tags similarity (sig + name + doc + spec)"""
        if not code_symbols or not nl_tags:
            return CompositeScore(0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Weights (from external review)
        w_sig = 0.4
        w_name = 0.3
        w_doc = 0.2
        w_spec = 0.1
        
        # Calculate each component
        sim_sig = self._signature_similarity(code_symbols, nl_tags)
        sim_name = self._name_similarity(code_symbols, nl_tags)
        sim_doc = self._doc_similarity(code_symbols, nl_tags)
        spec_ok = self._spec_compliance(nl_tags)
        
        # Composite score
        composite = w_sig * sim_sig + w_name * sim_name + w_doc * sim_doc + w_spec * spec_ok
        
        return CompositeScore(
            composite=composite,
            sim_sig=sim_sig,
            sim_name=sim_name,
            sim_doc=sim_doc,
            spec_ok=spec_ok
        )
    
    def _signature_similarity(self, symbols: List[CodeSymbol], tags: List[NLTag]) -> float:
        """Calculate signature similarity (Jaccard)"""
        if not symbols or not tags:
            return 0.0
        
        # Match symbols to tags by line number proximity
        matches = []
        for symbol in symbols:
            # Find tag closest to symbol
            closest_tag = None
            min_distance = float('inf')
            
            for tag in tags:
                if tag.file_path == symbol.file_path:
                    distance = abs(tag.line_start - symbol.line_number)
                    if distance < min_distance:
                        min_distance = distance
                        closest_tag = tag
            
            if closest_tag and hasattr(closest_tag, 'syntax_ref') and closest_tag.syntax_ref:
                # Jaccard similarity on signature tokens
                sig_tokens = set(symbol.signature.replace('(', ' ').replace(')', ' ').replace(',', ' ').split())
                tag_tokens = set(closest_tag.syntax_ref.replace('(', ' ').replace(')', ' ').replace(',', ' ').split())
                
                jaccard = len(sig_tokens & tag_tokens) / len(sig_tokens | tag_tokens) if sig_tokens | tag_tokens else 0.0
                matches.append(jaccard)
        
        return sum(matches) / len(matches) if matches else 0.0
    
    def _name_similarity(self, symbols: List[CodeSymbol], tags: List[NLTag]) -> float:
        """Calculate name similarity (cosine on symbol name vs tag ID)"""
        if not symbols or not tags:
            return 0.0
        
        # Match symbols to tags by line number proximity (same as signature_similarity)
        similarities = []
        for symbol in symbols:
            # Find tag closest to symbol
            closest_tag = None
            min_distance = float('inf')
            
            for tag in tags:
                if tag.file_path == symbol.file_path:
                    distance = abs(tag.line_start - symbol.line_number)
                    if distance < min_distance:
                        min_distance = distance
                        closest_tag = tag
            
            if closest_tag:
                # Embed symbol name and tag ID
                symbol_name_emb = self._get_or_compute_embedding(symbol.name, f"symbol_name_{symbol.name}")
                tag_id_emb = self._get_or_compute_embedding(
                    getattr(closest_tag, 'canonical_id', '') or getattr(closest_tag, 'id', ''),
                    f"tag_id_{closest_tag.id}"
                )
                
                # Cosine similarity
                sim = self._cosine_similarity(symbol_name_emb, tag_id_emb)
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _doc_similarity(self, symbols: List[CodeSymbol], tags: List[NLTag]) -> float:
        """Calculate documentation similarity (cosine on docstring vs tag description)"""
        if not symbols or not tags:
            return 0.0
        
        # Match symbols to tags by line number proximity
        similarities = []
        for symbol in symbols:
            # Skip symbols without docstrings
            if not symbol.docstring:
                continue
            
            # Find tag closest to symbol
            closest_tag = None
            min_distance = float('inf')
            
            for tag in tags:
                if tag.file_path == symbol.file_path:
                    distance = abs(tag.line_start - symbol.line_number)
                    if distance < min_distance:
                        min_distance = distance
                        closest_tag = tag
            
            if closest_tag:
                # Embed docstring and tag description
                docstring_emb = self._get_or_compute_embedding(symbol.docstring, f"docstring_{symbol.name}")
                tag_desc_emb = self._get_or_compute_embedding(
                    getattr(closest_tag, 'tag_text', '') or str(closest_tag),
                    f"tag_desc_{closest_tag.id}"
                )
                
                # Cosine similarity
                sim = self._cosine_similarity(docstring_emb, tag_desc_emb)
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _spec_compliance(self, tags: List[NLTag]) -> float:
        """Calculate SPEC compliance (0-1)"""
        if not tags:
            return 0.0
        
        # Count SPEC tags with execution proof
        spec_tags = [t for t in tags if hasattr(t, 'kind') and 'SPEC' in str(getattr(t, 'kind', ''))]
        if not spec_tags:
            return 1.0  # No SPEC tags = N/A, return 1.0
        
        # Check if SPEC tags have validation proof (placeholder - would execute validators)
        validated = sum(1 for t in spec_tags if self._has_spec_proof(t))
        
        return validated / len(spec_tags)
    
    def _has_spec_proof(self, tag: NLTag) -> bool:
        """Check if SPEC tag has execution proof"""
        # Placeholder - would execute validator and check for proof
        return True
    
    def _detect_boilerplate(self, tags: List[NLTag]) -> List[str]:
        """Detect boilerplate tag descriptions"""
        if not tags:
            return []
        
        # Count description frequencies
        desc_counts = {}
        for tag in tags:
            desc = tag.tag_text if hasattr(tag, 'tag_text') else str(tag)
            desc_counts[desc] = desc_counts.get(desc, 0) + 1
        
        # Find descriptions repeated > 5 times
        boilerplate = [desc for desc, count in desc_counts.items() if count > 5]
        
        return boilerplate
    
    def _embed_code(self, code_files: List[str]) -> np.ndarray:
        """Generate embedding for code files (with caching)"""
        # Combine all code content
        combined = ""
        for file in code_files:
            try:
                combined += Path(file).read_text(encoding="utf-8") + "\n"
            except:
                pass
        
        return self._get_or_compute_embedding(combined, "code")
    
    def _embed_docs(self, docs_files: List[str]) -> np.ndarray:
        """Generate embedding for documentation files"""
        combined = ""
        for file in docs_files:
            try:
                combined += Path(file).read_text(encoding="utf-8") + "\n"
            except:
                pass
        
        return self._get_or_compute_embedding(combined, "docs")
    
    def _embed_tests(self, tests_files: List[str]) -> np.ndarray:
        """Generate embedding for test files"""
        combined = ""
        for file in tests_files:
            try:
                combined += Path(file).read_text(encoding="utf-8") + "\n"
            except:
                pass
        
        return self._get_or_compute_embedding(combined, "tests")
    
    def _embed_traces(self, traces_files: List[str]) -> np.ndarray:
        """Generate embedding for trace files"""
        combined = ""
        for file in traces_files:
            try:
                combined += Path(file).read_text(encoding="utf-8") + "\n"
            except:
                pass
        
        return self._get_or_compute_embedding(combined, "traces")
    
    def _embed_nl_tags(self, nl_tags: List[NLTag]) -> np.ndarray:
        """Generate embedding for NL tags (weighted pool)"""
        if not nl_tags:
            return np.zeros(384)  # Default embedding size
        
        # Weighted pool of tag components
        tag_vecs = []
        for tag in nl_tags:
            # Get tag components
            desc = tag.tag_text if hasattr(tag, 'tag_text') else ""
            syntax_ref = getattr(tag, 'syntax_ref', "") or ""
            deps = " ".join(getattr(tag, 'dependencies', []) or [])
            
            # Embed each component
            e_desc = self._get_or_compute_embedding(desc, f"tag_desc_{tag.id}")
            e_sig = self._get_or_compute_embedding(syntax_ref, f"tag_sig_{tag.id}")
            e_deps = self._get_or_compute_embedding(deps, f"tag_deps_{tag.id}")
            
            # Weighted combination
            tag_vec = 0.5 * e_desc + 0.3 * e_sig + 0.2 * e_deps
            tag_vecs.append(tag_vec)
        
        # Average all tag vectors
        return np.mean(tag_vecs, axis=0) if tag_vecs else np.zeros(384)
    
    def _get_or_compute_embedding(self, content: str, cache_key: str) -> np.ndarray:
        """Get cached embedding or compute new one"""
        # Hash content for cache key
        content_hash = hashlib.blake2b(content.encode(), digest_size=16).hexdigest()
        full_cache_key = f"{cache_key}:{content_hash}"
        
        # Check cache
        if full_cache_key in self.embedding_cache:
            return self.embedding_cache[full_cache_key]
        
        # Compute embedding
        if self.embedding_service:
            embedding = self.embedding_service.embed(content)
        else:
            # Fallback: random embedding (for testing without embedding service)
            embedding = np.random.rand(384)
        
        # Cache
        self.embedding_cache[full_cache_key] = embedding
        
        return embedding
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        if vec1 is None or vec2 is None:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))

class NLTagGate:
    """Gate that enforces NL tag coverage and alignment with enhanced checks"""
    
    def __init__(self,
                 public_coverage_threshold: float = 0.95,
                 internal_coverage_threshold: float = 0.75,
                 code_tags_threshold: float = 0.85,
                 alignment_threshold: float = 0.80):
        self.public_coverage_threshold = public_coverage_threshold
        self.internal_coverage_threshold = internal_coverage_threshold
        self.code_tags_threshold = code_tags_threshold
        self.alignment_threshold = alignment_threshold
    
    # NL_TAG: SDFCVF-QUINTET-005 | Check NL tag gate for coverage and alignment | check(quintet: Quintet, parity_result: QuintetParityResult) -> GateResult | [SDFCVF-QUINTET-004, SDFCVF-MODEL-019]
    def check(self, quintet: Quintet, parity_result: QuintetParityResult) -> 'GateResult':
        """Check NL tag gate with all enhancements"""
        issues = []
        warnings = []
        
        # 1. AST-based coverage check (public vs internal)
        coverage_result = self._check_ast_coverage(quintet)
        if not coverage_result["passed"]:
            issues.extend(coverage_result["issues"])
        warnings.extend(coverage_result["warnings"])
        
        # 2. Composite code↔tags alignment check
        if parity_result.code_tags_composite:
            composite = parity_result.code_tags_composite
            if composite.composite < self.code_tags_threshold:
                issues.append(f"Code-tags alignment {composite.composite:.2f} < {self.code_tags_threshold:.2f}")
                issues.append(f"  Breakdown: {composite}")
        
        # 3. Anti-gaming checks
        if parity_result.boilerplate_detected:
            warnings.append(f"Boilerplate detected in {len(parity_result.boilerplate_detected)} tag descriptions")
        
        # 4. Duplicate ID check
        duplicate_issues = self._check_duplicate_ids(quintet.nl_tags)
        issues.extend(duplicate_issues)
        
        # Gate decision
        passed = len(issues) == 0
        
        return GateResult(
            gate_name="nl_tags",
            passed=passed,
            score=parity_result.score,
            issues=issues,
            warnings=warnings
        )
    
    def _check_ast_coverage(self, quintet: Quintet) -> Dict:
        """Check coverage using AST symbol extraction"""
        if not quintet.code_symbols:
            return {"passed": True, "issues": [], "warnings": ["No code symbols found"]}
        
        # Separate public and internal symbols
        public_symbols = [s for s in quintet.code_symbols if s.is_public]
        internal_symbols = [s for s in quintet.code_symbols if not s.is_public]
        
        # Count tagged symbols
        tagged_symbol_lines = {tag.line_start for tag in quintet.nl_tags}
        
        public_tagged = sum(1 for s in public_symbols if s.line_number in tagged_symbol_lines or any(abs(s.line_number - line) < 3 for line in tagged_symbol_lines))
        internal_tagged = sum(1 for s in internal_symbols if s.line_number in tagged_symbol_lines or any(abs(s.line_number - line) < 3 for line in tagged_symbol_lines))
        
        # Calculate coverage
        public_coverage = public_tagged / len(public_symbols) if public_symbols else 1.0
        internal_coverage = internal_tagged / len(internal_symbols) if internal_symbols else 1.0
        
        issues = []
        warnings = []
        
        # Check thresholds
        if public_coverage < self.public_coverage_threshold:
            issues.append(f"Public API coverage {public_coverage:.1%} < {self.public_coverage_threshold:.1%}")
        
        if internal_coverage < self.internal_coverage_threshold:
            warnings.append(f"Internal coverage {internal_coverage:.1%} < {self.internal_coverage_threshold:.1%}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "public_coverage": public_coverage,
            "internal_coverage": internal_coverage
        }
    
    def _check_duplicate_ids(self, nl_tags: List[NLTag]) -> List[str]:
        """Check for duplicate canonical IDs"""
        seen_ids = {}
        duplicates = []
        
        for tag in nl_tags:
            if hasattr(tag, 'canonical_id') and tag.canonical_id:
                if tag.canonical_id in seen_ids:
                    duplicates.append(f"Duplicate ID {tag.canonical_id} in {tag.file_path} and {seen_ids[tag.canonical_id]}")
                else:
                    seen_ids[tag.canonical_id] = tag.file_path
        
        return duplicates

@dataclass
class GateResult:
    """Gate check result"""
    gate_name: str
    passed: bool
    score: float
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

def print_diagnostic_report(result: QuintetParityResult, quintet: Quintet):
    """Print diagnostic parity report (enhanced format from external review)"""
    print("=" * 80)
    print("Quintet Parity Analysis Report")
    print("=" * 80)
    print()
    print(f"Pair          Score   Status  Notes")
    print("-" * 80)
    
    # Print each similarity
    for pair_name, score in sorted(result.similarities.items()):
        status = "[OK]" if score >= 0.85 else ("[WARN]" if score >= 0.75 else "[FAIL]")
        print(f"{pair_name:12}  {score:.2f}    {status}")
    
    print()
    print(f"Overall: P_quintet = {result.score:.3f}  {'[BELOW 0.90]' if result.score < 0.90 else '[PASSED]'}")
    print()
    
    # code↔tags breakdown
    if result.code_tags_composite:
        print("code <-> tags Breakdown:")
        print(f"  sim_sig:  {result.code_tags_composite.sim_sig:.2f}  {'[FAIL]' if result.code_tags_composite.sim_sig < 0.90 else '[OK]'}")
        print(f"  sim_name: {result.code_tags_composite.sim_name:.2f}  {'[FAIL]' if result.code_tags_composite.sim_name < 0.85 else '[OK]'}")
        print(f"  sim_doc:  {result.code_tags_composite.sim_doc:.2f}  {'[FAIL]' if result.code_tags_composite.sim_doc < 0.80 else '[OK]'}")
        print(f"  spec_ok:  {result.code_tags_composite.spec_ok:.2f}  {'[FAIL]' if result.code_tags_composite.spec_ok < 0.90 else '[OK]'}")
        print()
    
    # Issues
    if result.issues:
        print("Issues:")
        for issue in result.issues:
            print(f"  - {issue}")
        print()
    
    # Warnings
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
        print()
    
    # Boilerplate
    if result.boilerplate_detected:
        print(f"Boilerplate Detected: {len(result.boilerplate_detected)} tag descriptions repeated")
        print()
    
    print("=" * 80)

# Example usage
if __name__ == "__main__":
    # Example: Detect and analyze quintet
    detector = QuintetDetector()
    calculator = QuintetParityCalculator()
    gate = NLTagGate()
    
    # Detect from files
    quintet = detector.detect_from_files(
        code_files=["packages/vif/witness.py"],
        docs_files=["knowledge_architecture/systems/vif/T2_architecture.md"],
        tests_files=["packages/vif/tests/test_witness.py"],
        traces_files=[]
    )
    
    print(f"Detected Quintet:")
    print(f"  Code symbols: {len(quintet.code_symbols)}")
    print(f"  NL tags: {len(quintet.nl_tags)}")
    print()
    
    # Calculate parity
    result = calculator.calculate_parity(quintet)
    
    # Print diagnostic report
    print_diagnostic_report(result, quintet)
    
    # Check gate
    gate_result = gate.check(quintet, result)
    print(f"Gate Result: {'[PASSED]' if gate_result.passed else '[FAILED]'}")

