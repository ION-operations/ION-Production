# Remote and first push — checklist

**Full playbook (HTTPS, SSH, `gh`, troubleshooting):** [../08_GIT_WHEN_READY.md](../08_GIT_WHEN_READY.md)

**Status:** Run manually when an empty upstream repository exists. Local development does **not** require a remote.

## 1. Create an empty repository

On GitHub (or your host), create a **new empty** repo named e.g. `AIM-ION`.  
Do **not** initialize with README/license (avoid unrelated root commit).

## 2. Add `origin` and push

From this machine:

```bash
cd "/home/sev/AIMOS - Builds/AIM-ION"
git remote add origin https://github.com/<OWNER>/<REPO>.git
# or: git remote add origin git@github.com:<OWNER>/<REPO>.git

git push -u origin main
git push origin v0.1.0-aimion-root
```

## 3. Verify

```bash
git remote -v
git ls-remote --tags origin
```

## Optional: GitHub CLI next time

```bash
# after: sudo apt install gh && gh auth login
cd "/home/sev/AIMOS - Builds/AIM-ION"
gh repo create AIM-ION --private --source=. --remote=origin --push
git push origin v0.1.0-aimion-root
```

Adjust visibility (`--public` / `--internal`) to your policy.
