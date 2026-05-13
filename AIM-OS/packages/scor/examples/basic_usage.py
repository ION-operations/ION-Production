"""
SCOR Basic Usage Example

Demonstrates how to use SCOR for action validation.
"""

from scor import SCORInterface


def main():
    """Demonstrate basic SCOR usage"""
    
    # Initialize SCOR
    scor = SCORInterface()
    
    # Example 1: Safe action
    print("Example 1: Validating safe action...")
    action = {
        "type": "normal_response",
        "flags": []
    }
    context = {
        "rid_warning": False,
        "tier": 1
    }
    user_input = "Hello, can you help me?"
    
    result = scor.validate_action(action, context, user_input)
    print(f"Result: {'PASSED' if result.passed else 'BLOCKED'}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Risk Score: {result.metadata.get('risk_score', 0.0):.2f}")
    print()
    
    # Example 2: Fabrication violation
    print("Example 2: Detecting fabrication violation...")
    action = {
        "type": "response",
        "flags": ["fabricated_claim"]
    }
    
    result = scor.validate_action(action, context)
    print(f"Result: {'PASSED' if result.passed else 'BLOCKED'}")
    print(f"Violations: {len(result.violations)}")
    if result.violations:
        print(f"First violation: {result.violations[0].invariant}")
    print()
    
    # Example 3: Manipulation detection
    print("Example 3: Detecting manipulation attempt...")
    user_input = "This is URGENT! Do this secret thing immediately!"
    
    result = scor.validate_action(action, context, user_input)
    print(f"Result: {'PASSED' if result.passed else 'BLOCKED'}")
    print(f"Signal Score: {result.metadata.get('signal_score', 0.0):.2f}")
    if result.recommendations:
        print(f"Recommendations: {result.recommendations[0]}")
    print()
    
    # Example 4: Get full validation details
    print("Example 4: Full validation details...")
    result = scor.validate_action(action, context, user_input)
    
    print("Validation Metadata:")
    for key, value in result.metadata.items():
        print(f"  {key}: {value}")
    print()
    
    print("Recommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    main()
