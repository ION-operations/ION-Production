# ION Workspace Source Truth Protocol v0.1

Status: candidate_protocol
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001
Date: 2026-05-13
Authority: candidate only; no accepted-state claim

## Purpose

ION work has expanded beyond a single repo directory. The operator-facing project now lives as a workspace containing ION kernel code, GPT action surfaces, browser extension code, MCP surfaces, local daemons, dAimon, AIM-OS, WisdomNET, product packaging, and operating evidence.

This protocol defines `/home/sev/ION - Production` as the intended workspace source-truth root, subject to a controlled Git migration.

## Core rule

The workspace root is the human and agent navigation root. Git tracking must match that reality.

```text
/home/sev/ION - Production = intended source-truth workspace root
/home/sev/ION - Production/ION_Developement = current active ION kernel repo until migration completes
```

## Non-goals

- Do not use `/home/sev` as the project repo.
- Do not silently delete nested `.git` directories.
- Do not broad-add secrets, caches, virtualenvs, build outputs, Drive mirrors, or quarantine evidence.
- Do not treat moved folders as accepted source truth until they are tracked by the chosen Git model.

## Workspace domain model

```yaml
domain_id: ION_WORKSPACE_SOURCE_TRUTH
domain_type: source_control_and_cartography
owner_role: workspace_source_steward
risk_class: high_context_integrity
accepted_state_authority: false
settlement_required: true
primary_root: /home/sev/ION - Production
current_kernel_repo: /home/sev/ION - Production/ION_Developement
```

## Required managed surfaces

- Root workspace manifest.
- Git boundary audit.
- Nested repo backup plan.
- Monorepo migration plan.
- Root ignore policy.
- Integration promotion map.
- Path resolver registry.
- Agent mount instructions.

## Canonical top-level families

```text
ION_Developement/     active ION kernel and context repo
ION_GPT/              Custom GPT and Action Gateway release surfaces
browser_extension/    browser carrier extension
dAimon/               dAimon agent/application repo
mcp/                  local MCP preview/action/connector surfaces
local_daemon/         local bridge daemons
systemd/              local service templates
product_packager/     packaging/export builders
Cursor/               Cursor extension and SDK surfaces
AIM-OS/               AIM/legacy/adjacent architecture corpus
wisdomNET/            WisdomNET surfaces
ATLAS/                ATLAS surfaces
Needs_Routed/         operator staging lane
quarentine/           evidence quarantine, not active source
```

## Git source-truth options

### Option A: Absorb into one monorepo

Recommended for operator simplicity.

Pros:
- One root for agents and GitHub.
- Cross-system changes are atomic.
- Reduced path confusion.
- Better match to current operator mental model.

Risks:
- Nested repo history must be preserved deliberately.
- Large repo size may need pruning or Git LFS later.

### Option B: Workspace root with submodules

Useful if dAimon/AIM-OS must remain independently versioned.

Pros:
- Preserves separate project history naturally.
- Cleaner external project boundaries.

Risks:
- More confusing for GPT/Codex/operator workflows.
- Easy to forget submodule commits.

### Option C: Workspace root plus separate remote repos and manifests

Useful for long-term product separation.

Pros:
- Clean product boundaries.

Risks:
- Higher orchestration complexity now.

## Recommended posture

Adopt Option A unless a specific folder must retain a separate remote identity.

Before conversion:
- Bundle nested repo histories.
- Record current branch/commit/remotes.
- Create root `.gitignore`.
- Create root manifest.
- Confirm no secrets are staged.

After conversion:
- Update Codex mount root to `/home/sev/ION - Production`.
- Keep `ION_Developement` as a top-level family, not the only source truth.
- Regenerate path maps.
- Run targeted validation.

## Settlement gate

No migration commit is accepted until the operator reviews:

- `GIT_BOUNDARY_AUDIT_20260513.md`
- `NESTED_REPO_BACKUP_PLAN_20260513.md`
- `MONOREPO_MIGRATION_PLAN_20260513.md`
- `ION_WORKSPACE_MANIFEST.yaml`
- root ignore policy
