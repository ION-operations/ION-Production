# ION_VNEXT Front Door

Status: candidate vNext entrypoint
Created: 20260519T195049Z
Front-door binding: M33 candidate

This directory is the internal entrypoint for ION_VNEXT. It orients humans and
AI agents inside the clean rebuild without changing the legacy production root
front door.

## Read Order

For humans:

1. `HUMAN_START_HERE.md`
2. `AUTHORITY_BOUNDARIES.md`
3. `ROUTE_MAP.md`
4. `../01_canon/WORKSPACE_CANON.yaml`
5. `../01_canon/FAMILY_REGISTRY.yaml`

For AI agents and carriers:

1. `AI_START_HERE.md`
2. `../01_canon/PATH_POLICY.yaml`
3. `../01_canon/FRONT_DOOR_BINDING.yaml`
4. `../01_canon/CONTROL_SURFACE_REGISTRY.yaml`
5. `../02_kernel/ion_core/pyproject.toml`

## Binding Rule

Do not infer authority from tool visibility, current working directory, folder
presence, or readable files. Authority comes from canon, path policy, validation,
receipts, and operator approval.

Current project roots outside `ION_VNEXT/` remain source pools or evidence until
specific files are audited and copied by a bounded promotion packet.
