from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Optional, Protocol, Set

logger = logging.getLogger(__name__)


class CMCClient(Protocol):
	"""Protocol for a minimal CMC client the poller can use."""

	def list_atoms(
		self,
		*,
		tag: Optional[str] = None,
		modality_allowlist: Optional[Iterable[str]] = None,
		since_iso: Optional[str] = None,
		limit: int = 200,
	) -> Iterable[object]:
		...


class HHNIIndexer(Protocol):
	"""Protocol for invoking HHNI indexing."""

	def build_hhni_for_atom(self, *, atom: object, dgraph_client: object, qdrant_client: object) -> object:
		...


@dataclass
class CMCNotificationHandlerConfig:
	tag: str = "hhni_index"
	modality_allowlist: Set[str] = field(
		default_factory=lambda: {
			"text",
			"tcs_timeline",
			"plan_execution",
			"cas_introspection_analysis",
			"witness",
			"evidence",
		}
	)
	page_size: int = 200
	backoff_empty_seconds: float = 2.0
	backoff_backlog_seconds: float = 0.2
	dead_letter_log_path: Optional[str] = None  # JSONL file if provided


class CMCNotificationHandler:
	"""Poll CMC for atoms to index into HHNI with at-least-once, idempotent semantics."""

	def __init__(
		self,
		*,
		cmc_client: CMCClient,
		index_fn: Callable[..., object],
		dgraph_client: object,
		qdrant_client: object,
		config: Optional[CMCNotificationHandlerConfig] = None,
	) -> None:
		self.cmc_client = cmc_client
		self.index_fn = index_fn
		self.dgraph_client = dgraph_client
		self.qdrant_client = qdrant_client
		self.config = config or CMCNotificationHandlerConfig()
		self._indexed_ids: Set[str] = set()
		self._last_seen_iso: Optional[str] = None

	def is_indexed(self, atom_id: str) -> bool:
		return atom_id in self._indexed_ids

	def _record_dead_letter(self, atom: object, error: Exception) -> None:
		if not self.config.dead_letter_log_path:
			logger.warning("hhni.cmc_poller.dead_letter", extra={"atom_id": getattr(atom, "id", None), "error": str(error)})
			return
		try:
			with open(self.config.dead_letter_log_path, "a", encoding="utf-8") as f:
				entry = {
					"atom_id": getattr(atom, "id", None),
					"error": str(error),
				}
				f.write(json.dumps(entry) + "\n")
		except Exception as write_err:
			logger.error("hhni.cmc_poller.dead_letter_write_failed", extra={"error": str(write_err)})

	def run_once(self) -> int:
		"""Poll once and index any new atoms. Returns number of attempted indexes."""
		atoms = list(
			self.cmc_client.list_atoms(
				tag=self.config.tag,
				modality_allowlist=self.config.modality_allowlist,
				since_iso=self._last_seen_iso,
				limit=self.config.page_size,
			)
		)
		count = 0
		for atom in atoms:
			atom_id = getattr(atom, "id", None)
			if not atom_id:
				continue
			# Track max created_at as simple watermark if available
			created_at_val = getattr(atom, "created_at", None)
			created_iso: Optional[str] = None
			if isinstance(created_at_val, str):
				created_iso = created_at_val
			else:
				iso_attr = getattr(atom, "created_at_iso", None)
				if isinstance(iso_attr, str):
					created_iso = iso_attr
				else:
					try:
						created_iso = created_at_val.isoformat() if created_at_val is not None else None
					except Exception:
						created_iso = None
			if created_iso:
				self._last_seen_iso = max(self._last_seen_iso or "", created_iso) or created_iso
			if self.is_indexed(atom_id):
				continue
			try:
				self.index_fn(atom=atom, dgraph_client=self.dgraph_client, qdrant_client=self.qdrant_client)
				self._indexed_ids.add(atom_id)
				count += 1
			except Exception as exc:
				self._record_dead_letter(atom, exc)
		return count

	def run_forever(self) -> None:
		"""Simple loop with backoff suitable for a background thread/process."""
		while True:
			try:
				n = self.run_once()
				time.sleep(self.config.backoff_backlog_seconds if n > 0 else self.config.backoff_empty_seconds)
			except Exception as exc:  # pragma: no cover - safety loop
				logger.error("hhni.cmc_poller.loop_error", extra={"error": str(exc)})
				time.sleep(self.config.backoff_empty_seconds)


