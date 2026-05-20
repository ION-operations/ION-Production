# ION_VNEXT

Status: candidate vNext workspace, no production cutover
Created: 20260519T195049Z
Front-door binding: M33 candidate

ION_VNEXT is the clean rebuild target for ION Production. It is designed to make
workspace organization, authority, carrier movement, source promotion, runtime
state, context state, and release hygiene obvious to humans and AI agents.

ION_VNEXT is not the production root front door yet. The current roots outside
`ION_VNEXT/` remain source pools, evidence, or private/runtime material until a
bounded promotion packet audits and copies specific files with validation and a
receipt.

## Start Here

Human first read:

1. `00_front_door/HUMAN_START_HERE.md`
2. `00_front_door/AUTHORITY_BOUNDARIES.md`
3. `00_front_door/ROUTE_MAP.md`
4. `01_canon/WORKSPACE_CANON.yaml`
5. `01_canon/FAMILY_REGISTRY.yaml`

AI or carrier first read:

1. `00_front_door/AI_START_HERE.md`
2. `01_canon/PATH_POLICY.yaml`
3. `01_canon/FRONT_DOOR_BINDING.yaml`
4. `01_canon/CONTROL_SURFACE_REGISTRY.yaml`
5. `02_kernel/ion_core/pyproject.toml`

## Authority

No folder, document, carrier output, test result, or chat transcript becomes
accepted state by appearing here. State-bearing work still requires source
evidence, a bounded packet, path-policy fit, validation, receipt, and operator
or steward acceptance.

The M31 control surface is available under `02_kernel/ion_core` for path
authority, workspace-root classification, AI movement gating, Codex target
binding, and agent CWD boundary checks. It is a candidate control surface until
future packets accept or replace it.

Do not bulk-copy source pools, copy runtime/current-state JSON, include private
material, or migrate legacy roots without a promotion packet.
