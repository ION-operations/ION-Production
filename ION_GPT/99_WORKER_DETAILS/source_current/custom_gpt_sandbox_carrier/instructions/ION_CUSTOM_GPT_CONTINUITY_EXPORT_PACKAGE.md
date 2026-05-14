# ION Custom GPT Continuity Export Package v4.3

## Purpose

Every state-bearing sequence must be portable to a new chat. The carrier must
not rely on hidden chat memory. It must export remountable context or provide a
full YAML fallback in chat when file export is not possible.

## Required package

`ION_CONTINUITY_TRANSFER_PACKAGE_<timestamp>.zip`

Required files:

- README_START_HERE.md
- ion_continuity_transfer_manifest.yaml
- ion_boot_sequence_result.yaml
- ion_persona_response_envelope.yaml
- ion_sequence_continuation.yaml
- ion_dynamic_domain_agent_expansion.yaml
- ion_project_profile.yaml
- ion_receipt_summary.yaml
- ion_proof_manifest.yaml
- patches/cumulative_candidate.patch
- reports/validation_report.md
- tests/validation_results.yaml
- sources/source_manifest.yaml
- NEXT_CHAT_PROMPT.txt

## Remount rule

A new chat receiving this package must mount `ion_continuity_transfer_manifest.yaml`
before substantive answer, restore active route/objective/persona/domain-agent
state, and continue through Persona Interface.
