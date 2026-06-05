"""Leaf IO/hash/path helpers for Domain Weaver.

This helper module is intentionally stdlib-only so the Domain Weaver monolith
can import it without creating reverse kernel imports.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

DEFAULT_CODEX_QUEUE_RUNS_DIR = Path("ION/05_context/current/chatgpt_connector/codex_queue_runs")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _stamp_micro() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _stable_json_text(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _stable_json_sha256(data: Mapping[str, Any]) -> str:
    return hashlib.sha256(_stable_json_text(data).encode("utf-8")).hexdigest()


def _write_stable_json_and_hash(path: Path, data: Mapping[str, Any]) -> str:
    text = _stable_json_text(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_rel_path(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes root: {value}") from exc
    return candidate


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_ref(root: Path, rel_path: Path, reason: str, *, required: bool = True) -> dict[str, Any]:
    path = root / rel_path
    ref: dict[str, Any] = {
        "path": rel_path.as_posix(),
        "exists": path.is_file(),
        "required": required,
        "reason": reason,
    }
    if path.is_file():
        ref["sha256"] = _sha256_file(path)
    return ref


def _latest_json_refs(root: Path, rel_dir: Path, *, reason: str, limit: int = 4) -> list[dict[str, Any]]:
    directory = root / rel_dir
    if not directory.is_dir():
        return []
    refs: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda candidate: candidate.stat().st_mtime, reverse=True)[:limit]:
        refs.append(
            {
                "path": _rel(root, path),
                "exists": True,
                "sha256": _sha256_file(path),
                "reason": reason,
            }
        )
    return refs


def _latest_queue_run_refs(root: Path, *, limit: int = 4) -> list[dict[str, Any]]:
    run_root = root / DEFAULT_CODEX_QUEUE_RUNS_DIR
    if not run_root.is_dir():
        return []
    run_packets = [path / "run.json" for path in run_root.iterdir() if path.is_dir() and (path / "run.json").is_file()]
    refs: list[dict[str, Any]] = []
    for path in sorted(run_packets, key=lambda candidate: candidate.stat().st_mtime, reverse=True)[:limit]:
        refs.append(
            {
                "path": _rel(root, path),
                "exists": True,
                "sha256": _sha256_file(path),
                "reason": "Recent Codex queue run receipt used for queue settlement context.",
            }
        )
    return refs


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _path_mtime_epoch_seconds(root: Path, rel_path: Path) -> float:
    try:
        return (root / rel_path).stat().st_mtime
    except OSError:
        return 0.0


def _safe_id(value: Any) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(ch if ch.isalnum() else "_" for ch in text)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_") or "unknown"


def _parse_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list | tuple):
        return []
    cleaned: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def _task_return_body_path_from_return(
    root: Path,
    latest_return: Mapping[str, Any],
    fallback_run_packets: list[Mapping[str, Any]],
) -> str:
    template_result = _as_mapping(latest_return.get("template_action_proof_result"))
    touched_paths = [str(path) for path in template_result.get("touched_paths") or [] if str(path)]
    body_paths = [
        path
        for path in touched_paths
        if path.endswith("task_return_body.md") or path.endswith("latest_return.md")
    ]
    for body_path in reversed(body_paths):
        if (root / body_path).is_file():
            return body_path
    packet_body_path = str(latest_return.get("task_return_body_path") or "").strip()
    if packet_body_path and (root / packet_body_path).is_file():
        return packet_body_path
    packet_latest_return_path = str(latest_return.get("latest_return_markdown_path") or "").strip()
    if packet_latest_return_path and (root / packet_latest_return_path).is_file():
        return packet_latest_return_path
    for run in reversed(fallback_run_packets):
        run_body_path = str(run.get("task_return_body_path") or "").strip()
        if run_body_path and (root / run_body_path).is_file():
            return run_body_path
        run_latest_return_path = str(run.get("latest_return_markdown_path") or "").strip()
        if run_latest_return_path and (root / run_latest_return_path).is_file():
            return run_latest_return_path
        run_path = str(run.get("run_packet_path") or "")
        if not run_path:
            continue
        run_dir = (root / run_path).parent
        for candidate_name in ("task_return_body.md", "latest_return.md"):
            candidate = run_dir / candidate_name
            if candidate.is_file():
                return _rel(root, candidate)
    return ""


def _context_receipt_path_from_return(
    root: Path,
    latest_return: Mapping[str, Any],
    body_path: str,
    fallback_run_packets: list[Mapping[str, Any]],
) -> str:
    template_result = _as_mapping(latest_return.get("template_action_proof_result"))
    touched_paths = [str(path) for path in template_result.get("touched_paths") or [] if str(path)]
    receipt_paths = [path for path in touched_paths if path.endswith("context_receipt.json")]
    if receipt_paths:
        return receipt_paths[-1]
    if body_path:
        candidate = (root / body_path).parent / "context_receipt.json"
        if candidate.is_file():
            return _rel(root, candidate)
    for run in reversed(fallback_run_packets):
        run_path = str(run.get("run_packet_path") or "")
        if not run_path:
            continue
        candidate = (root / run_path).parent / "context_receipt.json"
        if candidate.is_file():
            return _rel(root, candidate)
    return ""


def _result_paths(result: Mapping[str, Any]) -> list[str]:
    paths: list[str] = []
    for key, value in result.items():
        if key.endswith("_path") and isinstance(value, str) and value:
            paths.append(value)
        elif key.endswith("_paths") and isinstance(value, list):
            paths.extend(str(item) for item in value if str(item))
    return paths


def _unique_paths(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out
