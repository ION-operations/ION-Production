"""GitHub communications fallback for ION carrier alignment.

This module is a non-authorizing fallback lane for moments when an MCP carrier
is unavailable, stale, or not exposed to the current model runtime. It prepares
GitHub-ready communication artifacts that a local operator can publish with the
GitHub CLI or attach through a PR/issue, but it never calls GitHub, never runs
``gh``, never stages/commits/pushes, and never grants production authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_github_data_plane_audit import audit_github_data_plane

SCHEMA_ID = "ion.github_comms_fallback.v1"
RECEIPT_SCHEMA_ID = "ion.github_comms_fallback.receipt.v1"
READY_VERDICT = "ION_GITHUB_COMMS_FALLBACK_ARTIFACT_READY"
BLOCKED_VERDICT = "ION_GITHUB_COMMS_FALLBACK_BLOCKED"

BASE_DIR = Path("ION/05_context/current/github_data_plane/comms_fallback")
ALLOWED_CHANNELS = {"issue", "pr", "comment", "artifact_only"}
DEFAULT_FALLBACK_REASON = "mcp_unavailable_or_not_exposed_to_current_carrier"
DEFAULT_SOURCE_CARRIER = "chatgpt_browser_sev"
DEFAULT_TARGET_CARRIER = "codex_cli_local_pc"
WRITE_CONFIRMATION_TOKEN = "ION_GITHUB_COMMS_FALLBACK_WRITE_CONFIRMED"
DEFAULT_TRANSPORT_STATUS = DEFAULT_FALLBACK_REASON
DEFAULT_LABELS = ["ion-comms-fallback", "mcp-unavailable", "needs-routing"]
COMMS_FALLBACK_DIR = BASE_DIR

FAILURE_CLASSES = (
    "GITHUB_COMMS_SCHEMA_FAILURE",
    "GITHUB_COMMS_SECRET_SCAN_BLOCK",
    "GITHUB_COMMS_TARGET_MISSING",
    "GITHUB_COMMS_CHANNEL_UNSUPPORTED",
    "GITHUB_DATA_PLANE_FAILURE",
    "CARRIER_ADAPTER_FAILURE",
    "ION_CORE_FAILURE",
    "POLICY_BLOCK_WORKING_AS_DESIGNED",
)

SECRET_PATTERNS = (
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("openai_project_key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b")),
    ("openai_secret_key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")),
    (
        "api_key_assignment",
        re.compile(
            r"\b(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|GH_TOKEN|API[_-]?KEY)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}",
            re.IGNORECASE,
        ),
    ),
    ("cloudflare_tunnel_token", re.compile(r"\b(?:TUNNEL_TOKEN|CLOUDFLARE[_-]?TOKEN)\b\s*[:=]", re.IGNORECASE)),
    ("browser_cookie", re.compile(r"\b(?:sessionid|auth_token|cookie)\b\s*[:=]", re.IGNORECASE)),
)

PLACEHOLDER_TOKENS = ("...", "<", "example", "placeholder", "redacted", "your_", "xxx")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_stamp(value: str) -> str:
    return value.replace(":", "").replace("+00:00", "Z").replace("+", "Z")


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:96] or "github_comms_fallback"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return resolve_shell_root_from_ion_root(root)


def _repo_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_placeholder_secret_line(line: str) -> bool:
    lowered = line.lower()
    return any(token in lowered for token in PLACEHOLDER_TOKENS)


def _secret_findings_for_text(text: str, *, label: str = "message") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if _is_placeholder_secret_line(line):
            continue
        for pattern_name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(
                    {
                        "surface": label,
                        "line": line_number,
                        "pattern": pattern_name,
                        "excerpt": f"<redacted:{pattern_name}>",
                    }
                )
    return findings


def scan_github_comms_text_for_secrets(*values: str) -> dict[str, Any]:
    """Return a redacted secret scan result for outbound comms text."""

    findings: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        findings.extend(_secret_findings_for_text(value or "", label=f"text_{index}"))
    return {
        "schema_id": "ion.github_comms_text_secret_scan.v1",
        "accepted": not findings,
        "finding_count": len(findings),
        "findings": findings[:100],
        "findings_truncated": len(findings) > 100,
        "secret_values_redacted": True,
    }


def _title_from_objective(objective: str, packet_id: str | None) -> str:
    prefix = "ION carrier fallback"
    compact = " ".join(objective.split())[:96] or "carrier alignment"
    if packet_id:
        return f"{prefix}: {packet_id} — {compact}"
    return f"{prefix}: {compact}"


def _audit_summary(audit: Mapping[str, Any]) -> dict[str, Any]:
    git = audit.get("git") if isinstance(audit.get("git"), Mapping) else {}
    alignment = audit.get("registry_alignment") if isinstance(audit.get("registry_alignment"), Mapping) else {}
    return {
        "verdict": audit.get("verdict"),
        "accepted": audit.get("accepted"),
        "failure_classification": audit.get("failure_classification"),
        "findings": audit.get("findings", []),
        "warnings": audit.get("warnings", []),
        "current_branch": git.get("current_branch"),
        "origin_configured": git.get("origin_configured"),
        "origin_url": git.get("origin_url"),
        "branch_alignment": alignment.get("branch_alignment"),
        "remote_alignment": alignment.get("remote_alignment"),
        "worktree_clean": (git.get("worktree") or {}).get("worktree_clean") if isinstance(git.get("worktree"), Mapping) else None,
    }


def _build_markdown_body(envelope: Mapping[str, Any]) -> str:
    data_plane = envelope.get("github_data_plane") if isinstance(envelope.get("github_data_plane"), Mapping) else {}
    requested_response = envelope.get("requested_response") or "Review, respond with current state, or attach a corrected packet/receipt."
    message = envelope.get("message") or ""
    evidence_refs = envelope.get("evidence_refs") or []
    lines = [
        "# ION GitHub comms fallback",
        "",
        "> Candidate carrier communication artifact. This is not accepted ION state until proof-gated and receipted.",
        "",
        "## Routing",
        "",
        f"- Comms ID: `{envelope.get('comms_id')}`",
        f"- Packet: `{envelope.get('packet_id') or 'none_declared'}`",
        f"- Channel: `{envelope.get('channel')}`",
        f"- Source carrier: `{envelope.get('source_carrier')}`",
        f"- Target carrier: `{envelope.get('target_carrier')}`",
        f"- Fallback reason: `{envelope.get('fallback_reason')}`",
        "",
        "## Objective",
        "",
        str(envelope.get("objective") or "").strip(),
        "",
        "## Message",
        "",
        str(message).strip(),
        "",
        "## Requested response",
        "",
        str(requested_response).strip(),
        "",
        "## Evidence refs",
        "",
    ]
    if evidence_refs:
        lines.extend(f"- `{ref}`" for ref in evidence_refs)
    else:
        lines.append("- none_declared")
    lines.extend(
        [
            "",
            "## Local/GitHub posture",
            "",
            f"- GitHub audit verdict: `{data_plane.get('verdict')}`",
            f"- GitHub audit accepted: `{data_plane.get('accepted')}`",
            f"- Current branch: `{data_plane.get('current_branch')}`",
            f"- Origin configured: `{data_plane.get('origin_configured')}`",
            f"- Branch alignment: `{data_plane.get('branch_alignment')}`",
            f"- Remote alignment: `{data_plane.get('remote_alignment')}`",
            "",
            "## Authority boundary",
            "",
            "- This artifact does not call GitHub.",
            "- This artifact does not run `gh`.",
            "- This artifact does not stage, commit, push, deploy, or mutate production state.",
            "- GitHub issues, PRs, and comments are proposals/evidence, not ION runtime authority.",
            "- Secrets, tokens, browser profiles, tunnel credentials, and production-only state are forbidden.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _command_plan(
    *,
    channel: str,
    title: str,
    body_rel: str,
    branch: str | None,
    issue_number: str | None,
) -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    manual_fallbacks = [
        "Copy the markdown body into a GitHub issue, PR body, or issue comment manually.",
        "Attach the JSON envelope and receipt to the synchronized project artifact bundle when GitHub is unavailable.",
    ]
    if channel == "issue":
        argv = ["gh", "issue", "create", "--title", title, "--body-file", body_rel]
        commands.append({"name": "create_issue", "argv": argv, "shell": shlex.join(argv)})
    elif channel == "pr":
        argv = ["gh", "pr", "create", "--title", title, "--body-file", body_rel]
        if branch:
            argv.extend(["--head", branch])
        argv.extend(["--base", "main"])
        commands.append({"name": "create_pull_request", "argv": argv, "shell": shlex.join(argv)})
    elif channel == "comment" and issue_number:
        argv = ["gh", "issue", "comment", str(issue_number), "--body-file", body_rel]
        commands.append({"name": "comment_on_issue_or_pr", "argv": argv, "shell": shlex.join(argv)})
    return {
        "schema_id": "ion.github_comms_fallback.command_plan.v1",
        "channel": channel,
        "requires_local_operator_execution": True,
        "network_access_used_by_generator": False,
        "github_mutation_performed_by_generator": False,
        "git_mutation_performed_by_generator": False,
        "commands": commands,
        "manual_fallbacks": manual_fallbacks,
    }


def build_github_comms_fallback(
    root: str | Path | None = None,
    *,
    objective: str,
    message: str,
    packet_id: str | None = None,
    title: str | None = None,
    channel: str = "issue",
    source_carrier: str = DEFAULT_SOURCE_CARRIER,
    target_carrier: str = DEFAULT_TARGET_CARRIER,
    fallback_reason: str = DEFAULT_FALLBACK_REASON,
    requested_response: str | None = None,
    evidence_refs: list[str] | None = None,
    issue_number: str | None = None,
    branch: str | None = None,
    write: bool = False,
) -> dict[str, Any]:
    """Build a non-authorizing GitHub comms fallback artifact package."""

    shell_root = _resolve_root(root)
    created_at = _now()
    normalized_channel = channel.strip().lower()
    normalized_objective = " ".join((objective or "").split())
    normalized_message = (message or "").strip()
    normalized_title = title.strip() if title else _title_from_objective(normalized_objective, packet_id)
    audit = audit_github_data_plane(shell_root)
    summary = _audit_summary(audit)
    current_branch = branch or summary.get("current_branch")

    findings: list[str] = []
    warnings: list[str] = []
    if not normalized_objective:
        findings.append("objective_required")
    if not normalized_message:
        findings.append("message_required")
    if normalized_channel not in ALLOWED_CHANNELS:
        findings.append("unsupported_channel")
    if normalized_channel == "comment" and not issue_number:
        findings.append("comment_channel_requires_issue_number")
    if normalized_channel == "pr" and not current_branch:
        findings.append("pr_channel_requires_branch")
    if summary.get("accepted") is not True:
        warnings.append("github_data_plane_audit_not_accepted")
    if summary.get("origin_configured") is not True and normalized_channel in {"issue", "pr", "comment"}:
        warnings.append("origin_remote_not_confirmed")

    secret_scan = scan_github_comms_text_for_secrets(
        normalized_objective,
        normalized_message,
        normalized_title,
        requested_response or "",
        "\n".join(evidence_refs or []),
    )
    if not secret_scan.get("accepted"):
        findings.append("secret_scan_block")

    comms_id = f"github_comms_{_safe_stamp(created_at)}_{_safe_slug(packet_id or normalized_objective)}"
    base_rel = BASE_DIR / comms_id
    envelope_rel = (base_rel / "envelope.json").as_posix()
    markdown_rel = (base_rel / "message.md").as_posix()
    commands_rel = (base_rel / "github_command_plan.json").as_posix()
    receipt_rel = (base_rel / "receipt.json").as_posix()

    accepted = not findings
    envelope: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "comms_id": comms_id,
        "created_at": created_at,
        "root": shell_root.as_posix(),
        "status": "artifact_ready" if accepted else "blocked",
        "verdict": READY_VERDICT if accepted else BLOCKED_VERDICT,
        "channel": normalized_channel,
        "packet_id": packet_id,
        "title": normalized_title,
        "objective": normalized_objective,
        "message": normalized_message if accepted else "<withheld_due_to_blocking_findings>",
        "message_sha256": _sha256_text(normalized_message) if normalized_message else None,
        "source_carrier": source_carrier,
        "target_carrier": target_carrier,
        "fallback_reason": fallback_reason,
        "requested_response": requested_response or "Review, respond with current state, or attach a corrected packet/receipt.",
        "evidence_refs": evidence_refs or [],
        "issue_number": issue_number,
        "branch": current_branch,
        "artifact_paths": {
            "envelope": envelope_rel,
            "markdown": markdown_rel,
            "github_command_plan": commands_rel,
            "receipt": receipt_rel,
        },
        "github_data_plane": summary,
        "mcp_boundary": {
            "direct_mcp_invocation_performed_by_generator": False,
            "direct_mcp_tool_namespace_observed_by_generator": False,
            "local_mcp_bridge_smoke_command": "PYTHONPATH=ION/04_packages python3 -m kernel.ion_mcp_local_bridge_smoke --ion-root . --json",
            "fallback_when": [
                "mcp_connector_not_exposed_to_current_carrier",
                "mcp_connector_stale_or_unconfirmed",
                "mcp_handshake_fails",
                "peer_agent_needs_auditable_handoff_without_shared_runtime_tooling",
            ],
        },
        "secret_scan": secret_scan,
        "findings": findings,
        "warnings": warnings,
        "failure_classification": (
            "GITHUB_COMMS_SECRET_SCAN_BLOCK"
            if "secret_scan_block" in findings
            else "GITHUB_COMMS_SCHEMA_FAILURE"
            if findings
            else None
        ),
        "failure_classes": FAILURE_CLASSES,
        "network_access_used": False,
        "git_mutation_performed": False,
        "github_mutation_performed": False,
        "mcp_mutation_performed": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claimed": False,
    }

    command_plan = _command_plan(
        channel=normalized_channel,
        title=normalized_title,
        body_rel=markdown_rel,
        branch=current_branch if isinstance(current_branch, str) else None,
        issue_number=issue_number,
    )
    envelope["github_command_plan"] = {
        "path": commands_rel,
        "command_count": len(command_plan["commands"]),
        "manual_fallback_count": len(command_plan["manual_fallbacks"]),
    }

    if write:
        if not accepted:
            envelope["write"] = {
                "requested": True,
                "performed": False,
                "finding": "write_blocked_due_to_findings",
            }
            return envelope
        markdown_text = _build_markdown_body(envelope)
        envelope_path = shell_root / envelope_rel
        markdown_path = shell_root / markdown_rel
        commands_path = shell_root / commands_rel
        receipt_path = shell_root / receipt_rel
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown_text, encoding="utf-8")
        _write_json(commands_path, command_plan)
        receipt = {
            "schema_id": RECEIPT_SCHEMA_ID,
            "comms_id": comms_id,
            "created_at": created_at,
            "status": "artifact_written",
            "files_touched": [markdown_rel, commands_rel, envelope_rel, receipt_rel],
            "artifact_sha256": {
                "markdown": _sha256_file(markdown_path),
                "github_command_plan": _sha256_file(commands_path),
            },
            "network_access_used": False,
            "git_mutation_performed": False,
            "github_mutation_performed": False,
            "mcp_mutation_performed": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claimed": False,
        }
        _write_json(receipt_path, receipt)
        envelope["receipt_sha256"] = _sha256_file(receipt_path)
        envelope["markdown_sha256"] = _sha256_file(markdown_path)
        envelope["github_command_plan_sha256"] = _sha256_file(commands_path)
        envelope["write"] = {"requested": True, "performed": True, "files_touched": receipt["files_touched"]}
        _write_json(envelope_path, envelope)
        envelope["envelope_sha256"] = _sha256_file(envelope_path)
        _write_json(envelope_path, envelope)
    else:
        envelope["write"] = {"requested": False, "performed": False}

    return envelope



# ---- Public draft compatibility API -------------------------------------------------
# These helpers are deliberately local-only. They let ChatGPT/Codex/GitHub lanes
# produce copyable communication artifacts when MCP is unavailable or not exposed
# to the current carrier, without mutating Git, GitHub, MCP, or accepted ION state.

_INLINE_CREDENTIAL_REMOTE_RE = re.compile(r"(https?://)([^/\s:@]+):([^/\s@]+)@")
_SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(?:secret|token|password|api[_-]?key|OPENAI_API_KEY|GITHUB_TOKEN|GH_TOKEN)\b\s*[:=]\s*[^\s,;]+",
    re.IGNORECASE,
)


def scan_public_text_for_secrets(fields: Mapping[str, Any]) -> dict[str, Any]:
    """Compatibility wrapper for outbound public text secret scan."""
    values: list[str] = []
    for value in fields.values():
        if isinstance(value, (list, tuple, set)):
            values.append("\n".join(str(item) for item in value))
        else:
            values.append(str(value or ""))
    return scan_github_comms_text_for_secrets(*values)


def redact_text(text: str) -> str:
    """Return public-safe text with common secret/token shapes redacted."""
    value = str(text or "")
    value = _INLINE_CREDENTIAL_REMOTE_RE.sub(r"\1<redacted>@", value)
    for _label, pattern in SECRET_PATTERNS:
        value = pattern.sub("<redacted>", value)
    value = _SECRET_ASSIGNMENT_RE.sub(lambda match: re.sub(r"([:=])\s*.*$", r"\1<redacted>", match.group(0)), value)
    return value


def _md_bullets(items: Sequence[str] | None) -> str:
    values = [redact_text(str(item).strip()) for item in (items or []) if str(item).strip()]
    return "\n".join(f"- {item}" for item in values) if values else "- none"


def draft_issue_payload(
    *,
    title: str,
    packet_id: str,
    objective: str,
    packet_path: str | None = None,
    evidence: Sequence[str] | None = None,
    artifacts: Sequence[str] | None = None,
    blockers: Sequence[str] | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    """Build a GitHub issue draft; no network, git, or GitHub mutation."""
    safe_title = redact_text(title)
    safe_packet_id = redact_text(packet_id)
    safe_objective = redact_text(objective)
    body = f"""# {safe_title}

Status: **candidate communication artifact, not accepted ION state**

## Packet

`{safe_packet_id}`

## Objective

{safe_objective}

## Packet path

`{redact_text(packet_path or 'not supplied')}`

## Message

{redact_text(message or 'MCP/tooling lane is unavailable or not exposed to the current carrier. This issue draft is a GitHub data-plane fallback only.')}

## Evidence

{_md_bullets(evidence)}

## Artifacts

{_md_bullets(artifacts)}

## Blockers

{_md_bullets(blockers)}

## Authority boundary

- No production authority
- No live execution authority
- No GitHub mutation performed by this draft
- No git mutation performed by this draft
- Not accepted ION state until reconciled through packets, proof gates, receipts, and Steward decision
"""
    return {
        "schema_id": "ion.github_comms_issue_draft.v1",
        "title": safe_title,
        "body": body,
        "labels": DEFAULT_LABELS,
        "packet_id": safe_packet_id,
        "github_mutation_performed": False,
        "git_mutation_performed": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "public_safe": scan_public_text_for_secrets({"title": safe_title, "body": body}).get("accepted", False),
    }


def draft_pr_payload(
    *,
    title: str,
    source_branch: str,
    packet_id: str,
    objective: str,
    touched_paths: Sequence[str] | None = None,
    validations: Sequence[str] | None = None,
    blockers: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build a GitHub PR draft body; no git or GitHub mutation."""
    safe_title = redact_text(title)
    body = f"""# {safe_title}

Status: **candidate PR communication, not accepted ION state**

## Packet

`{redact_text(packet_id)}`

## Objective

{redact_text(objective)}

## Source branch

`{redact_text(source_branch)}`

## Touched paths

{_md_bullets(touched_paths)}

## Validations

{_md_bullets(validations)}

## Known blockers

{_md_bullets(blockers)}

## Authority boundary

- No production authority
- No live execution authority
- No git mutation performed by this draft
- No GitHub mutation performed by this draft
- Merge, push, and accepted-state decisions remain outside this helper
"""
    return {
        "schema_id": "ion.github_comms_pr_draft.v1",
        "title": safe_title,
        "body": body,
        "source_branch": redact_text(source_branch),
        "packet_id": redact_text(packet_id),
        "github_mutation_performed": False,
        "git_mutation_performed": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "public_safe": scan_public_text_for_secrets({"title": safe_title, "body": body}).get("accepted", False),
    }


def write_draft_artifact(
    root: str | Path | None,
    draft: Mapping[str, Any],
    *,
    confirmation: str | None,
    title: str,
) -> dict[str, Any]:
    """Write a local candidate draft artifact after explicit confirmation only."""
    if confirmation != WRITE_CONFIRMATION_TOKEN:
        return {
            "ok": False,
            "schema_id": "ion.github_comms_draft_write_refusal.v1",
            "required_confirmation": WRITE_CONFIRMATION_TOKEN,
            "github_mutation_performed": False,
            "git_mutation_performed": False,
            "accepted_state_authority": False,
        }
    shell_root = _resolve_root(root)
    created_at = _now()
    slug = _safe_slug(title or draft.get("title") or "github_comms_draft")
    stem = f"github_comms_draft_{_safe_stamp(created_at)}_{slug}"
    rel_json = (COMMS_FALLBACK_DIR / f"{stem}.json").as_posix()
    rel_md = (COMMS_FALLBACK_DIR / f"{stem}.md").as_posix()
    payload = dict(draft)
    payload.update({
        "written_at": created_at,
        "local_candidate_written": True,
        "github_mutation_performed": False,
        "git_mutation_performed": False,
        "accepted_state_authority": False,
    })
    json_path = shell_root / rel_json
    md_path = shell_root / rel_md
    _write_json(json_path, payload)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(str(payload.get("body") or ""), encoding="utf-8")
    return {
        "ok": True,
        "schema_id": "ion.github_comms_draft_write_receipt.v1",
        "json_path": rel_json,
        "markdown_path": rel_md,
        "json_sha256": _sha256_file(json_path),
        "markdown_sha256": _sha256_file(md_path),
        "github_mutation_performed": False,
        "git_mutation_performed": False,
        "accepted_state_authority": False,
    }


# ---- MCP bridge compatibility projections ------------------------------------------

def _channel_from_target(target: str | None) -> str:
    normalized = (target or "issue").strip().lower()
    if normalized in {"pr"}:
        return "pr"
    if normalized in {"comment"}:
        return "comment"
    if normalized in {"pr_comment", "branch_handoff", "generic", "artifact_only"}:
        return "artifact_only"
    return "issue"


def build_github_comms_fallback_status(
    root: str | Path | None = None,
    *,
    mcp_observation: str | None = None,
) -> dict[str, Any]:
    """Read-only MCP-facing projection of GitHub comms fallback readiness."""
    shell_root = _resolve_root(root)
    try:
        audit = audit_github_data_plane(shell_root)
        summary = _audit_summary(audit)
    except Exception as exc:  # pragma: no cover - defensive bridge projection
        summary = {"verdict": "ION_GITHUB_DATA_PLANE_AUDIT_UNAVAILABLE", "accepted": False, "error": str(exc)}
    warnings: list[str] = []
    if summary.get("accepted") is not True:
        warnings.append("github_data_plane_audit_not_accepted")
    if summary.get("origin_configured") is not True:
        warnings.append("origin_remote_not_confirmed")
    return {
        "schema_id": SCHEMA_ID,
        "status_schema_id": "ion.github_comms_fallback.status.v1",
        "generated_at": _now(),
        "mode": "LOCAL_DRAFT_ONLY_NO_GITHUB_MUTATION",
        "verdict": "ION_GITHUB_COMMS_FALLBACK_STATUS_READY",
        "ok": True,
        "root": shell_root.as_posix(),
        "mcp_observation": redact_text(mcp_observation or "not_supplied"),
        "github_data_plane": summary,
        "warnings": warnings,
        "fallback_channels": sorted(ALLOWED_CHANNELS),
        "required_human_actions": [
            "Review generated markdown before posting to GitHub.",
            "Run any gh command plan only from a governed local/operator lane.",
            "Import the resulting GitHub URL/ref back into an ION packet, gate, and receipt.",
        ],
        "network_access_used": False,
        "git_mutation_performed": False,
        "github_mutation_performed": False,
        "mcp_mutation_performed": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "accepted_state_claimed": False,
    }


def build_github_comms_fallback_draft(
    root: str | Path | None = None,
    *,
    message: str,
    summary: str | None = None,
    target: str = "issue",
    related_ref: str | None = None,
    source_carrier: str = "unknown_carrier",
    mcp_status: str = DEFAULT_TRANSPORT_STATUS,
    write: bool = False,
    confirmation: str | None = None,
) -> dict[str, Any]:
    """Build a copy-block fallback draft; no network/GitHub/git mutation."""
    if write and confirmation != WRITE_CONFIRMATION_TOKEN:
        return {
            "schema_id": "ion.github_comms_fallback_draft.v1",
            "verdict": BLOCKED_VERDICT,
            "ok": False,
            "finding": "write_confirmation_required",
            "required_confirmation": WRITE_CONFIRMATION_TOKEN,
            "network_access_used": False,
            "github_mutation_performed": False,
            "git_mutation_performed": False,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    channel = _channel_from_target(target)
    objective = summary or "ION MCP/GitHub communications fallback"
    envelope = build_github_comms_fallback(
        root,
        objective=objective,
        message=message or objective,
        packet_id=related_ref,
        channel=channel,
        source_carrier=source_carrier,
        target_carrier=DEFAULT_TARGET_CARRIER,
        fallback_reason=mcp_status or DEFAULT_FALLBACK_REASON,
        evidence_refs=[f"source_carrier={source_carrier}", f"mcp_status={mcp_status or DEFAULT_FALLBACK_REASON}"],
        write=write,
    )
    markdown_body = _build_markdown_body(envelope) if envelope.get("verdict") == READY_VERDICT else ""
    result: dict[str, Any] = {
        "schema_id": "ion.github_comms_fallback_draft.v1",
        "draft_id": envelope.get("comms_id"),
        "verdict": envelope.get("verdict"),
        "ok": envelope.get("verdict") == READY_VERDICT,
        "target": target,
        "channel": channel,
        "related_ref": related_ref,
        "source_carrier": source_carrier,
        "mcp_status": redact_text(mcp_status or DEFAULT_FALLBACK_REASON),
        "write": envelope.get("write", {"requested": False, "performed": False}),
        "copy_blocks": {
            "github_issue_title": str(envelope.get("title") or objective),
            "github_issue_body": markdown_body,
            "github_pr_title": str(envelope.get("title") or objective),
            "github_pr_body": markdown_body,
            "github_command_plan_path": (envelope.get("artifact_paths") or {}).get("github_command_plan"),
        },
        "findings": envelope.get("findings", []),
        "warnings": envelope.get("warnings", []),
        "network_access_used": False,
        "github_mutation_performed": False,
        "git_mutation_performed": False,
        "accepted_state_authority": False,
        "accepted_state_claimed": False,
        "production_authority": False,
        "live_execution_authority": False,
    }
    if write:
        # build_github_comms_fallback has already performed only local file writes.
        result["artifact_paths"] = envelope.get("artifact_paths", {})
        result["envelope"] = envelope
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a non-authorizing ION GitHub comms fallback artifact.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--objective", required=True)
    parser.add_argument("--message", default=None)
    parser.add_argument("--message-file", default=None)
    parser.add_argument("--packet-id", default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--channel", choices=sorted(ALLOWED_CHANNELS), default="issue")
    parser.add_argument("--source-carrier", default=DEFAULT_SOURCE_CARRIER)
    parser.add_argument("--target-carrier", default=DEFAULT_TARGET_CARRIER)
    parser.add_argument("--fallback-reason", default=DEFAULT_FALLBACK_REASON)
    parser.add_argument("--requested-response", default=None)
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument("--issue-number", default=None)
    parser.add_argument("--branch", default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.message_file:
        message = Path(args.message_file).read_text(encoding="utf-8")
    else:
        message = args.message or ""

    result = build_github_comms_fallback(
        args.ion_root,
        objective=args.objective,
        message=message,
        packet_id=args.packet_id,
        title=args.title,
        channel=args.channel,
        source_carrier=args.source_carrier,
        target_carrier=args.target_carrier,
        fallback_reason=args.fallback_reason,
        requested_response=args.requested_response,
        evidence_refs=args.evidence_ref,
        issue_number=args.issue_number,
        branch=args.branch,
        write=args.write,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["verdict"])
        for path in (result.get("artifact_paths") or {}).values():
            print(path)
        for finding in result.get("findings", []):
            print(f"- {finding}")
    return 0 if result["verdict"] == READY_VERDICT else 1


if __name__ == "__main__":
    raise SystemExit(main())
