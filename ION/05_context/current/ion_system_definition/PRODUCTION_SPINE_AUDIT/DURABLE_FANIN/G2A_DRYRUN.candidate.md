# G2-A Dry-Run Report — Durable Settlement-Time Harvest (candidate)

```
schema_id: ion.production_spine.g2a_dryrun.v0_1_candidate
generated_at: 2026-06-17T18:00:00Z (approx)
generated_by: Composer carrier (role.mason) — G2-A proof-of-mechanism dry-run
posture: candidate_only
provenance: G2_DURABLE_FANIN_PLAN.candidate.md §1; LANE08 fixture; windowed hook reads
build_surface: /tmp only (helper + tests); zero real-repo .py edits
```

## What was proven

Packet **G2-A** (additive durable-harvest capture) is implementable as a **standalone, fail-soft helper** that:

1. Validates the nine locked dynamic-swarm `###` sections from `G2_DURABLE_FANIN_PLAN.candidate.md:76-86`.
2. Computes full-file UTF-8 SHA256 of `body_text`.
3. Writes `DURABLE_FANIN/lanes/LANE{NN}_{DOMAIN_SLUG}_GAP_RETURN.candidate.md` per `G2_DURABLE_FANIN_PLAN.candidate.md:54-58`.
4. Upserts `DURABLE_FANIN/MANIFEST.candidate.json` (`schema_id: ion.production_spine.durable_fanin_manifest.v0_1_candidate`) with lane metadata, `intake_accepted=true`, `semantically_settled=false` per `G2_DURABLE_FANIN_PLAN.candidate.md:94-114`.
5. Returns work-request metadata fields (`durable_harvest_path`, `durable_harvest_sha256`, `durable_harvest_at`, `durable_harvest_manifest_path`, `intake_accepted`, `semantically_settled`) without replacing existing request fields per `G2_DURABLE_FANIN_PLAN.candidate.md:119-132`.
6. Enforces idempotency on `(request_id, objective_sha256)` + identical hash → no-op; hash mismatch → `*.superseded.candidate.md` sibling + manifest `supersedes` pointer per `G2_DURABLE_FANIN_PLAN.candidate.md:117`.
7. Never raises into callers — all errors return `{"harvested": false, "error": ...}`.

Helper and tests live at `/tmp/g2a_durable_fanin_harvest.py` and `/tmp/test_g2a_durable_fanin_harvest.py` (not written to real source).

## /tmp test results

| # | Case | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Fresh harvest writes body + manifest + sha256 + metadata | **PASS** | `passed=5 failed=0`; body at `DURABLE_FANIN/lanes/LANE08_ION_VNEXT_KERNEL_CORE_GAP_RETURN.candidate.md`; manifest entry `lane_ordinal=8`, `body_sha256` matches LANE08 fixture |
| 2 | Re-harvest identical body → idempotent no-op | **PASS** | `harvested=false`, `idempotent_skip=true`; manifest bytes unchanged; body mtime unchanged |
| 3 | Hash mismatch → supersede chain | **PASS** | `LANE08_...superseded.candidate.md` sibling created; manifest `supersedes` pointer set; new `body_sha256` on active file |
| 4 | Missing required section → rejected, no write | **PASS** | truncated body (no `### ION OPERATIONAL POSTURE`); `error=missing_required_sections`; no body/manifest on disk |
| 5 | Fail-soft: unwritable lanes dir | **PASS** | `chmod 0444` on lanes dir; helper returned `harvested=false` with `error` key; **no exception raised** |

**Totals:** 5 PASS / 0 FAIL (`python3 /tmp/test_g2a_durable_fanin_harvest.py`).

## Candidate helper source (NOT written to real source)

```python
"""G2-A dry-run: standalone durable fan-in harvest helper (candidate-only)."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

DURABLE_FANIN_REL = Path(
    "ION/05_context/current/ion_system_definition/PRODUCTION_SPINE_AUDIT/DURABLE_FANIN"
)
MANIFEST_SCHEMA_ID = "ion.production_spine.durable_fanin_manifest.v0_1_candidate"

DURABLE_FANIN_REQUIRED_SECTIONS = (
    "### CONTEXT PROOF",
    "### TEMPLATE ACTION PROOF",
    "### VALIDATION",
    "### LANE CURRENTNESS REVIEW",
    "### PRODUCTION SPEC GAP REVIEW",
    "### DOMAIN WEAVER EVOLUTION REVIEW",
    "### BLOCKERS",
    "### RECOMMENDED NEXT PACKET",
    "### ION OPERATIONAL POSTURE",
)

METADATA_FIELDS = (
    "durable_harvest_path",
    "durable_harvest_sha256",
    "durable_harvest_at",
    "durable_harvest_manifest_path",
    "intake_accepted",
    "semantically_settled",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _section_heading_present(text: str, heading: str) -> bool:
    normalized = heading.strip().lower()
    for line in text.splitlines():
        if line.strip().lower() == normalized:
            return True
    return False


def _has_required_return_sections(text: str, sections: tuple[str, ...]) -> bool:
    return all(_section_heading_present(text, heading) for heading in sections)


def _parse_header_block(body_text: str) -> dict[str, str]:
    lines = body_text.splitlines()
    if not lines or lines[0].strip() != "```":
        raise ValueError("missing_header_fence_open")
    header_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "```":
            break
        header_lines.append(line)
    else:
        raise ValueError("missing_header_fence_close")

    header: dict[str, str] = {}
    for line in header_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        header[key.strip()] = value.strip()

    lane_id_raw = header.get("lane_id", "")
    ordinal_match = re.search(r"\(ordinal\s+(\d+)\)", lane_id_raw, re.IGNORECASE)
    lane_id = re.sub(r"\s*\(ordinal\s+\d+\)\s*$", "", lane_id_raw, flags=re.IGNORECASE).strip()
    ordinal = int(ordinal_match.group(1)) if ordinal_match else 0

    request_id = header.get("request_id", "").strip()
    objective_sha256 = header.get("objective_sha256", "").strip()
    if not lane_id or not ordinal or not request_id or not objective_sha256:
        raise ValueError("incomplete_header_fields")

    return {
        "lane_id": lane_id,
        "lane_ordinal": str(ordinal),
        "request_id": request_id,
        "objective_sha256": objective_sha256,
    }


def _domain_slug(lane_id: str) -> str:
    return lane_id.upper().replace("-", "_")


def _lane_body_rel_path(lane_ordinal: int, lane_id: str) -> Path:
    slug = _domain_slug(lane_id)
    return DURABLE_FANIN_REL / "lanes" / f"LANE{lane_ordinal:02d}_{slug}_GAP_RETURN.candidate.md"


def _manifest_rel_path() -> Path:
    return DURABLE_FANIN_REL / "MANIFEST.candidate.json"


def _load_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / _manifest_rel_path()
    if not manifest_path.exists():
        return {"schema_id": MANIFEST_SCHEMA_ID, "lanes": []}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest_not_object")
    data.setdefault("schema_id", MANIFEST_SCHEMA_ID)
    data.setdefault("lanes", [])
    return data


def _write_manifest(root: Path, manifest: Mapping[str, Any]) -> None:
    manifest_path = root / _manifest_rel_path()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _find_manifest_entry(manifest: Mapping[str, Any], request_id: str, objective_sha256: str) -> dict[str, Any] | None:
    for entry in manifest.get("lanes") or []:
        if not isinstance(entry, Mapping):
            continue
        if (
            str(entry.get("request_id") or "") == request_id
            and str(entry.get("objective_sha256") or "") == objective_sha256
        ):
            return dict(entry)
    return None


def _metadata_payload(
    *,
    body_rel: str,
    body_sha256: str,
    harvest_at: str,
    manifest_rel: str,
) -> dict[str, Any]:
    return {
        "durable_harvest_path": body_rel,
        "durable_harvest_sha256": body_sha256,
        "durable_harvest_at": harvest_at,
        "durable_harvest_manifest_path": manifest_rel,
        "intake_accepted": True,
        "semantically_settled": False,
    }


def _durable_fanin_harvest_lane_body_impl(
    root: Path,
    request: Mapping[str, Any],
    body_text: str,
    *,
    harvest_source: str,
) -> dict[str, Any]:
    if not body_text or not body_text.strip():
        return {"harvested": False, "error": "empty_body_text"}

    if not _has_required_return_sections(body_text, DURABLE_FANIN_REQUIRED_SECTIONS):
        missing = [
            section
            for section in DURABLE_FANIN_REQUIRED_SECTIONS
            if not _section_heading_present(body_text, section)
        ]
        return {"harvested": False, "error": "missing_required_sections", "missing_sections": missing}

    header = _parse_header_block(body_text)
    lane_ordinal = int(header["lane_ordinal"])
    lane_id = header["lane_id"]
    request_id = header["request_id"]
    objective_sha256 = header["objective_sha256"]

    body_sha256 = _sha256_text(body_text)
    body_rel_path = _lane_body_rel_path(lane_ordinal, lane_id)
    body_rel = body_rel_path.as_posix()
    manifest_rel = _manifest_rel_path().as_posix()
    harvest_at = _now_iso()
    idempotency_key = f"durable-fanin-lane-{lane_ordinal:02d}-{request_id}"

    manifest = _load_manifest(root)
    existing = _find_manifest_entry(manifest, request_id, objective_sha256)
    if existing and str(existing.get("body_sha256") or "") == body_sha256:
        metadata = _metadata_payload(
            body_rel=str(existing.get("body_path") or body_rel),
            body_sha256=body_sha256,
            harvest_at=str(existing.get("harvest_at") or harvest_at),
            manifest_rel=manifest_rel,
        )
        return {
            "harvested": False,
            "idempotent_skip": True,
            **metadata,
        }

    body_abs = root / body_rel_path
    body_abs.parent.mkdir(parents=True, exist_ok=True)

    superseded_rel: str | None = None
    if existing and str(existing.get("body_sha256") or "") != body_sha256:
        prior_rel = str(existing.get("body_path") or body_rel)
        prior_abs = root / prior_rel
        if prior_abs.exists():
            superseded_path = prior_abs.with_name(
                prior_abs.stem + ".superseded.candidate.md"
            )
            prior_abs.rename(superseded_path)
            superseded_rel = superseded_path.relative_to(root).as_posix()

    body_abs.write_text(body_text, encoding="utf-8")

    entry: dict[str, Any] = {
        "lane_ordinal": lane_ordinal,
        "lane_id": lane_id,
        "request_id": request_id,
        "body_path": body_rel,
        "body_sha256": body_sha256,
        "objective_sha256": objective_sha256,
        "harvest_source": harvest_source,
        "harvest_at": harvest_at,
        "idempotency_key": idempotency_key,
        "intake_accepted": True,
        "semantically_settled": False,
    }
    if superseded_rel:
        entry["supersedes"] = superseded_rel

    lanes = [dict(item) for item in manifest.get("lanes") or [] if isinstance(item, Mapping)]
    replaced = False
    for idx, item in enumerate(lanes):
        if (
            str(item.get("request_id") or "") == request_id
            and str(item.get("objective_sha256") or "") == objective_sha256
        ):
            lanes[idx] = entry
            replaced = True
            break
    if not replaced:
        lanes.append(entry)

    manifest_out = {"schema_id": MANIFEST_SCHEMA_ID, "lanes": lanes}
    _write_manifest(root, manifest_out)

    metadata = _metadata_payload(
        body_rel=body_rel,
        body_sha256=body_sha256,
        harvest_at=harvest_at,
        manifest_rel=manifest_rel,
    )
    return {"harvested": True, **metadata}


def _durable_fanin_harvest_lane_body(
    root: Path,
    request: Mapping[str, Any],
    body_text: str,
    *,
    harvest_source: str,
) -> dict[str, Any]:
    try:
        return _durable_fanin_harvest_lane_body_impl(
            root,
            request,
            body_text,
            harvest_source=harvest_source,
        )
    except Exception as exc:  # noqa: BLE001 — fail-soft boundary for additive hook
        return {"harvested": False, "error": str(exc)}
```

## Exact additive hook diffs (candidate — not applied)

### Hook 1 — Primary: connector `ion_submit_task_return` path

**Site:** `ion_chatgpt_browser_mcp_connector_contract.py:5073-5095` — after work-request status flip to `RETURN_RECORDED_PROOF_ACCEPTED` and `_write_json(request_path, request_payload)` at `:5095`. `text` is in scope from `:4802`.

```diff
--- a/ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py
+++ b/ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py
@@ -5092,6 +5092,22 @@
         request_payload["latest_working_capsule_preflight"] = working_capsule_update.get("preflight")
         if working_capsule_update.get("maintenance_attempted"):
             request_payload["latest_working_capsule_maintenance"] = working_capsule_update.get("maintenance")
         _write_json(request_path, request_payload)
+        # G2-A: durable settlement-time harvest (additive, fail-soft)
+        if accepted and text.strip():
+            harvest_result = _durable_fanin_harvest_lane_body(
+                root,
+                request_payload,
+                text,
+                harvest_source="settlement_time_capture",
+            )
+            if harvest_result.get("harvested") or harvest_result.get("idempotent_skip"):
+                for field in (
+                    "durable_harvest_path", "durable_harvest_sha256", "durable_harvest_at",
+                    "durable_harvest_manifest_path", "intake_accepted", "semantically_settled",
+                ):
+                    if field in harvest_result:
+                        request_payload[field] = harvest_result[field]
+                _write_json(request_path, request_payload)
         work_request_updated = True
     queue = _write_codex_work_queue_index(root)
     return _ok(
```

### Hook 2 — Secondary: queue runner run finalization

**Site:** `ion_codex_queue_runner.py:8534-8545` — inside `if accepted:` block, before `_write_run_packet(run_path, run)` at `:8545`. `request` loaded at `:8481`; `task_return_body_path` on run at `:5933`.

```diff
--- a/ION/04_packages/kernel/ion_codex_queue_runner.py
+++ b/ION/04_packages/kernel/ion_codex_queue_runner.py
@@ -8541,6 +8541,22 @@
         )
         if sync_reply.get("attempted"):
             run["domain_weaver_agent_comms_synced_reply"] = sync_reply
+        # G2-A: durable harvest before run-exhaust prune (additive, fail-soft)
+        task_return_body_rel = str(run.get("task_return_body_path") or "").strip()
+        if task_return_body_rel:
+            body_text = _read_rel_text_if_exists(shell_root, task_return_body_rel)
+            if body_text:
+                harvest_result = _durable_fanin_harvest_lane_body(
+                    shell_root,
+                    request,
+                    body_text,
+                    harvest_source="settlement_time_capture",
+                )
+                if harvest_result.get("harvested") or harvest_result.get("idempotent_skip"):
+                    for field in (
+                        "durable_harvest_path", "durable_harvest_sha256", "durable_harvest_at",
+                        "durable_harvest_manifest_path", "intake_accepted", "semantically_settled",
+                    ):
+                        if field in harvest_result:
+                            request[field] = harvest_result[field]
+                    _write_json(shell_root / request_rel, request)
     run["worker_return_status"] = _worker_return_status_for_run(run)
     _write_run_packet(run_path, run)
```

## Additivity + fail-soft argument

**Additivity:** Both hooks insert a guarded side-effect call *after* existing acceptance writes (`_write_json` at `ion_chatgpt_browser_mcp_connector_contract.py:5095`; sync_reply block ending `ion_codex_queue_runner.py:8543`) and *before* unchanged terminal paths (`work_request_updated = True` / `_write_run_packet` at `:8545`). Neither hook alters `accepted` computation (`:4857-4864`), status assignment (`:5073`), return payloads (`:5098-5104`, `:8562+`), reconciliation (`_domain_weaver_dynamic_swarm_fresh_context_reconciliation` — G2-C per `G2_DURABLE_FANIN_PLAN.candidate.md:142`), nor fan-in (`_domain_weaver_latest_dynamic_swarm_fanin_reissue_refs` — G2-D per `:159-167`). G2-A touches **only** `DURABLE_FANIN/` artifacts and optional additive metadata keys on the work request.

**Fail-soft:** `_durable_fanin_harvest_lane_body` wraps all logic in a top-level `try/except` returning `{"harvested": false, "error": ...}` (`/tmp/g2a_durable_fanin_harvest.py:258-273`). Hooks never branch on harvest failure; case 5 proves an induced I/O error does not raise. Carrier intake cannot be blocked by harvest faults.

## Residual risks

| Risk | Mitigation path |
| --- | --- |
| Header/body `request_id` drift from work-request JSON | Future hook may cross-check `request["request_id"]` vs header; dry-run trusts header per LANE08 contract |
| Concurrent harvest races on same lane | Manifest is last-writer; production packet should add file lock or atomic rename discipline |
| `return_contract_sections` per-request variance | G2-A locks nine dynamic-swarm sections; non-vNext lanes may need section resolver (G2-B migration) |
| Secondary hook reads pruned body | Primary connector hook is authoritative; secondary is best-effort before `_write_run_packet` |
| Helper placement in monolith | Real landing needs `DOMAIN_WEAVER_DURABLE_FANIN_ROOT` constant per `G2_DURABLE_FANIN_PLAN.candidate.md:147-151` |

## Non-claims

- This dry-run does **not** ratify production state, edit real kernel source, start workers, or flip G2 exit test green.
- Reconciliation honesty (G2-F) and semantic fan-in read-path rewire (G2-D) are **out of scope** for G2-A.
- Synthesis of this report is not settlement; operator review required before monolith landing.
- Pre-existing dirty kernel `.py` files in git status are **not** attributable to this carrier.
