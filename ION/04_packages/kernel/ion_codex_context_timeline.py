"""Read-only Codex context timeline projection for the cockpit.

This model makes the Codex Mini/Capsule/Long Horizon context substrate visible
as a diffable timeline.  It does not grant production, live execution,
accepted-state, secrets, or hidden-reasoning authority.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.codex_context_timeline.v1"
READY_VERDICT = "ION_CODEX_CONTEXT_TIMELINE_READY"
DEGRADED_VERDICT = "ION_CODEX_CONTEXT_TIMELINE_DEGRADED"

CURRENT = Path("ION/05_context/current")
SOLO_DIR = CURRENT / "codex_solo"
HISTORY_DIR = SOLO_DIR / "history"
HOOK_RUNTIME_ROOT = CURRENT / "codex_cli/hooks/runtime"

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "hidden_reasoning_exposed": False,
}

SURFACE_DEFS: tuple[dict[str, str], ...] = (
    {
        "surface_id": "mini",
        "label": "Mini",
        "path": "ION/05_context/current/codex_solo/MINI.md",
        "role": "lookup and receipt index",
        "format": "markdown",
        "lane": "short horizon",
    },
    {
        "surface_id": "capsule",
        "label": "Capsule",
        "path": "ION/05_context/current/codex_solo/CAPSULE.md",
        "role": "minimum working context",
        "format": "markdown",
        "lane": "minimum context",
    },
    {
        "surface_id": "hot_context",
        "label": "Hot Context",
        "path": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "role": "compiled boot and work context",
        "format": "markdown",
        "lane": "boot window",
    },
    {
        "surface_id": "long_horizon",
        "label": "Long Horizon",
        "path": "ION/05_context/current/codex_solo/LONG_HORIZON.json",
        "role": "compressed long-horizon capsule index",
        "format": "json",
        "lane": "long horizon",
    },
    {
        "surface_id": "route",
        "label": "Route",
        "path": "ION/05_context/current/codex_solo/ROUTE.json",
        "role": "context route and required refs",
        "format": "json",
        "lane": "route proof",
    },
    {
        "surface_id": "context_packages",
        "label": "Packages",
        "path": "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        "role": "context package selector",
        "format": "json",
        "lane": "package selection",
    },
    {
        "surface_id": "status",
        "label": "Status",
        "path": "ION/05_context/current/codex_solo/STATUS.json",
        "role": "codex solo status and latest settlement",
        "format": "json",
        "lane": "status",
    },
    {
        "surface_id": "carrier_limits",
        "label": "Carrier Limits",
        "path": "ION/05_context/current/codex_solo/CODEX_CARRIER_LIMITS_CONTEXT.json",
        "role": "current Codex carrier limit context",
        "format": "json",
        "lane": "limits",
    },
    {
        "surface_id": "candidate_capsule",
        "label": "Candidate YAML",
        "path": "ION/05_context/current/codex_solo/ION_CONTEXT_CAPSULE.candidate.yaml",
        "role": "candidate context capsule witness",
        "format": "yaml",
        "lane": "candidate witness",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file() and (path.parent / "pyproject.toml").is_file():
            return path.parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _read_text(path: Path, *, max_chars: int = 360_000) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n...[truncated for cockpit context timeline]"


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iso_mtime(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()


def _compact_line(value: Any, *, limit: int = 240) -> str:
    clean = re.sub(r"\s+", " ", str(value or "")).strip()
    return clean[:limit]


def _json_dumps(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)


def _canonical_json_or_text(path: Path, text: str) -> str:
    parsed = _read_json(path)
    if parsed is None:
        return text
    return _json_dumps(parsed)


def _tail_text(text: str, *, max_lines: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:]) if len(lines) > max_lines else text


def _summary_for_text(surface_id: str, text: str, parsed: Any | None) -> dict[str, Any]:
    if surface_id == "mini":
        lines = text.splitlines()
        lookup_rows = [line for line in lines if line.strip().startswith("- C-")]
        latest = next((line for line in lines if line.startswith("LAST_RECEIPT:")), "")
        return {
            "lookup_rows": len(lookup_rows),
            "latest_receipt": _compact_line(latest.replace("LAST_RECEIPT:", "")),
        }
    if surface_id == "capsule":
        rows = [line for line in text.splitlines() if line.lstrip().startswith("| C-")]
        return {
            "capsule_rows": len(rows),
            "latest_row": _compact_line(rows[-1] if rows else ""),
        }
    if surface_id == "long_horizon" and isinstance(parsed, Mapping):
        epochs = parsed.get("epochs") if isinstance(parsed.get("epochs"), list) else parsed.get("latest_epochs")
        return {
            "epoch_count": parsed.get("epoch_count", len(epochs) if isinstance(epochs, list) else 0),
            "capsule_entry_count": parsed.get("capsule_entry_count"),
        }
    if surface_id == "route" and isinstance(parsed, Mapping):
        entries = parsed.get("entries") if isinstance(parsed.get("entries"), list) else []
        missing = parsed.get("findings") if isinstance(parsed.get("findings"), list) else []
        return {
            "entry_count": len(entries),
            "missing_or_findings": len(missing),
            "required_count": sum(1 for entry in entries if isinstance(entry, Mapping) and entry.get("required")),
        }
    if surface_id == "context_packages" and isinstance(parsed, Mapping):
        packages = parsed.get("packages") if isinstance(parsed.get("packages"), list) else []
        selected = parsed.get("selected_by_default") if isinstance(parsed.get("selected_by_default"), list) else []
        return {
            "package_count": parsed.get("package_count", len(packages)),
            "selected_count": len(selected),
        }
    if isinstance(parsed, Mapping):
        return {
            "key_count": len(parsed),
            "keys": list(parsed.keys())[:10],
        }
    return {
        "non_empty_lines": len([line for line in text.splitlines() if line.strip()]),
    }


def _current_surface(shell_root: Path, surface: Mapping[str, str]) -> dict[str, Any]:
    surface_id = surface["surface_id"]
    rel_path = surface["path"]
    path = shell_root / rel_path
    exists = path.is_file()
    text = _read_text(path)
    parsed = _read_json(path)
    comparable = _current_comparable_text(surface_id, rel_path, path, text, parsed)
    line_count = len(text.splitlines()) if text else 0
    return {
        "surface_id": surface_id,
        "label": surface["label"],
        "path": rel_path,
        "role": surface["role"],
        "format": surface["format"],
        "lane": surface["lane"],
        "exists": exists,
        "bytes": path.stat().st_size if exists else 0,
        "line_count": line_count,
        "mtime": _iso_mtime(path),
        "sha256": _sha256_file(path),
        "compare_sha256": _sha256_text(comparable) if comparable else None,
        "compare_line_count": len(comparable.splitlines()) if comparable else 0,
        "summary": _summary_for_text(surface_id, text, parsed),
        "excerpt": _tail_text(text, max_lines=42)[:12_000],
        "full_text_path": rel_path,
        "copy_ready": exists,
        "comparison_basis": _comparison_basis(surface_id),
        "_compare_text": comparable,
    }


def _comparison_basis(surface_id: str) -> str:
    if surface_id == "capsule":
        return "capsule tail window"
    if surface_id == "hot_context":
        return "hot context metadata"
    if surface_id in {"route", "context_packages", "long_horizon", "status", "carrier_limits"}:
        return "canonical json projection"
    return "text"


def _current_comparable_text(surface_id: str, rel_path: str, path: Path, text: str, parsed: Any | None) -> str:
    if not path.is_file():
        return ""
    if surface_id == "capsule":
        return _tail_text(text, max_lines=80)
    if surface_id == "hot_context":
        return _json_dumps({"ok": True, "path": rel_path, "bytes": path.stat().st_size})
    if surface_id in {"long_horizon", "route", "context_packages", "status", "carrier_limits"}:
        return _json_dumps(parsed) if parsed is not None else text
    return text


def _snapshot_files(shell_root: Path, *, limit: int) -> list[Path]:
    history_root = shell_root / HISTORY_DIR
    if not history_root.is_dir():
        return []
    files = sorted(history_root.glob("codex_solo_post_*.json"))
    return files[-limit:]


def _snapshot_created_at(path: Path, data: Mapping[str, Any]) -> str:
    created = data.get("created_at")
    if isinstance(created, str) and created:
        return created
    match = re.search(r"codex_solo_post_(\d{8}T\d{6})\+0000", path.name)
    if match:
        stamp = match.group(1)
        return f"{stamp[0:4]}-{stamp[4:6]}-{stamp[6:8]}T{stamp[9:11]}:{stamp[11:13]}:{stamp[13:15]}+00:00"
    return _iso_mtime(path) or _now()


def _snapshot_surface_text(surface_id: str, model: Mapping[str, Any]) -> str:
    value = model.get(surface_id)
    if surface_id == "mini" and isinstance(value, Mapping):
        return str(value.get("text") or "")
    if surface_id == "capsule" and isinstance(value, Mapping):
        tail = value.get("tail")
        if isinstance(tail, list):
            return "\n".join(str(line) for line in tail)
        recent_rows = value.get("recent_rows")
        if isinstance(recent_rows, list):
            return _json_dumps(recent_rows)
    if surface_id == "hot_context" and isinstance(value, Mapping):
        return _json_dumps({key: value.get(key) for key in ("ok", "path", "bytes")})
    if surface_id in {"long_horizon", "route", "context_packages"} and isinstance(value, Mapping):
        return _json_dumps(value)
    if surface_id == "status":
        status = model.get("status")
        return _json_dumps(status) if status is not None else ""
    if isinstance(value, Mapping):
        return _json_dumps(value)
    if isinstance(value, str):
        return value
    return ""


def _surface_summary_from_snapshot(surface_id: str, model: Mapping[str, Any], text_value: str) -> dict[str, Any]:
    value = model.get(surface_id)
    if isinstance(value, Mapping):
        if surface_id == "capsule":
            return {
                "capsule_rows": value.get("entry_count"),
                "tail_lines": len(value.get("tail", [])) if isinstance(value.get("tail"), list) else None,
                "recent_rows": len(value.get("recent_rows", [])) if isinstance(value.get("recent_rows"), list) else None,
            }
        if surface_id == "long_horizon":
            return {
                "epoch_count": value.get("epoch_count"),
                "capsule_entry_count": value.get("capsule_entry_count"),
            }
        if surface_id == "context_packages":
            return {
                "package_count": value.get("package_count"),
                "selected_count": len(value.get("selected_by_default", [])) if isinstance(value.get("selected_by_default"), list) else None,
            }
        if surface_id == "route":
            return {
                "route_ok": value.get("ok"),
                "entry_count": len(value.get("entries", [])) if isinstance(value.get("entries"), list) else None,
                "finding_count": len(value.get("findings", [])) if isinstance(value.get("findings"), list) else None,
            }
        return {key: value.get(key) for key in list(value.keys())[:8] if isinstance(value.get(key), (str, int, float, bool)) or value.get(key) is None}
    return _summary_for_text(surface_id, text_value, None)


def _load_snapshot(path: Path, shell_root: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, Mapping):
        return None
    model = data.get("model") if isinstance(data.get("model"), Mapping) else {}
    surfaces: dict[str, dict[str, Any]] = {}
    for surface in SURFACE_DEFS:
        surface_id = surface["surface_id"]
        text_value = _snapshot_surface_text(surface_id, model)
        surfaces[surface_id] = {
            "surface_id": surface_id,
            "available": bool(text_value),
            "sha256": _sha256_text(text_value) if text_value else None,
            "line_count": len(text_value.splitlines()) if text_value else 0,
            "text": text_value,
            "summary": _surface_summary_from_snapshot(surface_id, model, text_value),
        }
    return {
        "checkpoint_id": str(data.get("checkpoint_id") or path.stem),
        "capsule_entry_id": str(data.get("capsule_entry_id") or ""),
        "created_at": _snapshot_created_at(path, data),
        "status": str(data.get("status") or ""),
        "summary": _compact_line(data.get("summary"), limit=520),
        "evidence_paths": [str(item) for item in data.get("evidence_paths", [])[:8]] if isinstance(data.get("evidence_paths"), list) else [],
        "path": path.relative_to(shell_root).as_posix() if path.is_relative_to(shell_root) else path.as_posix(),
        "bytes": path.stat().st_size,
        "production_authority": bool(data.get("production_authority")),
        "live_execution_authority": bool(data.get("live_execution_authority")),
        "surfaces": surfaces,
    }


def _diff_record(surface: Mapping[str, str], before_text: str, after_text: str, *, before_ref: str, after_ref: str) -> dict[str, Any] | None:
    if not before_text and not after_text:
        return None
    before_sha = _sha256_text(before_text) if before_text else None
    after_sha = _sha256_text(after_text) if after_text else None
    changed = before_sha != after_sha
    if not changed:
        return {
            "surface_id": surface["surface_id"],
            "label": surface["label"],
            "changed": False,
            "before_sha256": before_sha,
            "after_sha256": after_sha,
            "added_lines": 0,
            "removed_lines": 0,
            "line_delta": 0,
            "diff_excerpt": "",
            "diff_truncated": False,
            "before_ref": before_ref,
            "after_ref": after_ref,
            "basis": _comparison_basis(surface["surface_id"]),
        }
    before_lines = before_text.splitlines()
    after_lines = after_text.splitlines()
    diff_lines = list(difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=before_ref,
        tofile=after_ref,
        lineterm="",
        n=4,
    ))
    added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
    max_lines = 220
    excerpt_lines = diff_lines[:max_lines]
    truncated = len(diff_lines) > max_lines
    if truncated:
        excerpt_lines.append(f"...[diff truncated: {len(diff_lines) - max_lines} more lines]")
    return {
        "surface_id": surface["surface_id"],
        "label": surface["label"],
        "changed": True,
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "added_lines": added,
        "removed_lines": removed,
        "line_delta": len(after_lines) - len(before_lines),
        "diff_line_count": len(diff_lines),
        "diff_excerpt": "\n".join(excerpt_lines),
        "diff_truncated": truncated,
        "before_ref": before_ref,
        "after_ref": after_ref,
        "basis": _comparison_basis(surface["surface_id"]),
    }


def _surface_diffs(
    before_surfaces: Mapping[str, Mapping[str, Any]],
    after_surfaces: Mapping[str, Mapping[str, Any]],
    *,
    before_ref: str,
    after_ref: str,
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for surface in SURFACE_DEFS:
        surface_id = surface["surface_id"]
        before_text = str(before_surfaces.get(surface_id, {}).get("text") or "")
        after_text = str(after_surfaces.get(surface_id, {}).get("text") or "")
        record = _diff_record(surface, before_text, after_text, before_ref=before_ref, after_ref=after_ref)
        if record and record.get("changed"):
            changes.append(record)
    return changes


def _timeline_events(snapshots: list[dict[str, Any]], current_surfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for snapshot in snapshots:
        if previous is None:
            changes = []
        else:
            changes = _surface_diffs(
                previous["surfaces"],
                snapshot["surfaces"],
                before_ref=previous["checkpoint_id"],
                after_ref=snapshot["checkpoint_id"],
            )
        events.append(_checkpoint_event(snapshot, changes, baseline=previous is None))
        previous = snapshot
    current_map = {
        str(surface["surface_id"]): {
            "text": str(surface.get("_compare_text") or ""),
            "sha256": surface.get("compare_sha256"),
            "line_count": surface.get("compare_line_count"),
            "summary": surface.get("summary"),
        }
        for surface in current_surfaces
    }
    if previous is not None:
        changes = _surface_diffs(
            previous["surfaces"],
            current_map,
            before_ref=previous["checkpoint_id"],
            after_ref="current filesystem",
        )
        if changes:
            events.append({
                "event_id": "current_context_drift",
                "event_type": "current_context_drift",
                "created_at": _now(),
                "checkpoint_id": "current filesystem",
                "capsule_entry_id": "",
                "status": "CURRENT_FILESYSTEM_DIFF",
                "summary": "Current context files differ from the latest codex_solo checkpoint sample.",
                "evidence_paths": [str(surface.get("path")) for surface in current_surfaces if surface.get("exists")],
                "surface_changes": changes,
                "changed_surface_count": len(changes),
                "added_lines": sum(int(change.get("added_lines") or 0) for change in changes),
                "removed_lines": sum(int(change.get("removed_lines") or 0) for change in changes),
                "authority": dict(AUTHORITY_FALSE),
            })
    return list(reversed(events))


def _checkpoint_event(snapshot: Mapping[str, Any], changes: list[dict[str, Any]], *, baseline: bool) -> dict[str, Any]:
    return {
        "event_id": str(snapshot.get("checkpoint_id")),
        "event_type": "context_checkpoint",
        "created_at": snapshot.get("created_at"),
        "checkpoint_id": snapshot.get("checkpoint_id"),
        "capsule_entry_id": snapshot.get("capsule_entry_id"),
        "status": snapshot.get("status"),
        "summary": snapshot.get("summary"),
        "path": snapshot.get("path"),
        "bytes": snapshot.get("bytes"),
        "evidence_paths": snapshot.get("evidence_paths", []),
        "surface_changes": changes,
        "changed_surface_count": len(changes),
        "added_lines": sum(int(change.get("added_lines") or 0) for change in changes),
        "removed_lines": sum(int(change.get("removed_lines") or 0) for change in changes),
        "baseline": baseline,
        "production_authority": False,
        "live_execution_authority": False,
        "authority": dict(AUTHORITY_FALSE),
    }


def _context_boundaries(shell_root: Path, *, limit: int = 28) -> list[dict[str, Any]]:
    runtime_root = shell_root / HOOK_RUNTIME_ROOT
    if not runtime_root.is_dir():
        return []
    paths = [path for path in runtime_root.rglob("*") if path.is_file()]
    paths.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    records: list[dict[str, Any]] = []
    boundary_words = ("compact", "truncate", "capsule", "mini", "context")
    for path in paths[:240]:
        rel = path.relative_to(shell_root).as_posix()
        haystack = rel.lower()
        text_excerpt = ""
        if not any(word in haystack for word in boundary_words):
            try:
                text_excerpt = _read_text(path, max_chars=2400)
            except Exception:
                text_excerpt = ""
            haystack = f"{haystack}\n{text_excerpt.lower()}"
        if not any(word in haystack for word in boundary_words):
            continue
        if not text_excerpt:
            text_excerpt = _read_text(path, max_chars=48_000)
        records.append({
            "event_id": f"context_boundary_{len(records) + 1}",
            "event_type": "context_boundary",
            "path": rel,
            "hook": path.parent.name,
            "mtime": _iso_mtime(path),
            "bytes": path.stat().st_size,
            "summary": _receipt_summary(text_excerpt, fallback=rel),
        })
        if len(records) >= limit:
            break
    return records


def _first_meaningful_line(value: str) -> str:
    for line in value.splitlines():
        clean = line.strip()
        if clean and not clean.startswith("{") and not clean.startswith("["):
            return clean
    return ""


def _receipt_summary(value: str, *, fallback: str) -> str:
    try:
        data = json.loads(value)
    except Exception:
        return _compact_line(_first_meaningful_line(value) or fallback, limit=260)
    if not isinstance(data, Mapping):
        return _compact_line(fallback, limit=260)
    for key in (
        "summary",
        "event_name",
        "event",
        "hook_event",
        "lifecycle_event",
        "status",
        "verdict",
        "mini_ref",
        "capsule_ref",
        "checkpoint_id",
    ):
        if data.get(key):
            return _compact_line(f"{key}: {data.get(key)}", limit=260)
    payload = data.get("payload")
    if isinstance(payload, Mapping):
        for key in ("summary", "event", "type", "status", "message"):
            if payload.get(key):
                return _compact_line(f"{key}: {payload.get(key)}", limit=260)
    payload_summary = data.get("payload_summary")
    if isinstance(payload_summary, Mapping):
        hook = payload_summary.get("hook_event_name") or data.get("event_name")
        trigger = payload_summary.get("trigger")
        model = payload_summary.get("model")
        if hook or trigger or model:
            return _compact_line(f"{hook or 'context hook'} / {trigger or 'trigger'} / {model or 'model unknown'}", limit=260)
    return _compact_line(fallback, limit=260)


def _context_topology(shell_root: Path) -> dict[str, Any]:
    route = _read_json(shell_root / SOLO_DIR / "ROUTE.json")
    packages = _read_json(shell_root / SOLO_DIR / "CONTEXT_PACKAGES.json")
    route_entries = route.get("entries", []) if isinstance(route, Mapping) and isinstance(route.get("entries"), list) else []
    package_rows = packages.get("packages", []) if isinstance(packages, Mapping) and isinstance(packages.get("packages"), list) else []
    required = [entry for entry in route_entries if isinstance(entry, Mapping) and entry.get("required")]
    missing = [
        entry for entry in route_entries
        if isinstance(entry, Mapping) and entry.get("required") and entry.get("exists") is False
    ]
    selected = packages.get("selected_by_default", []) if isinstance(packages, Mapping) and isinstance(packages.get("selected_by_default"), list) else []
    return {
        "schema_id": "ion.codex_context_topology.v1",
        "route_path": (SOLO_DIR / "ROUTE.json").as_posix(),
        "package_path": (SOLO_DIR / "CONTEXT_PACKAGES.json").as_posix(),
        "route_entry_count": len(route_entries),
        "required_route_ref_count": len(required),
        "missing_required_route_ref_count": len(missing),
        "package_count": len(package_rows),
        "selected_package_count": len(selected),
        "selected_packages": selected[:16],
        "route_entries": route_entries[:28],
        "packages": package_rows[:20],
        "findings": route.get("findings", []) if isinstance(route, Mapping) and isinstance(route.get("findings"), list) else [],
    }


def _lanes(events: list[dict[str, Any]], current_surfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for surface in current_surfaces:
        surface_id = str(surface.get("surface_id"))
        lane_events: list[dict[str, Any]] = []
        for event in events:
            for change in event.get("surface_changes", []) if isinstance(event.get("surface_changes"), list) else []:
                if isinstance(change, Mapping) and change.get("surface_id") == surface_id:
                    lane_events.append({
                        "event_id": event.get("event_id"),
                        "created_at": event.get("created_at"),
                        "checkpoint_id": event.get("checkpoint_id"),
                        "added_lines": change.get("added_lines", 0),
                        "removed_lines": change.get("removed_lines", 0),
                        "line_delta": change.get("line_delta", 0),
                        "basis": change.get("basis"),
                    })
        lanes.append({
            "surface_id": surface_id,
            "label": surface.get("label"),
            "role": surface.get("role"),
            "lane": surface.get("lane"),
            "path": surface.get("path"),
            "exists": surface.get("exists"),
            "sha256": surface.get("sha256"),
            "change_count": len(lane_events),
            "latest_event": lane_events[0] if lane_events else None,
            "events": lane_events[:12],
        })
    return lanes


def _strip_private_surface_fields(surface: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in surface.items() if not key.startswith("_")}


def build_codex_context_timeline_model(root: str | Path | None = None, *, history_limit: int = 36) -> dict[str, Any]:
    """Build the read-only Codex context timeline model."""
    shell_root = _resolve_shell_root(root)
    safe_history_limit = max(4, min(int(history_limit), 80))
    current_surfaces = [_current_surface(shell_root, surface) for surface in SURFACE_DEFS]
    snapshot_paths = _snapshot_files(shell_root, limit=safe_history_limit)
    snapshots = [snapshot for path in snapshot_paths if (snapshot := _load_snapshot(path, shell_root)) is not None]
    events = _timeline_events(snapshots, current_surfaces)
    changed_events = [event for event in events if int(event.get("changed_surface_count") or 0) > 0]
    boundaries = _context_boundaries(shell_root)
    topology = _context_topology(shell_root)
    surface_records = [_strip_private_surface_fields(surface) for surface in current_surfaces]
    missing_surfaces = [surface for surface in surface_records if not surface.get("exists")]
    verdict = READY_VERDICT if not missing_surfaces else DEGRADED_VERDICT

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": verdict == READY_VERDICT,
        "shell_root": shell_root.as_posix(),
        "context_root": (shell_root / SOLO_DIR).as_posix(),
        "history_root": (shell_root / HISTORY_DIR).as_posix(),
        "north_star": "Show Codex context as a living, diffable system: current surfaces, historical checkpoints, context boundaries, route topology, and package selection.",
        "summary": {
            "surface_count": len(surface_records),
            "existing_surface_count": len(surface_records) - len(missing_surfaces),
            "missing_surface_count": len(missing_surfaces),
            "history_snapshot_count": len(snapshots),
            "history_snapshot_limit": safe_history_limit,
            "timeline_event_count": len(events),
            "diff_event_count": len(changed_events),
            "boundary_event_count": len(boundaries),
            "changed_surface_count": len({change.get("surface_id") for event in changed_events for change in event.get("surface_changes", []) if isinstance(change, Mapping)}),
            "route_entry_count": topology.get("route_entry_count", 0),
            "context_package_count": topology.get("package_count", 0),
            "missing_required_route_ref_count": topology.get("missing_required_route_ref_count", 0),
        },
        "surfaces": surface_records,
        "lanes": _lanes(events, current_surfaces),
        "timeline": events,
        "boundaries": boundaries,
        "topology": topology,
        "visibility_contract": {
            "visible": [
                "Mini/Capsule/Hot/Long Horizon current surface fingerprints and excerpts",
                "codex_solo checkpoint summaries",
                "diff excerpts between sampled checkpoints",
                "context route/package topology",
                "context boundary hook receipts when present",
            ],
            "not_visible": [
                "private internal reasoning text",
                "secret values or credentials",
                "accepted-state claims without receipts",
                "raw external Codex session transcripts",
            ],
            **AUTHORITY_FALSE,
        },
        "findings": [f"Missing context surface: {surface.get('path')}" for surface in missing_surfaces],
        **AUTHORITY_FALSE,
    }
