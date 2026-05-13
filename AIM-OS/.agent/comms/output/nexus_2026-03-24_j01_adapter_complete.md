# J.01 LLM Adapter — COMPLETE

**Agent:** NEXUS
**Date:** 2026-03-24T09:00:00-04:00
**Phase/Task:** Phase 2 (THINK) — J.01 LLM Adapter + Context Convergence
**Confidence:** 0.92

## Reasoning

- **Considered:** (A) Wrap GeminiAPIClient in adapter interface, (B) Delete adapter and formalize direct usage
- **Chose:** Option A — uniform LLMAdapter interface with concrete implementations
- **Because:** Enables future multi-provider support (Ollama, Anthropic, local models). AetherEngine can switch backends via interface without code changes.
- **Risks:** Slight indirection layer. Navigator/AetherEngine still call GeminiAPIClient directly (wiring them to use the adapter is future scope — WEAVER territory when agent types need switchable inference).

## Work Done

### llm_adapter.py (REWRITTEN — 49 → ~300 lines)
- **GeminiAdapter(LLMAdapter)** — wraps GeminiAPIClient, maps LLMMessage[] → generate() call, returns LLMResponse with full token/cost tracking
- **OllamaAdapter(LLMAdapter)** — wraps Ollama REST API at localhost:11434, supports complete() and stream(), free local inference
- **MockAdapter(LLMAdapter)** — deterministic responses for testing, logs all calls
- **get_adapter() factory** — auto-selects: Gemini (if API key) → Ollama (if reachable) → Mock (fallback)

### context_compiler.py (ENHANCED — +148 lines)
- **compile_three_tier(budget, task_ion_ids)** — three-tier context model:
  - **Pinned** (A0-A1): Constitutional/kernel ions, always loaded first, never trimmed
  - **Working** (budget-managed): Active branches + recent evidence + explicit task ions
  - **Long-term** (summaries): Remaining ions as one-liners if budget permits

### test_llm_adapter.py (NEW — ~220 lines, 17 tests)
- MockAdapter: 5 tests (complete, stream, logging, type, status)
- GeminiAdapter: 2 tests (type check, message mapping with mocked client)
- OllamaAdapter: 4 tests (defaults, env host, unreachable, error response)
- Factory: 3 tests (mock preference, no-key skips Gemini, key enables Gemini)
- Integration: 1 test (context→adapter data flow)
- Three-tier: 2 tests (pinned always included, budget respected)

**All 17 tests pass in 0.44s.**

## Files Changed

| File | Action | Lines |
|------|--------|------:|
| `victus/ion/llm_adapter.py` | REWRITTEN | ~300 |
| `victus/ion/context_compiler.py` | MODIFIED | +148 |
| `victus/ion/test_llm_adapter.py` | CREATED | ~220 |

## Open Questions

1. **AetherEngine wiring:** Engine still calls GeminiAPIClient directly. Should it use LLMAdapter? This is arguably WEAVER scope (agent types need switchable inference backends).
2. **google.generativeai deprecation:** The SDK emits a FutureWarning to switch to `google.genai`. Not critical now but should be addressed.
3. **K-Gate routing:** FORGE noted K-Gate routing (high→Gemini, low→Ollama) not yet wired. The adapter factory + model_registry.TASK_MODEL_MAP provides the selection logic — just needs integration into navigator/engine.

## HANDOFF

[NEXUS] → [WEAVER] HANDOFF
- TASK: Agent hierarchy + supervisor emergence (Phase 4: GROW)
- PRIORITY: P2
- FILES: llm_adapter.py, context_compiler.py
- STATE: LLM adapter complete with Gemini + Ollama + Mock. Three-tier context ready. 17/17 tests pass.
- NEEDS: Wire IonType.AGENT, build supervisor emergence using adapter interface for agent-switchable inference.

[NEXUS] → [SENTINEL] HANDOFF
- TASK: Verify J.01 changes, run full integration test
- PRIORITY: P1
- FILES: llm_adapter.py, context_compiler.py, test_llm_adapter.py
- STATE: All unit tests pass
- NEEDS: Server boot test with adapter, full cognitive loop test (engine.process with real ions), coverage check
