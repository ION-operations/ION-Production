from __future__ import annotations

from typing import Iterable, Optional

import pytest

from hhni.cmc_poller import CMCNotificationHandler, CMCNotificationHandlerConfig
from hhni import indexer as hhni_indexer


class _DummyAtom:
	def __init__(self, atom_id: str, created_at_iso: str, inline: str = "x", tags=None) -> None:
		self.id = atom_id
		# provide both ISO string and datetime variants to satisfy poller + indexer
		from datetime import datetime, timezone
		self.created_at_iso = created_at_iso
		self.created_at = datetime.now(timezone.utc)
		self.tags = tags or {"hhni_index": True}
		# minimal shape for indexer.build_hhni_for_atom
		self.content = type("Content", (), {"inline": inline, "uri": None, "media_type": "text/plain"})
		self.hash = "h"
		self.witness = type("Witness", (), {"snapshot_id": "snap"})
		self.created_at_dt = self.created_at


class _DummyCMC:
	def __init__(self, atoms: list[_DummyAtom]) -> None:
		self._atoms = atoms

	def list_atoms(
		self,
		*,
		tag: Optional[str] = None,
		modality_allowlist: Optional[Iterable[str]] = None,
		since_iso: Optional[str] = None,
		limit: int = 200,
	) -> Iterable[_DummyAtom]:
		# ignore modality in this dummy; filter by tag presence and since_iso
		def _ok(a: _DummyAtom) -> bool:
			if tag and not a.tags.get(tag, False):
				return False
			if since_iso and isinstance(a.created_at, str) and a.created_at <= since_iso:
				return False
			return True
		return [a for a in self._atoms if _ok(a)][:limit]


class _DummyDG:
	def __init__(self) -> None:
		self.upserts = []
	def upsert_nodes(self, nodes):
		self.upserts.append(nodes)


class _DummyQd:
	def upsert(self, collection_name, points):
		return {"ok": True}


def test_poller_indexes_new_atoms_idempotently(monkeypatch: pytest.MonkeyPatch):
	# Prepare two atoms; second one duplicates id
	atoms = [
		_DummyAtom("a1", "2025-01-27T10:00:00Z", inline="Hello"),
		_DummyAtom("a1", "2025-01-27T10:00:01Z", inline="Hello updated"),  # same id => idempotent skip after first
		_DummyAtom("a2", "2025-01-27T10:00:02Z", inline="World"),
	]
	cmc = _DummyCMC(atoms)
	dg = _DummyDG()
	qd = _DummyQd()

	handler = CMCNotificationHandler(
		cmc_client=cmc,
		index_fn=hhni_indexer.build_hhni_for_atom,
		dgraph_client=dg,
		qdrant_client=qd,
		config=CMCNotificationHandlerConfig(),
	)

	attempts_1 = handler.run_once()
	assert attempts_1 == 2  # a1, a2
	assert handler.is_indexed("a1") and handler.is_indexed("a2")

	# Run again → no new indexes (idempotent)
	attempts_2 = handler.run_once()
	assert attempts_2 == 0


def test_dead_letter_on_index_error(tmp_path):
	bad_atom = _DummyAtom("bad", "2025-01-27T11:00:00Z", inline=None)  # inline None causes early return path
	cmc = _DummyCMC([bad_atom])
	dg = _DummyDG()
	qd = _DummyQd()

	def _boom(**kwargs):
		raise RuntimeError("oops")

	log_path = tmp_path / "dlq.jsonl"
	handler = CMCNotificationHandler(
		cmc_client=cmc,
		index_fn=_boom,
		dgraph_client=dg,
		qdrant_client=qd,
		config=CMCNotificationHandlerConfig(dead_letter_log_path=str(log_path)),
	)
	attempts = handler.run_once()
	assert attempts == 0
	data = log_path.read_text(encoding="utf-8").strip()
	assert "bad" in data and "oops" in data


