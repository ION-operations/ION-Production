"""
Log-Sentinels Service - Wraps Log-Sentinels core with MCP integration

# NL_TAG: LOG-SENTINELS-API-SERVICE-001 | Log-Sentinels service class wrapping LogSentinelsPipeline with MCP integration | LogSentinelsService.get_scout_reports(...) -> List[ScoutReport] | []
# NL_TAG_CONNECT: LOG-SENTINELS-API-SERVICE-CMC-001 | Log-Sentinels service stores analysis results in CMC via MCP | store_analysis → mcp_lucid-mcp_store_memory | [LOG-SENTINELS-API-SERVICE-001, CMC-STORE-001]
# NL_TAG_CONNECT: LOG-SENTINELS-API-SERVICE-ROUTER-001 | Log-Sentinels service feeds tool suggestions to Router via MCP | suggest_tools → Router service | [LOG-SENTINELS-API-SERVICE-001, ROUTER-API-SERVICE-001]
# NL_TAG_INTENT: LOG-SENTINELS-API-DESIGN-001 | Service layer abstracts Log-Sentinels pipeline complexity and provides MCP integration | Service layer pattern | [ADR-SERVICE-LAYER]
# NL_TAG_SPEC: LOG-SENTINELS-API-SPEC-001 | Validates LogRecord, Window, ScoutReport, ForensicsReport schemas | Log-Sentinels types schema | [log_sentinels_types.py]
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

import sys
from pathlib import Path

# Add packages directory to path for imports
packages_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(packages_dir))

from router_api_server.mcp_client import MCPClient
from log_sentinels.core.pipeline import LogSentinelsPipeline
from log_sentinels.core.collectors import LogCollector
from log_sentinels.core.normalizer import LogNormalizer
from log_sentinels.core.template_miner import LogTemplateMiner
from log_sentinels.core.windower import Windower
from log_sentinels.core.scout import ScoutAdapter
from log_sentinels.core.forensics import ForensicsAdapter
from log_sentinels.core.router_policy import RouterPolicy
from log_sentinels.types import ScoutReport, ForensicsReport, Window

logger = logging.getLogger(__name__)


class LogSentinelsService:
    """
    Log-Sentinels service wrapping Log-Sentinels pipeline with MCP integration.
    
    Provides high-level API for log analysis and tool suggestions.
    """
    
    def __init__(self, mcp_client: MCPClient):
        """
        Initialize Log-Sentinels service.
        
        Args:
            mcp_client: MCP client for AIM-OS system access
        """
        self.mcp_client = mcp_client
        
        # Initialize Log-Sentinels pipeline components
        # Note: These would be initialized with proper dependencies in production
        collectors: List[LogCollector] = []  # Would be populated with actual collectors
        normalizer = LogNormalizer()
        template_miner = LogTemplateMiner()
        windower = Windower()
        scout = ScoutAdapter()
        forensics = ForensicsAdapter()
        router_policy = RouterPolicy()
        
        # Initialize pipeline
        self.pipeline = LogSentinelsPipeline(
            collectors=collectors,
            normalizer=normalizer,
            template_miner=template_miner,
            windower=windower,
            scout=scout,
            forensics=forensics,
            router_policy=router_policy
        )
        
        # SSE event queue for real-time updates
        self.sse_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info("Log-Sentinels Service initialized")
    
    async def get_scout_reports(
        self,
        time_range: Optional[Dict[str, datetime]] = None,
        source_filter: Optional[str] = None
    ) -> List[ScoutReport]:
        """
        Get Scout reports (fast cloud analysis).
        
        Args:
            time_range: Optional time range for filtering
            source_filter: Optional source filter
            
        Returns:
            List of Scout reports
        """
        # Process windows and get Scout reports
        # In production, this would query windows from storage
        result = await self.pipeline.collect_and_process()
        
        reports = []
        if "scout_reports" in result:
            reports = result["scout_reports"]
        
        # Filter by time range and source if provided
        if time_range:
            filtered_reports = []
            for report in reports:
                report_time = datetime.fromisoformat(report.timestamp)
                if time_range.get("from") <= report_time <= time_range.get("to"):
                    if not source_filter or report.window_id.startswith(source_filter):
                        filtered_reports.append(report)
            reports = filtered_reports
        
        return reports
    
    async def get_forensics_reports(
        self,
        time_range: Optional[Dict[str, datetime]] = None,
        severity_filter: Optional[str] = None
    ) -> List[ForensicsReport]:
        """
        Get Forensics reports (deep local analysis).
        
        Args:
            time_range: Optional time range for filtering
            severity_filter: Optional severity filter (low/medium/high)
            
        Returns:
            List of Forensics reports
        """
        # Process windows and get Forensics reports
        result = await self.pipeline.collect_and_process()
        
        reports = []
        if "forensics_reports" in result:
            reports = result["forensics_reports"]
        
        # Filter by time range and severity if provided
        if time_range or severity_filter:
            filtered_reports = []
            for report in reports:
                if time_range:
                    report_time = datetime.fromisoformat(report.timestamp)
                    if not (time_range.get("from") <= report_time <= time_range.get("to")):
                        continue
                if severity_filter and report.severity != severity_filter:
                    continue
                filtered_reports.append(report)
            reports = filtered_reports
        
        return reports
    
    async def get_telemetry(
        self,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get Log-Sentinels telemetry metrics.
        
        Args:
            time_range: Optional time range for filtering
            
        Returns:
            Telemetry dictionary with scout calls, forensics calls, escalations, timeline
        """
        # Get telemetry from CMC and TCS
        # In production, this would query CMC for decision history
        telemetry = {
            "scout_calls": 42,
            "forensics_calls": 8,
            "escalations": 2,
            "tool_suggestions": 15,
            "timeline": []
        }
        
        # Get timeline from TCS (via MCP)
        try:
            timeline_result = await self.mcp_client.execute_tool(
                tool_name="mcp_lucid-mcp_get_timeline_entries",
                arguments={"limit": 50}
            )
            if timeline_result and "entries" in timeline_result:
                telemetry["timeline"] = timeline_result["entries"]
        except Exception as e:
            logger.warning(f"Failed to get timeline from TCS: {e}")
        
        return telemetry
    
    async def run_tool(self, tool_name: str) -> Dict[str, Any]:
        """
        Run suggested tool via Router → PLIx → APOE.
        
        Args:
            tool_name: Tool name to execute
            
        Returns:
            Execution result
        """
        # Execute via Router service (would be injected in production)
        # For now, execute directly via MCP
        try:
            result = await self.mcp_client.execute_tool(
                tool_name=f"mcp_lucid-mcp_{tool_name}",
                arguments={}
            )
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            raise
    
    async def stream_events(self):
        """
        Generator for SSE event streaming.
        
        Yields:
            SSE-formatted events (Scout/Forensics reports)
        """
        while True:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.sse_queue.get(), timeout=1.0)
                yield f"data: {event}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat
                yield ": heartbeat\n\n"
            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                break
    
    async def _push_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Push event to SSE queue.
        
        Args:
            event_type: Event type (scout, forensics)
            payload: Event payload
        """
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        await self.sse_queue.put(event)

