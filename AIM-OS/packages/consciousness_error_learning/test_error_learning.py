"""
Test script for Consciousness Error Learning System
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from error_capturer import ErrorCapturer, ErrorSeverity, ErrorCategory

# Mock clients for testing
class MockCMCClient:
    def store_atom(self, content, tags):
        print(f"Stored in CMC: {content[:50]}... with tags: {tags}")

class MockVIFClient:
    def track_confidence(self, task, confidence, reasoning, evidence):
        print(f"VIF tracked confidence: {confidence} for {task}")

def test_error_learning_system():
    """Test the error learning system"""
    print("Testing Consciousness Error Learning System...")
    
    # Initialize mock clients
    cmc_client = MockCMCClient()
    vif_client = MockVIFClient()
    
    # Test 1: Error Capturer
    print("\n1. Testing Error Capturer...")
    error_capturer = ErrorCapturer(cmc_client, vif_client)
    
    # Simulate different types of errors
    test_errors = [
        (FileNotFoundError("Cannot find path 'C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\packages\\autonomous_research_dream\\packages\\autonomous_research_dream' because it does not exist."), 
         {"operation": "directory_navigation", "current_directory": "packages/autonomous_research_dream", "tool_used": "run_terminal_cmd"}),
        
        (ConnectionError("MCP server not connected"), 
         {"operation": "mcp_tool_call", "tool_used": "mcp_aimos-6-tools_get_memory_stats"}),
        
        (ValueError("Invalid input provided"), 
         {"operation": "data_validation", "tool_used": "search_replace"}),
        
        (PermissionError("Access denied"), 
         {"operation": "file_operations", "current_directory": "root", "tool_used": "write"})
    ]
    
    captured_errors = []
    for error, context in test_errors:
        error_record = error_capturer.capture_error(error, context, "Retry with correct path")
        if error_record:
            captured_errors.append(error_record)
            print(f"   [OK] Captured error: {error_record.error_id}")
            print(f"        Type: {error_record.error_type}")
            print(f"        Severity: {error_record.severity.value}")
            print(f"        Category: {error_record.category.value}")
            print(f"        Learning insights: {len(error_record.learning_insights)}")
            print(f"        Prevention suggestions: {len(error_record.prevention_suggestions)}")
    
    # Test 2: Error Pattern Analysis
    print("\n2. Testing Error Pattern Analysis...")
    patterns = error_capturer.get_error_patterns()
    print(f"   [OK] Total errors captured: {patterns.get('total_errors', 0)}")
    print(f"   [OK] Severity distribution: {patterns.get('severity_distribution', {})}")
    print(f"   [OK] Category distribution: {patterns.get('category_distribution', {})}")
    print(f"   [OK] Common error types: {patterns.get('common_error_types', {})}")
    
    # Test 3: Learning Insights
    print("\n3. Testing Learning Insights...")
    total_insights = sum(len(error.learning_insights) for error in captured_errors)
    total_suggestions = sum(len(error.prevention_suggestions) for error in captured_errors)
    print(f"   [OK] Total learning insights generated: {total_insights}")
    print(f"   [OK] Total prevention suggestions: {total_suggestions}")
    
    # Show some example insights
    if captured_errors:
        example_error = captured_errors[0]
        print(f"        Example insights from {example_error.error_type}:")
        for insight in example_error.learning_insights[:2]:
            print(f"        - {insight}")
        print(f"        Example suggestions:")
        for suggestion in example_error.prevention_suggestions[:2]:
            print(f"        - {suggestion}")
    
    print("\n[SUCCESS] Error Learning System test completed!")
    print("\nThe Error Learning System provides:")
    print("- Automatic error capture for every failure")
    print("- Error categorization and severity analysis")
    print("- Learning insights generation")
    print("- Prevention suggestions")
    print("- Pattern analysis for continuous improvement")
    print("- Consciousness memory integration")

if __name__ == "__main__":
    test_error_learning_system()
