# AIMOS Genome Surface Family Matrix - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_08_2026-03-14`
Status: evidence-only comparative matrix

## Scope

This matrix compares the three required genome-surface families directly:

- flat single-file genomes
- per-agent directory genome surfaces
- layered `cores/` + `platforms/` + `affinities/` architecture

## Family Matrix

| Family | Primary shape | Major files or directories | Visible intended loading model | Strengths in portability, richness, clarity, maintainability | Obvious costs or complexity signals |
| --- | --- | --- | --- | --- | --- |
| Flat single-file genomes | One `*.genome.md` file per agent or specialist loaded as a self-contained identity package | Root-level files such as `sev.genome.md`, `codex.genome.md`, `composer.genome.md`, `aether.genome.md`, `gemini.genome.md`, `antigravity.genome.md`, and specialist genome files; `21` flat genome files totaling `2214` lines in the current root set | Representative flat files say "Load this at conversation start" and embed identity, authority, project map, correction vectors, platform reality, and sometimes explicit file/tool guidance in one document | Highest single-file portability and fastest direct startup clarity; easy to paste, ship, or load whole; broad coverage for both general agents and specialists | Identity, platform mechanics, and model-specific behavior are mixed together; cross-platform reuse is weak; duplicate maintenance risk is visible because root flat files coexist with per-agent and layered forms |
| Per-agent directory genome surfaces | One directory per agent combining genome, README/load order, context, instructions, north star, and sometimes dynamics, maps, or drift logs | `.agent/genomes/sev/`, `.agent/genomes/opus/`, `.agent/genomes/codex/`, `.agent/genomes/composer/`; visible file counts are `9`, `15`, `6`, and `4` respectively | READMEs define a load order such as README → memory/messages/timeline → context → genome → task-specific dynamics/instructions; directory contents provide context and role-specific auxiliary surfaces | Richest agent-specific continuity, operational nuance, and role-specific onboarding; strongest compatibility with current chat/capsule/context/status continuity habits | Structure is uneven by agent, so maintainability and loader simplicity vary; portability is lower than flat files because useful context is spread across multiple files and subdirectories |
| Layered core / adapter / affinity architecture | Deployed genome assembled from three separate files: universal core + platform adapter + model affinity | `.agent/genomes/cores/` (`5` files), `.agent/genomes/platforms/` (`4` files), `.agent/genomes/affinities/` (`4` files), plus `GENOME_PROTOCOL.md`, `PORTING_GUIDE.md`, and preserved `legacy/` single-file genomes; core/adapter/affinity files total `13` files and `1223` lines | `GENOME_PROTOCOL.md` and `PORTING_GUIDE.md` define explicit assembly: `{agent}.core.md + {platform}.adapter.md + {model}.affinity.md` | Strongest explicit portability-by-design, cross-platform reuse, and separation of concerns; best maintainability potential when platform or model behavior changes without rewriting identity | Highest conceptual complexity at startup because deployment requires composition; current continuity surfaces still live mostly in per-agent directories, so layered loading is cleaner in theory than in current repo-wide adoption |

## Direct Notes

- The flat family remains the broadest by count, with `21` visible root-level genome files.
- The per-agent directory family is the richest in local continuity surfaces because it carries context, instructions, and task-mode files next to the agent genome.
- The layered family is the clearest architectural separation, but the packet explicitly keeps it under comparison rather than silent canon promotion.
- `legacy/` preserves older single-file genomes as historical inputs, which reinforces that multiple families are intentionally visible at once.
