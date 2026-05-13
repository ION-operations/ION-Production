"""
Prompt Chain Execution - MCP Tool Integration
Integrates chain executor with MCP server
"""

from typing import Dict, Any, Optional
from .executor import ChainExecutor, get_chain_executor


def execute_prompt_chain_via_mcp(
    chain_id: str,
    inputs: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    agent_name: str = "primary",
    memory_store = None,
    executor = None  # NEW: Optional executor instance with callback
) -> Dict[str, Any]:
    """
    Execute a prompt chain via MCP
    
    Args:
        chain_id: Chain ID (CMC atom ID)
        inputs: Input values for chain execution
        context: Execution context
        agent_name: Name of agent executing chain
        memory_store: Memory store instance
        
    Returns:
        Execution result
    """
    try:
        # Retrieve chain definition from CMC
        if not memory_store:
            return {
                "success": False,
                "error": "Memory system not initialized"
            }
        
        # Get chain atom
        try:
            atom = memory_store.get_atom(chain_id)
            if not atom:
                return {
                    "success": False,
                    "error": f"Chain not found: {chain_id}"
                }
            
            # Parse chain definition
            import json
            chain_definition = json.loads(atom.content.inline) if hasattr(atom.content, 'inline') else json.loads(atom.content)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve chain: {str(e)}"
            }
        
        # Get chain executor (use provided executor or create new one)
        if executor:
            executor_instance = executor
        else:
            executor_instance = get_chain_executor(memory=memory_store)
        
        # Execute chain
        result = executor_instance.execute_chain(
            chain_definition=chain_definition,
            inputs=inputs or {},
            context=context or {},
            agent_name=agent_name
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Chain execution failed: {str(e)}"
        }

