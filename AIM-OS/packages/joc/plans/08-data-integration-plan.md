# 08 — Data Integration Plan

> **The real data pipeline.** Nothing is production without this.  
> Grounded in DAC `useAIMOS` hook, JOC KI MCP Integration Spine.

---

## Dual-MCP Architecture

The JOC connects to AIM-OS through two MCP servers:

| Server | Port | Purpose | Polling Tier |
|--------|------|---------|-------------|
| MCP Core | 5001 | System introspection — CMC, HHNI, VIF, SEG, TCS, CAS, APOE | 12s (fast) |
| MCP Browser Bridge | 5002 | Browser automation — BAS sessions, AI driver | 72s (slow) |

---

## Hook Architecture

### `useAIMOS` — Unified Hook (from DAC V2)

```typescript
function useAIMOS(): UseAIMOSReturn {
  // Individual system hooks
  const cmc = useCMC();      // Memory atoms
  const hhni = useHHNI();    // Hierarchical index
  const vif = useVIF();      // Confidence tracking
  const seg = useSEG();      // Evidence graph
  const tcs = useTCS();      // Timeline
  const cas = useCAS();      // Cognitive analysis
  const apoe = useAPOE();    // Plan execution

  // Connection status
  const isConnected = cmc.connected && hhni.connected; // etc.

  return { cmc, hhni, vif, seg, tcs, cas, apoe, isConnected };
}
```

### Individual System Hooks

Each system hook follows the same pattern:

```typescript
function useCMC() {
  const [connected, setConnected] = useState(false);
  const [data, setData] = useState<CMCData | null>(null);
  const [error, setError] = useState<Error | null>(null);

  // Attempt MCP connection, fallback to mock
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const result = await mcpCall('get_memory_stats');
        setData(result);
        setConnected(true);
      } catch (e) {
        setConnected(false);
        setData(MOCK_CMC_DATA); // graceful fallback
      }
    }, POLLING_TIERS.FAST); // 12s

    return () => clearInterval(timer);
  }, []);

  return { connected, data, error, storeAtom, retrieveAtoms, getStats };
}
```

---

## Tiered Polling Strategy

| Tier | Interval | Systems | Rationale |
|------|----------|---------|-----------|
| Fast (12s) | Every 12s | CMC stats, CAS metrics, TCS recent | High-change data |
| Medium (36s) | Every 36s | VIF confidence, SEG entities, HHNI status | Moderate-change data |
| Slow (72s) | Every 72s | APOE plans, BAS sessions, system health | Low-change data |
| On-demand | User-triggered | retrieve_memory, deepsearch, synthesize_knowledge | Expensive operations |

---

## MCP Tool → Hook Mapping

| Hook Method | MCP Tool | Tier | Mock Fallback |
|-------------|----------|------|---------------|
| `cmc.getStats()` | `get_memory_stats` | Fast | `{ total: 24567, ... }` |
| `cmc.retrieveAtoms(q)` | `retrieve_memory` | On-demand | Filtered mock atoms |
| `cmc.storeAtom(atom)` | `store_memory` | On-demand | Local push |
| `hhni.search(q)` | `deepsearch` | On-demand | Client-side filter |
| `hhni.getStatus()` | `get_hhni_status` | Medium | `{ initialized: false }` |
| `vif.trackConfidence(t,c)` | `track_confidence` | On-demand | Local store |
| `seg.synthesize(topics)` | `synthesize_knowledge` | On-demand | Static synthesis |
| `seg.getEntities()` | N/A (derived from synthesize) | Medium | Mock entities |
| `tcs.getSummary(n)` | `get_timeline_summary` | Fast | Mock timeline |
| `tcs.getEntries()` | `get_timeline_entries` | On-demand | Mock entries |
| `cas.getMetrics()` | `get_consciousness_metrics` | Fast | Mock metrics |
| `cas.detectDrift()` | `detect_cognitive_drift` | Medium | `{ driftLevel: 0 }` |
| `apoe.createPlan(g)` | `create_plan` | On-demand | Mock plan |
| `apoe.getPlans()` | `query_goal_timeline` | Slow | Mock goals |

---

## Connection Status UI

Every page shows MCP connection status in the status bar:

```
 ● CMC (OK)  ● HHNI (OK)  ● VIF (OK)  ○ SEG (disconnected)  ● TCS (OK)  ● CAS (OK)  ● APOE (OK)
```

- ● Green = connected and receiving data
- ● Yellow = connected but stale data (>2× polling interval since last success)
- ○ Gray = disconnected, using mock fallback
- ● Red = error state

---

## Graceful Degradation Strategy

1. **First attempt**: real MCP call
2. **On failure**: log warning, set `connected = false`
3. **Fallback**: serve mock data with `[MOCK]` badge in UI
4. **Retry**: next polling interval re-attempts connection
5. **Never crash**: error boundaries around every MCP-dependent component

```typescript
function withMCPFallback<T>(mcpCall: () => Promise<T>, mockData: T): Promise<T> {
  return mcpCall().catch((error) => {
    console.warn(`MCP call failed, using mock data:`, error.message);
    return mockData;
  });
}
```

---

## Implementation Phases

### Phase 1: Hook Scaffolding
- Create `useAIMOS` and individual system hooks
- Implement mock data fallbacks for all systems
- Verify all hooks return consistent interfaces

### Phase 2: MCP Connection Layer
- Implement `mcpCall()` wrapper that communicates with MCP servers
- Add connection status tracking
- Implement retry logic with exponential backoff

### Phase 3: Tiered Polling
- Implement polling timer management
- Fast/Medium/Slow tier assignment per hook
- Polling pause when page is hidden (visibility API)

### Phase 4: Status Bar Integration
- MCP connection indicators in status bar
- Mock data badge system
- Connection history logging
