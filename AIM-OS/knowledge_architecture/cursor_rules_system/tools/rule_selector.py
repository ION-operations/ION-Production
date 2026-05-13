#!/usr/bin/env python3
"""
Dynamic Cursor Rules Selector

This tool automatically selects and combines appropriate cursor rules
based on the current task context and requirements.

Usage:
    python rule_selector.py --task "audit system" --output .cursorrules
    python rule_selector.py --context development --protocols ldp,quality
"""

import argparse
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

class ContextDetector:
    """Detects task context from task description or keywords."""
    
    def __init__(self):
        self.context_patterns = {
            'auditing': [
                'audit', 'review', 'analyze', 'discover', 'catalog',
                'system analysis', 'comprehensive review', 'inventory'
            ],
            'development': [
                'develop', 'code', 'implement', 'build', 'create',
                'programming', 'software development', 'feature'
            ],
            'documentation': [
                'document', 'write', 'create docs', 'documentation',
                'guide', 'manual', 'tutorial', 'explain'
            ],
            'testing': [
                'test', 'testing', 'validate', 'verify', 'check',
                'unit test', 'integration test', 'quality assurance'
            ],
            'deployment': [
                'deploy', 'deployment', 'production', 'release',
                'publish', 'ship', 'go live'
            ],
            'maintenance': [
                'maintain', 'maintenance', 'fix', 'bug', 'update',
                'refactor', 'optimize', 'improve'
            ]
        }
    
    def detect(self, task_description: str) -> str:
        """Detect context from task description."""
        task_lower = task_description.lower()
        
        # Score each context based on keyword matches
        context_scores = {}
        for context, keywords in self.context_patterns.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                context_scores[context] = score
        
        # Return context with highest score, or 'general' if no matches
        if context_scores:
            return max(context_scores, key=context_scores.get)
        return 'general'

class ProtocolSelector:
    """Selects appropriate protocols based on task requirements."""
    
    def __init__(self):
        self.protocol_mappings = {
            'ldp': {
                'keywords': ['ldp', 'lucid development protocol', 'system map', 'atlas'],
                'file': 'protocols/ldp_protocols.md'
            },
            'quality': {
                'keywords': ['quality', 'test', 'validation', 'assurance'],
                'file': 'protocols/quality_protocols.md'
            },
            'timeline': {
                'keywords': ['timeline', 'context', 'tracking', 'history'],
                'file': 'protocols/timeline_protocols.md'
            },
            'memory': {
                'keywords': ['memory', 'storage', 'retrieval', 'persistence'],
                'file': 'protocols/memory_protocols.md'
            }
        }
    
    def select(self, task_description: str, explicit_protocols: List[str] = None) -> List[str]:
        """Select protocols based on task description and explicit requirements."""
        selected_protocols = []
        
        # Add explicitly requested protocols
        if explicit_protocols:
            selected_protocols.extend(explicit_protocols)
        
        # Detect protocols from task description
        task_lower = task_description.lower()
        for protocol, config in self.protocol_mappings.items():
            if any(keyword in task_lower for keyword in config['keywords']):
                if protocol not in selected_protocols:
                    selected_protocols.append(protocol)
        
        return selected_protocols

class RuleCombiner:
    """Combines multiple rule files into a single cursor rules file."""
    
    def __init__(self, rules_directory: str = "knowledge_architecture/cursor_rules_system"):
        self.rules_directory = Path(rules_directory)
    
    def load_rule_file(self, rule_path: str) -> str:
        """Load a rule file and return its content."""
        full_path = self.rules_directory / rule_path
        if not full_path.exists():
            raise FileNotFoundError(f"Rule file not found: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def combine_rules(self, rule_files: List[str]) -> str:
        """Combine multiple rule files into a single rules file."""
        combined_rules = []
        
        # Add header
        combined_rules.append("# Dynamic Cursor Rules - Generated")
        combined_rules.append(f"# Generated: {self._get_timestamp()}")
        combined_rules.append("")
        
        # Add each rule file
        for rule_file in rule_files:
            try:
                content = self.load_rule_file(rule_file)
                combined_rules.append(f"# === {rule_file} ===")
                combined_rules.append(content)
                combined_rules.append("")
                combined_rules.append("---")
                combined_rules.append("")
            except FileNotFoundError as e:
                print(f"Warning: {e}")
                continue
        
        return "\n".join(combined_rules)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class RuleSelector:
    """Main rule selector that orchestrates the selection and combination process."""
    
    def __init__(self, rules_directory: str = "knowledge_architecture/cursor_rules_system"):
        self.rules_directory = Path(rules_directory)
        self.context_detector = ContextDetector()
        self.protocol_selector = ProtocolSelector()
        self.rule_combiner = RuleCombiner(rules_directory)
    
    def select_rules(self, 
                    task_description: str,
                    context: Optional[str] = None,
                    protocols: Optional[List[str]] = None,
                    include_base: bool = True) -> str:
        """Select and combine appropriate rules for the given task."""
        
        # Detect context if not provided
        if not context:
            context = self.context_detector.detect(task_description)
        
        # Select protocols if not provided
        if not protocols:
            protocols = self.protocol_selector.select(task_description)
        
        # Build list of rule files to include
        rule_files = []
        
        # Always include base rules (contains MCP integration as core rule)
        if include_base:
            rule_files.append("core/base_rules.md")
        
        # Add context-specific rules
        context_file = f"contexts/{context}_rules.md"
        if (self.rules_directory / context_file).exists():
            rule_files.append(context_file)
        
        # Add protocol rules
        for protocol in protocols:
            protocol_file = f"protocols/{protocol}_protocols.md"
            if (self.rules_directory / protocol_file).exists():
                rule_files.append(protocol_file)
        
        # MCP integration is now part of base rules, so no need to add separately
        # This ensures MCP tools are ALWAYS available regardless of context
        
        # Combine rules
        return self.rule_combiner.combine_rules(rule_files)
    
    def save_rules(self, rules_content: str, output_path: str = ".cursorrules"):
        """Save combined rules to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rules_content)
        print(f"Rules saved to: {output_path}")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Dynamic Cursor Rules Selector")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--context", help="Explicit context (auditing, development, etc.)")
    parser.add_argument("--protocols", help="Comma-separated list of protocols")
    parser.add_argument("--output", default=".cursorrules", help="Output file path")
    parser.add_argument("--rules-dir", default="knowledge_architecture/cursor_rules_system", 
                       help="Rules directory path")
    parser.add_argument("--no-base", action="store_true", help="Exclude base rules")
    
    args = parser.parse_args()
    
    # Parse protocols
    protocols = None
    if args.protocols:
        protocols = [p.strip() for p in args.protocols.split(',')]
    
    # Create rule selector
    selector = RuleSelector(args.rules_dir)
    
    # Select rules
    try:
        rules_content = selector.select_rules(
            task_description=args.task,
            context=args.context,
            protocols=protocols,
            include_base=not args.no_base
        )
        
        # Save rules
        selector.save_rules(rules_content, args.output)
        
        print("✅ Rules selection completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
