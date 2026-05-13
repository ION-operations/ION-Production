# ION Custom GPT Knowledge Upload Strategy

Status: candidate operator strategy.

## Constraint posture

OpenAI's current help pages describe GPT knowledge uploads as capped by file count, file size, and token limits. The published pages currently disagree on whether the GPT knowledge file count is 10 or 20, so ION should use a conservative 10-file primary set and keep an optional expanded set ready.

## Recommended answer

Upload both:

1. A focused ION sandbox-carrier package.
2. A full repo/workspace snapshot package.

The sandbox package is the working/operator package. The full repo snapshot is the source/context package. This keeps the GPT easy to boot while still allowing deep reference when needed.

## Primary 10-file upload set

1. `ION_CUSTOM_GPT_SANDBOX_CARRIER_PACKAGE_<timestamp>.zip`
   - Purpose: boot instructions, indexes, action posture, machine-block rules, GPT input maps.
   - Role: first file to inspect.

2. `ION_PRODUCTION_WORKSPACE_SNAPSHOT_<timestamp>.zip`
   - Purpose: full `ION - Production` repo/workspace snapshot excluding secrets, git history, caches, node_modules, virtualenvs, raw logs, and quarantine raw evidence.
   - Role: full source context.

3. `ION_DEVELOPMENT_CORE_SOURCE_<timestamp>.zip`
   - Purpose: focused `ION_Developement` working ION kernel/source/docs/tests/context.
   - Role: sandbox working version / main ION implementation context.

4. `ION_GPT_ACTION_RELEASE_AND_BUILDER_INPUTS_<timestamp>.zip`
   - Purpose: canonical Action schema, GPT Builder inputs, release domain, install/rollback/auth checklists.
   - Role: Action recovery and Builder configuration source.

5. `DAIMON_WORKSPACE_CONTEXT_<timestamp>.zip`
   - Purpose: dAimon local/sibling app source, bridge docs, extension integrations, sample outputs.
   - Role: dAimon companion context.

6. `BROWSER_EXTENSION_CONTEXT_<timestamp>.zip`
   - Purpose: extension source/build/context for ChatGPT page companion, docs/projects/queue/drop zones.
   - Role: browser carrier implementation context.

7. `UI_CANON_AND_JOC_CONTEXT_<timestamp>.zip`
   - Purpose: JOC/UI canon, Helixion cockpit UI protocol, non-monolith law, screenshots/proofs if curated.
   - Role: UI/domain workflow context.

8. `AIMOS_ATLAS_WISDOMNET_CONTEXT_<timestamp>.zip`
   - Purpose: AIMOS, Atlas, WisdomNET, and adjacent intelligence/orchestration lineage.
   - Role: adjacent-system architecture context.

9. `ION_RESEARCH_AND_DOCTRINE_CONTEXT_<timestamp>.zip`
   - Purpose: context engineering white paper, ION continuity substrate explainer, doctrine/research papers.
   - Role: theory/doctrine context.

10. `ION_LATEST_STATUS_AND_RECEIPTS_<timestamp>.zip`
    - Purpose: latest status summaries, current manifests, recent receipts, blockers, release reports, not raw runtime spam.
    - Role: freshness layer.

## If only 5 files are practical

Use:

1. sandbox-carrier package
2. full workspace snapshot
3. ION development core source
4. GPT Action release/builder inputs
5. latest status and receipts

## If 20 files are available

Split large domains further by project and source posture rather than uploading one giant archive. Keep the sandbox package first.

## Full repo snapshot rule

The full repo snapshot is useful, but it should not be the only upload. A full snapshot alone makes the GPT search too broadly and miss the intended boot path. The sandbox package tells it how to use the full repo.

## Exclusions

Never upload:

- `.git/`
- `.env*`
- `ION_VAULT_LOCAL/`
- secret/vault/credential files
- `.venv/`
- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- raw logs
- raw quarantine evidence unless specifically curated
- huge generated artifacts unless selected

## Naming rule

Every zip should include:

- `START_HERE.md`
- `PACKAGE_MANIFEST.json`
- `SHA256SUMS.json`
- `SOURCE_POSTURE.md`
- `LATEST_STATUS.md` when applicable

## Practical operating rule

Treat the sandbox-carrier package as the working version. Treat full repo/project zips as source libraries. The GPT should boot from sandbox package indexes, then route into full project snapshots only when needed.
