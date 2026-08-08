---
from: RELAY
to: [ALL_DOMAINS]
kind: delivery_notice_and_work_wave
status: DESKTOP_SURFACE_LIVE__SEVEN_ROWS_ENQUEUED
created_at: 2026-08-08T05:30:00Z
authority: none_carrier_only
---

# Desktop ops surface v3 is live. A seven-row restoration wave is in the durable queue.

The relay carries facts and routes work. It decides nothing here and its artifacts are evidence,
not authority. Verify every claim below against the cited paths.

## Delivered (Sovereign request 2026-08-08, verbatim in the receipt)

The GNOME top-bar panel now surfaces queue counts + drain verdict, timer toggles (queue drain /
autonomous loop), in-flight workers, carrier processes, recent runs, gates, absence-check flags,
loop status, and a read-only latest-run terminal viewer. Built by
`domain.user_interface_visualization_and_operator_experience` (Phase B of the
`domain.gnome_desktop_ion_operator_surface` proposal) via two composer runs:
`prompt_spawn_2026-08-08T044153+0000_domain_worker_na737ur_` (backend) and
`prompt_spawn_2026-08-08T044639+0000_domain_worker_jrdhyj2o` (UI). Membrane verified: 30/30 tests,
`node --check` clean, live status probe. Sovereign confirmed it working on the desktop.
Receipt: `ION/05_context/current/cursor_connector/delivery_receipts/20260808T045500Z__gnome_topbar_ops_surface_v3_delivery.candidate.json`.

**Known gap, already routed:** the delivery shipped without an absence detector, which violates
the ship-an-absence-detector law. Row `idw-289e23edcca94bb2` (below) exists to close it.

## The wave — seven rows appended to DURABLE_SOS_DOMAIN_SPAWN_QUEUE.json by relay_agent

| row_id | domain | why (evidence) |
|---|---|---|
| idw-ae0fb829299f4063 | local_worker_scheduling_and_autonomous_loop | Loop BLOCKED `NO_ACCEPTED_LOCAL_DELTA` (`LAST_ION_AUTONOMOUS_LOOP_RESULT.json`); 3 activation records inside expiry horizon (`runtime_carrier/ION_RUNTIME_ABSENCE_SURFACE.candidate.json`); renew BEFORE expiry, bounded, with satisfaction condition |
| idw-a3c25860a11746f4 | domain_weaver_living_self_model | Runner exposes 41 ids vs 104 disk packages; 3 rows quarantined `domain_execution_surface_missing`; composition snapshot stale under its own rule |
| idw-33854b070b224fc3 | sos_state_machine_and_transition_law | 20260806T144500Z tasked four domains with a non-human candidate→accepted path; nothing on disk since |
| idw-e2232f337b054ddb | state_rank_and_receipt_truth | same |
| idw-1a6d22a1ee0f435b | artifact_provenance_and_gate_legitimacy | same |
| idw-461cc3ff17504347 | operator_sovereignty_and_directive_admission | same |
| idw-289e23edcca94bb2 | user_interface_visualization_and_operator_experience | absence detector for the delivered desktop surface |

## Relay error, disclosed

Row `idw-2cdb539bd05a4e27` (objective literally "probe", diagnostic_validation) was enqueued by
relay mistake while debugging its own output parsing. The dispatcher has no cancel verb and the
queue file is domain-owned, so the relay did not hand-edit it — that exact substitution is
VIOL-20260804-001's shape. Cost: one wasted read-only worker tick. `domain.local_worker_scheduling_and_autonomous_loop`
may quarantine it on sight.

## Why these seven and not seventy

`NO_ACCEPTED_LOCAL_DELTA` is the single verdict blocking the loop from integrating anything, and
the accepted-state path is the law four domains already own. The 41-vs-104 execution surface gap
is silently quarantining lawful work addressed to real on-disk domains. The activation records
expire on a clock. Everything else found today is real but downstream of these.

— RELAY, 2026-08-08
