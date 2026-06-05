from __future__ import annotations

from kernel.ion_domain_weaver_semantic_ids import (
    VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
    canonicalize_codex_mount_identity,
    canonicalize_domain_weaver_domain_id,
)


def test_vnext_front_door_aliases_canonicalize_without_state_claim() -> None:
    for raw in (
        "ion_vnext_front_door",
        "domain.ion_vnext_front_door",
        "domain.ion_vnext_front_door_authority",
        "",
    ):
        result = canonicalize_domain_weaver_domain_id(
            raw,
            mount_id="role_atlas__ion_vnext_front_door",
            source="test",
        )

        assert result["canonical_domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
        assert result["alias_detected"] is True
        assert result["authority"]["accepted_state_authority"] is False
        assert result["authority"]["registry_write_performed"] is False


def test_vnext_front_door_canonical_id_passes_without_alias_claim() -> None:
    result = canonicalize_domain_weaver_domain_id(
        VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
        mount_id="role_atlas__ion_vnext_front_door",
        source="test",
    )

    assert result["raw_domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert result["canonical_domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert result["alias_detected"] is False
    assert result["authority"]["projection_write_performed"] is False


def test_empty_domain_id_only_canonicalizes_for_vnext_front_door_mount() -> None:
    result = canonicalize_domain_weaver_domain_id(
        "",
        mount_id="role_atlas__domain_archaeology_drift_watch",
        source="test",
    )

    assert result["raw_domain_id"] == ""
    assert result["canonical_domain_id"] == ""
    assert result["alias_detected"] is False
    assert result["authority"]["mount_write_performed"] is False


def test_unknown_domain_id_passes_through_without_alias_claim() -> None:
    result = canonicalize_domain_weaver_domain_id("domain.agent_communication_systems")

    assert result["canonical_domain_id"] == "domain.agent_communication_systems"
    assert result["alias_detected"] is False
    assert result["authority"]["projection_write_performed"] is False


def test_codex_mount_identity_uses_manifest_and_mount_alias() -> None:
    result = canonicalize_codex_mount_identity(
        "role_atlas__ion_vnext_front_door",
        {"domain_id": "ion_vnext_front_door", "role_id": "role.atlas"},
    )

    assert result["role_id"] == "role.atlas"
    assert result["raw_domain_id"] == ""
    assert result["manifest_domain_id"] == "ion_vnext_front_door"
    assert result["domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert result["domain_alias_detected"] is True


def test_codex_mount_identity_preserves_manifest_alias_for_review() -> None:
    result = canonicalize_codex_mount_identity(
        "role_atlas__ion_vnext_front_door",
        {"domain_id": "ion_vnext_front_door", "role_id": "role.atlas"},
    )

    semantic = result["semantic_identity"]
    assert result["domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert result["manifest_domain_id"] == "ion_vnext_front_door"
    assert semantic["raw_domain_id"] == "ion_vnext_front_door"
    assert semantic["canonical_domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert semantic["authority"]["accepted_state_authority"] is False
