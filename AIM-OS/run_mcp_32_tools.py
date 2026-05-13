#!/usr/bin/env python3
"""
Compatibility entrypoint for legacy imports.

Historically, scripts imported `SimpleMCPServer` from `run_mcp_32_tools`.
The active implementation now lives in `lucid_mcp_server.py`.
"""

from lucid_mcp_server import SimpleMCPServer

__all__ = ["SimpleMCPServer"]


def main() -> None:
    server = SimpleMCPServer()
    server.run()


if __name__ == "__main__":
    main()
