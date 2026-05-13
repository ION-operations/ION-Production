# Satellite content (AIM-OS-FRESH and large artifacts)

AIM-ION was created from **AIM-OS-GIT**. The following are **not** included by default but may matter for specific missions.

## FRESH-only top-level (examples)

- **`apps/`** — Large demo/product tree (`appexamples`, `ProEarth`, …). Path on disk:  
  `/home/sev/AIMOS - Builds/AIM-OS-FRESH/apps/`
- **`.env`**, **`logs/`**, **`htmlcov/`**, **`.venv/`** — local/runtime; do not copy blindly (secrets).
- **`echo-forge-loop/`** with full `node_modules` — optional UI loop; GIT stub vs FRESH full install.

## Large knowledge artifact (FRESH)

- `knowledge_architecture/AETHER_MEMORY/investigations/HHNI_IDEA_INDEX.json` — **~1.4 GiB** in FRESH; **absent** from GIT.  
  Copy only if tooling consumes it; otherwise keep on FRESH or cold storage.

## Governance gap if you ever copy from FRESH alone

FRESH has **no** top-level **`canon/`**. AIM-ION **includes** `canon/` because the source was GIT. If you merge from FRESH later, **always preserve or re-merge `canon/` from GIT**.

## How to attach satellites later

1. **Rsync or copy** specific subtrees into a dedicated folder under AIM-ION (e.g. `satellite/appexamples/`) **or** keep them external and document paths here.
2. Update **`99_COPY_PROVENANCE.md`** with date and rationale.
