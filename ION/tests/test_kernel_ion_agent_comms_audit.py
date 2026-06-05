import json
from pathlib import Path

from kernel.ion_agent_comms_audit import audit_agent_comms_chain
from kernel.ion_agent_comms_audit_actions import maybe_audit_agent_comms_result
from kernel.ion_agent_comms_audit_gate import audit_gate_for_run
from kernel.ion_agent_comms_directives import extract_agent_comms_directives
from kernel.ion_agent_comms_runs import build_agent_comms_runs_projection


def _write(root: Path, rel: str, value: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _write_json(root: Path, rel: str, value: dict) -> None:
    _write(root, rel, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")


def _seed_pristine_chain(root: Path) -> dict[str, str]:
    _seed_root(root)
    run_id = "agent_run_pristine_chain"
    thread_id = "thread_pristine_chain"
    thread_dir = "ION/05_context/current/agent_comms/threads/thread_pristine_chain/messages"
    root_message_id = "msg_operator_root"
    steward_message_id = "msg_steward_answer"
    ionologist_message_id = "msg_ionologist_answer"
    wp1 = "ION/05_context/current/chatgpt_connector/codex_work_requests/steward.json"
    wp2 = "ION/05_context/current/chatgpt_connector/codex_work_requests/ionologist.json"
    ret1 = "ION/05_context/current/chatgpt_connector/task_returns/steward_return.json"
    ret2 = "ION/05_context/current/chatgpt_connector/task_returns/ionologist_return.json"
    qr1 = "ION/05_context/current/chatgpt_connector/codex_queue_runs/steward/run.json"
    qr2 = "ION/05_context/current/chatgpt_connector/codex_queue_runs/ionologist/run.json"
    run_path = "ION/05_context/current/agent_comms/runs/agent_run_pristine_chain.json"
    steward_body = """Steward calls Ionologist.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "dispatch_mode": "queue_workpack",
  "objective": "Verify the pristine chain.",
  "body": "Return no-followup if clean.",
  "source_refs": ["ION/05_context/current/agent_comms/runs/agent_run_pristine_chain.json"]
}
```
"""
    ionologist_body = """Ionologist verified the chain.

```ion-agent-decision
{
  "schema_id": "ion.agent_comms.followup_decision.v1",
  "decision": "no_followup",
  "reason": "Chain evidence is complete.",
  "evidence_refs": ["ION/05_context/current/agent_comms/runs/agent_run_pristine_chain.json"]
}
```
"""
    root_msg = f"{thread_dir}/001_operator.json"
    steward_msg = f"{thread_dir}/002_steward.json"
    ionologist_msg = f"{thread_dir}/003_ionologist.json"
    _write_json(
        root,
        root_msg,
        {
            "schema_id": "ion.agent_comms.message.v1",
            "message_id": root_message_id,
            "thread_id": thread_id,
            "from_role": "operator",
            "to_roles": ["role.codex_carrier_steward"],
            "message_kind": "task_dispatch",
            "subject": "Pristine chain",
            "body": "Start.",
            "status": "sent",
            "artifact_refs": [wp1],
            "created_at": "2026-05-26T00:00:00+00:00",
        },
    )
    _write_json(
        root,
        steward_msg,
        {
            "schema_id": "ion.agent_comms.message.v1",
            "message_id": steward_message_id,
            "thread_id": thread_id,
            "parent_message_id": root_message_id,
            "from_role": "role.codex_carrier_steward",
            "to_roles": ["role.ionologist"],
            "message_kind": "answer",
            "subject": "Steward return",
            "body": steward_body,
            "status": "sent",
            "artifact_refs": [wp1, ret1, wp2],
            "created_at": "2026-05-26T00:01:00+00:00",
        },
    )
    _write_json(
        root,
        ionologist_msg,
        {
            "schema_id": "ion.agent_comms.message.v1",
            "message_id": ionologist_message_id,
            "thread_id": thread_id,
            "parent_message_id": steward_message_id,
            "from_role": "role.ionologist",
            "to_roles": ["role.codex_carrier_steward"],
            "message_kind": "answer",
            "subject": "Ionologist return",
            "body": ionologist_body,
            "status": "sent",
            "artifact_refs": [wp2, ret2],
            "created_at": "2026-05-26T00:02:00+00:00",
        },
    )
    directive = extract_agent_comms_directives(
        steward_body,
        source_ref=steward_msg,
        source_message_id=steward_message_id,
        from_role="role.codex_carrier_steward",
        scope_id=run_id,
    )["directives"][0]
    _write_json(
        root,
        "ION/05_context/current/agent_comms/automation/DIRECTIVE_LEDGER.json",
        {
            "schema_id": "ion.agent_comms.directive_ledger.v1",
            "processed": {
                directive["directive_id"]: {
                    "directive_id": directive["directive_id"],
                    "agent": "role.ionologist",
                    "workpack_path": wp2,
                    "dispatch_mode": "queue_workpack",
                }
            },
        },
    )
    _write_json(
        root,
        wp1,
        {
            "request_id": "req_steward",
            "agent_role_id": "role.codex_carrier_steward",
            "agent_display_name": "CODEX_CARRIER_STEWARD",
            "status": "RETURN_RECORDED_PROOF_ACCEPTED",
            "latest_return_packet_path": ret1,
            "return_packet_paths": [ret1],
            "codex_queue_runner_runs": [qr1],
        },
    )
    _write_json(
        root,
        wp2,
        {
            "request_id": "req_ionologist",
            "agent_role_id": "role.ionologist",
            "agent_display_name": "IONOLOGIST",
            "status": "RETURN_RECORDED_PROOF_ACCEPTED",
            "latest_return_packet_path": ret2,
            "return_packet_paths": [ret2],
            "codex_queue_runner_runs": [qr2],
        },
    )
    for rel, request_id, workpack, body in [
        (ret1, "req_steward", wp1, steward_body),
        (ret2, "req_ionologist", wp2, ionologist_body),
    ]:
        _write_json(
            root,
            rel,
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-26T00:03:00+00:00",
                "work_request_id": request_id,
                "work_request_path": workpack,
                "accepted_for_carrier_intake": True,
                "result": "RECORDED_FOR_CARRIER_INTAKE",
                "task_output_preview": body,
            },
        )
        receipt_rel = rel.replace("task_returns", "task_return_machine_receipts").replace(".json", "_machine_receipt.json")
        _write_json(
            root,
            receipt_rel,
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_machine_receipt.v1",
                "task_return_packet_path": rel,
                "accepted_for_carrier_intake": True,
                "result": "RECORDED_FOR_CARRIER_INTAKE",
            },
        )
    for rel, request_id in [(qr1, "req_steward"), (qr2, "req_ionologist")]:
        _write_json(
            root,
            rel,
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "request_id": request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "pid": 1234,
                "returncode": 0,
                "completed_at": "2026-05-26T00:04:00+00:00",
            },
        )
    _write_json(
        root,
        run_path,
        {
            "schema_id": "ion.agent_comms.run.v1",
            "run_id": run_id,
            "status": "complete",
            "objective": "Pristine chain",
            "dispatch_mode": "queue_workpack",
            "target_roles": ["role.codex_carrier_steward"],
            "thread_ids": [thread_id],
            "root_message_ids": [root_message_id],
            "workpack_paths": [wp1, wp2],
            "return_message_ids": {ret1: steward_message_id, ret2: ionologist_message_id},
            "return_message_paths": {ret1: steward_msg, ret2: ionologist_msg},
            "limits": {"max_agents": 3, "max_workpacks": 3, "max_directives": 2},
            "usage": {"processed_directive_count": 1},
            "created_at": "2026-05-26T00:00:00+00:00",
            "updated_at": "2026-05-26T00:05:00+00:00",
            "events": [],
        },
    )
    _write_json(
        root,
        "ION/05_context/current/agent_comms/runs/RUN_INDEX.json",
        {
            "schema_id": "ion.agent_comms.run_index.v1",
            "runs": {run_id: {"run_id": run_id, "run_path": run_path}},
        },
    )
    return {"run_id": run_id, "qr2": qr2}


def _seed_single_agent_clean_run(root: Path) -> dict[str, str]:
    _seed_root(root)
    run_id = "agent_run_single_agent_clean"
    thread_id = "thread_single_agent_clean"
    thread_dir = "ION/05_context/current/agent_comms/threads/thread_single_agent_clean/messages"
    root_message_id = "msg_operator_single"
    agent_message_id = "msg_ionologist_single"
    wp = "ION/05_context/current/chatgpt_connector/codex_work_requests/single_ionologist.json"
    ret = "ION/05_context/current/chatgpt_connector/task_returns/single_ionologist_return.json"
    qr = "ION/05_context/current/chatgpt_connector/codex_queue_runs/single_ionologist/run.json"
    run_path = "ION/05_context/current/agent_comms/runs/agent_run_single_agent_clean.json"
    agent_body = """Ionologist completed the direct check.

```ion-agent-decision
{
  "schema_id": "ion.agent_comms.followup_decision.v1",
  "decision": "no_followup",
  "reason": "The single-agent check is complete.",
  "evidence_refs": ["ION/05_context/current/agent_comms/runs/agent_run_single_agent_clean.json"]
}
```
"""
    root_msg = f"{thread_dir}/001_operator.json"
    agent_msg = f"{thread_dir}/002_ionologist.json"
    _write_json(
        root,
        root_msg,
        {
            "schema_id": "ion.agent_comms.message.v1",
            "message_id": root_message_id,
            "thread_id": thread_id,
            "from_role": "operator",
            "to_roles": ["role.ionologist"],
            "message_kind": "task_dispatch",
            "subject": "Single agent check",
            "body": "Inspect directly.",
            "status": "sent",
            "artifact_refs": [wp],
            "created_at": "2026-05-26T00:00:00+00:00",
        },
    )
    _write_json(
        root,
        agent_msg,
        {
            "schema_id": "ion.agent_comms.message.v1",
            "message_id": agent_message_id,
            "thread_id": thread_id,
            "parent_message_id": root_message_id,
            "from_role": "role.ionologist",
            "to_roles": ["operator"],
            "message_kind": "answer",
            "subject": "Single agent return",
            "body": agent_body,
            "status": "sent",
            "artifact_refs": [wp, ret],
            "created_at": "2026-05-26T00:01:00+00:00",
        },
    )
    _write_json(
        root,
        wp,
        {
            "request_id": "req_single_ionologist",
            "agent_role_id": "role.ionologist",
            "agent_display_name": "IONOLOGIST",
            "status": "RETURN_RECORDED_PROOF_ACCEPTED",
            "latest_return_packet_path": ret,
            "return_packet_paths": [ret],
            "codex_queue_runner_runs": [qr],
        },
    )
    _write_json(
        root,
        ret,
        {
            "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
            "created_at": "2026-05-26T00:02:00+00:00",
            "work_request_id": "req_single_ionologist",
            "work_request_path": wp,
            "accepted_for_carrier_intake": True,
            "result": "RECORDED_FOR_CARRIER_INTAKE",
            "task_output_preview": agent_body,
        },
    )
    _write_json(
        root,
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/single_ionologist_return_machine_receipt.json",
        {
            "schema_id": "ion.chatgpt_browser_connector_task_return_machine_receipt.v1",
            "task_return_packet_path": ret,
            "accepted_for_carrier_intake": True,
            "result": "RECORDED_FOR_CARRIER_INTAKE",
        },
    )
    _write_json(
        root,
        qr,
        {
            "schema_id": "ion.codex_queue_runner_run.v1",
            "request_id": "req_single_ionologist",
            "status": "RETURN_RECORDED_PROOF_ACCEPTED",
            "pid": 1234,
            "returncode": 0,
            "completed_at": "2026-05-26T00:03:00+00:00",
        },
    )
    _write_json(
        root,
        run_path,
        {
            "schema_id": "ion.agent_comms.run.v1",
            "run_id": run_id,
            "status": "complete",
            "objective": "Single agent check",
            "dispatch_mode": "queue_workpack",
            "from_role": "operator",
            "target_roles": ["role.ionologist"],
            "thread_ids": [thread_id],
            "root_message_ids": [root_message_id],
            "workpack_paths": [wp],
            "return_message_ids": {ret: agent_message_id},
            "return_message_paths": {ret: agent_msg},
            "limits": {"max_agents": 2, "max_workpacks": 2, "max_directives": 2},
            "usage": {"processed_directive_count": 0},
            "created_at": "2026-05-26T00:00:00+00:00",
            "updated_at": "2026-05-26T00:04:00+00:00",
            "events": [],
        },
    )
    _write_json(
        root,
        "ION/05_context/current/agent_comms/runs/RUN_INDEX.json",
        {
            "schema_id": "ion.agent_comms.run_index.v1",
            "runs": {run_id: {"run_id": run_id, "run_path": run_path}},
        },
    )
    return {"run_id": run_id, "qr": qr}


def test_agent_comms_chain_audit_passes_pristine_chain_and_writes_receipt(tmp_path: Path):
    seeded = _seed_pristine_chain(tmp_path)

    audit = audit_agent_comms_chain(tmp_path, {"run_id": seeded["run_id"]})

    assert audit["ok"] is True
    assert audit["audit_state"] == "PASS"
    assert audit["metrics"]["workpack_count"] == 2
    assert audit["metrics"]["accepted_return_count"] == 2
    assert audit["receipt_path"].endswith("_agent_comms_chain_audit.json")
    assert (tmp_path / audit["receipt_path"]).is_file()
    assert audit["evidence_sha256"]
    assert audit["evidence_file_count"] >= 7


def test_agent_comms_chain_audit_passes_single_agent_no_followup_run(tmp_path: Path):
    seeded = _seed_single_agent_clean_run(tmp_path)

    audit = audit_agent_comms_chain(tmp_path, {"run_id": seeded["run_id"], "write_receipt": False})

    assert audit["ok"] is True
    assert audit["audit_state"] == "PASS"
    assert audit["metrics"]["workpack_count"] == 1
    assert audit["metrics"]["directive_processed_count"] == 0
    assert audit["roles"] == ["operator", "role.ionologist"]


def test_agent_comms_chain_audit_fails_when_worker_evidence_is_not_pristine(tmp_path: Path):
    seeded = _seed_pristine_chain(tmp_path)
    queue_run = tmp_path / seeded["qr2"]
    payload = json.loads(queue_run.read_text(encoding="utf-8"))
    payload["status"] = "RETURN_RECORDED_PROOF_BLOCKED"
    queue_run.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audit = audit_agent_comms_chain(tmp_path, {"run_id": seeded["run_id"], "write_receipt": False})

    assert audit["ok"] is False
    assert audit["audit_state"] == "FAIL"
    assert "worker_runs_all_accepted" in audit["findings"]


def test_agent_comms_audit_gate_requires_fresh_pass_receipt(tmp_path: Path):
    seeded = _seed_pristine_chain(tmp_path)

    missing_gate = audit_gate_for_run(tmp_path, seeded["run_id"])
    assert missing_gate["clean"] is False
    assert missing_gate["state"] == "audit_missing"

    audit = audit_agent_comms_chain(tmp_path, {"run_id": seeded["run_id"]})
    clean_gate = audit_gate_for_run(tmp_path, seeded["run_id"], run_path=audit["run_path"])
    assert clean_gate["clean"] is True
    assert clean_gate["state"] == "clean"
    assert clean_gate["latest_audit_path"] == audit["receipt_path"]

    queue_run = tmp_path / seeded["qr2"]
    payload = json.loads(queue_run.read_text(encoding="utf-8"))
    payload["post_audit_mutation"] = True
    queue_run.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    stale_gate = audit_gate_for_run(tmp_path, seeded["run_id"], run_path=audit["run_path"])
    assert stale_gate["clean"] is False
    assert stale_gate["state"] == "audit_stale"
    assert "evidence_sha256_mismatch" in stale_gate["stale_reasons"]


def test_agent_comms_run_projection_uses_audit_gate_for_clean_state(tmp_path: Path):
    seeded = _seed_pristine_chain(tmp_path)

    before = build_agent_comms_runs_projection(tmp_path)
    before_run = before["runs"][0]
    assert before_run["status"] == "complete"
    assert before_run["is_clean"] is False
    assert before_run["clean_state"] == "audit_missing"
    assert before["audit_required_count"] == 1

    audit_agent_comms_chain(tmp_path, {"run_id": seeded["run_id"]})
    after = build_agent_comms_runs_projection(tmp_path)
    after_run = after["runs"][0]
    assert after_run["is_clean"] is True
    assert after_run["clean_state"] == "clean"
    assert after["clean_run_count"] == 1
    assert after["audit_required_count"] == 0


def test_agent_comms_completed_mutation_result_auto_writes_audit_receipt(tmp_path: Path):
    seeded = _seed_pristine_chain(tmp_path)

    result = maybe_audit_agent_comms_result(tmp_path, {}, {"ok": True, "run_id": seeded["run_id"]})

    assert result["auto_audit"]["state"] == "receipt_written"
    assert result["audit_gate"]["state"] == "clean"
    assert result["audit_gate"]["clean"] is True
    assert (tmp_path / result["auto_audit"]["receipt_path"]).is_file()
