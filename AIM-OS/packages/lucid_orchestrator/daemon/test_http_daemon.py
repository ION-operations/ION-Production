#!/usr/bin/env python3
"""Regression coverage for the HTTP daemon telemetry endpoints."""

import unittest
from pathlib import Path

from packages.lucid_orchestrator.daemon import http_daemon


class TelemetryEndpointTests(unittest.TestCase):
    """Validate live telemetry routes and their fallback behavior."""

    def setUp(self):
        self.client = http_daemon.app.test_client()

    def test_progress_endpoint_serves_snapshot_file(self):
        """Happy-path call should yield whatever is in the JSON artifact."""
        response = self.client.get("/api/telemetry/progress")
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertIn("phases", payload)
        self.assertTrue(payload["phases"])  # snapshot should list at least one phase

    def test_progress_endpoint_uses_builtin_fallback(self):
        """If the snapshot is missing, the daemon must serve the baked-in data."""
        original_path = http_daemon.TELEMETRY_PROGRESS_PATH
        http_daemon.TELEMETRY_PROGRESS_PATH = Path("nonexistent_progress_snapshot.json")
        try:
            response = self.client.get("/api/telemetry/progress")
            self.assertEqual(response.status_code, 200)

            payload = response.get_json()
            self.assertEqual(
                payload["notes"],
                http_daemon.DEFAULT_PROGRESS_SNAPSHOT["notes"],
            )
        finally:
            http_daemon.TELEMETRY_PROGRESS_PATH = original_path

    def test_confidence_endpoint_serves_snapshot_file(self):
        """Happy-path call should surface the authored confidence tiers."""
        response = self.client.get("/api/telemetry/confidence-routing")
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertIn("tiers", payload)
        # The checked-in snapshot has six tiers; keep the assertion loose but non-zero.
        self.assertGreaterEqual(len(payload["tiers"]), 3)

    def test_confidence_endpoint_uses_builtin_fallback(self):
        """Missing snapshot should force the tier list back to the defaults."""
        original_path = http_daemon.CONFIDENCE_SNAPSHOT_PATH
        http_daemon.CONFIDENCE_SNAPSHOT_PATH = Path("nonexistent_confidence_snapshot.json")
        try:
            response = self.client.get("/api/telemetry/confidence-routing")
            self.assertEqual(response.status_code, 200)

            payload = response.get_json()
            self.assertEqual(
                len(payload["tiers"]),
                len(http_daemon.DEFAULT_CONFIDENCE_SNAPSHOT["tiers"]),
            )
        finally:
            http_daemon.CONFIDENCE_SNAPSHOT_PATH = original_path


if __name__ == "__main__":
    unittest.main()
