#!/bin/bash
# Rename T-level files to L-level
# Usage: ./scripts/cutover/rename_t2l.sh <system_name>

set -e

SYSTEM=$1

if [ -z "$SYSTEM" ]; then
    echo "❌ Usage: $0 <system_name>"
    echo "Example: $0 cmc"
    exit 1
fi

SYSTEM_DIR="knowledge_architecture/systems/$SYSTEM"

if [ ! -d "$SYSTEM_DIR" ]; then
    echo "❌ System directory not found: $SYSTEM_DIR"
    exit 1
fi

cd "$SYSTEM_DIR"

echo "🔄 Renaming T→L for $SYSTEM..."

RENAMED=0

# Rename files
[ -f "T0_executive.md" ] && mv "T0_executive.md" "L0_executive.md" && RENAMED=$((RENAMED+1))
[ -f "T1_overview.md" ] && mv "T1_overview.md" "L1_overview.md" && RENAMED=$((RENAMED+1))
[ -f "T2_architecture.md" ] && mv "T2_architecture.md" "L2_architecture.md" && RENAMED=$((RENAMED+1))
[ -f "T3_detailed.md" ] && mv "T3_detailed.md" "L3_detailed.md" && RENAMED=$((RENAMED+1))
[ -f "T4_complete.md" ] && mv "T4_complete.md" "L4_complete.md" && RENAMED=$((RENAMED+1))
[ -f "T6_complete.md" ] && mv "T6_complete.md" "L6_complete.md" && RENAMED=$((RENAMED+1))

if [ $RENAMED -eq 0 ]; then
    echo "⚠️  No T-level files found to rename"
else
    echo "✅ Renamed $RENAMED files for $SYSTEM"
fi

