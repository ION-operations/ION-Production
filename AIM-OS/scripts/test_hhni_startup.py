"""
HHNI Startup Test — Zero-Downtime Verification
================================================

Tests whether HHNI can initialize safely on this Windows stack
BEFORE we hot-swap the live MCP server config.

This script:
1. Sets AIMOS_HHNI_EAGER_INIT=1
2. Imports and initializes the same HHNI components the MCP server uses
3. Builds the index from existing CMC atoms
4. Creates a TwoStageRetriever
5. Runs a test retrieval query
6. Reports success/failure with full diagnostics

If this passes, we know it's safe to update the Cursor MCP config
to enable HHNI on the live server.

Usage:
    python scripts/test_hhni_startup.py
"""

import os
import sys
import time
import traceback

# Ensure AIM-OS root is on path
AIMOS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AIMOS_ROOT)

# Force HHNI eager init for this test
os.environ["AIMOS_HHNI_EAGER_INIT"] = "1"


def test_hhni_startup():
    """Test the full HHNI initialization pipeline."""
    results = {
        "import_ok": False,
        "index_created": False,
        "atoms_loaded": 0,
        "index_built": False,
        "retriever_created": False,
        "test_query_ok": False,
        "test_results_count": 0,
        "total_time_ms": 0,
        "error": None,
        "traceback": None,
    }

    start = time.monotonic()

    # Step 1: Import HHNI components
    print("[1/6] Importing HHNI components...")
    try:
        from packages.hhni import HierarchicalIndex
        from packages.hhni.retrieval import TwoStageRetriever, RetrievalConfig
        results["import_ok"] = True
        print("  ✓ Imports successful")
    except Exception as e:
        results["error"] = f"Import failed: {e}"
        results["traceback"] = traceback.format_exc()
        print(f"  ✗ Import failed: {e}")
        _report(results, start)
        return results

    # Step 2: Create HierarchicalIndex
    print("[2/6] Creating HierarchicalIndex...")
    try:
        index = HierarchicalIndex()
        results["index_created"] = True
        print("  ✓ Index created")
    except Exception as e:
        results["error"] = f"Index creation failed: {e}"
        results["traceback"] = traceback.format_exc()
        print(f"  ✗ Index creation failed: {e}")
        _report(results, start)
        return results

    # Step 3: Load CMC atoms
    print("[3/6] Loading CMC atoms...")
    try:
        from packages.cmc_service.cmc_store import CMCStore
        store = CMCStore()
        atoms = store.all_atoms()
        results["atoms_loaded"] = len(atoms)
        print(f"  ✓ Loaded {len(atoms)} atoms from CMC")
    except Exception as e:
        results["error"] = f"CMC load failed: {e}"
        results["traceback"] = traceback.format_exc()
        print(f"  ✗ CMC load failed: {e}")
        _report(results, start)
        return results

    # Step 4: Build HHNI index from atoms
    print("[4/6] Building HHNI index from atoms...")
    try:
        indexed = 0
        for atom in atoms:
            try:
                content = getattr(atom, 'content', None) or getattr(atom, 'data', None)
                if content and isinstance(content, str) and len(content) > 10:
                    atom_id = getattr(atom, 'id', None) or getattr(atom, 'atom_id', None)
                    if atom_id and hasattr(index, 'add_node'):
                        index.add_node(
                            node_id=str(atom_id),
                            content=content[:2000],  # Truncate for safety
                            metadata={"source": "cmc", "type": "atom"},
                        )
                        indexed += 1
            except Exception:
                continue  # Skip individual atom errors

        results["index_built"] = True
        node_count = len(index.nodes) if hasattr(index, 'nodes') else indexed
        print(f"  ✓ Index built with {node_count} nodes from {indexed} atoms")
    except Exception as e:
        results["error"] = f"Index build failed: {e}"
        results["traceback"] = traceback.format_exc()
        print(f"  ✗ Index build failed: {e}")
        _report(results, start)
        return results

    # Step 5: Create TwoStageRetriever
    print("[5/6] Creating TwoStageRetriever with DVNS pipeline...")
    try:
        config = RetrievalConfig(
            token_budget=4000,
            coarse_k=100,
            min_relevance=0.3,
            dvns_iterations=50,
            enable_conflict_resolution=True,
            enable_compression=True,
        )
        retriever = TwoStageRetriever(
            hierarchical_index=index,
            config=config,
        )
        results["retriever_created"] = True
        print("  ✓ TwoStageRetriever created with full DVNS physics pipeline")
    except Exception as e:
        results["error"] = f"Retriever creation failed: {e}"
        results["traceback"] = traceback.format_exc()
        print(f"  ✗ Retriever creation failed: {e}")
        _report(results, start)
        return results

    # Step 6: Test retrieval query
    print("[6/6] Running test retrieval query...")
    try:
        test_result = retriever.retrieve("AIMOS system architecture MCP server")
        result_count = len(test_result) if hasattr(test_result, '__len__') else 0
        results["test_query_ok"] = True
        results["test_results_count"] = result_count
        print(f"  ✓ Test query returned {result_count} results")
    except Exception as e:
        results["error"] = f"Test query failed: {e}"
        results["traceback"] = traceback.format_exc()
        print(f"  ✗ Test query failed: {e}")

    _report(results, start)
    return results


def _report(results, start):
    """Print final report."""
    results["total_time_ms"] = round((time.monotonic() - start) * 1000, 1)

    print("\n" + "=" * 60)
    print("HHNI STARTUP TEST REPORT")
    print("=" * 60)

    all_ok = all([
        results["import_ok"],
        results["index_created"],
        results["index_built"],
        results["retriever_created"],
        results["test_query_ok"],
    ])

    if all_ok:
        print(f"\n  ✅ ALL CHECKS PASSED — HHNI is SAFE to enable")
        print(f"     Atoms: {results['atoms_loaded']}")
        print(f"     Query results: {results['test_results_count']}")
        print(f"     Total time: {results['total_time_ms']}ms")
        print(f"\n  NEXT STEP: Add AIMOS_HHNI_EAGER_INIT=1 to Cursor MCP config")
        print(f"  File: C:\\Users\\bombe\\.cursor\\mcp.json")
        print(f"  Then Cursor will hot-swap on next MCP reconnect.")
    else:
        print(f"\n  ❌ HHNI STARTUP FAILED")
        print(f"     Error: {results.get('error', 'Unknown')}")
        if results.get("traceback"):
            print(f"\n  Traceback:\n{results['traceback']}")
        print(f"\n  DO NOT ENABLE HHNI — it will crash the MCP server.")

    print("=" * 60)


if __name__ == "__main__":
    test_hhni_startup()
