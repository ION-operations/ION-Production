# Supabase Folder Consolidation Map

Status: candidate consolidation map.
Date: 2026-05-13.

## Decision summary

There should be one active Supabase project root:

```text
/home/sev/ION - Production/ION_Developement/supabase
```

The quarantined folder should remain evidence only:

```text
/home/sev/ION - Production/quarentine/supabase
```

## Active root contents

```text
supabase/.gitignore
supabase/README_ION_LOCAL_SETUP.md
supabase/config.toml
supabase/live_schema_snapshots/ion_ops_live_schema_20260513.sql
supabase/migrations/001_initial_ion_ops.sql
supabase/migrations/002_dev_private_cockpit_read_policies.sql
supabase/migrations/003_ion_ops_authority_and_rpc.sql
supabase/migrations/004_ion_ops_api_grants.sql
supabase/migrations/005_ion_ops_cockpit_readmodel_fixes.sql
supabase/seed/001_ion_ops_bootstrap_seed.sql
supabase/tests/validate_initial_ion_ops_sql.py
```

Also observed:

```text
supabase/.temp/
```

`.temp/` is Supabase CLI local link/runtime metadata. It is not a second project
root.

## Quarantined root contents

```text
quarentine/supabase/README_ION_LOCAL_SETUP.md
quarentine/supabase/migrations/001_initial_ion_ops.sql
quarentine/supabase/seed/001_ion_ops_bootstrap_seed.sql
quarentine/supabase/tests/validate_initial_ion_ops_sql.py
```

## Comparison

```text
active file count: 20
quarantined file count: 4
active size: 160K
quarantined size: 40K
```

Identical:

```text
README_ION_LOCAL_SETUP.md
```

Divergent:

```text
migrations/001_initial_ion_ops.sql
seed/001_ion_ops_bootstrap_seed.sql
tests/validate_initial_ion_ops_sql.py
```

Missing from quarantine:

```text
config.toml
live_schema_snapshots/
migrations/002_dev_private_cockpit_read_policies.sql
migrations/003_ion_ops_authority_and_rpc.sql
migrations/004_ion_ops_api_grants.sql
migrations/005_ion_ops_cockpit_readmodel_fixes.sql
```

## Proposed action

After review, rename the quarantined folder to make its status impossible to
misread:

```text
/home/sev/ION - Production/quarentine/supabase
-> /home/sev/ION - Production/quarentine/supabase_legacy_pre_baseline_20260513
```

Do not merge it into the active repo.

Do not delete it until a cleanup receipt records file hashes and the operator
approves deletion.

## Cleanup receipt requirements

Before deletion, record:

```text
path
file_count
sha256 per file
reason_for_deletion
replacement canonical path
operator approval
timestamp
```

## Non-claims

This map does not delete, move, or merge Supabase files.
This map does not claim accepted state.
