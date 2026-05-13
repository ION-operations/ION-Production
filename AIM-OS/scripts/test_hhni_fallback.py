"""
HHNI Fallback Test v3 — Pre-mock approach
==========================================
Injects a fake embeddings module into sys.modules BEFORE
any HHNI code is imported, so the hanging
'from sentence_transformers import SentenceTransformer' never executes.

Usage:  python scripts/test_hhni_fallback.py
"""

import os, sys, time, types

AIMOS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AIMOS_ROOT)

# ── PRE-MOCK: Create a fake embeddings module BEFORE HHNI is imported ──
fake_emb = types.ModuleType("packages.hhni.embeddings")
fake_emb.encode_text = None          # Force fallback path
fake_emb.encode_texts = None
fake_emb.SentenceTransformer = None
fake_emb.get_model = lambda: None
sys.modules["packages.hhni.embeddings"] = fake_emb
sys.modules["hhni.embeddings"] = fake_emb

print("=" * 60)
print("HHNI FALLBACK-MODE TEST (pre-mock, no torch)")
print("=" * 60)

start = time.monotonic()

# Step 1: Import
print("\n[1/6] Importing HHNI (embeddings pre-mocked)...")
try:
    from packages.hhni import HierarchicalIndex
    from packages.hhni.retrieval import TwoStageRetriever, RetrievalConfig
    print("  OK")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Step 2: Create index
print("[2/6] Creating HierarchicalIndex...")
try:
    index = HierarchicalIndex()
    print("  OK")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Step 3: Load CMC atoms
print("[3/6] Loading CMC atoms...")
try:
    from packages.cmc_service.cmc_store import CMCStore
    store = CMCStore()
    atoms = store.all_atoms()
    print(f"  OK — {len(atoms)} atoms")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Step 4: Index atoms
print("[4/6] Indexing atoms into HHNI...")
indexed = 0
for atom in atoms:
    try:
        content = getattr(atom, 'content', None) or getattr(atom, 'data', '')
        if not content or not isinstance(content, str) or len(content) < 10:
            continue
        atom_id = str(getattr(atom, 'id', None) or getattr(atom, 'atom_id', f'a{indexed}'))
        index.index_document(content=content[:1500], doc_id=atom_id)
        indexed += 1
        if indexed >= 20:  # Quick test with first 20
            break
    except Exception:
        continue
nodes = len(index.nodes) if hasattr(index, 'nodes') else 0
print(f"  OK — {indexed} docs indexed, {nodes} nodes")

# Step 5: Create retriever
print("[5/6] Creating TwoStageRetriever...")
try:
    config = RetrievalConfig(
        token_budget=4000, coarse_k=50,
        min_relevance=0.1, dvns_iterations=20,
    )
    retriever = TwoStageRetriever(hierarchical_index=index, config=config)
    print("  OK")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Step 6: Test query
print("[6/6] Test retrieval query...")
try:
    results = retriever.retrieve("MCP server architecture system")
    count = len(results) if hasattr(results, '__len__') else 0
    print(f"  OK — {count} results")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

elapsed = round((time.monotonic() - start) * 1000, 1)
print(f"\n{'=' * 60}")
print(f"ALL PASSED in {elapsed}ms")
print(f"HHNI works in fallback mode (no torch, no sentence-transformers)")
print(f"Nodes: {nodes} | Query results: {count}")
print(f"\nNEXT: Patch lucid_mcp_server.py to pre-mock embeddings before HHNI init")
print(f"{'=' * 60}")
