import json
from pathlib import Path

from kernel.ion_needs_routed_intake import (
    BLOCKED_VERDICT,
    WRITE_CONFIRMATION,
    build_needs_routed_intake,
    write_needs_routed_intake,
)


def _needs_root(tmp_path: Path) -> Path:
    root = tmp_path / "Needs_Routed"
    (root / "drop").mkdir(parents=True)
    return root


def test_needs_routed_scan_classifies_drop_items_without_mutation(tmp_path):
    root = _needs_root(tmp_path)
    patch = root / "drop" / "ION_CODEX_QUEUE_START_NO_RECEIPT_CANDIDATE.patch"
    custom_zip = root / "drop" / "ION_CUSTOM_GPT_V4_7_DOGFOOD_CONTEXT_PACKAGE.zip"
    workpacket = root / "drop" / "PCKT-ION-TEST-WORKPACKET.md"
    secret = root / "drop" / "service_role_token.env"
    patch.write_text("diff --git a/a b/a\n", encoding="utf-8")
    custom_zip.write_bytes(b"not a real zip, classification uses name only")
    workpacket.write_text("# Workpacket\n\nPCKT-ION-TEST", encoding="utf-8")
    secret.write_text("not-read-as-secret-content", encoding="utf-8")

    result = build_needs_routed_intake(needs_root=root)

    routes = {item["original_path"]: item["route_class"] for item in result["items"]}
    assert result["ok"] is True
    assert result["write_performed"] is False
    assert routes["Needs_Routed/drop/ION_CODEX_QUEUE_START_NO_RECEIPT_CANDIDATE.patch"] == "apply_candidate_patch"
    assert routes["Needs_Routed/drop/ION_CUSTOM_GPT_V4_7_DOGFOOD_CONTEXT_PACKAGE.zip"] == "custom_gpt_package_review"
    assert routes["Needs_Routed/drop/PCKT-ION-TEST-WORKPACKET.md"] == "queue_codex_workpacket"
    assert routes["Needs_Routed/drop/service_role_token.env"] == "secret_or_private_blocked"
    assert patch.exists()
    assert secret.exists()


def test_needs_routed_write_requires_confirmation(tmp_path):
    root = _needs_root(tmp_path)
    (root / "drop" / "candidate.patch").write_text("diff --git a/a b/a\n", encoding="utf-8")

    result = write_needs_routed_intake(needs_root=root, confirmation="wrong")

    assert result["ok"] is False
    assert result["verdict"] == BLOCKED_VERDICT
    assert "write_confirmation_required" in result["blocked_findings"]
    assert (root / "drop" / "candidate.patch").exists()
    assert not (root / "receipts").exists()


def test_needs_routed_write_archives_drop_items_and_writes_receipt(tmp_path):
    root = _needs_root(tmp_path)
    patch = root / "drop" / "candidate.patch"
    secret = root / "drop" / "private_key.pem"
    patch.write_text("diff --git a/a b/a\n", encoding="utf-8")
    secret.write_text("fake test key", encoding="utf-8")

    result = write_needs_routed_intake(needs_root=root, confirmation=WRITE_CONFIRMATION)

    assert result["ok"] is True
    assert result["write_performed"] is True
    assert result["file_moves_performed"] is True
    assert result["queue_mutation_performed"] is False
    assert not patch.exists()
    assert not secret.exists()
    moved = {item["original_path"]: item for item in result["items"]}
    assert moved["Needs_Routed/drop/candidate.patch"]["status"] == "ingested_moved_to_history"
    assert moved["Needs_Routed/drop/private_key.pem"]["status"] == "blocked_moved_for_review"
    receipt = root.parent / result["receipt_path"]
    index = root.parent / result["index_path"]
    assert receipt.exists()
    assert index.exists()
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["accepted_state_claim"] is False
    assert payload["production_authority"] is False


def test_needs_routed_write_does_not_move_top_level_backlog_by_default(tmp_path):
    root = tmp_path / "Needs_Routed"
    root.mkdir()
    backlog = root / "ION_CUSTOM_GPT_BACKLOG.patch"
    backlog.write_text("diff --git a/a b/a\nCUSTOM_GPT\n", encoding="utf-8")

    result = write_needs_routed_intake(
        needs_root=root,
        scan_scope="root",
        confirmation=WRITE_CONFIRMATION,
    )

    assert result["ok"] is True
    assert backlog.exists()
    assert result["file_moves_performed"] is False
    assert result["items"][0]["status"] == "review_only_not_moved"
    assert "legacy_or_source_lane_backlog_not_moved_by_default" in result["items"][0]["reasons"]
