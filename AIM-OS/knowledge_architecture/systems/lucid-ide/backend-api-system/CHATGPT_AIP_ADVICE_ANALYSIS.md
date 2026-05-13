# ChatGPT AIP Advice Analysis & Integration

**Date:** 2025-01-27  
**Source:** ChatGPT (external AI advisor)  
**Status:** ✅ **REVIEWED & INTEGRATED**

---

## 📋 **OVERVIEW**

ChatGPT provided concrete implementation guidance for AIP (AIM-OS Application Integration Protocol) with:
- JSON Schema for manifest validation
- Command Server endpoint implementation
- JWT authentication
- Dynamic panel registration code
- New MCP tools
- WebSocket event bus
- Tool-to-service mapping
- Security enhancements

**Our Assessment:** ✅ **EXCELLENT** - Aligns perfectly with our Phase 1-6 roadmap and provides concrete, ship-ready code.

---

## ✅ **WHAT WE'RE ADOPTING**

### **1. JSON Schema for `aimos.json` Manifest** ⭐ **PRIORITY 1**

**Status:** ✅ **ADOPTED** - Will implement in Phase 2

**Why:** Provides validation, single source of truth, prevents errors

**Location:** `packages/aimos-sdk/schemas/aimos.manifest.schema.json`

**Action:** Create schema file and add validation to SDK

### **2. Command Server `/api/apps/register` Endpoint** ⭐ **PRIORITY 1**

**Status:** ✅ **ADOPTED** - Phase 2 implementation

**Why:** Provides auth, validation, better UX than raw MCP calls

**Location:** `cursor-addon/src/commandServer.ts`

**Action:** Add endpoint with JWT issuance

### **3. JWT Authentication** ⭐ **PRIORITY 2**

**Status:** ✅ **ADOPTED** - Phase 5 (can start earlier)

**Why:** Security, permissions, rate limiting foundation

**Decision:** Start with HS256, migrate to RS256 later (see decisions below)

**Action:** Add auth middleware to Command Server

### **4. Dynamic Panel Registration in IDE DAC v2** ⭐ **PRIORITY 2**

**Status:** ✅ **ADOPTED** - Phase 3 implementation

**Why:** Enables extensibility, aligns with our roadmap

**Location:** `ide_orchestration/prototypes/dac/src/components/IDELayout.tsx`

**Action:** Add dynamic panel loading (augments hardcoded panels)

### **5. New MCP Tools** ⭐ **PRIORITY 2**

**Status:** ✅ **ADOPTED** - Phase 3 & Phase 6

**Tools:**
- `register_panel` - Panel registration
- `report_resource_usage` - Resource tracking

**Location:** `lucid_mcp_server.py`

**Action:** Add tools to MCP server

### **6. WebSocket Event Bus** ⭐ **PRIORITY 3**

**Status:** ✅ **ADOPTED** - Phase 4 enhancement

**Why:** Real-time events, better UX than polling

**Location:** `cursor-addon/src/commandServer.ts`

**Action:** Add WebSocket server for event subscriptions

### **7. Tool-to-Service Mapping** ⭐ **PRIORITY 2**

**Status:** ✅ **ADOPTED** - Phase 5 (auth/permissions)

**Why:** Enables service-level permissions

**Location:** `cursor-addon/src/commandServer.ts`

**Action:** Create mapping and use for auth checks

### **8. Backend API System Migration** ⭐ **PRIORITY 3**

**Status:** ✅ **ADOPTED** - Long-term consolidation

**Why:** Removes duplicate storage, unifies on CMC

**Action:** Migrate Next.js API routes to use Command Server/MCP

### **9. Security Quick Wins** ⭐ **PRIORITY 2**

**Status:** ✅ **ADOPTED** - Phase 5

**Actions:**
- JWT validation on `/mcp/execute`
- Service permissions enforcement
- Rate limiting (per-app token bucket)
- VIF witnesses for auth decisions

### **10. SDK Enhancements** ⭐ **PRIORITY 2**

**Status:** ✅ **ADOPTED** - Phase 3 & Phase 6

**New Methods:**
- `panels.register(def)` - Panel registration
- `resources.report({ memory_mb, cpu_percent })` - Resource reporting
- `events.wsSubscribe(eventType, handler)` - WebSocket subscriptions

**Location:** `packages/aimos-sdk/src/services/`

**Action:** Add methods to SDK

---

## 🎯 **DECISIONS ON CHATGPT'S QUESTIONS**

### **1. Token Algorithm**

**Decision:** ✅ **HS256 for now, RS256 later**

**Rationale:**
- HS256 is simpler (single secret)
- RS256 requires key management
- Can migrate later without breaking changes
- Start simple, evolve as needed

**Implementation:**
```typescript
const JWT_ALG = "HS256" // Start here
// Future: Migrate to RS256 with key rotation
```

### **2. Panel Component Resolution**

**Decision:** ✅ **Local only (`../panels/${component}`) for now**

**Rationale:**
- Simpler security model
- No remote code execution risks
- Can add remote modules later if needed
- IDE DAC v2 controls panel code

**Implementation:**
```typescript
const Comp = React.lazy(() => import(`../panels/${component}`))
```

**Future Enhancement:** Allow remote modules with CSP and validation

### **3. Rate Limits**

**Decision:** ✅ **Per-app (50 req/s burst 100)**

**Rationale:**
- Simpler to implement
- Per-service can be added later
- Token bucket is standard pattern
- Prevents abuse without complexity

**Implementation:**
```typescript
// Token bucket per app_id (from JWT sub)
const rateLimiter = new TokenBucket({
  refillRate: 50, // req/s
  capacity: 100 // burst
})
```

### **4. Resource Policy**

**Decision:** ✅ **Throttle (soft limit) with warnings**

**Rationale:**
- Hard fails are disruptive
- Throttling allows graceful degradation
- Warnings enable proactive management
- Better UX than hard failures

**Implementation:**
```typescript
if (usage.memory_mb > declared.memory_mb * 1.2) {
  // Warning + throttle (slow down requests)
  // Don't hard fail unless > 2x declared
}
```

### **5. Event Model**

**Decision:** ✅ **Keep "eventType + payload" for now, adopt PROV/OpenLineage later**

**Rationale:**
- Simple envelope is easier to start
- PROV/OpenLineage can be added as metadata
- Don't over-engineer initially
- Can evolve schema without breaking changes

**Implementation:**
```typescript
// Simple envelope now
{ type: "eventType", payload: {...} }

// Future: Add PROV/OpenLineage metadata
{ type: "eventType", payload: {...}, provenance: {...}, lineage: {...} }
```

---

## 📝 **INTEGRATION PLAN**

### **Phase 2: Enhanced App Registry (Updated)**

**New Tasks:**
- [x] Create JSON Schema for `aimos.json` manifest
- [x] Add `/api/apps/register` endpoint to Command Server
- [x] Implement JWT issuance (HS256)
- [x] Add manifest validation (JSON Schema)
- [x] Create tool-to-service mapping
- [x] Add auth middleware to `/mcp/execute`

**Files to Create/Update:**
- `packages/aimos-sdk/schemas/aimos.manifest.schema.json` (NEW)
- `cursor-addon/src/commandServer.ts` (UPDATE - add `/api/apps/register`)
- `cursor-addon/src/auth.ts` (NEW - JWT validation)
- `cursor-addon/src/toolServiceMap.ts` (NEW - tool-to-service mapping)

### **Phase 3: Panel Registry System (Updated)**

**New Tasks:**
- [x] Add `register_panel` MCP tool
- [x] Update IDE DAC v2 `IDELayout.tsx` for dynamic panels
- [x] Add `panels.register()` to SDK
- [x] Panel component resolution (local only)

**Files to Create/Update:**
- `lucid_mcp_server.py` (UPDATE - add `register_panel` tool)
- `ide_orchestration/prototypes/dac/src/components/IDELayout.tsx` (UPDATE - dynamic panels)
- `packages/aimos-sdk/src/services/panel.ts` (UPDATE - add `register` method)

### **Phase 4: Unified Event System (Updated)**

**New Tasks:**
- [x] Add WebSocket server to Command Server
- [x] Implement `/events/subscribe` endpoint
- [x] Add `events.wsSubscribe()` to SDK
- [x] Keep polling as fallback

**Files to Create/Update:**
- `cursor-addon/src/commandServer.ts` (UPDATE - add WebSocket server)
- `packages/aimos-sdk/src/services/event.ts` (UPDATE - add `wsSubscribe` method)

### **Phase 5: Authentication & Authorization (Updated)**

**New Tasks:**
- [x] JWT validation middleware
- [x] Service-level permissions (via tool-to-service map)
- [x] Rate limiting (per-app token bucket)
- [x] VIF witnesses for auth decisions

**Files to Create/Update:**
- `cursor-addon/src/auth.ts` (UPDATE - add rate limiting)
- `cursor-addon/src/commandServer.ts` (UPDATE - add auth middleware)
- `lucid_mcp_server.py` (UPDATE - add VIF witness for auth)

### **Phase 6: Resource Management Unification (Updated)**

**New Tasks:**
- [x] Add `report_resource_usage` MCP tool
- [x] Add `resources.report()` to SDK
- [x] Implement throttling policy (soft limits)
- [x] Add resource warnings

**Files to Create/Update:**
- `lucid_mcp_server.py` (UPDATE - add `report_resource_usage` tool)
- `packages/aimos-sdk/src/services/resources.ts` (NEW - ResourceService)
- `daemon_rag_system/resource_manager/resource_manager.py` (UPDATE - add throttling)

---

## 🔄 **MIGRATION STRATEGY**

### **Backend API System Migration**

**Current:** Next.js API routes write to files

**Target:** Next.js API routes call Command Server/MCP

**Steps:**
1. Update Next.js routes to call Command Server
2. Replace file writes with `store_memory` MCP tool
3. Replace file reads with `retrieve_memory` MCP tool
4. Add VIF witnesses around operations
5. Remove duplicate routes after IDE switches to SDK

**Timeline:** Phase 7 (after Phase 1-6 complete)

---

## ✅ **ACCEPTANCE CRITERIA**

### **Manifest Validation**
- ✅ Valid manifest with one panel passes
- ✅ Unknown service in `required_services` fails with precise error
- ✅ Panel missing `component` fails
- ✅ `app_version` not SemVer fails

### **Auth & Gating**
- ✅ App registered with `["cmc"]` can call `store_memory`, cannot call `track_confidence`
- ✅ Expired token rejected
- ✅ Missing bearer token → `401`
- ✅ Invalid manifest rejected with actionable error strings

### **Dynamic Panels**
- ✅ Renders without throwing when `panels.list()` rejects (logs error, no crash)
- ✅ Inject two mock panels (`left`, `main`) → those sections mount
- ✅ Lazy component fallback visible during load

### **MCP Tools**
- ✅ `register_panel` rejects missing `id` / `location`
- ✅ `report_resource_usage` persists and is queryable with `retrieve_memory(tags)`

### **WebSocket Events**
- ✅ Client subscribes, receives "subscribed"
- ✅ Broadcast to a topic delivers to subscribers only
- ✅ Disconnect cleans subscriptions

### **Tool-to-Service Mapping**
- ✅ Adding a new tool without mapping → default deny (forces service assignment)
- ✅ Mapping change takes effect immediately

### **Backend Migration**
- ✅ No API route writes to files; all persistent writes are CMC atoms
- ✅ Removing `/api/*` duplicates doesn't break IDE DAC v2 (SDK in use)

---

## 📊 **IMPLEMENTATION PRIORITY**

**Week 1-2 (Phase 2):**
1. JSON Schema for manifest
2. `/api/apps/register` endpoint
3. JWT issuance (HS256)
4. Tool-to-service mapping
5. Auth middleware

**Week 3-4 (Phase 3):**
1. `register_panel` MCP tool
2. Dynamic panel loading in IDE DAC v2
3. SDK `panels.register()` method

**Week 5-6 (Phase 4):**
1. WebSocket server
2. `/events/subscribe` endpoint
3. SDK `events.wsSubscribe()` method

**Week 7-8 (Phase 5):**
1. Rate limiting
2. Service permissions enforcement
3. VIF witnesses for auth

**Week 9-10 (Phase 6):**
1. `report_resource_usage` MCP tool
2. SDK `resources.report()` method
3. Resource throttling policy

---

## 🎯 **KEY INSIGHTS**

1. **Start Simple:** HS256, local panels, simple event envelope
2. **Evolve Later:** RS256, remote modules, PROV/OpenLineage
3. **Security First:** JWT from day one, service permissions, rate limiting
4. **MCP-First:** Everything goes through MCP, Command Server is wrapper
5. **Augment, Don't Replace:** Dynamic panels augment hardcoded panels

---

**Status:** ✅ **INTEGRATED**  
**Next Steps:** Begin Phase 2 implementation with JSON Schema and `/api/apps/register` endpoint

