# Gemini Deep Think — Context Prep Guide

**Purpose:** Prepare **context packs** for **Gemini Deep Think** when working via AI chat.  
**Constraint:** **10 files per upload** per prompt.  
**Critical:** Deep Think **does not have the project** — only what we give it (uploaded files + user message).  
**Date:** 2026-02-22  
**Status:** Living doc — update as limits or product behavior change.

---

## 1. What Is Gemini Deep Think?

- **Product:** Gemini app’s **reasoning mode** (“Deep Think”) — same UI as chat, but you choose Deep Think before sending.
- **How it works:** You **attach up to 10 files** and type a message. Deep Think reasons over **only** those file contents + your message. Responses can take several minutes.
- **Availability:** Gemini app for **Google AI Ultra** subscribers.
- **Use here:** Second opinion / deep-analysis partner. **No API** — workflow is: we prepare a handoff + file list; user uploads those files in the chat and types their question.

---

## 2. Deep Think Has No Project (Critical)

**Deep Think does not have access to AIM-OS, the repo, or any other context.**

It only sees:
- The **files attached** to that prompt (≤10).
- The **text the user types** (question/task).

So every pack must be **self-contained**. We choose ≤10 **full** documents (or large contiguous excerpts with path/line refs) so that, together with the user’s message, Deep Think has enough to reason. We do **not** assume it can “go look at” other docs or the codebase. We give it everything it needs in the upload list.

---

## 3. The 10-File Limit

- Gemini allows **up to 10 files per prompt** (attach in the same message). We design for **10 max**.
- Each “file” = one logical document: one full .md, one full code file, or one full task brief we write. **Content:** Full, not summarized — because those files are Deep Think’s **only** context for that session.
- If the task needs more than 10 docs, we merge into fewer files or split into multiple sessions (each with its own ≤10-file pack).

---

## 4. What a Context Pack Is

A **context pack** = what we prepare so the user can run one Deep Think session:

1. **Handoff (HANDOFF_*.md):** Task brief + **exact list of files to attach** (paths from repo root). Says what we want Deep Think to do and what each file is. User can paste the handoff into the chat or attach it as one of the 10 files.
2. **File list (≤10):** Repo paths to the documents the user will **upload** in Gemini. Each file = full document (full plan, full overview, full spec) so Deep Think has real context. No “key excerpts” unless we explicitly create one merged doc.
3. **User’s question:** What the user types in the chat (we don’t write this; we suggest it in the handoff).

**Workflow:** User opens Gemini → Deep Think → **attaches** the files from the handoff list (upload) → types question (and optionally pastes/attaches the handoff) → send. Deep Think sees only those files + the message.

---

## 5. Preparing a Pack (Checklist)

### 5.1 Create a HANDOFF_*.md

- **Task:** What we want Deep Think to do (one short paragraph).
- **Files to attach:** Table or list with repo path + one-line purpose. **≤10 files.** Paths relative to repo root so the user can find them.
- **What we need from Deep Think:** Bullet list (e.g. go/no-go, risks, corrections).
- **Constraints (if needed):** e.g. “Single HTML, WebGPU, no build step” so Deep Think doesn’t assume otherwise.

### 5.2 Choose the files

- Each file = **full** document (full plan, full overview, full state). Not summaries.
- If one doc is huge (e.g. 500+ lines), we can use one **large contiguous section** and note in the handoff “attach this section only” with path + line or section name.
- Total: 10 or fewer. Count the handoff as one of the 10 if the user attaches it.

### 5.3 What to avoid

- Do not assume Deep Think has any prior context (project, previous chats, other files). Pack = self-contained.
- Do not exceed 10 files; merge or split sessions.
- Do not list “key excerpts” without providing a single file that contains that content (e.g. we create ONE doc that is “GCM Exec Summary + Architecture + Phase 1” and list that as one file).

---

## 6. Where Packs Live

- **Handoffs:** `knowledge_architecture/AGENT_ONBOARDING/DEEP_THINK_PACKS/` — INDEX.md lists packs; each HANDOFF_*.md has task + file list.
- **Globe sign-off:** HANDOFF_GLOBE_SIGNOFF.md (task + 5–6 files: sign-off plan, T0, T1, weather state, GCM excerpt).
- **Store responses:** `DEEP_THINK_PACKS/RESPONSES/` (see RESPONSES/README.md; update RESPONSES_INDEX.md when adding).
- **This guide:** `knowledge_architecture/AGENT_ONBOARDING/GEMINI_DEEP_THINK_CONTEXT_GUIDE.md`.

---

## 7. References

- Gemini file upload (up to 10 files per prompt): [support.google.com/gemini/answer/14903178](https://support.google.com/gemini/answer/14903178)
- Deep Think: [support.google.com/gemini/answer/16345172](https://support.google.com/gemini/answer/16345172)

---

*Deep Think has no project. Only uploaded files + user message. We prepare the handoff and ≤10 file list so the user can give it everything it needs.*
