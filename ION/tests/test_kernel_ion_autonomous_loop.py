import json
from pathlib import Path

from kernel.ion_autonomous_loop import run_autonomous_loop


def test_autonomous_loop_no_work_exits_zero(tmp_path: Path) -> None:
    from unittest.mock import patch

    from kernel.ion_autonomous_loop import main

    (tmp_path / "ION" / "REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION" / "REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")

    no_work = {
        "schema_id": "ion.autonomous_loop_result.v1",
        "status": "BLOCKED",
        "stop_reason": "NO_ACCEPTED_LOCAL_DELTA",
        "steps_integrated": 0,
    }
    with patch("kernel.ion_autonomous_loop.run_autonomous_loop", return_value=no_work):
        assert main(["--ion-root", str(tmp_path), "--goal", "test"]) == 0


def test_autonomous_loop_survival_slice_writes_state(tmp_path: Path) -> None:
    (tmp_path / "ION" / "05_context" / "current" / "agent_context_systems").mkdir(parents=True)
    (tmp_path / "ION" / "REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION" / "REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")

    result = run_autonomous_loop(
        ion_root=tmp_path,
        goal="Find one contradiction and propose one patch",
        max_steps=3,
        write=True,
    )
    assert result["status"] == "PASS"
    assert result["steps_integrated"] == 1
    assert (tmp_path / "ION/05_context/current/LAST_ION_AUTONOMOUS_LOOP_RESULT.json").exists()
    assert (tmp_path / "ION/05_context/current/ACTIVE_COCKPIT_VIEW_MODEL.json").exists()
    lead_dev_context = tmp_path / "ION/05_context/current/agent_context_systems/LEAD_DEV_ACTIVE_CONTEXT_PACKAGE_V101.md"
    assert lead_dev_context.exists()
    cockpit = json.loads(
        (tmp_path / "ION/05_context/current/ACTIVE_COCKPIT_VIEW_MODEL.json").read_text(encoding="utf-8")
    )
    assert cockpit["active_line"] == "V103_TEMPORAL_CONTEXT_ENFORCEMENT_RECONCILIATION"
    assert cockpit["context_lifecycle_verdict"] in {"PASS_WITH_LIFECYCLE_MODEL", "REVIEW_REQUIRED"}


def test_autonomous_loop_honors_max_steps_when_integration_rejects(tmp_path: Path) -> None:
    from unittest.mock import patch

    (tmp_path / "ION" / "REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION" / "REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")

    def _reject(**_kwargs: object) -> dict[str, object]:
        return {"accepted": False, "findings": ["rejected_for_test"]}

    with patch("kernel.ion_autonomous_loop.steward_integrate_return", side_effect=_reject):
        result = run_autonomous_loop(
            ion_root=tmp_path,
            goal="max steps probe",
            max_steps=4,
            write=False,
        )
    assert result["steps_attempted"] == 4
    assert result["steps_integrated"] == 0
    assert result["max_steps"] == 4
    assert result["stop_reason"] == "NO_ACCEPTED_LOCAL_DELTA"


def test_autonomous_loop_idle_streak_emits_absence_alert(tmp_path: Path) -> None:
    from unittest.mock import patch

    from kernel.ion_autonomous_loop import IDLE_ABSENCE_ALERT_THRESHOLD, update_loop_idle_streak

    (tmp_path / "ION" / "REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION" / "REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")

    def _reject(**_kwargs: object) -> dict[str, object]:
        return {"accepted": False}

    with patch("kernel.ion_autonomous_loop.steward_integrate_return", side_effect=_reject):
        for i in range(IDLE_ABSENCE_ALERT_THRESHOLD):
            result = run_autonomous_loop(
                ion_root=tmp_path,
                goal=f"idle streak probe {i}",
                max_steps=1,
                write=True,
            )
    assert result["stop_reason"] == "NO_ACCEPTED_LOCAL_DELTA"
    assert result["idle_streak"]["consecutive_idle_cycles"] == IDLE_ABSENCE_ALERT_THRESHOLD
    assert result["idle_streak"]["absence_alert_active"] is True
    assert result.get("loop_absence_findings")
    alert_path = tmp_path / "ION/05_context/current/autonomous_loop/LOOP_IDLE_ABSENCE_ALERT.candidate.json"
    assert alert_path.is_file()
    alert = json.loads(alert_path.read_text(encoding="utf-8"))
    assert alert["finding_code"] == "FINDING_AUTONOMOUS_LOOP_CONSECUTIVE_IDLE_CYCLES"

    update_loop_idle_streak(
        tmp_path,
        cycle_id="reset_cycle",
        integrated=1,
        stop_reason="LOCAL_SURVIVAL_SLICE_ACCEPTED_FIRST_DELTA",
        write=True,
        created_at="2026-08-08T12:00:00+00:00",
    )
    streak_path = tmp_path / "ION/05_context/current/autonomous_loop/LOOP_IDLE_STREAK.candidate.json"
    streak = json.loads(streak_path.read_text(encoding="utf-8"))
    assert streak["consecutive_idle_cycles"] == 0
