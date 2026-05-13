# dAimon — Project Instructions

This project follows the **dAimon Continuity Bridge** for Gemini-native governed inheritance.

## Project Rules
1. **Governed State:** All state changes (code, config, docs) must be classified as `CANDIDATE` and cleared via `dAimon` settlement before becoming inheritable.
2. **MCP Evidence:** Every governed retrieval must be accompanied by an MCP visibility trace (even if simulated via local harness).
3. **Receipt-First:** Do not finalize a task without generating a `dAimon` receipt artifact.
4. **Test Matrix:** Follow the gates in `orchestration/test_matrix.json`.

## Active Domains
- `continuity_substrate`
- `generative_governance`
- `capability_routing`
- `mcp_visibility`
- `enterprise_trust`
- `cloud_runtime`
- `demo_video_agent`

## Execution Loop
- Use `python scripts/validate_scaffold.py` to check baseline.
- Use `python scripts/run_local_demo.py` to test continuity.
- Use `python scripts/run_gemini_handoff_demo.py` for live carrier proof.
