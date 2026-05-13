# Design Heritage Quick-Reference Index

```
       ____. _____  __________  ____   ____.___.  _________
      |    |/  _  \ \______   \ \   \ /   /|   |/   _____/
      |    /  /_\  \ |       _/  \   Y   / |   |\_____  \
  |   |   /    |    \|    |   \   \     /  |   |/        \
  |___|___\____|__  /|____|   /    \___/   |___/_______  /
                  \/        \/                         \/
```

> This index links every document a tournament competitor needs.
> All paths are relative to the AIM-OS root.

---

## Tier 0 — Must Read Before Building

| Doc | Path | Why |
|-----|------|-----|
| **Tournament Rules** | `packages/joc-tournament/RULES.md` | 7 non-negotiable operational laws |
| **Codex Brief** | `packages/joc-tournament/builds/codex/CODEX_TOURNAMENT_BRIEF_2026-03-07.md` | The correct championship question |
| **UI Canon** | `knowledge/joc_master_blueprint/artifacts/architecture/binding_ui_canon.md` | 8 binding UI laws |
| **Panel Registry** | `packages/joc/src/store/panelRegistry.ts` | 12 panels, 12 workspaces — all canonical types |

---

## Tier 1 — Architecture Heritage

| Doc | Path | Size | Author |
|-----|------|------|--------|
| DACv2 Design Document | `ide_orchestration/prototypes/dac/V2_DESIGN_DOCUMENT.md` | 29KB | Dac |
| Best Ideas Synthesis | `ide_orchestration/prototypes/dac/BEST_IDEAS_SYNTHESIS.md` | 22KB | Dac |
| Novel UI Design Proposals | `ide_orchestration/research/NOVEL_UI_DESIGN_PROPOSALS.md` | 18KB | Sam |
| PDAS Proposal | `ide_orchestration/research/PDAS_PROPOSAL.md` | 17KB | Lex |
| Evolution Roadmap v2 | `knowledge/joc_master_blueprint/artifacts/planning/evolution_roadmap_v2.md` | KI | Team |
| Technical Audit | `knowledge/joc_master_blueprint/artifacts/technical/joc_technical_audit_and_inventory.md` | KI | Team |

---

## Tier 2 — Individual Agent Prototypes

| Agent | Layout Doc | Key Insight |
|-------|-----------|-------------|
| Aether | `ide_orchestration/prototypes/aether/IDE_LAYOUT_PROTOTYPE_AETHER.md` | Debug infra built-in, 5 AIM-OS structure panels, 3 code explorer variants |
| Max | `ide_orchestration/prototypes/max/IDE_LAYOUT_PROTOTYPE_MAX.md` | Everything is a panel. Drag/drop/resize. Layout presets. |
| Lex | `ide_orchestration/prototypes/lex/IDE_LAYOUT_PROTOTYPE_LEX.md` | AIM-OS as first-class citizen. PDAS. Contradiction detection. |
| Codex | `ide_orchestration/prototypes/codex/IDE_LAYOUT_PROTOTYPE_CODEX.md` | Architecture-first. 4-pane Lucid Orchestrator. Quality gates. |
| Rev | `ide_orchestration/prototypes/rev/REV_PROTOTYPE_DESIGN.md` | Research-driven. WCAG 2.1 AA. Performance-optimized. |
| Dac | `ide_orchestration/prototypes/dac/IDE_LAYOUT_PROTOTYPE_DAC.md` | Comprehensive hooks. V2 synthesis. 31-panel registry. |

---

## Tier 3 — Deep Dives

### Dac Phase Analyses
| Phase | Doc |
|-------|-----|
| Architecture | `ide_orchestration/prototypes/dac/PHASE1_ARCHITECTURE_ANALYSIS.md` |
| Features | `ide_orchestration/prototypes/dac/PHASE1_FEATURES_ANALYSIS.md` |
| Panels | `ide_orchestration/prototypes/dac/PHASE1_PANELS_ANALYSIS.md` |
| Mock Data | `ide_orchestration/prototypes/dac/PHASE1_MOCK_DATA_ANALYSIS.md` |
| Aether Analysis | `ide_orchestration/prototypes/dac/PHASE2_AETHER_ANALYSIS.md` |
| Codex Analysis | `ide_orchestration/prototypes/dac/PHASE2_CODEX_ANALYSIS.md` |
| Lex Analysis | `ide_orchestration/prototypes/dac/PHASE2_LEX_ANALYSIS.md` |
| Max Analysis | `ide_orchestration/prototypes/dac/PHASE2_MAX_ANALYSIS.md` |
| Rev Analysis | `ide_orchestration/prototypes/dac/PHASE2_REV_ANALYSIS.md` |
| Better Ideas | `ide_orchestration/prototypes/dac/PHASE4_BETTER_IDEAS_DISCOVERY.md` |

### AIM-OS Knowledge Items
| KI | Path (relative to knowledge/) |
|----|------|
| Oracle System | `joc_master_blueprint/artifacts/architecture/oracle_system.md` |
| Assistant Rail | `joc_master_blueprint/artifacts/implementation/assistant_rail_component.md` |
| Agent Builder UI | `joc_master_blueprint/artifacts/intelligence/agent_builder_ui.md` |
| MCP Integration | `joc_master_blueprint/artifacts/mcp_integration.md` |
| System Atlas | `joc_master_blueprint/artifacts/system_atlas.md` |
| SEER Integration | `joc_master_blueprint/artifacts/technical/seer_integration.md` |
| Agent Coordination | `joc_master_blueprint/artifacts/collaboration/agent_coordination_and_comms.md` |
| AI Editor | `joc_master_blueprint/artifacts/mission_control/ai_editor.md` |

---

## Tier 4 — Codebase Reference

### Shell Components
| Component | Path |
|-----------|------|
| TopBar | `packages/joc/src/components/layout/TopBar.tsx` |
| LeftIconBar | `packages/joc/src/components/layout/LeftIconBar.tsx` |
| LeftDrawerSystem | `packages/joc/src/components/layout/LeftDrawerSystem.tsx` |
| AssistantRail | `packages/joc/src/components/layout/AssistantRail.tsx` |
| BottomBar | `packages/joc/src/components/layout/BottomBar.tsx` |

### Stores
| Store | Path |
|-------|------|
| Panel Registry | `packages/joc/src/store/panelRegistry.ts` |
| JOC Store | `packages/joc/src/store/jocStore.ts` |

### Surface Engine
| Component | Path |
|-----------|------|
| All 8 components | `packages/joc/src/components/engine/Surface*.tsx` |

### Icons
| File | Components |
|------|-----------|
| `packages/joc/src/components/icons/index.tsx` | 28 SVG icon components |

### Shared Tournament Files
| File | Purpose |
|------|---------|
| `packages/joc-tournament/shared/types.ts` | Re-exported types + TruthState + workspace sets |
| `packages/joc-tournament/shared/ascii-art.ts` | 5 ASCII art styles for branding |

---

*Study the heritage. Respect the Canon. Answer the cockpit question. Build.*
