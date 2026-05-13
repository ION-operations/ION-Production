#!/bin/bash
# Backup L-level documents before T→L cutover
# Usage: ./scripts/cutover/backup_legacy.sh

set -e

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

echo "📦 Backing up L-level documents..."

for system in "${SYSTEMS[@]}"; do
    SRC_DIR="knowledge_architecture/systems/$system"
    DST_DIR="legacy_docs/$system"
    
    if [ -d "$SRC_DIR" ]; then
        mkdir -p "$DST_DIR"
        
        # Copy L-level files if they exist
        if ls "$SRC_DIR"/L*.md 1> /dev/null 2>&1; then
            cp "$SRC_DIR"/L*.md "$DST_DIR"/ 2>/dev/null || true
            echo "✅ Backed up $system"
        else
            echo "⚠️  No L-level files found for $system (may be first cutover)"
        fi
    else
        echo "⚠️  System directory not found: $SRC_DIR"
    fi
done

echo ""
echo "✅ Backup complete"
echo "📁 Backup location: legacy_docs/"

