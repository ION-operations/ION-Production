# JARVIS Injector Runtime

Local Windows computer-action runtime for AIM-OS.

Phase A scope in this scaffold:

- target registry loading
- local API surface
- in-memory execution queue
- deterministic window resolution / restore / activation
- keyboard adapter path
- artifact vault layout and execution logging
- structured response capture via `/api/capture/last-message` for DOM, UIA, or plaintext snapshots

Current verification note:

- sample targets only use infrastructure-level verification (`window_visible`, `window_active`)
- production target verification still needs CDP/UIA/visual outcome signals before this runtime should be trusted for autonomous send flows

Current capture note:

- the capture engine already preserves paragraphs, headings, lists, code blocks, tables, and tool-call/result blocks
- live DOM/UIA acquisition from running targets is not implemented yet; current route expects supplied snapshots or plaintext

This package is intentionally separate from `packages/browser-automation-service/`.
BAS remains the browser lane. This runtime owns local desktop control.
