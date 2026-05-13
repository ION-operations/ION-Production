from __future__ import annotations

import os
import types
import sys
from typing import Any, Dict, List

import pytest

from hhni import indexer
from hhni.retrieval import TwoStageRetriever, RetrievalConfig
from hhni.semantic_search import SearchResult, EmbeddingProvider
from hhni.hierarchical_index import IndexLevel


class DummyActivationTracker:
    calls: List[Dict[str, Any]] = []

    def __init__(self) -> None:
        # separate instance buffer if needed
        self.instance_calls: List[Dict[str, Any]] = []

    def _record(self, name: str, payload: Dict[str, Any]) -> None:
        rec = {"method": name, "payload": payload}
        DummyActivationTracker.calls.append(rec)
        self.instance_calls.append(rec)

    # API per Meta spec (subset used by HHNI Phase 1 wiring)
    def capture_state(self, *, source: str, data: Dict[str, Any]) -> None:
        self._record("capture_state", {"source": source, "data": data})

    def record_document_read(self, *, document_id: str) -> None:
        self._record("record_document_read", {"document_id": document_id})

    def record_concept_use(self, *, concepts: List[str], metadata: Dict[str, Any]) -> None:
        self._record("record_concept_use", {"concepts": list(concepts), "metadata": dict(metadata)})

    def record_principle_use(self, *, principle: str, metadata: Dict[str, Any]) -> None:
        self._record("record_principle_use", {"principle": principle, "metadata": dict(metadata)})


def _install_fake_cas_module(monkeypatch: pytest.MonkeyPatch) -> None:
    DummyActivationTracker.calls.clear()
    fake_module = types.ModuleType("packages.cas.client")
    fake_module.ActivationTracker = DummyActivationTracker  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "packages.cas.client", fake_module)


class DummyAtom:
    def __init__(self, atom_id: str, inline: str, tags=None) -> None:
        self.id = atom_id
        self.content = type("Content", (), {"inline": inline, "uri": None, "media_type": "text/plain"})
        self.tags = tags or {}
        # use HHNINode default factory pattern (not importing models here)
        from datetime import datetime, timezone

        self.created_at = datetime.now(timezone.utc)
        self.hash = "hash123"
        self.witness = type("Witness", (), {"snapshot_id": "snap-1"})


class DummyDGraphClient:
    def __init__(self) -> None:
        self.upserts: List[Dict[str, Any]] = []

    def upsert_nodes(self, nodes) -> None:
        self.upserts.append({"nodes": list(nodes)})


class DummyQdrantClient:
    def upsert(self, collection_name, points):
        return {"ok": True}


@pytest.fixture(autouse=True)
def enable_cas(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CAS_ENABLED", "true")
    _install_fake_cas_module(monkeypatch)
    yield
    DummyActivationTracker.calls.clear()


def test_indexer_calls_cas_pre_and_post_hooks(monkeypatch: pytest.MonkeyPatch):
    dg = DummyDGraphClient()
    qd = DummyQdrantClient()
    atom = DummyAtom("a1", "Hello world.\nThis is a test.")

    # Run
    nodes = indexer.build_hhni_for_atom(atom=atom, dgraph_client=dg, qdrant_client=qd)

    # Assert CAS calls happened (order-insensitive check by method names)
    methods = [c["method"] for c in DummyActivationTracker.calls]
    assert "capture_state" in methods  # pre_index
    assert "record_document_read" in methods
    assert methods.count("capture_state") >= 2  # pre_index + post_index
    assert "record_concept_use" in methods

    # Basic payload sanity
    pre = next(c for c in DummyActivationTracker.calls if c["method"] == "capture_state" and c["payload"]["source"] == "hhni.pre_index")
    post = next(c for c in DummyActivationTracker.calls if c["method"] == "capture_state" and c["payload"]["source"] == "hhni.post_index")
    assert pre["payload"]["data"]["atom_id"] == "a1"
    assert post["payload"]["data"]["atom_id"] == "a1"
    # Ensure enriched payload fields exist
    assert "content_preview" in pre["payload"]["data"]
    assert isinstance(pre["payload"]["data"]["content_preview"], str)
    assert isinstance(nodes, list) and len(nodes) > 0


def test_retrieval_calls_cas_retrieval_hook(monkeypatch: pytest.MonkeyPatch):
    # Prepare retriever with minimal fakes
    retr = TwoStageRetriever(hierarchical_index=object(), config=RetrievalConfig(coarse_k=3, min_relevance=0.0))

    # Fake coarse search results
    def fake_search(query: str, target_level: IndexLevel, top_k: int, filter_fn=None):
        node = type("Node", (), {"id": "n1", "level": IndexLevel.PARAGRAPH, "content": "x", "summary": "x", "metadata": {}})
        return [SearchResult(node=node, score=0.9, confidence=0.9, provider=EmbeddingProvider.FALLBACK)]

    monkeypatch.setattr(retr.semantic_search, "search", fake_search)

    # Fake DVNS refinement
    class _Metrics:
        iterations = 5
        avg_velocity = 0.1
        avg_displacement = 0.2
        max_velocity = 0.01

    class _Particle:
        def __init__(self, id: str):
            self.id = id
            self.position = type("P", (), {"x": 0, "y": 0, "z": 0})
            self.mass = 1.0

    class _SimResult:
        def __init__(self):
            self.metrics = _Metrics()
            self.particles = [_Particle("n1")]

    monkeypatch.setattr(retr, "_run_dvns_refinement", lambda *a, **k: _SimResult())

    # Fake budget allocation
    class _Alloc:
        def __init__(self):
            self.included = [type("I", (), {"source_id": "n1"})]
            self.excluded = []
            self.total_tokens_used = 10
            self.efficiency = 0.8
            self.audit_trail = {"excluded_high_relevance": []}

    monkeypatch.setattr(retr.budget_manager, "optimize_for_budget", lambda *a, **k: _Alloc())

    # Run
    result = retr.retrieve("hello", token_budget=100, target_level=IndexLevel.PARAGRAPH)

    # Assert CAS retrieval hook fired
    methods = [c["method"] for c in DummyActivationTracker.calls]
    assert "record_principle_use" in methods
    assert "capture_state" in methods

    # Sanity
    assert result.total_tokens == 10
    rec = next(c for c in DummyActivationTracker.calls if c["method"] == "record_principle_use")
    assert rec["payload"]["principle"] == "hhni.retrieval"
    assert rec["payload"]["metadata"]["selected_ids"] == ["n1"]

    # Validate retrieval capture_state enrichment
    retrieval_states = [
        c for c in DummyActivationTracker.calls
        if c["method"] == "capture_state" and c["payload"]["source"] == "hhni.retrieval"
    ]
    assert len(retrieval_states) >= 1
    state = retrieval_states[-1]
    data = state["payload"]["data"]
    assert data.get("selected_ids") == ["n1"]
    assert data.get("dvns_iterations") == 5


