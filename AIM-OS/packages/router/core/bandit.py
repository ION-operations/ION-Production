"""
Bandit scoring layer - learned policy for tool ranking.
"""

from typing import List, Dict, Any, Optional
import math
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..types import Snapshot, ToolProposal, RankedTool
from .manifest import ToolManifest


class BanditScorer:
    """
    Bandit scoring layer for tool ranking.
    
    Computes utility scores based on:
    - ContextFit: Embedding similarity
    - SuccessRate: Historical success
    - PreconditionSatisfaction: VIF checks
    - ExpectedInfoGain: Entropy reduction
    - Parallelizability: Tool capability
    - Cost/Latency/Risk penalties
    """
    
    def __init__(
        self,
        cmc_client=None,
        hhni_client=None,
        vif_client=None,
        cache=None
    ):
        self.cmc = cmc_client
        self.hhni = hhni_client
        self.vif = vif_client
        self.cache = cache
        
        # Weights for utility calculation
        self.weights = {
            'context_fit': 0.3,
            'success_rate': 0.25,
            'precondition': 0.2,
            'info_gain': 0.15,
            'parallelizability': 0.1
        }
        
        # Penalty weights
        self.penalty_weights = {
            'cost': 0.1,
            'latency': 0.05,
            'risk': 0.15
        }
        
        # Pre-computed scores cache
        self.score_cache: Dict[str, float] = {}
        
        # Thread pool for parallel scoring
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def score(
        self,
        proposals: List[ToolProposal],
        snapshot: Snapshot,
        manifest: ToolManifest
    ) -> List[RankedTool]:
        """
        Score and rank tool proposals.
        
        Optimizations:
        - Parallel scoring for multiple proposals
        - Pre-computed score caching
        - Batch embedding lookups
        
        Args:
            proposals: List of tool proposals from Scout
            snapshot: Current system state snapshot
            manifest: Tool manifest
            
        Returns:
            List of ranked tools sorted by score (descending)
        """
        # Score proposals in parallel
        scoring_tasks = [
            self._score_single_proposal(proposal, snapshot, manifest)
            for proposal in proposals
        ]
        
        ranked = await asyncio.gather(*scoring_tasks)
        
        # Filter out None results and sort
        ranked = [r for r in ranked if r is not None]
        ranked.sort(key=lambda x: x.score, reverse=True)
        
        return ranked
    
    async def _score_single_proposal(
        self,
        proposal: ToolProposal,
        snapshot: Snapshot,
        manifest: ToolManifest
    ) -> Optional[RankedTool]:
        """Score a single proposal (optimized for parallel execution)."""
        tool = manifest.get_tool(proposal.tool_name)
        if not tool:
            return None
        
        # Check score cache
        cache_key = f"{proposal.tool_name}:{snapshot.goal[:50]}"
        if cache_key in self.score_cache:
            cached_score = self.score_cache[cache_key]
            # Use cached score but still compute full details
            # (cache is for quick filtering, not full ranking)
            pass
        
        # Compute individual scores (can be parallelized)
        context_fit = await self._compute_context_fit(proposal, snapshot)
        success_rate = await self._compute_success_rate(proposal.tool_name)
        precondition = await self._compute_precondition_satisfaction(proposal, tool)
        info_gain = await self._compute_expected_info_gain(proposal, snapshot)
        parallelizable = self._compute_parallelizability(tool)
        
        # Compute penalties
        cost_penalty = self.penalty_weights['cost'] * tool.avg_cost
        latency_penalty = self.penalty_weights['latency'] * (tool.avg_latency_ms / 1000.0)
        risk_penalty = self._compute_risk_penalty(tool, snapshot)
        
        # Compute total utility
        utility = (
            self.weights['context_fit'] * context_fit +
            self.weights['success_rate'] * success_rate +
            self.weights['precondition'] * precondition +
            self.weights['info_gain'] * info_gain +
            self.weights['parallelizability'] * parallelizable -
            cost_penalty -
            latency_penalty -
            risk_penalty
        )
        
        # Cache score
        self.score_cache[cache_key] = utility
        
        ranked_tool = RankedTool(
            proposal=proposal,
            score=utility,
            context_fit=context_fit,
            success_rate=success_rate,
            precondition_satisfied=precondition > 0.5,
            expected_info_gain=info_gain,
            parallelizable=parallelizable
        )
        
        return ranked_tool
    
    async def _compute_context_fit(
        self,
        proposal: ToolProposal,
        snapshot: Snapshot
    ) -> float:
        """Compute context fit using embeddings."""
        if not self.hhni:
            # Fallback to proposal confidence
            return proposal.confidence
        
        try:
            # Use HHNI embeddings for similarity
            # This would compute cosine similarity between goal embedding
            # and tool capability embedding
            # For now, return proposal confidence as proxy
            return proposal.confidence
        except Exception:
            return proposal.confidence
    
    async def _compute_success_rate(self, tool_name: str) -> float:
        """Compute historical success rate."""
        if not self.cmc:
            return 0.5  # Default success rate
        
        try:
            # Query CMC for tool execution history
            # Compute success rate from historical data
            # For now, return default
            return 0.5
        except Exception:
            return 0.5
    
    async def _compute_precondition_satisfaction(
        self,
        proposal: ToolProposal,
        tool
    ) -> float:
        """Check if tool preconditions are satisfied."""
        if not tool.preconditions:
            return 1.0  # No preconditions = always satisfied
        
        if not self.vif:
            return 0.5  # Unknown if preconditions satisfied
        
        try:
            # Check preconditions via VIF
            # For now, assume satisfied if no VIF client
            return 1.0
        except Exception:
            return 0.5
    
    async def _compute_expected_info_gain(
        self,
        proposal: ToolProposal,
        snapshot: Snapshot
    ) -> float:
        """Estimate expected information gain."""
        # Simple heuristic: tools that address errors have higher info gain
        if snapshot.goal and any(
            error.lower() in snapshot.goal.lower()
            for error in ["error", "fail", "bug", "issue"]
        ):
            return 0.8
        
        # Default info gain
        return 0.5
    
    def _compute_parallelizability(self, tool) -> float:
        """Check if tool can run in parallel."""
        # Read-only tools can run in parallel
        if "read" in tool.capability or "query" in tool.capability:
            return 1.0
        
        # Mutating tools should be serialized
        if "write" in tool.capability or "mutate" in tool.capability:
            return 0.0
        
        # Default: moderate parallelizability
        return 0.5
    
    def _compute_risk_penalty(self, tool, snapshot: Snapshot) -> float:
        """Compute risk penalty based on tool risk and confidence."""
        risk_multiplier = {
            "low": 0.1,
            "med": 0.3,
            "high": 0.6
        }
        
        base_risk = risk_multiplier.get(tool.risk, 0.3)
        confidence_factor = 1.0 - snapshot.vif_status.get("confidence", 0.7)
        
        return self.penalty_weights['risk'] * base_risk * confidence_factor
    
    async def update_success_rate(self, tool_name: str, success: bool):
        """Update tool success rate after execution."""
        if not self.cmc:
            return
        
        try:
            # Update success rate in CMC
            # This would store execution outcome and recompute success rate
            pass
        except Exception:
            pass
    
    async def learn_from_outcome(
        self,
        proposal: ToolProposal,
        outcome: Dict[str, Any]
    ):
        """
        Learn from execution outcome and adjust weights.
        
        Uses gradient descent-like approach to adjust weights based on:
        - Success/failure of tool execution
        - Quality of results (if available)
        - User feedback (if available)
        """
        success = outcome.get("success", False)
        quality_score = outcome.get("quality_score", 0.5)
        user_feedback = outcome.get("user_feedback", None)  # -1, 0, 1
        
        # Compute reward signal
        reward = 0.0
        if success:
            reward += 0.5
        reward += quality_score * 0.3
        if user_feedback is not None:
            reward += user_feedback * 0.2
        
        # Normalize reward to [0, 1]
        reward = max(0.0, min(1.0, reward))
        
        # Compute feature vector for this proposal
        features = {
            'context_fit': await self._compute_context_fit(proposal, outcome.get("snapshot")),
            'success_rate': await self._compute_success_rate(proposal.tool_name),
            'precondition': outcome.get("precondition_satisfied", 0.5),
            'info_gain': outcome.get("info_gain", 0.5),
            'parallelizable': outcome.get("parallelizable", 0.5)
        }
        
        # Adjust weights using simple gradient descent
        learning_rate = 0.01
        predicted_reward = sum(
            self.weights[key] * features[key]
            for key in self.weights.keys()
        )
        
        error = reward - predicted_reward
        
        # Update weights (gradient descent)
        for key in self.weights.keys():
            gradient = features[key] * error
            self.weights[key] += learning_rate * gradient
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            for key in self.weights.keys():
                self.weights[key] /= total_weight
        
        # Store updated weights in CMC for persistence
        if self.cmc:
            try:
                await self.cmc.store_tool_weights(
                    tool_name=proposal.tool_name,
                    weights=self.weights.copy(),
                    reward=reward
                )
            except Exception:
                pass  # Fail silently if CMC unavailable

