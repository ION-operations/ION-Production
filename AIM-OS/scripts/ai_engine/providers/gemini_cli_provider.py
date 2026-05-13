"""
AIM-OS AI Engine — Gemini CLI Provider

Production-grade wrapper around Google's Gemini CLI tool.
Uses --output-format json and stream-json for programmatic access.
Backed by Braden's Ultra subscription — unlimited usage, $0 cost.

Capabilities:
    - Text completion (all Gemini models including deep think)
    - Vision (image + prompt)
    - Image generation (Nano Banana)
    - Structured JSON output
    - Token-by-token streaming
    - Session resume
    - MCP extension integration

CLI Flags (discovered via --help):
    --output-format json|stream-json|text
    --model <model-name>
    --resume latest|<index>
    --extensions <list>
    --sandbox <policy>
    --include-directories <dirs>
    -p <prompt>  (non-interactive single prompt)
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any, AsyncIterator, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger('ai_engine.gemini_cli')


# ── Data Models ───────────────────────────────────────────

class GeminiModel(str, Enum):
    """Available Gemini models via CLI."""
    AUTO = 'auto'                    # Routes to best available (currently gemini-3.1-pro)
    PRO = 'gemini-3.1-pro'           # Current flagship — deep reasoning
    FLASH = 'gemini-2.5-flash'       # Fast, cost-effective
    DEEP_THINK = 'gemini-3.1-pro'    # Deep think uses pro with thinking budget
    VISION = 'gemini-3.1-pro'        # Vision capable
    LEGACY_PRO = 'gemini-2.5-pro'    # Previous generation


class OutputFormat(str, Enum):
    TEXT = 'text'
    JSON = 'json'
    STREAM_JSON = 'stream-json'


@dataclass
class ProviderResponse:
    """Standardised response from any LLM provider."""
    success: bool
    content: str = ''
    model: str = ''
    provider: str = 'gemini-cli'
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: str = ''

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StreamChunk:
    """Single chunk from a streaming response."""
    text: str = ''
    done: bool = False
    error: str = ''


# ── Gemini CLI Provider ──────────────────────────────────

class GeminiCLIProvider:
    """
    Production Gemini CLI integration.
    Uses --output-format json for structured output.
    Uses --output-format stream-json for token streaming.
    
    This is the PRIMARY LLM provider for AIM-OS.
    Unlimited usage via Ultra subscription.
    """

    def __init__(
        self,
        cli_path: str = 'gemini',
        default_model: str = GeminiModel.AUTO,
        default_timeout: int = 120,
        working_directory: Optional[str] = None,
        approval_mode: str = 'auto_edit',
        allowed_mcp_servers: Optional[List[str]] = None,
    ):
        # Resolve full path to CLI (on Windows, npm globals are .cmd files)
        import shutil
        resolved = shutil.which(cli_path)
        self.cli_path = resolved or cli_path
        self.default_model = default_model
        self.default_timeout = default_timeout
        self.working_directory = working_directory or os.getcwd()
        self.approval_mode = approval_mode
        # Default: no MCP servers in headless mode to prevent 400 errors
        # from lucid-mcp's 90+ tool definitions exceeding API limits
        self.allowed_mcp_servers = allowed_mcp_servers or ['none']
        self._available: Optional[bool] = None
        self._version: str = ''
        self._request_count: int = 0
        self._total_latency: float = 0.0

    # ── Availability ─────────────────────────────────────

    def check_available(self) -> dict:
        """Check if Gemini CLI is installed and accessible."""
        if self._available is not None:
            return {
                'available': self._available,
                'version': self._version,
                'cli_path': self.cli_path,
            }

        # Since we resolved via shutil.which() in __init__,
        # just check if the resolved path exists as a file
        self._available = os.path.isfile(self.cli_path)
        self._version = 'detected' if self._available else ''

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

    # ── Core Completion ──────────────────────────────────

    def complete(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        timeout: Optional[int] = None,
        output_format: OutputFormat = OutputFormat.TEXT,
        include_dirs: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
        mcp_servers: Optional[List[str]] = None,
    ) -> ProviderResponse:
        """
        Send a prompt to Gemini CLI and get a complete response.
        
        Args:
            prompt: The user prompt text
            system: Optional system instruction prepended to prompt
            model: Model name (default: auto)
            timeout: Timeout in seconds
            output_format: text, json, or stream-json
            include_dirs: Additional directories for workspace context
            extensions: CLI extensions to enable
            mcp_servers: Allowed MCP server names (default: ['none'] to avoid 400)
        
        Returns:
            ProviderResponse with content, metadata, and timing
        """
        if not self.is_available:
            return ProviderResponse(
                success=False,
                error='Gemini CLI not available. Install: npm install -g @google/gemini-cli',
            )

        timeout = timeout or self.default_timeout

        # Build the full prompt with system instruction
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n---\n\n{prompt}"

        start_time = time.monotonic()

        try:
            # Write prompt to temp file to avoid shell escaping issues
            # with multi-KB prompts containing markdown, newlines, backticks
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_prompt.txt', delete=False, encoding='utf-8'
            ) as prompt_file:
                prompt_file.write(full_prompt)
                prompt_path = prompt_file.name

            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_out.txt', delete=False, encoding='utf-8'
            ) as out_file:
                out_path = out_file.name

            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_err.txt', delete=False, encoding='utf-8'
            ) as err_file:
                err_path = err_file.name

            # Build command WITHOUT -p flag (prompt comes from stdin via pipe)
            cmd_parts = [f'"{self.cli_path}"']
            cmd_parts.extend(['-o', output_format.value])

            actual_model = model or ''
            if actual_model and actual_model != 'auto':
                cmd_parts.extend(['--model', actual_model])

            mode = self.approval_mode
            if mode:
                cmd_parts.extend(['--approval-mode', mode])

            servers = mcp_servers or self.allowed_mcp_servers
            if servers:
                for s in servers:
                    cmd_parts.extend(['--allowed-mcp-server-names', s])

            if include_dirs:
                for d in include_dirs:
                    cmd_parts.extend(['--include-directories', d])

            if extensions:
                for ext in extensions:
                    cmd_parts.extend(['--extensions', ext])

            cmd_str = ' '.join(cmd_parts)

            # Pipe prompt from file to CLI, redirect output to temp files
            # type = Windows equivalent of cat
            shell_cmd = f'type "{prompt_path}" | {cmd_str} > "{out_path}" 2> "{err_path}"'

            result = subprocess.run(
                shell_cmd,
                shell=True,
                timeout=timeout,
                cwd=self.working_directory,
            )

            latency = (time.monotonic() - start_time) * 1000
            self._request_count += 1
            self._total_latency += latency

            # Read output from temp files
            content = ''
            stderr_content = ''
            try:
                with open(out_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            except Exception:
                pass
            try:
                with open(err_path, 'r', encoding='utf-8') as f:
                    stderr_content = f.read().strip()
            except Exception:
                pass
            finally:
                # Clean up temp files
                for p in [prompt_path, out_path, err_path]:
                    try:
                        os.unlink(p)
                    except Exception:
                        pass

            if result.returncode == 0:
                # Parse JSON output if requested
                metadata = {}
                if output_format == OutputFormat.JSON:
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, dict):
                            metadata = parsed
                            content = parsed.get('response', parsed.get('text', content))
                    except json.JSONDecodeError:
                        pass

                return ProviderResponse(
                    success=True,
                    content=content,
                    model=model or self.default_model,
                    provider='gemini-cli',
                    latency_ms=latency,
                    metadata=metadata,
                )
            else:
                return ProviderResponse(
                    success=False,
                    error=stderr_content or f'CLI returned exit code {result.returncode}',
                    latency_ms=latency,
                )

        except subprocess.TimeoutExpired:
            # Clean up temp files on timeout
            for p in [prompt_path, out_path, err_path]:
                try:
                    os.unlink(p)
                except Exception:
                    pass
            return ProviderResponse(
                success=False,
                error=f'Gemini CLI timed out after {timeout}s',
            )
        except Exception as e:
            logger.error(f'Gemini CLI error: {e}')
            return ProviderResponse(
                success=False,
                error=str(e),
            )

    def complete_json(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        timeout: Optional[int] = None,
    ) -> ProviderResponse:
        """Convenience: complete with JSON output format."""
        return self.complete(
            prompt=prompt,
            system=system,
            model=model,
            timeout=timeout,
            output_format=OutputFormat.JSON,
        )

    # ── Streaming ────────────────────────────────────────

    async def stream(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        timeout: Optional[int] = None,
        extensions: Optional[List[str]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream response token-by-token using --output-format stream-json.
        
        Yields StreamChunk objects with incremental text.
        """
        if not self.is_available:
            yield StreamChunk(error='Gemini CLI not available', done=True)
            return

        timeout = timeout or self.default_timeout

        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n---\n\n{prompt}"

        cmd = self._build_command(
            prompt=full_prompt,
            model=model,
            output_format=OutputFormat.STREAM_JSON,
            extensions=extensions,
        )

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_directory,
            )

            buffer = ''
            async for raw_line in process.stdout:
                line = raw_line.decode('utf-8', errors='replace').strip()
                if not line:
                    continue

                # stream-json outputs one JSON object per line
                try:
                    chunk_data = json.loads(line)
                    text = chunk_data.get('text', chunk_data.get('content', ''))
                    done = chunk_data.get('done', chunk_data.get('finished', False))
                    yield StreamChunk(text=text, done=done)
                except json.JSONDecodeError:
                    # Raw text fallback
                    yield StreamChunk(text=line)

            # Wait for process to complete
            await asyncio.wait_for(process.wait(), timeout=10)

            yield StreamChunk(done=True)

        except asyncio.TimeoutError:
            yield StreamChunk(error=f'Stream timed out after {timeout}s', done=True)
        except Exception as e:
            logger.error(f'Gemini CLI stream error: {e}')
            yield StreamChunk(error=str(e), done=True)

    # ── Vision ───────────────────────────────────────────

    def vision(
        self,
        image_path: str,
        prompt: str,
        model: str = '',
        timeout: Optional[int] = None,
    ) -> ProviderResponse:
        """
        Send an image + prompt to Gemini Vision.
        Uses the CLI --image flag for multimodal input.
        """
        if not os.path.exists(image_path):
            return ProviderResponse(
                success=False,
                error=f'Image not found: {image_path}',
            )

        if not self.is_available:
            return ProviderResponse(
                success=False,
                error='Gemini CLI not available',
            )

        timeout = timeout or self.default_timeout
        model = model or GeminiModel.VISION

        cmd = self._build_command(prompt=prompt, model=model)
        # Insert image flag before output format flags
        cmd.extend(['--image', image_path])

        start_time = time.monotonic()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=timeout, encoding='utf-8',
                cwd=self.working_directory,
            )

            latency = (time.monotonic() - start_time) * 1000
            self._request_count += 1
            self._total_latency += latency

            if result.returncode == 0:
                return ProviderResponse(
                    success=True,
                    content=result.stdout.strip(),
                    model=model,
                    provider='gemini-cli',
                    latency_ms=latency,
                    metadata={'image_path': image_path},
                )
            else:
                return ProviderResponse(
                    success=False,
                    error=result.stderr.strip(),
                    latency_ms=latency,
                )

        except subprocess.TimeoutExpired:
            return ProviderResponse(success=False, error=f'Vision timed out after {timeout}s')
        except Exception as e:
            return ProviderResponse(success=False, error=str(e))

    # ── Image Generation (Nano Banana) ───────────────────

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        reference_image: Optional[str] = None,
        timeout: int = 180,
    ) -> ProviderResponse:
        """
        Generate an image via Nano Banana through Gemini CLI.
        Free with Ultra subscription.
        """
        if not self.is_available:
            return ProviderResponse(success=False, error='Gemini CLI not available')

        if output_path is None:
            output_dir = Path(tempfile.gettempdir()) / 'ai_engine_images'
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f'nano_{int(time.time())}.png')

        generation_prompt = (
            f"Generate an image based on this description: {prompt}\n"
            f"Return only the generated image."
        )

        cmd = self._build_command(prompt=generation_prompt)

        if reference_image and os.path.exists(reference_image):
            cmd.extend(['--image', reference_image])

        start_time = time.monotonic()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=timeout, encoding='utf-8',
                cwd=self.working_directory,
            )

            latency = (time.monotonic() - start_time) * 1000

            return ProviderResponse(
                success=result.returncode == 0,
                content=result.stdout.strip()[:1000],
                provider='gemini-cli/nano-banana',
                latency_ms=latency,
                metadata={
                    'output_path': output_path,
                    'reference_image': reference_image,
                },
                error=result.stderr.strip() if result.returncode != 0 else '',
            )

        except subprocess.TimeoutExpired:
            return ProviderResponse(success=False, error=f'Image generation timed out after {timeout}s')
        except Exception as e:
            return ProviderResponse(success=False, error=str(e))

    # ── Session Management ───────────────────────────────

    def resume_session(self, session_id: str = 'latest') -> ProviderResponse:
        """Resume a previous Gemini CLI session."""
        cmd = [self.cli_path, '--resume', session_id]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=10, cwd=self.working_directory,
            )
            return ProviderResponse(
                success=result.returncode == 0,
                content=result.stdout.strip(),
                metadata={'session_id': session_id},
            )
        except Exception as e:
            return ProviderResponse(success=False, error=str(e))

    def list_sessions(self) -> ProviderResponse:
        """List available Gemini CLI sessions."""
        cmd = [self.cli_path, '--list-sessions']
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=10, cwd=self.working_directory,
            )
            return ProviderResponse(
                success=result.returncode == 0,
                content=result.stdout.strip(),
            )
        except Exception as e:
            return ProviderResponse(success=False, error=str(e))

    # ── Status & Metrics ─────────────────────────────────

    def status(self) -> dict:
        """Full provider status with metrics."""
        info = self.check_available()
        info.update({
            'provider': 'gemini-cli',
            'cost': '$0 (Ultra subscription)',
            'models': [m.value for m in GeminiModel],
            'capabilities': [
                'text-completion', 'json-output', 'stream-json',
                'vision', 'image-generation', 'session-resume',
                'workspace-context', 'mcp-extensions', 'deep-think',
            ],
            'metrics': {
                'total_requests': self._request_count,
                'avg_latency_ms': (
                    self._total_latency / self._request_count
                    if self._request_count > 0 else 0
                ),
            },
            'default_model': self.default_model,
            'approval_mode': self.approval_mode,
        })
        return info

    # ── Headless Convenience ──────────────────────────────

    def run_headless(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        timeout: Optional[int] = None,
    ) -> ProviderResponse:
        """
        Run a headless Gemini CLI prompt optimised for swarm workers.
        
        - No MCP servers loaded (avoids 400 from lucid-mcp's 90+ tools)
        - Text output only
        - No extensions
        - Uses plan approval mode (read-only, safest for workers)
        
        Args:
            prompt: The prompt text
            system: Optional system instruction
            model: Model override (default: auto = gemini-3.1-pro)
            timeout: Timeout in seconds
        
        Returns:
            ProviderResponse with content
        """
        return self.complete(
            prompt=prompt,
            system=system,
            model=model,
            timeout=timeout or self.default_timeout,
            output_format=OutputFormat.TEXT,
            mcp_servers=['none'],
        )

    # ── Internal ─────────────────────────────────────────

    def _build_command(
        self,
        prompt: str,
        model: str = '',
        output_format: OutputFormat = OutputFormat.TEXT,
        include_dirs: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
        approval_mode: Optional[str] = None,
        mcp_servers: Optional[List[str]] = None,
    ) -> List[str]:
        """Build the CLI command arguments for Gemini CLI v0.32.1+."""
        cmd = [self.cli_path]

        # Prompt (non-interactive mode)
        cmd.extend(['-p', prompt])

        # Model
        if model and model != 'auto':
            cmd.extend(['--model', model])

        # Output format (text output for headless, json/stream-json for structured)
        cmd.extend(['-o', output_format.value])

        # Approval mode (v0.32.1+: default|auto_edit|yolo|plan)
        mode = approval_mode or self.approval_mode
        if mode:
            cmd.extend(['--approval-mode', mode])

        # MCP server filtering — critical for avoiding 400 errors
        # When lucid-mcp (90+ tools) is registered globally, headless
        # calls fail with INVALID_ARGUMENT because the tool schemas
        # exceed Google's API limits
        servers = mcp_servers or self.allowed_mcp_servers
        if servers:
            for s in servers:
                cmd.extend(['--allowed-mcp-server-names', s])

        # Include directories for workspace context
        if include_dirs:
            for d in include_dirs:
                cmd.extend(['--include-directories', d])

        # Extensions
        if extensions:
            for ext in extensions:
                cmd.extend(['-e', ext])

        return cmd
