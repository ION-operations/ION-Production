# Agent Capability Evaluation Framework - 2026-03-06

**Owner:** Sev  
**Purpose:** Measure which agent/model/runtime combinations are strongest at which classes of work so AIM-OS team composition can improve over time.

---

## 1. Evaluation Axes

Score each agent or runtime surface on a 1-5 scale per task packet:

1. **Strategic reasoning**
2. **Implementation throughput**
3. **Audit rigor**
4. **Context retention**
5. **Tool/runtime access reliability**
6. **Cross-file coordination**
7. **Design sensitivity**
8. **Communication discipline**
9. **Recovery from ambiguity**
10. **Verification quality**

Use notes, not just numbers. Numbers compress; notes explain.

---

## 2. Evaluation Rule

Every meaningful packet should log:
- owner
- supporting agents
- runtime surfaces used
- task class
- outcome
- verification result
- what each agent was unusually good or weak at

Do not score vibes. Score demonstrated packet behavior.

---

## 3. Current Working Hypotheses

| Agent / Surface | Expected Strengths | Likely Risks |
|---|---|---|
| **Sev / Cursor-Codex** | doctrine, force design, synthesis, executive framing | over-abstraction, canon conflict if not grounded |
| **Opus / Antigravity** | shipping, architecture execution, UI/system build tempo | speed can outrun doctrine or polish gates |
| **Codex CLI** | backend contracts, protocol rigor, bounded implementation | over-specification, weaker broad orchestration |
| **Gemini CLI** | large-context research, synthesis, swarm reconnaissance | output can drift academic without sharp task framing |
| **Composer 1.5** | audit sweeps, indexing, multi-file normalization | can optimize patterns without owning architecture |
| **Browser GPT lanes** | external reasoning, critique, comparison | weaker live repo truth and transport asymmetry |

These are hypotheses only. They must be tested against packets.

---

## 4. Packet Logging Template

Use this format after each major packet:

```md
## Packet
- ID:
- Date:
- Goal:
- Owner:
- Support:
- Runtime surfaces:
- Verification:

## Scores
- Strategic reasoning:
- Implementation throughput:
- Audit rigor:
- Context retention:
- Tool/runtime access reliability:
- Cross-file coordination:
- Design sensitivity:
- Communication discipline:
- Recovery from ambiguity:
- Verification quality:

## Notes
- What worked:
- What failed:
- Best-fit agent(s) for this task class:
- Should this become a reusable specialist or clone:
```

---

## 5. First Evaluation Tracks

1. **Transport clarity packets**
   Goal: compare Codex, Opus, and browser-side lanes on MCP truth and troubleshooting accuracy.

2. **Genome/protocol evolution packets**
   Goal: compare Sev, Codex, and Composer on canon cleanup speed vs correctness.

3. **JOC execution packets**
   Goal: compare Opus, Composer, and support research lanes on implementation quality vs validation discipline.

4. **Agent runtime packets**
   Goal: compare Codex and Opus collaboration on moving clone/genome runtime from spec to code.

---

## 6. Promotion Rule

An agent or clone should be promoted into a durable role only when:
- it repeatedly outperforms alternatives on the same task class
- its lane can be stated clearly
- the cost of coordinating it is lower than the value it creates
- its failure modes are known enough to manage

---

*Measure the force. Then evolve it.*
