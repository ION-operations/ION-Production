# ION Codex Local PC Operating Packet

Status: candidate operating packet  
Packet: `PCKT-SEV-002-CODEX-LOCAL-PC-OS-AND-GITHUB-FALLBACK`  
Authority: local read-first bootstrap, candidate implementation support  
Production authority: false  
Live execution authority: false  
Accepted state authority: false

## Objective

Make the local PC the primary ION execution substrate with Codex CLI as the
bounded local filesystem/build/test carrier, while preserving ChatGPT Browser as
coordination carrier and GitHub as durable fallback/data plane.

This packet does not authorize broad mutation. It establishes the readiness,
visibility, and fallback controls needed before stronger automation or worker
spawning is trusted.

## Current carrier split

```text
ChatGPT Browser / Sev:
  coordination, packet formation, review, branch strategy, artifact export

Codex CLI on local PC:
  bounded filesystem/build/test work, local command evidence, candidate diffs

MCP:
  preferred live control-plane socket when exposed and healthy

GitHub:
  durable data/comms fallback: issues, PRs, branches, artifact refs, review history

Google Drive sync:
  visibility / file-transfer lane only; not runtime authority, not settlement authority
```

## Local first readiness commands

Run from the shell root that contains `pyproject.toml` and `ION/REPO_AUTHORITY.md`:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_status --ion-root . --json
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_cli_carrier_audit --ion-root . --json
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_carrier_domain status --ion-root . --json
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_carrier_domain cockpit --ion-root . --json
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_local_pc_readiness --ion-root . --json --write
PYTHONPATH=ION/04_packages python3 -m kernel.ion_github_comms_fallback status --ion-root . --json --write
```

The new readiness helper is intentionally read-only. It checks repo surfaces,
Codex CLI availability, Git branch/dirty state, local service ports, and GitHub
fallback posture. It does not read hidden Codex memories, start sessions, call
MCP, mutate GitHub, or change Git.

## Codex local audit prompt

The carrier OS context package includes a candidate local audit prompt:

```text
ION_CODEX_CARRIER_OS_CONTEXT_PACKAGE_001/CODEX_LOCAL_AUDIT_PROMPT.md
```

Use it as a read-only Codex pass first. The uploaded context package was based
on an older `FULL2` snapshot, so it is useful direction but not authoritative
for `FULL3` until reconciled.

## Codex execution pattern

For implementation packets after readiness is reconciled:

```bash
codex exec \
  --sandbox workspace-write \
  --approval-policy on-request \
  --output-last-message ION/05_context/current/codex_cli/latest_return.md \
  "$(cat ION/05_context/current/codex_cli/latest_prompt.md)"
```

Required return sections:

```text
### CONTEXT PROOF
### TEMPLATE ACTION PROOF
### RESULT
```

No Codex return is accepted state until proof gates and settlement accept it.

## MCP path

Preferred check:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_mcp_local_bridge_smoke --ion-root . --json
```

Read-only Codex carrier MCP projections should expose:

```text
ion.codex.carrier.status
ion.codex.carrier.cockpit
```

If this ChatGPT session cannot see the MCP namespace even after refresh, use
GitHub comms fallback below while keeping MCP as preferred local control plane.

## GitHub comms fallback

When MCP is unavailable to Sev/GPT browser, draft a candidate issue or PR body
instead of attempting live mutation:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_github_comms_fallback issue-draft \
  --ion-root . \
  --title "ION Codex local PC readiness" \
  --packet-id "PCKT-SEV-002-CODEX-LOCAL-PC-OS-AND-GITHUB-FALLBACK" \
  --objective "Expose local readiness evidence and route the next Codex implementation pass." \
  --evidence "ION/05_context/current/codex_local_pc/CODEX_LOCAL_PC_READINESS.json" \
  --artifacts "candidate patch bundle" \
  --json
```

To save a local draft artifact:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_github_comms_fallback issue-draft \
  --ion-root . \
  --title "ION Codex local PC readiness" \
  --packet-id "PCKT-SEV-002-CODEX-LOCAL-PC-OS-AND-GITHUB-FALLBACK" \
  --objective "Expose local readiness evidence and route the next Codex implementation pass." \
  --write \
  --confirmation ION_GITHUB_COMMS_FALLBACK_WRITE_CONFIRMED \
  --json
```

This writes only local draft files. It does not run `gh issue create`, stage,
commit, push, or accept state.

## Google Drive sync guidance

Google Drive sync is useful for live visibility if it preserves the working tree
shape. Treat it as a visibility lane:

- prefer syncing a clean clone or explicit branch workspace;
- do not sync `.env`, tunnel credentials, browser profiles, token stores, or
  private logs;
- preserve `.git` only if the connector/tooling can read it safely and the
  operator expects branch/diff visibility;
- use GitHub branches/PRs for durable diffs and review, not Drive file versions;
- record any Drive-derived artifact into an ION packet or receipt before using
  it as inherited context.

## First operational sequence

1. Restore or sync the local `FULL3` project into a real Git working tree.
2. Run the readiness commands above.
3. Run the read-only local Codex audit prompt from the carrier OS package.
4. If MCP is visible, query `ion.codex.carrier.status` and
   `ion.codex.carrier.cockpit` read-only.
5. If MCP is not visible, generate a GitHub fallback issue draft with readiness
   evidence.
6. Create a scoped branch for implementation, such as
   `work/codex-local-pc-os-bootstrap`.
7. Let Codex CLI implement one bounded packet at a time.
8. Return patch, validation evidence, and receipt paths to Sev for review and
   settlement planning.

## Non-claims

This packet does not claim:

```text
MCP is exposed to every ChatGPT session
Google Drive is runtime authority
GitHub comments are ION state
Codex memory is accepted state
local services are currently running
production authority
merge authority
secret authority
```
