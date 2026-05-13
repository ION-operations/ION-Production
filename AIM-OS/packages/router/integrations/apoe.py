"""
Router-APOE integration.

Converts Router ToolCallPlan to APOE ExecutionPlan.
"""

from typing import Dict, Any, Optional
from ...core.types import ToolCallPlan, ToolCallStep
from ...core.manifest import ToolManifest


class APOEIntegration:
    """
    Integration between Router and APOE.
    
    Converts Router ToolCallPlan to APOE ExecutionPlan format.
    """
    
    def __init__(self, apoe_client=None):
        self.apoe = apoe_client
    
    async def generate_plan(
        self,
        tool_plan: ToolCallPlan,
        manifest: ToolManifest
    ) -> Dict[str, Any]:
        """
        Convert Router ToolCallPlan to APOE ExecutionPlan.
        
        Args:
            tool_plan: Router tool call plan
            manifest: Tool manifest
            
        Returns:
            APOE ExecutionPlan dictionary
        """
        # Convert steps to APOE format
        apoe_steps = []
        
        for step in tool_plan.steps:
            tool = manifest.get_tool(step.tool)
            if not tool:
                continue
            
            apoe_step = {
                "name": step.tool,
                "description": f"Execute {step.tool}",
                "role_name": self._determine_role(step.tool, tool),
                "inputs": step.args,
                "dependencies": self._get_dependencies(step, tool_plan.steps),
                "gates": self._convert_gates(step.preflight) if step.preflight else [],
                "timeout_ms": step.timeout_ms,
                "budget": self._estimate_budget(tool)
            }
            apoe_steps.append(apoe_step)
        
        return {
            "plan_id": tool_plan.plan_id,
            "goal": tool_plan.goal,
            "steps": apoe_steps,
            "max_depth": tool_plan.max_depth,
            "budget": tool_plan.budget
        }
    
    def _determine_role(self, tool_name: str, tool) -> str:
        """Determine APOE role for tool."""
        # Map tool capabilities to APOE roles
        if any("memory" in cap or "retrieve" in cap for cap in tool.capability):
            return "Retriever"
        elif any("build" in cap or "create" in cap for cap in tool.capability):
            return "Builder"
        elif any("verify" in cap or "validate" in cap for cap in tool.capability):
            return "Verifier"
        elif any("plan" in cap or "orchestrate" in cap for cap in tool.capability):
            return "Planner"
        else:
            return "Operator"  # Default role
    
    def _get_dependencies(
        self,
        step: ToolCallStep,
        all_steps: list
    ) -> list:
        """Get step dependencies based on parallel groups."""
        deps = []
        
        # If step has parallel_group, depend on previous steps in same group
        if step.parallel_group:
            for other_step in all_steps:
                if (other_step.parallel_group == step.parallel_group and
                    other_step.id != step.id):
                    # Check if other_step comes before this step
                    # (simplified - would need proper ordering in production)
                    pass
        
        return deps
    
    def _convert_gates(self, preflight: list) -> list:
        """Convert Router preflight checks to APOE gates."""
        gates = []
        
        for check in preflight:
            gate = {
                "name": check,
                "type": "vif",
                "condition": f"preflight.{check} == true"
            }
            gates.append(gate)
        
        return gates
    
    def _estimate_budget(self, tool) -> Dict[str, float]:
        """Estimate budget for tool execution."""
        return {
            "tokens": tool.avg_cost * 1000,  # Rough estimate
            "time_ms": tool.avg_latency_ms
        }
    
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute APOE plan.
        
        Args:
            plan: APOE ExecutionPlan
            
        Returns:
            Execution result
        """
        if not self.apoe:
            # Stub - would call APOE executor in production
            return {"status": "stub", "plan_id": plan["plan_id"]}
        
        # In production: return await self.apoe.execute(plan)
        return {"status": "stub"}

