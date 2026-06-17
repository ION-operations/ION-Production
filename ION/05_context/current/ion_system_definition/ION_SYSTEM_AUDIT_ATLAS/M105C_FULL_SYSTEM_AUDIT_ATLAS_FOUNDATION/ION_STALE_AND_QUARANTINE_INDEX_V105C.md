# ION Stale / Quarantine / Defect Index v105C

Status: sandbox candidate index

## Confirmed Defect: Prose-Proof Return Intake

Confirmed files:

```text
ION/04_packages/kernel/ion_context_proof_gate.py
sha256: 89be39b92c39f4a59f29571c4e1223578863ead1b95a3a91db32799e2dd79cd0

ION/04_packages/kernel/ion_template_action_gate.py
sha256: bb1d1868db945a6fbb40e1c2d61dae3df341603129b77ca54026df563707a634

ION/04_packages/kernel/ion_carrier_task_return.py
sha256: 516e39db4f44d5aaf85023b7fa94713f8d2fb018597f01e86c6dc9c82f0e8a28

ION/tests/test_kernel_ion_context_proof_gate.py
sha256: 3529ca8ca1e5debf6938da5145c6ca4c4e3d3f0f69a1025972d01453796c756d
```

Defect statement:

```text
These gates validate model-written markdown as context/template/action proof.
They are useful as historical proof-shape gates but are not proof-native enough
for ION's current law.
```

Required repair direction:

```text
runtime emits machine proof
parser validates machine proof
AI return references proof artifacts
settlement inherits verified machine evidence
```

## Currentness Drift: vNext README / Front Door

Observed from sandbox:
- vNext top-level README is current through M102 in some sections and missing M103/M104/M105 as living-encyclopedia first-class currentness.
- M105B pointer binding package exists as candidate patch, not live state.

## Superseded Artifact: Side Encyclopedia Patch Trees

Rejected/superseded unless explicitly accepted as mirror/reference:

```text
ION_VNEXT/09_references/ION_ENCYCLOPEDIA/*
```

The canonical living encyclopedia path is under:

```text
ION/docs/encyclopedia/
```

## Witness / Source Pool Risks

- `Needs_Routed/` contains many candidate patches and zips; it is source-pool evidence, not active state.
- `ION Developement.zip` is broad but stale in embedded vNext.
- `ION_VNEXT_.zip` carries newer vNext/Domain Weave files.
- GPT Pro M105A/M106 bundle is witness material: salvage M106 advisory only after rebasing to v4.1.

