"""
AIM-OS AI Engine — Audit Task Templates
=========================================

Pre-defined audit tasks that the sandbox agent can execute.
Each task type defines what to analyze, how to structure output,
and what success looks like.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class AuditType(Enum):
    """Types of audit tasks the sandbox agent can perform."""
    PACKAGE = 'package_audit'
    ABILITY = 'ability_audit'
    INTEGRATION = 'integration_audit'
    SELF_IMPROVE = 'self_improve'
    CODEBASE_SCAN = 'codebase_scan'


@dataclass
class AuditTask:
    """A structured audit task for the sandbox agent."""
    task_id: str
    audit_type: AuditType
    target: str  # What to audit (package name, file path, capability name)
    description: str
    focus_areas: List[str] = field(default_factory=list)
    context_files: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    max_tokens: int = 16000
    priority: str = 'medium'

    def to_prompt(self) -> str:
        """Convert this task to a prompt for the sandbox agent."""
        prompt = f"# Audit Task: {self.task_id}\n\n"
        prompt += f"**Type:** {self.audit_type.value}\n"
        prompt += f"**Target:** {self.target}\n\n"
        prompt += f"## Description\n{self.description}\n\n"

        if self.focus_areas:
            prompt += "## Focus Areas\n"
            for area in self.focus_areas:
                prompt += f"- {area}\n"
            prompt += "\n"

        if self.context_files:
            prompt += "## Key Files to Examine\n"
            for f in self.context_files:
                prompt += f"- `{f}`\n"
            prompt += "\n"

        if self.expected_outputs:
            prompt += "## Expected Outputs\n"
            for output in self.expected_outputs:
                prompt += f"- {output}\n"
            prompt += "\n"

        return prompt


# ── Pre-built Task Templates ──────────────────────────────


def package_audit(package_name: str, package_path: str = '') -> AuditTask:
    """Audit a package: API surface, bugs, test coverage, documentation."""
    if not package_path:
        package_path = f"packages/{package_name}"

    return AuditTask(
        task_id=f"pkg_audit_{package_name}",
        audit_type=AuditType.PACKAGE,
        target=package_name,
        description=f"""Perform a comprehensive audit of the `{package_name}` package.

Your goal is to thoroughly understand this package and produce a detailed report.
You MUST read all source files in the package before writing your report.""",
        focus_areas=[
            "API surface — document all public classes, functions, and their signatures",
            "Bugs — identify any bugs, race conditions, or error handling gaps",
            "Code quality — assess naming, structure, complexity, DRY violations",
            "Test coverage — identify untested code paths",
            "Documentation — assess inline docs, missing docstrings",
            "Dependencies — what this package imports and depends on",
            "Integration points — how other packages use this one",
        ],
        context_files=[
            package_path,
            f"{package_path}/__init__.py",
        ],
        expected_outputs=[
            "Write `audit_report.md` in your workspace with full findings",
            "Write `api_surface.json` listing all public APIs with signatures",
            "Write `bugs_found.json` listing any bugs with severity and file:line",
            "Write `recommendations.md` with prioritized improvement suggestions",
        ],
    )


def ability_audit(capability: str, engine_path: str = 'scripts/ai_engine') -> AuditTask:
    """Audit a specific AI Engine capability."""
    return AuditTask(
        task_id=f"ability_audit_{capability}",
        audit_type=AuditType.ABILITY,
        target=capability,
        description=f"""Audit the `{capability}` capability of the AIM-OS AI Engine.

Read the engine source code, understand how this capability works,
assess its strengths and weaknesses, and propose improvements.
Write improved code in your workspace to demonstrate your proposals.""",
        focus_areas=[
            f"How {capability} is implemented in the engine",
            "Input/output contract and data flow",
            "Edge cases and failure modes",
            "Performance characteristics",
            "How it could be improved or extended",
        ],
        context_files=[
            f"{engine_path}/engine.py",
            f"{engine_path}/test_harness.py",
        ],
        expected_outputs=[
            "Write `capability_analysis.md` with detailed assessment",
            "Write `improved_code.py` with proposed improvements",
            "Write `test_cases.py` with new test cases for edge cases",
        ],
    )


def self_improve_task(
    audit_findings: str,
    target_file: str,
    improvement_goal: str,
) -> AuditTask:
    """Given prior audit findings, write improved code and test it."""
    return AuditTask(
        task_id=f"self_improve_{target_file.replace('/', '_').replace('.', '_')}",
        audit_type=AuditType.SELF_IMPROVE,
        target=target_file,
        description=f"""Based on the following audit findings, write improved code.

## Prior Audit Findings
{audit_findings}

## Improvement Goal
{improvement_goal}

## Instructions
1. Read the current implementation of `{target_file}`
2. Write an improved version in your workspace
3. Write tests for the improved version
4. Write a migration guide explaining what changed and why""",
        focus_areas=[
            "Address all issues identified in the audit",
            "Maintain backward compatibility",
            "Add comprehensive error handling",
            "Include proper type hints and docstrings",
        ],
        context_files=[target_file],
        expected_outputs=[
            f"Write improved version of the target file in workspace",
            "Write `tests.py` with test cases for the improvements",
            "Write `migration_guide.md` explaining changes",
        ],
    )


def codebase_scan(scope: str = 'packages', focus: str = 'health') -> AuditTask:
    """Broad codebase health scan."""
    return AuditTask(
        task_id=f"codebase_scan_{scope}_{focus}",
        audit_type=AuditType.CODEBASE_SCAN,
        target=scope,
        description=f"""Perform a broad health scan of the AIM-OS `{scope}/` directory.

Focus on: {focus}

Scan all subdirectories, identify patterns, and produce a health report.
This is a broad overview, not a deep dive into any single package.""",
        focus_areas=[
            "Package inventory — list all packages with status",
            "Common patterns — identify shared patterns across packages",
            "Inconsistencies — naming, structure, or convention violations",
            "Dead code — packages that appear unused or abandoned",
            f"Specific focus: {focus}",
        ],
        context_files=[scope],
        expected_outputs=[
            "Write `health_report.md` with overview findings",
            "Write `package_inventory.json` listing all packages with metadata",
            "Write `action_items.md` with prioritized fixes",
        ],
    )
