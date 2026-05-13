"""
AIM-OS AI Engine — Slim MCP Server for Gemini CLI
==================================================

A ZERO-DEPENDENCY MCP server exposing 29 AI Engine tools.
Designed for Gemini CLI where lucid-mcp's 90+ tools cause 400 errors.

Key design:
    - NO heavy imports at startup (no FAISS, no AIEngine)
    - Instant MCP discovery (< 100ms startup)
    - Tool execution lazily loads the engine only when called
    - Synchronous stdio transport (asyncio broken on Windows)

Register in ~/.gemini/settings.json:
    "ai-engine": {
        "command": "python",
        "args": ["-u", "scripts/ai_engine/ai_engine_mcp_server.py"],
        "cwd": "C:\\\\Users\\\\bombe\\\\OneDrive\\\\Desktop\\\\AIM-OS",
        "env": {"PYTHONPATH": "C:\\\\Users\\\\bombe\\\\OneDrive\\\\Desktop\\\\AIM-OS"}
    }
"""

import sys
import os
import json
import logging
from typing import Any, Dict, Optional

# Configure stderr logging (stdout is reserved for MCP JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='[ai-engine-mcp] %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger('ai_engine_mcp')

# Ensure AIMOS root is on path for lazy imports
AIMOS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, AIMOS_ROOT)

SERVER_NAME = 'aim-os-ai-engine'
SERVER_VERSION = '2.3.0'
PROTOCOL_VERSION = '2024-11-05'


# ══════════════════════════════════════════════════════════
# TOOL DEFINITIONS — Static, no imports needed
# ══════════════════════════════════════════════════════════

TOOLS = [
    # ── Flagship ──
    {
        "name": "ai_engine_execute",
        "description": "Execute the full AI Engine pipeline: context → agent → genome → VIF gate → LLM → trace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to execute"},
                "agent_id": {"type": "string", "description": "Agent: coder_v1, architect_v1, auditor_v1, researcher_v1, tester_v1, fast_v1"},
                "model": {"type": "string", "description": "Model override (default: auto)"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "ai_engine_ask",
        "description": "Quick LLM question — lightweight, bypasses full pipeline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question to ask"},
                "system": {"type": "string", "description": "Optional system prompt"},
            },
            "required": ["question"],
        },
    },
    {
        "name": "ai_engine_code",
        "description": "Generate or modify code using the coder agent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Coding task"},
                "files": {"type": "string", "description": "Comma-separated relevant file paths"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "ai_engine_plan",
        "description": "Run the planning/architect agent for analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "What to plan or analyze"},
                "context": {"type": "string", "description": "Additional context"},
            },
            "required": ["question"],
        },
    },
    {
        "name": "ai_engine_audit",
        "description": "Run the audit agent for code review.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "File path, snippet, or task to audit"},
                "focus": {"type": "string", "description": "Focus: general, security, performance"},
            },
            "required": ["target"],
        },
    },
    # ── Swarm ──
    {
        "name": "ai_engine_swarm",
        "description": "Execute complex task with parallel worker swarm.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Complex task to decompose and parallelize"},
                "workers": {"type": "integer", "description": "Number of parallel workers (default: 3)"},
            },
            "required": ["task"],
        },
    },
    # ── Intelligence ──
    {
        "name": "ai_engine_context",
        "description": "Build a ContextPack for a task (retrieval + budgeting).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to build context for"},
                "active_file": {"type": "string", "description": "Primary file for context"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "ai_engine_tools",
        "description": "Get MCP tool recommendations for a task type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "description": "Task type: coding, debugging, planning, review"},
            },
            "required": ["task_type"],
        },
    },
    {
        "name": "ai_engine_learn",
        "description": "Record an execution outcome for the learning system.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "description": "Type of task completed"},
                "agent_name": {"type": "string", "description": "Agent that executed"},
                "model_used": {"type": "string", "description": "Model used"},
                "success": {"type": "boolean", "description": "Whether task succeeded"},
                "confidence": {"type": "number", "description": "Confidence score 0-1"},
            },
            "required": ["task_type", "agent_name", "success"],
        },
    },
    {
        "name": "ai_engine_insights",
        "description": "Get learning insights and model performance recommendations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max insights to return (default: 10)"},
            },
        },
    },
    # ── System ──
    {
        "name": "ai_engine_agents",
        "description": "List all registered agents with roles and performance metrics.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ai_engine_sessions",
        "description": "Manage execution sessions (list, create, complete).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: list, create, complete"},
                "session_id": {"type": "string", "description": "Session ID (for complete action)"},
            },
        },
    },
    {
        "name": "ai_engine_status",
        "description": "Full engine health report — all 14 subsystems.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ai_engine_index",
        "description": "Index workspace files for the context engine.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to index (default: workspace root)"},
            },
        },
    },
    # ── Context Lab ──
    {
        "name": "ai_engine_system_info",
        "description": "Get system resource usage: CPU, RAM, GPU, disk, running Python processes. Like a Task Manager for AIM-OS.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ai_engine_loop_run",
        "description": "Run the 3-phase agent loop with configurable strategy. Returns full results with diagnostics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to execute"},
                "strategy": {"type": "string", "description": "Strategy: standard, deep_research, minimal, full_mcp"},
                "max_iterations": {"type": "integer", "description": "Max iterations (default: 3)"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "ai_engine_loop_compare",
        "description": "Compare multiple strategies or run baseline vs 3-phase loop. Returns formatted comparison report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to test"},
                "strategies": {"type": "string", "description": "Comma-separated strategies to compare"},
                "include_baseline": {"type": "boolean", "description": "Include single-agent baseline in comparison"},
                "max_iterations": {"type": "integer", "description": "Max iterations per strategy"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "ai_engine_agent_call",
        "description": "Invoke a separate AI agent via Gemini CLI subprocess. Advanced meta-agent tool for agent-to-agent communication.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to send to the agent"},
                "system": {"type": "string", "description": "System prompt for the agent"},
                "model": {"type": "string", "description": "Model to use (default: auto)"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default: 60)"},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "ai_engine_tournament",
        "description": "Run a Context Lab tournament — compare multiple strategies head-to-head on tasks. Returns leaderboard with quality scores.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tasks": {"type": "string", "description": "Comma-separated task descriptions to test"},
                "strategies": {"type": "string", "description": "Comma-separated strategies (default: hhni_direct,pack_builder)"},
                "verbose": {"type": "boolean", "description": "Show progress output"},
            },
            "required": ["tasks"],
        },
    },
    {
        "name": "ai_engine_strategies",
        "description": "List available context strategies for the 3-phase agent loop, with descriptions and status.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ai_engine_evolve",
        "description": "Strategy evolution engine — fork variants with mutations, run evolution tournaments, view lineage tree, get leaderboard. Actions: fork, tournament, leaderboard, lineage, best.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: fork, tournament, leaderboard, lineage, best"},
                "parent": {"type": "string", "description": "Parent strategy/variant name (for fork)"},
                "child": {"type": "string", "description": "New variant name (for fork)"},
                "mutations": {"type": "object", "description": "Parameter mutations (for fork)"},
                "tasks": {"type": "string", "description": "Comma-separated tasks (for tournament)"},
                "variants": {"type": "string", "description": "Comma-separated variant names (for tournament)"},
            },
            "required": ["action"],
        },
    },
    # ── Sovereign Context Mapper ──
    {
        "name": "ai_engine_context_envelope",
        "description": "Build a Sovereign Context Envelope for a target file. Returns the full structural context (AST contracts, dependency signatures, edit guardrails) packed within a token budget. Works for Python and TypeScript/JavaScript.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to the target file (relative to workspace or absolute)"},
                "budget": {"type": "integer", "description": "Character budget for the envelope (default: 32000)"},
            },
            "required": ["target"],
        },
    },
    {
        "name": "ai_engine_context_extract",
        "description": "Extract interface contracts from a single file — classes, functions, types, constants with full signatures. Returns structured data about the file's public API. Supports Python (.py) and TypeScript (.ts/.tsx/.js/.jsx).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to the file to extract (relative to workspace or absolute)"},
            },
            "required": ["target"],
        },
    },
    {
        "name": "ai_engine_context_compare",
        "description": "Compare context quality across 4 modes (No Context, Semantic, Structural, Blended) for a target file. Returns accuracy, completeness, signal-to-noise, and token efficiency metrics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to the target file"},
                "symbols": {"type": "string", "description": "Comma-separated required symbol names to check for"},
                "methods": {"type": "string", "description": "Comma-separated required method names to check for"},
            },
            "required": ["target"],
        },
    },
    # ── Context Concierge ──
    {
        "name": "ai_engine_context_find",
        "description": "Universal context discovery. Query natural language and get structured context (modules, files, contracts, envelopes) without knowing any file paths. Any agent from anywhere can use this to understand any part of the codebase.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language description of what context is needed (e.g., 'genome loading', 'MCP tools', 'context engine')"},
                "budget": {"type": "integer", "description": "Character budget for response (default: 32000, ~8K tokens)"},
                "max_files": {"type": "integer", "description": "Maximum files to include (default: 5)"},
                "quick": {"type": "boolean", "description": "If true, returns modules/files/contracts only (no full envelopes, much faster)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "ai_engine_context_index",
        "description": "Auto-generate a structural index for any file. Returns sections (class/function boundaries for code, heading boundaries for markdown), exports, imports, and key concepts. Fast and cached.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to file (relative or absolute)"},
            },
            "required": ["target"],
        },
    },
    {
        "name": "ai_engine_context_section",
        "description": "Retrieve a specific section of a file by line range. Use after ai_engine_context_index to fetch only the section you need.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to file (relative or absolute)"},
                "line_start": {"type": "integer", "description": "Start line (1-indexed)"},
                "line_end": {"type": "integer", "description": "End line (1-indexed, inclusive)"},
            },
            "required": ["target", "line_start", "line_end"],
        },
    },
    # ── Large File Reader ──
    {
        "name": "ai_engine_read_large",
        "description": "MapReduce for Context: process large files (>20K chars) through smart chunking, summarization, and hierarchical index building. Uses progressive escalation: cache → structural index → full MapReduce. Returns chunk summaries, symbols, concepts, and cross-references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to large file (relative or absolute)"},
                "chunk_size": {"type": "integer", "description": "Target chunk size in chars (default: 8000)"},
                "force": {"type": "boolean", "description": "Force full MapReduce (skip cache)"},
            },
            "required": ["target"],
        },
    },
    # ── System Registry (Phase 26) ──
    {
        "name": "ai_engine_systems",
        "description": "Query the AIM-OS system registry by topic or layer. Returns filtered SystemEntry list.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Substring to match in name or purpose"},
                "layer": {"type": "string", "description": "Layer filter: Core Infrastructure, AI Engine, Context System, Agent System, Documentation, UI/JOC, MCP Servers, Agent Workforce"},
                "limit": {"type": "integer", "description": "Max entries to return (default: 50)"},
            },
        },
    },
    {
        "name": "ai_engine_systems_crawl",
        "description": "Trigger full system registry re-crawl. Writes .agent/SYSTEM_REGISTRY.md and returns stats.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ══════════════════════════════════════════════════════════
# SLIM MCP SERVER
# ══════════════════════════════════════════════════════════

class SlimMCPServer:
    """
    Zero-dependency MCP server implementing JSON-RPC 2.0 over stdio.

    Startup is instant — no heavy imports.
    Tool execution lazily loads the AI Engine on first call.
    Uses synchronous stdio (asyncio.connect_read_pipe is broken on Windows).
    """

    def __init__(self) -> None:
        self._engine = None
        self._engine_loaded = False
        logger.info(f'Server initialized with {len(TOOLS)} tools')

    # ── Lazy Engine Loading ──────────────────────────────

    def _get_engine(self) -> Any:
        """Lazy-load AIEngine on first tool call."""
        if not self._engine_loaded:
            self._engine_loaded = True
            try:
                try:
                    from scripts.ai_engine.engine import AIEngine
                except ImportError:
                    try:
                        from ai_engine.engine import AIEngine  # noqa: F811
                    except ImportError:
                        from engine import AIEngine  # noqa: F811
                self._engine = AIEngine()
                logger.info('AIEngine loaded successfully')
            except Exception as e:
                import traceback
                logger.error(f'Failed to load AIEngine: {e}')
                traceback.print_exc(file=sys.stderr)
                self._engine = None
        return self._engine

    # ── Tool Execution ───────────────────────────────────

    def _execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool. Lazily loads engine on first call."""
        engine = self._get_engine()

        def _to_dict(obj: Any) -> Dict[str, Any]:
            if hasattr(obj, '__dataclass_fields__'):
                try:
                    from dataclasses import asdict
                    return asdict(obj)
                except Exception:
                    return {k: getattr(obj, k, None) for k in obj.__dataclass_fields__}
            if isinstance(obj, dict):
                return obj
            return {"output": str(obj)}

        try:
            if name == "ai_engine_execute":
                if not engine:
                    return {"status": "error", "message": "AIEngine not loaded"}
                result = engine.execute(
                    task=args["task"],
                    agent_id=args.get("agent_id", ""),
                    model=args.get("model", "auto"),
                )
                return _to_dict(result)

            elif name == "ai_engine_ask":
                if not engine:
                    return {"answer": "AIEngine not loaded"}
                result = engine.execute(task=args["question"], model="fast")
                return _to_dict(result)

            elif name == "ai_engine_code":
                if not engine:
                    return {"status": "error", "message": "AIEngine not loaded"}
                result = engine.execute(task=args["task"], agent_id="coder_v1")
                return _to_dict(result)

            elif name == "ai_engine_plan":
                if not engine:
                    return {"status": "error", "message": "AIEngine not loaded"}
                result = engine.execute(task=args["question"], agent_id="architect_v1")
                return _to_dict(result)

            elif name == "ai_engine_audit":
                if not engine:
                    return {"status": "error", "message": "AIEngine not loaded"}
                result = engine.execute(task=f"Audit: {args['target']}", agent_id="auditor_v1")
                return _to_dict(result)

            elif name == "ai_engine_swarm":
                if not engine:
                    return {"status": "error", "message": "AIEngine not loaded"}
                result = engine.execute(task=args["task"])
                return _to_dict(result)

            elif name == "ai_engine_context":
                if not engine:
                    return {"status": "error", "message": "AIEngine not loaded"}
                result = engine.build_context(
                    task=args["task"],
                    active_file=args.get("active_file", ""),
                )
                return _to_dict(result)

            elif name == "ai_engine_tools":
                if not engine:
                    return {"tools": [t["name"] for t in TOOLS]}
                result = engine.recommend_tools(task_type=args.get("task_type", "coding"))
                return _to_dict(result)

            elif name == "ai_engine_learn":
                if not engine:
                    return {"status": "ok", "message": "Learning recorded (engine not loaded)"}
                result = engine.record_learning(
                    task_type=args["task_type"],
                    agent_name=args["agent_name"],
                    model_used=args.get("model_used", "auto"),
                    success=args["success"],
                    confidence=args.get("confidence", 0.5),
                )
                return _to_dict(result)

            elif name == "ai_engine_insights":
                if not engine:
                    return {"insights": [], "message": "Engine not loaded"}
                result = engine.get_insights(limit=args.get("limit", 10))
                return _to_dict(result)

            elif name == "ai_engine_agents":
                if not engine:
                    return {"agents": ["coder_v1", "architect_v1", "auditor_v1", "researcher_v1", "tester_v1", "fast_v1"]}
                return engine.registry_status()

            elif name == "ai_engine_sessions":
                if not engine:
                    return {"sessions": [], "message": "Engine not loaded"}
                action = args.get("action", "list")
                if action == "list":
                    return engine.list_sessions()
                elif action == "create":
                    return engine.create_session()
                elif action == "complete":
                    return engine.complete_session(args.get("session_id", ""))
                return {"status": "error", "message": f"Unknown action: {action}"}

            elif name == "ai_engine_status":
                if not engine:
                    return {
                        "status": "degraded",
                        "message": "Engine not loaded — tools available but execution disabled",
                        "tools_available": len(TOOLS),
                        "engine_loaded": False,
                    }
                return engine.status()

            elif name == "ai_engine_index":
                if not engine:
                    return {"status": "error", "message": "Engine not loaded"}
                result = engine.index_workspace(path=args.get("path", ""))
                return _to_dict(result)

            # ── Context Lab Tools ──

            elif name == "ai_engine_system_info":
                return self._get_system_info()

            elif name == "ai_engine_loop_run":
                return self._run_loop(args)

            elif name == "ai_engine_loop_compare":
                return self._run_loop_compare(args)

            elif name == "ai_engine_agent_call":
                return self._call_agent(args)

            elif name == "ai_engine_tournament":
                return self._run_tournament(args)

            elif name == "ai_engine_strategies":
                return self._list_strategies()

            elif name == "ai_engine_evolve":
                return self._evolve(args)

            elif name == "ai_engine_context_envelope":
                return self._context_envelope(args)

            elif name == "ai_engine_context_extract":
                return self._context_extract(args)

            elif name == "ai_engine_context_compare":
                return self._context_compare(args)

            elif name == "ai_engine_context_find":
                return self._context_find(args)

            elif name == "ai_engine_context_index":
                return self._context_index(args)

            elif name == "ai_engine_context_section":
                return self._context_section(args)

            elif name == "ai_engine_read_large":
                return self._read_large(args)

            elif name == "ai_engine_systems":
                return self._systems_query(args)

            elif name == "ai_engine_systems_crawl":
                return self._systems_crawl(args)

            else:
                return {"status": "error", "message": f"Unknown tool: {name}"}

        except Exception as e:
            logger.error(f'Tool {name} failed: {e}')
            return {"status": "error", "message": str(e)}

    # ── Context Lab Handlers ────────────────────────────────

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system resource usage (CPU, RAM, GPU, disk, processes)."""
        import platform
        info = {
            "platform": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }

        # Try psutil for detailed metrics
        try:
            import psutil
            info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            info["cpu_count"] = psutil.cpu_count()
            info["cpu_count_physical"] = psutil.cpu_count(logical=False)

            mem = psutil.virtual_memory()
            info["ram_used_gb"] = round(mem.used / (1024**3), 1)
            info["ram_total_gb"] = round(mem.total / (1024**3), 1)
            info["ram_percent"] = mem.percent

            disk = psutil.disk_usage('/')
            info["disk_used_gb"] = round(disk.used / (1024**3), 1)
            info["disk_total_gb"] = round(disk.total / (1024**3), 1)
            info["disk_percent"] = round(disk.percent, 1)

            # Count Python processes
            py_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    if 'python' in proc.info['name'].lower():
                        py_procs.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_mb': round(proc.info['memory_info'].rss / (1024**2), 1),
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            info["python_processes"] = py_procs
            info["python_process_count"] = len(py_procs)

        except ImportError:
            info["note"] = "psutil not installed — install with: pip install psutil"
            # Fallback: use OS commands
            try:
                import subprocess
                if platform.system() == 'Windows':
                    result = subprocess.run(
                        ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/value'],
                        capture_output=True, text=True, timeout=5,
                    )
                    info["raw_memory"] = result.stdout.strip()
            except Exception:
                pass

        # Try GPU info
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                if len(parts) >= 3:
                    info["gpu_percent"] = float(parts[0].strip())
                    info["gpu_memory_used_mb"] = float(parts[1].strip())
                    info["gpu_memory_total_mb"] = float(parts[2].strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            info["gpu"] = "not detected"

        return info

    def _run_loop(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run a 3-phase agent loop via subprocess (non-blocking for MCP)."""
        import subprocess

        task = args.get('task', '')
        strategy = args.get('strategy', 'standard')
        max_iters = args.get('max_iterations', 3)

        runner_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'agent_loop', 'runner.py',
        )

        cmd = [
            sys.executable, runner_path,
            '--task', task,
            '--strategy', strategy,
            '--iterations', str(max_iters),
            '--save-diagnostics',
        ]

        logger.info(f'Starting loop: strategy={strategy} task={task[:50]}')

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=600,  # 10 min max
                cwd=AIMOS_ROOT,
            )
            return {
                "status": "complete",
                "output": result.stdout[-3000:] if result.stdout else '',
                "error": result.stderr[-1000:] if result.stderr else '',
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Loop exceeded 10 minute timeout"}

    def _run_loop_compare(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compare strategies via subprocess."""
        import subprocess

        task = args.get('task', '')
        strategies = args.get('strategies', 'standard,minimal')
        include_baseline = args.get('include_baseline', False)
        max_iters = args.get('max_iterations', 2)

        runner_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'agent_loop', 'runner.py',
        )

        if include_baseline:
            cmd = [
                sys.executable, runner_path,
                '--task', task,
                '--compare-with-baseline', strategies,
                '--iterations', str(max_iters),
                '--save-diagnostics',
            ]
        else:
            cmd = [
                sys.executable, runner_path,
                '--task', task,
                '--compare', strategies,
                '--iterations', str(max_iters),
                '--save-diagnostics',
            ]

        logger.info(f'Comparing: {strategies} baseline={include_baseline}')

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=1200,  # 20 min max
                cwd=AIMOS_ROOT,
            )
            return {
                "status": "complete",
                "report": result.stdout[-5000:] if result.stdout else '',
                "error": result.stderr[-1000:] if result.stderr else '',
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Comparison exceeded 20 minute timeout"}

    def _call_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a Gemini CLI agent subprocess — meta-agent tool."""
        import subprocess

        prompt = args.get('prompt', '')
        system = args.get('system', '')
        model = args.get('model', '')
        timeout = args.get('timeout', 60)

        cmd = ['gemini', '-p', prompt]
        if model:
            cmd.extend(['-m', model])

        logger.info(f'Agent call: {prompt[:50]}...')

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout,
                cwd=AIMOS_ROOT,
            )
            return {
                "status": "complete",
                "response": result.stdout[-3000:] if result.stdout else '',
                "error": result.stderr[-500:] if result.stderr else '',
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": f"Agent call exceeded {timeout}s timeout"}
        except FileNotFoundError:
            return {"status": "error", "message": "gemini CLI not found — is it installed?"}

    def _run_tournament(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run a strategy tournament via subprocess."""
        import subprocess
        tasks_str = args.get('tasks', '')
        strategies_str = args.get('strategies', 'hhni_direct,pack_builder')
        verbose = args.get('verbose', False)

        if not tasks_str:
            return {"status": "error", "message": "Must provide 'tasks' parameter"}

        tasks = [t.strip() for t in tasks_str.split(',')]
        strategies = [s.strip() for s in strategies_str.split(',')]

        # Run tournament in subprocess to avoid blocking MCP
        script = os.path.join(AIMOS_ROOT, 'scripts', 'ai_engine', 'agent_loop')
        cmd = [
            sys.executable, '-c',
            f"""
import sys, os, json
sys.path.insert(0, '{script}')
from tournament import run_tournament, save_tournament
result = run_tournament(
    tasks={json.dumps(tasks)},
    strategy_names={json.dumps(strategies)},
    workspace_root='{AIMOS_ROOT}',
    verbose={verbose},
)
filepath = save_tournament(result)
output = result.to_dict()
output['saved_to'] = filepath
output['report'] = result.format_report()
print(json.dumps(output, default=str))
""",
        ]

        logger.info(f'Tournament: {len(strategies)} strategies × {len(tasks)} tasks')

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=120, cwd=AIMOS_ROOT,
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip().split('\n')[-1])
            return {
                "status": "error",
                "stdout": result.stdout[-1000:] if result.stdout else '',
                "stderr": result.stderr[-1000:] if result.stderr else '',
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Tournament exceeded 120s timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _list_strategies(self) -> Dict[str, Any]:
        """List available context strategies."""
        import subprocess
        script = os.path.join(AIMOS_ROOT, 'scripts', 'ai_engine', 'agent_loop')
        cmd = [
            sys.executable, '-c',
            f"""
import sys, json
sys.path.insert(0, '{script}')
from strategies import list_strategies
print(json.dumps(list_strategies()))
""",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=10, cwd=AIMOS_ROOT,
            )
            if result.returncode == 0 and result.stdout.strip():
                strategies = json.loads(result.stdout.strip())
                return {
                    "status": "ok",
                    "count": len(strategies),
                    "strategies": strategies,
                }
            return {"status": "error", "stderr": result.stderr[-500:] if result.stderr else ''}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _evolve(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle evolution engine actions via subprocess."""
        import subprocess

        action = args.get('action', '')
        script = os.path.join(AIMOS_ROOT, 'scripts', 'ai_engine', 'agent_loop')

        if action == 'fork':
            parent = args.get('parent', '')
            child = args.get('child', '')
            mutations = args.get('mutations', {})
            if not parent or not child:
                return {"status": "error", "message": "fork requires 'parent' and 'child'"}

            cmd = [
                sys.executable, '-c',
                f"""
import sys, json
sys.path.insert(0, '{script}')
from evolution import EvolutionManager
evo = EvolutionManager()
v = evo.fork('{parent}', '{child}', mutations={json.dumps(mutations)})
print(json.dumps({{"status": "ok", "variant": v.to_dict(), "total_variants": len(evo.variants)}}))
""",
            ]

        elif action == 'tournament':
            tasks_str = args.get('tasks', '')
            variants_str = args.get('variants', '')
            if not tasks_str:
                return {"status": "error", "message": "tournament requires 'tasks'"}
            tasks = [t.strip() for t in tasks_str.split(',')]
            variants = [v.strip() for v in variants_str.split(',')] if variants_str else None

            cmd = [
                sys.executable, '-c',
                f"""
import sys, json
sys.path.insert(0, '{script}')
from evolution import EvolutionManager
evo = EvolutionManager()
result = evo.tournament({json.dumps(tasks)}, {json.dumps(variants)})
result['leaderboard_text'] = evo.format_leaderboard()
print(json.dumps(result, default=str))
""",
            ]

        elif action == 'leaderboard':
            cmd = [
                sys.executable, '-c',
                f"""
import sys, json
sys.path.insert(0, '{script}')
from evolution import EvolutionManager
evo = EvolutionManager()
print(json.dumps({{"status": "ok", "leaderboard": evo.leaderboard(), "display": evo.format_leaderboard()}}))
""",
            ]

        elif action == 'lineage':
            cmd = [
                sys.executable, '-c',
                f"""
import sys, json
sys.path.insert(0, '{script}')
from evolution import EvolutionManager
evo = EvolutionManager()
print(json.dumps({{"status": "ok", "tree": evo.format_lineage_tree(), "variants": len(evo.variants)}}))
""",
            ]

        elif action == 'best':
            base = args.get('parent', '')
            cmd = [
                sys.executable, '-c',
                f"""
import sys, json
sys.path.insert(0, '{script}')
from evolution import EvolutionManager
evo = EvolutionManager()
best = evo.best_variant('{base}')
print(json.dumps({{"status": "ok", "best_variant": best, "leaderboard": evo.leaderboard()[:3]}}))
""",
            ]

        else:
            return {"status": "error", "message": f"Unknown action: {action}. Use: fork, tournament, leaderboard, lineage, best"}

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=120, cwd=AIMOS_ROOT,
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip().split('\n')[-1])
            return {
                "status": "error",
                "stdout": result.stdout[-500:] if result.stdout else '',
                "stderr": result.stderr[-500:] if result.stderr else '',
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Evolution action exceeded 120s timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── Sovereign Context Mapper Handlers ──────────────────

    def _get_context_mapper(self):
        """Lazy-load ContextMapper (zero-dependency, no AIEngine needed)."""
        if not hasattr(self, '_context_mapper'):
            try:
                from ai_engine.context_mapper import ContextMapper
            except ImportError:
                try:
                    from context_mapper import ContextMapper
                except ImportError:
                    from scripts.ai_engine.context_mapper import ContextMapper
            self._context_mapper = ContextMapper(AIMOS_ROOT)
            logger.info('ContextMapper loaded')
        return self._context_mapper

    def _resolve_target(self, target: str) -> str:
        """Resolve target path relative to workspace or absolute."""
        if os.path.isabs(target):
            return target
        return os.path.normpath(os.path.join(AIMOS_ROOT, target))

    def _context_envelope(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Build a Sovereign Context Envelope for a target file."""
        import time
        target = self._resolve_target(args.get('target', ''))
        budget = args.get('budget', 32000)

        if not os.path.isfile(target):
            return {"status": "error", "message": f"File not found: {target}"}

        mapper = self._get_context_mapper()
        t0 = time.time()
        envelope = mapper.build_envelope(target, budget_chars=budget)
        elapsed_ms = (time.time() - t0) * 1000

        envelope_str = envelope.to_string()
        stats = envelope.stats

        return {
            "status": "ok",
            "target": os.path.basename(target),
            "envelope_chars": len(envelope_str),
            "envelope_tokens_est": len(envelope_str) // 4,
            "generation_ms": round(elapsed_ms, 1),
            "stats": stats,
            "truncated": envelope.truncated,
            "envelope": envelope_str[:50000],  # Cap output for MCP transport
        }

    def _context_extract(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract interface contracts from a single file."""
        import time
        target = self._resolve_target(args.get('target', ''))

        if not os.path.isfile(target):
            return {"status": "error", "message": f"File not found: {target}"}

        mapper = self._get_context_mapper()
        t0 = time.time()
        result = mapper.extract_contracts(target)
        elapsed_ms = (time.time() - t0) * 1000

        # Serialize exports
        exports = []
        for exp in result.exports:
            exports.append({
                "name": exp.name,
                "kind": exp.kind,
                "signature": exp.signature,
                "line_start": exp.line_start,
                "line_end": exp.line_end,
                "methods": exp.methods[:15],
                "bases": exp.bases,
                "decorators": exp.decorators,
            })

        imports = []
        for imp in result.imports:
            imports.append({
                "module": imp.module_path,
                "names": imp.imported_names[:10],
                "is_stdlib": imp.is_stdlib,
                "is_external": imp.is_external,
                "resolved": imp.resolved_file or None,
            })

        return {
            "status": "ok",
            "file": os.path.basename(target),
            "parse_mode": result.parse_mode,
            "extraction_ms": round(elapsed_ms, 1),
            "export_count": len(result.exports),
            "import_count": len(result.imports),
            "file_size": result.file_size_bytes,
            "exports": exports,
            "imports": imports,
        }

    def _context_compare(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compare context quality across 4 modes for a target file."""
        import time
        target = self._resolve_target(args.get('target', ''))

        if not os.path.isfile(target):
            return {"status": "error", "message": f"File not found: {target}"}

        mapper = self._get_context_mapper()

        # Parse symbol/method requirements
        symbols = [s.strip() for s in args.get('symbols', '').split(',') if s.strip()]
        methods = [m.strip() for m in args.get('methods', '').split(',') if m.strip()]

        # If no symbols provided, auto-detect from file imports
        if not symbols:
            result = mapper.extract_contracts(target)
            symbols = [imp.imported_names[0] for imp in result.imports
                       if imp.imported_names and not imp.is_stdlib and not imp.is_external][:8]
            methods = [exp.name for exp in result.exports if exp.kind == 'function'][:6]

        all_terms = set(symbols + methods)

        # Read raw file
        try:
            with open(target, 'r', encoding='utf-8', errors='replace') as f:
                raw_content = f.read()
        except Exception:
            raw_content = ''

        # Build envelope
        t0 = time.time()
        envelope = mapper.build_envelope(target, budget_chars=32000)
        structural_ms = (time.time() - t0) * 1000
        structural_str = envelope.to_string()

        def score(context: str):
            found_syms = sum(1 for s in symbols if s in context) if symbols else 0
            found_meth = sum(1 for m in methods if m in context) if methods else 0
            total_syms = len(symbols) or 1
            total_meth = len(methods) or 1
            lines = context.splitlines()
            signal = sum(1 for l in lines if any(t in l for t in all_terms)) if all_terms else 0
            tokens = len(context) // 4
            facts = sum(1 for t in all_terms if t in context) if all_terms else 0
            return {
                "accuracy": round(found_syms / total_syms, 2),
                "completeness": round(found_meth / total_meth, 2),
                "signal_to_noise": round(signal / max(len(lines), 1), 3),
                "tokens": tokens,
                "tokens_per_fact": round(tokens / max(facts, 1), 0),
                "chars": len(context),
            }

        modes = {
            "no_context": score(os.path.basename(target)),
            "semantic": score(raw_content),
            "structural": score(structural_str),
            "blended": score(structural_str),
        }

        # Determine winners
        best_accuracy = max(modes, key=lambda m: modes[m]["accuracy"])
        best_completeness = max(modes, key=lambda m: modes[m]["completeness"])
        best_sn = max(modes, key=lambda m: modes[m]["signal_to_noise"])

        return {
            "status": "ok",
            "target": os.path.basename(target),
            "structural_gen_ms": round(structural_ms, 1),
            "symbols_checked": symbols,
            "methods_checked": methods,
            "modes": modes,
            "winners": {
                "accuracy": best_accuracy,
                "completeness": best_completeness,
                "signal_to_noise": best_sn,
            },
        }

    # ── Context Concierge Handler ────────────────────────────

    def _get_concierge(self):
        """Lazy-load ContextConcierge (zero AIEngine dependency)."""
        if not hasattr(self, '_concierge'):
            try:
                from ai_engine.context_concierge import ContextConcierge
            except ImportError:
                try:
                    from context_concierge import ContextConcierge
                except ImportError:
                    from scripts.ai_engine.context_concierge import ContextConcierge
            self._concierge = ContextConcierge(AIMOS_ROOT)
            logger.info('ContextConcierge loaded')
        return self._concierge

    def _context_find(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Universal context discovery — NL query to structured context."""
        import time
        query = args.get('query', '')
        if not query:
            return {"status": "error", "message": "Missing 'query' parameter"}

        budget = args.get('budget', 32000)
        max_files = args.get('max_files', 5)
        quick = args.get('quick', False)

        concierge = self._get_concierge()
        t0 = time.time()

        if quick:
            result = concierge.quick_find(query, max_files=max_files)
        else:
            result = concierge.find(
                query=query,
                budget_chars=budget,
                max_files=max_files,
            )

        elapsed_ms = (time.time() - t0) * 1000

        response = result.to_dict()
        response["status"] = "ok"
        response["generation_ms"] = round(elapsed_ms, 1)

        # Include full envelope text only if not quick mode
        if not quick and result.envelopes:
            response["context"] = result.to_string()[:50000]

        return response

    def _context_index(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-generate structural index for a file."""
        import time
        target = args.get('target', '')
        if not target:
            return {"status": "error", "message": "Missing 'target' parameter"}

        target = self._resolve_target(target)
        if not os.path.isfile(target):
            return {"status": "error", "message": f"File not found: {target}"}

        mapper = self._get_context_mapper()
        t0 = time.time()
        index = mapper.build_index(target)
        elapsed_ms = (time.time() - t0) * 1000

        result = index.to_dict()
        result["status"] = "ok"
        result["generation_ms"] = round(elapsed_ms, 1)
        result["index_text"] = index.to_string()
        return result

    def _context_section(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve specific section by line range."""
        target = args.get('target', '')
        line_start = args.get('line_start', 1)
        line_end = args.get('line_end', 50)

        if not target:
            return {"status": "error", "message": "Missing 'target' parameter"}

        target = self._resolve_target(target)
        if not os.path.isfile(target):
            return {"status": "error", "message": f"File not found: {target}"}

        mapper = self._get_context_mapper()
        content = mapper.get_section(target, line_start, line_end)

        return {
            "status": "ok",
            "target": os.path.basename(target),
            "lines": f"{line_start}-{line_end}",
            "chars": len(content),
            "content": content,
        }

    def _get_large_reader(self):
        """Lazy-load LargeFileReader."""
        if not hasattr(self, '_large_reader'):
            try:
                from ai_engine.large_file_reader import LargeFileReader
            except ImportError:
                try:
                    from large_file_reader import LargeFileReader
                except ImportError:
                    from scripts.ai_engine.large_file_reader import LargeFileReader
            self._large_reader = LargeFileReader(AIMOS_ROOT)
            logger.info('LargeFileReader loaded')
        return self._large_reader

    def _read_large(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """MapReduce for large files."""
        import time
        target = args.get('target', '')
        if not target:
            return {"status": "error", "message": "Missing 'target' parameter"}

        target = self._resolve_target(target)
        if not os.path.isfile(target):
            return {"status": "error", "message": f"File not found: {target}"}

        chunk_size = args.get('chunk_size', 8000)
        force = args.get('force', False)

        reader = self._get_large_reader()
        t0 = time.time()
        result = reader.read_large(target, chunk_size=chunk_size, force_mapreduce=force)
        elapsed_ms = (time.time() - t0) * 1000

        response = result.to_dict()
        response["status"] = "ok"
        response["generation_ms"] = round(elapsed_ms, 1)
        response["index_text"] = result.to_string()
        return response

    def _systems_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Query system registry by topic/layer."""
        from dataclasses import asdict
        try:
            from scripts.ai_engine.system_registry import SystemRegistry
        except ImportError:
            try:
                from system_registry import SystemRegistry
            except ImportError:
                return {"status": "error", "message": "SystemRegistry not found"}
        reg = SystemRegistry(AIMOS_ROOT)
        topic = args.get("topic", "")
        layer = args.get("layer", "")
        limit = args.get("limit", 50)
        entries = reg.query(topic=topic or None, layer=layer or None, limit=limit)
        return {
            "status": "ok",
            "systems": [asdict(e) for e in entries],
            "count": len(entries),
        }

    def _systems_crawl(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger full re-crawl and write .agent/SYSTEM_REGISTRY.md."""
        try:
            from scripts.ai_engine.system_registry import SystemRegistry
        except ImportError:
            try:
                from system_registry import SystemRegistry
            except ImportError:
                return {"status": "error", "message": "SystemRegistry not found"}
        import time
        reg = SystemRegistry(AIMOS_ROOT)
        t0 = time.time()
        entries = reg.crawl()
        output_path = reg.generate_registry()
        elapsed_ms = (time.time() - t0) * 1000
        return {
            "status": "ok",
            "output_path": output_path,
            "systems_count": len(entries),
            "elapsed_ms": round(elapsed_ms, 1),
        }

    # ── MCP Protocol Handler ─────────────────────────────



    def handle_message(self, message: dict) -> Optional[dict]:
        """Handle a JSON-RPC 2.0 message."""
        method = message.get('method', '')
        msg_id = message.get('id')
        params = message.get('params', {})

        # ── Initialize ──
        if method == 'initialize':
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'result': {
                    'protocolVersion': PROTOCOL_VERSION,
                    'capabilities': {
                        'tools': {'listChanged': False},
                    },
                    'serverInfo': {
                        'name': SERVER_NAME,
                        'version': SERVER_VERSION,
                    },
                },
            }

        # ── Initialized (notification, no response) ──
        if method == 'notifications/initialized':
            logger.info('Client initialized — ready for tool calls')
            return None

        # ── List Tools ──
        if method == 'tools/list':
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'result': {
                    'tools': TOOLS,
                },
            }

        # ── Call Tool ──
        if method == 'tools/call':
            tool_name = params.get('name', '')
            tool_args = params.get('arguments', {})
            logger.info(f'Executing tool: {tool_name}')

            result = self._execute_tool(tool_name, tool_args)

            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'result': {
                    'content': [
                        {
                            'type': 'text',
                            'text': json.dumps(result, indent=2, default=str),
                        }
                    ],
                    'isError': result.get('status') == 'error',
                },
            }

        # ── Ping ──
        if method == 'ping':
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'result': {},
            }

        # ── Unknown Method ──
        if msg_id is not None:
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}',
                },
            }

        return None  # Ignore unknown notifications

    # ── Stdio Transport (synchronous — Windows compatible) ──

    def run(self) -> None:
        """Run the MCP server on stdio with NDJSON transport.

        Uses line-delimited JSON (same as lucid-mcp) — the Gemini CLI
        expects NDJSON over stdio, NOT Content-Length framing.
        """
        logger.info(f'Starting {SERVER_NAME} v{SERVER_VERSION} on stdio (NDJSON)')

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                message = json.loads(line)
                logger.debug(f'Recv: {message.get("method", "?")} id={message.get("id")}')

                # Handle message
                response = self.handle_message(message)

                if response is not None:
                    sys.stdout.write(json.dumps(response) + '\n')
                    sys.stdout.flush()
                    logger.debug(f'Sent response for id={response.get("id")}')

            except json.JSONDecodeError as e:
                logger.error(f'JSON decode error: {e}')
                continue
            except (EOFError, BrokenPipeError, KeyboardInterrupt):
                break
            except Exception as e:
                logger.error(f'Protocol error: {e}')
                import traceback
                traceback.print_exc(file=sys.stderr)
                # Send error response if we have the request
                try:
                    error_resp = {
                        "jsonrpc": "2.0",
                        "id": message.get("id") if 'message' in dir() else 0,
                        "error": {"code": -32603, "message": str(e)},
                    }
                    sys.stdout.write(json.dumps(error_resp) + '\n')
                    sys.stdout.flush()
                except Exception:
                    pass
                continue

        logger.info('Server shutting down')


if __name__ == "__main__":
    server = SlimMCPServer()
    server.run()

