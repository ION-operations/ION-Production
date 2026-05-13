# Codex Design Brief - JARVIS Mission Control

**Agent:** Codex  
**Date:** 2026-03-07  
**Status:** Proposal only. Awaiting operator review before build.  
**Round:** Phase 1 - Shell + Mission Control masterpiece page  

---

## 1. Proposal Thesis

Codex proposes a JARVIS Mission Control page built as a **precision operator instrument** rather than a generic dashboard.

The design goal is:

**Make AIM-OS instantly governable to a non-coder sovereign.**

That means the page must let Braden understand, within seconds:
- current system health
- current agent force state
- current mission state
- current approvals and escalations
- current truth quality (`LIVE`, `MOCK`, `OFFLINE`, etc.)

This proposal intentionally does **not** try to build the full app yet.

It proposes:
- a complete shell grammar
- one flagship workspace done to production-grade quality
- a scalable model for later workspace expansion if approved

---

## 2. The Core Design Idea

The page is not arranged like a SaaS analytics dashboard.

It is arranged like a command instrument:

- **top bar** for workspace control, global state, and command access
- **left drawer** for force-local command context
- **main mission surface** for the live situation picture
- **assistant rail** for conversation, context, actions, and evidence
- **bottom drawer** for diagnostics, temporal trace, and event flow

The visual language is:
- matte black
- engraved labels
- recessed telemetry windows
- amber accent only where action or priority demands it
- dense but machined hierarchy

---

## 3. Mission Control Workspace Concept

Mission Control should be the first page because it best proves the JARVIS thesis.

It should answer five operator questions immediately:

1. What is the state of the organism?
2. What is the state of the force?
3. What is happening now?
4. What needs me?
5. What is true versus simulated?

### Proposed Main Surface Zones

#### Zone A - Command Readout Band

A horizontal band of recessed telemetry modules near the top of the main surface showing:
- MCP state
- memory atoms
- active agents
- active missions
- approvals pending
- degraded systems count

These are not decorative stats cards.
They should look like machine telemetry windows.

#### Zone B - Force Picture

Primary central area showing:
- current agent roster
- active callsigns
- state indicators
- workload / mission assignment
- escalated vs idle vs blocked states

This is the heart of the page.
Mission Control must show the force.

#### Zone C - Mission Queue and Attention Stack

A structured list or split-pane view for:
- currently running missions
- queued missions
- blocked missions
- newest escalation items

This should feel like an operations queue, not a Kanban board.

#### Zone D - Truth and Recovery Strip

A dedicated visible area for:
- `LIVE` / `MOCK` / `OFFLINE`
- degraded systems
- last successful sync or poll
- recovery recommendations if degraded

This is essential. The system must tell the truth.

#### Zone E - Activity Chronicle

A dense event strip or chronological module showing:
- recent important events
- agent handoffs
- mission completions
- failures
- approvals

Not a noisy social feed.
A chronicle.

---

## 4. Shell Proposal

### 4.1 Top Bar

Purpose:
- workspace switching
- global command palette access
- operator identity
- clock / sync state
- global system state indicators

Design:
- low-height machined bar
- engraved workspace labels
- one strong amber action
- dense but calm

### 4.2 Left Drawer

Mission Control left drawer should contain:
- Agent Fleet
- Mission Queue
- System Status

These should be vertically stacked or tab-switched with strong hierarchy.

The left drawer is for **local command context**, not random overflow.

### 4.3 Assistant Rail

Role:
- not chat-only
- must be the persistent intelligence rail

Modes:
- Chat
- Context
- Actions
- Memory/Evidence

For Mission Control, the rail should be especially useful for:
- operator questions
- pending approvals
- quick explanation of current degraded states
- related evidence/memory for the selected mission or agent

### 4.4 Bottom Drawer

Purpose:
- diagnostics
- timeline/activity
- problems/events
- debug/telemetry

Mission Control should default this drawer to:
- Activity Chronicle
- Diagnostics

Terminal can exist later, but should not dominate Mission Control by default.

---

## 5. Answers To The 7 Design Questions

### 1. Which workspaces?

Proposal:
- keep **7 primary** workspaces for first production shell

Primary:
- Mission Control
- Dispatch
- Agent Workforce
- Context Lab
- Oracle
- Infra Console
- Builder

Secondary/later:
- Calendar
- Context Graph
- System Atlas
- Session
- Mission Builder

Reason:
- twelve first-class workspaces dilute operational grammar
- seven creates stronger navigation identity

### 2. What panels per workspace?

For Mission Control specifically:
- Left Drawer:
  - Agent Fleet
  - Mission Queue
  - System Status
- Assistant Rail:
  - Chat / Context / Actions / Memory
- Bottom Drawer:
  - Activity Chronicle
  - Diagnostics

### 3. Bottom bar purpose?

It is for:
- diagnostics
- temporal trace
- event/activity flow
- problems/debug

It is not just a terminal dock.

### 4. Navigation model?

Primary:
- top-bar workspace switching
- command palette
- keyboard shortcuts

Codex does **not** recommend deep nested navigation as the primary model.

### 5. Assistant Rail role?

It is the persistent intelligence rail.

Not chat-only.

It should unify:
- operator conversation
- current context
- actions / approvals
- memory / evidence

### 6. Data truth signals?

Every meaningful module should declare:
- `LIVE`
- `CACHED`
- `MOCK`
- `OFFLINE`
- `SPECULATIVE`

This should be embedded in the visual grammar as:
- small status LEDs
- engraved status labels
- occasional strip-level warnings for degraded systems

No large cartoon badges.

### 7. What makes it feel like a precision instrument?

These five things:
- recessed telemetry windows instead of floating cards
- engraved micro-labels and monospace readouts
- material hierarchy with matte black surface depth
- tiny but unmistakable status lights
- no wasted or decorative surface

---

## 6. Information Hierarchy

Mission Control must respect operator attention.

### Primary
- force status
- mission status
- health state
- truth state

### Secondary
- approvals
- recent critical events
- selected entity context

### Tertiary
- deeper diagnostics
- evidence chains
- extended logs

That tertiary material belongs in drawers and rail states, not the central surface.

---

## 7. Data Truth Strategy

The design should make truth state feel native to the hardware language.

Proposal:
- `LIVE` = green micro-indicator + standard contrast readout
- `CACHED` = amber indicator + timestamp
- `MOCK` = engraved amber label inside the module
- `OFFLINE` = dimmed gray readout + explicit failure line
- `SPECULATIVE` = cool blue or ghosted annotation, clearly secondary

This avoids giant warning banners while still making truth explicit.

If a whole subsystem is degraded, then a stronger strip-level warning may appear.

---

## 8. Interaction Model

The shell should feel mechanically coherent:

- top-level workspace switches should reconfigure drawer defaults
- hover states should feel like sensor activation, not generic glow
- primary actions should use amber sparingly
- drawer expansion should feel like instrument compartments opening
- the assistant rail should feel like an intelligence console sliding into attention

Motion should be purposeful and minimal.

---

## 9. Codex Build Boundaries

If approved, Codex will build:
- the shell wrapper
- the Mission Control workspace
- truth-state wiring scaffolds
- responsive behavior for `1280`, `1920`, and `2560+`

Codex will **not** attempt full-workspace completion in this phase.

---

## 10. Risks and Watchpoints

### Risk 1 - Too much panel density

Mitigation:
- keep central surface mission-first
- push deep detail into drawers/rail

### Risk 2 - Beautiful but dishonest surface

Mitigation:
- truth-state system embedded from day one

### Risk 3 - Shell complexity outruns real use

Mitigation:
- Mission Control optimized for five core operator questions only

### Risk 4 - Tournament drift into style contest

Mitigation:
- judge based on governability, not spectacle alone

---

## 11. Why This Proposal Should Advance

This proposal is strong because it:
- matches the tournament laws
- respects the aesthetic brief
- inherits the real shell grammar already present in JARVIS
- narrows the scope correctly
- uses Mission Control to prove the cockpit thesis directly
- prioritizes operator governability over decorative futurism

---

## 12. Approval Request

Codex requests review on:
- workspace set
- Mission Control page selection
- left drawer contents
- bottom drawer default contents
- truth-state presentation
- overall shell direction

If approved, Codex will move to implementation of the shell plus Mission Control page only.
