"""
Log-Sentinels-Router integration.

Feeds tool suggestions from Log-Sentinels to Router.
"""

from typing import List, Dict, Any
from ...core.types import ScoutReport, ForensicsReport


class RouterIntegration:
    """
    Integration between Log-Sentinels and Router.
    
    Feeds tool suggestions from log analysis to Router.
    Router uses suggestions to inform tool selection.
    """
    
    def __init__(self, router_client=None):
        self.router = router_client
    
    async def suggest_tools(
        self,
        report: ScoutReport
    ):
        """
        Feed tool suggestions to Router.
        
        Args:
            report: Scout report with suggested tools
        """
        if not self.router or not report.suggested_tools:
            return
        
        # In production, would feed suggestions to Router:
        # await self.router.receive_suggestions(
        #     tools=report.suggested_tools,
        #     context={
        #         "source": "log_analysis",
        #         "window_id": report.window_id,
        #         "summary": report.summary,
        #         "severity": report.severity,
        #         "confidence": report.confidence
        #     }
        # )
        pass
    
    async def suggest_tools_from_forensics(
        self,
        report: ForensicsReport
    ):
        """
        Feed tool suggestions from Forensics report to Router.
        
        Args:
            report: Forensics report with suggested tools
        """
        if not self.router or not report.suggested_tools:
            return
        
        # Similar to suggest_tools but with forensics context
        await self.suggest_tools(report)
    
    async def validate_execution(
        self,
        tool_name: str,
        execution_result: Dict[str, Any]
    ) -> bool:
        """
        Validate tool execution result.
        
        Log-Sentinels can analyze execution logs to validate success.
        
        Args:
            tool_name: Tool that was executed
            execution_result: Execution result
            
        Returns:
            Whether execution was successful
        """
        if not self.router:
            return True  # Default to success
        
        # In production, would:
        # 1. Analyze execution logs
        # 2. Determine if execution was successful
        # 3. Update Router success rates
        
        return True

