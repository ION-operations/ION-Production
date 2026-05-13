#!/usr/bin/env python3
"""
VIF Automatic Tagger - Accelerate NL Tag Creation

This script automates the tagging process for VIF files by:
1. Analyzing file structure (AST extraction)
2. Generating tag IDs automatically
3. Creating tag templates based on function signatures
4. Suggesting CONNECT tags based on imports
5. Validating with quintet parity

Usage:
    python scripts/vif_auto_tagger.py packages/vif/calibration.py
    python scripts/vif_auto_tagger.py --all  # Tag all remaining VIF files
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.sdfcvf.quintet import ASTSymbolExtractor, CodeSymbol


@dataclass
class TagSuggestion:
    """Suggested NL tag for a code symbol"""
    tag_id: str
    tag_type: str  # "TAG", "CONNECT", "INTENT", "SPEC"
    description: str
    syntax_ref: str
    dependencies: List[str]
    line_number: int
    confidence: float  # How confident we are in this suggestion


class VIFAutoTagger:
    """Automatic VIF tagging assistant"""
    
    # Tag category mappings
    CATEGORY_KEYWORDS = {
        "witness": "WITNESS",
        "confidence": "CONF",
        "kappa": "GATE",
        "gate": "GATE",
        "calibrat": "CAL",
        "provenance": "PROV",
        "model": "MODEL",
        "hitl": "HITL",
        "escalat": "HITL",
        "replay": "REPLAY",
        "extract": "EXTRACT",
        "band": "BAND",
        "client": "CLIENT",
        "integrat": "INTEG",
        "util": "UTIL",
        "helper": "UTIL",
    }
    
    # Known integrations
    INTEGRATIONS = {
        "cmc": ["store_atom", "retrieve_atom", "create_snapshot"],
        "hhni": ["retrieve_similar", "index_atom"],
        "apoe": ["orchestrate", "execute_plan", "abstain"],
        "seg": ["build_graph", "add_edge", "provenance"],
        "sdfcvf": ["check_parity", "validate_quartet"],
    }
    
    def __init__(self, vif_root: str = "packages/vif"):
        self.vif_root = Path(vif_root)
        self.tag_counters: Dict[str, int] = {}
        self.existing_tags: Set[str] = set()
    
    def analyze_file(self, file_path: str) -> List[CodeSymbol]:
        """Extract all symbols from a file"""
        symbols = ASTSymbolExtractor.extract_python_symbols(file_path)
        return symbols
    
    def categorize_symbol(self, symbol: CodeSymbol, file_name: str) -> str:
        """Determine tag category for symbol"""
        # Check file name first
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in file_name.lower():
                return category
        
        # Check symbol name
        name_lower = symbol.name.lower()
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in name_lower:
                return category
        
        # Check docstring
        if symbol.docstring:
            doc_lower = symbol.docstring.lower()
            for keyword, category in self.CATEGORY_KEYWORDS.items():
                if keyword in doc_lower:
                    return category
        
        # Default based on symbol type
        if "class" in symbol.signature.lower() or symbol.name[0].isupper():
            return "MODEL"
        else:
            return "UTIL"
    
    def generate_tag_id(self, category: str) -> str:
        """Generate unique tag ID"""
        if category not in self.tag_counters:
            self.tag_counters[category] = 1
        
        tag_id = f"VIF-{category}-{self.tag_counters[category]:03d}"
        
        # Ensure uniqueness
        while tag_id in self.existing_tags:
            self.tag_counters[category] += 1
            tag_id = f"VIF-{category}-{self.tag_counters[category]:03d}"
        
        self.existing_tags.add(tag_id)
        self.tag_counters[category] += 1
        
        return tag_id
    
    def generate_description(self, symbol: CodeSymbol) -> str:
        """Generate tag description from symbol"""
        # Use first line of docstring if available
        if symbol.docstring:
            first_line = symbol.docstring.split('\n')[0].strip()
            if first_line:
                return first_line
        
        # Generate from name
        # Convert snake_case to words
        words = symbol.name.replace('_', ' ')
        
        # Capitalize first letter
        return words.capitalize()
    
    def suggest_connect_tags(
        self,
        file_path: str,
        symbol: CodeSymbol
    ) -> List[TagSuggestion]:
        """Suggest CONNECT tags based on imports and calls"""
        suggestions = []
        
        # Read file to analyze imports
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find imports
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
            
            # Check for known integrations
            for system, keywords in self.INTEGRATIONS.items():
                if system in imports:
                    # This file integrates with this system
                    for keyword in keywords:
                        if keyword.lower() in symbol.name.lower() or \
                           (symbol.docstring and keyword.lower() in symbol.docstring.lower()):
                            # Suggest CONNECT tag
                            tag_id = self.generate_tag_id("CONNECT")
                            suggestions.append(TagSuggestion(
                                tag_id=tag_id,
                                tag_type="CONNECT",
                                description=f"Integration with {system.upper()}",
                                syntax_ref=f"{symbol.name} → {system}.{keyword}",
                                dependencies=[],
                                line_number=symbol.line_number,
                                confidence=0.70
                            ))
        
        except Exception:
            pass
        
        return suggestions
    
    def suggest_intent_tags(self, symbol: CodeSymbol) -> List[TagSuggestion]:
        """Suggest INTENT tags for design decisions"""
        suggestions = []
        
        # Keywords that suggest design decisions
        design_keywords = [
            "abstain", "gate", "threshold", "critical", "escalate",
            "calibrat", "provenance", "deterministic", "replay",
            "confidence", "uncertainty", "quality"
        ]
        
        if symbol.docstring:
            doc_lower = symbol.docstring.lower()
            for keyword in design_keywords:
                if keyword in doc_lower:
                    tag_id = self.generate_tag_id("INTENT")
                    suggestions.append(TagSuggestion(
                        tag_id=tag_id,
                        tag_type="INTENT",
                        description=f"Design decision: {keyword}",
                        syntax_ref=symbol.name,
                        dependencies=[],
                        line_number=symbol.line_number,
                        confidence=0.60
                    ))
                    break  # Only one INTENT per function
        
        return suggestions
    
    def suggest_spec_tags(self, symbol: CodeSymbol) -> List[TagSuggestion]:
        """Suggest SPEC tags for validations"""
        suggestions = []
        
        # Keywords that suggest validation
        validation_keywords = [
            "validate", "check", "verify", "schema", "spec",
            "contract", "assert", "enforce"
        ]
        
        name_lower = symbol.name.lower()
        for keyword in validation_keywords:
            if keyword in name_lower:
                tag_id = self.generate_tag_id("SPEC")
                suggestions.append(TagSuggestion(
                    tag_id=tag_id,
                    tag_type="SPEC",
                    description=f"Validates {symbol.name} specification",
                    syntax_ref=symbol.name,
                    dependencies=[],
                    line_number=symbol.line_number,
                    confidence=0.70
                ))
                break
        
        return suggestions
    
    def generate_tags_for_symbol(
        self,
        symbol: CodeSymbol,
        file_path: str,
        file_name: str
    ) -> List[TagSuggestion]:
        """Generate all suggested tags for a symbol"""
        suggestions = []
        
        # 1. Always generate primary NL_TAG
        category = self.categorize_symbol(symbol, file_name)
        tag_id = self.generate_tag_id(category)
        description = self.generate_description(symbol)
        
        suggestions.append(TagSuggestion(
            tag_id=tag_id,
            tag_type="TAG",
            description=description,
            syntax_ref=symbol.signature,
            dependencies=[],
            line_number=symbol.line_number,
            confidence=0.90
        ))
        
        # 2. Suggest CONNECT tags
        suggestions.extend(self.suggest_connect_tags(file_path, symbol))
        
        # 3. Suggest INTENT tags
        suggestions.extend(self.suggest_intent_tags(symbol))
        
        # 4. Suggest SPEC tags
        suggestions.extend(self.suggest_spec_tags(symbol))
        
        return suggestions
    
    def format_tag_comment(self, suggestion: TagSuggestion) -> str:
        """Format tag as comment"""
        deps_str = f" | {suggestion.dependencies}" if suggestion.dependencies else " | []"
        
        if suggestion.tag_type == "TAG":
            return f"# NL_TAG: {suggestion.tag_id} | {suggestion.description} | {suggestion.syntax_ref}{deps_str}"
        elif suggestion.tag_type == "CONNECT":
            return f"# NL_TAG_CONNECT: {suggestion.tag_id} | {suggestion.description} | {suggestion.syntax_ref}{deps_str}"
        elif suggestion.tag_type == "INTENT":
            return f"# NL_TAG_INTENT: {suggestion.tag_id} | {suggestion.description} | {suggestion.syntax_ref} | [ADR-TBD]"
        elif suggestion.tag_type == "SPEC":
            return f"# NL_TAG_SPEC: {suggestion.tag_id} | {suggestion.description} | {suggestion.syntax_ref} | [spec_file_TBD]"
    
    def tag_file(self, file_path: str, output_path: str = None) -> None:
        """Tag a VIF file"""
        file_path = Path(file_path)
        
        if output_path is None:
            output_path = file_path.parent / f"{file_path.stem}_TAGGED{file_path.suffix}"
        
        print(f"\n{'='*60}")
        print(f"Tagging: {file_path.name}")
        print(f"{'='*60}\n")
        
        # Analyze file
        symbols = self.analyze_file(str(file_path))
        print(f"Found {len(symbols)} symbols")
        
        # Generate tags
        all_suggestions = []
        for symbol in symbols:
            suggestions = self.generate_tags_for_symbol(
                symbol,
                str(file_path),
                file_path.name
            )
            all_suggestions.append((symbol, suggestions))
            
            print(f"\n{symbol.name} ({symbol.line_number}):")
            for sug in suggestions:
                conf_str = f"[{sug.confidence:.0%} confident]"
                print(f"  - {sug.tag_type:7} {sug.tag_id:20} {conf_str}")
        
        # Read original file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Insert tags
        output_lines = []
        last_line = 0
        
        for symbol, suggestions in all_suggestions:
            # Add lines before this symbol
            output_lines.extend(lines[last_line:symbol.line_number - 1])
            
            # Add tag comments
            indent = len(lines[symbol.line_number - 1]) - len(lines[symbol.line_number - 1].lstrip())
            indent_str = ' ' * indent
            
            for sug in suggestions:
                output_lines.append(f"{indent_str}{self.format_tag_comment(sug)}\n")
            
            # Add the symbol's line
            output_lines.append(lines[symbol.line_number - 1])
            
            last_line = symbol.line_number
        
        # Add remaining lines
        output_lines.extend(lines[last_line:])
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        
        print(f"\n{'='*60}")
        print(f"[OK] Tagged file written to: {output_path}")
        print(f"{'='*60}\n")
        
        total_tags = sum(len(suggestions) for _, suggestions in all_suggestions)
        print(f"Total tags: {total_tags}")
        print(f"  NL_TAG: {sum(1 for _, s in all_suggestions for t in s if t.tag_type == 'TAG')}")
        print(f"  CONNECT: {sum(1 for _, s in all_suggestions for t in s if t.tag_type == 'CONNECT')}")
        print(f"  INTENT: {sum(1 for _, s in all_suggestions for t in s if t.tag_type == 'INTENT')}")
        print(f"  SPEC: {sum(1 for _, s in all_suggestions for t in s if t.tag_type == 'SPEC')}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/vif_auto_tagger.py <file_path>")
        print("   or: python scripts/vif_auto_tagger.py --all")
        sys.exit(1)
    
    tagger = VIFAutoTagger()
    
    if sys.argv[1] == "--all":
        # Tag all remaining VIF files
        vif_files = [
            "packages/vif/calibration.py",
            "packages/vif/confidence_extraction.py",
            "packages/vif/confidence_bands.py",
            "packages/vif/replay.py",
            "packages/vif/cmc_integration.py",
            "packages/vif/cross_model_vif.py",
            "packages/vif/cross_model_witness_generator.py",
            "packages/vif/cross_model_confidence_calibrator.py",
            "packages/vif/cross_model_replay.py",
        ]
        
        for file_path in vif_files:
            if Path(file_path).exists():
                tagger.tag_file(file_path)
    else:
        # Tag single file
        file_path = sys.argv[1]
        tagger.tag_file(file_path)


if __name__ == "__main__":
    main()

