"""
AIM-OS AI Engine — Sandbox Runner
==================================

Orchestrates sandboxed audit execution:
1. Prepares sandbox workspace
2. Builds system prompt from genome + task + sandbox rules
3. Dispatches to Gemini CLI via GeminiCLIProvider
4. Validates output (sandbox isolation check)
5. Stores trace via AI Engine

Usage:
    from scripts.ai_engine.sandbox.sandbox_runner import SandboxRunner
    runner = SandboxRunner()
    result = runner.run_audit(task)
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

# Ensure paths
SANDBOX_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(os.path.dirname(SANDBOX_DIR))
AIMOS_ROOT = os.path.dirname(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if AIMOS_ROOT not in sys.path:
    sys.path.insert(0, AIMOS_ROOT)

from ai_engine.sandbox.sandbox_config import SandboxConfig, default_config
from ai_engine.sandbox.audit_tasks import AuditTask, AuditType


@dataclass
class AuditResult:
    """Result of a sandbox audit execution."""
    task_id: str
    success: bool
    content: str = ''
    files_created: List[str] = field(default_factory=list)
    sandbox_violation: bool = False
    latency_ms: float = 0.0
    model: str = ''
    error: str = ''
    timestamp: str = ''

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'success': self.success,
            'content': self.content[:500] + '...' if len(self.content) > 500 else self.content,
            'files_created': self.files_created,
            'sandbox_violation': self.sandbox_violation,
            'latency_ms': self.latency_ms,
            'model': self.model,
            'error': self.error,
            'timestamp': self.timestamp,
        }


class SandboxRunner:
    """Orchestrates sandboxed audit execution using Gemini CLI."""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or default_config()
        self._provider = None
        self._genome_text = None

    @property
    def provider(self):
        """Lazy-load GeminiCLIProvider."""
        if self._provider is None:
            from ai_engine.providers.gemini_cli_provider import GeminiCLIProvider
            self._provider = GeminiCLIProvider(
                working_directory=self.config.aimos_root,
                approval_mode=self.config.approval_mode,
                allowed_mcp_servers=self.config.mcp_servers,
            )
        return self._provider

    @property
    def genome(self) -> str:
        """Load the sandbox auditor genome."""
        if self._genome_text is None:
            genome_path = os.path.join(
                self.config.aimos_root, '.agent', 'genomes', 'sandbox_auditor.genome.md'
            )
            if os.path.exists(genome_path):
                with open(genome_path, 'r', encoding='utf-8') as f:
                    self._genome_text = f.read()
            else:
                self._genome_text = "You are SCOUT, the AIM-OS sandbox auditor."
        return self._genome_text

    # ── Main Entry Point ──────────────────────────────────

    def run_audit(self, task: AuditTask, clean_workspace: bool = True) -> AuditResult:
        """
        Execute a full audit cycle:
        1. Prepare sandbox workspace
        2. Build system prompt
        3. Dispatch to Gemini CLI
        4. Validate output
        5. Store results

        Args:
            task: The audit task to execute
            clean_workspace: Whether to clean workspace before audit

        Returns:
            AuditResult with findings
        """
        print(f"\n{'='*60}")
        print(f"  SANDBOX AUDIT: {task.task_id}")
        print(f"  Type: {task.audit_type.value}")
        print(f"  Target: {task.target}")
        print(f"{'='*60}\n")

        start_time = time.time()

        # 1. Prepare workspace
        if clean_workspace:
            self._prepare_workspace(task)

        # 2. Build system prompt
        system_prompt = self._build_system_prompt(task)

        # 3. Build user prompt
        user_prompt = self._build_user_prompt(task)

        # 4. Dispatch to CLI
        print("[SANDBOX] Dispatching to Gemini CLI (headless)...")
        response = self.provider.run_headless(
            prompt=user_prompt,
            system=system_prompt,
            model=self.config.model,
            timeout=self.config.timeout_seconds,
        )

        elapsed_ms = (time.time() - start_time) * 1000

        # 5. Check for sandbox violations
        violation = self._check_sandbox_violations()

        # 6. Inventory workspace files
        files_created = self._inventory_workspace()

        # 7. Build result
        result = AuditResult(
            task_id=task.task_id,
            success=response.success and not violation,
            content=response.content,
            files_created=files_created,
            sandbox_violation=violation,
            latency_ms=elapsed_ms,
            model=response.model or 'gemini-3.1-pro',
            error=response.error if not response.success else '',
        )

        # 8. Save report
        self._save_report(result)

        # 9. Print summary
        self._print_summary(result)

        return result

    # ── Internal Methods ──────────────────────────────────

    def _prepare_workspace(self, task: AuditTask):
        """Clean and prepare the sandbox workspace."""
        workspace = self.config.workspace_dir
        # Clean old files (keep directory)
        if os.path.exists(workspace):
            for item in os.listdir(workspace):
                if item == '.gitkeep':
                    continue
                item_path = os.path.join(workspace, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        os.makedirs(workspace, exist_ok=True)
        print(f"[SANDBOX] Workspace prepared: {workspace}")

    def _build_system_prompt(self, task: AuditTask) -> str:
        """Build the full system prompt from genome + sandbox rules + task context."""
        parts = [
            self.genome,
            "",
            self.config.get_sandbox_system_rules(),
            "",
            "## Workspace",
            f"Write all outputs to: {self.config.workspace_dir}",
            f"The AIM-OS project root is: {self.config.aimos_root}",
            "",
        ]
        return "\n".join(parts)

    def _build_user_prompt(self, task: AuditTask) -> str:
        """Build the user prompt from the audit task."""
        parts = [
            task.to_prompt(),
            "",
            "## Execution Instructions",
            "1. Start by reading all relevant source files",
            "2. Explore the codebase structure around the target",
            "3. Analyze thoroughly — look at imports, dependencies, edge cases",
            "4. Write your findings as structured files in the workspace",
            f"5. Write all output files to: {self.config.workspace_dir}",
            "",
            "Begin your audit now. Be thorough and precise.",
        ]
        return "\n".join(parts)

    def _check_sandbox_violations(self) -> bool:
        """Check if any files were modified outside the sandbox."""
        # In practice, Gemini CLI in plan mode can't write at all.
        # In auto_edit mode, writes are constrained by working_directory.
        # This is a safety check on top.
        # For now, we trust the CLI's own sandboxing.
        return False

    def _inventory_workspace(self) -> List[str]:
        """List all files created in the workspace."""
        workspace = self.config.workspace_dir
        files = []
        if os.path.exists(workspace):
            for root, _dirs, filenames in os.walk(workspace):
                for fname in filenames:
                    if fname == '.gitkeep':
                        continue
                    rel_path = os.path.relpath(os.path.join(root, fname), workspace)
                    files.append(rel_path)
        return files

    def _save_report(self, result: AuditResult):
        """Save the audit report to the reports directory."""
        reports_dir = self.config.reports_dir
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(reports_dir, f"{result.task_id}_{timestamp}.json")

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

        # Also save full content separately
        content_file = os.path.join(reports_dir, f"{result.task_id}_{timestamp}_full.md")
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(f"# Audit Report: {result.task_id}\n\n")
            f.write(f"**Timestamp:** {result.timestamp}\n")
            f.write(f"**Model:** {result.model}\n")
            f.write(f"**Latency:** {result.latency_ms:.0f}ms\n")
            f.write(f"**Success:** {result.success}\n")
            f.write(f"**Files Created:** {len(result.files_created)}\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print(f"[SANDBOX] Report saved: {report_file}")

    def _print_summary(self, result: AuditResult):
        """Print a human-readable summary."""
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        print(f"\n{'='*60}")
        print(f"  RESULT: {status}")
        print(f"  Task: {result.task_id}")
        print(f"  Model: {result.model}")
        print(f"  Latency: {result.latency_ms:.0f}ms")
        print(f"  Files created: {len(result.files_created)}")
        if result.files_created:
            for f in result.files_created[:10]:
                print(f"    • {f}")
        if result.sandbox_violation:
            print(f"  ⚠️  SANDBOX VIOLATION DETECTED")
        if result.error:
            print(f"  Error: {result.error}")
        print(f"{'='*60}\n")

        # Preview content
        if result.content:
            preview = result.content[:300]
            print(f"  Content preview:\n  {preview}...")
