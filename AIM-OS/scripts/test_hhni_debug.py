"""Quick debug — find exactly where the hang occurs."""
import sys, types, os, time
sys.path.insert(0, '.')

print("Step 1: Blocking torch and sentence_transformers...", flush=True)
t0 = time.time()

# Block torch and ALL its submodules with a meta_path finder
class TorchBlocker:
    _BLOCKED = ('torch', 'sentence_transformers')
    
    def find_module(self, fullname, path=None):
        for b in self._BLOCKED:
            if fullname == b or fullname.startswith(b + '.'):
                return self
        return None
    
    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = types.ModuleType(fullname)
        mod.__path__ = []
        mod.__loader__ = self
        mod.__spec__ = None
        sys.modules[fullname] = mod
        return mod

sys.meta_path.insert(0, TorchBlocker())
print(f"  Done in {(time.time()-t0)*1000:.0f}ms", flush=True)

print("Step 2: Importing packages.hhni (will trigger __init__.py)...", flush=True)
t1 = time.time()
try:
    import packages.hhni as hhni
    print(f"  Done in {(time.time()-t1)*1000:.0f}ms — {len(dir(hhni))} attrs", flush=True)
except Exception as e:
    print(f"  FAILED in {(time.time()-t1)*1000:.0f}ms: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 3: Creating index...", flush=True)
t2 = time.time()
idx = hhni.HierarchicalIndex()
idx.index_document("Test document about MCP", "doc1")
print(f"  Done in {(time.time()-t2)*1000:.0f}ms — {len(idx.nodes)} nodes", flush=True)

print("Step 4: Creating retriever...", flush=True)
t3 = time.time()
r = hhni.TwoStageRetriever(
    hierarchical_index=idx,
    config=hhni.RetrievalConfig(
        token_budget=2000, coarse_k=10,
        min_relevance=0.1, dvns_iterations=5
    )
)
print(f"  Done in {(time.time()-t3)*1000:.0f}ms", flush=True)

print("Step 5: Test query...", flush=True)
t4 = time.time()
res = r.retrieve("MCP server")
print(f"  Done in {(time.time()-t4)*1000:.0f}ms — {len(res)} results", flush=True)

total = (time.time()-t0)*1000
print(f"\nALL PASSED in {total:.0f}ms total", flush=True)
