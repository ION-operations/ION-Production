"""Persistence adapters.

The local sample uses JsonFileStore. MongoAtlasStore is a target adapter for
Cloud Run / MongoDB Atlas. It is intentionally fail-closed when credentials are
absent.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import os


class JsonFileStore:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, payload: Any) -> Path:
        path = self.output_dir / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def read_json(self, name: str) -> Any:
        return json.loads((self.output_dir / name).read_text(encoding="utf-8"))


class MongoAtlasStore:
    def __init__(self, uri: str | None = None, db_name: str | None = None):
        self.uri = uri or os.getenv("MONGODB_URI")
        self.db_name = db_name or os.getenv("MONGODB_DB", "ion_continuity_bridge")
        if not self.uri:
            raise RuntimeError("MONGODB_URI is required for MongoAtlasStore")
        try:
            from pymongo import MongoClient  # type: ignore
        except Exception as exc:
            raise RuntimeError("pymongo is required for MongoAtlasStore") from exc
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def insert_many(self, collection: str, docs: List[Dict[str, Any]]) -> List[str]:
        if not docs:
            return []
        result = self.db[collection].insert_many(docs)
        return [str(x) for x in result.inserted_ids]

    def insert_one(self, collection: str, doc: Dict[str, Any]) -> str:
        result = self.db[collection].insert_one(doc)
        return str(result.inserted_id)

    def find(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return list(self.db[collection].find(query, {"_id": 0}))
