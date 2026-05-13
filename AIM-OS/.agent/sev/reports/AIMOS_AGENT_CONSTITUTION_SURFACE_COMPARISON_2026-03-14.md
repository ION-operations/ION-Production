# AIMOS Agent Constitution Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_15_2026-03-14`
Status: evidence-only comparative constitution analysis

## Comparative Table

| Comparison axis | Root north-star docs | In-tree `north_star.md` docs | `genome.md` docs | `README.md` docs | Host or lane instruction files |
| --- | --- | --- | --- | --- | --- |
| Identity authority | Strongest where present: they speak at the highest self-reference and mission-law layer | Medium-high, but uneven because some are redirects and some are duplicates or standalone local stars | Strong identity authority inside every sampled lane because all four lanes have genomes | Lower identity authority; usually defer to deeper constitution files | High host-specific identity authority inside the exact runtime they target |
| Mission and role definition | Strong at high-altitude role, season, and command-chain framing | Mixed: can restate or defer mission depending on the lane | Strongest dense mission-and-role definition family overall | Light mission framing only; mostly entrypoint and navigation | Strong at current mission, runtime duties, and lane-specific reporting chains |
| Load-order or startup role | Weak-to-medium; some imply first-read priority, but not as procedural load-order docs | Medium; SEV's redirect explicitly gives a read order | Medium; some genomes say "load this at conversation start," but startup steps are not their main comparative value | Strongest load-order family; every sampled README explicitly sequences startup reads or calls | Strong host-startup role when the runtime is known; often the sharpest host-side gate |
| Host specificity | Low; root north stars speak broadly above any one host | Low-to-medium; still mostly lane identity, not runtime adaptation | Low-to-medium; genomes mention platform reality but remain broad constitutions | Medium; READMEs sit inside a lane directory and point to that lane's local stack | Strongest host specificity by clear margin |
| Correction-vector or behavioral control density | Medium; north stars carry laws and success bars, but not the densest correction system | Lower and more variable than genomes | Strongest behavioral density overall through correction vectors, scope, principles, and drift logs | Low; READMEs are compact guides, not full behavioral constitutions | High in runtime-specific ways: they encode MCP-first, chat/capsule routing, freeze law, and role boundaries for the host |
| Portability across lanes | Low because only some lanes have root-level stars at all | Medium-low because implementations differ sharply and one sampled lane is missing entirely | Highest portability across the sampled lanes because all four have genome files in the same family | High portability across the sampled lanes as a directory-entry pattern | Lower portability because each instruction file is tied to a host, mode, or specialized audit lane |
| Relationship to doctrine and continuity surfaces | Indirect; they set the worldview above doctrine and continuity | Bridging role; often route readers from one constitution surface to another | Strong relation through comms doctrine references and scope law, but still one layer above rolling continuity | Strong relation to continuity because they explicitly point to context and chat paths | Strongest direct relation because they bind constitutions to doctrine, continuity, MCP usage, chat docs, and capsules in one surface |
| Drift or contradiction tendency | Medium-high because sibling families can diverge from them and some lanes lack them entirely | Highest family inconsistency: redirect, duplicate, standalone, and missing cases coexist | Medium-high because deep constitutions can lag or conflict with newer stars and instructions | Medium because they are short and current, but can omit families or reduce nuance | High because duplication and lane branching are visible, especially in SEV and COMPOSER instruction surfaces |

## Direct Comparative Reading

### Root north stars vs `genome.md`

- Root north stars are strongest at the highest self-story: season, command chain, campaign framing, and what the lane ultimately exists to do.
- `genome.md` is stronger than north stars at dense operational constitution: scope, correction vectors, non-negotiables, and system ownership.
- Findings Board 13 makes the sharpest example explicit: OPUS's genome carries autonomous acting-command law that diverges visibly from the OPUS north-star layer.

### In-tree `north_star.md` vs root north stars

- These are not one uniform family locally.
- `sev/north_star.md` is a compatibility redirect, `opus/north_star.md` is a full duplicate of the root star, and `codex/north_star.md` is the main visible north-star surface for CODEX.
- That means the in-tree family is doing different jobs in different lanes rather than preserving one stable pattern.

### `README.md` vs host or lane instruction files

- `README.md` is the best file family for answering "what do I read first and what local directory matters next?"
- Host or lane instruction files are better for answering "what does this exact runtime or lane require right now?"
- READMEs are more portable across lanes; instructions are more operationally specific and therefore more fragmentation-prone.

## Net Comparative Answer

1. Root north stars anchor the highest-level self-reference and mission horizon where they exist.
2. In-tree `north_star.md` files anchor per-directory self-reference and compatibility, but as an internally inconsistent family.
3. `genome.md` anchors the densest long-horizon constitution layer across all sampled lanes.
4. `README.md` anchors load order and directory entry.
5. Host or lane instruction files anchor host-specific operating law and packetized adaptation.

These are comparative role answers only. They do not select a final constitution winner or imply cleanup.
