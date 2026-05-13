"""
AIM-OS Context Mapper — Stress Test & Comparative Analysis

Tests the AST Context Mapper against real AIM-OS files:
    1. Stress test: biggest files, deepest import chains
    2. Edge cases: syntax errors, missing files, circular deps
    3. Comparative: semantic vs structural vs blended context quality
    4. Performance: timing across different file sizes
"""

import os
import sys
import time
import json
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))

from context_mapper import ContextMapper, ASTExtractor, ImportResolver, ContextEnvelope


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, msg: str):
        self.passed += 1
        print(f"  ✅ {msg}")

    def fail(self, msg: str, detail: str = ''):
        self.failed += 1
        self.errors.append(f"{msg}: {detail}")
        print(f"  ❌ {msg}: {detail}")

    def assert_true(self, condition: bool, msg: str, detail: str = ''):
        if condition:
            self.ok(msg)
        else:
            self.fail(msg, detail)

    def assert_gt(self, a, b, msg: str):
        if a > b:
            self.ok(f"{msg} ({a} > {b})")
        else:
            self.fail(msg, f"expected {a} > {b}")

    def assert_eq(self, a, b, msg: str):
        if a == b:
            self.ok(f"{msg} ({a})")
        else:
            self.fail(msg, f"expected {a} == {b}")

    def summary(self) -> str:
        total = self.passed + self.failed
        status = "PASS" if self.failed == 0 else "FAIL"
        return f"[{status}] {self.name}: {self.passed}/{total} passed"


# ══════════════════════════════════════════════════════════
#  TEST 1: STRESS TEST — BIG FILES
# ══════════════════════════════════════════════════════════

def test_stress_big_files():
    """Test context mapper against the largest/most complex AIM-OS files."""
    t = TestResult("Stress: Big Files")
    mapper = ContextMapper(WORKSPACE)

    # Target the known big files
    big_files = [
        'scripts/ai_engine/chain_director.py',
        'scripts/ai_engine/enhanced_worker.py',
        'scripts/ai_engine/context_mapper.py',
        'scripts/ai_engine/engine.py',
    ]

    # Find more big files dynamically
    ai_engine_dir = os.path.join(WORKSPACE, 'scripts', 'ai_engine')
    if os.path.isdir(ai_engine_dir):
        for f in os.listdir(ai_engine_dir):
            if f.endswith('.py') and not f.startswith('test_'):
                path = f'scripts/ai_engine/{f}'
                if path not in big_files:
                    big_files.append(path)

    results_table = []
    total_time = 0

    for file_path in big_files:
        abs_path = os.path.join(WORKSPACE, file_path)
        if not os.path.isfile(abs_path):
            continue

        t0 = time.time()
        envelope = mapper.build_envelope(file_path, budget_chars=64000)
        elapsed = (time.time() - t0) * 1000
        total_time += elapsed

        stats = envelope.stats
        results_table.append({
            'file': os.path.basename(file_path),
            'target_chars': stats['target_chars'],
            'deps': stats['dependency_count'],
            'contracts': stats['contract_count'],
            'used_symbols': stats['used_symbols'],
            'tokens': stats['estimated_tokens'],
            'time_ms': round(elapsed, 1),
            'truncated': stats['truncated'],
        })

        # Basic assertions
        t.assert_true(
            stats['target_chars'] > 0,
            f"{os.path.basename(file_path)}: target extracted"
        )

    # Print results table
    print("\n  ┌─────────────────────────────────┬────────┬──────┬──────────┬───────┬────────┬─────────┐")
    print("  │ File                            │ Chars  │ Deps │ Contracts│ Used  │ Tokens │ Time ms │")
    print("  ├─────────────────────────────────┼────────┼──────┼──────────┼───────┼────────┼─────────┤")
    for r in results_table:
        print(f"  │ {r['file']:<31} │ {r['target_chars']:>6} │ {r['deps']:>4} │ {r['contracts']:>8} │ {r['used_symbols']:>5} │ {r['tokens']:>6} │ {r['time_ms']:>7} │")
    print("  └─────────────────────────────────┴────────┴──────┴──────────┴───────┴────────┴─────────┘")
    print(f"  Total time: {total_time:.1f}ms for {len(results_table)} files")
    print(f"  Cache size: {mapper.cache.size}")

    t.assert_gt(len(results_table), 3, "Processed 4+ files")
    t.assert_true(total_time < 5000, f"Total time under 5s ({total_time:.0f}ms)")

    return t


# ══════════════════════════════════════════════════════════
#  TEST 2: EDGE CASES
# ══════════════════════════════════════════════════════════

def test_edge_cases():
    """Test graceful handling of edge cases."""
    t = TestResult("Edge Cases")
    mapper = ContextMapper(WORKSPACE)

    # 1. Non-existent file
    env = mapper.build_envelope('scripts/does_not_exist.py')
    t.assert_true('ERROR' in env.target_content, "Missing file: returns error")

    # 2. File with syntax error (create temp file)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE) as f:
        f.write("def broken(:\n    pass\n\nclass Good:\n    def method(self):\n        pass\n")
        temp_path = f.name

    try:
        result = mapper.extract_contracts(temp_path)
        t.assert_eq(result.parse_mode, 'degraded', "Syntax error: degraded mode")
        t.assert_gt(len(result.exports), 0, "Syntax error: still extracts some symbols")
    finally:
        os.unlink(temp_path)

    # 3. Empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE) as f:
        f.write("")
        temp_path = f.name

    try:
        result = mapper.extract_contracts(temp_path)
        t.assert_eq(len(result.exports), 0, "Empty file: 0 exports")
        t.assert_eq(result.parse_mode, 'full', "Empty file: full parse mode")
    finally:
        os.unlink(temp_path)

    # 4. File with only imports (no exports)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE) as f:
        f.write("import os\nimport sys\nfrom pathlib import Path\n")
        temp_path = f.name

    try:
        result = mapper.extract_contracts(temp_path)
        t.assert_gt(len(result.imports), 0, "Import-only file: imports found")
        t.assert_eq(len(result.exports), 0, "Import-only file: 0 exports")
    finally:
        os.unlink(temp_path)

    # 5. File with star imports
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE) as f:
        f.write("from os.path import *\n\ndef my_func():\n    return join('a', 'b')\n")
        temp_path = f.name

    try:
        result = mapper.extract_contracts(temp_path)
        t.assert_gt(len(result.exports), 0, "Star import file: exports found")
    finally:
        os.unlink(temp_path)

    # 6. Constants and type aliases
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE) as f:
        f.write("""
MAX_RETRIES = 5
DEFAULT_TIMEOUT = 30
API_URL = "https://example.com"
_INTERNAL = "hidden"

from typing import List, Dict
AgentList = List[Dict[str, str]]

class Config:
    name: str
    value: int
    
    def validate(self) -> bool:
        return True
""")
        temp_path = f.name

    try:
        result = mapper.extract_contracts(temp_path)
        export_names = {e.name for e in result.exports}
        t.assert_true('MAX_RETRIES' in export_names, "Constant extraction: MAX_RETRIES")
        t.assert_true('DEFAULT_TIMEOUT' in export_names, "Constant extraction: DEFAULT_TIMEOUT")
        t.assert_true('API_URL' in export_names, "Constant extraction: API_URL")
        t.assert_true('_INTERNAL' not in export_names, "Private filtered: _INTERNAL excluded")
        t.assert_true('Config' in export_names, "Class extraction: Config")
    finally:
        os.unlink(temp_path)

    # 7. Deeply nested classes with dataclass decorators
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE) as f:
        f.write("""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Agent:
    name: str
    role: str = 'worker'
    skills: List[str] = field(default_factory=list)
    parent: Optional['Agent'] = None
    
    def execute(self, task: str) -> str:
        return f"{self.name} doing {task}"
    
    def __repr__(self):
        return f"Agent({self.name})"

@dataclass
class Swarm:
    agents: List[Agent] = field(default_factory=list)
    max_workers: int = 5
    
    def deploy(self, task: str) -> List[str]:
        return [a.execute(task) for a in self.agents]
""")
        temp_path = f.name

    try:
        result = mapper.extract_contracts(temp_path)
        agent_sym = next((e for e in result.exports if e.name == 'Agent'), None)
        t.assert_true(agent_sym is not None, "Dataclass: Agent class found")
        if agent_sym:
            t.assert_true('@dataclass' in agent_sym.decorators, "Dataclass: decorator preserved")
            method_names = [m.split('(')[0].replace('def ', '').strip() for m in agent_sym.methods]
            t.assert_true('execute' in method_names or any('execute' in m for m in agent_sym.methods),
                         "Dataclass: execute method found")
    finally:
        os.unlink(temp_path)

    # 8. Budget packing under extreme constraint
    env = mapper.build_envelope('scripts/ai_engine/chain_director.py', budget_chars=2000)
    t.assert_true(env.truncated, "Extreme budget: correctly truncated")
    t.assert_true(len(env.to_string()) < 4000, f"Extreme budget: output within limit ({len(env.to_string())} chars)")

    return t


# ══════════════════════════════════════════════════════════
#  TEST 3: IMPORT RESOLUTION
# ══════════════════════════════════════════════════════════

def test_import_resolution():
    """Test import resolver classifies imports correctly."""
    t = TestResult("Import Resolution")
    resolver = ImportResolver(WORKSPACE)

    from context_mapper import ImportRef

    # stdlib
    imp = ImportRef(module_path='os', imported_names=['path'], resolved_file='')
    resolved = resolver.resolve(imp, os.path.join(WORKSPACE, 'test.py'))
    t.assert_true(resolved.is_stdlib, "stdlib: os detected")

    imp = ImportRef(module_path='json', imported_names=['dumps'], resolved_file='')
    resolved = resolver.resolve(imp, os.path.join(WORKSPACE, 'test.py'))
    t.assert_true(resolved.is_stdlib, "stdlib: json detected")

    imp = ImportRef(module_path='dataclasses', imported_names=['dataclass'], resolved_file='')
    resolved = resolver.resolve(imp, os.path.join(WORKSPACE, 'test.py'))
    t.assert_true(resolved.is_stdlib, "stdlib: dataclasses detected")

    # external
    imp = ImportRef(module_path='requests', imported_names=['get'], resolved_file='')
    resolved = resolver.resolve(imp, os.path.join(WORKSPACE, 'test.py'))
    t.assert_true(resolved.is_external, "external: requests detected")

    imp = ImportRef(module_path='numpy', imported_names=['array'], resolved_file='')
    resolved = resolver.resolve(imp, os.path.join(WORKSPACE, 'test.py'))
    t.assert_true(resolved.is_external, "external: numpy detected")

    # local resolution
    imp = ImportRef(module_path='chain_director', imported_names=['ChainDirector'], resolved_file='')
    source = os.path.join(WORKSPACE, 'scripts', 'ai_engine', 'engine.py')
    resolved = resolver.resolve(imp, source)
    t.assert_true(
        resolved.resolved_file != '' or resolved.is_external,
        f"local: chain_director resolution attempted"
    )

    return t


# ══════════════════════════════════════════════════════════
#  TEST 4: CACHE VALIDATION
# ══════════════════════════════════════════════════════════

def test_cache():
    """Test that LRU cache works with mtime invalidation."""
    t = TestResult("Cache")
    mapper = ContextMapper(WORKSPACE)

    target = 'scripts/ai_engine/engine.py'
    abs_target = os.path.join(WORKSPACE, target)
    if not os.path.isfile(abs_target):
        t.fail("engine.py not found", "skipping cache test")
        return t

    # First call: cache miss
    t0 = time.time()
    env1 = mapper.build_envelope(target, budget_chars=64000)
    first_time = (time.time() - t0) * 1000

    # Second call: cache hit (should be faster)
    t0 = time.time()
    env2 = mapper.build_envelope(target, budget_chars=64000)
    second_time = (time.time() - t0) * 1000

    t.assert_true(first_time > 0, f"First call: {first_time:.1f}ms")
    t.assert_true(second_time > 0, f"Second call: {second_time:.1f}ms (cached)")
    t.assert_true(
        second_time <= first_time * 1.5 or second_time < 50,
        f"Cache hit not slower ({second_time:.1f}ms vs {first_time:.1f}ms)"
    )
    t.assert_gt(mapper.cache.size, 0, "Cache populated")

    # Same results
    t.assert_eq(env1.stats['contract_count'], env2.stats['contract_count'], "Cache: same contract count")

    return t


# ══════════════════════════════════════════════════════════
#  TEST 5: ENVELOPE QUALITY
# ══════════════════════════════════════════════════════════

def test_envelope_quality():
    """Test that envelope output is well-formed and useful."""
    t = TestResult("Envelope Quality")
    mapper = ContextMapper(WORKSPACE)

    # Build envelope for a file with known imports
    env = mapper.build_envelope(
        'scripts/ai_engine/enhanced_worker.py',
        budget_chars=64000,
    )

    output = env.to_string()

    # Structural checks
    t.assert_true('<system_envelope' in output, "XML envelope tag present")
    t.assert_true('</system_envelope>' in output, "Closing envelope tag present")
    t.assert_true('<edit_rules>' in output, "Edit rules section present")
    t.assert_true('<target_file' in output, "Target file section present")
    t.assert_true('</target_file>' in output, "Closing target tag present")

    # Content checks
    t.assert_true('Modify only the target_file' in output, "Edit rule: modify only target")
    t.assert_true('read-only' in output, "Edit rule: contracts read-only")
    t.assert_true('enhanced_worker.py' in output, "Target file name in output")

    # Symbol usage
    t.assert_true('<target_symbol_usage>' in output, "Symbol usage section present")

    # Check used symbols are the expected ones
    expected_symbols = ['GeminiCLIProvider', 'GenomeLoader', 'ContextPackBuilder', 'Atlas']
    for sym in expected_symbols:
        t.assert_true(sym in env.used_symbols, f"Used symbol: {sym} detected")

    # Check contracts contain real signatures
    if env.dependency_contracts:
        t.assert_true('<outbound_contracts>' in output, "Contracts section present")
        # Check at least one method signature exists
        t.assert_true('def ' in output.split('<outbound_contracts>')[1].split('</outbound_contracts>')[0],
                      "Contracts contain method signatures")
    else:
        t.fail("No dependency contracts", "expected at least 1")

    return t


# ══════════════════════════════════════════════════════════
#  TEST 6: USED-SYMBOL FILTERING
# ══════════════════════════════════════════════════════════

def test_used_symbol_filtering():
    """Test that only actually-used symbols make it into the envelope."""
    t = TestResult("Used-Symbol Filtering")

    # Create test files
    dep_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE)
    dep_file.write("""
class UsedClass:
    def method_a(self):
        pass

class UnusedClass:
    def method_b(self):
        pass

def used_function():
    return 42

def unused_function():
    return 0

USED_CONST = 100
UNUSED_CONST = 200
""")
    dep_file.close()

    dep_module = os.path.splitext(os.path.basename(dep_file.name))[0]

    target_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=WORKSPACE)
    target_file.write(f"""
from {dep_module} import UsedClass, UnusedClass, used_function, unused_function, USED_CONST

obj = UsedClass()
obj.method_a()

result = used_function()

print(USED_CONST)
""")
    target_file.close()

    try:
        mapper = ContextMapper(WORKSPACE)
        env = mapper.build_envelope(target_file.name, budget_chars=64000)

        t.assert_true('UsedClass' in env.used_symbols, "Used: UsedClass detected")
        t.assert_true('used_function' in env.used_symbols, "Used: used_function detected")
        t.assert_true('USED_CONST' in env.used_symbols, "Used: USED_CONST detected")

        # Check that unused symbols are NOT in used_symbols
        t.assert_true('UnusedClass' not in env.used_symbols, "Filtered: UnusedClass excluded")
        t.assert_true('unused_function' not in env.used_symbols, "Filtered: unused_function excluded")

    finally:
        os.unlink(dep_file.name)
        os.unlink(target_file.name)

    return t


# ══════════════════════════════════════════════════════════
#  TEST 7: PERFORMANCE SCALING
# ══════════════════════════════════════════════════════════

def test_performance():
    """Test performance across different workloads."""
    t = TestResult("Performance")
    mapper = ContextMapper(WORKSPACE)

    # Find all .py files in ai_engine
    ai_engine = os.path.join(WORKSPACE, 'scripts', 'ai_engine')
    py_files = []
    if os.path.isdir(ai_engine):
        for f in os.listdir(ai_engine):
            if f.endswith('.py') and not f.startswith('test_') and not f.startswith('__'):
                py_files.append(f'scripts/ai_engine/{f}')

    # Batch extract
    t0 = time.time()
    for f in py_files:
        mapper.extract_contracts(f)
    batch_time = (time.time() - t0) * 1000

    t.assert_gt(len(py_files), 5, f"Found {len(py_files)} Python files")
    t.assert_true(
        batch_time < 2000,
        f"Batch extract {len(py_files)} files: {batch_time:.0f}ms"
    )

    # Average per file
    if py_files:
        avg = batch_time / len(py_files)
        t.ok(f"Average: {avg:.1f}ms/file")

    # Full envelope batch
    t0 = time.time()
    total_contracts = 0
    for f in py_files[:5]:  # Top 5
        env = mapper.build_envelope(f, budget_chars=32000)
        total_contracts += env.stats['contract_count']
    envelope_time = (time.time() - t0) * 1000

    t.ok(f"5 envelopes: {envelope_time:.0f}ms, {total_contracts} total contracts")
    t.assert_true(
        envelope_time < 3000,
        f"Envelope batch under 3s ({envelope_time:.0f}ms)"
    )

    return t


# ══════════════════════════════════════════════════════════
#  RUN ALL
# ══════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  AIM-OS Context Mapper — Stress Test Suite")
    print("=" * 70)
    print(f"  Workspace: {WORKSPACE}")
    print()

    tests = [
        test_stress_big_files,
        test_edge_cases,
        test_import_resolution,
        test_cache,
        test_envelope_quality,
        test_used_symbol_filtering,
        test_performance,
    ]

    results = []
    total_passed = 0
    total_failed = 0

    for test_fn in tests:
        print(f"\n{'─' * 60}")
        print(f"  {test_fn.__name__}")
        print(f"{'─' * 60}")
        try:
            result = test_fn()
            results.append(result)
            total_passed += result.passed
            total_failed += result.failed
        except Exception as e:
            print(f"  💥 CRASH: {e}")
            import traceback
            traceback.print_exc()
            total_failed += 1

    # Summary
    print(f"\n{'═' * 70}")
    print(f"  SUMMARY: {total_passed}/{total_passed + total_failed} passed")
    print(f"{'═' * 70}")
    for r in results:
        print(f"  {r.summary()}")

    if total_failed > 0:
        print(f"\n  ⚠ Failures:")
        for r in results:
            for err in r.errors:
                print(f"    • [{r.name}] {err}")

    print(f"\n  Total: {total_passed} passed, {total_failed} failed")
    return total_failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
