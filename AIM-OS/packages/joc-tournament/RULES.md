# JARVIS Tournament Rules

**Status:** active local tournament rules
**Purpose:** keep the JARVIS tournament focused on building the best operator cockpit over AIMOS, not merely the prettiest screen.

---

## 1. What JARVIS Is

JARVIS is the operator and development cockpit for AIMOS.

It exists to let a non-coder sovereign:
- see the force
- inspect truth
- steer agents
- recover from failure
- understand system state without reading the whole repo

It is not the AIMOS runtime itself.

---

## 2. What JARVIS Is Not

JARVIS is not:
- a generic dashboard
- a page collection with nicer chrome
- a reskin of the current shell
- a mock-heavy fantasy detached from the backend

---

## 3. Non-Negotiable Laws

### Law 1 - Force visibility first

A winning build must make the workforce and the system legible:
- agent status
- mission flow
- approvals
- comms state
- system health

If it looks premium but hides the force, it loses.

### Law 2 - Data truth must be explicit

Every meaningful surface must declare whether it is:
- `LIVE`
- `CACHED`
- `MOCK`
- `OFFLINE`
- `SPECULATIVE`

No mock data may masquerade as runtime truth.

### Law 3 - Workspace logic must be real

Workspace switching must materially reconfigure the cockpit.

Do not ship one shell with different labels.

### Law 4 - Layout must serve operations

The layout should help the operator:
- dispatch
- inspect
- recover
- correlate
- adjudicate

Dead space, ornamental density, or aesthetic noise count against the build.

### Law 5 - AIMOS layer discipline

The build must respect the difference between:
- `core`
- `runtime`
- `cockpit`
- `product`
- `bootstrap-only`

JARVIS belongs to the `cockpit` layer.

### Law 6 - Degraded mode matters

The UI must still make sense when MCP or live systems are unavailable.

A good cockpit reveals failure clearly instead of collapsing into ambiguity.

### Law 7 - Premium does not mean vague

"Billion-dollar ops center" means:
- confidence
- clarity
- materials
- hierarchy
- motion with purpose

Not neon clutter or sci-fi cosplay.

---

## 4. Required Deliverables Per Competitor

Each competitor should provide:
- one build directory under `packages/joc-tournament/builds/<agent>/`
- one short design brief
- one screenshot set per round
- one truth map of live vs mock surfaces
- one note explaining main workspace logic

---

## 5. Tournament Format - Masterpiece Gate

The tournament should **not** begin with full-app implementation.

Phase 1 is:
- one complete shell wrapper
- one masterpiece workspace/page
- enough drawer and rail behavior to prove the shell grammar
- enough mock/live placeholders to show the real intended operating model

This means each competitor must build:
- Top bar / workspace switching
- Left drawer behavior
- Right-side assistant rail behavior
- Bottom diagnostic strip or drawer behavior
- one fully realized primary page

They should **not** try to finish every workspace before review.

### Phase 1 Required Package

Each competitor must submit:
- one shell implementation
- one primary page implementation
- one design brief
- one truth map
- one "what I would build next" note
- screenshots for `1280`, `1920`, and `2560+`

### Phase 1 Review Gate

After Phase 1, the operator reviews proposals and decides:
- approve for continuation
- request redesign
- cherry-pick ideas into a merged direction

No competitor should assume they are building the whole production app in one uninterrupted sweep.

---

## 6. Page Selection Rule

The default recommended Phase 1 page is:
- `Mission Control`

Why:
- it is the clearest expression of JARVIS as cockpit
- it exposes force visibility, truth signaling, system health, and layout intelligence immediately
- it is the easiest page for the operator to judge at a glance

Alternative page choices are allowed only if the competitor explicitly argues why that page better proves the JARVIS thesis.

---

## 7. What Phase 1 Must Prove

The Phase 1 submission must prove:
- the shell feels real
- the chosen page feels production-grade
- the operator can understand the system quickly
- the build knows the difference between live, mock, and offline truth
- the layout uses width and drawers intelligently

If it cannot prove those, more pages will not save it.

---

## 8. What Should Win

The winning build should feel like:
- the operator can actually run AIMOS from it
- the system is telling the truth
- the layout understands work
- the UI belongs to a real intelligence cockpit

If the tournament produces that, it is a success.
