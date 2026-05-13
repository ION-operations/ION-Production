"""
Tool manifest system - capability contract for all tools.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SideEffect(str, Enum):
    """Side effect types."""
    FS = "fs"
    NETWORK = "network"
    AI = "ai"
    INDEX = "index"
    NONE = "none"


@dataclass
class Tool:
    """Tool definition with capability contract."""
    name: str
    version: str
    capability: List[str]  # Tags: "index:refresh", "test:run", "lint:fix"
    inputs: Dict[str, Any]  # Schema (would use Zod/JSON Schema in production)
    outputs: Dict[str, Any]  # Schema
    preconditions: List[str]  # Declarative checks
    side_effects: List[SideEffect]
    avg_latency_ms: float
    avg_cost: float  # Tokens/$ or compute units
    risk: str  # "low", "med", "high"
    success_rate: float  # Rolling success rate (0-1)
    examples: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


class ToolManifest:
    """
    Tool manifest registry.
    
    Maintains registry of all available tools with their
    capabilities, requirements, and metadata.
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Register a tool in the manifest."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        return list(self.tools.values())
    
    def find_tools_by_capability(self, capability: str) -> List[Tool]:
        """Find tools by capability tag."""
        return [
            tool for tool in self.tools.values()
            if capability in tool.capability
        ]
    
    def find_tools_by_tag(self, tag: str) -> List[Tool]:
        """Find tools by tag (partial match on capability)."""
        return [
            tool for tool in self.tools.values()
            if any(tag in cap for cap in tool.capability)
        ]
    
    def get_tool_count(self) -> int:
        """Get total number of registered tools."""
        return len(self.tools)
    
    def initialize_aimos_tools(self):
        """Initialize with AIM-OS MCP tools."""
        # Core AIM-OS Tools
        self.register(Tool(
            name="store_memory",
            version="1.0.0",
            capability=["memory:store", "cmc:write"],
            inputs={"content": "string", "tags": "object"},
            outputs={"atom_id": "string", "success": "boolean"},
            preconditions=["cmc_available"],
            side_effects=[SideEffect.INDEX],
            avg_latency_ms=50.0,
            avg_cost=0.001,
            risk="low",
            success_rate=0.95
        ))
        
        self.register(Tool(
            name="retrieve_memory",
            version="1.0.0",
            capability=["memory:retrieve", "hhni:query"],
            inputs={"query": "string", "limit": "number"},
            outputs={"results": "array"},
            preconditions=["hhni_available"],
            side_effects=[SideEffect.NONE],
            avg_latency_ms=100.0,
            avg_cost=0.002,
            risk="low",
            success_rate=0.90
        ))
        
        self.register(Tool(
            name="track_confidence",
            version="1.0.0",
            capability=["vif:track", "quality:gate"],
            inputs={"task": "string", "confidence": "number"},
            outputs={"success": "boolean"},
            preconditions=["vif_available"],
            side_effects=[SideEffect.INDEX],
            avg_latency_ms=30.0,
            avg_cost=0.0005,
            risk="low",
            success_rate=0.98
        ))
        
        # Add more AIM-OS tools as needed
        # This is a sample - would register all 59+ MCP tools

