# AIMOS Control Comms Doctrine Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_13_2026-03-14`
Status: evidence-only comparative doctrine analysis

## Comparative Table

| Comparison axis | `AGENTS.md` | `.agent/STARTUP.md` | `.agent/COMMS_DOCTRINE.md` | `.agent/CONTEXT_CAPSULE_PROTOCOL.md` | `.agent/comms/COMMS_PROTOCOL.md` | `.agent/comms/COMMS_CANONICAL.md` |
| --- | --- | --- | --- | --- | --- | --- |
| Identity and routing role | Strongest host-based identity router; binds host to callsign, lane file, and chat path | Requires identity confirmation but does not resolve host-specific routing by itself | Assumes a stable callsign and enforces its use in every response | No identity-routing role beyond the `CALLSIGN` field inside capsules | Strong on canonical sender IDs and route keys once identity already exists | Uses route names operationally, but does not define the full identity map |
| Startup role | Provides host-specific next-read order and MCP-first behavior, but not the fullest session checklist | Strongest startup gate; gives the ordered pre-work sequence and first-message requirement | Repeats and militarizes startup through the Session Startup Protocol | No broad startup role; only governs PRE/POST capsule use inside a substantive turn | Includes a filesystem comms startup flow, but only for the comms layer | Gives a compact "where to check" startup reminder, not a full boot protocol |
| Message-format or discipline role | Light response control through chat-doc redirection and MCP-first behavior | First-message template only; not a full message-format law | Strongest message-discipline surface through mandatory headers, message types, overwrite law, and chain-of-command rules | Strongest capsule-format law, but limited to capsule structure rather than all responses | Naming-format law for files and IDs, not response-format law for chat text | Minimal posting/checking guidance; no broad response-format law |
| Filesystem or MCP comms role | Strongest MCP-first claim in this family; tells Codex-family lanes to use MCP before text | Defines MCP verification order and fail-closed behavior, then points into inbox/broadcast/status reads | Declares live bus as default when reachable, but does not define the concrete filesystem layout | Capsule storage only; no general comms routing role | Strongest filesystem comms role: source of truth, directory layout, aliases, names, tooling, and identity lock | Strongest minimal comms-flow summary: where to check, where to post, and when to double-post |
| Current-state control role | Redirects active output into dated chat docs and capsules, and carries the freeze block | Requires updating status files and a startup announcement before operating | Requires debriefing and status awareness, but focuses more on behavior than on persistence mechanics | Strongest continuity role for mission/now/must-not/evidence/next handoff inside a turn | Strongest durable current-state mechanics through inbox, handoff, and status-file conventions | Useful as a quick operational reminder, but thinner than the protocol for durable state handling |
| Capsule role | Capsule pilot surface; introduces the requirement and a seven-field shape | No capsule-specific role | No exact capsule format beyond general discipline expectations | Strongest capsule surface by a clear margin; exact header, invariants, oversight, and freeze interaction | Only indirect capsule role through storage conventions and route keys | No capsule role |
| Overlap or conflict tendency | High overlap with almost every sibling: startup, first-response behavior, MCP precedence, and capsule rules | Highest overlap with `AGENTS.md` and `.agent/COMMS_DOCTRINE.md` because all three touch startup and reporting | High overlap with `AGENTS.md` and `.agent/STARTUP.md`; also touches live-bus behavior that intersects with comms docs | Narrow overlap, but exact field set conflicts slightly with the broader pilot wording captured in collision `C-06` | Direct tension with MCP-first surfaces because it states filesystem source-of-truth and MCP-as-accelerator in collision `C-03` | Lower-granularity overlap: compresses protocol and startup guidance into a simpler quick-reference flow |

## Direct Comparative Reading

### `AGENTS.md` vs `.agent/STARTUP.md`

- `AGENTS.md` is strongest at answering who the actor is in this host and what file comes next.
- `.agent/STARTUP.md` is strongest at enforcing the ordered boot sequence once that actor identity is known.
- Collision `C-01` remains real because both surfaces claim early-session precedence from different directions.

### `.agent/STARTUP.md` vs `.agent/COMMS_DOCTRINE.md`

- `.agent/STARTUP.md` is the stronger pre-work gate.
- `.agent/COMMS_DOCTRINE.md` is the stronger in-work and response-format discipline surface.
- Collision `C-08` remains real because first-response expectations exist in both surfaces, not just one.

### `AGENTS.md` and `.agent/COMMS_DOCTRINE.md` vs `.agent/comms/COMMS_PROTOCOL.md`

- `AGENTS.md` and `.agent/COMMS_DOCTRINE.md` lean toward MCP as the live or first transport when available.
- `.agent/comms/COMMS_PROTOCOL.md` is the strongest filesystem-persistence law and explicitly states that `.agent/comms/` files are the source of truth.
- Collision `C-03` remains the sharpest transport-precedence ambiguity in this family.

### `.agent/comms/COMMS_PROTOCOL.md` vs `.agent/comms/COMMS_CANONICAL.md`

- `.agent/comms/COMMS_PROTOCOL.md` is the detailed mechanics layer: route keys, aliases, names, status layout, tooling, and identity locks.
- `.agent/comms/COMMS_CANONICAL.md` is the compressed operator-flow layer: where to check, where to post, and when to post in more than one place.
- These two surfaces are adjacent rather than identical; the protocol is deeper, the canonical doc is simpler.

### `AGENTS.md` vs `.agent/CONTEXT_CAPSULE_PROTOCOL.md`

- `AGENTS.md` is the broader control surface that introduces capsules into the main operating law.
- `.agent/CONTEXT_CAPSULE_PROTOCOL.md` is the stronger exact specification once capsule use is already in scope.
- Collision `C-06` remains a narrow but real field-set mismatch because lane instructions add an `MCP:` line while the core capsule spec defines seven required fields.

## Net Comparative Answer

1. `AGENTS.md` anchors identity routing and lane binding.
2. `.agent/STARTUP.md` anchors session boot discipline.
3. `.agent/COMMS_DOCTRINE.md` anchors response discipline and chain-of-command behavior.
4. `.agent/CONTEXT_CAPSULE_PROTOCOL.md` anchors capsule invariants and drift detection.
5. `.agent/comms/COMMS_PROTOCOL.md` anchors durable filesystem comms mechanics and identity-safe routing.
6. `.agent/comms/COMMS_CANONICAL.md` anchors the shortest high-clarity operational comms flow.

These are comparative role answers only. They do not select final canon winners or collapse the rule layer into one file.
