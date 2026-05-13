# ION Failure Report Entrance

Status: active current-context entrance.
Created: 2026-05-13.

## Purpose

This folder is the operator-facing entrance for serious ION workflow failures.

Use this entrance when a carrier, agent, workflow, Action surface, UI flow, queue
lane, or context package failure causes loss of trust, repeated operator burden,
or inability to continue work.

## Trigger conditions

Create or update a failure report before continuing implementation when any of
these occur:

- The operator reports trust is lost.
- The operator reports three consecutive failures or repeated bad instructions.
- A live control surface is replaced, broken, or made ambiguous.
- A candidate/template artifact is confused with a live install target.
- A GPT Action, MCP, queue, Supabase, browser-extension, or gateway lane mutates
  or attempts to mutate through the wrong authority path.
- An agent continues after an auth failure, schema failure, or explicit stop
  signal.
- The operator says they are unable to continue work because of the failure.

## Required carrier behavior

When this entrance is triggered, the carrier must stop normal implementation and
switch to failure posture:

1. Do not defend the prior action.
2. Do not continue live Action calls, queue work, deployments, or broad edits.
3. Preserve evidence.
4. Identify the exact failed instruction, artifact, or commit path.
5. Separate candidate/template output from accepted/live surfaces.
6. Document operator impact.
7. Document root cause and missing gates.
8. Define containment before recovery.
9. Resume only after the operator explicitly approves the recovery gate.

## Report format

Every failure report should include:

- Incident title.
- Date.
- Operator impact.
- Failed instruction chain.
- Affected files/surfaces.
- What was true.
- What the carrier incorrectly assumed.
- Root cause.
- Missing gates.
- Containment decision.
- Recovery prerequisites.
- Non-claims.

## Active reports

- `2026-05-13_GPT001_ACTION_SCHEMA_CONTROL_SURFACE_FAILURE.md`

## Operating rule

Three repeated errors against the same operator workflow is a hard stop.

The correct next output is a forensic report and containment plan, not another
implementation attempt.
