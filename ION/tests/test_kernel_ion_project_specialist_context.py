import json
from pathlib import Path

from kernel.ion_project_specialist_context import (
    SPECIALIST_INDEX,
    build_project_specialist_contexts,
)


def write_json(root: Path, rel: str, payload: dict) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def seed_project_dossier_index(root: Path) -> Path:
    organized = root / "organized/domains/01_water_simulation/hyper-h2o"
    organized.mkdir(parents=True, exist_ok=True)
    project_dossier_rel = "ION/05_context/current/project_portfolio/dossiers/domains/water-simulation/projects/cosmos-hyper-h2o.json"
    project_dossier_md_rel = "ION/05_context/current/project_portfolio/dossiers/domains/water-simulation/projects/cosmos-hyper-h2o.md"
    write_json(
        root,
        project_dossier_rel,
        {
            "schema_id": "ion.project_canon_dossier.v1",
            "identity": {
                "family_id": "cosmos:hyper-h2o",
                "label": "Hyper H2O",
                "current_path": (root / "source/hyper-h2o-v2").as_posix(),
            },
            "counts": {
                "project_count": 2,
                "version_count": 2,
                "branch_count": 1,
                "diff_count": 1,
                "doc_count": 2,
                "reference_count": 1,
                "launchable_count": 1,
            },
            "source_organization": {
                "current_source": (root / "source/hyper-h2o-v2").as_posix(),
                "current_source_copy": (organized / "source/current").as_posix(),
                "organized_path": organized.as_posix(),
                "duplicate_policy": "historical full folders are lineage witnesses, not edit targets",
            },
        },
    )
    (root / project_dossier_md_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / project_dossier_md_rel).write_text("# Hyper H2O Canon Dossier\n", encoding="utf-8")
    write_json(
        root,
        "ION/05_context/current/project_portfolio/dossiers/PROJECT_CANON_DOSSIER_INDEX.json",
        {
            "ok": True,
            "schema_id": "ion.project_canon_dossier_index.v1",
            "generated_at": "2026-06-03T12:00:00+00:00",
            "status": "project_canon_dossiers_ready",
            "organization_contract": {
                "materialized_root": (root / "organized").as_posix(),
            },
            "summary": {
                "domain_dossier_count": 1,
                "project_dossier_count": 1,
                "mirrored_project_dossier_count": 1,
            },
            "domains": [
                {
                    "domain_id": "water-simulation",
                    "label": "Water Simulation",
                    "folder": "01_water_simulation",
                    "family_count": 1,
                    "project_count": 2,
                    "version_count": 2,
                    "diff_count": 1,
                    "doc_count": 2,
                    "reference_count": 1,
                    "domain_dossier_relpath": "ION/05_context/current/project_portfolio/dossiers/domains/water-simulation/DOMAIN_DOSSIER.json",
                    "domain_dossier_markdown_relpath": "ION/05_context/current/project_portfolio/dossiers/domains/water-simulation/DOMAIN_DOSSIER.md",
                    "projects": [
                        {
                            "family_id": "cosmos:hyper-h2o",
                            "label": "Hyper H2O",
                            "domain_id": "water-simulation",
                            "current_path": (root / "source/hyper-h2o-v2").as_posix(),
                            "organized_path": organized.as_posix(),
                            "version_count": 2,
                            "diff_count": 1,
                            "doc_count": 2,
                            "reference_count": 1,
                            "launchable_count": 1,
                            "project_dossier_path": (root / project_dossier_rel).as_posix(),
                            "project_dossier_relpath": project_dossier_rel,
                            "project_dossier_markdown_path": (root / project_dossier_md_rel).as_posix(),
                            "project_dossier_markdown_relpath": project_dossier_md_rel,
                        }
                    ],
                }
            ],
        },
    )
    return organized


def test_project_specialist_contexts_write_domain_project_packets_and_folder_capsule(tmp_path):
    organized = seed_project_dossier_index(tmp_path)

    index = build_project_specialist_contexts(tmp_path)

    assert index["ok"] is True
    assert index["status"] == "project_specialist_contexts_ready"
    assert index["summary"]["domain_specialist_capsule_count"] == 1
    assert index["summary"]["project_specialist_capsule_count"] == 1
    assert index["summary"]["domain_agent_packet_count"] == 3
    assert index["summary"]["project_agent_packet_count"] == 5
    assert index["summary"]["total_agent_packet_count"] == 8
    assert (tmp_path / SPECIALIST_INDEX).exists()

    ion_dir = organized / ".ion"
    for name in (
        "PROJECT_SPECIALIST_CONTEXT_CAPSULE.json",
        "PROJECT_SPECIALIST_CONTEXT_CAPSULE.md",
        "ION_CONTEXT_CAPSULE.yaml",
        "ACTIVE_CONTEXT_PACKAGE.md",
        "SPECIALIST_AGENT_PACKETS.json",
        "AGENT.yaml",
        "DOMAIN.yaml",
        "RELATIONSHIPS.yaml",
    ):
        assert (ion_dir / name).exists()

    project = index["domains"][0]["project_specialist_capsules"][0]
    roles = {row["agent_role"] for row in project["agent_packets"]}
    assert roles == {
        "role.steward",
        "role.context_cartographer",
        "role.mason",
        "role.nemesis",
        "role.ionologist",
    }

    packet = json.loads(Path(project["agent_packets"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert packet["schema_id"] == "ion.agent_invocation_packet.v1"
    assert packet["execution"]["queue"] is False
    assert packet["authority"]["accepted_state_authority"] is False
    assert packet["authority"]["production_authority"] is False
    assert packet["authority"]["live_execution_authority"] is False
    assert packet["authority"]["secrets_authority"] is False
    assert packet["authority"]["local_write_authority"] == "none"
    assert "ION/05_context/current/project_portfolio/dossiers/PROJECT_CANON_DOSSIER_INDEX.json" in packet["capsule_context"]["required_reads"]

    receipt_paths = list((tmp_path / "ION/05_context/current/project_portfolio/receipts").glob("*_project_specialist_context_receipt.json"))
    assert len(receipt_paths) == 1
    receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8"))
    assert receipt["agent_invocation_status"] == "prepared_not_invoked"
    assert receipt["accepted_state_authority"] is False


def test_project_specialist_contexts_report_missing_dossier_index(tmp_path):
    result = build_project_specialist_contexts(tmp_path)

    assert result["ok"] is False
    assert result["status"] == "project_canon_dossier_index_missing"
    assert result["accepted_state_authority"] is False
