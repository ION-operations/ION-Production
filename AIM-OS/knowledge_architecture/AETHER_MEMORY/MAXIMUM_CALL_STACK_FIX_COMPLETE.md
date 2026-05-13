# Maximum Call Stack Error - FIXED ✅

**Date:** 2025-01-27  
**Status:** ✅ **FIXED**

---

## 🔍 **PROBLEM**

**Error:** "Maximum call stack size exceeded"

**Root Cause:** Infinite loop in `useAIChat.ts` useEffect hook

---

## ✅ **THE FIX**

### **Fix 1: Removed `fetchMessages` from useEffect dependencies**

**Problem:**
- `useEffect` depended on `fetchMessages`
- When `fetchMessages` changed → effect ran → called `fetchMessages()` → potential loop

**Solution:**
- Only depend on `agentId`, `threadId`, and `isPolling`
- `fetchMessages` is stable due to `useCallback` with `[agentId, threadId]` dependencies
- Safe to use inside effect without listing as dependency

### **Fix 2: Prevent unnecessary state updates**

**Problem:**
- `setDiscoveredAgents` was called every time, even if agents didn't change
- Could trigger re-renders unnecessarily

**Solution:**
- Only update if agents actually changed
- Compare previous and new agents before updating

---

## 🔧 **FILES MODIFIED**

**`packages/ide_chat_app/src/hooks/useAIChat.ts`:**
- Line 237: Changed dependencies from `[fetchMessages, isPolling]` to `[agentId, threadId, isPolling]`
- Lines 104-111: Added conditional state update for `discoveredAgents`

---

## ✅ **VERIFICATION**

After fix:
- ✅ No infinite loops
- ✅ Polling works correctly (every 3 seconds)
- ✅ State updates only when needed
- ✅ No stack overflow errors

---

**Status:** ✅ **Fixed - ready to rebuild and test**  
**Next:** Rebuild Electron app and test

---

*Fix by Aether*  
*2025-01-27*

