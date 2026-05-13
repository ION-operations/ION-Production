# Composer Owns ChatGPT Context

**Braden directive:** Composer takes all discussions as needed for ChatGPT and is responsible for packaging into a zip for easy sending.

---

## Composer's Responsibilities

1. **Gather** — Collect discussion summaries, key decisions, roundtable threads from team
2. **Maintain** — Keep `00_operational_definition.md`, `01_current_truth.md`, `02_canonical_map.md`, `03_next_task.md` current
3. **Package** — Run `powershell -File scripts/package_chatgpt_context.ps1` → creates `context/chatgpt_context_YYYY-MM-DD_HHMM.zip`
4. **Deliver** — Zip at `context/chatgpt_context_YYYY-MM-DD_HHMM.zip` for Braden to send to ChatGPT

---

## Team: Route to Composer

When you have:
- Discussion summaries for ChatGPT
- Key decisions that should inform ChatGPT
- Updates to current truth, canonical map, or next tasks

→ Send to Composer via MCP or `.agent/comms/inbox/composer/`

---

## How Braden Uses It

1. Run `powershell -File scripts/package_chatgpt_context.ps1` (or ask Composer to do it)
2. Get zip from `context/chatgpt_context_*.zip`
3. Send zip / paste contents to ChatGPT
4. ChatGPT responds from pasted truth only
