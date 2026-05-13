import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import shadow_bci_v1_emitter as emitter  # noqa: E402


class ShadowBciStrictSchemaProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = ROOT / "fixtures" / "extracted_file_fixture_v0.json"
        self.strict_schema_path = ROOT / "shadow_bci_v1_strict_schema.json"

    def test_emitter_output_validates_against_strict_profile(self) -> None:
        fixture = emitter.read_json(self.fixture_path)
        records = emitter.emit_records_from_fixture(fixture)
        ok, errors = emitter.validate_records(records, self.strict_schema_path)
        self.assertTrue(ok, msg="\n".join(errors))

    def test_strict_profile_catches_missing_boundary_view_level(self) -> None:
        fixture = emitter.read_json(self.fixture_path)
        records = emitter.emit_records_from_fixture(fixture)
        boundary_view = next(r for r in records if r.get("record_type") == "bci_boundary_view")
        boundary_view.pop("view_level", None)
        ok, errors = emitter.validate_records(records, self.strict_schema_path)
        self.assertFalse(ok)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
