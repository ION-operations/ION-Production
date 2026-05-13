# Evidence — Proof Register

## Verified Facts

| # | Claim | Confidence | Source | Date |
|---|-------|-----------|--------|------|
| E001 | AIM-OS-GIT has 63,786 files / 1.7GB | 1.0 | `find/du` output | 2026-03-24 |
| E002 | operation-victus has 7,929 files / 19MB | 1.0 | `find/du` output | 2026-03-24 |
| E003 | AIM-OS-FRESH has 110,507 files / 7.5GB | 1.0 | `find/du` output | 2026-03-24 |
| E004 | AIM-OS-GIT has 67 top-level directories | 1.0 | `ls` output | 2026-03-24 |
| E005 | 14 audit documents exist in AIM-OS-GIT | 1.0 | `fd *audit*` output | 2026-03-24 |
| E006 | 27 index/map documents exist in AIM-OS-GIT | 1.0 | `fd *index*` output | 2026-03-24 |
| E007 | ION runtime has 103 .py files in victus/ion/ | 1.0 | `fd *.py` output | 2026-03-24 |
| E008 | AIM-OS-GIT has 71 packages/ subdirectories | 1.0 | `fd` output | 2026-03-24 |
| E009 | Constitution has 39 articles (supreme law) | 1.0 | Deep-read | 2026-03-24 |
| E010 | Atlas defines L1-L8 load order, 32 canonical objects | 1.0 | Deep-read | 2026-03-24 |
| E011 | Navigator implements §7 loop: 7 steps with LLM augment | 1.0 | Deep-read navigator.py | 2026-03-24 |
| E012 | GovernedWrite has 10-stage pipeline (W1-W10) | 1.0 | Deep-read governed_write.py | 2026-03-24 |
| E013 | VIF κ-gating uses 4 criticality levels | 1.0 | Deep-read kappa_gate.py | 2026-03-24 |

## 2026-03-25 Code Audit — ION Source Verification

| # | Claim | Confidence | Source | Date |
|---|-------|-----------|--------|------|
| E014 | aether_engine.py imports GeminiAPIClient, has full cognitive loop (LISTEN/ROUTE/GOVERN/SPEAK) | 1.0 | `aether_engine.py:1-50` — imports at L27-37, docstring L1-18 | 2026-03-25 |
| E015 | aether_engine.py is 457 lines with `create_aether_engine()` factory | 1.0 | `aether_engine.py` total lines = 457 | 2026-03-25 |
| E016 | context_compiler.py is 446 lines with 3-tier compilation (Pinned/Working/Long-term) | 1.0 | `context_compiler.py` total lines = 446, authority-rank priority at L30-39 | 2026-03-25 |
| E017 | server.py L14: `from victus.ion.aether_engine import create_aether_engine` | 1.0 | `server.py:14` — exact import line | 2026-03-25 |
| E018 | server.py L36: `engine = create_aether_engine(ion_root=ion_root)` — uses real factory | 1.0 | `server.py:36` — exact factory call | 2026-03-25 |
| E019 | model.py is 941 lines (not 802), has `IonType.AGENT` at L51 | 1.0 | `model.py` total lines = 941, L51: `AGENT = "agent"` | 2026-03-25 |
| E020 | model.py L152-163: `AgentRole` enum (specialist/supervisor/domain_mgr/auditor/executive/oracle) | 1.0 | `model.py:152-163` — full enum listing | 2026-03-25 |
| E021 | model.py L91-95: backward-compatible enum aliases (A1_LOCAL, A3_CORE, A4_SYSTEM still exist) | 1.0 | `model.py:91-95` — aliases with deprecation comments | 2026-03-25 |
| E022 | gemini_api.py exists with real Gemini SDK integration and rate-limit retries | 1.0 | `gemini_api.py:1-300` — full module read | 2026-03-25 |
| E023 | data/.ion/ has 13 directories: .locks, archive, automations, branches, capsules, comms, evidence, intents, manifests, memory, protocol, specs, timeline | 1.0 | `list_dir` output | 2026-03-25 |
