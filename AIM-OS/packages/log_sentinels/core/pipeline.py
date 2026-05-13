"""
Log-Sentinels pipeline - main processing pipeline.
"""

from typing import List, Dict, Any, Optional
import uuid
import time

from ..types import LogRecord, Window, ScoutReport, ForensicsReport, RouterDecision
from .collectors import LogCollector
from .normalizer import LogNormalizer
from .template_miner import LogTemplateMiner
from .windower import Windower
from .scout import ScoutAdapter
from .forensics import ForensicsAdapter
from .router_policy import RouterPolicy


class LogSentinelsPipeline:
    """
    Main Log-Sentinels pipeline.
    
    Flow:
    1. Collect logs from sources
    2. Normalize (redact PII)
    3. Mine templates
    4. Create windows
    5. Scout analysis (fast, cloud)
    6. Router policy decision
    7. Forensics analysis (if escalated, local)
    8. Record in SEG/VIF/CMC/TCS
    """
    
    def __init__(
        self,
        collectors: List[LogCollector],
        normalizer: LogNormalizer,
        template_miner: LogTemplateMiner,
        windower: Windower,
        scout: ScoutAdapter,
        forensics: ForensicsAdapter,
        router_policy: RouterPolicy
    ):
        self.collectors = collectors
        self.normalizer = normalizer
        self.template_miner = template_miner
        self.windower = windower
        self.scout = scout
        self.forensics = forensics
        self.router_policy = router_policy
        
        # Buffer for log records
        self.log_buffer: List[LogRecord] = []
    
    async def process_window(self, win_id: str) -> Dict[str, Any]:
        """
        Process a log window.
        
        Args:
            win_id: Window ID to process
            
        Returns:
            Processing result with Scout/Forensics reports
        """
        # Get window
        window = await self._get_window(win_id)
        if not window:
            return {"error": "Window not found"}
        
        # Scout analysis (fast, cloud)
        scout_report = await self.scout.analyze(window)
        
        # Router policy decision
        novelty = await self.template_miner.novelty_score(window)
        decision = self.router_policy.decide(scout_report, novelty)
        
        result = {
            "window_id": win_id,
            "scout_report": scout_report,
            "decision": decision
        }
        
        if decision.kind == "escalate":
            # Forensics analysis (deep, local)
            context = await self._build_local_context(window)
            forensics_report = await self.forensics.analyze(window, context)
            result["forensics_report"] = forensics_report
        
        return result
    
    async def collect_and_process(self) -> Dict[str, Any]:
        """
        Collect logs and process windows.
        
        Returns:
            Processing results
        """
        # Collect logs from all sources
        all_logs = []
        for collector in self.collectors:
            logs = await collector.collect()
            all_logs.extend(logs)
        
        # Normalize (redact PII)
        normalized_logs = []
        for log in all_logs:
            normalized = self.normalizer.normalize(log)
            normalized_logs.append(normalized)
        
        # Mine templates
        templates = self.template_miner.mine(normalized_logs)
        
        # Create windows
        window = await self.windower.create_window(normalized_logs)
        if not window:
            return {"status": "no_window", "reason": "insufficient_records"}
        
        # Update window with templates
        window.templates = templates
        
        # Process window
        return await self.process_window(window.id)
    
    async def _get_window(self, win_id: str) -> Optional[Window]:
        """Get window by ID (stub - would query storage in production)."""
        # In production, would query window storage
        return None
    
    async def _build_local_context(self, window: Window) -> Dict[str, Any]:
        """Build local context for forensics analysis."""
        # In production, would gather:
        # - Recent diffs
        # - Failing tests
        # - Recent PRs
        # - System state
        return {
            "window": window,
            "context": "local_context_placeholder"
        }

