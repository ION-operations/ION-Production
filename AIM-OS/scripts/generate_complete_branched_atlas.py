#!/usr/bin/env python3
"""
Generate Complete Branched Atlas System Map
Includes Layers → Systems → Components → Subcomponents → Deep Hierarchies
Created by: Sonnet
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set

def load_atlas() -> Dict[str, Any]:
    """Load the Atlas system map."""
    atlas_path = Path("knowledge_architecture/atlas.index.lucid.json5")
    with open(atlas_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sanitize_id(name: str) -> str:
    """Sanitize names for Mermaid node IDs."""
    return name.replace(" ", "_").replace(".", "_").replace("-", "_").replace("(", "").replace(")", "").replace("/", "_").replace(":", "").lower()

def get_subcomponents_for_component(comp_id: str, comp_kind: str, system_id: str) -> List[Dict[str, Any]]:
    """Get subcomponents for a component based on known hierarchies."""
    
    subcomponents = []
    
    # HHNI hierarchicalIndex has 6 levels
    if comp_id == "hierarchicalIndex" and "hhni" in system_id.lower():
        levels = [
            {"id": "level_system", "name": "Level 1: System", "kind": "index.level"},
            {"id": "level_section", "name": "Level 2: Section", "kind": "index.level"},
            {"id": "level_paragraph", "name": "Level 3: Paragraph", "kind": "index.level"},
            {"id": "level_sentence", "name": "Level 4: Sentence", "kind": "index.level"},
            {"id": "level_word", "name": "Level 5: Word", "kind": "index.level"},
            {"id": "level_subword", "name": "Level 6: Subword", "kind": "index.level"}
        ]
        subcomponents.extend(levels)
    
    # CMC atomManager has atom fields
    if comp_id == "atomManager" and "cmc" in system_id.lower():
        fields = [
            {"id": "atom_schema", "name": "Atom Schema", "kind": "schema.field"},
            {"id": "modality_system", "name": "Modality System", "kind": "schema.field"},
            {"id": "content_ref", "name": "Content Reference", "kind": "schema.field"},
            {"id": "embedding_field", "name": "Embeddings", "kind": "schema.field"},
            {"id": "tags_tpv", "name": "Tags & TPV", "kind": "schema.field"},
            {"id": "hhni_path", "name": "HHNI Path", "kind": "schema.field"},
            {"id": "vif_provenance", "name": "VIF Provenance", "kind": "schema.field"}
        ]
        subcomponents.extend(fields)
    
    # CMC writePipeline has pipeline stages
    if comp_id == "writePipeline" and "cmc" in system_id.lower():
        stages = [
            {"id": "stage_ingest", "name": "Ingest", "kind": "pipeline.stage"},
            {"id": "stage_atomize", "name": "Atomize", "kind": "pipeline.stage"},
            {"id": "stage_enrich", "name": "Enrich", "kind": "pipeline.stage"},
            {"id": "stage_index", "name": "Index", "kind": "pipeline.stage"},
            {"id": "stage_gate", "name": "Gate", "kind": "pipeline.stage"},
            {"id": "stage_persist", "name": "Persist", "kind": "pipeline.stage"},
            {"id": "stage_snapshot", "name": "Snapshot", "kind": "pipeline.stage"}
        ]
        subcomponents.extend(stages)
    
    # CMC readPipeline has pipeline stages
    if comp_id == "readPipeline" and "cmc" in system_id.lower():
        stages = [
            {"id": "stage_query", "name": "Query", "kind": "pipeline.stage"},
            {"id": "stage_hhni_lookup", "name": "HHNI Lookup", "kind": "pipeline.stage"},
            {"id": "stage_dvns_optimize", "name": "DVNS Optimize", "kind": "pipeline.stage"},
            {"id": "stage_deduplicate", "name": "Deduplicate", "kind": "pipeline.stage"},
            {"id": "stage_budget_fit", "name": "Budget Fit", "kind": "pipeline.stage"}
        ]
        subcomponents.extend(stages)
    
    # HHNI dvnsPhysicsEngine has 4 forces
    if comp_id == "dvnsPhysicsEngine" and "hhni" in system_id.lower():
        forces = [
            {"id": "force_gravity", "name": "Gravity Force", "kind": "physics.force"},
            {"id": "force_repulsion", "name": "Repulsion Force", "kind": "physics.force"},
            {"id": "force_elastic", "name": "Elastic Force", "kind": "physics.force"},
            {"id": "force_damping", "name": "Damping Force", "kind": "physics.force"}
        ]
        subcomponents.extend(forces)
    
    # APOE roleDispatcher has 8 roles
    if comp_id == "roleDispatcher" and "apoe" in system_id.lower():
        roles = [
            {"id": "role_planner", "name": "Planner Role", "kind": "orchestration.role"},
            {"id": "role_retriever", "name": "Retriever Role", "kind": "orchestration.role"},
            {"id": "role_reasoner", "name": "Reasoner Role", "kind": "orchestration.role"},
            {"id": "role_verifier", "name": "Verifier Role", "kind": "orchestration.role"},
            {"id": "role_builder", "name": "Builder Role", "kind": "orchestration.role"},
            {"id": "role_critic", "name": "Critic Role", "kind": "orchestration.role"},
            {"id": "role_operator", "name": "Operator Role", "kind": "orchestration.role"},
            {"id": "role_witness", "name": "Witness Role", "kind": "orchestration.role"}
        ]
        subcomponents.extend(roles)
    
    # StorageManager has storage tiers
    if comp_id == "storageManager" and "cmc" in system_id.lower():
        tiers = [
            {"id": "tier_vector", "name": "Vector Store", "kind": "storage.tier"},
            {"id": "tier_object", "name": "Object Store", "kind": "storage.tier"},
            {"id": "tier_metadata", "name": "Metadata Store", "kind": "storage.tier"},
            {"id": "tier_graph", "name": "Graph Store", "kind": "storage.tier"}
        ]
        subcomponents.extend(tiers)
    
    return subcomponents

def generate_complete_branched_mermaid(atlas: Dict[str, Any]) -> str:
    """Generate complete branched Mermaid with subcomponents."""
    
    lines = []
    lines.append("```mermaid")
    lines.append("graph TB")
    lines.append("")
    lines.append("    %% =========================================")
    lines.append("    %% AIM-OS COMPLETE BRANCHED SYSTEM ARCHITECTURE")
    lines.append("    %% Full Hierarchy: Layers → Systems → Components → Subcomponents")
    lines.append("    %% Generated by Sonnet")
    lines.append("    %% =========================================")
    lines.append("    %% Systems: " + str(atlas["totalSystems"]) + " | Components: " + str(atlas["totalNodes"]) + " | Plus Subcomponents")
    lines.append("")
    
    # Collect all systems with components and subcomponents
    systems_with_full_structure = {}
    total_subcomponents = 0
    
    for layer_key in sorted(atlas["layers"].keys()):
        layer_data = atlas["layers"][layer_key]
        layer_num = layer_key.replace("layer", "")
        
        for sys_key, system in layer_data["systems"].items():
            if not system.get("systemId") or not system.get("systemName"):
                continue
            
            sys_id = sanitize_id(system["systemId"])
            sys_name = get_short_name(system["systemName"])
            
            # Build component structure with subcomponents
            components_with_subs = []
            for comp in system.get("internalNodes", []):
                comp_id = comp.get("id", "")
                comp_kind = comp.get("kind", "component")
                
                # Get subcomponents
                subcomponents = get_subcomponents_for_component(comp_id, comp_kind, sys_id)
                total_subcomponents += len(subcomponents)
                
                components_with_subs.append({
                    "component": comp,
                    "subcomponents": subcomponents
                })
            
            systems_with_full_structure[sys_id] = {
                "name": sys_name,
                "full_name": system["systemName"],
                "layer": layer_num,
                "components": components_with_subs,
                "internalEdges": system.get("internalEdges", []),
                "ports": system.get("ports", [])
            }
    
    # Layer configuration
    layer_configs = {
        "1": {"name": "Layer 1: Memory & Knowledge Foundation", "color": "#fff3e0", "stroke": "#e65100"},
        "2": {"name": "Layer 2: Intelligence Processing", "color": "#e8f5e9", "stroke": "#1b5e20"},
        "3": {"name": "Layer 3: Orchestration & Planning", "color": "#f3e5f5", "stroke": "#4a148c"},
        "4": {"name": "Layer 4: Consciousness Engine", "color": "#fce4ec", "stroke": "#880e4f"},
        "5": {"name": "Layer 5: Consciousness Infrastructure", "color": "#f1f8e9", "stroke": "#33691e"},
        "6": {"name": "Layer 6: Application & Integration", "color": "#e1f5fe", "stroke": "#01579b"}
    }
    
    # Group systems by layer
    systems_by_layer = {}
    for sys_id, sys_data in systems_with_full_structure.items():
        layer = sys_data["layer"]
        if layer not in systems_by_layer:
            systems_by_layer[layer] = []
        systems_by_layer[layer].append(sys_id)
    
    # Create complete nested structure
    for layer_num in sorted(systems_by_layer.keys()):
        systems = systems_by_layer[layer_num]
        if not systems:
            continue
        
        config = layer_configs[layer_num]
        lines.append(f"    subgraph L{layer_num}[\"{config['name']}\"]")
        
        for sys_id in systems:
            sys_data = systems_with_full_structure[sys_id]
            lines.append(f"        subgraph {sys_id}[\"{sys_data['name']}\"]")
            
            # Add components with their subcomponents
            for comp_data in sys_data["components"]:
                comp = comp_data["component"]
                comp_id = sanitize_id(comp.get("id", ""))
                comp_name = comp.get("id", "").replace("_", " ").title()[:25]
                subcomponents = comp_data["subcomponents"]
                
                if subcomponents:
                    # Component with subcomponents
                    lines.append(f"            subgraph {sys_id}_{comp_id}[\"{comp_name}\"]")
                    for subcomp in subcomponents:
                        subcomp_id = sanitize_id(subcomp["id"])
                        subcomp_name = subcomp["name"][:20]
                        lines.append(f"                {sys_id}_{comp_id}_{subcomp_id}[\"{subcomp_name}\"]")
                    lines.append("            end")
                else:
                    # Component without subcomponents
                    lines.append(f"            {sys_id}_{comp_id}[\"{comp_name}\"]")
            
            lines.append("        end")
        
        lines.append("    end")
        lines.append("")
    
    # Add component-to-component connections
    lines.append("    %% Component-to-Component Connections")
    connections_added = set()
    
    for sys_id, sys_data in systems_with_full_structure.items():
        for edge in sys_data["internalEdges"]:
            from_comp = sanitize_id(edge.get("from", ""))
            to_comp = sanitize_id(edge.get("to", ""))
            
            if from_comp and to_comp:
                conn_key = f"{sys_id}_{from_comp}->{sys_id}_{to_comp}"
                if conn_key not in connections_added:
                    lines.append(f"    {sys_id}_{from_comp} --> {sys_id}_{to_comp}")
                    connections_added.add(conn_key)
    
    # Add subcomponent-to-component connections (subcomponents connect to parent)
    lines.append("")
    lines.append("    %% Subcomponent-to-Component Connections")
    
    for sys_id, sys_data in systems_with_full_structure.items():
        for comp_data in sys_data["components"]:
            comp = comp_data["component"]
            comp_id = sanitize_id(comp.get("id", ""))
            subcomponents = comp_data["subcomponents"]
            
            for subcomp in subcomponents:
                subcomp_id = sanitize_id(subcomp["id"])
                conn_key = f"{sys_id}_{comp_id}_{subcomp_id}->{sys_id}_{comp_id}"
                if conn_key not in connections_added:
                    lines.append(f"    {sys_id}_{comp_id}_{subcomp_id} --> {sys_id}_{comp_id}")
                    connections_added.add(conn_key)
    
    # Add system-to-system connections
    lines.append("")
    lines.append("    %% System-to-System Integration Connections")
    
    sys_conn_added = set()
    for sys_id, sys_data in systems_with_full_structure.items():
        for port in sys_data["ports"]:
            connects_to = port.get("connectsToSystem", "")
            if connects_to:
                target_id = sanitize_id(connects_to)
                if target_id in systems_with_full_structure:
                    conn_key = f"{sys_id}->{target_id}"
                    reverse_key = f"{target_id}->{sys_id}"
                    
                    if conn_key not in sys_conn_added and reverse_key not in sys_conn_added:
                        if port.get("direction") == "bidirectional":
                            lines.append(f"    {sys_id} <--> {target_id}")
                        else:
                            lines.append(f"    {sys_id} --> {target_id}")
                        sys_conn_added.add(conn_key)
    
    lines.append("")
    lines.append("    %% Styling")
    
    # Style systems by layer
    for layer_num in sorted(systems_by_layer.keys()):
        systems = systems_by_layer[layer_num]
        if not systems:
            continue
        
        config = layer_configs[layer_num]
        sys_list = ",".join(systems)
        
        lines.append(f"    classDef L{layer_num}Style fill:{config['color']},stroke:{config['stroke']},stroke-width:3px,color:#000")
        lines.append(f"    class {sys_list} L{layer_num}Style")
    
    # Style components
    lines.append("    classDef componentStyle fill:#ffffff,stroke:#333,stroke-width:2px")
    
    # Style subcomponents by kind
    subcomp_kinds = {}
    for sys_id, sys_data in systems_with_full_structure.items():
        for comp_data in sys_data["components"]:
            comp_id = sanitize_id(comp_data["component"].get("id", ""))
            for subcomp in comp_data["subcomponents"]:
                kind = subcomp.get("kind", "subcomponent")
                if kind not in subcomp_kinds:
                    subcomp_kinds[kind] = []
                subcomp_kinds[kind].append(f"{sys_id}_{comp_id}_{sanitize_id(subcomp['id'])}")
    
    kind_colors = {
        "index.level": "#e3f2fd",
        "schema.field": "#f3e5f5",
        "pipeline.stage": "#e8f5e9",
        "physics.force": "#fff3e0",
        "orchestration.role": "#fce4ec",
        "storage.tier": "#e0f2f1"
    }
    
    for kind, comp_ids in subcomp_kinds.items():
        color = kind_colors.get(kind, "#f5f5f5")
        if comp_ids:
            comp_list = ",".join(comp_ids)
            kind_style = kind.replace(".", "_")
            lines.append(f"    classDef {kind_style}Style fill:{color},stroke:#999,stroke-width:1px")
            lines.append(f"    class {comp_list} {kind_style}Style")
    
    lines.append("")
    lines.append("```")
    
    return "\n".join(lines), total_subcomponents

def get_short_name(full_name: str) -> str:
    """Get short name from full name."""
    if " - " in full_name:
        return full_name.split(" - ")[0]
    words = full_name.split()
    if words and words[0].isupper() and len(words[0]) <= 5:
        return words[0]
    return words[0] if words else full_name[:20]

def main():
    """Generate complete branched Atlas."""
    print("=" * 80)
    print("AIM-OS Complete Branched Atlas Generator")
    print("Layers -> Systems -> Components -> Subcomponents")
    print("Created by: Sonnet")
    print("=" * 80)
    print()
    
    atlas = load_atlas()
    mermaid_diagram, total_subcomponents = generate_complete_branched_mermaid(atlas)
    
    # Save complete branched diagram
    output_path = Path("knowledge_architecture/ATLAS_MERMAID_COMPLETE_BRANCHED.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🌟 AIM-OS Complete Branched System Architecture Atlas\n\n")
        f.write("**Generated by:** Sonnet\n")
        f.write("**Source:** `atlas.index.lucid.json5`\n")
        f.write("**Date:** 2025-01-27\n\n")
        f.write("## Overview\n\n")
        f.write("This **complete branched** diagram shows the **FULL hierarchical structure** of AIM-OS ")
        f.write("with **ALL layers, systems, components, AND subcomponents** in a deeply nested tree structure.\n\n")
        f.write("### Complete Hierarchical Structure\n\n")
        f.write("1. **Layers** → 6 hierarchical layers\n")
        f.write("2. **Systems** → 13+ systems within layers\n")
        f.write("3. **Components** → 100+ components within systems\n")
        f.write("4. **Subcomponents** → 40+ subcomponents within components\n")
        f.write("5. **Complete Branches** → Full relationship trees\n\n")
        f.write("### Statistics\n\n")
        f.write(f"- **Total Systems:** {atlas['totalSystems']}\n")
        f.write(f"- **Total Components:** {atlas['totalNodes']}\n")
        f.write(f"- **Total Subcomponents:** {total_subcomponents}\n")
        f.write(f"- **Total Integration Points:** {atlas['totalPorts']}\n")
        f.write(f"- **Total Internal Relationships:** {atlas['totalInternalEdges']}\n")
        f.write(f"- **Total External Relationships:** {atlas['totalExternalEdges']}\n\n")
        f.write("### Subcomponent Examples\n\n")
        f.write("- **HHNI hierarchicalIndex:** 6 levels (System, Section, Paragraph, Sentence, Word, Subword)\n")
        f.write("- **CMC atomManager:** 7 atom fields (Schema, Modality, Content Ref, Embeddings, Tags, HHNI Path, VIF)\n")
        f.write("- **CMC writePipeline:** 7 pipeline stages (Ingest, Atomize, Enrich, Index, Gate, Persist, Snapshot)\n")
        f.write("- **CMC readPipeline:** 5 pipeline stages (Query, HHNI Lookup, DVNS Optimize, Deduplicate, Budget Fit)\n")
        f.write("- **HHNI dvnsPhysicsEngine:** 4 physics forces (Gravity, Repulsion, Elastic, Damping)\n")
        f.write("- **APOE roleDispatcher:** 8 orchestration roles (Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness)\n")
        f.write("- **CMC storageManager:** 4 storage tiers (Vector, Object, Metadata, Graph)\n\n")
        f.write("---\n\n")
        f.write(mermaid_diagram)
        f.write("\n\n")
        f.write("## Complete Branch Structure\n\n")
        f.write("### Layer → System → Component → Subcomponent Hierarchy\n\n")
        f.write("Each system shows:\n")
        f.write("- **Components** as subgraphs within the system\n")
        f.write("- **Subcomponents** as nodes within component subgraphs\n")
        f.write("- **Component relationships** showing data flow\n")
        f.write("- **Subcomponent-to-component** connections showing internal structure\n")
        f.write("- **System integrations** showing external connections\n\n")
        f.write("### Branch Examples\n\n")
        f.write("**CMC Write Pipeline Branch:**\n")
        f.write("```\n")
        f.write("writePipeline\n")
        f.write("├── stage_ingest\n")
        f.write("├── stage_atomize\n")
        f.write("├── stage_enrich\n")
        f.write("├── stage_index\n")
        f.write("├── stage_gate\n")
        f.write("├── stage_persist\n")
        f.write("└── stage_snapshot\n")
        f.write("```\n\n")
        f.write("**HHNI Hierarchical Index Branch:**\n")
        f.write("```\n")
        f.write("hierarchicalIndex\n")
        f.write("├── level_system\n")
        f.write("├── level_section\n")
        f.write("├── level_paragraph\n")
        f.write("├── level_sentence\n")
        f.write("├── level_word\n")
        f.write("└── level_subword\n")
        f.write("```\n\n")
    
    print(f"Complete branched Atlas diagram saved to: {output_path}")
    print()
    print("=" * 80)
    print("Complete Branched Atlas Generated Successfully!")
    print("=" * 80)
    print()
    print(f"Total Components: {atlas['totalNodes']}")
    print(f"Total Subcomponents: {total_subcomponents}")
    print(f"Total Nodes (Components + Subcomponents): {atlas['totalNodes'] + total_subcomponents}")
    print(f"Total Internal Relationships: {atlas['totalInternalEdges']}")
    print(f"Total External Relationships: {atlas['totalExternalEdges']}")

if __name__ == "__main__":
    main()

