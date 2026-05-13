# RELAY Mission Packet - Cursor Codex Host Verification - 2026-03-06

**Status:** Active candidate mission packet  
**Mission owner:** Sev  
**Assigned specialist:** RELAY  
**Recommended host:** GPT-5.4 in Cursor/Codex  
**Mission class:** Host verification / transport truth / instruction-path audit  
**Output location:** `.agent/sev/reports/RELAY_CURSOR_CODEX_HOST_VERIFICATION_CARD_2026-03-06.md`

---

## 1. Mission ID + Intent

**Mission ID:** `RELAY-001-cursor-codex-host-verification`

**Mission objective:** Produce one evidence-backed host verification card that explains how Cursor Codex actually receives AIM-OS instructions, tools, and MCP access, and how that differs from Cursor Composer and Codex CLI.

---

## 2. Northstar Mapping

This packet reduces one of the highest-friction coordination failures in AIM-OS: multiple agents assuming that "Codex" is one surface when it is actually several distinct runtimes with different control layers.

This supports:
- correct delegation
- fewer false MCP diagnoses
- safer future Codex-runtime hardening
- better per-host doctrine

---

## 3. Read This First

1. `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`
2. `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`
3. `.agent/sev/candidate_genomes/relay.genome.md`
4. `docs/CODEX_IDE_MCP_ONBOARDING_V1.md`
5. `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md`
6. `.agent/STARTUP.md`
7. `.agent/genomes/codex.genome.md`
8. `.cursorrules`
9. `.cursor/rules/base-rules.mdc`
10. `.cursor/rules/modes/COMPOSER.mdc`
11. `C:\Users\bombe\.codex\config.toml`
12. `C:\Users\bombe\.codex\rules\default.rules`

---

## 4. Scope Boundaries

## 4.1 In scope

- read-only inspection of Cursor Codex host behavior
- read-only comparison with Cursor Composer and Codex CLI config surfaces
- repo-tracked rule layers
- user-home config layers required to explain runtime truth
- one local report in `.agent/sev/reports/`

## 4.2 Out of scope

- editing home-directory host configs
- restarting MCP or IDE services
- changing `.cursor` rule files
- changing `.codex` rule files
- broad global-canon rewrites

---

## 5. Implementation Expectations

### Allowed behavior

- inspect repo files, user-home config, and host-visible instruction text
- verify whether the Cursor Codex lane has:
  - its own injected session instructions
  - inherited repo rules
  - inherited Codex CLI config
  - mounted MCP transport
- compare what is proven versus what is assumed

### Required verification behavior

- if MCP is visibly mounted in the target host, prove it with at least one simple successful tool call such as `get_memory_stats`
- if collaboration tools are mounted, verify one collaboration surface such as `get_ai_messages`
- if no tools are mounted, say so explicitly and identify the failure boundary

### Forbidden behavior

- claiming that Cursor Codex is equivalent to Codex CLI without evidence
- claiming that Composer rules automatically apply to Codex pane without evidence
- "fixing" the host instead of documenting it

---

## 6. Required Deliverable

Create:
- `.agent/sev/reports/RELAY_CURSOR_CODEX_HOST_VERIFICATION_CARD_2026-03-06.md`

Required sections:

1. **Executive summary**
   - 5-8 high-signal findings
2. **Instruction source map**
   - what is host-injected
   - what is repo-tracked
   - what is inherited from user-home config
3. **MCP/tool verification**
   - what transport exists
   - what proof was run
   - what succeeded or failed
4. **Divergence table**
   - Cursor Composer
   - Cursor Codex
   - Codex CLI
   - important differences
5. **Hardening recommendations**
   - exact next moves
6. **Verification notes**
   - files and surfaces actually checked

---

## 7. Suggested Verification Surfaces

- visible host instructions in the Cursor Codex session
- `.cursorrules`
- `.cursor/rules/*`
- `C:\Users\bombe\.codex\config.toml`
- `C:\Users\bombe\.codex\rules\default.rules`
- Cursor MCP cache under `C:\Users\bombe\.cursor\projects\...\mcps\`
- MCP execution proof if the host actually exposes it

---

## 8. Reporting Format

Every meaningful update from RELAY should use:

### A. What changed
- exact surfaces checked or report sections completed

### B. Assumptions
- any host behavior that could not be directly inspected

### C. Merge impact
- local-only, no runtime mutation

### D. Drift check
- confirm no host config was modified

### E. Validation result
- what transport/instruction claims are proven

### F. Next move
- immediate next verification step

### G. Deliverable summary
- What
- Where
- How to verify

---

## 9. Escalation Triggers

Escalate back to Sev if:
- the host appears to use instruction layers that cannot be inspected from the lane
- a change to user-home config would be required to continue
- the host proves materially different from the current Sev matrix
- the lane is asked to mutate runtime settings rather than verify them

---

## 10. Definition of Done

Mission is done when:
- the verification card exists at the specified path
- Cursor Codex versus Cursor Composer versus Codex CLI differences are clearly stated
- Sev can issue the next Codex hardening packet without repeating the same investigation
