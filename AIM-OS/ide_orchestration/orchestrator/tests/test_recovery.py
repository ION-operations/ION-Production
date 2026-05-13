import tempfile
import unittest
from pathlib import Path

from ide_orchestration.orchestrator.recovery import RecoveryEngine


class RecoveryEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        checkpoint_dir = Path(self.tmpdir.name, "checkpoints")
        telemetry_log = Path(self.tmpdir.name, "telemetry.log")
        self.engine = RecoveryEngine(
            checkpoint_dir=checkpoint_dir, telemetry_log=telemetry_log
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_checkpoint_and_list(self) -> None:
        cp = self.engine.checkpoint("cp1", {"task_a", "task_b"}, notes="first")
        self.assertTrue(cp.path.exists())
        checkpoints = self.engine.available_checkpoints()
        self.assertEqual(len(checkpoints), 1)
        self.assertEqual(checkpoints[0].name, "cp1")

    def test_load_and_rollback(self) -> None:
        self.engine.checkpoint("cp2", {"task_x"})
        restored = self.engine.rollback("cp2", {"task_z"})
        self.assertIsNotNone(restored)
        self.assertEqual(restored.completed_tasks, {"task_x"})

    def test_missing_checkpoint_returns_none(self) -> None:
        self.assertIsNone(self.engine.rollback("missing", set()))


if __name__ == "__main__":
    unittest.main()
