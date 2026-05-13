"""
RAG MCP Middleware - Integrates RAG proxy with MCP server

Intercepts tools/list requests and filters tools using RAG proxy based on
conversation context, achieving 80% context reduction.

Author: Solo
Date: 2025-10-30
"""

from __future__ import annotations

import logging
import inspect
from typing import Dict, List, Any, Optional, Deque
from collections import deque
from pathlib import Path
from datetime import datetime
import sys

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

try:
    from mcp_rag_proxy.rag_proxy import MCPRAGProxy
    from mcp_rag_proxy.embedding_generator import ToolEmbeddingInput
    RAG_AVAILABLE = True
except ImportError:
    try:
        from rag_proxy import MCPRAGProxy
        from embedding_generator import ToolEmbeddingInput
        RAG_AVAILABLE = True
    except ImportError:
        RAG_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGMCPMiddleware:
    """Middleware that filters MCP tools using RAG proxy"""
    
    def __init__(
        self,
        rag_proxy: Optional[MCPRAGProxy] = None,
        max_context_history: int = 10,
        enable_rag: bool = True
    ):
        """Initialize RAG middleware
        
        Args:
            rag_proxy: RAG proxy instance (creates new if None)
            max_context_history: Maximum conversation history to keep
            enable_rag: Enable RAG filtering (False = pass through all tools)
        """
        self.enable_rag = enable_rag and RAG_AVAILABLE
        
        if self.enable_rag:
            if rag_proxy is None:
                metadata_path = Path(__file__).parent / "tools_metadata.json"
                proxy_kwargs: Dict[str, Any] = {
                    "tools_metadata_path": str(metadata_path),
                    "max_tools": 10,  # Return top 10 tools (80% reduction from 54)
                    "similarity_threshold": 0.0,  # Let consciousness weighting filter
                    "consciousness_weight": 0.3,
                }

                # Backward/forward compatible ctor call across proxy versions.
                try:
                    ctor_params = inspect.signature(MCPRAGProxy.__init__).parameters
                    if "use_new_embeddings" in ctor_params:
                        proxy_kwargs["use_new_embeddings"] = True
                except Exception:
                    pass

                self.rag_proxy = MCPRAGProxy(**proxy_kwargs)
            else:
                self.rag_proxy = rag_proxy
            
            # Conversation context for tool selection
            self.context_history: Deque[str] = deque(maxlen=max_context_history)
            self.current_context: str = ""
            self.last_selection: Optional[Dict[str, Any]] = None
            
            logger.info(f"RAG MCP Middleware initialized (max_tools={self.rag_proxy.max_tools})")
        else:
            logger.warning("RAG MCP Middleware disabled (RAG not available or disabled)")
            self.rag_proxy = None
    
    def add_context(self, text: str):
        """Add text to conversation context
        
        Args:
            text: Text to add to context
        """
        if not self.enable_rag:
            return
        
        self.context_history.append(text)
        # Update current context (last 3 messages for better relevance)
        recent_context = " ".join(list(self.context_history)[-3:])
        self.current_context = recent_context
    
    def filter_tools(
        self,
        all_tools: List[Dict[str, Any]],
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter tools using RAG proxy
        
        Args:
            all_tools: List of all available tools
            query: Optional explicit query (uses context if None)
            
        Returns:
            Filtered list of tools
        """
        if not self.enable_rag or not self.rag_proxy:
            # Pass through all tools if RAG disabled
            return all_tools
        
        # Use explicit query or current context
        search_query = query or self.current_context or "general AI operations"
        
        # Select relevant tools using RAG proxy
        try:
            selections = self.rag_proxy.select_tools(
                query=search_query,
                consciousness_state="neutral",  # Could be enhanced with actual state
                max_tools=self.rag_proxy.max_tools
            )
            
            # Get tool IDs from selections
            selected_tool_ids = {s.tool_id for s in selections}
            
            # Filter tools list
            filtered_tools = [
                tool for tool in all_tools
                if tool.get("name") in selected_tool_ids
            ]
            
            logger.info(
                f"RAG filtered {len(all_tools)} tools → {len(filtered_tools)} tools "
                f"({(1 - len(filtered_tools) / len(all_tools)) * 100:.1f}% reduction)"
            )
            
            return filtered_tools
            
        except Exception as e:
            logger.error(f"RAG filtering failed: {e}, returning all tools")
            return all_tools
    
    def extract_query_from_request(self, request: Dict[str, Any]) -> Optional[str]:
        """Extract query from MCP request (if available)
        
        Args:
            request: MCP request dictionary
            
        Returns:
            Extracted query string or None
        """
        # MCP doesn't have a standard way to pass context to tools/list
        # But we can extract from params if a custom extension exists
        params = request.get("params", {})
        return params.get("query") or params.get("context")
    
    def handle_tools_list(
        self,
        request: Dict[str, Any],
        all_tools: List[Dict[str, Any]],
        request_id: Any
    ) -> Dict[str, Any]:
        """Handle tools/list request with RAG filtering
        
        Args:
            request: MCP request dictionary
            all_tools: List of all available tools
            request_id: Request ID
            
        Returns:
            MCP response with filtered tools
        """
        # Extract query if available
        query = self.extract_query_from_request(request)
        
        # Filter tools using RAG
        filtered_tools = self.filter_tools(all_tools, query=query)
        
        # Store selected tool IDs for learning
        selected_tool_ids = [tool.get("name") for tool in filtered_tools]
        search_query = query or self.current_context or "general AI operations"
        self.last_selection = {
            "query": search_query,
            "tools": selected_tool_ids,
            "timestamp": datetime.now()
        }
        
        # Return filtered tools list
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": filtered_tools
            }
        }
    
    def record_tool_usage(
        self,
        tool_name: str,
        success: bool = True,
        quality_score: float = 1.0,
        outcome: str = ""
    ):
        """Record tool usage for learning
        
        Args:
            tool_name: Name of tool that was used
            success: Whether usage was successful
            quality_score: Quality score (0.0-1.0)
            outcome: Outcome description
        """
        if not self.enable_rag or not self.rag_proxy or not self.last_selection:
            return
        
        try:
            self.rag_proxy.record_tool_usage(
                tool_id=tool_name,
                query=self.last_selection["query"],
                selected_tools=self.last_selection["tools"],
                consciousness_state="neutral",  # Could be enhanced
                tool_used=tool_name,
                success=success,
                quality_score=quality_score,
                outcome=outcome
            )
        except Exception as e:
            logger.error(f"Failed to record tool usage: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.enable_rag or not self.rag_proxy:
            return {
                "enabled": False,
                "rag_available": RAG_AVAILABLE
            }
        
        stats = {
            "enabled": True,
            "rag_available": True,
            "max_tools": self.rag_proxy.max_tools,
            "context_history_size": len(self.context_history),
            "current_context_length": len(self.current_context),
            "total_tools": self.rag_proxy.vector_index.size() if self.rag_proxy.use_new_embeddings else len(self.rag_proxy.tools_metadata)
        }
        
        # Add learning stats if available
        if self.rag_proxy.enable_learning and self.rag_proxy.learning_engine:
            try:
                learning_stats = self.rag_proxy.learning_engine.get_learning_stats()
                stats["learning"] = learning_stats
            except Exception as e:
                logger.warning(f"Failed to get learning stats: {e}")
        
        return stats

