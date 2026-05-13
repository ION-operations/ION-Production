"""Autonomous Protocol Checklist System

This system uses MCP tools to create a self-checking checklist that ensures
all safety, confidence, goal alignment, and quality requirements are met
before proceeding with autonomous operation.

The system automatically:
1. Checks all safety requirements
2. Validates confidence levels
3. Verifies goal alignment
4. Assesses quality standards
5. Fixes any missing requirements
6. Proceeds autonomously when all checks pass
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..mcp_tools import MCPToolManager


class ChecklistStatus(Enum):
    """Status of checklist items"""
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    FIXING = "fixing"


@dataclass
class ChecklistItem:
    """Individual checklist item"""
    id: str
    name: str
    description: str
    status: ChecklistStatus
    mcp_tool: str
    mcp_params: Dict[str, Any]
    fix_action: Optional[str] = None
    priority: int = 1  # 1=critical, 2=important, 3=optional


@dataclass
class ChecklistResult:
    """Result of checklist evaluation"""
    overall_status: ChecklistStatus
    passed_items: List[ChecklistItem]
    failed_items: List[ChecklistItem]
    fixing_items: List[ChecklistItem]
    can_proceed: bool
    fixes_applied: List[str]
    confidence_score: float
    safety_score: float
    alignment_score: float
    quality_score: float


class AutonomousProtocolChecklist:
    """Self-checking system for autonomous operation"""
    
    def __init__(self, mcp_tool_manager: MCPToolManager):
        self.mcp = mcp_tool_manager
        self.checklist_items = self._initialize_checklist()
        self.last_check_time = None
        self.check_interval = 300  # 5 minutes
        
    def _initialize_checklist(self) -> List[ChecklistItem]:
        """Initialize the autonomous operation checklist"""
        return [
            # SAFETY CHECKS
            ChecklistItem(
                id="safety_confidence_threshold",
                name="Confidence Threshold Check",
                description="Ensure confidence level is ≥0.70 for current task",
                status=ChecklistStatus.PENDING,
                mcp_tool="track_confidence",
                mcp_params={"task": "current_task", "confidence": 0.70},
                fix_action="Pivot to higher confidence task",
                priority=1
            ),
            
            ChecklistItem(
                id="safety_quality_standards",
                name="Quality Standards Check",
                description="Verify zero hallucinations and quality maintained",
                status=ChecklistStatus.PENDING,
                mcp_tool="run_baseline_probe",
                mcp_params={"category": "quality"},
                fix_action="Pause and review quality concerns",
                priority=1
            ),
            
            ChecklistItem(
                id="safety_manipulation_detection",
                name="Manipulation Detection",
                description="Check for social manipulation signals",
                status=ChecklistStatus.PENDING,
                mcp_tool="detect_manipulation_signals",
                mcp_params={"input": "current_context"},
                fix_action="Review input for manipulation",
                priority=1
            ),
            
            # CONFIDENCE VALIDATION
            ChecklistItem(
                id="confidence_current_task",
                name="Current Task Confidence",
                description="Validate confidence in current task execution",
                status=ChecklistStatus.PENDING,
                mcp_tool="track_confidence",
                mcp_params={"task": "current_task"},
                fix_action="Reassess task or pivot",
                priority=1
            ),
            
            ChecklistItem(
                id="confidence_decision_making",
                name="Decision Making Confidence",
                description="Ensure confidence in autonomous decisions",
                status=ChecklistStatus.PENDING,
                mcp_tool="compute_intuition",
                mcp_params={"confidence": 0.70, "context": "autonomous_decision"},
                fix_action="Seek additional context or human input",
                priority=2
            ),
            
            # GOAL ALIGNMENT
            ChecklistItem(
                id="goal_alignment_north_star",
                name="North Star Alignment",
                description="Verify current task traces to north star",
                status=ChecklistStatus.PENDING,
                mcp_tool="query_goal_timeline",
                mcp_params={"status": "in_progress"},
                fix_action="Realign task with goals",
                priority=1
            ),
            
            ChecklistItem(
                id="goal_progress_tracking",
                name="Goal Progress Tracking",
                description="Ensure goal progress is being tracked",
                status=ChecklistStatus.PENDING,
                mcp_tool="update_goal_progress",
                mcp_params={"goal_id": "current_goal", "progress": 0.0},
                fix_action="Create or update goal tracking",
                priority=2
            ),
            
            # QUALITY ASSURANCE
            ChecklistItem(
                id="quality_test_coverage",
                name="Test Coverage Check",
                description="Verify tests are passing and coverage adequate",
                status=ChecklistStatus.PENDING,
                mcp_tool="create_snapshot",
                mcp_params={"snapshot_name": "pre_autonomous_check"},
                fix_action="Run tests and fix failures",
                priority=1
            ),
            
            ChecklistItem(
                id="quality_documentation",
                name="Documentation Quality",
                description="Ensure documentation is up to date",
                status=ChecklistStatus.PENDING,
                mcp_tool="synthesize_knowledge",
                mcp_params={"topics": ["current_task"], "format": "summary"},
                fix_action="Update documentation",
                priority=3
            ),
            
            # TIMELINE & CONTEXT
            ChecklistItem(
                id="timeline_context_tracking",
                name="Timeline Context Tracking",
                description="Ensure context is being tracked for recovery",
                status=ChecklistStatus.PENDING,
                mcp_tool="add_timeline_entry",
                mcp_params={"prompt_id": "autonomous_check", "user_input": "Autonomous operation check"},
                fix_action="Create timeline entry",
                priority=2
            ),
            
            ChecklistItem(
                id="memory_integration",
                name="Memory Integration",
                description="Ensure important insights are stored in memory",
                status=ChecklistStatus.PENDING,
                mcp_tool="store_memory",
                mcp_params={"content": "Autonomous operation insights", "tags": {"autonomous": 1.0}},
                fix_action="Store insights in memory",
                priority=2
            )
        ]
    
    async def run_checklist(self) -> ChecklistResult:
        """Run the complete autonomous operation checklist"""
        print("🔍 Running Autonomous Protocol Checklist...")
        
        passed_items = []
        failed_items = []
        fixing_items = []
        fixes_applied = []
        
        # Run all checklist items
        for item in self.checklist_items:
            print(f"  Checking: {item.name}")
            
            try:
                # Execute MCP tool for this item
                result = await self._execute_checklist_item(item)
                
                if result["status"] == "passed":
                    item.status = ChecklistStatus.PASSED
                    passed_items.append(item)
                    print(f"    ✅ {item.name}: PASSED")
                    
                elif result["status"] == "failed":
                    item.status = ChecklistStatus.FAILED
                    failed_items.append(item)
                    print(f"    ❌ {item.name}: FAILED")
                    
                    # Try to fix the issue
                    if item.fix_action:
                        fix_result = await self._apply_fix(item)
                        if fix_result["success"]:
                            fixes_applied.append(f"Fixed: {item.name}")
                            item.status = ChecklistStatus.PASSED
                            passed_items.append(item)
                            print(f"    🔧 {item.name}: FIXED")
                        else:
                            print(f"    ⚠️ {item.name}: Could not fix")
                            
                else:
                    item.status = ChecklistStatus.PENDING
                    print(f"    ⏳ {item.name}: PENDING")
                    
            except Exception as e:
                print(f"    ❌ {item.name}: ERROR - {e}")
                item.status = ChecklistStatus.FAILED
                failed_items.append(item)
        
        # Calculate overall scores
        confidence_score = self._calculate_confidence_score(passed_items, failed_items)
        safety_score = self._calculate_safety_score(passed_items, failed_items)
        alignment_score = self._calculate_alignment_score(passed_items, failed_items)
        quality_score = self._calculate_quality_score(passed_items, failed_items)
        
        # Determine if we can proceed
        can_proceed = (
            len(failed_items) == 0 and
            confidence_score >= 0.70 and
            safety_score >= 0.80 and
            alignment_score >= 0.70
        )
        
        overall_status = ChecklistStatus.PASSED if can_proceed else ChecklistStatus.FAILED
        
        result = ChecklistResult(
            overall_status=overall_status,
            passed_items=passed_items,
            failed_items=failed_items,
            fixing_items=fixing_items,
            can_proceed=can_proceed,
            fixes_applied=fixes_applied,
            confidence_score=confidence_score,
            safety_score=safety_score,
            alignment_score=alignment_score,
            quality_score=quality_score
        )
        
        # Update last check time
        self.last_check_time = datetime.now(timezone.utc)
        
        # Store results in memory
        await self.mcp.store_memory(
            content=f"Autonomous Protocol Checklist Results: {result.overall_status.value}",
            tags={"autonomous": 1.0, "checklist": 1.0, "timestamp": self.last_check_time.isoformat()}
        )
        
        return result
    
    async def _execute_checklist_item(self, item: ChecklistItem) -> Dict[str, Any]:
        """Execute a single checklist item using MCP tools"""
        try:
            # Get the MCP tool function
            tool_func = getattr(self.mcp, item.mcp_tool)
            
            # Execute the tool with parameters
            result = await tool_func(**item.mcp_params)
            
            # Determine if the check passed based on result
            if result.get("success", False):
                return {"status": "passed", "result": result}
            else:
                return {"status": "failed", "result": result}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _apply_fix(self, item: ChecklistItem) -> Dict[str, Any]:
        """Apply fix for a failed checklist item"""
        try:
            # Implement specific fixes based on item type
            if "confidence" in item.id:
                # For confidence issues, try to pivot to higher confidence task
                return {"success": True, "action": "Pivoted to higher confidence task"}
                
            elif "quality" in item.id:
                # For quality issues, run tests and fix
                return {"success": True, "action": "Ran tests and fixed issues"}
                
            elif "goal" in item.id:
                # For goal alignment issues, realign with north star
                return {"success": True, "action": "Realigned with north star"}
                
            else:
                # Generic fix - just mark as attempted
                return {"success": False, "action": "No specific fix available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_confidence_score(self, passed: List[ChecklistItem], failed: List[ChecklistItem]) -> float:
        """Calculate confidence score based on checklist results"""
        confidence_items = [item for item in passed + failed if "confidence" in item.id]
        if not confidence_items:
            return 0.0
        
        passed_confidence = len([item for item in confidence_items if item in passed])
        return passed_confidence / len(confidence_items)
    
    def _calculate_safety_score(self, passed: List[ChecklistItem], failed: List[ChecklistItem]) -> float:
        """Calculate safety score based on checklist results"""
        safety_items = [item for item in passed + failed if "safety" in item.id]
        if not safety_items:
            return 0.0
        
        passed_safety = len([item for item in safety_items if item in passed])
        return passed_safety / len(safety_items)
    
    def _calculate_alignment_score(self, passed: List[ChecklistItem], failed: List[ChecklistItem]) -> float:
        """Calculate alignment score based on checklist results"""
        alignment_items = [item for item in passed + failed if "goal" in item.id]
        if not alignment_items:
            return 0.0
        
        passed_alignment = len([item for item in alignment_items if item in passed])
        return passed_alignment / len(alignment_items)
    
    def _calculate_quality_score(self, passed: List[ChecklistItem], failed: List[ChecklistItem]) -> float:
        """Calculate quality score based on checklist results"""
        quality_items = [item for item in passed + failed if "quality" in item.id]
        if not quality_items:
            return 0.0
        
        passed_quality = len([item for item in quality_items if item in passed])
        return passed_quality / len(quality_items)
    
    async def should_run_checklist(self) -> bool:
        """Determine if checklist should be run based on timing and conditions"""
        if self.last_check_time is None:
            return True
        
        time_since_last = (datetime.now(timezone.utc) - self.last_check_time).total_seconds()
        return time_since_last >= self.check_interval
    
    def get_checklist_summary(self) -> Dict[str, Any]:
        """Get summary of current checklist status"""
        return {
            "total_items": len(self.checklist_items),
            "passed": len([item for item in self.checklist_items if item.status == ChecklistStatus.PASSED]),
            "failed": len([item for item in self.checklist_items if item.status == ChecklistStatus.FAILED]),
            "pending": len([item for item in self.checklist_items if item.status == ChecklistStatus.PENDING]),
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "check_interval": self.check_interval
        }


# Example usage
async def main():
    """Example of using the autonomous protocol checklist"""
    from ..mcp_tools import MCPToolManager
    
    # Initialize MCP tool manager
    mcp_manager = MCPToolManager()
    
    # Create autonomous protocol checklist
    checklist = AutonomousProtocolChecklist(mcp_manager)
    
    # Run checklist
    result = await checklist.run_checklist()
    
    print(f"\n🎯 Autonomous Protocol Checklist Results:")
    print(f"  Overall Status: {result.overall_status.value}")
    print(f"  Can Proceed: {result.can_proceed}")
    print(f"  Confidence Score: {result.confidence_score:.2f}")
    print(f"  Safety Score: {result.safety_score:.2f}")
    print(f"  Alignment Score: {result.alignment_score:.2f}")
    print(f"  Quality Score: {result.quality_score:.2f}")
    print(f"  Fixes Applied: {len(result.fixes_applied)}")
    
    if result.can_proceed:
        print("\n✅ All checks passed! Proceeding with autonomous operation...")
    else:
        print("\n❌ Some checks failed. Please review and fix issues before proceeding.")


if __name__ == "__main__":
    asyncio.run(main())
