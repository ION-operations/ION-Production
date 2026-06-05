from __future__ import annotations

import os
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from kernel.ion_domain_weaver_context_active_resolver import (
    apply_active_context_gated_refresh,
    build_active_context_gated_refresh_plan,
    build_active_context_reissue_preflight,
    build_context_active_resolver_status,
    derive_active_context_refresh_target_coverage,
    resolve_domain_active_context,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test-root\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# test authority\n", encoding="utf-8")
    codex_solo = root / "ION/05_context/current/codex_solo"
    codex_solo.mkdir(parents=True, exist_ok=True)
    (codex_solo / "CAPSULE.md").write_text("# capsule\n", encoding="utf-8")
    (codex_solo / "MINI.md").write_text("# mini\n", encoding="utf-8")
    (codex_solo / "HOT_CONTEXT.md").write_text("# hot\n", encoding="utf-8")
    _write_json(codex_solo / "LONG_HORIZON.json", {"epoch_count": 1})
    _write_json(codex_solo / "ROUTE.json", {"entries": []})
    _write_json(
        codex_solo / "STATUS.json",
        {
            "active_context": {
                "context_packages_path": "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
                "minimum_context_path": "ION/05_context/current/codex_solo/CAPSULE.md",
                "hot_context_path": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
                "long_horizon_path": "ION/05_context/current/codex_solo/LONG_HORIZON.json",
            },
            "authority": {
                "production_authority": False,
                "live_execution_authority": False,
            },
        },
    )
    _write_json(
        codex_solo / "CONTEXT_PACKAGES.json",
        {
            "schema_id": "ion.codex_solo_context_packages.v1",
            "generated_at": "2099-01-01T00:00:00+00:00",
            "production_authority": False,
            "live_execution_authority": False,
            "package_count": 3,
            "selected_by_default": [
                "minimum_working_capsule",
                "mini_lookup_index",
                "mission_active_package",
            ],
            "packages": [
                {
                    "package_id": "minimum_working_capsule",
                    "context_type": "active_short_horizon",
                    "load_policy": "always_inline_first",
                    "path_refs": ["ION/05_context/current/codex_solo/CAPSULE.md"],
                },
                {
                    "package_id": "mini_lookup_index",
                    "context_type": "receipt_lookup",
                    "load_policy": "index_only_not_primary_prompt",
                    "path_refs": ["ION/05_context/current/codex_solo/MINI.md"],
                },
                {
                    "package_id": "mission_active_package",
                    "context_type": "current_objective",
                    "load_policy": "injected_per_queue_or_chat_turn",
                    "path_refs": ["ION/05_context/current/codex_solo/HOT_CONTEXT.md"],
                },
            ],
        },
    )


def _mount(root: Path, mount_id: str, active_md: str = "active\n", lane_id: str | None = None) -> Path:
    _root(root)
    ion_dir = root / "ION/05_context/current/codex_agent_mounts" / mount_id / ".ion"
    ion_dir.mkdir(parents=True)
    left, _, right = mount_id.partition("__")
    role_id = f"role.{left[len('role_'):]}" if left.startswith("role_") else ""
    domain_id = f"domain.{right[len('domain_'):]}" if right.startswith("domain_") else ""
    _write_json(
        ion_dir.parent / "ION_AGENT_MOUNT_MANIFEST.json",
        {"role_id": role_id, "domain_id": domain_id},
    )
    for name in (
        "ION_CONTEXT_CAPSULE.yaml",
        "AGENT.yaml",
        "DOMAIN.yaml",
        "RELATIONSHIPS.yaml",
        "COMMUNICATIONS.json",
        "ADDRESS_BOOK.json",
        "CONTEXT_IDENTITY.json",
    ):
        (ion_dir / name).write_text(f"{name}\n", encoding="utf-8")
    (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").write_text(active_md, encoding="utf-8")
    active_json = {"domain_id": domain_id, "role_id": role_id}
    if lane_id:
        active_json["lane_id"] = lane_id
    _write_json(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json", active_json)
    return ion_dir


def _mark_active_context_refs_stale(ion_dir: Path) -> None:
    stale = time.time() - 200_000
    for name in ("ACTIVE_CONTEXT_PACKAGE.md", "ACTIVE_CONTEXT_PACKAGE.json"):
        path = ion_dir / name
        if path.exists():
            os.utime(path, (stale, stale))


def test_resolves_fresh_domain_active_context(tmp_path: Path) -> None:
    _mount(tmp_path, "role_context_cartographer__domain_context_active_resolver")

    result = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.context_active_resolver",
    )

    assert result["ok"] is True
    assert result["resolver_id"] == "domain.context_active_resolver"
    assert result["mutates_active_state"] is False
    assert result["root_proof"]["ok"] is True
    assert result["codex_solo_context_health"]["ok"] is True
    assert result["materialize_all_guard"]["materialize_all_allowed"] is False
    assert result["materialize_all_guard"]["finding"] == "materialize_all_blocked_until_fresh_active_context_package_proof"
    assert result["selected"]["role_id"] == "role.context_cartographer"
    assert result["selected"]["domain_id"] == "domain.context_active_resolver"
    assert result["selected"]["authority"]["materialization_write_authority"] is False


def test_rejects_stale_active_context_package(tmp_path: Path) -> None:
    ion_dir = _mount(tmp_path, "role_context_cartographer__domain_context_active_resolver")
    stale = time.time() - 10_000
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.md", (stale, stale))
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json", (stale, stale))

    result = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.context_active_resolver",
        max_age_seconds=1,
    )

    assert result["ok"] is False
    assert "active_context_package_stale" in result["blockers"]
    assert result["next_action"] == "repair_or_reissue_active_context_package"


def test_active_context_reissue_preflight_enumerates_targets_without_refresh(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    stale = time.time() - 200_000
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.md", (stale, stale))
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json", (stale, stale))

    result = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )

    assert result["ok"] is True
    assert result["preflight_completed"] is True
    assert result["mutates_active_state"] is False
    assert result["refresh_run"] is False
    assert result["refresh_allowed_now"] is False
    assert result["target_mount_count"] == 1
    assert result["mount_package_refs_requiring_reissue_count"] == len(result["mount_package_refs_requiring_reissue"])
    assert result["preflight_required_leases"] == []
    assert "gated_refresh_not_run_preflight_only" in result["blockers"]
    assert "active_context_targets_require_reissue" in result["blockers"]
    target = result["target_mounts"][0]
    assert target["mount_id"] == "role_context_cartographer__domain_context_active_resolver"
    assert target["expected_lane_metadata"]["domain_id"] == "domain.context_active_resolver"
    assert target["expected_lane_metadata"]["role_id"] == "role.context_cartographer"
    assert target["expected_lane_metadata"]["lane_ids"] == ["stale_resolver_lane"]
    lease = result["gated_refresh_required_leases"][0]
    assert lease["lease_scope"] == "gated_refresh_only"
    assert lease["lease_type"] == "exclusive_write"
    assert lease["lease_not_requested_by_preflight"] is True
    assert "ION/05_context/current/codex_agent_mounts/role_context_cartographer__domain_context_active_resolver/.ion/ACTIVE_CONTEXT_PACKAGE.md" in lease["target_paths"]
    assert result["gated_refresh_gate"]["required_next_packet"] == "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1"
    assert "materialize_all" in result["gated_refresh_gate"]["forbidden_actions"]
    assert result["receipt_plan"]["codex_solo_post_allowed_only_after_lead_fanin_settlement"] is True
    assert result["rollback_plan"]["required_before_refresh"] is True


def test_active_context_reissue_preflight_derives_exact_stale_refresh_targets(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="partially_stale_resolver_lane",
    )
    stale = time.time() - 200_000
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.md", (stale, stale))

    result = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="partially_stale_resolver_lane",
        max_age_seconds=60,
    )

    md_path = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_context_cartographer__domain_context_active_resolver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    json_path = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_context_cartographer__domain_context_active_resolver/.ion/ACTIVE_CONTEXT_PACKAGE.json"
    )
    assert result["target_mount_count"] == 1
    assert result["mount_package_refs_requiring_reissue_count"] == 1
    assert result["mount_package_refs_requiring_reissue"] == [
        {
            "mount_id": "role_context_cartographer__domain_context_active_resolver",
            "path": md_path,
            "reason": "active_context_package_stale",
            "age_seconds": result["mount_package_refs_requiring_reissue"][0]["age_seconds"],
            "max_context_age_seconds": 60,
        }
    ]
    target = result["target_mounts"][0]
    assert target["active_context_fresh"] is True
    assert target["active_context_package_refs_requiring_refresh"][0]["path"] == md_path
    assert target["required_refresh_target_paths"] == [md_path]
    assert result["gated_refresh_required_leases"][0]["target_paths"] == [md_path]
    assert json_path not in result["gated_refresh_required_leases"][0]["target_paths"]
    assert "active_context_targets_require_reissue" in result["blockers"]

    plan = build_active_context_gated_refresh_plan(
        result,
        **_valid_refresh_gate(result),
    )
    assert plan["ok"] is False
    assert plan["write_gate_passed"] is False
    assert plan["preview_diagnostic_only"] is True
    assert plan["write_authority_granted"] is False
    assert plan["live_worker_shift_gate_checked"] is False
    assert plan["non_preview_refresh_allowed"] is False
    assert plan["target_coverage"]["required_target_paths"] == [md_path]
    assert plan["target_coverage"]["diagnostic_target_coverage_ok"] is True
    assert plan["target_coverage"]["target_coverage_ok"] is False
    assert plan["refresh_plan"]["would_write_paths"] == [md_path]


def test_active_context_reissue_preflight_enumerates_stale_codex_solo_refs(tmp_path: Path) -> None:
    _mount(tmp_path, "role_context_cartographer__domain_context_active_resolver")
    hot_context = tmp_path / "ION/05_context/current/codex_solo/HOT_CONTEXT.md"
    stale = time.time() - 200_000
    os.utime(hot_context, (stale, stale))

    result = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        max_age_seconds=1,
    )

    assert result["ok"] is True
    assert result["refresh_run"] is False
    assert {
        "source": "codex_solo_context_package",
        "path": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "reason": "codex_solo_context_package_ref_stale",
    } in result["stale_package_refs"]
    assert "codex_solo_context_package_ref_stale" in result["blockers"]
    assert result["gated_refresh_gate"]["allowed_now"] is False


def test_active_context_preflight_canonicalizes_vnext_front_door_manifest_only_mount(tmp_path: Path) -> None:
    _root(tmp_path)
    manifest_path = (
        tmp_path
        / "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    _write_json(manifest_path, {"role_id": "role.atlas", "domain_id": "ion_vnext_front_door"})

    result = build_active_context_reissue_preflight(tmp_path, max_age_seconds=60)

    target = [
        row for row in result["target_mounts"]
        if row["mount_id"] == "role_atlas__ion_vnext_front_door"
    ][0]
    assert target["role_id"] == "role.atlas"
    assert target["domain_id"] == "domain.vnext_front_door"
    assert target["semantic_identity"]["manifest_domain_id"] == "ion_vnext_front_door"
    assert target["semantic_identity"]["canonical_domain_id"] == "domain.vnext_front_door"
    assert target["semantic_identity"]["domain_alias_detected"] is True
    assert "active_context_package_missing" in target["blockers"]
    assert target["mount_launch_ready"] is False
    assert "mount_launch_completeness_missing_required_refs" in target["mount_completeness_blockers"]


def test_resolver_blocks_fresh_but_launch_incomplete_vnext_mount(tmp_path: Path) -> None:
    _root(tmp_path)
    mount = tmp_path / "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door"
    ion_dir = mount / ".ion"
    ion_dir.mkdir(parents=True, exist_ok=True)
    _write_json(mount / "ION_AGENT_MOUNT_MANIFEST.json", {"role_id": "role.atlas", "domain_id": "ion_vnext_front_door"})
    (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").write_text("fresh active context\n", encoding="utf-8")
    _write_json(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json", {"lane_id": "atlas_lane"})

    resolved = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.vnext_front_door",
        max_age_seconds=60,
    )

    assert resolved["selected"]["mount_id"] == "role_atlas__ion_vnext_front_door"
    assert resolved["selected"]["active_context_fresh"] is True
    assert resolved["selected"]["mount_launch_ready"] is False
    assert resolved["ok"] is False
    assert resolved["next_action"] == "repair_generated_mount_launch_completeness"
    assert "mount_launch_completeness_missing_required_refs" in resolved["blockers"]
    assert "mount_context_identity_missing" in resolved["blockers"]

    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.vnext_front_door",
        max_age_seconds=60,
    )
    assert preflight["target_mount_count"] == 0
    assert preflight["mount_package_refs_requiring_reissue_count"] == 0
    assert preflight["launch_incomplete_mount_count"] == 1
    assert preflight["launch_incomplete_mounts"][0]["mount_id"] == "role_atlas__ion_vnext_front_door"
    assert "mount_launch_completeness_incomplete" in preflight["blockers"]


def test_status_reports_mount_counts(tmp_path: Path) -> None:
    _mount(tmp_path, "role_context_cartographer__domain_context_active_resolver")
    (tmp_path / "ION/05_context/current/codex_agent_mounts/.hidden_support").mkdir(parents=True)
    (tmp_path / "ION/05_context/current/codex_agent_mounts/cosmos_support_folder").mkdir(parents=True)

    status = build_context_active_resolver_status(tmp_path)
    preflight = build_active_context_reissue_preflight(tmp_path)

    assert status["available"] is True
    assert status["ok"] is True
    assert status["root_proof"]["ok"] is True
    assert status["codex_solo_context_health"]["ok"] is True
    assert status["materialize_all_guard"]["materialize_all_allowed"] is False
    assert status["inspected_mount_count"] == 1
    assert preflight["inspected_mount_count"] == status["inspected_mount_count"]
    assert status["fresh_active_context_count"] == 1
    assert status["launch_ready_mount_count"] == 1
    assert status["launch_incomplete_mount_count"] == 0


def test_resolver_reports_active_root_proof_failure(tmp_path: Path) -> None:
    result = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.context_active_resolver",
    )

    assert result["ok"] is False
    assert result["root_proof"]["ok"] is False
    assert "active_root_proof_failed" in result["blockers"]
    assert result["next_action"] == "repair_active_root_proof"


def test_resolver_reports_codex_solo_missing_and_stale_package_refs(tmp_path: Path) -> None:
    _root(tmp_path)
    hot_context = tmp_path / "ION/05_context/current/codex_solo/HOT_CONTEXT.md"
    stale = time.time() - 200_000
    os.utime(hot_context, (stale, stale))
    manifest_path = tmp_path / "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["packages"].append({
        "package_id": "broken_package",
        "context_type": "test",
        "load_policy": "test",
        "path_refs": ["ION/05_context/current/codex_solo/MISSING.md"],
    })
    manifest["package_count"] = len(manifest["packages"])
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.context_active_resolver",
        max_age_seconds=1,
    )
    health = result["codex_solo_context_health"]

    assert result["ok"] is False
    assert health["ok"] is False
    assert "codex_solo_context_package_ref_missing" in health["blockers"]
    assert "codex_solo_context_package_ref_stale" in health["blockers"]
    assert "ION/05_context/current/codex_solo/MISSING.md" in health["missing_path_refs"]
    assert "ION/05_context/current/codex_solo/HOT_CONTEXT.md" in health["stale_path_refs"]
    assert "no_matching_active_context_mount" in result["blockers"]
    assert result["next_action"] == "repair_or_reissue_codex_solo_context_packages"
    assert result["materialize_all_guard"]["recommended_next_packet"] == (
        "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-REISSUE-PREFLIGHT-AND-GATED-REFRESH-V0_1"
    )
    assert "fresh_active_context_package_proof_missing" in result["materialize_all_guard"]["blockers"]


def test_resolver_binds_requested_lane_to_active_context_package(tmp_path: Path) -> None:
    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="resolver_gate_test_lane",
    )

    matched = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.context_active_resolver",
        lane="resolver_gate_test_lane",
    )
    missing_lane = resolve_domain_active_context(
        tmp_path,
        domain_id="domain.context_active_resolver",
        lane="other_lane",
    )

    assert matched["ok"] is True
    assert matched["selected"]["lane_ids"] == ["resolver_gate_test_lane"]
    assert missing_lane["ok"] is False
    assert "no_matching_active_context_mount_for_lane" in missing_lane["blockers"]


def test_domain_weaver_read_only_action_resolves_context_without_projection_materialization(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver import execute_domain_weaver_action

    _mount(tmp_path, "role_context_cartographer__domain_context_active_resolver")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "resolve_context_active",
            "domain_id": "domain.context_active_resolver",
        },
    )

    assert result["ok"] is True
    assert result["required_confirmation"] == "not_required_read_only"
    assert result["summary"]["projection_materialized"] is False
    assert result["summary"]["worker_started_count"] == 0
    assert result["results"]["context_active_resolver"]["selected"]["role_id"] == "role.context_cartographer"


def test_runtime_branch_route_resolves_context_active(tmp_path: Path) -> None:
    from kernel.ion_runtime_service_control import invoke_runtime_service_route

    _mount(tmp_path, "role_context_cartographer__domain_context_active_resolver")

    result = invoke_runtime_service_route(
        tmp_path,
        route_id="resolve_context_active",
        args={"domain_id": "domain.context_active_resolver"},
    )

    assert result["ok"] is True
    assert result["resolver_id"] == "domain.context_active_resolver"
    assert result["selected"]["mount_id"] == "role_context_cartographer__domain_context_active_resolver"
    assert result["mutates_active_state"] is False


def _queue_template(request_id: str) -> dict[str, object]:
    from kernel.ion_domain_weaver import CODEX_WORK_REQUESTS_DIR

    return {
        "request_id": request_id,
        "packet_path": (CODEX_WORK_REQUESTS_DIR / f"{request_id}.json").as_posix(),
        "dedupe_key": f"test:{request_id}",
        "lane_id": "resolver_gate_test_lane",
        "domain_id": "domain.context_active_resolver",
        "role_id": "role.context_cartographer",
        "objective": "resolver worker-start gate test",
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _working_capsule_identity(root: Path, **overrides: object) -> dict[str, object]:
    from kernel.ion_working_capsule_identity import build_working_capsule_identity

    mount_root = root / "ION/05_context/current/codex_agent_mounts/role_context_cartographer__domain_context_active_resolver"
    payload = build_working_capsule_identity(
        root=root,
        cwd=mount_root,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        carrier_instance_id="codex_session_readiness_test",
        codex_agent_mount=mount_root,
    ).to_dict()
    payload.update(overrides)
    return payload


def _write_queued_request(
    root: Path,
    request_id: str,
    lane_id: str,
    *,
    working_capsule_identity: dict[str, object] | None = None,
    extra: dict[str, object] | None = None,
) -> Path:
    from kernel.ion_domain_weaver_worker_start_readiness import CODEX_WORK_REQUESTS_DIR

    _root(root)
    path = root / CODEX_WORK_REQUESTS_DIR / f"{request_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "request_id": request_id,
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "lane_id": lane_id,
        "domain_id": "domain.context_active_resolver",
        "role_id": "role.context_cartographer",
        "role_tier": "R4_CONTEXT_CARTOGRAPHER",
        "callsign": "Noether",
        "work_class": "test",
        "request_kind": "test_worker_start_readiness",
        "working_capsule_identity": working_capsule_identity or _working_capsule_identity(root),
    }
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_worker_start_readiness_action_blocks_missing_lane_context(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver import execute_domain_weaver_action

    _write_queued_request(tmp_path, "codex_req_readiness_missing_lane_context", "missing_context_lane")

    result = execute_domain_weaver_action(tmp_path, {"action": "worker_start_readiness"})

    assert result["ok"] is False
    assert result["required_confirmation"] == "not_required_read_only"
    assert result["summary"]["projection_materialized"] is False
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["blocked_lane_count"] == 1
    assert result["summary"]["next_action"] == "hydrate_or_reissue_lane_active_context_packages"


def test_worker_start_readiness_action_allows_fresh_lane_context(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver import execute_domain_weaver_action

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="ready_context_lane",
    )
    _write_queued_request(tmp_path, "codex_req_readiness_ready_lane_context", "ready_context_lane")

    result = execute_domain_weaver_action(tmp_path, {"action": "worker_start_readiness"})

    assert result["ok"] is True
    assert result["summary"]["ready_to_start_workers"] is True
    assert result["summary"]["blocked_lane_count"] == 0
    assert result["results"]["worker_start_readiness"]["next_action"] == "worker_start_context_ready"
    readiness = result["results"]["worker_start_readiness"]
    request = readiness["request_results"][0]
    assert request["active_root_proof"]["proof_ok"] is True
    assert request["worker_identity"]["domain_id"] == "domain.context_active_resolver"
    assert request["worker_identity"]["role_id"] == "role.context_cartographer"
    assert request["worker_identity"]["role_tier"] == "R4_CONTEXT_CARTOGRAPHER"
    assert request["worker_identity"]["callsign"] == "Noether"
    assert request["domain_alignment"]["prestart_domain_checked"] == "domain.context_active_resolver"
    assert request["worker_return_status"]["product_state"] is False
    assert readiness["worker_shift_conflict_posture"]["risk_level"] == "none"


def test_runtime_branch_route_reports_worker_start_readiness(tmp_path: Path) -> None:
    from kernel.ion_runtime_service_control import invoke_runtime_service_route

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="runtime_ready_context_lane",
    )
    _write_queued_request(tmp_path, "codex_req_runtime_readiness_ready", "runtime_ready_context_lane")

    result = invoke_runtime_service_route(tmp_path, route_id="worker_start_readiness", args={})

    assert result["ok"] is True
    assert result["ready_to_start_workers"] is True
    assert result["mutates_active_state"] is False


def test_worker_start_readiness_blocks_shared_capsule_multi_queue_hazard(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import (
        CODEX_WORK_REQUESTS_DIR,
        build_domain_weaver_worker_start_readiness,
    )

    _root(tmp_path)
    request_root = tmp_path / CODEX_WORK_REQUESTS_DIR
    request_root.mkdir(parents=True, exist_ok=True)
    for index in (1, 2):
        (request_root / f"roleless_{index}.json").write_text(
            json.dumps(
                {
                    "request_id": f"codex_req_roleless_{index}",
                    "status": "QUEUED_FOR_CODEX_CARRIER",
                    "lane_id": "implementation_lane",
                    "domain_id": "domain.parallel_execution",
                    "work_class": "implementation",
                    "production_authority": False,
                    "live_execution_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    result = build_domain_weaver_worker_start_readiness(tmp_path)

    assert result["ok"] is False
    assert "shared_capsule_concurrency_hazard_live" in result["blockers"]
    assert result["worker_shift_conflict_posture"]["risk_level"] == "high"
    assert result["worker_shift_conflict_posture"]["queueable_role_or_mount_missing_count"] == 2
    assert result["summary"]["shared_capsule_concurrency_hazard"] is True


def test_worker_start_readiness_blocks_active_worker_shift_write_conflicts_and_unbound_identity(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="ready_context_lane",
    )
    _write_queued_request(tmp_path, "codex_req_readiness_ready_but_conflicted", "ready_context_lane")
    board_path = tmp_path / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift.board.v1",
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": "lease-unbound",
                        "worker_id": "UNBOUND_WORKER_ID",
                        "lease_mode": "write",
                        "paths": ["ION/04_packages/kernel/ion_domain_weaver_worker_start_readiness.py"],
                    },
                    {
                        "lease_id": "lease-overlap",
                        "worker_id": "worker.bound",
                        "lease_mode": "write",
                        "paths": ["ION/04_packages/kernel/ion_domain_weaver_worker_start_readiness.py"],
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = build_domain_weaver_worker_start_readiness(tmp_path)

    assert result["ok"] is False
    assert result["summary"]["ready_queueable_request_count"] == 1
    assert "worker_shift_conflict_posture_not_clear" in result["blockers"]
    assert result["worker_shift_conflict_posture"]["risk_level"] == "high"
    assert "unbound_worker_identity_present" in result["worker_shift_conflict_posture"]["blockers"]
    assert "overlapping_write_lease_hard_conflict_present" in result["worker_shift_conflict_posture"]["blockers"]
    assert result["worker_shift_conflict_posture"]["unbound_lease_worker_ids"] == ["lease-unbound"]


def test_worker_start_readiness_blocks_shared_codex_solo_working_capsule_identity(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="ready_context_lane",
    )
    identity = _working_capsule_identity(
        tmp_path,
        instance_capsule_id="shared_codex_solo",
        working_capsule_path=(tmp_path / "ION/05_context/current/codex_solo").as_posix(),
    )
    _write_queued_request(
        tmp_path,
        "codex_req_readiness_shared_codex_solo_capsule",
        "ready_context_lane",
        working_capsule_identity=identity,
    )

    result = build_domain_weaver_worker_start_readiness(tmp_path)
    request = result["request_results"][0]

    assert result["ok"] is False
    assert result["ready_to_start_workers"] is False
    assert "working_capsule_identity_preflight_blocked" in result["blockers"]
    assert "shared_codex_solo_as_working_capsule_forbidden" in request["blockers"]
    assert request["capsule_identity_preflight"]["classification"] == "identity_blocked"
    assert result["summary"]["capsule_identity_blocked_request_count"] == 1


def test_worker_start_readiness_blocks_old_root_working_capsule_reference(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="ready_context_lane",
    )
    identity = _working_capsule_identity(
        tmp_path,
        parent_capsule_ref="/home/sev/ION - Production/ION_CODEX FULL/ION/05_context/current/codex_solo/CAPSULE.md",
        lineage_id="lineage_from_old_root_incident",
    )
    _write_queued_request(
        tmp_path,
        "codex_req_readiness_old_root_capsule_ref",
        "ready_context_lane",
        working_capsule_identity=identity,
    )

    result = build_domain_weaver_worker_start_readiness(tmp_path)
    request = result["request_results"][0]

    assert result["ok"] is False
    assert result["ready_to_start_workers"] is False
    assert "working_capsule_identity_preflight_blocked" in result["blockers"]
    assert "stale_ion_codex_full_root_reference" in request["blockers"]
    assert request["capsule_identity_preflight"]["classification"] == "identity_blocked"
    assert "stale_ion_codex_full_root_reference" in result["summary"]["capsule_identity_blockers"]


def test_worker_start_readiness_blocks_shared_codex_solo_fallback_declaration(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="ready_context_lane",
    )
    _write_queued_request(
        tmp_path,
        "codex_req_readiness_shared_fallback",
        "ready_context_lane",
        extra={
            "working_capsule_identity": None,
            "shared_codex_solo_fallback_reason": "shared fallback witness only; not a unique worker capsule",
        },
    )

    result = build_domain_weaver_worker_start_readiness(tmp_path)
    request = result["request_results"][0]

    assert result["ok"] is False
    assert result["ready_to_start_workers"] is False
    assert "working_capsule_identity_preflight_blocked" in result["blockers"]
    assert "shared_codex_solo_fallback_not_worker_start_identity" in request["blockers"]
    assert request["capsule_identity_preflight"]["classification"] == "shared_codex_solo_fallback"


def test_worker_start_readiness_binds_capsule_identity_to_request_and_selected_mount(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="ready_context_lane",
    )
    wrong_mount = tmp_path / "ION/05_context/current/codex_agent_mounts/role_wrong__domain_wrong"
    identity = _working_capsule_identity(
        tmp_path,
        domain_id="domain.wrong",
        role_id="role.wrong",
        lane_id="wrong_context_lane",
        codex_agent_mount=wrong_mount.as_posix(),
    )
    _write_queued_request(
        tmp_path,
        "codex_req_readiness_capsule_binding_mismatch",
        "ready_context_lane",
        working_capsule_identity=identity,
        extra={
            "selected_mount_id": "role_wrong__domain_wrong",
            "selected_mount_path": "ION/05_context/current/codex_agent_mounts/role_wrong__domain_wrong",
        },
    )

    result = build_domain_weaver_worker_start_readiness(tmp_path)
    request = result["request_results"][0]

    assert result["ok"] is False
    assert result["next_action"] == "repair_working_capsule_identity_before_worker_start"
    assert result["summary"]["next_action"] == "repair_working_capsule_identity_before_worker_start"
    assert result["summary"]["resolver_ready_request_count"] == 1
    assert result["summary"]["ready_queueable_request_count"] == 0
    assert "queueable_lanes_missing_fresh_active_context" not in result["blockers"]
    assert "working_capsule_identity_request_binding_blocked" in result["blockers"]
    assert "working_capsule_domain_id_request_mismatch" in request["blockers"]
    assert "working_capsule_role_id_request_mismatch" in request["blockers"]
    assert "working_capsule_lane_id_request_mismatch" in request["blockers"]
    assert "request_selected_mount_id_mismatch" in request["blockers"]
    assert "request_selected_mount_path_mismatch" in request["blockers"]
    assert "working_capsule_selected_mount_id_mismatch" in request["blockers"]
    assert "working_capsule_selected_mount_path_mismatch" in request["blockers"]
    assert request["capsule_identity_request_binding"]["finding"] == "working_capsule_request_binding_blocked"


def test_worker_start_readiness_does_not_block_non_queueable_fallback_preview(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import (
        CODEX_WORK_REQUESTS_DIR,
        build_domain_weaver_worker_start_readiness,
    )

    _root(tmp_path)
    request_root = tmp_path / CODEX_WORK_REQUESTS_DIR
    request_root.mkdir(parents=True, exist_ok=True)
    (request_root / "fallback_preview.json").write_text(
        json.dumps(
            {
                "request_id": "codex_req_fallback_preview",
                "status": "PREVIEW_ONLY",
                "lane_id": "preview_lane",
                "domain_id": "domain.preview",
                "working_capsule_identity": None,
                "shared_codex_solo_fallback_reason": "fallback witness only for preview",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = build_domain_weaver_worker_start_readiness(tmp_path)

    assert result["queueable_requests"] == []
    assert result["blockers"] == []
    assert result["next_action"] == "no_queueable_worker_start_requests"
    assert result["summary"]["capsule_identity_blocked_request_count"] == 0


def test_worker_start_backlog_hygiene_separates_exact_ready_from_dirty_global_queue(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver_worker_start_readiness import (
        build_domain_weaver_worker_start_backlog_hygiene,
    )
    from kernel.ion_working_capsule_identity import build_working_capsule_identity

    mount_id = "role_wave_scheduler__domain_domain_weaver_fanout_control"
    _mount(tmp_path, mount_id, lane_id="architecture_lane")
    mount_root = tmp_path / "ION/05_context/current/codex_agent_mounts" / mount_id
    identity = build_working_capsule_identity(
        root=tmp_path,
        cwd=mount_root,
        domain_id="domain.domain_weaver_fanout_control",
        role_id="role.wave_scheduler",
        carrier_instance_id="codex_session_backlog_hygiene_test",
        codex_agent_mount=mount_root,
    ).to_dict()
    exact_path = _write_queued_request(
        tmp_path,
        "codex_req_exact_spawn_dispatch_ready",
        "architecture_lane",
        working_capsule_identity=identity,
        extra={
            "created_at": "2099-01-01T00:00:00+00:00",
            "updated_at": "2099-01-01T00:00:00+00:00",
            "domain_id": "domain.domain_weaver_fanout_control",
            "agent_role_id": "role.wave_scheduler",
            "role_tier": "specialist",
            "callsign": "Babbage",
            "work_class": "domain_weaver_spawn_dispatch",
            "request_kind": "domain_weaver_spawn_dispatch",
            "selected_mount_id": mount_id,
            "selected_mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
        },
    )
    _write_queued_request(
        tmp_path,
        "codex_req_dirty_missing_domain",
        "audit_lane",
        working_capsule_identity=None,
        extra={
            "created_at": "2001-01-01T00:00:00+00:00",
            "updated_at": "2001-01-01T00:00:00+00:00",
            "domain_id": "",
            "role_id": "",
            "agent_role_id": "",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
        },
    )

    result = build_domain_weaver_worker_start_backlog_hygiene(
        tmp_path,
        stale_after_seconds=60,
        example_limit=4,
    )

    assert result["hygiene_ok"] is False
    assert result["global_worker_start_readiness_ok"] is False
    assert result["exact_start_possible"] is True
    assert result["general_queue_processing_allowed"] is False
    assert result["codex_queue_run_started"] is False
    assert result["candidate_exact_request_paths"] == [
        exact_path.relative_to(tmp_path).as_posix()
    ]
    assert result["summary"]["exact_spawn_dispatch_ready_count"] == 1
    assert result["summary"]["missing_domain_request_count"] == 1
    assert result["summary"]["historical_or_stale_request_count"] == 1
    assert result["groups"]["exact_spawn_dispatch_ready"][0]["domain_id"] == "domain.domain_weaver_fanout_control"
    assert result["groups"]["missing_domain"][0]["request_id"] == "codex_req_dirty_missing_domain"
    assert any(
        packet["packet_id"] == "PCKT-DOMAIN-WEAVER-WORKER-START-READINESS-QUEUE-HYGIENE-SETTLEMENT-V0_1"
        for packet in result["next_packets"]
    )
    assert any(
        packet["packet_id"] == "PCKT-DOMAIN-WEAVER-EXACT-SPAWN-DISPATCH-START-GATE-V0_1"
        for packet in result["next_packets"]
    )


def test_worker_start_gate_blocks_missing_context_but_preserves_queue_request(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver import _domain_weaver_queue_live_carrier_work_requests

    _root(tmp_path)
    result = _domain_weaver_queue_live_carrier_work_requests(
        tmp_path,
        live_carrier_binding={"work_request_templates": [_queue_template("codex_req_resolver_gate_missing")]},
        start_workers_requested=True,
        max_worker_starts=1,
    )

    summary = result["summary"]
    ledger = result["ledger"]
    start = ledger["worker_start_results"][0]
    assert result["ok"] is False
    assert summary["queued_request_count"] == 1
    assert summary["worker_started_count"] == 0
    assert summary["worker_start_status"] == "worker_start_blocked_context_inactive"
    assert start["finding"] == "context_active_resolver_blocked"
    assert "no_matching_active_context_mount_for_lane" in start["blockers"]


def test_worker_start_gate_blocks_stale_context_but_writes_worker_start_receipt(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver import _domain_weaver_queue_live_carrier_work_requests

    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="resolver_gate_test_lane",
    )
    stale = time.time() - 200_000
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.md", (stale, stale))
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json", (stale, stale))

    result = _domain_weaver_queue_live_carrier_work_requests(
        tmp_path,
        live_carrier_binding={"work_request_templates": [_queue_template("codex_req_resolver_gate_stale")]},
        start_workers_requested=True,
        max_worker_starts=1,
    )

    ledger_path = tmp_path / result["queue_ledger_path"]
    start = result["ledger"]["worker_start_results"][0]
    assert ledger_path.is_file()
    assert result["summary"]["worker_start_status"] == "worker_start_blocked_context_inactive"
    assert start["finding"] == "context_active_resolver_blocked"
    assert "active_context_package_stale" in start["blockers"]
    assert result["summary"]["worker_started_count"] == 0


def test_repin_reaudit_worker_start_gate_blocks_missing_context_after_request_materialization(tmp_path: Path) -> None:
    from kernel.ion_domain_weaver import _domain_weaver_start_repin_plan_nemesis_reaudit

    _root(tmp_path)
    semantic_repin_plan = {
        "summary": {
            "semantic_repin_plan_ready": True,
            "repin_record_count": 1,
            "current_context_pin_count": 1,
            "current_drifted_pin_count": 0,
            "dynamic_context_reference_count": 1,
            "reauditable_return_count": 1,
        },
        "repin_records": [
            {
                "source_request_id": "codex_req_resolver_gate_repin_source",
                "source_request_path": "ION/05_context/current/codex_work/requests/source.json",
                "source_latest_return_packet_path": "",
                "source_task_return_body_path": "",
            }
        ],
    }

    result = _domain_weaver_start_repin_plan_nemesis_reaudit(
        tmp_path,
        semantic_repin_plan=semantic_repin_plan,
        packet_id="PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPINNED-NEMESIS-REAUDIT-20260601",
    )

    start = result["worker_start_result"]
    assert (tmp_path / result["request_path"]).is_file()
    assert result["summary"]["request_materialized"] is True
    assert result["summary"]["worker_start_status"] == "worker_start_blocked_context_inactive"
    assert result["summary"]["worker_started_count"] == 0
    assert start["finding"] == "context_active_resolver_blocked"


def _valid_refresh_gate(preflight: dict[str, object]) -> dict[str, object]:
    leases = preflight["gated_refresh_required_leases"] or preflight["target_mounts"][0]["required_refresh_leases"]
    target_paths = list(leases[0]["target_paths"])
    return {
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        "idempotency_key": "gauss-refresh-preview-001",
        "agent_id": "gauss_active_context_refresh",
        "lease_id": "lease-gauss-refresh-001",
        "lease_type": "exclusive_write",
        "lease_target_paths": target_paths,
        "lease_proof": {
            "ok": True,
            "active": True,
            "agent_id": "gauss_active_context_refresh",
            "lease_id": "lease-gauss-refresh-001",
            "lease_type": "exclusive_write",
            "target_paths": target_paths,
        },
    }


def _write_worker_shift_board(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
    lease_type: str = "exclusive_write",
    claimed_at: str | None = None,
) -> None:
    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = claimed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    _write_json(
        board_path,
        {
            "schema_id": "ion.worker_shift_board.v0_1",
            "updated_at": timestamp,
            "authority": {
                "accepted_state_authority": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
            "active_shifts": [],
            "active_leases": [
                {
                    "lease_id": lease_id,
                    "worker_id": agent_id,
                    "mode": lease_type,
                    "lease_type": lease_type,
                    "paths": target_paths,
                    "raw_paths": target_paths,
                    "resolved_paths": target_paths,
                    "status": "ACTIVE",
                    "claimed_at": timestamp,
                    "identity_binding_status": "BOUND_TRUE_NAME",
                }
            ],
            "stale_workers": [],
            "recent_signoffs": [],
            "recent_receipts": [],
        },
    )


def test_active_context_gated_refresh_blocks_missing_proof_fields(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)

    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )
    result = build_active_context_gated_refresh_plan(preflight)

    assert result["ok"] is False
    assert result["refresh_run"] is False
    assert result["mutates_active_state"] is False
    assert result["materialize_all_guard"]["materialize_all_allowed"] is False
    assert "active_context_refresh_confirmation_required" in result["blockers"]
    assert "active_context_refresh_idempotency_key_required" in result["blockers"]
    assert "active_context_refresh_actor_identity_required" in result["blockers"]
    assert "active_context_refresh_lease_id_required" in result["blockers"]
    assert "active_context_refresh_lease_proof_required" in result["blockers"]
    assert result["next_action"] == "repair_refresh_gate_inputs"


def test_active_context_gated_refresh_non_preview_requires_live_worker_shift_lease(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )

    result = build_active_context_gated_refresh_plan(
        preflight,
        root=tmp_path,
        preview_only=False,
        allow_write=True,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-apply-001",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-001",
        lease_type="exclusive_write",
    )

    assert result["ok"] is False
    assert result["write_gate_passed"] is False
    assert result["refresh_run"] is False
    assert result["mutates_active_state"] is False
    assert result["lease_gate"]["lease_evidence_source"] == "worker_shift.require_active_edit_lease"
    assert result["lease_gate"]["worker_shift_live_lease_required"] is True
    assert result["lease_gate"]["worker_shift_live_lease_gate"]["worker_shift_gate"]["finding"] == "active_edit_lease_not_found"
    assert "active_context_refresh_live_lease_not_found" in result["blockers"]
    assert "active_context_refresh_lease_proof_required" not in result["blockers"]


def test_active_context_gated_refresh_non_preview_ignores_self_attested_lease_proof(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )

    result = build_active_context_gated_refresh_plan(
        preflight,
        root=tmp_path,
        preview_only=False,
        allow_write=True,
        **_valid_refresh_gate(preflight),
    )

    assert result["ok"] is False
    assert result["write_gate_passed"] is False
    assert result["refresh_run"] is False
    assert result["mutates_active_state"] is False
    assert result["lease_gate"]["proof_present"] is True
    assert result["lease_gate"]["lease_evidence_source"] == "worker_shift.require_active_edit_lease"
    assert result["lease_gate"]["caller_supplied_lease_proof_scope"] == "preview_diagnostics_only_not_write_authority"
    assert result["lease_gate"]["provided_target_paths"] == []
    assert result["lease_gate"]["worker_shift_live_lease_gate"]["worker_shift_gate"]["finding"] == "active_edit_lease_not_found"
    assert "active_context_refresh_live_lease_not_found" in result["blockers"]


def test_active_context_gated_refresh_preview_seals_caller_proof_as_diagnostic_only(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )

    result = build_active_context_gated_refresh_plan(
        preflight,
        **_valid_refresh_gate(preflight),
    )

    assert result["ok"] is False
    assert result["write_gate_passed"] is False
    assert result["preview_diagnostic_only"] is True
    assert result["preview_inputs_valid"] is True
    assert result["write_authority_granted"] is False
    assert result["live_worker_shift_gate_checked"] is False
    assert result["non_preview_refresh_allowed"] is False
    assert result["readiness_claimed"] is False
    assert result["lease_gate"]["lease_evidence_source"] == "caller_supplied_preview_lease_proof_diagnostic_only"
    assert result["lease_gate"]["caller_supplied_lease_proof_scope"] == "preview_diagnostics_only_not_write_authority"
    assert result["lease_gate"]["preview_diagnostic_only"] is True
    assert result["lease_gate"]["write_authority_granted"] is False
    assert result["lease_gate"]["live_worker_shift_gate_checked"] is False
    assert result["lease_gate"]["non_preview_refresh_allowed"] is False
    assert result["lease_gate"]["target_coverage_ok"] is False
    assert result["lease_gate"]["diagnostic_target_coverage_ok"] is True
    assert result["target_coverage"]["lease_evidence_source"] == "caller_supplied_preview_lease_proof_diagnostic_only"
    assert result["target_coverage"]["target_coverage_ok"] is False
    assert result["target_coverage"]["diagnostic_target_coverage_ok"] is True
    assert result["receipt"]["result"] == "preview_diagnostic_only"
    assert result["receipt"]["write_gate_passed"] is False
    assert result["receipt"]["write_authority_granted"] is False
    assert result["receipt"]["live_worker_shift_gate_checked"] is False
    assert result["receipt"]["non_preview_refresh_allowed"] is False
    assert result["receipt"]["readiness_claimed"] is False
    assert "active_context_refresh_preview_diagnostic_only_not_write_authority" in result["blockers"]


def test_active_context_refresh_target_coverage_reports_partial_lease_target_proof(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="partial_coverage_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="partial_coverage_resolver_lane",
        max_age_seconds=1,
    )
    required_paths = preflight["gated_refresh_required_leases"][0]["target_paths"]
    partial_paths = [required_paths[0]]
    partial_proof = {
        "ok": True,
        "active": True,
        "agent_id": "gauss_active_context_refresh",
        "lease_id": "lease-gauss-refresh-001",
        "lease_type": "exclusive_write",
        "target_paths": partial_paths,
    }

    coverage = derive_active_context_refresh_target_coverage(
        preflight,
        lease_target_paths=partial_paths,
        lease_proof=partial_proof,
    )
    plan = build_active_context_gated_refresh_plan(
        preflight,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-preview-001",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-001",
        lease_type="exclusive_write",
        lease_target_paths=partial_paths,
        lease_proof=partial_proof,
    )

    assert coverage["target_coverage_ok"] is False
    assert coverage["required_target_paths"] == required_paths
    assert coverage["provided_target_paths"] == partial_paths
    assert coverage["missing_target_paths"] == [required_paths[1]]
    assert "lease_proof.target_paths" in coverage["proof_fields_required"]
    assert "active_context_refresh_lease_target_coverage_incomplete" in coverage["blockers"]
    assert plan["ok"] is False
    assert plan["write_gate_passed"] is False
    assert plan["lease_gate"]["missing_target_paths"] == [required_paths[1]]
    assert plan["target_coverage"]["missing_target_paths"] == [required_paths[1]]
    assert "active_context_refresh_lease_target_coverage_incomplete" in plan["blockers"]


def test_active_context_gated_refresh_preview_builds_receipt_without_mutation(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        active_md="old active context\n",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )

    result = build_active_context_gated_refresh_plan(
        preflight,
        **_valid_refresh_gate(preflight),
    )

    assert result["ok"] is False
    assert result["write_gate_passed"] is False
    assert result["preview_only"] is True
    assert result["refresh_run"] is False
    assert result["refresh_allowed_now"] is False
    assert result["mutates_active_state"] is False
    assert result["authority"]["materialization_write_authority"] is False
    assert result["preview_diagnostic_only"] is True
    assert result["write_authority_granted"] is False
    assert result["live_worker_shift_gate_checked"] is False
    assert result["non_preview_refresh_allowed"] is False
    assert result["readiness_claimed"] is False
    assert result["receipt"]["result"] == "preview_diagnostic_only"
    assert result["receipt"]["write_gate_passed"] is False
    assert result["receipt"]["write_authority_granted"] is False
    assert result["receipt"]["live_worker_shift_gate_checked"] is False
    assert result["receipt"]["non_preview_refresh_allowed"] is False
    assert result["receipt"]["readiness_claimed"] is False
    assert "active_context_refresh_preview_diagnostic_only_not_write_authority" in result["blockers"]
    assert "active_context_refresh_preview_only_not_run" in result["blockers"]
    assert result["refresh_plan"]["would_write_paths"] == preflight["gated_refresh_required_leases"][0]["target_paths"]
    assert (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").read_text(encoding="utf-8") == "old active context\n"


def test_active_context_gated_refresh_non_preview_write_path_remains_blocked(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        active_md="unchanged active context\n",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )
    _write_worker_shift_board(
        tmp_path,
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-001",
        target_paths=preflight["gated_refresh_required_leases"][0]["target_paths"],
    )

    result = build_active_context_gated_refresh_plan(
        preflight,
        root=tmp_path,
        preview_only=False,
        allow_write=True,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-apply-001",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-001",
        lease_type="exclusive_write",
    )

    assert result["ok"] is False
    assert result["write_gate_passed"] is True
    assert result["refresh_run"] is False
    assert result["mutates_active_state"] is False
    assert result["lease_gate"]["worker_shift_live_lease_gate"]["ok"] is True
    assert result["lease_gate"]["worker_shift_live_lease_gate"]["worker_shift_gate"]["ok"] is True
    assert result["receipt"]["result"] == "write_blocked"
    assert "active_context_refresh_write_path_not_implemented" in result["blockers"]
    assert result["next_action"] == "implement_separate_active_context_refresh_write_path"
    assert (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").read_text(encoding="utf-8") == "unchanged active context\n"


def test_active_context_refresh_apply_writes_only_gated_active_context_targets(tmp_path: Path) -> None:
    ion_dir = _mount(
        tmp_path,
        "role_context_cartographer__domain_context_active_resolver",
        active_md="old active context\n",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(ion_dir)
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )
    target_paths = preflight["gated_refresh_required_leases"][0]["target_paths"]
    _write_worker_shift_board(
        tmp_path,
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-apply-001",
        target_paths=target_paths,
    )

    result = apply_active_context_gated_refresh(
        preflight,
        root=tmp_path,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-apply-001",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-apply-001",
        execute_write=True,
    )

    assert result["ok"] is True
    assert result["refresh_run"] is True
    assert result["mutates_active_state"] is True
    assert result["accepted_state_claim"] is False
    assert result["authority"]["materialization_write_authority"] is False
    assert result["target_count"] == len(target_paths)
    assert result["gate"]["write_gate_passed"] is True
    assert (tmp_path / result["receipt_path"]).is_file()
    md_text = (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").read_text(encoding="utf-8")
    json_payload = json.loads((ion_dir / "ACTIVE_CONTEXT_PACKAGE.json").read_text(encoding="utf-8"))
    assert "gated_active_context_refresh" in md_text
    assert "role.context_cartographer" in md_text
    assert json_payload["schema_id"] == "ion.domain_weaver.active_context_package.refreshed.v0_1_candidate"
    assert json_payload["role_id"] == "role.context_cartographer"
    assert json_payload["domain_id"] == "domain.context_active_resolver"
    assert json_payload["lane_ids"] == ["stale_resolver_lane"]
    assert json_payload["accepted_state_authority"] is False
    assert all(row["changed"] is True for row in result["targets"])


def test_active_context_refresh_apply_creates_missing_manifest_only_package_files(tmp_path: Path) -> None:
    _root(tmp_path)
    mount = tmp_path / "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door"
    mount.mkdir(parents=True, exist_ok=True)
    _write_json(
        mount / "ION_AGENT_MOUNT_MANIFEST.json",
        {"role_id": "role.atlas", "domain_id": "ion_vnext_front_door"},
    )
    preflight = build_active_context_reissue_preflight(
        tmp_path,
        domain_id="domain.vnext_front_door",
        role_id="role.atlas",
        max_age_seconds=1,
    )
    target_paths = preflight["gated_refresh_required_leases"][0]["target_paths"]
    _write_worker_shift_board(
        tmp_path,
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-apply-missing-001",
        target_paths=target_paths,
    )

    result = apply_active_context_gated_refresh(
        preflight,
        root=tmp_path,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-apply-missing-001",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-apply-missing-001",
        execute_write=True,
    )

    assert result["ok"] is True
    assert (mount / ".ion/ACTIVE_CONTEXT_PACKAGE.md").is_file()
    assert (mount / ".ion/ACTIVE_CONTEXT_PACKAGE.json").is_file()
    payload = json.loads((mount / ".ion/ACTIVE_CONTEXT_PACKAGE.json").read_text(encoding="utf-8"))
    assert payload["domain_id"] == "domain.vnext_front_door"
    assert payload["semantic_identity"]["domain_alias_detected"] is True
    assert payload["semantic_identity"]["semantic_identity"]["alias_detected"] is True
    assert payload["accepted_state_authority"] is False


def test_active_context_refresh_apply_rejects_non_mount_target_paths(tmp_path: Path) -> None:
    _root(tmp_path)
    bad_path = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    preflight = {
        "schema_id": "ion.domain_weaver.active_context_reissue_preflight.v0_1_candidate",
        "packet_id": "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-REISSUE-PREFLIGHT-AND-GATED-REFRESH-V0_1",
        "preflight_completed": True,
        "refresh_run": False,
        "mutates_active_state": False,
        "active_root": tmp_path.as_posix(),
        "target_mounts": [],
        "mount_package_refs_requiring_reissue": [
            {"path": bad_path, "mount_id": "domain_weaver", "reason": "bad_path_probe"}
        ],
    }
    _write_worker_shift_board(
        tmp_path,
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-apply-bad-001",
        target_paths=[bad_path],
    )

    result = apply_active_context_gated_refresh(
        preflight,
        root=tmp_path,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-apply-bad-001",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-apply-bad-001",
        execute_write=True,
    )

    assert result["ok"] is False
    assert result["refresh_run"] is False
    assert result["mutates_active_state"] is False
    assert "active_context_refresh_target_must_be_mount_ion_active_context_package" in result["blockers"]
    assert not (tmp_path / bad_path).exists()


def test_active_context_gated_refresh_non_preview_blocks_wrong_worker_shift_lease(tmp_path: Path) -> None:
    cases = [
        {
            "name": "wrong_actor",
            "agent_id": "wrong_actor",
            "lease_type": "exclusive_write",
            "paths": "required",
            "claimed_at": None,
            "expected": "active_context_refresh_live_lease_actor_mismatch",
        },
        {
            "name": "wrong_mode",
            "agent_id": "gauss_active_context_refresh",
            "lease_type": "write",
            "paths": "required",
            "claimed_at": None,
            "expected": "active_context_refresh_live_lease_mode_mismatch",
        },
        {
            "name": "wrong_path",
            "agent_id": "gauss_active_context_refresh",
            "lease_type": "exclusive_write",
            "paths": ["ION/05_context/current/codex_agent_mounts/other/.ion/ACTIVE_CONTEXT_PACKAGE.md"],
            "claimed_at": None,
            "expected": "active_context_refresh_live_lease_target_coverage_incomplete",
        },
        {
            "name": "stale",
            "agent_id": "gauss_active_context_refresh",
            "lease_type": "exclusive_write",
            "paths": "required",
            "claimed_at": (datetime.now(timezone.utc) - timedelta(hours=5)).replace(microsecond=0).isoformat(),
            "expected": "active_context_refresh_live_lease_stale",
        },
    ]
    for case in cases:
        root = tmp_path / case["name"]
        ion_dir = _mount(
            root,
            "role_context_cartographer__domain_context_active_resolver",
            lane_id="stale_resolver_lane",
        )
        _mark_active_context_refs_stale(ion_dir)
        preflight = build_active_context_reissue_preflight(
            root,
            domain_id="domain.context_active_resolver",
            role_id="role.context_cartographer",
            lane="stale_resolver_lane",
            max_age_seconds=1,
        )
        required_paths = preflight["gated_refresh_required_leases"][0]["target_paths"]
        target_paths = required_paths if case["paths"] == "required" else case["paths"]
        _write_worker_shift_board(
            root,
            agent_id=case["agent_id"],
            lease_id="lease-gauss-refresh-001",
            target_paths=target_paths,
            lease_type=case["lease_type"],
            claimed_at=case["claimed_at"],
        )

        result = build_active_context_gated_refresh_plan(
            preflight,
            root=root,
            preview_only=False,
            allow_write=True,
            confirmation="ION_BOUNDED_WRITE_CONFIRMED",
            idempotency_key=f"gauss-refresh-apply-{case['name']}",
            agent_id="gauss_active_context_refresh",
            lease_id="lease-gauss-refresh-001",
            lease_type="exclusive_write",
        )

        assert result["ok"] is False
        assert result["write_gate_passed"] is False
        assert case["expected"] in result["blockers"]


def test_active_context_gated_refresh_non_preview_blocks_wrong_root_live_lease(tmp_path: Path) -> None:
    active_root = tmp_path / "active"
    wrong_root = tmp_path / "wrong"
    active_ion_dir = _mount(
        active_root,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    _mark_active_context_refs_stale(active_ion_dir)
    _mount(
        wrong_root,
        "role_context_cartographer__domain_context_active_resolver",
        lane_id="stale_resolver_lane",
    )
    preflight = build_active_context_reissue_preflight(
        active_root,
        domain_id="domain.context_active_resolver",
        role_id="role.context_cartographer",
        lane="stale_resolver_lane",
        max_age_seconds=1,
    )
    _write_worker_shift_board(
        wrong_root,
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-001",
        target_paths=preflight["gated_refresh_required_leases"][0]["target_paths"],
    )

    result = build_active_context_gated_refresh_plan(
        preflight,
        root=wrong_root,
        preview_only=False,
        allow_write=True,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="gauss-refresh-apply-wrong-root",
        agent_id="gauss_active_context_refresh",
        lease_id="lease-gauss-refresh-001",
        lease_type="exclusive_write",
    )

    assert result["ok"] is False
    assert result["write_gate_passed"] is False
    assert "active_context_refresh_live_lease_root_mismatch" in result["blockers"]
