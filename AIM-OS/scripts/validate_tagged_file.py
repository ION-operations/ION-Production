#!/usr/bin/env python3
"""Quick validation script for tagged files"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.sdfcvf.quintet import QuintetDetector, QuintetParityCalculator, NLTagGate, print_diagnostic_report

def validate_file(file_path):
    """Validate a single tagged file"""
    print(f"\n{'='*60}")
    print(f"Validating: {file_path}")
    print(f"{'='*60}\n")
    
    # Detect quintet
    detector = QuintetDetector()
    quintet = detector.detect_from_files(
        code_files=[file_path],
        docs_files=[],
        tests_files=[],
        traces_files=[]
    )
    
    print(f"Detection:")
    print(f"  Code symbols: {len(quintet.code_symbols)}")
    print(f"  NL tags: {len(quintet.nl_tags)}")
    
    # Calculate parity
    calculator = QuintetParityCalculator()
    result = calculator.calculate_parity(quintet)
    
    print(f"\nQuintet Parity:")
    print(f"  Score: {result.score:.3f}")
    print(f"  Status: {'PASSED' if result.score >= 0.90 else 'NEEDS WORK'}")
    
    # Check gate
    gate = NLTagGate(
        public_coverage_threshold=0.95,
        internal_coverage_threshold=0.75,
        code_tags_threshold=0.85
    )
    gate_result = gate.check(quintet, result)
    
    print(f"\nGate Result:")
    print(f"  Passed: {gate_result.passed}")
    if gate_result.issues:
        print(f"  Issues: {len(gate_result.issues)}")
        for issue in gate_result.issues[:3]:
            print(f"    - {issue}")
    if gate_result.warnings:
        print(f"  Warnings: {len(gate_result.warnings)}")
        for warning in gate_result.warnings[:3]:
            print(f"    - {warning}")
    
    print(f"\n{'='*60}\n")
    
    return result.score >= 0.90 and gate_result.passed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_tagged_file.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    passed = validate_file(file_path)
    
    sys.exit(0 if passed else 1)

