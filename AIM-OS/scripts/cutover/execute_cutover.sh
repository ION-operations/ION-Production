#!/bin/bash
# Master T→L Cutover Execution Script
# Usage: ./scripts/cutover/execute_cutover.sh

set -e

echo "🚀 T→L Cutover Execution"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SYSTEMS=(
    "cmc"
    "hhni"
    "vif"
    "apoe"
    "seg"
    "sdfcvf"
    "cognitive_analysis"
    "cross_model_consciousness"
    "timeline_context_system"
    "dual_prompt_architecture"
    "capability_awareness"
    "dynamic_onboarding"
    "advanced_monaco_editor"
    "autonomous_research_dream"
)

# Step 1: Backup
echo "📦 Step 1: Backing up L-level documents..."
./scripts/cutover/backup_legacy.sh
echo ""

# Step 2: Rename T→L for all systems
echo "🔄 Step 2: Renaming T→L for all systems..."
for system in "${SYSTEMS[@]}"; do
    ./scripts/cutover/rename_t2l.sh "$system"
done
echo ""

# Step 3: Update references
echo "🔄 Step 3: Updating references..."
python scripts/cutover/update_references.py
echo ""

# Step 4: Remove banners
echo "🔄 Step 4: Removing transitional banners..."
python scripts/cutover/remove_banners.py
echo ""

# Step 5: Validate
echo "🔍 Step 5: Validating cutover..."
./scripts/cutover/validate_cutover.sh
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cutover execution complete!"
echo ""
echo "Next steps:"
echo "1. Run L0-L6 gate validation"
echo "2. Update gate results"
echo "3. Update tracking files"
echo "4. Document completion"

