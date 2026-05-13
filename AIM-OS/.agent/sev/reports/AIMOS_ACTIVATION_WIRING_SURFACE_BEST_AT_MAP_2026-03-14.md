# AIMOS Activation-Wiring Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_22_2026-03-14`

This map answers what each activation-and-wiring family appears best at locally.
It does not select a final activation canon.

| Surface family | Best at locally | Narrower than siblings where | Unique activation or wiring value preserved |
| --- | --- | --- | --- |
| Startup or runbook surfaces | Best at stating the intended startup order, fallback law, and operator recovery flow | They are weaker than scripts, bridge code, and probes at proving that the host is actually started or reachable | They preserve the clearest human-readable activation doctrine |
| Bootstrap or control-script surfaces | Best at actually causing bridge recovery and checking bridge readiness | They are weaker than host clients at expressing per-host consumption shape and weaker than live probes at proving every dependent capability | They preserve the concrete operational path from doctrine to restart, test, and ensure behavior |
| Bridge or server surfaces | Best at defining the real transport endpoints and protocol shapes AIM-OS makes available | They are weaker than live probes at proving which surface is active right now and weaker than host clients at showing host-specific consumption behavior | They preserve the actual transport and endpoint machinery behind bridge readiness |
| Host-adapter or client surfaces | Best at showing how concrete hosts try to consume MCP or MCP-backed state | They are weaker than control scripts at global recovery and weaker than live probes at proving present reachability | They preserve the most specific picture of host-by-host wiring behavior |
| Live readiness probe surfaces | Best at proving what activation and dependent readiness look like on this host right now | They are weaker than runbooks and scripts at prescribing recovery and weaker than server code at expressing total transport breadth | They preserve the freshest constraint on every other activation surface |

## Best-At Answer

- Startup/runbook surfaces are best at telling AIM-OS how activation should happen.
- Bootstrap/control scripts are best at making AIM-OS activation happen.
- Bridge/server surfaces are best at exposing where AIM-OS transport actually lives.
- Host-adapter/client surfaces are best at showing how AIM-OS hosts actually try to connect.
- Live readiness probes are best at proving what AIM-OS activation looks like right now on this host.

## Local Constraint

No single activation-and-wiring family stands alone as total truth on this host:

- startup prose can drift from active routing details,
- control scripts can prove bridge readiness without proving subsystem health,
- server surfaces can define multiple endpoint shapes at once,
- host clients do not all target the same path,
- and live readiness can be healthy at the bridge while dependent capabilities remain uneven.
