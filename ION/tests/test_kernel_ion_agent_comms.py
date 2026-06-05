import json
from pathlib import Path

from kernel.ion_agent_comms import (
    ack_agent_message,
    build_agent_comms_projection,
    create_agent_message_branch,
    extract_agent_mentions,
    list_agent_threads,
    read_agent_thread,
    send_agent_message,
)
from kernel.ion_agent_comms_directory import build_agent_communication_directory
from kernel.ion_agent_comms_directives import (
    build_agent_comms_directive_pickup_projection,
    extract_agent_comms_directives,
    process_agent_comms_directives,
)
from kernel.ion_agent_comms_runs import (
    build_agent_comms_runs_projection,
    continue_agent_comms_run,
    pickup_agent_comms_run,
    start_agent_comms_run,
    start_agent_comms_run_worker,
)
from kernel.ion_agent_spawn_templates import build_agent_spawn_templates_projection, execute_agent_spawn_template


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")


def _seed_invocable_ionologist(root: Path) -> None:
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
                "    default_mount_posture: CODEX_NATIVE_CONTEXT_AUTHORITY_SPECIALIST_CHASSIS",
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
        _write(root, rel, f"# {Path(rel).stem}\nAgent Context System\none-file-per-step\n")


def test_agent_comms_sends_threaded_message_with_inbox_outbox_signal_and_projection(tmp_path: Path):
    _seed_root(tmp_path)

    result = send_agent_message(
        tmp_path,
        {
            "from_role": "operator",
            "to_roles": ["role.steward", "role.relay"],
            "message_kind": "operator_intent",
            "subject": "Build team comms",
            "body": "Create a real durable agent communication substrate.",
            "source_refs": ["ION/02_architecture/CONTINUITY_ARCHITECTURE.md"],
        },
    )

    assert result["ok"] is True
    assert result["channel_id"] == "front_door"
    assert result["room_id"] == "room.channel.front_door"
    assert result["room_kind"] == "main"
    assert (tmp_path / result["room_capsule_path"]).is_file()
    assert (tmp_path / result["message_path"]).is_file()
    assert (tmp_path / result["thread_path"]).is_file()
    assert (tmp_path / result["signal_path"]).is_file()
    assert len(result["inbox_refs"]) == 2
    assert len(result["outbox_refs"]) == 1

    message = json.loads((tmp_path / result["message_path"]).read_text(encoding="utf-8"))
    assert message["schema_id"] == "ion.agent_comms.message.v1"
    assert message["from_role"] == "operator"
    assert message["to_roles"] == ["role.steward", "role.relay"]
    assert message["room_capsule_path"] == result["room_capsule_path"]
    assert message["production_authority"] is False

    listed = list_agent_threads(tmp_path, role_id="steward")
    assert listed["thread_count"] == 1
    assert listed["threads"][0]["thread_id"] == result["thread_id"]
    assert listed["threads"][0]["room_capsule_path"] == result["room_capsule_path"]

    thread = read_agent_thread(tmp_path, result["thread_id"], role_id="role.steward")
    assert thread["ok"] is True
    assert thread["message_count"] == 1
    assert thread["messages"][0]["message_id"] == result["message_id"]
    assert thread["messages"][0]["work_panel"]["schema_id"] == "ion.agent_comms.work_panel.v1"
    assert thread["messages"][0]["work_panel"]["room_id"] == "room.channel.front_door"
    assert thread["messages"][0]["work_panel"]["navigation"]["room_capsule_path"] == result["room_capsule_path"]
    assert [tab["tab_id"] for tab in thread["messages"][0]["work_panel"]["tabs"]] == [
        "message",
        "route",
        "context",
        "branches",
        "agents",
        "raw",
    ]

    projection = build_agent_comms_projection(tmp_path, agents=[{"role_id": "role.steward"}])
    assert projection["schema_id"] == "ion.agent_comms.projection.v1"
    assert projection["summary"]["thread_count"] == 1
    assert projection["summary"]["message_count"] == 1
    assert projection["summary"]["room_count"] == 1
    assert projection["rooms"]["room_kind_counts"]["main"] == 1
    assert projection["rooms"]["rooms"][0]["room_capsule_path"] == result["room_capsule_path"]
    assert projection["unread_by_role"]["role.steward"] == 1


def test_agent_comms_direct_room_creates_direct_channel_and_room_capsule(tmp_path: Path):
    _seed_root(tmp_path)

    result = send_agent_message(
        tmp_path,
        {
            "from_role": "role.steward",
            "to_roles": ["role.ionologist"],
            "message_kind": "question",
            "room_kind": "direct",
            "subject": "Specialist pair check",
            "body": "Can you review the cited room contract?",
            "source_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json#room_contract"],
        },
    )

    assert result["ok"] is True
    assert result["room_kind"] == "direct"
    assert result["room_id"].startswith("room.direct.")
    assert result["channel_id"].startswith("dm_")
    assert result["report_to_room_id"] == "room.main.team"
    capsule = json.loads((tmp_path / result["room_capsule_path"]).read_text(encoding="utf-8"))
    assert capsule["schema_id"] == "ion.agent_comms.room_capsule.v1"
    assert capsule["room_id"] == result["room_id"]
    assert capsule["room_kind"] == "direct"
    assert capsule["summary_required"] is True
    assert capsule["route_deeper_refs"]["message_path"] == result["message_path"]

    projection = build_agent_comms_projection(tmp_path)
    assert projection["summary"]["room_count"] == 1
    assert projection["rooms"]["room_kind_counts"]["direct"] == 1
    assert projection["rooms"]["rooms"][0]["latest_message_id"] == result["message_id"]


def test_agent_comms_projection_compacts_agent_home_view_artifacts(tmp_path: Path):
    _seed_root(tmp_path)
    home_rel = "ION/05_context/current/agent_comms/projections/agent_home_view_role_steward.json"
    scout_rel = "ION/05_context/current/agent_comms/projections/agent_home_view_scout_context_card_role_steward.json"
    loop_rel = "ION/05_context/current/agent_comms/projections/agent_home_view_self_improvement_role_steward.json"

    _write(
        tmp_path,
        home_rel,
        json.dumps(
            {
                "schema_id": "ion.agent_home_view.v0",
                "updated_at": "2026-05-30T22:00:00+00:00",
                "identity": {"assigned_role": "role.steward"},
                "source_surfaces": {
                    "files": [
                        "ION/05_context/current/agent_comms/projections/MESSAGE_INDEX.json",
                    ],
                    "not_used_for_orientation": [
                        "ION/05_context/current/agent_comms/logs/messages.jsonl",
                    ],
                },
                "scout_context_card_path": scout_rel,
                "self_improvement_loop_path": loop_rel,
            }
        ) + "\n",
    )
    _write(
        tmp_path,
        scout_rel,
        json.dumps(
            {
                "schema_id": "ion.agent_home_view.scout_context_card.v0",
                "compact_defaults": {"inbox_scan_cap": 2, "thread_scan_cap": 2, "carrier_queue_scan_cap": 3},
                "context_read_order": [
                    {
                        "step": 1,
                        "surface": "ION/05_context/current/agent_comms/projections/MESSAGE_INDEX.json",
                        "scan_cap": 20,
                        "reason": "compact attention feed",
                    }
                ],
                "forbidden_default_surfaces": [
                    "ION/05_context/current/chatgpt_connector/codex_queue_runs",
                ],
            }
        ) + "\n",
    )
    _write(
        tmp_path,
        loop_rel,
        json.dumps(
            {
                "schema_id": "ion.agent_home_view.self_improvement_loop.v0",
                "status": "items_ready",
                "counts": {"blockers": 1, "follow_ups": 0, "total": 1},
                "items": [
                    {
                        "work_item_id": "steward_blocker_1",
                        "kind": "blocker",
                        "priority": "high",
                        "summary": "Return packet missing proof links",
                        "suggested_action": "respond_with_task_return_and_receipts",
                        "proof_links": [
                            "ION/05_context/current/chatgpt_connector/task_returns/return.json",
                        ],
                        "source": "msg-1",
                    }
                ],
            }
        ) + "\n",
    )

    projection = build_agent_comms_projection(tmp_path, agents=[{"role_id": "role.steward"}])
    assert projection["summary"]["agent_home_view_count"] == 1
    home_view = projection["agent_home_views"][0]
    assert home_view["role_id"] == "role.steward"
    assert home_view["projection_path"] == home_rel
    assert home_view["self_improvement_loop"]["items"][0]["work_item_id"] == "steward_blocker_1"
    forbidden = set(home_view["scout_context_card"]["forbidden_default_surfaces"])
    assert "ION/05_context/current/agent_comms/logs/messages.jsonl" in forbidden
    assert "ION/05_context/current/chatgpt_connector/codex_queue_runs" in forbidden


def test_agent_communication_directory_projects_availability_and_automation_policy(tmp_path: Path):
    _seed_root(tmp_path)

    directory = build_agent_communication_directory(
        tmp_path,
        agents=[
            {
                "role_id": "role.steward",
                "display_name": "STEWARD",
                "invocable": True,
                "context_system_card": "ION/REPO_AUTHORITY.md",
                "registry_primary_domain": "domain.ops",
            }
        ],
        domains=[{"domain_id": "domain.ops", "display_name": "Ops"}],
    )

    assert directory["schema_id"] == "ion.agent_communication_directory.v1"
    assert directory["available_agent_count"] == 1
    steward = directory["agents_by_role"]["role.steward"]
    assert steward["available_for_comms"] is True
    assert steward["can_initiate_comms"] is True
    assert steward["inbox_path"].endswith("role_steward")
    assert "steward" in steward["aliases"]
    assert steward["mention"] == "@role.steward"
    assert steward["communication_contract"]["directive_role"] == "role.steward"
    assert directory["automation_comms_policy"]["limits"]["default_prompt_limit"] == 12
    assert directory["task_run_policy"]["default_limits"]["max_agents"] == 8
    assert directory["task_run_policy"]["observability"]["run_graph_schema_id"] == "ion.agent_comms.run_graph.v1"
    contact_contract = directory["contact_contract"]
    assert contact_contract["schema_id"] == "ion.agent_contact_contract.v1"
    assert contact_contract["routing_source_of_truth"] == "COMMUNICATION_DIRECTORY.json#contact_contract"
    assert contact_contract["aliases_by_token"]["steward"] == "role.steward"
    assert contact_contract["agents_by_role"]["role.steward"]["communication_contract"]["contact_contract_schema_id"] == "ion.agent_contact_contract.v1"
    assert contact_contract["template_contracts"]["agent_workpack_decision"]["directive_schema_id"] == "ion.agent_comms.directive.v1"
    assert contact_contract["routing_rules"][0]["contact_group"] == "orchestration"
    room_contract = directory["room_contract"]
    assert room_contract["schema_id"] == "ion.agent_room_contract.v1"
    assert room_contract["routing_source_of_truth"] == "COMMUNICATION_DIRECTORY.json#room_contract"
    assert room_contract["recommended_owner_role"] == "role.comms_cartographer"
    assert room_contract["rooms_by_id"]["room.main.team"]["room_kind"] == "main"
    assert room_contract["rooms_by_id"]["room.domain.domain.ops"]["room_kind"] == "domain"
    assert room_contract["context_loading"]["first_read"] == "room_capsule"
    assert steward["communication_contract"]["room_contract_schema_id"] == "ion.agent_room_contract.v1"


def test_agent_contact_contract_projects_peer_routing_groups_and_templates(tmp_path: Path):
    _seed_root(tmp_path)

    directory = build_agent_communication_directory(
        tmp_path,
        agents=[
            {
                "role_id": "role.steward",
                "display_name": "STEWARD",
                "invocable": True,
                "context_system_card": "ION/REPO_AUTHORITY.md",
                "registry_primary_domain": "domain.ops",
            },
            {
                "role_id": "role.ionologist",
                "display_name": "IONOLOGIST",
                "invocable": True,
                "context_system_card": "ION/REPO_AUTHORITY.md",
                "registry_primary_domain": "domain.ion_system_definition",
            },
            {
                "role_id": "role.nemesis",
                "display_name": "NEMESIS",
                "invocable": True,
                "context_system_card": "ION/REPO_AUTHORITY.md",
                "registry_primary_domain": "domain.review",
            },
            {
                "role_id": "role.mason",
                "display_name": "MASON",
                "invocable": True,
                "context_system_card": "ION/REPO_AUTHORITY.md",
                "registry_primary_domain": "domain.runtime",
            },
        ],
        domains=[
            {"domain_id": "domain.ops", "display_name": "Ops"},
            {"domain_id": "domain.ion_system_definition", "display_name": "ION System Definition"},
            {"domain_id": "domain.review", "display_name": "Review"},
            {"domain_id": "domain.runtime", "display_name": "Runtime"},
        ],
    )

    contract = directory["contact_contract"]
    ionologist_contacts = {row["role_id"]: row for row in contract["contacts_by_role"]["role.ionologist"]}
    assert ionologist_contacts["role.steward"]["relationship_tags"] == ["orchestration_escalation"]
    assert "review_or_dissent" in ionologist_contacts["role.nemesis"]["relationship_tags"]
    assert "implementation_or_runtime" in ionologist_contacts["role.mason"]["relationship_tags"]
    assert contract["contact_groups_by_role"]["role.ionologist"]["orchestration"] == ["role.steward"]
    assert contract["contact_groups_by_role"]["role.ionologist"]["review"] == ["role.nemesis"]
    assert contract["contact_groups_by_role"]["role.ionologist"]["implementation_runtime"] == ["role.mason"]
    assert contract["domains_by_id"]["domain.ion_system_definition"]["available_agent_roles"] == ["role.ionologist"]
    assert contract["escalation_routes"][0]["available_roles"] == ["role.steward"]
    assert contract["contact_edge_count"] == 12
    assert contract["agent_decision_boundary"].startswith("Agents choose who to contact")
    assert directory["task_run_policy"]["observability"]["audit_gate_schema_id"] == "ion.agent_comms.audit_gate.v1"
    assert directory["start_comms"]["task_run_start_endpoint"] == "/cockpit/agents/comms/run/start"
    assert directory["start_comms"]["task_run_audit_endpoint"] == "/cockpit/agents/comms/run/audit"
    assert directory["start_comms"]["mention_syntax"] == "@agent_alias"
    assert directory["start_comms"]["directive_schema_id"] == "ion.agent_comms.directive.v1"
    assert directory["start_comms"]["example_directive"]["dispatch_mode"] == "queue_workpack"


def test_agent_comms_mentions_route_to_agent_inbox(tmp_path: Path):
    _seed_root(tmp_path)
    directory = build_agent_communication_directory(
        tmp_path,
        agents=[
            {"role_id": "role.ionologist", "display_name": "IONOLOGIST", "invocable": True},
            {"role_id": "role.comms_cartographer", "display_name": "COMMS CARTOGRAPHER", "invocable": True},
            {"role_id": "role.codex_carrier_steward", "display_name": "CODEX CARRIER STEWARD", "invocable": True},
        ],
        domains=[],
    )
    directory_path = tmp_path / "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"
    directory_path.parent.mkdir(parents=True, exist_ok=True)
    directory_path.write_text(json.dumps(directory, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    mentions = extract_agent_mentions(tmp_path, "@ionologist please review with @comms_cartographer and @missing_specialist.")

    assert mentions["roles"] == ["role.ionologist", "role.comms_cartographer"]
    assert mentions["unresolved"] == ["@missing_specialist"]

    sent = send_agent_message(
        tmp_path,
        {
            "from_role": "role.codex_carrier_steward",
            "to_roles": [],
            "channel_id": "team",
            "message_kind": "question",
            "subject": "ION specialist review",
            "body": "@ionologist please review the Codex CLI specialist capsule.",
        },
    )

    assert sent["ok"] is True
    assert sent["to_roles"] == ["role.ionologist"]
    assert sent["mentioned_roles"] == ["role.ionologist"]
    assert sent["mention_routing_applied"] is True
    assert sent["inbox_refs"] == [f"ION/05_context/current/agent_comms/inbox/role_ionologist/{sent['message_id']}.json"]

    message = json.loads((tmp_path / sent["message_path"]).read_text(encoding="utf-8"))
    assert message["to_roles"] == ["role.ionologist"]
    assert message["mentions"][0]["token"] == "@ionologist"
    assert message["mentions"][0]["resolved"] is True

    thread = read_agent_thread(tmp_path, sent["thread_id"], role_id="role.ionologist")
    agent_tab = next(tab for tab in thread["messages"][0]["work_panel"]["tabs"] if tab["tab_id"] == "agents")
    assert any(record["kind"] == "mentions" and "role.ionologist" in record["detail"] for record in agent_tab["records"])
    projection = build_agent_comms_projection(tmp_path)
    assert projection["unread_by_role"]["role.ionologist"] == 1


def test_agent_spawn_template_enforces_automation_prompt_limit(tmp_path: Path):
    _seed_root(tmp_path)
    payload = {
        "template_id": "agent_comms_decision",
        "dispatch_mode": "comms_only",
        "dispatch_source": "automation",
        "automation_id": "auto.limited",
        "automation_prompt_limit": 1,
        "automation_window_minutes": 60,
        "agent": "role.steward",
        "objective": "Ask once.",
        "body": "One guarded automation prompt.",
    }

    first = execute_agent_spawn_template(tmp_path, payload)
    second = execute_agent_spawn_template(tmp_path, {**payload, "objective": "Ask twice."})

    assert first["ok"] is True
    assert first["automation_comms_check"]["guard_active"] is True
    assert first["automation_usage_log_path"] == "ION/05_context/current/agent_comms/automation/USAGE.jsonl"
    assert second["ok"] is False
    assert second["finding"] == "automation_prompt_limit_exceeded"
    projection = build_agent_comms_projection(tmp_path)
    assert projection["summary"]["message_count"] == 1
    assert projection["conversation"]["panel_count"] == 1
    assert projection["conversation"]["work_panels"][0]["message_id"] == first["comms_result"]["message_id"]


def test_agent_comms_ack_marks_message_and_inbox_read(tmp_path: Path):
    _seed_root(tmp_path)
    sent = send_agent_message(
        tmp_path,
        from_role="role.relay",
        to_roles=["role.steward"],
        message_kind="relay_packet",
        subject="Route request",
        body="Relay has packetized the operator intent for Steward.",
    )

    ack = ack_agent_message(tmp_path, message_id=sent["message_id"], ack_by="steward")

    assert ack["ok"] is True
    message = json.loads((tmp_path / sent["message_path"]).read_text(encoding="utf-8"))
    assert message["status"] == "acknowledged"
    assert message["acked_by"][0]["ack_by"] == "role.steward"

    inbox_ref = json.loads((tmp_path / sent["inbox_refs"][0]).read_text(encoding="utf-8"))
    assert inbox_ref["status"] == "read"
    projection = build_agent_comms_projection(tmp_path)
    assert projection["unread_by_role"]["role.steward"] == 0


def test_agent_comms_branch_creates_navigable_child_thread(tmp_path: Path):
    _seed_root(tmp_path)
    sent = send_agent_message(
        tmp_path,
        from_role="role.steward",
        to_roles=["role.mason"],
        channel_id="team",
        message_kind="task_dispatch",
        subject="Build branchable agent chat",
        body="Need Mason to inspect the chat panel model and branch if details are needed.",
        source_refs=["ION/04_packages/kernel/ion_agent_comms.py"],
    )

    branch = create_agent_message_branch(
        tmp_path,
        {
            "source_message_id": sent["message_id"],
            "from_role": "role.mason",
            "to_roles": ["role.steward"],
            "body": "Opening a focused branch to review the implementation details.",
        },
    )

    assert branch["ok"] is True
    assert branch["source_message_id"] == sent["message_id"]
    assert branch["new_thread_id"] != sent["thread_id"]

    parent_thread = read_agent_thread(tmp_path, sent["thread_id"])
    parent_panel = parent_thread["messages"][0]["work_panel"]
    branch_tab = next(tab for tab in parent_panel["tabs"] if tab["tab_id"] == "branches")
    assert branch_tab["count"] == 1
    assert branch_tab["records"][0]["thread_id"] == branch["new_thread_id"]

    child_thread = read_agent_thread(tmp_path, branch["new_thread_id"])
    child_message = child_thread["messages"][0]
    assert child_message["parent_message_id"] == sent["message_id"]
    assert child_message["branch_parent_thread_id"] == sent["thread_id"]


def test_agent_comms_reply_preserves_parent_message_link(tmp_path: Path):
    _seed_root(tmp_path)
    sent = send_agent_message(
        tmp_path,
        from_role="role.ionologist",
        to_roles=["role.codex_carrier_steward"],
        channel_id="team",
        message_kind="question",
        subject="Need CLI context answer",
        body="Can Codex confirm the current capsule mount path?",
    )

    reply = send_agent_message(
        tmp_path,
        from_role="role.codex_carrier_steward",
        to_roles=["role.ionologist"],
        channel_id="team",
        thread_id=sent["thread_id"],
        message_kind="answer",
        subject="Re: Need CLI context answer",
        body="The current mount path is available in the source refs.",
        parent_message_id=sent["message_id"],
    )

    assert reply["ok"] is True
    reply_message = json.loads((tmp_path / reply["message_path"]).read_text(encoding="utf-8"))
    assert reply_message["thread_id"] == sent["thread_id"]
    assert reply_message["parent_message_id"] == sent["message_id"]

    thread = read_agent_thread(tmp_path, sent["thread_id"])
    parent = next(message for message in thread["messages"] if message["message_id"] == sent["message_id"])
    branch_tab = next(tab for tab in parent["work_panel"]["tabs"] if tab["tab_id"] == "branches")
    assert any(record["kind"] == "child_message" and record["message_id"] == reply["message_id"] for record in branch_tab["records"])


def test_agent_comms_run_starts_real_bounded_task_packet(tmp_path: Path):
    _seed_root(tmp_path)

    result = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Coordinate Codex and ION specialist review.",
            "body": "@ionologist review the current durable comms packet path.",
            "target_roles": ["role.ionologist"],
            "max_directives": 2,
            "automation_prompt_limit": 3,
        },
    )

    assert result["ok"] is True
    assert result["thread_ids"]
    assert result["message_ids"]
    run = json.loads((tmp_path / result["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "active"
    assert run["limits"]["max_directives"] == 2
    assert run["limits"]["automation_prompt_limit"] == 3
    assert run["target_roles"] == ["role.ionologist"]
    assert run["policy"].startswith("Run pickup only processes explicit")

    projection = build_agent_comms_projection(tmp_path)
    runs = projection["runs"]
    assert runs["schema_id"] == "ion.agent_comms.runs.projection.v1"
    assert runs["active_run_count"] == 1
    assert runs["runs"][0]["run_id"] == result["run_id"]


def test_agent_comms_run_pickup_processes_thread_directives_under_limit(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Let Codex ask Ionologist for a bounded decision.",
            "body": "@codex_carrier_steward decide whether another specialist is needed.",
            "target_roles": ["role.codex_carrier_steward"],
            "max_directives": 1,
            "automation_prompt_limit": 2,
        },
    )
    directive_body = """Codex decides Ionologist needs the next packet.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review this run packet and return a bounded decision.",
  "body": "Use the run thread as source evidence and do not claim accepted state."
}
```
"""
    sent = send_agent_message(
        tmp_path,
        {
            "thread_id": started["thread_ids"][0],
            "channel_id": "team",
            "from_role": "role.codex_carrier_steward",
            "to_roles": ["role.ionologist"],
            "message_kind": "decision_request",
            "subject": "Need ION specialist decision",
            "body": directive_body,
        },
    )

    pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 5})

    assert sent["ok"] is True
    assert pickup["ok"] is True
    assert pickup["processed_directive_count"] == 1
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "limit_reached"
    assert run["usage"]["processed_directive_count"] == 1
    assert run["workpack_paths"]
    assert (tmp_path / run["workpack_paths"][0]).is_file()

    blocked = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"]})
    assert blocked["ok"] is False
    assert blocked["finding"] == "run_not_active"


def test_agent_comms_run_pickup_syncs_real_task_return_into_thread(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist to return operational proof.",
            "body": "@ionologist inspect the run packet and return bounded proof.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_directives": 2,
            "automation_prompt_limit": 2,
        },
    )

    assert started["ok"] is True
    assert started["workpack_paths"]
    workpack_rel = started["workpack_paths"][0]
    workpack = json.loads((tmp_path / workpack_rel).read_text(encoding="utf-8"))
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_ionologist_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": True,
                "result": "bounded_ionologist_return_observed",
                "task_output_preview": "Ionologist returned real bounded proof for this run.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2})

    assert pickup["ok"] is True
    assert pickup["processed_directive_count"] == 0
    assert pickup["return_sync_count"] == 1
    assert pickup["operational_evidence"]["operational_state"] == "response_observed"
    assert pickup["operational_evidence"]["task_return_count"] == 1
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["return_message_ids"][return_rel]
    message_path = tmp_path / run["return_message_paths"][return_rel]
    synced_message = json.loads(message_path.read_text(encoding="utf-8"))
    assert synced_message["from_role"] == "role.ionologist"
    assert synced_message["message_kind"] == "answer"
    assert return_rel in synced_message["artifact_refs"]
    assert "Real task return observed" in synced_message["body"]
    assert "bounded_ionologist_return_observed" in synced_message["body"]

    projection = build_agent_comms_projection(tmp_path)
    projected_run = projection["runs"]["runs"][0]
    assert projected_run["operational_state"] == "response_observed"
    assert projected_run["task_return_count"] == 1
    assert projected_run["agent_response_count"] == 1
    assert projected_run["latest_return_packet_path"] == return_rel
    assert projected_run["policy_gate"]["state"] == "within_limits"
    assert projected_run["graph"]["node_count"] >= 4
    assert any(edge["kind"] == "produced_return" for edge in projected_run["graph"]["edges"])
    assert any(edge["kind"] == "synced_reply" for edge in projected_run["graph"]["edges"])


def test_agent_comms_run_workpack_contract_requires_followup_decision(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)

    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist to make a visible follow-up decision.",
            "body": "@ionologist inspect the packet and either call another agent or stop explicitly.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
        },
    )

    assert started["ok"] is True
    workpack = json.loads((tmp_path / started["workpack_paths"][0]).read_text(encoding="utf-8"))
    assert "Agent follow-up contract:" in workpack["objective"]
    assert "ion-agent-comms" in workpack["objective"]
    assert "ion-agent-decision" in workpack["objective"]
    assert "ion.agent_comms.followup_decision.v1" in workpack["objective"]
    assert "no_followup" in workpack["objective"]


def test_agent_comms_run_projection_surfaces_no_followup_decision(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist to stop when no collaborator is needed.",
            "body": "@ionologist inspect and return no-followup if no other specialist is needed.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
        },
    )
    workpack_rel = started["workpack_paths"][0]
    workpack = json.loads((tmp_path / workpack_rel).read_text(encoding="utf-8"))
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_ionologist_no_followup_decision.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": False,
                "result": "ionologist_no_followup_decision_returned",
                "task_output_preview": """Ionologist reviewed the packet and no additional specialist is needed.

```ion-agent-decision
{
  "schema_id": "ion.agent_comms.followup_decision.v1",
  "decision": "no_followup",
  "reason": "The requested verification is complete with the current evidence.",
  "evidence_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"]
}
```
""",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2})

    assert pickup["ok"] is True
    assert pickup["processed_directive_count"] == 0
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "complete"
    projection = build_agent_comms_projection(tmp_path)
    projected_run = projection["runs"]["runs"][0]
    assert projected_run["followup_decision"]["state"] == "no_followup_declared"
    assert projected_run["completion_state"]["followup_decision"]["state"] == "no_followup_declared"
    work_item = projected_run["work_items"][0]
    assert work_item["followup_decision"]["state"] == "no_followup"
    assert work_item["followup_decision"]["reason"] == "The requested verification is complete with the current evidence."


def test_agent_comms_run_pickup_processes_directive_from_synced_task_return(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist to route a follow-up specialist.",
            "body": "@ionologist inspect the run and ask Codex Carrier Steward if needed.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_agents": 3,
            "max_workpacks": 3,
            "max_directives": 2,
            "automation_prompt_limit": 4,
        },
    )
    workpack_rel = started["workpack_paths"][0]
    workpack = json.loads((tmp_path / workpack_rel).read_text(encoding="utf-8"))
    assert "@ionologist inspect the run and ask Codex Carrier Steward if needed." in workpack["objective"]
    assert "Agent follow-up contract:" in workpack["objective"]
    assert "ion-agent-comms" in workpack["objective"]
    assert workpack["task_body"].startswith("@ionologist inspect the run")
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_ionologist_followup_directive_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": True,
                "result": "ionologist_requests_codex_carrier_followup",
                "task_output_preview": """Ionologist needs Codex Carrier Steward to inspect the CLI mount.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.ionologist",
  "agent": "role.codex_carrier_steward",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Inspect the Codex CLI specialist communication mount.",
  "body": "Return a bounded decision to the same Team Comms run.",
  "source_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"]
}
```
""",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2})

    assert pickup["ok"] is True
    assert pickup["return_sync_count"] == 1
    assert pickup["processed_directive_count"] == 1
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "active"
    assert run["usage"]["processed_directive_count"] == 1
    assert len(run["workpack_paths"]) == 2
    followup_workpack_path = next(path for path in run["workpack_paths"] if path != workpack_rel)
    followup_workpack = json.loads((tmp_path / followup_workpack_path).read_text(encoding="utf-8"))
    assert followup_workpack["agent_role_id"] == "role.codex_carrier_steward"
    assert "Return a bounded decision to the same Team Comms run." in followup_workpack["objective"]
    assert followup_workpack["task_body"].startswith("Return a bounded decision to the same Team Comms run.")
    assert "Agent follow-up contract:" in followup_workpack["task_body"]
    assert "ion.agent_comms.followup_decision.v1" in followup_workpack["task_body"]
    assert run["return_message_ids"][return_rel]
    assert any(event["event"] == "return_sync_before_directive_pickup" for event in run["events"])
    assert run["events"][-1]["event"] == "directive_pickup"
    assert run["events"][-1]["workpack_paths"] == [followup_workpack_path]
    assert run["events"][-1]["spawned_thread_ids"]

    projection = build_agent_comms_projection(tmp_path)
    projected_run = projection["runs"]["runs"][0]
    assert projected_run["workpack_count"] == 2
    assert projected_run["task_return_count"] == 1
    assert projected_run["policy_gate"]["state"] == "within_limits"
    assert any(edge["kind"] == "tracks_workpack" and followup_workpack["request_id"] in edge["target"] for edge in projected_run["graph"]["edges"])


def test_agent_comms_run_pickup_refreshes_synced_return_from_latest_return_artifact(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist to route from full latest return.",
            "body": "@ionologist inspect the run and ask Codex Carrier Steward if needed.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_agents": 3,
            "max_workpacks": 3,
            "max_directives": 2,
            "automation_prompt_limit": 4,
        },
    )
    workpack_rel = started["workpack_paths"][0]
    workpack_path = tmp_path / workpack_rel
    workpack = json.loads(workpack_path.read_text(encoding="utf-8"))
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_truncated_preview_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": False,
                "result": "RETURN_TEMPLATE_INVALID",
                "task_output_preview": "Truncated proof text before the directive appears.",
                "raw_latest_return_md_expected_from_run_packet": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    first_pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2})

    assert first_pickup["ok"] is True
    assert first_pickup["return_sync_count"] == 1
    assert first_pickup["processed_directive_count"] == 0
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    synced_message_path = tmp_path / run["return_message_paths"][return_rel]
    synced_message = json.loads(synced_message_path.read_text(encoding="utf-8"))
    assert "ion-agent-comms" not in synced_message["body"]

    queue_run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_full_latest_return/run.json"
    workpack["codex_queue_runner_runs"] = [queue_run_rel]
    workpack_path.write_text(json.dumps(workpack, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(tmp_path, queue_run_rel, "{}\n")
    _write(
        tmp_path,
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_full_latest_return/latest_return.md",
        "Full return includes the directive after the packet preview boundary.\n\n"
        + ("context proof filler\n" * 380)
        + """

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.ionologist",
  "agent": "role.codex_carrier_steward",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Inspect the full latest return directive path.",
  "body": "Return a bounded decision to the same Team Comms run."
}
```
""",
    )

    second_pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2})

    assert second_pickup["ok"] is True
    assert second_pickup["return_sync_count"] >= 1
    assert second_pickup["processed_directive_count"] == 1
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    refreshed_message = json.loads(synced_message_path.read_text(encoding="utf-8"))
    assert "ion-agent-comms" in refreshed_message["body"]
    assert len(run["workpack_paths"]) == 2
    assert run["usage"]["agent_return_message_count"] == 1
    assert run["usage"]["queued_workpack_count"] == 2


def test_agent_comms_run_continue_processes_followup_and_starts_next_worker(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started_paths: list[str] = []

    def fake_process_queue(_root, *, request_path=None, start=False, background=True, timeout_seconds=0, **_kwargs):
        started_paths.append(str(request_path))
        return {
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{Path(str(request_path)).stem}/run.json",
                "request_path": request_path,
                "pid": 8765,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr("kernel.ion_agent_comms_runs.process_codex_queue_once", fake_process_queue)
    monkeypatch.setattr("kernel.ion_agent_comms_runs._pid_matches_worker", lambda pid, run_packet_path="": pid == 4321)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist to continue to Codex Carrier Steward.",
            "body": "@ionologist inspect and route the next bounded specialist if needed.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_agents": 3,
            "max_workpacks": 3,
            "max_directives": 2,
            "automation_prompt_limit": 4,
        },
    )
    first_workpack_rel = started["workpack_paths"][0]
    workpack = json.loads((tmp_path / first_workpack_rel).read_text(encoding="utf-8"))
    assert "@ionologist inspect and route the next bounded specialist if needed." in workpack["objective"]
    assert "Agent follow-up contract:" in workpack["objective"]
    assert "ion-agent-comms" in workpack["objective"]
    assert workpack["task_body"].startswith("@ionologist inspect and route")
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_continue_followup_directive_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": first_workpack_rel,
                "accepted_for_carrier_intake": True,
                "result": "continue_needs_codex_carrier",
                "task_output_preview": """Continue to Codex Carrier Steward.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.ionologist",
  "agent": "role.codex_carrier_steward",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review chained Team Comms operation.",
  "body": "Return a bounded decision to the same run."
}
```
""",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    continued = continue_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 2, "max_worker_starts": 1})

    assert continued["ok"] is True
    assert continued["processed_directive_count"] == 1
    assert continued["return_sync_count"] == 1
    assert continued["worker_start_count"] == 1
    assert len(started_paths) == 1
    assert started_paths[0] != first_workpack_rel
    assert continued["worker_results"][0]["workpack_path"] == started_paths[0]
    followup_workpack = json.loads((tmp_path / started_paths[0]).read_text(encoding="utf-8"))
    assert "Agent follow-up contract:" in followup_workpack["task_body"]
    assert "ion.agent_comms.followup_decision.v1" in followup_workpack["task_body"]
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["usage"]["worker_start_count"] == 1
    assert run["events"][-1]["event"] == "request_specific_worker_start"


def test_agent_comms_run_worker_start_is_request_specific(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    captured: dict[str, object] = {}

    def fake_process_queue(_root, *, request_path=None, start=False, background=True, timeout_seconds=0, **_kwargs):
        captured.update(
            {
                "request_path": request_path,
                "start": start,
                "background": background,
                "timeout_seconds": timeout_seconds,
            }
        )
        return {
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/test/run.json",
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
            "objective": "Ask Ionologist for request-specific worker proof.",
            "body": "@ionologist inspect the packet and return bounded proof.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
        },
    )
    workpack_path = started["workpack_paths"][0]

    result = start_agent_comms_run_worker(
        tmp_path,
        {"run_id": started["run_id"], "workpack_path": workpack_path, "timeout_seconds": 600},
    )

    assert result["ok"] is True
    assert result["worker_started"] is True
    assert result["request_specific_worker_start"] is True
    assert result["workpack_path"] == workpack_path
    assert captured["request_path"] == workpack_path
    assert captured["start"] is True
    assert captured["background"] is True
    assert captured["timeout_seconds"] == 600
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["usage"]["worker_start_attempt_count"] == 1
    assert run["usage"]["worker_start_count"] == 1
    assert run["events"][-1]["event"] == "request_specific_worker_start"
    assert run["events"][-1]["workpack_path"] == workpack_path
    assert run["events"][-1]["run_packet_path"].endswith("/run.json")
    projection = build_agent_comms_runs_projection(tmp_path)
    projected_run = projection["runs"][0]
    assert projection["active_worker_count"] == 1
    assert projected_run["active_worker_count"] == 1
    assert projected_run["worker_runtime"]["has_active_worker"] is True
    assert projected_run["worker_runtime"]["latest_worker"]["status"] == "running"
    assert projected_run["worker_runtime"]["latest_worker"]["pid"] == 4321
    assert projected_run["worker_runtime"]["latest_worker"]["workpack_path"] == workpack_path


def test_agent_comms_run_worker_start_blocks_workpack_outside_run(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)

    def fake_process_queue(*_args, **_kwargs):
        raise AssertionError("queue runner should not start for a workpack outside the run")

    monkeypatch.setattr("kernel.ion_agent_comms_runs.process_codex_queue_once", fake_process_queue)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist for a bounded answer.",
            "body": "@ionologist inspect the packet and return bounded proof.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
        },
    )

    result = start_agent_comms_run_worker(
        tmp_path,
        {
            "run_id": started["run_id"],
            "workpack_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/not_this_run.json",
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "workpack_not_in_run"
    assert result["request_specific_worker_start"] is True


def test_agent_comms_run_worker_start_skips_already_returned_workpack(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)

    def fake_process_queue(*_args, **_kwargs):
        raise AssertionError("queue runner should not start after a real return is observed")

    monkeypatch.setattr("kernel.ion_agent_comms_runs.process_codex_queue_once", fake_process_queue)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist for one real return.",
            "body": "@ionologist inspect the packet and return bounded proof.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
        },
    )
    workpack_rel = started["workpack_paths"][0]
    workpack = json.loads((tmp_path / workpack_rel).read_text(encoding="utf-8"))
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_ionologist_worker_skip_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": True,
                "result": "worker_start_skip_return_observed",
                "task_output_preview": "Ionologist already returned before a worker start was requested.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    result = start_agent_comms_run_worker(tmp_path, {"run_id": started["run_id"], "workpack_path": workpack_rel})

    assert result["ok"] is True
    assert result["finding"] == "workpack_already_returned"
    assert result["worker_started"] is False
    assert result["return_sync_count"] == 1
    assert result["operational_evidence"]["operational_state"] == "response_observed"
    assert return_rel in result["return_packet_paths"]
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "complete"
    assert any(event["event"] == "worker_start_skipped_return_observed" for event in run["events"])
    assert run["events"][-1]["event"] == "run_completed"
    assert run["return_message_ids"][return_rel]


def test_agent_comms_run_pickup_waits_for_return_after_workpack_capacity_reached(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Ask Ionologist for one bounded response.",
            "body": "@ionologist inspect the packet and return bounded proof.",
            "target_roles": ["role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_workpacks": 1,
            "max_directives": 1,
            "max_pickups": 2,
        },
    )

    pickup = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 1})

    assert pickup["ok"] is True
    assert pickup["finding"] == "workpack_capacity_reached_waiting_for_returns"
    assert pickup["processed_directive_count"] == 0
    assert pickup["return_sync_count"] == 0
    assert pickup["policy_gate"]["state"] == "within_limits"
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "active"
    assert run["usage"]["pickup_count"] == 1
    assert run["events"][-1]["event"] == "pickup_waiting_for_workpack_return"

    projection = build_agent_comms_projection(tmp_path)
    projected_run = projection["runs"]["runs"][0]
    assert projected_run["operational_state"] == "workpack_active"
    assert projected_run["policy_gate"]["state"] == "within_limits"

    workpack_rel = started["workpack_paths"][0]
    workpack = json.loads((tmp_path / workpack_rel).read_text(encoding="utf-8"))
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_ionologist_capacity_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": workpack["request_id"],
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": True,
                "result": "bounded_capacity_return_observed",
                "task_output_preview": "Ionologist returned after workpack capacity was reached.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    synced = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 1})

    assert synced["ok"] is True
    assert synced["finding"] == "workpack_capacity_reached_return_sync_complete"
    assert synced["return_sync_count"] == 1
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "complete"
    assert any(event["event"] == "pickup_return_sync_at_workpack_capacity" for event in run["events"])
    assert run["events"][-1]["event"] == "run_completed"

    extra = pickup_agent_comms_run(tmp_path, {"run_id": started["run_id"], "max_directives": 1})

    assert extra["ok"] is True
    assert extra["finding"] == "run_complete"
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["status"] == "complete"
    assert run["events"][-1]["event"] == "run_completed"


def test_agent_comms_run_start_can_attach_existing_returned_workpack(tmp_path: Path):
    _seed_root(tmp_path)
    workpack_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/existing_mason_returned.json"
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/existing_mason_return.json"
    _write(
        tmp_path,
        workpack_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_existing_mason_return",
                "packet_path": workpack_rel,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "agent_role_id": "role.mason",
                "agent_display_name": "MASON",
                "return_packet_paths": [return_rel],
                "latest_return_packet_path": return_rel,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "work_request_id": "codex_req_existing_mason_return",
                "work_request_path": workpack_rel,
                "accepted_for_carrier_intake": True,
                "result": "existing_mason_return_observed",
                "task_output_preview": "Mason return came from an existing task return packet.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    started = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Surface existing returned workpack evidence.",
            "body": "Attach the returned Mason workpack to Team Comms.",
            "target_roles": ["role.mason"],
            "existing_workpack_paths": [workpack_rel],
        },
    )

    assert started["ok"] is True
    assert started["return_sync_count"] == 1
    assert started["operational_evidence"]["operational_state"] == "response_observed"
    run = json.loads((tmp_path / started["run_path"]).read_text(encoding="utf-8"))
    assert run["return_message_ids"][return_rel]
    synced_message = json.loads((tmp_path / run["return_message_paths"][return_rel]).read_text(encoding="utf-8"))
    assert synced_message["from_role"] == "role.mason"
    assert return_rel in synced_message["artifact_refs"]


def test_agent_comms_run_policy_gate_blocks_agent_fanout(tmp_path: Path):
    _seed_root(tmp_path)

    blocked = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Over-broad fanout should be blocked.",
            "body": "Ask two agents while max_agents is one.",
            "target_roles": ["role.mason", "role.ionologist"],
            "max_agents": 1,
        },
    )

    assert blocked["ok"] is False
    assert blocked["finding"] == "run_policy_limit_exceeded"
    assert blocked["limit"] == "max_agents"
    assert blocked["used"] == 2
    assert blocked["max"] == 1


def test_agent_comms_run_policy_gate_blocks_workpack_fanout(tmp_path: Path):
    _seed_root(tmp_path)

    blocked = start_agent_comms_run(
        tmp_path,
        {
            "objective": "Over-broad workpack fanout should be blocked.",
            "body": "Queue too many workpacks for this bounded run.",
            "target_roles": ["role.mason", "role.ionologist"],
            "dispatch_mode": "queue_workpack",
            "max_agents": 4,
            "max_workpacks": 1,
        },
    )

    assert blocked["ok"] is False
    assert blocked["finding"] == "run_policy_limit_exceeded"
    assert blocked["limit"] == "max_workpacks"
    assert blocked["used"] == 2
    assert blocked["max"] == 1


def test_agent_spawn_template_can_route_comms_only_packet(tmp_path: Path):
    _seed_root(tmp_path)

    templates = build_agent_spawn_templates_projection()
    assert templates["schema_id"] == "ion.agent_spawn_templates.v1"
    assert any(template["template_id"] == "agent_comms_decision" for template in templates["templates"])

    result = execute_agent_spawn_template(
        tmp_path,
        {
            "template_id": "agent_comms_decision",
            "dispatch_mode": "comms_only",
            "agent": "role.steward",
            "objective": "Decide whether this packet should be routed.",
            "body": "Please review the packet and return a bounded decision.",
        },
    )

    assert result["ok"] is True
    assert result["spawn_status"] == "COMMS_PACKET_SENT"
    assert result["invocation_result"] is None
    assert (tmp_path / result["comms_result"]["message_path"]).is_file()
    projection = build_agent_comms_projection(tmp_path)
    assert projection["summary"]["message_count"] == 1
    assert projection["unread_by_role"]["role.steward"] == 1


def test_agent_comms_directive_extracts_explicit_agent_authored_block():
    body = """Need IONOLOGIST review.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review the Codex CLI specialist capsule and decide if communication routing is correct.",
  "body": "Use the attached context refs and return a bounded decision.",
  "room_kind": "direct",
  "report_to_room_id": "room.main.team",
  "source_refs": ["ION/05_context/current/codex_agent_mounts/"]
}
```
"""

    extracted = extract_agent_comms_directives(
        body,
        source_ref="agent_chat://turn/1",
        source_message_id="msg_agent_1",
        from_role="role.codex_carrier_steward",
    )

    assert extracted["ok"] is True
    assert extracted["directive_count"] == 1
    directive = extracted["directives"][0]
    assert directive["from_role"] == "role.codex_carrier_steward"
    assert directive["agent"] == "role.ionologist"
    assert directive["dispatch_mode"] == "queue_workpack"
    assert directive["template_id"] == "agent_workpack_decision"
    assert directive["room_kind"] == "direct"
    assert directive["report_to_room_id"] == "room.main.team"


def test_agent_comms_directive_implicit_id_is_stable_across_return_replays():
    body = """Need IONOLOGIST review.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Validate the follow-up workpack inheritance path.",
  "body": "Return a bounded decision to the same Team Comms run."
}
```
"""

    first = extract_agent_comms_directives(
        body,
        source_ref="ION/05_context/current/chatgpt_connector/task_returns/replayed_a.json",
        source_message_id="msg_replay_a",
        from_role="role.codex_carrier_steward",
        scope_id="agent_run_replay_scope",
    )
    second = extract_agent_comms_directives(
        body,
        source_ref="ION/05_context/current/chatgpt_connector/task_returns/replayed_b.json",
        source_message_id="msg_replay_b",
        from_role="role.codex_carrier_steward",
        scope_id="agent_run_replay_scope",
    )
    other_scope = extract_agent_comms_directives(
        body,
        source_ref="ION/05_context/current/chatgpt_connector/task_returns/replayed_b.json",
        source_message_id="msg_replay_b",
        from_role="role.codex_carrier_steward",
        scope_id="agent_run_other_scope",
    )

    assert first["ok"] is True
    assert second["ok"] is True
    first_directive = first["directives"][0]
    second_directive = second["directives"][0]
    assert first_directive["directive_id"] == second_directive["directive_id"]
    assert first_directive["legacy_directive_id"] != second_directive["legacy_directive_id"]
    assert first_directive["source_ref"] != second_directive["source_ref"]
    assert other_scope["directives"][0]["directive_id"] != first_directive["directive_id"]


def test_agent_comms_directive_extracts_after_prior_markdown_fence():
    body = """Evidence table:

```text
ION/path | sha | excerpt
```

Decision requires another specialist.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review the post-fence directive route.",
  "body": "Return a bounded decision."
}
```
"""

    extracted = extract_agent_comms_directives(
        body,
        source_ref="agent_chat://turn/after-fence",
        source_message_id="msg_agent_after_fence",
        from_role="role.codex_carrier_steward",
    )

    assert extracted["ok"] is True
    assert extracted["directive_count"] == 1
    assert extracted["directives"][0]["agent"] == "role.ionologist"
    assert extracted["directives"][0]["objective"] == "Review the post-fence directive route."


def test_agent_comms_directive_pickup_routes_through_spawn_template_and_ledger(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    directive_body = """Codex Carrier Steward needs Ionologist review.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review whether Codex CLI specialist and ION specialist can communicate through durable directives.",
  "body": "Return a bounded decision using the required proof sections.",
  "source_refs": ["ION/05_context/current/codex_agent_mounts/role_codex_carrier_steward__domain_codex_carrier_sync/.ion/COMMUNICATIONS.json"]
}
```
"""
    sent = send_agent_message(
        tmp_path,
        {
            "from_role": "role.codex_carrier_steward",
            "to_roles": ["role.steward"],
            "message_kind": "task_dispatch",
            "room_id": "room.mission.directive_pickup",
            "room_kind": "mission",
            "report_to_room_id": "room.main.team",
            "subject": "Need ION specialist decision",
            "body": directive_body,
        },
    )

    result = process_agent_comms_directives(tmp_path, {"message_path": sent["message_path"]})

    assert result["ok"] is True
    assert result["processed_directive_count"] == 1
    assert result["already_processed_count"] == 0
    assert (tmp_path / result["ledger_path"]).is_file()
    assert (tmp_path / result["receipt_path"]).is_file()
    routed = result["results"][0]["spawn_result"]
    assert routed["ok"] is True
    assert routed["spawn_status"] == "WORKPACK_QUEUED"
    assert routed["dispatch_mode"] == "queue_workpack"
    assert routed["target_agent"] == "role.ionologist"
    assert routed["production_authority"] is False
    assert routed["live_execution_authority"] is False
    assert routed["accepted_state_authority"] is False
    assert routed["live_external_agent_execution_proven"] is False
    assert routed["spawned_comms_message_id"] == routed["comms_result"]["message_id"]
    assert routed["comms_result"]["room_id"] == "room.mission.directive_pickup"
    assert routed["comms_result"]["room_kind"] == "mission"
    assert routed["comms_result"]["report_to_room_id"] == "room.main.team"
    assert (tmp_path / routed["comms_result"]["room_capsule_path"]).is_file()
    workpack_path = routed["invocation_result"]["codex_work_request_path"]
    assert routed["workpack_path"] == workpack_path
    workpack = json.loads((tmp_path / workpack_path).read_text(encoding="utf-8"))
    assert workpack["agent_role_id"] == "role.ionologist"
    assert workpack["status"] == "QUEUED_FOR_CODEX_CARRIER"
    record = result["results"][0]["ledger_record"]
    assert record["source_message_id"] == sent["message_id"]
    assert record["spawned_comms_message_id"] == routed["comms_result"]["message_id"]
    assert record["comms_message_id"] == routed["comms_result"]["message_id"]
    assert record["target_agent"] == "role.ionologist"
    assert record["dispatch_mode"] == "queue_workpack"
    assert record["room_id"] == "room.mission.directive_pickup"
    assert record["room_kind"] == "mission"
    assert record["room_capsule_path"] == routed["comms_result"]["room_capsule_path"]
    assert record["workpack_path"] == workpack_path
    assert record["workpack_status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert record["live_external_agent_execution_proven"] is False
    assert record["production_authority"] is False
    assert record["live_execution_authority"] is False
    assert record["accepted_state_authority"] is False

    duplicate = process_agent_comms_directives(tmp_path, {"message_path": sent["message_path"]})
    assert duplicate["ok"] is True
    assert duplicate["processed_directive_count"] == 0
    assert duplicate["already_processed_count"] == 1
    assert duplicate["receipt_path"] != result["receipt_path"]

    pickup = build_agent_comms_directive_pickup_projection(tmp_path)
    assert pickup["schema_id"] == "ion.agent_comms.directive_pickup.projection.v1"
    assert pickup["action_id"] == "agent_comms.process_directives"
    assert pickup["directive_fence"] == "ion-agent-comms"
    assert "start_workpack" in pickup["allowed_dispatch_modes"]
    assert pickup["processed_count"] == 1
    assert pickup["receipt_count"] >= 1
    assert "spawned_comms_message_id" in pickup["evidence_fields"]
    assert "target_agent" in pickup["evidence_fields"]
    assert pickup["live_external_agent_execution_proven"] is False
    assert pickup["recent_processed"][0]["agent"] == "role.ionologist"
    assert pickup["recent_processed"][0]["target_agent"] == "role.ionologist"
    assert pickup["recent_processed"][0]["source_message_id"] == sent["message_id"]
    assert pickup["recent_processed"][0]["spawned_comms_message_id"] == routed["comms_result"]["message_id"]
    assert pickup["recent_processed"][0]["workpack_path"] == workpack_path
    assert pickup["recent_processed"][0]["production_authority"] is False
    assert pickup["recent_processed"][0]["live_execution_authority"] is False
    assert pickup["recent_processed"][0]["accepted_state_authority"] is False
    assert pickup["recent_receipts"][0]["path"].endswith("_directive_pickup.json")


def test_agent_comms_directive_pickup_dedupes_same_directive_replayed_from_new_message(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_invocable_ionologist(tmp_path)
    directive_body = """Codex Carrier Steward needs Ionologist review.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review replay idempotency for Team Comms directives.",
  "body": "Return a bounded decision using the same run scope."
}
```
"""
    first_message = send_agent_message(
        tmp_path,
        {
            "from_role": "role.codex_carrier_steward",
            "to_roles": ["role.steward"],
            "message_kind": "task_dispatch",
            "subject": "Need ION specialist decision",
            "body": directive_body,
        },
    )
    first = process_agent_comms_directives(tmp_path, {"message_path": first_message["message_path"], "run_id": "agent_run_replay_test"})
    before_workpacks = sorted((tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob("*.json"))
    replayed_message = send_agent_message(
        tmp_path,
        {
            "thread_id": first_message["thread_id"],
            "from_role": "role.codex_carrier_steward",
            "to_roles": ["role.steward"],
            "message_kind": "task_dispatch",
            "subject": "Need ION specialist decision",
            "body": directive_body,
        },
    )

    replayed = process_agent_comms_directives(tmp_path, {"message_path": replayed_message["message_path"], "run_id": "agent_run_replay_test"})
    after_workpacks = sorted((tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob("*.json"))

    assert first["ok"] is True
    assert first["processed_directive_count"] == 1
    assert replayed["ok"] is True
    assert replayed["processed_directive_count"] == 0
    assert replayed["already_processed_count"] == 1
    assert before_workpacks == after_workpacks


def test_agent_comms_directive_pickup_respects_legacy_source_path_ledger_id(tmp_path: Path):
    _seed_root(tmp_path)
    directive_body = """Codex Carrier Steward needs Ionologist review.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review legacy directive idempotency.",
  "body": "Return a bounded decision without spawning a duplicate."
}
```
"""
    sent = send_agent_message(
        tmp_path,
        {
            "from_role": "role.codex_carrier_steward",
            "to_roles": ["role.steward"],
            "message_kind": "task_dispatch",
            "subject": "Need ION specialist decision",
            "body": directive_body,
        },
    )
    extracted = extract_agent_comms_directives(
        directive_body,
        source_ref=sent["message_path"],
        source_message_id=sent["message_id"],
        from_role="role.codex_carrier_steward",
        scope_id=sent["thread_id"],
    )
    directive = extracted["directives"][0]
    legacy_id = directive["legacy_directive_id"]
    ledger_path = tmp_path / "ION/05_context/current/agent_comms/automation/DIRECTIVE_LEDGER.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.agent_comms.directive_ledger.v1",
                "created_at": "2026-05-25T00:00:00+00:00",
                "updated_at": "2026-05-25T00:00:00+00:00",
                "processed": {
                    legacy_id: {
                        "directive_id": legacy_id,
                        "processed_at": "2026-05-25T00:00:00+00:00",
                        "agent": "role.ionologist",
                        "dispatch_mode": "queue_workpack",
                        "workpack_path": "legacy/workpack.json",
                    }
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = process_agent_comms_directives(tmp_path, {"message_path": sent["message_path"]})

    assert result["ok"] is True
    assert result["processed_directive_count"] == 0
    assert result["already_processed_count"] == 1
    assert result["results"][0]["directive_id"] == directive["directive_id"]
    assert result["results"][0]["processed_directive_id"] == legacy_id
