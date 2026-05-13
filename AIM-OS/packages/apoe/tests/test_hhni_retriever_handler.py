"""Targeted tests for APOE HHNI retriever handler (standard interface)."""

from __future__ import annotations
from typing import Any, List
from unittest.mock import patch
import pytest

from apoe.retriever_role import RetrieverRole
from apoe.models import Budget


class _FakeNode:
	"""Minimal node to mimic HHNI node structure."""
	def __init__(self, node_id: str, content: str, level: Any, metadata: dict | None = None):
		self.id = node_id
		self.content = content
		self.level = level
		self.metadata = metadata or {}


class _Level:
	"""Mimic enum with value attribute."""
	def __init__(self, value: str):
		self.value = value


class _FakeItem:
	def __init__(self, node: _FakeNode, score: float):
		self.node = node
		self.score = score


class _FakeResult:
	def __init__(self, items: List[_FakeItem], total_tokens: int):
		self.selected_items = items
		self.total_tokens = total_tokens
		self.coarse_time_ms = 5
		self.dvns_time_ms = 7
		self.relevance_score = 0.9
		self.efficiency = 0.8
		self.audit_trail = {"ok": True}


class _FakeRetriever:
	"""Stand-in for TwoStageRetriever with config."""
	def __init__(self, hierarchical_index: Any, config: Any):
		self.index = hierarchical_index
		self.config = config

	def retrieve(self, query: str, token_budget: int, target_level: Any, provider: Any):
		items = [
			_FakeItem(_FakeNode("n1", "content 1", _Level("paragraph")), 0.95),
			_FakeItem(_FakeNode("n2", "content 2", _Level("paragraph")), 0.90),
		]
		# Return within budget
		return _FakeResult(items, total_tokens=min(token_budget, 1200))


@patch("apoe.retriever_role.TwoStageRetriever", _FakeRetriever)
@patch("apoe.retriever_role.HHNI_AVAILABLE", True)
def test_retriever_budget_metrics_and_schema():
	"""Ensure handler respects budget and returns RetrievalResult-like schema."""
	hhni_index = object()  # placeholder
	role = RetrieverRole(hierarchical_index=hhni_index)
	budget = Budget(tokens_limit=1500, time_limit_seconds=10.0)
	result = role.execute(
		inputs={"query": "test", "modality": "code", "k": 5, "enable_dvns": True},
		budget=budget,
	)
	assert "context" in result and isinstance(result["context"], list)
	assert "total_tokens" in result and result["total_tokens"] <= 1500
	assert "relevance_scores" in result
	assert result["metrics"]["budget_utilization"] <= 1.0
	assert result["modality"] == "code"
	assert result["k"] == len(result["context"])
	assert result["dvns_enabled"] is True


@patch("apoe.retriever_role.TwoStageRetriever", _FakeRetriever)
@patch("apoe.retriever_role.HHNI_AVAILABLE", True)
def test_retriever_multi_resolution_path():
	"""Ensure multi-resolution branch returns per-level results."""
	hhni_index = object()
	role = RetrieverRole(hierarchical_index=hhni_index)
	budget = Budget(tokens_limit=3000, time_limit_seconds=10.0)
	result = role._execute_multi_resolution(
		inputs={"query": "test", "resolution_levels": ["section", "paragraph"], "modality": "docs"},
		budget=budget,
	)
	assert "multi_resolution" in result
	assert set(result["multi_resolution"].keys()) == {"section", "paragraph"}
	assert result["total_tokens"] > 0
	assert result["modality"] == "docs"


