# NEXT PACKET: M34 Kernel Dependency Expansion

M33 binds the internal ION_VNEXT front door only. M34 should expand the kernel slice only if the operator approves a bounded dependency-closed packet.

Required M34 posture:

- Do not migrate source pools.
- Do not copy runtime/current-state JSON.
- Do not touch private material.
- Do not bind or modify production root shims unless a separate front-door cutover packet authorizes it.
- Identify exact source modules, helper dependencies, tests, and validation before landing.
