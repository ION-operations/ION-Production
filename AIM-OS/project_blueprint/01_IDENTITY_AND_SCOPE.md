# Identity and scope

## What AIM-ION is

**AIM-ION** is a **working copy** of the AIM-OS program material, created from **`AIM-OS-GIT`** with:

- **Full git history** (`.git` preserved).
- **Tier A + Tier B** content: runtime/code, scripts, tests, governance (`PROJECT_TRUTH`, `canon/`, `docs/`), full `Documentation/` and `Documentation_Consolidated/`, and `knowledge_architecture/` (as present in source at copy time).
- **Regenerable artifacts excluded** at copy time: `node_modules/`, `.venv/`, `__pycache__/`, `htmlcov/`, `.pytest_cache/`, coverage files.

## What AIM-ION is not

- **Not a rename of the upstream remote** — remotes in `.git/config` still point wherever GIT pointed; update intentionally if you fork.
- **Not a full mirror of AIM-OS-FRESH** — FRESH-only trees (e.g. top-level `apps/`, giant `HHNI_IDEA_INDEX.json`) are documented in `06_SATELLITE_AND_FRESH.md`, not bulk-copied here by default.

## Naming

- **AIM-ION** = this curated copy + blueprint folder.
- **AIM-OS-GIT** = source snapshot for this copy.
- **AIM-OS-FRESH** = expanded satellite tree for demos and local artifacts.

## Change policy

- Prefer **normal git workflow** inside AIM-ION once you set `origin` / branches to your policy.
- Keep **`project_blueprint/99_COPY_PROVENANCE.md`** updated if you re-sync from GIT or merge FRESH assets.
