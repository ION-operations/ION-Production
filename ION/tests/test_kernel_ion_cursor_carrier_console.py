import json
import re
from pathlib import Path

from kernel.ion_chatgpt_browser_mcp_http_preview import HELIXION_SITE_NAV_ITEMS
from kernel.ion_cursor_carrier_chat import render_cursor_carrier_console_html


def _write_minimal_ion_tree(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


def _write_turn_packet(root: Path) -> None:
    turn = {
        "schema_id": "ion.carrier_turn_packet.v1",
        "spawn_queue": [
            {
                "index": 1,
                "role": "steward",
                "context_package_path": "ION/05_context/current/pkg.md",
                "context_load_receipt_path": "ION/05_context/current/receipt.json",
            }
        ],
    }
    path = root / "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(turn, indent=2) + "\n", encoding="utf-8")


def test_render_cursor_carrier_console_html_embeds_model_and_endpoints(tmp_path: Path) -> None:
    _write_minimal_ion_tree(tmp_path)
    _write_turn_packet(tmp_path)

    html = render_cursor_carrier_console_html(tmp_path)

    assert isinstance(html, str)
    assert "<html" in html.lower()
    assert "Cursor CLI" in html
    assert "/cockpit/cursor/model.json" in html
    assert "/cockpit/cursor/turn" in html
    assert "steward" in html

    match = re.search(
        r'<script id="initial-model" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert match is not None
    embedded = json.loads(match.group(1))
    assert isinstance(embedded.get("spawn_queue"), list)
    assert embedded["spawn_queue"][0]["role"] == "steward"


def test_helixion_nav_contains_cursor_item() -> None:
    assert any(item.get("href") == "/cockpit/cursor" for item in HELIXION_SITE_NAV_ITEMS)
