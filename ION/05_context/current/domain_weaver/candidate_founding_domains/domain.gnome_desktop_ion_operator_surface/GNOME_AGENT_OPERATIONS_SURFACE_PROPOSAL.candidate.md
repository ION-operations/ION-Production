# GNOME ION Agent Operations Surface — Candidate Proposal

```yaml
schema_id: ion.domain.gnome_agent_operations_surface_proposal.v0_1_candidate
packet_id: PCKT-GNOME-ION-AGENT-OPERATIONS-SURFACE-PROPOSAL-20260724
owner_domain_id: domain.gnome_desktop_ion_operator_surface
issued_by_domain: domain.domain_mitosis_and_agent_society_formation
generated_at: "2026-07-24T14:53:00Z"
status: candidate_phase_a_discovery_authorized
workflow_state: routed_for_review
review_owner_domain_id: domain.artifact_provenance_and_gate_legitimacy
bounded_review_packet: ION/05_context/current/domain_weaver/candidate_founding_domains/domain.artifact_provenance_and_gate_legitimacy/receipts/PCKT-GNOME-OPS-SURFACE-PHASE-A-REVIEW-20260804.candidate.yaml
reassignment_ref: ION/05_context/current/domain_weaver/candidate_founding_domains/domain.gnome_desktop_ion_operator_surface/GNOME_PROPOSAL_REVIEW_REASSIGNMENT.candidate.yaml
void_operator_seat_gate_retired: true
carrier: cursor_agent
model: composer-2.5
```

## 1. Domain evolution decision

**Decision:** mitosis new child domain `domain.gnome_desktop_ion_operator_surface` under `domain.user_interface_visualization_and_operator_experience`.

**Rationale:** JOC cockpit (`ION/08_ui/joc_cockpit_shell/`) is web-based operator UX. GNOME Shell extension surfaces are desktop-native, lifecycle-distinct, and require platform-specific specialists. Folding agent operations into runtime_carrier or lead Steward would overload service domains with presentation law.

**Not chosen:**
- Evolve only `user_interface_visualization_and_operator_experience` in place — scope mixes web cockpit and GNOME Shell without dedicated society.
- New fourth root domain — unnecessary; mitosis child with explicit peer relationships is sufficient.

## 2. Candidate domain charter and boundaries

| Owns | Does not own |
|------|----------------|
| GNOME top-bar and popover UX | systemd unit lifecycle |
| Agent hierarchy projection layout | MCP transport internals |
| Importance ranking and aggregation display | Action gateway admission policy |
| Attach/focus/detach terminal UX | Goal scheduler implementation |
| Desktop incident attention cues | Queue drain execution |
| Connection panel refresh cadence | Registry promotion |

Charter path: `candidate_founding_domains/domain.gnome_desktop_ion_operator_surface/domain.gnome_desktop_ion_operator_surface.domain.candidate.yaml`

## 3. Specialist roles, mounts, and activation plan

| Role | Responsibility | Mount | Carrier | Activation phase |
|------|----------------|-------|---------|------------------|
| `role.gnome_shell_extension_architect` | Shell 42 constraints, extension.js, stylesheet, metadata | `role_gnome_shell_extension_architect__domain_gnome_desktop_ion_operator_surface` | Composer 2.5 | Phase A proposal mockup |
| `role.operator_information_architect` | two-row layout, fallbacks, scalable ranking UX | `role_operator_information_architect__domain_gnome_desktop_ion_operator_surface` | Composer 2.5 | Phase A |
| `role.desktop_session_attach_controller` | detached PTY attach/focus/detach law | `role_desktop_session_attach_controller__domain_gnome_desktop_ion_operator_surface` | Composer 2.5 | Phase B |
| `role.runtime_health_semanticist` | truth dimension mapping, no cosmetic health | reuse `role.runtime_cartographer` peer read | Composer 2.5 | Phase A discovery |
| `role.hierarchy_projection_cartographer` | domain tree and relationship rollups | reuse `role.vizier` peer read | Composer 2.5 | Phase A |
| `role.autonomous_loop_steward` | goal/wakeup feed consumer | `role_autonomous_loop_steward__domain_local_worker_scheduling_and_autonomous_loop` | Composer 2.5 | Phase B |
| `role.context_cartographer` | continuity freshness witnesses | existing mount peer | Composer 2.5 | Phase A |
| `role.comms_cartographer` | incident and blocker routing display | existing mount peer | Composer 2.5 | Phase A |

**Activation sequence:**
1. Materialize GNOME domain folder + `.ion/` capsule (MASON/kernel mount lane).
2. Spawn Phase A proposal workers (Composer 2.5) — bounded discovery only.
3. `domain.artifact_provenance_and_gate_legitimacy` bounded review packet (PCKT-GNOME-OPS-SURFACE-PHASE-A-REVIEW-20260804) routes Phase A only; Phase B GNOME implementation remains gated by discovery receipts, not operator seats.

## 4. UX and information architecture

### Top-bar summary (two-row when space permits)

**Row 1:** highest-attention agent short name · owning domain · attention badge  
**Row 2:** goal/packet id · status verb · carrier class · freshness age

**One-row fallback:** `ATTN: <agent> · <domain> · <status> · +N`  
**Narrow fallback:** icon + count + worst severity color (no name churn animation)

### Expanded popover

Sections: Hierarchy tree · Active · Waiting · Blocked · Stale · Recent returns · Services · Incidents · Search/filter/pin

### Detached terminal law (UX)

- Open terminal → attach/focus existing detached session if present; else spawn via autonomous loop steward.
- Close terminal → detach only; receipt emitted.
- Stop/cancel/restart → action-admission modal with receipt path preview.

## 5. Runtime / session / control-plane architecture

```
[Canonical stores]
  GOAL_REGISTRY.candidate.json          ← local_worker_scheduling
  worker_shift/leases/                  ← runtime truth
  ACTIVE_CARRIER_TURN_PACKET.json       ← orchestration truth
  DOMAIN_FIELD_COORDINATE_INDEX         ← hierarchy truth
  control.py status JSON                ← connection truth

        ↓ event bus + 30s bounded poll fallback

[GNOME projection layer]              ← gnome_desktop_ion_operator_surface
  extension.js top-bar + popover
  importance ranker (read-only)
  attach controller API

        ↓ optional observer

[gnome-terminal / Ptyxis attach view]   ← not lifecycle owner
```

**Truth dimensions exposed independently:** registered · mounted · continuity_loaded · process_alive · turn_running · goal_active · waiting · blocked · returned · synced · settled · service_healthy (per group)

## 6. Scalable importance and aggregation algorithm

Deterministic score (higher wins top-bar slot):

| Signal | Weight |
|--------|--------|
| critical_incident_or_blocked_mission_path | 1000 |
| lead_goal_critical_path_owner | 900 |
| operator_attention_required | 800 |
| failed_or_stale_continuity | 700 |
| active_work_near_term_return | 500 |
| waiting_dependency_blocked | 300 |
| healthy_background | 100 |
| idle_resumable | 10 |

**Overflow policy:** show top-1 in bar, `+N` count, pinned agents bypass cap (max 3 pins), hierarchy rollups collapse siblings under domain nodes in popover. No render of hundreds of flat names.

## 7. GNOME integration plan

**Existing surface:** `desktop/gnome-shell/ion-helixion-control@helixion.net/`

| Phase | Change |
|-------|--------|
| A | Add read-only agent summary strip adjacent to connection switches; consume JSON status feed |
| B | New popover module `agentOperations.js` fed by canonical projection API |
| C | Attach controller hooks calling autonomous loop steward attach API |
| D | Split connection panel into submodule; preserve `control.py` strict mutation law |

**Preserve:** `control.py` compiled-in groups only; no arbitrary shell from UI.

## 8. Security, admission, accessibility, performance

- **Security:** no secrets in extension memory; action tokens never displayed; mutations only through admitted APIs with receipts.
- **Action admission:** destructive ops require `runtime_carrier_and_action_admission` policy check.
- **Accessibility:** keyboard navigable popover; high-contrast badges; no sole reliance on color.
- **Performance:** debounce UI updates 500ms; cap popover DOM nodes at 200 with virtualized list; probe budget max 3 concurrent.

## 9. Phased prototype and proof plan

| Phase | Deliverable | Success measure |
|-------|-------------|-----------------|
| A0 | Proposal + domain charter (this doc) | APGL bounded review packet issued; void operator-seat gate retired (P29) |
| A1 | Disposable JSON projection mock + bar wireframe | top-bar renders from mock without inferring health from terminal |
| B1 | Attach API spec + detached worker proof | close gnome-terminal does not stop worker PID |
| B2 | Importance ranker unit tests on fixture agent set | 100 agents → stable top-1 selection |
| C1 | Popover hierarchy from live DOMAIN_FIELD_COORDINATE_INDEX | domain rollups match filesystem |
| C2 | Connection + agent combined panel | per-group degradation scoped correctly |

## 10. Return routing

- **Review witness:** `domain.artifact_provenance_and_gate_legitimacy` (bounded packet; non-blocking)
- **Implementation owner:** `domain.gnome_desktop_ion_operator_surface` (after mount materialization)
- **Not implementing here:** runtime repair, scheduler code, registry writes

## Non-claims

candidate_only · no_accepted_state · no_broad_implementation · no_registry_promotion
