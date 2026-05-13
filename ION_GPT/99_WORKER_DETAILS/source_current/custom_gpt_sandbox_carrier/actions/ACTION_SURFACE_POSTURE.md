# Action Surface Posture

The Custom GPT Action surface is a human-admin control surface. It is governed separately from the sandbox-carrier knowledge package.

## Current canonical install targets

GPT Builder currently uses two separate Action schemas:

```text
ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

## Forbidden install targets

Do not install domain fragments, examples, old workpacket schemas, or historical schemas into GPT Builder.

Do not use the former path below as an active install target:

```text
ION_GPT/custom_gpt_action_gateway/openapi.yaml
```

## Recovery requirement

Before any GPT Builder edit, generate and review a release bundle through `kernel.ion_action_schema_release` or the current ION_GPT release package.

Required release artifacts:

- `ACTION_SCHEMA_RELEASE_REPORT.md`
- `OPERATION_ID_MANIFEST.json`
- `GPT_BUILDER_INSTALL_SHEET.md`
- `GPT_BUILDER_ROLLBACK_SHEET.md`
- `AUTH_TOKEN_HANDOFF_CHECKLIST.md`
