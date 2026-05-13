# Quintet Gate Policy

Purpose: keep quintet/nl_tags quality standards high while removing false blocking from unrelated baseline debt.

## Policy Model

Configuration file:

- `config/quintet_gate_policy.json`

Modes:

- `strict`: blocking gate for all staged code changes.
- `balanced` (default): blocking only when critical paths are touched.
- `advisory`: never blocks, always reports findings.

Critical paths are declared explicitly in policy and include core AIM-OS runtime surfaces.

## Local Hook Installation

Install policy-driven hook:

```powershell
python scripts/git/install_quintet_hook.py
```

Backward-compatible entrypoint:

```powershell
python scripts/install_sdfcvf_hooks.py
```

## Mode Overrides

Current shell override:

```powershell
$env:AIMOS_QUINTET_GATE_MODE = "strict"   # strict|balanced|advisory
```

Force blocking regardless of mode:

```powershell
$env:AIMOS_QUINTET_FORCE_BLOCK = "1"
```

## Runner (Manual / CI)

Pre-commit-equivalent run:

```powershell
python scripts/git/quintet_pre_commit_gate.py --stage pre-commit
```

All tracked files (CI-style):

```powershell
python scripts/git/quintet_pre_commit_gate.py --all-files --stage ci --json
```

Changed-scope run (PR-style):

```powershell
python scripts/git/quintet_pre_commit_gate.py --changed-against <base_sha_or_branch> --stage ci-pr --json
```

## Recommended Enforcement Strategy

1. Local pre-commit: `balanced` by default.
2. Pull-request CI: blocking on changed scope for critical paths.
3. Main/release branch: strict full-repo run with documented waivers.

Current CI entrypoint:

- `.github/workflows/quintet-gate.yml`
