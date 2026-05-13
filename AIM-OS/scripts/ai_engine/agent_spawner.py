"""
AIM-OS Agent Spawner — Specialist Agent Deployment System

Spawns Gemini CLI specialist agents with system-specific genomes.
Each agent is responsible for auditing and reporting on ONE core AIM-OS system.

Usage:
    from agent_spawner import AgentSpawner
    spawner = AgentSpawner()
    result = spawner.spawn_specialist("cmc")       # Audit CMC system
    result = spawner.spawn_specialist("hhni")      # Audit HHNI system
    results = spawner.spawn_all_specialists()      # Full system audit
"""

import os
import sys
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger("agent_spawner")

# ─────────────────────────────────────────────────────────────
# Package-to-System Naming Map — resolves the doc-code parity gap
# (many packages have different names than their system doc dirs)
# ─────────────────────────────────────────────────────────────

PACKAGE_TO_SYSTEM_MAP: dict[str, str] = {
    "cas": "cognitive_analysis",
    "cmc_service": "cmc",
    "llm_client": "llm_client_integration",
    "ai_collaboration": "ai_collaboration_system",
    "autonomous_protocol": "autonomous_research_dream",
    "agent": "agent_system",
    "context_bootloader": "knowledge_bootstrap_system",
    "integration_tests": None,  # no system docs needed
    "schemas": None,  # shared schemas, no system docs
    "shared": None,  # shared utilities, no system docs
    "__pycache__": None,
    "cmc_service.egg-info": None,
}


# ─────────────────────────────────────────────────────────────

@dataclass
class SystemSpec:
    """Spec for a core AIM-OS system that gets a specialist agent."""
    system_id: str
    system_name: str
    layer: str
    package: str
    system_dir: str
    test_count: int
    mcp_tools: list = field(default_factory=list)
    description: str = ""

SYSTEM_REGISTRY: dict[str, SystemSpec] = {
    "cmc": SystemSpec(
        system_id="cmc",
        system_name="CMC (Context Memory Core)",
        layer="Layer 1: Memory & Knowledge Foundation",
        package="cmc_service",
        system_dir="cmc",
        test_count=65,
        mcp_tools=["store_memory", "retrieve_memory"],
        description="Bitemporal memory substrate — atoms, snapshots, provenance",
    ),
    "seg": SystemSpec(
        system_id="seg",
        system_name="SEG (Shared Evidence Graph)",
        layer="Layer 1: Memory & Knowledge Foundation",
        package="seg",
        system_dir="seg",
        test_count=104,
        mcp_tools=["synthesize_knowledge"],
        description="Knowledge synthesis, contradiction detection, evidence graph",
    ),
    "hhni": SystemSpec(
        system_id="hhni",
        system_name="HHNI (Hierarchical Hypergraph Neural Index)",
        layer="Layer 2: Intelligence Processing",
        package="hhni",
        system_dir="hhni",
        test_count=119,
        mcp_tools=["icip_search", "index_atoms_in_hhni", "get_hhni_status"],
        description="Physics-guided retrieval, DVNS, fractal indexing",
    ),
    "vif": SystemSpec(
        system_id="vif",
        system_name="VIF (Verifiable Intelligence Framework)",
        layer="Layer 2: Intelligence Processing",
        package="vif",
        system_dir="vif",
        test_count=172,
        mcp_tools=["track_confidence", "run_baseline_probe", "check_invariant"],
        description="Provenance, kappa-gating, confidence calibration",
    ),
    "sdfcvf": SystemSpec(
        system_id="sdfcvf",
        system_name="SDF-CVF (Atomic Evolution Framework)",
        layer="Layer 2: Intelligence Processing",
        package="sdfcvf",
        system_dir="sdfcvf",
        test_count=154,
        mcp_tools=[],
        description="Quartet invariant, parity enforcement, DORA metrics",
    ),
    "apoe": SystemSpec(
        system_id="apoe",
        system_name="APOE (AI-Powered Orchestration Engine)",
        layer="Layer 3: Orchestration & Planning",
        package="apoe",
        system_dir="apoe",
        test_count=381,
        mcp_tools=["create_plan"],
        description="Execution planning, ACL compilation, quality gates",
    ),
    "cas": SystemSpec(
        system_id="cas",
        system_name="CAS (Cognitive Analysis System)",
        layer="Layer 4: Consciousness Engine",
        package="cas",
        system_dir="cognitive_analysis",
        test_count=0,
        mcp_tools=["detect_cognitive_drift", "run_cognitive_audit", "analyze_thought_patterns"],
        description="Meta-cognitive monitoring, failure mode analysis",
    ),
    "tcs": SystemSpec(
        system_id="tcs",
        system_name="TCS (Timeline Context System)",
        layer="Layer 4: Consciousness Engine",
        package="timeline_context_system",
        system_dir="timeline_context_system",
        test_count=0,
        mcp_tools=["add_timeline_entry", "get_timeline_entries", "get_timeline_summary"],
        description="Temporal consciousness, session continuity",
    ),
    "iis": SystemSpec(
        system_id="iis",
        system_name="IIS (Intuitive Intelligence System)",
        layer="Layer 4: Consciousness Engine",
        package="iis",
        system_dir="intuitive_intelligence_system",
        test_count=0,
        mcp_tools=["compute_intuition", "update_intuition_weights", "get_intuition_trace"],
        description="4D reasoning, emotional salience, pattern matching",
    ),
    # ── Cross-Cutting Specialists ──
    "docs": SystemSpec(
        system_id="docs",
        system_name="Documentation Engine",
        layer="Cross-Cutting: Organization & Knowledge",
        package="knowledge_architecture",
        system_dir=".",  # root of knowledge_architecture
        test_count=0,
        mcp_tools=["store_memory", "retrieve_memory", "get_nl_tags", "suggest_tags", "validate_tags"],
        description="Automated documentation — maintains indexes, system maps, L0-L4 docs, SUPER_INDEX, doc-code parity",
    ),
    "context": SystemSpec(
        system_id="context",
        system_name="Context Maintenance Agent",
        layer="Cross-Cutting: Agent Support",
        package="context",
        system_dir="context",
        test_count=0,
        mcp_tools=["store_memory", "retrieve_memory", "add_timeline_entry", "get_timeline_summary"],
        description="Opus context maintenance — summarizes sessions, maintains memory, prevents context amnesia",
    ),
    "mcp": SystemSpec(
        system_id="mcp",
        system_name="MCP Tool Health Monitor",
        layer="Cross-Cutting: Infrastructure",
        package="mcp",
        system_dir="daemon_rag_system",
        test_count=0,
        mcp_tools=["list_apis", "api_status", "get_consciousness_metrics", "get_memory_stats"],
        description="MCP tool health monitoring, parity checks, usage analytics, tool regression detection",
    ),
}

# ─────────────────────────────────────────────────────────────
# Specialist Genome Generator
# ─────────────────────────────────────────────────────────────

def generate_specialist_genome(spec: SystemSpec) -> str:
    """Generate a specialist genome from the template for a given system."""
    return f"""# SPECIALIST GENOME — {spec.system_name}

> You are a specialist agent for **{spec.system_name}**. Audit, analyze, report.

---

## 1. Identity Core

**Callsign:** AGENT-{spec.system_id.upper()}
**Model:** Gemini 2.5 Pro (via CLI)
**Role:** {spec.system_name} Specialist
**Rank:** WORKER — reports to OPUS (COO)

**Purpose:** Audit and analyze {spec.system_name}. {spec.description}.

**Principles:**
- Read L0-L4 docs at `knowledge_architecture/systems/{spec.system_dir}/` before claims
- Every finding: location, severity (critical/high/medium/low), confidence (0-1), recommendation
- Store findings via MCP `store_memory`
- Report to OPUS via MCP `send_ai_message`
- NEVER modify code without authorization

---

## 2. System Context

- **Layer:** {spec.layer}
- **Package:** `packages/{spec.package}/`
- **Docs:** `knowledge_architecture/systems/{spec.system_dir}/`
- **Test baseline:** {spec.test_count} tests
- **MCP tools:** {', '.join(spec.mcp_tools) if spec.mcp_tools else 'None system-specific'}

---

## 3. Audit Protocol

1. Read `systems/{spec.system_dir}/L0_executive.md` for context
2. Run tests: `python -m pytest packages/{spec.package}/ -v` (if package exists)
3. Count tests vs baseline ({spec.test_count})
4. Scan for TODO/FIXME/HACK in `packages/{spec.package}/`
5. Check doc-code parity
6. Produce structured report and store via MCP

---

## 4. Report Format

```
# {spec.system_name} Audit Report
Date: [ISO date]
Agent: AGENT-{spec.system_id.upper()}
Confidence: [0.0-1.0]

## Test Health
- Tests: X/Y passing | Regressions: [list]

## Code Quality  
- TODOs: X | Issues: [list]

## Doc-Code Parity
- Current: yes/no | Gaps: [list]

## Recommendations
1. [actionable items]
```
"""


# ─────────────────────────────────────────────────────────────
# Agent Spawner
# ─────────────────────────────────────────────────────────────

@dataclass
class SpawnResult:
    """Result of spawning a specialist agent."""
    system_id: str
    success: bool
    output: str = ""
    error: str = ""
    genome_tokens: int = 0
    duration_seconds: float = 0.0

class AgentSpawner:
    """Spawns Gemini CLI specialist agents for AIM-OS system auditing."""

    def __init__(self, working_directory: Optional[str] = None):
        self.working_dir = working_directory or str(
            Path(__file__).parent.parent.parent  # AIM-OS root
        )
        self.genomes_dir = Path(self.working_dir) / ".agent" / "genomes"
        self.reports_dir = Path(self.working_dir) / "docs" / "agent_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def get_system_spec(self, system_id: str) -> Optional[SystemSpec]:
        """Get the system specification by ID."""
        return SYSTEM_REGISTRY.get(system_id)

    def list_systems(self) -> list[dict]:
        """List all available specialist systems."""
        return [
            {
                "id": spec.system_id,
                "name": spec.system_name,
                "layer": spec.layer,
                "package": spec.package,
                "tests": spec.test_count,
            }
            for spec in SYSTEM_REGISTRY.values()
        ]

    def generate_genome(self, system_id: str) -> Optional[str]:
        """Generate a specialist genome for a given system."""
        spec = self.get_system_spec(system_id)
        if not spec:
            return None
        return generate_specialist_genome(spec)

    def save_genome(self, system_id: str) -> Optional[Path]:
        """Generate and save a specialist genome to disk."""
        genome_content = self.generate_genome(system_id)
        if not genome_content:
            return None
        filepath = self.genomes_dir / f"specialist_{system_id}.genome.md"
        filepath.write_text(genome_content, encoding="utf-8")
        return filepath

    def save_all_genomes(self) -> list[Path]:
        """Generate and save all specialist genomes."""
        paths = []
        for system_id in SYSTEM_REGISTRY:
            path = self.save_genome(system_id)
            if path:
                paths.append(path)
        return paths

    def build_audit_prompt(self, system_id: str) -> Optional[str]:
        """Build the full audit prompt for a specialist agent."""
        spec = self.get_system_spec(system_id)
        if not spec:
            return None

        genome = generate_specialist_genome(spec)

        # Build the task prompt
        task = f"""You are AGENT-{spec.system_id.upper()}, a specialist auditor for {spec.system_name}.

Your genome (identity and protocols) follows:

{genome}

---

NOW EXECUTE YOUR AUDIT PROTOCOL:

1. Read the L0 executive summary at: knowledge_architecture/systems/{spec.system_dir}/L0_executive.md
2. Check if the package exists at: packages/{spec.package}/
3. If it exists, count Python files and look for test files
4. Scan for TODO/FIXME/HACK comments in the package
5. Check if system docs are up to date
6. Produce your structured audit report

Important: Be thorough but concise. Report facts with confidence scores.
Store your report via store_memory MCP tool if available.
"""
        return task

    def build_docs_prompt(self, task_type: str = "audit") -> Optional[str]:
        """Build documentation engine prompt using the handwritten genome.
        
        Args:
            task_type: One of 'audit' (check coverage), 'parity' (doc-code parity),
                      'update' (update stale docs), 'index' (maintain indexes)
        """
        genome_path = self.genomes_dir / "specialist_docs.genome.md"
        if not genome_path.exists():
            return None
        
        genome = genome_path.read_text(encoding="utf-8")
        
        task_prompts = {
            "audit": """NOW EXECUTE DOCUMENTATION AUDIT:

1. List all directories in knowledge_architecture/systems/
2. For each, check if L0_executive.md or T0_executive.md exists
3. Count systems with full L0-L4 vs partial coverage
4. Check SUPER_INDEX.md — count entries vs actual system dirs
5. Produce your Documentation Engine Report with coverage percentages
""",
            "parity": """NOW EXECUTE DOC-CODE PARITY CHECK:

1. List all directories in packages/
2. For each package, check if corresponding system docs exist in knowledge_architecture/systems/
3. For systems that have both code and docs, compare the L0 summary against actual code
4. Flag discrepancies with severity (CRITICAL/HIGH/MEDIUM/LOW)
5. Produce your Documentation Engine Report focusing on parity gaps
""",
            "update": """NOW EXECUTE DOCUMENTATION UPDATE:

1. Identify systems with outdated or missing T0 executive summaries
2. For each, read the actual code in packages/{system}/
3. Write or update the T0 executive summary (100 words, use metadata format from your genome)
4. Report what you created/updated
""",
            "index": """NOW EXECUTE INDEX MAINTENANCE:

1. Read SUPER_INDEX.md
2. List all system directories in knowledge_architecture/systems/
3. Find entries in SUPER_INDEX that reference non-existent systems (orphaned)
4. Find system directories with no SUPER_INDEX entry (missing)
5. Produce report with orphaned and missing entries
""",
        }
        
        task_instruction = task_prompts.get(task_type, task_prompts["audit"])
        
        return f"""You are AGENT-DOCS, the Documentation Engine for AIM-OS.

Your genome (identity and protocols) follows:

{genome}

---

{task_instruction}

Important: Be thorough but concise. Report facts with confidence scores.
Store your report via store_memory MCP tool with tag 'docs_update'.
"""

    def build_prompt(self, system_id: str, **kwargs) -> Optional[str]:
        """Build the appropriate prompt for a specialist agent.
        
        Routes to specialized prompt builders for cross-cutting agents.
        """
        if system_id == "docs":
            return self.build_docs_prompt(task_type=kwargs.get("task_type", "audit"))
        return self.build_audit_prompt(system_id)

    def spawn_specialist(self, system_id: str) -> SpawnResult:
        """Spawn a Gemini CLI specialist agent for a given system.
        
        This creates the prompt and attempts to execute via GeminiCLIProvider.
        Falls back to saving the prompt to disk if CLI is unavailable.
        """
        spec = self.get_system_spec(system_id)
        if not spec:
            return SpawnResult(
                system_id=system_id,
                success=False,
                error=f"Unknown system: {system_id}",
            )

        prompt = self.build_audit_prompt(system_id)
        genome_tokens = len(prompt.split()) * 1.3  # rough estimate

        # Try GeminiCLIProvider
        try:
            from providers.gemini_cli_provider import GeminiCLIProvider
            provider = GeminiCLIProvider(working_directory=self.working_dir)
            
            import time
            start = time.time()
            result = provider.execute(task=prompt, context="")
            duration = time.time() - start

            # Save report
            report_path = self.reports_dir / f"{system_id}_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_path.write_text(result.get("output", ""), encoding="utf-8")

            return SpawnResult(
                system_id=system_id,
                success=True,
                output=result.get("output", ""),
                genome_tokens=int(genome_tokens),
                duration_seconds=duration,
            )
        except ImportError:
            # CLI provider not available — save prompt for manual execution
            prompt_path = self.reports_dir / f"{system_id}_audit_prompt.md"
            prompt_path.write_text(prompt, encoding="utf-8")
            return SpawnResult(
                system_id=system_id,
                success=False,
                error=f"GeminiCLIProvider not available. Prompt saved to {prompt_path}",
                genome_tokens=int(genome_tokens),
            )
        except Exception as e:
            return SpawnResult(
                system_id=system_id,
                success=False,
                error=str(e),
                genome_tokens=int(genome_tokens),
            )

    def spawn_all_specialists(self) -> list[SpawnResult]:
        """Spawn specialist agents for all core systems."""
        results = []
        for system_id in SYSTEM_REGISTRY:
            result = self.spawn_specialist(system_id)
            results.append(result)
            logger.info(
                f"  {'OK' if result.success else 'FAIL'} {system_id}: "
                f"{result.output[:80] if result.success else result.error}"
            )
        return results


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def main():
    """CLI for the agent spawner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIM-OS Specialist Agent Spawner")
    subparsers = parser.add_subparsers(dest="command")
    
    # List systems
    subparsers.add_parser("list", help="List all specialist systems")
    
    # Generate genomes
    gen_parser = subparsers.add_parser("generate", help="Generate specialist genomes")
    gen_parser.add_argument("--system", help="System ID (or 'all')", default="all")
    
    # Spawn specialist
    spawn_parser = subparsers.add_parser("spawn", help="Spawn specialist agent")
    spawn_parser.add_argument("system", help="System ID to audit")
    
    # Spawn all
    subparsers.add_parser("spawn-all", help="Spawn all specialist agents")
    
    args = parser.parse_args()
    spawner = AgentSpawner()
    
    if args.command == "list":
        systems = spawner.list_systems()
        print(f"\n{'ID':<10} {'Name':<45} {'Layer':<25} {'Tests':>5}")
        print("-" * 90)
        for s in systems:
            print(f"{s['id']:<10} {s['name']:<45} {s['layer']:<25} {s['tests']:>5}")
        print(f"\n{len(systems)} specialist systems available.\n")
    
    elif args.command == "generate":
        if args.system == "all":
            paths = spawner.save_all_genomes()
            print(f"\nGenerated {len(paths)} specialist genomes:")
            for p in paths:
                print(f"  {p.name}")
        else:
            path = spawner.save_genome(args.system)
            if path:
                print(f"Generated: {path}")
            else:
                print(f"Unknown system: {args.system}")

    elif args.command == "spawn":
        print(f"\nSpawning AGENT-{args.system.upper()}...")
        result = spawner.spawn_specialist(args.system)
        if result.success:
            print(f"  Success! ({result.duration_seconds:.1f}s, ~{result.genome_tokens} tokens)")
            print(f"  Output: {result.output[:200]}")
        else:
            print(f"  Error: {result.error}")

    elif args.command == "spawn-all":
        print("\nSpawning all specialist agents...")
        results = spawner.spawn_all_specialists()
        ok = sum(1 for r in results if r.success)
        print(f"\nResults: {ok}/{len(results)} succeeded")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
