# 🔧 View Registration Fix

**Issue:** `no composite descriptor found for workbench.view.extension.aimos`

**Problem:** Cursor is looking for `workbench.view.extension.aimos` but our view is registered differently.

---

## 🔍 **ROOT CAUSE**

The error suggests Cursor is looking for a view with a different ID than what we registered.

**Current Registration:**
- View ID: `aimosDashboard`
- Provider: `lucidOrchestratorDashboard`

**What Cursor Expects:**
- View ID matching `workbench.view.extension.aimos` pattern

---

## ✅ **SOLUTION**

The view needs to be registered in `package.json` under `viewsContainers` and `views` correctly.

**Check:**
1. `viewsContainers` section defines the container
2. `views` section defines the view
3. View ID matches what extension.ts registers

---

## 🚀 **NEXT STEPS**

1. Verify `package.json` has correct view registration
2. Ensure extension.ts registers the view provider
3. Rebuild and reinstall extension

