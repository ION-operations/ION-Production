# ION Continuity Transfer Package

This package is a portable handoff bundle for a future GPT/chat/carrier.

Read order:

1. `ion_continuity_transfer_manifest.yaml`
2. `ion_boot_sequence_result.yaml`
3. `ion_persona_response_envelope.yaml`
4. `ion_sequence_continuation.yaml`
5. `ion_project_profile.yaml`
6. `ion_receipt_summary.yaml`
7. `ion_proof_manifest.yaml`
8. `NEXT_CHAT_PROMPT.txt`

Authority:

- This package is candidate continuity evidence.
- It is not accepted state by itself.
- It grants no production, deployment, live execution, or secrets authority.

Project hash:

- `ion_project_hash` is the continuity identity for this package/chat branch.
- If this package is mounted in a later chat, reuse the package hash instead of inventing a new one.
- If no package is mounted, create a new candidate continuity package and assign a new hash.
- Action/MCP project-hash enforcement is a later gateway guard; this package only carries the identity.
