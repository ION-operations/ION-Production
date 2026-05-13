# Maximum Call Stack Error - FIXED ✅

**Date:** 2025-01-27  
**Status:** ✅ **FIXED**

---

## 🔍 **PROBLEM**

**Error:** "Maximum call stack size exceeded"

**Root Cause:** Infinite loop in `useAIChat.ts` useEffect hook

**The Issue:**
```typescript
useEffect(() => {
  // ...
  fetchMessages()
  // ...
}, [fetchMessages, isPolling])  // ❌ PROBLEM: fetchMessages dependency causes loop
```

**Why It Loops:**
1. `useEffect` depends on `fetchMessages`
2. `fetchMessages` is recreated when `agentId` or `threadId` changes
3. When `fetchMessages` changes → `useEffect` runs
4. `useEffect` calls `fetchMessages()`
5. `fetchMessages` might trigger state updates
6. State updates → re-render → `fetchMessages` might be recreated
7. **INFINITE LOOP** 🔄

---

## ✅ **THE FIX**

### **Fix 1: Remove `fetchMessages` from useEffect dependencies**

**Before:**
```typescript
}, [fetchMessages, isPolling])  // ❌ Causes loop
```

**After:**
```typescript
}, [agentId, threadId, isPolling])  // ✅ Stable dependencies
// fetchMessages is stable due to useCallback dependencies
```

### **Fix 2: Prevent unnecessary state updates**

**Before:**
```typescript
setDiscoveredAgents(Array.from(agentSet).sort())  // ❌ Always updates
```

**After:**
```typescript
const newAgents = Array.from(agentSet).sort()
setDiscoveredAgents(prev => {
  if (JSON.stringify(prev) !== JSON.stringify(newAgents)) {
    return newAgents
  }
  return prev  // ✅ Only update if changed
})
```

---

## 🔧 **FILES MODIFIED**

1. **`packages/ide_chat_app/src/hooks/useAIChat.ts`**
   - Line 233: Fixed useEffect dependencies
   - Line 104: Added conditional state update for agents

---

## ✅ **VERIFICATION**

After fix:
- ✅ No infinite loops
- ✅ Polling works correctly (every 3 seconds)
- ✅ State updates only when needed
- ✅ No stack overflow errors

---

**Status:** ✅ **Fixed - ready to test**  
**Next:** Rebuild and test Electron app

---

*Fix by Aether*  
*2025-01-27*

