import unittest

from ide_orchestration.orchestrator.progress_tracker import ProgressTracker
from ide_orchestration.orchestrator.graph_manager import GraphManager


class DummyManager(GraphManager):
    """Wrap GraphManager loading from fixture ChainSpec to avoid file IO?"""


class ProgressTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = GraphManager("ide_orchestration/chains/ChainSpec.yaml")
        self.tracker = ProgressTracker(self.manager)

    def test_phase_progress_returns_entries(self) -> None:
        completed = {"task_cursor_landscape"}
        result = self.tracker.phase_progress(completed)
        self.assertTrue(result)
        research_phase = next(r for r in result if r.phase_id == "research_phase")
        self.assertGreaterEqual(research_phase.total, 1)

    def test_predictive_metrics_shape(self) -> None:
        completed = {"task_cursor_landscape", "task_codex_capabilities"}
        metrics = self.tracker.predictive_metrics(completed, {"research_phase": 2.0})
        self.assertIn("research_phase", metrics)
        self.assertIn("eta_days", metrics["research_phase"])


if __name__ == "__main__":
    unittest.main()
