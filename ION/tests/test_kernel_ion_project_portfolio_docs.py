from pathlib import Path
import json
import zipfile

from kernel.ion_project_launcher import project_launch_metadata
from kernel.ion_project_portfolio import (
    PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION,
    materialize_project_portfolio_action,
    scan_project_portfolio,
)


def test_project_portfolio_projects_docs_and_references(tmp_path: Path):
    ion_root = tmp_path / "ion"
    cosmos_root = tmp_path / "cosmos"
    app_dev_root = tmp_path / "application_dev"
    target = tmp_path / "organized"
    project = cosmos_root / "ProFlow" / "hyper-water-lab"
    docs = project / "docs"
    docs.mkdir(parents=True)
    app_dev_root.mkdir()
    ion_root.mkdir()
    (ion_root / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    (project / "package.json").write_text(
        '{"name":"proflow-water-lab","version":"1.2.3","homepage":"https://example.test/proflow","scripts":{"dev":"vite --host 127.0.0.1"}}\n',
        encoding="utf-8",
    )
    (project / "README.md").write_text("# ProFlow Water Lab\n\nPrimary operator overview.\n", encoding="utf-8")
    (docs / "ARCHITECTURE.md").write_text("# Architecture\n\nRendering and fluid architecture.\n", encoding="utf-8")
    (docs / "SOURCE_AUTHORITY.md").write_text("# Source Authority\n\nDataset and source references.\n", encoding="utf-8")

    portfolio = scan_project_portfolio(
        ion_root,
        cosmos_root=cosmos_root,
        application_dev_root=app_dev_root,
        materialized_root=target,
    )

    assert portfolio["summary"]["documentation_surface_count"] >= 3
    water_domain = next(domain for domain in portfolio["canonical_domains"] if domain["domain_id"] == "water-simulation")
    assert water_domain["doc_count"] >= 3
    assert water_domain["reference_count"] >= 3
    family = next(family for family in portfolio["families"] if family["domain_id"] == "water-simulation")
    assert family["docs"]["coverage"]["has_readme"] is True
    assert family["docs"]["coverage"]["has_architecture"] is True
    assert family["docs"]["coverage"]["has_references"] is True
    assert family["versions"][0]["docs"]["doc_count"] >= 3
    assert any(doc["kind"] == "source" for doc in family["docs"]["docs"])
    assert family["operating_system"]["schema_id"] == "ion.project_operating_system.v1"
    assert family["operating_system"]["readiness_score"] >= 70
    assert family["operating_system"]["maintenance_lanes"]
    assert water_domain["operating_system"]["schema_id"] == "ion.project_domain_operating_system.v1"
    assert water_domain["operating_system"]["board_columns"]


def test_project_portfolio_materialize_action_is_confirmed_and_receipted(monkeypatch, tmp_path: Path):
    ion_root = tmp_path / "ion"
    cosmos_root = tmp_path / "cosmos"
    app_dev_root = tmp_path / "application_dev"
    target = tmp_path / "organized"
    project = cosmos_root / "GlobeView" / "earth-lab"
    project.mkdir(parents=True)
    app_dev_root.mkdir()
    ion_root.mkdir()
    (ion_root / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    (project / "package.json").write_text('{"name":"earth-lab","version":"2.0.0","scripts":{"dev":"vite"}}\n', encoding="utf-8")
    (project / "README.md").write_text("# Earth Lab\n", encoding="utf-8")

    monkeypatch.setenv("ION_COSMOS_ROOT", cosmos_root.as_posix())
    monkeypatch.setenv("ION_APPLICATION_DEV_ROOT", app_dev_root.as_posix())
    monkeypatch.setenv("ION_PROJECTS_ORGANIZED_ROOT", target.as_posix())

    blocked = materialize_project_portfolio_action(ion_root, {})
    assert blocked["ok"] is False
    assert blocked["finding"] == "project_portfolio_materialize_confirmation_required"

    wrong_target = materialize_project_portfolio_action(
        ion_root,
        {
            "confirmation": PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION,
            "target": (tmp_path / "wrong").as_posix(),
        },
    )
    assert wrong_target["ok"] is False
    assert wrong_target["finding"] == "unsupported_project_portfolio_materialize_target"

    result = materialize_project_portfolio_action(
        ion_root,
        {"confirmation": PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION},
    )

    assert result["ok"] is True
    assert result["materialized_root"] == target.as_posix()
    assert result["portfolio_summary"]["family_count"] >= 1
    assert result["latest_receipt"]["relpath"].endswith("_project_portfolio_materialization_receipt.json")
    assert (target / "MANIFEST.json").exists()
    assert (target / "domains").exists()
    assert result["accepted_state_authority"] is False
    assert result["production_authority"] is False


def test_project_portfolio_merges_cosmos_archive_lineage_and_diffs(tmp_path: Path):
    ion_root = tmp_path / "ion"
    cosmos_root = tmp_path / "cosmos"
    app_dev_root = tmp_path / "application_dev"
    target = tmp_path / "organized"
    latest = cosmos_root / "sailboat-ilca-latest-viewer" / "source" / "latest"
    latest_src = latest / "src"
    app_dev_root.mkdir()
    ion_root.mkdir()
    latest_src.mkdir(parents=True)
    (ion_root / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    (latest / "package.json").write_text(
        json.dumps({"name": "laser-ilca-parametric-r3f", "version": "0.9.0", "scripts": {"dev": "vite"}}),
        encoding="utf-8",
    )
    (latest / "vite.config.ts").write_text("export default {};\n", encoding="utf-8")
    (latest_src / "boat.ts").write_text("export const hull = 'latest';\n", encoding="utf-8")
    (latest_src / "rig.ts").write_text("export const rig = 'new';\n", encoding="utf-8")
    archive_path = cosmos_root / "laser-ilca-parametric-r3f-v0.8-fixed-step-coupled-sim.zip"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "laser-ilca-parametric-r3f-v0.8-fixed-step-coupled-sim/package.json",
            json.dumps({"name": "laser-ilca-parametric-r3f", "version": "0.8.0", "scripts": {"dev": "vite"}}),
        )
        archive.writestr("laser-ilca-parametric-r3f-v0.8-fixed-step-coupled-sim/README.md", "# ILCA v0.8\n")
        archive.writestr("laser-ilca-parametric-r3f-v0.8-fixed-step-coupled-sim/src/boat.ts", "export const hull = 'old';\n")

    portfolio = scan_project_portfolio(
        ion_root,
        cosmos_root=cosmos_root,
        application_dev_root=app_dev_root,
        materialized_root=target,
    )

    family = next(family for family in portfolio["families"] if family["family_id"] == "cosmos:sailboat-ilca")
    assert family["source_ids"] == ["cosmos", "cosmos_archive"]
    assert family["version_count"] == 2
    assert family["current_path"] == latest.as_posix()
    assert family["launchable_count"] == 1
    diff = family["diffs"][0]["file_diff"]
    assert diff["status"] == "ready"
    assert "src/rig.ts" in diff["added_sample"]
    assert "src/boat.ts" in diff["changed_sample"]


def test_project_launcher_detects_static_app_html_package(tmp_path: Path):
    project = tmp_path / "earth-static"
    app = project / "app"
    app.mkdir(parents=True)
    (project / "package.json").write_text(
        json.dumps({"name": "earth-static", "scripts": {"serve": "python3 -m http.server 5174 --directory app"}}),
        encoding="utf-8",
    )
    (app / "EARTH.html").write_text("<main>earth</main>\n", encoding="utf-8")

    metadata = project_launch_metadata(project)

    assert metadata["launchable"] is True
    assert metadata["framework"] == "static"
