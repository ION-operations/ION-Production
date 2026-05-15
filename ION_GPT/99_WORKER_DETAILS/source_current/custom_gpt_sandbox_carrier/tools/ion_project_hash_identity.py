"""ION project hash identity helper.

This helper creates public identity manifests only. It never creates bearer
secrets, account credentials, private keys, or capability tokens. Authorization
must be performed by Helixion using account/session approval or OAuth.
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import Any


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def new_project_hash(project_label: str | None = None, entropy_bytes: int = 32) -> str:
    """Return an unguessable public project identity hash.

    The value is public/non-secret. Entropy resists enumeration and collision,
    but knowing the hash does not grant access.
    """
    if entropy_bytes < 16:
        raise ValueError("entropy_bytes must be at least 16")
    payload = {
        "schema_id": "ion.project_hash_seed.v1",
        "project_label": project_label or "untitled_project",
        "nonce": _b64url(secrets.token_bytes(entropy_bytes)),
    }
    digest = hashlib.sha256(b"ion.project_identity.v1\0" + canonical_json(payload)).digest()
    return "ionproj_" + _b64url(digest)


def build_project_identity(
    project_hash: str,
    project_label: str,
    validation_base_url: str = "https://helixion.net",
) -> dict[str, Any]:
    return {
        "schema_id": "ion.project_identity.v1",
        "ion_project_hash": project_hash,
        "project_label": project_label,
        "hash_role": "public_identity_locator",
        "identity_is_secret": False,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issuer": "local_candidate",
        "security_model": {
            "hash_grants_access": False,
            "authorization_lives_at": "helixion",
            "secrets_in_folder": False,
        },
        "helixion": {
            "validation_base_url": validation_base_url,
            "claim_required_for_private_context": True,
        },
        "public_validation": {
            "key_branch_registry": "ION_HASH_BRANCHES.yaml",
            "validation_pointers": "ION_VALIDATION_POINTERS.yaml",
        },
        "non_exportable": [
            "private_keys",
            "bearer_tokens",
            "oauth_tokens",
            "session_cookies",
            "vault_contents",
            "credentials",
            "capability_tokens",
            "hidden_chain_of_thought",
        ],
    }


def build_hash_branches(
    project_hash: str,
    context_mesh_sha256: str = "<pending>",
    continuity_package_sha256: str = "<pending>",
) -> dict[str, Any]:
    return {
        "schema_id": "ion.hash_branch_registry.v1",
        "ion_project_hash": project_hash,
        "secrets_present": False,
        "branches": [
            {
                "branch_id": "root_identity",
                "branch_type": "project_identity",
                "hash_or_pointer": "ION_PROJECT_IDENTITY.yaml",
                "secret": False,
                "validation_role": "locates project for Helixion validation",
                "exportable": True,
            },
            {
                "branch_id": "context_mesh",
                "branch_type": "content_hash",
                "hash_or_pointer": context_mesh_sha256,
                "secret": False,
                "validation_role": "proves mounted context mesh content",
                "exportable": True,
            },
            {
                "branch_id": "continuity_package",
                "branch_type": "package_hash",
                "hash_or_pointer": continuity_package_sha256,
                "secret": False,
                "validation_role": "proves transfer package content",
                "exportable": True,
            },
            {
                "branch_id": "action_capability",
                "branch_type": "helixion_pointer",
                "hash_or_pointer": "helixion://capability/request/<claim_id_or_route>",
                "secret": False,
                "validation_role": "requests server-side capability; does not contain capability secret",
                "exportable": True,
            },
        ],
    }


def build_claim_handshake(
    project_hash: str,
    carrier_instance_id: str,
    challenge_nonce: str,
    package_hash: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_id": "ion.helixion_hash_handshake.v1",
        "request": {
            "ion_project_hash": project_hash,
            "carrier_instance_id": carrier_instance_id,
            "challenge_nonce": challenge_nonce,
            "package_hash": package_hash or "<none>",
            "branch_hashes": [],
        },
        "server_decision": {
            "status": "pending_approval",
            "private_metadata_returned": False,
            "approval_url": "https://helixion.net/project/claim/<claim_id>",
            "claim_id": "<claim_id>",
        },
        "authorization_boundary": {
            "hash_grants_access": False,
            "user_identity_source": "helixion_session_approval",
            "capability_token_exportable": False,
        },
    }


def manifest_contains_no_secrets(manifest: dict[str, Any]) -> bool:
    text = json.dumps(manifest, sort_keys=True).lower()
    forbidden = [
        "bearer ",
        "oauth_token_value",
        "private_key_value",
        "session_cookie_value",
        "capability_token_value",
        "password",
    ]
    return not any(token in text for token in forbidden)
