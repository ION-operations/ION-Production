"""
Router system test suite - comprehensive unit and integration tests.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.core.router import Router
from router.core.scout import ScoutLLM
from router.core.bandit import BanditScorer
from router.core.rules import RulesEngine
from router.core.manifest import ToolManifest, Tool, SideEffect
from router.core.snapshot import SnapshotBuilder
from router.core.cache import RouterCache
from router.types import (
    RouterContext,
    Snapshot,
    ToolProposal,
    ToolCallPlan,
    ToolCallStep
)


@pytest.fixture
def sample_tool():
    """Create a sample tool for testing."""
    return Tool(
        name="test_tool",
        version="1.0.0",
        capability=["test:run", "debug:analyze"],
        inputs={"file": "string"},
        outputs={"result": "string"},
        preconditions=["file_exists"],
        side_effects=[SideEffect.NONE],
        avg_latency_ms=100.0,
        avg_cost=0.001,
        risk="low",
        success_rate=0.9
    )


@pytest.fixture
def tool_manifest(sample_tool):
    """Create tool manifest with sample tool."""
    manifest = ToolManifest()
    manifest.register(sample_tool)
    return manifest


@pytest.fixture
def router_context():
    """Create sample router context."""
    return RouterContext(
        goal="Fix test failures",
        task="Run tests and fix errors",
        confidence=0.8,
        files=["test_file.py"],
        errors=["Test failed"],
        agent_intent="debug",
        budget={"tokens": 1000, "cost": 0.1}
    )


@pytest.fixture
def snapshot():
    """Create sample snapshot."""
    return Snapshot(
        cmc_decisions=[],
        hhni_context=[],
        vif_status={"confidence": 0.8},
        seg_evidence=[],
        tcs_cursor={},
        goal="Fix test failures",
        summary="Test context summary"
    )


class TestRouterCache:
    """Test Router caching system."""
    
    @pytest.mark.asyncio
    async def test_cache_proposals(self, snapshot):
        """Test caching tool proposals."""
        cache = RouterCache(ttl_seconds=300)
        
        proposals = [
            ToolProposal(
                tool_name="test_tool",
                rationale="Test rationale",
                draft_arguments={},
                confidence=0.8
            )
        ]
        
        # Cache proposals
        await cache.cache_proposals(snapshot, proposals)
        
        # Retrieve cached proposals
        cached = await cache.get_cached_proposals(snapshot)
        assert cached == proposals
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, snapshot):
        """Test cache expiration."""
        cache = RouterCache(ttl_seconds=1)  # 1 second TTL
        
        proposals = [
            ToolProposal(
                tool_name="test_tool",
                rationale="Test",
                draft_arguments={},
                confidence=0.8
            )
        ]
        
        await cache.cache_proposals(snapshot, proposals)
        
        # Should be cached
        cached = await cache.get_cached_proposals(snapshot)
        assert cached == proposals
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Should be expired
        cached = await cache.get_cached_proposals(snapshot)
        assert cached is None
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = RouterCache()
        stats = cache.get_stats()
        
        assert "context_cache_size" in stats
        assert "max_size" in stats
        assert stats["max_size"] == 1000


class TestScoutLLM:
    """Test Scout LLM adapter."""
    
    @pytest.mark.asyncio
    async def test_propose_with_cache(self, snapshot, tool_manifest):
        """Test tool proposal with pattern caching."""
        scout = ScoutLLM()
        
        # First call - should generate proposals
        proposals1 = await scout.propose(snapshot, tool_manifest)
        
        # Second call with same snapshot - should use cache
        proposals2 = await scout.propose(snapshot, tool_manifest)
        
        # Should return same proposals (from cache)
        assert proposals1 == proposals2
    
    def test_pattern_key_generation(self, snapshot):
        """Test pattern key generation."""
        scout = ScoutLLM()
        key1 = scout._get_pattern_key(snapshot)
        key2 = scout._get_pattern_key(snapshot)
        
        # Same snapshot should generate same key
        assert key1 == key2
    
    def test_optimized_prompt(self, snapshot, tool_manifest):
        """Test optimized prompt generation."""
        scout = ScoutLLM()
        prompt = scout._build_optimized_prompt(snapshot, tool_manifest)
        
        # Should contain goal and context
        assert snapshot.goal[:200] in prompt
        assert "Tools" in prompt
        assert len(prompt) < 2000  # Should be reasonably sized


class TestBanditScorer:
    """Test Bandit scoring layer."""
    
    @pytest.mark.asyncio
    async def test_score_proposals(self, snapshot, tool_manifest):
        """Test scoring tool proposals."""
        bandit = BanditScorer()
        
        proposals = [
            ToolProposal(
                tool_name="test_tool",
                rationale="Test",
                draft_arguments={},
                confidence=0.8
            )
        ]
        
        ranked = await bandit.score(proposals, snapshot, tool_manifest)
        
        assert len(ranked) > 0
        assert ranked[0].proposal.tool_name == "test_tool"
        assert ranked[0].score >= 0
    
    @pytest.mark.asyncio
    async def test_parallel_scoring(self, snapshot, tool_manifest):
        """Test parallel scoring of multiple proposals."""
        bandit = BanditScorer()
        
        proposals = [
            ToolProposal(
                tool_name="test_tool",
                rationale="Test",
                draft_arguments={},
                confidence=0.8
            )
            for _ in range(5)
        ]
        
        ranked = await bandit.score(proposals, snapshot, tool_manifest)
        
        assert len(ranked) == 5
        # Should be sorted by score (descending)
        scores = [r.score for r in ranked]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_learn_from_outcome(self):
        """Test learning from execution outcome."""
        bandit = BanditScorer()
        
        proposal = ToolProposal(
            tool_name="test_tool",
            rationale="Test",
            draft_arguments={},
            confidence=0.8
        )
        
        outcome = {
            "success": True,
            "quality_score": 0.9,
            "user_feedback": 1
        }
        
        # Should not raise exception
        await bandit.learn_from_outcome(proposal, outcome)
        
        # Weights should be normalized
        total_weight = sum(bandit.weights.values())
        assert abs(total_weight - 1.0) < 0.01


class TestRulesEngine:
    """Test Rules engine."""
    
    def test_validate_plan(self, tool_manifest):
        """Test plan validation."""
        rules = RulesEngine()
        
        plan = ToolCallPlan(
            plan_id="test_plan",
            goal="Test goal",
            steps=[
                ToolCallStep(
                    id="step1",
                    tool="test_tool",
                    args={}
                )
            ],
            context=RouterContext(
                goal="Test",
                task="Test",
                confidence=0.8,
                files=[],
                errors=[],
                agent_intent="test",
                budget={}
            )
        )
        
        result = rules.validate(plan)
        assert isinstance(result, ValidationResult)
        assert result.passed or len(result.reasons) > 0
    
    def test_depth_limit(self):
        """Test depth limit validation."""
        rules = RulesEngine()
        rules.max_depth = 2
        
        plan = ToolCallPlan(
            plan_id="test",
            goal="Test",
            steps=[ToolCallStep(id=f"s{i}", tool="test", args={}) for i in range(5)],
            context=RouterContext(
                goal="Test",
                task="Test",
                confidence=0.8,
                files=[],
                errors=[],
                agent_intent="test",
                budget={}
            )
        )
        
        result = rules.validate(plan)
        if len(plan.steps) > rules.max_depth:
            assert not result.passed


class TestRouter:
    """Test Router main class."""
    
    @pytest.mark.asyncio
    async def test_decide_with_cache(self, router_context, tool_manifest):
        """Test Router decision with caching."""
        scout = ScoutLLM()
        bandit = BanditScorer()
        rules = RulesEngine()
        snapshot_builder = Mock(spec=SnapshotBuilder)
        cache = RouterCache()
        
        # Mock snapshot builder
        snapshot = Snapshot(
            cmc_decisions=[],
            hhni_context=[],
            vif_status={},
            seg_evidence=[],
            tcs_cursor={},
            goal=router_context.goal,
            summary="Test summary"
        )
        snapshot_builder.build = AsyncMock(return_value=snapshot)
        
        router = Router(
            scout=scout,
            bandit=bandit,
            rules=rules,
            manifest=tool_manifest,
            snapshot_builder=snapshot_builder,
            cache=cache
        )
        
        # First decision
        plan1 = await router.decide(router_context)
        assert isinstance(plan1, ToolCallPlan)
        
        # Second decision (should use cache)
        plan2 = await router.decide(router_context)
        assert isinstance(plan2, ToolCallPlan)
    
    @pytest.mark.asyncio
    async def test_update_success_rate(self, tool_manifest):
        """Test updating tool success rate."""
        scout = ScoutLLM()
        bandit = BanditScorer()
        rules = RulesEngine()
        snapshot_builder = Mock(spec=SnapshotBuilder)
        
        router = Router(
            scout=scout,
            bandit=bandit,
            rules=rules,
            manifest=tool_manifest,
            snapshot_builder=snapshot_builder
        )
        
        # Should not raise exception
        await router.update_success_rate("test_tool", True)


class TestToolManifest:
    """Test Tool manifest system."""
    
    def test_register_tool(self, sample_tool):
        """Test registering a tool."""
        manifest = ToolManifest()
        manifest.register(sample_tool)
        
        assert manifest.get_tool("test_tool") == sample_tool
        assert manifest.get_tool_count() == 1
    
    def test_find_tools_by_capability(self, sample_tool):
        """Test finding tools by capability."""
        manifest = ToolManifest()
        manifest.register(sample_tool)
        
        tools = manifest.find_tools_by_capability("test:run")
        assert len(tools) == 1
        assert tools[0] == sample_tool
    
    def test_list_tools(self, sample_tool):
        """Test listing all tools."""
        manifest = ToolManifest()
        manifest.register(sample_tool)
        
        tools = manifest.list_tools()
        assert len(tools) == 1
        assert tools[0] == sample_tool


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

