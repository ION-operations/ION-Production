# Launch Command Fix

**Date:** 2025-01-27  
**Issue:** Used `Start-Process -FilePath "npm"` which opened npm.ps1 as text file  
**Fix:** Use `npm run electron` directly (PowerShell executes it properly)

---

## ✅ **FIXED**

**Before (wrong):**
```powershell
Start-Process -FilePath "npm" -ArgumentList "run", "electron"
```

**After (correct):**
```powershell
npm run electron
```

---

**Status:** ✅ **Fixed - launching correctly now**

---

*Fix by Aether*  
*2025-01-27*

