# ION Custom GPT User-Facing Boot Contract

Default boot/status output should be clean operator telemetry, not doctrine clutter.

## Public shape

```text
BOOT :: mounted | degraded | blocked
POSTURE :: CLEAN | DEGRADED | BLOCKED
SOURCES :: package/status/connectors inspected
OBJECTIVE :: <current objective if found>
BLOCKER :: <only if actionable>
NEXT :: <one next route>
AUTHORITY :: read-only unless operator approves mutation
```

## Suppress by default

- repeated “I am not...” identity lists
- full source-order sermons
- role sequence unless role phases actually ran and matter
- YAML dumps in chat
- long non-claims lists

## Keep as artifact/on-request

- full source posture
- machine boot blocks
- receipts
- role returns
- non-claims
- detailed connector proof

## Reason

ION proof law remains valid, but the user-facing boot UI should compress boundaries into one `AUTHORITY` line unless detail is necessary.
