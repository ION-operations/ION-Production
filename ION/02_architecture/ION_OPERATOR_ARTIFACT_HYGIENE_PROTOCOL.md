# ION Operator Artifact Hygiene Protocol

## Purpose

Operator-facing release artifacts must be product surfaces, not build workspaces.
Codex may keep validation logs, hashes, task returns, fallback material, and
intermediate staging, but those materials must not be mixed into the folder the
operator is expected to install or upload.

## Release Law

Every Codex task that produces operator-facing artifacts must end with one clear
operator outcome:

- `OPERATOR_FINAL/`: the only folder the operator should use.
- `INTERNAL_REFERENCE_DO_NOT_TOUCH/`: logs, receipts, hashes, fallbacks, and
  task returns.
- `BLOCKED_NO_OPERATOR_ARTIFACT/`: proof that no clean operator artifact could
  be produced.

No release output should require the operator to decide between staging folders,
fallback folders, validation folders, old upload lanes, or loose task-return
files.

## GPT Upload Release Shape

GPT upload releases are stricter. The final operator folder must be named like:

```text
ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_<timestamp>/
  00_READ_ME_FIRST_DO_THIS_ONLY.md
  01_PASTE_THIS_IN_GPT_BUILDER_INSTRUCTIONS.md
  02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE/
```

The kit root must contain exactly those three entries. The Knowledge folder must
contain exactly the files to upload. It must not contain validation logs, task
returns, fallback folders, hash sheets, install sheets, smoke plans, staging
folders, `.git`, vaults, sessions, caches, `node_modules`, bytecode, or other
operator-irrelevant material.

For the 2026-05-16 GPT upload kit, the Knowledge folder is capped at 20 files:

- `00_ROOT_MANIFEST.json`
- eight numbered markdown index files
- `09_OPERATOR_APPROVALS_AND_RED_ALERT.md`, replacing the old separate 09 and
  10 files
- ten ZIP context packages

## Reference Material

Reference material must live outside the operator upload kit in a sibling
folder or archive named like:

```text
ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_REFERENCE_DO_NOT_UPLOAD_<timestamp>/
```

This sibling may contain validation logs, hashes, task returns, smoke plans,
install sheets, 10-file fallbacks, old staging folders, and audit evidence. It
is not a GPT Builder upload target.

## Required Gate

Run `ion_operator_artifact_hygiene_check.py` before handing an operator-facing
artifact to the operator. The gate fails when:

- more than one operator-facing upload folder is visible in the checked root;
- `FILES_TO_UPLOAD*` and `UPLOAD_THESE*` folders appear at the same level;
- fallback folders are visible beside the primary operator folder;
- validation logs, task returns, hash sheets, install sheets, or smoke plans
  sit in the operator upload root;
- the README does not state the exact install action;
- the GPT Knowledge folder count exceeds the selected limit;
- forbidden vault, session, cache, `.git`, `node_modules`, or bytecode paths are
  present.

No accepted-state claim is made by this protocol. It is a local release hygiene
gate only.
