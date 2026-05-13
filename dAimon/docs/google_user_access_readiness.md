# Google User Access Readiness

This gate separates proven runtime behavior from proven human/tester access.

The existing dAimon proof can show that Cloud Run, Agent Engine, Gemini, and
MongoDB-backed retrieval work. That does not automatically prove that a named
judge, collaborator, or tester can open the Google Cloud project, invoke the
deployed agent, or call the Cloud Run surface from their own account.

## Read-only Check

Run:

```bash
python scripts/check_google_user_access_readiness.py --target-user user@example.com
```

or set:

```text
DAIMON_TEST_USER_EMAILS=user@example.com,other@example.com
```

The script writes:

```text
sample_outputs/google_user_access_readiness.json
```

It checks only current state. It does not grant IAM, deploy, rotate secrets, or
mutate accepted dAimon state.

## What It Proves

- `gcloud` is available and can query the configured project.
- Required Google APIs are enabled for the dAimon runtime gate.
- The Cloud Run service can be resolved.
- Cloud Run invocation is either public or granted to the target principal.
- Target principals have a direct Vertex AI user/admin-style project role for
  direct Agent Engine use.
- The local Agent Engine deployment receipt identifies the runtime service
  account used by the proof agent.

## What It Does Not Prove

- Enterprise SSO or organization policy correctness.
- Least-privilege custom IAM design.
- That public Cloud Run access is the right release posture.
- That Google console UI sharing or Devpost judge access has been manually
  exercised in a browser.

## Manual Console Actions

If the readiness artifact reports blockers, use Google Cloud console or
`gcloud` to resolve them:

- Add testers to the project with `roles/aiplatform.user` or an equivalent
  least-privilege custom role if they need direct Vertex AI / Agent Engine use.
- Add `roles/run.invoker` on the dAimon Cloud Run service only if the service
  is not intentionally public.
- Add a project visibility role such as Browser or Viewer if testers need to
  inspect the project in console.
- Re-run the readiness script and attach the JSON receipt.

References:

- Cloud Run IAM roles: https://cloud.google.com/run/docs/reference/iam/roles
- Vertex AI generative access control: https://cloud.google.com/vertex-ai/generative-ai/docs/access-control
- Agent Engine deployed-agent access: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/access
