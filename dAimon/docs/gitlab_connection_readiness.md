# GitLab Connection Readiness

Status: planned read-only setup
Date: 2026-05-10

## Goal

Add GitLab as a governed software lifecycle surface for dAimon without granting
merge, deploy, secret, or broad mutation authority.

## First Safe Connection

Use read-only setup first.

Required local values:

```text
GITLAB_BASE_URL=https://gitlab.com
GITLAB_PROJECT_ID=
GITLAB_TOKEN=
```

For self-managed GitLab, replace `GITLAB_BASE_URL` with the instance URL.

## Token Guidance

Create a GitLab project access token or personal access token with the smallest
scope that can read the target project.

Initial read-only target:

- `read_api`

Do not use broad write scopes until a write packet, approval evidence, and a
receipt path exist.

## dAimon Surfaces

GitLab objects become witness or candidate context first:

- issues
- merge requests
- CI pipelines
- job logs and artifacts
- security scan status
- review comments
- deployment evidence

## Proof Gates

Before claiming live GitLab integration:

- Read-only project metadata probe succeeds.
- Issue/MR fixture maps into dAimon continuity objects.
- CI/security status is cited in a receipt candidate.
- Mutating issue/comment/MR action remains disabled without operator approval.

## Non-Claims

- dAimon does not replace human code review.
- dAimon does not bypass CI, security review, or merge approval.
- GitLab token values must not be pasted into chat or committed.
