# ION Custom GPT Front-Door Carrier Product Contract Repair Report v0.4

Created: 20260513T175345Z  
Posture: sandbox-candidate  
Accepted state claim: false  
Production authority: false  
Live execution authority: false

## Objective

Continue the Custom GPT branch as lead developer and evolve the boot/persona repair
from prompt patching into a testable front-door carrier product contract.

The target defect class is: the GPT treats the chat as a conversational surface
that can reset or discuss the route, instead of treating it as an ION carrier
transaction that must continue active workflow state and return through Persona
Interface.

## Source evidence inspected

- `ION_CUSTOM_GPT_PERSONA_RETURN_GATE_REPAIR_CANDIDATE_20260513T173011Z.zip`
- `ION_DEVELOPMENT_CORE_SOURCE_20260513T145238Z.zip::ION_Developement/ION/02_architecture/FRONT_DOOR_PERSONA_RELAY_STEWARD_BOUNDARY_PROTOCOL.md`
- `ION_DEVELOPMENT_CORE_SOURCE_20260513T145238Z.zip::ION_Developement/ION/02_architecture/FRONT_DOOR_RUNTIME_ENTRY_PROTOCOL.md`
- `ION_DEVELOPMENT_CORE_SOURCE_20260513T145238Z.zip::ION_Developement/ION/02_architecture/FRONT_DOOR_CHAT_ORCHESTRATION_ADAPTER_PROTOCOL.md`
- `ION_DEVELOPMENT_CORE_SOURCE_20260513T145238Z.zip::ION_Developement/ION/02_architecture/PERSONA_CONTEXT_BUDGET_AND_HORIZON_PROTOCOL.md`
- `ION_DEVELOPMENT_CORE_SOURCE_20260513T145238Z.zip::ION_Developement/ION/02_architecture/ION_FRONT_DOOR_AUTONOMOUS_TEAM_WORKFLOW_PROTOCOL.md`
- `ION_DEVELOPMENT_CORE_SOURCE_20260513T145238Z.zip::ION_Developement/.cursor/rules/ion-persona-user-facing.mdc`

## Product decision

The GPT should not be optimized as a Discord/chat companion for ION. It should be
a carrier-control surface:

```text
operator_turn
-> Persona ingress
-> Relay semantic packet
-> Steward routing/orchestration
-> bounded work object / blocker
-> proof compression
-> Relay return package
-> Persona Return Gate
-> Persona Interface response
```

The visible answer can expose compact telemetry, but the human-facing substance
must be Persona rendering of real workflow output.

## Implemented candidate changes

- Added `ION_CUSTOM_GPT_FRONT_DOOR_CARRIER_PRODUCT_CONTRACT.md`.
- Added `ION_CUSTOM_GPT_PERSONA_RETURN_PACKAGE.schema.json`.
- Added `ION_CUSTOM_GPT_SEQUENCE_CONTINUATION_ENVELOPE.schema.json`.
- Added `ion_custom_gpt_sequence_harness.py` to make active-sequence continuation testable.
- Added `test_front_door_carrier_product_contract_candidate.py`.
- Rebuilt `CURRENT_INSTRUCTIONS_TO_PASTE.md` and `ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md`
  as compact v0.4 paste-ready instructions (`7987` chars each), while preserving full v4 archive copies.
- Updated GPT Builder instructions and source instructions with:
  - `FRONT_DOOR_CARRIER_PRODUCT_LAW`
  - `PERSONA_AS_PUBLIC_RENDERER_NOT_CHAT_BUDDY`
  - `FRONT_DOOR_TRANSACTION_SEQUENCE`
  - `FINAL_ANSWER_GATE`
- Updated boot route with:
  - product contract refs;
  - operator-turn classifier;
  - final-answer gate;
  - workflow-object requirement.
- Updated context package to mount the new contract, schemas, and harness.
- Updated boot/persona templates and internal workflow with front-door product behavior.

## Changed files

- `ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md`
- `ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE_FULL_V4_ARCHIVE.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/context/ION_CUSTOM_GPT_SANDBOX_CARRIER_CONTEXT_PACKAGE.yaml`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_BOOT_SEQUENCE.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_FRONT_DOOR_CARRIER_PRODUCT_CONTRACT.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000_FULL_V4_ARCHIVE.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_PERSONA_RETURN_GATE.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/routes/BOOT_TO_PERSONA_ROUTE.yaml`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_PERSONA_RETURN_PACKAGE.schema.json`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_SEQUENCE_CONTINUATION_ENVELOPE.schema.json`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_PERSONA_INTERFACE_RESPONSE.template.md`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/tools/ion_custom_gpt_sequence_harness.py`
- `ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/workflows/ION_CUSTOM_GPT_INTERNAL_WORKFLOW.md`
- `START_HERE_FOR_CUSTOM_GPT.md`
- `test_front_door_carrier_product_contract_candidate.py`

## Regression results

- `/opt/pyvenv/bin/python test_boot_process_repair_candidate.py` -> exit `0`; stdout: `boot process repair candidate regression: PASS
active sequence continuation regression: PASS`; stderr: artifact_tool spreadsheet warmup warning observed; command exit_code stayed 0
- `/opt/pyvenv/bin/python test_front_door_carrier_product_contract_candidate.py` -> exit `0`; stdout: `front door carrier product contract candidate regression: PASS`; stderr: artifact_tool spreadsheet warmup warning observed; command exit_code stayed 0
- `/opt/pyvenv/bin/python -m pytest -q test_persona_return_gate_candidate.py test_front_door_carrier_product_contract_candidate.py` -> exit `0`; stdout: `...........                                                              [100%]
11 passed in 0.22s`; stderr: artifact_tool spreadsheet warmup warning observed; command exit_code stayed 0

## Important caveat

The test commands printed a sandbox Python startup warning from `artifact_tool`
spreadsheet warmup to stderr. The tested commands returned exit code `0`; the
warning was not produced by the candidate package tests.

## Acceptance criteria for promotion

1. Review diff and package contents.
2. Paste updated `ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md`
   into GPT Builder only through the approved release lane.
3. Upload/replace the updated knowledge package set from this candidate bundle.
4. Run live boot regression manually:
   - `boot-sequence` must emit boot telemetry and `ION ::` in the same answer.
   - `NEXT` must not be `BOOT_TO_PERSONA_INTERFACE_RESPONSE` unless blocked.
   - `proceed` and unrelated text must continue the active object, not select a new objective.
   - Persona must explain real workflow proof/artifacts without becoming Steward.
5. Record acceptance/rollback receipt.

## Status

Candidate bundle is ready for operator review/promotion. It is not accepted state
until promoted through the GPT release lane and receipted.
