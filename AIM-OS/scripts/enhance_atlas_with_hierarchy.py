#!/usr/bin/env python3
"""
Enhance Atlas System Map with Complete Hierarchical Structure
Adds component branches, subcomponents, and full relationship mapping
Created by: Sonnet
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def load_atlas() -> Dict[str, Any]:
    """Load the Atlas system map."""
    atlas_path = Path("knowledge_architecture/atlas.index.lucid.json5")
    with open(atlas_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def enhance_atlas_with_hierarchy(atlas: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance Atlas with complete hierarchical structure."""
    
    enhanced = {
        "atlasId": atlas["atlasId"],
        "atlasName": atlas["atlasName"] + " - Enhanced Hierarchical",
        "version": "v2.0.0",
        "description": atlas["description"] + " Enhanced with complete hierarchical component structure showing all branches, subcomponents, and relationships.",
        "createdBy": "Sonnet",
        "createdDate": "2025-01-27",
        "format": "Atlas Map - Complete Hierarchical Architecture",
        "organization": "Layer → System → Component → Subcomponent hierarchy",
        "totalSystems": atlas["totalSystems"],
        "totalNodes": atlas["totalNodes"],
        "totalPorts": atlas["totalPorts"],
        "totalInternalEdges": atlas["totalInternalEdges"],
        "totalExternalEdges": atlas["totalExternalEdges"],
        "hierarchicalStructure": {},
        "layers": {}
    }
    
    # Process each layer and enhance with hierarchical structure
    for layer_key in sorted(atlas["layers"].keys()):
        layer_data = atlas["layers"][layer_key]
        layer_num = layer_key.replace("layer", "")
        
        enhanced_layer = {
            "layerId": layer_data["layerId"],
            "layerName": layer_data["layerName"],
            "purpose": layer_data["purpose"],
            "dependencies": layer_data["dependencies"],
            "systems": {}
        }
        
        # Process each system in the layer
        for sys_key, system in layer_data["systems"].items():
            if not system.get("systemId") or not system.get("systemName"):
                continue
            
            enhanced_system = {
                "systemId": system["systemId"],
                "systemName": system["systemName"],
                "version": system.get("version", "v0.1"),
                "description": system.get("description", ""),
                "status": system.get("status", "production"),
                "layer": system.get("layer", int(layer_num)),
                "sourcePath": system.get("sourcePath", ""),
                
                # Hierarchical component structure
                "components": {
                    "byKind": {},
                    "byRelationship": {},
                    "hierarchicalTree": {}
                },
                
                # Original data preserved
                "internalNodes": system.get("internalNodes", []),
                "ports": system.get("ports", []),
                "internalEdges": system.get("internalEdges", []),
                "externalEdges": system.get("externalEdges", []),
                "riskOverlay": system.get("riskOverlay", {}),
                "governance": system.get("governance", {}),
                "monitoring": system.get("monitoring", {})
            }
            
            # Organize components by kind
            components_by_kind = {}
            for comp in system.get("internalNodes", []):
                kind = comp.get("kind", "unknown.component")
                if kind not in components_by_kind:
                    components_by_kind[kind] = []
                components_by_kind[kind].append(comp)
            
            enhanced_system["components"]["byKind"] = components_by_kind
            
            # Build component relationship tree
            component_tree = {}
            component_ids = {comp.get("id"): comp for comp in system.get("internalNodes", [])}
            
            # Map components by their relationships
            for edge in system.get("internalEdges", []):
                from_comp = edge.get("from")
                to_comp = edge.get("to")
                
                if from_comp not in component_tree:
                    component_tree[from_comp] = {
                        "component": component_ids.get(from_comp, {}),
                        "children": [],
                        "parents": [],
                        "relationships": []
                    }
                
                if to_comp not in component_tree:
                    component_tree[to_comp] = {
                        "component": component_ids.get(to_comp, {}),
                        "children": [],
                        "parents": [],
                        "relationships": []
                    }
                
                # Add relationship
                component_tree[from_comp]["children"].append(to_comp)
                component_tree[to_comp]["parents"].append(from_comp)
                component_tree[from_comp]["relationships"].append({
                    "to": to_comp,
                    "type": edge.get("type", ""),
                    "data_flow": edge.get("data_flow", "")
                })
            
            enhanced_system["components"]["hierarchicalTree"] = component_tree
            
            # Map components by integration ports
            integration_map = {}
            for port in system.get("ports", []):
                port_id = port.get("portId", "")
                connects_to = port.get("connectsToSystem", "")
                
                # Find components that might handle this port
                # (based on component names or responsibilities)
                handling_components = []
                for comp in system.get("internalNodes", []):
                    comp_id = comp.get("id", "").lower()
                    comp_resp = comp.get("responsibility", "").lower()
                    
                    # Check if component name/responsibility suggests port handling
                    if (port_id.lower() in comp_id or 
                        port_id.lower() in comp_resp or
                        "integration" in comp_id or
                        "port" in comp_id or
                        "interface" in comp_id):
                        handling_components.append(comp.get("id"))
                
                if handling_components:
                    integration_map[port_id] = {
                        "port": port,
                        "handlingComponents": handling_components,
                        "connectsToSystem": connects_to
                    }
            
            enhanced_system["components"]["byRelationship"] = integration_map
            
            # Use short key for system
            short_key = sys_key if sys_key else system["systemId"].split(".")[-1]
            enhanced_layer["systems"][short_key] = enhanced_system
        
        enhanced["layers"][layer_key] = enhanced_layer
    
    # Build global hierarchical structure
    enhanced["hierarchicalStructure"] = {
        "layers": len(enhanced["layers"]),
        "systems": {},
        "componentDepth": {},
        "relationshipGraph": {}
    }
    
    # Calculate component depth for each system
    for layer_key, layer_data in enhanced["layers"].items():
        for sys_key, system in layer_data["systems"].items():
            tree = system["components"]["hierarchicalTree"]
            
            # Calculate max depth
            max_depth = 0
            def calculate_depth(comp_id, visited=None):
                if visited is None:
                    visited = set()
                if comp_id in visited:
                    return 0
                visited.add(comp_id)
                
                if comp_id not in tree:
                    return 1
                
                children = tree[comp_id].get("children", [])
                if not children:
                    return 1
                
                return 1 + max((calculate_depth(child, visited.copy()) for child in children), default=0)
            
            for comp_id in tree.keys():
                depth = calculate_depth(comp_id)
                max_depth = max(max_depth, depth)
            
            enhanced["hierarchicalStructure"]["componentDepth"][system["systemId"]] = {
                "maxDepth": max_depth,
                "totalComponents": len(system["components"]["hierarchicalTree"]),
                "rootComponents": [comp_id for comp_id, data in tree.items() if not data.get("parents")]
            }
    
    return enhanced

def main():
    """Enhance Atlas with hierarchical structure."""
    print("=" * 80)
    print("AIM-OS Atlas Hierarchical Enhancement")
    print("Created by: Sonnet")
    print("=" * 80)
    print()
    
    atlas = load_atlas()
    enhanced = enhance_atlas_with_hierarchy(atlas)
    
    # Save enhanced Atlas
    output_path = Path("knowledge_architecture/atlas.index.enhanced.lucid.json5")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced, f, indent=2, ensure_ascii=False)
    
    print(f"Enhanced hierarchical Atlas saved to: {output_path}")
    print()
    print("Enhancements:")
    print(f"  - Components organized by kind: {sum(len(sys['components']['byKind']) for layer in enhanced['layers'].values() for sys in layer['systems'].values())} kinds")
    print(f"  - Component hierarchical trees: {sum(len(sys['components']['hierarchicalTree']) for layer in enhanced['layers'].values() for sys in layer['systems'].values())} trees")
    print(f"  - Integration mappings: {sum(len(sys['components']['byRelationship']) for layer in enhanced['layers'].values() for sys in layer['systems'].values())} mappings")
    print()
    print("=" * 80)
    print("Atlas Enhancement Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

