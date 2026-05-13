import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import shadow_bci_v1_emitter as emitter  # noqa: E402


class ShadowBciEmitterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = ROOT / "fixtures" / "extracted_file_fixture_v0.json"
        self.schema_path = ROOT / "shadow_bci_v1_schema.json"
        self.out_dir = ROOT / "out"

    def test_fixture_loads_expected_shape(self) -> None:
        fixture = emitter.read_json(self.fixture_path)
        emitter.ensure_required_fixture_fields(fixture)
        self.assertIn("source_path", fixture)
        self.assertIsInstance(fixture["imports"], list)
        self.assertIsInstance(fixture["contracts"], list)

    def test_emission_contains_required_record_types_and_views(self) -> None:
        result = emitter.run_prototype(
            fixture_path=self.fixture_path,
            schema_path=self.schema_path,
            out_dir=self.out_dir,
            write_output=False,
        )
        summary = result["summary"]
        self.assertIn("bci_atom", summary["record_types"])
        self.assertIn("bci_boundary_view", summary["record_types"])
        self.assertIn("L0", summary["view_levels"])
        self.assertIn("L5", summary["view_levels"])
        self.assertGreater(summary["atom_count"], 0)
        self.assertGreaterEqual(summary["boundary_view_count"], 2)

    def test_schema_validation_catches_invalid_record(self) -> None:
        fixture = emitter.read_json(self.fixture_path)
        records = emitter.emit_records_from_fixture(fixture)
        records[0]["record_type"] = "not_valid"
        is_valid, errors = emitter.validate_records(records, self.schema_path)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
