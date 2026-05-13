# AIMOS Branch External Lineage Question Set - 2026-03-13

Status: evidence-only lineage question set for `CONSOLIDATION-WORK-PACKAGE-02`

Purpose:
- turn visible branch and external ambiguity into concrete questions
- keep the questions tied to direct evidence
- avoid answering anything not verifiable from this machine

## Visible Branch Evidence Used

- current local checkout: `aimos-march-2026-update` at `4b9ae0935`
- local branches visible: `aimos-march-2026-update`, `clean-master`, `codexgit-mcp-fallback-offline-comms`, `master`
- visible remote refs: `origin/aimos-march-2026-update`, `origin/clean-master`, `origin/codexgit-mcp-fallback-offline-comms`, `origin/feature/phase-2-hhni`, `origin/main`, `origin/master`
- remote HEAD target: `origin/feature/phase-2-hhni`
- `origin/feature/phase-2-hhni` and `origin/main` point to the same visible commit `d07e9021e`
- operator-reported-only external branch/surface: other-laptop branch / JOC evolution

## Question Set

| QID | Evidence-based question | Evidence basis | Why unresolved in this pass |
|---|---|---|---|
| LQ-001 | Why is the active local checkout `aimos-march-2026-update` while remote HEAD points to `origin/feature/phase-2-hhni` instead of `origin/main` or `origin/master`? | local branch scan plus remote HEAD observation | branch names and HEAD target do not explain governance or intended integration order |
| LQ-002 | If `origin/feature/phase-2-hhni` and `origin/main` currently point to the same visible commit, is that equality intentional, temporary, or stale remote configuration? | both refs resolve to `d07e9021e` in the current scan | equal commit position alone does not explain intended branch roles |
| LQ-003 | What is the intended lineage relationship between `aimos-march-2026-update` and the remote refs `origin/main` and `origin/feature/phase-2-hhni`? | `aimos-march-2026-update` points to `4b9ae0935` while the two remote refs above point to `d07e9021e` | current machine shows divergence, not lineage intent |
| LQ-004 | Are `clean-master` and `codexgit-mcp-fallback-offline-comms` active consolidation branches, preserved historical branches, or branch-local slices whose truth has already been carried elsewhere? | both local and remote refs are visible with distinct commit subjects | ref presence does not reveal present-day status or ownership |
| LQ-005 | Is the operator-reported other-laptop branch represented by any remote not fetched into this checkout, any private remote, or any unshared local-only branch on another machine? | no visible local or remote ref matches the reported other-laptop branch | this machine cannot see off-machine refs that were never published or fetched |
| LQ-006 | Which branch currently holds the freshest JOC work: the visible local checkout, a visible remote ref, or the operator-reported other-laptop branch? | local repo contains JOC surfaces; operator also reported off-branch JOC evolution | no recency proof exists here for the off-machine work |
| LQ-007 | Which branch currently holds the freshest Echo Forge work: the visible local root `echo-forge-loop/` surface or an off-branch / off-machine variant? | local root surface exists; operator reported broader work across EchoForge | this pass has no access to off-branch or off-machine EchoForge lineage |
| LQ-008 | Which branch currently holds the freshest Antigravity extension work: the visible `packages/antigravity-extension/` tree or an off-branch / off-machine variant? | local package exists; operator reported broader work across the Antigravity extension | this pass has no access to off-branch or off-machine lineage |
| LQ-009 | Are the visible root/path mismatches, such as Echo Forge documentation still naming `apps/echo-forge-loop/`, the result of branch drift, path migration, or an unmerged external branch? | local docs and local tree disagree on Echo Forge path | current disk evidence shows collision, not its historical cause |
| LQ-010 | What remote or handoff path, if any, carries the operator-reported off-branch work back into the visible repo lineage? | Work Package 01 and external ambiguity register explicitly record off-branch/off-machine work | no fetchable ref, no linked remote, and no visible synchronization artifact in this pass answers that |

## Constraint

- these are lineage questions only
- they are intentionally unresolved in this pass
- they exist so later reconciliation can ask concrete, evidence-rooted questions instead of relying on folklore
