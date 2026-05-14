# ION Continuity Transfer Package Template v4.3

Required zip root:

```text
ION_CONTINUITY_TRANSFER_PACKAGE_<timestamp>/
├── README_START_HERE.md
├── ion_continuity_transfer_manifest.yaml
├── ion_boot_sequence_result.yaml
├── ion_persona_response_envelope.yaml
├── ion_sequence_continuation.yaml
├── ion_dynamic_domain_agent_expansion.yaml
├── ion_project_profile.yaml
├── ion_receipt_summary.yaml
├── ion_proof_manifest.yaml
├── patches/cumulative_candidate.patch
├── reports/validation_report.md
├── tests/validation_results.yaml
├── sources/source_manifest.yaml
└── NEXT_CHAT_PROMPT.txt
```

The manifest hashes every included file and declares omissions through
ION_OMITTED_FILES.yaml when export profiles are used.
