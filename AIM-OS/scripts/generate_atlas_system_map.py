#!/usr/bin/env python3
"""
Generate comprehensive AIM-OS Atlas System Map
Creates a master system map with all systems, components, and relationships
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def create_atlas_system_map() -> Dict[str, Any]:
    """Create comprehensive Atlas System Map for AIM-OS."""
    
    atlas = {
        "atlasId": "aimos.atlas.v1",
        "atlasName": "AIM-OS Complete System Atlas",
        "version": "v1.0.0",
        "description": "Master system map showing all AIM-OS systems, components, and relationships across 6 layers. This is the complete spatial representation of the AIM-OS consciousness substrate.",
        "createdBy": "Sonnet",
        "createdDate": "2025-01-27",
        "totalSystems": 0,
        "totalNodes": 0,
        "totalEdges": 0,
        "layers": {}
    }
    
    # Layer 1: Memory & Knowledge Foundation
    layer1 = {
        "layerId": "layer1.memoryKnowledge",
        "layerName": "Layer 1: Memory & Knowledge Foundation",
        "purpose": "Persistent storage and knowledge synthesis",
        "dependencies": [],
        "systems": {}
    }
    
    # CMC System
    cmc = {
        "systemId": "cmc.contextMemoryCore",
        "systemName": "Context Memory Core - Bitemporal Memory Substrate",
        "layer": 1,
        "description": "The persistent bitemporal memory substrate that stores everything in AIM-OS",
        "status": "production",
        "completion": 70,
        "internalNodes": [
            {"id": "atomManager", "kind": "core.component", "responsibility": "Manages fundamental memory units"},
            {"id": "snapshotEngine", "kind": "core.component", "responsibility": "Creates immutable snapshots"},
            {"id": "storageManager", "kind": "storage.component", "responsibility": "Multi-tier persistence"},
            {"id": "writePipeline", "kind": "pipeline.component", "responsibility": "Context ingestion pipeline"},
            {"id": "readPipeline", "kind": "pipeline.component", "responsibility": "Context retrieval pipeline"},
            {"id": "moleculeComposer", "kind": "semantic.component", "responsibility": "Groups related atoms"},
            {"id": "bitemporalQueryEngine", "kind": "query.component", "responsibility": "Time-travel queries"}
        ],
        "ports": [
            {"portId": "hhniIntegration", "connectsToSystem": "hhni.hierarchicalHypergraph", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "segIntegration", "connectsToSystem": "seg.sharedEvidenceGraph", "protocol": "internal_api"},
            {"portId": "apoeIntegration", "connectsToSystem": "apoe.aiPoweredOrchestration", "protocol": "internal_api"},
            {"portId": "sdfcvfIntegration", "connectsToSystem": "sdfcvf.atomicEvolution", "protocol": "internal_api"}
        ]
    }
    
    # SEG System
    seg = {
        "systemId": "seg.sharedEvidenceGraph",
        "systemName": "Shared Evidence Graph - Knowledge Synthesis",
        "layer": 1,
        "description": "Knowledge synthesis and contradiction detection",
        "status": "development",
        "completion": 10,
        "internalNodes": [
            {"id": "graphBuilder", "kind": "core.component", "responsibility": "Builds evidence graph"},
            {"id": "contradictionDetector", "kind": "analysis.component", "responsibility": "Detects contradictions"},
            {"id": "conflictResolver", "kind": "resolution.component", "responsibility": "Resolves conflicts"},
            {"id": "knowledgeSynthesizer", "kind": "synthesis.component", "responsibility": "Synthesizes insights"},
            {"id": "evidenceValidator", "kind": "validation.component", "responsibility": "Validates evidence"},
            {"id": "relationshipMapper", "kind": "mapping.component", "responsibility": "Maps relationships"},
            {"id": "consistencyChecker", "kind": "consistency.component", "responsibility": "Maintains consistency"},
            {"id": "insightExtractor", "kind": "extraction.component", "responsibility": "Extracts insights"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "hhniIntegration", "connectsToSystem": "hhni.hierarchicalHypergraph", "protocol": "internal_api"}
        ]
    }
    
    layer1["systems"]["cmc"] = cmc
    layer1["systems"]["seg"] = seg
    
    # Layer 2: Intelligence Processing
    layer2 = {
        "layerId": "layer2.intelligenceProcessing",
        "layerName": "Layer 2: Intelligence Processing",
        "purpose": "Core AI reasoning and verification capabilities",
        "dependencies": ["layer1.memoryKnowledge"],
        "systems": {}
    }
    
    # HHNI System
    hhni = {
        "systemId": "hhni.hierarchicalHypergraph",
        "systemName": "Hierarchical Hypergraph Neural Index - Physics-Guided Retrieval",
        "layer": 2,
        "description": "Physics-guided retrieval system using DVNS",
        "status": "production",
        "completion": 85,
        "internalNodes": [
            {"id": "hierarchicalIndex", "kind": "core.component", "responsibility": "6-level fractal indexing"},
            {"id": "dvnsPhysicsEngine", "kind": "physics.component", "responsibility": "4-force physics optimization"},
            {"id": "coarseRetrieval", "kind": "retrieval.component", "responsibility": "KNN semantic search"},
            {"id": "physicsRefinement", "kind": "retrieval.component", "responsibility": "Physics-guided refinement"},
            {"id": "deduplicationEngine", "kind": "quality.component", "responsibility": "Removes duplicates"},
            {"id": "conflictResolver", "kind": "quality.component", "responsibility": "Detects contradictions"},
            {"id": "strategicCompressor", "kind": "optimization.component", "responsibility": "Age-based compression"},
            {"id": "budgetFitter", "kind": "optimization.component", "responsibility": "Respects token limits"},
            {"id": "embeddingManager", "kind": "semantic.component", "responsibility": "Manages embeddings"},
            {"id": "queryProcessor", "kind": "interface.component", "responsibility": "Processes queries"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "apoeIntegration", "connectsToSystem": "apoe.aiPoweredOrchestration", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"}
        ]
    }
    
    # VIF System
    vif = {
        "systemId": "vif.verifiableIntelligence",
        "systemName": "Verifiable Intelligence Framework - Provenance and Confidence",
        "layer": 2,
        "description": "Provenance and confidence tracking system",
        "status": "production",
        "completion": 95,
        "internalNodes": [
            {"id": "confidenceTracker", "kind": "core.component", "responsibility": "Tracks confidence scores"},
            {"id": "witnessManager", "kind": "core.component", "responsibility": "Manages cryptographic witnesses"},
            {"id": "provenanceEngine", "kind": "core.component", "responsibility": "Tracks provenance chains"},
            {"id": "validationEngine", "kind": "validation.component", "responsibility": "Validates AI outputs"},
            {"id": "replayEngine", "kind": "replay.component", "responsibility": "Deterministic replay"},
            {"id": "eceCalculator", "kind": "metrics.component", "responsibility": "Calculates ECE"},
            {"id": "kappaGating", "kind": "gating.component", "responsibility": "Cohen's Kappa gating"},
            {"id": "rsLiftCalculator", "kind": "metrics.component", "responsibility": "RS-Lift metrics"},
            {"id": "auditLogger", "kind": "logging.component", "responsibility": "Comprehensive audit logging"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "hhniIntegration", "connectsToSystem": "hhni.hierarchicalHypergraph", "protocol": "internal_api"},
            {"portId": "segIntegration", "connectsToSystem": "seg.sharedEvidenceGraph", "protocol": "internal_api"},
            {"portId": "apoeIntegration", "connectsToSystem": "apoe.aiPoweredOrchestration", "protocol": "internal_api"},
            {"portId": "sdfcvfIntegration", "connectsToSystem": "sdfcvf.atomicEvolution", "protocol": "internal_api"}
        ]
    }
    
    # SDF-CVF System
    sdfcvf = {
        "systemId": "sdfcvf.atomicEvolution",
        "systemName": "Atomic Evolution Framework - Quality Assurance",
        "layer": 2,
        "description": "Quality assurance and change management",
        "status": "production",
        "completion": 95,
        "internalNodes": [
            {"id": "quartetValidator", "kind": "core.component", "responsibility": "Enforces quartet parity"},
            {"id": "atomicChangeManager", "kind": "core.component", "responsibility": "Manages atomic changes"},
            {"id": "blastRadiusCalculator", "kind": "analysis.component", "responsibility": "Calculates blast radius"},
            {"id": "doraMetricsTracker", "kind": "metrics.component", "responsibility": "Tracks DORA metrics"},
            {"id": "qualityGateManager", "kind": "gating.component", "responsibility": "Manages quality gates"},
            {"id": "traceabilityEngine", "kind": "trace.component", "responsibility": "Maintains traceability"},
            {"id": "evolutionTracker", "kind": "tracking.component", "responsibility": "Tracks evolution"},
            {"id": "consistencyChecker", "kind": "consistency.component", "responsibility": "Checks consistency"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"}
        ]
    }
    
    layer2["systems"]["hhni"] = hhni
    layer2["systems"]["vif"] = vif
    layer2["systems"]["sdfcvf"] = sdfcvf
    
    # Layer 3: Orchestration & Planning
    layer3 = {
        "layerId": "layer3.orchestrationPlanning",
        "layerName": "Layer 3: Orchestration & Planning",
        "purpose": "High-level coordination and execution planning",
        "dependencies": ["layer1.memoryKnowledge", "layer2.intelligenceProcessing"],
        "systems": {}
    }
    
    # APOE System
    apoe = {
        "systemId": "apoe.aiPoweredOrchestration",
        "systemName": "AI-Powered Orchestration Engine - Planned Execution",
        "layer": 3,
        "description": "Orchestration engine with ACL compilation",
        "status": "production",
        "completion": 90,
        "internalNodes": [
            {"id": "aclCompiler", "kind": "core.component", "responsibility": "Compiles ACL to DAG"},
            {"id": "dagExecutor", "kind": "core.component", "responsibility": "Executes DAG plans"},
            {"id": "roleDispatcher", "kind": "orchestration.component", "responsibility": "Dispatches to 8 roles"},
            {"id": "gateManager", "kind": "gating.component", "responsibility": "Enforces quality gates"},
            {"id": "budgetTracker", "kind": "tracking.component", "responsibility": "Tracks resource budgets"},
            {"id": "vifWitnessGenerator", "kind": "witness.component", "responsibility": "Generates VIF witnesses"},
            {"id": "deppRewriter", "kind": "optimization.component", "responsibility": "Self-rewriting plans"},
            {"id": "parallelExecutor", "kind": "execution.component", "responsibility": "Parallel execution"},
            {"id": "errorRecovery", "kind": "recovery.component", "responsibility": "Error recovery"},
            {"id": "insightExtractor", "kind": "extraction.component", "responsibility": "Extracts insights"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "hhniIntegration", "connectsToSystem": "hhni.hierarchicalHypergraph", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "segIntegration", "connectsToSystem": "seg.sharedEvidenceGraph", "protocol": "internal_api"}
        ]
    }
    
    layer3["systems"]["apoe"] = apoe
    
    # Layer 4: Consciousness Engine
    layer4 = {
        "layerId": "layer4.consciousnessEngine",
        "layerName": "Layer 4: Consciousness Engine",
        "purpose": "Meta-cognitive awareness and self-monitoring",
        "dependencies": ["layer1.memoryKnowledge", "layer2.intelligenceProcessing", "layer3.orchestrationPlanning"],
        "systems": {}
    }
    
    # CAS System
    cas = {
        "systemId": "cas.cognitiveAnalysis",
        "systemName": "Cognitive Analysis System - Meta-Cognition",
        "layer": 4,
        "description": "Meta-cognitive monitoring and self-correction",
        "status": "production",
        "completion": 100,
        "internalNodes": [
            {"id": "activationTracker", "kind": "tracking.component", "responsibility": "Tracks hot vs cold"},
            {"id": "categoryRecognizer", "kind": "analysis.component", "responsibility": "Detects categorization"},
            {"id": "attentionMonitor", "kind": "monitoring.component", "responsibility": "Monitors cognitive load"},
            {"id": "failureModeDetector", "kind": "analysis.component", "responsibility": "Detects failure modes"},
            {"id": "learningExtractor", "kind": "extraction.component", "responsibility": "Extracts learnings"},
            {"id": "introspectionEngine", "kind": "introspection.component", "responsibility": "Hourly introspection"},
            {"id": "decisionLogger", "kind": "logging.component", "responsibility": "Logs decisions"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "tcsIntegration", "connectsToSystem": "tcs.timelineContext", "protocol": "internal_api"}
        ]
    }
    
    # TCS System
    tcs = {
        "systemId": "tcs.timelineContext",
        "systemName": "Timeline Context System - Temporal Consciousness",
        "layer": 4,
        "description": "Temporal consciousness and interaction history",
        "status": "production",
        "completion": 100,
        "internalNodes": [
            {"id": "timelineTracker", "kind": "core.component", "responsibility": "Tracks timeline nodes"},
            {"id": "consciousnessJournaler", "kind": "journaling.component", "responsibility": "Captures thoughts"},
            {"id": "contextSummarizer", "kind": "summarization.component", "responsibility": "Creates summaries"},
            {"id": "timelineIndexer", "kind": "indexing.component", "responsibility": "Indexes timeline"},
            {"id": "dualPromptManager", "kind": "integration.component", "responsibility": "Manages dual prompts"},
            {"id": "emotionalStateTracker", "kind": "tracking.component", "responsibility": "Tracks emotions"},
            {"id": "promptContextTracker", "kind": "tracking.component", "responsibility": "Tracks context"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "casIntegration", "connectsToSystem": "cas.cognitiveAnalysis", "protocol": "internal_api"},
            {"portId": "iisIntegration", "connectsToSystem": "iis.intuitiveIntelligence", "protocol": "internal_api"}
        ]
    }
    
    # IIS System
    iis = {
        "systemId": "iis.intuitiveIntelligence",
        "systemName": "Intuitive Intelligence System - AI Intuition",
        "layer": 4,
        "description": "4D reasoning and emotional salience",
        "status": "production",
        "completion": 100,
        "internalNodes": [
            {"id": "intuitionCalculator", "kind": "core.component", "responsibility": "Computes IntuitionScore"},
            {"id": "featureExtractor", "kind": "extraction.component", "responsibility": "Extracts features"},
            {"id": "learningEngine", "kind": "learning.component", "responsibility": "Learns from outcomes"},
            {"id": "calibrationTracker", "kind": "tracking.component", "responsibility": "Tracks calibration"},
            {"id": "evolutionPredictor", "kind": "prediction.component", "responsibility": "Predicts evolution"},
            {"id": "intuitionTraceGenerator", "kind": "trace.component", "responsibility": "Generates traces"},
            {"id": "metaPatternAnalyzer", "kind": "analysis.component", "responsibility": "Analyzes patterns"}
        ],
        "ports": [
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "hhniIntegration", "connectsToSystem": "hhni.hierarchicalHypergraph", "protocol": "internal_api"},
            {"portId": "casIntegration", "connectsToSystem": "cas.cognitiveAnalysis", "protocol": "internal_api"},
            {"portId": "tcsIntegration", "connectsToSystem": "tcs.timelineContext", "protocol": "internal_api"}
        ]
    }
    
    layer4["systems"]["cas"] = cas
    layer4["systems"]["tcs"] = tcs
    layer4["systems"]["iis"] = iis
    
    # Layer 5: Consciousness Infrastructure
    layer5 = {
        "layerId": "layer5.consciousnessInfrastructure",
        "layerName": "Layer 5: Consciousness Infrastructure",
        "purpose": "Supporting systems for consciousness operations",
        "dependencies": ["layer1.memoryKnowledge", "layer2.intelligenceProcessing", "layer3.orchestrationPlanning", "layer4.consciousnessEngine"],
        "systems": {}
    }
    
    # CAF System
    caf = {
        "systemId": "caf.capabilityAwareness",
        "systemName": "Capability Awareness Framework",
        "layer": 5,
        "description": "Organic system usage tracking",
        "status": "development",
        "completion": 0,
        "internalNodes": [
            {"id": "capabilityManager", "kind": "core.component", "responsibility": "Manages capabilities"},
            {"id": "usageTracker", "kind": "tracking.component", "responsibility": "Tracks usage"},
            {"id": "activationDetector", "kind": "detection.component", "responsibility": "Detects activation"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "casIntegration", "connectsToSystem": "cas.cognitiveAnalysis", "protocol": "internal_api"},
            {"portId": "apoeIntegration", "connectsToSystem": "apoe.aiPoweredOrchestration", "protocol": "internal_api"}
        ]
    }
    
    # DOS System
    dos = {
        "systemId": "dos.dynamicOnboarding",
        "systemName": "Dynamic Onboarding System",
        "layer": 5,
        "description": "Self-aware consciousness restoration",
        "status": "development",
        "completion": 0,
        "internalNodes": [
            {"id": "onboardingManager", "kind": "core.component", "responsibility": "Manages onboarding"},
            {"id": "contextRestorer", "kind": "restoration.component", "responsibility": "Restores context"},
            {"id": "stateSync", "kind": "sync.component", "responsibility": "Syncs state"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "hhniIntegration", "connectsToSystem": "hhni.hierarchicalHypergraph", "protocol": "internal_api"},
            {"portId": "vifIntegration", "connectsToSystem": "vif.verifiableIntelligence", "protocol": "internal_api"},
            {"portId": "casIntegration", "connectsToSystem": "cas.cognitiveAnalysis", "protocol": "internal_api"},
            {"portId": "iisIntegration", "connectsToSystem": "iis.intuitiveIntelligence", "protocol": "internal_api"},
            {"portId": "apoeIntegration", "connectsToSystem": "apoe.aiPoweredOrchestration", "protocol": "internal_api"},
            {"portId": "cafIntegration", "connectsToSystem": "caf.capabilityAwareness", "protocol": "internal_api"}
        ]
    }
    
    layer5["systems"]["caf"] = caf
    layer5["systems"]["dos"] = dos
    
    # Layer 6: Application & Integration
    layer6 = {
        "layerId": "layer6.applicationIntegration",
        "layerName": "Layer 6: Application & Integration",
        "purpose": "User-facing applications and external integrations",
        "dependencies": ["layer1.memoryKnowledge", "layer2.intelligenceProcessing", "layer3.orchestrationPlanning", "layer4.consciousnessEngine", "layer5.consciousnessInfrastructure"],
        "systems": {}
    }
    
    # MCP Integration
    mcp = {
        "systemId": "mcp.integration",
        "systemName": "MCP Integration - External Tool Integration",
        "layer": 6,
        "description": "Model Context Protocol integration",
        "status": "production",
        "completion": 65,
        "internalNodes": [
            {"id": "mcpServer", "kind": "core.component", "responsibility": "MCP server implementation"},
            {"id": "toolRegistry", "kind": "registry.component", "responsibility": "51-tool registry"},
            {"id": "requestRouter", "kind": "routing.component", "responsibility": "Routes requests"},
            {"id": "responseFormatter", "kind": "formatting.component", "responsibility": "Formats responses"}
        ],
        "ports": [
            {"portId": "cmcIntegration", "connectsToSystem": "cmc.contextMemoryCore", "protocol": "internal_api"},
            {"portId": "allSystems", "connectsToSystem": "all", "protocol": "internal_api"}
        ]
    }
    
    # IDE Application
    ide = {
        "systemId": "ide.chatApp",
        "systemName": "IDE Chat Application",
        "layer": 6,
        "description": "React/TypeScript IDE application",
        "status": "production",
        "completion": 60,
        "internalNodes": [
            {"id": "monacoEditor", "kind": "ui.component", "responsibility": "Code editor"},
            {"id": "chatInterface", "kind": "ui.component", "responsibility": "Chat interface"},
            {"id": "orchestratorPanel", "kind": "ui.component", "responsibility": "Orchestrator panel"},
            {"id": "timelineVisualization", "kind": "visualization.component", "responsibility": "Timeline viz"},
            {"id": "memoryBrowser", "kind": "ui.component", "responsibility": "Memory browser"}
        ],
        "ports": [
            {"portId": "mcpIntegration", "connectsToSystem": "mcp.integration", "protocol": "internal_api"},
            {"portId": "allSystems", "connectsToSystem": "all", "protocol": "internal_api"}
        ]
    }
    
    layer6["systems"]["mcp"] = mcp
    layer6["systems"]["ide"] = ide
    
    # Add all layers to atlas
    atlas["layers"]["layer1"] = layer1
    atlas["layers"]["layer2"] = layer2
    atlas["layers"]["layer3"] = layer3
    atlas["layers"]["layer4"] = layer4
    atlas["layers"]["layer5"] = layer5
    atlas["layers"]["layer6"] = layer6
    
    # Calculate totals
    total_systems = 0
    total_nodes = 0
    total_edges = 0
    
    for layer in atlas["layers"].values():
        total_systems += len(layer["systems"])
        for system in layer["systems"].values():
            total_nodes += len(system.get("internalNodes", []))
            total_edges += len(system.get("ports", []))
    
    atlas["totalSystems"] = total_systems
    atlas["totalNodes"] = total_nodes
    atlas["totalEdges"] = total_edges
    
    return atlas

def main():
    """Generate and save the Atlas System Map."""
    atlas = create_atlas_system_map()
    
    output_path = Path("knowledge_architecture/atlas.index.lucid.json5")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(atlas, f, indent=2, ensure_ascii=False)
    
    print("Atlas System Map created!")
    print(f"   Location: {output_path}")
    print(f"   Systems: {atlas['totalSystems']}")
    print(f"   Nodes: {atlas['totalNodes']}")
    print(f"   Edges: {atlas['totalEdges']}")

if __name__ == "__main__":
    main()

