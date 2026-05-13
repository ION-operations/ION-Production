[CODEX -> OPUS] HANDOFF
- TASK: Structured last-message capture subsystem
- PRIORITY: P1
- FILES: `packages/jarvis_injector/src/jarvis_injector/capture/`, `packages/jarvis_injector/src/jarvis_injector/api/routes_capture.py`, `packages/joc/src/types/windowCapture.ts`
- STATE: Landed and smoke-tested with DOM snapshot input. Output preserves paragraphs, code blocks, and tool-call blocks as structured AST plus plaintext/markdown renderings.
- NEEDS: When you want cockpit UI wiring, the next reasonable move is a capture inspector panel in JOC that renders block tree + markdown + plaintext side by side.
