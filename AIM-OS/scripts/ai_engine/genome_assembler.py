"""
AIM-OS Genome Assembler v2.0

Assembles deployed genomes from the 3-layer architecture:
    Universal Core + Platform Adapter + Model Affinity = Deployed Genome

Also provides validation and Gemini CLI spawning.

Usage:
    python genome_assembler.py assemble opus antigravity claude
    python genome_assembler.py validate
    python genome_assembler.py spawn agent-cmc
    python genome_assembler.py spawn-division engineering
    python genome_assembler.py list
    python genome_assembler.py matrix
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

GENOMES_ROOT = Path(__file__).parent.parent.parent / ".agent" / "genomes"
CORES_DIR = GENOMES_ROOT / "cores"
SPECIALISTS_DIR = CORES_DIR / "specialists"
PLATFORMS_DIR = GENOMES_ROOT / "platforms"
AFFINITIES_DIR = GENOMES_ROOT / "affinities"


# ─────────────────────────────────────────────────────────────
# Force Structure Registry
# ─────────────────────────────────────────────────────────────

@dataclass
class AgentSpec:
    """An agent in the force structure."""
    callsign: str
    rank: str
    division: str
    core_file: str           # relative to CORES_DIR or SPECIALISTS_DIR
    default_platform: str    # adapter filename stem (e.g. "cli")
    default_model: str       # affinity filename stem (e.g. "gemini")
    reports_to: str = ""
    is_specialist: bool = False

# ── Executives ──
EXECUTIVES = {
    "opus": AgentSpec("OPUS", "EXECUTIVE", "Command", "opus.core.md", "antigravity", "claude", "Braden"),
    "sev": AgentSpec("SEV", "EXECUTIVE", "Command", "sev.core.md", "chatgpt", "gpt", "Braden"),
    "composer": AgentSpec("COMPOSER", "EXECUTIVE", "Audit", "composer.core.md", "cursor", "claude", "OPUS"),
    "composer-sev": AgentSpec("COMPOSER-SEV", "SPECIALIST", "QA", "composer-sev.core.md", "cursor", "claude", "COMPOSER"),
}

# ── Named Agents ──
NAMED_AGENTS = {
    "codex": AgentSpec("CODEX", "LEAD", "Engineering", "codex.core.md", "cursor", "gpt", "OPUS"),
    "gemini": AgentSpec("GEMINI", "LEAD", "Intelligence", "gemini.core.md", "cli", "gemini", "SEV"),
}

# ── Division Specialists ──  
# All specialists default to Gemini CLI
def _spec(callsign, rank, division, core_file, reports_to):
    return AgentSpec(callsign, rank, division, core_file, "cli", "gemini", reports_to, is_specialist=True)

SPECIALISTS = {
    # Engineering Division (reports to CODEX)
    "agent-cmc": _spec("AGENT-CMC", "SPECIALIST", "Engineering", "specialist_cmc.genome.md", "CODEX"),
    "agent-seg": _spec("AGENT-SEG", "SPECIALIST", "Engineering", "specialist_seg.genome.md", "CODEX"),
    "agent-hhni": _spec("AGENT-HHNI", "SPECIALIST", "Engineering", "specialist_hhni.genome.md", "CODEX"),
    "agent-vif": _spec("AGENT-VIF", "SPECIALIST", "Engineering", "specialist_vif.genome.md", "CODEX"),
    "agent-sdfcvf": _spec("AGENT-SDFCVF", "SPECIALIST", "Engineering", "specialist_sdfcvf.genome.md", "CODEX"),
    "agent-apoe": _spec("AGENT-APOE", "SPECIALIST", "Engineering", "specialist_apoe.genome.md", "CODEX"),
    "agent-cas": _spec("AGENT-CAS", "SPECIALIST", "Engineering", "specialist_cas.genome.md", "CODEX"),
    "agent-tcs": _spec("AGENT-TCS", "SPECIALIST", "Engineering", "specialist_tcs.genome.md", "CODEX"),
    "agent-iis": _spec("AGENT-IIS", "SPECIALIST", "Engineering", "specialist_iis.genome.md", "CODEX"),
    "agent-context": _spec("AGENT-CONTEXT", "SPECIALIST", "Engineering", "specialist_context.genome.md", "CODEX"),
    
    # UI Division (reports to agent-design-system)
    "agent-design-system": _spec("AGENT-DESIGN-SYSTEM", "LEAD", "UI", "agent-design-system.core.md", "OPUS"),
    "agent-component-architect": _spec("AGENT-COMPONENT-ARCHITECT", "LEAD", "UI", "agent-component-architect.core.md", "agent-design-system"),
    "agent-canvas-composer": _spec("AGENT-CANVAS-COMPOSER", "SPECIALIST", "UI", "specialist_canvas_composer.core.md", "agent-design-system"),
    "agent-motion-director": _spec("AGENT-MOTION-DIRECTOR", "SPECIALIST", "UI", "specialist_motion_director.core.md", "agent-design-system"),
    "agent-a11y": _spec("AGENT-A11Y", "SPECIALIST", "UI", "agent-a11y.core.md", "agent-design-system"),
    
    # Infrastructure Division (reports to agent-mcp)
    "agent-mcp": _spec("AGENT-MCP", "LEAD", "Infrastructure", "specialist_mcp.genome.md", "OPUS"),
    "agent-transport": _spec("AGENT-TRANSPORT", "SPECIALIST", "Infrastructure", "agent-transport.core.md", "agent-mcp"),
    "agent-security": _spec("AGENT-SECURITY", "SPECIALIST", "Infrastructure", "agent-security.core.md", "agent-mcp"),
    "agent-devops": _spec("AGENT-DEVOPS", "SPECIALIST", "Infrastructure", "agent-devops.core.md", "agent-mcp"),
    "agent-host": _spec("AGENT-HOST", "SPECIALIST", "Infrastructure", "agent-host.core.md", "agent-mcp"),
    "agent-network": _spec("AGENT-NETWORK", "SPECIALIST", "Infrastructure", "agent-network.core.md", "agent-mcp"),
    
    # Intelligence Division (reports to GEMINI)
    "agent-research-strategist": _spec("AGENT-RESEARCH-STRATEGIST", "SPECIALIST", "Intelligence", "specialist_research_strategist.core.md", "GEMINI"),
    "agent-knowledge-auditor": _spec("AGENT-KNOWLEDGE-AUDITOR", "SPECIALIST", "Intelligence", "specialist_knowledge_auditor.core.md", "GEMINI"),
    "agent-canon-compiler": _spec("AGENT-CANON-COMPILER", "SPECIALIST", "Intelligence", "specialist_canon_compiler.core.md", "GEMINI"),
    "agent-web-researcher": _spec("AGENT-WEB-RESEARCHER", "SPECIALIST", "Intelligence", "agent-web-researcher.core.md", "GEMINI"),
    "agent-adaptive": _spec("AGENT-ADAPTIVE", "LEAD", "Intelligence", "agent-adaptive.core.md", "GEMINI"),
    
    # Documentation Division (reports to agent-docs)
    "agent-docs": _spec("AGENT-DOCS", "LEAD", "Documentation", "specialist_docs.genome.md", "SEV"),
    "agent-api-docs": _spec("AGENT-API-DOCS", "SPECIALIST", "Documentation", "agent-api-docs.core.md", "agent-docs"),
    "agent-tutorials": _spec("AGENT-TUTORIALS", "SPECIALIST", "Documentation", "agent-tutorials.core.md", "agent-docs"),
    "agent-arch-mapper": _spec("AGENT-ARCH-MAPPER", "SPECIALIST", "Documentation", "agent-arch-mapper.core.md", "agent-docs"),
    
    # QA Division (reports to agent-qa-lead)
    "agent-qa-lead": _spec("AGENT-QA-LEAD", "LEAD", "QA", "agent-qa-lead.core.md", "COMPOSER"),
    "agent-unit-test": _spec("AGENT-UNIT-TEST", "SPECIALIST", "QA", "agent-unit-test.core.md", "agent-qa-lead"),
    "agent-integration-test": _spec("AGENT-INTEGRATION-TEST", "SPECIALIST", "QA", "agent-integration-test.core.md", "agent-qa-lead"),
    "agent-perf": _spec("AGENT-PERF", "SPECIALIST", "QA", "agent-perf.core.md", "agent-qa-lead"),
    
    # Product Division (reports to agent-product)
    "agent-product": _spec("AGENT-PRODUCT", "LEAD", "Product", "agent-product.core.md", "OPUS"),
    "agent-ux-research": _spec("AGENT-UX-RESEARCH", "SPECIALIST", "Product", "agent-ux-research.core.md", "agent-product"),
    "agent-demo": _spec("AGENT-DEMO", "SPECIALIST", "Product", "agent-demo.core.md", "agent-product"),
    "agent-onboarding": _spec("AGENT-ONBOARDING", "SPECIALIST", "Product", "agent-onboarding.core.md", "agent-product"),
}

# All agents combined
ALL_AGENTS = {**EXECUTIVES, **NAMED_AGENTS, **SPECIALISTS}


# ─────────────────────────────────────────────────────────────
# Genome Assembler
# ─────────────────────────────────────────────────────────────

class GenomeAssembler:
    """Assembles 3-layer genomes from core + adapter + affinity files."""
    
    def __init__(self, genomes_root: Optional[Path] = None):
        self.root = genomes_root or GENOMES_ROOT
        self.cores = self.root / "cores"
        self.specialists = self.cores / "specialists"
        self.platforms = self.root / "platforms"
        self.affinities = self.root / "affinities"
    
    def find_core(self, agent_id: str) -> Optional[Path]:
        """Find the core file for an agent."""
        spec = ALL_AGENTS.get(agent_id)
        if not spec:
            return None
        
        # Check cores/ first, then cores/specialists/
        core_path = self.cores / spec.core_file
        if core_path.exists():
            return core_path
        
        specialist_path = self.specialists / spec.core_file
        if specialist_path.exists():
            return specialist_path
        
        return None
    
    def find_adapter(self, platform: str) -> Optional[Path]:
        """Find the adapter file for a platform."""
        path = self.platforms / f"{platform}.adapter.md"
        return path if path.exists() else None
    
    def find_affinity(self, model: str) -> Optional[Path]:
        """Find the affinity file for a model."""
        path = self.affinities / f"{model}.affinity.md"
        return path if path.exists() else None
    
    def assemble(self, agent_id: str, platform: Optional[str] = None, 
                 model: Optional[str] = None) -> str:
        """Assemble a full genome from core + adapter + affinity.
        
        Args:
            agent_id: Agent identifier (e.g., "opus", "agent-cmc")
            platform: Override default platform (e.g., "cli", "antigravity")
            model: Override default model (e.g., "gemini", "claude")
        
        Returns:
            Assembled genome as a single string
        """
        spec = ALL_AGENTS.get(agent_id)
        if not spec:
            raise ValueError(f"Unknown agent: {agent_id}. Available: {list(ALL_AGENTS.keys())}")
        
        platform = platform or spec.default_platform
        model = model or spec.default_model
        
        # Find files
        core_path = self.find_core(agent_id)
        adapter_path = self.find_adapter(platform)
        affinity_path = self.find_affinity(model)
        
        parts = []
        parts.append(f"<!-- ASSEMBLED GENOME: {spec.callsign} | {platform} | {model} -->")
        parts.append(f"<!-- Generated: {datetime.now().isoformat()} -->")
        parts.append("")
        
        # Core (required)
        if core_path:
            parts.append(core_path.read_text(encoding="utf-8"))
        else:
            parts.append(f"<!-- WARNING: Core not found for {agent_id} ({spec.core_file}) -->")
        
        parts.append("\n---\n")
        
        # Adapter (optional but recommended)
        if adapter_path:
            parts.append(adapter_path.read_text(encoding="utf-8"))
        else:
            parts.append(f"<!-- NOTE: No adapter found for platform '{platform}' -->")
        
        parts.append("\n---\n")
        
        # Affinity (optional but recommended)
        if affinity_path:
            parts.append(affinity_path.read_text(encoding="utf-8"))
        else:
            parts.append(f"<!-- NOTE: No affinity found for model '{model}' -->")
        
        return "\n".join(parts)
    
    def assemble_to_file(self, agent_id: str, output_dir: Optional[Path] = None,
                         platform: Optional[str] = None, model: Optional[str] = None) -> Path:
        """Assemble and save to disk."""
        spec = ALL_AGENTS.get(agent_id)
        platform = platform or spec.default_platform
        model = model or spec.default_model
        
        output_dir = output_dir or (self.root / "assembled")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        content = self.assemble(agent_id, platform, model)
        filename = f"{agent_id}_{platform}_{model}.genome.md"
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        return path


# ─────────────────────────────────────────────────────────────
# Genome Validator
# ─────────────────────────────────────────────────────────────

class GenomeValidator:
    """Validates genome files and force structure integrity."""
    
    def __init__(self, genomes_root: Optional[Path] = None):
        self.root = genomes_root or GENOMES_ROOT
        self.assembler = GenomeAssembler(self.root)
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> dict:
        """Run all validation checks."""
        self.errors = []
        self.warnings = []
        
        self._check_unique_callsigns()
        self._check_core_files_exist()
        self._check_adapter_files_exist()
        self._check_affinity_files_exist()
        self._check_division_leads()
        self._check_reporting_chains()
        
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "agents_checked": len(ALL_AGENTS),
            "cores_found": sum(1 for a in ALL_AGENTS if self.assembler.find_core(a)),
            "cores_missing": sum(1 for a in ALL_AGENTS if not self.assembler.find_core(a)),
        }
    
    def _check_unique_callsigns(self):
        """Every agent must have a unique callsign."""
        callsigns = {}
        for agent_id, spec in ALL_AGENTS.items():
            if spec.callsign in callsigns:
                self.errors.append(
                    f"Duplicate callsign '{spec.callsign}': {agent_id} and {callsigns[spec.callsign]}"
                )
            callsigns[spec.callsign] = agent_id
    
    def _check_core_files_exist(self):
        """Every agent should have a core file on disk."""
        for agent_id, spec in ALL_AGENTS.items():
            if not self.assembler.find_core(agent_id):
                self.warnings.append(f"Core file missing for {agent_id}: {spec.core_file}")
    
    def _check_adapter_files_exist(self):
        """Every referenced platform should have an adapter."""
        platforms = set(s.default_platform for s in ALL_AGENTS.values())
        for platform in platforms:
            if not self.assembler.find_adapter(platform):
                self.errors.append(f"Adapter file missing for platform: {platform}")
    
    def _check_affinity_files_exist(self):
        """Every referenced model should have an affinity."""
        models = set(s.default_model for s in ALL_AGENTS.values())
        for model in models:
            if not self.assembler.find_affinity(model):
                self.errors.append(f"Affinity file missing for model: {model}")
    
    def _check_division_leads(self):
        """Every division should have at least one LEAD."""
        divisions = set(s.division for s in ALL_AGENTS.values())
        for div in divisions:
            leads = [a for a, s in ALL_AGENTS.items() if s.division == div and s.rank == "LEAD"]
            if not leads and div not in ("Command", "Audit"):
                self.warnings.append(f"Division '{div}' has no LEAD agent")
    
    def _check_reporting_chains(self):
        """Every agent should report to someone who exists."""
        all_callsigns = set(s.callsign for s in ALL_AGENTS.values())
        all_callsigns.add("Braden")  # COMMAND
        for agent_id, spec in ALL_AGENTS.items():
            if spec.reports_to and spec.reports_to not in all_callsigns:
                # Check if reports_to is an agent_id instead of callsign
                if spec.reports_to not in ALL_AGENTS:
                    self.warnings.append(
                        f"{agent_id} reports to '{spec.reports_to}' which is not a known callsign"
                    )


# ─────────────────────────────────────────────────────────────
# Gemini CLI Spawner
# ─────────────────────────────────────────────────────────────

class GeminiSpawner:
    """Spawns agents via Gemini CLI with assembled genomes."""
    
    def __init__(self, working_directory: Optional[str] = None):
        self.working_dir = working_directory or str(
            Path(__file__).parent.parent.parent  # AIM-OS root
        )
        self.assembler = GenomeAssembler()
    
    def spawn(self, agent_id: str, task: str, 
              platform: str = "cli", model: str = "gemini",
              sandbox: bool = True) -> dict:
        """Spawn an agent via Gemini CLI.
        
        Args:
            agent_id: Agent identifier from the force structure
            task: The task/mission to assign
            platform: Platform adapter to use
            model: Model affinity to use  
            sandbox: If True, use --sandbox flag (read-only)
        
        Returns:
            Dict with success, output, error, duration
        """
        import time
        
        # Assemble the genome
        genome = self.assembler.assemble(agent_id, platform, model)
        
        # Build the full prompt
        spec = ALL_AGENTS[agent_id]
        prompt = f"""{genome}

---

# MISSION ASSIGNMENT

You are {spec.callsign}. Your genome has been loaded above.

## Task
{task}

## Rules
1. Follow your work protocol exactly
2. Store findings via MCP `store_memory` if available
3. Report to {spec.reports_to} via MCP `send_ai_message` if available
4. Produce structured output per your report format
5. Be thorough but concise
"""
        
        # Save prompt to temp file
        prompt_file = Path(self.working_dir) / ".agent" / "genomes" / "assembled" / f"{agent_id}_mission.md"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt, encoding="utf-8")
        
        # Build gemini CLI command
        cmd = ["gemini"]
        if sandbox:
            cmd.append("--sandbox")
        cmd.extend(["--prompt", str(prompt_file)])
        
        print(f"  Spawning {spec.callsign} ({spec.rank}, {spec.division})...")
        print(f"  Platform: {platform} | Model: {model}")
        print(f"  Prompt saved: {prompt_file}")
        
        # Try to execute
        try:
            start = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
                cwd=self.working_dir,
            )
            duration = time.time() - start
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "duration": duration,
                "agent": agent_id,
                "callsign": spec.callsign,
            }
        except FileNotFoundError:
            return {
                "success": False,
                "output": "",
                "error": "gemini CLI not found. Install with: npm install -g @anthropic/gemini-cli",
                "duration": 0,
                "agent": agent_id,
                "callsign": spec.callsign,
                "prompt_path": str(prompt_file),
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Timeout (300s)",
                "duration": 300,
                "agent": agent_id,
                "callsign": spec.callsign,
            }
    
    def spawn_division(self, division: str, task: str, sandbox: bool = True) -> list[dict]:
        """Spawn all agents in a division."""
        results = []
        for agent_id, spec in ALL_AGENTS.items():
            if spec.division.lower() == division.lower() and spec.is_specialist:
                result = self.spawn(agent_id, task, sandbox=sandbox)
                results.append(result)
        return results


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def cmd_assemble(args):
    """Assemble a genome."""
    assembler = GenomeAssembler()
    try:
        content = assembler.assemble(args.agent, args.platform, args.model)
        if args.output:
            Path(args.output).write_text(content, encoding="utf-8")
            print(f"Assembled genome saved to: {args.output}")
        else:
            print(content)
    except ValueError as e:
        print(f"Error: {e}")

def cmd_validate(args):
    """Validate the genome system."""
    validator = GenomeValidator()
    result = validator.validate_all()
    
    print(f"\n{'='*60}")
    print(f"  GENOME VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"  Agents checked:  {result['agents_checked']}")
    print(f"  Cores found:     {result['cores_found']}")
    print(f"  Cores missing:   {result['cores_missing']}")
    print(f"  Status:          {'✅ VALID' if result['valid'] else '❌ ERRORS FOUND'}")
    
    if result['errors']:
        print(f"\n  ERRORS ({len(result['errors'])}):")
        for e in result['errors']:
            print(f"    ❌ {e}")
    
    if result['warnings']:
        print(f"\n  WARNINGS ({len(result['warnings'])}):")
        for w in result['warnings']:
            print(f"    ⚠️  {w}")
    
    print(f"\n{'='*60}\n")

def cmd_spawn(args):
    """Spawn an agent via Gemini CLI."""
    spawner = GeminiSpawner()
    result = spawner.spawn(args.agent, args.task, sandbox=not args.no_sandbox)
    
    if result['success']:
        print(f"\n✅ {result['callsign']} completed ({result['duration']:.1f}s)")
        print(result['output'][:500])
    else:
        print(f"\n❌ {result['callsign']} failed: {result['error']}")
        if 'prompt_path' in result:
            print(f"  Prompt saved for manual execution: {result['prompt_path']}")

def cmd_list(args):
    """List all agents."""
    print(f"\n{'Callsign':<30} {'Rank':<12} {'Division':<16} {'Platform':<12} {'Model':<8} {'Reports To'}")
    print("-" * 110)
    
    # Sort by division then rank
    rank_order = {"COMMAND": 0, "EXECUTIVE": 1, "LEAD": 2, "SPECIALIST": 3, "WORKER": 4}
    sorted_agents = sorted(ALL_AGENTS.items(), key=lambda x: (x[1].division, rank_order.get(x[1].rank, 5)))
    
    current_div = None
    for agent_id, spec in sorted_agents:
        if spec.division != current_div:
            current_div = spec.division
            print(f"\n  ── {current_div} ──")
        print(f"  {spec.callsign:<28} {spec.rank:<12} {spec.division:<16} {spec.default_platform:<12} {spec.default_model:<8} {spec.reports_to}")
    
    print(f"\n  Total: {len(ALL_AGENTS)} agents\n")

def cmd_matrix(args):
    """Show the platform x model deployment matrix."""
    matrix = {}
    for agent_id, spec in ALL_AGENTS.items():
        key = (spec.default_platform, spec.default_model)
        if key not in matrix:
            matrix[key] = []
        matrix[key].append(spec.callsign)
    
    print(f"\n{'Platform':<15} {'Model':<10} {'Count':<6} {'Agents'}")
    print("-" * 80)
    for (platform, model), agents in sorted(matrix.items()):
        agent_str = ", ".join(agents[:5])
        if len(agents) > 5:
            agent_str += f" (+{len(agents)-5} more)"
        print(f"  {platform:<13} {model:<10} {len(agents):<6} {agent_str}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="AIM-OS Genome Assembler v2.0 — 3-Layer Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python genome_assembler.py assemble opus antigravity claude
  python genome_assembler.py assemble agent-cmc cli gemini
  python genome_assembler.py validate
  python genome_assembler.py spawn agent-cmc --task "Audit CMC memory system"
  python genome_assembler.py list
  python genome_assembler.py matrix
"""
    )
    subparsers = parser.add_subparsers(dest="command")
    
    # assemble
    asm = subparsers.add_parser("assemble", help="Assemble a genome from core + adapter + affinity")
    asm.add_argument("agent", help="Agent ID (e.g., opus, agent-cmc)")
    asm.add_argument("platform", nargs="?", help="Platform (default: agent's default)")
    asm.add_argument("model", nargs="?", help="Model (default: agent's default)")
    asm.add_argument("-o", "--output", help="Output file path")
    
    # validate
    subparsers.add_parser("validate", help="Validate genome system integrity")
    
    # spawn
    sp = subparsers.add_parser("spawn", help="Spawn agent via Gemini CLI")
    sp.add_argument("agent", help="Agent ID to spawn")
    sp.add_argument("--task", required=True, help="Mission/task to assign")
    sp.add_argument("--no-sandbox", action="store_true", help="Allow file writes")
    
    # spawn-division
    sd = subparsers.add_parser("spawn-division", help="Spawn all agents in a division")
    sd.add_argument("division", help="Division name")
    sd.add_argument("--task", required=True, help="Mission/task to assign")
    
    # list
    subparsers.add_parser("list", help="List all agents in force structure")
    
    # matrix
    subparsers.add_parser("matrix", help="Show platform x model deployment matrix")
    
    args = parser.parse_args()
    
    handlers = {
        "assemble": cmd_assemble,
        "validate": cmd_validate,
        "spawn": cmd_spawn,
        "list": cmd_list,
        "matrix": cmd_matrix,
    }
    
    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
