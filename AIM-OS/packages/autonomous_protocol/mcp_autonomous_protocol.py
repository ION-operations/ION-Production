"""MCP Tool for Autonomous Protocol Checklist

This MCP tool provides autonomous operation control using the checklist system.
It allows the AI to:
1. Run autonomous protocol checklist
2. Start/stop/pause autonomous operation
3. Get status of autonomous operation
4. Fix issues automatically
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .autonomous_checklist import AutonomousProtocolChecklist, ChecklistResult, ChecklistStatus


@dataclass
class AutonomousOperationState:
    """Current state of autonomous operation"""
    is_active: bool
    is_paused: bool
    current_task: Optional[str]
    confidence_level: float
    safety_score: float
    alignment_score: float
    quality_score: float
    last_check_time: Optional[datetime]
    issues_count: int
    fixes_applied: List[str]


class MCPAutonomousProtocol:
    """MCP tool for autonomous operation control"""
    
    def __init__(self, mcp_tool_manager):
        self.mcp = mcp_tool_manager
        self.checklist = AutonomousProtocolChecklist(mcp_tool_manager)
        self.state = AutonomousOperationState(
            is_active=False,
            is_paused=False,
            current_task=None,
            confidence_level=0.0,
            safety_score=0.0,
            alignment_score=0.0,
            quality_score=0.0,
            last_check_time=None,
            issues_count=0,
            fixes_applied=[]
        )
    
    async def start_autonomous_operation(self, task: str, confidence: float = 0.70) -> Dict[str, Any]:
        """Start autonomous operation with given task and confidence level"""
        print(f"🚀 Starting autonomous operation for task: {task}")
        
        # Set current task and confidence
        self.state.current_task = task
        self.state.confidence_level = confidence
        
        # Run initial checklist
        result = await self.checklist.run_checklist()
        
        if result.can_proceed:
            self.state.is_active = True
            self.state.is_paused = False
            self.state.issues_count = len(result.failed_items)
            self.state.fixes_applied = result.fixes_applied
            
            # Store in memory
            await self.mcp.store_memory(
                content=f"Started autonomous operation: {task}",
                tags={"autonomous": 1.0, "operation": "start", "task": task}
            )
            
            return {
                "success": True,
                "message": "Autonomous operation started successfully",
                "task": task,
                "confidence": confidence,
                "checklist_result": {
                    "overall_status": result.overall_status.value,
                    "confidence_score": result.confidence_score,
                    "safety_score": result.safety_score,
                    "alignment_score": result.alignment_score,
                    "quality_score": result.quality_score
                }
            }
        else:
            return {
                "success": False,
                "message": "Cannot start autonomous operation - checklist failed",
                "failed_checks": [item.name for item in result.failed_items],
                "suggestions": [item.fix_action for item in result.failed_items if item.fix_action]
            }
    
    async def pause_autonomous_operation(self) -> Dict[str, Any]:
        """Pause autonomous operation"""
        if not self.state.is_active:
            return {
                "success": False,
                "message": "No active autonomous operation to pause"
            }
        
        self.state.is_paused = True
        
        # Store in memory
        await self.mcp.store_memory(
            content=f"Paused autonomous operation: {self.state.current_task}",
            tags={"autonomous": 1.0, "operation": "pause", "task": self.state.current_task}
        )
        
        return {
            "success": True,
            "message": "Autonomous operation paused",
            "task": self.state.current_task
        }
    
    async def resume_autonomous_operation(self) -> Dict[str, Any]:
        """Resume autonomous operation after pause"""
        if not self.state.is_active:
            return {
                "success": False,
                "message": "No active autonomous operation to resume"
            }
        
        if not self.state.is_paused:
            return {
                "success": False,
                "message": "Autonomous operation is not paused"
            }
        
        # Run checklist before resuming
        result = await self.checklist.run_checklist()
        
        if result.can_proceed:
            self.state.is_paused = False
            
            # Store in memory
            await self.mcp.store_memory(
                content=f"Resumed autonomous operation: {self.state.current_task}",
                tags={"autonomous": 1.0, "operation": "resume", "task": self.state.current_task}
            )
            
            return {
                "success": True,
                "message": "Autonomous operation resumed",
                "task": self.state.current_task,
                "checklist_result": {
                    "overall_status": result.overall_status.value,
                    "confidence_score": result.confidence_score,
                    "safety_score": result.safety_score,
                    "alignment_score": result.alignment_score,
                    "quality_score": result.quality_score
                }
            }
        else:
            return {
                "success": False,
                "message": "Cannot resume autonomous operation - checklist failed",
                "failed_checks": [item.name for item in result.failed_items]
            }
    
    async def stop_autonomous_operation(self) -> Dict[str, Any]:
        """Stop autonomous operation completely"""
        if not self.state.is_active:
            return {
                "success": False,
                "message": "No active autonomous operation to stop"
            }
        
        task = self.state.current_task
        self.state.is_active = False
        self.state.is_paused = False
        self.state.current_task = None
        
        # Store in memory
        await self.mcp.store_memory(
            content=f"Stopped autonomous operation: {task}",
            tags={"autonomous": 1.0, "operation": "stop", "task": task}
        )
        
        return {
            "success": True,
            "message": "Autonomous operation stopped",
            "task": task
        }
    
    async def get_autonomous_status(self) -> Dict[str, Any]:
        """Get current status of autonomous operation"""
        return {
            "is_active": self.state.is_active,
            "is_paused": self.state.is_paused,
            "current_task": self.state.current_task,
            "confidence_level": self.state.confidence_level,
            "safety_score": self.state.safety_score,
            "alignment_score": self.state.alignment_score,
            "quality_score": self.state.quality_score,
            "last_check_time": self.state.last_check_time.isoformat() if self.state.last_check_time else None,
            "issues_count": self.state.issues_count,
            "fixes_applied": self.state.fixes_applied
        }
    
    async def run_autonomous_checklist(self) -> Dict[str, Any]:
        """Run the autonomous protocol checklist"""
        result = await self.checklist.run_checklist()
        
        # Update state with results
        self.state.confidence_level = result.confidence_score
        self.state.safety_score = result.safety_score
        self.state.alignment_score = result.alignment_score
        self.state.quality_score = result.quality_score
        self.state.issues_count = len(result.failed_items)
        self.state.fixes_applied = result.fixes_applied
        self.state.last_check_time = datetime.now(timezone.utc)
        
        return {
            "success": True,
            "overall_status": result.overall_status.value,
            "can_proceed": result.can_proceed,
            "confidence_score": result.confidence_score,
            "safety_score": result.safety_score,
            "alignment_score": result.alignment_score,
            "quality_score": result.quality_score,
            "passed_items": len(result.passed_items),
            "failed_items": len(result.failed_items),
            "fixes_applied": result.fixes_applied,
            "failed_checks": [item.name for item in result.failed_items],
            "suggestions": [item.fix_action for item in result.failed_items if item.fix_action]
        }
    
    async def fix_autonomous_issues(self) -> Dict[str, Any]:
        """Attempt to fix issues found in autonomous operation"""
        result = await self.checklist.run_checklist()
        
        fixes_applied = []
        for item in result.failed_items:
            if item.fix_action:
                # Apply fix
                fix_result = await self.checklist._apply_fix(item)
                if fix_result["success"]:
                    fixes_applied.append(f"Fixed: {item.name}")
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "remaining_issues": len(result.failed_items) - len(fixes_applied)
        }
    
    async def should_continue_autonomous(self) -> Dict[str, Any]:
        """Check if autonomous operation should continue"""
        if not self.state.is_active or self.state.is_paused:
            return {
                "should_continue": False,
                "reason": "Not active or paused"
            }
        
        # Run checklist
        result = await self.checklist.run_checklist()
        
        if result.can_proceed:
            return {
                "should_continue": True,
                "reason": "All checks passed",
                "confidence_score": result.confidence_score,
                "safety_score": result.safety_score
            }
        else:
            return {
                "should_continue": False,
                "reason": "Checklist failed",
                "failed_checks": [item.name for item in result.failed_items],
                "suggestions": [item.fix_action for item in result.failed_items if item.fix_action]
            }
    
    async def generate_next_autonomous_task(self) -> Dict[str, Any]:
        """Generate next task for autonomous operation"""
        # Query goal timeline for next tasks
        goals = await self.mcp.query_goal_timeline(status="planned", limit=5)
        
        if goals["success"] and goals["count"] > 0:
            next_goal = goals["goals"][0]
            return {
                "success": True,
                "next_task": next_goal["name"],
                "goal_id": next_goal["goal_id"],
                "priority": next_goal["priority"],
                "confidence": 0.75  # Default confidence for goal-based tasks
            }
        else:
            # Fallback to general task generation
            return {
                "success": True,
                "next_task": "Continue current work and identify next priorities",
                "goal_id": None,
                "priority": "medium",
                "confidence": 0.70
            }


# MCP Tool Functions (to be integrated with MCP server)
async def mcp_start_autonomous_operation(task: str, confidence: float = 0.70) -> Dict[str, Any]:
    """MCP tool: Start autonomous operation"""
    # This would be called from the MCP server
    # Implementation would initialize MCPAutonomousProtocol and call start_autonomous_operation
    pass

async def mcp_pause_autonomous_operation() -> Dict[str, Any]:
    """MCP tool: Pause autonomous operation"""
    pass

async def mcp_resume_autonomous_operation() -> Dict[str, Any]:
    """MCP tool: Resume autonomous operation"""
    pass

async def mcp_stop_autonomous_operation() -> Dict[str, Any]:
    """MCP tool: Stop autonomous operation"""
    pass

async def mcp_get_autonomous_status() -> Dict[str, Any]:
    """MCP tool: Get autonomous operation status"""
    pass

async def mcp_run_autonomous_checklist() -> Dict[str, Any]:
    """MCP tool: Run autonomous protocol checklist"""
    pass

async def mcp_fix_autonomous_issues() -> Dict[str, Any]:
    """MCP tool: Fix autonomous operation issues"""
    pass

async def mcp_should_continue_autonomous() -> Dict[str, Any]:
    """MCP tool: Check if should continue autonomous operation"""
    pass

async def mcp_generate_next_autonomous_task() -> Dict[str, Any]:
    """MCP tool: Generate next autonomous task"""
    pass
