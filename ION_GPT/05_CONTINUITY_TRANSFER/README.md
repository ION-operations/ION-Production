# 05 Continuity Transfer

Use this folder when carrying an ION Custom GPT chat forward into a new chat.

## What this is

A continuity transfer package is a portable candidate handoff. It carries:

- boot result
- persona envelope
- sequence continuation
- project hash
- receipt summary
- proof manifest
- next-chat prompt

## New chat with no previous package

Start with `boot-sequence`. The GPT should report that no prior continuity package is mounted and create or request a new candidate continuity package before state-bearing work.

## New chat with a previous package

Attach the latest continuity transfer zip and use its `NEXT_CHAT_PROMPT.txt`.

The GPT must reuse the package `ion_project_hash`. If the hash is missing or conflicts, it should block and report the mismatch.

## Current local export folder

Generated continuity zips are built under:

```text
ION_EXPORTS_LOCAL/continuity_transfer/
```

A latest package copy or pointer may also appear in:

```text
LATEST_PACKAGE/
```

## Authority

Continuity packages are candidate evidence only. They do not grant production, deployment, live execution, secrets, or accepted-state authority.
