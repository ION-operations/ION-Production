from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from jarvis_injector.core.models import DispatchResult, ExecutionRecord


class ExecutionTelemetry:
    def __init__(self, jsonl_path: Path, sqlite_path: Path) -> None:
        self._jsonl_path = jsonl_path
        self._sqlite_path = sqlite_path
        self._jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self._sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._sqlite_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    execution_id TEXT PRIMARY KEY,
                    target_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    adapter_used TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    error TEXT
                )
                """
            )

    def record_execution(self, record: ExecutionRecord) -> None:
        payload = record.model_dump(mode="json")
        with self._jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")

        result = record.result
        with sqlite3.connect(self._sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO episodes (execution_id, target_id, state, adapter_used, created_at, completed_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(execution_id) DO UPDATE SET
                    target_id = excluded.target_id,
                    state = excluded.state,
                    adapter_used = excluded.adapter_used,
                    completed_at = excluded.completed_at,
                    error = excluded.error
                """,
                (
                    record.execution_id,
                    record.request.target_id,
                    record.state.value,
                    result.adapter_used.value if result and result.adapter_used else None,
                    record.created_at.isoformat(),
                    result.completed_at.isoformat() if result else None,
                    result.error if result else None,
                ),
            )

    def summarize_last_runs(self, limit: int = 20) -> list[dict[str, str | None]]:
        with sqlite3.connect(self._sqlite_path) as connection:
            cursor = connection.execute(
                """
                SELECT execution_id, target_id, state, adapter_used, created_at, completed_at, error
                FROM episodes
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()

        return [
            {
                "executionId": row[0],
                "targetId": row[1],
                "state": row[2],
                "adapterUsed": row[3],
                "createdAt": row[4],
                "completedAt": row[5],
                "error": row[6],
            }
            for row in rows
        ]

