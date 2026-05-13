"""
Comprehensive tests for quintet parity system

Tests all major functionality:
- AST symbol extraction
- Quintet detection
- Composite code↔tags metric
- NL tag gate
- Parity calculation
- Anti-gaming checks
"""

from __future__ import annotations

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from sdfcvf.quintet import (
    ASTSymbolExtractor,
    CodeSymbol,
    Quintet,
    QuintetDetector,
    QuintetParityCalculator,
    QuintetParityResult,
    CompositeScore,
    NLTagGate,
    GateResult,
    print_diagnostic_report
)

# Mock NLTag for testing
class MockNLTag:
    """Mock NL tag for testing without nl_tags package dependency"""
    def __init__(self, id, tag_text, syntax_ref, line_start, file_path, kind="TAG", dependencies=None):
        self.id = id
        self.canonical_id = id
        self.tag_text = tag_text
        self.syntax_ref = syntax_ref
        self.line_start = line_start
        self.file_path = file_path
        self.kind = kind
        self.dependencies = dependencies or []


class TestASTSymbolExtractor:
    """Test AST-based symbol extraction"""
    
    def test_extract_python_function(self, tmp_path):
        """Test extraction of Python function"""
        # Create test file
        test_file = tmp_path / "test_func.py"
        test_file.write_text('''
def hello_world(name: str, age: int) -> str:
    """Greet someone with their name and age"""
    return f"Hello {name}, you are {age} years old"
''')
        
        # Extract symbols
        symbols = ASTSymbolExtractor.extract_python_symbols(str(test_file))
        
        # Verify
        assert len(symbols) == 1
        assert symbols[0].name == "hello_world"
        assert "name" in symbols[0].signature
        assert "age" in symbols[0].signature
        assert symbols[0].docstring == "Greet someone with their name and age"
        assert symbols[0].is_public == True
        assert symbols[0].language == "python"
    
    def test_extract_python_class(self, tmp_path):
        """Test extraction of Python class"""
        test_file = tmp_path / "test_class.py"
        test_file.write_text('''
class Calculator:
    """A simple calculator"""
    
    def add(self, a, b):
        """Add two numbers"""
        return a + b
    
    def _private_helper(self):
        """Internal helper"""
        pass
''')
        
        symbols = ASTSymbolExtractor.extract_python_symbols(str(test_file))
        
        # Should extract class + 2 methods
        assert len(symbols) == 3
        
        # Check class
        class_symbol = [s for s in symbols if s.name == "Calculator"][0]
        assert class_symbol.docstring == "A simple calculator"
        assert class_symbol.is_public == True
        
        # Check public method
        add_symbol = [s for s in symbols if s.name == "add"][0]
        assert add_symbol.is_public == True
        
        # Check private method
        private_symbol = [s for s in symbols if s.name == "_private_helper"][0]
        assert private_symbol.is_public == False
    
    def test_extract_async_function(self, tmp_path):
        """Test extraction of async function"""
        test_file = tmp_path / "test_async.py"
        test_file.write_text('''
async def fetch_data(url: str) -> dict:
    """Fetch data from URL"""
    return {"data": "mock"}
''')
        
        symbols = ASTSymbolExtractor.extract_python_symbols(str(test_file))
        
        assert len(symbols) == 1
        assert symbols[0].name == "fetch_data"
        assert "url" in symbols[0].signature
    
    def test_extract_empty_file(self, tmp_path):
        """Test extraction from empty file"""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")
        
        symbols = ASTSymbolExtractor.extract_python_symbols(str(test_file))
        assert len(symbols) == 0
    
    def test_extract_syntax_error(self, tmp_path):
        """Test extraction from file with syntax error"""
        test_file = tmp_path / "bad_syntax.py"
        test_file.write_text("def broken(\n")
        
        symbols = ASTSymbolExtractor.extract_python_symbols(str(test_file))
        assert len(symbols) == 0  # Should return empty list on error


class TestQuintetDetector:
    """Test quintet detection"""
    
    def test_detect_from_files(self, tmp_path):
        """Test quintet detection from file lists"""
        # Create test files
        code_file = tmp_path / "code.py"
        code_file.write_text('''
# NL_TAG: TEST-001 | Test function | test_func() -> None | []
def test_func():
    """Test function"""
    pass
''')
        
        docs_file = tmp_path / "docs.md"
        docs_file.write_text("# Documentation\nThis is a test.")
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test_test_func(): pass")
        
        # Detect quintet
        detector = QuintetDetector()
        quintet = detector.detect_from_files(
            code_files=[str(code_file)],
            docs_files=[str(docs_file)],
            tests_files=[str(test_file)],
            traces_files=[]
        )
        
        # Verify
        assert len(quintet.code) == 1
        assert len(quintet.docs) == 1
        assert len(quintet.tests) == 1
        assert len(quintet.traces) == 0
        assert len(quintet.code_symbols) == 1
        assert quintet.code_symbols[0].name == "test_func"
    
    def test_detect_with_no_files(self):
        """Test detection with empty file lists"""
        detector = QuintetDetector()
        quintet = detector.detect_from_files(
            code_files=[],
            docs_files=[],
            tests_files=[],
            traces_files=[]
        )
        
        assert len(quintet.code) == 0
        assert len(quintet.docs) == 0
        assert len(quintet.tests) == 0
        assert len(quintet.traces) == 0
        assert len(quintet.code_symbols) == 0


class TestQuintetParityCalculator:
    """Test quintet parity calculation"""
    
    def test_calculate_parity_basic(self):
        """Test basic parity calculation"""
        calculator = QuintetParityCalculator()
        
        # Create minimal quintet
        quintet = Quintet(
            code=["test.py"],
            docs=["test.md"],
            tests=["test_test.py"],
            traces=[],
            nl_tags=[],
            code_symbols=[]
        )
        
        result = calculator.calculate_parity(quintet)
        
        # Verify structure
        assert isinstance(result, QuintetParityResult)
        assert 0.0 <= result.score <= 1.0
        assert len(result.similarities) == 10  # 10 pairwise comparisons
        assert result.is_quintet == True
    
    def test_parity_all_similarities_present(self):
        """Test that all 10 similarities are calculated"""
        calculator = QuintetParityCalculator()
        
        quintet = Quintet(
            code=["test.py"],
            docs=["test.md"],
            tests=["test_test.py"],
            traces=["trace.json"],
            nl_tags=[],
            code_symbols=[]
        )
        
        result = calculator.calculate_parity(quintet)
        
        # Check all 10 pairs exist
        expected_pairs = [
            "code_docs", "code_tests", "code_traces", "code_tags",
            "docs_tests", "docs_traces", "docs_tags",
            "tests_traces", "tests_tags",
            "traces_tags"
        ]
        
        for pair in expected_pairs:
            assert pair in result.similarities
            assert isinstance(result.similarities[pair], float)
    
    def test_composite_code_tags_metric(self):
        """Test composite code↔tags metric calculation"""
        calculator = QuintetParityCalculator()
        
        # Create code symbols
        symbols = [
            CodeSymbol(
                name="test_func",
                signature="test_func(arg1, arg2)",
                line_number=10,
                file_path="test.py",
                docstring="Test function",
                is_public=True
            )
        ]
        
        # Create matching tags
        tags = [
            MockNLTag(
                id="TEST-001",
                tag_text="Test function",
                syntax_ref="test_func(arg1, arg2)",
                line_start=9,
                file_path="test.py"
            )
        ]
        
        composite = calculator._calculate_composite_code_tags(symbols, tags)
        
        # Verify structure
        assert isinstance(composite, CompositeScore)
        assert 0.0 <= composite.composite <= 1.0
        assert 0.0 <= composite.sim_sig <= 1.0
        assert 0.0 <= composite.sim_name <= 1.0
        assert 0.0 <= composite.sim_doc <= 1.0
        assert 0.0 <= composite.spec_ok <= 1.0
    
    def test_signature_similarity_exact_match(self):
        """Test signature similarity with exact match"""
        calculator = QuintetParityCalculator()
        
        symbols = [
            CodeSymbol(
                name="func",
                signature="func(a, b, c)",
                line_number=10,
                file_path="test.py"
            )
        ]
        
        tags = [
            MockNLTag(
                id="TEST-001",
                tag_text="Test",
                syntax_ref="func(a, b, c)",
                line_start=9,
                file_path="test.py"
            )
        ]
        
        sim = calculator._signature_similarity(symbols, tags)
        
        # Exact match should be high (Jaccard ~ 1.0)
        assert sim > 0.9
    
    def test_signature_similarity_no_match(self):
        """Test signature similarity with no match"""
        calculator = QuintetParityCalculator()
        
        symbols = [
            CodeSymbol(
                name="func",
                signature="func(a, b, c)",
                line_number=10,
                file_path="test.py"
            )
        ]
        
        tags = [
            MockNLTag(
                id="TEST-001",
                tag_text="Test",
                syntax_ref="completely_different(x, y, z)",
                line_start=9,
                file_path="test.py"
            )
        ]
        
        sim = calculator._signature_similarity(symbols, tags)
        
        # No match should be low
        assert sim < 0.5
    
    def test_boilerplate_detection(self):
        """Test boilerplate tag detection"""
        calculator = QuintetParityCalculator()
        
        # Create tags with repeated descriptions
        tags = [
            MockNLTag(id=f"TEST-{i:03d}", tag_text="Generic function", syntax_ref="", line_start=i, file_path="test.py")
            for i in range(10)  # 10 identical descriptions
        ]
        
        boilerplate = calculator._detect_boilerplate(tags)
        
        # Should detect "Generic function" as boilerplate (> 5 repetitions)
        assert len(boilerplate) > 0
        assert any("Generic function" in b for b in boilerplate)
    
    def test_embedding_cache(self):
        """Test embedding caching works"""
        calculator = QuintetParityCalculator()
        
        content = "test content for caching"
        
        # First call - compute
        emb1 = calculator._get_or_compute_embedding(content, "test")
        
        # Second call - should use cache
        emb2 = calculator._get_or_compute_embedding(content, "test")
        
        # Should be identical (from cache)
        assert (emb1 == emb2).all()
        
        # Different content should give different embedding
        emb3 = calculator._get_or_compute_embedding("different content", "test2")
        assert not (emb1 == emb3).all()


class TestNLTagGate:
    """Test NL tag gate enforcement"""
    
    def test_check_coverage_pass(self):
        """Test gate passes with good coverage"""
        gate = NLTagGate(
            public_coverage_threshold=0.90,
            internal_coverage_threshold=0.70
        )
        
        # Create quintet with good coverage
        symbols = [
            CodeSymbol("func1", "func1()", 10, "test.py", is_public=True),
            CodeSymbol("func2", "func2()", 20, "test.py", is_public=True),
        ]
        
        tags = [
            MockNLTag("TEST-001", "Func 1", "func1()", 9, "test.py"),
            MockNLTag("TEST-002", "Func 2", "func2()", 19, "test.py"),
        ]
        
        quintet = Quintet(
            code=["test.py"],
            docs=[],
            tests=[],
            traces=[],
            nl_tags=tags,
            code_symbols=symbols
        )
        
        parity_result = QuintetParityResult(
            score=0.95,
            similarities={},
            code_tags_composite=CompositeScore(0.90, 0.90, 0.85, 0.80, 1.0)
        )
        
        result = gate.check(quintet, parity_result)
        
        assert result.passed == True
        assert len(result.issues) == 0
    
    def test_check_coverage_fail_public(self):
        """Test gate fails with low public coverage"""
        gate = NLTagGate(public_coverage_threshold=0.95)
        
        # 2 public functions, only 1 tagged = 50% coverage
        symbols = [
            CodeSymbol("func1", "func1()", 10, "test.py", is_public=True),
            CodeSymbol("func2", "func2()", 20, "test.py", is_public=True),
        ]
        
        tags = [
            MockNLTag("TEST-001", "Func 1", "func1()", 9, "test.py"),
        ]
        
        quintet = Quintet(
            code=["test.py"],
            docs=[],
            tests=[],
            traces=[],
            nl_tags=tags,
            code_symbols=symbols
        )
        
        parity_result = QuintetParityResult(
            score=0.95,
            similarities={},
            code_tags_composite=CompositeScore(0.90, 0.90, 0.85, 0.80, 1.0)
        )
        
        result = gate.check(quintet, parity_result)
        
        assert result.passed == False
        assert any("Public API coverage" in issue for issue in result.issues)
    
    def test_check_composite_alignment_fail(self):
        """Test gate fails with low composite score"""
        gate = NLTagGate(code_tags_threshold=0.85)
        
        quintet = Quintet(
            code=["test.py"],
            docs=[],
            tests=[],
            traces=[],
            nl_tags=[],
            code_symbols=[]
        )
        
        # Low composite score
        parity_result = QuintetParityResult(
            score=0.95,
            similarities={},
            code_tags_composite=CompositeScore(0.60, 0.50, 0.60, 0.70, 1.0)  # Below threshold
        )
        
        result = gate.check(quintet, parity_result)
        
        assert result.passed == False
        assert any("Code-tags alignment" in issue for issue in result.issues)
    
    def test_check_duplicate_ids(self):
        """Test duplicate canonical ID detection"""
        gate = NLTagGate()
        
        # Create tags with duplicate IDs
        tags = [
            MockNLTag("TEST-001", "First", "func1()", 10, "file1.py"),
            MockNLTag("TEST-001", "Second", "func2()", 20, "file2.py"),  # Duplicate ID!
        ]
        
        quintet = Quintet(
            code=["test.py"],
            docs=[],
            tests=[],
            traces=[],
            nl_tags=tags,
            code_symbols=[]
        )
        
        parity_result = QuintetParityResult(
            score=0.95,
            similarities={},
            code_tags_composite=CompositeScore(0.90, 0.90, 0.85, 0.80, 1.0)
        )
        
        result = gate.check(quintet, parity_result)
        
        assert result.passed == False
        assert any("Duplicate ID" in issue for issue in result.issues)
    
    def test_check_boilerplate_warning(self):
        """Test boilerplate detection adds warning"""
        gate = NLTagGate()
        
        quintet = Quintet(
            code=["test.py"],
            docs=[],
            tests=[],
            traces=[],
            nl_tags=[],
            code_symbols=[]
        )
        
        # Parity result with boilerplate detected
        parity_result = QuintetParityResult(
            score=0.95,
            similarities={},
            code_tags_composite=CompositeScore(0.90, 0.90, 0.85, 0.80, 1.0),
            boilerplate_detected=["Generic description", "Another generic"]
        )
        
        result = gate.check(quintet, parity_result)
        
        # Should pass but with warnings
        assert len(result.warnings) > 0
        assert any("Boilerplate" in warning for warning in result.warnings)


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_end_to_end_workflow(self, tmp_path):
        """Test complete workflow: detect → calculate → gate"""
        # Create test code file with tags
        code_file = tmp_path / "example.py"
        code_file.write_text('''
# NL_TAG: EX-001 | Add two numbers | add(a, b) -> int | []
def add(a, b):
    """Add two numbers together"""
    return a + b

# NL_TAG: EX-002 | Subtract two numbers | subtract(a, b) -> int | []
def subtract(a, b):
    """Subtract b from a"""
    return a - b
''')
        
        # Detect quintet
        detector = QuintetDetector()
        quintet = detector.detect_from_files(
            code_files=[str(code_file)],
            docs_files=[],
            tests_files=[],
            traces_files=[]
        )
        
        # Verify detection
        assert len(quintet.code_symbols) == 2
        assert quintet.code_symbols[0].name == "add"
        assert quintet.code_symbols[1].name == "subtract"
        
        # Calculate parity
        calculator = QuintetParityCalculator()
        parity_result = calculator.calculate_parity(quintet)
        
        # Verify parity
        assert isinstance(parity_result, QuintetParityResult)
        assert len(parity_result.similarities) == 10
        
        # Check gate
        gate = NLTagGate()
        gate_result = gate.check(quintet, parity_result)
        
        # Verify gate result
        assert isinstance(gate_result, GateResult)
        assert gate_result.gate_name == "nl_tags"


class TestDiagnosticReporting:
    """Test diagnostic report generation"""
    
    def test_print_diagnostic_report(self, capsys):
        """Test diagnostic report prints correctly"""
        result = QuintetParityResult(
            score=0.87,
            similarities={
                "code_docs": 0.90,
                "code_tests": 0.85,
                "code_traces": 0.80,
                "code_tags": 0.88,
                "docs_tests": 0.92,
                "docs_traces": 0.86,
                "docs_tags": 0.89,
                "tests_traces": 0.84,
                "tests_tags": 0.87,
                "traces_tags": 0.85
            },
            code_tags_composite=CompositeScore(0.88, 0.90, 0.85, 0.82, 1.0),
            issues=["Test issue"],
            warnings=["Test warning"],
            boilerplate_detected=["Generic description"]
        )
        
        quintet = Quintet(code=[], docs=[], tests=[], traces=[], nl_tags=[])
        
        # Print report
        print_diagnostic_report(result, quintet)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify output contains key sections
        assert "Quintet Parity Analysis Report" in captured.out
        assert "code_tags" in captured.out
        assert "P_quintet = 0.870" in captured.out
        assert "code <-> tags Breakdown" in captured.out
        assert "Issues:" in captured.out
        assert "Test issue" in captured.out
        assert "Warnings:" in captured.out
        assert "Test warning" in captured.out
        assert "Boilerplate Detected" in captured.out


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

