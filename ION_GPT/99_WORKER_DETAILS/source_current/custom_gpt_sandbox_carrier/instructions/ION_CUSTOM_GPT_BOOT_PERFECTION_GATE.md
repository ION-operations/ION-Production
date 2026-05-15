# ION Custom GPT Boot Perfection Gate v1.1

Boot is not product-ready merely because it prints `ION ::`. The carrier must
prove the mount, receipt, persona envelope, machine-block fencing,
Action/MCP/tool posture, continuity/hash state, upload set, and blockers.

## Required Boot Answer Boundary

After any tool calls or probes, the assistant-authored final boot answer starts
with `BOOT`. Tool trace UI may appear separately, but the final response must
not include conversational preamble before the BOOT envelope.

## Required Machine Blocks

Serious boot objects must be emitted as fenced YAML blocks with canonical schema
IDs and stable top-level keys:

- `ion_boot_sequence_result` using `ion.boot_sequence_result.v1`
- `ion_boot_audit` using `ion.boot_perfection_audit.v1`
- `ion_action_surface_audit` using `ion.action_surface_audit.v1` when Action,
  MCP, or tool surfaces are available
- `ion_persona` using `ion.persona_response_envelope.v0_1`

`ion_action_surface_audit` must not be buried only inside `ion_boot_audit`.

## Audit Statuses

Use only:

- `pass`
- `pass_with_warnings`
- `warn`
- `fail`
- `not_inspected`
- `not_available`

Boot may return `PASS_WITH_WARNINGS`, but must not imply perfection when
continuity, project hash, Action auth, MCP mutation proof, or upload-set proof is
pending.

## Hard Failures

Fail or block boot readiness when:

- the boot route is not completed through Persona Interface;
- serious machine objects are emitted as raw unfenced YAML;
- `ION ::` is missing for substantive boot;
- accepted-state, production, or live authority is claimed without proof;
- protected Action/MCP mutation is attempted without explicit approval/receipt;
- secrets/vault absence is claimed without authorized inspection;
- no workflow object or boot receipt is created.
