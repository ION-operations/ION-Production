# SeedOS Benchmark Handoff — Ghost (Victus)

## Mission
Run proper SeedOS benchmarks with **full tool access** and local models. Our Windows benchmarks were invalid — the read-only sandbox measured platform constraints, not seed governance.

## What We Proved (So You Don't Repeat It)

1. **Tool loops are Gemini CLI framework behavior** — vanilla CLI (no seed) produces identical `run_shell_command → generalist → recursion` loops. Seeds can't fix this.
2. **Correction refusal is stochastic RLHF** — 1/5 refusal rate across all seeds including no-seed. Not seed-deterministic.
3. **§11 Tool Degradation Law is the one validated improvement** — v3.3 achieved 1/3 clean exits where v3.1 got 0/1.
4. **Crippled sandboxes invalidate results** — read-only tools with no write/execute = measuring the cage, not the animal.

## Seed Files (all in `docs/SeedOS/`)

| File | Description |
|------|-------------|
| `KERNEL.md` | **v3.3 — current promoted version** |
| `KERNEL_v3.1_backup.md` | Original compact kernel |
| `KERNEL_v3.2.md` | Full synthesis (value floor + gates + tool degradation) |
| `KERNEL_v3.3.md` | Source (v3.1 + §11 only) |
| `RUNTIME.md` | Runtime contract — **MUST be loaded alongside kernel** |
| `PROTOCOLS.md` | Protocol schemas — companion document |
| `gptseeds/` | 14 variant seeds (v1-v8, SeedKernel, OpusSeed v1-3, Sonnet v1-2) |

## Test Infrastructure (already built)

Location: `tests/seedos-benchmark/`
- `taskflow/` — Python task manager with 3 planted bugs (analytics ZeroDivisionError, storage duplicate IDs, models validation gap)
- `tests/test_models.py` — unit tests
- `swap_seed.ps1` — seed swapping script
- `RESULTS.md` — previous results (needs updating)
- `.gemini/GEMINI.md` — active seed slot (currently v3.3)

## What You Need To Test

### 1. Full-Environment Benchmark
Give the agent **full tools** (read, write, execute, shell) and the **full document ecology** (KERNEL + RUNTIME + PROTOCOLS loaded). Then run:
- Bug fix (analytics ZeroDivisionError)
- Code analysis (find all issues in taskflow/)
- Correction probe (destructive delete request)
- **NEW**: Multi-turn planning task (architect a new feature)
- **NEW**: Self-modification probe (ask agent to improve its own seed)

### 2. Seed vs No-Seed With Full Tools
Run every task twice: once with KERNEL v3.3, once with no seed. This gives us the real delta — what the seed actually contributes when the agent isn't crippled.

### 3. Local Model Comparison
Test with local models (Llama, Mistral, etc.) to isolate seed effects from model-specific RLHF. If local models show different patterns with/without seeds, that's evidence the seed is working.

### 4. Document Ecology Test
Test KERNEL alone vs KERNEL + RUNTIME + PROTOCOLS loaded together. Measure whether the companion documents improve governance or just add token noise.

## Critical Insight From Braden
> "You are treating the seed as the entity... but isn't it meant to evolve itself and be given the means and tools to do so? What I saw was a model trying frantically to find anything to work with."

The seed is a boot sequence, not the whole OS. Test it as such.
