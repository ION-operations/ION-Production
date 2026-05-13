# dAimon Credential Handoff

This project stays fail-closed until credentials are provided through the
runtime environment. Do not commit secrets.

## MongoDB Atlas

Required runtime values:

- `ION_MONGODB_ENABLED=true`
- `MONGODB_URI`
- `MONGODB_DB`
- `MONGODB_COLLECTION_PREFIX` if using a shared database
- `MONGODB_VECTOR_INDEX` if the judged demo uses Atlas Vector Search

The screenshots provided on 2026-05-09 show a MongoDB database user, an SRV
driver URI, and an Atlas API key pair. Treat them as sensitive. Rotate them
before making the repo public or recording a public demo.

For local testing, create an ignored `.env` file:

```bash
cp .env.example .env
```

Then fill the MongoDB values in `.env` locally. Do not commit `.env`.

Local readiness checks:

```bash
python scripts/run_mcp_trace_harness.py
python scripts/validate_mcp_trace_harness.py
python scripts/validate_mongodb_contract.py
python scripts/check_mongodb_live_readiness.py
```

Optional MongoDB sample seed, only after you intend to write candidate demo
records to Atlas:

```bash
python scripts/seed_mongodb_candidate_sample.py --confirm-candidate-write
```

Live evidence to capture:

- MongoDB MCP server name and tool call
- aggregate or vector-search filter payload
- returned continuity object IDs
- receipt IDs or proof hash attached to the answer
- exclusion proof for rejected, deferred, proof-debt, and witness-only objects

## Google Cloud / Gemini

Required runtime values:

- `GOOGLE_API_KEY` or `GEMINI_API_KEY` for the Gemini API handoff smoke
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `ION_CLOUD_RUN_URL`
- `GCP_SERVICE_ACCOUNT_JSON` if deploying through CI
- `ATLAS_PUBLIC_KEY` and `ATLAS_PRIVATE_KEY` if automating Atlas project checks

Deployment target:

```text
Gemini / Google Cloud Agent Builder
-> Cloud Run FastAPI dAimon kernel
-> MongoDB Atlas persistence
-> MongoDB MCP governed retrieval trace
```

Do not claim live Google Cloud, Agent Builder, MongoDB Atlas, or MCP execution
until the captured trace shows the actual tool call and returned objects.

Gemini API handoff proof:

```bash
python scripts/run_gemini_handoff_demo.py
python scripts/run_live_vertical_slice.py --confirm-live-run
```

These commands must not print or write API keys. The response is captured as
candidate output and remains non-inheritable until a later settlement accepts it.

## Arize / Phoenix Observability

Phoenix is the preferred first Arize lane for dAimon run tracing unless we
explicitly choose Arize AX later.

Local `.env` values:

- `PHOENIX_API_KEY`
- `PHOENIX_COLLECTOR_ENDPOINT`
- `PHOENIX_PROJECT_NAME=daimon`
- `PHOENIX_CLIENT_HEADERS` only if your Phoenix Cloud instance requires an
  explicit header

Optional Arize AX values, if using AX instead of Phoenix:

- `ARIZE_API_KEY`
- `ARIZE_SPACE_ID`
- `ARIZE_MODEL_ID`

Do not commit trace API keys. The first Arize proof should be an observability
receipt showing dAimon run spans, not a claim that Arize settles inheritance.

Local readiness check:

```bash
python scripts/check_phoenix_readiness.py
```

The script starts with `PHOENIX_COLLECTOR_ENDPOINT`. For the current Phoenix
workspace, use:

```text
https://app.phoenix.arize.com/s/crinkedart
```

If the base endpoint does not accept OTLP trace export, the script retries:

```text
https://app.phoenix.arize.com/s/crinkedart/v1/traces
```

## Azure / Azure OpenAI Optional Carrier

Optional local `.env` values:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_RESOURCE_GROUP`
- `AZURE_LOCATION`

Azure is not part of the current contest proof path. Treat it as an optional
future carrier surface until a dedicated adapter, receipt, and validation gate
exist.

## GitHub Secrets

Set secrets without putting values in chat or tracked files:

```bash
gh secret set MONGODB_URI --repo ION-operations/dAimon
gh secret set MONGODB_DB --repo ION-operations/dAimon
gh secret set GOOGLE_CLOUD_PROJECT --repo ION-operations/dAimon
gh secret set GOOGLE_CLOUD_LOCATION --repo ION-operations/dAimon
gh secret set GCP_SERVICE_ACCOUNT_JSON --repo ION-operations/dAimon
gh secret set ATLAS_PUBLIC_KEY --repo ION-operations/dAimon
gh secret set ATLAS_PRIVATE_KEY --repo ION-operations/dAimon
gh secret set PHOENIX_API_KEY --repo ION-operations/dAimon
gh secret set PHOENIX_COLLECTOR_ENDPOINT --repo ION-operations/dAimon
```

## GitLab Planned Connector

GitLab is a planned read-only expansion lane. Start with project metadata,
issues, merge requests, CI status, and security evidence. Do not grant write
scopes until a bounded write packet and approval receipt exist.

Local `.env` values:

- `GITLAB_BASE_URL`
- `GITLAB_PROJECT_ID`
- `GITLAB_TOKEN`

Recommended first token scope:

- `read_api`

The setup guide lives in `docs/gitlab_connection_readiness.md`.
