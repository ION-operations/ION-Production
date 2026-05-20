# Human Start Here

Status: M33 candidate front-door guide

ION_VNEXT is the clean rebuild workspace for ION Production. It is intended to
make the future organization obvious before the legacy production root is
changed.

ION_VNEXT is not a bulk migration. It does not mean the old roots are obsolete,
renamed, moved, or accepted into the new canon. Current roots remain source
pools, evidence, runtime surfaces, archive witnesses, or private material until
a future packet audits and promotes specific files.

## First Read

1. `AUTHORITY_BOUNDARIES.md`
2. `ROUTE_MAP.md`
3. `../01_canon/WORKSPACE_CANON.yaml`
4. `../01_canon/FAMILY_REGISTRY.yaml`
5. `../01_canon/STATE_LIFECYCLE.yaml`
6. `../01_canon/LEGACY_SOURCE_POOLS.yaml`
7. `../01_canon/MIGRATION_RULES.yaml`
8. `../01_canon/QUALITY_STANDARD.yaml`

## What Is Live Here

The M25 skeleton and M31 control surface are present under Git custody:

- `../01_canon/` holds the vNext organization canon candidates.
- `../02_kernel/ion_core/` holds the first dependency-closed control surface.
- `../02_kernel/ion_core/tests/control/` holds the control tests.

This front door does not switch production behavior. It only makes the vNext
entry path explicit inside `ION_VNEXT`.

## Operator Rule

For new work, choose a bounded packet before changing files. The next expected
routes are listed in `ROUTE_MAP.md`.
