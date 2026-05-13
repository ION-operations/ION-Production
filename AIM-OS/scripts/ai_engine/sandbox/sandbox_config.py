"""
AIM-OS AI Engine — Sandbox Configuration
=========================================

Defines paths, permissions, and resource limits for sandboxed agent execution.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class SandboxConfig:
    """Configuration for a sandbox execution environment."""

    # ── Paths ──
    aimos_root: str = ''
    sandbox_root: str = ''
    workspace_dir: str = ''
    reports_dir: str = ''

    # ── Permissions ──
    read_paths: List[str] = field(default_factory=list)
    write_paths: List[str] = field(default_factory=list)
    forbidden_paths: List[str] = field(default_factory=list)

    # ── Resource limits ──
    max_output_tokens: int = 32000
    timeout_seconds: int = 300
    max_workspace_size_mb: int = 100

    # ── CLI settings ──
    approval_mode: str = 'auto_edit'
    mcp_servers: List[str] = field(default_factory=lambda: ['none'])
    model: str = ''  # auto

    def __post_init__(self):
        if not self.aimos_root:
            self.aimos_root = str(Path(__file__).parent.parent.parent.parent)
        if not self.sandbox_root:
            self.sandbox_root = str(Path(__file__).parent)
        if not self.workspace_dir:
            self.workspace_dir = os.path.join(self.sandbox_root, 'workspace')
        if not self.reports_dir:
            self.reports_dir = os.path.join(self.sandbox_root, 'reports')
        if not self.read_paths:
            self.read_paths = [
                self.aimos_root,  # Full AIM-OS codebase (read-only)
            ]
        if not self.write_paths:
            self.write_paths = [
                self.workspace_dir,
                self.reports_dir,
            ]
        if not self.forbidden_paths:
            self.forbidden_paths = [
                os.path.join(self.aimos_root, '.git'),
                os.path.join(self.aimos_root, 'node_modules'),
                os.path.join(self.aimos_root, '.env'),
            ]

    def ensure_directories(self):
        """Create sandbox directories if they don't exist."""
        os.makedirs(self.workspace_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def is_write_allowed(self, path: str) -> bool:
        """Check if a path is within allowed write areas."""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(os.path.abspath(wp)) for wp in self.write_paths)

    def is_read_allowed(self, path: str) -> bool:
        """Check if a path is within allowed read areas."""
        abs_path = os.path.abspath(path)
        # Block forbidden paths
        if any(abs_path.startswith(os.path.abspath(fp)) for fp in self.forbidden_paths):
            return False
        return any(abs_path.startswith(os.path.abspath(rp)) for rp in self.read_paths)

    def get_sandbox_system_rules(self) -> str:
        """Generate system prompt rules for sandbox enforcement."""
        return f"""## SANDBOX RULES (MANDATORY)
You are operating in a SANDBOXED environment.

### ALLOWED:
- READ any file in: {', '.join(self.read_paths)}
- WRITE files ONLY in: {self.workspace_dir}
- Search the web for documentation, best practices, patterns
- Analyze code, find bugs, propose improvements

### FORBIDDEN:
- Writing ANY file outside {self.workspace_dir}
- Modifying production code directly
- Accessing: {', '.join(self.forbidden_paths)}
- Running destructive commands (rm, del, format)
- Installing system packages

### OUTPUT:
- Write your analysis to {self.workspace_dir}/
- Structure findings as JSON when possible
- Include confidence scores for findings
"""


def default_config() -> SandboxConfig:
    """Create a default sandbox configuration."""
    config = SandboxConfig()
    config.ensure_directories()
    return config
