import json
from pathlib import Path

from kernel.ion_project_canon_dossier import (
    DOSSIER_INDEX,
    build_project_canon_dossiers,
)


def write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def seed_project_portfolio_manifest(root: Path) -> Path:
    organized = root / "organized/domains/01_water_simulation/hyper-h2o"
    organized.mkdir(parents=True, exist_ok=True)
    write_json(
        root,
        "ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json",
        {
            "schema_id": "ion.project_portfolio.v1",
            "generated_at": "2026-06-03T12:00:00+00:00",
            "status": "project_portfolio_ready",
            "summary": {
                "canonical_domain_count": 1,
                "project_root_count": 2,
                "family_count": 1,
                "versioned_family_count": 1,
                "diff_manifest_count": 1,
                "documentation_surface_count": 2,
            },
            "organizer": {
                "materialized_root": (root / "organized").as_posix(),
                "source_copy_policy": "domain/project current source copy only; historical full folders become lineage pointers and diff manifests",
            },
            "canonical_domains": [
                {
                    "domain_id": "water-simulation",
                    "group_id": "water-simulation",
                    "label": "Water Simulation",
                    "summary": "Water projects.",
                    "folder": "01_water_simulation",
                    "sort_order": 1,
                    "family_count": 1,
                    "project_count": 2,
                    "version_count": 2,
                    "branch_count": 1,
                    "diff_count": 1,
                    "launchable_count": 1,
                    "doc_count": 2,
                    "reference_count": 1,
                    "documented_family_count": 1,
                    "versioned_family_count": 1,
                    "operating_system": {
                        "posture": "ready",
                        "average_readiness_score": 86,
                        "board_columns": [{"column_id": "ready", "label": "Ready", "count": 1}],
                        "top_risks": [],
                        "maintenance_rhythm": [{"cadence": "weekly", "label": "Lineage Review", "focus": "diffs"}],
                    },
                    "docs": {"status": "domain_docs_projected", "recommended_sections": ["Project Overview"]},
                }
            ],
            "families": [
                {
                    "family_id": "cosmos:hyper-h2o",
                    "domain_id": "water-simulation",
                    "domain_label": "Water Simulation",
                    "label": "Hyper H2O",
                    "source_ids": ["cosmos"],
                    "project_count": 2,
                    "version_count": 2,
                    "branch_count": 1,
                    "diff_count": 1,
                    "launchable_count": 1,
                    "doc_count": 2,
                    "reference_count": 1,
                    "current_project_id": "cosmos:hyper-h2o-v2",
                    "current_path": (root / "source/hyper-h2o-v2").as_posix(),
                    "organized_path": organized.as_posix(),
                    "lineage_status": "version_chain_ready",
                    "materialization_plan": "copy current source only; write version lineage and diff manifests",
                    "current": {
                        "project_id": "cosmos:hyper-h2o-v2",
                        "path": (root / "source/hyper-h2o-v2").as_posix(),
                        "stack": "vite",
                        "launchable": True,
                        "launch": {"launchable": True, "status": "ready", "framework": "vite", "action_path": "/launch"},
                    },
                    "versions": [
                        {
                            "version_id": "001-v1",
                            "project_id": "cosmos:hyper-h2o-v1",
                            "display_label": "v1 - Hyper H2O",
                            "branch_label": "Main",
                            "path": (root / "source/hyper-h2o-v1").as_posix(),
                            "stack": "vite",
                            "launchable": False,
                            "is_current": False,
                            "docs": {"doc_count": 1, "status": "docs_present"},
                        },
                        {
                            "version_id": "002-v2",
                            "project_id": "cosmos:hyper-h2o-v2",
                            "display_label": "v2 - Hyper H2O",
                            "branch_label": "Main",
                            "path": (root / "source/hyper-h2o-v2").as_posix(),
                            "stack": "vite",
                            "launchable": True,
                            "is_current": True,
                            "docs": {"doc_count": 1, "status": "docs_present"},
                        },
                    ],
                    "diffs": [
                        {
                            "diff_id": "001_v1_to_v2",
                            "from_project_id": "cosmos:hyper-h2o-v1",
                            "to_project_id": "cosmos:hyper-h2o-v2",
                            "from_label": "v1 - Hyper H2O",
                            "to_label": "v2 - Hyper H2O",
                            "from_path": (root / "source/hyper-h2o-v1").as_posix(),
                            "to_path": (root / "source/hyper-h2o-v2").as_posix(),
                            "status": "candidate_diff_manifest",
                            "copy_policy": "do not copy historical source roots",
                            "file_diff": {
                                "status": "ready",
                                "added_count": 2,
                                "removed_count": 1,
                                "changed_count": 3,
                                "changed_sample": ["src/App.tsx", "src/water.ts", "package.json"],
                            },
                        }
                    ],
                    "docs": {
                        "status": "docs_present",
                        "doc_count": 2,
                        "reference_count": 1,
                        "coverage": {"has_readme": True, "has_architecture": True, "has_runbook": False, "has_references": True},
                        "primary_docs": [{"kind": "readme", "title": "README", "path": "README.md"}],
                        "references": [{"label": "Source root", "target": "/source"}],
                        "target_docs": [{"label": "Project overview", "path": "docs/PROJECT_OVERVIEW.md"}],
                    },
                    "operating_system": {
                        "posture": "ready",
                        "readiness_score": 86,
                        "quality_gates": [{"label": "Docs Bound", "status": "pass", "evidence": "2 docs"}],
                        "risk_register": [{"severity": "medium", "title": "Preview proof missing", "mitigation": "capture screenshot"}],
                        "next_actions": [{"action_id": "capture_preview", "label": "Capture preview", "detail": "attach screenshot"}],
                    },
                }
            ],
        },
    )
    return organized


def test_project_canon_dossier_generator_writes_index_domain_project_and_mirror(tmp_path):
    organized = seed_project_portfolio_manifest(tmp_path)

    index = build_project_canon_dossiers(tmp_path)

    assert index["ok"] is True
    assert index["summary"]["domain_dossier_count"] == 1
    assert index["summary"]["project_dossier_count"] == 1
    assert (tmp_path / DOSSIER_INDEX).exists()
    assert (organized / "CANON_DOSSIER.md").exists()
    assert (organized / "CANON_DOSSIER.json").exists()

    domain_markdown = (tmp_path / "ION/05_context/current/project_portfolio/dossiers/domains/water-simulation/DOMAIN_DOSSIER.md").read_text(encoding="utf-8")
    project_markdown = (tmp_path / "ION/05_context/current/project_portfolio/dossiers/domains/water-simulation/projects/cosmos-hyper-h2o.md").read_text(encoding="utf-8")
    assert "Domain Workflow" in domain_markdown
    assert "Hyper H2O" in domain_markdown
    assert "001_v1_to_v2" in project_markdown
    assert "change explanation" in project_markdown
    assert "Chats And Context Capsules" in project_markdown
    assert "binding_pending" in project_markdown
    assert "Future Plan" in project_markdown

    receipt_paths = list((tmp_path / "ION/05_context/current/project_portfolio/receipts").glob("*_project_canon_dossier_receipt.json"))
    assert len(receipt_paths) == 1
    receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8"))
    assert receipt["project_dossier_count"] == 1
    assert receipt["accepted_state_authority"] is False
    assert receipt["production_authority"] is False


def test_project_canon_dossier_generator_reports_missing_manifest(tmp_path):
    result = build_project_canon_dossiers(tmp_path)

    assert result["ok"] is False
    assert result["status"] == "project_portfolio_manifest_missing"
    assert result["accepted_state_authority"] is False
