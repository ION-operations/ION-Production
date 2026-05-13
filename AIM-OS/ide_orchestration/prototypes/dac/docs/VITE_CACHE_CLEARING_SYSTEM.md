# Vite Cache Clearing System - Design Discussion

**Purpose:** Implement a comprehensive cache clearing system for Vite dev server to resolve module loading issues and improve development experience.

---

## 🎯 **PROBLEM STATEMENT**

**Current Issues:**
- Vite hot reload cache can cause "Failed to fetch dynamically imported module" errors
- Browser cache can serve stale modules
- Vite's internal cache (`.vite` directory) can become corrupted
- No easy way to clear caches without manual intervention
- Developers waste time troubleshooting cache issues

**Impact:**
- Development workflow interruptions
- Frustration from repeated cache-related errors
- Time lost debugging cache issues instead of building features

---

## 📋 **TYPES OF CACHES**

### **1. Vite Build Cache (`.vite/` directory)**
**Location:** `node_modules/.vite/` or project root `.vite/`
**Purpose:** Caches transformed modules, dependencies, and build artifacts
**When to clear:** Module transformation errors, dependency changes, plugin issues
**How to clear:** Delete `.vite/` directory

### **2. Browser Cache (Service Worker / HTTP Cache)**
**Location:** Browser's cache storage
**Purpose:** Caches HTTP responses for faster loading
**When to clear:** Stale module errors, HMR not working
**How to clear:** Hard refresh (Ctrl+Shift+R), clear browser cache, or programmatic via DevTools

### **3. Module Cache (Dynamic Import Cache)**
**Location:** Browser's module map
**Purpose:** Caches ES module imports
**When to clear:** Module loading failures, circular dependency issues
**How to clear:** Page reload, or programmatic cache invalidation

### **4. Vite Dependency Cache (`node_modules/.vite/deps/`)**
**Location:** `node_modules/.vite/deps/`
**Purpose:** Pre-bundled dependencies for faster startup
**When to clear:** Dependency updates, pre-bundling errors
**How to clear:** Delete `node_modules/.vite/deps/` or entire `.vite/` directory

---

## 🔧 **IMPLEMENTATION APPROACHES**

### **Approach 1: Command Server Endpoint (Recommended)**
**Pros:**
- Can be called from IDE UI or external tools
- Integrates with existing Command Server infrastructure
- Can trigger dev server restart if needed
- Can clear multiple cache types

**Cons:**
- Requires Command Server to be running
- Needs file system access

**Implementation:**
```typescript
// Add to Command Server
POST /dev/vite/clear-cache
{
  "types": ["build", "deps", "all"], // Optional: specific cache types
  "restart": true // Optional: restart dev server after clearing
}
```

### **Approach 2: IDE UI Button**
**Pros:**
- Easy access from IDE
- Visual feedback
- Can show cache status

**Cons:**
- Requires UI component
- Only accessible when IDE is open

**Implementation:**
- Add "Clear Cache" button to IDE toolbar
- Shows cache size/stats
- Confirmation dialog before clearing

### **Approach 3: Automatic Detection & Clearing**
**Pros:**
- Proactive problem solving
- No manual intervention needed

**Cons:**
- May clear cache unnecessarily
- Could mask real errors
- Performance overhead

**Implementation:**
- Detect module loading failures
- Automatically clear cache and retry
- Log actions for debugging

### **Approach 4: Hybrid Approach (Recommended)**
**Combines all three:**
- Command Server endpoint for programmatic access
- IDE UI button for manual clearing
- Automatic detection for common errors

---

## 🛠️ **TECHNICAL IMPLEMENTATION**

### **1. Cache Detection**
```typescript
interface CacheInfo {
  buildCache: {
    path: string
    size: number
    exists: boolean
  }
  depsCache: {
    path: string
    size: number
    exists: boolean
  }
  totalSize: number
}
```

### **2. Cache Clearing Functions**
```typescript
// Clear Vite build cache
async function clearViteBuildCache(projectPath: string): Promise<void> {
  const viteCachePath = path.join(projectPath, 'node_modules', '.vite')
  if (fs.existsSync(viteCachePath)) {
    await fs.promises.rm(viteCachePath, { recursive: true, force: true })
  }
}

// Clear dependency cache only
async function clearViteDepsCache(projectPath: string): Promise<void> {
  const depsCachePath = path.join(projectPath, 'node_modules', '.vite', 'deps')
  if (fs.existsSync(depsCachePath)) {
    await fs.promises.rm(depsCachePath, { recursive: true, force: true })
  }
}

// Clear all Vite caches
async function clearAllViteCaches(projectPath: string): Promise<void> {
  await clearViteBuildCache(projectPath)
}
```

### **3. Browser Cache Clearing**
```typescript
// Via DevTools Protocol (if Electron/Chrome)
async function clearBrowserCache(): Promise<void> {
  // Use Chrome DevTools Protocol
  // Or trigger hard reload via window.location.reload(true)
}

// Via Service Worker (if using)
async function clearServiceWorkerCache(): Promise<void> {
  const registrations = await navigator.serviceWorker.getRegistrations()
  for (const registration of registrations) {
    await registration.unregister()
  }
  await caches.keys().then(keys => {
    keys.forEach(key => caches.delete(key))
  })
}
```

### **4. Dev Server Restart**
```typescript
// Restart Vite dev server
async function restartViteDevServer(projectPath: string): Promise<void> {
  // Find running Vite process
  // Kill it gracefully
  // Restart with 'npm run dev' or 'vite'
}
```

---

## 🎨 **UI INTEGRATION**

### **Option A: Toolbar Button**
```tsx
<button
  onClick={handleClearCache}
  className="p-2 hover:bg-gray-700 rounded"
  title="Clear Vite Cache"
>
  <RefreshCw className="w-4 h-4" />
</button>
```

### **Option B: Settings Panel**
- Cache management section
- Show cache sizes
- Clear individual cache types
- Auto-clear on errors toggle

### **Option C: Error Panel Integration**
- When module loading fails, show "Clear Cache & Retry" button
- One-click solution for cache issues

---

## 🔄 **WORKFLOW INTEGRATION**

### **Scenario 1: Manual Cache Clear**
1. User clicks "Clear Cache" button
2. Show confirmation dialog with cache sizes
3. Clear selected cache types
4. Optionally restart dev server
5. Show success/error feedback

### **Scenario 2: Automatic Cache Clear**
1. Detect module loading failure
2. Check error pattern (cache-related)
3. Automatically clear cache
4. Retry module load
5. Log action for debugging

### **Scenario 3: Dev Server Restart**
1. User clicks "Restart Dev Server"
2. Gracefully stop current server
3. Clear caches (optional)
4. Start new server instance
5. Show connection status

---

## 📊 **CACHE STATISTICS**

**Display:**
- Total cache size
- Build cache size
- Dependencies cache size
- Last cleared timestamp
- Cache hit/miss rates (if available)

**Benefits:**
- Understand cache usage
- Identify when cache is too large
- Track cache clearing frequency

---

## 🚨 **SAFETY CONSIDERATIONS**

### **1. Confirmation Dialogs**
- Warn before clearing large caches
- Show cache sizes before clearing
- Explain what will happen

### **2. Backup Strategy**
- Option to backup cache before clearing
- Restore option if issues occur

### **3. Selective Clearing**
- Clear only specific cache types
- Don't clear everything if not needed

### **4. Error Handling**
- Handle file system errors gracefully
- Don't break dev server if cache clear fails
- Log all actions for debugging

---

## 🎯 **RECOMMENDED IMPLEMENTATION**

### **Phase 1: Command Server Endpoint**
1. Add `/dev/vite/clear-cache` endpoint
2. Implement cache detection
3. Implement cache clearing functions
4. Add restart dev server capability

### **Phase 2: IDE UI Integration**
1. Add cache status display
2. Add "Clear Cache" button
3. Add confirmation dialogs
4. Show cache statistics

### **Phase 3: Automatic Detection**
1. Detect module loading failures
2. Pattern matching for cache errors
3. Automatic cache clear with retry
4. User notification of auto-actions

### **Phase 4: Advanced Features**
1. Cache size monitoring
2. Cache health checks
3. Scheduled cache clearing
4. Cache optimization suggestions

---

## 🔗 **INTEGRATION POINTS**

### **Command Server**
- Add endpoints for cache management
- Integrate with existing dev server management
- Use existing logging infrastructure

### **IDE UI**
- Add to toolbar or settings panel
- Use existing UI components
- Follow existing design patterns

### **Error Handling**
- Integrate with ErrorBoundary
- Show cache clear option on errors
- Log cache-related errors

---

## 📝 **API DESIGN**

### **Endpoints**

**GET `/dev/vite/cache/info`**
```json
{
  "buildCache": {
    "path": "node_modules/.vite",
    "size": 52428800,
    "exists": true
  },
  "depsCache": {
    "path": "node_modules/.vite/deps",
    "size": 104857600,
    "exists": true
  },
  "totalSize": 157286400
}
```

**POST `/dev/vite/cache/clear`**
```json
{
  "types": ["build", "deps"], // or "all"
  "restart": false
}
```

**Response:**
```json
{
  "success": true,
  "cleared": ["build", "deps"],
  "freed": 157286400,
  "restarted": false
}
```

**POST `/dev/vite/restart`**
```json
{
  "clearCache": true,
  "cacheTypes": ["build"]
}
```

---

## 🎨 **UI MOCKUP**

### **Cache Management Panel**
```
┌─────────────────────────────────────┐
│ Cache Management                    │
├─────────────────────────────────────┤
│ Build Cache:     50 MB              │
│ Dependencies:    100 MB             │
│ Total:           150 MB              │
│                                     │
│ [Clear Build Cache]                │
│ [Clear Dependencies]                │
│ [Clear All Caches]                  │
│                                     │
│ ☑ Auto-clear on module errors      │
│                                     │
│ Last cleared: 2 minutes ago         │
└─────────────────────────────────────┘
```

### **Error Panel Integration**
```
┌─────────────────────────────────────┐
│ Module Loading Failed                │
├─────────────────────────────────────┤
│ Failed to fetch: ManagerAIChat.tsx  │
│                                     │
│ This might be a cache issue.        │
│                                     │
│ [Clear Cache & Retry]               │
│ [Reload Page]                       │
└─────────────────────────────────────┘
```

---

## 🚀 **QUICK WINS**

### **Immediate Implementation (30 min)**
1. Add simple cache clear script to `package.json`
2. Add Command Server endpoint for cache clearing
3. Add basic UI button

### **Short-term (2-3 hours)**
1. Full cache detection and statistics
2. Selective cache clearing
3. Dev server restart integration
4. Error panel integration

### **Long-term (1-2 days)**
1. Automatic cache clearing
2. Cache health monitoring
3. Advanced statistics and analytics
4. Cache optimization suggestions

---

## 💡 **ALTERNATIVE APPROACHES**

### **1. Vite Plugin**
- Create custom Vite plugin
- Hook into Vite's cache system
- More integrated but requires plugin development

### **2. NPM Scripts**
- Add cache clear scripts to package.json
- Simple but requires terminal access
- Less integrated with IDE

### **3. VS Code Task**
- Create VS Code task for cache clearing
- Accessible via Command Palette
- Good middle ground

---

## 🎯 **RECOMMENDATION**

**Start with Command Server endpoint + IDE UI button:**
- Fast to implement
- Provides immediate value
- Can be extended later
- Works with existing infrastructure

**Then add automatic detection:**
- Reduces manual intervention
- Improves developer experience
- Can be toggled on/off

---

## 📚 **REFERENCES**

- Vite Cache Documentation: https://vitejs.dev/guide/dep-pre-bundling.html
- Vite Config: `vite.config.ts`
- Command Server: `cursor-addon/src/commandServer.ts`
- Existing restart patterns: MCP server restart endpoint

---

**Next Steps:**
1. Review and discuss approach
2. Implement Phase 1 (Command Server endpoint)
3. Add IDE UI integration
4. Test and iterate

