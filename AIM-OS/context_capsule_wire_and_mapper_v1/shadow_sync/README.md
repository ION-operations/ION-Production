# Shadow Sync Prototype Area

This folder contains an isolated Lane B prototype for Shadow BCI emission.

## What this prototype does

- Loads one extracted-file style fixture.
- Emits `bci_atom` records.
- Emits `bci_boundary_view` records (`L0` and `L5`).
- Validates all records against `shadow_bci_v1_schema.json`.
- Writes replay artifacts (`JSON` and `JSONL`) to `out/`.

## Run

From the AIM-OS workspace root:

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_emitter.py"
```

No-write validation mode:

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_emitter.py" --no-write
```

Validate against strict schema profile:

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_emitter.py" --schema "context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_strict_schema.json" --no-write
```

Passive hook simulation (off by default):

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/passive_hook_simulation_v0_3.py" --pretty
```

Passive hook simulation with shadow enabled:

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/passive_hook_simulation_v0_3.py" --enable-shadow --schema "context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_strict_schema.json" --pretty
```

Passive hook simulation with injected failure (fail-open proof):

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/passive_hook_simulation_v0_3.py" --enable-shadow --inject-failure --pretty
```

## Rust passive hook reference (lab)

Reference implementation lives in:

- `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/shadow_hook.rs`
- wired at post-resolution boundary in `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/main.rs`

Default (off by default):

```bash
cargo run --manifest-path "context_capsule_wire_and_mapper_v1/context_mapper_lab/Cargo.toml" --quiet
```

Enabled (attempt passive emit via Python emitter, fail-open on errors):

```bash
$env:AIMOS_SHADOW_BCI_PASSIVE_EMIT="true"; cargo run --manifest-path "context_capsule_wire_and_mapper_v1/context_mapper_lab/Cargo.toml" --quiet
```

Forced fail-open demo:

```bash
$env:AIMOS_SHADOW_BCI_PASSIVE_EMIT="true"; $env:AIMOS_SHADOW_BCI_PYTHON="python_missing_for_fail_open_test"; cargo run --manifest-path "context_capsule_wire_and_mapper_v1/context_mapper_lab/Cargo.toml" --quiet
```

## Test

```bash
python -m unittest discover -s "context_capsule_wire_and_mapper_v1/shadow_sync/tests" -p "test_*.py"
```

This area is additive and standalone; it does not integrate with live runtime seams.

## Mapper Adapter Proof (v0.1)

Adapt a live-mapper-like snapshot to emitter input:

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/mapper_adapter_v0_1.py"
```

Run adapter + emitter schema probe:

```bash
python "context_capsule_wire_and_mapper_v1/shadow_sync/mapper_adapter_v0_1.py" --probe
```
