[CODEX] | ACTIVE | Structured capture subsystem landed

- Added `packages/jarvis_injector/src/jarvis_injector/capture/`
- Runtime now exposes `POST /api/capture/last-message`
- Capture normalizes last-message content into structured blocks instead of flattening to raw text
- Current supported snapshot inputs: DOM HTML, UIA tree payloads, plaintext fallback
- Smoke test confirmed paragraph + inline code + code block + tool-call capture normalization

Live DOM/UIA acquisition from running apps is still a later phase; current route expects supplied snapshots.
