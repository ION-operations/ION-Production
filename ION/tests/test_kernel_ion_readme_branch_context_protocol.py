import json
from pathlib import Path

import yaml

from kernel.ion_branch_context import (
    BLOCKED_VERDICT,
    READY_VERDICT,
    classify_branch_context_node,
    compile_branch_entry_packet,
    normalize_ion_tags,
    validate_branch_context_node,
)


def test_readme_branch_protocol_files_are_present_and_cross_linked():
    protocol = Path("ION/02_architecture/README_BRANCH_CONTEXT_PROTOCOL.md")
    schema = Path("ION/03_registry/ion_branch_context_node.schema.json")
    policy = Path("ION/03_registry/ion_branch_context_policy.yaml")
    readme_template = Path("ION/07_templates/context/README_BRANCH_NODE.template.md")
    capsule_template = Path("ION/07_templates/context/ION_CONTEXT_CAPSULE.branch.template.yaml")

    for path in [protocol, schema, policy, readme_template, capsule_template]:
        assert path.is_file(), path

    text = protocol.read_text(encoding="utf-8")
    assert "README_BRANCH_CONTEXT_LAW" in text
    assert "CAPSULE_FIRST_LAW" in text
    assert "NATURAL_AI_ENTRY_LAW" in text
    assert "PARENT_CHILD_CONTEXT_GRAVITY_LAW" in text
    assert "BRANCH_MATURITY_LEVELS" in text
    assert "ion_branch_context_node.schema.json" in text

    data = json.loads(schema.read_text(encoding="utf-8"))
    assert data["properties"]["schema_id"]["const"] == "ion.branch_context_node.v0_1"
    assert "maturity_level" in data["required"]

    policy_data = yaml.safe_load(policy.read_text(encoding="utf-8"))
    assert "B2_capsule_node" in policy_data["maturity_rules"]
    assert "tags_never_grant_authority" in policy_data["hard_limits"]


def test_branch_context_validator_accepts_minimum_capsule(tmp_path: Path):
    (tmp_path / "README.md").write_text(
        "# Demo Branch\n\nRead `ION_CONTEXT_CAPSULE.yaml` first.\n\n## Receipts / History\n\nNone yet.\n",
        encoding="utf-8",
    )
    (tmp_path / "ION_CONTEXT_CAPSULE.yaml").write_text(
        """
schema_id: ion.branch_context_node.v0_1
branch_id: demo_branch
branch_label: Demo Branch
path: demo
maturity_level: B2_capsule_node
purpose: Validate demo branch context.
authority:
  accepted_state_claim: false
  production_authority: false
  live_execution_authority: false
  default_work_authority: read_only
parent_domain: root
parent_chain:
  - root
child_domains: []
read_order:
  - README.md
  - ION_CONTEXT_CAPSULE.yaml
local_surfaces:
  protocols: []
  routes: []
  templates: []
  schemas: []
  agents: []
  registries: []
  tests: []
  receipts: []
  status: []
  child_index: []
receipts:
  latest: []
  required_before_state_claim: true
  missing_receipt_response: emit_blocker_or_candidate_receipt_fragment
continuity_export:
  include:
    - README.md
    - ION_CONTEXT_CAPSULE.yaml
tags:
  - Branch:Demo
  - authority:no-production
  - authority:no-live
""",
        encoding="utf-8",
    )

    assert classify_branch_context_node(tmp_path) == "B2_capsule_node"
    report = validate_branch_context_node(tmp_path)
    assert report["ok"] is True
    assert report["verdict"] == READY_VERDICT
    assert report["tags"] == ["branch:demo", "authority:no-production", "authority:no-live"]

    packet = compile_branch_entry_packet(tmp_path)
    assert packet["schema_id"] == "ion.branch_entry_packet.v0_1"
    assert packet["accepted_state_claim"] is False
    assert packet["production_authority"] is False


def test_branch_context_validator_blocks_authority_overclaim(tmp_path: Path):
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRead `ION_CONTEXT_CAPSULE.yaml`.\n\nReceipts: none.\n",
        encoding="utf-8",
    )
    (tmp_path / "ION_CONTEXT_CAPSULE.yaml").write_text(
        """
schema_id: ion.branch_context_node.v0_1
branch_id: bad_branch
branch_label: Bad Branch
path: bad
maturity_level: B2_capsule_node
purpose: Demonstrate blocked authority overclaim.
authority:
  accepted_state_claim: false
  production_authority: true
  live_execution_authority: true
read_order:
  - README.md
local_surfaces: {}
receipts:
  latest: []
  required_before_state_claim: true
continuity_export:
  include:
    - README.md
tags:
  - authority:approved
""",
        encoding="utf-8",
    )

    report = validate_branch_context_node(tmp_path)
    codes = {item["code"] for item in report["findings"]}
    assert report["ok"] is False
    assert report["verdict"] == BLOCKED_VERDICT
    assert "capsule_claims_production_authority" in codes
    assert "capsule_claims_live_execution_authority" in codes


def test_normalize_ion_tags_is_deterministic_and_dedupes():
    assert normalize_ion_tags([" Branch:Root ", "branch:root", "Proof Tool Call"]) == [
        "branch:root",
        "proof-tool-call",
    ]


def test_pilot_branch_context_nodes_validate():
    for rel in [".", "ION", "ION/02_architecture", "ION/07_templates/context"]:
        report = validate_branch_context_node(Path(rel))
        assert report["ok"] is True, (rel, report)
        assert not any(item["severity"] == "blocker" for item in report["findings"])
        assert report["authority"]["production_authority"] is False
        assert report["authority"]["live_execution_authority"] is False
