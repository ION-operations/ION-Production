import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import passive_hook_simulation_v0_3 as sim  # noqa: E402


class PassiveHookSimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = sim.read_json(ROOT / "fixtures" / "live_mapper_snapshot_v0_1.json")
        self.schema = ROOT / "shadow_bci_v1_strict_schema.json"
        self.expected_live = sim.simulate_live_response(self.snapshot)

    def test_shadow_disabled_returns_identical_live_response(self) -> None:
        result = sim.run_passive_hook(
            self.snapshot, shadow_enabled=False, schema_path=self.schema
        )
        self.assertEqual(result["live_response"], self.expected_live)
        self.assertFalse(result["shadow_observation"]["attempted"])
        self.assertFalse(result["shadow_observation"]["success"])

    def test_shadow_enabled_success_keeps_live_response(self) -> None:
        result = sim.run_passive_hook(
            self.snapshot, shadow_enabled=True, schema_path=self.schema
        )
        self.assertEqual(result["live_response"], self.expected_live)
        self.assertTrue(result["shadow_observation"]["attempted"])
        self.assertTrue(result["shadow_observation"]["success"])
        self.assertGreater(result["shadow_observation"]["record_count"], 0)

    def test_shadow_failure_is_fail_open(self) -> None:
        result = sim.run_passive_hook(
            self.snapshot,
            shadow_enabled=True,
            schema_path=self.schema,
            inject_shadow_failure=True,
        )
        self.assertEqual(result["live_response"], self.expected_live)
        self.assertTrue(result["shadow_observation"]["attempted"])
        self.assertFalse(result["shadow_observation"]["success"])
        self.assertIn("Injected shadow failure", result["shadow_observation"]["error"])


if __name__ == "__main__":
    unittest.main()
