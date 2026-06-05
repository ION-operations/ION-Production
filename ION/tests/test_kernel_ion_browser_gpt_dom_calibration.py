import json
from pathlib import Path

from kernel.ion_browser_gpt_dom_calibration import (
    BASE_DIR,
    PROFILE_SCHEMA_ID,
    browser_gpt_detected_selector_is_acceptable,
    build_selector_profile,
    default_dom_probe_extension_root,
    latest_browser_gpt_dom_summary,
    merge_surface_candidate_sets,
    playwright_auto_interaction_plan,
    probe_control_candidate_is_safe,
    probe_phase_sweep_projection,
    probe_surface_coverage_from_snapshot,
    prior_native_dom_evidence,
    record_browser_gpt_dom_probe_snapshot,
    surface_candidates_from_prior_native_dom_evidence,
    surface_candidates_from_probe_snapshot,
    write_seed_candidate_profile,
    _playwright_discovery_script,
    _playwright_wait_for_chatgpt_ready,
)
from kernel.ion_cockpit_view_model import build_cockpit_view_model


def write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def seed_minimal_cockpit_runtime(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    current = "ION/05_context/current"
    write_json(root, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "ready"})
    write_json(root, f"{current}/ACTIVE_WORK_PACKET.json", {"carrier": "codex_cli", "objective": "browser gpt dom"})
    write_json(root, f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json", {"role_spawn_plan": []})
    write_json(root, f"{current}/ACTIVE_CARRIER_TURN_PACKET.json", {"carrier": "codex_cli", "objective": "browser gpt dom"})
    write_json(root, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(root, f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json", {"items": []})
    write_json(root, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": []})
    write_json(root, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(root, f"{current}/ACTIVE_FRONT_DOOR_PROOF_TRACE.json", {})
    write_json(root, f"{current}/ACTIVE_LANE_TIMELINE_VIEW_MODEL.json", {})
    write_json(root, f"{current}/ACTIVE_RECEIPT_HYDRATION_VIEW_MODEL.json", {})
    write_json(root, f"{current}/ACTIVE_RUNTIME_DEBUG_OVERLAY.json", {})
    write_json(root, f"{current}/SAFE_FULL_PROJECT_PACKAGE_RESULT_V110.json", {})
    write_json(root, f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json", {})


def test_seed_candidate_profile_writes_schema_health_and_receipt(tmp_path: Path):
    result = write_seed_candidate_profile(tmp_path, "chatgpt_web_test")

    assert result["ok"] is True
    assert result["status"] == "degraded"
    assert result["production_authority"] is False
    assert (tmp_path / result["profile_path"]).exists()
    assert (tmp_path / result["health_path"]).exists()
    assert (tmp_path / result["receipt_path"]).exists()
    assert (tmp_path / BASE_DIR / "schemas/browser_gpt_dom_selector_profile.schema.json").exists()

    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))
    assert profile["schema_id"] == PROFILE_SCHEMA_ID
    assert profile["surfaces"]["composer"]["selector"] == "#prompt-textarea"
    assert profile["authority"]["silent_send_authority"] is False


def test_live_candidate_profile_marks_required_surfaces_ready():
    profile = build_selector_profile(
        "chatgpt_web_live_test",
        surface_candidates={
            "composer": [{"selector": "#prompt-textarea", "score": 92, "validated_by": ["visible", "unique_selector", "editable_shape"]}],
            "send_button": [{"selector": "[data-testid='send-button']", "score": 88, "validated_by": ["visible", "unique_selector"]}],
            "message_list": [{"selector": "main", "score": 81, "validated_by": ["visible", "unique_selector"]}],
        },
        calibration_source="unit_test_live_candidates",
    )

    assert profile["status"] == "selector_profile_candidate_ready"
    assert profile["surfaces"]["composer"]["confidence"] == 0.92
    assert profile["surfaces"]["send_button"]["status"] == "validated_candidate"


def test_default_dom_probe_extension_root_detects_operator_final(tmp_path: Path):
    extension_root = tmp_path / "browser_extension/browser_gpt_dom_probe/OPERATOR_FINAL"
    extension_root.mkdir(parents=True)
    (extension_root / "manifest.json").write_text("{}", encoding="utf-8")
    (extension_root / "content.js").write_text("(() => {})();\n", encoding="utf-8")

    assert default_dom_probe_extension_root(tmp_path) == extension_root


def test_merge_surface_candidate_sets_preserves_best_score_and_phases():
    merged = merge_surface_candidate_sets(
        {
            "composer": [
                {
                    "selector": "#prompt-textarea",
                    "score": 70,
                    "phase": "base",
                    "rect": {"left": 1, "top": 2, "width": 300, "height": 40},
                }
            ]
        },
        {
            "composer": [
                {
                    "selector": "#prompt-textarea",
                    "score": 92,
                    "phase": "after_menu",
                    "rect": {"left": 1, "top": 2, "width": 300, "height": 40},
                }
            ]
        },
    )

    assert merged["composer"][0]["score"] == 92
    assert merged["composer"][0]["observed_in_phases"] == ["base", "after_menu"]


def test_playwright_auto_interaction_plan_never_clicks_send():
    plan = playwright_auto_interaction_plan()

    assert plan
    assert "send_button" not in {item["surface_id"] for item in plan}
    assert {"file_attach_button", "model_picker", "thinking_mode_control"} <= {item["surface_id"] for item in plan}


def test_send_button_seed_selectors_are_not_generic_svg_buttons():
    profile = build_selector_profile("chatgpt_web_seed_test")

    send_surface = profile["surfaces"]["send_button"]
    assert "button:has(svg)" not in [send_surface["selector"], *send_surface["fallbacks"]]
    assert "Enter when composer has a draft" in send_surface["hotkeys"]
    assert profile["surfaces"]["slash_command_menu"]["hotkeys"] == ["/"]
    assert profile["surfaces"]["slash_command_option"]["kind"] == "composer_command_option"


def test_native_snapshot_rejects_voice_button_as_send_selector_even_operator_pick(tmp_path: Path):
    write_json(
        tmp_path,
        "ION/05_context/current/chatops_bridge/runtime/native_dom_snapshots/latest_native_dom_snapshot.json",
        {
            "captured_at": "2026-05-26T18:45:26.842Z",
            "url": "https://chatgpt.com/",
            "browser_gpt_dom": {
                "status": "degraded",
                "required_surface_presence": {"composer": True, "send_button": False, "message_list": True},
                "detected": {
                    "composer": {"found": True, "selector": "#prompt-textarea", "tag": "div", "attrs": {"role": "textbox"}},
                    "send_button": {"found": False, "role": "send_button"},
                    "message_list": {"found": True, "selector": "#main", "tag": "main"},
                    "voice_mic_button": {"found": True, "selector": "button[aria-label=\"Start Voice\"]", "tag": "button", "label": "Start Voice"},
                },
            },
            "browser_gpt_operator_picks": {
                "targets": {
                    "send_button": {"found": True, "selector": "button[aria-label=\"Start Voice\"]", "label": "Start Voice", "tag": "button"},
                }
            },
        },
    )

    evidence = prior_native_dom_evidence(tmp_path)
    candidates = surface_candidates_from_prior_native_dom_evidence(evidence)

    assert evidence["browser_gpt_required_surface_presence"]["send_button"] is False
    assert "send_button" not in evidence["browser_gpt_selectors"]
    assert "send_button" not in candidates


def test_playwright_discovery_script_includes_generic_scan_and_new_surfaces():
    script = _playwright_discovery_script("unit")

    assert "generic_scan" in script
    assert "tools_menu_opener" in script
    assert "drawer_surface" in script
    assert '"phase": "unit"' not in script  # phase is a JS const, not injected as raw JSON object text.


def test_playwright_wait_for_chatgpt_ready_reports_timeout_for_challenge_text():
    class FakePage:
        def __init__(self):
            self.calls = 0

        def evaluate(self, _script):
            self.calls += 1
            return {
                "ready": False,
                "cloudflare": True,
                "body_preview": "Verifying... Cloudflare",
            }

        def wait_for_timeout(self, _timeout):
            return None

    result = _playwright_wait_for_chatgpt_ready(FakePage(), timeout_ms=1)

    assert result["status"] == "timeout"
    assert result["cloudflare"] is True


def test_prior_native_dom_evidence_reads_needs_routed_snapshot(tmp_path: Path):
    write_json(
        tmp_path,
        "Needs_Routed/ion_native_dom_snapshot_20260514T1857344.json",
        {
            "captured_at": "2026-05-14T18:57:34.449Z",
            "url": "https://chatgpt.com/g/g-test",
            "detected": {
                "rail_host": {"selector": "#stage-slideover-sidebar"},
                "sidebar_toggle": {"selector": "button[aria-label=\"Open sidebar\"]"},
            },
            "ion_state": {"native_drawer_is_open": False, "native_left_mode": "context"},
        },
    )

    evidence = prior_native_dom_evidence(tmp_path)

    assert evidence["status"] == "present"
    assert evidence["source_kind"] == "needs_routed_native_dom_snapshot"
    assert evidence["selectors"]["rail_host"] == "#stage-slideover-sidebar"


def test_probe_snapshot_candidates_include_composer_send_and_upload():
    snapshot = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
        "url": "https://chatgpt.com/",
        "visible_controls": [
            {"selector": "#prompt-textarea", "tag": "textarea", "role": "textbox", "rect": {"width": 500, "height": 80}},
            {"selector": "button[aria-label='Send prompt']", "tag": "button", "aria_label": "Send prompt", "rect": {"width": 36, "height": 36}},
            {"selector": "#composer-plus-btn", "tag": "button", "aria_label": "Add files and more", "rect": {"width": 36, "height": 36}},
        ],
        "visible_messages": [],
    }

    candidates = surface_candidates_from_probe_snapshot(snapshot)

    assert candidates["composer"][0]["selector"] == "#prompt-textarea"
    assert candidates["send_button"][0]["selector"] == "button[aria-label='Send prompt']"
    assert candidates["file_attach_button"][0]["selector"] == "#composer-plus-btn"


def test_record_probe_snapshot_writes_profile_artifacts(tmp_path: Path):
    result = record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "probe.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-25T23:58:00Z",
                "url": "https://chatgpt.com/",
                "dom_health": {"composer_present": True, "visible_button_count": 3},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "textarea", "role": "textbox", "rect": {"width": 500, "height": 80}},
                    {"selector": "button[aria-label='Send prompt']", "tag": "button", "aria_label": "Send prompt", "rect": {"width": 36, "height": 36}},
                ],
                "visible_messages": [],
                "targets": [],
                "target_count": 0,
            },
        },
    )

    assert result["ok"] is True
    assert (tmp_path / result["snapshot_path"]).exists()
    assert (tmp_path / result["profile_path"]).exists()
    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))
    assert profile["calibration_source"] == "dom_probe_extension_auto_snapshot"
    assert profile["surfaces"]["composer"]["selector"] == "#prompt-textarea"


def test_chatops_probe_snapshot_filters_extension_queue_send_button():
    snapshot = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
        "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True},
        "dom_health": {"composer_present": False},
        "visible_controls": [
            {
                "selector": "button[aria-label=\"Send next queued item\"]",
                "tag": "button",
                "role": "send_button",
                "aria_label": "Send next queued item",
                "text_preview": "Send next queued item Send",
            },
            {
                "selector": "#composer-plus-btn",
                "tag": "button",
                "aria_label": "Add files and more",
            },
        ],
        "visible_messages": [],
    }

    candidates = surface_candidates_from_probe_snapshot(snapshot)

    assert "send_button" not in candidates
    assert candidates["file_attach_button"][0]["selector"] == "#composer-plus-btn"
    assert probe_control_candidate_is_safe("send_button", snapshot["visible_controls"][0], snapshot) is False


def test_probe_surface_candidates_accept_empty_message_list_region():
    snapshot = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
        "source": {
            "extension": "ION ChatOps Bridge",
            "compatibility_auto_probe": True,
            "build_marker": "browser_gpt_dom_auto_probe_20260526T0212Z",
        },
        "dom_health": {"composer_present": True, "send_available": True, "visible_button_count": 3},
        "visible_controls": [
            {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
            {"selector": "#composer-submit-button", "tag": "button", "role": "send_button", "source_surface": "send_button"},
            {"selector": "main", "tag": "main", "role": "message_list", "source_surface": "message_list"},
        ],
        "visible_messages": [],
    }

    candidates = surface_candidates_from_probe_snapshot(snapshot)
    coverage = probe_surface_coverage_from_snapshot(snapshot)

    assert candidates["send_button"][0]["selector"] == "#composer-submit-button"
    assert candidates["message_list"][0]["selector"] == "main"
    assert "send_button" not in coverage["missing_required_surface_ids"]
    assert "message_list" not in coverage["missing_required_surface_ids"]


def test_fresh_chat_probe_preserves_draft_send_selector_from_recent_phase(tmp_path: Path):
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "draft_send_phase.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T18:38:52Z",
                "url": "https://chatgpt.com/",
                "capture_reason": "phase_sweep_draft_send_button_probe",
                "phase_sweep": {"phase": "draft_send_button_probe", "status": "observed"},
                "dom_health": {"composer_present": True, "composer_editable": True, "send_available": True},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "#composer-submit-button", "tag": "button", "role": "send_button", "source_surface": "send_button", "aria_label": "Send prompt"},
                    {"selector": "#main", "tag": "main", "role": "message_list", "source_surface": "message_list"},
                ],
                "visible_messages": [],
                "targets": [],
            },
        },
    )
    result = record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "fresh_new_chat.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T18:45:46Z",
                "url": "https://chatgpt.com/",
                "capture_reason": "auto",
                "dom_health": {"composer_present": True, "composer_editable": True, "send_available": False},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "#main", "tag": "main", "role": "message_list", "source_surface": "message_list"},
                    {"selector": "button[aria-label=\"Start Voice\"]", "tag": "button", "role": "voice_mic_button", "source_surface": "voice_mic_button", "aria_label": "Start Voice"},
                ],
                "visible_messages": [],
                "targets": [],
            },
        },
    )

    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))
    twin = latest_browser_gpt_dom_summary(tmp_path)["chatgpt_dom_twin"]

    assert result["status"] == "ready"
    assert profile["surfaces"]["send_button"]["selector"] == "#composer-submit-button"
    assert profile["page_state_evidence"]["latest_page_state"] == "fresh_empty_chat"
    assert twin["send"]["selector"] == "#composer-submit-button"
    assert twin["composer"]["send_available"] is False
    assert twin["state"]["send_selector_state"] == "latent_until_draft"


def test_probe_surface_candidates_reject_stale_drawer_menu_false_positives():
    snapshot = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
        "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True},
        "dom_health": {"composer_present": True},
        "visible_controls": [
            {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
            {
                "selector": "button[aria-label='Minimize ChatGPT drawer']",
                "tag": "button",
                "role": "model_menu_option",
                "source_surface": "model_menu_option",
                "aria_label": "Minimize ChatGPT drawer",
            },
            {
                "selector": "button[aria-label='Open Agent drawer panel']",
                "tag": "button",
                "role": "tools_menu_option",
                "source_surface": "tools_menu_option",
                "aria_label": "Open Agent drawer panel",
            },
        ],
        "visible_messages": [],
    }

    candidates = surface_candidates_from_probe_snapshot(snapshot)

    assert "composer" in candidates
    assert "model_menu_option" not in candidates
    assert "tools_menu_option" not in candidates


def test_probe_surface_candidates_reject_sidebar_search_as_slash_command():
    snapshot = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
        "dom_health": {"composer_present": True},
        "visible_controls": [
            {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
            {
                "selector": "div > nav > div:nth-of-type(2) > div:nth-of-type(2) > button",
                "tag": "button",
                "role": "slash_command_option",
                "source_surface": "slash_command_option",
                "aria_label": "Search chats",
                "text_preview": "Search chats",
            },
        ],
        "visible_messages": [],
    }

    candidates = surface_candidates_from_probe_snapshot(snapshot)

    assert "composer" in candidates
    assert "slash_command_option" not in candidates


def test_record_probe_snapshot_sanitizes_extension_queue_control_from_artifact(tmp_path: Path):
    result = record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "live_polluted_probe.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T01:11:18Z",
                "url": "https://chatgpt.com/",
                "source": {
                    "extension": "ION ChatOps Bridge",
                    "compatibility_auto_probe": True,
                    "build_marker": "browser_gpt_dom_auto_probe_20260526T0212Z",
                },
                "dom_health": {"composer_present": True, "visible_button_count": 6},
                "visible_controls": [
                    {
                        "selector": "#prompt-textarea",
                        "tag": "div",
                        "role": "composer",
                        "source_surface": "composer",
                        "aria_label": "Chat with ChatGPT",
                    },
                    {
                        "selector": "button[aria-label=\"Send next queued message\"]",
                        "tag": "button",
                        "role": "send_button",
                        "source_surface": "send_button",
                        "aria_label": "Send next queued message",
                        "text_preview": "Send next queued message Send",
                    },
                    {
                        "selector": "#composer-plus-btn",
                        "tag": "button",
                        "role": "file_attach_button",
                        "source_surface": "file_attach_button",
                        "aria_label": "Add files and more",
                    },
                ],
                "visible_messages": [],
                "targets": [],
                "target_count": 0,
            },
        },
    )

    assert result["finding"] == "probe_snapshot_recorded"
    artifact = json.loads((tmp_path / result["snapshot_path"]).read_text(encoding="utf-8"))
    controls = artifact["snapshot"]["visible_controls"]
    assert [item["selector"] for item in controls] == ["#prompt-textarea", "#composer-plus-btn"]
    assert artifact["snapshot"]["sanitization"]["removed_visible_control_count"] == 1
    assert artifact["source"]["extension"] == "ION ChatOps Bridge"
    assert artifact["source"]["sanitized"] is True
    assert artifact["source"]["build_marker"] == "browser_gpt_dom_auto_probe_20260526T0212Z"

    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))
    assert profile["surfaces"]["composer"]["selector"] == "#prompt-textarea"
    assert profile["probe_snapshot_evidence"]["visible_control_count"] == 2
    assert profile["probe_snapshot_evidence"]["removed_visible_control_count"] == 1


def test_probe_surface_coverage_reports_phase_dependent_missing_surfaces():
    snapshot = {
        "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
        "dom_health": {"composer_present": True, "visible_button_count": 4},
        "visible_controls": [
            {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
            {"selector": "#composer-plus-btn", "tag": "button", "role": "file_attach_button", "source_surface": "file_attach_button"},
            {"selector": "button[aria-label='Open sidebar']", "tag": "button", "role": "left_sidebar_toggle", "source_surface": "left_sidebar_toggle"},
        ],
        "visible_messages": [],
    }

    coverage = probe_surface_coverage_from_snapshot(snapshot)

    assert "composer" in coverage["found_surface_ids"]
    assert "file_attach_button" in coverage["found_surface_ids"]
    assert "send_button" in coverage["missing_required_surface_ids"]
    actions = {item["surface_id"]: item for item in coverage["phase_capture_actions"]}
    assert actions["file_upload_menu_option"]["phase"] == "attach_menu_open"
    assert actions["file_upload_menu_option"]["opener_found"] is True
    assert actions["model_menu_option"]["opener_found"] is False


def test_probe_snapshot_projection_includes_latest_surface_coverage(tmp_path: Path):
    result = record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "coverage_probe.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T01:20:00Z",
                "url": "https://chatgpt.com/",
                "dom_health": {"composer_present": True, "visible_button_count": 3},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "#composer-plus-btn", "tag": "button", "role": "file_attach_button", "source_surface": "file_attach_button"},
                ],
                "visible_messages": [],
                "targets": [],
                "target_count": 0,
            },
        },
    )

    assert result["finding"] == "probe_snapshot_recorded"
    summary = latest_browser_gpt_dom_summary(tmp_path)
    coverage = summary["probe_intake"]["latest_usable_probe"]["surface_coverage"]
    assert coverage["found_surface_count"] >= 2
    assert coverage["phase_capture_action_count"] >= 1
    assert summary["probe_intake"]["latest_surface_coverage"]["schema_id"] == "ion.browser_gpt_dom_probe_surface_coverage.v1"


def test_probe_projection_effective_coverage_backfills_ready_profile_required_surfaces(tmp_path: Path):
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "stale_probe.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T02:28:34Z",
                "url": "https://chatgpt.com/",
                "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True},
                "dom_health": {"composer_present": True, "visible_button_count": 1},
                "visible_controls": [{"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"}],
                "visible_messages": [],
                "targets": [],
            },
        },
    )
    write_json(
        tmp_path,
        "ION/05_context/current/browser_gpt_dom_profiles/latest.selector_profile.json",
        {
            "schema_id": "ion.browser_gpt_dom_selector_profile.v1",
            "surfaces": {
                "composer": {"selector": "#prompt-textarea", "confidence": 0.88, "candidate_count": 1, "validated_by": ["probe_snapshot"]},
                "send_button": {"selector": "#composer-submit-button", "confidence": 0.86, "candidate_count": 1, "validated_by": ["native_dom_snapshot"]},
                "message_list": {"selector": "main", "confidence": 0.82, "candidate_count": 1, "validated_by": ["native_dom_snapshot"]},
            },
        },
    )

    summary = latest_browser_gpt_dom_summary(tmp_path)
    effective = summary["probe_intake"]["effective_surface_coverage"]
    issue_resolution = summary["probe_intake"]["issue_resolution"]

    assert summary["probe_intake"]["latest_in_page_script_build_status"] == "in_page_script_unmarked"
    assert effective["missing_required_surface_count"] == 0
    assert set(effective["profile_backfilled_surface_ids"]) == {"send_button", "message_list"}
    assert issue_resolution["status"] == "handled"
    assert issue_resolution["blocking_issue_count"] == 0
    assert issue_resolution["operator_action_required"] is False
    assert {row["finding"] for row in issue_resolution["rows"]} >= {
        "raw_probe_required_surface_gap_compensated",
        "in_page_script_unmarked_but_compensated",
    }


def test_chatgpt_dom_twin_projects_controls_without_send_authority(tmp_path: Path):
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "twin_probe.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T03:05:00Z",
                "url": "https://chatgpt.com/",
                "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True, "build_marker": "browser_gpt_dom_auto_probe_20260526T0212Z"},
                "dom_health": {"composer_present": True, "composer_editable": True, "send_available": True, "response_streaming": False},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "#composer-submit-button", "tag": "button", "role": "send_button", "source_surface": "send_button", "aria_label": "Send prompt"},
                    {"selector": "#main", "tag": "main", "role": "message_list", "source_surface": "message_list"},
                    {"selector": "#composer-plus-btn", "tag": "button", "role": "file_attach_button", "source_surface": "file_attach_button", "aria_label": "Add files and more"},
                    {"selector": "button[aria-label='GPT-5']", "tag": "button", "role": "model_picker", "source_surface": "model_picker", "aria_label": "GPT-5"},
                    {"selector": "button[aria-label='Thinking']", "tag": "button", "role": "thinking_mode_control", "source_surface": "thinking_mode_control", "aria_label": "Thinking"},
                    {"selector": "button[aria-label='Tools']", "tag": "button", "role": "tools_menu_opener", "source_surface": "tools_menu_opener", "aria_label": "Tools"},
                ],
                "visible_messages": [
                    {"role": "user", "selector": "[data-message-author-role='user']", "text_preview": "hello"},
                    {"role": "assistant", "selector": "[data-message-author-role='assistant']", "text_preview": "hi"},
                ],
                "targets": [],
            },
        },
    )

    summary = latest_browser_gpt_dom_summary(tmp_path)
    twin = summary["chatgpt_dom_twin"]
    controls = {item["surface_id"]: item for item in twin["controls"]}

    assert twin["schema_id"] == "ion.browser_gpt_dom_twin.v1"
    assert twin["status"] == "ready"
    assert twin["composer"]["selector"] == "#prompt-textarea"
    assert twin["send"]["selector"] == "#composer-submit-button"
    assert twin["send"]["approved_send_required"] is True
    assert twin["send"]["live_send_authority"] is False
    assert twin["transcript"]["message_count"] == 2
    assert {"file_attach_button", "model_picker", "thinking_mode_control", "tools_menu_opener"} <= set(controls)
    assert summary["authority"]["approved_send_required"] is True


def test_chatgpt_dom_twin_does_not_treat_previewless_anchors_as_readable_messages(tmp_path: Path):
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "twin_probe_previewless.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T04:50:00Z",
                "url": "https://chatgpt.com/",
                "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True},
                "dom_health": {"composer_present": True, "composer_editable": True, "send_available": True},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "#composer-submit-button", "tag": "button", "role": "send_button", "source_surface": "send_button"},
                    {"selector": "#main", "tag": "main", "role": "message_list", "source_surface": "message_list"},
                ],
                "visible_messages": [
                    {"role": "user", "selector": "section > div > div", "text_length": 42},
                    {"role": "assistant", "selector": "section > div > div:nth-of-type(2)", "text_length": 84},
                ],
                "targets": [],
            },
        },
    )

    transcript = latest_browser_gpt_dom_summary(tmp_path)["chatgpt_dom_twin"]["transcript"]

    assert transcript["message_count"] == 0
    assert transcript["raw_visible_message_count"] == 2
    assert transcript["unreadable_message_count"] == 2
    assert transcript["readability_status"] == "unreadable_anchors"
    assert transcript["empty_transcript"] is True


def test_chatgpt_dom_twin_preserves_full_text_and_visible_timeline_events(tmp_path: Path):
    full_response = (
        "Proceed complete.\n\n"
        "Implemented: runtime_freshness_probe\n\n"
        "Added a read-only route under runtime_services:\n"
        "runtime_services.runtime_freshness_probe\n\n"
        "Receipt: ION/05_context/current/runtime_services/test_run_receipts/example.json"
    )
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "twin_probe_timeline.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-06-02T15:30:00Z",
                "url": "https://chatgpt.com/",
                "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True},
                "dom_health": {"composer_present": True, "composer_editable": True, "send_available": True, "response_streaming": False},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "#composer-submit-button", "tag": "button", "role": "send_button", "source_surface": "send_button"},
                    {"selector": "#main", "tag": "main", "role": "message_list", "source_surface": "message_list"},
                ],
                "visible_messages": [
                    {"role": "assistant", "selector": "[data-message-author-role='assistant']", "text_full": full_response, "text_preview": "Proceed complete.", "text_length": len(full_response)},
                ],
                "timeline_events": [
                    {"event_type": "message", "role": "assistant", "index": 0, "text_full": full_response, "text_preview": "Proceed complete."},
                    {"event_type": "tool_status", "role": "assistant_status", "label": "Talked", "state": "completed", "service_name": "ion-actions.helixion.net", "text_full": "Talked to ion-actions.helixion.net"},
                    {"event_type": "thinking_status", "role": "assistant_status", "label": "Thought", "state": "completed", "duration_text": "3m 33s", "text_full": "Thought for 3m 33s"},
                ],
                "targets": [],
            },
        },
    )

    transcript = latest_browser_gpt_dom_summary(tmp_path)["chatgpt_dom_twin"]["transcript"]

    assert transcript["messages"][0]["text_full"] == full_response
    assert transcript["messages"][0]["text_preview"] == "Proceed complete."
    assert transcript["timeline_event_count"] == 3
    assert transcript["status_event_count"] == 2
    assert transcript["tool_event_count"] == 1
    assert transcript["timeline_events"][1]["service_name"] == "ion-actions.helixion.net"
    assert transcript["timeline_events"][2]["duration_text"] == "3m 33s"


def test_chatgpt_dom_twin_repairs_bad_profile_send_selector_from_safe_fallback(tmp_path: Path):
    write_json(
        tmp_path,
        "ION/05_context/current/browser_gpt_dom_profiles/latest.selector_profile.json",
        {
            "schema_id": "ion.browser_gpt_dom_selector_profile.v1",
            "profile_id": "chatgpt_web_bad_send",
            "origin": "https://chatgpt.com",
            "target_url": "https://chatgpt.com/",
            "surfaces": {
                "composer": {"selector": "#prompt-textarea", "confidence": 0.88, "candidate_count": 1, "validated_by": ["probe_snapshot"]},
                "send_button": {
                    "selector": "div > h1 > div > span:nth-of-type(1) > button",
                    "fallbacks": ["#composer-submit-button"],
                    "confidence": 0.86,
                    "candidate_count": 2,
                    "validated_by": ["probe_snapshot"],
                    "best_candidate": {"label": "Braden", "selector": "div > h1 > div > span:nth-of-type(1) > button"},
                    "observed_candidates": [
                        {"label": "Braden", "selector": "div > h1 > div > span:nth-of-type(1) > button"},
                        {"label": "", "selector": "#composer-submit-button"},
                    ],
                },
                "message_list": {"selector": "#main", "confidence": 0.82, "candidate_count": 1, "validated_by": ["probe_snapshot"]},
            },
            "authority": {"approved_send_required": True, "silent_send_authority": False},
        },
    )

    summary = latest_browser_gpt_dom_summary(tmp_path)
    twin = summary["chatgpt_dom_twin"]

    assert twin["status"] == "ready"
    assert twin["send"]["selector"] == "#composer-submit-button"
    assert twin["send"]["live_send_authority"] is False


def test_probe_phase_sweep_projection_merges_recent_phase_snapshots(tmp_path: Path):
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "phase_base.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T01:30:00Z",
                "url": "https://chatgpt.com/",
                "capture_reason": "phase_sweep_base",
                "phase_sweep": {"schema_id": "ion.browser_gpt_dom_probe_phase_sweep.v1", "phase": "base", "status": "base_capture"},
                "dom_health": {"composer_present": True},
                "visible_controls": [{"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"}],
                "visible_messages": [],
                "targets": [],
            },
        },
    )
    record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "phase_model.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T01:30:02Z",
                "url": "https://chatgpt.com/",
                "capture_reason": "phase_sweep_model_menu_open",
                "phase_sweep": {
                    "schema_id": "ion.browser_gpt_dom_probe_phase_sweep.v1",
                    "phase": "model_menu_open",
                    "status": "opened_for_capture",
                    "outcome": {"opener_found": True, "click_performed": True, "opener_selector": "button[aria-label='Model']"},
                },
                "dom_health": {"composer_present": True},
                "visible_controls": [
                    {"selector": "#prompt-textarea", "tag": "div", "role": "composer", "source_surface": "composer"},
                    {"selector": "button[aria-label='GPT-5']", "tag": "button", "role": "model_picker", "source_surface": "model_picker"},
                ],
                "visible_messages": [],
                "targets": [],
            },
        },
    )

    phase_sweep = probe_phase_sweep_projection(tmp_path)

    assert phase_sweep["status"] == "present"
    assert phase_sweep["phase_count"] == 2
    assert phase_sweep["opened_phase_count"] == 1
    assert "composer" in phase_sweep["merged_found_surface_ids"]
    assert "model_picker" in phase_sweep["merged_found_surface_ids"]


def test_degraded_chatops_probe_snapshot_preserves_existing_ready_profile(tmp_path: Path):
    write_json(
        tmp_path,
        "Needs_Routed/ion_native_dom_snapshot_20260525T2251286.json",
        {
            "captured_at": "2026-05-25T22:51:28.603Z",
            "url": "https://chatgpt.com/g/g-test/c/thread",
            "browser_gpt_dom": {
                "status": "ready",
                "required_surface_presence": {"composer": True, "send_button": True, "message_list": True},
                "detected": {
                    "composer": {"found": True, "selector": "#prompt-textarea", "tag": "div", "attrs": {"role": "textbox"}},
                    "send_button": {"found": True, "selector": "#composer-submit-button", "tag": "button"},
                    "message_list": {"found": True, "selector": "main", "tag": "main"},
                },
            },
        },
    )
    seed = write_seed_candidate_profile(tmp_path, "chatgpt_web_test")
    before = json.loads((tmp_path / seed["profile_path"]).read_text(encoding="utf-8"))

    result = record_browser_gpt_dom_probe_snapshot(
        tmp_path,
        {
            "filename": "bad_auto_probe.json",
            "snapshot": {
                "schema_id": "ion.browser_gpt_dom_probe_snapshot.v1",
                "captured_at": "2026-05-26T00:30:05Z",
                "url": "https://chatgpt.com/",
                "source": {"extension": "ION ChatOps Bridge", "compatibility_auto_probe": True},
                "dom_health": {"composer_present": False, "visible_button_count": 1},
                "visible_controls": [
                    {
                        "selector": "button[aria-label=\"Send next queued item\"]",
                        "tag": "button",
                        "role": "send_button",
                        "aria_label": "Send next queued item",
                    }
                ],
                "visible_messages": [],
                "targets": [],
            },
        },
    )
    after = json.loads((tmp_path / seed["profile_path"]).read_text(encoding="utf-8"))

    assert result["finding"] == "probe_snapshot_recorded_profile_preserved_degraded"
    assert "latest_degraded_probe_snapshot_path" in result
    assert "latest_probe_snapshot_path" not in result
    assert (tmp_path / result["latest_degraded_probe_snapshot_path"]).exists()
    assert not (tmp_path / BASE_DIR / "probe_snapshots/latest_probe_snapshot.json").exists()
    assert before["surfaces"]["send_button"]["selector"] == "#composer-submit-button"
    assert after["surfaces"]["send_button"]["selector"] == "#composer-submit-button"

    summary = latest_browser_gpt_dom_summary(tmp_path)
    probe_intake = summary["probe_intake"]
    assert probe_intake["status"] == "degraded_probe_observed"
    assert probe_intake["latest_usable_probe"]["status"] == "missing"
    assert probe_intake["latest_degraded_probe"]["status"] == "present"
    assert probe_intake["profile_preservation_guard"] == "degraded_auto_probe_cannot_overwrite_profile"


def test_seed_profile_imports_browser_gpt_surfaces_from_native_snapshot(tmp_path: Path):
    write_json(
        tmp_path,
        "Needs_Routed/ion_native_dom_snapshot_20260525T2033129.json",
        {
            "captured_at": "2026-05-25T20:33:12.994Z",
            "url": "https://chatgpt.com/g/g-test/c/thread",
            "detected": {"rail_host": {"selector": "#stage-slideover-sidebar"}},
            "browser_gpt_dom": {
                "status": "ready",
                "required_surface_presence": {"composer": True, "send_button": True, "message_list": True},
                "detected": {
                    "composer": {"found": True, "selector": "#prompt-textarea"},
                    "send_button": {"found": True, "selector": "[data-testid='send-button']"},
                    "message_list": {
                        "found": True,
                        "anchors": [{"selector": "[data-message-author-role='assistant']"}],
                    },
                },
            },
        },
    )

    result = write_seed_candidate_profile(tmp_path, "chatgpt_web_test")
    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))

    assert result["status"] == "ready"
    assert profile["calibration_source"] == "native_dom_snapshot_import"
    assert profile["surfaces"]["composer"]["confidence"] == 0.88
    assert profile["surfaces"]["send_button"]["selector"] == "[data-testid='send-button']"
    assert profile["prior_live_dom_evidence"]["browser_gpt_status"] == "ready"


def test_seed_profile_imports_operator_clicked_message_list(tmp_path: Path):
    write_json(
        tmp_path,
        "Needs_Routed/ion_native_dom_snapshot_20260525T2045000.json",
        {
            "captured_at": "2026-05-25T20:45:00.000Z",
            "url": "https://chatgpt.com/g/g-test/c/thread",
            "browser_gpt_dom": {
                "status": "degraded",
                "required_surface_presence": {"composer": True, "send_button": True, "message_list": False},
                "detected": {
                    "composer": {"found": True, "selector": "#prompt-textarea"},
                    "send_button": {"found": True, "selector": "#composer-submit-button"},
                    "message_list": {"found": False, "anchors": []},
                },
            },
            "browser_gpt_operator_picks": {
                "targets": {
                    "message_list": {
                        "found": True,
                        "selector": "[data-testid='conversation-turn-3']",
                    },
                    "file_attach_button": {
                        "found": True,
                        "selector": "button[aria-label='Upload']",
                        "hotkeys": ["Ctrl+U"],
                    },
                    "model_picker": {
                        "found": True,
                        "selector": "button[aria-label='GPT-5.5']",
                    },
                    "model_menu_option": {
                        "found": True,
                        "selector": "[role='option'][data-model='gpt-5.5']",
                    },
                    "thinking_mode_control": {
                        "found": True,
                        "selector": "button[aria-label='Thinking']",
                    },
                    "thinking_effort_option": {
                        "found": True,
                        "selector": "[role='menuitemradio'][data-effort='high']",
                    }
                }
            },
        },
    )

    result = write_seed_candidate_profile(tmp_path, "chatgpt_web_test")
    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))

    assert result["status"] == "ready"
    assert profile["surfaces"]["message_list"]["selector"] == "[data-testid='conversation-turn-3']"
    assert profile["surfaces"]["file_attach_button"]["selector"] == "button[aria-label='Upload']"
    assert profile["surfaces"]["file_attach_button"]["hotkeys"] == ["Ctrl+U"]
    assert profile["surfaces"]["model_picker"]["selector"] == "button[aria-label='GPT-5.5']"
    assert profile["surfaces"]["model_menu_option"]["selector"] == "[role='option'][data-model='gpt-5.5']"
    assert profile["surfaces"]["thinking_mode_control"]["selector"] == "button[aria-label='Thinking']"
    assert profile["surfaces"]["thinking_effort_option"]["selector"] == "[role='menuitemradio'][data-effort='high']"
    assert profile["prior_live_dom_evidence"]["browser_gpt_operator_hotkeys"]["file_attach_button"] == ["Ctrl+U"]
    assert profile["prior_live_dom_evidence"]["browser_gpt_operator_pick_count"] == 6


def test_native_snapshot_import_keeps_stable_core_selectors_over_operator_clicks(tmp_path: Path):
    write_json(
        tmp_path,
        "Needs_Routed/ion_native_dom_snapshot_20260525T2251286.json",
        {
            "captured_at": "2026-05-25T22:51:28.603Z",
            "url": "https://chatgpt.com/g/g-test/c/thread",
            "browser_gpt_dom": {
                "status": "ready",
                "required_surface_presence": {"composer": True, "send_button": True, "message_list": True},
                "detected": {
                    "composer": {"found": True, "selector": "#prompt-textarea", "tag": "div", "attrs": {"role": "textbox"}},
                    "send_button": {"found": True, "selector": "#composer-submit-button", "tag": "button"},
                    "message_list": {"found": True, "selector": "main", "tag": "main"},
                },
            },
            "browser_gpt_operator_picks": {
                "targets": {
                    "composer": {"found": True, "selector": "div:nth-of-type(2) > form > div:nth-of-type(2)"},
                    "send_button": {"found": True, "selector": "form button:nth-of-type(3)"},
                    "thinking_mode_control": {"found": True, "selector": "#radix-_r_4a_"},
                }
            },
        },
    )

    result = write_seed_candidate_profile(tmp_path, "chatgpt_web_test")
    profile = json.loads((tmp_path / result["profile_path"]).read_text(encoding="utf-8"))

    assert profile["surfaces"]["composer"]["selector"] == "#prompt-textarea"
    assert profile["surfaces"]["send_button"]["selector"] == "#composer-submit-button"
    assert profile["surfaces"]["thinking_mode_control"]["selector"] == "#radix-_r_4a_"


def test_browser_gpt_native_detected_selector_rejects_non_button_control_false_positive():
    assert browser_gpt_detected_selector_is_acceptable(
        "model_picker",
        {"found": True, "selector": "section[data-testid=\"conversation-turn-4\"]", "tag": "section"},
    ) is False
    assert browser_gpt_detected_selector_is_acceptable(
        "model_picker",
        {"found": True, "selector": "button[aria-label='GPT-5']", "tag": "button"},
    ) is True


def test_cockpit_view_model_projects_browser_gpt_dom_summary(tmp_path: Path):
    seed_minimal_cockpit_runtime(tmp_path)
    write_json(
        tmp_path,
        "Needs_Routed/ion_native_dom_snapshot_20260514T1857344.json",
        {
            "captured_at": "2026-05-14T18:57:34.449Z",
            "url": "https://chatgpt.com/g/g-test",
            "detected": {"rail_host": {"selector": "#stage-slideover-sidebar"}},
        },
    )
    write_seed_candidate_profile(tmp_path, "chatgpt_web_test")

    model = build_cockpit_view_model(tmp_path)
    browser_gpt_dom = model["extension_micro_shell"]["browser_gpt_dom"]

    assert browser_gpt_dom["schema_id"] == "ion.browser_gpt_dom_profile_summary.v1"
    assert browser_gpt_dom["latest_profile_id"] == "chatgpt_web_test"
    assert browser_gpt_dom["prior_live_dom_evidence"]["status"] == "present"
    assert browser_gpt_dom["probe_intake"]["normal_latest_advances_only_on_usable_probe"] is True
    surface_rows = {row["surface_id"]: row for row in browser_gpt_dom["surfaces"]}
    assert surface_rows["composer"]["hotkeys"] == ["Shift+Enter inserts newline", "/ opens slash commands"]
    assert surface_rows["slash_command_menu"]["hotkeys"] == ["/"]
    assert surface_rows["slash_command_option"]["phase_dependency"]["phase"] == "slash_command_menu_open"
    assert browser_gpt_dom["authority"]["approved_send_required"] is True
    assert model["top_bar"]["browser_gpt_dom_status"] == "degraded"


def test_missing_browser_gpt_dom_summary_is_fail_soft(tmp_path: Path):
    summary = latest_browser_gpt_dom_summary(tmp_path)

    assert summary["status"] == "missing_profile"
    assert summary["production_authority"] is False
    assert "run_browser_gpt_calibration" in summary["recommended_action"]
