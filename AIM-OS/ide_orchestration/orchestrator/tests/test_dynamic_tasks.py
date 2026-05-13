import tempfile
import textwrap
import unittest
from pathlib import Path

from ide_orchestration.orchestrator.dynamic_task_generator import (
    DynamicTaskGenerator,
)


RULES_FIXTURE = """
version: 1
rules:
  - id: rule_positive_signal
    conditions:
      - path: signals.value
        operator: gt
        value: 0
    task:
      id: task_positive_followup
      description: "Triggered when signal is positive"
      phase: test_phase
      workstream: ws_dynamic_tasking
      ai_modes: ["ide"]
      gate_refs: ["task.spec_integrity"]
  - id: rule_missing_signal
    conditions:
      - path: signals.value
        operator: exists
    task:
      id: task_exists_followup
      description: "Triggered when signal exists"
      phase: test_phase
      workstream: ws_dynamic_tasking
"""


class DynamicTaskGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.rules_path = Path(self.tmpdir.name) / "rules.yaml"
        self.rules_path.write_text(textwrap.dedent(RULES_FIXTURE), encoding="utf-8")
        self.generator = DynamicTaskGenerator(rules_path=self.rules_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_list_rule_ids(self) -> None:
        self.assertEqual(
            self.generator.list_rule_ids(), ["rule_positive_signal", "rule_missing_signal"]
        )

    def test_generate_tasks_matches_conditions(self) -> None:
        context = {"signals": {"value": 10}}
        tasks = self.generator.generate_tasks(context)
        self.assertEqual(len(tasks), 2)
        ids = {task.id for task in tasks}
        self.assertIn("task_positive_followup", ids)
        self.assertIn("task_exists_followup", ids)

    def test_generate_tasks_respects_exclusions_and_conditions(self) -> None:
        context = {"signals": {"value": -1}}
        tasks = self.generator.generate_tasks(context, exclude_tasks=["rule_missing_signal"])
        self.assertEqual(len(tasks), 0)


if __name__ == "__main__":
    unittest.main()
