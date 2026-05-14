# ION Transfer Ignore / Export Profiles v4.6

## Purpose

Folder capsules add local intelligence; export profiles keep transfers clean,
small, safe, and purpose-specific.

## Required surfaces

- `.ionignore`
- `ION_EXPORT_PROFILE.yaml`
- `ION_TRANSFER_MANIFEST.yaml`
- `ION_OMITTED_FILES.yaml`
- `ION_EXTERNAL_REFERENCES.yaml`
- `NEXT_CHAT_PROMPT.txt`

## Profiles

- minimal_continuity
- working_handoff
- full_reproducible
- public_safe

## Non-exportable boundary

Vaults, secrets, credentials, tokens, browser session data, local cache, and
hidden chain-of-thought are never exportable. Omitted relevant files are
recorded with reasons rather than forgotten.
