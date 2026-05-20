# Next Packet M36 Kernel Layer Selection

## Proposed Packet

M36_KERNEL_LAYER_SELECTION

## Objective

Select the next smallest useful vNext kernel layer after return-proof gates.

## Starting Point

M35 landed the return-proof gates only:

- `ion_context_proof_gate.py`
- `ion_template_action_gate.py`

## Candidate Categories To Reassess

- carrier mount receipt
- package/profile handling
- receipt primitives
- clean export / hygiene
- status/read-only visibility
- branch context/capsule handling

## Required Boundary

Do not promote runtime queues, ledgers, current-state JSON, Actions/MCP runtime wrappers, GPT Builder schemas, browser execution, provider integrations, private material, or broad agent automation unless a future packet explicitly proves dependency closure.
