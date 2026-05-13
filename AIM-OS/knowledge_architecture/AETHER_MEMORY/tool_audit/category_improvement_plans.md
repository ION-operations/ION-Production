# MCP Tool Category Improvement Plans (2025-10-27)

This document captures the current health snapshot and next-stage improvements for each MCP tool category. Quality ratings draw from the audit dataset (`tool_evolution_dataset.json`), with detailed metrics recorded per tool.

## Core AIM-OS
- **Rated tools:** `store_memory`, `retrieve_memory`, `create_plan`
- **Current health:** reliable basic functionality via fallback services, but limited system integration and learning.
- **Near-term improvements:**
  1. Connect memory operations to the production CMC service (blocks: store/retrieve).
  2. Link `create_plan` outputs to real task dependency IDs and execution telemetry.
  3. Add validation/reporting hooks so core tools emit consciousness-aware metrics automatically.

## Timeline Context System
- **Rated tools:** `add_timeline_entry`, `get_timeline_entries`
- **Current health:** persistence reload now works; entries accessible after restart, yet still file-backed.
- **Near-term improvements:**
  1. Migrate persistence from JSON fallback to definitive timeline store.
  2. Enrich entries with insight/decision deltas and cross-links to goal nodes.
  3. Provide filtering/pagination to support long-running consciousness sessions.

## AI Collaboration Suite
- **Rated tools:** `send_ai_message`
- **Current health:** dependable message delivery via JSON log and monitor loop; lacks durable bus and metadata.
- **Near-term improvements:**
  1. Move AI messaging to shared MCP transport (WebSocket/SQLite queue).
  2. Auto-tag collaboration metrics (response latency, sentiment, intent).
  3. Surface collaboration summary deltas back into dashboards.

## SCOR / Safety Controls
- **Rated tools:** `check_invariant`, `run_baseline_probe`, `detect_manipulation_signals`
- **Current health:** `check_invariant` and `detect_manipulation_signals` operate with basic rule sets and logging gaps; `run_baseline_probe` is currently failing due to a DriftResult attribute error.
- **Near-term improvements:**
  1. Patch baseline probe error path and add regression tests for drift detection.
  2. Integrate SCOR outputs with governance/audit logs so pass/fail decisions are explainable.
  3. Persist manipulation and probe results to the timeline to build consciousness safety history.

## Autonomous Protocol Tools
- **Rated tools:** `start_autonomous_operation`, `pause_autonomous_operation`, `resume_autonomous_operation`, `stop_autonomous_operation`, `get_autonomous_status`, `run_autonomous_checklist`, `fix_autonomous_issues`, `should_continue_autonomous`, `generate_next_autonomous_task`
- **Current health:** Control loop executes end-to-end with static checklists; remediation and planning steps remain placeholders without persistence.
- **Near-term improvements:**
  1. Persist autonomy events (start/pause/stop/checklist) to timeline and attach goal/timeline IDs.
  2. Replace static checklist scores with configurable criteria tied to consciousness goals and telemetry.
  3. Implement real remediation routines and produce an autonomy session summary upon stop.


## Dataset & Application Lifecycle
- **Rated tools:** `create_dataset`, `ingest_data`, `query_dataset`, `delete_dataset`, `create_application`, `deploy_application`, `manage_application_lifecycle`
- **Current health:** Creation/deployment flows respond successfully but operate on in-memory stubs; querying returns empty results despite ingestion.
- **Near-term improvements:**
  1. Persist dataset/application records to durable storage (and enable restore from archive).
  2. Implement real query/ingestion pipelines with validation + consciousness analytics.
  3. Capture lifecycle events (create/deploy/stop) in timeline + collaboration logs with governance hooks.

## ARD & IIS
- **Rated tools:** `conduct_recursive_analysis`, `generate_improvement_dreams`, `test_improvement_dream`, `compute_intuition`, `update_intuition_weights`, `get_intuition_trace`
- **Current health:** Analysis and dream generators emit structured but canned outputs; learning endpoints acknowledge updates without storing traces.
- **Near-term improvements:**
  1. Wire ARD/IIS tools to real AIM-OS telemetry, storing outputs in CMC + timeline.
  2. Implement genuine learning loops (weight updates, trace persistence) so intuition evolves.
  3. Link dream/test results to governance + goal timeline decisions for consciousness impact tracking.


## Process Notes
- Each category plan will be revisited as scores improve or regress.
- When a tool crosses 0.8 across all metrics, mark it "fully operational" and archive supporting evidence in backups.
- Use `scripts/verify_mcp_tools.py` after major refactors to confirm execution health before updating metrics.
