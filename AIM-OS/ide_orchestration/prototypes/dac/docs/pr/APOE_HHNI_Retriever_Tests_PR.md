Title: APOE: Add HHNI Retriever Handler Tests (budget, schema, multi-resolution, fallback)

Summary
- Add focused tests validating APOE HHNI retriever handler behavior: budget adherence, schema compliance, adaptive multi‑resolution, and HHNI‑unavailable fallback.
- No runtime changes to handler; tests run under a patched HHNI shim.

Scope
- Files:
  - packages/apoe/tests/test_retriever_role_handler.py (new)
- Validates:
  - Budget propagation and total token cap
  - Output schema keys and metrics
  - Multi‑resolution branch and budget respect
  - HHNI‑unavailable fallback (error + empty context)

Notes
- Green locally (pytest). No dependency on external services.

Links
- Agent board (Alex): ide_orchestration/prototypes/dac/docs/agents/alex/COORDINATION_BOARD.md
- HHNI ref: packages/hhni/*


