"""
PLIx Compiler - Compiles tool execution to PLIx contracts → APOE ExecutionPlans

# NL_TAG: ROUTER-API-PLIX-001 | PLIx compiler for tool execution → PLIx contract → APOE ExecutionPlan | PLIxCompiler.compile_tool_execution(...) -> ExecutionPlan | []
# NL_TAG_CONNECT: ROUTER-API-PLIX-HHNI-001 | PLIx compiler resolves tags via HHNI | resolve_tag → mcp_lucid-mcp_retrieve_memory | [ROUTER-API-PLIX-001, HHNI-RETRIEVE-001]
# NL_TAG_CONNECT: ROUTER-API-PLIX-APOE-001 | PLIx compiler generates APOE ExecutionPlans | compile_to_apoe → APOE ExecutionPlan | [ROUTER-API-PLIX-001, APOE-PLAN-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-005 | PLIx integration enables intent-aware tool execution with tag-based entity references | Intent-driven execution | [ADR-PLIX-INTEGRATION]
# NL_TAG_SPEC: ROUTER-API-SPEC-006 | Validates PLIx contract schemas and APOE ExecutionPlan schemas | PLIx contract schema | [plix_schema.json]
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from ..mcp_client import MCPClient

logger = logging.getLogger(__name__)


@dataclass
class PLIxContract:
    """PLIx contract representation."""
    intent: str
    entity_tag: Optional[str] = None
    preconditions: Optional[List[str]] = None
    postconditions: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionPlan:
    """APOE ExecutionPlan representation."""
    plan_id: str
    steps: List[Dict[str, Any]]
    roles: Dict[str, str]
    gates: List[Dict[str, Any]]
    budget: Dict[str, float]
    entity_tag: Optional[str] = None


class PLIxCompiler:
    """
    PLIx compiler for tool execution → PLIx contract → APOE ExecutionPlan.
    
    Compiles tool execution requests into PLIx contracts, resolves entity tags,
    and generates APOE ExecutionPlans for intent-aware execution.
    """
    
    def __init__(self, mcp_client: MCPClient):
        """
        Initialize PLIx compiler.
        
        Args:
            mcp_client: MCP client for HHNI tag resolution and APOE execution
        """
        self.mcp_client = mcp_client
        logger.info("PLIx Compiler initialized")
    
    async def compile_tool_execution(
        self,
        tool_name: str,
        args: Dict[str, Any],
        intent: Optional[str] = None,
        entity_tag: Optional[str] = None
    ) -> ExecutionPlan:
        """
        Compile tool execution to PLIx contract → APOE ExecutionPlan.
        
        Args:
            tool_name: Tool name to execute
            args: Tool arguments
            intent: Optional intent description
            entity_tag: Optional PLIx entity tag
            
        Returns:
            APOE ExecutionPlan ready for execution
        """
        # Build PLIx contract
        contract = self._build_contract(tool_name, args, intent, entity_tag)
        
        # Resolve entity tag if provided
        resolved_entity = None
        if contract.entity_tag:
            resolved_entity = await self._resolve_tag(contract.entity_tag)
        
        # Compile to APOE ExecutionPlan
        plan = await self._compile_to_apoe(contract, resolved_entity, tool_name, args)
        
        return plan
    
    def _build_contract(
        self,
        tool_name: str,
        args: Dict[str, Any],
        intent: Optional[str],
        entity_tag: Optional[str]
    ) -> PLIxContract:
        """
        Build PLIx contract from tool execution request.
        
        Args:
            tool_name: Tool name
            args: Tool arguments
            intent: Optional intent
            entity_tag: Optional entity tag
            
        Returns:
            PLIx contract
        """
        # Generate intent if not provided
        if not intent:
            intent = f"Execute {tool_name} with provided arguments"
        
        # Generate entity tag if not provided (use tool name as entity)
        if not entity_tag:
            entity_tag = f"plix://tool/{tool_name}"
        
        # Build preconditions from tool arguments
        preconditions = []
        if args:
            preconditions.append(f"arguments_provided == true")
        
        # Build postconditions (tool execution success)
        postconditions = [
            f"{tool_name}_executed == true",
            "execution_success == true"
        ]
        
        # Build constraints (defaults)
        constraints = [
            "confidence >= 0.70",
            "cost <= 1.0",
            "time <= 300000"
        ]
        
        # Build metadata
        metadata = {
            "tool_name": tool_name,
            "args": args,
            "timestamp": datetime.now().isoformat()
        }
        
        return PLIxContract(
            intent=intent,
            entity_tag=entity_tag,
            preconditions=preconditions,
            postconditions=postconditions,
            constraints=constraints,
            metadata=metadata
        )
    
    async def _resolve_tag(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        Resolve PLIx tag via HHNI.
        
        Args:
            tag: PLIx tag (e.g., "plix://tool/mcp_lucid-mcp_store_memory")
            
        Returns:
            Resolved entity information or None
        """
        try:
            # Query HHNI for tag resolution
            result = await self.mcp_client.execute_tool(
                tool_name="mcp_lucid-mcp_retrieve_memory",
                arguments={
                    "query": tag,
                    "limit": 1
                }
            )
            
            if result and "memories" in result and len(result["memories"]) > 0:
                return result["memories"][0]
            
            return None
        except Exception as e:
            logger.warning(f"Tag resolution failed for {tag}: {e}")
            return None
    
    async def _compile_to_apoe(
        self,
        contract: PLIxContract,
        resolved_entity: Optional[Dict[str, Any]],
        tool_name: str,
        args: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Compile PLIx contract to APOE ExecutionPlan.
        
        Args:
            contract: PLIx contract
            resolved_entity: Resolved entity information
            tool_name: Tool name
            args: Tool arguments
            
        Returns:
            APOE ExecutionPlan
        """
        import uuid
        
        plan_id = str(uuid.uuid4())
        
        # Build execution step
        step = {
            "id": f"step_{plan_id}",
            "action": tool_name,
            "inputs": args,
            "role": self._map_role(tool_name),
            "preconditions": contract.preconditions or [],
            "postconditions": contract.postconditions or [],
            "entity_tag": contract.entity_tag,
            "resolved_entity": resolved_entity
        }
        
        # Build roles mapping
        roles = {
            step["role"]: step["role"]
        }
        
        # Build gates from constraints
        gates = []
        for constraint in contract.constraints or []:
            gates.append({
                "type": "constraint",
                "constraint": constraint,
                "check": f"validate_constraint('{constraint}')"
            })
        
        # Add confidence gate
        gates.append({
            "type": "confidence",
            "threshold": 0.70,
            "check": "validate_confidence()"
        })
        
        # Build budget from metadata
        budget = {
            "max_cost": contract.metadata.get("max_cost", 1.0),
            "max_time": contract.metadata.get("max_time", 300000),
            "max_tokens": contract.metadata.get("max_tokens", 10000)
        }
        
        return ExecutionPlan(
            plan_id=plan_id,
            steps=[step],
            roles=roles,
            gates=gates,
            budget=budget,
            entity_tag=contract.entity_tag
        )
    
    def _map_role(self, tool_name: str) -> str:
        """
        Map tool name to APOE role.
        
        Args:
            tool_name: Tool name
            
        Returns:
            APOE role name
        """
        # Extract namespace from tool name
        if "." in tool_name:
            namespace = tool_name.split(".")[0]
        elif "_" in tool_name:
            namespace = tool_name.split("_")[0]
        else:
            namespace = "default"
        
        # Map namespace to role
        role_mapping = {
            "mcp": "mcp_executor",
            "api": "api_executor",
            "db": "database_executor",
            "ai": "ai_agent",
            "router": "router_agent"
        }
        
        return role_mapping.get(namespace, "default_executor")

