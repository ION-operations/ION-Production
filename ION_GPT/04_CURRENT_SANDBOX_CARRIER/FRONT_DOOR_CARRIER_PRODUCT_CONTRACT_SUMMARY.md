# ION Custom GPT Front-Door Carrier v4.2 Summary

Status: candidate package integrated for review.

User-visible behavior required by this contract:

- `boot-sequence` completes the boot route and includes `ION ::` in the same answer.
- Boot emits a candidate `ion_boot_sequence_result` block before the Persona response.
- Serious ION work emits a visible `ion_persona` envelope before `ION ::`.
- `proceed` continues the active mounted route instead of picking unrelated work.
- Persona Interface is ingress, final renderer, and user-facing sense-maker.
- Steward remains the orchestrator/manager.
- Criticism or friction becomes audit criteria, blockers, patches, receipts, or the next bounded sequence, not debate.
- Project continuity is carried by `ion_project_hash` when a continuity package is mounted; enforcement through Actions/MCP is a later packet.
- If a route cannot finish in one response, the GPT emits a structured continuation envelope.

Paste target:

```text
ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md
```

Upload package folder:

```text
ION_GPT/02_PACKAGES_TO_UPLOAD/UPLOAD_THESE_ZIPS/
```

Action schema folders:

```text
ION_GPT/03_ACTIONS/ion-actions.helixion.net/
ION_GPT/03_ACTIONS/ion.helixion.net_mcp/
```

Continuity transfer folder:

```text
ION_GPT/05_CONTINUITY_TRANSFER/
```

Detailed worker/release evidence:

```text
ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/
```
