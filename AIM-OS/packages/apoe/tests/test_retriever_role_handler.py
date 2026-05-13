from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

import apoe.retriever_role as rr
from apoe.models import Budget


class _DummyLevel:
	# Mimic Enum with .value used in handler
	value = 4


class _DummyNode:
	def __init__(self, id: str, content: str):
		self.id = id
		self.content = content
		self.level = _DummyLevel()
		self.metadata = {"source": "test"}


class _DummyItem:
	def __init__(self, node: _DummyNode, score: float):
		self.node = node
		self.score = score


class _DummyResult:
	def __init__(self, items: List[_DummyItem], total_tokens: int):
		self.selected_items = items
		self.total_tokens = total_tokens
		# Populate metrics fields expected by handler
		self.coarse_time_ms = 12.3
		self.dvns_time_ms = 45.6
		self.relevance_score = sum(i.score for i in items) / max(len(items), 1)
		self.efficiency = 0.8
		self.audit_trail = {"excluded_high_relevance": []}


class _DummyRetriever:
	def __init__(self, *, hierarchical_index, config):
		self.index = hierarchical_index
		self.config = config
		self.last_call_kwargs: Dict[str, Any] = {}

	def retrieve(self, *, query: str, token_budget: int, target_level, provider) -> _DummyResult:
		self.last_call_kwargs = {
			"query": query,
			"token_budget": token_budget,
			"target_level": target_level,
			"provider": provider,
		}
		items = [
			_DummyItem(_DummyNode("n1", "alpha"), 0.9),
			_DummyItem(_DummyNode("n2", "beta"), 0.8),
		]
		# Return total_tokens bounded by provided token_budget
		return _DummyResult(items, total_tokens=min(token_budget, 1234))


@pytest.fixture(autouse=True)
def _force_hhni(monkeypatch: pytest.MonkeyPatch):
	# Force HHNI availability and patch retriever with dummy
	monkeypatch.setattr(rr, "HHNI_AVAILABLE", True)
	monkeypatch.setattr(rr, "TwoStageRetriever", _DummyRetriever)
	# Stub RetrievalConfig used by RetrieverRole.__init__
	class _StubRetrievalConfig:
		def __init__(
			self,
			*,
			coarse_k: int,
			min_relevance: float,
			token_budget: int,
			enable_conflict_resolution: bool,
			enable_compression: bool,
		):
			self.coarse_k = coarse_k
			self.min_relevance = min_relevance
			self.token_budget = token_budget
			self.enable_conflict_resolution = enable_conflict_resolution
			self.enable_compression = enable_compression
	monkeypatch.setattr(rr, "RetrievalConfig", _StubRetrievalConfig)
	# Provide minimal stubs for types used
	class _StubIndex:
		pass
	monkeypatch.setattr(rr, "HierarchicalIndex", _StubIndex)
	# Enum-like provider not used by dummy, but pass something
	class _StubProvider:
		LOCAL = "local"
	monkeypatch.setattr(rr, "EmbeddingProvider", _StubProvider)
	# Provide IndexLevel enum with attributes used in _modality_to_level()
	class _StubIndexLevel:
		SYSTEM = object()
		SECTION = object()
		PARAGRAPH = object()
		SENTENCE = object()
	monkeypatch.setattr(rr, "IndexLevel", _StubIndexLevel)


def test_budget_adherence(monkeypatch: pytest.MonkeyPatch):
	index = object()
	role = rr.RetrieverRole(hierarchical_index=index)
	assert role.retriever is not None
	# Budget smaller than dummy default
	budget = Budget(tokens_limit=500, time_limit_seconds=5.0)
	inputs = {"query": "q", "k": 10, "modality": "docs", "enable_dvns": True}
	result = role.execute(inputs=inputs, budget=budget)
	assert result["total_tokens"] <= 500
	# Ensure config and call propagated token budget
	assert role.retriever.config.token_budget == 500
	assert role.retriever.last_call_kwargs.get("token_budget") == 500


def test_schema_compliance():
	index = object()
	role = rr.RetrieverRole(hierarchical_index=index)
	budget = Budget(tokens_limit=800, time_limit_seconds=10.0)
	inputs = {"query": "schema test", "k": 2, "modality": "text"}
	result = role.execute(inputs=inputs, budget=budget)
	# Top-level keys
	for key in ["context", "total_tokens", "relevance_scores", "modality", "k", "dvns_enabled", "metrics"]:
		assert key in result
	# Context item shape
	assert isinstance(result["context"], list) and len(result["context"]) >= 1
	item = result["context"][0]
	for key in ["id", "content", "level", "relevance", "metadata"]:
		assert key in item
	# Metrics fields presence
	metrics = result["metrics"]
	for key in ["coarse_time_ms", "dvns_time_ms", "relevance_score", "efficiency", "budget_utilization"]:
		assert key in metrics


def test_fallback_when_no_query():
	index = object()
	role = rr.RetrieverRole(hierarchical_index=index)
	result = role.execute(inputs={"query": ""}, budget=Budget(tokens_limit=100, time_limit_seconds=1.0))
	assert result.get("error") == "No query provided"


def test_multi_resolution_mode(monkeypatch: pytest.MonkeyPatch):
	index = object()
	role = rr.RetrieverRole(hierarchical_index=index)
	# Provide resolution levels to trigger multi-resolution branch
	inputs = {
		"query": "multi",
		"modality": "docs",
		"resolution_levels": ["system", "section", "paragraph"],
	}
	budget = Budget(tokens_limit=900, time_limit_seconds=10.0)
	result = role.execute(inputs=inputs, budget=budget)
	assert "multi_resolution" in result
	mr = result["multi_resolution"]
	# Should include entries for each requested level
	for level in ["system", "section", "paragraph"]:
		assert level in mr
		assert "items" in mr[level]
	assert result["total_tokens"] <= budget.tokens_limit


def test_hhni_unavailable_fallback(monkeypatch: pytest.MonkeyPatch):
	# Simulate HHNI unavailable
	monkeypatch.setattr(rr, "HHNI_AVAILABLE", False)
	role = rr.RetrieverRole(hierarchical_index=None)
	inputs = {"query": "q", "k": 5, "modality": "docs"}
	budget = Budget(tokens_limit=200, time_limit_seconds=5.0)
	result = role.execute(inputs=inputs, budget=budget)
	assert result.get("error") == "HHNI not available"
	assert result.get("context") == []

