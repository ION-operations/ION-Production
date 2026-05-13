"""
Snapshot builder - builds system state snapshot from AIM-OS systems.
"""

from typing import Dict, List, Any
from datetime import datetime

from ..types import RouterContext, Snapshot


class SnapshotBuilder:
    """
    Builds snapshot of current system state from AIM-OS systems.
    
    Pulls from:
    - CMC: Recent decisions, diffs
    - HHNI: Semantic context retrieval
    - VIF: Quality status
    - SEG: Evidence chains
    - TCS: Timeline cursor
    """
    
    def __init__(
        self,
        cmc_client=None,
        hhni_client=None,
        vif_client=None,
        seg_client=None,
        tcs_client=None
    ):
        self.cmc = cmc_client
        self.hhni = hhni_client
        self.vif = vif_client
        self.seg = seg_client
        self.tcs = tcs_client
    
    async def build(self, ctx: RouterContext) -> Snapshot:
        """
        Build snapshot from current system state.
        
        Args:
            ctx: Router context
            
        Returns:
            Snapshot with all system state
        """
        # Pull from CMC
        cmc_decisions = await self._get_cmc_decisions(ctx)
        
        # Pull from HHNI
        hhni_context = await self._get_hhni_context(ctx)
        
        # Pull from VIF
        vif_status = await self._get_vif_status(ctx)
        
        # Pull from SEG
        seg_evidence = await self._get_seg_evidence(ctx)
        
        # Pull from TCS
        tcs_cursor = await self._get_tcs_cursor(ctx)
        
        # Build summary
        summary = self._build_summary(
            cmc_decisions,
            hhni_context,
            vif_status,
            seg_evidence,
            tcs_cursor
        )
        
        return Snapshot(
            cmc_decisions=cmc_decisions,
            hhni_context=hhni_context,
            vif_status=vif_status,
            seg_evidence=seg_evidence,
            tcs_cursor=tcs_cursor,
            goal=ctx.goal,
            summary=summary,
            timestamp=datetime.utcnow()
        )
    
    async def _get_cmc_decisions(self, ctx: RouterContext) -> List[Dict[str, Any]]:
        """Get recent decisions from CMC."""
        if not self.cmc:
            return []
        
        # Use MCP tool to retrieve memory
        try:
            # This would use mcp_lucid-mcp_retrieve_memory in production
            # For now, return empty list
            return []
        except Exception:
            return []
    
    async def _get_hhni_context(self, ctx: RouterContext) -> List[Dict[str, Any]]:
        """Get semantic context from HHNI."""
        if not self.hhni:
            return []
        
        try:
            # Use HHNI to retrieve relevant context
            # This would use mcp_lucid-mcp_retrieve_memory with HHNI backend
            return []
        except Exception:
            return []
    
    async def _get_vif_status(self, ctx: RouterContext) -> Dict[str, Any]:
        """Get VIF quality status."""
        if not self.vif:
            return {}
        
        try:
            # Get VIF status
            return {
                "confidence": ctx.confidence,
                "status": "active"
            }
        except Exception:
            return {}
    
    async def _get_seg_evidence(self, ctx: RouterContext) -> List[Dict[str, Any]]:
        """Get evidence chains from SEG."""
        if not self.seg:
            return []
        
        try:
            # Get SEG evidence related to context
            return []
        except Exception:
            return []
    
    async def _get_tcs_cursor(self, ctx: RouterContext) -> Dict[str, Any]:
        """Get timeline cursor from TCS."""
        if not self.tcs:
            return {}
        
        try:
            # Get TCS cursor
            return {
                "sequence": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception:
            return {}
    
    def _build_summary(
        self,
        cmc_decisions: List[Dict[str, Any]],
        hhni_context: List[Dict[str, Any]],
        vif_status: Dict[str, Any],
        seg_evidence: List[Dict[str, Any]],
        tcs_cursor: Dict[str, Any]
    ) -> str:
        """Build compact summary from all system state."""
        parts = []
        
        if cmc_decisions:
            parts.append(f"{len(cmc_decisions)} recent decisions")
        
        if hhni_context:
            parts.append(f"{len(hhni_context)} context items")
        
        if vif_status:
            parts.append(f"VIF confidence: {vif_status.get('confidence', 0.0)}")
        
        if seg_evidence:
            parts.append(f"{len(seg_evidence)} evidence chains")
        
        return "; ".join(parts) if parts else "No context available"

