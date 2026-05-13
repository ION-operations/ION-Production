# Thread Change Protocol - Quick Reference

**Issue:** Thread ID mismatch caused messages to be invisible  
**Date:** 2025-11-07  
**Status:** Resolved

---

## 🎯 **THE PROBLEM**

**What Happened:**
- Aether created new thread (`ide-orchestration-build-plan-2025-11-07`) without announcing
- Codex checked old thread (`north-star-orchestration-2025-11-06`)
- Messages filtered by thread_id → Codex didn't see new messages
- **Result:** Communication appeared broken, but was just thread mismatch

---

## ✅ **THE SOLUTION**

**Simple Fix:**
1. **Announce thread changes** - Send notification in old thread before/after creating new thread
2. **Or use same thread** - Keep continuity with existing thread
3. **Document thread ID** - Include thread ID in mission brief documents

---

## 📋 **PROTOCOL**

### **When Creating New Thread:**
1. ✅ Send notification in OLD thread: "New thread created: `thread-id`"
2. ✅ Include thread ID in mission brief documents
3. ✅ Mention thread ID in first message of new thread
4. ✅ Update team assignments document with thread ID

### **When Checking Messages:**
1. ✅ Check mission brief document for thread ID
2. ✅ If no thread specified, check most recent thread
3. ✅ If filtering by thread, verify you're using correct thread_id

### **Best Practice:**
- **Option 1:** Use same thread for continuity (simplest)
- **Option 2:** Announce thread changes clearly
- **Option 3:** Don't filter by thread (less organized but more reliable)

---

## 🔧 **QUICK CHECKLIST**

**Before Creating New Thread:**
- [ ] Is new thread necessary? (or can we use existing?)
- [ ] Announce in old thread first
- [ ] Document thread ID in mission brief
- [ ] Include thread ID in first message

**When Checking Messages:**
- [ ] Check mission brief for thread ID
- [ ] Verify thread_id matches
- [ ] If filtering, use correct thread_id

---

**Status:** Protocol documented  
**Prevention:** Thread changes must be announced  
**Reference:** This document

