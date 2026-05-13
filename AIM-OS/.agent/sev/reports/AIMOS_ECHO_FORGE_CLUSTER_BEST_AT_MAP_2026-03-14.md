# AIMOS Echo Forge Cluster Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_10_2026-03-14`
Status: evidence-only comparative answer map

## Best-At Answers

| Surface | What it appears best at locally | Where it seems narrower than siblings | Unique value preserved locally | Direct evidence |
| --- | --- | --- | --- | --- |
| `echo-forge-loop/` | Best at presenting the full Echo Forge organism as a user-facing cognition product with chat, mission control, and broad inspection panels in one browser shell | Narrower than `echo-forge-loop/server/` in direct execution and service-endpoint breadth; narrower than `echo-forge-loop/supabase/` in durable backend persistence and hosted cloud state | Preserves the richest operator-facing view of the loop, including chat flow, run control, and multi-panel inspection across memory, journal, knowledge, trust, evolution, and context | `README.md` describes the 9-phase mission-control UI and 25+ dashboard panels; `docs/ECHO_FORGE_LOOP_APP_DOCUMENTATION.md` maps the tabbed shell and chat flow; `src/` and `src/components/` counts show the largest visible UI surface in the cluster |
| `echo-forge-loop/server/` | Best at running the Echo Forge loop locally and exposing it as a streaming service with development-side capabilities beyond chat alone | Narrower than `echo-forge-loop/` in operator-facing UI breadth; narrower than `echo-forge-loop/supabase/` in hosted persistence depth and cloud deployment continuity | Preserves the clearest privacy-local and development-local execution path, including the same `aim-chat` contract plus health, research, evolution, filesystem, and terminal endpoints | `server/main.py` exposes `/chat`, `/functions/v1/aim-chat`, `/research`, `/health`, filesystem, terminal, and evolution routes; `server/aim_chat_loop.py` implements local 9-phase execution and memory/traces in `server/memory/` |
| `echo-forge-loop/supabase/` | Best at giving Echo Forge a cloud-native function and persistence backbone for hosted runs, evidence, and long-lived state | Narrower than `echo-forge-loop/` in user-facing interaction and narrower than `echo-forge-loop/server/` in local IDE-style service breadth | Preserves the remote schema and edge-function surface that can store and connect events, tasks, journal entries, context, knowledge, witnesses, plans, and other run artifacts over time | `supabase/config.toml` declares the project and edge functions; `supabase/functions/aim-chat/index.ts` writes atoms, witnesses, plans, snapshots, and evidence-graph records; migrations define the durable table surface for the organism |

## Net Comparative Answer

1. `echo-forge-loop/` appears best at the operator-facing product shell.
2. `echo-forge-loop/server/` appears best at local execution and streaming service delivery.
3. `echo-forge-loop/supabase/` appears best at hosted persistence and cloud-function continuity.

The map stays comparative. It does not rank one Echo Forge surface as the canon winner.
