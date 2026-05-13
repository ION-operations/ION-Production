#!/usr/bin/env python3
"""
Daemon/RAG MCP Server - MCP Protocol Wrapper

Wraps Daemon/RAG System for Cursor IDE integration via MCP protocol.
Handles JSON-RPC 2.0 protocol communication and delegates to Daemon/RAG system.

Author: Sonnet (for Daemon/RAG System)
Date: 2025-10-31
Purpose: Enable Cursor IDE integration via MCP protocol
"""

import sys
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add AIM-OS root to path for imports
aimos_root = Path(__file__).parent.parent
sys.path.insert(0, str(aimos_root))
# Also add daemon_rag_system directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Try importing as module first
    try:
        from daemon_rag_system.daemon_rag_system import DaemonRAGSystem, DaemonConfig, DaemonStatus
    except ImportError:
        # Fallback: import directly from file
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "daemon_rag_system",
            Path(__file__).parent / "daemon_rag_system.py"
        )
        daemon_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(daemon_module)
        DaemonRAGSystem = daemon_module.DaemonRAGSystem
        DaemonConfig = daemon_module.DaemonConfig
        DaemonStatus = daemon_module.DaemonStatus
    DAEMON_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to import Daemon/RAG system: {e}")
    DAEMON_AVAILABLE = False
    DaemonRAGSystem = None
    DaemonConfig = None
    DaemonStatus = None


class MCPProtocolHandler:
    """Handles MCP protocol communication for Daemon/RAG System"""
    
    def __init__(self):
        """Initialize MCP protocol handler"""
        self.daemon: Optional[DaemonRAGSystem] = None
        self.config: Optional[DaemonConfig] = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize daemon system"""
        if not DAEMON_AVAILABLE:
            logger.error("Daemon/RAG system not available")
            return False
        
        try:
            self.config = DaemonConfig(
                max_tools=40,
                learning_enabled=True,
                performance_monitoring_enabled=True,
                log_level="INFO"
            )
            self.daemon = DaemonRAGSystem(self.config)
            success = self.daemon.start()
            
            if success:
                self.initialized = True
                logger.info("Daemon/RAG system initialized successfully")
            else:
                logger.error("Failed to start daemon system")
            
            return success
        except Exception as e:
            logger.error(f"Error initializing daemon: {e}", exc_info=True)
            return False
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol request"""
        if not self.initialized and request.get("method") != "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": "Server not initialized. Call initialize first."
                }
            }
        
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request_id, params)
            elif method == "ping":
                return self._handle_ping(request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def _handle_initialize(self, request_id: Optional[int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        if not self.initialized:
            success = self.initialize()
            if not success:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": "Failed to initialize daemon system"
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "daemon-rag-system",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list(self, request_id: Optional[int]) -> Dict[str, Any]:
        """Handle tools/list request - return available tools from daemon"""
        if not self.daemon:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": "Daemon not initialized"
                }
            }
        
        try:
            # Get tools from daemon's tool registry
            tools = self.daemon.tool_registry.get_all_tools()
            
            # Convert to MCP tool format (limit to 40 tools as per daemon config)
            mcp_tools = []
            for tool in tools[:40]:  # Ensure we don't exceed 40-tool limit
                mcp_tools.append({
                    "name": tool.tool_id,
                    "description": tool.description,
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "user_input": {
                                "type": "string",
                                "description": "User input text describing the task"
                            },
                            "environment": {
                                "type": "object",
                                "description": "Environment context (optional)",
                                "additionalProperties": True
                            }
                        },
                        "required": ["user_input"]
                    }
                })
            
            logger.info(f"Returning {len(mcp_tools)} tools to Cursor IDE")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": mcp_tools
                }
            }
        except Exception as e:
            logger.error(f"Error listing tools: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Error listing tools: {str(e)}"
                }
            }
    
    def _handle_tools_call(self, request_id: Optional[int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request - process request through daemon"""
        if not self.daemon:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": "Daemon not initialized"
                }
            }
        
        try:
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Extract user input and environment from arguments
            user_input = arguments.get("user_input", "")
            environment = arguments.get("environment", {})
            
            if not user_input:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Missing required parameter: user_input"
                    }
                }
            
            # Process request through daemon system
            logger.info(f"Processing request via tool: {tool_name}")
            response = self.daemon.process_request(
                user_input=user_input,
                environment=environment or {}
            )
            
            # Format response for MCP protocol
            if response.get("success"):
                # Success response
                content_text = json.dumps({
                    "selected_tools": response.get("selected_tools", []),
                    "context_profile": response.get("context_profile", {}),
                    "selection_result": response.get("selection_result", {}),
                    "performance_metrics": response.get("performance_metrics", {}),
                    "reasoning": response.get("reasoning", "")
                }, indent=2)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": content_text
                            }
                        ]
                    }
                }
            else:
                # Error response
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": response.get("error", "Unknown error processing request")
                    }
                }
                
        except Exception as e:
            logger.error(f"Error calling tool: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Error processing request: {str(e)}"
                }
            }
    
    def _handle_ping(self, request_id: Optional[int]) -> Dict[str, Any]:
        """Handle ping request"""
        if self.daemon and DAEMON_AVAILABLE:
            status = self.daemon.status.value if hasattr(self.daemon.status, 'value') else str(self.daemon.status)
        else:
            status = "stopped"
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "status": status,
                "daemon_initialized": self.initialized
            }
        }
    
    def shutdown(self):
        """Shutdown daemon system"""
        if self.daemon:
            try:
                self.daemon.stop()
                logger.info("Daemon system stopped")
            except Exception as e:
                logger.error(f"Error stopping daemon: {e}")


def main():
    """Main MCP server loop - handles stdio communication"""
    handler = MCPProtocolHandler()
    
    # Process requests from stdin (MCP protocol uses stdio)
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                
                # Handle request
                response = handler.handle_request(request)
                
                # Send response to stdout
                print(json.dumps(response))
                sys.stdout.flush()  # CRITICAL: Flush immediately for MCP protocol
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        handler.shutdown()


if __name__ == "__main__":
    # Use unbuffered I/O for MCP protocol (CRITICAL on Windows)
    if sys.platform == "win32":
        import msvcrt
        import os
        # Set stdout to binary mode for unbuffered output
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
        sys.stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0)
    
    main()

