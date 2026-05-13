#!/usr/bin/env python3
"""Deploy the dAimon FastAPI kernel to Cloud Run.

This script keeps deploy evidence sanitary:
- it loads local `.env` values but never writes secrets to artifacts;
- it stores `MONGODB_URI` in Secret Manager instead of `--set-env-vars`;
- it writes a redacted deploy summary whether deploy succeeds or blocks.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env

SUMMARY_PATH = ROOT / "sample_outputs" / "cloud_run_deploy_summary.json"


def public_loaded_keys(keys: list[str]) -> list[str]:
    secret_terms = ("KEY", "TOKEN", "SECRET", "URI", "PASSWORD", "CREDENTIAL")
    return sorted(key for key in keys if not any(term in key.upper() for term in secret_terms))


def find_gcloud() -> str | None:
    found = shutil.which("gcloud")
    if found:
        return found
    local = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"
    return str(local) if local.exists() else None


def write_summary(payload: dict[str, Any]) -> None:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("schema", "daimon.cloud_run_deploy_summary.v0_1")
    payload.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
    payload.setdefault("accepted_state_changed", False)
    payload.setdefault("external_mutation_attempted", False)
    SUMMARY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_cmd(args: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        cwd=ROOT,
        check=check,
        capture_output=True,
    )


def gcloud_value(args: list[str]) -> str | None:
    try:
        result = run_cmd(args, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if value and value != "(unset)" else None


def safe_env_vars() -> str:
    values = {
        "ION_MODE": "cloud_run_live",
        "ION_MONGODB_ENABLED": "true",
        "MONGODB_DB": os.getenv("MONGODB_DB", "ion_continuity_bridge"),
        "MONGODB_COLLECTION_PREFIX": os.getenv("MONGODB_COLLECTION_PREFIX", ""),
        "MONGODB_VECTOR_INDEX": os.getenv("MONGODB_VECTOR_INDEX", "ion_continuity_vector_index"),
    }
    return ",".join(f"{key}={value}" for key, value in values.items())


def cloudbuild_config(image: str) -> Path:
    config_text = "\n".join([
        "steps:",
        "- name: gcr.io/cloud-builders/docker",
        "  args:",
        "  - build",
        "  - -f",
        "  - ion_kernel/Dockerfile",
        "  - -t",
        f"  - {image}",
        "  - .",
        "images:",
        f"- {image}",
        "",
    ])
    handle = tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml", encoding="utf-8")
    with handle:
        handle.write(config_text)
    return Path(handle.name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-deploy", action="store_true")
    parser.add_argument("--project", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--service", default="daimon-ion-kernel")
    parser.add_argument("--artifact-repo", default="daimon")
    parser.add_argument("--secret-name", default="daimon-mongodb-uri")
    parser.add_argument("--service-account", default=None)
    parser.add_argument("--allow-unauthenticated", action="store_true")
    args = parser.parse_args()

    loaded = load_local_env(ROOT / ".env")
    args.project = args.project or os.getenv("GOOGLE_CLOUD_PROJECT")
    args.region = args.region or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    args.service_account = args.service_account or os.getenv("DAIMON_CLOUD_RUN_SERVICE_ACCOUNT", "")
    gcloud = find_gcloud()
    if not gcloud:
        write_summary({
            "ok": False,
            "stage": "preflight",
            "blockers": ["gcloud CLI is not installed or not on PATH."],
            "safe_loaded_env_keys": public_loaded_keys(loaded),
            "secret_inputs_present": {"MONGODB_URI": bool(os.getenv("MONGODB_URI"))},
        })
        print(json.dumps(json.loads(SUMMARY_PATH.read_text(encoding="utf-8")), indent=2))
        return 2

    project = args.project or gcloud_value([gcloud, "config", "get-value", "project"])
    mongo_uri = os.getenv("MONGODB_URI")
    if not args.confirm_deploy:
        write_summary({
            "ok": False,
            "stage": "confirmation_required",
            "blockers": ["Rerun with --confirm-deploy to perform Cloud Run, Cloud Build, Artifact Registry, and Secret Manager mutations."],
            "project_resolved": bool(project),
            "region": args.region,
            "service": args.service,
            "secret_inputs_present": {"MONGODB_URI": bool(mongo_uri)},
        })
        print(json.dumps(json.loads(SUMMARY_PATH.read_text(encoding="utf-8")), indent=2))
        return 1
    if not project:
        write_summary({
            "ok": False,
            "stage": "preflight",
            "blockers": ["GOOGLE_CLOUD_PROJECT is missing and gcloud has no configured project."],
            "region": args.region,
            "service": args.service,
            "secret_inputs_present": {"MONGODB_URI": bool(mongo_uri)},
        })
        print(json.dumps(json.loads(SUMMARY_PATH.read_text(encoding="utf-8")), indent=2))
        return 2
    if not mongo_uri:
        write_summary({
            "ok": False,
            "stage": "preflight",
            "blockers": ["MONGODB_URI is missing; Cloud Run cannot query live dAimon continuity state."],
            "project": project,
            "region": args.region,
            "service": args.service,
            "secret_inputs_present": {"MONGODB_URI": False},
        })
        print(json.dumps(json.loads(SUMMARY_PATH.read_text(encoding="utf-8")), indent=2))
        return 2

    image_tag = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    image = f"{args.region}-docker.pkg.dev/{project}/{args.artifact_repo}/{args.service}:{image_tag}"
    commands_run: list[str] = []
    deploy_url: str | None = None
    try:
        run_cmd([
            gcloud,
            "services",
            "enable",
            "run.googleapis.com",
            "cloudbuild.googleapis.com",
            "artifactregistry.googleapis.com",
            "secretmanager.googleapis.com",
            "--project",
            project,
        ])
        commands_run.append("gcloud services enable run/cloudbuild/artifactregistry/secretmanager")

        repo_describe = run_cmd([
            gcloud,
            "artifacts",
            "repositories",
            "describe",
            args.artifact_repo,
            "--location",
            args.region,
            "--project",
            project,
        ], check=False)
        if repo_describe.returncode != 0:
            run_cmd([
                gcloud,
                "artifacts",
                "repositories",
                "create",
                args.artifact_repo,
                "--repository-format",
                "docker",
                "--location",
                args.region,
                "--description",
                "dAimon Cloud Run images",
                "--project",
                project,
            ])
            commands_run.append("gcloud artifacts repositories create")

        secret_describe = run_cmd([
            gcloud,
            "secrets",
            "describe",
            args.secret_name,
            "--project",
            project,
        ], check=False)
        if secret_describe.returncode != 0:
            run_cmd([
                gcloud,
                "secrets",
                "create",
                args.secret_name,
                "--replication-policy",
                "automatic",
                "--project",
                project,
            ])
            commands_run.append("gcloud secrets create")
        run_cmd([
            gcloud,
            "secrets",
            "versions",
            "add",
            args.secret_name,
            "--data-file",
            "-",
            "--project",
            project,
        ], input_text=mongo_uri)
        commands_run.append("gcloud secrets versions add")

        config_path = cloudbuild_config(image)
        try:
            run_cmd([gcloud, "builds", "submit", "--config", str(config_path), "--project", project, "."])
        finally:
            config_path.unlink(missing_ok=True)
        commands_run.append("gcloud builds submit")

        deploy_args = [
            gcloud,
            "run",
            "deploy",
            args.service,
            "--image",
            image,
            "--region",
            args.region,
            "--project",
            project,
            "--platform",
            "managed",
            "--set-env-vars",
            safe_env_vars(),
            "--set-secrets",
            f"MONGODB_URI={args.secret_name}:latest",
            "--format",
            "value(status.url)",
        ]
        if args.allow_unauthenticated:
            deploy_args.append("--allow-unauthenticated")
        if args.service_account:
            deploy_args.extend(["--service-account", args.service_account])
        deploy_result = run_cmd(deploy_args)
        deploy_url = deploy_result.stdout.strip() or None
        commands_run.append("gcloud run deploy")
    except subprocess.CalledProcessError as exc:
        write_summary({
            "ok": False,
            "stage": "deploy_failed",
            "project": project,
            "region": args.region,
            "service": args.service,
            "image": image,
            "commands_run": commands_run,
            "blockers": [exc.stderr.strip() or exc.stdout.strip() or str(exc)],
            "secret_inputs_present": {"MONGODB_URI": True},
            "external_mutation_attempted": bool(commands_run),
        })
        print(json.dumps(json.loads(SUMMARY_PATH.read_text(encoding="utf-8")), indent=2))
        return exc.returncode or 1

    write_summary({
        "ok": True,
        "stage": "deployed",
        "project": project,
        "region": args.region,
        "service": args.service,
        "image": image,
        "cloud_run_url": deploy_url,
        "commands_run": commands_run,
        "secret_inputs_present": {"MONGODB_URI": True},
        "external_mutation_attempted": True,
    })
    print(json.dumps(json.loads(SUMMARY_PATH.read_text(encoding="utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
