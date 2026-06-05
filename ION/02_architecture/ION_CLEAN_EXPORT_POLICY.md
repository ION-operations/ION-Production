# ION Clean Export Policy

Status: candidate
Authority: local packaging policy only; no accepted-state claim, production authority, live execution authority, deploy authority, push authority, or secrets authority.

## Purpose

Clean exports package reviewable source and state evidence from the current single-carrier sandbox root without carrying local secrets, vault material, dependency caches, bytecode, browser profiles, tunnel credentials, or raw operator inbox bulk.

The export is evidence for review. It is not accepted ION state and does not promote any report, packet, branch context, or Wave output.

## Source and Output Boundary

The builder operates from the active ION shell root where `pyproject.toml` and `ION/REPO_AUTHORITY.md` are siblings. Default output is outside that source root under `ION_EXPORTS_LOCAL/`.

Clean export output must remain workspace-local while staying outside the active repo. For the active production workspace this means:

- workspace root: `/home/sev/ION - Production`
- active repo root: `/home/sev/ION - Production/ION_Developement`
- preferred export root: `/home/sev/ION - Production/ION_EXPORTS_LOCAL`

Relative output paths resolve from the workspace root (`ion_root.parent`), not from arbitrary process cwd. The builder must refuse outputs that resolve outside the workspace root, outputs inside the active repo, and the legacy escaped path `/home/sev/ION_EXPORTS_LOCAL` unless a future explicit override authorizes it.

## Include By Default

- Kernel source under `ION/04_packages/kernel/`.
- Tests under `ION/tests/`.
- Public doctrine, architecture, registry, docs, and templates under `ION/01_doctrine/`, `ION/02_architecture/`, `ION/03_registry/`, `ION/docs/`, and `ION/07_templates/`.
- Selected root orientation files such as `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `pyproject.toml`, and `ION/REPO_AUTHORITY.md`.
- Redacted/current review reports and ledgers under `ION/05_context/current/reports/`.
- Immediate current-state JSON manifests under `ION/05_context/current/*.json`.
- Worker-shift sign-on, lease, and sign-off receipts under `ION/05_context/current/worker_shift/signons/`, `leases/`, and `signoffs/`.

## Required Review Evidence

A clean export should include these evidence files when present:

- `ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_REPORT.md`
- `ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_LEDGER.json`
- `ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md`
- `ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_LEDGER.json`
- `ION/05_context/current/reports/WAVE_003_PLAN_ONLY.md`

Wave 003 remains plan-only unless a separate explicit packet authorizes generation. A clean export must not create Wave 003 packages.

## Always Exclude

- `ION_VAULT_LOCAL/**`
- `.env*`
- `.git/**`
- `Needs_Routed/**` raw bulk by default
- `node_modules/**`
- `.venv/**`, `venv/**`, `env/**`
- `__pycache__/**`, `*.pyc`, `*.pyo`
- `.pytest_cache/**`, `.ruff_cache/**`, `.mypy_cache/**`, `.cache/**`
- browser profiles and host-local browser state
- tunnel credentials and credential-shaped local key material
- generated export output directories

`Needs_Routed/` may only be represented through redacted manifests or explicitly selected review artifacts in a separate packet.

## Secret Gate

The builder must scan every included file before creating an archive. It must refuse the export if an included file has a secret-shaped filename or raw secret-looking content. Findings must identify the path and rule without emitting secret values.

Excluded vault paths and `.env*` files must not be read to prove exclusion.

## Manifest Requirements

Each run emits a manifest payload with:

- export id and creation time;
- source root;
- dry-run flag;
- file count and byte count;
- archive path and SHA-256 when an archive is written;
- included file records with SHA-256 hashes;
- excluded path summary;
- warning list;
- secret-scan verdict;
- ION status verdict at export time;
- authority fields set to false for accepted state, production, live execution, deployment, push, and secrets.

Dry-run must report the same planned inclusion, exclusion, warning, secret-scan, and status data without creating a zip.
