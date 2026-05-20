# AI Start Here

Status: M33 candidate carrier guide

You are inside `ION_VNEXT`, the clean rebuild target. Do not treat the legacy
workspace root, sibling folders, tool visibility, or chat context as authority.

## Required First Reads

1. `../01_canon/PATH_POLICY.yaml`
2. `../01_canon/FRONT_DOOR_BINDING.yaml`
3. `../01_canon/CONTROL_SURFACE_REGISTRY.yaml`
4. `../01_canon/WORKSPACE_CANON.yaml`
5. `../01_canon/FAMILY_REGISTRY.yaml`
6. `../01_canon/STATE_LIFECYCLE.yaml`
7. `../01_canon/MIGRATION_RULES.yaml`
8. `../02_kernel/ion_core/pyproject.toml`

## Carrier Entry Rules

Before substantive work:

1. Report `pwd` and resolved workspace root.
2. Classify the intended target path.
3. Identify the governing packet and allowed write set.
4. Verify the target is inside the authorized vNext area.
5. Refuse wrong-root, private, runtime/current-state, and bulk-copy movements.

## M31 Control Surface

Use the control registry at `../01_canon/CONTROL_SURFACE_REGISTRY.yaml`.

Available candidate controls:

- `path_authority`: classifies and authorizes workspace paths.
- `workspace_root_registry`: resolves current roots, canonical roots, aliases,
  and root-class warnings.
- `ai_movement_gate`: rejects wrong-root, secret/vault, alias, and authority
  escalating movement.
- `codex_work_request_target_binding`: binds Codex work requests to explicit
  target roots and movement classes.
- `agent_cwd_boundary`: prevents silent agent launch from the wrong project
  root.

Run control tests from `../02_kernel/ion_core` when a packet requires proof:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p no:cacheprovider
```

## Hard Stops

Stop and report a blocker if work requires production deployment, runtime JSON
mutation, source-pool bulk copy, private material, GPT Builder changes, Action
or MCP mutation, service restart, or legacy root-shim edits.
