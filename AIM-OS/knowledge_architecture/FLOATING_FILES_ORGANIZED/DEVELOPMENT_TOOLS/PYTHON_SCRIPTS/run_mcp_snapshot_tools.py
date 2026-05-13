#!/usr/bin/env python3
"""
MCP Server: Snapshot Management Tools
Purpose: Snapshot system as MCP tools for safe backup/restore
Status: Ready to add to production server when expanding
"""

import asyncio
import json
import sys
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import snapshot system
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.snapshot_system import SnapshotSystem

app = Server("snapshot-tools")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available snapshot tools"""
    return [
        Tool(
            name="create_snapshot",
            description="Create a snapshot of MCP production files before making changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Snapshot name (e.g., 'pre_mcp_expansion')"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of files to snapshot (defaults to MCP files)",
                        "default": None
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="restore_snapshot",
            description="Restore MCP files from a snapshot",
            inputSchema={
                "type": "object",
                "properties": {
                    "snapshot_id": {
                        "type": "string",
                        "description": "ID of snapshot to restore"
                    }
                },
                "required": ["snapshot_id"]
            }
        ),
        Tool(
            name="list_snapshots",
            description="List all available snapshots",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="archive_snapshot",
            description="Archive a snapshot (move to archive/old folder, never delete)",
            inputSchema={
                "type": "object",
                "properties": {
                    "snapshot_id": {
                        "type": "string",
                        "description": "ID of snapshot to archive"
                    }
                },
                "required": ["snapshot_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls"""
    snapshot = SnapshotSystem()
    
    if name == "create_snapshot":
        snap_name = arguments.get("name", "manual_snapshot")
        files = arguments.get("files", None)
        
        if files is None:
            # Default MCP production files
            files = [
                "run_mcp_6_tools.py",
                "mcp_memory/cmc.db",
                "C:/Users/bombe/.cursor/mcp.json"
            ]
        
        manifest = snapshot.create_snapshot(snap_name, files)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "snapshot_id": manifest["snapshot_id"],
                "timestamp": manifest["timestamp"],
                "files_count": len(manifest["files"]),
                "location": f"snapshots/{manifest['snapshot_id']}"
            }, indent=2)
        )]
    
    elif name == "restore_snapshot":
        snapshot_id = arguments.get("snapshot_id")
        if not snapshot_id:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "snapshot_id required"}, indent=2)
            )]
        
        result = snapshot.restore_snapshot(snapshot_id)
        return [TextContent(
            type="text",
            text=json.dumps({"success": result}, indent=2)
        )]
    
    elif name == "list_snapshots":
        snapshots = snapshot.list_snapshots()
        return [TextContent(
            type="text",
            text=json.dumps({"snapshots": snapshots}, indent=2)
        )]
    
    elif name == "archive_snapshot":
        snapshot_id = arguments.get("snapshot_id")
        if not snapshot_id:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "snapshot_id required"}, indent=2)
            )]
        
        result = snapshot.archive_snapshot(snapshot_id)
        return [TextContent(
            type="text",
            text=json.dumps({"success": result}, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
