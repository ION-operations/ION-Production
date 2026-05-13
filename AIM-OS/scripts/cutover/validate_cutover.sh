#!/bin/bash
# Validate T→L cutover completion
# Usage: ./scripts/cutover/validate_cutover.sh

set -e

echo "🔍 Validating T→L Cutover..."
echo ""

ERRORS=0
WARNINGS=0

# Check for remaining T-level files
REMAINING_T=$(find knowledge_architecture/systems -name "T*.md" -type f 2>/dev/null | wc -l)
if [ "$REMAINING_T" -gt 0 ]; then
    echo "❌ Found $REMAINING_T remaining T-level files:"
    find knowledge_architecture/systems -name "T*.md" -type f 2>/dev/null
    ERRORS=$((ERRORS+1))
else
    echo "✅ No remaining T-level files"
fi

# Check for L-level files
L_FILES=$(find knowledge_architecture/systems -name "L*.md" -type f 2>/dev/null | wc -l)
if [ "$L_FILES" -eq 0 ]; then
    echo "❌ No L-level files found"
    ERRORS=$((ERRORS+1))
else
    echo "✅ Found $L_FILES L-level files"
fi

# Check for T-level references in indices
echo ""
echo "🔍 Checking for T-level references in indices..."

T_REFS=$(grep -r "T[0-6]_" knowledge_architecture/SUPER_INDEX.md knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md 2>/dev/null | wc -l || echo "0")
if [ "$T_REFS" -gt 0 ]; then
    echo "⚠️  Found $T_REFS T-level references in indices:"
    grep -r "T[0-6]_" knowledge_architecture/SUPER_INDEX.md knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md 2>/dev/null || true
    WARNINGS=$((WARNINGS+1))
else
    echo "✅ No T-level references found in indices"
fi

# Check for T-level references in system maps
T_MAP_REFS=$(find knowledge_architecture/systems -name "system.map.lucid.json5" -exec grep -l "T[0-6]_" {} \; 2>/dev/null | wc -l || echo "0")
if [ "$T_MAP_REFS" -gt 0 ]; then
    echo "⚠️  Found $T_MAP_REFS system maps with T-level references"
    find knowledge_architecture/systems -name "system.map.lucid.json5" -exec grep -l "T[0-6]_" {} \; 2>/dev/null || true
    WARNINGS=$((WARNINGS+1))
else
    echo "✅ No T-level references found in system maps"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Cutover validation PASSED"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Cutover validation PASSED with warnings ($WARNINGS warnings)"
    exit 0
else
    echo "❌ Cutover validation FAILED ($ERRORS errors, $WARNINGS warnings)"
    exit 1
fi

