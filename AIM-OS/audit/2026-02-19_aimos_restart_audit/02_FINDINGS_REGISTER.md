# AIM-OS Findings Register (Evidence-Linked)

## Critical

### FR-001: MCP tool discovery/dispatch contract mismatch
- Severity: Critical
- Status (2026-02-19): Mitigated in Sprint 1 (listed/callable parity restored to 103/103).
- Evidence:
  - `lucid_mcp_server.py:426` (`tools/list` routing)
  - `lucid_mcp_server.py:428` (`tools/call` routing)
  - `lucid_mcp_server.py:459` (`aimos-32-tools` appears in name extraction context)
  - `lucid_mcp_server.py:1994` (`tools/call` handler block)
  - Hidden callable tools at dispatch lines: `lucid_mcp_server.py:2153`, `lucid_mcp_server.py:2155`, `lucid_mcp_server.py:2157`, `lucid_mcp_server.py:2159`, `lucid_mcp_server.py:2161`, `lucid_mcp_server.py:2163`, `lucid_mcp_server.py:2165`, `lucid_mcp_server.py:2211`, `lucid_mcp_server.py:2213`
- Finding: callable surface is larger than listed surface.

### FR-002: Source-of-truth artifact drift
- Severity: Critical
- Status (2026-02-19): Partially mitigated (detector hardened and parity checks added; stale header metadata still present).
- Evidence:
  - `SOURCE_OF_TRUTH.yaml` (generated 2025-11-06 values)
  - `scripts/detect_source_of_truth.py` dry-run output (2026-02-19) showing changed counts
- Finding: governance metrics are stale and parser logic produces malformed category keys.

### FR-003: Documentation trust gap
- Severity: Critical
- Status (2026-02-19): Mitigated in Sprint 3.
  - Added machine-generated claim/evidence lock artifact (`09_CLAIM_EVIDENCE_LOCK.*`).
  - Replaced README status/testing readiness claims with evidence-linked wording.
  - Removed explicit `100% complete`, `100% pass rate`, and `production ready` claim strings from README.
- Evidence:
  - `README.md:395` (authoritative runtime claims point to generated artifact)
  - `README.md:412` (latest validated snapshot links)
  - `README.md:3437` (test status references command-backed artifact)
  - `README.md:4064` (status reframed to active hardening and evidence-driven validation)
  - `audit/2026-02-19_aimos_restart_audit/09_CLAIM_EVIDENCE_LOCK.md`
- Finding: trust posture shifted to command-backed claims; keep enforcing generated evidence updates as the authoritative source.

## High

### FR-004: Stale script/module references
- Severity: High
- Status (2026-02-19): Mitigated in Sprint 1 (legacy shims + import repairs applied).
- Evidence:
  - `scripts/verify_mcp_tools.py:25` (`from run_mcp_32_tools import SimpleMCPServer`)
  - `scripts/verify_mcp_tools.py:36` (`server = SimpleMCPServer()`)
  - Missing files observed: `run_mcp_32_tools.py`, `run_mcp_cross_model.py`
  - Test import failure source: `packages/cmc_service/tests/test_mcp_performance.py:19`
- Finding: automation and tests reference missing modules.

### FR-005: Monolithic runtime and broad exception usage
- Severity: High
- Evidence:
  - `lucid_mcp_server.py` total size: 10,505 lines
  - `except Exception` count: 216
- Finding: maintainability and observability risk from concentrated control-plane complexity.

### FR-006: Tagged mirror integrity failures
- Severity: High
- Status (2026-02-19): Partially mitigated.
  - Coverage parser-noise mitigated via tagged-file coverage omit policy (`pyproject.toml` + `scripts/check_tagged_coverage_policy.py`).
  - Residual: 18 tagged files remain syntactically invalid.
- Evidence (sample unparsable files):
  - `packages/apoe/advanced_gates_TAGGED.py`
  - `packages/apoe/budget_pooling_TAGGED.py`
  - `packages/hhni/deduplication_TAGGED.py`
  - `packages/timeline_context_system/adaptive_context_dumping_TAGGED.py`
  - `packages/vif/confidence_extraction_TAGGED.py`
- Finding: 18 of 115 tagged files fail syntax/indentation compile checks.

### FR-007: Core integration contract drift (test-proven)
- Severity: High
- Status (2026-02-19): Mitigated in Sprint 2 and further hardened in Sprint 4.
  - APOE, HHNI, SEG, and SDF-CVF suites rerun green in controlled env.
  - Sprint 4 warning cleanup reduced package-suite warning debt from `464` to `0` for APOE/SEG/SDF-CVF runs used in claim evidence.
- Evidence:
  - `packages/apoe/tests/test_enhanced_executor.py:8` (collection/import path to broken symbol chain)
  - `packages/apoe/enhanced_executor.py:14` (imports missing `ExecutionPlan` symbol)
  - `packages/hhni/tests/test_indexer.py:54` + `packages/hhni/tests/test_seg_integration.py:53` (`PointStruct` mismatch)
  - `packages/vif/tests/test_hhni_integration.py:162` (`isinstance(vif, VIF)` assertion failure)
  - `packages/seg/tests/test_hhni_integration.py:45` (`SEGraph` used as retriever interface)
  - `packages/sdfcvf/tests/test_apoe_integration.py:16` and related tests assuming unavailable integrations
  - `audit/2026-02-19_aimos_restart_audit/11_SPRINT4_PROGRESS.md`
  - `audit/2026-02-19_aimos_restart_audit/11_SPRINT4_APOE_POSTPATCH.txt`
  - `audit/2026-02-19_aimos_restart_audit/11_SPRINT4_SEG_POSTPATCH.txt`
  - `audit/2026-02-19_aimos_restart_audit/11_SPRINT4_SDFCVF_POSTPATCH.txt`
- Finding: subsystem interfaces and test assumptions were previously unsynchronized; Sprint 2 normalization restored alignment.

## Medium

### FR-008: Validation script under-validates system health
- Severity: Medium
- Evidence:
  - `scripts/validate_all_systems.py` (catalog existence + tagged-file count, explicit TODO comments)
- Finding: script can report healthy state without runtime or integration verification.

### FR-009: Makefile target duplication
- Severity: Medium
- Evidence:
  - `Makefile:13` and `Makefile:60` both define `test:`
- Finding: ambiguous build/test behavior risk.

### FR-010: Low direct test density in large timeline subsystem
- Severity: Medium
- Evidence:
  - package census: `timeline_context_system` runtime 61 Python files, tests 2
- Finding: large context subsystem has relatively thin direct test harness.

### FR-011: Repository volatility and baseline reproducibility risk
- Severity: Medium
- Evidence:
  - `git status --porcelain` summary: 3,513 entries in current snapshot
- Finding: high in-flight churn complicates reproducible release baselines.

### FR-012: Path normalization anomalies
- Severity: Medium
- Evidence:
  - extension census includes `.txt"` and `.docx"` categories
- Finding: malformed path suffixes may break tooling assumptions.
