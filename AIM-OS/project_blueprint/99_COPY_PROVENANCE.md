# Copy provenance

| Field | Value |
|--------|--------|
| **Destination** | `/home/sev/AIMOS - Builds/AIM-ION/` |
| **Primary source** | `/home/sev/AIMOS - Builds/AIM-OS-GIT/` |
| **Method** | `rsync -a` (archive: perms, times, symlinks, recursive) |
| **Tier** | A + B (full working tree from GIT, excluding regenerable artifacts) |
| **Date (workspace)** | 2026-04-05 |

## Excludes (regenerable / noisy)

- `node_modules/`
- `.venv/`
- `__pycache__/`
- `htmlcov/`
- `.pytest_cache/`
- `.coverage`
- `coverage.xml`

## Command (exact)

```bash
mkdir -p "/home/sev/AIMOS - Builds/AIM-ION"
rsync -a --info=progress2 \
  --exclude 'node_modules/' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude 'htmlcov/' \
  --exclude '.pytest_cache/' \
  --exclude '.coverage' \
  --exclude 'coverage.xml' \
  "/home/sev/AIMOS - Builds/AIM-OS-GIT/" \
  "/home/sev/AIMOS - Builds/AIM-ION/"
```

## Post-copy verification (automated)

```text
du -sh AIM-ION  →  ~2.6G (approx; depends on source state)
test -d AIM-ION/canon     → OK
test -f AIM-ION/lucid_mcp_server.py → OK
packages/joc/node_modules → absent (expected)
```

## Not copied (by design)

- Entire **AIM-OS-FRESH** tree (see `06_SATELLITE_AND_FRESH.md`).
- **`node_modules`** — restore with npm per package.

## Git working tree note

This copy is a **filesystem mirror** of `AIM-OS-GIT` at copy time (including whatever was on disk for unstaged changes). **`rsync` excluded every `node_modules/` directory.** If the source repository **tracks** files under a path named `node_modules/`, those paths will be **missing** here and `git status` may show deletions.

**Optional reset to match `HEAD` exactly** (discards uncommitted working-tree diffs in AIM-ION — confirm before running):

```bash
cd "/home/sev/AIMOS - Builds/AIM-ION"
git restore .
# git clean -fd   # removes ALL untracked files — do NOT run until project_blueprint/ is committed or copied aside
```

For a **pristine** clone next time, prefer `git clone` to AIM-ION path, then add `project_blueprint/` from this atlas.

## Git refoundation (orphan repo)

**Date:** 2026-04-05

The directory **`AIM-ION/.git`** was **deleted** and replaced with a **new** repository:

- `git init -b main`
- Initial commit: all paths allowed by `.gitignore` (~17k files); **no** prior commit history or **`origin`** remote.

**Documented last upstream pointer (informational only):**  
commit `812bc34ab41d2cf10674f33faa8976a0b5224554` on branch `aimos-march-2026-update` (AIM-OS).

Details: **`07_GIT_FOUNDATION.md`**, **`manifests/INITIAL_REPO_AUDIT.md`**.

---

## Next operator actions

1. Run **`03_FIRST_BOOTSTRAP.md`**
2. Set **git remotes** to your fork or canonical server
3. Optionally merge FRESH satellites — document here if you do
4. If `git status` noise matters, apply **Git working tree note** above deliberately
