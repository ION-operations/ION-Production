"""
MCP Client - Wrapper for Command Server HTTP calls

# NL_TAG: ROUTER-API-MCP-001 | MCP client wrapper for Command Server HTTP integration | MCPClient.execute_tool(...) -> Dict[str, Any] | []
# NL_TAG_CONNECT: ROUTER-API-MCP-CMD-001 | MCP client calls Command Server HTTP endpoint | execute_tool → POST /mcp/execute | [ROUTER-API-MCP-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-002 | MCP integration via HTTP wrapper simplifies AIM-OS system access without direct stdio management | HTTP wrapper pattern | [ADR-MCP-INTEGRATION]
# NL_TAG_SPEC: ROUTER-API-SPEC-002 | Validates MCP tool execution requests/responses | MCP tool schema | [mcp_tool_schema.json]
"""

import httpx
import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP client wrapper for Command Server HTTP integration.
    
    Provides async HTTP client for calling MCP tools via Command Server.
    """
    
    def __init__(self, command_server_url: str = "http://localhost:5001"):
        """
        Initialize MCP client.
        
        Args:
            command_server_url: Command Server HTTP endpoint URL
        """
        self.command_server_url = command_server_url.rstrip('/')
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        logger.info(f"MCP Client initialized with Command Server: {command_server_url}")
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute MCP tool via Command Server HTTP endpoint.
        
        Args:
            tool_name: MCP tool name (e.g., "mcp_lucid-mcp_store_memory")
            arguments: Tool arguments dictionary
            retries: Number of retry attempts on failure
            
        Returns:
            Tool execution result dictionary
            
        Raises:
            HTTPException: If tool execution fails after retries
        """
        url = f"{self.command_server_url}/mcp/execute"
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }
        
        last_error = None
        for attempt in range(retries):
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"MCP tool executed: {tool_name} (attempt {attempt + 1})")
                return result
                
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"MCP tool execution failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=f"MCP tool execution failed: {tool_name} - {e.response.text}"
                    )
            except httpx.RequestError as e:
                last_error = e
                logger.error(f"MCP client request error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                else:
                    raise HTTPException(
                        status_code=503,
                        detail=f"MCP client connection error: {str(e)}"
                    )
        
        # Should not reach here, but handle just in case
        raise HTTPException(
            status_code=500,
            detail=f"MCP tool execution failed after {retries} attempts: {last_error}"
        )
    
    async def batch_execute(
        self,
        tools: list[tuple[str, Dict[str, Any]]],
        max_parallel: int = 5
    ) -> list[Dict[str, Any]]:
        """
        Execute multiple MCP tools in parallel (with concurrency limit).
        
        Args:
            tools: List of (tool_name, arguments) tuples
            max_parallel: Maximum parallel executions
            
        Returns:
            List of execution results (in order)
        """
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def execute_with_semaphore(tool_name: str, arguments: Dict[str, Any]):
            async with semaphore:
                return await self.execute_tool(tool_name, arguments)
        
        tasks = [
            execute_with_semaphore(tool_name, arguments)
            for tool_name, arguments in tools
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Tool execution failed: {tools[i][0]} - {result}")
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        logger.info("MCP Client closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

