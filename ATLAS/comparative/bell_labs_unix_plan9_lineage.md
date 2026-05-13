# Comparative: Bell Labs — Unix, Plan 9, Inferno, and descendants

**Atlas scope:** **Lineage and design pressure** from **Bell Labs** (and successors) on **OS** and **language** research relevant to **ION** — not corporate history as gossip.  
**Evidence:** Tiers per cell; primary literature upgrades preferred over encyclopedic surveys.

---

## 1. One-line map

```
Research Unix (1970s) → Plan 9 (1990s Bell Labs) → forks (9front) & parallel products (Inferno)
         ↘ cultural / people continuity ↙
              Go language (Google; many Bell alumni)
```

| Artifact | ATLAS package | Role |
|----------|---------------|------|
| **Plan 9** | `systems/plan-9` | Namespace + **9P** + distributed file model |
| **9front** | `systems/9front` | **Fork** — community Plan 9 |
| **Inferno** | `systems/inferno-os` | **Limbo** + **Dis** + **Styx** — portable OS appliance |
| **Linux v9fs** | `systems/linux-kernel` (see Plan 9 relations) | **9P client** in kernel |

---

## 2. Unix vs Plan 9 (design contrast)

| Dimension | Classic Unix (survey) | Plan 9 (survey) |
|-----------|----------------------|-----------------|
| **Composition** | Fixed namespaces + mount | **Per-process** synthetic namespace |
| **Network FS** | NFS (later), etc. | **9P** as **native** file protocol |
| **Philosophy** | “Everything is a file” (slogan) | Pushed toward **uniform resource** naming (`DOCUMENTED`, `src-wiki-plan9-design`) |
| **Code volume** | Large kernels (varies) | **Small kernel** + user services (pattern) |

**Tier note:** Unix row is **INFERRED** generalization; Plan 9 row **DOCUMENTED** via `src-wiki-plan9`.

---

## 3. Plan 9 ↔ Inferno

| Dimension | Plan 9 | Inferno |
|-----------|--------|---------|
| **Language** | C, Alef (history), … | **Limbo** |
| **Execution** | Native processes | **Dis** VM |
| **Wire protocol** | **9P** | **Styx** (9P family) |
| **Portability** | Tied to Plan 9 kernel | **Hosted** on many OSes (`DOCUMENTED`, `src-wiki-inferno`) |

**Edge in ATLAS:** `plan-9` **`influences`** `inferno-os` (design ancestry).

---

## 4. 9front (fork)

- **Identity:** `systems/9front` **`fork_of`** `plan-9`.  
- **Why separate:** **Governance**, **release**, and **hardware** support differ — do not collapse into `plan-9` package.

---

## 5. 9P outside Plan 9 (integration landscape)

| System | Relationship |
|--------|----------------|
| **Linux v9fs** | Kernel **client** for 9P — `src-linux-v9fs` in `plan-9/sources.yaml` |
| **QEMU virtio 9p** | Guest–host file sharing — **DOCUMENTED** kernel docs |
| **Plan 9 from User Space (plan9port)** | Userland ports — pointer in kernel doc (`DOCUMENTED` link) |

---

## 6. Go (optional cultural link)

**Go** language tooling and standard library show **Plan 9 / Bell** engineering culture (many shared authors). **Not** an OS — treat as **INFERRED** design pressure until a dedicated `systems/golang` package is seeded with **DOCUMENTED** primary sources.

---

## 7. PL/I and Bell Labs (orthogonal thread)

**PL/I** (`systems/pl-i`) is **IBM / SHARE** mainframe lineage — **not** Plan 9. It matters for **language** history and **Multics** documentation overlap (`HISTORICAL`). **Do not** merge narratives.

---

## 8. Unknown / do-not-merge

- **Internal** Bell Labs org charts as architecture.  
- **“Plan 9 won”** or **“Inferno failed”** without dated metrics — prefer **mechanism** claims.

---

## Suggested package seeds (future)

| Slug | Topic |
|------|--------|
| `unix-v7` or `research-unix` | Historical Unix for lineage |
| `golang` | Language + runtime as system |
| `ada`, `algol-60`, `rust` | Additional HLL / safety lineages |
