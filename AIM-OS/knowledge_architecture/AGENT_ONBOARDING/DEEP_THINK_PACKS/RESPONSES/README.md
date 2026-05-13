# Deep Think Responses — Storage

**Purpose:** Store all **responses from Gemini 3 Deep Think** so we can reuse advice, trace decisions, and avoid losing context across sessions.

---

## Where to save

- **Folder:** `knowledge_architecture/AGENT_ONBOARDING/DEEP_THINK_PACKS/RESPONSES/`
- **One file per response.** Paste or export the full Deep Think reply into a new file here.

---

## Naming convention

Use a short, consistent pattern so responses are easy to find and sort:

- **Format:** `YYYY-MM-DD_PackN_topic-summary.md`  
  or: `YYYY-MM-DD_topic-summary.md` if the pack isn’t obvious.

**Examples:**

- `2026-02-22_Pack1_two-tier-container-validation.md`
- `2026-02-23_Pack2_phase3-soft-boundary-design.md`
- `2026-02-24_Pack4_roadmap-order-and-risks.md`
- `2026-02-25_goals-prioritization-2-week-focus.md`

Use lowercase, hyphens for spaces. Keep the topic summary to a few words.

---

## What to put in the file

1. **Optional header (frontmatter or first lines):**
   - Date of the Deep Think run
   - Pack used (e.g. Pack 1, Pack 4)
   - One-line summary of the ask
2. **Full response:** Paste the complete Deep Think reply (markdown or plain text).
3. **Optional footer:** Any follow-up you did (e.g. “Implemented Step 1 and 2 on 2026-02-26”) or link to code/PR.

---

## Index of responses

Keep a running list in **RESPONSES_INDEX.md** (in this folder) so we can scan all responses without opening each file. When you add a new response file, add one line to the index (date, filename, pack, one-line summary).

See: [RESPONSES_INDEX.md](RESPONSES_INDEX.md)
