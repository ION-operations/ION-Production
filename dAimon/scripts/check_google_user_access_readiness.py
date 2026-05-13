#!/usr/bin/env python3
"""Read-only Google Cloud tester access readiness check for dAimon.

This script distinguishes runtime proof from human/tester access proof. It
queries Google Cloud IAM and Cloud Run configuration when gcloud is available,
but it never grants roles, deploys services, or mutates state.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env

OUT = ROOT / "sample_outputs" / "google_user_access_readiness.json"
DEPLOY_SUMMARY = ROOT / "sample_outputs" / "cloud_run_deploy_summary.json"
AGENT_DEPLOY_SUMMARY = ROOT / "sample_outputs" / "agent_engine_deploy_summary.json"

REQUIRED_APIS = {
    "run.googleapis.com",
    "aiplatform.googleapis.com",
}
CLOUD_RUN_INVOKER_ROLES = {
    "roles/run.invoker",
    "roles/run.servicesInvoker",
    "roles/run.admin",
    "roles/editor",
    "roles/owner",
}
VERTEX_USER_ROLES = {
    "roles/aiplatform.user",
    "roles/aiplatform.admin",
    "roles/editor",
    "roles/owner",
}
CONSOLE_VISIBILITY_ROLES = {
    "roles/browser",
    "roles/viewer",
    "roles/editor",
    "roles/owner",
    "roles/aiplatform.user",
    "roles/aiplatform.admin",
}


def find_gcloud() -> str | None:
    found = shutil.which("gcloud")
    if found:
        return found
    local = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"
    return str(local) if local.exists() else None


def write_json(payload: Mapping[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = dict(payload)
    data.setdefault("schema", "daimon.google_user_access_readiness.v0_1")
    data.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
    data.setdefault("accepted_state_changed", False)
    data.setdefault("external_mutation_attempted", False)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_cmd(args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def gcloud_text(gcloud: str, args: list[str]) -> tuple[str | None, str | None]:
    result = run_cmd([gcloud, *args])
    if result.returncode != 0:
        return None, (result.stderr.strip() or result.stdout.strip() or f"gcloud exited {result.returncode}")
    value = result.stdout.strip()
    return (value if value and value != "(unset)" else None), None


def gcloud_json(gcloud: str, args: list[str]) -> tuple[Any | None, str | None]:
    result = run_cmd([gcloud, *args])
    if result.returncode != 0:
        return None, (result.stderr.strip() or result.stdout.strip() or f"gcloud exited {result.returncode}")
    try:
        return json.loads(result.stdout or "null"), None
    except json.JSONDecodeError as exc:
        return None, f"gcloud returned non-JSON output: {exc}"


def split_principals(values: Iterable[str]) -> list[str]:
    principals: list[str] = []
    for value in values:
        for raw_item in value.split(","):
            item = raw_item.strip()
            if not item:
                continue
            if ":" not in item and "@" in item:
                item = f"user:{item}"
            principals.append(item)
    return sorted(dict.fromkeys(principals))


def role_members(policy: Mapping[str, Any], roles: set[str]) -> set[str]:
    members: set[str] = set()
    for binding in policy.get("bindings", []):
        if not isinstance(binding, Mapping) or binding.get("role") not in roles:
            continue
        for member in binding.get("members", []):
            members.add(str(member))
    return members


def principal_roles(policy: Mapping[str, Any], principal: str) -> set[str]:
    roles: set[str] = set()
    for binding in policy.get("bindings", []):
        if not isinstance(binding, Mapping):
            continue
        if principal in {str(member) for member in binding.get("members", [])}:
            roles.add(str(binding.get("role")))
    return roles


def public_invoker_present(service_policy: Mapping[str, Any]) -> bool:
    invokers = role_members(service_policy, CLOUD_RUN_INVOKER_ROLES)
    return "allUsers" in invokers or "allAuthenticatedUsers" in invokers


def build_access_rows(
    principals: list[str],
    *,
    service_policy: Mapping[str, Any],
    project_policy: Mapping[str, Any],
    cloud_run_public: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    service_invokers = role_members(service_policy, CLOUD_RUN_INVOKER_ROLES)
    project_invokers = role_members(project_policy, CLOUD_RUN_INVOKER_ROLES)
    for principal in principals:
        project_roles = principal_roles(project_policy, principal)
        service_roles = principal_roles(service_policy, principal)
        cloud_run_direct = principal in service_invokers or principal in project_invokers
        cloud_run_ok = cloud_run_public or cloud_run_direct
        vertex_roles = sorted(project_roles.intersection(VERTEX_USER_ROLES))
        console_roles = sorted(project_roles.intersection(CONSOLE_VISIBILITY_ROLES))
        rows.append({
            "principal": principal,
            "cloud_run_invocation": {
                "ok": cloud_run_ok,
                "via_public_invoker": cloud_run_public,
                "direct_role_observed": cloud_run_direct,
                "service_roles": sorted(service_roles.intersection(CLOUD_RUN_INVOKER_ROLES)),
                "project_roles": sorted(project_roles.intersection(CLOUD_RUN_INVOKER_ROLES)),
            },
            "vertex_agent_engine_access": {
                "ok": bool(vertex_roles),
                "project_roles": vertex_roles,
                "expected_any_role": sorted(VERTEX_USER_ROLES),
            },
            "console_project_visibility": {
                "ok": bool(console_roles),
                "project_roles": console_roles,
                "expected_any_role": sorted(CONSOLE_VISIBILITY_ROLES),
            },
        })
    return rows


def status_row(check_id: str, status: str, detail: str, evidence: Any = None) -> dict[str, Any]:
    row = {"check_id": check_id, "status": status, "detail": detail}
    if evidence is not None:
        row["evidence"] = evidence
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--service", default="daimon-ion-kernel")
    parser.add_argument("--target-user", action="append", default=[])
    parser.add_argument("--agent-resource", default=None)
    args = parser.parse_args()

    load_local_env(ROOT / ".env")
    deploy_summary = load_json(DEPLOY_SUMMARY)
    agent_summary = load_json(AGENT_DEPLOY_SUMMARY)
    gcloud = find_gcloud()
    env_principals = os.getenv("DAIMON_TEST_USER_EMAILS", "")
    target_principals = split_principals([env_principals, *args.target_user])
    project = args.project or os.getenv("GOOGLE_CLOUD_PROJECT") or deploy_summary.get("project")
    region = args.region or os.getenv("GOOGLE_CLOUD_LOCATION") or deploy_summary.get("region") or "us-central1"
    agent_resource = args.agent_resource or agent_summary.get("remote_agent_name")

    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if not gcloud:
        blockers.append("gcloud CLI is not installed or was not found at ~/google-cloud-sdk/bin/gcloud.")
        write_json({
            "ok": False,
            "proof_status": "google_user_access_blocked",
            "blockers": blockers,
            "warnings": warnings,
            "target_principals": target_principals,
            "checks": checks,
        })
        print(json.dumps(json.loads(OUT.read_text(encoding="utf-8")), indent=2))
        return 2
    checks.append(status_row("gcloud_present", "pass", "gcloud CLI is available.", gcloud))

    active_account, account_error = gcloud_text(gcloud, ["config", "get-value", "account"])
    configured_project, project_error = gcloud_text(gcloud, ["config", "get-value", "project"])
    project = project or configured_project
    if account_error:
        warnings.append(f"Could not read active gcloud account: {account_error}")
    if project_error:
        warnings.append(f"Could not read configured gcloud project: {project_error}")
    if not project:
        blockers.append("GOOGLE_CLOUD_PROJECT is missing and gcloud has no configured project.")

    if not target_principals:
        blockers.append("No target users configured; pass --target-user or set DAIMON_TEST_USER_EMAILS.")

    services: list[dict[str, Any]] = []
    service_names: set[str] = set()
    services_checked = False
    service_describe: dict[str, Any] = {}
    service_policy: dict[str, Any] = {}
    project_policy: dict[str, Any] = {}
    command_errors: list[str] = []

    if project:
        services_data, err = gcloud_json(
            gcloud,
            ["services", "list", "--enabled", "--project", str(project), "--format=json"],
        )
        if err:
            command_errors.append(f"services list: {err}")
        elif isinstance(services_data, list):
            services = services_data
            service_names = {str(item.get("config", {}).get("name", "")) for item in services}
            services_checked = True

        service_describe_data, err = gcloud_json(
            gcloud,
            [
                "run",
                "services",
                "describe",
                str(args.service),
                "--region",
                str(region),
                "--project",
                str(project),
                "--format=json",
            ],
        )
        if err:
            command_errors.append(f"cloud run describe: {err}")
        elif isinstance(service_describe_data, dict):
            service_describe = service_describe_data

        service_policy_data, err = gcloud_json(
            gcloud,
            [
                "run",
                "services",
                "get-iam-policy",
                str(args.service),
                "--region",
                str(region),
                "--project",
                str(project),
                "--format=json",
            ],
        )
        if err:
            command_errors.append(f"cloud run get-iam-policy: {err}")
        elif isinstance(service_policy_data, dict):
            service_policy = service_policy_data

        project_policy_data, err = gcloud_json(
            gcloud,
            ["projects", "get-iam-policy", str(project), "--format=json"],
        )
        if err:
            command_errors.append(f"project get-iam-policy: {err}")
        elif isinstance(project_policy_data, dict):
            project_policy = project_policy_data

    for error in command_errors:
        blockers.append(error)

    missing_apis = sorted(REQUIRED_APIS.difference(service_names)) if services_checked else []
    if services_checked and missing_apis:
        blockers.append(f"Required Google APIs not proven enabled: {missing_apis}")
    checks.append(status_row(
        "required_google_apis",
        "pass" if services_checked and not missing_apis else ("blocker" if missing_apis else "not_checked"),
        "Required APIs are enabled."
        if services_checked and not missing_apis
        else ("Some required APIs were not observed enabled." if missing_apis else "Required APIs were not checked because gcloud service listing failed."),
        {"required": sorted(REQUIRED_APIS), "missing": missing_apis, "checked": services_checked},
    ))

    cloud_run_url = (
        service_describe.get("status", {}).get("url")
        or service_describe.get("uri")
        or deploy_summary.get("cloud_run_url")
        or os.getenv("ION_CLOUD_RUN_URL")
    )
    cloud_run_public = public_invoker_present(service_policy)
    checks.append(status_row(
        "cloud_run_runtime_surface",
        "pass" if cloud_run_url else "blocker",
        "Cloud Run service URL is resolved." if cloud_run_url else "Cloud Run service URL was not resolved.",
        cloud_run_url,
    ))
    checks.append(status_row(
        "cloud_run_invoker_policy",
        "pass" if cloud_run_public else "warn",
        "Cloud Run allows public or authenticated-public invocation." if cloud_run_public else "Cloud Run is not public; direct target-user invoker roles are required.",
        {
            "public_invoker": cloud_run_public,
            "invoker_members": sorted(role_members(service_policy, CLOUD_RUN_INVOKER_ROLES)),
        },
    ))

    agent_service_account = agent_summary.get("service_account")
    checks.append(status_row(
        "agent_engine_resource",
        "pass" if agent_resource else "warn",
        "Agent Engine resource is known from deploy summary." if agent_resource else "Agent Engine resource was not found in local evidence.",
        {
            "agent_resource": agent_resource,
            "service_account": agent_service_account,
        },
    ))

    access_rows = build_access_rows(
        target_principals,
        service_policy=service_policy,
        project_policy=project_policy,
        cloud_run_public=cloud_run_public,
    )
    for row in access_rows:
        principal = row["principal"]
        if not row["cloud_run_invocation"]["ok"]:
            blockers.append(f"{principal} does not have proven Cloud Run invocation access.")
        if not row["vertex_agent_engine_access"]["ok"]:
            blockers.append(f"{principal} does not have a proven Vertex AI user/admin role.")
        if not row["console_project_visibility"]["ok"]:
            warnings.append(f"{principal} does not have a direct project visibility role in the fetched policy.")

    ok = not blockers
    proof_status = "google_user_access_ready" if ok else "google_user_access_blocked_or_incomplete"
    write_json({
        "ok": ok,
        "proof_status": proof_status,
        "project": project,
        "region": region,
        "service": args.service,
        "cloud_run_url": cloud_run_url,
        "gcloud": {
            "path": gcloud,
            "active_account_present": bool(active_account),
            "configured_project": configured_project,
        },
        "target_principals": target_principals,
        "runtime_identity": {
            "agent_engine_resource": agent_resource,
            "agent_service_account": agent_service_account,
            "cloud_run_service_account": service_describe.get("spec", {}).get("template", {}).get("spec", {}).get("serviceAccountName"),
        },
        "access_rows": access_rows,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "recommended_manual_actions": [] if ok else [
            "Add target tester emails with --target-user or DAIMON_TEST_USER_EMAILS.",
            "Grant each tester Vertex AI User or an equivalent least-privilege custom role if they must invoke Agent Engine directly.",
            "Grant Cloud Run Invoker on the dAimon service only if the service is not intentionally public.",
            "Re-run this script after console/IAM changes and attach the JSON receipt.",
        ],
        "docs": [
            "https://cloud.google.com/run/docs/reference/iam/roles",
            "https://cloud.google.com/vertex-ai/generative-ai/docs/access-control",
            "https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/access",
        ],
    })
    print(json.dumps(json.loads(OUT.read_text(encoding="utf-8")), indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
