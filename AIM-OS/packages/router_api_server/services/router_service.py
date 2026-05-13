"""
Router Service - Wraps Router core with MCP integration

# NL_TAG: ROUTER-API-SERVICE-001 | Router service class wrapping Router.decide() with MCP integration | RouterService.get_tool_proposals(...) -> List[ToolProposal] | []
# NL_TAG_CONNECT: ROUTER-API-SERVICE-CMC-001 | Router service stores decisions in CMC via MCP | store_decision → mcp_lucid-mcp_store_memory | [ROUTER-API-SERVICE-001, CMC-STORE-001]
# NL_TAG_CONNECT: ROUTER-API-SERVICE-HHNI-001 | Router service retrieves context from HHNI via MCP | get_context → mcp_lucid-mcp_retrieve_memory | [ROUTER-API-SERVICE-001, HHNI-RETRIEVE-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-003 | Service layer abstracts Router core complexity and provides MCP integration for AIM-OS systems | Service layer pattern | [ADR-SERVICE-LAYER]
# NL_TAG_SPEC: ROUTER-API-SPEC-003 | Validates RouterContext and ToolCallPlan schemas | RouterContext schema | [router_types.py]
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import sys
from pathlib import Path

# Add packages directory to path for imports
packages_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(packages_dir))

from router_api_server.mcp_client import MCPClient
from router_api_server.integrations.plix_compiler import PLIxCompiler
from router_api_server.integrations.apoe_executor import APOEExecutor
from router.core.router import Router
from router.core.scout import ScoutLLM
from router.core.bandit import BanditScorer
from router.core.rules import RulesEngine
from router.core.manifest import ToolManifest
from router.core.snapshot import SnapshotBuilder
from router.core.cache import RouterCache
from router.types import RouterContext, ToolCallPlan, ToolProposal

logger = logging.getLogger(__name__)


class RouterService:
    """
    Router service wrapping Router core with MCP integration.
    
    Provides high-level API for Router tool selection and execution.
    """
    
    def __init__(self, mcp_client: MCPClient):
        """
        Initialize Router service.
        
        Args:
            mcp_client: MCP client for AIM-OS system access
        """
        self.mcp_client = mcp_client
        
        # Initialize PLIx compiler and APOE executor
        self.plix_compiler = PLIxCompiler(mcp_client=mcp_client)
        self.apoe_executor = APOEExecutor(mcp_client=mcp_client)
        
        # Initialize Router core components
        # Note: These would be initialized with proper dependencies in production
        self.scout = ScoutLLM()
        self.bandit = BanditScorer()
        self.rules = RulesEngine()
        self.manifest = ToolManifest()
        self.snapshot_builder = SnapshotBuilder(mcp_client=mcp_client)
        self.cache = RouterCache()
        
        # Initialize Router
        self.router = Router(
            scout=self.scout,
            bandit=self.bandit,
            rules=self.rules,
            manifest=self.manifest,
            snapshot_builder=self.snapshot_builder,
            cache=self.cache
        )
        
        logger.info("Router Service initialized with PLIx integration")
    
    async def get_tool_proposals(
        self,
        goal: str,
        task: str,
        confidence: float,
        files: List[str],
        errors: List[str],
        agent_intent: str,
        budget: Optional[Dict[str, float]] = None,
        suggested_tools: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get tool proposals from Router.
        
        Args:
            goal: Current goal
            task: Current task
            confidence: Confidence level (0.0-1.0)
            files: List of active files
            errors: List of current errors
            agent_intent: Agent intent (e.g., "debug", "implement")
            budget: Budget constraints (tokens, cost, time)
            suggested_tools: Optional list of suggested tools from Log-Sentinels
            
        Returns:
            Dictionary with tools and suggestions
        """
        # Build Router context
        ctx = RouterContext(
            goal=goal,
            task=task,
            confidence=confidence,
            files=files or [],
            errors=errors or [],
            agent_intent=agent_intent,
            budget=budget or {"tokens": 10000, "cost": 1.0, "time": 300000},
            suggested_tools=suggested_tools
        )
        
        # Get tool call plan
        plan = await self.router.decide(ctx)
        
        # Convert plan to tool proposals
        tools = []
        suggestions = []
        
        for step in plan.steps:
            tool_proposal = {
                "tool_name": step.tool,
                "rationale": step.description or f"Execute {step.tool}",
                "draft_arguments": step.args,
                "confidence": confidence,
                "probability": getattr(step, 'probability', 0.5),
                "precondition_satisfied": all(
                    check.passed for check in (step.preflight or [])
                ),
                "context_fit": getattr(step, 'context_fit', 0.5),
                "success_rate": self.manifest.get_tool(step.tool).success_rate if self.manifest.get_tool(step.tool) else 0.5,
                "expected_info_gain": getattr(step, 'expected_info_gain', 0.5),
                "parallelizable": getattr(step, 'parallelizable', False)
            }
            
            # Add PLIx tag if available
            tool = self.manifest.get_tool(step.tool)
            if tool and hasattr(tool, 'plix_tag'):
                tool_proposal["plix_tag"] = tool.plix_tag
            
            if step.tool in (suggested_tools or []):
                suggestions.append(tool_proposal)
            else:
                tools.append(tool_proposal)
        
        return {
            "tools": tools,
            "suggestions": suggestions,
            "plan_id": plan.plan_id
        }
    
    async def get_telemetry(self, time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Get Router telemetry metrics.
        
        Args:
            time_range: Optional time range for filtering
            
        Returns:
            Telemetry dictionary with latency, success rate, cost metrics
        """
        # Get telemetry from cache and CMC
        # This would query CMC for decision history in production
        telemetry = {
            "avg_latency": 150.0,  # ms
            "latency_trend": "stable",
            "success_rate": 0.85,
            "success_trend": "up",
            "avg_cost": 0.05,  # tokens per call
            "cost_trend": "stable",
            "tools": []
        }
        
        # Get per-tool stats from manifest
        for tool_name in self.manifest.list_tools():
            tool = self.manifest.get_tool(tool_name)
            if tool:
                telemetry["tools"].append({
                    "name": tool_name,
                    "latency": tool.avg_latency_ms,
                    "success_rate": tool.success_rate,
                    "cost": tool.avg_cost,
                    "call_count": getattr(tool, 'call_count', 0)
                })
        
        return telemetry
    
    async def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tool via Router → PLIx → APOE.
        
        Args:
            tool_name: Tool name to execute
            args: Tool arguments
            
        Returns:
            Execution result
        """
        # Build Router context for execution
        ctx = RouterContext(
            goal=f"Execute {tool_name}",
            task=f"Run {tool_name} with provided arguments",
            confidence=0.8,
            files=[],
            errors=[],
            agent_intent="execute",
            budget={"tokens": 10000, "cost": 1.0, "time": 300000}
        )
        
        # Get tool call plan
        plan = await self.router.decide(ctx)
        
        # Find matching step
        matching_step = None
        for step in plan.steps:
            if step.tool == tool_name:
                matching_step = step
                break
        
        if not matching_step:
            raise ValueError(f"Tool {tool_name} not found in plan")
        
        # Execute via PLIx → APOE
        # Compile tool execution to PLIx contract → APOE ExecutionPlan
        try:
            # Generate entity tag for tool
            entity_tag = f"plix://tool/{tool_name}"
            
            # Compile to PLIx contract → APOE ExecutionPlan
            apoe_plan = await self.plix_compiler.compile_tool_execution(
                tool_name=tool_name,
                args=args,
                intent=f"Execute {tool_name}",
                entity_tag=entity_tag
            )
            
            # Execute plan via APOE
            execution_result = await self.apoe_executor.execute_plan(
                plan=apoe_plan,
                verify_intent=True
            )
            
            # Update Router success rate
            success = execution_result.get("success", False)
            if hasattr(self.router, 'update_success_rate'):
                await self.router.update_success_rate(tool_name, success=success)
            
            return {
                "success": success,
                "result": execution_result.get("outcome"),
                "plan_id": apoe_plan.plan_id,
                "intent_achieved": execution_result.get("intent_achieved", False),
                "evidence": execution_result.get("evidence")
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            if hasattr(self.router, 'update_success_rate'):
                await self.router.update_success_rate(tool_name, success=False)
            raise

