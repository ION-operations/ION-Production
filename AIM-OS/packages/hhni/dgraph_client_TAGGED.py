"""DGraph GraphQL client wrapper for HHNI."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from time import sleep
from typing import Iterable, Optional

import requests

from .safety import HHNIQueryGates

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5
MAX_RETRIES = 3
BACKOFF_SECONDS = 0.5


@dataclass
# NL_TAG: VIF-CLIENT-001 | Dgraphclient | class DGraphClient | []
class DGraphClient:
    host: str = "http://localhost:8080"
    graphql_endpoint: str = "/graphql"

    # NL_TAG: VIF-CLIENT-002 |  url | _url(self) | []
    def _url(self) -> str:
        return f"{self.host.rstrip('/')}{self.graphql_endpoint}"

    # NL_TAG: VIF-CLIENT-003 | Upsert nodes | upsert_nodes(self, nodes) | []
    def upsert_nodes(self, nodes: Iterable[dict]) -> None:
        payload = {
            "query": "mutation($input: [AddHHNINodeInput!]!) { addHHNINode(input: $input) { numUids } }",
            "variables": {"input": list(nodes)},
        }
        self._post(payload, action="hhni.upsert")

    # NL_TAG: VIF-CLIENT-004 | Query | query(self, query, variables) | []
    def query(self, query: str, variables: Optional[dict] = None, *, first: Optional[int] = None) -> dict:
        safe_query = HHNIQueryGates.apply_limits(query, first=first)
        payload = {"query": safe_query, "variables": variables or {}}
        response = self._post(payload, action="hhni.query")
        return response.get("data", {})

    # NL_TAG: VIF-CLIENT-005 | Health | health(self) | []
    def health(self) -> dict:
        try:
            response = requests.get(f"{self.host.rstrip('/')}/health?all", timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network call
            logger.error("hhni.dgraph.health_failed", extra={"error": str(exc)})
            return {"status": "unhealthy", "error": str(exc)}

    # NL_TAG: VIF-CLIENT-006 |  post | _post(self, payload) | []
    def _post(self, payload: dict, *, action: str) -> dict:
        url = self._url()
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                if "errors" in data:
                    raise RuntimeError(json.dumps(data["errors"]))
                return data
            except (requests.RequestException, json.JSONDecodeError, RuntimeError) as exc:
                logger.warning(
                    "hhni.dgraph.request_failed",
                    extra={
                        "action": action,
                        "attempt": attempt,
                        "error": str(exc),
                        "payload_size": len(json.dumps(payload)) if payload else 0,
                    },
                )
                if attempt == MAX_RETRIES:
                    logger.error(
                        "hhni.dgraph.request_aborted",
                        extra={"action": action, "error": str(exc)},
                    )
                    raise
                sleep(BACKOFF_SECONDS * attempt)
        return {}
