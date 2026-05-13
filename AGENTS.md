# Agent Instructions for ION Production Workspace

## Active root

The active workspace root is:

```text
/home/sev/ION - Production
```

The active ION kernel/context tree is:

```text
/home/sev/ION - Production/ION_Developement
```

Do not use `/home/sev` as the project Git root.
Do not use the former `/home/sev/ION - Production/ION_CODEX FULL` path except as historical evidence in old receipts/docs.

## First files to read

Before substantial work, inspect:

```text
README.md
START_HERE_FOR_ANY_AGENT.md
ION_WORKSPACE_MANIFEST.yaml
ION_Developement/ION/REPO_AUTHORITY.md
ION_Developement/ION/05_context/current/codex_solo/HOT_CONTEXT.md
ION_Developement/ION/05_context/current/codex_solo/MINI.md
ION_Developement/ION/05_context/current/codex_solo/CAPSULE.md
ION_Developement/ION/05_context/current/codex_solo/STATUS.json
```

## Continuity recovery rule

When the user says a Codex/terminal chat was lost, asks about memory, or mentions ION context/capsule continuity, do not answer from current chat context alone.

Before claiming there is no memory, inspect local recovery artifacts:

```text
/home/sev/.codex/history.jsonl
/home/sev/.codex/session_index.jsonl
latest matching file under /home/sev/.codex/sessions/
ION_Developement/ION/05_context/current/codex_solo/HOT_CONTEXT.md
ION_Developement/ION/05_context/current/codex_solo/MINI.md
ION_Developement/ION/05_context/current/codex_solo/CAPSULE.md
ION_Developement/ION/05_context/current/codex_solo/STATUS.json
```

## Workpacket/artifact lane rule

Current incoming material is staged under:

```text
Needs_Routed/
```

Legacy/candidate/archive material may exist under:

```text
quarentine/
```

Do not declare a workpacket, diff, package, or artifact absent before checking these lanes.

## GPT Builder / Action Gateway rule

Do not give operator-facing GPT Builder instructions from memory or fragments.

Canonical GPT Builder Action schemas:

```text
ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

Worker/source evidence for the Action Gateway schema:

```text
ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml
```

That worker/source path is evidence/reference only, not the GPT Builder install
target.

Do not use the former `ION_GPT/custom_gpt_action_gateway/openapi.yaml` path as
an install target. That path is historical/stale after the ION_GPT folder
reorganization.

Release tooling:

```text
ION_Developement/ION/04_packages/kernel/ion_action_schema_release.py
```

Hard rule:

```text
No validated release bundle, no GPT Builder change.
```

If a protected GPT Action returns `AUTH_INVALID`, `gateway_token_invalid`, or unexpected `AUTH_MISSING`, stop all protected Action calls immediately.

## Secrets and vault

Local vault:

```text
ION_VAULT_LOCAL/
```

Vault contents are ignored by Git. Do not print or commit secret values. Agents may report only presence/absence.

## Quarantine rule

`quarentine/` is archive witness material, not active source by default. Promote specific files through a bounded packet before using them as active implementation source.

## Authority boundaries

- No production deployment unless explicitly approved.
- No Git push unless explicitly approved.
- No destructive file deletion unless explicitly approved.
- No service restarts unless explicitly requested.
- No live Action/MCP mutation lane unless explicitly requested.
- No accepted-state claim without proof/receipt/settlement.
