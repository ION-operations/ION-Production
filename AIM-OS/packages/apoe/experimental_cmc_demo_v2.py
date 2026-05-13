"""Demo script for experimental APOE→CMC integration v2.

This is a self-contained example that exercises `CMCPlanStoreV2` and
`MemoryAwareExecutorV2` from `experimental_cmc_integration_v2` without touching
the production `cmc_integration.py` module or tests.

Run (from repo root):

    python -m packages.apoe.experimental_cmc_demo_v2

It will:
  - create an in-memory CMCPlanStoreV2 (no real CMC client)
  - execute a few mock plans
  - print history and aggregated statistics
  - print the exact payload shape that would be sent to CMC
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from .experimental_cmc_integration_v2 import (
    CMCPlanStoreV2,
    MemoryAwareExecutorV2,
    PlanMemoryV2,
)


class MockCMCClient:
    """Simple mock CMC client that captures create_atom payloads in-memory."""

    def __init__(self) -> None:
        self.calls = []

    def create_atom(self, *args: Any, **kwargs: Any) -> None:
        # We support both payload=AtomCreate(...) and legacy kwargs
        if "payload" in kwargs:
            payload = kwargs["payload"]
            record: Dict[str, Any] = {
                "modality": getattr(payload, "modality", None),
                "tags": getattr(payload, "tags", None),
                "metadata": getattr(payload, "metadata", None),
                "content": getattr(getattr(payload, "content", None), "inline", None),
            }
        else:
            record = {
                "modality": kwargs.get("modality"),
                "tags": kwargs.get("tags"),
                "metadata": kwargs.get("metadata"),
                "content": kwargs.get("content"),
            }
        self.calls.append(record)


def _print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    mock_cmc = MockCMCClient()
    store = CMCPlanStoreV2(cmc_client=mock_cmc)
    executor = MemoryAwareExecutorV2(plan_store=store)

    class MockPlan:
        def __init__(self, steps: int) -> None:
            self.steps = list(range(steps))

    # Execute a few runs for the same plan
    for i in range(3):
        executor.execute_with_memory(plan_name="demo_plan", plan=MockPlan(steps=3), execution_id=f"exec_{i:03d}")

    # Mark a partial run with an error
    store.store_plan_start("demo_plan", "exec_partial", total_steps=5, metadata={"origin": "demo"})
    store.update_plan_progress("exec_partial", steps_completed=2, current_outputs={"partial": True})
    store.record_error("exec_partial", message="network timeout")
    store.store_plan_partial("exec_partial", partial_outputs={"note": "will retry later"})

    # Show history
    _print_header("History for demo_plan (newest first)")
    history = store.retrieve_plan_history("demo_plan", limit=10)
    for mem in history:
        print(f"- {mem.execution_id} | status={mem.status} | steps={mem.steps_completed}/{mem.total_steps} | "
              f"started_at={mem.started_at.isoformat()} | completed_at={mem.completed_at}")

    # Show stats
    stats = store.get_plan_statistics("demo_plan")
    _print_header("Aggregated stats for demo_plan")
    print(asdict(stats))

    # Show last CMC payload
    _print_header("Example CMC payload (last call)")
    if mock_cmc.calls:
        last = mock_cmc.calls[-1]
        print("modality:", last["modality"])
        print("tags:", last["tags"])
        print("metadata keys:", sorted(last["metadata"].keys()) if isinstance(last["metadata"], dict) else None)
        print("content (truncated):", (last["content"] or "")[:200])
    else:
        print("No CMC calls recorded (CMC client not configured).")


if __name__ == "__main__":
    main()


