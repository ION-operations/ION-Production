# Monorepo Migration Plan - 2026-05-13

Status: candidate_plan
Packet: PCKT-ION-WORKSPACE-MONOREPO-SOURCE-TRUTH-001

## Decision target

Make `/home/sev/ION - Production` the main ION workspace repo.

## Why

The project is now naturally organized as one workspace of cooperating surfaces, not one isolated kernel repo. The AI/operator workflow benefits from one root, one map, and one release/control boundary.

## Proposed phases

### Phase 0: Containment

- Freeze GPT Builder changes.
- Do not push broad integration deletions from `ION_Developement` alone.
- Keep quarantine as archive witness only.

### Phase 1: Evidence and backup

- Record nested repo branches/remotes/status.
- Create Git bundles for nested repos.
- Verify bundles.
- Generate workspace file count/size summary.
- Run a secret/path risk scan before first root commit.

### Phase 2: Root repo creation

- Initialize or promote `/home/sev/ION - Production` as the project repo.
- Use reviewed root `.gitignore`.
- Add `ION_WORKSPACE_MANIFEST.yaml`.
- Add root `AGENTS.md` and `START_HERE_FOR_ANY_AGENT.md` as mount entrypoints.

### Phase 3: Nested repo strategy

Preferred: absorb nested repo contents into the monorepo after bundle backup.

Options:

```text
flatten_absorb: keep files, remove nested .git after backup
history_preserve: use git subtree/import strategy where practical
submodule: keep separate Git identity only where needed
```

Recommended initial treatment:

```text
ION_Developement -> absorb into workspace monorepo
dAimon -> likely absorb unless external deployment repo needs independence
AIM-OS -> decide: absorb as archive/knowledge corpus or keep submodule/reference
```

### Phase 4: Path normalization

- Treat `../ION_GPT`, `../mcp`, etc. as workspace paths during transition.
- After root repo lands, convert docs and code to workspace-root-relative canonical paths where useful.
- Keep legacy path resolver for old packets and evidence.

### Phase 5: Validation

Run only after operator approval:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION_Developement/ION/04_packages PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q \
  ION_Developement/ION/tests/test_kernel_ion_workspace_paths.py \
  ION_Developement/ION/tests/test_kernel_ion_action_schema_release.py \
  ION_Developement/ION/tests/test_kernel_ion_custom_gpt_action_gateway.py
```

### Phase 6: First root commit

The first root commit should be a source-truth commit, not a feature commit.

Candidate message:

```text
PCKT: establish ION Production workspace source truth
```

## Hard stop conditions

- Secret file would be staged.
- Nested repo bundle missing.
- GPT Builder schema/auth lane touched.
- Quarantine treated as active source.
- Parent `/home/sev` Git repo used as source truth.
