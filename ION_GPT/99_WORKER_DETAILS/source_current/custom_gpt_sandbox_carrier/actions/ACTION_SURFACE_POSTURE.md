# Action Surface Posture

The Custom GPT Action surface is a human-admin control surface. It is governed separately from the sandbox-carrier knowledge package.

## Current canonical install target

```text
ION_GPT/custom_gpt_action_gateway/openapi.yaml
```

## Forbidden install targets

Do not install domain fragments, examples, or old workpacket schemas into GPT Builder.

## Recovery requirement

Before any GPT Builder edit, generate and review a release bundle through `kernel.ion_action_schema_release`.

Required release artifacts:

- `ACTION_SCHEMA_RELEASE_REPORT.md`
- `COMBINED_OPENAPI_SCHEMA.yaml`
- `OPERATION_ID_MANIFEST.json`
- `GPT_BUILDER_INSTALL_SHEET.md`
- `GPT_BUILDER_ROLLBACK_SHEET.md`
- `AUTH_TOKEN_HANDOFF_CHECKLIST.md`
