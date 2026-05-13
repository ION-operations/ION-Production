"""TCS Integration for APOE

Creates timeline entries for APOE plan and step execution events.
Uses MCP tool mcp_lucid-mcp_add_timeline_entry for timeline entry creation.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import asyncio

from .models import Step, StepStatus, Budget, RoleType, Gate
from .acl_parser import ExecutionPlan
from .executor import ExecutionResult

logger = logging.getLogger(__name__)

# TCS MCP tool availability (optional)
TCS_AVAILABLE = True  # Assume available, will check at runtime


class APOETCSIntegration:
    """
    Integrates APOE with TCS for timeline entry creation.
    
    Creates timeline entries for:
    - Plan execution events (start, completion)
    - Step execution events (start, completion)
    - Gate evaluation events
    - Budget milestone events
    - DEPP modification events
    - Error events
    """
    
    def __init__(self, mcp_client: Optional[Any] = None):
        """
        Initialize TCS integration.
        
        Args:
            mcp_client: Optional MCP client for timeline operations.
                        If None, timeline entries will be skipped (non-blocking).
        """
        self.mcp_client = mcp_client
        self.enabled = mcp_client is not None
        
        if not self.enabled:
            logger.warning("TCS integration disabled: No MCP client provided")
    
    def create_plan_start_entry(
        self,
        plan: ExecutionPlan,
        execution_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for plan execution start.
        
        Args:
            plan: Execution plan
            execution_id: Unique execution identifier
            
        Returns:
            Timeline entry creation result (entry_id, atom_id, etc.) or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_plan_start",
                "title": f"Plan {plan.name} Execution Started",
                "description": f"Plan execution started: {plan.name}",
                "context_data": {
                    "plan_name": plan.name,
                    "plan_id": plan.name,  # Use plan name as ID (or plan.id if available)
                    "execution_id": execution_id,
                    "total_steps": len(plan.steps),
                    "roles": list(plan.roles.keys()) if plan.roles else [],
                    "budget": None  # Plan-level budget not stored in ExecutionPlan model
                },
                "tags": ["apoe", "plan_execution", "start"],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan.name,
                    "execution_id": execution_id
                }
            }
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create plan start timeline entry: {e}")
            return None
    
    def create_plan_complete_entry(
        self,
        plan: ExecutionPlan,
        execution_id: str,
        result: ExecutionResult
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for plan execution completion.
        
        Args:
            plan: Executed plan
            execution_id: Unique execution identifier
            result: Execution result
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_plan_complete",
                "title": f"Plan {plan.name} Execution Completed",
                "description": f"Plan execution completed: {plan.name}",
                "context_data": {
                    "plan_name": plan.name,
                    "plan_id": plan.name,
                    "execution_id": execution_id,
                    "success": result.success,
                    "completed_steps": result.completed_steps,
                    "failed_steps": result.failed_steps,
                    "skipped_steps": result.skipped_steps,
                    "total_steps": result.total_steps,
                    "total_duration_seconds": result.total_duration_seconds,
                    "completion_rate": result.completion_rate(),
                    "effectiveness_score": getattr(result, 'effectiveness_score', None)
                },
                "tags": ["apoe", "plan_execution", "complete", "success" if result.success else "failure"],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan.name,
                    "execution_id": execution_id
                }
            }
            
            # Add VIF witness ID if available
            if hasattr(plan, 'metadata') and plan.metadata:
                vif_witness_id = plan.metadata.get("vif_witness_id")
                if vif_witness_id:
                    entry_data["metadata"]["vif_witness_id"] = vif_witness_id
            
            # Add SEG evidence ID if available
            if hasattr(plan, 'metadata') and plan.metadata:
                seg_trace = plan.metadata.get("seg_trace")
                if seg_trace and isinstance(seg_trace, dict):
                    plan_evidence_id = seg_trace.get("plan_evidence_id")
                    if plan_evidence_id:
                        entry_data["metadata"]["seg_evidence_id"] = plan_evidence_id
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create plan complete timeline entry: {e}")
            return None
    
    def create_step_start_entry(
        self,
        step: Step,
        plan_name: str,
        execution_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for step execution start.
        
        Args:
            step: Step being executed
            plan_name: Name of parent plan
            execution_id: Unique execution identifier
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_step_start",
                "title": f"Step {step.name} Started",
                "description": f"Step {step.id} execution started: {step.description or step.name}",
                "context_data": {
                    "step_id": step.id,
                    "step_name": step.name,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "role": step.role.value if step.role else None,
                    "role_name": step.role_name,
                    "description": step.description,
                    "budget": {
                        "tokens": step.budget.tokens_limit if step.budget else None,
                        "time_seconds": step.budget.time_limit_seconds if step.budget else None
                    } if step.budget else None
                },
                "tags": ["apoe", "step_execution", "start", step.role.value if step.role else "unknown"],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": step.id
                }
            }
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create step start timeline entry: {e}")
            return None
    
    def create_step_complete_entry(
        self,
        step: Step,
        plan_name: str,
        execution_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for step execution completion.
        
        Args:
            step: Executed step
            plan_name: Name of parent plan
            execution_id: Unique execution identifier
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Determine status and confidence
            status = step.status.value if hasattr(step.status, 'value') else str(step.status)
            confidence = None
            if step.outputs:
                confidence = step.outputs.get("confidence")
            
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_step_complete",
                "title": f"Step {step.name} Completed",
                "description": f"Step {step.id} execution completed: {step.description or step.name}",
                "context_data": {
                    "step_id": step.id,
                    "step_name": step.name,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "role": step.role.value if step.role else None,
                    "role_name": step.role_name,
                    "status": status,
                    "confidence": confidence,
                    "duration_seconds": step.duration() if step.duration() else None,
                    "outputs": step.outputs,
                    "error": step.error
                },
                "tags": ["apoe", "step_execution", "complete", status, step.role.value if step.role else "unknown"],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": step.id
                }
            }
            
            # Add VIF witness ID if available
            if hasattr(step, 'metadata') and step.metadata:
                vif_witness_id = step.metadata.get("vif_witness_id")
                if vif_witness_id:
                    entry_data["metadata"]["vif_witness_id"] = vif_witness_id
            
            # Add SEG evidence ID if available
            if hasattr(step, 'metadata') and step.metadata:
                # SEG evidence IDs would be stored in step metadata if available
                seg_evidence_id = step.metadata.get("seg_evidence_id")
                if seg_evidence_id:
                    entry_data["metadata"]["seg_evidence_id"] = seg_evidence_id
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create step complete timeline entry: {e}")
            return None
    
    def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Call MCP tool for timeline entry creation (synchronous wrapper).
        
        Args:
            tool_name: MCP tool name (e.g., "mcp_lucid-mcp_add_timeline_entry")
            arguments: Tool arguments
            
        Returns:
            Tool result (entry_id, atom_id, timestamp, etc.) or None on error
        """
        if not self.mcp_client:
            return None
        
        try:
            # Try async call first (if client is async)
            if hasattr(self.mcp_client, 'call_tool'):
                # Check if it's async
                import inspect
                if inspect.iscoroutinefunction(self.mcp_client.call_tool):
                    # Run async call in event loop
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is already running, create task
                            # For now, skip (would need proper async integration)
                            logger.warning("Event loop already running, skipping async MCP call")
                            return None
                        else:
                            result = loop.run_until_complete(
                                self.mcp_client.call_tool(tool_name, arguments)
                            )
                            return result
                    except RuntimeError:
                        # No event loop, create one
                        result = asyncio.run(self.mcp_client.call_tool(tool_name, arguments))
                        return result
                else:
                    # Synchronous call
                    result = self.mcp_client.call_tool(tool_name, arguments)
                    return result
            elif hasattr(self.mcp_client, 'execute_tool'):
                # Try execute_tool
                import inspect
                if inspect.iscoroutinefunction(self.mcp_client.execute_tool):
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            logger.warning("Event loop already running, skipping async MCP call")
                            return None
                        else:
                            result = loop.run_until_complete(
                                self.mcp_client.execute_tool(tool_name, arguments)
                            )
                            return result
                    except RuntimeError:
                        result = asyncio.run(self.mcp_client.execute_tool(tool_name, arguments))
                        return result
                else:
                    result = self.mcp_client.execute_tool(tool_name, arguments)
                    return result
            elif hasattr(self.mcp_client, 'call_tool_sync'):
                # Synchronous interface
                result = self.mcp_client.call_tool_sync(tool_name, arguments)
                return result
            else:
                logger.warning(f"MCP client does not support tool calls: {self.mcp_client}")
                return None
        except Exception as e:
            logger.warning(f"Failed to call MCP tool {tool_name}: {e}")
            return None
    
    def create_gate_evaluation_entry(
        self,
        gate: Gate,
        step: Step,
        plan_name: str,
        execution_id: str,
        passed: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for gate evaluation.
        
        Args:
            gate: Gate that was evaluated
            step: Step the gate belongs to
            plan_name: Name of parent plan
            execution_id: Unique execution identifier
            passed: Whether gate passed or failed
            context: Optional evaluation context
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_gate_evaluation",
                "title": f"Gate {gate.name} {'Passed' if passed else 'Failed'}",
                "description": f"Gate {gate.id} ({gate.name}) evaluation: {'passed' if passed else 'failed'}",
                "context_data": {
                    "gate_id": gate.id,
                    "gate_name": gate.name,
                    "gate_type": gate.gate_type if hasattr(gate, 'gate_type') else "quality",
                    "condition": gate.condition,
                    "result": "passed" if passed else "failed",
                    "step_id": step.id,
                    "step_name": step.name,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "on_fail": gate.on_fail if hasattr(gate, 'on_fail') else "abort",
                    "evaluation_context": context or {}
                },
                "tags": ["apoe", "gate_evaluation", "passed" if passed else "failed", gate.gate_type if hasattr(gate, 'gate_type') else "quality"],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": step.id,
                    "gate_id": gate.id
                }
            }
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create gate evaluation timeline entry: {e}")
            return None
    
    def create_budget_milestone_entry(
        self,
        plan_name: str,
        execution_id: str,
        milestone_type: str,
        budget_data: Dict[str, Any],
        step_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for budget milestone.
        
        Args:
            plan_name: Name of parent plan
            execution_id: Unique execution identifier
            milestone_type: Type of milestone (e.g., "50%_consumed", "budget_exceeded", "budget_adjusted")
            budget_data: Budget information (tokens, time, consumed, remaining)
            step_id: Optional step ID if milestone is step-specific
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_budget_milestone",
                "title": f"Budget Milestone: {milestone_type}",
                "description": f"Budget milestone reached: {milestone_type}",
                "context_data": {
                    "milestone_type": milestone_type,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "budget": budget_data,
                    "step_id": step_id
                },
                "tags": ["apoe", "budget_milestone", milestone_type],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": step_id
                }
            }
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create budget milestone timeline entry: {e}")
            return None
    
    def create_depp_modification_entry(
        self,
        modification: Any,  # PlanModification from depp
        plan_name: str,
        execution_id: str,
        reason: str,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for DEPP modification.
        
        Args:
            modification: PlanModification object
            plan_name: Name of parent plan
            execution_id: Unique execution identifier
            reason: Reason for modification
            confidence: Confidence in modification
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Extract modification details
            modification_type = getattr(modification, 'modification_type', 'unknown')
            target_step_id = getattr(modification, 'target_step_id', None)
            modification_id = getattr(modification, 'modification_id', None)
            
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_depp_modification",
                "title": f"DEPP Modification: {modification_type}",
                "description": f"DEPP modified plan: {modification_type} - {reason}",
                "context_data": {
                    "modification_id": modification_id,
                    "modification_type": modification_type,
                    "target_step_id": target_step_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "reason": reason,
                    "confidence": confidence,
                    "new_data": getattr(modification, 'new_data', {})
                },
                "tags": ["apoe", "depp", "modification", modification_type],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": target_step_id,
                    "modification_id": modification_id
                }
            }
            
            # Add SEG evidence ID if available (DEPP modifications may reference SEG evidence)
            if hasattr(modification, 'metadata') and modification.metadata:
                seg_evidence_id = modification.metadata.get("seg_evidence_id")
                if seg_evidence_id:
                    entry_data["metadata"]["seg_evidence_id"] = seg_evidence_id
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create DEPP modification timeline entry: {e}")
            return None
    
    def create_error_entry(
        self,
        error_type: str,
        error_message: str,
        plan_name: str,
        execution_id: str,
        step_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create timeline entry for error event.
        
        Args:
            error_type: Type of error (e.g., "execution_error", "gate_failure", "budget_exceeded")
            error_message: Error message
            plan_name: Name of parent plan
            execution_id: Unique execution identifier
            step_id: Optional step ID if error is step-specific
            context: Optional error context
            
        Returns:
            Timeline entry creation result or None if disabled
        """
        if not self.enabled or not self.mcp_client:
            return None
        
        try:
            # Prepare timeline entry data
            entry_data = {
                "event_type": "apoe_error",
                "title": f"Error: {error_type}",
                "description": f"APOE error occurred: {error_message}",
                "context_data": {
                    "error_type": error_type,
                    "error_message": error_message,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": step_id,
                    "error_context": context or {}
                },
                "tags": ["apoe", "error", error_type],
                "metadata": {
                    "correlation_id": execution_id,
                    "plan_id": plan_name,
                    "execution_id": execution_id,
                    "step_id": step_id
                }
            }
            
            # Create timeline entry via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_add_timeline_entry", entry_data)
            return result
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create error timeline entry: {e}")
            return None
    
    # ============================================================================
    # PHASE 3: TIMELINE QUERY METHODS
    # ============================================================================
    
    def query_execution_history(
        self,
        execution_id: str,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query timeline entries for a specific execution.
        
        Args:
            execution_id: Execution identifier
            event_types: Optional list of event types to filter by
            
        Returns:
            List of timeline entries for this execution
        """
        if not self.enabled or not self.mcp_client:
            return []
        
        try:
            # Prepare query parameters
            query_params = {
                "metadata_filter": {
                    "execution_id": execution_id
                },
                "sort_by": "timestamp",
                "order": "asc"
            }
            
            # Add event type filter if provided
            if event_types:
                query_params["event_types"] = event_types
            
            # Query timeline entries via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_get_timeline_entries", query_params)
            
            if result and "entries" in result:
                return result["entries"]
            return []
            
        except Exception as e:
            logger.warning(f"Failed to query execution history: {e}")
            return []
    
    def query_plan_history(
        self,
        plan_id: str,
        event_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query timeline entries for a specific plan (all executions).
        
        Args:
            plan_id: Plan identifier
            event_types: Optional list of event types to filter by
            limit: Maximum number of results
            
        Returns:
            List of timeline entries for this plan
        """
        if not self.enabled or not self.mcp_client:
            return []
        
        try:
            # Prepare query parameters
            query_params = {
                "metadata_filter": {
                    "plan_id": plan_id
                },
                "sort_by": "timestamp",
                "order": "desc",
                "limit": limit
            }
            
            # Add event type filter if provided
            if event_types:
                query_params["event_types"] = event_types
            
            # Query timeline entries via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_get_timeline_entries", query_params)
            
            if result and "entries" in result:
                return result["entries"]
            return []
            
        except Exception as e:
            logger.warning(f"Failed to query plan history: {e}")
            return []
    
    def query_time_range(
        self,
        start_time: str,
        end_time: str,
        event_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query timeline entries within a time range.
        
        Args:
            start_time: Start time (ISO 8601 format)
            end_time: End time (ISO 8601 format)
            event_types: Optional list of event types to filter by
            tags: Optional list of tags to filter by
            limit: Maximum number of results
            
        Returns:
            List of timeline entries within time range
        """
        if not self.enabled or not self.mcp_client:
            return []
        
        try:
            # Prepare query parameters
            query_params = {
                "start_time": start_time,
                "end_time": end_time,
                "sort_by": "timestamp",
                "order": "asc",
                "limit": limit
            }
            
            # Add event type filter if provided
            if event_types:
                query_params["event_types"] = event_types
            
            # Add tag filter if provided
            if tags:
                query_params["tags"] = tags
            
            # Query timeline entries via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_get_timeline_entries", query_params)
            
            if result and "entries" in result:
                return result["entries"]
            return []
            
        except Exception as e:
            logger.warning(f"Failed to query time range: {e}")
            return []
    
    def query_by_event_type(
        self,
        event_type: str,
        plan_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query timeline entries by event type.
        
        Args:
            event_type: Event type to filter by
            plan_id: Optional plan identifier
            execution_id: Optional execution identifier
            limit: Maximum number of results
            
        Returns:
            List of timeline entries matching event type
        """
        if not self.enabled or not self.mcp_client:
            return []
        
        try:
            # Prepare query parameters
            query_params = {
                "event_types": [event_type],
                "sort_by": "timestamp",
                "order": "desc",
                "limit": limit
            }
            
            # Add metadata filters if provided
            metadata_filter = {}
            if plan_id:
                metadata_filter["plan_id"] = plan_id
            if execution_id:
                metadata_filter["execution_id"] = execution_id
            
            if metadata_filter:
                query_params["metadata_filter"] = metadata_filter
            
            # Query timeline entries via MCP tool
            result = self._call_mcp_tool("mcp_lucid-mcp_get_timeline_entries", query_params)
            
            if result and "entries" in result:
                return result["entries"]
            return []
            
        except Exception as e:
            logger.warning(f"Failed to query by event type: {e}")
            return []
    
    def restore_execution_state(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Restore execution state from timeline entries.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Dictionary with restored execution state
        """
        if not self.enabled or not self.mcp_client:
            return {}
        
        try:
            # Query all timeline entries for this execution
            entries = self.query_execution_history(execution_id)
            
            if not entries:
                return {}
            
            # Reconstruct execution state from timeline entries
            execution_state = {
                "execution_id": execution_id,
                "plan_id": None,
                "plan_name": None,
                "start_time": None,
                "end_time": None,
                "status": "unknown",
                "steps": {},
                "total_steps": 0,
                "completed_steps": 0,
                "failed_steps": 0,
                "skipped_steps": 0,
                "abstained_steps": 0,
                "total_duration_seconds": 0.0,
                "success": False
            }
            
            # Process entries in chronological order
            for entry in entries:
                event_type = entry.get("event_type")
                context_data = entry.get("context_data", {})
                timestamp = entry.get("timestamp")
                
                if event_type == "apoe_plan_start":
                    execution_state["plan_id"] = context_data.get("plan_id")
                    execution_state["plan_name"] = context_data.get("plan_name")
                    execution_state["total_steps"] = context_data.get("total_steps", 0)
                    execution_state["start_time"] = timestamp
                    execution_state["status"] = "running"
                
                elif event_type == "apoe_step_start":
                    step_id = context_data.get("step_id")
                    if step_id:
                        execution_state["steps"][step_id] = {
                            "step_id": step_id,
                            "step_name": context_data.get("step_name"),
                            "role": context_data.get("role"),
                            "start_time": timestamp,
                            "status": "running"
                        }
                
                elif event_type == "apoe_step_complete":
                    step_id = context_data.get("step_id")
                    if step_id and step_id in execution_state["steps"]:
                        step_state = execution_state["steps"][step_id]
                        step_state["status"] = context_data.get("status", "completed")
                        step_state["confidence"] = context_data.get("confidence")
                        step_state["duration_seconds"] = context_data.get("duration_seconds")
                        step_state["end_time"] = timestamp
                        step_state["outputs"] = context_data.get("outputs")
                        step_state["error"] = context_data.get("error")
                        
                        # Update step counts
                        status = step_state["status"]
                        if status == "completed":
                            execution_state["completed_steps"] += 1
                        elif status == "failed":
                            execution_state["failed_steps"] += 1
                        elif status == "skipped":
                            execution_state["skipped_steps"] += 1
                        elif status == "abstained":
                            execution_state["abstained_steps"] += 1
                
                elif event_type == "apoe_plan_complete":
                    execution_state["end_time"] = timestamp
                    execution_state["status"] = "completed" if context_data.get("success") else "failed"
                    execution_state["success"] = context_data.get("success", False)
                    execution_state["completed_steps"] = context_data.get("completed_steps", 0)
                    execution_state["failed_steps"] = context_data.get("failed_steps", 0)
                    execution_state["total_duration_seconds"] = context_data.get("total_duration_seconds", 0.0)
            
            return execution_state
            
        except Exception as e:
            logger.warning(f"Failed to restore execution state: {e}")
            return {}
    
    def analyze_execution_performance(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Analyze execution performance from timeline entries.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Dictionary with performance metrics
        """
        if not self.enabled or not self.mcp_client:
            return {}
        
        try:
            # Query all timeline entries for this execution
            entries = self.query_execution_history(execution_id)
            
            if not entries:
                return {}
            
            # Analyze performance
            step_durations = []
            gate_evaluations = []
            budget_milestones = []
            errors = []
            
            for entry in entries:
                event_type = entry.get("event_type")
                context_data = entry.get("context_data", {})
                
                if event_type == "apoe_step_complete":
                    duration = context_data.get("duration_seconds")
                    if duration:
                        step_durations.append({
                            "step_id": context_data.get("step_id"),
                            "step_name": context_data.get("step_name"),
                            "role": context_data.get("role"),
                            "duration_seconds": duration,
                            "status": context_data.get("status")
                        })
                
                elif event_type == "apoe_gate_evaluation":
                    gate_evaluations.append({
                        "gate_id": context_data.get("gate_id"),
                        "gate_name": context_data.get("gate_name"),
                        "result": context_data.get("result"),
                        "step_id": context_data.get("step_id")
                    })
                
                elif event_type == "apoe_budget_milestone":
                    budget_milestones.append({
                        "milestone_type": context_data.get("milestone_type"),
                        "budget": context_data.get("budget", {}),
                        "step_id": context_data.get("step_id")
                    })
                
                elif event_type == "apoe_error":
                    errors.append({
                        "error_type": context_data.get("error_type"),
                        "error_message": context_data.get("error_message"),
                        "step_id": context_data.get("step_id")
                    })
            
            # Calculate metrics
            total_duration = sum(s["duration_seconds"] for s in step_durations)
            avg_step_duration = total_duration / len(step_durations) if step_durations else 0.0
            gate_pass_rate = sum(1 for g in gate_evaluations if g["result"] == "passed") / len(gate_evaluations) if gate_evaluations else 1.0
            error_rate = len(errors) / len(entries) if entries else 0.0
            
            return {
                "execution_id": execution_id,
                "total_entries": len(entries),
                "step_count": len(step_durations),
                "total_duration_seconds": total_duration,
                "average_step_duration_seconds": avg_step_duration,
                "gate_evaluations": len(gate_evaluations),
                "gate_pass_rate": gate_pass_rate,
                "budget_milestones": len(budget_milestones),
                "errors": len(errors),
                "error_rate": error_rate,
                "step_durations": step_durations,
                "gate_evaluations_details": gate_evaluations,
                "budget_milestones_details": budget_milestones,
                "errors_details": errors
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze execution performance: {e}")
            return {}

