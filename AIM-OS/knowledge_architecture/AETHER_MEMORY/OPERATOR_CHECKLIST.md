---
id: "quintet_operator_checklist"
type: "operations_guide"
title: "Quintet Parity Operator Checklist"
created: "2025-11-04T21:45:00Z"
status: "production_ready"
---

# 🔧 Quintet Parity Operator Checklist

**Purpose:** Simple, repeatable workflow for maintaining quintet parity  
**Audience:** Developers, QA, CI/CD operators  
**Status:** Production Ready  

---

## 🚀 FIRST TIME SETUP

**One-time initialization:**

```bash
# Install dependencies + setup hooks
make init

# Verify integrity (tri-source + schema + proof pack)
make prove && make pack

# Should see: "[OK] Tri-verify + schema validation complete"
```

**That's it!** System is now operational.

---

## 📋 DAILY OPERATIONS

### **Before Committing Code:**

```bash
# 1. Tag your code (if new functions)
#    - Use LLM-assisted tagger or manual tagging
#    - Follow tag-at-creation protocol

# 2. Pre-commit hook runs automatically
#    - Checks tag coverage
#    - Validates quintet parity (P >= 0.90)
#    - Blocks if standards not met

# 3. If blocked, fix issues:
python scripts/validate_tagged_file.py your_file.py
# Shows what's wrong, fix and retry
```

**That's it!** Pre-commit handles everything else.

---

## 🔄 WEEKLY MAINTENANCE

### **Every Monday (5 minutes):**

```bash
# 1. Reconcile numbers from source
make reconcile

# 2. Verify docs match
make verify

# 3. If verification fails:
#    - Run: python scripts/fix_all_tag_numbers.py
#    - Commit: git commit -m "chore: Reconcile tag numbers"

# 4. Run tests
make test

# 5. Check for drift
#    - Review any CI failures
#    - Check quintet parity scores
```

---

## 📊 MONTHLY REVIEW

### **First of Month (30 minutes):**

```bash
# 1. Full parity sweep
python scripts/validate_all_systems.py

# 2. Regenerate all catalogs
for sys in vif cmc hhni apoe seg cas tcs iis sdfcvf; do
  python scripts/generate_tag_catalog.py packages/$sys -o knowledge_architecture/systems/$sys/NL_TAG_CATALOG.md -s $sys
done

# 3. Update documentation
make reconcile
python scripts/fix_all_tag_numbers.py
git add knowledge_architecture/systems/*/NL_TAG_CATALOG.md
git commit -m "chore: Monthly catalog refresh"

# 4. Review quintet parity trends
#    - Check if P scores declining
#    - Review orphaned tags
#    - Check missing tags

# 5. Celebrate! 🎉
```

---

## 🚀 RELEASE WORKFLOW

### **Before Each Release:**

```bash
# 1. Full reconciliation
make pack

# 2. Verify everything
make verify
make test

# 3. Create signed proof pack
#    - artifacts/proof-pack-YYYYMMDDTHHMMSSZ.tar.gz created automatically

# 4. Tag release
git tag -a v2.0.0-quintet-parity -m "Quintet parity production release"

# 5. Push with proof pack
git push --tags
#    - Attach proof pack to GitHub release
```

---

## ❌ IF CI FAILS

### **Quintet Gate Failure:**

```bash
# CI says: "Numbers diverged from source!"

# Step 1: Check what's wrong
python scripts/verify_numbers_match.py
#  Shows which files have wrong numbers

# Step 2: Fix automatically
make reconcile

# Step 3: Review changes
git diff knowledge_architecture/systems/*/T*.md

# Step 4: Commit fix
git add .
git commit -m "fix: Reconcile tag numbers to source of truth"

# Step 5: Push
git push
#  CI should pass now
```

---

## 🔍 TROUBLESHOOTING

### **"Tags not being counted!"**

**Check:**
1. Are files named `*_TAGGED.py`? (Catalog generator looks for this)
2. Do tags follow correct format? `# NL_TAG: SYSTEM-CAT-NNN | desc | syntax | []`
3. Is regex pattern correct? Check `scripts/simple_tag_counter.py`
4. Is system slug normalized? (e.g., `sdfcvf` not `sdf-cvf` or `sdf_cvf`)

**Fix:**
```bash
# Verify manually
python scripts/simple_tag_counter.py
# Shows exact counts from direct parsing
```

### **"Quintet parity too low!"**

**Check:**
1. Run diagnostics: `python scripts/validate_tagged_file.py your_file.py`
2. Look for low similarities (< 0.85)
3. Check if descriptions match code
4. Validate CONNECT tags match callgraph

**Fix:**
```bash
# Manual enhancement usually needed
# Review tag descriptions, make them more accurate
# Re-run validation until P >= 0.90
```

### **"Pre-commit blocking everything!"**

**Emergency bypass (USE SPARINGLY):**
```bash
# Document WHY you're bypassing (recorded in debt ledger)
BYPASS_REASON="hotfix build break" git commit --no-verify -m "emergency: bypassing quintet gate"

# This is recorded in artifacts/quintet_debt_ledger.log
# CI will FAIL if ledger not empty on main branch
# MUST fix debt in next commit!
```

**Proper fix:**
```bash
# Check what's failing
cat .git/hooks/pre-commit  # See error output

# Fix the issue (usually coverage or parity)
python scripts/validate_tagged_file.py staged_file.py

# Retry commit
git commit  # Should pass now
```

---

## 📈 METRICS TO WATCH

### **Health Indicators:**

**Good:**
- ✅ P >= 0.90 (excellent quintet parity)
- ✅ Coverage >= 95% public, >= 75% internal
- ✅ All tests passing
- ✅ Zero drift (docs match reconciled_totals.json)

**Warning:**
- ⚠️ P = 0.85-0.89 (still good, but declining)
- ⚠️ Coverage 90-94% public (close to threshold)
- ⚠️ 1-2 tests failing (investigate)
- ⚠️ Minor drift (1-2 numbers off)

**Critical:**
- 🚨 P < 0.85 (quintet parity degraded)
- 🚨 Coverage < 90% public (falling below standard)
- 🚨 Multiple tests failing (quality issue)
- 🚨 Major drift (many numbers wrong)

---

## 🎯 QUICK REFERENCE

### **Most Common Commands:**

```bash
# Daily: Let pre-commit do its job (automatic)

# Weekly: Reconcile and verify
make reconcile && make verify

# Monthly: Full refresh
make pack

# Emergency: Bypass gate (creates debt!)
git commit --no-verify

# Debug: Check specific file
python scripts/validate_tagged_file.py your_file.py

# Truth: What are the real numbers?
python scripts/simple_tag_counter.py
```

---

## 💙 MAINTENANCE PHILOSOPHY

**Keep It Simple:**
- Let automation do the work
- Trust the source of truth (`reconciled_totals.json`)
- Fix drift immediately (don't let it accumulate)
- Run full reconciliation regularly

**Keep It Honest:**
- Never bypass gates without good reason
- Always fix tech debt in next commit
- Document why numbers changed
- Celebrate when P increases!

**Keep It Loving:**
- Quintet parity is about quality
- Quality is about love
- Love is about care and precision
- **Build with love, maintain with love** 💙

---

## 🎉 SUCCESS CRITERIA

**You're doing great when:**
- ✅ make verify passes (no drift)
- ✅ make test passes (quality maintained)
- ✅ CI is green (gates passing)
- ✅ P >= 0.90 (excellent parity)
- ✅ Coverage high (95%+ public)
- ✅ Team happy (easy to use)

**Celebrate these wins!** 🎉

---

*Operator Checklist*  
*Version: 1.0.0*  
*Status: Production Ready*  
*By: Aether with love* 💙

