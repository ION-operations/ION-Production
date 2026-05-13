#!/usr/bin/env python3
"""
AIM-OS SSE MCP Server for ChatGPT Integration

Exposes AIM-OS MCP tools via SSE transport for native ChatGPT App connection.
Uses FastMCP framework matching OpenAI's reference implementation.

Usage:
    python scripts/mcp_sse_server.py
    
Then expose via ngrok:
    ngrok http 8000

Paste the ngrok HTTPS URL into ChatGPT App creation screen.

Does NOT replace:
    - Cursor stdio MCP (lucid_mcp_server.py)
    - HTTP fallback (mcp_http_fallback_server.py on :5001)
"""

import sys
import os
import json
import logging
import subprocess
import shutil
from collections import deque
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

# Add repo root to path
REPO_ROOT = str(Path(__file__).parent.parent)
sys.path.insert(0, REPO_ROOT)

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aimos-sse-mcp")

# ── Data paths ──────────────────────────────────────────────────────
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
MEMORY_DIR = os.path.join(REPO_ROOT, "data", "memory")
MESSAGES_FILE = os.path.join(DATA_DIR, "mcp_ai_messages.json")
TIMELINE_FILE = os.path.join(DATA_DIR, "mcp_timeline_entries.json")

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

# ── Load existing lucid_mcp_server for delegate calls ──────────────
def _load_lucid_server():
    """Load the main SimpleMCPServer to delegate tool calls."""
    try:
        import importlib.util
        server_path = os.path.join(REPO_ROOT, "lucid_mcp_server.py")
        spec = importlib.util.spec_from_file_location("lucid_mcp_server", server_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        server = mod.SimpleMCPServer(memory_directory=MEMORY_DIR)
        logger.info("SimpleMCPServer loaded successfully")
        return server
    except Exception as e:
        logger.error(f"Failed to load SimpleMCPServer: {e}")
        return None

# Global delegate
_delegate = None
_request_id = 0

def _call_delegate(tool_name: str, arguments: dict) -> Any:
    """Call a tool on the delegate SimpleMCPServer."""
    global _delegate, _request_id
    if _delegate is None:
        _delegate = _load_lucid_server()
    if _delegate is None:
        return {"error": "SimpleMCPServer not available"}
    
    _request_id += 1
    request = {
        "jsonrpc": "2.0",
        "id": _request_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    try:
        response = _delegate.handle_request(request)
        if "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                try:
                    return json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    return text
        if "error" in response:
            return {"error": response["error"].get("message", "Unknown error")}
        return response
    except Exception as e:
        logger.error(f"Delegate call failed for {tool_name}: {e}")
        return {"error": str(e)}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_read_text(rel_path: str, max_chars: int) -> Dict[str, Any]:
    abs_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
    if not os.path.exists(abs_path):
        return {
            "path": rel_path,
            "exists": False,
            "size_bytes": 0,
            "truncated": False,
            "content": "",
        }

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except UnicodeDecodeError:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except Exception as exc:
        return {
            "path": rel_path,
            "exists": True,
            "size_bytes": os.path.getsize(abs_path),
            "truncated": False,
            "content": "",
            "read_error": str(exc),
        }

    truncated = len(raw) > max_chars
    return {
        "path": rel_path,
        "exists": True,
        "size_bytes": len(raw.encode("utf-8", errors="replace")),
        "truncated": truncated,
        "content": raw[:max_chars] if truncated else raw,
    }


def _git_value(args: List[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", REPO_ROOT, *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return (result.stdout or "").strip()
    except Exception:
        return ""


def _resolve_repo_path(path_value: str) -> Tuple[bool, str]:
    repo_root = Path(REPO_ROOT).resolve()
    candidate = Path(path_value)
    abs_candidate = candidate if candidate.is_absolute() else (repo_root / candidate)
    try:
        abs_resolved = abs_candidate.resolve()
    except Exception:
        return False, f"Invalid path: {path_value}"
    if repo_root not in abs_resolved.parents and abs_resolved != repo_root:
        return False, f"Path escapes repository root: {path_value}"
    return True, str(abs_resolved)


def _normalize_relpath(abs_path: str) -> str:
    return os.path.relpath(abs_path, REPO_ROOT).replace("\\", "/")


def _list_tree_entries(root_abs: str, max_depth: int, max_entries: int) -> List[Dict[str, Any]]:
    root_path = Path(root_abs)
    if not root_path.exists():
        return []

    entries: List[Dict[str, Any]] = []
    queue = deque([(root_path, 0)])
    while queue and len(entries) < max_entries:
        current, depth = queue.popleft()
        try:
            children = sorted(list(current.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
        except Exception:
            continue

        for child in children:
            if len(entries) >= max_entries:
                break
            child_rel = _normalize_relpath(str(child))
            item: Dict[str, Any] = {
                "path": child_rel,
                "type": "dir" if child.is_dir() else "file",
                "depth": depth + 1,
            }
            if child.is_file():
                try:
                    item["size_bytes"] = child.stat().st_size
                except Exception:
                    item["size_bytes"] = None
            entries.append(item)
            if child.is_dir() and depth + 1 < max_depth:
                queue.append((child, depth + 1))

    return entries


# ── Create FastMCP server ──────────────────────────────────────────

server_instructions = """
AIM-OS MCP Server — Artificial Intelligence Memory Operating System.

You are connected to the AIM-OS team coordination infrastructure.
Use these tools to communicate with other agents, store/retrieve memories,
create plans, track goals, and monitor system quality.

Team members: Opus (COO), Braden (CEO), Codex, Gemini, Composer.
Protocol: Military comms (SITREP/WILCO/FLASH). Always coordinate.
"""

mcp = FastMCP(
    name="AIM-OS",
    instructions=server_instructions
)


# ── COMMS TOOLS ────────────────────────────────────────────────────

@mcp.tool()
async def send_ai_message(
    from_ai: str,
    to_ai: str,
    content: str,
    message_type: str = "discussion",
    priority: str = "medium",
    thread_id: str = "",
    holder_id: str = "",
    response_required: bool = False
) -> Dict[str, Any]:
    """
    Send a message to another AI agent in the AIM-OS team.
    
    Args:
        from_ai: Your agent name (e.g., "GPT 5.2")
        to_ai: Target agent or "all" for broadcast
        content: Message content
        message_type: discussion, task_handoff, problem_solving, status_update, urgent
        priority: low, medium, high, urgent
        thread_id: Optional conversation thread ID
        holder_id: Identity lock holder when sender lock is enabled
        response_required: Whether receiver response is required
    """
    args = {
        "from_ai": from_ai, "to_ai": to_ai, "content": content,
        "message_type": message_type, "priority": priority
    }
    if thread_id:
        args["thread_id"] = thread_id
    if holder_id:
        args["holder_id"] = holder_id
    args["response_required"] = bool(response_required)
    return _call_delegate("send_ai_message", args)


@mcp.tool()
async def get_ai_messages(
    to_ai: str = "",
    from_ai: str = "",
    limit: int = 20,
    message_type: str = "",
    thread_id: str = "",
    content_search: str = "",
    normalize_names: bool = True
) -> Dict[str, Any]:
    """
    Retrieve messages from the AI communication bus.
    
    Args:
        to_ai: Filter by recipient
        from_ai: Filter by sender
        limit: Max messages to return
        message_type: Filter by type
        thread_id: Filter by thread
        content_search: Keyword filter for message content
        normalize_names: Enable canonical/alias name normalization
    """
    args = {"limit": limit}
    if to_ai: args["to_ai"] = to_ai
    if from_ai: args["from_ai"] = from_ai
    if message_type: args["message_type"] = message_type
    if thread_id: args["thread_id"] = thread_id
    if content_search: args["content_search"] = content_search
    args["normalize_names"] = bool(normalize_names)
    return _call_delegate("get_ai_messages", args)


# ── MEMORY TOOLS ───────────────────────────────────────────────────

@mcp.tool()
async def store_memory(
    content: str,
    tags: Dict[str, Any] = {}
) -> Dict[str, Any]:
    """
    Store information in AIM-OS persistent memory.
    Use after completing tasks, learning insights, or making decisions.
    
    Args:
        content: The information to store
        tags: Optional tags for categorization (e.g., {"category": "plan", "priority": "high"})
    """
    return _call_delegate("store_memory", {"content": content, "tags": tags})


@mcp.tool()
async def retrieve_memory(
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search and retrieve memories from AIM-OS persistent memory.
    
    Args:
        query: Search query for memories
        limit: Maximum number of memories to return
    """
    return _call_delegate("retrieve_memory", {"query": query, "limit": limit})


@mcp.tool()
async def get_memory_stats() -> Dict[str, Any]:
    """Get statistics about the AIM-OS memory system."""
    return _call_delegate("get_memory_stats", {})


# ── PLANNING TOOLS ─────────────────────────────────────────────────

@mcp.tool()
async def create_plan(
    goal: str,
    context: str = "",
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create an execution plan for a complex task.
    
    Args:
        goal: The goal to achieve
        context: Current context and constraints
        priority: low, medium, high, critical
    """
    args = {"goal": goal, "priority": priority}
    if context: args["context"] = context
    return _call_delegate("create_plan", args)


@mcp.tool()
async def create_goal_timeline_node(
    goal_id: str,
    name: str,
    description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a goal as a timeline planning node.
    
    Args:
        goal_id: Goal identifier (e.g., "OBJ-01")
        name: Goal name
        description: Goal description
        priority: critical, high, medium, low
    """
    return _call_delegate("create_goal_timeline_node", {
        "goal_id": goal_id, "name": name,
        "description": description, "priority": priority
    })


@mcp.tool()
async def update_goal_progress(
    goal_id: str,
    progress: float,
    status: str = "in_progress",
    milestone: str = ""
) -> Dict[str, Any]:
    """
    Update goal progress and status.
    
    Args:
        goal_id: Goal identifier
        progress: Progress (0.0 to 1.0)
        status: planned, in_progress, completed, blocked, cancelled
        milestone: Optional milestone description
    """
    args = {"goal_id": goal_id, "progress": progress, "status": status}
    if milestone: args["milestone"] = milestone
    return _call_delegate("update_goal_progress", args)


# ── QUALITY TOOLS ──────────────────────────────────────────────────

@mcp.tool()
async def track_confidence(
    task: str,
    confidence: float,
    reasoning: str = "",
    evidence: List[str] = []
) -> Dict[str, Any]:
    """
    Track confidence and provenance for a task or decision.
    MANDATORY during analysis and before major decisions.
    
    Args:
        task: Task being tracked
        confidence: Confidence level (0.0 to 1.0)
        reasoning: Reasoning for confidence level
        evidence: Supporting evidence list
    """
    args = {"task": task, "confidence": confidence}
    if reasoning: args["reasoning"] = reasoning
    if evidence: args["evidence"] = evidence
    return _call_delegate("track_confidence", args)


# ── TIMELINE TOOLS ─────────────────────────────────────────────────

@mcp.tool()
async def add_timeline_entry(
    prompt_id: str,
    user_input: str,
    context_state: Dict[str, Any] = {}
) -> Dict[str, Any]:
    """
    Track context at each prompt in the timeline.
    Use after completing major tasks or reaching milestones.
    
    Args:
        prompt_id: Unique prompt identifier
        user_input: User input for this prompt
        context_state: Current context state
    """
    args = {"prompt_id": prompt_id, "user_input": user_input}
    if context_state: args["context_state"] = context_state
    return _call_delegate("add_timeline_entry", args)


@mcp.tool()
async def get_timeline_summary(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent timeline entries for context restoration.
    Use at session start.
    
    Args:
        limit: Number of recent entries to return
    """
    return _call_delegate("get_timeline_summary", {"limit": limit})


# ── KNOWLEDGE TOOLS ────────────────────────────────────────────────

@mcp.tool()
async def synthesize_knowledge(
    topics: List[str],
    depth: str = "medium",
    format: str = "summary"
) -> Dict[str, Any]:
    """
    Synthesize knowledge across topics from AIM-OS memory.
    
    Args:
        topics: Topics to synthesize
        depth: shallow, medium, deep
        format: summary, detailed, structured
    """
    return _call_delegate("synthesize_knowledge", {
        "topics": topics, "depth": depth, "format": format
    })


# ── COLLABORATION TOOLS ───────────────────────────────────────────

@mcp.tool()
async def get_ai_collaboration_summary() -> Dict[str, Any]:
    """Get summary of AI collaboration activity and metrics."""
    return _call_delegate("get_ai_collaboration_summary", {})


@mcp.tool()
async def context_pack_get_current(
    include_contents: bool = False,
    max_chars_per_file: int = 12000
) -> Dict[str, Any]:
    """
    Return a compact, canonical "current truth" context pack for external ChatGPT sync.

    Args:
        include_contents: Include trimmed text content for key files.
        max_chars_per_file: Truncation cap per included file.
    """
    if max_chars_per_file < 500:
        max_chars_per_file = 500
    if max_chars_per_file > 50000:
        max_chars_per_file = 50000

    key_files = [
        "context/00_operational_definition.md",
        "context/01_current_truth.md",
        "context/02_canonical_map.md",
        "context/03_tonight_plan.md",
        "context/99_nightly_sync_capsule.md",
        "PROJECT_TRUTH/02_canonical_doc_index.md",
        "PROJECT_TRUTH/03_already_built_registry.md",
        "PROJECT_TRUTH/05_operational_definition.md",
        "PROJECT_TRUTH/07_next_bounded_task.md",
    ]

    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "--short", "HEAD"])

    files_payload = []
    for rel_path in key_files:
        entry = _safe_read_text(rel_path, max_chars_per_file)
        if not include_contents:
            entry.pop("content", None)
        files_payload.append(entry)

    return {
        "success": True,
        "generated_at": _utc_now_iso(),
        "transport": "sse",
        "branch": branch or None,
        "commit": commit or None,
        "files": files_payload,
        "summary": {
            "total_files": len(key_files),
            "existing_files": sum(1 for f in files_payload if f.get("exists")),
            "missing_files": [f.get("path") for f in files_payload if not f.get("exists")],
            "include_contents": bool(include_contents),
            "max_chars_per_file": max_chars_per_file,
        },
    }


@mcp.tool()
async def repo_read_file(
    path: str,
    max_chars: int = 12000
) -> Dict[str, Any]:
    """
    Read a repository file safely (read-only).

    Args:
        path: Repo-relative or absolute path under repo root.
        max_chars: Max characters to return.
    """
    if max_chars < 200:
        max_chars = 200
    if max_chars > 100000:
        max_chars = 100000

    ok, resolved = _resolve_repo_path(path)
    if not ok:
        return {"success": False, "error": resolved}

    rel = _normalize_relpath(resolved)
    payload = _safe_read_text(rel, max_chars)
    payload["success"] = bool(payload.get("exists"))
    if not payload.get("exists"):
        payload["error"] = f"File not found: {rel}"
    return payload


@mcp.tool()
async def repo_list_tree(
    root: str = ".",
    max_depth: int = 3,
    max_entries: int = 500
) -> Dict[str, Any]:
    """
    List repository tree entries from a root path (read-only).

    Args:
        root: Repo-relative or absolute root path under repository.
        max_depth: Maximum depth to traverse.
        max_entries: Maximum total entries to return.
    """
    if max_depth < 1:
        max_depth = 1
    if max_depth > 10:
        max_depth = 10
    if max_entries < 1:
        max_entries = 1
    if max_entries > 5000:
        max_entries = 5000

    ok, resolved = _resolve_repo_path(root)
    if not ok:
        return {"success": False, "error": resolved}
    if not os.path.isdir(resolved):
        return {"success": False, "error": f"Not a directory: {root}"}

    entries = _list_tree_entries(resolved, max_depth, max_entries)
    return {
        "success": True,
        "root": _normalize_relpath(resolved),
        "max_depth": max_depth,
        "max_entries": max_entries,
        "returned_entries": len(entries),
        "entries": entries,
    }


@mcp.tool()
async def repo_search(
    query: str,
    roots: List[str] = [],
    max_results: int = 100,
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Search repository text using ripgrep (read-only).

    Args:
        query: Search query string.
        roots: Optional list of root directories/files to search.
        max_results: Max matching lines to return.
        case_sensitive: Case-sensitive search.
    """
    if not query or not query.strip():
        return {"success": False, "error": "query is required"}

    if max_results < 1:
        max_results = 1
    if max_results > 2000:
        max_results = 2000

    rg_path = shutil.which("rg")
    if not rg_path:
        return {"success": False, "error": "ripgrep (rg) not found on system path"}

    target_args: List[str] = []
    if roots:
        for root in roots:
            ok, resolved = _resolve_repo_path(root)
            if not ok:
                return {"success": False, "error": resolved}
            target_args.append(resolved)
    else:
        target_args.append(REPO_ROOT)

    cmd = [
        rg_path,
        "--line-number",
        "--no-heading",
        "--color",
        "never",
        "--hidden",
        "-g",
        "!.git",
    ]
    if not case_sensitive:
        cmd.append("-i")
    cmd.extend([query, *target_args])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=REPO_ROOT,
        )
    except Exception as exc:
        return {"success": False, "error": f"search execution failed: {exc}"}

    lines = [line for line in (proc.stdout or "").splitlines() if line.strip()]
    matches = []
    for line in lines[:max_results]:
        # Format: path:line:content
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        raw_path, raw_line, raw_text = parts
        try:
            line_no = int(raw_line)
        except ValueError:
            line_no = None
        rel_path = _normalize_relpath(raw_path) if os.path.isabs(raw_path) else raw_path.replace("\\", "/")
        matches.append({
            "path": rel_path,
            "line": line_no,
            "text": raw_text,
        })

    return {
        "success": True,
        "query": query,
        "case_sensitive": bool(case_sensitive),
        "max_results": max_results,
        "returned_results": len(matches),
        "truncated": len(lines) > max_results,
        "matches": matches,
    }


@mcp.tool()
async def repo_diff_since(
    commit: str,
    paths: List[str] = [],
    include_patch: bool = False,
    max_patch_chars: int = 20000
) -> Dict[str, Any]:
    """
    Get git diff summary (and optional patch) since a commit (read-only).

    Args:
        commit: Base commit/tag/ref.
        paths: Optional repo-relative path filters.
        include_patch: Include unified patch text.
        max_patch_chars: Max patch chars when include_patch=true.
    """
    if not commit or not commit.strip():
        return {"success": False, "error": "commit is required"}

    git_base = ["git", "-C", REPO_ROOT]
    filtered_paths: List[str] = []
    for path in paths:
        ok, resolved = _resolve_repo_path(path)
        if not ok:
            return {"success": False, "error": resolved}
        filtered_paths.append(_normalize_relpath(resolved))

    name_status_cmd = [*git_base, "diff", "--name-status", commit]
    if filtered_paths:
        name_status_cmd.extend(["--", *filtered_paths])

    try:
        ns_proc = subprocess.run(
            name_status_cmd,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        return {"success": False, "error": f"git diff failed: {exc}"}

    if ns_proc.returncode not in (0, 1):
        stderr = (ns_proc.stderr or "").strip()
        return {"success": False, "error": stderr or f"git diff returned {ns_proc.returncode}"}

    changed_files = []
    for line in (ns_proc.stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            changed_files.append({
                "status": parts[0],
                "path": parts[1].replace("\\", "/"),
            })

    patch_text = ""
    patch_truncated = False
    if include_patch:
        if max_patch_chars < 500:
            max_patch_chars = 500
        if max_patch_chars > 200000:
            max_patch_chars = 200000

        patch_cmd = [*git_base, "diff", "--unified=2", commit]
        if filtered_paths:
            patch_cmd.extend(["--", *filtered_paths])
        try:
            patch_proc = subprocess.run(
                patch_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            patch_text = patch_proc.stdout or ""
            patch_truncated = len(patch_text) > max_patch_chars
            if patch_truncated:
                patch_text = patch_text[:max_patch_chars]
        except Exception as exc:
            patch_text = f"[patch unavailable: {exc}]"

    return {
        "success": True,
        "commit": commit,
        "paths": filtered_paths,
        "changed_count": len(changed_files),
        "changed_files": changed_files,
        "include_patch": bool(include_patch),
        "patch_truncated": patch_truncated,
        "patch": patch_text if include_patch else "",
    }


# ── INFRASTRUCTURE TOOLS ───────────────────────────────────────────

_server_start_time = datetime.now(timezone.utc)
_tool_call_count = 0

@mcp.tool()
async def infra_health() -> Dict[str, Any]:
    """
    Get infrastructure health status for all AIM-OS services.
    Use this to check if services are running and healthy.
    Returns status of SSE server, memory system, and connectivity.
    """
    global _tool_call_count
    _tool_call_count += 1

    uptime_seconds = (datetime.now(timezone.utc) - _server_start_time).total_seconds()

    # Check memory system
    memory_ok = False
    try:
        stats = _call_delegate("get_memory_stats", {})
        memory_ok = not isinstance(stats, dict) or "error" not in stats
    except Exception:
        pass

    # Check data directories
    data_ok = os.path.isdir(DATA_DIR) and os.path.isdir(MEMORY_DIR)

    services = {
        "mcp_sse_server": {
            "status": "UP",
            "uptime_seconds": round(uptime_seconds, 1),
            "port": 8000,
            "tool_calls": _tool_call_count,
            "transport": "sse"
        },
        "lucid_mcp_core": {
            "status": "UP" if memory_ok else "DOWN",
            "delegate_loaded": _delegate is not None,
        },
        "data_layer": {
            "status": "UP" if data_ok else "DOWN",
            "data_dir": DATA_DIR,
            "memory_dir": MEMORY_DIR,
        },
    }

    all_up = all(s["status"] == "UP" for s in services.values())

    return {
        "ok": all_up,
        "status": "UP" if all_up else "DEGRADED",
        "timestamp": _utc_now_iso(),
        "server_version": "2.0.0",
        "uptime_seconds": round(uptime_seconds, 1),
        "services": services,
    }


# ── Entry point ────────────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("AIM-OS SSE MCP Server v2.0")
    logger.info("Transport: SSE (Server-Sent Events)")
    logger.info("Host: 0.0.0.0:8000")
    logger.info("Tools: 19 (comms, memory, planning, quality, timeline, knowledge, context, repo, infra)")
    logger.info("")
    logger.info("Next: Run 'python scripts/ngrok_tunnel.py' and paste URL into ChatGPT App")
    logger.info("=" * 60)
    
    mcp.run(transport="sse", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()


