# Git — full playbook when hosting is available

**Use this when you are ready to connect AIM-ION to GitHub, GitLab, or another host.**  
Until then, **no remote is required**: local `main`, commits, and tags are valid. This document does not assume `gh`, SSH keys, or tokens are already configured.

---

## 1. What you have today (local-only is correct)

| Item | Expected state |
|------|----------------|
| Branch | `main` |
| History | Orphan repo (no AIM-OS graph); see `07_GIT_FOUNDATION.md` |
| Tag | `v0.1.0-aimion-root` on the first root commit |
| Remote | **None** until you add `origin` — not an error |
| Large dirs | `Documentation_Consolidated/`, `node_modules/`, `.venv/` follow `.gitignore` |

Verify locally:

```bash
cd "/path/to/AIM-ION"
git status
git branch --show-current
git tag -l
git remote -v    # empty until you add origin
git log --oneline -5
```

---

## 2. Preconditions on the host

1. Create a **new empty** repository (e.g. `AIM-ION` under your org or user).
2. **Do not** add a README, `.gitignore`, or license via the host UI (avoids a stray first commit you must merge).
3. Decide **HTTPS + PAT** or **SSH**. Enterprise may mandate one or the other.

---

## 3. First-time push (HTTPS)

Replace `OWNER` and `REPO` with your values.

```bash
cd "/path/to/AIM-ION"

git remote add origin https://github.com/OWNER/REPO.git

# Push all commits on main (you may have more than the root commit)
git push -u origin main

# Push the annotated root tag (and any other tags you care about)
git push origin v0.1.0-aimion-root
git push origin --tags   # optional: all tags
```

When prompted for password on GitHub, use a **Personal Access Token** (classic or fine-grained) with `repo` scope, not your account password.

---

## 4. First-time push (SSH)

```bash
cd "/path/to/AIM-ION"

git remote add origin git@github.com:OWNER/REPO.git
ssh -T git@github.com   # should greet you; fix keys if it fails

git push -u origin main
git push origin v0.1.0-aimion-root
```

---

## 5. GitHub CLI path (optional)

After `gh auth login`:

```bash
cd "/path/to/AIM-ION"
gh repo create REPO_NAME --private --source=. --remote=origin --push
git push origin v0.1.0-aimion-root   # if create did not push tags
```

Adjust `--public` or org: `gh repo create ORG/REPO ...`.

---

## 6. After the first push

| Task | Notes |
|------|--------|
| **Default branch** | Set `main` as default in host UI if needed. |
| **Branch protection** | Require PRs for `main`, status checks when CI exists. |
| **Do not** add old AIM-OS as second remote unless you intend upstream sync; use a **separate clone** of AIM-OS to avoid mistaken `push`. |
| **Collaborators** | Invite with least privilege; document in your runbook. |

---

## 7. Ongoing workflow (summary)

```bash
git pull --rebase origin main   # before starting work, when origin exists
# ... edit ...
git add -A
git status                      # confirm no secrets / huge binaries
git commit -m "feat: ..."
git push origin main
```

---

## 8. Troubleshooting

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| `remote origin already exists` | Second `git remote add` | `git remote remove origin` then re-add, or `git remote set-url origin <URL>` |
| `failed to push ... non-fast-forward` | Remote has commits you lack | Do **not** force-push blindly; inspect `git fetch origin` and `git log main..origin/main` |
| `tag already exists` | Tag pushed twice | Normal; use `git push origin v0.1.0-aimion-root` once, or delete tag on remote only if policy allows |
| `permission denied (publickey)` | SSH key not loaded / wrong account | `ssh-add -l`, fix `~/.ssh/config` host alias |
| `Authentication failed` (HTTPS) | Expired PAT or wrong scope | Regenerate token with `repo` access |

---

## 9. Related blueprint files

| File | Role |
|------|------|
| [07_GIT_FOUNDATION.md](./07_GIT_FOUNDATION.md) | Why orphan repo, policy |
| [manifests/REMOTE_PUSH_CHECKLIST.md](./manifests/REMOTE_PUSH_CHECKLIST.md) | Short copy-paste checklist |
| [manifests/INITIAL_REPO_AUDIT.md](./manifests/INITIAL_REPO_AUDIT.md) | Lineage table, file counts |
| [99_COPY_PROVENANCE.md](./99_COPY_PROVENANCE.md) | Rsync + refoundation |

---

## 10. Quick reference — one screen

```text
1. Empty repo on host (no README).
2. git remote add origin <URL>
3. git push -u origin main
4. git push origin v0.1.0-aimion-root
5. git remote -v && git ls-remote --tags origin
```

*End of playbook.*
