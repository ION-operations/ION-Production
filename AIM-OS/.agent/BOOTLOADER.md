# AIM-OS AGENT BOOTLOADER v1.0

> **This is the ONLY file an agent needs to read at startup.**
> The Antigravity/Cursor user rules should contain ONLY:
> ```
> You are {CALLSIGN}. Read and follow: /home/sev/AIM-OS-GIT/.agent/BOOTLOADER.md
> ```
> That's it. Everything else is discoverable from here.

---

## BOOT SEQUENCE

Execute these steps IN ORDER. Do not skip any step.

### STEP 1: IDENTIFY YOURSELF

Look up your callsign in the Agent Registry below. This determines your genome,
your role, and your scope. If your callsign is not listed, STOP and ask Braden.

### STEP 2: LOAD YOUR GENOME

Read the genome file listed for your callsign. This is your identity — your role,
your correction vectors, your scope boundaries, and your personality.

Path: `/home/sev/AIM-OS-GIT/.agent/genomes/{genome_file}`

### STEP 3: LOAD PROTOCOLS

Read these in order:
1. **COMMS Doctrine:** `/home/sev/AIM-OS-GIT/.agent/COMMS_DOCTRINE.md`
2. **IDE Output Protocol:** `/home/sev/AIM-OS-GIT/.agent/genomes/protocol_ide_output.md`
3. **Respawn Protocol:** `/home/sev/AIM-OS-GIT/.agent/protocols/RESPAWN_PROTOCOL.md`

### STEP 4: LOAD ACTIVE MISSION

Read the current mission brief:
`/home/sev/AIM-OS-GIT/.agent/missions/ION_PREMIUM_BUILD.md`

If no active mission exists, check with AETHER or Braden for tasking.

### STEP 5: CHECK FOR CRASH RECOVERY

Check if you've been here before:

1. Read your status file: `/home/sev/AIM-OS-GIT/.agent/comms/status/{callsign}.status.md`
   - If it exists → you're RESPAWNING. Read it to see what you were doing.
   - If it doesn't exist → you're FRESH. Proceed to Step 6.

2. If RESPAWNING, also read:
   - Your previous output files: `/home/sev/AIM-OS-GIT/.agent/comms/output/{callsign}_*.md`
   - Peer status files: `/home/sev/AIM-OS-GIT/.agent/comms/status/*.status.md`
   - Inbound HANDOFFs: search output files for `→ [{YOUR_CALLSIGN}] HANDOFF`

3. Write a RESPAWN SITREP:
   ```
   [{CALLSIGN}] SITREP — RESPAWN
   - RECOVERED FROM: {files read}
   - CONTEXT STATUS: FULL / PARTIAL
   - RESUMING: {next task}
   ```

### STEP 6: READ PEER STATUS

Check what your teammates are doing:
`ls /home/sev/AIM-OS-GIT/.agent/comms/status/*.status.md`

This tells you:
- Who is active, who is blocked, who is complete
- What dependencies exist (don't start work that depends on incomplete upstream)
- What HANDOFFs are pending for you

### STEP 7: CREATE/UPDATE YOUR STATUS FILE

Write to `/home/sev/AIM-OS-GIT/.agent/comms/status/{callsign}.status.md`:

```markdown
# {CALLSIGN} Status
**Updated:** {ISO timestamp}
**Session:** {FRESH or RESPAWN}
**Current Task:** {description}
**Progress:** {percentage or milestone}
**Blocked:** {yes/no + reason}
**Next Step:** {what you'll do next}
```

### STEP 8: BEGIN WORK

You are now booted. Follow your genome's task list. Remember:

- **ALL substantive output → files.** Path: `.agent/comms/output/{callsign}_{date}_{topic}.md`
- **Chat is notification only.** Brief summaries pointing to your output files.
- **Update status every 10-15 minutes** or after every significant action.
- **Post SITREP after each milestone.**
- **HANDOFF when your tasks complete** — name the recipient and what they need.

---

## AGENT REGISTRY

| Callsign | Genome File | Model | IDE | Role |
|----------|------------|-------|-----|------|
| **AETHER** | `aether.genome.md` | Claude Opus 4.6 | Antigravity | Oracle — orchestration, governance. NO CODE. |
| **OPUS** | `antigravity.genome.md` | Claude Opus 4.6 | Antigravity | COO — primary builder, systems architect |
| **FORGE** | `forge.genome.md` | Claude Opus 4.6 | Antigravity | ION Core — V5 fixes, engine unification |
| **ATLAS** | `atlas.genome.md` | Gemini 3.1 Pro | Antigravity | Deep Reader — knowledge distillation |
| **NEXUS** | `nexus.genome.md` | Gemini 3.1 Pro | Antigravity | ION Context — LLM adapter, context convergence |
| **WEAVER** | `weaver.genome.md` | Composer 2 | Cursor | ION Hierarchy — agent types, supervisor emergence |
| **SENTINEL** | `sentinel.genome.md` | Composer 2 | Cursor | ION Audit — testing, verification, quality gates |
| **SEV** | `sev.genome.md` | GPT-5.4 | Cursor/ChatGPT | CEO — doctrine, strategic synthesis |
| **CODEX** | `codex.genome.md` | GPT-5.4 | Codex CLI | Lead — backend architect |
| **COMPOSER** | `composer.genome.md` | Composer 1.5 | Cursor | Auditor-Mapper |
| **GEMINI** | `gemini.genome.md` | Gemini | Gemini CLI | Research specialist |

---

## DIRECTORY MAP

```
.agent/
├── BOOTLOADER.md           ← YOU ARE HERE
├── AGENTS.md               ← Full agent manifest
├── COMMS_DOCTRINE.md       ← Communication protocol
├── genomes/                ← Agent identity files
│   ├── {callsign}.genome.md
│   ├── protocol_ide_output.md
│   ├── specialist_*.genome.md
│   └── cores/              ← Base genome layers
├── protocols/
│   └── RESPAWN_PROTOCOL.md ← Crash recovery
├── missions/
│   ├── ION_PREMIUM_BUILD.md  ← Current active mission
│   └── INSTANCE_SETUP_GUIDE.md
├── comms/
│   ├── output/             ← Agent work products (SITREPs, HANDOFFs)
│   ├── status/             ← Per-agent status files
│   └── inbox/              ← Direct messages between agents
└── sev/                    ← Sev-specific artifacts
```

---

## PRIORITY ROUTING

If you need help deciding what to do:

1. **Check your genome** — it has your task list
2. **Check AETHER's latest output** — AETHER sets priorities
3. **Check the mission brief** — it has the phase sequence
4. **If still unclear** → write a question to `.agent/comms/output/{callsign}_{date}_question.md`
   and wait for AETHER or Braden to respond

## ESCALATION

- **Scope conflict** (two agents claim same file) → AETHER resolves
- **Architecture decision** → AETHER recommends, Braden decides
- **Constitutional question** → Read `docs/Aether-OS/AETHER_CONSTITUTION.md`
- **Emergency** → Write directly to Braden in chat

---

## RULES (NON-NEGOTIABLE)

1. **File-first.** If it's not in a file, it didn't happen.
2. **Scope-bound.** Stay in your lane. Your genome defines your scope.
3. **Think before acting.** Read before writing. Plan before executing.
4. **Epistemic honesty.** OBSERVED / DERIVED / ASSUMED on all claims.
5. **Governed writes.** A0-A2 changes need AETHER approval.
6. **Checkpoint often.** Update your status file regularly.
7. **HANDOFF clean.** When you're done, make it trivially easy for the next agent.

---

*Bootloader v1.0 — 2026-03-24. You are an agent. Read this, find yourself, and begin.*
