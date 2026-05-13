"""
AIM-OS System Registry — Master System Index (Phase 26)

Crawls ALL AIM-OS systems and produces an authoritative hierarchical index.
Uses Atlas for module discovery, agent_spawner for core system specs,
and ContextMapper for per-file enrichment when needed.

Output: .agent/SYSTEM_REGISTRY.md

Design: Lazy imports to match ai_engine_mcp_server zero-dependency startup.
"""

import os
import sys
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger('ai_engine.system_registry')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))


# ── Data Models ──────────────────────────────────────────

@dataclass
class SystemEntry:
    """A single system in the AIM-OS registry."""
    name: str
    category: str
    purpose: str
    key_files: List[str] = field(default_factory=list)
    status: str = "active"
    exports: List[str] = field(default_factory=list)
    lines: int = 0
    dependencies: List[str] = field(default_factory=list)


# Layer categories from Phase 26 spec
LAYER_CORE = "Core Infrastructure"
LAYER_ENGINE = "AI Engine"
LAYER_CONTEXT = "Context System"
LAYER_AGENT = "Agent System"
LAYER_DOCS = "Documentation"
LAYER_UI = "UI/JOC"
LAYER_MCP = "MCP Servers"
LAYER_WORKFORCE = "Agent Workforce"


# Mapping from Atlas module names / agent_spawner IDs to layer categories
MODULE_TO_LAYER: Dict[str, str] = {
    # Atlas modules
    "ai_engine": LAYER_ENGINE,
    "swarm": LAYER_ENGINE,
    "context": LAYER_CONTEXT,
    "agent_loop": LAYER_ENGINE,
    "providers": LAYER_ENGINE,
    "safety": LAYER_ENGINE,
    "learning": LAYER_ENGINE,
    "genomes": LAYER_WORKFORCE,
    "joc": LAYER_UI,
    "lucid_mcp": LAYER_MCP,
    "daemon_rag": LAYER_CONTEXT,
    # agent_spawner core systems
    "cmc": LAYER_CORE,
    "seg": LAYER_CORE,
    "hhni": LAYER_CORE,
    "vif": LAYER_CORE,
    "sdfcvf": LAYER_CORE,
    "apoe": LAYER_CORE,
    "cas": LAYER_CORE,
    "tcs": LAYER_CORE,
    "iis": LAYER_CORE,
    "docs": LAYER_DOCS,
    "mcp": LAYER_MCP,
}


# ── SystemRegistry ───────────────────────────────────────

class SystemRegistry:
    """
    Crawls AIM-OS workspace and produces a hierarchical system index.
    """

    def __init__(self, workspace_root: str = ""):
        self.workspace_root = workspace_root or WORKSPACE
        self._entries: List[SystemEntry] = []
        self._last_crawl_time: float = 0.0

    def crawl(self) -> List[SystemEntry]:
        """
        Scan workspace using Atlas + agent_spawner SYSTEM_REGISTRY.
        Returns list of SystemEntry.
        """
        start = time.monotonic()
        self._entries = []

        # 1. Add agent_spawner core systems (CMC, HHNI, VIF, etc.)
        try:
            from scripts.ai_engine.agent_spawner import SYSTEM_REGISTRY
        except ImportError:
            try:
                from agent_spawner import SYSTEM_REGISTRY
            except ImportError:
                SYSTEM_REGISTRY = {}

        for sys_id, spec in SYSTEM_REGISTRY.items():
            layer = MODULE_TO_LAYER.get(sys_id, LAYER_CORE)
            key_files = []
            if spec.package:
                pkg_path = os.path.join(self.workspace_root, "packages", spec.package)
                if os.path.isdir(pkg_path):
                    for root, _, files in os.walk(pkg_path):
                        for f in files:
                            if f.endswith(('.py', '.ts', '.tsx')):
                                key_files.append(os.path.relpath(os.path.join(root, f), self.workspace_root))
                            if len(key_files) >= 10:
                                break
                        if len(key_files) >= 10:
                            break
            self._entries.append(SystemEntry(
                name=spec.system_name,
                category=layer,
                purpose=spec.description or "",
                key_files=key_files[:10],
                status="active",
                exports=spec.mcp_tools or [],
                lines=0,
                dependencies=[],
            ))

        # 2. Add Atlas modules (ai_engine, swarm, joc, etc.)
        try:
            from scripts.ai_engine.atlas_agent import Atlas
        except ImportError:
            try:
                from atlas_agent import Atlas
            except ImportError:
                Atlas = None

        if Atlas:
            atlas = Atlas(self.workspace_root)
            stats = atlas.index(force=True)
            for mod_name, mod_info in atlas.map.modules.items():
                if mod_name in MODULE_TO_LAYER:
                    layer = MODULE_TO_LAYER[mod_name]
                else:
                    layer = LAYER_ENGINE
                # Avoid duplicates with agent_spawner (e.g. context, docs, mcp)
                existing_names = {e.name for e in self._entries}
                display_name = mod_info.name.replace("_", " ").title()
                if display_name in existing_names:
                    continue
                self._entries.append(SystemEntry(
                    name=display_name,
                    category=layer,
                    purpose=mod_info.purpose or mod_info.description or "",
                    key_files=mod_info.files[:10] if mod_info.files else [],
                    status="active",
                    exports=mod_info.key_classes[:15] + mod_info.key_functions[:15],
                    lines=mod_info.total_lines,
                    dependencies=mod_info.dependencies[:10],
                ))

        # 3. Add ai_engine top-level modules (engine.py, chain_director, context_mapper, etc.)
        context_modules = {"context_mapper", "context_concierge", "context_engine", "large_file_reader"}
        engine_dir = os.path.join(self.workspace_root, "scripts", "ai_engine")
        if os.path.isdir(engine_dir):
            engine_files = [
                "engine.py", "chain_director.py", "context_mapper.py", "context_concierge.py",
                "context_engine.py", "large_file_reader.py", "atlas_agent.py", "genome_loader.py",
                "agent_runtime.py", "agent_spawner.py", "roundtable.py", "enhanced_worker.py",
                "ai_engine_mcp_server.py",
            ]
            existing_bases = {e.name.lower().replace(" ", "_") for e in self._entries}
            for f in engine_files:
                fpath = os.path.join(engine_dir, f)
                if os.path.isfile(fpath):
                    base = os.path.splitext(f)[0]
                    if base in existing_bases:
                        continue
                    existing_bases.add(base)
                    layer = LAYER_CONTEXT if base in context_modules else LAYER_ENGINE
                    try:
                        line_count = sum(1 for _ in open(fpath, encoding="utf-8", errors="replace"))
                    except Exception:
                        line_count = 0
                    self._entries.append(SystemEntry(
                        name=base.replace("_", " ").title(),
                        category=layer,
                        purpose=f"scripts/ai_engine/{f}",
                        key_files=[f"scripts/ai_engine/{f}"],
                        status="active",
                        exports=[],
                        lines=line_count,
                        dependencies=[],
                    ))

        self._last_crawl_time = time.time()
        elapsed = (time.monotonic() - start) * 1000
        logger.info(f"[SystemRegistry] Crawled {len(self._entries)} systems in {elapsed:.0f}ms")
        return self._entries

    def categorize(self, entries: Optional[List[SystemEntry]] = None) -> Dict[str, List[SystemEntry]]:
        """Group entries by layer category."""
        entries = entries or self._entries
        result: Dict[str, List[SystemEntry]] = {}
        for e in entries:
            if e.category not in result:
                result[e.category] = []
            result[e.category].append(e)
        return result

    def generate_registry(self, output_path: Optional[str] = None) -> str:
        """
        Write .agent/SYSTEM_REGISTRY.md. Returns the written path.
        """
        if not self._entries:
            self.crawl()

        output_path = output_path or os.path.join(self.workspace_root, ".agent", "SYSTEM_REGISTRY.md")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        by_layer = self.categorize()
        layer_order = [
            LAYER_CORE, LAYER_ENGINE, LAYER_CONTEXT, LAYER_AGENT,
            LAYER_DOCS, LAYER_UI, LAYER_MCP, LAYER_WORKFORCE,
        ]

        lines = [
            "# AIM-OS System Registry",
            "",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._last_crawl_time))}",
            f"**Total systems:** {len(self._entries)}",
            "",
            "> Phase 26 Master System Index. Machine-generated. For curated navigation, see LEDGER_SOURCE_OF_TRUTH_INDEX.",
            "",
            "---",
            "",
        ]

        for layer in layer_order:
            entries = by_layer.get(layer, [])
            if not entries:
                continue
            lines.append(f"## {layer}")
            lines.append("")
            lines.append("| Name | Purpose | Key Files | Status | Exports | Lines |")
            lines.append("|------|---------|------------|--------|---------|-------|")
            for e in sorted(entries, key=lambda x: x.name):
                key_files_str = ", ".join(e.key_files[:3]) if e.key_files else "-"
                if len(key_files_str) > 50:
                    key_files_str = key_files_str[:47] + "..."
                exports_str = ", ".join(e.exports[:5]) if e.exports else "-"
                if len(exports_str) > 40:
                    exports_str = exports_str[:37] + "..."
                purpose_short = (e.purpose[:60] + "...") if len(e.purpose) > 60 else e.purpose
                lines.append(f"| {e.name} | {purpose_short} | {key_files_str} | {e.status} | {exports_str} | {e.lines} |")
            lines.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"[SystemRegistry] Wrote {output_path}")
        return output_path

    def query(self, topic: str, layer: Optional[str] = None, limit: int = 50) -> List[SystemEntry]:
        """Filter entries by topic (substring in name/purpose) and/or layer."""
        if not self._entries:
            self.crawl()
        results = []
        topic_lower = topic.lower() if topic else ""
        for e in self._entries:
            if layer and e.category != layer:
                continue
            if topic_lower and topic_lower not in e.name.lower() and topic_lower not in e.purpose.lower():
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return results

    def diff_since(self, timestamp: float) -> List[str]:
        """Return names of systems whose key files changed since timestamp."""
        if not self._entries:
            self.crawl()
        changed = []
        for e in self._entries:
            for f in e.key_files:
                fpath = os.path.join(self.workspace_root, f)
                if os.path.isfile(fpath) and os.path.getmtime(fpath) > timestamp:
                    changed.append(e.name)
                    break
        return changed


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    reg = SystemRegistry()
    reg.crawl()
    path = reg.generate_registry()
    print(f"Wrote {path}")
