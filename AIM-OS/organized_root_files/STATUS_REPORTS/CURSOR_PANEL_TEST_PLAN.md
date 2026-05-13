# CURSOR PANEL TEST - COMPLETELY SEPARATE

**Goal:** Test if `createWebviewPanel` works in Cursor  
**Approach:** VS Code's official example, no WebviewViewProvider  
**Location:** Root level, separate from AIMOS

---

## WHAT WE KNOW

1. **WebviewViewProvider FAILS** - "no provider registered" error
2. **createWebviewPanel SHOULD WORK** - It's what VS Code uses
3. **We need to TEST** - Can we even make a basic panel work?

---

## PLAN

Create extension at root level:
- `cursor-panel-test/` (separate from cursor-addon)
- ONE file: `extension.ts`
- ONE command: open panel
- Uses ONLY `createWebviewPanel` (NOT WebviewViewProvider)
- Simplest possible HTML

---

**Status:** Ready to create  
**Next:** Create the extension

