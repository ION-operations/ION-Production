# Active Path Reference Sweep

Status: candidate sweep note.
Date: 2026-05-13.

## Scope

This sweep continued the workspace reorganization repair after integrations were
promoted from:

```text
ION/09_integrations/
```

to workspace-level roots:

```text
../ION_GPT/
../browser_extension/
../mcp/
../systemd/
../Cursor/
../product_packager/
```

## Runtime-facing updates

Updated active tests and helper modules to use the workspace resolver or new
promoted paths for:

```text
Custom GPT Action OpenAPI
MCP Action OpenAPI
systemd templates
browser extension files
Cursor SDK files
product packager
MCP donor/current trunk audit
ChatOps docs browser aliases
Codex prompt/root wording
```

## Safety boundaries

The docs browser exposes promoted roots as named aliases:

```text
browser_extension
ION_GPT
mcp
```

It does not allow arbitrary `../` browsing from user-provided paths.

The bounded patch lane was not expanded to sibling workspace roots.

## Intentional legacy references

Some legacy references remain intentionally:

- path resolver mapping definitions
- legacy fallback paths
- historical tests that model old sandbox-return diffs
- archived reports
- prior current-context messages

These should not all be edited blindly.

## Remaining path-debt categories

### Git move/delete state

Git still sees the old `ION/09_integrations/*` paths as deleted. This needs a
commit strategy:

```text
either restore compatibility tracked copies
or commit a governed workspace promotion with a path registry and release note
```

### Historical docs

Many docs and old reports still mention:

```text
ION/09_integrations/
ION_CODEX FULL
```

These should be updated only in current setup docs and active registries first.
Historical receipts should remain as historical evidence unless explicitly
superseded.

### Service safety

Do not restart services until targeted validation confirms:

```text
Action Gateway can serve the promoted OpenAPI.
MCP preview/action schema can be read from promoted mcp root.
systemd status can find promoted templates.
browser extension projections can read promoted extension files.
```

## Non-claims

No services restarted.
No Actions called.
No Supabase calls run.
No commit or push claimed.
No accepted-state claim.
