"""AST-backed index for the Domain Weaver monolith.

This module intentionally does not import ``ion_domain_weaver``.  The monolith is
large, authority-bearing, and state-adjacent, so this indexer reads it as source
text and produces navigation artifacts for humans and AI agents.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_ID = "ion.domain_weaver.monolith_index.v0_1"
DEFAULT_SOURCE_PATH = Path("ION/04_packages/kernel/ion_domain_weaver.py")
DEFAULT_OUTPUT_DIR = Path("ION/05_context/current/domain_weaver/monolith_index")
DEFAULT_INDEX_JSON_NAME = "DOMAIN_WEAVER_MONOLITH_INDEX.latest.json"
DEFAULT_INDEX_MD_NAME = "DOMAIN_WEAVER_MONOLITH_INDEX.latest.md"

WRITE_CALL_NAMES = {
    "_write_domain_weaver_operator_action_history",
    "_write_stable_json_and_hash",
    "append",
    "mkdir",
    "replace",
    "unlink",
    "write_bytes",
    "write_text",
}
READ_CALL_NAMES = {
    "_latest_json_refs",
    "_latest_queue_run_refs",
    "_read_json_file",
    "exists",
    "glob",
    "read_bytes",
    "read_text",
}
HIGH_RISK_WORDS = {
    "accepted_state": "accepted_state",
    "action_history": "operator_action_history",
    "active_binding": "active_binding",
    "active_context": "active_context",
    "carrier": "carrier",
    "context": "context",
    "dispatcher": "dispatcher",
    "exact_active": "exact_active",
    "fanin": "fanin",
    "fanout": "fanout",
    "lease": "lease",
    "live": "live",
    "materializ": "materialization",
    "mutation": "mutation",
    "operator": "operator_action",
    "proof": "proof",
    "queue": "queue",
    "registry": "registry",
    "settlement": "settlement",
    "topology": "topology",
    "worker_start": "worker_start",
    "write": "write",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


def compact(value: str, limit: int = 140) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)] + "..."


def rel_path(root: Path | None, path: Path) -> str:
    if root is None:
        return path.as_posix()
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    if isinstance(node, ast.Call):
        return call_name(node.func)
    return ""


def simple_call_name(name: str) -> str:
    return name.rsplit(".", 1)[-1] if name else ""


def iter_top_level_targets(node: ast.AST) -> Iterable[str]:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            yield from _target_names(target)
    elif isinstance(node, ast.AnnAssign):
        yield from _target_names(node.target)


def _target_names(target: ast.AST) -> Iterable[str]:
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for item in target.elts:
            yield from _target_names(item)


def string_literals(node: ast.AST) -> list[str]:
    values: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            values.append(child.value)
    return values


def schema_literals(strings: Sequence[str]) -> list[str]:
    return sorted({value for value in strings if value.startswith("ion.domain_weaver") or value.startswith("ion.codex")})


def packet_literals(strings: Sequence[str]) -> list[str]:
    return sorted({value for value in strings if value.startswith("PCKT-DOMAIN-WEAVER")})


def path_like_literals(strings: Sequence[str]) -> list[str]:
    results = set()
    for value in strings:
        if "/" in value and not value.startswith("http"):
            results.add(value)
        elif value.endswith((".json", ".md", ".py", ".txt", ".yaml", ".yml")):
            results.add(value)
    return sorted(results)


def names_referenced(node: ast.AST) -> list[str]:
    names = {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
    }
    return sorted(names)


def calls_in_node(node: ast.AST) -> list[str]:
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = call_name(child.func)
            if name:
                calls.append(name)
    return sorted(set(calls))


def source_segment(lines: Sequence[str], start: int, end: int) -> str:
    if start <= 0 or end < start:
        return ""
    return "\n".join(lines[start - 1 : end])


def signature_for_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({unparse(node.args)})"


def function_doc_summary(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    doc = ast.get_docstring(node) or ""
    if not doc:
        return ""
    return compact(doc.splitlines()[0], 180)


def classify_category(name: str, strings: Sequence[str], calls: Sequence[str]) -> str:
    haystack = " ".join([name, *strings, *calls]).lower()
    if name == "execute_domain_weaver_action":
        return "action_dispatcher"
    if "context_active" in haystack or "worker_start_context" in haystack or "readiness" in haystack:
        return "context_and_worker_gates"
    if "queue_governance" in haystack or "classify_queue" in haystack or "queue_lifecycle" in haystack:
        return "queue_governance"
    if "dynamic_swarm" in haystack or "topology" in haystack or "fission" in haystack:
        return "topology_and_swarm"
    if "exact_active" in haystack or "active_invocable" in haystack:
        return "exact_active_binding"
    if "live_fanin" in haystack or "live_carrier" in haystack or "return_monitor" in haystack:
        return "live_binding_and_fanin"
    if "wave2" in haystack or "wave1" in haystack or "foundation_wave" in haystack:
        return "wave_packet_templates"
    if "ui_" in haystack or "activity_city" in haystack or "visual_proof" in haystack or "cockpit" in haystack:
        return "ui_and_visual_proof"
    if "promotion" in haystack or "gate" in haystack or "steward_ready" in haystack or "phase_closure" in haystack:
        return "promotion_and_reviews"
    if "materialize" in name or "materialization" in haystack:
        return "materializers"
    if "projection" in haystack or "dogfood" in haystack or "founding_assembly" in haystack:
        return "projection_builders"
    if "operator_action" in haystack or "action_history" in haystack:
        return "operator_action_history"
    if name.startswith(("build_", "_build_")) and ("template" in haystack or "request" in haystack):
        return "packet_template_builders"
    if name.startswith(("_latest", "_file", "_safe", "_rel", "_read", "_write", "_stamp", "_now")):
        return "compatibility_or_io_helpers"
    if name.startswith("_") and len(calls) <= 6:
        return "private_helper"
    return "general_domain_weaver"


def risk_tags_for(name: str, strings: Sequence[str], calls: Sequence[str], refs: Sequence[str]) -> list[str]:
    haystack = " ".join([name, *strings, *calls, *refs]).lower()
    tags = {tag for word, tag in HIGH_RISK_WORDS.items() if word in haystack}
    simple_calls = {simple_call_name(call) for call in calls}
    if simple_calls & WRITE_CALL_NAMES:
        tags.add("writes_file")
    if simple_calls & READ_CALL_NAMES:
        tags.add("reads_file")
    if "start_workers" in haystack or "worker_started" in haystack:
        tags.add("worker_start")
    if "confirmation" in haystack:
        tags.add("confirmation_gate")
    if "authority" in haystack:
        tags.add("authority_gate")
    if not tags:
        tags.add("low_signal")
    return sorted(tags)


def assignment_category(name: str, strings: Sequence[str]) -> str:
    if name.endswith("_PATH"):
        return "path_constant"
    if name.endswith("_DIR"):
        return "directory_constant"
    if name.endswith("_SCHEMA_ID") or any(value.startswith("ion.domain_weaver") for value in strings):
        return "schema_constant"
    if name.endswith("_PACKET_ID") or any(value.startswith("PCKT-DOMAIN-WEAVER") for value in strings):
        return "packet_constant"
    if "ACTION" in name or "ALLOWED" in name:
        return "action_policy"
    if "ROUTE" in name or "LANE" in name:
        return "route_catalog"
    return "module_constant"


def assignment_value_preview(node: ast.AST) -> str:
    value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else node
    literal = safe_literal(value)
    if literal is not None:
        return compact(repr(literal), 180)
    return compact(unparse(value), 180)


def assignment_literal_values(node: ast.AST) -> Any:
    value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else node
    literal = safe_literal(value)
    if isinstance(literal, (str, int, float, bool)) or literal is None:
        return literal
    if isinstance(literal, (list, tuple, set)):
        return list(literal)
    if isinstance(literal, dict):
        return literal
    return None


def extract_allowed_actions(assignments: Sequence[Mapping[str, Any]]) -> list[str]:
    for row in assignments:
        if row.get("name") == "DOMAIN_WEAVER_ALLOWED_OPERATOR_ACTIONS":
            value = row.get("literal_value")
            if isinstance(value, list):
                return [str(item) for item in value]
    return []


def extract_read_only_actions(assignments: Sequence[Mapping[str, Any]]) -> list[str]:
    for row in assignments:
        if row.get("name") == "DOMAIN_WEAVER_READ_ONLY_CONTEXT_ACTIONS":
            value = row.get("literal_value")
            if isinstance(value, list):
                return [str(item) for item in value]
    return []


def action_literals_from_test(test: ast.AST) -> list[str]:
    results: set[str] = set()
    for node in ast.walk(test):
        if not isinstance(node, ast.Compare):
            continue
        left_is_action = isinstance(node.left, ast.Name) and node.left.id == "action"
        if not left_is_action:
            continue
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, ast.Eq):
                literal = safe_literal(comparator)
                if isinstance(literal, str):
                    results.add(literal)
            elif isinstance(op, ast.In):
                literal = safe_literal(comparator)
                if isinstance(literal, (tuple, list, set)):
                    results.update(str(item) for item in literal if isinstance(item, str))
    return sorted(results)


def body_summary(node: ast.If, internal_names: set[str]) -> dict[str, Any]:
    calls = calls_in_node(ast.Module(body=node.body, type_ignores=[]))
    internal_calls = sorted({simple_call_name(call) for call in calls if simple_call_name(call) in internal_names})
    strings = string_literals(ast.Module(body=node.body, type_ignores=[]))
    return {
        "line_start": node.lineno,
        "line_end": getattr(node, "end_lineno", node.lineno),
        "internal_calls": internal_calls[:40],
        "result_keys": sorted({value for value in strings if value in {"summary", "results", "evidence_paths", "receipt_paths", "worker_started_count", "queue_ledger_path", "projection_materialized"}}),
        "risk_tags": risk_tags_for("dispatcher_branch", strings, calls, []),
    }


def extract_dispatcher_branches(
    tree: ast.Module,
    internal_names: set[str],
) -> tuple[list[dict[str, Any]], int | None, int | None]:
    dispatcher = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "execute_domain_weaver_action":
            dispatcher = node
            break
    if dispatcher is None:
        return [], None, None
    branches: list[dict[str, Any]] = []
    for node in ast.walk(dispatcher):
        if not isinstance(node, ast.If):
            continue
        actions = action_literals_from_test(node.test)
        if not actions:
            continue
        summary = body_summary(node, internal_names)
        for action in actions:
            branches.append({"action": action, **summary})
    branches.sort(key=lambda item: (int(item["line_start"]), str(item["action"])))
    return branches, dispatcher.lineno, dispatcher.end_lineno


def build_assignment_index(tree: ast.Module) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        for name in iter_top_level_targets(node):
            strings = string_literals(node)
            rows.append(
                {
                    "name": name,
                    "line_start": node.lineno,
                    "line_end": getattr(node, "end_lineno", node.lineno),
                    "category": assignment_category(name, strings),
                    "value_preview": assignment_value_preview(node),
                    "literal_value": assignment_literal_values(node),
                    "schema_ids": schema_literals(strings),
                    "packet_ids": packet_literals(strings),
                    "path_literals": path_like_literals(strings),
                }
            )
    return rows


def build_import_index(tree: ast.Module) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                rows.append({"module": alias.name, "name": alias.asname or alias.name, "line": node.lineno, "kind": "import"})
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            for alias in node.names:
                rows.append({"module": module, "name": alias.name, "asname": alias.asname or "", "line": node.lineno, "kind": "from"})
    return rows


def build_function_index(tree: ast.Module, assignments: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    internal_names = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    constants = {str(row["name"]) for row in assignments}
    rows: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls = calls_in_node(node)
        refs = names_referenced(node)
        strings = string_literals(node)
        internal_calls = sorted({simple_call_name(call) for call in calls if simple_call_name(call) in internal_names})
        constant_refs = sorted(set(refs) & constants)
        action_literals = sorted({
            value
            for value in strings
            if value.startswith(("queue_", "materialize_", "start_", "settle_", "refresh_", "classify_", "resolve_", "context_", "worker_"))
        })
        category = classify_category(node.name, strings, calls)
        risk_tags = risk_tags_for(node.name, strings, calls, refs)
        rows.append(
            {
                "name": node.name,
                "kind": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "loc": max(0, (node.end_lineno or node.lineno) - node.lineno + 1),
                "signature": signature_for_function(node),
                "doc": function_doc_summary(node),
                "category": category,
                "risk_tags": risk_tags,
                "internal_calls": internal_calls,
                "external_call_count": len([call for call in calls if simple_call_name(call) not in internal_names]),
                "constant_refs": constant_refs,
                "path_constant_refs": [ref for ref in constant_refs if ref.endswith(("_PATH", "_DIR"))],
                "action_literals": action_literals,
                "schema_ids": schema_literals(strings),
                "packet_ids": packet_literals(strings),
                "path_literals": path_like_literals(strings),
            }
        )
    return rows


def build_function_chunks(functions: Sequence[Mapping[str, Any]], chunk_size: int = 35) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for chunk_index, start in enumerate(range(0, len(functions), chunk_size), start=1):
        chunk = list(functions[start : start + chunk_size])
        if not chunk:
            continue
        categories = Counter(str(row["category"]) for row in chunk)
        risk_tags = Counter(tag for row in chunk for tag in row.get("risk_tags", []))
        chunks.append(
            {
                "region_id": f"region_{chunk_index:02d}",
                "line_start": chunk[0]["line_start"],
                "line_end": chunk[-1]["line_end"],
                "symbol_count": len(chunk),
                "first_symbol": chunk[0]["name"],
                "last_symbol": chunk[-1]["name"],
                "dominant_categories": [name for name, _count in categories.most_common(5)],
                "dominant_risk_tags": [name for name, _count in risk_tags.most_common(8)],
            }
        )
    return chunks


def build_category_regions(functions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in functions:
        grouped.setdefault(str(row["category"]), []).append(row)
    regions: list[dict[str, Any]] = []
    for category, rows in sorted(grouped.items()):
        regions.append(
            {
                "category": category,
                "line_start": min(int(row["line_start"]) for row in rows),
                "line_end": max(int(row["line_end"]) for row in rows),
                "symbol_count": len(rows),
                "symbols": [str(row["name"]) for row in rows[:60]],
                "symbols_truncated": max(0, len(rows) - 60),
            }
        )
    return sorted(regions, key=lambda item: (int(item["line_start"]), str(item["category"])))


def build_action_index(
    assignments: Sequence[Mapping[str, Any]],
    dispatcher_branches: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    allowed = extract_allowed_actions(assignments)
    read_only = set(extract_read_only_actions(assignments))
    branches_by_action: dict[str, list[Mapping[str, Any]]] = {}
    for branch in dispatcher_branches:
        branches_by_action.setdefault(str(branch["action"]), []).append(branch)
    rows: list[dict[str, Any]] = []
    for action in allowed:
        branches = branches_by_action.get(action, [])
        rows.append(
            {
                "action": action,
                "read_only_context_action": action in read_only,
                "branch_count": len(branches),
                "branch_lines": [branch["line_start"] for branch in branches],
                "risk_tags": sorted({tag for branch in branches for tag in branch.get("risk_tags", [])}),
                "internal_calls": sorted({call for branch in branches for call in branch.get("internal_calls", [])})[:50],
            }
        )
    branch_actions = set(branches_by_action)
    return {
        "allowed_action_count": len(allowed),
        "dispatcher_branch_action_count": len(branch_actions),
        "read_only_context_actions": sorted(read_only),
        "unbranched_allowed_actions": sorted(set(allowed) - branch_actions),
        "branched_actions_not_in_allowed_catalog": sorted(branch_actions - set(allowed)),
        "actions": rows,
    }


def discover_domain_weaver_modules(root: Path | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    kernel_dir = root / "ION/04_packages/kernel"
    if not kernel_dir.exists():
        return []
    rows = []
    for path in sorted(kernel_dir.glob("ion_domain_weaver*.py")):
        rows.append(
            {
                "path": rel_path(root, path),
                "bytes": path.stat().st_size,
                "lines": len(path.read_text(encoding="utf-8").splitlines()),
                "sha256": sha256_file(path),
            }
        )
    return rows


def build_domain_weaver_monolith_index_from_source(
    source_path: Path,
    *,
    root: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    source_path = Path(source_path)
    source_text = source_path.read_text(encoding="utf-8")
    lines = source_text.splitlines()
    tree = ast.parse(source_text, filename=source_path.as_posix())
    assignments = build_assignment_index(tree)
    functions = build_function_index(tree, assignments)
    internal_names = {str(row["name"]) for row in functions}
    dispatcher_branches, dispatcher_start, dispatcher_end = extract_dispatcher_branches(tree, internal_names)
    action_index = build_action_index(assignments, dispatcher_branches)
    imports = build_import_index(tree)
    path_constants = [row for row in assignments if row["category"] in {"path_constant", "directory_constant"}]
    schema_constants = [row for row in assignments if row["category"] == "schema_constant"]
    packet_constants = [row for row in assignments if row["category"] == "packet_constant"]
    category_counts = Counter(str(row["category"]) for row in functions)
    risk_counts = Counter(tag for row in functions for tag in row.get("risk_tags", []))
    high_risk_symbols = [
        {
            "name": row["name"],
            "line_start": row["line_start"],
            "line_end": row["line_end"],
            "category": row["category"],
            "risk_tags": row["risk_tags"],
        }
        for row in functions
        if any(tag in set(row.get("risk_tags", [])) for tag in {"writes_file", "materialization", "accepted_state", "worker_start", "active_binding", "operator_action_history", "dispatcher"})
    ]
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": generated_at or utc_now_iso(),
        "active_root": root.as_posix() if root else "",
        "authority": {
            "candidate_index_only": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "source": {
            "path": rel_path(root, source_path),
            "sha256": sha256_bytes(source_text.encode("utf-8")),
            "bytes": len(source_text.encode("utf-8")),
            "line_count": len(lines),
        },
        "summary": {
            "top_level_function_count": len(functions),
            "top_level_assignment_count": len(assignments),
            "import_count": len(imports),
            "path_constant_count": len(path_constants),
            "schema_constant_count": len(schema_constants),
            "packet_constant_count": len(packet_constants),
            "allowed_action_count": action_index["allowed_action_count"],
            "dispatcher_branch_action_count": action_index["dispatcher_branch_action_count"],
            "dispatcher_line_start": dispatcher_start,
            "dispatcher_line_end": dispatcher_end,
            "category_counts": dict(sorted(category_counts.items())),
            "risk_tag_counts": dict(sorted(risk_counts.items())),
        },
        "agent_usage": {
            "read_first": [
                "ION/05_context/current/domain_weaver/AGENTS.md",
                "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml",
                "ION/05_context/current/domain_weaver/monolith_index/DOMAIN_WEAVER_MONOLITH_INDEX.latest.md",
                "ION/05_context/current/domain_weaver/monolith_index/DOMAIN_WEAVER_MONOLITH_INDEX.latest.json",
            ],
            "regenerate_command": "PYTHONPATH=ION/04_packages python3 -m kernel.ion_domain_weaver_monolith_index --root . --write",
            "editing_rule": "Use line spans and risk tags to pick the narrowest symbol or category before editing ion_domain_weaver.py.",
        },
        "imports": imports,
        "source_regions": build_function_chunks(functions),
        "category_regions": build_category_regions(functions),
        "constants": assignments,
        "path_constants": path_constants,
        "schema_constants": schema_constants,
        "packet_constants": packet_constants,
        "functions": functions,
        "symbols_by_name": {str(row["name"]): {"line_start": row["line_start"], "line_end": row["line_end"], "category": row["category"]} for row in functions},
        "action_index": action_index,
        "dispatcher_branches": dispatcher_branches,
        "high_risk_symbols": high_risk_symbols,
        "sibling_domain_weaver_modules": discover_domain_weaver_modules(root),
        "non_claims": [
            "This index does not import or execute ion_domain_weaver.py.",
            "This index does not claim materialization readiness, accepted state, production authority, live execution authority, or secrets authority.",
            "Generated line spans are navigation aids; re-run after source edits before relying on them.",
        ],
    }


def build_domain_weaver_monolith_index(
    root: Path | str | None = None,
    *,
    source_path: Path | str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve() if root is not None else Path.cwd().resolve()
    source = Path(source_path) if source_path is not None else root_path / DEFAULT_SOURCE_PATH
    if not source.is_absolute():
        source = root_path / source
    return build_domain_weaver_monolith_index_from_source(source, root=root_path, generated_at=generated_at)


def render_domain_weaver_monolith_index_markdown(index: Mapping[str, Any]) -> str:
    source = dict(index.get("source") or {})
    summary = dict(index.get("summary") or {})
    action_index = dict(index.get("action_index") or {})
    regions = list(index.get("source_regions") or [])
    category_regions = list(index.get("category_regions") or [])
    high_risk = list(index.get("high_risk_symbols") or [])
    modules = list(index.get("sibling_domain_weaver_modules") or [])
    lines = [
        "# Domain Weaver Monolith Index",
        "",
        f"Generated: `{index.get('generated_at', '')}`",
        "",
        "Authority: candidate navigation artifact only. It does not import or execute the monolith and grants no production, live execution, accepted-state, or secrets authority.",
        "",
        "## Source",
        "",
        f"- Path: `{source.get('path', '')}`",
        f"- SHA256: `{source.get('sha256', '')}`",
        f"- Lines: `{source.get('line_count', 0)}`",
        f"- Top-level functions: `{summary.get('top_level_function_count', 0)}`",
        f"- Top-level assignments/constants: `{summary.get('top_level_assignment_count', 0)}`",
        f"- Allowed operator actions: `{summary.get('allowed_action_count', 0)}`",
        f"- Dispatcher branch actions detected: `{summary.get('dispatcher_branch_action_count', 0)}`",
        "",
        "## How Future Agents Should Use This",
        "",
        "1. Read the folder-local Domain Weaver `AGENTS.md` and `.ion` capsule first.",
        "2. Search this Markdown for the area name, action name, risk tag, or function name.",
        "3. Open the JSON index for the full symbol record, calls, constants, and exact line spans.",
        "4. Re-run the index before editing if `ion_domain_weaver.py` changed.",
        "",
        "Regenerate:",
        "",
        "```bash",
        str(dict(index.get("agent_usage") or {}).get("regenerate_command", "")),
        "```",
        "",
        "## Source Regions",
        "",
        "| Region | Lines | Symbols | Dominant Categories | Dominant Risk Tags | First -> Last |",
        "|---|---:|---:|---|---|---|",
    ]
    for row in regions:
        lines.append(
            "| {region_id} | {line_start}-{line_end} | {symbol_count} | {categories} | {risks} | `{first}` -> `{last}` |".format(
                region_id=row.get("region_id", ""),
                line_start=row.get("line_start", ""),
                line_end=row.get("line_end", ""),
                symbol_count=row.get("symbol_count", ""),
                categories=", ".join(row.get("dominant_categories") or []),
                risks=", ".join(row.get("dominant_risk_tags") or []),
                first=row.get("first_symbol", ""),
                last=row.get("last_symbol", ""),
            )
        )
    lines.extend([
        "",
        "## Category Regions",
        "",
        "| Category | Lines | Symbol Count | First Symbols |",
        "|---|---:|---:|---|",
    ])
    for row in category_regions:
        symbols = ", ".join(f"`{name}`" for name in (row.get("symbols") or [])[:8])
        truncated = int(row.get("symbols_truncated") or 0)
        if truncated:
            symbols += f", ... +{truncated}"
        lines.append(
            f"| {row.get('category', '')} | {row.get('line_start', '')}-{row.get('line_end', '')} | {row.get('symbol_count', '')} | {symbols} |"
        )
    lines.extend([
        "",
        "## Dispatcher Action Index",
        "",
        f"- Read-only context actions: `{', '.join(action_index.get('read_only_context_actions') or [])}`",
        f"- Unbranched allowed actions detected: `{len(action_index.get('unbranched_allowed_actions') or [])}`",
        f"- Branched actions outside allowed catalog: `{len(action_index.get('branched_actions_not_in_allowed_catalog') or [])}`",
        "",
        "| Action | Branch Lines | Read Only | Risk Tags | Key Internal Calls |",
        "|---|---:|---|---|---|",
    ])
    for row in action_index.get("actions") or []:
        calls = ", ".join(f"`{call}`" for call in (row.get("internal_calls") or [])[:8])
        lines.append(
            "| `{action}` | {lines_} | {read_only} | {risks} | {calls} |".format(
                action=row.get("action", ""),
                lines_=", ".join(str(item) for item in row.get("branch_lines") or []),
                read_only="yes" if row.get("read_only_context_action") else "no",
                risks=", ".join(row.get("risk_tags") or []),
                calls=calls,
            )
        )
    lines.extend([
        "",
        "## High-Risk Symbol Shortlist",
        "",
        "Full risk detail is in the JSON. This list is for quick triage before touching the monolith.",
        "",
        "| Symbol | Lines | Category | Risk Tags |",
        "|---|---:|---|---|",
    ])
    for row in high_risk[:120]:
        lines.append(
            f"| `{row.get('name', '')}` | {row.get('line_start', '')}-{row.get('line_end', '')} | {row.get('category', '')} | {', '.join(row.get('risk_tags') or [])} |"
        )
    if len(high_risk) > 120:
        lines.append(f"| ... | ... | ... | {len(high_risk) - 120} more in JSON |")
    lines.extend([
        "",
        "## Domain Weaver Sibling Modules",
        "",
        "| Module | Lines | Bytes | SHA256 |",
        "|---|---:|---:|---|",
    ])
    for row in modules:
        lines.append(f"| `{row.get('path', '')}` | {row.get('lines', '')} | {row.get('bytes', '')} | `{row.get('sha256', '')}` |")
    lines.extend([
        "",
        "## Non-Claims",
        "",
    ])
    for item in index.get("non_claims") or []:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def write_domain_weaver_monolith_index(
    root: Path | str | None = None,
    *,
    source_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve() if root is not None else Path.cwd().resolve()
    index = build_domain_weaver_monolith_index(root_path, source_path=source_path, generated_at=generated_at)
    target_dir = Path(output_dir) if output_dir is not None else root_path / DEFAULT_OUTPUT_DIR
    if not target_dir.is_absolute():
        target_dir = root_path / target_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / DEFAULT_INDEX_JSON_NAME
    md_path = target_dir / DEFAULT_INDEX_MD_NAME
    json_text = stable_json_text(index)
    md_text = render_domain_weaver_monolith_index_markdown(index)
    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    return {
        "ok": True,
        "json_path": rel_path(root_path, json_path),
        "json_sha256": sha256_bytes(json_text.encode("utf-8")),
        "markdown_path": rel_path(root_path, md_path),
        "markdown_sha256": sha256_bytes(md_text.encode("utf-8")),
        "source_sha256": dict(index.get("source") or {}).get("sha256"),
        "summary": index.get("summary"),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Domain Weaver monolith navigation index.")
    parser.add_argument("--root", default=".", help="ION active root. Defaults to current directory.")
    parser.add_argument("--source-path", default=None, help="Optional monolith source path relative to root.")
    parser.add_argument("--output-dir", default=None, help="Optional output directory relative to root.")
    parser.add_argument("--write", action="store_true", help="Write latest JSON and Markdown artifacts.")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.write:
        result = write_domain_weaver_monolith_index(
            root,
            source_path=args.source_path,
            output_dir=args.output_dir,
        )
        print(stable_json_text(result), end="")
        return 0
    index = build_domain_weaver_monolith_index(root, source_path=args.source_path)
    print(stable_json_text(index), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
