"""
Unified Router-Log-Sentinels service.

Combines Router and Log-Sentinels into unified service with closed-loop learning.
"""

from typing import List, Dict, Any
import uuid

from ...router.core.router import Router
from ...router.core.types import RouterContext, ToolCallPlan
from ...log_sentinels.core.pipeline import LogSentinelsPipeline
from ...log_sentinels.core.types import LogRecord
from ...router.integrations.apoe import APOEIntegration
from ...router.integrations.seg import SEGIntegration
from ...router.integrations.cmc import CMCIntegration
from ...router.integrations.tcs import TCSIntegration
from ...log_sentinels.integrations.seg import SEGIntegration as LogSentinelsSEG
from ...log_sentinels.integrations.vif import VIFIntegration as LogSentinelsVIF
from ...log_sentinels.integrations.cmc import CMCIntegration as LogSentinelsCMC
from ...log_sentinels.integrations.tcs import TCSIntegration as LogSentinelsTCS
from ...log_sentinels.integrations.router import RouterIntegration


class UnifiedRouterSentinelsService:
    """
    Unified service combining Router and Log-Sentinels.
    
    Provides closed-loop learning:
    1. Log-Sentinels analyzes logs → suggests tools
    2. Router selects best tools → executes via APOE
    3. Log-Sentinels validates execution → updates success rates
    4. Complete evidence chain in SEG
    """
    
    def __init__(
        self,
        router: Router,
        log_sentinels: LogSentinelsPipeline,
        apoe_integration: APOEIntegration,
        router_seg: SEGIntegration,
        router_cmc: CMCIntegration,
        router_tcs: TCSIntegration,
        sentinels_seg: LogSentinelsSEG,
        sentinels_vif: LogSentinelsVIF,
        sentinels_cmc: LogSentinelsCMC,
        sentinels_tcs: LogSentinelsTCS,
        router_integration: RouterIntegration
    ):
        self.router = router
        self.log_sentinels = log_sentinels
        self.apoe = apoe_integration
        self.router_seg = router_seg
        self.router_cmc = router_cmc
        self.router_tcs = router_tcs
        self.sentinels_seg = sentinels_seg
        self.sentinels_vif = sentinels_vif
        self.sentinels_cmc = sentinels_cmc
        self.sentinels_tcs = sentinels_tcs
        self.router_integration = router_integration
    
    async def process_logs_and_route(
        self,
        logs: List[LogRecord],
        goal: str,
        task: str,
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """
        Process logs and route to tool execution.
        
        Complete flow:
        1. Log-Sentinels analyzes logs
        2. Router receives tool suggestions
        3. Router selects best tools
        4. APOE executes tools
        5. Log-Sentinels validates execution
        6. Update success rates
        7. Record unified evidence chain
        
        Args:
            logs: Log records to analyze
            goal: Goal for tool selection
            task: Task description
            confidence: Confidence level
            
        Returns:
            Execution result with complete evidence chain
        """
        # 1. Log-Sentinels analyzes logs
        # (In production, would use log_sentinels pipeline)
        scout_report = await self._analyze_logs(logs)
        
        # 2. Feed tool suggestions to Router
        if scout_report.suggested_tools:
            await self.router_integration.suggest_tools(scout_report)
        
        # 3. Router receives tool suggestions and selects best tools
        router_context = RouterContext(
            goal=goal,
            task=task,
            confidence=confidence,
            files=[],
            errors=[],
            agent_intent=task,
            budget={},
            suggested_tools=scout_report.suggested_tools,
            log_insights={
                "summary": scout_report.summary,
                "severity": scout_report.severity,
                "confidence": scout_report.confidence
            }
        )
        
        tool_plan = await self.router.decide(router_context)
        
        # 4. APOE executes tools
        apoe_plan = await self.apoe.generate_plan(tool_plan, self.router.manifest)
        execution_result = await self.apoe.execute(apoe_plan)
        
        # 5. Log-Sentinels validates execution
        validation = await self._validate_execution(execution_result)
        
        # 6. Update success rates
        for step in tool_plan.steps:
            success = validation.get(step.id, {}).get("success", False)
            await self.router.update_success_rate(step.tool, success)
        
        # 7. Record unified evidence chain
        evidence_chain = await self._record_unified_evidence(
            scout_report,
            tool_plan,
            execution_result,
            validation
        )
        
        return {
            "scout_report": scout_report,
            "tool_plan": tool_plan,
            "execution_result": execution_result,
            "validation": validation,
            "evidence_chain": evidence_chain
        }
    
    async def _analyze_logs(self, logs: List[LogRecord]) -> ScoutReport:
        """Analyze logs using Log-Sentinels (stub)."""
        # In production, would use log_sentinels pipeline
        from ...log_sentinels.core.types import ScoutReport, Severity
        
        return ScoutReport(
            window_id=str(uuid.uuid4()),
            summary="Log analysis placeholder",
            confidence=0.7,
            severity=Severity.MEDIUM,
            tags=[],
            suggested_tools=[]
        )
    
    async def _validate_execution(
        self,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Validate execution using Log-Sentinels (stub)."""
        # In production, would analyze execution logs
        return {
            step_id: {"success": True}
            for step_id in execution_result.get("step_ids", [])
        }
    
    async def _record_unified_evidence(
        self,
        scout_report,
        tool_plan: ToolCallPlan,
        execution_result: Dict[str, Any],
        validation: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Record complete evidence chain in SEG."""
        chain = []
        
        # Record Scout report
        scout_node_id = await self.sentinels_seg.record_scout_report(scout_report)
        chain.append(scout_node_id)
        
        # Record tool selection
        selection_node_id = await self.router_seg.record_decision(tool_plan)
        chain.append(selection_node_id)
        
        # Link Scout to selection
        # await self.sentinels_seg.link_tool_suggestions(
        #     scout_report,
        #     [selection_node_id]
        # )
        
        # Record tool executions
        for step in tool_plan.steps:
            if step.id in execution_result:
                exec_node_id = await self.router_seg.record_execution(
                    tool_plan,
                    step,
                    execution_result[step.id],
                    selection_node_id
                )
                chain.append(exec_node_id)
        
        # Store in CMC
        await self.router_cmc.store_decision(tool_plan)
        await self.sentinels_cmc.store_report(scout_report)
        
        # Record in TCS
        await self.router_tcs.record_selection(tool_plan)
        await self.sentinels_tcs.record_incident(scout_report)
        
        return chain

