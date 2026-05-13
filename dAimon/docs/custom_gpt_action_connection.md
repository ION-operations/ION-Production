# Custom GPT Action Connection

Status: setup-ready, explicit-use only
Date: 2026-05-10

## Goal

Connect the dAimon Companion Custom GPT to the existing ION Action Gateway so it
can read dAimon proof/status and submit only bounded, approved packets.

## Builder Steps

1. Open the dAimon Companion in the Custom GPT builder.
2. Go to Configure -> Actions.
3. Create or update the action.
4. Import the schema from:

```text
https://ion-actions.helixion.net/openapi.yaml
```

5. Configure auth as bearer/API-key auth using the existing
   `ION_ACTION_GATEWAY_TOKEN` value from the local gateway env file.
6. Test these operations first:

- `ionGatewayHealth`
- `ionGatewayDaimonVisibility`
- `ionGatewayPolicy`

7. Leave mutating operations disabled by behavior unless Braden gives explicit
   approval evidence for a bounded packet.

## Expected Safe Test

The useful dAimon test is:

```text
GET /projects/daimon/visibility
```

Expected result:

- dAimon repo present.
- Cloud Run live status visible.
- Agent Builder MongoDB MCP trace proof visible.
- Google user access readiness visible.
- Current blockers listed, or an empty blocker list.
- No secrets, tokens, MongoDB URI, raw service account JSON, or `.env` content.

## Non-Claims

- Importing the Action schema does not grant arbitrary local PC access.
- Tool visibility is not production authority or live execution authority.
- Custom GPT output remains candidate until dAimon proof, receipt, and
  settlement gates accept it.
