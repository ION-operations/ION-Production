# C2-C3 Server Resurrection + System Unification — COMPLETE

**Agent:** FORGE
**Date:** 2026-03-23T21:45:00-04:00
**Phase/Task:** V5 C2 (Server Resurrection) + C3 (System Unification)
**Confidence:** 0.85

## Reasoning

### C2: Server Resurrection
- server.py was importing mock engine from `victus.aether.engine` (57 lines) instead of real AetherEngine at `victus.ion.aether_engine` (457 lines)
- V5 §2 C2 specifies using `create_aether_engine()` factory (line 414) which correctly wires: IonStore → IonIndex → IonGraph → ManifestManager → GeminiAPIClient → GovernedWritePipeline
- Mock used `(llm, compiler, bus)` constructor — completely different interface than real engine `(store, index, graph, manifest, gemini, pipeline)`
- Also removed dead import of `evolution_node` (not needed by new engine path)
- Made `/aether/think` endpoint async since real engine uses `await engine.process()`
- **Decision:** Used `data/.ion` as ion_root (subdirectory of `data_dir`) consistent with the factory's default

### C3: Capsule Unification
- capsule.py was creating capsules with `IonType.EVIDENCE` + `AuthorityClass.A4_SYSTEM` — both wrong per V5 §2 C3
- model.py `create_capsule_ion()` factory (line 756) correctly uses `IonType.CAPSULE` + `AuthorityClass.A5_INFRA`
- Fixed to match canonical factory pattern
- **Mock engine NOT deleted** — file is orphaned (zero imports), leaving for SENTINEL verification before physical removal

## Work Done

### C2 Changes (server.py)

| Line Range | Change |
|------------|--------|
| 13-20 | Removed 6 imports (GovernedWritePipeline, IonIndex, AetherEngine mock, ContextCompiler, MockAdapter, evolution_node). Added `create_aether_engine` import. |
| 36-48 | Replaced manual component construction with `create_aether_engine(ion_root=ion_root)`. Engine factory builds store, index, graph, manifest, gemini, pipeline internally. |
| 67-71 | Made `/aether/think` async. Changed from `engine.think(msg, [])` → `await engine.process(msg)` with proper AetherResponse handling. |

### C3 Changes (capsule.py)

| Line | Change |
|------|--------|
| 8 | Added `CapsulePhase` import |
| 23 | `IonType.EVIDENCE` → `IonType.CAPSULE` |
| 24 | `A4_RUNTIME` → `A5_INFRA` |

### K-Gate Verification

- ✅ server.py syntax validates (`ast.parse` — PASS)
- ✅ `grep -rn "from victus.aether.engine"` returns zero matches — mock engine fully dereferenced
- ✅ capsule.py uses canonical `IonType.CAPSULE` + `A5_INFRA`
- ⚠️ Full server boot test not run (requires FastAPI + all dependencies installed) — SENTINEL should run this

## Files Changed

| File | Action | Lines Changed |
|------|--------|---------------|
| `victus/ion/server.py` | MODIFIED | ~20 lines |
| `victus/ion/capsule.py` | MODIFIED | 3 lines |

## Open Questions

1. **Mock engine deletion:** `victus/aether/engine.py` (57 lines) is orphaned — zero imports. Should be deleted but SENTINEL should verify first.
2. **evolution_node.py:** `victus/aether/evolution_node.py` still exists — may be used by other code. Needs audit.
3. **Full server boot:** Requires `fastapi`, `uvicorn`, `pyyaml` and all victus deps installed. SENTINEL should attempt `uvicorn victus.ion.server:app --host 0.0.0.0 --port 8000`.
4. **LLM path:** Server will run in offline mode without `GOOGLE_API_KEY` set. K-Gate routing (high→Gemini API, low→Ollama) not yet wired — remains for NEXUS scope.

## HANDOFF

[FORGE] → [SENTINEL] HANDOFF
- TASK: Verify C1-C3 changes
- PRIORITY: P0
- FILES: server.py, capsule.py, + 10 C1 enum files
- STATE: All V5 C1-C3 code changes applied
- NEEDS: Full import test, server boot test, mock engine deletion approval

[FORGE] → [NEXUS] HANDOFF
- TASK: J.01 LLM adapter + context convergence
- PRIORITY: P1
- FILES: aether_engine.py, gemini_api.py, llm_adapter.py
- STATE: C1-C3 complete, real engine wired
- NEEDS: Wire K-Gate LLM routing, complete context compiler integration
