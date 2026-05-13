# ION Custom GPT Cumulative Single-Diff Release Candidate

Created: 20260513T193224Z

## Purpose

This package consolidates all current Custom GPT boot/persona/front-door carrier patches into one release-candidate bundle and one cumulative diff.

## Base and final candidate

- Base: `source_packages/ION_CUSTOM_GPT_SANDBOX_CARRIER_PACKAGE_20260513T160555Z.zip`
- Final candidate: `source_packages/ION_CUSTOM_GPT_FRONT_DOOR_CARRIER_PRODUCT_CONTRACT_REPAIR_CANDIDATE_20260513T175345Z.zip`
- Extracted final tree: `final_candidate_tree/`

## Primary diff

- Patch: `cumulative_diff/ion_custom_gpt_cumulative_single_diff_20260513T193224Z.patch`
- Markdown audit view: `cumulative_diff/ion_custom_gpt_cumulative_single_diff_20260513T193224Z.md`

The patch is a single cumulative diff from the original sandbox carrier package to the v4 front-door carrier product-contract candidate. It was dry-run tested and applied against a clean base extraction; the patched tree matched the final v4 candidate exactly by SHA-256 file hashes.

## Included patch lineage

1. v1 boot-process repair
2. v2 active-sequence continuation repair
3. v3 Persona Return Gate repair
4. v4 front-door carrier product contract

Prior patch diffs, reports, and packets are preserved under `evidence/`.

## Validation

`validation/validation_20260513T193224Z.md` records:
- v4 regression tests: `11 passed`
- cumulative patch dry-run: exit `0`
- cumulative patch apply: exit `0`
- patched tree exact match: `True`

## Authority posture

Sandbox candidate only. This bundle does not claim accepted state, live execution authority, production mutation, GPT Builder update, Git update, or deployment.
