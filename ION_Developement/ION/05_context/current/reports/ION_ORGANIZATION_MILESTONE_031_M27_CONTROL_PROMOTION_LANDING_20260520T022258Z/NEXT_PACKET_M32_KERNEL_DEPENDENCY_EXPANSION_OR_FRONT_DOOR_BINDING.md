# Next Packet - M32 Kernel Dependency Expansion Or Front Door Binding

Status: recommended next packet

M31 landed the dependency-closed first control surface into ION_VNEXT.

## Candidate Next Directions

Choose one bounded direction:

1. `M32_KERNEL_DEPENDENCY_EXPANSION`
   - Identify the next minimal kernel dependencies needed after the five control modules.
   - Keep tests local to `ION_VNEXT/02_kernel/ion_core`.
   - No runtime/current-state JSON.

2. `M32_FRONT_DOOR_BINDING`
   - Bind `ION_VNEXT/00_front_door` and root shims to the new control surface.
   - Keep current root compatibility intact.
   - No carrier cutover yet.

## Hard Boundaries

- No source-pool bulk copy.
- No `ION_Developement` rename.
- No sibling-root move.
- No runtime/current-state JSON migration.
- No GPT Builder, Actions/MCP, service, deployment, or Git push without explicit approval.
