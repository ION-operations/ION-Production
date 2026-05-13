# First Root Commit Staging Plan - 2026-05-13

Status: candidate_plan
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001
Accepted state authority: false

## Current root

```text
/home/sev/ION - Production
```

## Ignore posture verified

The following local/security/cache paths are ignored before staging:

```text
ION_Developement/.env.supabase.local
dAimon/.env
AIM-OS/data/mcp/sentinel_session_secret.key
dAimon/.venv
ION_Developement/ION/08_ui/joc_cockpit_shell/node_modules
ION_VAULT_LOCAL
```

## File-count posture excluding ignored files

```text
.codex                         2
.github                        1
AGENTS.md                      1
AIM-OS                         11844
ATLAS                          3461
Cursor                         14
ION_Developement               6557
ION_GPT                        15
ION_WORKSPACE_MANIFEST.yaml    1
Needs_Routed                   118
START_HERE_FOR_ANY_AGENT.md    1
browser_extension              16
dAimon                         121
local_daemon                   2
mcp                            9
product_packager               2
quarentine                     3847
systemd                        7
what is ION?                   3
```

## Recommended commit layers

### Commit 1: workspace source-truth shell

Stage only:

```text
.gitignore
AGENTS.md
START_HERE_FOR_ANY_AGENT.md
ION_WORKSPACE_MANIFEST.yaml
.codex/
.github/
ION_Developement/ION/02_architecture/ION_WORKSPACE_SOURCE_TRUTH_PROTOCOL_V0_1.md
ION_Developement/ION/03_registry/ion_workspace_source_truth_registry.yaml
ION_Developement/ION/docs/setup/ION_LOCAL_SECRET_VAULT.md
ION_Developement/ION/05_context/current/repo_organization/*20260513*.md
ION_Developement/ION/05_context/current/repo_organization/*20260513*.txt
ION_Developement/ION/05_context/current/repo_organization/*20260513*.gitignore
```

Commit message:

```text
PCKT: establish ION Production workspace source-truth shell
```

### Commit 2: active ION kernel repo absorption

Stage `ION_Developement/` excluding ignored env/cache/build files.

Commit message:

```text
PCKT: absorb active ION development tree into workspace root
```

### Commit 3: promoted integration roots

Stage:

```text
ION_GPT/
browser_extension/
mcp/
local_daemon/
systemd/
product_packager/
Cursor/
```

Commit message:

```text
PCKT: track promoted ION integration roots
```

### Commit 4: dAimon workspace source

Stage `dAimon/` excluding ignored `.env` and `.venv`.

Commit message:

```text
PCKT: absorb dAimon workspace source
```

### Commit 5: knowledge/application corpora

Stage only after review because of size:

```text
AIM-OS/
ATLAS/
wisdomNET/
what is ION?/
Needs_Routed/
```

Commit message:

```text
PCKT: absorb ION knowledge and adjacent system corpora
```

### Commit 6: quarantine index only, not raw archives

Do not stage all of `quarentine/` by default. Stage only index/README/manifest files unless the operator explicitly wants archive evidence in Git.

## Rationale

This preserves the operator's workspace model while keeping each large domain reviewable.

## Stop conditions

- Any env/key/token file appears staged.
- Any virtualenv or node_modules path appears staged.
- Any GPT Builder release instruction appears without the action-release domain package.
- Any quarantine bundle/raw archive is staged unintentionally.
