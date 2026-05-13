LUCID MCP Daemon — Capsule summary

Launch:
  python -u lucid_mcp_server.py

  Run from the AIM-OS (or project) repository root so that packages/ and workspace paths resolve.
  Set PYTHONPATH to that root. The -u flag keeps stdout/stderr unbuffered (required for MCP over stdio).

MCP transport:
  JSON-RPC 2.0 over stdio. One JSON object per line on stdin/stdout; flush after each response.
  All logging goes to stderr so stdout stays JSON-only for the protocol.

Tools:
  Registered on SimpleMCPServer. Exposed via initialize, tools/list, and tools/call.
  For full runtime (packages/, CMC, HHNI, etc.) use the complete AIM-OS repo; this capsule includes only the daemon entrypoint for mission reference.
