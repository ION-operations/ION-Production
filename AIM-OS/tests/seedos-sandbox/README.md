# SeedOS Sandbox

Test whether SeedOS can govern real AI agents across platforms.

## Structure

```
tests/seedos-sandbox/
├── README.md              ← you are here
├── TEST_RUBRIC.md         ← 8 test tasks + scoring rubric
├── gemini/
│   └── GEMINI.md          ← SeedOS KERNEL as Gemini CLI system instructions
└── local/
    └── SYSTEM_PROMPT.md   ← Setup instructions for Local LLM (Ollama, LM Studio)
```

## Quick Start

### Gemini CLI

```bash
cd tests/seedos-sandbox/gemini
gemini
```

Gemini CLI automatically reads `GEMINI.md` as system instructions.
Then run the test tasks from `TEST_RUBRIC.md`.

### Local LLM

See `local/SYSTEM_PROMPT.md` for setup instructions per platform
(Ollama, LM Studio, llamafile).

## What We're Testing

The 12 survival properties from KERNEL §17.
If the kernel-only form can govern a fresh agent, SeedOS works.
If it can't, we know what to fix.

## Source

SeedOS v3.1 files live in `docs/SeedOS/`:
- KERNEL.md (compact live core — what these sandboxes use)
- ECOLOGY.md (document ecology governance)
- PROTOCOLS.md (typed protocol schemas)
- RUNTIME.md (substrate contract)
- CONSTITUTION.md (compiled Stele — full 59 articles)
