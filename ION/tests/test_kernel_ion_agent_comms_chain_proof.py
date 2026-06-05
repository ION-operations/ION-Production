import json
from pathlib import Path

from kernel.ion_agent_comms_chain_proof import prove_agent_comms_chain
from kernel.ion_agent_comms_runs import continue_agent_comms_run, start_agent_comms_run, start_agent_comms_run_worker


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(root: Path, rel: str, value: dict) -> None:
    _write(root, rel, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-chain-proof-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")


def _seed_invocable_agents(root: Path) -> None:
    for rel in [
        "ION/03_registry/codex_cli_carrier_profile.yaml",
        "ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
        "ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md",
        "ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py",
        "ION/04_packages/kernel/ion_codex_queue_runner.py",
        "ION/04_packages/kernel/ion_agent_invocation_broker.py",
    ]:
        _write(root, rel)
    _write(
        root,
        "ION/03_registry/agent_context_system_registry.yaml",
        "\n".join(
            [
                "registry_id: ion.agent_context_system_registry.v1",
                "agents:",
                "  - role_id: role.codex_carrier_steward",
                "    display_name: CODEX_CARRIER_STEWARD",
                "    context_system_card: ION/05_context/current/agent_context_systems/CODEX_CARRIER_STEWARD.context_system.md",
                "context_specialists:",
                "  - role_id: role.ionologist",
                "    display_name: IONOLOGIST",
                "    context_system_card: ION/05_context/current/agent_context_systems/IONOLOGIST.context_system.md",
                "    base_sources:",
                "      - ION/03_registry/boots/IONOLOGIST.boot.md",
                "      - ION/03_registry/semantic_identities/IONOLOGIST.semantic.yaml",
                "      - ION/03_registry/domains/domain.ion_system_definition.domain.yaml",
                "",
            ]
        ),
    )
    _write(
        root,
        "ION/03_registry/agent_roster_registry.yaml",
        "\n".join(
            [
                "registry_id: current_phase.agent_roster_registry",
                "roster_records:",
                "  - entity_id: role.ionologist",
                "    display_name: Ionologist",
                "    live_status: ACTIVE_CURRENT_PHASE",
                "    registry_primary_domain: domain.ion_system_definition",
                "  - entity_id: role.codex_carrier_steward",
                "    display_name: Codex Carrier Steward",
                "    live_status: ACTIVE_CURRENT_PHASE",
                "    registry_primary_domain: domain.codex_carrier_sync",
                "",
            ]
        ),
    )
    for rel in [
        "ION/05_context/current/agent_context_systems/CODEX_CARRIER_STEWARD.context_system.md",
        "ION/05_context/current/agent_context_systems/IONOLOGIST.context_system.md",
        "ION/03_registry/boots/IONOLOGIST.boot.md",
        "ION/03_registry/semantic_identities/IONOLOGIST.semantic.yaml",
        "ION/03_registry/domains/domain.ion_system_definition.domain.yaml",
    ]:
        _write(root, rel, f"# {Path(rel).stem}\nAgent Context System\n")


def _write_return(root: Path, workpack_rel: str, result: str, body: str) -> str:
    workpack = json.loads((root / workpack_rel).read_text(encoding="utf-8"))
    return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{Path(workpack_rel).stem}_{result}.json"
    _write_json(
        root,
        return_rel,
        {
            "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
            "created_at": "2026-05-26T00:00:00+00:00",
            "work_request_id": workpack["request_id"],
            "work_request_path": workpack_rel,
            "accepted_for_carrier_intake": True,
            "result": result,
            "task_output_preview": body,
        },
    )
    _write_json(
        root,
        return_rel.replace("task_returns", "task_return_machine_receipts").replace(".json", "_machine_receipt.json"),
        {
            "schema_id": "ion.chatgpt_browser_connector_task_return_machine_receipt.v1",
            "task_return_packet_path": return_rel,
            "accepted_for_carrier_intake": True,
            "result": "RECORDED_FOR_CARRIER_INTAKE",
        },
    )
    return return_rel


def test_agent_comms_chain_proof_passes_full_two_agent_chain(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_invocable_agents(tmp_path)

    def fake_process_queue(_root, *, request_path=None, start=False, background=True, timeout_seconds=0, **_kwargs):
        return {
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{Path(str(request_path)).stem}/run.json",
                "request_path": request_path,
                "pid": 4321,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr("kernel.ion_agent_comms_runs.process_codex_queue_once", fake_process_queue)
    monkeypatch.setattr("kernel.ion_agent_comms_runs._pid_matches_worker", lambda pid, run_packet_path="": pid == 4321)

    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Prove Ionologist can route Codex Carrier Steward.",
            "body": "@ionologist inspect and call Codex Carrier Steward if needed.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_agents": 3,
            "max_workpacks": 3,
            "max_directives": 2,
            "automation_prompt_limit": 4,
        },
    )
    first_workpack = started["workpack_paths"][0]
    first_worker = start_agent_comms_run_worker(tmp_path, {"run_id": started["run_id"], "workpack_path": first_workpack})
    assert first_worker["worker_started"] is True
    _write_return(
        tmp_path,
        first_workpack,
        "ionologist_calls_steward",
        """Ionologist needs Codex Carrier Steward.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.ionologist",
  "agent": "role.codex_carrier_steward",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review the Team Comms chain proof.",
  "body": "Return a bounded final decision."
}
```
""",
    )

    continued = continue_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2, "max_worker_starts": 1})
    assert continued["processed_directive_count"] == 1
    assert continued["worker_start_count"] == 1
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    followup_workpack = next(path for path in run["workpack_paths"] if path != first_workpack)
    _write_return(
        tmp_path,
        followup_workpack,
        "steward_no_followup",
        """Codex Carrier Steward verified the route and stops.

```ion-agent-decision
{
  "schema_id": "ion.agent_comms.followup_decision.v1",
  "decision": "no_followup",
  "reason": "The two-agent chain has closed.",
  "evidence_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"]
}
```
""",
    )
    final = continue_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2, "max_worker_starts": 1})
    assert final["ok"] is True

    proof = prove_agent_comms_chain(tmp_path, {"run_id": started["run_id"], "write_receipt": False})

    assert proof["ok"] is True
    assert proof["proof_state"] == "chain_proved"
    assert proof["first_missing_link"] == ""
    assert proof["metrics"]["agent_role_count"] == 2
    assert proof["metrics"]["directive_count"] == 1
    assert proof["metrics"]["workpack_count"] == 2
    assert proof["metrics"]["task_return_count"] == 2
    assert proof["metrics"]["machine_receipt_count"] == 2
    assert proof["metrics"]["synced_reply_count"] == 2
    assert [link["link_id"] for link in proof["links"]][:4] == [
        "run_observed",
        "message_sent",
        "multi_agent_handoff",
        "directive_observed",
    ]
    assert all(link["ok"] is True for link in proof["links"] if link["required"] is True)


def test_agent_comms_chain_proof_reports_exact_missing_link(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_agents(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Prove missing worker is explicit.",
            "body": "@ionologist inspect but no worker has started yet.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
        },
    )

    proof = prove_agent_comms_chain(
        tmp_path,
        {
            "run_id": started["run_id"],
            "require_directive": False,
            "require_machine_receipts": False,
            "min_agents": 1,
            "write_receipt": False,
        },
    )

    assert proof["ok"] is False
    assert proof["proof_state"] == "blocked_at_worker_started"
    assert proof["first_missing_link"] == "worker_started"
    missing = {link["link_id"]: link for link in proof["links"] if link["ok"] is not True}
    assert missing["worker_started"]["detail"]["runtime_worker_count"] == 0
    assert "task_return_observed" in proof["missing_links"]
