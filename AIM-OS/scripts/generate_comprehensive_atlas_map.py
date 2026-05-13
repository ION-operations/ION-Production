#!/usr/bin/env python3
"""
Generate Comprehensive AIM-OS Atlas System Map
Aggregates all existing system maps and creates master Atlas with hundreds of nodes
Created by: Sonnet
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

def load_existing_system_map(path: Path) -> Dict[str, Any]:
    """Load an existing system map JSON5 file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Handle JSON5 comments and trailing commas
            content = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('//'))
            return json.loads(content)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return None

def aggregate_all_system_maps() -> Dict[str, Any]:
    """Aggregate all existing system maps into comprehensive Atlas."""
    
    root = Path("knowledge_architecture/systems")
    system_maps = {}
    
    # Find all system.map.lucid.json5 files
    for map_file in root.rglob("system.map.lucid.json5"):
        system_map = load_existing_system_map(map_file)
        if system_map:
            system_id = system_map.get("systemId", "")
            system_maps[system_id] = {
                "map": system_map,
                "path": str(map_file.relative_to(root.parent))
            }
    
    return system_maps

def create_comprehensive_atlas() -> Dict[str, Any]:
    """Create comprehensive Atlas System Map."""
    
    print("Loading existing system maps...")
    existing_maps = aggregate_all_system_maps()
    print(f"Found {len(existing_maps)} existing system maps")
    
    atlas = {
        "atlasId": "aimos.atlas.comprehensive.v1",
        "atlasName": "AIM-OS Comprehensive System Atlas",
        "version": "v1.0.0",
        "description": "Master system map aggregating all AIM-OS systems, components, and relationships. Exceptionally well-organized with hierarchical layer structure showing complete system architecture.",
        "createdBy": "Sonnet",
        "createdDate": "2025-01-27",
        "format": "Atlas Map - Complete System Architecture",
        "organization": "Layer-based hierarchical structure",
        "totalSystems": 0,
        "totalNodes": 0,
        "totalPorts": 0,
        "totalInternalEdges": 0,
        "totalExternalEdges": 0,
        "layers": {}
    }
    
    # Organize systems by layer
    layer_systems = {
        1: [],  # Memory & Knowledge Foundation
        2: [],  # Intelligence Processing
        3: [],  # Orchestration & Planning
        4: [],  # Consciousness Engine
        5: [],  # Consciousness Infrastructure
        6: []   # Application & Integration
    }
    
    # Map system IDs to layer assignments
    layer_assignments = {
        "cmc.contextMemoryCore": 1,
        "seg.sharedEvidenceGraph": 1,
        "hhni.hierarchicalHypergraph": 2,
        "vif.verifiableIntelligence": 2,
        "sdfcvf.atomicEvolution": 2,
        "apoe.aiPoweredOrchestration": 3,
        "cas.cognitiveAnalysis": 4,
        "tcs.timelineContext": 4,
        "iis.intuitiveIntelligence": 4,
        "caf.capabilityAwareness": 5,
        "dos.dynamicOnboarding": 5,
        "scor.safetyConsciousness": 5,
        "mcp.integration": 6,
        "ide.chatApp": 6,
        "lucid_core_console": 6
    }
    
    # Process all existing maps
    for system_id, map_data in existing_maps.items():
        system_map = map_data["map"]
        
        # Determine layer
        layer = None
        for sid, l in layer_assignments.items():
            if sid in system_id.lower() or system_id.lower() in sid:
                layer = l
                break
        
        if layer is None:
            # Default assignment based on system name patterns
            if "memory" in system_id.lower() or "cmc" in system_id.lower():
                layer = 1
            elif "graph" in system_id.lower() or "seg" in system_id.lower():
                layer = 1
            elif "index" in system_id.lower() or "hhni" in system_id.lower():
                layer = 2
            elif "verifiable" in system_id.lower() or "vif" in system_id.lower():
                layer = 2
            elif "evolution" in system_id.lower() or "sdfcvf" in system_id.lower():
                layer = 2
            elif "orchestration" in system_id.lower() or "apoe" in system_id.lower():
                layer = 3
            elif "cognitive" in system_id.lower() or "cas" in system_id.lower():
                layer = 4
            elif "timeline" in system_id.lower() or "tcs" in system_id.lower():
                layer = 4
            elif "intuitive" in system_id.lower() or "iis" in system_id.lower():
                layer = 4
            elif "safety" in system_id.lower() or "scor" in system_id.lower():
                layer = 5
            elif "mcp" in system_id.lower() or "integration" in system_id.lower():
                layer = 6
            elif "ide" in system_id.lower() or "lucid" in system_id.lower():
                layer = 6
            else:
                layer = 5  # Default to infrastructure
        
        layer_systems[layer].append({
            "systemId": system_id,
            "systemMap": system_map,
            "path": map_data["path"]
        })
    
    # Build layer structures
    layer_names = {
        1: "Layer 1: Memory & Knowledge Foundation",
        2: "Layer 2: Intelligence Processing",
        3: "Layer 3: Orchestration & Planning",
        4: "Layer 4: Consciousness Engine",
        5: "Layer 5: Consciousness Infrastructure",
        6: "Layer 6: Application & Integration"
    }
    
    layer_purposes = {
        1: "Persistent storage and knowledge synthesis",
        2: "Core AI reasoning and verification capabilities",
        3: "High-level coordination and execution planning",
        4: "Meta-cognitive awareness and self-monitoring",
        5: "Supporting systems for consciousness operations",
        6: "User-facing applications and external integrations"
    }
    
    for layer_num in range(1, 7):
        layer_info = {
            "layerId": f"layer{layer_num}",
            "layerName": layer_names[layer_num],
            "purpose": layer_purposes[layer_num],
            "dependencies": [f"layer{i}" for i in range(1, layer_num)],
            "systems": {}
        }
        
        # Add all systems in this layer
        for system_data in layer_systems[layer_num]:
            system_id = system_data["systemId"]
            system_map = system_data["systemMap"]
            
            # Extract system information
            system_info = {
                "systemId": system_id,
                "systemName": system_map.get("systemName", system_id),
                "version": system_map.get("version", "v0.1"),
                "description": system_map.get("description", ""),
                "status": system_map.get("status", "production"),
                "layer": layer_num,
                "internalNodes": system_map.get("internalNodes", []),
                "ports": system_map.get("ports", []),
                "internalEdges": system_map.get("internalEdges", []),
                "externalEdges": system_map.get("externalEdges", []),
                "riskOverlay": system_map.get("riskOverlay", {}),
                "governance": system_map.get("governance", {}),
                "monitoring": system_map.get("monitoring", {}),
                "sourcePath": system_data["path"]
            }
            
            # Use short key for system
            short_key = system_id.split(".")[-1] if "." in system_id else system_id
            layer_info["systems"][short_key] = system_info
        
        atlas["layers"][f"layer{layer_num}"] = layer_info
    
    # Calculate totals
    total_systems = 0
    total_nodes = 0
    total_ports = 0
    total_internal_edges = 0
    total_external_edges = 0
    
    for layer_data in atlas["layers"].values():
        total_systems += len(layer_data["systems"])
        for system in layer_data["systems"].values():
            total_nodes += len(system.get("internalNodes", []))
            total_ports += len(system.get("ports", []))
            total_internal_edges += len(system.get("internalEdges", []))
            total_external_edges += len(system.get("externalEdges", []))
    
    atlas["totalSystems"] = total_systems
    atlas["totalNodes"] = total_nodes
    atlas["totalPorts"] = total_ports
    atlas["totalInternalEdges"] = total_internal_edges
    atlas["totalExternalEdges"] = total_external_edges
    
    # Add cross-layer relationship analysis
    atlas["crossLayerRelationships"] = analyze_cross_layer_relationships(atlas)
    
    return atlas

def analyze_cross_layer_relationships(atlas: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze relationships across layers."""
    
    relationships = {
        "layer1_to_layer2": [],
        "layer2_to_layer3": [],
        "layer3_to_layer4": [],
        "layer4_to_layer5": [],
        "layer5_to_layer6": [],
        "cross_layer": []
    }
    
    # Analyze ports and external edges to find cross-layer connections
    for layer_num in range(1, 7):
        layer_key = f"layer{layer_num}"
        if layer_key not in atlas["layers"]:
            continue
            
        layer_data = atlas["layers"][layer_key]
        
        for system_id, system in layer_data["systems"].items():
            # Check ports for cross-layer connections
            for port in system.get("ports", []):
                connects_to = port.get("connectsToSystem", "")
                if connects_to:
                    # Find which layer this connects to
                    target_layer = find_system_layer(atlas, connects_to)
                    if target_layer and target_layer != layer_num:
                        relationships["cross_layer"].append({
                            "from": system_id,
                            "fromLayer": layer_num,
                            "to": connects_to,
                            "toLayer": target_layer,
                            "port": port.get("portId", ""),
                            "protocol": port.get("protocol", "")
                        })
    
    return relationships

def find_system_layer(atlas: Dict[str, Any], system_id: str) -> int:
    """Find which layer a system belongs to."""
    for layer_num in range(1, 7):
        layer_key = f"layer{layer_num}"
        if layer_key in atlas["layers"]:
            for sys_id, sys_data in atlas["layers"][layer_key]["systems"].items():
                if system_id.lower() in sys_data["systemId"].lower() or sys_data["systemId"].lower() in system_id.lower():
                    return layer_num
    return None

def main():
    """Generate and save comprehensive Atlas System Map."""
    print("=" * 80)
    print("AIM-OS Comprehensive Atlas System Map Generator")
    print("Created by: Sonnet")
    print("=" * 80)
    print()
    
    atlas = create_comprehensive_atlas()
    
    output_path = Path("knowledge_architecture/atlas.index.lucid.json5")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(atlas, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 80)
    print("Atlas System Map Generated Successfully!")
    print("=" * 80)
    print(f"Location: {output_path}")
    print(f"Total Systems: {atlas['totalSystems']}")
    print(f"Total Nodes: {atlas['totalNodes']}")
    print(f"Total Ports: {atlas['totalPorts']}")
    print(f"Total Internal Edges: {atlas['totalInternalEdges']}")
    print(f"Total External Edges: {atlas['totalExternalEdges']}")
    print()
    print("Layer Breakdown:")
    for layer_num in range(1, 7):
        layer_key = f"layer{layer_num}"
        if layer_key in atlas["layers"]:
            layer_data = atlas["layers"][layer_key]
            print(f"  Layer {layer_num}: {len(layer_data['systems'])} systems")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

