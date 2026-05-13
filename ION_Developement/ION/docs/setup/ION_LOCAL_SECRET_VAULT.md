# ION Local Secret Vault

Status: candidate_setup_doc
Date: 2026-05-13

## Local vault path

```text
/home/sev/ION - Production/ION_VAULT_LOCAL
```

This folder is local-only and ignored by Git. It is intended for machine-local secrets and credential handoff notes.

## Rules

- Never commit vault contents.
- Never print secret values in chat or logs.
- Agents may check whether required keys exist, but should report only presence/absence.
- Do not put Supabase service-role or secret keys into GPT Builder, OpenAPI schemas, docs, or commits.
- Do not store production credentials unless the operator explicitly decides the local machine is the authority for that secret.

## Suggested files

```text
ION_VAULT_LOCAL/.env.supabase.local
ION_VAULT_LOCAL/.env.action_gateway.local
ION_VAULT_LOCAL/.env.cloudflare.local
ION_VAULT_LOCAL/credential_sources.md
```

## Runtime loading posture

Runtime services should load secrets from environment variables or explicitly sourced local env files. Tracked ION code and docs should only name the required variable names.
