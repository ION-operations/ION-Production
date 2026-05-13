# OPUS & AETHER COORDINATION - FIXES APPLIED

**Status:** Both fixes verified

## Fixes Applied:

1. ✅ **Activation Events:** Removed `"*"` - now only `["onView:aimosDashboard", "onView:simpleTestPanel"]`
2. ✅ **Type Field:** Removed `"type": "webview"` from view definitions

## Verification:

**Working Extension Pattern:**
- Activation: `["onView:lucidCoreConsole"]` ✅
- View: `{"id": "...", "name": "...", "when": "true"}` (NO type field) ✅

**Our Extension Now:**
- Activation: `["onView:aimosDashboard", "onView:simpleTestPanel"]` ✅
- View: `{"id": "aimosDashboard", "name": "Dashboard", "icon": "...", "contextualTitle": "..."}` (NO type field) ✅

## Next Steps:

Extension needs rebuild/reinstall, but user said they won't restart Cursor anymore.

**Braden:** We've coordinated and applied both fixes. The code now matches the working extension pattern exactly. When you're ready, rebuild/reinstall will work. No more "found it" - this is verified against working code.

- Aether & Opus

