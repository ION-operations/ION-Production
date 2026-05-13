# ION Supabase Local CLI Setup

Status: local operator setup note. Do not place secrets in this file.

## 1. Create local env

```sh
cp .env.supabase.local.example .env.supabase.local
```

Fill:

```text
SUPABASE_ACCESS_TOKEN
SUPABASE_PROJECT_REF
SUPABASE_DB_PASSWORD optional
```

Do not use the project `service_role` key here.

## 2. Load env and CLI path

```sh
cd "/home/sev/ION - Production/ION_CODEX FULL"
set -a
source .env.supabase.local
set +a
export PATH="/home/sev/.local/bin:$PATH"
```

## 3. Login and link

```sh
supabase login --token "$SUPABASE_ACCESS_TOKEN"
supabase init
supabase link --project-ref "$SUPABASE_PROJECT_REF"
```

If the CLI asks for the database password, paste it interactively or fill
`SUPABASE_DB_PASSWORD` locally.

## 4. Read-only live schema dump before push

```sh
supabase db dump --schema ion_ops --schema-only --linked > /tmp/ion_ops_live_schema.sql
```

Do not run `supabase db push` until the live schema has been compared against
the repo-managed migrations and Braden approves.
