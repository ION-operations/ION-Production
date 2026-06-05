# GitHub Comms Fallback Packet

Packet ID: `<packet-id>`
Template: `GITHUB_COMMS_FALLBACK_PACKET`
Status: candidate until proof-gated and receipted

## Objective

State the bounded carrier-to-carrier communication objective.

## Fallback reason

Use this packet only when direct MCP or local connector communication is
unavailable, stale, blocked, or not exposed to the active carrier.

## Source carrier

- Callsign:
- Carrier:
- Session/context refs:

## Target carrier

- Callsign or agent:
- Carrier:
- Expected response:

## Message

Write the message that should become a GitHub issue, PR body, issue/PR comment,
or artifact-only handoff.

## Evidence refs

- packet/context/receipt refs:
- local validation refs:
- artifact refs:

## Channel

One of:

- `issue`
- `pr`
- `comment`
- `artifact_only`

## Secret review

Confirm that the message excludes credentials, tokens, browser cookies, browser
profiles, tunnel secrets, private keys, private logs, and production-only state.

## Required proof

- generated `envelope.json`
- generated `message.md`
- generated `github_command_plan.json`
- generated `receipt.json`
- GitHub URL or operator deferral reason if published

## Authority boundary

GitHub comms are proposals/evidence, not accepted ION runtime state. No generated
command may be run without local operator or governed carrier approval.
