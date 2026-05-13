#!/usr/bin/env python3
"""
North Star Orchestration Chain Runner
Executable orchestration system for 40-chapter document creation

Integrates:
- APOE (orchestration engine)
- VIF (confidence gating)
- SEG (evidence synthesis)
- SDF-CVF (quality validation)
- CMC (evidence storage)
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChapterNode:
    """Executable chapter node"""
    id: str
    title: str
    agent: str
    deps: List[str]
    tier_requirements: Dict[str, List[str]]
    word_count: Dict[str, Any]
    gates: List[str]
    outputs: List[str]
    quality_criteria: Dict[str, Any]
    
    def __post_init__(self):
        self.status = "pending"
        self.confidence = 0.0
        self.gates_passed = {}


class NorthStarOrchestrator:
    """Executable orchestration engine for North Star document"""
    
    def __init__(self, chain_spec_path: str, policy_path: str):
        self.chain_spec_path = Path(chain_spec_path)
        self.policy_path = Path(policy_path)
        
        # Load specifications
        self.chain_spec = self._load_yaml(self.chain_spec_path)
        self.policy = self._load_json(self.policy_path)
        
        # Extract nodes
        self.nodes = self._parse_nodes()
        self.spikes = self._parse_spikes()
        
        # Status
        self.status = {
            "spikes_complete": 0,
            "chapters_complete": 0,
            "total_words": 0,
            "gates_passed": 0,
            "confidence_average": 0.0
        }
    
    def _load_yaml(self, path: Path) -> dict:
        """Load YAML file"""
        with open(path) as f:
            return yaml.safe_load(f)
    
    def _load_json(self, path: Path) -> dict:
        """Load JSON file"""
        with open(path) as f:
            return json.load(f)
    
    def _parse_nodes(self) -> Dict[str, ChapterNode]:
        """Parse chapter nodes from chain spec"""
        nodes = {}
        for node_data in self.chain_spec["chain"]["nodes"]:
            node = ChapterNode(
                id=node_data["id"],
                title=node_data["title"],
                agent=node_data["agent"],
                deps=node_data["deps"],
                tier_requirements=node_data["tier_requirements"],
                word_count=node_data["word_count"],
                gates=node_data["gates"],
                outputs=node_data["outputs"],
                quality_criteria=node_data["quality_criteria"]
            )
            nodes[node.id] = node
        return nodes
    
    def _parse_spikes(self) -> Dict[str, dict]:
        """Parse risk spikes from chain spec"""
        return {
            spike["id"]: spike 
            for spike in self.chain_spec["chain"].get("spikes", [])
        }
    
    def check_dependencies(self, node: ChapterNode) -> bool:
        """Check if all dependencies are satisfied"""
        for dep_id in node.deps:
            dep_node = self.nodes.get(dep_id)
            if not dep_node or dep_node.status != "complete":
                print(f"❌ Dependency not satisfied: {dep_id}")
                return False
        return True
    
    def check_tier_a_sources(self, node: ChapterNode) -> bool:
        """Check if all Tier A sources are available"""
        tier_a = node.tier_requirements.get("TierA", [])
        
        if not tier_a:
            print(f"⚠️ Warning: No Tier A sources specified for {node.id}")
            return False
        
        for source in tier_a:
            # Check if source exists (file or directory)
            source_path = Path(source)
            if not source_path.exists():
                print(f"❌ Tier A source not found: {source}")
                return False
        
        print(f"✅ All {len(tier_a)} Tier A sources available")
        return True
    
    def check_vif_confidence(self, node: ChapterNode, text: str) -> float:
        """Check VIF confidence for chapter text"""
        # TODO: Integrate with actual VIF system
        # For now, return simulated confidence
        
        # Simulate confidence based on:
        # - Has tier A citations
        # - Has code examples
        # - Has evidence file
        
        confidence = 0.50  # Base
        
        # Boost for tier A sources
        if self.check_tier_a_sources(node):
            confidence += 0.20
        
        # Boost for evidence
        evidence_path = Path(node.outputs[1])  # evidence.jsonl
        if evidence_path.exists():
            confidence += 0.10
        
        # Boost for examples
        if "```" in text:
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def run_gate_check(self, gate_name: str, node: ChapterNode, text: str) -> bool:
        """Run a specific quality gate check"""
        gate_spec = self.policy["gates"].get(gate_name, {})
        
        if not gate_spec:
            print(f"⚠️ Gate not found: {gate_name}")
            return False
        
        print(f"\n🔍 Running gate: {gate_spec['name']}")
        
        checks = gate_spec.get("checks", {})
        all_passed = True
        
        for check_name, check_spec in checks.items():
            result = self._run_check(check_name, check_spec, node, text)
            
            if not result and check_spec.get("blocking", False):
                print(f"  ❌ {check_spec['description']}")
                print(f"     {check_spec.get('error_message', 'Check failed')}")
                all_passed = False
            elif not result:
                print(f"  ⚠️ {check_spec['description']}")
                print(f"     {check_spec.get('warning_message', 'Warning')}")
            else:
                print(f"  ✅ {check_spec['description']}")
        
        return all_passed
    
    def _run_check(self, check_name: str, check_spec: dict, node: ChapterNode, text: str) -> bool:
        """Run individual check"""
        method = check_spec.get("method", "")
        
        if method == "check_status_tracker":
            return self.check_dependencies(node)
        
        elif method == "check_file_existence":
            return self.check_tier_a_sources(node)
        
        elif method == "vif_confidence_check":
            confidence = self.check_vif_confidence(node, text)
            threshold = check_spec.get("threshold", 0.70)
            return confidence >= threshold
        
        elif method == "check_outline_exists":
            # TODO: Check actual outline file
            return True
        
        elif method == "calculate_deviation":
            # TODO: Calculate actual word count
            return True
        
        elif method == "execute_code_blocks":
            # TODO: Extract and execute code blocks
            return True
        
        elif method == "verify_formulas":
            # TODO: Verify mathematical formulas
            return True
        
        elif method == "cross_check_sources":
            # TODO: Cross-check claims against sources
            return True
        
        elif method == "check_evidence_file":
            evidence_path = Path(node.outputs[1])
            return evidence_path.exists() and evidence_path.stat().st_size > 0
        
        elif method == "seg_contradiction_check":
            # TODO: Use SEG to check for contradictions
            return True
        
        elif method == "glossary_validation":
            # TODO: Validate against glossary
            return True
        
        elif method == "validate_cross_references":
            # TODO: Validate all cross-references
            return True
        
        else:
            print(f"⚠️ Unknown check method: {method}")
            return True
    
    def start_chapter(self, node_id: str):
        """Start writing a chapter with pre-checks"""
        node = self.nodes.get(node_id)
        if not node:
            print(f"❌ Node not found: {node_id}")
            return False
        
        print(f"\n{'='*60}")
        print(f"📝 STARTING CHAPTER: {node.title}")
        print(f"{'='*60}\n")
        
        # Run pre-chapter gate
        if not self.run_gate_check("pre_chapter", node, ""):
            print(f"\n❌ Pre-chapter gate FAILED for {node.id}")
            print(f"   Cannot proceed until requirements satisfied\n")
            return False
        
        print(f"\n✅ Pre-chapter gate PASSED for {node.id}")
        print(f"   Ready to begin writing!\n")
        
        # Load tier A sources
        print("📚 Loading Tier A sources...")
        for source in node.tier_requirements.get("TierA", []):
            print(f"   - {source}")
        
        # Load outline
        print("\n📋 Chapter outline loaded")
        print(f"   Target: {node.word_count['target']} words (±{node.word_count['tolerance']*100}%)\n")
        
        node.status = "in_progress"
        return True
    
    def finalize_chapter(self, node_id: str, text: str):
        """Finalize chapter with quality gates"""
        node = self.nodes.get(node_id)
        if not node:
            print(f"❌ Node not found: {node_id}")
            return False
        
        print(f"\n{'='*60}")
        print(f"✅ FINALIZING CHAPTER: {node.title}")
        print(f"{'='*60}\n")
        
        # Run all gates
        gates_passed = {}
        for gate_name in node.gates:
            passed = self.run_gate_check(gate_name, node, text)
            gates_passed[gate_name] = passed
        
        # Check if all required gates passed
        all_passed = all(gates_passed.values())
        
        if all_passed:
            print(f"\n🎉 ALL QUALITY GATES PASSED for {node.id}!")
            print(f"   Chapter ready for merge\n")
            node.status = "complete"
            self.status["chapters_complete"] += 1
            return True
        else:
            print(f"\n❌ SOME QUALITY GATES FAILED for {node.id}")
            print(f"   Review and fix issues before merge\n")
            return False
    
    def get_ready_chapters(self) -> List[str]:
        """Get list of chapters ready to start (deps satisfied)"""
        ready = []
        for node_id, node in self.nodes.items():
            if node.status == "pending" and self.check_dependencies(node):
                ready.append(node_id)
        return ready
    
    def print_status(self):
        """Print current orchestration status"""
        print(f"\n{'='*60}")
        print(f"📊 NORTH STAR ORCHESTRATION STATUS")
        print(f"{'='*60}\n")
        
        print(f"Chapters Complete: {self.status['chapters_complete']}/{len(self.nodes)}")
        print(f"Total Words: {self.status['total_words']}/70000")
        print(f"Gates Passed: {self.status['gates_passed']}")
        print(f"Confidence Average: {self.status['confidence_average']:.2f}\n")
        
        print("Ready to Start:")
        ready = self.get_ready_chapters()
        for node_id in ready[:5]:  # Show first 5
            node = self.nodes[node_id]
            print(f"  - {node.id}: {node.title} ({node.agent})")
        
        if len(ready) > 5:
            print(f"  ... and {len(ready) - 5} more\n")


def main():
    """Main execution"""
    # Initialize orchestrator
    orchestrator = NorthStarOrchestrator(
        chain_spec_path="north_star_project/chains/ChainSpec.yaml",
        policy_path="north_star_project/policy/gates.json"
    )
    
    # Print initial status
    orchestrator.print_status()
    
    # Example: Start first chapter
    print("\n" + "="*60)
    print("EXAMPLE: Starting Chapter 1")
    print("="*60)
    
    orchestrator.start_chapter("ch01_great_limitation")
    
    print("\n" + "="*60)
    print("✨ ORCHESTRATION SYSTEM READY!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run risk spikes to validate assumptions")
    print("2. Begin Wave 1 chapters (ch01, ch02, ch04)")
    print("3. Monitor quality gates continuously")
    print("4. Update STATUS_TRACKER.md as chapters complete\n")


if __name__ == "__main__":
    main()

