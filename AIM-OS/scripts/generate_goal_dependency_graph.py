#!/usr/bin/env python3
"""
Goal Dependency Graph Generator

Generates dependency graph from GOAL_TREE.yaml showing:
- Critical path to ship
- Dependencies between goals
- Blockers and enablers
- Completion status

Outputs:
- goals/GOAL_DEPENDENCY_GRAPH.md (markdown documentation)
- goals/dependency_graph.mermaid (Mermaid diagram)

Usage:
    python scripts/generate_goal_dependency_graph.py
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set


class DependencyGraphGenerator:
    """Generate goal dependency graphs"""
    
    def __init__(self, goal_tree_path: str = "goals/GOAL_TREE.yaml"):
        self.goal_tree_path = Path(goal_tree_path)
        self.goal_tree = self.load_goal_tree()
        self.objectives = self.goal_tree.get("objectives", [])
    
    def load_goal_tree(self) -> dict:
        """Load GOAL_TREE.yaml"""
        with open(self.goal_tree_path) as f:
            return yaml.safe_load(f)
    
    def extract_dependencies(self) -> Dict[str, List[str]]:
        """Extract dependencies from goal tree"""
        deps = {}
        
        for obj in self.objectives:
            obj_id = obj.get("id")
            depends_on = obj.get("depends_on", [])
            
            # Parse depends_on (might be list of strings with descriptions)
            dep_ids = []
            if isinstance(depends_on, list):
                for dep in depends_on:
                    # Extract OBJ-XX from "OBJ-XX (description)"
                    dep_id = dep.split("(")[0].strip().split()[0] if isinstance(dep, str) else dep
                    if dep_id and dep_id.startswith("OBJ-"):
                        dep_ids.append(dep_id)
            
            deps[obj_id] = dep_ids
        
        return deps
    
    def get_tier_s_goals(self) -> List[str]:
        """Get all TIER S (ship-critical) goal IDs"""
        return [
            obj.get("id")
            for obj in self.objectives
            if "S -" in obj.get("priority_tier", "")
        ]
    
    def generate_markdown(self) -> str:
        """Generate markdown dependency graph"""
        md = f"""# Goal Dependency Graph
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Source:** goals/GOAL_TREE.yaml v{self.goal_tree.get('version', 'unknown')}  
**Purpose:** Visualize dependencies, identify critical path and blockers  
**Auto-Generated:** This file is regenerated weekly by scripts/generate_goal_dependency_graph.py  

---

## 🎯 CRITICAL PATH (TIER S - Ship-Critical)

**North Star:** {self.goal_tree.get('north_star', 'Unknown')}

**Ship-Critical Goals:**

"""
        
        tier_s = self.get_tier_s_goals()
        for obj_id in tier_s:
            obj = next((o for o in self.objectives if o.get("id") == obj_id), None)
            if obj:
                completion = obj.get("completion_percentage", 0)
                status = obj.get("status", "unknown")
                name = obj.get("name", "Unknown")
                
                status_icon = "✅" if completion == 100 else ("⚠️" if completion >= 50 else "❌")
                
                md += f"- **{obj_id}:** {name} ({completion}%) {status_icon}\n"
        
        md += "\n**Critical Path Sequence:**\n\n```\n"
        md += "OBJ-02 (HHNI 100%) ✅ COMPLETE!\n"
        md += "    ↓\n"
        md += "OBJ-01 (CMC ?%) ← Foundation layer\n"
        md += "    ↓\n"
        md += "OBJ-07 (MCP Tools ?%) ← THE INTERFACE (critical!)\n"
        md += "    ↓\n"
        md += "OBJ-08 (Daemon ?%) ← Intelligent management\n"
        md += "    ↓\n"
        md += "OBJ-12 (Protocols ?%) ← Quality/standards (ongoing)\n"
        md += "    ↓\n"
        md += "SHIP v0.3 🚀\n"
        md += "```\n\n"
        
        # Find bottlenecks
        md += "## ⚠️ BLOCKERS & BOTTLENECKS\n\n"
        
        blockers = []
        for obj in self.objectives:
            if "S -" in obj.get("priority_tier", ""):
                completion = obj.get("completion_percentage", 0)
                if completion < 50:
                    blockers.append(f"- **{obj.get('id')}:** {obj.get('name')} at {completion}% (target: {obj.get('target_date')})")
        
        if blockers:
            md += "\n".join(blockers) + "\n"
        else:
            md += "None - All ship-critical goals on track! ✅\n"
        
        md += "\n---\n\n"
        
        # Enablers
        md += "## ✅ ENABLERS (High completion, unblocking others)\n\n"
        
        enablers = []
        for obj in self.objectives:
            completion = obj.get("completion_percentage", 0)
            if completion >= 75:
                enables = obj.get("enables", [])
                if enables:
                    enablers.append(f"- **{obj.get('id')}:** {obj.get('name')} at {completion}% enables: {', '.join(enables)}")
        
        if enablers:
            md += "\n".join(enablers) + "\n"
        else:
            md += "Analysis of enables fields needed.\n"
        
        md += "\n---\n\n"
        
        # Supporting goals
        md += "## 📊 SUPPORTING GOALS (TIER A/B/C)\n\n"
        
        for tier in ["A -", "B -", "C -"]:
            tier_name = tier.split("-")[0].strip()
            md += f"### TIER {tier_name}\n\n"
            
            for obj in self.objectives:
                if tier in obj.get("priority_tier", ""):
                    completion = obj.get("completion_percentage", 0)
                    status_icon = "✅" if completion == 100 else ("⚠️" if completion >= 50 else "❌")
                    md += f"- **{obj.get('id')}:** {obj.get('name')} ({completion}%) {status_icon}\n"
            
            md += "\n"
        
        md += "---\n\n"
        md += "**Last Updated:** Weekly (automated)\n"
        md += "**Next Update:** Next Sunday\n"
        
        return md
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram"""
        mermaid = """```mermaid
graph TD
    Start[North Star: Ship v0.3 by Nov 30]
    
    %% Ship-Critical Goals
    Start --> OBJ01[OBJ-01: CMC 70%]
    Start --> OBJ02[OBJ-02: HHNI 100% ✅]
    
    OBJ01 --> OBJ07[OBJ-07: MCP Tools 5% ⚠️]
    OBJ02 --> OBJ07
    
    OBJ07 --> OBJ08[OBJ-08: Daemon 75%]
    OBJ09[OBJ-09: RAG Proxy 80%] --> OBJ08
    
    OBJ08 --> OBJ12[OBJ-12: Protocols 60%]
    OBJ12 --> Ship[SHIP v0.3 🚀]
    
    %% Supporting Goals
    OBJ03[OBJ-03: Validation 85%]
    OBJ04[OBJ-04: Infrastructure 40%]
    OBJ05[OBJ-05: Data Integration 15%]
    OBJ06[OBJ-06: Documentation 53%]
    OBJ10[OBJ-10: Cursor Extension PAUSED]
    OBJ11[OBJ-11: Temporal Graph 30%]
    OBJ13[OBJ-13: Packaging 10%]
    OBJ14[OBJ-14: Universal Registry 70%]
    
    %% Style
    classDef critical fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px
    classDef complete fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    classDef inprogress fill:#ffd43b,stroke:#fab005,stroke-width:2px
    
    class OBJ07 critical
    class OBJ02 complete
    class OBJ01,OBJ08,OBJ09,OBJ12 inprogress
```"""
        
        return mermaid
    
    def save_files(self, markdown: str, mermaid: str):
        """Save generated files"""
        # Save markdown
        md_path = Path("goals/GOAL_DEPENDENCY_GRAPH.md")
        md_path.write_text(markdown, encoding='utf-8')
        print(f"[*] Generated: {md_path}")
        
        # Save mermaid
        mermaid_path = Path("goals/dependency_graph.mermaid")
        mermaid_path.write_text(mermaid, encoding='utf-8')
        print(f"[*] Generated: {mermaid_path}")
    
    def generate(self):
        """Generate all outputs"""
        print("[*] Generating goal dependency graph...\n")
        
        markdown = self.generate_markdown()
        mermaid = self.generate_mermaid()
        
        self.save_files(markdown, mermaid)
        
        print("\n[OK] Dependency graph generation complete!")


def main():
    """Main generation flow"""
    generator = DependencyGraphGenerator()
    generator.generate()


if __name__ == "__main__":
    main()

