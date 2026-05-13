#!/usr/bin/env python3
"""Test which packages can be imported successfully."""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

packages_to_test = [
    ("advanced_monaco_editor", None),  # TypeScript, won't import
    ("agent", "conscious_agent"),
    ("ai_collaboration", "ai_messaging"),
    ("aimos_mobile_app", None),  # TypeScript
    ("aimos-sdk", None),  # TypeScript
    ("api_service_registry", None),
    ("apoe", None),
    ("apoe_runner", None),
    ("autonomous_protocol", None),
    ("autonomous_research_dream", None),
    ("browser-automation-service", None),  # TypeScript
    ("capability_awareness", None),
    ("cas", "ActivationTracker"),
    ("cmc_service", "MemoryStore"),
    ("consciousness_analyzer", None),
    ("consciousness_creativity_engine", None),
    ("consciousness_error_learning", None),
    ("consciousness_learning_engine", None),
    ("consciousness_optimization_detector", None),
    ("context_bootloader", None),
    ("deepsearch", None),
    ("doc_builder", None),
    ("hhni", "HierarchicalIndex"),
    ("holographic_memory", None),
    ("icip_search", None),
    ("ide_chat_app", None),  # TypeScript/React
    ("igodn", None),  # TypeScript
    ("integration_tests", None),
    ("intent_classification", None),
    ("intuitive_intelligence_system", None),
    ("llm_client", None),
    ("log_sentinels", None),
    ("lucid_core_console", None),  # TypeScript
    ("lucid_document_editor", None),  # TypeScript
    ("lucid_mcp_server", None),
    ("lucid_orchestrator", None),  # TypeScript
    ("mcp_data_integration", None),
    ("mcp_debugging_system", None),
    ("mcp_rag_proxy", None),
    ("mcp_server", None),
    ("meta_optimizer", None),
    ("meta_reasoning", None),
    ("nl_tags", None),
    ("orchestration_builder", None),
    ("plix", None),  # TypeScript
    ("prompt_chains", None),
    ("prompt_chain_executor", None),
    ("quaternion_kernel", None),  # Rust
    ("quaternion_math", None),
    ("router", None),
    ("router_api_server", None),
    ("safety_systems", None),
    ("schemas", None),
    ("scor", None),
    ("sdfcvf", None),
    ("seg", "SEGraph"),
    ("sis", None),
    ("specialist_system", None),
    ("temporal_consciousness", None),
    ("timeline_context_system", None),
    ("unified", None),
    ("vif", "VIF"),
]

results = {"success": [], "failed": [], "skipped": []}

print("=" * 60)
print("PACKAGE IMPORT TEST")
print("=" * 60)

for package_name, test_class in packages_to_test:
    # Skip TypeScript/Rust packages
    if package_name in ["advanced_monaco_editor", "aimos_mobile_app", "aimos-sdk", 
                        "browser-automation-service", "ide_chat_app", "igodn",
                        "lucid_core_console", "lucid_document_editor", "lucid_orchestrator",
                        "plix", "quaternion_kernel"]:
        print(f"⏭️  {package_name}: SKIPPED (not Python)")
        results["skipped"].append(package_name)
        continue
    
    try:
        if test_class:
            exec(f"from {package_name} import {test_class}")
        else:
            exec(f"import {package_name}")
        print(f"✅ {package_name}: SUCCESS")
        results["success"].append(package_name)
    except Exception as e:
        error_msg = str(e)[:50]
        print(f"❌ {package_name}: FAILED - {error_msg}")
        results["failed"].append((package_name, str(e)))

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"✅ Success: {len(results['success'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⏭️  Skipped: {len(results['skipped'])}")
print(f"📊 Total: {len(packages_to_test)}")

if results['failed']:
    print("\n" + "=" * 60)
    print("FAILURES DETAIL")
    print("=" * 60)
    for pkg, err in results['failed']:
        print(f"\n{pkg}:")
        print(f"  {err[:200]}")

