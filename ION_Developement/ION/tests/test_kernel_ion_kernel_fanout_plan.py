import json

from kernel.ion_kernel_fanout_plan import build_kernel_fanout_plan


def test_fanout_plan_detects_path_conflicts():
    graph = {
        "parent_packet_id": "PCKT-CONFLICT-001",
        "max_parallel": 2,
        "children": [
            {
                "child_id": "child_a",
                "objective": "Update worker scheduler draft.",
                "write_paths": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
            },
            {
                "child_id": "child_b",
                "objective": "Adjust scheduler tests.",
                "write_paths": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
            },
        ],
    }

    plan = build_kernel_fanout_plan(graph)

    assert plan["verdict"] == "ION_KERNEL_FANOUT_PLAN_READY"
    assert plan["child_count"] == 2
    assert len(plan["conflict_locks"]) == 1
    lock = plan["conflict_locks"][0]
    assert lock["lock_type"] == "path_overlap"
    assert lock["holder_children"] == ["child_a", "child_b"]


def test_fanout_plan_dependency_order_is_topological():
    graph = {
        "parent_packet_id": "PCKT-ORDER-001",
        "max_parallel": 2,
        "children": [
            {"child_id": "collect", "objective": "Collect evidence."},
            {"child_id": "patch", "objective": "Implement bounded patch.", "depends_on": ["collect"]},
            {"child_id": "verify", "objective": "Run verification.", "depends_on": ["patch"]},
        ],
    }

    plan = build_kernel_fanout_plan(graph)

    assert plan["verdict"] == "ION_KERNEL_FANOUT_PLAN_READY"
    assert plan["dependency_order"] == ["collect", "patch", "verify"]
    assert plan["blocked_findings"] == []


def test_fanout_plan_model_routing_uses_spark_for_low_risk_and_frontier_for_architecture():
    graph = {
        "parent_packet_id": "PCKT-ROUTING-001",
        "children": [
            {
                "child_id": "routine_patch",
                "objective": "Implement routine parser cleanup.",
                "work_class": "code_patch",
                "risk_level": "low",
                "context_need": "medium",
            },
            {
                "child_id": "architecture_review",
                "objective": "Plan architecture schema workflow policy changes.",
                "work_class": "architecture_design",
                "risk_level": "medium",
            },
        ],
    }

    plan = build_kernel_fanout_plan(graph)
    models = {row["child_id"]: row["model_move"]["selected_model"] for row in plan["children"]}

    assert models["routine_patch"] == "gpt-5.3-codex-spark"
    assert models["architecture_review"] == "gpt-5.5"


def test_fanout_plan_compact_response_omits_full_objective_bodies():
    long_phrase = "bounded fanout scheduler objective details "
    long_objective = long_phrase * 300
    graph = {
        "parent_packet_id": "PCKT-COMPACT-001",
        "children": [{"child_id": "long_task", "objective": long_objective}],
    }

    plan = build_kernel_fanout_plan(graph, compact=True)
    blob = json.dumps(plan, sort_keys=True)

    assert plan["response_compact"] is True
    assert "objective_excerpt" in plan["children"][0]
    assert len(plan["children"][0]["objective_excerpt"]) <= 180
    assert long_phrase * 5 not in blob
    assert len(blob) < 12000
