# MCP / Systemd / Browser Path Repair

Status: candidate repair note.
Date: 2026-05-13.

## Scope

This repair extends workspace path resolution after the integration promotion out
of:

```text
ION/09_integrations/
```

into workspace-level roots:

```text
../mcp/
../systemd/
../browser_extension/
```

## Updated surfaces

Systemd service status now resolves:

```text
../systemd/user
```

with legacy fallback for:

```text
ION/09_integrations/systemd/user
```

MCP connector contract now resolves:

```text
../mcp/chatgpt_connector
../mcp
```

for required-path and read/search visibility where appropriate.

It does not broaden the bounded patch write allowlist to sibling workspace roots.

Browser extension cockpit visibility now resolves:

```text
../browser_extension/ion_chatops_bridge
```

instead of assuming the old `ION/09_integrations` path.

## Updated files

```text
ION/04_packages/kernel/ion_local_service_status.py
ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py
ION/04_packages/kernel/ion_cockpit_view_model.py
ION/04_packages/kernel/ion_mcp_bridge_audit.py
ION/tests/test_kernel_ion_chatgpt_browser_mcp_action_openapi.py
ION/tests/test_kernel_ion_local_service_status.py
ION/tests/test_kernel_ion_chatops_action_schema.py
ION/docs/setup/ION_LOCAL_USER_SERVICES_SYSTEMD_RUNBOOK.md
```

## Remaining work

There are still stale documentation and historical references to:

```text
ION/09_integrations/
ION_CODEX FULL
```

These should be handled by a documentation/index sweep, not mixed into runtime
path repair.

## Non-claims

No services restarted.
No Action calls run.
No Supabase calls run.
No commit or push claimed.
No accepted-state claim.
