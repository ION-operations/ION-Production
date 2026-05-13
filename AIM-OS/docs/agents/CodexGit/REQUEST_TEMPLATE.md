# CodexGit Request Template

Use this when requesting Git operations from `CodexGit`.

## Request

- Operation: [branch-rename | scoped-commit | push | cleanup | release-tag]
- Branch: `branch-name`
- Remote: `origin`
- Scope paths:
  - `path/one`
  - `path/two`

## Constraints

- Allow `--no-verify`: [yes/no]
- Allow branch deletion: [yes/no]
- Allow force push: [yes/no]
- Quintet gate mode: [strict | balanced | advisory]

## Validation Required

- [ ] Build
- [ ] Tests
- [ ] Parser/syntax checks
- [ ] None

## Deliverables

- [ ] Commit hash
- [ ] Push result
- [ ] PR URL
- [ ] Rollback command
