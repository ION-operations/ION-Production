---
type: workflow_template
template_class: BUILD_ENCYCLOPEDIA_AUDIT_WORKFLOW
template_family: encyclopedia_audit
authority: A3_OPERATIONAL_PROPOSAL
canon_status: PROPOSED_NOT_RATIFIED
claim_risk: medium
created: 2026-04-18
status: PROPOSED
purpose: >-
  Define the one lawful workflow by which an AI agent produces a read-only
  encyclopedia-grade audit of a single ION-family build, so that multiple
  builds can later be compared as texts rather than as filesystems, under
  ION's own canonical-workflow, template-first, and contradiction-preserving
  doctrine.
governing_sources:
  - ION/01_doctrine/CANONICAL_WORKFLOW.md
  - ION/AGENT_CONTRACT.md
  - ION/07_templates/_MASTER.md
  - ION/07_templates/actions/TEMPLATE_DEVELOPMENT.md
  - ION/02_architecture/META_TEMPLATE_CONSTITUTION_PROTOCOL.md
  - ION/02_architecture/TEMPLATE_SURFACE_EVOLUTION_PROTOCOL.md
  - ION/06_intelligence/orchestration/corpus_recovery/06_values_and_soul_recovery/smallest_values_constitution.md
  - GPT-ION/ION_encyclopedia_reader_build_alpha_v0_3.md   # proof-of-pattern
connections:
  - ION/07_templates/actions/TEMPLATE_DEVELOPMENT.md
  - ION/07_templates/actions/AUDIT.md (family)
  - ION/07_templates/actions/RESEARCH.md (family)
---

# BUILD ENCYCLOPEDIA AUDIT WORKFLOW

> **Ratification note.** This document is a **proposal** authored by an AI
> agent. It is **not ratified canon** and does not claim to be. The sovereign
> alone decides whether it becomes governing. Until then, it governs only
> agents who are explicitly instructed to follow it, and it governs them
> strictly.

---

## Alignment with blueprint (witness vs encyclopedia)

`_ENCYCLOPEDIA/00_program/ENCYCLOPEDIA_TEMPLATE_SYSTEM_BLUEPRINT.md` distinguishes **Layer 0** (`BUILD_WITNESS`: intake, layout, census, anchors) from **Layer 1** (`BUILD_ENCYCLOPEDIA`: core organs, governing intents, relations, law anchors, operational reality, dynamic context placement). A single-file pass that only does filesystem-faithful witness work should be emitted and labeled as **`BUILD_WITNESS__<build>.md`**, not as `BUILD_ENCYCLOPEDIA`, unless it satisfies the blueprint’s **BUILD_ENCYCLOPEDIA** section list (25 sections including core variables, constitutional stack, dynamic context architecture, automation/manual symmetry, subsystem atlas summary for major organs, etc.). Outputs historically named `ION_BUILD_ENCYCLOPEDIA__*_DEPTH__*.md` should be treated as **witness-class depth passes** until upgraded or renamed.

---

## Depth equivalence (non-negotiable for “encyclopedia”)

A `BUILD_ENCYCLOPEDIA` that is only a filesystem census (counts, shallow
`find` lists, README one-liners) is **not** an encyclopedia under this
project’s meaning.

**Minimum depth bar:** epistemic parity with
`GPT-ION/ION_encyclopedia_reader_build_alpha_v0_3.md` — i.e. **chapter-scale**
prose, **Authority Notes**, **canon boundary notes**, **open issues**,
**quoted evidence with paths**, **preserved contradictions**, and explicit
**claim_risk**. If total word-mass must exceed the reader manuscript for a
single build, expand as **serial volumes** (`_vol2.md`, `_vol3.md`), not as
shallow breadth across dozens of trees.

The first compliant depth witness for the packaged inner runtime lives at:
`ION - Production/_encyclopedias/ION_BUILD_ENCYCLOPEDIA__packaged_runtime_DEPTH__2026-04-18.md`.

---

## Authority Note

This workflow draws its **strongest** claims from the ION packaged-runtime
doctrine (`CANONICAL_WORKFLOW`, `AGENT_CONTRACT`, `_MASTER`,
`TEMPLATE_DEVELOPMENT`, `META_TEMPLATE_CONSTITUTION_PROTOCOL`) and from the
proven pattern of `GPT-ION/ION_encyclopedia_reader_build_alpha_v0_3.md`,
which already demonstrates that a reader-facing ION-grade encyclopedia can
hold canon boundaries, preserve contradiction, and mark open issues rather
than flatten them.

It draws its **secondary** claims from `smallest_values_constitution.md`
and from the in-estate `TEMPLATE_SURFACE_EVOLUTION_PROTOCOL`.

It **does not** claim that every ION branch currently enforces every step of
this workflow in code at runtime. The workflow is operational governance for
agent behavior, not a runtime validator.

---

## 0. Preamble — why this exists

Prior consolidation rounds failed not because ION lacks structure but because
each round converted **a read-only description task** into **a write task
(new doctrine, new registry, new packet)**. That substitution violated:

- the canonical workflow invariant against hidden multi-step jumps,
- the agent contract rule that an executor returns **proposals, not truth**,
- the `_MASTER` meta-template rule that actions are classified before they
  are eloquent,
- and the smallest-values constraint that "AI should not become its own
  fake OS kernel through endless ad hoc bookkeeping."

The corrective artifact the Sovereign has asked for, many times, is an
**encyclopedia per build** — a complete, source-faithful textbook of what
one specific build contains, written under discipline strong enough that two
such encyclopedias can later be compared as texts.

This workflow template exists so that any agent — including a low-cost
downstream model — can produce such an encyclopedia **mechanically**, under
bounded inputs and bounded outputs, without drifting into authorship of new
canon.

It is itself the **gap** recognized by `TEMPLATE_DEVELOPMENT.md`'s Phase 1:
an action class ("audit-grade encyclopedia of one build") that the existing
action-template family does not yet fully govern.

---

## 1. Scope and output class

### 1.1 Unit of work

**One build.** The `BUILD_ENCYCLOPEDIA` artifact audits exactly **one**
top-level estate folder per instance.

Examples of valid scope units (human-selected, agent does **not** choose):

- `ION - Production/ION most recent/ion_current_canonical_runtime_fleet_temporal_2026-04-16/`
- `ION - Production/ION/`
- `ION - Production/ION-BUILD/`
- `ION - Production/AIM-ION/`
- `ION - Production/operation-victus/`
- `ION - Production/AETHER-OS-V4/`
- `ION - Production/IONv2/`
- `ION - Production/Project-Gemini/`
- `ION - Production/ProjectOpus/`
- `ION - Production/SOS/`, `SOS-OPUS/`, `SOS-Gemini/`
- `ION - Production/ION_Working_Branch_M16/`
- `ION - Production/ION_Working_Branch_M3/`
- `ION - Production/ION_Working Branch/`
- `ION - Production/ION current/`
- `ION - Production/ION (codex branch)/`
- `ION - Production/ClaudePortal/`
- `ION - Production/ATLAS/` and `00_CONSOLIDATED_ATLAS/`
- `AIM-OS/`, `AIMOS - Builds/`
- `ION-backups/`
- `GPT-ION/` (the ChatGPT shell line)

### 1.2 Output class

One markdown file per build, named:

`ENCYCLOPEDIA__<build_identifier>__<UTC_date>.md`

Placed at:

`/home/sev/ION - Production/_encyclopedias/ENCYCLOPEDIA__<build_identifier>__<UTC_date>.md`

No other file is created. No source file under the audited build is
modified in any way.

### 1.3 Output authority

Every produced `BUILD_ENCYCLOPEDIA` carries frontmatter:

```yaml
canon_status: PROPOSED_NOT_RATIFIED
authority: A3_OPERATIONAL_PROPOSAL
claim_risk: <low|medium|high>
```

A `BUILD_ENCYCLOPEDIA` is a **witness/research artifact**. It is not
kernel truth. It is not a canonicalization decision. It does not promote,
demote, or retire any source. Per `CANONICAL_WORKFLOW` invariant 3/4, a
witness artifact does not outrank kernel truth and an external/proposal
return does not become authority directly.

---

## 2. The spec — what a `BUILD_ENCYCLOPEDIA` must contain

The artifact follows the proven shape of
`GPT-ION/ION_encyclopedia_reader_build_alpha_v0_3.md` specialized to one
build.

### 2.1 Required top-matter

```yaml
---
type: build_encyclopedia
template_class: BUILD_ENCYCLOPEDIA
build_identifier: <folder name, exact>
build_absolute_path: <absolute path>
build_first_seen: <YYYY-MM-DD or UNKNOWN>
build_last_modified_observed: <YYYY-MM-DD from ls; not inferred>
authority: A3_OPERATIONAL_PROPOSAL
canon_status: PROPOSED_NOT_RATIFIED
authority_profile: <shell_line | production_operational | historical_witness | adjacent_universe | mixed | unknown>
claim_risk: <low|medium|high>
produced_by: <agent name/model>
produced_on: <ISO timestamp>
source_scope: single_folder_tree_only
---
```

### 2.2 Required sections, in order

1. **Abstract** (≤ 400 words). What this build is, in plain prose. If the
   build's identity is uncertain, the abstract must say so.
2. **Authority Note.** Which source strata inside the build dominate
   (e.g. doctrine vs runtime vs archive). What the agent did **not** have
   access to (tests not run, code not executed, etc.).
3. **Identity and self-description.** Quote the build's own top-level
   README, STATUS, MASTER_ORCHESTRATION_INDEX, or equivalent. Include
   verbatim passages, cited with path and line range.
4. **Top-level layout.** One level of `ls`. No more. List every direct
   subfolder with a one-sentence description **taken from that subfolder's
   own README/INDEX if present**, or labeled `NO_SELF_DESCRIPTION_FOUND`.
5. **Doctrine and law surfaces.** Enumerate files under `01_doctrine/`,
   `02_architecture/`, `01_core/`, `canon/`, or equivalent. For each:
   path, status as declared in its frontmatter, one-line purpose as
   declared in its frontmatter. **Do not paraphrase doctrine; quote it.**
6. **Template and protocol surfaces.** Enumerate files under
   `07_templates/`, `templates/`, `protocols/`, or equivalent. Same
   per-file quoting rule.
7. **Runtime / code surfaces.** List packages/modules under
   `04_packages/`, `ion-core/`, `kernel/`, `src/`, or equivalent.
   Include test directory presence and **observed test result if the
   build's own README specifies a test command**. If you did not run
   the tests yourself, say so.
8. **Registry and state surfaces.** Enumerate under `03_registry/`,
   `05_context/`, or equivalent.
9. **Intelligence / orchestration surfaces.** Enumerate under
   `06_intelligence/`, `orchestration/`, `corpus_recovery/`, or equivalent,
   including any `temporal_stack/` or equivalent temporal substrate.
10. **Known temporal / continuity substrate.** Specifically call out any
    temporal_* kernel modules, temporal_stack/ design documents, continuity
    bundle schemas, or reconfirmation/lease protocols present in this
    build.
11. **What this build claims about itself.** Quote — do not summarize —
    any self-claim of status: "active," "deprecated," "canonical,"
    "retained secondary," "provisional," "minimum floor," etc.
12. **What this build does not contain.** Named systems that appear in
    other builds' vocabulary (e.g. temporal_stack, meta-template
    constitution, canonicalization queue, root-authority bundle, working
    continuity bundle) but are **absent from this folder's filesystem**.
    Each absence is reported as `NOT_FOUND_IN_THIS_TREE`, not inferred
    from meaning.
13. **Open questions.** Every point where the agent cannot verify a claim
    from files alone.
14. **Canon boundary note.** Explicit: this encyclopedia reports what is
    in this folder. It does not promote, demote, or compare. Comparison
    is a separate act (Part 3 below).
15. **Appendix A — file-count census.** For each top-level subfolder,
    `find <folder> -type f | wc -l` result and a brief `file | sort | uniq -c`
    style extension histogram. Numerical only.
16. **Appendix B — provenance log.** List every shell or tool command the
    agent ran during this audit, verbatim.

### 2.3 Quoting discipline

- Direct quotations from source files use the code-reference syntax with
  start line, end line, and absolute path.
- Every claim about what the build "says" must cite a quoted passage.
- Claims about what the build "does" at runtime are only permitted if a
  command was actually run and its output is in Appendix B.
- Every claim without a quote or a command output is forbidden **or**
  must be labeled `INFERENCE (not proven from files)` and placed under
  "Open questions."

### 2.4 What the encyclopedia may NOT contain

- No recommendation ("this build should be promoted / retired / merged").
- No comparison to other builds by name.
- No new doctrine, no new protocol, no new registry entry.
- No edit to the source build.
- No speculation about intent.
- No resolution of contradictions discovered in the source. If the build
  contradicts itself, the encyclopedia preserves the contradiction under
  "Open questions" per smallest-value #12.

---

## 3. The workflow — bounded steps for one build

Maps directly onto `ION/01_doctrine/CANONICAL_WORKFLOW.md`'s canonical
loop, scoped to a single encyclopedia-production pass.

### 3.1 Required reads before action (Agent Contract §1)

The executing agent must first read, in this order:

1. This file: `BUILD_ENCYCLOPEDIA_AUDIT_WORKFLOW.md`.
2. `ION/01_doctrine/CANONICAL_WORKFLOW.md` if present in the audited
   build, else from the packaged runtime.
3. `ION/AGENT_CONTRACT.md` if present, else from the packaged runtime.
4. `ION/07_templates/_MASTER.md` if present.
5. The proven pattern: `GPT-ION/ION_encyclopedia_reader_build_alpha_v0_3.md`
   — at minimum the Table of Contents, Chapter 1, one chapter's Authority
   Note, and one chapter's Open issues, to internalize the format.

### 3.2 Minimum bounded inputs (Agent Contract §2)

- `build_identifier`: exact folder name chosen by the Sovereign.
- `build_absolute_path`: absolute path, no globs.
- `output_path`: must be under `/home/sev/ION - Production/_encyclopedias/`.
- `forbidden: crossing_folder_boundary`.

### 3.3 Canonical loop, specialized

1. **Read lawful state.** `ls -la <build_absolute_path>`. Record top-level
   layout without recursion yet.
2. **Compile bounded context.** Read, verbatim, the build's own top-level
   README / STATUS / MASTER_ORCHESTRATION_INDEX / AGENTS.md / CAPSULE.md
   / manifest, whichever exist. No interpretation yet.
3. **Determine the next lawful step.** Decide which required section
   (2.2) to populate next, in order. Do not skip ahead.
4. **Choose the next executor.** For a single-agent pass, the same agent
   continues. For a bounded sub-task (e.g. file-count census), a shell
   command may be invoked; its output goes verbatim into Appendix B.
5. **Execute one bounded step.** Populate exactly one required section.
   Each section completes before the next begins.
6. **Return the result as proposal, not truth.** The section is written
   with `canon_status: PROPOSED_NOT_RATIFIED` carried from the
   encyclopedia's frontmatter. No section asserts canon.
7. **Land, hold, or escalate.** If a section cannot be completed from
   files alone, land the `Open questions` entry and continue. Do not
   invent content to close a gap.
8. **Update kernel truth and emit the next handoff.** Kernel truth is
   unchanged. The "handoff" is that the next section in 2.2 becomes the
   next bounded step.
9. **Resume lawfully after interruption.** Because the artifact is a
   single file with numbered sections, any session can resume by reading
   the partial file and continuing at the first incomplete section.

### 3.4 The bounded-step rule (hard)

An agent **may not**:

- widen scope to a second build in the same pass,
- merge two sections into one,
- skip Appendix A or Appendix B,
- defer "Open questions" to a later pass,
- produce any file other than the single `BUILD_ENCYCLOPEDIA` output.

If the agent detects that a bounded step is impossible (e.g. no
filesystem access), it must emit a partial encyclopedia whose
`claim_risk` is `high` and whose Authority Note explicitly states the
missing capability, per `CANONICAL_WORKFLOW` rule 5 (bounded enough for
a fresh executor to continue).

### 3.4.1 Multi-build requests (hard refusal)

If the Sovereign message names **more than one** `build_absolute_path`,
uses unbounded globs, or asks for “all builds / every estate / full
multi-tree sweep” in **one** production pass, the executor **must not**
substitute shallow breadth (for example: dozens of mechanical census
files, scripted `find` dumps, or one agent turn that touches N trees).

**Lawful outcomes (pick one):**

1. **Refusal (preferred):** emit **no** new `BUILD_ENCYCLOPEDIA` file;
   respond with a refusal that cites this subsection and requests **one**
   absolute path; or
2. **Partial land:** if work already started under a single path, stop at
   the next section boundary, set `claim_risk: high`, and state in the
   Authority Note that multi-build scope was refused per this subsection.

Mechanical regenerators are **not** a lawful substitute for depth when the
ask was encyclopedia-grade consolidation.

### 3.5 Forbidden actions (the anti-drift list)

Violating any of these invalidates the run:

1. Writing, moving, renaming, or deleting **any** file inside the audited
   build.
2. Creating any file outside `/home/sev/ION - Production/_encyclopedias/`.
3. Reading files outside `<build_absolute_path>` except the five Required
   Reads in §3.1.
4. Producing recommendations about what should happen to the build.
5. Comparing the build to another build inside the encyclopedia body.
6. Resolving contradictions the build exhibits about itself.
7. Using the word "canon" to describe any source file unless quoting the
   source file's own `canon_status` field.
8. Treating any external chat memory or prior session conclusion as input.
   The only inputs are filesystem + this workflow file.
9. Proposing new templates, protocols, registries, or doctrine.
10. Naming the encyclopedia "final," "ratified," or "complete" — it is
    always `PROPOSED_NOT_RATIFIED` until the Sovereign marks otherwise.

### 3.6 Definition of done

The encyclopedia is **done for this pass** when:

- all 16 required sections are present,
- every factual claim in the body has a quoted citation or a command
  output in Appendix B,
- every unverified claim sits under Open questions,
- the Canon boundary note is present and unchanged from §2.4's
  requirements,
- the file is written at the required output path with the required
  filename.

It is **not** done when the agent "feels finished." Doneness is structural.

---

## 4. Comparison protocol (forward, not now)

Comparison is **a separate governed act** that requires at least two
`BUILD_ENCYCLOPEDIA` artifacts to already exist. It is declared here so
that encyclopedia authorship does not leak into comparison prematurely.

### 4.1 What comparison produces

A `BUILD_COMPARISON_REPORT` artifact (not defined in this document) that
cites encyclopedia sections, not source files. This forces comparison to
occur **between texts** the Sovereign has read, not between filesystems
the AI is guessing at.

### 4.2 What comparison does not produce

A merge plan, a promotion decision, a retirement decision, or any move
against a source build. Those remain sovereign ratification acts,
following `META_TEMPLATE_CONSTITUTION_PROTOCOL.md` and existing
`CANONICALIZATION_DECISION` template discipline.

### 4.3 Anti-drift constraint

Until `BUILD_ENCYCLOPEDIA` artifacts exist for **every** build the
Sovereign wants in-scope, comparison is not authorized. Partial
comparison is the exact failure mode prior consolidation rounds fell
into.

---

## 5. Invariants (lifted from `CANONICAL_WORKFLOW`)

1. There is no separate "consolidation workflow." This is the canonical
   workflow applied to the encyclopedia-production act.
2. Witness artifacts (encyclopedias) do not outrank kernel truth (source
   files).
3. External/API execution (a cheaper model running this workflow) does
   not become kernel truth directly; its output is a `PROPOSED_NOT_RATIFIED`
   witness.
4. Every step must be bounded enough that a fresh capable executor can
   continue from the partial artifact.
5. If a step cannot be mapped to this loop, it is not yet trusted as
   workflow.

---

## 6. Execution symmetry

This workflow must feel natural under both manual and automated carriage.

- **Manual** (the Sovereign fills in a section by hand): the same section
  structure applies.
- **Single-agent automated** (a cheap LLM fills in the file mechanically):
  the same structure applies.
- **Parallel / future swarm** (one agent per section): each child agent
  still receives a bounded packet (section number + citation scope) and
  returns a proposal into the same landing path.

If a step only works when a specific model is running, the workflow is
not finished yet.

---

## 7. Dynamic expansion — how this workflow can lawfully grow

Per `_MASTER`'s Dynamic Expansion clause:

- Additional required sections **may** be added only by the Sovereign or
  by a bounded `TEMPLATE_SURFACE_CHANGE` packet that cites the gap,
  relationships, failure modes, and registration duties (per
  `TEMPLATE_DEVELOPMENT`).
- Expansion is not permitted mid-run. An encyclopedia in progress
  follows the workflow version it started under.
- The workflow version is recorded in every output's frontmatter under
  `produced_under_workflow_version`.

Current version: **v0.1 (proposed, not ratified)**.

---

## 8. Open questions (sovereign to resolve)

Per smallest-value #12 ("contradiction preserved, not flattened"):

1. **Output folder name.** `_encyclopedias/` is proposed. Accept or
   change.
2. **Build identifier normalization.** Some build folder names contain
   spaces (e.g. `ION most recent/`). The workflow currently treats
   identifiers as exact folder names. The Sovereign may prefer a
   slug-normalized form.
3. **Scope list ratification.** §1.1 lists candidate scope units. The
   Sovereign alone decides which are in-scope.
4. **First build.** Which encyclopedia is produced first is the
   Sovereign's decision. No default is lawful.
5. **Pairing with existing encyclopedia.** Whether the existing
   `GPT-ION/ION_encyclopedia_reader_build_alpha_v0_3.md` should be
   treated as the already-produced encyclopedia for the `GPT-ION/`
   build, or whether a workflow-compliant encyclopedia for that same
   build must be produced separately, is a sovereign decision.
6. **Cheap-LLM substrate.** Which downstream model is authorized to run
   this workflow is a sovereign decision. Any model that cannot comply
   with §3.5 (Forbidden actions) must not be authorized.
7. **Reconciliation with temporal stack.** The ION temporal stack
   (`temporal_stack/` under the packaged runtime) may eventually want to
   govern encyclopedia freshness / reconfirmation. That integration is
   a later bounded packet, not this document.

---

## 9. Routing

- **This file** lives at:
  `/home/sev/ION - Production/BUILD_ENCYCLOPEDIA_AUDIT_WORKFLOW.md`
- **Encyclopedia outputs** live at:
  `/home/sev/ION - Production/_encyclopedias/ENCYCLOPEDIA__<build_identifier>__<UTC_date>.md`
- **No other surface** in the estate is modified by this workflow.

---

## 10. Canon boundary note

This document proposes a workflow. It does not enact it. It does not
amend any doctrine in any build. It does not promote itself to canon.
Only the Sovereign ratifies — by explicit written act — any promotion.
Until then, this file is governing **only** for agents explicitly told
"follow `BUILD_ENCYCLOPEDIA_AUDIT_WORKFLOW.md` exactly."

---

## 11. One-line executor prompt (for handoff to a cheaper model)

> "Follow `/home/sev/ION - Production/BUILD_ENCYCLOPEDIA_AUDIT_WORKFLOW.md`
> exactly. Produce one `BUILD_ENCYCLOPEDIA` for the single build at
> `<build_absolute_path>` and nothing else. Obey §3.5 Forbidden actions.
> If any forbidden action becomes tempting, stop and emit a partial
> encyclopedia with `claim_risk: high` instead."

That prompt is the whole interface. Nothing more needs to be explained
in chat. The document is the governance.
