# ION Custom GPT Context Mesh Orchestration

## Entry rule

Before substantive work in a folder, mount the nearest
`ION_CONTEXT_CAPSULE.yaml`, then parent capsules up to root, then the active
continuity package. Do not rely on chat memory alone.

## Merge order

1. current operator instruction;
2. root authority files (`AGENTS.md`, repo authority, release locks);
3. local folder capsule;
4. parent folder capsules;
5. mounted continuity/context packages;
6. historical capsules;
7. weak model recall.

## Conflict rule

A stale local capsule cannot override a current receipt or root authority. The
carrier must report conflicts and either block or create a repair packet.

## Dogfood route

The v4.7 route is:

`MOUNT_LOCAL_CAPSULES -> BUILD_CONTEXT_MESH -> BUILD_CONTEXT_PACKAGE -> EXPORT_TRANSFER_PACKAGE -> REMOUNT_SIMULATION -> VALIDATE -> RECEIPT -> PERSONA_RETURN_GATE`.

The final visible reply must include compact telemetry, a package/receipt
summary, and a Persona-rendered explanation of what was actually built.
