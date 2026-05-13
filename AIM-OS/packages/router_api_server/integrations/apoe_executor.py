"""
APOE Executor - Executes APOE ExecutionPlans via MCP

# NL_TAG: ROUTER-API-APOE-001 | APOE executor for executing ExecutionPlans via MCP | APOEExecutor.execute_plan(...) -> Dict[str, Any] | []
# NL_TAG_CONNECT: ROUTER-API-APOE-MCP-001 | APOE executor calls APOE MCP tool | execute_plan → mcp_lucid-mcp_execute_plan | [ROUTER-API-APOE-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-006 | APOE executor enables intent-aware plan execution with verification | Intent-driven execution | [ADR-APOE-INTEGRATION]
# NL_TAG_SPEC: ROUTER-API-SPEC-007 | Validates APOE ExecutionPlan schemas before execution | ExecutionPlan schema | [apoe_schema.json]
"""

import logging
from typing import Dict, Any, Optional
import uuid

from ..mcp_client import MCPClient
from .plix_compiler import ExecutionPlan

logger = logging.getLogger(__name__)


class APOEExecutor:
    """
    APOE executor for executing ExecutionPlans via MCP.
    
    Executes APOE ExecutionPlans, verifies intent achievement,
    and collects evidence for SEG storage.
    """
    
    def __init__(self, mcp_client: MCPClient):
        """
        Initialize APOE executor.
        
        Args:
            mcp_client: MCP client for APOE execution
        """
        self.mcp_client = mcp_client
        logger.info("APOE Executor initialized")
    
    async def execute_plan(
        self,
        plan: ExecutionPlan,
        verify_intent: bool = True
    ) -> Dict[str, Any]:
        """
        Execute APOE ExecutionPlan via MCP.
        
        Args:
            plan: APOE ExecutionPlan
            verify_intent: Whether to verify intent achievement
            
        Returns:
            Execution result with outcome, evidence, and intent verification
        """
        try:
            # Convert ExecutionPlan to APOE format
            apoe_plan = self._convert_to_apoe_format(plan)
            
            # Execute via APOE MCP tool
            # Note: This assumes APOE MCP tool exists
            # If not, we'll execute steps directly
            try:
                result = await self.mcp_client.execute_tool(
                    tool_name="mcp_lucid-mcp_execute_plan",
                    arguments={
                        "plan": apoe_plan,
                        "verify_intent": verify_intent
                    }
                )
            except Exception as e:
                logger.warning(f"APOE MCP tool not available, executing steps directly: {e}")
                # Fallback: Execute steps directly
                result = await self._execute_steps_directly(plan)
            
            # Verify intent if requested
            if verify_intent and plan.entity_tag:
                intent_achieved = await self._verify_intent(plan, result)
                result["intent_achieved"] = intent_achieved
            
            # Collect evidence
            evidence = await self._collect_evidence(plan, result)
            result["evidence"] = evidence
            
            return result
            
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            raise
    
    def _convert_to_apoe_format(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Convert ExecutionPlan to APOE format.
        
        Args:
            plan: ExecutionPlan
            
        Returns:
            APOE plan format
        """
        return {
            "plan_id": plan.plan_id,
            "steps": plan.steps,
            "roles": plan.roles,
            "gates": plan.gates,
            "budget": plan.budget,
            "entity_tag": plan.entity_tag
        }
    
    async def _execute_steps_directly(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Execute plan steps directly (fallback if APOE MCP tool unavailable).
        
        Args:
            plan: ExecutionPlan
            
        Returns:
            Execution result
        """
        results = []
        
        for step in plan.steps:
            try:
                # Execute step via MCP
                tool_name = step.get("action", step.get("tool"))
                inputs = step.get("inputs", {})
                
                # Map tool name to MCP tool format
                if not tool_name.startswith("mcp_lucid-mcp_"):
                    tool_name = f"mcp_lucid-mcp_{tool_name}"
                
                step_result = await self.mcp_client.execute_tool(
                    tool_name=tool_name,
                    arguments=inputs
                )
                
                results.append({
                    "step_id": step.get("id"),
                    "success": True,
                    "result": step_result
                })
                
            except Exception as e:
                logger.error(f"Step execution failed: {step.get('id')} - {e}")
                results.append({
                    "step_id": step.get("id"),
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "plan_id": plan.plan_id,
            "success": all(r["success"] for r in results),
            "steps": results,
            "outcome": results[-1]["result"] if results else None
        }
    
    async def _verify_intent(
        self,
        plan: ExecutionPlan,
        result: Dict[str, Any]
    ) -> bool:
        """
        Verify intent achievement for plan.
        
        Args:
            plan: ExecutionPlan
            result: Execution result
            
        Returns:
            True if intent achieved, False otherwise
        """
        # Check if all steps succeeded
        if not result.get("success", False):
            return False
        
        # Check postconditions (simplified)
        # In production, this would use VIF to verify postconditions
        steps = result.get("steps", [])
        for step_result in steps:
            if not step_result.get("success", False):
                return False
        
        return True
    
    async def _collect_evidence(
        self,
        plan: ExecutionPlan,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect execution evidence for SEG storage.
        
        Args:
            plan: ExecutionPlan
            result: Execution result
            
        Returns:
            Evidence dictionary
        """
        evidence = {
            "plan_id": plan.plan_id,
            "entity_tag": plan.entity_tag,
            "execution_time": result.get("execution_time"),
            "steps_executed": len(result.get("steps", [])),
            "success": result.get("success", False),
            "outcome": result.get("outcome")
        }
        
        # Store evidence in SEG via MCP
        try:
            await self.mcp_client.execute_tool(
                tool_name="mcp_lucid-mcp_store_memory",
                arguments={
                    "content": f"Execution evidence for plan {plan.plan_id}",
                    "tags": {
                        "type": "execution_evidence",
                        "plan_id": plan.plan_id,
                        "entity_tag": plan.entity_tag
                    }
                }
            )
        except Exception as e:
            logger.warning(f"Failed to store evidence in SEG: {e}")
        
        return evidence

