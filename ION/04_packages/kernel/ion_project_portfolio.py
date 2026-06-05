"""Project portfolio discovery and candidate organization.

This module builds a local, read-only catalog for the Helixion Projects cockpit
and can materialize a non-destructive candidate organization folder. The
materialized folder is source-focused: runtime installs, build outputs, raw data,
receipts, proof bundles, git internals, and secret-looking files are skipped.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
from typing import Any, Iterable, Mapping
import zipfile

from .ion_project_launcher import project_launch_metadata


CURRENT = Path("ION/05_context/current")
PORTFOLIO_DIR = CURRENT / "project_portfolio"
PORTFOLIO_MANIFEST = PORTFOLIO_DIR / "PROJECT_PORTFOLIO_MANIFEST.json"
PORTFOLIO_RECEIPTS_DIR = PORTFOLIO_DIR / "receipts"
SCHEMA_ID = "ion.project_portfolio.v1"
MATERIALIZE_SCHEMA_ID = "ion.project_portfolio_materialization.v1"
PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION = "ION_PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMED"

MARKER_FILES = {
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "vite.config.ts",
    "vite.config.js",
    "vite.config.mjs",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
}

SCAN_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".codex",
    ".agents",
    ".next",
    ".nuxt",
    ".turbo",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "builds",
    "out",
    "coverage",
    "playwright-report",
    "test-results",
    "validation_outputs",
}

ARCHIVE_SOURCE_ID = "cosmos_archive"
ARCHIVE_SOURCE_LABEL = "Cosmos Archives"
ARCHIVE_SCAN_LIMIT = 160
ARCHIVE_HASH_MAX_BYTES = 80_000_000

COPY_IGNORED_DIRS = {
    *SCAN_IGNORED_DIRS,
    "data",
    "data1",
    "raw",
    "proof",
    "receipts",
    "backups",
    "archive",
    "archives",
    "tmp",
    "temp",
    "logs",
    ".terraform",
    ".vercel",
}

SECRET_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "secrets.json",
}

VERSION_TOKEN_RE = re.compile(r"(M\d+[A-Z]?|OWM[_-]?\d+|v\d+(?:[._-]\d+)*|20\d{6})", re.IGNORECASE)
DATE_TOKEN_RE = re.compile(r"(20\d{6})")
SAFE_ID_RE = re.compile(r"[^a-z0-9]+")
DOC_FILE_EXTENSIONS = {".md", ".mdx", ".txt", ".rst", ".html", ".htm", ".pdf"}
PRIMARY_DOC_NAMES = {
    "readme.md",
    "readme.mdx",
    "readme.txt",
    "architecture.md",
    "runbook.md",
    "quickstart.md",
    "getting_started.md",
    "getting-started.md",
    "changelog.md",
    "license",
}
REFERENCE_DOC_TOKENS = (
    "reference",
    "source",
    "authority",
    "manifest",
    "registry",
    "dataset",
    "api",
    "schema",
    "contract",
    "decision",
    "adr",
    "runbook",
    "architecture",
    "spec",
    "design",
)

CANONICAL_DOMAINS = [
    {
        "domain_id": "water-simulation",
        "label": "Water Simulation",
        "summary": "Water, ocean, fluid, H2O, wave, splash, and ProFlow work.",
        "folder": "01_water_simulation",
    },
    {
        "domain_id": "clouds-volumetrics",
        "label": "Clouds & Volumetrics",
        "summary": "Cloud, atmosphere, fog, volumetric rendering, and sky systems.",
        "folder": "02_clouds_volumetrics",
    },
    {
        "domain_id": "globe-planetary",
        "label": "Globe & Planetary",
        "summary": "Earth, globe, orbital evolution, planetary visualization, and terrain-scale world systems.",
        "folder": "03_globe_planetary",
    },
    {
        "domain_id": "lucid-editor",
        "label": "Lucid Editor",
        "summary": "Lucid Engine, editor, lasso, canvas, and application-builder work.",
        "folder": "04_lucid_editor",
    },
    {
        "domain_id": "ion-platform",
        "label": "ION Platform",
        "summary": "ION cockpit, carrier, context, queue, MCP, and platform projects.",
        "folder": "05_ion_platform",
    },
    {
        "domain_id": "vegetation-trees",
        "label": "Vegetation & Trees",
        "summary": "ProTree, vegetation, forests, leaves, canopy, and biome work.",
        "folder": "06_vegetation_trees",
    },
    {
        "domain_id": "terrain-geology",
        "label": "Terrain & Geology",
        "summary": "Terrain, rock, soil, geology, erosion, and landform projects.",
        "folder": "07_terrain_geology",
    },
    {
        "domain_id": "visual-effects",
        "label": "Visual Effects",
        "summary": "Special effects, particles, postprocessing, and visual experiments.",
        "folder": "08_visual_effects",
    },
    {
        "domain_id": "tools-generated-apps",
        "label": "Tools & Generated Apps",
        "summary": "Generated app labs, one-off tools, launchers, and miscellaneous prototypes.",
        "folder": "09_tools_generated_apps",
    },
]

DOMAIN_BY_ID = {domain["domain_id"]: domain for domain in CANONICAL_DOMAINS}


@dataclass(frozen=True)
class ProjectRoot:
    source_id: str
    source_label: str
    source_root: Path
    path: Path
    rel_path: str
    markers: tuple[str, ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compact(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return fallback


def slug(value: Any, fallback: str = "item") -> str:
    cleaned = SAFE_ID_RE.sub("-", compact(value, fallback).lower()).strip("-")
    return cleaned[:96] or fallback


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def default_application_dev_root(root: str | Path | None = None) -> Path:
    configured = os.environ.get("ION_APPLICATION_DEV_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    if root:
        shell_root = Path(root).expanduser().resolve()
        local = shell_root / "Application_Dev"
        if local.exists():
            return local
        sibling = shell_root.parent / "Application_Dev"
        if sibling.exists():
            return sibling
    return (Path.home() / "Application_Dev").resolve()


def default_cosmos_workspace_root(root: str | Path | None = None) -> Path:
    configured = os.environ.get("ION_COSMOS_ROOT") or os.environ.get("ION_COSMOS_WORKSPACE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    candidates: list[Path] = []
    if root:
        shell_root = Path(root).expanduser().resolve()
        candidates.extend([shell_root / "Cosmos", shell_root.parent / "Cosmos"])
    candidates.append(Path.home() / "Cosmos")
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def default_cosmos_project_root(root: str | Path | None = None) -> Path:
    configured = os.environ.get("ION_COSMOS_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    workspace = default_cosmos_workspace_root(root)
    project = workspace / "earth-forge"
    if project.exists():
        return project.resolve()
    old = Path.home() / "Cosmos" / "earth-forge"
    return old.resolve()


def default_materialized_root(root: str | Path | None = None) -> Path:
    configured = os.environ.get("ION_PROJECTS_ORGANIZED_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / "ION_PROJECTS_PROFESSIONAL_ORGANIZED_CANDIDATE").resolve()


def build_project_portfolio_model(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    return scan_project_portfolio(
        shell_root,
        cosmos_root=default_cosmos_workspace_root(shell_root),
        application_dev_root=default_application_dev_root(shell_root),
        materialized_root=default_materialized_root(shell_root),
    )


def scan_project_portfolio(
    root: str | Path,
    *,
    cosmos_root: str | Path,
    application_dev_root: str | Path,
    materialized_root: str | Path,
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    cosmos = Path(cosmos_root).expanduser().resolve()
    app_dev = Path(application_dev_root).expanduser().resolve()
    target = Path(materialized_root).expanduser().resolve()
    source_specs = [
        ("cosmos", "Cosmos", cosmos),
        ("application_dev", "Application Dev", app_dev),
        ("ion", "ION Development", shell_root),
    ]
    roots: list[ProjectRoot] = []
    workspace_dirs: list[dict[str, Any]] = []
    for source_id, source_label, source_root in source_specs:
        if not source_root.exists():
            continue
        if source_id == "ion":
            roots.extend(_ion_project_roots(source_label, source_root))
        else:
            roots.extend(_project_roots(source_id, source_label, source_root))
        workspace_dirs.extend(_workspace_dirs(source_id, source_label, source_root))

    projects = [_project_row(item) for item in roots]
    archive_projects = _archive_project_rows(
        cosmos,
        existing_project_paths={compact(project.get("path")) for project in projects},
    )
    projects.extend(archive_projects)
    families = _family_rows(projects, workspace_dirs, target)
    groups = _group_rows(families)
    canonical_domains = _canonical_domain_rows(families)
    duplicate_clusters = _duplicate_clusters(projects)
    recommendations = _recommendations(families, duplicate_clusters, target)
    os_ready_count = len([family for family in families if compact((family.get("operating_system") or {}).get("posture")) == "ready"])
    os_watch_count = len([family for family in families if compact((family.get("operating_system") or {}).get("posture")) == "watch"])
    os_blocked_count = len([family for family in families if compact((family.get("operating_system") or {}).get("posture")) == "blocked"])
    materialized_present = target.exists()
    manifest_rel = PORTFOLIO_MANIFEST.as_posix()
    summary = {
        "source_root_count": len([spec for spec in source_specs if spec[2].exists()]),
        "workspace_dir_count": len(workspace_dirs),
        "project_root_count": len(projects),
        "archive_project_count": len(archive_projects),
        "family_count": len(families),
        "group_count": len(canonical_domains),
        "canonical_domain_count": len(canonical_domains),
        "launchable_count": len([project for project in projects if project.get("launchable")]),
        "documentation_surface_count": sum(int(project.get("docs", {}).get("doc_count") or 0) for project in projects if isinstance(project.get("docs"), Mapping)),
        "reference_count": sum(int(project.get("docs", {}).get("reference_count") or 0) for project in projects if isinstance(project.get("docs"), Mapping)),
        "documented_family_count": len([family for family in families if int(family.get("doc_count") or 0) > 0]),
        "project_os_ready_count": os_ready_count,
        "project_os_watch_count": os_watch_count,
        "project_os_blocked_count": os_blocked_count,
        "legacy_copy_cluster_count": len(duplicate_clusters),
        "duplicate_cluster_count": len(duplicate_clusters),
        "versioned_family_count": len([family for family in families if family.get("version_count", 0) > 1]),
        "materialized_present": materialized_present,
    }
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": utc_now(),
        "status": "project_portfolio_ready",
        "source_roots": {
            "cosmos": cosmos.as_posix(),
            "cosmos_archives": cosmos.as_posix(),
            "application_dev": app_dev.as_posix(),
            "ion": shell_root.as_posix(),
        },
        "source_present": {
            "cosmos": cosmos.exists(),
            "cosmos_archives": cosmos.exists(),
            "application_dev": app_dev.exists(),
            "ion": shell_root.exists(),
        },
        "organizer": {
            "manifest_path": (shell_root / PORTFOLIO_MANIFEST).as_posix(),
            "manifest_relpath": manifest_rel,
            "materialized_root": target.as_posix(),
            "materialized_present": materialized_present,
            "materialize_path": "/cockpit/projects/organizer/materialize",
            "materialize_confirmation": PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION,
            "latest_materialization_receipt": _latest_materialization_receipt(shell_root),
            "source_copy_policy": "domain/project current source copy only; historical full folders become lineage pointers and diff manifests",
            "layout": "domains/<domain>/<project>/source/current plus lineage, notes, and screenshots",
            "excluded_dirs": sorted(COPY_IGNORED_DIRS),
            "max_file_bytes": 25_000_000,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "summary": summary,
        "canonical_domains": canonical_domains,
        "groups": groups,
        "families": families,
        "projects": projects,
        "workspace_dirs": workspace_dirs,
        "duplicate_clusters": duplicate_clusters,
        "recommendations": recommendations,
    }


def materialize_project_portfolio_action(root: str | Path = ".", payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    shell_root = Path(root).expanduser().resolve()
    if compact(payload.get("confirmation")) != PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION:
        return {
            "ok": False,
            "finding": "project_portfolio_materialize_confirmation_required",
            "required_confirmation": PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMATION,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    materialized_root = default_materialized_root(shell_root)
    requested_target = compact(payload.get("target"))
    if requested_target:
        try:
            requested_root = Path(requested_target).expanduser().resolve()
        except OSError:
            requested_root = Path("__invalid_target__")
        if requested_root != materialized_root:
            return {
                "ok": False,
                "finding": "unsupported_project_portfolio_materialize_target",
                "requested_target": requested_target,
                "allowed_target": materialized_root.as_posix(),
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            }

    result = materialize_project_portfolio(shell_root, target=materialized_root)
    portfolio = read_json(shell_root / PORTFOLIO_MANIFEST)
    latest_receipt = _latest_materialization_receipt(shell_root)
    return {
        **result,
        "portfolio_summary": portfolio.get("summary", {}) if isinstance(portfolio.get("summary"), Mapping) else {},
        "organizer": portfolio.get("organizer", {}) if isinstance(portfolio.get("organizer"), Mapping) else {},
        "latest_receipt": latest_receipt,
        "materialized_root": materialized_root.as_posix(),
        "copy_policy": "non_destructive_candidate_current_source_and_lineage_projection",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def materialize_project_portfolio(root: str | Path = ".", target: str | Path | None = None) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    materialized_root = Path(target).expanduser().resolve() if target else default_materialized_root(shell_root)
    portfolio = scan_project_portfolio(
        shell_root,
        cosmos_root=default_cosmos_workspace_root(shell_root),
        application_dev_root=default_application_dev_root(shell_root),
        materialized_root=materialized_root,
    )
    materialized_root.mkdir(parents=True, exist_ok=True)
    copies: list[dict[str, Any]] = []
    for family in portfolio.get("families", []):
        if not isinstance(family, Mapping):
            continue
        current = family.get("current")
        if not isinstance(current, Mapping):
            continue
        source_path = Path(compact(current.get("path"))).expanduser()
        domain_id = compact(family.get("domain_id") or family.get("group_id"), "tools-generated-apps")
        domain = DOMAIN_BY_ID.get(domain_id, DOMAIN_BY_ID["tools-generated-apps"])
        family_dir = materialized_root / "domains" / compact(domain.get("folder"), slug(domain_id)) / slug(family.get("label") or family.get("family_id"), "project")
        if compact(current.get("source_id")) == "ion":
            family_dir.mkdir(parents=True, exist_ok=True)
            _write_family_workspace(family_dir, family, domain)
            copies.append(
                {
                    "family_id": family.get("family_id"),
                    "domain_id": domain_id,
                    "source": source_path.as_posix(),
                    "target": (family_dir / "source" / "current").as_posix(),
                    "copy_status": "manifest_only_core_root",
                    "files_copied": 0,
                    "bytes_copied": 0,
                    "skipped": ["ion_core_root_not_copied"],
                }
            )
            continue
        if not source_path.exists() or not source_path.is_dir():
            continue
        current_dir = family_dir / "source" / "current"
        copy_result = _copy_source_tree(source_path, current_dir)
        _write_family_workspace(family_dir, family, domain)
        copies.append(
            {
                "family_id": family.get("family_id"),
                "domain_id": domain_id,
                "source": source_path.as_posix(),
                "target": current_dir.as_posix(),
                **copy_result,
            }
        )

    portfolio = {
        **portfolio,
        "summary": {
            **portfolio.get("summary", {}),
            "materialized_present": True,
        },
        "organizer": {
            **portfolio.get("organizer", {}),
            "materialized_root": materialized_root.as_posix(),
            "materialized_present": True,
            "latest_materialization_receipt": _latest_materialization_receipt(shell_root),
        },
        "materialization": {
            "schema_id": MATERIALIZE_SCHEMA_ID,
            "created_at": utc_now(),
            "copy_count": len(copies),
            "copies": copies,
            "non_claims": [
                "original project folders were not moved, deleted, or quarantined",
                "only current project source is copied into the professional organizer",
                "historical full folders are represented as lineage records and diff manifests, not copied versions",
                "candidate organizer folders are not accepted canonical replacements",
            ],
        },
    }
    write_json(shell_root / PORTFOLIO_MANIFEST, portfolio)
    write_json(materialized_root / "MANIFEST.json", portfolio)
    _write_portfolio_readme(materialized_root, portfolio)
    receipt = _write_materialization_receipt(shell_root, materialized_root, portfolio, copies)
    portfolio["organizer"]["latest_materialization_receipt"] = _latest_materialization_receipt(shell_root)
    write_json(shell_root / PORTFOLIO_MANIFEST, portfolio)
    write_json(materialized_root / "MANIFEST.json", portfolio)
    return {
        "ok": True,
        "schema_id": "ion.project_portfolio_materialization_result.v1",
        "manifest_path": (shell_root / PORTFOLIO_MANIFEST).as_posix(),
        "materialized_root": materialized_root.as_posix(),
        "receipt_path": receipt.as_posix(),
        "copy_count": len(copies),
        "project_root_count": portfolio.get("summary", {}).get("project_root_count", 0),
        "family_count": portfolio.get("summary", {}).get("family_count", 0),
        "duplicate_cluster_count": portfolio.get("summary", {}).get("duplicate_cluster_count", 0),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _project_roots(source_id: str, source_label: str, source_root: Path, *, max_depth: int = 4) -> list[ProjectRoot]:
    rows: list[ProjectRoot] = []
    seen: set[Path] = set()
    base_depth = len(source_root.parts)
    for dirpath, dirnames, filenames in os.walk(source_root):
        current = Path(dirpath)
        rel_depth = len(current.parts) - base_depth
        dirnames[:] = [name for name in dirnames if name not in SCAN_IGNORED_DIRS and not name.startswith(".tmp")]
        if rel_depth >= max_depth:
            dirnames[:] = []
        markers = tuple(sorted(set(filenames).intersection(MARKER_FILES)))
        if not markers:
            continue
        if current in seen:
            continue
        seen.add(current)
        try:
            rel_path = current.relative_to(source_root).as_posix() or "."
        except ValueError:
            rel_path = current.as_posix()
        rows.append(ProjectRoot(source_id, source_label, source_root, current, rel_path, markers))
    return rows


def _ion_project_roots(source_label: str, source_root: Path) -> list[ProjectRoot]:
    try:
        markers = tuple(sorted(path.name for path in source_root.iterdir() if path.is_file() and path.name in MARKER_FILES))
    except OSError:
        markers = ()
    if not markers:
        markers = ("pyproject.toml",) if (source_root / "pyproject.toml").exists() else ()
    if not markers:
        return []
    return [ProjectRoot("ion", source_label, source_root, source_root, ".", markers)]


def _workspace_dirs(source_id: str, source_label: str, source_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        children = [path for path in source_root.iterdir() if path.is_dir() and path.name not in SCAN_IGNORED_DIRS]
    except OSError:
        return rows
    for child in sorted(children, key=lambda item: item.name.lower()):
        if child.name.startswith("."):
            continue
        family_id, group_id, family_label = _infer_family(source_id, child.name, (child.name,), {})
        rows.append(
            {
                "workspace_dir_id": f"{source_id}:{slug(child.name)}",
                "source_id": source_id,
                "source_label": source_label,
                "family_id": family_id,
                "group_id": group_id,
                "label": family_label,
                "name": child.name,
                "path": child.as_posix(),
                "rel_path": child.name,
            }
        )
    return rows


def _archive_project_rows(source_root: Path, *, existing_project_paths: set[str]) -> list[dict[str, Any]]:
    if not source_root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for archive_path in _archive_paths(source_root):
        row = _archive_project_row(source_root, archive_path, existing_project_paths=existing_project_paths)
        if row:
            rows.append(row)
    return rows


def _archive_paths(source_root: Path) -> list[Path]:
    scan_dirs = [source_root, source_root / "ProFlow" / "builds"]
    seen: set[Path] = set()
    rows: list[Path] = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists() or not scan_dir.is_dir():
            continue
        try:
            candidates = sorted(scan_dir.glob("*.zip"), key=lambda item: (item.stat().st_mtime, item.name.lower()), reverse=True)
        except OSError:
            continue
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            rows.append(resolved)
            if len(rows) >= ARCHIVE_SCAN_LIMIT:
                return rows
    return rows[:ARCHIVE_SCAN_LIMIT]


def _archive_project_row(source_root: Path, archive_path: Path, *, existing_project_paths: set[str]) -> dict[str, Any] | None:
    summary = _zip_archive_summary(archive_path)
    if compact(summary.get("status")) != "ok":
        return None
    package_json = summary.get("package_json") if isinstance(summary.get("package_json"), Mapping) else {}
    root_name = compact(summary.get("root_name"), archive_path.stem)
    archive_rel_path = _relative_to(archive_path, source_root)
    rel_parts = tuple(PurePosixPath(archive_rel_path).parts)
    family_id, group_id, family_label = _infer_family(ARCHIVE_SOURCE_ID, archive_path.stem, rel_parts, package_json)
    domain_id = _canonical_domain_id(ARCHIVE_SOURCE_ID, archive_path.stem, rel_parts, package_json)
    assembled_path = _archive_assembled_path(source_root, archive_path, summary)
    if assembled_path and assembled_path.as_posix() in existing_project_paths:
        return None

    scripts = package_json.get("scripts") if isinstance(package_json.get("scripts"), Mapping) else {}
    markers = tuple(compact(marker) for marker in summary.get("markers", []) if compact(marker))
    name = compact(package_json.get("name"), archive_path.stem)
    version = compact(package_json.get("version"), "")
    version_token, date_token, milestone_token = _version_tokens(archive_path.stem, archive_rel_path, version)
    stack = _stack(markers, scripts)
    if assembled_path:
        project_path = assembled_path
        launch = {
            **project_launch_metadata(assembled_path, scripts=scripts, markers=markers),
            "project_path": assembled_path.as_posix(),
        }
        launchable = bool(launch.get("launchable"))
        load_mode = "source_path"
        status = "archive_backed_source_present"
    else:
        project_path = archive_path
        launchable = False
        launch = {
            "launchable": False,
            "framework": stack,
            "mode": "archive_metadata_only",
            "requires_local_machine": True,
            "install_repair_on_launch": False,
            "managed_window_stops_server": False,
            "status": "archive_not_extracted",
            "project_path": archive_path.as_posix(),
        }
        load_mode = "archive_zip"
        status = "archive_witness_only"

    docs = _archive_docs(archive_path, summary, package_json=package_json, source_root=source_root, assembled_path=assembled_path)
    project_id = f"{ARCHIVE_SOURCE_ID}:{slug(archive_rel_path)}"
    return {
        "project_id": project_id,
        "source_id": ARCHIVE_SOURCE_ID,
        "source_label": ARCHIVE_SOURCE_LABEL,
        "family_id": family_id,
        "group_id": group_id,
        "domain_id": domain_id,
        "domain_label": DOMAIN_BY_ID.get(domain_id, {}).get("label", _label_from_name(domain_id)),
        "family_label": family_label,
        "label": _label_from_name(name or archive_path.stem),
        "name": name,
        "package_version": version,
        "version_token": version_token,
        "date_token": date_token,
        "milestone_token": milestone_token,
        "branch_id": "archive",
        "branch_label": "Archive",
        "path": project_path.as_posix(),
        "source_root": source_root.as_posix(),
        "rel_path": archive_rel_path,
        "markers": list(markers),
        "stack": stack,
        "launchable": launchable,
        "launch": launch,
        "docs": docs,
        "scripts": {key: compact(value) for key, value in scripts.items() if key in {"dev", "start", "build", "test", "lint", "preview", "serve", "validate"}},
        "load": {
            "mode": load_mode,
            "label": "Load assembled source" if assembled_path else "Inspect archive version",
            "path": project_path.as_posix(),
            "archive_path": archive_path.as_posix(),
            "launchable": launchable,
        },
        "archive": {
            "schema_id": "ion.project_archive_source.v1",
            "status": status,
            "archive_path": archive_path.as_posix(),
            "archive_rel_path": archive_rel_path,
            "root_name": root_name,
            "package_json_path": compact(summary.get("package_json_path")),
            "file_count": int(summary.get("file_count") or 0),
            "doc_count": int(summary.get("doc_count") or 0),
            "total_uncompressed_bytes": int(summary.get("total_uncompressed_bytes") or 0),
            "archive_bytes": archive_path.stat().st_size if archive_path.exists() else 0,
            **_archive_hash_metadata(archive_path),
            "assembled_path": assembled_path.as_posix() if assembled_path else "",
        },
        "has_git": False,
        "status": status,
    }


def _zip_archive_summary(archive_path: Path) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            names = [info.filename for info in infos]
            root_name = _zip_common_root(names)
            markers: set[str] = set()
            doc_entries: list[dict[str, Any]] = []
            app_entries: list[str] = []
            package_json: dict[str, Any] = {}
            package_json_path = ""
            package_infos = [info for info in infos if PurePosixPath(info.filename).name == "package.json" and not _zip_entry_ignored(info.filename, root_name)]
            if package_infos:
                package_info = sorted(package_infos, key=lambda info: (len(PurePosixPath(info.filename).parts), info.filename))[0]
                package_json_path = package_info.filename
                try:
                    payload = json.loads(archive.read(package_info).decode("utf-8", errors="replace"))
                    package_json = payload if isinstance(payload, dict) else {}
                except Exception:
                    package_json = {}
            for info in infos:
                rel_path = _zip_entry_rel(info.filename, root_name)
                if not rel_path or _zip_entry_ignored(info.filename, root_name):
                    continue
                basename = PurePosixPath(rel_path).name
                if basename in MARKER_FILES:
                    markers.add(basename)
                suffix = PurePosixPath(rel_path).suffix.lower()
                lower = rel_path.lower()
                if suffix in {".html", ".htm"} and (rel_path.startswith("app/") or rel_path.count("/") == 0):
                    app_entries.append(rel_path)
                if suffix in DOC_FILE_EXTENSIONS or basename.lower() in PRIMARY_DOC_NAMES:
                    doc_entries.append({"path": info.filename, "rel_path": rel_path, "bytes": info.file_size})
            return {
                "status": "ok",
                "root_name": root_name,
                "file_count": len(infos),
                "total_uncompressed_bytes": sum(info.file_size for info in infos),
                "markers": sorted(markers),
                "package_json": package_json,
                "package_json_path": package_json_path,
                "doc_entries": sorted(doc_entries, key=lambda item: compact(item.get("rel_path")))[:96],
                "doc_count": len(doc_entries),
                "app_entries": sorted(set(app_entries))[:24],
            }
    except (OSError, zipfile.BadZipFile):
        return {"status": "unreadable_zip"}


def _archive_docs(
    archive_path: Path,
    summary: Mapping[str, Any],
    *,
    package_json: Mapping[str, Any],
    source_root: Path,
    assembled_path: Path | None,
) -> dict[str, Any]:
    docs: list[dict[str, Any]] = []
    for entry in summary.get("doc_entries", []) if isinstance(summary.get("doc_entries"), list) else []:
        if not isinstance(entry, Mapping):
            continue
        row = _archive_doc_row(archive_path, entry)
        if row:
            docs.append(row)
        if len(docs) >= 48:
            break
    docs = sorted(docs, key=lambda row: (0 if row.get("primary") else 1, compact(row.get("kind")), compact(row.get("rel_path"))))
    references = [
        {
            "type": "archive_source",
            "label": "Archive source",
            "target": archive_path.as_posix(),
            "detail": "Cosmos zip archive represented as a version lineage source.",
        },
        {
            "type": "source_collection",
            "label": "Source collection",
            "target": source_root.as_posix(),
            "detail": "Parent local source collection for this archive.",
        },
    ]
    if assembled_path:
        references.append(
            {
                "type": "assembled_source",
                "label": "Assembled source",
                "target": assembled_path.as_posix(),
                "detail": "Clean local extraction/assembly path mapped to this archive version.",
            }
        )
    references.extend(_package_reference_rows(package_json))
    primary = docs[0] if docs else {}
    return {
        "schema_id": "ion.project_archive_docs.v1",
        "status": "docs_present" if docs else "docs_missing",
        "doc_count": len(docs),
        "reference_count": len(references),
        "primary_doc": primary,
        "docs": docs,
        "references": references,
        "coverage": {
            "has_readme": any(compact(row.get("kind")) == "readme" for row in docs),
            "has_architecture": any(compact(row.get("kind")) == "architecture" for row in docs),
            "has_runbook": any(compact(row.get("kind")) == "runbook" for row in docs),
            "has_reference": any(bool(row.get("reference")) for row in docs) or bool(references),
        },
    }


def _archive_doc_row(archive_path: Path, entry: Mapping[str, Any]) -> dict[str, Any] | None:
    rel_path = compact(entry.get("rel_path"))
    archive_entry = compact(entry.get("path"), rel_path)
    if not rel_path:
        return None
    lower = rel_path.lower()
    kind = _doc_kind(lower)
    title, excerpt = _zip_doc_title_excerpt(archive_path, archive_entry, int(entry.get("bytes") or 0))
    return {
        "title": title or _label_from_name(PurePosixPath(rel_path).stem),
        "kind": kind,
        "rel_path": rel_path,
        "path": f"{archive_path.as_posix()}::{archive_entry}",
        "extension": PurePosixPath(rel_path).suffix.lower() or PurePosixPath(rel_path).name.lower(),
        "bytes": int(entry.get("bytes") or 0),
        "primary": PurePosixPath(rel_path).name.lower() in PRIMARY_DOC_NAMES or rel_path.count("/") == 0 and kind in {"readme", "architecture", "runbook"},
        "reference": any(token in lower for token in REFERENCE_DOC_TOKENS),
        "excerpt": excerpt,
        "source_root": archive_path.as_posix(),
    }


def _zip_doc_title_excerpt(archive_path: Path, archive_entry: str, size: int, *, max_chars: int = 520) -> tuple[str, str]:
    suffix = PurePosixPath(archive_entry).suffix.lower()
    if suffix not in {".md", ".mdx", ".txt", ".rst", ".html", ".htm", ""} or size > 400_000:
        return "", ""
    try:
        with zipfile.ZipFile(archive_path) as archive:
            text = archive.read(archive_entry).decode("utf-8", errors="replace")
    except Exception:
        return "", ""
    return _title_excerpt_from_text(text, max_chars=max_chars)


def _package_reference_rows(package_json: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    repository = package_json.get("repository")
    if isinstance(repository, Mapping):
        repository = repository.get("url")
    for key, label in (("homepage", "Homepage"), ("repository", "Repository"), ("bugs", "Issue tracker")):
        value = repository if key == "repository" else package_json.get(key)
        if isinstance(value, Mapping):
            value = value.get("url")
        if compact(value):
            rows.append({"type": key, "label": label, "target": compact(value), "detail": "Package metadata reference."})
    return rows


def _archive_assembled_path(source_root: Path, archive_path: Path, summary: Mapping[str, Any]) -> Path | None:
    stem = archive_path.stem
    root_name = compact(summary.get("root_name"))
    candidates: list[Path] = []
    if root_name:
        candidates.append(source_root / root_name)
    lower_stem = stem.lower()
    if lower_stem.startswith("laser-ilca-parametric-r3f-v0.9"):
        candidates.append(source_root / "sailboat-ilca-latest-viewer" / "source" / "latest")
    if lower_stem.startswith("ion_earth_orbital_evo_m9b"):
        candidates.append(source_root / "cosmos-zip-assemblies" / "earth-orbital-evo" / "source" / "latest")
    if lower_stem.startswith("owm_017"):
        candidates.append(source_root / "cosmos-zip-assemblies" / "hyper-h2o" / "source" / "latest")
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate.resolve()
    return None


def _archive_hash_metadata(archive_path: Path) -> dict[str, Any]:
    try:
        size = archive_path.stat().st_size
    except OSError:
        return {"sha256": "", "hash_status": "missing"}
    if size > ARCHIVE_HASH_MAX_BYTES:
        return {"sha256": "", "hash_status": "skipped_large_archive"}
    try:
        return {"sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(), "hash_status": "ready"}
    except OSError:
        return {"sha256": "", "hash_status": "unreadable"}


def _zip_common_root(names: Iterable[str]) -> str:
    first_parts = []
    for name in names:
        parts = PurePosixPath(name).parts
        if parts:
            first_parts.append(parts[0])
    unique = {part for part in first_parts if part not in {"", "."}}
    return next(iter(unique)) if len(unique) == 1 else ""


def _zip_entry_rel(name: str, root_name: str) -> str:
    parts = PurePosixPath(name).parts
    if root_name and parts and parts[0] == root_name:
        parts = parts[1:]
    return PurePosixPath(*parts).as_posix() if parts else ""


def _zip_entry_ignored(name: str, root_name: str) -> bool:
    rel_path = _zip_entry_rel(name, root_name)
    parts = PurePosixPath(rel_path).parts
    if any(part in COPY_IGNORED_DIRS or _looks_secret(part) for part in parts):
        return True
    return _looks_secret(PurePosixPath(rel_path).name)


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _project_row(item: ProjectRoot) -> dict[str, Any]:
    package_json = read_json(item.path / "package.json")
    scripts = package_json.get("scripts") if isinstance(package_json.get("scripts"), Mapping) else {}
    rel_parts = tuple(Path(item.rel_path).parts) if item.rel_path != "." else (item.path.name,)
    family_id, group_id, family_label = _infer_family(item.source_id, item.path.name, rel_parts, package_json)
    domain_id = _canonical_domain_id(item.source_id, item.path.name, rel_parts, package_json)
    branch_id, branch_label = _branch_from_rel_path(item.rel_path)
    name = compact(package_json.get("name"), item.path.name)
    version = compact(package_json.get("version"), "")
    version_token, date_token, milestone_token = _version_tokens(item.path.name, item.rel_path, version)
    stack = _stack(item.markers, scripts)
    launch = {
        **project_launch_metadata(item.path, scripts=scripts, markers=item.markers),
        "project_path": item.path.as_posix(),
    }
    launchable = bool(launch.get("launchable"))
    docs = _project_docs(item.path, package_json=package_json, source_root=item.source_root)
    project_id = "ion:ion-development" if item.source_id == "ion" and item.rel_path == "." else f"{item.source_id}:{slug(item.rel_path)}"
    return {
        "project_id": project_id,
        "source_id": item.source_id,
        "source_label": item.source_label,
        "family_id": family_id,
        "group_id": group_id,
        "domain_id": domain_id,
        "domain_label": DOMAIN_BY_ID.get(domain_id, {}).get("label", _label_from_name(domain_id)),
        "family_label": family_label,
        "label": _label_from_name(name or item.path.name),
        "name": name,
        "package_version": version,
        "version_token": version_token,
        "date_token": date_token,
        "milestone_token": milestone_token,
        "branch_id": branch_id,
        "branch_label": branch_label,
        "path": item.path.as_posix(),
        "source_root": item.source_root.as_posix(),
        "rel_path": item.rel_path,
        "markers": list(item.markers),
        "stack": stack,
        "launchable": launchable,
        "launch": launch,
        "docs": docs,
        "scripts": {key: compact(value) for key, value in scripts.items() if key in {"dev", "start", "build", "test", "lint", "preview"}},
        "load": {
            "mode": "source_path",
            "label": "Load version in cockpit",
            "path": item.path.as_posix(),
            "launchable": launchable,
        },
        "has_git": (item.path / ".git").exists(),
        "status": "source_present",
    }


def _branch_from_rel_path(rel_path: str) -> tuple[str, str]:
    parts = [part for part in Path(rel_path).parts if part and part != "."]
    if len(parts) <= 1:
        return "main", "Main"
    if parts[0] == "cosmos-zip-assemblies":
        return "assembled-latest", "Assembled Latest"
    branch_parts = parts[1:-1] if len(parts) > 2 else parts[1:]
    if not branch_parts:
        return "main", "Main"
    label = " / ".join(_label_from_name(part) for part in branch_parts[:3])
    return slug("/".join(branch_parts)), label


def _project_docs(path: Path, *, package_json: Mapping[str, Any], source_root: Path) -> dict[str, Any]:
    docs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for doc_path in _candidate_doc_paths(path):
        try:
            rel_path = doc_path.relative_to(path).as_posix()
        except ValueError:
            rel_path = doc_path.name
        if rel_path in seen:
            continue
        seen.add(rel_path)
        row = _doc_row(path, doc_path, rel_path)
        if row:
            docs.append(row)
        if len(docs) >= 48:
            break
    docs = sorted(docs, key=lambda row: (0 if row.get("primary") else 1, compact(row.get("kind")), compact(row.get("rel_path"))))
    primary = docs[0] if docs else {}
    references = _project_reference_rows(path, package_json=package_json, source_root=source_root)
    return {
        "schema_id": "ion.project_docs.v1",
        "status": "docs_present" if docs else "docs_missing",
        "doc_count": len(docs),
        "reference_count": len(references),
        "primary_doc": primary,
        "docs": docs,
        "references": references,
        "coverage": {
            "has_readme": any(compact(row.get("kind")) == "readme" for row in docs),
            "has_architecture": any(compact(row.get("kind")) == "architecture" for row in docs),
            "has_runbook": any(compact(row.get("kind")) == "runbook" for row in docs),
            "has_reference": any(bool(row.get("reference")) for row in docs) or bool(references),
        },
    }


def _candidate_doc_paths(path: Path) -> list[Path]:
    rows: list[Path] = []
    direct_names = [
        "README.md",
        "README.mdx",
        "README.txt",
        "ARCHITECTURE.md",
        "RUNBOOK.md",
        "QUICKSTART.md",
        "CHANGELOG.md",
        "LICENSE",
    ]
    for name in direct_names:
        candidate = path / name
        if candidate.exists() and candidate.is_file():
            rows.append(candidate)
    for rel_dir in ("docs", "doc", "references", "reference", "notes"):
        doc_dir = path / rel_dir
        if not doc_dir.exists() or not doc_dir.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(doc_dir):
            current = Path(dirpath)
            dirnames[:] = [name for name in dirnames if name not in SCAN_IGNORED_DIRS and not _looks_secret(name)]
            for filename in filenames:
                if _looks_secret(filename):
                    continue
                file_path = current / filename
                if file_path.suffix.lower() in DOC_FILE_EXTENSIONS or filename.lower() in PRIMARY_DOC_NAMES:
                    rows.append(file_path)
            if len(rows) >= 80:
                return rows
    return rows


def _doc_row(root: Path, doc_path: Path, rel_path: str) -> dict[str, Any] | None:
    try:
        stat = doc_path.stat()
    except OSError:
        return None
    lower = rel_path.lower()
    kind = _doc_kind(lower)
    title, excerpt = _doc_title_excerpt(doc_path)
    return {
        "title": title or _label_from_name(Path(rel_path).stem),
        "kind": kind,
        "rel_path": rel_path,
        "path": doc_path.as_posix(),
        "extension": doc_path.suffix.lower() or Path(rel_path).name.lower(),
        "bytes": stat.st_size,
        "primary": Path(rel_path).name.lower() in PRIMARY_DOC_NAMES or rel_path.count("/") == 0 and kind in {"readme", "architecture", "runbook"},
        "reference": any(token in lower for token in REFERENCE_DOC_TOKENS),
        "excerpt": excerpt,
        "source_root": root.as_posix(),
    }


def _doc_kind(lower_rel_path: str) -> str:
    if "readme" in lower_rel_path:
        return "readme"
    if "architecture" in lower_rel_path or "design" in lower_rel_path:
        return "architecture"
    if "runbook" in lower_rel_path or "quickstart" in lower_rel_path or "getting" in lower_rel_path:
        return "runbook"
    if "decision" in lower_rel_path or "/adr" in lower_rel_path or "adr-" in lower_rel_path:
        return "decision"
    if "reference" in lower_rel_path or "api" in lower_rel_path or "schema" in lower_rel_path or "contract" in lower_rel_path:
        return "reference"
    if "source" in lower_rel_path or "authority" in lower_rel_path or "manifest" in lower_rel_path or "registry" in lower_rel_path:
        return "source"
    if "changelog" in lower_rel_path or "release" in lower_rel_path:
        return "changelog"
    if "license" in lower_rel_path:
        return "license"
    return "doc"


def _doc_title_excerpt(path: Path, *, max_chars: int = 520) -> tuple[str, str]:
    if path.suffix.lower() not in {".md", ".mdx", ".txt", ".rst", ".html", ".htm", ""}:
        return "", ""
    try:
        if path.stat().st_size > 400_000:
            return "", ""
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", ""
    return _title_excerpt_from_text(text, max_chars=max_chars)


def _title_excerpt_from_text(text: str, *, max_chars: int = 520) -> tuple[str, str]:
    title = ""
    excerpt_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not title and line.startswith("#"):
            title = line.lstrip("#").strip()
            continue
        if line.startswith("```"):
            continue
        excerpt_lines.append(line)
        if len(" ".join(excerpt_lines)) >= max_chars:
            break
    excerpt = " ".join(excerpt_lines)[:max_chars]
    return title, excerpt


def _project_reference_rows(path: Path, *, package_json: Mapping[str, Any], source_root: Path) -> list[dict[str, Any]]:
    rows = [
        {
            "type": "source_root",
            "label": "Source root",
            "target": path.as_posix(),
            "detail": "Local project root represented by this portfolio row.",
        },
        {
            "type": "source_collection",
            "label": "Source collection",
            "target": source_root.as_posix(),
            "detail": "Parent local source collection for this project root.",
        },
    ]
    repository = package_json.get("repository")
    if isinstance(repository, Mapping):
        repository = repository.get("url")
    for key, label in (("homepage", "Homepage"), ("repository", "Repository"), ("bugs", "Issue tracker")):
        value = repository if key == "repository" else package_json.get(key)
        if isinstance(value, Mapping):
            value = value.get("url")
        if compact(value):
            rows.append({"type": key, "label": label, "target": compact(value), "detail": "Package metadata reference."})
    return rows


def _infer_family(source_id: str, name: str, rel_parts: tuple[str, ...], package_json: Mapping[str, Any]) -> tuple[str, str, str]:
    top = rel_parts[0] if rel_parts else name
    lower_name = name.lower()
    lower_top = top.lower()
    package_name = compact(package_json.get("name"), lower_name).lower()
    text = " ".join([lower_name, lower_top, " ".join(part.lower() for part in rel_parts), package_name])
    base = top
    group_id = _canonical_domain_id(source_id, name, rel_parts, package_json)
    if source_id in {"cosmos", ARCHIVE_SOURCE_ID}:
        if lower_top == "cosmos-zip-assemblies" and len(rel_parts) > 1:
            base = rel_parts[1]
        elif "laser-ilca" in text or "sailboat" in text or " ilca" in f" {text}" or "ilca-" in text:
            base = "sailboat-ilca"
        elif lower_top in {"proflow", "protree", "prorock_soil", "terrain", "volumetrics", "water"}:
            base = top
        elif lower_top in {"earth-forge", "studioearth", "earth_cosmo_", "cosmic-earth-view", "globeview"}:
            base = "earth-forge"
        elif lower_top.startswith("ion_earth_orbital_evo"):
            base = "earth-orbital-evo"
        elif lower_top.startswith("ion_earth_m"):
            base = "earth-milestones"
        elif lower_top.startswith("port-hyper-h2-o") or lower_top.startswith("owm_") or "hyperh2o" in lower_top:
            base = "hyper-h2o"
        elif "earth" in lower_top or "cosmo" in lower_top or "globe" in lower_top:
            base = "earth-forge"
    elif source_id == "application_dev":
        if lower_top == "lucidengine":
            base = "lucid-engine"
        elif lower_top == "claude":
            base = "claude-apps"
        elif lower_top in {"devcompanion", "codexultimate", "bigproject"}:
            base = top
        elif "proflow" in package_name:
            base = "proflow"
    elif source_id == "ion":
        base = "ion-development"
    family_slug = slug(base)
    family_source = "cosmos" if source_id == ARCHIVE_SOURCE_ID else source_id
    return f"{family_source}:{family_slug}", group_id, _label_from_name(base)


def _canonical_domain_id(source_id: str, name: str, rel_parts: tuple[str, ...], package_json: Mapping[str, Any]) -> str:
    top = rel_parts[0].lower() if rel_parts else name.lower()
    text = " ".join(
        [
            name,
            " ".join(rel_parts),
            compact(package_json.get("name")),
            compact(package_json.get("description")),
        ]
    ).lower()
    if source_id == "ion":
        return "ion-platform"
    if source_id in {"cosmos", ARCHIVE_SOURCE_ID} and (
        top.startswith("ion_earth")
        or top in {"earth-forge", "studioearth", "earth_cosmo_", "cosmic-earth-view", "globeview"}
        or top.startswith("port-hyper-h2-o")
    ):
        return "globe-planetary"
    if any(token in text for token in ("lucidengine", "lucid-engine", "lucid engine", "editor", "lasso", "canvas")):
        return "lucid-editor"
    if any(token in text for token in ("proflow", "water", "h2o", "ocean", "splash", "wave", "fluid", "hydro", "owm", "boltwater", "sailboat", "laser-ilca", "ilca")):
        return "water-simulation"
    if any(token in text for token in ("volumetric", "volumetrics", "cloud", "fog", "atmosphere", "sky", "mist")):
        return "clouds-volumetrics"
    if any(token in text for token in ("protree", "tree", "forest", "leaf", "leaves", "canopy", "vegetation", "biome")):
        return "vegetation-trees"
    if any(token in text for token in ("terrain", "prorock", "rock", "soil", "geology", "erosion", "landform")):
        return "terrain-geology"
    if any(token in text for token in ("globe", "earth", "cosmo", "orbital", "planet", "world", "studioearth")):
        return "globe-planetary"
    if any(token in text for token in ("specialeffects", "special effects", "particle", "particles", "effect", "shader")):
        return "visual-effects"
    return "tools-generated-apps"


def _version_tokens(name: str, rel_path: str, package_version: str) -> tuple[str, str, str]:
    haystack = " ".join([name, rel_path, package_version])
    tokens = VERSION_TOKEN_RE.findall(haystack)
    date_tokens = DATE_TOKEN_RE.findall(haystack)
    milestone = next((token.upper().replace("_", "-") for token in tokens if token.lower().startswith("m")), "")
    version_token = tokens[0].replace("_", "-") if tokens else compact(package_version, "snapshot")
    date_token = date_tokens[-1] if date_tokens else ""
    return version_token, date_token, milestone


def _stack(markers: Iterable[str], scripts: Mapping[str, Any]) -> str:
    marker_set = set(markers)
    script_values = " ".join(compact(value).lower() for value in scripts.values())
    if "next.config.mjs" in marker_set or "next.config.js" in marker_set or "next.config.ts" in marker_set or "next" in script_values:
        return "next"
    if any(marker.startswith("vite.config") for marker in marker_set) or "vite" in script_values:
        return "vite"
    if "Cargo.toml" in marker_set:
        return "rust"
    if "pyproject.toml" in marker_set:
        return "python"
    if "package.json" in marker_set:
        return "node"
    return "project"


def _family_rows(projects: list[dict[str, Any]], workspace_dirs: list[dict[str, Any]], materialized_root: Path) -> list[dict[str, Any]]:
    by_family: dict[str, dict[str, Any]] = {}
    for workspace in workspace_dirs:
        family_id = compact(workspace.get("family_id"), "unknown")
        by_family.setdefault(
            family_id,
            {
                "family_id": family_id,
                "group_id": compact(workspace.get("group_id"), "general"),
                "domain_id": compact(workspace.get("group_id"), "tools-generated-apps"),
                "label": compact(workspace.get("label"), family_id),
                "source_ids": set(),
                "workspace_dirs": [],
                "projects": [],
            },
        )
        by_family[family_id]["workspace_dirs"].append(workspace)
        by_family[family_id]["source_ids"].add(compact(workspace.get("source_id"), "unknown"))
    for project in projects:
        family_id = compact(project.get("family_id"), "unknown")
        row = by_family.setdefault(
            family_id,
            {
                "family_id": family_id,
                "group_id": compact(project.get("group_id"), "general"),
                "domain_id": compact(project.get("domain_id"), compact(project.get("group_id"), "tools-generated-apps")),
                "label": compact(project.get("family_label"), family_id),
                "source_ids": set(),
                "workspace_dirs": [],
                "projects": [],
            },
        )
        row["projects"].append(project)
        row["source_ids"].add(compact(project.get("source_id"), "unknown"))
        if row.get("group_id") == "general":
            row["group_id"] = compact(project.get("group_id"), "general")
        if not row.get("domain_id") or row.get("domain_id") == "general":
            row["domain_id"] = compact(project.get("domain_id"), compact(project.get("group_id"), "tools-generated-apps"))
    families: list[dict[str, Any]] = []
    for family_id, row in by_family.items():
        family_projects = sorted(
            row["projects"],
            key=lambda project: (
                _version_sort_rank(project),
                compact(project.get("date_token")),
                compact(project.get("rel_path")),
            ),
        )
        current = family_projects[-1] if family_projects else None
        domain_id = compact(row.get("domain_id"), compact(row.get("group_id"), "tools-generated-apps"))
        domain = DOMAIN_BY_ID.get(domain_id, DOMAIN_BY_ID["tools-generated-apps"])
        project_slug = slug(compact(row.get("label"), family_id), "project")
        organized_path = (materialized_root / "domains" / compact(domain.get("folder"), slug(domain_id)) / project_slug).as_posix()
        versions = []
        for index, project in enumerate(family_projects):
            token = compact(project.get("version_token"), "snapshot")
            version_slug = f"{index + 1:03d}-{slug(token or project.get('project_id'), f'version-{index + 1}')}"
            display_label = _version_display_label(project, index)
            versions.append(
                {
                    "version_id": version_slug,
                    "project_id": project["project_id"],
                    "label": project["label"],
                    "display_label": display_label,
                    "sequence_label": f"v{index + 1:03d}",
                    "version_token": project.get("version_token"),
                    "date_token": project.get("date_token"),
                    "milestone_token": project.get("milestone_token"),
                    "branch_id": project.get("branch_id"),
                    "branch_label": project.get("branch_label"),
                    "path": project.get("path"),
                    "stack": project.get("stack"),
                    "launchable": project.get("launchable"),
                    "is_current": bool(current and project.get("project_id") == current.get("project_id")),
                    "load": {
                        "mode": "source_path",
                        "label": "Load version in cockpit",
                        "path": project.get("path"),
                        "organized_current_source": f"{organized_path}/source/current" if current and project.get("project_id") == current.get("project_id") else "",
                        "organized_version_manifest": f"{organized_path}/lineage/versions/{version_slug}.json",
                        "launchable": project.get("launchable"),
                    },
                    "launch": {
                        **dict(project.get("launch") if isinstance(project.get("launch"), Mapping) else {}),
                        "project_id": project.get("project_id"),
                        "version_id": version_slug,
                        "label": display_label,
                        "project_path": project.get("path"),
                    },
                    "docs": dict(project.get("docs") if isinstance(project.get("docs"), Mapping) else {}),
                }
            )
        branches = _branch_rows(versions)
        diffs = _load_family_diff_rows(organized_path, versions)
        docs = _family_docs_summary(family_projects, versions, organized_path)
        operating_system = _family_operating_system(
            family_id=family_id,
            label=compact(row.get("label"), family_id),
            domain_id=domain_id,
            versions=versions,
            branches=branches,
            diffs=diffs,
            docs=docs,
            projects=family_projects,
            current=current or {},
            organized_path=organized_path,
        )
        families.append(
            {
                "family_id": family_id,
                "group_id": compact(row.get("group_id"), "general"),
                "domain_id": domain_id,
                "domain_label": DOMAIN_BY_ID.get(domain_id, {}).get(
                    "label",
                    _label_from_name(domain_id),
                ),
                "label": compact(row.get("label"), family_id),
                "source_ids": sorted(row["source_ids"]),
                "workspace_dir_count": len(row["workspace_dirs"]),
                "project_count": len(family_projects),
                "version_count": len(versions),
                "branch_count": len(branches),
                "diff_count": len(diffs),
                "launchable_count": len([project for project in family_projects if project.get("launchable")]),
                "doc_count": docs.get("doc_count", 0),
                "reference_count": docs.get("reference_count", 0),
                "current_project_id": current.get("project_id") if current else "",
                "current_path": current.get("path") if current else "",
                "current": current or {},
                "versions": versions,
                "branches": branches,
                "diffs": diffs,
                "docs": docs,
                "operating_system": operating_system,
                "organized_path": organized_path,
                "lineage_status": "version_chain_ready" if len(versions) > 1 else "single_root",
                "materialization_plan": "copy current source only; write version lineage and diff manifests; keep originals untouched",
            }
        )
    return sorted(families, key=lambda family: (compact(family.get("group_id")), compact(family.get("label"))))


def _branch_rows(versions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for version in versions:
        branch_id = compact(version.get("branch_id"), "main")
        row = rows.setdefault(
            branch_id,
            {
                "branch_id": branch_id,
                "label": compact(version.get("branch_label"), "Main"),
                "version_count": 0,
                "launchable_count": 0,
                "latest_version": {},
            },
        )
        row["version_count"] += 1
        if version.get("launchable"):
            row["launchable_count"] += 1
        row["latest_version"] = version
    return sorted(rows.values(), key=lambda row: (0 if row.get("branch_id") == "main" else 1, compact(row.get("label"))))


def _version_display_label(project: Mapping[str, Any], index: int) -> str:
    token = compact(project.get("milestone_token") or project.get("version_token"))
    date_token = compact(project.get("date_token"))
    branch_label = compact(project.get("branch_label"))
    label = compact(project.get("label") or project.get("name") or project.get("project_id"), f"Version {index + 1}")
    if token and token.lower() not in {"0.0.0", "snapshot"}:
        return f"{token} - {label}"
    if date_token:
        return f"{date_token} - {label}"
    if branch_label and branch_label != "Main":
        return f"{branch_label} - {label}"
    return f"v{index + 1:03d} - {label}"


def _version_sort_rank(project: Mapping[str, Any]) -> tuple[int, int, int, int, int]:
    token = compact(project.get("milestone_token") or project.get("version_token") or project.get("package_version"))
    haystack = " ".join(
        [
            token,
            compact(project.get("label")),
            compact(project.get("name")),
            compact(project.get("path")),
            compact(project.get("date_token")),
        ]
    ).lower()
    milestone = re.search(r"\bm(\d+)([a-z]?)\b", haystack, re.IGNORECASE)
    if milestone:
        letter = milestone.group(2).lower()
        return (40, int(milestone.group(1)), ord(letter) - 96 if letter else 0, int(compact(project.get("date_token"), "0") or 0), 0)
    owm = re.search(r"\bowm[-_ ]?(\d+)\b", haystack, re.IGNORECASE)
    if owm:
        return (30, int(owm.group(1)), 0, int(compact(project.get("date_token"), "0") or 0), 0)
    version = re.search(r"\bv(\d+)(?:[._-](\d+))?(?:[._-](\d+))?\b", haystack, re.IGNORECASE)
    if version:
        return (
            20,
            int(version.group(1) or 0),
            int(version.group(2) or 0),
            int(version.group(3) or 0),
            int(compact(project.get("date_token"), "0") or 0),
        )
    semver = re.search(r"\b(\d+)\.(\d+)(?:\.(\d+))?\b", haystack)
    if semver:
        return (
            20,
            int(semver.group(1) or 0),
            int(semver.group(2) or 0),
            int(semver.group(3) or 0),
            int(compact(project.get("date_token"), "0") or 0),
        )
    date_token = compact(project.get("date_token"))
    return (10 if date_token else 0, int(date_token or 0), 0, 0, 0)


def _load_family_diff_rows(organized_path: str, versions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    manifest_path = Path(organized_path) / "lineage" / "DIFF_MANIFEST.json"
    payload = read_json(manifest_path)
    rows = payload.get("diffs") if isinstance(payload.get("diffs"), list) else []
    if rows and _diff_manifest_matches_versions(rows, versions):
        return [dict(row, manifest_path=manifest_path.as_posix()) for row in rows if isinstance(row, Mapping)]
    return [
        {
            **row,
            "manifest_path": manifest_path.as_posix(),
            "file_diff": row.get("file_diff", {"status": "not_materialized"}),
        }
        for row in _version_diff_manifest(versions, include_file_diff=True)
    ]


def _diff_manifest_matches_versions(rows: list[Any], versions: list[dict[str, Any]]) -> bool:
    if len(rows) != max(0, len(versions) - 1):
        return False
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            return False
        previous = versions[index - 1]
        current = versions[index]
        if compact(row.get("from_project_id")) != compact(previous.get("project_id")):
            return False
        if compact(row.get("to_project_id")) != compact(current.get("project_id")):
            return False
    return True


def _family_docs_summary(projects: list[dict[str, Any]], versions: list[dict[str, Any]], organized_path: str) -> dict[str, Any]:
    docs: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    seen_docs: set[str] = set()
    for project in projects:
        project_docs = project.get("docs") if isinstance(project.get("docs"), Mapping) else {}
        for doc in project_docs.get("docs", []) if isinstance(project_docs.get("docs"), list) else []:
            if not isinstance(doc, Mapping):
                continue
            key = compact(doc.get("path") or doc.get("rel_path"))
            if not key or key in seen_docs:
                continue
            seen_docs.add(key)
            docs.append(dict(doc, project_id=project.get("project_id"), project_label=project.get("label")))
        for ref in project_docs.get("references", []) if isinstance(project_docs.get("references"), list) else []:
            if isinstance(ref, Mapping):
                references.append(dict(ref, project_id=project.get("project_id")))
    docs = sorted(docs, key=lambda row: (0 if row.get("primary") else 1, compact(row.get("kind")), compact(row.get("rel_path"))))
    current_version = next((version for version in versions if version.get("is_current")), versions[-1] if versions else {})
    target_docs = [
        {"label": "Project overview", "path": f"{organized_path}/docs/PROJECT_OVERVIEW.md", "status": "candidate_target"},
        {"label": "Architecture", "path": f"{organized_path}/docs/ARCHITECTURE.md", "status": "candidate_target"},
        {"label": "Runbook", "path": f"{organized_path}/docs/RUNBOOK.md", "status": "candidate_target"},
        {"label": "References", "path": f"{organized_path}/docs/REFERENCES.md", "status": "candidate_target"},
        {"label": "Decision log", "path": f"{organized_path}/docs/DECISIONS.md", "status": "candidate_target"},
        {"label": "Version notes", "path": f"{organized_path}/lineage/versions", "status": "candidate_target"},
    ]
    return {
        "schema_id": "ion.project_family_docs.v1",
        "status": "docs_present" if docs else "docs_missing",
        "doc_count": len(docs),
        "reference_count": len(references),
        "documented_version_count": len([version for version in versions if _version_docs(version).get("doc_count", 0)]),
        "current_version_id": current_version.get("version_id") if isinstance(current_version, Mapping) else "",
        "primary_docs": docs[:8],
        "docs": docs[:80],
        "references": references[:40],
        "target_docs": target_docs,
        "coverage": {
            "has_readme": any(compact(row.get("kind")) == "readme" for row in docs),
            "has_architecture": any(compact(row.get("kind")) == "architecture" for row in docs),
            "has_runbook": any(compact(row.get("kind")) == "runbook" for row in docs),
            "has_references": any(bool(row.get("reference")) for row in docs) or bool(references),
        },
    }


def _version_docs(version: Mapping[str, Any]) -> Mapping[str, Any]:
    docs = version.get("docs")
    return docs if isinstance(docs, Mapping) else {}


def _family_operating_system(
    *,
    family_id: str,
    label: str,
    domain_id: str,
    versions: list[dict[str, Any]],
    branches: list[dict[str, Any]],
    diffs: list[dict[str, Any]],
    docs: Mapping[str, Any],
    projects: list[dict[str, Any]],
    current: Mapping[str, Any],
    organized_path: str,
) -> dict[str, Any]:
    version_count = len(versions)
    branch_count = len(branches)
    diff_count = len(diffs)
    launchable_count = len([version for version in versions if version.get("launchable")])
    doc_count = int(docs.get("doc_count") or 0)
    reference_count = int(docs.get("reference_count") or 0)
    coverage = docs.get("coverage") if isinstance(docs.get("coverage"), Mapping) else {}
    has_current = bool(compact(current.get("path")))
    has_version_chain = version_count > 1
    has_materialized_diff = any(
        isinstance(diff.get("file_diff"), Mapping) and compact(diff.get("file_diff", {}).get("status")) == "ready"
        for diff in diffs
    )
    ready_signals = [
        has_current,
        doc_count > 0,
        bool(coverage.get("has_readme")),
        bool(coverage.get("has_architecture")),
        bool(coverage.get("has_references")),
        launchable_count > 0,
        diff_count > 0 or version_count <= 1,
    ]
    score = round(100 * len([signal for signal in ready_signals if signal]) / len(ready_signals))
    if score >= 72:
        posture = "ready"
    elif score >= 38:
        posture = "watch"
    else:
        posture = "blocked"
    lifecycle = [
        _lifecycle_stage("01_inventory", "Inventory", has_current, "Identify source roots, current copy, and domain placement."),
        _lifecycle_stage("02_consolidate", "Consolidate", version_count <= 1 or diff_count > 0, "Convert duplicate full roots into version/diff lineage."),
        _lifecycle_stage("03_document", "Document", doc_count > 0 and bool(coverage.get("has_references")), "Bind docs and references to this project/version."),
        _lifecycle_stage("04_launch", "Launch", launchable_count > 0, "Provide a managed local launch path with repair and stop controls."),
        _lifecycle_stage("05_verify", "Verify", has_materialized_diff or (launchable_count > 0 and doc_count > 0), "Create visual/runtime proof and source-diff proof."),
        _lifecycle_stage("06_maintain", "Maintain", score >= 72, "Keep a repeatable stewardship loop for notes, screenshots, diffs, and releases."),
    ]
    gates = [
        _quality_gate("source_current", "Current Source", has_current, compact(current.get("path"), "missing")),
        _quality_gate("domain_fit", "Domain Fit", domain_id != "tools-generated-apps", domain_id),
        _quality_gate("docs_bound", "Docs Bound", doc_count > 0, f"{doc_count} docs / {reference_count} refs"),
        _quality_gate("launch_path", "Local Launch", launchable_count > 0, f"{launchable_count} launchable versions"),
        _quality_gate("version_lineage", "Version Lineage", version_count <= 1 or diff_count > 0, f"{version_count} versions / {diff_count} diffs"),
        _quality_gate("organizer_target", "Organizer Target", bool(organized_path), organized_path),
        _quality_gate("secret_boundary", "Secret Boundary", True, "copy policy skips secret-looking files"),
    ]
    lanes = [
        _maintenance_lane(
            "source_canon",
            "Source Canon",
            "ready" if has_current else "blocked",
            "Keep one current source path and preserve historical roots as lineage.",
            compact(current.get("path"), "select current source"),
        ),
        _maintenance_lane(
            "docs_references",
            "Docs & References",
            "ready" if doc_count and reference_count else "watch" if doc_count else "blocked",
            "Keep README, architecture, runbook, source authority, and references attached to project/version.",
            "fill missing docs health pills",
        ),
        _maintenance_lane(
            "local_runtime",
            "Local Runtime",
            "ready" if launchable_count else "watch",
            "Use managed launchers that repair dependencies and stop dev servers when app windows close.",
            "verify launch for current version",
        ),
        _maintenance_lane(
            "lineage_diff",
            "Lineage & Diffs",
            "ready" if diff_count else "watch" if version_count > 1 else "ready",
            "Represent evolution as adjacent diff units, not copied full project folders.",
            "materialize diff manifest for adjacent versions" if version_count > 1 else "single root; no diff work needed",
        ),
        _maintenance_lane(
            "quality_proof",
            "Quality Proof",
            "watch",
            "Bind screenshots, notes, runtime proof, and regression observations to exact versions.",
            "attach proof after local launch or visual review",
        ),
        _maintenance_lane(
            "human_workflow",
            "Human Workflow",
            "watch",
            "Support operator triage, favorites, notes, screenshots, quarantine decisions, and release review.",
            "review operating risks and promote next bounded action",
        ),
    ]
    risks = _family_risk_register(
        version_count=version_count,
        branch_count=branch_count,
        diff_count=diff_count,
        launchable_count=launchable_count,
        doc_count=doc_count,
        reference_count=reference_count,
        coverage=coverage,
        has_current=has_current,
    )
    workflows = [
        {"workflow_id": "triage", "label": "Triage", "cadence": "on selection", "trigger": "new or duplicate project appears", "output": "domain/family/version classification"},
        {"workflow_id": "consolidate", "label": "Consolidate", "cadence": "per family", "trigger": "multiple roots or branch folders", "output": "current source plus lineage/diff manifest"},
        {"workflow_id": "launch_review", "label": "Launch Review", "cadence": "per version", "trigger": "launchable source selected", "output": "managed local launch proof and stop behavior"},
        {"workflow_id": "docs_review", "label": "Docs Review", "cadence": "per project", "trigger": "missing docs health gate", "output": "README/architecture/runbook/references attached"},
        {"workflow_id": "operator_review", "label": "Operator Review", "cadence": "after proof", "trigger": "candidate ready for quarantine/promotion", "output": "notes, screenshots, and next bounded action"},
    ]
    next_actions = _family_next_actions(risks, lanes)
    return {
        "schema_id": "ion.project_operating_system.v1",
        "family_id": family_id,
        "label": label,
        "domain_id": domain_id,
        "posture": posture,
        "readiness_score": score,
        "summary": {
            "version_count": version_count,
            "branch_count": branch_count,
            "diff_count": diff_count,
            "launchable_count": launchable_count,
            "doc_count": doc_count,
            "reference_count": reference_count,
            "risk_count": len(risks),
        },
        "lifecycle": lifecycle,
        "maintenance_lanes": lanes,
        "quality_gates": gates,
        "risk_register": risks,
        "human_workflows": workflows,
        "next_actions": next_actions,
        "operating_principles": [
            "one current source copy per project family",
            "historical full folders become lineage references and diff units",
            "docs, notes, screenshots, and launch proof attach to project/version, never a detached bucket",
            "local launches are explicit managed machine actions with stop controls",
            "candidate organizer state is not accepted production state",
        ],
        "authority": {
            "candidate_projection": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def _lifecycle_stage(stage_id: str, label: str, ready: bool, objective: str) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "label": label,
        "status": "ready" if ready else "watch",
        "objective": objective,
    }


def _quality_gate(gate_id: str, label: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "label": label,
        "status": "pass" if passed else "needs_work",
        "evidence": evidence,
    }


def _maintenance_lane(lane_id: str, label: str, status: str, objective: str, next_action: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "status": status,
        "objective": objective,
        "next_action": next_action,
    }


def _family_risk_register(
    *,
    version_count: int,
    branch_count: int,
    diff_count: int,
    launchable_count: int,
    doc_count: int,
    reference_count: int,
    coverage: Mapping[str, Any],
    has_current: bool,
) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    if not has_current:
        risks.append({"risk_id": "current_source_missing", "severity": "high", "title": "Current source missing", "mitigation": "select or materialize one current source root"})
    if version_count > 1 and diff_count == 0:
        risks.append({"risk_id": "version_copy_sprawl", "severity": "high", "title": "Multiple full roots without diff units", "mitigation": "convert adjacent roots into lineage/diff manifests"})
    if branch_count > 3:
        risks.append({"risk_id": "branch_sprawl", "severity": "medium", "title": "Branch/workspace sprawl", "mitigation": "group branches into named maintenance lanes"})
    if launchable_count == 0:
        risks.append({"risk_id": "no_local_launcher", "severity": "medium", "title": "No local launch path", "mitigation": "create or map a managed launcher for the current version"})
    if doc_count == 0:
        risks.append({"risk_id": "documentation_absent", "severity": "high", "title": "No discovered docs", "mitigation": "attach README, architecture, runbook, and references"})
    if doc_count and not coverage.get("has_architecture"):
        risks.append({"risk_id": "architecture_missing", "severity": "medium", "title": "Architecture doc missing", "mitigation": "add architecture notes to project docs target"})
    if reference_count == 0:
        risks.append({"risk_id": "reference_index_missing", "severity": "medium", "title": "Reference index missing", "mitigation": "record source, package, dataset, and external references"})
    return risks[:8]


def _family_next_actions(risks: list[dict[str, Any]], lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for risk in risks[:4]:
        actions.append(
            {
                "action_id": f"resolve_{compact(risk.get('risk_id'), 'risk')}",
                "label": compact(risk.get("title"), "Resolve risk"),
                "lane": "risk",
                "priority": compact(risk.get("severity"), "medium"),
                "detail": compact(risk.get("mitigation"), "Review and resolve risk."),
            }
        )
    for lane in lanes:
        if compact(lane.get("status")) in {"watch", "blocked"}:
            actions.append(
                {
                    "action_id": f"advance_{compact(lane.get('lane_id'), 'lane')}",
                    "label": compact(lane.get("label"), "Advance lane"),
                    "lane": compact(lane.get("lane_id"), "lane"),
                    "priority": "medium",
                    "detail": compact(lane.get("next_action"), "Advance maintenance lane."),
                }
            )
    if not actions:
        actions.append(
            {
                "action_id": "maintain_project_system",
                "label": "Maintain operating loop",
                "lane": "maintenance",
                "priority": "normal",
                "detail": "Keep docs, launch proof, screenshots, and diff manifests current.",
            }
        )
    return actions[:6]


def _group_rows(families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for family in families:
        group_id = compact(family.get("domain_id") or family.get("group_id"), "tools-generated-apps")
        row = groups.setdefault(
            group_id,
            {
                "group_id": group_id,
                "label": DOMAIN_BY_ID.get(group_id, {}).get("label", _label_from_name(group_id.split(":", 1)[-1])),
                "family_count": 0,
                "project_count": 0,
                "launchable_count": 0,
                "versioned_family_count": 0,
            },
        )
        row["family_count"] += 1
        row["project_count"] += int(family.get("project_count") or 0)
        row["launchable_count"] += int(family.get("launchable_count") or 0)
        if int(family.get("version_count") or 0) > 1:
            row["versioned_family_count"] += 1
    return sorted(groups.values(), key=lambda group: compact(group.get("label")))


def _canonical_domain_rows(families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_domain: dict[str, list[dict[str, Any]]] = {}
    for family in families:
        domain_id = compact(family.get("domain_id") or family.get("group_id"), "tools-generated-apps")
        by_domain.setdefault(domain_id, []).append(family)
    for index, domain in enumerate(CANONICAL_DOMAINS):
        domain_id = domain["domain_id"]
        domain_families = sorted(by_domain.get(domain_id, []), key=lambda item: compact(item.get("label")))
        if not domain_families:
            continue
        docs = _domain_docs_summary(domain_families, domain)
        operating_system = _domain_operating_system(domain_families, domain)
        rows.append(
            {
                "domain_id": domain_id,
                "group_id": domain_id,
                "label": domain["label"],
                "summary": domain["summary"],
                "folder": domain["folder"],
                "sort_order": index + 1,
                "family_count": len(domain_families),
                "project_count": sum(int(family.get("project_count") or 0) for family in domain_families),
                "version_count": sum(int(family.get("version_count") or 0) for family in domain_families),
                "branch_count": sum(int(family.get("branch_count") or 0) for family in domain_families),
                "diff_count": sum(int(family.get("diff_count") or 0) for family in domain_families),
                "launchable_count": sum(int(family.get("launchable_count") or 0) for family in domain_families),
                "versioned_family_count": len([family for family in domain_families if int(family.get("version_count") or 0) > 1]),
                "doc_count": docs.get("doc_count", 0),
                "reference_count": docs.get("reference_count", 0),
                "documented_family_count": docs.get("documented_family_count", 0),
                "docs": docs,
                "operating_system": operating_system,
                "families": [
                    {
                        "family_id": family.get("family_id"),
                        "label": family.get("label"),
                        "version_count": family.get("version_count", 0),
                        "branch_count": family.get("branch_count", 0),
                        "diff_count": family.get("diff_count", 0),
                        "project_count": family.get("project_count", 0),
                        "launchable_count": family.get("launchable_count", 0),
                        "doc_count": family.get("doc_count", 0),
                        "reference_count": family.get("reference_count", 0),
                        "ops_posture": (family.get("operating_system") or {}).get("posture") if isinstance(family.get("operating_system"), Mapping) else "",
                        "ops_score": (family.get("operating_system") or {}).get("readiness_score") if isinstance(family.get("operating_system"), Mapping) else 0,
                        "current_path": family.get("current_path"),
                    }
                    for family in domain_families
                ],
            }
        )
    return rows


def _domain_docs_summary(families: list[dict[str, Any]], domain: Mapping[str, Any]) -> dict[str, Any]:
    docs: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    target_docs: list[dict[str, Any]] = []
    for family in families:
        family_docs = family.get("docs") if isinstance(family.get("docs"), Mapping) else {}
        for doc in family_docs.get("primary_docs", []) if isinstance(family_docs.get("primary_docs"), list) else []:
            if isinstance(doc, Mapping):
                docs.append(dict(doc, family_id=family.get("family_id"), family_label=family.get("label")))
        for ref in family_docs.get("references", []) if isinstance(family_docs.get("references"), list) else []:
            if isinstance(ref, Mapping):
                references.append(dict(ref, family_id=family.get("family_id"), family_label=family.get("label")))
        for target_doc in family_docs.get("target_docs", []) if isinstance(family_docs.get("target_docs"), list) else []:
            if isinstance(target_doc, Mapping):
                target_docs.append(dict(target_doc, family_id=family.get("family_id"), family_label=family.get("label")))
    return {
        "schema_id": "ion.project_domain_docs.v1",
        "status": "domain_docs_projected",
        "doc_count": sum(int(family.get("doc_count") or 0) for family in families),
        "reference_count": sum(int(family.get("reference_count") or 0) for family in families),
        "documented_family_count": len([family for family in families if int(family.get("doc_count") or 0) > 0]),
        "top_docs": docs[:18],
        "references": references[:30],
        "target_docs": target_docs[:30],
        "recommended_sections": [
            "Project Overview",
            "Architecture",
            "Runbook",
            "Version Notes",
            "Diff Evolution",
            "Source Authority",
            "References",
            "Screenshots",
            "Operator Review Notes",
        ],
        "source_curation": {
            "domain_label": compact(domain.get("label")),
            "folder": compact(domain.get("folder")),
            "rule": "attach docs and references to domains, projects, and versions; do not keep docs as a separate unrelated tab inventory",
        },
    }


def _domain_operating_system(families: list[dict[str, Any]], domain: Mapping[str, Any]) -> dict[str, Any]:
    family_ops = [family.get("operating_system") for family in families if isinstance(family.get("operating_system"), Mapping)]
    ready = [ops for ops in family_ops if compact(ops.get("posture")) == "ready"]
    watch = [ops for ops in family_ops if compact(ops.get("posture")) == "watch"]
    blocked = [ops for ops in family_ops if compact(ops.get("posture")) == "blocked"]
    scores = [int(ops.get("readiness_score") or 0) for ops in family_ops]
    average_score = round(sum(scores) / len(scores)) if scores else 0
    posture = "ready" if average_score >= 72 else "watch" if average_score >= 38 else "blocked"
    top_risks: list[dict[str, Any]] = []
    for family in families:
        ops = family.get("operating_system") if isinstance(family.get("operating_system"), Mapping) else {}
        for risk in ops.get("risk_register", []) if isinstance(ops.get("risk_register"), list) else []:
            if isinstance(risk, Mapping):
                top_risks.append(dict(risk, family_id=family.get("family_id"), family_label=family.get("label")))
    top_risks = sorted(top_risks, key=lambda item: {"high": 0, "medium": 1, "low": 2}.get(compact(item.get("severity")), 3))[:12]
    board_columns = [
        {
            "column_id": "ready",
            "label": "Ready",
            "count": len(ready),
            "families": _domain_board_families(families, "ready"),
        },
        {
            "column_id": "watch",
            "label": "Watch",
            "count": len(watch),
            "families": _domain_board_families(families, "watch"),
        },
        {
            "column_id": "blocked",
            "label": "Blocked",
            "count": len(blocked),
            "families": _domain_board_families(families, "blocked"),
        },
        {
            "column_id": "launchable",
            "label": "Launchable",
            "count": len([family for family in families if int(family.get("launchable_count") or 0) > 0]),
            "families": [
                {"family_id": family.get("family_id"), "label": family.get("label"), "count": family.get("launchable_count", 0)}
                for family in families
                if int(family.get("launchable_count") or 0) > 0
            ][:10],
        },
        {
            "column_id": "needs_docs",
            "label": "Needs Docs",
            "count": len([family for family in families if int(family.get("doc_count") or 0) == 0]),
            "families": [
                {"family_id": family.get("family_id"), "label": family.get("label"), "count": family.get("doc_count", 0)}
                for family in families
                if int(family.get("doc_count") or 0) == 0
            ][:10],
        },
    ]
    return {
        "schema_id": "ion.project_domain_operating_system.v1",
        "domain_id": compact(domain.get("domain_id")),
        "label": compact(domain.get("label")),
        "posture": posture,
        "average_readiness_score": average_score,
        "family_count": len(families),
        "ready_count": len(ready),
        "watch_count": len(watch),
        "blocked_count": len(blocked),
        "top_risks": top_risks,
        "board_columns": board_columns,
        "maintenance_rhythm": [
            {"cadence": "daily", "label": "Active Build Triage", "focus": "launch failures, notes, screenshots, next action"},
            {"cadence": "weekly", "label": "Lineage Review", "focus": "duplicate roots, version/diff manifests, quarantine candidates"},
            {"cadence": "per milestone", "label": "Release Review", "focus": "docs health, local proof, source authority, export package"},
            {"cadence": "continuous", "label": "Reference Hygiene", "focus": "source links, package metadata, datasets, decisions"},
        ],
        "authority": {
            "candidate_projection": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def _domain_board_families(families: list[dict[str, Any]], posture: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in families:
        ops = family.get("operating_system") if isinstance(family.get("operating_system"), Mapping) else {}
        if compact(ops.get("posture")) != posture:
            continue
        rows.append(
            {
                "family_id": family.get("family_id"),
                "label": family.get("label"),
                "score": ops.get("readiness_score", 0),
                "risk_count": (ops.get("summary") or {}).get("risk_count", 0) if isinstance(ops.get("summary"), Mapping) else 0,
            }
        )
    return rows[:10]


def _duplicate_clusters(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clusters: dict[str, list[dict[str, Any]]] = {}
    for project in projects:
        key = f"{project.get('family_id')}:{slug(project.get('name') or project.get('label'))}"
        clusters.setdefault(key, []).append(project)
    rows: list[dict[str, Any]] = []
    for key, items in clusters.items():
        if len(items) < 2:
            continue
        rows.append(
            {
                "cluster_id": slug(key),
                "family_id": items[0].get("family_id"),
                "label": items[0].get("family_label") or items[0].get("label"),
                "count": len(items),
                "paths": [compact(item.get("path")) for item in items],
                "recommendation": "keep one current source copy and convert the rest into lineage/diff manifests before quarantine",
            }
        )
    return sorted(rows, key=lambda cluster: (-int(cluster.get("count") or 0), compact(cluster.get("label"))))


def _recommendations(families: list[dict[str, Any]], duplicate_clusters: list[dict[str, Any]], target: Path) -> list[dict[str, Any]]:
    rows = [
        {
            "title": "Materialize professional domain/project organizer",
            "detail": f"Write domain/project folders with current source, lineage, notes, screenshots, and diff manifests under {target.as_posix()}.",
            "status": "ready",
        }
    ]
    for family in sorted(families, key=lambda item: int(item.get("version_count") or 0), reverse=True)[:6]:
        if int(family.get("version_count") or 0) <= 1:
            continue
        rows.append(
            {
                "title": f"Collapse {family.get('label')} into a version chain",
                "detail": f"{family.get('version_count')} roots should become one current source plus version manifests.",
                "family_id": family.get("family_id"),
                "status": "candidate",
            }
        )
    return rows


def _copy_source_tree(source: Path, target: Path) -> dict[str, Any]:
    if target.exists():
        return {"copy_status": "already_exists", "files_copied": 0, "bytes_copied": 0, "skipped": ["target_exists"]}
    files_copied = 0
    bytes_copied = 0
    skipped: list[str] = []
    max_file_bytes = 25_000_000
    for dirpath, dirnames, filenames in os.walk(source):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in COPY_IGNORED_DIRS and not _looks_secret(name)]
        try:
            rel = current.relative_to(source)
        except ValueError:
            continue
        dest_dir = target / rel
        dest_dir.mkdir(parents=True, exist_ok=True)
        for filename in filenames:
            if _looks_secret(filename):
                skipped.append((rel / filename).as_posix())
                continue
            source_file = current / filename
            try:
                size = source_file.stat().st_size
            except OSError:
                skipped.append((rel / filename).as_posix())
                continue
            if size > max_file_bytes:
                skipped.append((rel / filename).as_posix())
                continue
            dest_file = dest_dir / filename
            try:
                shutil.copy2(source_file, dest_file)
            except OSError:
                skipped.append((rel / filename).as_posix())
                continue
            files_copied += 1
            bytes_copied += size
            if files_copied >= 6000:
                skipped.append("copy_file_limit_reached")
                return {"copy_status": "partial_file_limit", "files_copied": files_copied, "bytes_copied": bytes_copied, "skipped": skipped[:80]}
    write_json(
        target / ".ion_organizer_copy_policy.json",
        {
            "source": source.as_posix(),
            "copied_at": utc_now(),
            "excluded_dirs": sorted(COPY_IGNORED_DIRS),
            "max_file_bytes": max_file_bytes,
            "secret_file_names_skipped": sorted(SECRET_FILE_NAMES),
        },
    )
    return {"copy_status": "copied", "files_copied": files_copied, "bytes_copied": bytes_copied, "skipped": skipped[:80]}


def _write_family_workspace(family_dir: Path, family: Mapping[str, Any], domain: Mapping[str, Any]) -> None:
    lineage_dir = family_dir / "lineage"
    versions_dir = lineage_dir / "versions"
    diffs_dir = lineage_dir / "diffs"
    docs_dir = family_dir / "docs"
    notes_dir = family_dir / "notes"
    screenshots_dir = family_dir / "screenshots"
    versions_dir.mkdir(parents=True, exist_ok=True)
    diffs_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    for generated_dir in (versions_dir, diffs_dir):
        for generated_file in generated_dir.glob("*.json"):
            try:
                generated_file.unlink()
            except OSError:
                pass
    lines = [
        f"# {compact(family.get('label'), 'Project')} Lineage",
        "",
        f"Domain: {compact(domain.get('label'), 'Project Domain')}",
        "",
        "This is a candidate professional organizer view. Originals remain untouched.",
        "Only `source/current` is a source copy. Historical roots are represented by lineage and diff records.",
        "",
        f"- project_id: `{compact(family.get('family_id'))}`",
        f"- domain_id: `{compact(family.get('domain_id') or family.get('group_id'))}`",
        f"- current_source: `{compact(family.get('current_path'))}`",
        f"- version_count: `{compact(family.get('version_count'), '0')}`",
        "",
        "## Versions",
        "",
    ]
    versions = [version for version in family.get("versions", []) if isinstance(version, Mapping)]
    for index, version in enumerate(versions):
        if not isinstance(version, Mapping):
            continue
        token = compact(version.get("version_token"), "snapshot")
        lines.append(f"- `{token}` {compact(version.get('label'))}: `{compact(version.get('path'))}`")
        version_slug = f"{index + 1:03d}-{slug(token or version.get('project_id'), f'version-{index + 1}')}"
        write_json(versions_dir / f"{version_slug}.json", version)
    diff_rows = _version_diff_manifest(versions)
    write_json(lineage_dir / "VERSIONS.json", {"versions": versions})
    write_json(lineage_dir / "DIFF_MANIFEST.json", {"diffs": diff_rows})
    for row in diff_rows:
        write_json(diffs_dir / f"{compact(row.get('diff_id'), 'diff')}.json", row)
    (lineage_dir / "LINEAGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    _write_diff_plan(lineage_dir / "DIFF_EVOLUTION_PLAN.md", family, diff_rows)
    (docs_dir / "README.md").write_text(
        "\n".join(
            [
                f"# {compact(family.get('label'), 'Project')} Documentation",
                "",
                "Attach documentation to this exact project family. Keep docs with the source lineage instead of in a disconnected global notes bucket.",
                "",
                "## Suggested Files",
                "",
                "- `PROJECT_OVERVIEW.md`",
                "- `ARCHITECTURE.md`",
                "- `RUNBOOK.md`",
                "- `REFERENCES.md`",
                "- `DECISIONS.md`",
                "",
                "## Current Source",
                "",
                f"`{compact(family.get('current_path'))}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docs_dir / "REFERENCES.md").write_text(
        _family_references_markdown(family),
        encoding="utf-8",
    )
    (notes_dir / "README.md").write_text(
        "# Project Notes\n\nAttach notes to this exact project. Use one markdown file per subject, decision, or review.\n",
        encoding="utf-8",
    )
    (screenshots_dir / "README.md").write_text(
        "# Project Screenshots\n\nAttach screenshots for this exact project or version. Keep filenames descriptive.\n",
        encoding="utf-8",
    )
    write_json(
        family_dir / "PROJECT.json",
        {
            **dict(family),
            "domain": {
                "domain_id": compact(domain.get("domain_id")),
                "label": compact(domain.get("label")),
                "folder": compact(domain.get("folder")),
            },
            "workspace_layout": {
                "current_source_copy": "source/current",
                "docs": "docs",
                "lineage": "lineage",
                "notes": "notes",
                "screenshots": "screenshots",
            },
        },
    )


def _version_diff_manifest(versions: list[Mapping[str, Any]], *, include_file_diff: bool = True) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fingerprint_cache: dict[str, dict[str, Any]] = {}
    for index in range(1, len(versions)):
        previous = versions[index - 1]
        current = versions[index]
        previous_token = slug(previous.get("version_token") or previous.get("milestone_token") or previous.get("project_id"), f"v{index}")
        current_token = slug(current.get("version_token") or current.get("milestone_token") or current.get("project_id"), f"v{index + 1}")
        rows.append(
            {
                "diff_id": f"{index:03d}_{previous_token}_to_{current_token}",
                "from_project_id": previous.get("project_id"),
                "to_project_id": current.get("project_id"),
                "from_path": previous.get("path"),
                "to_path": current.get("path"),
                "from_version": previous.get("version_token"),
                "to_version": current.get("version_token"),
                "from_label": previous.get("display_label") or previous.get("label") or previous.get("project_id"),
                "to_label": current.get("display_label") or current.get("label") or current.get("project_id"),
                "from_branch": previous.get("branch_label"),
                "to_branch": current.get("branch_label"),
                "status": "candidate_diff_manifest",
                "copy_policy": "do not copy historical source roots; use this pair as the bounded diff evolution unit",
                "file_diff": _file_diff_summary(
                    compact(previous.get("path")),
                    compact(current.get("path")),
                    fingerprint_cache=fingerprint_cache,
                )
                if include_file_diff
                else {"status": "not_materialized"},
            }
        )
    return rows


def _family_references_markdown(family: Mapping[str, Any]) -> str:
    docs = family.get("docs") if isinstance(family.get("docs"), Mapping) else {}
    references = docs.get("references") if isinstance(docs.get("references"), list) else []
    source_docs = docs.get("docs") if isinstance(docs.get("docs"), list) else []
    lines = [
        f"# {compact(family.get('label'), 'Project')} References",
        "",
        "Candidate reference index generated from local project roots. Originals remain untouched.",
        "",
        "## Source References",
        "",
    ]
    if not references:
        lines.append("- No package or source references projected yet.")
    for ref in references:
        if not isinstance(ref, Mapping):
            continue
        lines.append(f"- {compact(ref.get('label'), compact(ref.get('type'), 'reference'))}: `{compact(ref.get('target'))}`")
    lines.extend(["", "## Discovered Docs", ""])
    if not source_docs:
        lines.append("- No source docs projected yet.")
    for doc in source_docs[:80]:
        if not isinstance(doc, Mapping):
            continue
        lines.append(f"- {compact(doc.get('title'), compact(doc.get('rel_path'), 'doc'))}: `{compact(doc.get('path'))}`")
    return "\n".join(lines) + "\n"


def _file_diff_summary(previous_path: str, current_path: str, *, fingerprint_cache: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    previous = _cached_source_fingerprint(Path(previous_path).expanduser(), fingerprint_cache=fingerprint_cache)
    current = _cached_source_fingerprint(Path(current_path).expanduser(), fingerprint_cache=fingerprint_cache)
    if previous.get("status") != "ok" or current.get("status") != "ok":
        return {
            "status": "not_available",
            "previous_status": previous.get("status"),
            "current_status": current.get("status"),
        }
    previous_files = previous.get("files", {})
    current_files = current.get("files", {})
    if not isinstance(previous_files, Mapping) or not isinstance(current_files, Mapping):
        return {"status": "not_available"}
    previous_keys = set(previous_files)
    current_keys = set(current_files)
    added = sorted(current_keys - previous_keys)
    removed = sorted(previous_keys - current_keys)
    changed = sorted(key for key in previous_keys.intersection(current_keys) if previous_files.get(key) != current_files.get(key))
    return {
        "status": "ready",
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(changed),
        "added_sample": added[:80],
        "removed_sample": removed[:80],
        "changed_sample": changed[:80],
        "previous_file_count": len(previous_keys),
        "current_file_count": len(current_keys),
        "truncated": bool(previous.get("truncated") or current.get("truncated")),
    }


def _cached_source_fingerprint(path: Path, *, fingerprint_cache: dict[str, dict[str, Any]] | None) -> dict[str, Any]:
    if fingerprint_cache is None:
        return _source_fingerprint_any(path)
    try:
        key = path.resolve().as_posix()
    except OSError:
        key = path.as_posix()
    cached = fingerprint_cache.get(key)
    if cached is not None:
        return cached
    fingerprint = _source_fingerprint_any(path)
    fingerprint_cache[key] = fingerprint
    return fingerprint


def _source_fingerprint_any(path: Path, *, max_files: int = 4000, max_hash_bytes: int = 2_000_000) -> dict[str, Any]:
    if path.exists() and path.is_file() and path.suffix.lower() == ".zip":
        return _zip_source_fingerprint_map(path, max_files=max_files)
    return _source_fingerprint_map(path, max_files=max_files, max_hash_bytes=max_hash_bytes)


def _source_fingerprint_map(path: Path, *, max_files: int = 4000, max_hash_bytes: int = 2_000_000) -> dict[str, Any]:
    if not path.exists() or not path.is_dir():
        return {"status": "missing", "files": {}}
    files: dict[str, str] = {}
    truncated = False
    for dirpath, dirnames, filenames in os.walk(path):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in COPY_IGNORED_DIRS and not _looks_secret(name)]
        try:
            rel_dir = current.relative_to(path)
        except ValueError:
            continue
        for filename in filenames:
            if _looks_secret(filename):
                continue
            source_file = current / filename
            try:
                stat = source_file.stat()
            except OSError:
                continue
            rel_file = (rel_dir / filename).as_posix()
            if stat.st_size <= max_hash_bytes:
                try:
                    digest = hashlib.sha256(source_file.read_bytes()).hexdigest()
                except OSError:
                    digest = f"unreadable:{stat.st_size}"
            else:
                digest = f"large:{stat.st_size}"
            files[rel_file] = f"{stat.st_size}:{digest}"
            if len(files) >= max_files:
                truncated = True
                return {"status": "ok", "files": files, "truncated": truncated}
    return {"status": "ok", "files": files, "truncated": truncated}


def _zip_source_fingerprint_map(path: Path, *, max_files: int = 4000) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"status": "missing", "files": {}}
    files: dict[str, str] = {}
    truncated = False
    try:
        with zipfile.ZipFile(path) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            root_name = _zip_common_root(info.filename for info in infos)
            for info in infos:
                rel_file = _zip_entry_rel(info.filename, root_name)
                if not rel_file or _zip_entry_ignored(info.filename, root_name):
                    continue
                files[rel_file] = f"{info.file_size}:crc:{info.CRC:08x}"
                if len(files) >= max_files:
                    truncated = True
                    return {"status": "ok", "files": files, "truncated": truncated}
    except (OSError, zipfile.BadZipFile):
        return {"status": "unreadable_zip", "files": {}}
    return {"status": "ok", "files": files, "truncated": truncated}


def _write_diff_plan(path: Path, family: Mapping[str, Any], diff_rows: list[Mapping[str, Any]]) -> None:
    lines = [
        f"# {compact(family.get('label'), 'Project')} Diff Evolution Plan",
        "",
        "Goal: preserve evolution without storing complete historical project copies in the organized folder.",
        "",
        "## Rules",
        "",
        "- `source/current` is the only copied source tree.",
        "- Prior roots remain referenced by path until a bounded migration converts them into patch artifacts.",
        "- Each adjacent version pair below is a diff unit, not a folder to copy.",
        "",
        "## Diff Units",
        "",
    ]
    if not diff_rows:
        lines.append("- No version diff units projected for this project yet.")
    for row in diff_rows:
        lines.append(f"- `{compact(row.get('diff_id'))}`")
        lines.append(f"  - from: `{compact(row.get('from_path'))}`")
        lines.append(f"  - to: `{compact(row.get('to_path'))}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_portfolio_readme(target: Path, portfolio: Mapping[str, Any]) -> None:
    summary = portfolio.get("summary") if isinstance(portfolio.get("summary"), Mapping) else {}
    lines = [
        "# ION Projects Professional Organized Candidate",
        "",
        "This folder is a non-destructive professional organization of local project roots.",
        "Original Cosmos, Application_Dev, and ION folders were not moved or deleted.",
        "",
        "## Summary",
        "",
        f"- canonical domains: {summary.get('canonical_domain_count', summary.get('group_count', 0))}",
        f"- project roots: {summary.get('project_root_count', 0)}",
        f"- project families: {summary.get('family_count', 0)}",
        f"- versioned projects: {summary.get('versioned_family_count', 0)}",
        "",
        "## Policy",
        "",
        "- `domains/<domain>/<project>/source/current` contains the only copied source tree for a project.",
        "- `domains/<domain>/<project>/lineage` preserves version pointers and diff evolution units.",
        "- `domains/<domain>/<project>/notes` stores notes for that exact project.",
        "- `domains/<domain>/<project>/screenshots` stores screenshots for that exact project.",
        "- Historical project roots are not copied as full duplicate folders.",
        "- Runtime installs, build outputs, raw data, proof folders, receipts, git internals, and secret-looking files are skipped.",
    ]
    (target / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_materialization_receipt(shell_root: Path, target: Path, portfolio: Mapping[str, Any], copies: list[dict[str, Any]]) -> Path:
    receipt = {
        "schema_id": "ion.project_portfolio_materialization_receipt.v1",
        "created_at": utc_now(),
        "target": target.as_posix(),
        "manifest_path": (shell_root / PORTFOLIO_MANIFEST).as_posix(),
        "copy_count": len(copies),
        "family_count": portfolio.get("summary", {}).get("family_count", 0),
        "project_root_count": portfolio.get("summary", {}).get("project_root_count", 0),
        "copies": copies,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = shell_root / PORTFOLIO_RECEIPTS_DIR / f"{stamp}_project_portfolio_materialization_receipt.json"
    write_json(path, receipt)
    return path


def _latest_materialization_receipt(shell_root: Path) -> dict[str, Any]:
    receipt_dir = shell_root / PORTFOLIO_RECEIPTS_DIR
    try:
        candidates = sorted(receipt_dir.glob("*_project_portfolio_materialization_receipt.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    except OSError:
        candidates = []
    if not candidates:
        return {}
    path = candidates[0]
    payload = read_json(path)
    relpath = ""
    try:
        relpath = path.relative_to(shell_root).as_posix()
    except ValueError:
        relpath = path.as_posix()
    return {
        "path": path.as_posix(),
        "relpath": relpath,
        "created_at": payload.get("created_at"),
        "target": payload.get("target"),
        "copy_count": payload.get("copy_count"),
        "family_count": payload.get("family_count"),
        "project_root_count": payload.get("project_root_count"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _looks_secret(name: str) -> bool:
    lower = name.lower()
    if lower in SECRET_FILE_NAMES:
        return True
    return "secret" in lower or "credential" in lower or lower.endswith(".pem") or lower.endswith(".key")


def _label_from_name(value: Any) -> str:
    text = compact(value, "Project").replace("_", " ").replace("-", " ").replace("/", " ")
    words = [word for word in text.split() if word]
    if not words:
        return "Project"
    return " ".join(word if word.isupper() else word[:1].upper() + word[1:] for word in words)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build or materialize the ION project portfolio catalog.")
    parser.add_argument("--root", default=".", help="Active ION root.")
    parser.add_argument("--target", default="", help="Materialized candidate organizer folder.")
    parser.add_argument("--materialize", action="store_true", help="Create the candidate organizer folder.")
    args = parser.parse_args(argv)
    if args.materialize:
        result = materialize_project_portfolio(args.root, target=args.target or None)
    else:
        root = Path(args.root).expanduser().resolve()
        result = build_project_portfolio_model(root)
        write_json(root / PORTFOLIO_MANIFEST, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
