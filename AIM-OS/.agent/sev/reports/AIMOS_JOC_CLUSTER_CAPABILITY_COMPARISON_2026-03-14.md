# AIMOS JOC Cluster Capability Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_07_2026-03-14`
Status: evidence-only comparative capability analysis

## Comparative Table

| Comparison axis | `packages/joc/` | `IDE/` | `packages/ide_chat_app/` | `packages/joc-tournament/` |
| --- | --- | --- | --- | --- |
| Operator interaction model | Multi-workspace cockpit with pages for dashboard, dispatch, session, vault, diagnostics, infrastructure, calendar, mission-building, oracle, and synthesizer flows | Tabbed desktop control shell with Dashboard, Services, Agents, Console, Vault, and SEER tabs | Drawer-heavy dashboard and development environment with chat, agent-management, orchestration, telemetry, tooling, and file/editing surfaces | Competitor and heritage surface for studying, comparing, and building JOC variants rather than serving as the everyday operator cockpit |
| Runtime / host relationship | Browser Vite app at `5011` with optional Electron shell; directly wired to BAS and MCP-facing services | Tauri desktop wrapper that points at live local services on `5001`, `5002`, and `5011` | Electron app with React UI; onboarding docs also describe Cursor-extension-aware rendering and MCP calls through the extension command server on `5001` | Launch and build arena that points competitors back to the JOC runtime target on `5011`; not itself the main host shell |
| System visibility or telemetry role | Strong on operational visibility through session, dispatch, diagnostics, comms, compute, GPU, and vault pages | Strongest on coarse service-state monitoring and credential-vault visibility from one compact shell | Strongest on rich internal telemetry and collaboration surfaces through Lucid Orchestrator, message monitoring, daemon services, analytics, and real-time collaboration services | Strongest on historical and comparative visibility into design laws, prototypes, and alternative build approaches |
| Planning / chat / dashboard / experiment emphasis | Most balanced toward mission control and operations workflow | Most focused on service control, credential handling, and command-console operations | Most focused on chat, orchestration, AI-development workflow, collaboration, and dashboard experimentation | Most focused on experimentation, scoring, build comparison, and design-heritage study |
| Portability or host coupling | Moderately portable as a browser app, but operationally coupled to BAS, MCP, and the existing JOC service contract | Most tightly coupled to a local desktop host and fixed local ports; small shell, strong environment assumptions | Coupled to Electron and to the local command-server/extension path for MCP-backed features; broader UI surface than `IDE/` | Conceptually coupled to JOC canon and launch target, but not tightly bound to one runtime process because it is primarily a build/reference corpus |

## Direct Comparative Reading

### `packages/joc/` vs `IDE/`

- `packages/joc/` is the deeper operational application surface.
- `IDE/` is the thinner desktop wrapper that watches and controls the surrounding service plane.

### `packages/joc/` vs `packages/ide_chat_app/`

- `packages/joc/` concentrates on mission-control structure and operator workflows.
- `packages/ide_chat_app/` concentrates more heavily on chat, collaboration, orchestration, and experimentation inside a development-environment frame.

### `packages/joc/` vs `packages/joc-tournament/`

- `packages/joc/` is the runtime shell being shaped and extended.
- `packages/joc-tournament/` is the comparative design and build corpus that studies what that shell could become.

### `IDE/` vs `packages/ide_chat_app/`

- `IDE/` is narrower, more service-ops-oriented, and more explicitly wired to vault/SEER/service health actions.
- `packages/ide_chat_app/` is broader in UI depth and AI-development features, but also carries a larger, more complex application surface.

### `packages/ide_chat_app/` vs `packages/joc-tournament/`

- `packages/ide_chat_app/` is a live application surface.
- `packages/joc-tournament/` is a comparative experiment and heritage surface.

### `IDE/` vs `packages/joc-tournament/`

- `IDE/` is a compact operator shell around live services.
- `packages/joc-tournament/` is a design and build framework for comparing JOC directions.
