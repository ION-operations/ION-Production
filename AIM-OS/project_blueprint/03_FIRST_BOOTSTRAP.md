# First bootstrap (after copy)

## 1. Python environment

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Adjust if your team uses `pyproject.toml` / Poetry / uv — follow existing org standards.

## 2. Node / frontend packages

At minimum, restore dependencies where you develop UI:

```bash
cd packages/joc && npm ci
cd ../browser-automation-service && npm ci
```

Repeat for any other `package.json` you touch (`npm ci` when `package-lock.json` exists, else `npm install`).

## 3. Smoke checks (optional but recommended)

- MCP / HTTP fallback and BAS: follow `PROJECT_TRUTH/06_operational_spine.md` and `docs/` runbooks.
- `pytest` subsets: run targeted suites before full-repo runs (large tree).

## 4. Git remotes

This copy includes **`.git`** from AIM-OS-GIT. Inspect and retarget:

```bash
git remote -v
```

Rename `origin`, add a new remote, or keep read-only mirror — **your** policy.
