# CodexGit Operating Runbook

## 1) Intake

- Confirm target branch and remote.
- Confirm scope: exact files or exact subsystem.
- Confirm constraints: no history rewrite, no destructive cleanup unless approved.

## 2) Preflight Commands

Run from repo root:

```powershell
git branch --show-current
git remote -v
python scripts/git/codexgit_status_report.py
python scripts/git/quintet_pre_commit_gate.py --stage pre-commit
```

If branch is wrong:

```powershell
git branch -m <new-branch-name>
git push origin -u <new-branch-name>
git push origin --delete <old-branch-name>
```

## 3) Commit Curation In Dirty Trees

- Stage only intended paths with explicit `git add <file...>`.
- Verify staged set:

```powershell
git diff --cached --stat
git diff --cached
```

- If repo hook fails on unrelated policy gates, report exactly what failed and why.
- Use `--no-verify` only when explicitly justified and documented in commit report.

## 4) Push + Handoff

- Push to tracked branch.
- Provide PR URL.
- Include:
  - commit hash
  - scope summary
  - validation results
  - known residual risk

## 5) Rollback Strategy

Preferred in shared branches:

- `git revert <commit>`

Avoid unless explicitly approved:

- `git reset --hard`
- force push to rewrite published history

## 6) Definition of Done

- Branch naming is correct.
- Commit scope is explicit and minimal.
- Validation evidence is recorded.
- Push completed and PR link shared.
- No unrelated file loss.
