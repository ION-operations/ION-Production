# ION GitHub Communications Fallback Protocol

Status: candidate protocol for review.  
Packet: `PCKT-SEV-001-GITHUB-COMMS-FALLBACK`

## Purpose

ION carriers should prefer the bounded MCP lane when it is available and fresh.
When MCP is unavailable, not exposed to the current carrier, stale, or blocked,
GitHub may serve as a public, auditable communications fallback.

This protocol does not make GitHub an ION runtime authority. GitHub issues, pull
requests, and comments are evidence and proposals. They are accepted only after
normal ION proof gates, Steward integration, and receipts.

## Carrier routing order

1. **Direct local ION/Codex lane** — local PC plus Codex CLI for bounded build,
   test, and proof work.
2. **MCP lane** — read-only or dry-run connector/tool access where the active
   carrier can actually invoke the MCP surface.
3. **GitHub comms fallback** — issue, PR, comment, or artifact-only envelope
   prepared by `kernel.ion_github_comms_fallback` and published only by a local
   operator or approved GitHub carrier.
4. **Google Drive visibility layer** — synchronized project files and artifact
   bundles for live visibility. Drive is not runtime authority and must not carry
   credentials or production-only state.

## Generated fallback artifacts

The fallback generator writes under:

```text
ION/05_context/current/github_data_plane/comms_fallback/<comms_id>/
```

Each fallback bundle contains:

- `envelope.json` — structured carrier message, packet, routing, boundary, and
  GitHub data-plane summary.
- `message.md` — GitHub-ready issue/PR/comment body.
- `github_command_plan.json` — `gh` CLI commands for a local operator to run if
  approved. The generator does not run them.
- `receipt.json` — local artifact-write receipt.

## Non-authority boundary

The generator must not:

- call GitHub;
- run `gh`;
- stage, commit, push, or deploy;
- mutate production infrastructure;
- access or print secrets;
- claim accepted ION state.

## Secret policy

Outbound fallback text is scanned for token-like material. Secret-like messages
are blocked and withheld. The secret scanner reports path/type/line metadata with
redacted excerpts only.

Forbidden material includes API keys, GitHub tokens, browser cookies, Cloudflare
tunnel tokens, private keys, browser profiles, and production-only state.

## Local operator flow

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages \
python3 -m kernel.ion_github_comms_fallback \
  --ion-root . \
  --packet-id PCKT-SEV-001-GITHUB-COMMS-FALLBACK \
  --objective "Create an auditable fallback lane when MCP is unavailable." \
  --message-file /path/to/message.md \
  --channel issue \
  --write \
  --json
```

Then review the generated `github_command_plan.json`. If the operator approves,
run the listed `gh` command locally. Record the GitHub URL back into the packet,
receipt, or settlement artifact.

## Proof requirements

A valid fallback handoff must show:

- packet or objective;
- source and target carrier;
- fallback reason;
- message hash;
- secret scan result;
- GitHub data-plane audit summary;
- non-authority flags;
- local artifact receipt;
- later GitHub URL or operator decision if published.
