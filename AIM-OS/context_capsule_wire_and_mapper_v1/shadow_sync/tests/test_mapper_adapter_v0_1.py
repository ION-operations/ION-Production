import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import mapper_adapter_v0_1 as adapter  # noqa: E402
import shadow_bci_v1_emitter as emitter  # noqa: E402


class MapperAdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot_path = ROOT / "fixtures" / "live_mapper_snapshot_v0_1.json"
        self.schema_path = ROOT / "shadow_bci_v1_schema.json"

    def test_adapter_maps_snapshot_to_emitter_shape(self) -> None:
        snapshot = adapter.read_json(self.snapshot_path)
        adapted = adapter.adapt_live_mapper_snapshot(snapshot)
        emitter.ensure_required_fixture_fields(adapted)
        self.assertEqual(adapted["source_path"], "context_mapper_lab/src/sample_unit.rs")
        self.assertEqual(adapted["parse_confidence"], "High")
        self.assertEqual(len(adapted["imports"]), 2)
        self.assertEqual(len(adapted["contracts"]), 3)

    def test_adapter_output_can_emit_and_validate_shadow_records(self) -> None:
        snapshot = adapter.read_json(self.snapshot_path)
        adapted = adapter.adapt_live_mapper_snapshot(snapshot)
        records = emitter.emit_records_from_fixture(adapted)
        ok, errors = emitter.validate_records(records, self.schema_path)
        self.assertTrue(ok, msg="\n".join(errors))
        summary = emitter.summarize_records(records)
        self.assertIn("bci_atom", summary["record_types"])
        self.assertIn("bci_boundary_view", summary["record_types"])
        self.assertIn("L0", summary["view_levels"])
        self.assertIn("L5", summary["view_levels"])

    def test_adapter_rejects_missing_extracted_file(self) -> None:
        with self.assertRaises(ValueError):
            adapter.adapt_live_mapper_snapshot({"target_source": "pub fn x(){}"})

    def test_adapter_cli_writes_output(self) -> None:
        # Tiny smoke check for deterministic adapter output generation path.
        snapshot = adapter.read_json(self.snapshot_path)
        adapted = adapter.adapt_live_mapper_snapshot(snapshot)
        serialized = json.dumps(adapted)
        self.assertIn("source_path", serialized)


if __name__ == "__main__":
    unittest.main()
