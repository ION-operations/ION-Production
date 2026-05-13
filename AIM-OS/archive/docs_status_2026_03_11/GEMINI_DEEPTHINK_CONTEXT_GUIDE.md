# Gemini Deep Think — What It Is and How We Use It

**Purpose:** Use Gemini Deep Think for complex reasoning. This doc explains what Deep Think is, **how it gets context** (only what you give it), and how we prepare **context packages** so you can use it effectively.

**Audience:** Braden (systems architect). No coding assumed.

---

## 1. What Is Gemini Deep Think?

**Deep Think** is Gemini’s **advanced reasoning mode** in the Gemini app. You use it like a chat: you attach files and type a message; Deep Think spends more time reasoning before answering.

- **Where:** [gemini.google.com](https://gemini.google.com). Click **Deep Think** (then Submit), not regular send.
- **Requirements:** Signed in, 18+, **Google AI Ultra** (or Ultra for Business). Experimental.
- **Wait:** Responses can take several minutes. You can leave and get a notification when ready.

---

## 2. How Deep Think Gets Context (Critical)

**Deep Think is an AI chat. It does not have your project.**

It only sees:
1. **The files you attach** (upload) to that message — up to **10 files per prompt**.
2. **The text you type** in the chat (your question or task).

It does **not** see your repo, your other docs, or any previous chats unless you re-attach or re-paste. So every time you use it, we must give it **everything it needs inside those ≤10 files + your message**. The context package is that set of files (and a clear task/question) so that the session is **self-contained**.

---

## 3. The 10-File Upload Limit

- In Gemini you can attach **up to 10 files** in the same prompt (exact limit may vary by product; we design for **10 max**).
- Each file = one document (e.g. one .md, one .txt, one .pdf). Full content — we don’t trim to summaries, because Deep Think has nothing else. Each file should be **complete** (full plan, full overview, etc.) so it can reason.
- If the task needs more than 10 docs, we merge some into fewer files or split into multiple Deep Think sessions.

---

## 4. What a Context Package Is

A **context package** is what we prepare so you can use Deep Think for a specific task:

1. **A handoff** (task brief): Short doc that says who you are, what you want Deep Think to do, and **which files to attach**. You can paste the handoff into the chat or attach it as file 1.
2. **A list of ≤10 files** to **upload** from the repo (paths we give you). Those files are the **only** project context Deep Think will see. We choose full documents — full plan, full overview, full state — not summaries.
3. **Your question** — what you type in the chat (e.g. “Should I approve the full plan or hold section 5? Risks?”).

**Workflow:** Open Gemini → Deep Think → **attach** the files from the list (upload) → type your question (and optionally paste the handoff so Deep Think knows the task) → send. Deep Think reasons over **only** those file contents + your message.

---

## 5. Where We Prepare Packs

- **Handoffs and file lists:** `knowledge_architecture/AGENT_ONBOARDING/DEEP_THINK_PACKS/` — INDEX.md lists all packs; each **HANDOFF_*.md** has the task and the exact **files to attach** (≤10).
- **Globe sign-off pack:** [HANDOFF_GLOBE_SIGNOFF.md](../knowledge_architecture/AGENT_ONBOARDING/DEEP_THINK_PACKS/HANDOFF_GLOBE_SIGNOFF.md) — task + list of 5–6 files to upload (sign-off plan, T0, T1, weather state, GCM excerpt).
- **This guide:** `docs/GEMINI_DEEPTHINK_CONTEXT_GUIDE.md`.
- **Agent guide (same rules):** `knowledge_architecture/AGENT_ONBOARDING/GEMINI_DEEP_THINK_CONTEXT_GUIDE.md`.

**To get a new pack:** Ask in Cursor (e.g. “Prepare a Deep Think context package for [topic]: handoff + list of ≤10 files to upload.”). We’ll add a HANDOFF_*.md and list the repo files to attach. We do **not** give Deep Think access to the project — we give it **those files only**.

---

## 6. References

- Use Deep Think: [support.google.com/gemini/answer/16345172](https://support.google.com/gemini/answer/16345172)
- Upload files in Gemini (up to 10 per prompt): [support.google.com/gemini/answer/14903178](https://support.google.com/gemini/answer/14903178)

---

*Deep Think has no project. Only what you give it: up to 10 uploaded files + your message. We prepare the handoff and file list so that’s enough.*
