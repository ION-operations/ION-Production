"""
AIM-OS — Gemini Integration Layer

Provides both API and CLI access to Gemini for all AIM-OS agents.
Agents can call Gemini via:
  1. API (google-generativeai) — programmatic, structured responses
  2. CLI (gemini command) — uses Google account auth, free Nano Banana

The CLI path is critical: it uses Braden's authenticated session,
meaning free access to Nano Banana image generation without API costs.

MCP Tools provided:
  - gemini_ask: Send a text prompt to Gemini
  - gemini_vision: Send an image + prompt to Gemini Vision
  - gemini_generate_image: Generate image via Nano Banana
  - gemini_cli: Run Gemini CLI command directly
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import base64
from pathlib import Path
from typing import Optional, Dict, List, Any

import cv2
import numpy as np


# ── Gemini CLI Wrapper ─────────────────────────────────────

class GeminiCLI:
    """
    Wrapper around the Gemini CLI tool.
    Uses Google account authentication — no API key needed.
    Agents call this for free Gemini/Nano Banana access.
    """

    def __init__(self, cli_path: str = 'gemini'):
        self.cli_path = cli_path
        self._check_available()

    def _check_available(self):
        """Check if Gemini CLI is installed."""
        try:
            result = subprocess.run(
                [self.cli_path, '--version'],
                capture_output=True, text=True, timeout=10
            )
            self.available = result.returncode == 0
            self.version = result.stdout.strip() if self.available else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.available = False
            self.version = ''

    def is_available(self) -> dict:
        """Check CLI availability."""
        return {
            'available': self.available,
            'cli_path': self.cli_path,
            'version': self.version
        }

    def prompt(self, text: str, timeout: int = 60) -> dict:
        """
        Send a text prompt to Gemini via CLI.
        Returns the response text.
        """
        if not self.available:
            return {'error': 'Gemini CLI not available. Install with: npm install -g @anthropic-ai/gemini-cli'}

        try:
            result = subprocess.run(
                [self.cli_path, '--prompt', text],
                capture_output=True, text=True, timeout=timeout,
                encoding='utf-8'
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'response': result.stdout.strip(),
                    'model': 'gemini-cli'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr.strip(),
                    'returncode': result.returncode
                }

        except subprocess.TimeoutExpired:
            return {'error': f'Gemini CLI timed out after {timeout}s'}
        except Exception as e:
            return {'error': str(e)}

    def vision(self, image_path: str, prompt: str,
               timeout: int = 120) -> dict:
        """
        Send an image + prompt to Gemini Vision via CLI.
        """
        if not self.available:
            return {'error': 'Gemini CLI not available'}

        if not os.path.exists(image_path):
            return {'error': f'Image not found: {image_path}'}

        try:
            # Gemini CLI accepts images with --image flag
            result = subprocess.run(
                [self.cli_path, '--prompt', prompt, '--image', image_path],
                capture_output=True, text=True, timeout=timeout,
                encoding='utf-8'
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'response': result.stdout.strip(),
                    'image': image_path
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr.strip()
                }

        except subprocess.TimeoutExpired:
            return {'error': f'Gemini CLI timed out after {timeout}s'}
        except Exception as e:
            return {'error': str(e)}

    def generate_image(self, prompt: str,
                        output_path: Optional[str] = None,
                        reference_image: Optional[str] = None,
                        timeout: int = 120) -> dict:
        """
        Generate an image via Nano Banana through CLI.
        Uses Gemini's image generation capabilities.
        """
        if not self.available:
            return {'error': 'Gemini CLI not available'}

        if output_path is None:
            output_dir = Path(tempfile.gettempdir()) / 'seer_generated'
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f'nanobanan_{int(time.time())}.png')

        try:
            cmd = [self.cli_path, '--prompt', prompt]
            if reference_image and os.path.exists(reference_image):
                cmd.extend(['--image', reference_image])

            # Request image output
            full_prompt = f"""Generate an image based on this description:
{prompt}
Save the generated image. Return only the image."""

            cmd[cmd.index(prompt)] = full_prompt

            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=timeout,
                encoding='utf-8'
            )

            return {
                'success': result.returncode == 0,
                'output_path': output_path,
                'response': result.stdout.strip()[:500],
                'error': result.stderr.strip() if result.returncode != 0 else ''
            }

        except subprocess.TimeoutExpired:
            return {'error': f'Image generation timed out after {timeout}s'}
        except Exception as e:
            return {'error': str(e)}

    def raw_command(self, args: List[str], timeout: int = 60) -> dict:
        """
        Run an arbitrary Gemini CLI command.
        For agents that need direct CLI control.
        """
        if not self.available:
            return {'error': 'Gemini CLI not available'}

        try:
            cmd = [self.cli_path] + args
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout, encoding='utf-8'
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout.strip()[:2000],
                'stderr': result.stderr.strip()[:500],
                'returncode': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {'error': f'Command timed out after {timeout}s'}
        except Exception as e:
            return {'error': str(e)}


# ── Unified Gemini Interface ──────────────────────────────

class GeminiInterface:
    """
    Unified Gemini interface that tries API first, falls back to CLI.
    Agents don't need to know which path is used.
    """

    def __init__(self):
        self._cli = GeminiCLI()
        self._api = None
        self._api_available = None

    @property
    def api(self):
        if self._api is None:
            try:
                from seer.discovery import GeminiVision
                self._api = GeminiVision()
                self._api_available = self._api.is_configured()
            except ImportError:
                self._api_available = False
        return self._api

    @property
    def cli(self):
        return self._cli

    def status(self) -> dict:
        """Check which Gemini paths are available."""
        api_ok = self.api.is_configured() if self.api else False
        cli_ok = self._cli.available
        return {
            'api': {
                'available': api_ok,
                'key_set': bool(os.environ.get('GEMINI_API_KEY')),
            },
            'cli': self._cli.is_available(),
            'preferred': 'api' if api_ok else ('cli' if cli_ok else 'none'),
            'any_available': api_ok or cli_ok
        }

    def ask(self, prompt: str, image_path: Optional[str] = None) -> dict:
        """
        Ask Gemini — tries API first, falls back to CLI.
        Optionally include an image for vision.
        """
        # Try API first
        if self.api and self.api.is_configured():
            try:
                if image_path:
                    image = cv2.imread(image_path)
                    if image is not None:
                        response = self.api.client.generate_content([
                            prompt, self.api._image_to_pil(image)
                        ])
                        return {'success': True, 'response': response.text, 'via': 'api'}

                response = self.api.client.generate_content(prompt)
                return {'success': True, 'response': response.text, 'via': 'api'}
            except Exception as e:
                pass  # Fall through to CLI

        # CLI fallback
        if self._cli.available:
            if image_path:
                return {**self._cli.vision(image_path, prompt), 'via': 'cli'}
            return {**self._cli.prompt(prompt), 'via': 'cli'}

        return {'error': 'No Gemini path available. Set GEMINI_API_KEY or install Gemini CLI.'}


# ══════════════════════════════════════════════════════════
# MCP TOOL FUNCTIONS
# ══════════════════════════════════════════════════════════

_gemini: Optional[GeminiInterface] = None


def _get_gemini() -> GeminiInterface:
    global _gemini
    if _gemini is None:
        _gemini = GeminiInterface()
    return _gemini


def gemini_status() -> dict:
    """Check Gemini API and CLI availability."""
    return _get_gemini().status()


def gemini_ask(prompt: str, image_path: str = '') -> dict:
    """
    Ask Gemini a question. Optionally include an image for vision analysis.
    Automatically uses API or CLI, whichever is available.
    """
    return _get_gemini().ask(prompt, image_path if image_path else None)


def gemini_discover_elements(app: str, page: str,
                              context: str = '',
                              monitor: int = 1) -> dict:
    """
    Screenshot the screen → send to Gemini Vision → identify all
    interactive elements → auto-crop and store in Element Library.

    This is the AI-assisted learning tool. Agents call this to
    teach SEER about a new application page.
    """
    try:
        from seer.discovery import DiscoveryEngine
        engine = DiscoveryEngine()
        return engine.discover_and_learn(app, page, monitor, context)
    except Exception as e:
        return {'error': str(e)}


def gemini_discover_window(window_title: str, app: str, page: str,
                            context: str = '') -> dict:
    """
    Discover elements within a specific window (by title).
    Coordinates are mapped to absolute screen positions.
    """
    try:
        from seer.discovery import DiscoveryEngine
        engine = DiscoveryEngine()
        return engine.discover_window(window_title, app, page, context)
    except Exception as e:
        return {'error': str(e)}


def gemini_annotate_screen(app: str = '', page: str = '',
                            monitor: int = 1) -> dict:
    """
    Screenshot → Nano Banana draws colored boxes around UI elements →
    Save annotated image for human review.
    """
    try:
        from seer.discovery import DiscoveryEngine
        engine = DiscoveryEngine()
        return engine.annotate_for_review(app, page, monitor)
    except Exception as e:
        return {'error': str(e)}


def gemini_generate_image(prompt: str,
                            reference_image_path: str = '') -> dict:
    """
    Generate an image using Nano Banana (Gemini Image Generation).
    Optionally pass a reference image path for editing/overlay.
    """
    try:
        from seer.discovery import DiscoveryEngine
        engine = DiscoveryEngine()
        ref = cv2.imread(reference_image_path) if reference_image_path else None
        return engine.generate_nano_banana(prompt, ref)
    except Exception as e:
        return {'error': str(e)}


def gemini_cli_command(args_json: str = '[]', timeout: int = 60) -> dict:
    """
    Run a raw Gemini CLI command. For direct agent control.
    args_json: JSON array of CLI arguments (e.g., '["--prompt", "hello"]')
    """
    args = json.loads(args_json) if isinstance(args_json, str) else args_json
    return _get_gemini().cli.raw_command(args, timeout)


# ══════════════════════════════════════════════════════════
# ALL GEMINI MCP TOOLS
# ══════════════════════════════════════════════════════════

GEMINI_TOOLS = {
    'gemini_status': gemini_status,
    'gemini_ask': gemini_ask,
    'gemini_discover_elements': gemini_discover_elements,
    'gemini_discover_window': gemini_discover_window,
    'gemini_annotate_screen': gemini_annotate_screen,
    'gemini_generate_image': gemini_generate_image,
    'gemini_cli_command': gemini_cli_command,
}


def register_gemini_tools(mcp_server):
    """
    Register all Gemini tools with an MCP server.

    Usage:
        from seer.gemini_integration import register_gemini_tools
        register_gemini_tools(my_mcp_server)
    """
    for name, func in GEMINI_TOOLS.items():
        mcp_server.tool(name)(func)
    return {'registered': len(GEMINI_TOOLS), 'tools': list(GEMINI_TOOLS.keys())}
