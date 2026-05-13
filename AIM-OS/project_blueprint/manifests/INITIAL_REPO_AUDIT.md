# Initial repository audit — AIM-ION orphan Git

**Generated:** 2026-04-05  
**Git:** fresh `main`, single root commit (no AIM-OS history).

**Current root commit:** run `git rev-parse HEAD` in this repo (embedding the hash in this file would desync on every amend).  
**Tracked files at last audit:** 17,095

---

## 1. Lineage (not in Git graph — record only)

| Field | Value |
|--------|--------|
| Prior upstream repo | `https://github.com/sev-32/AIM-OS.git` |
| Last known upstream commit (pre-cut) | `812bc34ab41d2cf10674f33faa8976a0b5224554` |
| Prior branch name | `aimos-march-2026-update` |
| Prior commit subject | `feat(mcp/joc): Expose V3 ION via endpoints and launch Cognitive Explorer dashboard` |
| Prior commit time | 2026-03-22 15:44:48 -0400 |
| Filesystem mirror | `rsync` from `AIM-OS-GIT` per `99_COPY_PROVENANCE.md` |

---

## 2. Index statistics (first commit)

| Metric | Value |
|--------|--------|
| **Tracked files** (`git ls-files`) | **17,095** (at root commit) |
| **Working tree on disk** (approx.) | **~1.8 GiB** (after removing old `.git`; excludes ignored corpora on disk) |
| `node_modules` in index | **0** |
| `Documentation_Consolidated/` in index | **0** (directory ignored by `.gitignore`) |

---

## 3. Tracked files by top-level prefix (approximate)

Counts from `git ls-files` first path segment. Note: **166** paths under `Documentation/` use **quoted** filenames (emoji / special names); they appear as a separate first-segment token in naive splits — combined human meaning is still under `Documentation/`.

| Prefix | Files (naive first segment) |
|--------|-----------------------------|
| `Documentation/` | 5,055 (+ 166 quoted-path entries → **5,221** documentation paths) |
| `knowledge_architecture/` | 3,370 |
| `packages/` | 1,980 |
| `ide_orchestration/` | 1,458 |
| `.agent/` | 1,119 |
| `cursor-addon/` | 627 |
| `archive/` | 498 |
| `Testing/` | 493 |
| `docs/` | 308 |
| `scripts/` | 294 |
| `north_star_project/` | 263 |
| `forensics_backups/` | 259 |
| `coordination/` | 201 |
| `canon/` | 162 |
| (other roots) | see full `git ls-files` |

Full machine listing (optional refresh):

```bash
git ls-files | awk -F/ '{print $1}' | sort | uniq -c | sort -nr
```

---

## 4. Major intentional exclusions (`.gitignore`)

Non-exhaustive; see root `.gitignore` for authority.

| Category | Examples |
|----------|----------|
| Dependencies | `node_modules/`, `.venv/` |
| Large doc corpus (on disk, not in Git) | `Documentation_Consolidated/` |
| Secrets / local | `.env`, `gmail.txt`, vault paths |
| Runtime JSON (often local-only) | `mcp_ai_messages.json`, `mcp_timeline_entries.json`, some `mcp_memory/index/tags/*.json` |
| Binaries / media | `*.pdf`, `*.zip`, model weights, video |
| Build artifacts | `IDE/src-tauri/target/`, `htmlcov/` |
| HHNI dumps | `**/HHNI_IDEA_INDEX.json` |

**Audit implication:** The repo on disk can still **contain** ignored directories (e.g. `Documentation_Consolidated/` from rsync); they are **not** part of this Git project unless you change policy.

---

## 5. Key spine files verified in index

- `lucid_mcp_server.py`
- `PROJECT_TRUTH/README.md`
- `canon/audits/system_audits/AUDIT_01_SYSTEM_MAP.md`
- `pyproject.toml`, `requirements.txt`, `Makefile`

---

## 6. Remotes

**None** after refoundation. Add only when the new canonical hosting exists:

```bash
git remote add origin <NEW-URL>
git push -u origin main
```

---

## 7. Re-audit commands

```bash
git ls-files | wc -l
git status
git remote -v
du -sh .
```
