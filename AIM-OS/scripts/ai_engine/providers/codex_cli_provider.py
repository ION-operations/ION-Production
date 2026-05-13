"""
AIM-OS AI Engine — Codex CLI Provider

Production wrapper around OpenAI's Codex CLI tool (codex-cli v0.111.0).
Uses `codex exec` for non-interactive execution with JSONL output.

Capabilities:
    - Non-interactive exec (codex exec)
    - JSONL structured output (--json)
    - Deliverable capture (--output-last-message)
    - Configurable sandbox (-s danger-full-access | read-only)
    - Headless mode for swarm workers
    - Additional writable directories (--add-dir)

CLI Flags (discovered via `codex exec --help`):
    codex exec              Non-interactive execution
    --json                  JSONL events to stdout
    -o, --output-last-message <FILE>  Write last message to file
    -s, --sandbox <MODE>    Sandbox policy
    --skip-git-repo-check   Skip git repo check
    --add-dir <DIR>         Additional writable directories
    -C <DIR>                Working directory
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger('ai_engine.codex_cli')

# Import shared response types from sibling module
try:
    from .gemini_cli_provider import ProviderResponse
except ImportError:
    # Fallback for direct execution
    @dataclass
    class ProviderResponse:
        """Standardised response from any LLM provider."""
        success: bool
        content: str = ''
        model: str = ''
        provider: str = 'codex-cli'
        tokens_in: int = 0
        tokens_out: int = 0
        latency_ms: float = 0.0
        metadata: Dict[str, Any] = field(default_factory=dict)
        error: str = ''

        def to_dict(self) -> dict:
            return asdict(self)


# ── Sandbox Modes ─────────────────────────────────────────

class SandboxMode:
    """Codex CLI sandbox policies."""
    FULL_ACCESS = 'danger-full-access'
    READ_ONLY = 'read-only'
    DEFAULT = FULL_ACCESS  # Match existing launcher


# ── Codex CLI Provider ───────────────────────────────────

class CodexCLIProvider:
    """
    Production Codex CLI integration.

    Uses `codex exec` for non-interactive agent execution.
    Supports JSONL output and deliverable file capture.

    This is a SECONDARY CLI provider — used alongside Gemini CLI:
      1. When OpenAI models are preferred for a task
      2. When codex-specific capabilities are needed
      3. For multi-provider swarm diversification
    """

    def __init__(
        self,
        cli_path: str = 'codex',
        default_timeout: int = 180,
        working_directory: Optional[str] = None,
        sandbox_mode: str = SandboxMode.DEFAULT,
        additional_dirs: Optional[List[str]] = None,
        skip_git_check: bool = True,
    ):
        import shutil
        # On Windows, npm globals are .cmd files
        resolved = shutil.which(cli_path) or shutil.which(f'{cli_path}.cmd')
        self.cli_path = resolved or cli_path
        self.default_timeout = default_timeout
        self.working_directory = working_directory or os.getcwd()
        self.sandbox_mode = sandbox_mode
        self.additional_dirs = additional_dirs or []
        self.skip_git_check = skip_git_check
        self._available: Optional[bool] = None
        self._version: str = ''
        self._request_count: int = 0
        self._total_latency: float = 0.0

    # ── Availability ─────────────────────────────────────

    def check_available(self) -> dict:
        """Check if Codex CLI is installed and accessible."""
        if self._available is not None:
            return {
                'available': self._available,
                'version': self._version,
                'cli_path': self.cli_path,
            }

        try:
            result = subprocess.run(
                [self.cli_path, '--version'],
                capture_output=True, text=True,
                timeout=10, encoding='utf-8',
            )
            if result.returncode == 0:
                self._version = result.stdout.strip()
                self._available = True
            else:
                self._available = False
                self._version = ''
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            self._available = False
            self._version = ''

        return {
            'available': self._available,
            'version': self._version,
            'cli_path': self.cli_path,
        }

    @property
    def is_available(self) -> bool:
        if self._available is None:
            self.check_available()
        return self._available

    # ── Core Execution ───────────────────────────────────

    def complete(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        timeout: Optional[int] = None,
        sandbox: Optional[str] = None,
        output_json: bool = False,
        additional_dirs: Optional[List[str]] = None,
    ) -> ProviderResponse:
        """
        Execute a prompt via `codex exec` and capture the response.

        Uses --output-last-message to capture the final agent response
        to a temp file, which is then read and returned.

        Args:
            prompt: The user prompt text
            system: Optional system instruction prepended to prompt
            model: Model override (not directly supported by codex exec,
                   included for interface compatibility)
            timeout: Timeout in seconds (default: 180)
            sandbox: Sandbox mode override
            output_json: If True, add --json for JSONL event output
            additional_dirs: Extra writable directories

        Returns:
            ProviderResponse with content from the agent's last message
        """
        if not self.is_available:
            return ProviderResponse(
                success=False,
                provider='codex-cli',
                error='Codex CLI not available. Install: npm install -g @openai/codex',
            )

        timeout = timeout or self.default_timeout

        # Build the full prompt with system instruction
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n---\n\n{prompt}"

        start_time = time.monotonic()

        # Create temp files for prompt input and deliverable output
        prompt_path = None
        deliverable_path = None

        try:
            # Write prompt to temp file (avoids shell escaping issues)
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_codex_prompt.txt',
                delete=False, encoding='utf-8',
            ) as f:
                f.write(full_prompt)
                prompt_path = f.name

            # Temp file for deliverable (--output-last-message)
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_codex_out.txt',
                delete=False, encoding='utf-8',
            ) as f:
                deliverable_path = f.name

            # Build codex exec command
            cmd_parts = [f'"{self.cli_path}"', 'exec']

            # Working directory
            cmd_parts.extend(['-C', f'"{self.working_directory}"'])

            # Sandbox mode
            sb = sandbox or self.sandbox_mode
            cmd_parts.extend(['-s', sb])

            # Output last message to file
            cmd_parts.extend(['--output-last-message', f'"{deliverable_path}"'])

            # Skip git check
            if self.skip_git_check:
                cmd_parts.append('--skip-git-repo-check')

            # JSONL output
            if output_json:
                cmd_parts.append('--json')

            # Additional directories
            dirs = additional_dirs or self.additional_dirs
            for d in dirs:
                cmd_parts.extend(['--add-dir', f'"{d}"'])

            # Pipe prompt from file via stdin
            cmd_str = ' '.join(cmd_parts)
            shell_cmd = f'type "{prompt_path}" | {cmd_str}'

            # Create stderr capture file
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_codex_err.txt',
                delete=False, encoding='utf-8',
            ) as f:
                err_path = f.name

            # Add stderr redirect
            shell_cmd += f' 2> "{err_path}"'

            logger.info(f'[CodexCLI] Executing: {shell_cmd[:200]}...')

            result = subprocess.run(
                shell_cmd,
                shell=True,
                timeout=timeout,
                cwd=self.working_directory,
            )

            latency = (time.monotonic() - start_time) * 1000
            self._request_count += 1
            self._total_latency += latency

            # Read deliverable (last agent message)
            content = ''
            try:
                with open(deliverable_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            except Exception:
                pass

            # Read stderr
            stderr_content = ''
            try:
                with open(err_path, 'r', encoding='utf-8') as f:
                    stderr_content = f.read().strip()
            except Exception:
                pass

            if result.returncode == 0 and content:
                return ProviderResponse(
                    success=True,
                    content=content,
                    model=model or 'codex-default',
                    provider='codex-cli',
                    latency_ms=latency,
                    metadata={
                        'sandbox': sb,
                        'version': self._version,
                        'deliverable_path': deliverable_path,
                    },
                )
            elif result.returncode == 0 and not content:
                return ProviderResponse(
                    success=True,
                    content='(Codex completed but produced no deliverable output)',
                    model=model or 'codex-default',
                    provider='codex-cli',
                    latency_ms=latency,
                    metadata={'sandbox': sb, 'note': 'empty deliverable'},
                )
            else:
                return ProviderResponse(
                    success=False,
                    provider='codex-cli',
                    error=stderr_content or f'Codex CLI exited with code {result.returncode}',
                    latency_ms=latency,
                    content=content,  # May still have partial output
                )

        except subprocess.TimeoutExpired:
            latency = (time.monotonic() - start_time) * 1000
            return ProviderResponse(
                success=False,
                provider='codex-cli',
                error=f'Codex CLI timed out after {timeout}s',
                latency_ms=latency,
            )
        except Exception as e:
            logger.error(f'Codex CLI error: {e}')
            return ProviderResponse(
                success=False,
                provider='codex-cli',
                error=str(e),
            )
        finally:
            # Clean up temp files
            for p in [prompt_path, deliverable_path]:
                if p:
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
            try:
                os.unlink(err_path)
            except Exception:
                pass

    # ── Headless Convenience ──────────────────────────────

    def run_headless(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        timeout: Optional[int] = None,
    ) -> ProviderResponse:
        """
        Run a headless Codex CLI prompt optimised for swarm workers.

        - Full sandbox access (danger-full-access)
        - No JSONL output (just deliverable capture)
        - Skip git repo check for speed

        Args:
            prompt: The prompt text
            system: Optional system instruction
            model: Model override (for interface compat)
            timeout: Timeout in seconds

        Returns:
            ProviderResponse with content
        """
        return self.complete(
            prompt=prompt,
            system=system,
            model=model,
            timeout=timeout or self.default_timeout,
            sandbox=SandboxMode.FULL_ACCESS,
            output_json=False,
        )

    # ── Status & Metrics ─────────────────────────────────

    def status(self) -> dict:
        """Full provider status with metrics."""
        info = self.check_available()
        info.update({
            'provider': 'codex-cli',
            'cost': 'OpenAI API credits',
            'capabilities': [
                'text-completion', 'code-generation', 'file-editing',
                'shell-commands', 'deliverable-capture',
            ],
            'sandbox_mode': self.sandbox_mode,
            'skip_git_check': self.skip_git_check,
            'metrics': {
                'total_requests': self._request_count,
                'avg_latency_ms': (
                    self._total_latency / self._request_count
                    if self._request_count > 0 else 0
                ),
            },
        })
        return info


# ── Quick Test ────────────────────────────────────────────

if __name__ == '__main__':
    """Quick availability check when run directly."""
    provider = CodexCLIProvider()
    status = provider.check_available()

    print('╔════════════════════════════════════════╗')
    print('║   Codex CLI Provider — Quick Check    ║')
    print('╚════════════════════════════════════════╝')
    print()

    if status['available']:
        print(f'  ✅ Codex CLI available')
        print(f'     Version: {status["version"]}')
        print(f'     Path: {status["cli_path"]}')
    else:
        print(f'  ❌ Codex CLI not found')
        print(f'     Install: npm install -g @openai/codex')

    print()
    full = provider.status()
    print(f'  Sandbox: {full["sandbox_mode"]}')
    print(f'  Capabilities: {", ".join(full["capabilities"])}')
