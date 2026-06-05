from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from kernel import ion_domain_weaver_monolith_index as monolith_index


SYNTHETIC_MONOLITH = '''"""Synthetic Domain Weaver-shaped source for index tests."""
from pathlib import Path

SCHEMA_ID = "ion.domain_weaver.synthetic.v0_1"
DOMAIN_WEAVER_ROOT = Path("ION/05_context/current/domain_weaver")
DOMAIN_WEAVER_TEST_PATH = DOMAIN_WEAVER_ROOT / "TEST.candidate.json"
DOMAIN_WEAVER_TEST_PACKET_ID = "PCKT-DOMAIN-WEAVER-INDEX-TEST-20260604-ATTEMPT-001"
DOMAIN_WEAVER_ALLOWED_OPERATOR_ACTIONS = (
    "context_active_resolver_status",
    "queue_test_packet",
    "materialize_test_preview",
)
DOMAIN_WEAVER_READ_ONLY_CONTEXT_ACTIONS = ("context_active_resolver_status",)


def _read_json_file(path):
    return {}


def _domain_weaver_queue_live_carrier_work_requests(root):
    return {"queue_ledger_path": DOMAIN_WEAVER_TEST_PATH.as_posix()}


def materialize_domain_weaver_projection(root):
    (root / DOMAIN_WEAVER_TEST_PATH).write_text("{}\\n", encoding="utf-8")
    return {"schema_id": SCHEMA_ID}


def execute_domain_weaver_action(root, payload):
    action = str((payload or {}).get("action") or "")
    if action == "context_active_resolver_status":
        return {"ok": True, "results": {"read_only": True}}
    if action == "queue_test_packet":
        return _domain_weaver_queue_live_carrier_work_requests(root)
    if action == "materialize_test_preview":
        return materialize_domain_weaver_projection(root)
    return {"ok": False, "finding": "unknown_action"}
'''


def _write_synthetic_source(root: Path) -> Path:
    source = root / "ION" / "04_packages" / "kernel" / "ion_domain_weaver.py"
    source.parent.mkdir(parents=True)
    source.write_text(SYNTHETIC_MONOLITH, encoding="utf-8")
    return source


def test_monolith_index_module_does_not_import_real_monolith() -> None:
    sys.modules.pop("kernel.ion_domain_weaver_monolith_index", None)
    sys.modules.pop("kernel.ion_domain_weaver", None)

    module = importlib.import_module("kernel.ion_domain_weaver_monolith_index")

    assert module.SCHEMA_ID == monolith_index.SCHEMA_ID
    assert "kernel.ion_domain_weaver" not in sys.modules


def test_build_index_extracts_symbols_constants_actions_and_risk(tmp_path: Path) -> None:
    source = _write_synthetic_source(tmp_path)

    index = monolith_index.build_domain_weaver_monolith_index_from_source(
        source,
        root=tmp_path,
        generated_at="2026-06-04T04:00:00+00:00",
    )

    assert index["schema_id"] == monolith_index.SCHEMA_ID
    assert index["source"]["path"] == "ION/04_packages/kernel/ion_domain_weaver.py"
    assert index["summary"]["top_level_function_count"] == 4
    assert index["summary"]["allowed_action_count"] == 3
    assert index["summary"]["dispatcher_branch_action_count"] == 3

    constants = {row["name"]: row for row in index["constants"]}
    assert constants["SCHEMA_ID"]["category"] == "schema_constant"
    assert constants["DOMAIN_WEAVER_TEST_PATH"]["category"] == "path_constant"
    assert constants["DOMAIN_WEAVER_TEST_PACKET_ID"]["category"] == "packet_constant"

    symbols = index["symbols_by_name"]
    assert symbols["execute_domain_weaver_action"]["category"] == "action_dispatcher"
    assert symbols["materialize_domain_weaver_projection"]["category"] == "materializers"

    functions = {row["name"]: row for row in index["functions"]}
    materializer = functions["materialize_domain_weaver_projection"]
    assert "writes_file" in materializer["risk_tags"]
    assert "materialization" in materializer["risk_tags"]
    assert "DOMAIN_WEAVER_TEST_PATH" in materializer["path_constant_refs"]

    actions = {row["action"]: row for row in index["action_index"]["actions"]}
    assert actions["context_active_resolver_status"]["read_only_context_action"] is True
    assert actions["queue_test_packet"]["branch_count"] == 1
    assert "_domain_weaver_queue_live_carrier_work_requests" in actions["queue_test_packet"]["internal_calls"]
    assert actions["materialize_test_preview"]["branch_count"] == 1
    assert index["action_index"]["unbranched_allowed_actions"] == []


def test_write_index_creates_json_and_markdown_artifacts(tmp_path: Path) -> None:
    source = _write_synthetic_source(tmp_path)
    output_dir = tmp_path / "ION" / "05_context" / "current" / "domain_weaver" / "monolith_index"

    result = monolith_index.write_domain_weaver_monolith_index(
        tmp_path,
        source_path=source,
        output_dir=output_dir,
        generated_at="2026-06-04T04:00:00+00:00",
    )

    json_path = tmp_path / result["json_path"]
    markdown_path = tmp_path / result["markdown_path"]
    assert json_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert payload["summary"]["dispatcher_branch_action_count"] == 3
    assert "Domain Weaver Monolith Index" in markdown
    assert "queue_test_packet" in markdown
    assert "PYTHONPATH=ION/04_packages python3 -m kernel.ion_domain_weaver_monolith_index" in markdown


def test_real_domain_weaver_allowed_actions_have_dispatcher_branches() -> None:
    source = Path("ION/04_packages/kernel/ion_domain_weaver.py")

    index = monolith_index.build_domain_weaver_monolith_index_from_source(
        source,
        root=Path("."),
        generated_at="2026-06-04T21:20:00+00:00",
    )

    assert index["action_index"]["unbranched_allowed_actions"] == []
    assert index["action_index"]["branched_actions_not_in_allowed_catalog"] == []
    actions = {row["action"]: row for row in index["action_index"]["actions"]}
    live_fanout = actions["queue_approval_governed_live_fanout"]
    assert live_fanout["branch_count"] == 1
    assert "_domain_weaver_queue_live_carrier_work_requests" in live_fanout["internal_calls"]
