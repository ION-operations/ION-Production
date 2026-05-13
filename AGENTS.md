## Root Workpackets Artifact Lane Rule

Before declaring any sandbox package, workpacket, zip, artifact bundle, or ChatGPT
Browser generated package absent, check the main project workpackets lane:

- `/home/sev/ION - Production/ION_CODEX FULL/workpackets/`

This lane is outside `/home/sev/ION - Production/ION_CODEX FULL/ION`, so searches
limited to the `ION/` subtree will miss valid current artifacts.

## Continuity Recovery Rule

When the user says a Codex/terminal chat was lost, asks about memory, or mentions
ION context/capsule continuity, do not answer from current chat context alone.
Before claiming there is no memory, inspect local recovery artifacts:

- `/home/sev/.codex/history.jsonl`
- `/home/sev/.codex/session_index.jsonl`
- latest matching file under `/home/sev/.codex/sessions/`
- `/home/sev/ION - Production/ION_CODEX FULL/ION/05_context/current/codex_solo/HOT_CONTEXT.md`
- `/home/sev/ION - Production/ION_CODEX FULL/ION/05_context/current/codex_solo/MINI.md`
- `/home/sev/ION - Production/ION_CODEX FULL/ION/05_context/current/codex_solo/CAPSULE.md`
- `/home/sev/ION - Production/ION_CODEX FULL/ION/05_context/current/codex_solo/STATUS.json`

The active ION root is `/home/sev/ION - Production/ION_CODEX FULL`.
If the current shell root is `/home/sev` or `/home/sev/ION - Production`, the
active-root SessionStart hook may not fire. Recover explicitly from the files
above before asking the user to repeat context.
