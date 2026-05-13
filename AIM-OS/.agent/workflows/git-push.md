---
description: how to push to git on the AIM-OS project (HTTPS credentials required)
---

# Git Push Workflow

## CRITICAL RULES — READ BEFORE EVERY GIT OPERATION

1. **ONE command at a time.** Never run git commands in parallel.
2. **NEVER terminate a git push.** The push opens a Windows credential popup that the user must interact with. If you terminate the command, it kills the credential flow.
3. **Use `SafeToAutoRun: false` for git push.** The user must approve it so they're ready for the credential popup.
4. **Set `WaitMsBeforeAsync: 10000` for git push.** This gives it max time to complete synchronously (credentials may already be cached).
5. **If push goes to background, WAIT with `command_status` using `WaitDurationSeconds: 300`.** Do NOT send any other commands to the same terminal.
6. **Do NOT run git add/commit/push as a single chained command.** Run each step separately and verify success before proceeding.

## Step-by-Step

### 1. Stage files
```powershell
git add <specific files or directories>
```
- SafeToAutoRun: true
- WaitMsBeforeAsync: 10000
- Verify: command should complete synchronously

### 2. Commit
```powershell
git commit -m "descriptive message"
```
- SafeToAutoRun: true
- WaitMsBeforeAsync: 10000
- Verify: look for commit hash in output

### 3. Push
```powershell
git push origin <branch-name>
```
- **SafeToAutoRun: false** (user approval required)
- **WaitMsBeforeAsync: 10000**
- If it goes to background: call `command_status` with `WaitDurationSeconds: 300`
- **DO NOT TERMINATE.** The user is entering credentials.
- Verify: look for `->` in output showing branch push

## Remote and Branch Info
- Remote: `origin` → `https://github.com/sev-32/AIM-OS.git`
- Primary branch: `aimos-march-2026-update`
- Relay branch: `ops/relay` (for Ghost cross-machine sync)

## Common Mistakes That Break Everything
- ❌ Running multiple git commands in parallel
- ❌ Terminating a push command while credentials popup is showing
- ❌ Setting WaitMsBeforeAsync too low on push (causes background + potential termination)
- ❌ Chaining `git add && git commit && git push` in one command
- ❌ Running other terminal commands while push is waiting for credentials
