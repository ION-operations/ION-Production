"""
Router core implementation - main Router class.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..types import (
    RouterContext,
    Snapshot,
    ToolCallPlan,
    ToolCallStep,
    ValidationResult,
)
from .scout import ScoutLLM
from .bandit import BanditScorer
from .rules import RulesEngine
from .manifest import ToolManifest
from .snapshot import SnapshotBuilder
from .cache import RouterCache


class Router:
    """
    Main Router class for intelligent tool selection.
    
    Responsibilities:
    - Observe current system state
    - Propose candidate tools via Scout LLM
    - Score tools via Bandit layer
    - Generate tool call plans
    - Execute plans via APOE
    - Learn from outcomes
    """
    
    def __init__(
        self,
        scout: ScoutLLM,
        bandit: BanditScorer,
        rules: RulesEngine,
        manifest: ToolManifest,
        snapshot_builder: SnapshotBuilder,
        cache: Optional[RouterCache] = None
    ):
        self.scout = scout
        self.bandit = bandit
        self.rules = rules
        self.manifest = manifest
        self.snapshot_builder = snapshot_builder
        self.cache = cache or RouterCache()
    
    async def decide(self, ctx: RouterContext) -> ToolCallPlan:
        """
        Main decision method - generates tool call plan.
        
        Control loop:
        1. Observe - Build snapshot
        2. Propose - Scout LLM suggests tools
        3. Score - Bandit layer ranks tools
        4. Plan - Generate ToolCallPlan
        5. Validate - Rules engine validates plan
        
        Args:
            ctx: Router context with goal, task, etc.
            
        Returns:
            ToolCallPlan ready for execution
        """
        # 1. Observe
        snapshot = await self.snapshot_builder.build(ctx)
        
        # Check cache for proposals
        cached_proposals = await self.cache.get_cached_proposals(snapshot)
        
        if cached_proposals:
            # Use cached proposals
            proposals = cached_proposals
        else:
            # 2. Propose
            proposals = await self.scout.propose(snapshot, self.manifest)
            # Cache proposals
            await self.cache.cache_proposals(snapshot, proposals)
        
        # 3. Score
        ranked = await self.bandit.score(proposals, snapshot)
        
        # 4. Plan
        plan = await self._compile_plan(ranked, snapshot, ctx)
        
        # 5. Validate
        validation = self.rules.validate(plan)
        if not validation.passed:
            # Return minimal plan or escalate
            plan = await self._handle_validation_failure(plan, validation)
        
        return plan
    
    async def _compile_plan(
        self,
        ranked: List,
        snapshot: Snapshot,
        ctx: RouterContext
    ) -> ToolCallPlan:
        """Compile ranked tools into execution plan."""
        plan_id = str(uuid.uuid4())
        steps = []
        
        # Select top-k tools under budget
        top_tools = ranked[:10]  # Top 10 tools
        
        for i, ranked_tool in enumerate(top_tools):
            tool = self.manifest.get_tool(ranked_tool.proposal.tool_name)
            if not tool:
                continue
            
            step = ToolCallStep(
                id=f"{plan_id}_step_{i}",
                tool=ranked_tool.proposal.tool_name,
                args=ranked_tool.proposal.draft_arguments,
                parallel_group=None,  # Will be determined by rules
                preflight=None,  # Will be determined by rules
                timeout_ms=int(tool.avg_latency_ms * 2),  # 2x average latency
            )
            steps.append(step)
        
        return ToolCallPlan(
            plan_id=plan_id,
            goal=ctx.goal,
            steps=steps,
            context=ctx,
            max_depth=3,
            budget=ctx.budget
        )
    
    async def _handle_validation_failure(
        self,
        plan: ToolCallPlan,
        validation: ValidationResult
    ) -> ToolCallPlan:
        """Handle validation failure - return safe plan or escalate."""
        # For now, return plan with warnings
        # In production, would escalate or return minimal plan
        return plan
    
    async def update_success_rate(
        self,
        tool_name: str,
        success: bool
    ):
        """Update tool success rate after execution."""
        await self.bandit.update_success_rate(tool_name, success)
    
    async def learn_from_outcome(
        self,
        plan: ToolCallPlan,
        result: Dict[str, Any]
    ):
        """Learn from execution outcome."""
        for step in plan.steps:
            success = result.get(step.id, {}).get("success", False)
            await self.update_success_rate(step.tool, success)
            
            # Update Bandit weights based on outcome
            await self.bandit.learn_from_outcome(step, result.get(step.id, {}))

