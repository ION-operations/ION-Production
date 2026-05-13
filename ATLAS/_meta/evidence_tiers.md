# Evidence Tiers

**Status:** DOCUMENTED (repository constitution)

ATLAS attaches exactly one primary tier to each claim unless the claim is explicitly composite (then split the claim).

## Tier definitions

| Tier | Meaning | Typical sources |
|------|---------|-----------------|
| **DOCUMENTED** | Stated in primary vendor/docs, standards, or source with stable reference. | Manuals, API reference, RFCs, kernel source comments matching behavior, formal papers from authors. |
| **OBSERVED** | Reproducible measurement or capture of externals; internals not asserted. | Traces, benchmarks, public endpoint behavior, layout of public repos, conference talks with demos. |
| **HISTORICAL** | Time-indexed fact about releases, naming, org changes, or documented design decisions in primary memoirs/papers. | Release notes, archived specs, peer-reviewed history, oral history with citation. |
| **INFERRED** | Best-effort conclusion from public signals; not directly stated by primary sources. | Pattern matching across docs, partial code visibility, economic/organizational inference. |
| **UNKNOWN** | Insufficient grounded material; any statement would be speculative. | — |

## Rules

1. **DOCUMENTED** requires a pointer in `sources.yaml` or standards list with stable locator (URL + version/date, commit hash, section).  
2. **OBSERVED** must describe the observation protocol (what was run, what was captured).  
3. **INFERRED** must list the weakest link in the chain (what is not directly seen).  
4. **UNKNOWN** is preferred over confident prose when primary evidence is missing.  
5. For **AI product runtimes** and **closed cloud systems**, default internal architecture to **UNKNOWN** unless a primary technical paper or verified engineering blog from the operator states it.

## Composite rows in `13_evidence_ledger.md`

Use sub-rows:

```text
| Claim | Tier | Notes |
| Overall topology | INFERRED | From job postings + public API shapes |
| API rate limit headers | OBSERVED | Captured 2026-04-02 from documented endpoint |
```
