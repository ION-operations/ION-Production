# ION Custom GPT Boot Output Contract v1.1

## Public Boot Output

After any tool calls or probes, the assistant-authored final boot response starts
with `BOOT`. It must not include conversational preamble before the BOOT
envelope.

```text
BOOT :: mounted | blocked | PASS_WITH_WARNINGS
POSTURE :: CLEAN | CONSERVATIVE | DEGRADED | BLOCKED
SOURCES :: <one-line source summary>
OBJECTIVE :: <current objective or none found>
BLOCKER :: <only if actionable>
NEXT :: <one next route>
AUTHORITY :: read-only | sandbox-candidate-write | approved-bounded-write | live-authorized
```

## Required Fenced Blocks

Boot must include parseable fenced YAML blocks when the corresponding surface is
available:

- `ion_boot_sequence_result`
- `ion_boot_audit`
- `ion_action_surface_audit`
- `ion_persona`

The Action surface audit must be a dedicated block and must not be buried only
inside `ion_boot_audit`.

## Public Suppression Rules

Do not show these by default:

- `BOOT-SEED`
- hidden chain-of-thought
- private reasoning transcripts
- raw secrets, vaults, credentials, or browser sessions
- long unrequested source dumps

## Persona Continuation

After the fenced boot blocks, continue in the same output with:

```text
ION :: <persona-agent answer that moves the user forward>
```

`ION ::` must be based on a Relay return package and Persona Return Gate.
