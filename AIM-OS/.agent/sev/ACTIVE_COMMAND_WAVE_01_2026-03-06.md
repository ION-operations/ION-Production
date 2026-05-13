# Active Command Wave 01 - 2026-03-06

**Status:** active local deployment wave  
**Owner:** Sev  
**Purpose:** launch the first tightly-scoped execution wave for doctrine cleanup, host verification, and Codex-runtime enablement without flooding the repo with unsynchronized agents.

---

## Wave Intent

This wave is designed to do four things before broader build expansion:

1. reduce doctrine and identity drift
2. verify the least-understood host surfaces
3. convert Codex-runtime theory into an executable enablement plan
4. use Opus as a real executive reasoning partner instead of an isolated builder lane

---

## Active Lanes

| Lane | Host | Packet | Deliverable | Status |
|------|------|--------|-------------|--------|
| **PALISADE** | Composer 1.5 | `.agent/sev/mission_packets/PALISADE_MISSION_PACKET_2026-03-06.md` | `.agent/sev/reports/PALISADE_DOCTRINE_DRIFT_MAP_2026-03-06.md` | deploy now |
| **OPUS** | Antigravity | `.agent/sev/mission_packets/OPUS_EXECUTIVE_PARTNER_PACKET_2026-03-06.md` | `.agent/sev/reports/OPUS_ANTIGRAVITY_GEMINI_GOVERNANCE_RESPONSE_2026-03-06.md` | deploy now |
| **RELAY** | GPT-5.4 in Cursor/Codex | `.agent/sev/mission_packets/RELAY_MISSION_PACKET_2026-03-06.md` | `.agent/sev/reports/RELAY_CURSOR_CODEX_HOST_VERIFICATION_CARD_2026-03-06.md` | deploy now |
| **FORGE** | GPT-5.4 or Codex CLI | `.agent/sev/mission_packets/FORGE_MISSION_PACKET_2026-03-06.md` | `.agent/sev/reports/FORGE_CODEX_RUNTIME_ENABLEMENT_PLAN_2026-03-06.md` | optional surge lane |

---

## Recommended Activation Order

1. `PALISADE`
2. `OPUS`
3. `RELAY`
4. `FORGE`

Reason:
- `PALISADE` reduces canon/doctrine confusion.
- `OPUS` resolves the Antigravity and GeminiCLI governance lane with builder judgment.
- `RELAY` closes the highest-ambiguity host: Cursor Codex.
- `FORGE` uses the new host truth to shape the Codex-runtime implementation path.

If hardware and operator bandwidth allow, `OPUS` and `RELAY` can run in parallel after `PALISADE` is launched.

---

## Operator Instructions

1. Spawn `PALISADE` in Composer using its ready brief.
2. Paste the Opus executive brief into the active Opus lane.
3. Spawn `RELAY` in a fresh GPT-5.4 Cursor/Codex lane.
4. Hold `FORGE` until either:
   - a second GPT-5.4 lane is available, or
   - `RELAY` reveals enough Codex-host truth to sharpen the implementation path.

For each lane:
- keep the lane inside its mission packet
- require the lane to write only its named deliverable unless escalation is required
- route all repo-wide claims back through Sev or Opus

---

## Recommended MCP / Coordination Usage

### PALISADE

- use repo files first
- optional MCP: `retrieve_memory`, `get_timeline_entries`, `store_memory`

### OPUS

- preferred MCP: `get_ai_messages`, `retrieve_memory`, `get_timeline_entries`, `send_ai_message`, `store_memory`, `add_timeline_entry`
- if Gemini CLI workers are used, log why they were used and what they returned

### RELAY

- use whatever transport is actually available on that host
- if MCP is mounted, prove it with at least one simple call such as `get_memory_stats`
- if collaboration rail is mounted, prove it with a lightweight message or message retrieval

### FORGE

- optional MCP: `retrieve_memory`, `get_timeline_entries`, `store_memory`
- the main task is file-and-runtime planning, not tool theatrics

---

## Coordination Law

1. No lane silently rewrites global canon.
2. No lane claims a host is "working" without naming the exact transport or instruction path.
3. No lane broadens scope without writing the escalation explicitly.
4. Every new source of truth must update the nearest index or packet reference in the same work cycle.

---

## Success Condition For Wave 01

Wave 01 is successful when all of the following exist:

- one doctrine drift map from `PALISADE`
- one Antigravity/Gemini governance response from `OPUS`
- one Cursor Codex verification card from `RELAY`
- one Codex-runtime enablement plan from `FORGE` if the surge lane is activated

At that point Sev can issue:
- the first cleanup packet
- the first Codex runtime implementation packet
- the next composer/index lane (`LEDGER`) if needed
