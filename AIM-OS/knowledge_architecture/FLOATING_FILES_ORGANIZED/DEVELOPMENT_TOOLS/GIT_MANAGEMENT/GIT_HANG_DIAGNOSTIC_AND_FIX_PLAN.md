# Git Hang Diagnostic and Fix Plan

**Priority:** CRITICAL - Blocks all recovery and memory operations  
**Date:** 2025-10-26  
**Status:** Planning investigation  

---

## 🚨 THE PROBLEM

**Git commands hang in Cursor's terminal:**
- `git status` - HANGS
- `git show` - HANGS  
- `git checkout` - HANGS
- `git restore` - HANGS
- `git commit` (without `-m`) - HANGS (opens editor, blocks)
- Many other git commands - HANG

**What WORKS:**
- `git log --oneline -N` - WORKS
- `git commit -m "message"` - WORKS (short messages)
- GitHub pushes - WORK
- GitHub pulls - WORK

**Impact:**
- Can't restore from commits
- Can't verify file history
- Can't check what changed
- Blocks all recovery operations
- Forces manual file manipulation
- Loses git-based memory/intelligence

---

## 🔍 HYPOTHESIS: WHY GIT HANGS

### **Theory 1: Editor Configuration**
**Most Likely:** Git is trying to open an editor (for commit messages, merge conflicts, etc.) but can't find or launch the editor properly in Cursor's terminal.

**Evidence:**
- `git commit` without `-m` hangs (tries to open editor)
- Other commands that might trigger editor also hang
- `git log --oneline` works (no editor needed)
- `git commit -m "msg"` works (bypasses editor)

**Fix:** Configure git to use a headless editor or set `EDITOR` environment variable

### **Theory 2: PowerShell Terminal Issues**
**Possible:** Cursor's integrated PowerShell terminal has issues with certain git commands, possibly related to:
- Pager (less/more) not working
- Input buffering issues
- Terminal compatibility issues

**Fix:** Configure git to not use pager, or use different terminal

### **Theory 3: Large Repository**
**Possible:** The AIM-OS repository is large (1000+ files) and certain commands hang while processing.

**Evidence:** Some git commands work, others don't - pattern suggests specific commands hang

**Fix:** Optimize git configuration for large repos

### **Theory 4: File Watcher/Lock Issues**
**Possible:** Another process has git locks or is watching files, causing git commands to wait.

**Fix:** Kill any processes holding git locks, check for file watchers

---

## 🔧 DIAGNOSTIC STEPS

### **Step 1: Check Git Configuration**
```powershell
# Check current git editor setting
git config --global core.editor

# Check pager setting
git config --global core.pager

# List all git config
git config --global --list
```

### **Step 2: Test With Editor Unset**
```powershell
# Try git with no editor
$env:GIT_EDITOR = ""
git status

# Or set to vim (terminal-based)
$env:GIT_EDITOR = "vim"
git status

# Or set to notepad
$env:GIT_EDITOR = "notepad"
git status
```

### **Step 3: Check Git Version**
```powershell
git --version

# Check if it's the Windows Git or WSL Git
which git
```

### **Step 4: Test Outside Cursor**
- Open regular PowerShell (not Cursor's terminal)
- Navigate to repository
- Run `git status`
- See if it hangs there too

### **Step 5: Check For Lock Files**
```powershell
# Look for git lock files
Get-ChildItem -Path .git -Recurse -Filter "*.lock" -ErrorAction SilentlyContinue

# Look for index.lock (common cause of hangs)
Test-Path .git/index.lock
```

### **Step 6: Check Git LFS (if used)**
```powershell
# Check if Git LFS is installed
git lfs version

# Check if repo uses LFS
git lfs ls-files
```

---

## 💡 PROPOSED FIXES (In Order)

### **Fix 1: Configure Git Editor (Most Likely Fix)**
```powershell
# Set git to use a headless editor (no GUI popup)
git config --global core.editor "code --wait"

# OR set to notepad (simple, reliable)
git config --global core.editor "notepad"

# OR disable editor entirely (use -m flag always)
git config --global core.editor "true"
```

### **Fix 2: Disable Git Pager**
```powershell
# Disable pager (prevents hangs on output)
git config --global core.pager ""

# OR set to cat (simple output)
git config --global core.pager "cat"
```

### **Fix 3: Set Terminal Environment**
```powershell
# In Cursor terminal, add to profile or set per-session
$env:GIT_EDITOR = "notepad"
$env:GIT_PAGER = "cat"
```

### **Fix 4: Use Git With Options**
```powershell
# Skip hooks and pager
git --no-pager status

# Or always use -m flag for commits
# (no hanging on editor)
```

### **Fix 5: Fix Lock Files**
```powershell
# Remove any lock files (if exists)
Remove-Item .git/index.lock -ErrorAction SilentlyContinue
Remove-Item .git/*.lock -ErrorAction SilentlyContinue
```

---

## 📋 ACTION PLAN

### **Immediate (Try First):**
1. Configure git editor to `notepad` or `code --wait`
2. Disable git pager
3. Test if `git status` works

### **If That Doesn't Work:**
4. Check lock files and remove them
5. Test git outside Cursor terminal
6. Check Git LFS configuration

### **If Still Hanging:**
7. Reinstall Git for Windows
8. Check for antivirus interfering
9. Check Windows Defender exclusions

---

## 🎯 SUCCESS CRITERIA

**Git commands should:**
- ✅ `git status` returns in <2 seconds
- ✅ `git show <hash>` returns in <2 seconds  
- ✅ `git checkout <branch>` returns in <2 seconds
- ✅ `git restore <file>` returns in <2 seconds
- ✅ No hangs or indefinite waits

---

## 📝 TESTING

**After applying fix:**
```powershell
# Test basic commands
git status
git log --oneline -5
git show HEAD
git diff HEAD~1

# All should return quickly without hanging
```

---

## 🔄 ROLLBACK

**If fix breaks things:**
```powershell
# Restore git config to default
git config --global --unset core.editor
git config --global --unset core.pager
```

---

**This is the #1 priority blocker for reliable memory/intelligence operations. Fixing this will unlock all the recovery and snapshot capabilities we need.** 🎯
