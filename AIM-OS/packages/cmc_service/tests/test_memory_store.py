from __future__ import annotations

from pathlib import Path
import os

import pytest

from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate, WitnessStub
from cmc_service.store_io import JournalCorruptionError


@pytest.fixture()
def sqlite_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryStore:
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    yield store
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


@pytest.fixture()
def jsonl_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryStore:
    monkeypatch.setenv("CMC_BACKEND", "jsonl")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    yield store
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


@pytest.mark.parametrize("backend_fixture", ["sqlite_store", "jsonl_store"])
def test_create_and_list_atom(request: pytest.FixtureRequest, backend_fixture: str) -> None:
    store: MemoryStore = request.getfixturevalue(backend_fixture)
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Hello", media_type="text/plain"),
            tags={"example": 1.0},
        )
    )

    atoms = list(store.list_atoms())
    assert len(atoms) == 1
    assert atoms[0].id == atom.id
    assert atoms[0].tags["example"] == pytest.approx(1.0)


@pytest.mark.parametrize("backend_fixture", ["sqlite_store", "jsonl_store"])
def test_snapshot_roundtrip(request: pytest.FixtureRequest, backend_fixture: str) -> None:
    store: MemoryStore = request.getfixturevalue(backend_fixture)
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="World"),
        )
    )
    snapshot = store.create_snapshot()
    assert atom.id in snapshot.atom_ids

    replayed = list(store.replay_snapshot(snapshot.id))
    assert len(replayed) == 1
    assert replayed[0].id == atom.id


@pytest.mark.parametrize("backend_fixture", ["sqlite_store", "jsonl_store"])
def test_snapshot_deterministic(request: pytest.FixtureRequest, backend_fixture: str) -> None:
    store: MemoryStore = request.getfixturevalue(backend_fixture)
    for word in ["alpha", "beta", "gamma"]:
        store.create_atom(
            AtomCreate(modality="text", content=AtomContent(inline=word))
        )
    snapshot1 = store.create_snapshot()
    snapshot2 = store.create_snapshot()
    assert snapshot1.id == snapshot2.id


def test_snapshot_id_stable_after_reload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    store_path = tmp_path / "cmc"

    store = MemoryStore(store_path)
    for word in ["delta", "epsilon", "zeta"]:
        store.create_atom(
            AtomCreate(modality="text", content=AtomContent(inline=word))
        )
    original_snapshot = store.create_snapshot(note="baseline")
    store.close()

    reloaded_store = MemoryStore(store_path)
    reloaded_snapshot = reloaded_store.create_snapshot(note="baseline")
    assert reloaded_snapshot.id == original_snapshot.id
    reloaded_store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


def test_witness_stub_auto_generation_disabled_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that witness stub auto-generation is disabled by default"""
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test"),
        )
    )
    
    # Witness stub should be empty (default behavior)
    assert atom.witness.model_id is None
    assert atom.witness.tool_ids == []
    assert atom.witness.snapshot_id is None
    assert atom.witness.correlation_id is None
    
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


def test_witness_stub_auto_generation_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that witness stub auto-generation works when enabled"""
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    monkeypatch.setenv("LLM_MODEL_ID", "test-model-123")
    monkeypatch.setenv("LLM_TOOL_IDS", "tool1,tool2,tool3")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path, auto_generate_witness_stub=True)
    
    correlation_id = "test-correlation-456"
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test"),
        ),
        correlation_id=correlation_id,
    )
    
    # Witness stub should be populated
    assert atom.witness.model_id == "test-model-123"
    assert atom.witness.tool_ids == ["tool1", "tool2", "tool3"]
    assert atom.witness.correlation_id == correlation_id
    assert atom.witness.uncertainty_band == "green"
    
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)
    monkeypatch.delenv("LLM_TOOL_IDS", raising=False)


def test_witness_stub_auto_generation_with_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that witness stub uses snapshot ID when available"""
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    monkeypatch.setenv("LLM_MODEL_ID", "test-model-789")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path, auto_generate_witness_stub=True)
    
    # Create a snapshot first
    snapshot = store.create_snapshot(note="test snapshot")
    
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test"),
        )
    )
    
    # Witness stub should use the snapshot ID
    assert atom.witness.model_id == "test-model-789"
    assert atom.witness.snapshot_id == snapshot.id
    
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)


def test_witness_stub_auto_generation_override_per_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that auto_generate_witness parameter can override instance setting"""
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    monkeypatch.setenv("LLM_MODEL_ID", "test-model-override")
    store_path = tmp_path / "cmc"
    
    # Store with auto-generation disabled
    store = MemoryStore(store_path, auto_generate_witness_stub=False)
    
    # Override to enable for this call
    atom1 = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test 1"),
        ),
        auto_generate_witness=True,
    )
    assert atom1.witness.model_id == "test-model-override"
    
    # Override to disable for this call (even though instance default is False)
    atom2 = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test 2"),
        ),
        auto_generate_witness=False,
    )
    assert atom2.witness.model_id is None
    
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)


def test_witness_stub_auto_generation_with_context_snapshot_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that context_snapshot_id parameter is used when provided"""
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    monkeypatch.setenv("LLM_MODEL_ID", "test-model-context")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path, auto_generate_witness_stub=True)
    
    # Create a snapshot
    snapshot = store.create_snapshot(note="context snapshot")
    
    # Provide explicit context_snapshot_id
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test"),
        ),
        context_snapshot_id=snapshot.id,
    )
    
    # Witness stub should use the provided snapshot ID
    assert atom.witness.snapshot_id == snapshot.id
    
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)


def test_witness_stub_model_id_caching(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that model ID is cached to avoid repeated env lookups"""
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    monkeypatch.setenv("LLM_MODEL_ID", "cached-model")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path, auto_generate_witness_stub=True)
    
    # Create multiple atoms
    atom1 = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test 1"),
        )
    )
    
    # Change env var (should not affect cached value)
    monkeypatch.setenv("LLM_MODEL_ID", "new-model")
    
    atom2 = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Test 2"),
        )
    )
    
    # Both should use cached value
    assert atom1.witness.model_id == "cached-model"
    assert atom2.witness.model_id == "cached-model"
    
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)


def test_journal_corruption_triggers_quarantine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMC_BACKEND", "jsonl")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    atom = store.create_atom(
        AtomCreate(modality="text", content=AtomContent(inline="corrupt"))
    )
    store.create_snapshot()
    store.close()

    atoms_log = store_path / "atoms.log"
    data = atoms_log.read_bytes()
    atoms_log.write_bytes(data[:-1])

    with pytest.raises(JournalCorruptionError):
        MemoryStore(store_path)
    monkeypatch.delenv("CMC_BACKEND", raising=False)


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
