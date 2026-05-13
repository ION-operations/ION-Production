# AIMOS Echo Forge Cluster Capability Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_10_2026-03-14`
Status: evidence-only comparative capability analysis

## Comparative Table

| Comparison axis | `echo-forge-loop/` | `echo-forge-loop/server/` | `echo-forge-loop/supabase/` |
| --- | --- | --- | --- |
| User or operator interaction role | Primary user-facing chat and mission-control dashboard with panel navigation across chat, research, runs, memory, journal, cognition, trust, persona, evolution, and context | Indirect operator surface through local service endpoints, launch scripts, health checks, research routes, and IDE-style file or terminal APIs rather than a rich browser shell | Minimal direct operator UI; primarily a backend surface reached through edge functions and data access rather than a standalone interface |
| Backend or service role | Consumes backend services, streams events into the UI, and coordinates client-side state, but is not the main compute engine | Strongest local service runtime in the cluster: runs the 9-phase cognition pipeline and exposes chat, research, evolution, filesystem, and terminal endpoints | Strongest hosted service path in the cluster: packages cloud edge functions for chat, AI step flows, auditing, verification, journal, and research |
| Persistence or cloud role | Can use Supabase or localStorage depending on configuration; client layer mainly reads and renders persisted state | Maintains local JSON memory for reflections, rules, knowledge, and run traces inside `server/memory/` | Owns the deepest durable persistence model through SQL migrations and edge-function writes into events, tasks, journal, context, knowledge, witness, and plan-related tables |
| Portability or deployment dependence | Most portable as a browser app, but still depends on environment variables and either a local or cloud backend path | Portable to local machines with Python and provider tooling, but tied to FastAPI runtime and local model-provider setup | Most deployment-dependent because it assumes a Supabase project, secrets, edge runtime, and remote database state |
| Relationship to the larger Echo Forge loop | Umbrella product surface that renders and organizes the whole Echo Forge experience for the operator | Local execution core that drives the loop directly when the app points `VITE_CHAT_URL` at the local server | Hosted persistence and cloud-function variant that lets the same loop run against a managed backend and database spine |

## Direct Comparative Reading

### `echo-forge-loop/` vs `echo-forge-loop/server/`

- `echo-forge-loop/` is the visible product shell and mission-control renderer.
- `echo-forge-loop/server/` is the local engine that actually runs and streams the cognition loop.

### `echo-forge-loop/` vs `echo-forge-loop/supabase/`

- `echo-forge-loop/` gives the operator the live interface and dashboard.
- `echo-forge-loop/supabase/` gives the cluster the hosted function and durable data surface.

### `echo-forge-loop/server/` vs `echo-forge-loop/supabase/`

- `echo-forge-loop/server/` is the stronger local execution and IDE-service path.
- `echo-forge-loop/supabase/` is the stronger cloud persistence and hosted backend path.

## Net Comparative Answer

1. `echo-forge-loop/` is the strongest operator-facing product surface in the cluster.
2. `echo-forge-loop/server/` is the strongest local execution and streaming service surface in the cluster.
3. `echo-forge-loop/supabase/` is the strongest hosted persistence and edge-function surface in the cluster.

These are local comparative role answers only. They do not collapse the cluster into one generic app label or imply a merger path.
