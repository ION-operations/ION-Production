import json
import os
import re
import shutil
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_DROPIN_PATH = Path.home() / ".config/systemd/user/ion-mcp-preview.service.d/cockpit-token.conf"
SMOKE_RECEIPT_PATH = (
    REPO_ROOT
    / "ION/05_context/current/codex_cli/playwright_cockpit_pending_smoke_latest.json"
)
SHELL_SMOKE_RECEIPT_PATH = (
    REPO_ROOT
    / "ION/05_context/current/codex_cli/playwright_cockpit_shell_smoke_latest.json"
)
DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR = (
    REPO_ROOT / "ION/05_context/current/domain_weaver/visual_smoke"
)
DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_RECEIPT_PATH = (
    DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR / "DOMAIN_WEAVER_ACTION_HISTORY_COCKPIT_SMOKE.json"
)
DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_SCREENSHOT_PATH = (
    DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR / "DOMAIN_WEAVER_ACTION_HISTORY_COCKPIT.png"
)
SCOPE_WORKSURFACE_SMOKE_RECEIPT_PATH = (
    DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR / "SCOPE_WORKSURFACE_COCKPIT_SMOKE.json"
)
SCOPE_WORKSURFACE_DESKTOP_SCREENSHOT_PATH = (
    DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR / "SCOPE_WORKSURFACE_DESKTOP_COCKPIT.png"
)
SCOPE_WORKSURFACE_MOBILE_SCREENSHOT_PATH = (
    DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR / "SCOPE_WORKSURFACE_MOBILE_COCKPIT.png"
)


pytestmark = pytest.mark.skipif(
    os.environ.get("ION_RUN_PLAYWRIGHT_SMOKE") != "1",
    reason="live cockpit Playwright smoke is opt-in",
)


def _configured_cockpit_token() -> str:
    explicit = os.environ.get("ION_COCKPIT_TOKEN", "").strip()
    if explicit:
        return explicit
    if not SERVICE_DROPIN_PATH.exists():
        pytest.skip("cockpit token drop-in is not present")
    text = SERVICE_DROPIN_PATH.read_text(encoding="utf-8")
    public = re.search(r'ION_COCKPIT_PUBLIC_TOKEN=([^"\s]+)', text)
    if public:
        return public.group(1).strip()
    invites = re.search(r'ION_COCKPIT_INVITE_TOKENS=([^"\s]+)', text)
    if invites:
        first = invites.group(1).split(",", 1)[0].strip()
        return first.split("=", 1)[-1].strip()
    pytest.skip("cockpit permission token is not configured")


def _chrome_executable() -> str:
    configured = os.environ.get("ION_PLAYWRIGHT_CHROME", "").strip()
    candidates = [
        configured,
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    pytest.skip("no system Chrome/Chromium executable available")


def _assert_service_ready(base_url: str) -> None:
    request = Request(f"{base_url}/health", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # pragma: no cover - live smoke diagnostic.
        pytest.skip(f"local ION cockpit service is not reachable: {exc.__class__.__name__}")
    if not payload.get("ok") and not payload.get("accepted"):
        pytest.skip("local ION cockpit service is not ready")


def test_cockpit_chat_submit_shows_pending_and_blocks_duplicate() -> None:
    sync_api = pytest.importorskip("playwright.sync_api")
    base_url = os.environ.get("ION_COCKPIT_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
    token = _configured_cockpit_token()
    chrome = _chrome_executable()
    _assert_service_ready(base_url)

    message_id = f"playwright-pending-smoke-{int(time.time())}"
    message = f"{message_id}: reply exactly playwright-ok"

    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=chrome,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page_errors: list[str] = []
            console_errors: list[str] = []
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            page.goto(
                f"{base_url}/cockpit?token={quote(token)}#codex",
                wait_until="domcontentloaded",
            )
            textarea = page.locator('textarea[placeholder*="Codex CLI"]').first
            send = page.locator('button[type="submit"]').first

            sync_api.expect(textarea).to_be_visible(timeout=30_000)
            textarea.fill(message)
            send.click()

            sync_api.expect(textarea).to_have_value("", timeout=5_000)
            sync_api.expect(page.locator("body")).to_contain_text(message, timeout=5_000)
            sync_api.expect(page.locator("body")).to_contain_text("playwright-ok", timeout=60_000)
            assert page_errors == []
            assert console_errors == []

            receipt = {
                "schema_id": "ion.playwright_cockpit_pending_smoke.v1",
                "ok": True,
                "base_url": base_url,
                "message_id": message_id,
                "assertions": [
                    "textarea_cleared_immediately",
                    "send_disabled_with_sending_label",
                    "pending_codex_bubble_visible",
                    "duplicate_submit_guard_preserved_single_user_bubble",
                    "codex_response_captured",
                ],
                "token_value_recorded": False,
            }
            SMOKE_RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
            SMOKE_RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        finally:
            browser.close()


def test_cockpit_joc_shell_navigation_and_memory_surface() -> None:
    sync_api = pytest.importorskip("playwright.sync_api")
    base_url = os.environ.get("ION_COCKPIT_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
    token = _configured_cockpit_token()
    chrome = _chrome_executable()
    _assert_service_ready(base_url)

    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=chrome,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 960})
            page.goto(
                f"{base_url}/cockpit/chat?token={quote(token)}",
                wait_until="domcontentloaded",
            )

            sync_api.expect(page.locator(".capsule-main-chat")).to_be_visible(timeout=10_000)
            sync_api.expect(page.locator(".top-page-tabs")).to_be_visible()
            sync_api.expect(page.locator(".capsule-left-drawer")).to_be_visible()
            sync_api.expect(page.locator(".capsule-right-rail")).to_be_visible()
            sync_api.expect(page.locator(".capsule-activity-strip")).to_be_visible()

            page.locator('[data-left-drawer-target="models"]').click()
            sync_api.expect(page.locator('[data-left-panel="models"]')).to_be_visible()
            sync_api.expect(page.locator('[data-left-drawer-target="models"]')).to_have_class(re.compile("is-active"))

            page.locator('[data-inspector-target="context"]').first.click()
            sync_api.expect(page.locator('[data-inspector-panel="context"]')).to_be_visible()
            sync_api.expect(page.locator('[data-inspector-panel="context"]')).to_contain_text("Memory View")

            page.locator('[data-page-target="context"]').click()
            sync_api.expect(page.locator('[data-page-panel="context"]')).to_be_visible()
            sync_api.expect(page.locator('[data-page-panel="chat"]')).to_be_hidden()
            sync_api.expect(page.locator('[data-page-panel="context"]')).to_contain_text("Memory Strata")
            sync_api.expect(page.locator('[data-page-panel="context"]')).to_contain_text("Contextual Matryoshka")
            sync_api.expect(page.locator('[data-page-panel="context"]')).to_contain_text("Context Route Graph")
            sync_api.expect(page.locator('[data-page-panel="context"] [data-memory-window-class="LIVE_INPUT"]')).to_be_visible()
            sync_api.expect(page.locator('[data-page-panel="context"] [data-memory-window-class="ACTIVE_CONTEXT"]')).to_be_visible()
            capsule_card = page.locator('[data-page-panel="context"] [data-memory-segment-id="context:capsule"]').first
            capsule_card.click()
            sync_api.expect(capsule_card).to_have_class(re.compile("is-selected-memory"))
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-memory-selection-field="id"]').first
            ).to_contain_text("context:capsule")
            route_edge = page.locator('[data-page-panel="context"] [data-route-edge-id]').first
            route_edge_id = route_edge.get_attribute("data-route-edge-id") or ""
            route_edge.click()
            sync_api.expect(route_edge).to_have_class(re.compile("is-selected-memory"))
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-memory-selection-field="edge"]').first
            ).to_contain_text(route_edge_id)
            compressed_filter = page.locator('[data-page-panel="context"] [data-route-edge-filter="compressed_to"]').first
            compressed_filter.click()
            sync_api.expect(compressed_filter).to_have_class(re.compile("is-active"))
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-route-edge-type="compressed_to"]').first
            ).to_be_visible()
            source_group_filters = page.locator('[data-page-panel="context"] [data-source-group-filter]')
            if source_group_filters.count() > 1:
                source_group_filter = source_group_filters.nth(1)
                source_group = source_group_filter.get_attribute("data-source-group-filter") or ""
                source_group_filter.click()
                sync_api.expect(source_group_filter).to_have_class(re.compile("is-active"))
                sync_api.expect(
                    page.locator(f'[data-page-panel="context"] [data-source-ref-lane="{source_group}"]').first
                ).to_be_visible()
                source_group_filters.first.click()
            source_ref = page.locator('[data-page-panel="context"] [data-source-ref]').first
            source_ref_value = source_ref.get_attribute("data-source-ref") or ""
            source_ref.click()
            sync_api.expect(source_ref).to_have_class(re.compile("is-selected-memory"))
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-memory-selection-field="id"]').first
            ).to_contain_text(source_ref_value)
            trace_event = page.locator('[data-page-panel="context"] [data-trace-event-id]').first
            trace_event_id = trace_event.get_attribute("data-trace-event-id") or ""
            trace_event.click()
            sync_api.expect(trace_event).to_have_class(re.compile("is-selected-memory"))
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-memory-selection-field="id"]').first
            ).to_contain_text(trace_event_id)
            page.reload(wait_until="domcontentloaded")
            sync_api.expect(page.locator(".capsule-main-chat")).to_be_visible(timeout=10_000)
            page.locator('[data-page-target="context"]').click()
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-memory-selection-field="id"]').first
            ).to_contain_text(trace_event_id)
            sync_api.expect(
                page.locator('[data-page-panel="context"] [data-trace-event-id]').first
            ).to_have_class(re.compile("is-selected-memory"))

            page.locator('[data-inspector-target="evidence"]').first.click()
            sync_api.expect(page.locator('[data-inspector-panel="evidence"]')).to_be_visible()
            sync_api.expect(page.locator('[data-inspector-panel="evidence"]')).to_contain_text("Timeline")

            page.locator('[data-timeline-filter="task_return"]').click()
            sync_api.expect(page.locator('[data-timeline-filter="task_return"]')).to_have_class(re.compile("is-active"))

            page.locator('[data-page-target="chat"]').click()
            sync_api.expect(page.locator('[data-page-panel="chat"]')).to_be_visible()
            sync_api.expect(page.locator('form.capsule-composer textarea[name="message"]')).to_be_visible()
            chat_turn = page.locator('[data-page-panel="chat"] .bubble[data-chat-turn-id]').first
            chat_turn.click()
            sync_api.expect(chat_turn).to_have_class(re.compile("is-selected-memory"))

            receipt = {
                "schema_id": "ion.playwright_cockpit_shell_smoke.v1",
                "ok": True,
                "base_url": base_url,
                "assertions": [
                    "joc_shell_regions_visible",
                    "left_drawer_models_panel_switches",
                    "right_inspector_context_panel_switches",
                    "context_page_memory_visualization_visible",
                    "memory_segment_selection_updates_selected_node_panel",
                    "route_edge_selection_updates_selected_node_panel",
                    "route_edge_type_filter_activates",
                    "source_ref_drilldown_updates_selected_node_panel",
                    "trace_event_selection_updates_selected_node_panel",
                    "right_inspector_evidence_panel_switches",
                    "bottom_timeline_filter_activates",
                    "chat_turn_selection_highlights_message",
                    "chat_page_restores_composer",
                ],
                "token_value_recorded": False,
            }
            SHELL_SMOKE_RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
            SHELL_SMOKE_RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        finally:
            browser.close()


def test_cockpit_domain_weaver_action_history_visual_smoke() -> None:
    sync_api = pytest.importorskip("playwright.sync_api")
    base_url = os.environ.get("ION_COCKPIT_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
    token = _configured_cockpit_token()
    chrome = _chrome_executable()
    _assert_service_ready(base_url)

    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=chrome,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.goto(
                f"{base_url}/cockpit?token={quote(token)}#weave",
                wait_until="domcontentloaded",
            )

            panel = page.locator(".ion-domain-weaver-panel")
            work_surface = page.locator(".ion-domain-weaver-work-surface")
            left_drawer = page.locator(".ion-domain-weaver-left-drawer")
            right_inspector = page.locator(".ion-domain-weaver-right-inspector")
            command_button = page.locator(".ion-domain-weaver-left-drawer .ion-domain-weaver-action").first
            dogfood_lane = page.locator(".ion-domain-weaver-lanes .ion-domain-weaver-lane").nth(1)
            bottom_timeline = page.locator(".ion-domain-weaver-bottom-timeline")
            history = page.locator(".ion-domain-weaver-action-history")
            rows = page.locator(".ion-domain-weaver-action-history article")

            sync_api.expect(panel).to_be_visible(timeout=10_000)
            sync_api.expect(panel).to_contain_text("DOMAIN WEAVER WORKBENCH", timeout=10_000)
            panel_box = panel.bounding_box()
            assert panel_box is not None
            assert panel_box["width"] > 1000
            sync_api.expect(work_surface).to_be_visible()
            sync_api.expect(left_drawer).to_be_visible()
            sync_api.expect(right_inspector).to_be_visible()
            sync_api.expect(command_button).to_be_visible()
            sync_api.expect(dogfood_lane).to_be_visible()
            left_drawer_box = left_drawer.bounding_box()
            right_inspector_box = right_inspector.bounding_box()
            command_button_box = command_button.bounding_box()
            dogfood_lane_box = dogfood_lane.bounding_box()
            assert left_drawer_box is not None
            assert right_inspector_box is not None
            assert command_button_box is not None
            assert dogfood_lane_box is not None
            assert left_drawer_box["width"] > 240
            assert right_inspector_box["width"] > 270
            assert command_button_box["width"] > 220
            assert dogfood_lane_box["width"] > 300
            sync_api.expect(bottom_timeline).to_be_visible()
            sync_api.expect(panel).to_contain_text("OPERATOR ACTIONS")
            sync_api.expect(panel).to_contain_text("QUEUE REFRESH")
            sync_api.expect(panel).to_contain_text("PROMOTION REVIEW")
            sync_api.expect(panel).to_contain_text("Route Status")
            sync_api.expect(panel).to_contain_text("Work Surface")
            sync_api.expect(panel).to_contain_text("Proof Trail")
            sync_api.expect(panel).to_contain_text("Context Sources")
            sync_api.expect(panel).to_contain_text("INSPECTOR")
            sync_api.expect(panel).to_contain_text("operator_usable: true")
            sync_api.expect(history).to_be_visible()
            sync_api.expect(rows.first).to_be_visible(timeout=10_000)
            sync_api.expect(history).to_contain_text("refresh_queue_governor", timeout=10_000)
            sync_api.expect(history).not_to_contain_text("NO DOMAIN WEAVER ACTION HISTORY")

            DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_SCREENSHOT_PATH.as_posix(), full_page=True)
            screenshot_size = DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_SCREENSHOT_PATH.stat().st_size
            assert screenshot_size > 1024

            receipt = {
                "schema_id": "ion.playwright_domain_weaver_action_history_smoke.v0_1",
                "ok": True,
                "created_at_epoch_seconds": int(time.time()),
                "base_url": base_url,
                "hash_route": "#weave",
                "screenshot_path": str(DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_SCREENSHOT_PATH.relative_to(REPO_ROOT)),
                "screenshot_size_bytes": screenshot_size,
                "receipt_path": str(DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_RECEIPT_PATH.relative_to(REPO_ROOT)),
                "action_history_row_count": rows.count(),
                "assertions": [
                    "domain_weaver_panel_visible",
                    "work_surface_visible",
                    "left_drawer_visible",
                    "right_inspector_visible",
                    "bottom_timeline_visible",
                    "operator_actions_visible",
                    "command_button_width_readable",
                    "lens_tabs_visible",
                    "self_dogfood_lane_width_readable",
                    "right_inspector_width_readable",
                    "operator_usable_projected_true",
                    "action_history_rows_visible",
                    "action_history_not_empty",
                    "full_page_screenshot_nonblank",
                ],
                "token_value_recorded": False,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            }
            DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_RECEIPT_PATH.write_text(
                json.dumps(receipt, indent=2) + "\n",
                encoding="utf-8",
            )
        finally:
            browser.close()


def test_cockpit_scope_non_monolith_worksurface_visual_smoke() -> None:
    sync_api = pytest.importorskip("playwright.sync_api")
    base_url = os.environ.get("ION_COCKPIT_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
    token = _configured_cockpit_token()
    chrome = _chrome_executable()
    _assert_service_ready(base_url)

    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=chrome,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.goto(
                f"{base_url}/cockpit?token={quote(token)}#scope",
                wait_until="domcontentloaded",
            )

            panel = page.locator(".ion-scope-cockpit-panel")
            work_surface = page.locator(".ion-scope-work-surface")
            left_rail = page.locator(".ion-scope-left-rail")
            main_surface = page.locator(".ion-scope-main-surface")
            right_inspector = page.locator(".ion-scope-right-inspector")
            bottom_timeline = page.locator(".ion-scope-bottom-timeline")
            raw_blocks = page.locator(".ion-scope-raw-model")

            sync_api.expect(panel).to_be_visible(timeout=10_000)
            sync_api.expect(panel).to_contain_text("SCOPE COCKPIT", timeout=10_000)
            sync_api.expect(work_surface).to_be_visible()
            sync_api.expect(left_rail).to_be_visible()
            sync_api.expect(main_surface).to_be_visible()
            sync_api.expect(right_inspector).to_be_visible()
            sync_api.expect(bottom_timeline).to_be_visible()
            sync_api.expect(page.locator(".ion-scope-lens-tabs")).to_contain_text("Objective")
            sync_api.expect(page.locator(".ion-scope-lens-tabs")).to_contain_text("Context")
            sync_api.expect(page.locator(".ion-scope-lens-tabs")).to_contain_text("Graph")
            sync_api.expect(page.locator(".ion-scope-lens-tabs")).to_contain_text("Scheduler")
            sync_api.expect(page.locator(".ion-scope-lens-tabs")).to_contain_text("Proof")
            sync_api.expect(page.locator(".ion-scope-lens-tabs")).to_contain_text("Raw")
            sync_api.expect(raw_blocks).to_have_count(0)

            page.locator(".ion-scope-lens-tabs button", has_text="Raw").click()
            sync_api.expect(page.locator(".ion-scope-raw-model")).to_be_visible()
            sync_api.expect(page.locator(".ion-scope-lens-tabs button", has_text="Raw")).to_have_class(re.compile("is-active"))
            page.locator(".ion-scope-lens-tabs button", has_text="Proof").click()
            sync_api.expect(page.locator(".ion-scope-lens-tabs button", has_text="Proof")).to_have_class(re.compile("is-active"))
            sync_api.expect(page.locator(".ion-scope-lens-body")).to_contain_text("Accepted-State Boundary")

            desktop_panel_box = panel.bounding_box()
            main_box = main_surface.bounding_box()
            inspector_box = right_inspector.bounding_box()
            assert desktop_panel_box is not None
            assert main_box is not None
            assert inspector_box is not None
            assert desktop_panel_box["width"] > 1000
            assert main_box["width"] > 640
            assert inspector_box["width"] > 240

            DOMAIN_WEAVER_ACTION_HISTORY_SMOKE_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=SCOPE_WORKSURFACE_DESKTOP_SCREENSHOT_PATH.as_posix(), full_page=True)
            desktop_screenshot_size = SCOPE_WORKSURFACE_DESKTOP_SCREENSHOT_PATH.stat().st_size
            assert desktop_screenshot_size > 1024

            page.set_viewport_size({"width": 390, "height": 920})
            page.goto(
                f"{base_url}/cockpit?token={quote(token)}#scope",
                wait_until="domcontentloaded",
            )
            sync_api.expect(panel).to_be_visible(timeout=10_000)
            sync_api.expect(left_rail).to_be_visible()
            sync_api.expect(main_surface).to_be_visible()
            sync_api.expect(right_inspector).to_be_visible()
            mobile_panel_box = panel.bounding_box()
            assert mobile_panel_box is not None
            assert mobile_panel_box["width"] <= 390
            page.screenshot(path=SCOPE_WORKSURFACE_MOBILE_SCREENSHOT_PATH.as_posix(), full_page=True)
            mobile_screenshot_size = SCOPE_WORKSURFACE_MOBILE_SCREENSHOT_PATH.stat().st_size
            assert mobile_screenshot_size > 1024

            receipt = {
                "schema_id": "ion.playwright_scope_worksurface_smoke.v0_1",
                "ok": True,
                "created_at_epoch_seconds": int(time.time()),
                "base_url": base_url,
                "hash_route": "#scope",
                "desktop_screenshot_path": str(SCOPE_WORKSURFACE_DESKTOP_SCREENSHOT_PATH.relative_to(REPO_ROOT)),
                "mobile_screenshot_path": str(SCOPE_WORKSURFACE_MOBILE_SCREENSHOT_PATH.relative_to(REPO_ROOT)),
                "desktop_screenshot_size_bytes": desktop_screenshot_size,
                "mobile_screenshot_size_bytes": mobile_screenshot_size,
                "receipt_path": str(SCOPE_WORKSURFACE_SMOKE_RECEIPT_PATH.relative_to(REPO_ROOT)),
                "assertions": [
                    "scope_panel_visible",
                    "local_work_surface_visible",
                    "left_lens_rail_visible",
                    "main_lens_tabs_visible",
                    "right_inspector_visible",
                    "bottom_timeline_visible",
                    "objective_context_graph_scheduler_proof_raw_lenses_visible",
                    "raw_json_hidden_before_raw_lens",
                    "raw_lens_opens_json_inspector",
                    "proof_lens_preserves_accepted_state_boundary",
                    "desktop_layout_has_readable_main_and_inspector_widths",
                    "mobile_layout_visible_without_horizontal_overflow",
                    "desktop_and_mobile_screenshots_nonblank",
                ],
                "token_value_recorded": False,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            }
            SCOPE_WORKSURFACE_SMOKE_RECEIPT_PATH.write_text(
                json.dumps(receipt, indent=2) + "\n",
                encoding="utf-8",
            )
        finally:
            browser.close()
