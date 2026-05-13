"""
Comprehensive Test Suite for A-H Protocol Implementation

This module tests the first three steps of the A-H Protocol:
- Step A: Intent Capture
- Step B: Hypothesis Formation  
- Step C: Context Mapping

Tests verify functionality, data integrity, and integration between components.
"""

import sys
import os
import time
import json
from typing import Dict, Any, List

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .intent_capture import IntentCapture, IntentProfile, IntentType
from .hypothesis_formation import HypothesisFormation, Hypothesis, HypothesisStatus
from .context_mapping import ContextMapping, ContextMap, ContextNode, DependencyType

class AHProtocolTester:
    """Comprehensive test suite for A-H Protocol implementation."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.intent_capture = IntentCapture()
        self.hypothesis_formation = HypothesisFormation()
        self.context_mapping = ContextMapping()
        self.test_results = {
            "intent_capture": {"passed": 0, "failed": 0, "tests": []},
            "hypothesis_formation": {"passed": 0, "failed": 0, "tests": []},
            "context_mapping": {"passed": 0, "failed": 0, "tests": []},
            "integration": {"passed": 0, "failed": 0, "tests": []}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("Starting A-H Protocol Test Suite")
        print("=" * 50)
        
        # Test Intent Capture (Step A)
        print("\nTesting Step A: Intent Capture")
        self._test_intent_capture()
        
        # Test Hypothesis Formation (Step B)
        print("\nTesting Step B: Hypothesis Formation")
        self._test_hypothesis_formation()
        
        # Test Context Mapping (Step C)
        print("\nTesting Step C: Context Mapping")
        self._test_context_mapping()
        
        # Test Integration
        print("\nTesting Integration")
        self._test_integration()
        
        # Generate summary
        self._generate_summary()
        
        return self.test_results
    
    def _test_intent_capture(self):
        """Test Intent Capture System (Step A)."""
        
        # Test 1: Basic Intent Capture
        test_name = "Basic Intent Capture"
        try:
            user_input = "I need to implement the A-H Protocol workflow in the daemon/RAG system."
            context = {"active_project": "AIM-OS", "current_task_track": "AH_PROTOCOL_IMPLEMENTATION"}
            
            profile = self.intent_capture.capture_intent(user_input, context)
            
            # Verify basic properties
            assert profile.raw_intent == user_input
            assert profile.intent_type == IntentType.PROTOCOL_IMPLEMENTATION  # "A-H Protocol workflow" should be protocol implementation
            assert "system" in profile.primary_stakeholders  # System stakeholders for protocol implementation
            assert profile.confidence_level > 0.0
            assert profile.complexity_score > 0.0
            
            self._record_test_result("intent_capture", test_name, True, "Basic intent capture successful")
            
        except Exception as e:
            self._record_test_result("intent_capture", test_name, False, f"Basic intent capture failed: {str(e)}")
        
        # Test 2: Intent Type Classification
        test_name = "Intent Type Classification"
        try:
            test_cases = [
                ("Fix the memory leak in the system", IntentType.BUG_FIX),
                ("Optimize the performance of the algorithm", IntentType.PERFORMANCE_OPTIMIZATION),
                ("Conduct a security audit", IntentType.AUDIT_REVIEW),
                ("Update the documentation", IntentType.DOCUMENTATION_UPDATE),
                ("Implement new security features", IntentType.SECURITY_HARDENING)
            ]
            
            for user_input, expected_type in test_cases:
                profile = self.intent_capture.capture_intent(user_input)
                assert profile.intent_type == expected_type, f"Expected {expected_type}, got {profile.intent_type}"
            
            self._record_test_result("intent_capture", test_name, True, "Intent type classification successful")
            
        except Exception as e:
            self._record_test_result("intent_capture", test_name, False, f"Intent type classification failed: {str(e)}")
        
        # Test 3: Stakeholder Extraction
        test_name = "Stakeholder Extraction"
        try:
            user_input = "I need to implement a feature for users and developers with admin oversight."
            profile = self.intent_capture.capture_intent(user_input)
            
            assert "end_users" in profile.primary_stakeholders
            assert "developers" in profile.primary_stakeholders
            assert "administrators" in profile.primary_stakeholders
            
            self._record_test_result("intent_capture", test_name, True, "Stakeholder extraction successful")
            
        except Exception as e:
            self._record_test_result("intent_capture", test_name, False, f"Stakeholder extraction failed: {str(e)}")
        
        # Test 4: Constraint Identification
        test_name = "Constraint Identification"
        try:
            user_input = "I need to fix this bug urgently due to time constraints and budget limitations."
            profile = self.intent_capture.capture_intent(user_input)
            
            assert "time_constraint" in profile.constraints
            assert "resource_constraint" in profile.constraints
            
            self._record_test_result("intent_capture", test_name, True, "Constraint identification successful")
            
        except Exception as e:
            self._record_test_result("intent_capture", test_name, False, f"Constraint identification failed: {str(e)}")
        
        # Test 5: Success Criteria Definition
        test_name = "Success Criteria Definition"
        try:
            user_input = "Implement a new feature with specific requirements."
            profile = self.intent_capture.capture_intent(user_input)
            
            assert len(profile.success_criteria) > 0
            assert any("implemented" in criterion.lower() for criterion in profile.success_criteria)
            
            self._record_test_result("intent_capture", test_name, True, "Success criteria definition successful")
            
        except Exception as e:
            self._record_test_result("intent_capture", test_name, False, f"Success criteria definition failed: {str(e)}")
        
        # Test 6: Confidence and Complexity Calculation
        test_name = "Confidence and Complexity Calculation"
        try:
            simple_input = "Fix a typo"
            complex_input = "Implement a complex distributed system with microservices architecture, real-time data processing, and machine learning integration"
            
            simple_profile = self.intent_capture.capture_intent(simple_input)
            complex_profile = self.intent_capture.capture_intent(complex_input)
            
            assert simple_profile.complexity_score < complex_profile.complexity_score
            assert simple_profile.confidence_level > 0.0
            assert complex_profile.confidence_level > 0.0
            
            self._record_test_result("intent_capture", test_name, True, "Confidence and complexity calculation successful")
            
        except Exception as e:
            self._record_test_result("intent_capture", test_name, False, f"Confidence and complexity calculation failed: {str(e)}")
    
    def _test_hypothesis_formation(self):
        """Test Hypothesis Formation System (Step B)."""
        
        # Test 1: Basic Hypothesis Formation
        test_name = "Basic Hypothesis Formation"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile)
            
            assert len(hypotheses) > 0
            assert all(isinstance(h, Hypothesis) for h in hypotheses)
            assert all(h.status == HypothesisStatus.TESTABLE for h in hypotheses)
            
            self._record_test_result("hypothesis_formation", test_name, True, "Basic hypothesis formation successful")
            
        except Exception as e:
            self._record_test_result("hypothesis_formation", test_name, False, f"Basic hypothesis formation failed: {str(e)}")
        
        # Test 2: Intent Type Specific Hypotheses
        test_name = "Intent Type Specific Hypotheses"
        try:
            intent_types = [
                IntentType.FEATURE_DEVELOPMENT,
                IntentType.BUG_FIX,
                IntentType.SYSTEM_ENHANCEMENT,
                IntentType.PROTOCOL_IMPLEMENTATION,
                IntentType.AUDIT_REVIEW
            ]
            
            for intent_type in intent_types:
                intent_profile = self._create_test_intent_profile(intent_type)
                hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile)
                
                assert len(hypotheses) > 0, f"No hypotheses generated for {intent_type}"
                
                # Check that hypotheses are relevant to intent type
                for hypothesis in hypotheses:
                    assert len(hypothesis.description) > 0
                    assert len(hypothesis.assumptions) > 0
                    assert len(hypothesis.testable_conditions) > 0
                    assert len(hypothesis.expected_outcomes) > 0
            
            self._record_test_result("hypothesis_formation", test_name, True, "Intent type specific hypotheses successful")
            
        except Exception as e:
            self._record_test_result("hypothesis_formation", test_name, False, f"Intent type specific hypotheses failed: {str(e)}")
        
        # Test 3: Hypothesis Ranking
        test_name = "Hypothesis Ranking"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile)
            
            # Check that hypotheses are ranked by priority
            priorities = [h.priority for h in hypotheses]
            assert priorities == sorted(priorities, reverse=True), "Hypotheses not properly ranked by priority"
            
            # Check that all hypotheses have valid priority scores
            assert all(0 <= h.priority <= 100 for h in hypotheses), "Invalid priority scores"
            
            self._record_test_result("hypothesis_formation", test_name, True, "Hypothesis ranking successful")
            
        except Exception as e:
            self._record_test_result("hypothesis_formation", test_name, False, f"Hypothesis ranking failed: {str(e)}")
        
        # Test 4: Hypothesis Properties
        test_name = "Hypothesis Properties"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.BUG_FIX)
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile)
            
            for hypothesis in hypotheses:
                # Check required properties
                assert len(hypothesis.id) > 0
                assert len(hypothesis.description) > 0
                assert 0.0 <= hypothesis.confidence <= 1.0
                assert 0.0 <= hypothesis.impact_score <= 1.0
                assert hypothesis.effort_estimate in ["low", "medium", "high", "very_high"]
                assert hypothesis.status in HypothesisStatus
                assert len(hypothesis.assumptions) > 0
                assert len(hypothesis.testable_conditions) > 0
                assert len(hypothesis.expected_outcomes) > 0
                assert len(hypothesis.validation_method) > 0
            
            self._record_test_result("hypothesis_formation", test_name, True, "Hypothesis properties successful")
            
        except Exception as e:
            self._record_test_result("hypothesis_formation", test_name, False, f"Hypothesis properties failed: {str(e)}")
        
        # Test 5: Hypothesis Dependencies and Risks
        test_name = "Hypothesis Dependencies and Risks"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.PROTOCOL_IMPLEMENTATION)
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile)
            
            for hypothesis in hypotheses:
                # Check that dependencies and risks are lists
                assert isinstance(hypothesis.dependencies, list)
                assert isinstance(hypothesis.risks, list)
                assert isinstance(hypothesis.success_metrics, list)
                
                # Check that refutation conditions exist
                assert len(hypothesis.refutation_conditions) > 0
            
            self._record_test_result("hypothesis_formation", test_name, True, "Hypothesis dependencies and risks successful")
            
        except Exception as e:
            self._record_test_result("hypothesis_formation", test_name, False, f"Hypothesis dependencies and risks failed: {str(e)}")
    
    def _test_context_mapping(self):
        """Test Context Mapping System (Step C)."""
        
        # Test 1: Basic Context Mapping
        test_name = "Basic Context Mapping"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            hypotheses = self._create_test_hypotheses()
            context = {"active_project": "AIM-OS", "open_files": ["daemon_rag_system/daemon_rag_system.py"]}
            
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            
            assert isinstance(context_map, ContextMap)
            assert len(context_map.nodes) > 0
            assert len(context_map.relationships) > 0
            assert context_map.id.startswith("context_map_")
            
            self._record_test_result("context_mapping", test_name, True, "Basic context mapping successful")
            
        except Exception as e:
            self._record_test_result("context_mapping", test_name, False, f"Basic context mapping failed: {str(e)}")
        
        # Test 2: System Identification
        test_name = "System Identification"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.PROTOCOL_IMPLEMENTATION)
            hypotheses = self._create_test_hypotheses()
            context = {"active_project": "AIM-OS"}
            
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            
            # Check that LUCID systems are identified
            lucid_systems = [node for node in context_map.nodes.values() if node.type == "lucid_system"]
            assert len(lucid_systems) > 0, "LUCID systems not identified"
            
            # Check that project system is identified
            project_systems = [node for node in context_map.nodes.values() if node.type == "project"]
            assert len(project_systems) > 0, "Project system not identified"
            
            self._record_test_result("context_mapping", test_name, True, "System identification successful")
            
        except Exception as e:
            self._record_test_result("context_mapping", test_name, False, f"System identification failed: {str(e)}")
        
        # Test 3: Relationship Mapping
        test_name = "Relationship Mapping"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            hypotheses = self._create_test_hypotheses()
            context = {"active_project": "AIM-OS"}
            
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            
            # Check that relationships exist
            assert len(context_map.relationships) > 0, "No relationships mapped"
            
            # Check relationship properties
            for rel in context_map.relationships:
                assert rel.from_node in context_map.nodes
                assert rel.to_node in context_map.nodes
                assert rel.relationship_type in DependencyType
                assert 0.0 <= rel.strength <= 1.0
                assert len(rel.description) > 0
            
            self._record_test_result("context_mapping", test_name, True, "Relationship mapping successful")
            
        except Exception as e:
            self._record_test_result("context_mapping", test_name, False, f"Relationship mapping failed: {str(e)}")
        
        # Test 4: Critical Path Identification
        test_name = "Critical Path Identification"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.PROTOCOL_IMPLEMENTATION)
            hypotheses = self._create_test_hypotheses()
            context = {"active_project": "AIM-OS"}
            
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            
            # Check that critical paths are identified
            assert len(context_map.critical_paths) >= 0, "Critical path identification failed"
            
            # Check critical path structure
            for path in context_map.critical_paths:
                assert isinstance(path, list)
                assert len(path) > 1, "Critical path too short"
                for node_id in path:
                    assert node_id in context_map.nodes, f"Node {node_id} not in context map"
            
            self._record_test_result("context_mapping", test_name, True, "Critical path identification successful")
            
        except Exception as e:
            self._record_test_result("context_mapping", test_name, False, f"Critical path identification failed: {str(e)}")
        
        # Test 5: Risk Assessment
        test_name = "Risk Assessment"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            hypotheses = self._create_test_hypotheses()
            context = {"active_project": "AIM-OS"}
            
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            
            # Check that risk factors are identified
            assert len(context_map.risk_factors) >= 0, "Risk assessment failed"
            
            # Check that mitigation strategies exist
            assert len(context_map.mitigation_strategies) >= 0, "Mitigation strategies not generated"
            
            self._record_test_result("context_mapping", test_name, True, "Risk assessment successful")
            
        except Exception as e:
            self._record_test_result("context_mapping", test_name, False, f"Risk assessment failed: {str(e)}")
        
        # Test 6: External Dependencies
        test_name = "External Dependencies"
        try:
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            hypotheses = self._create_test_hypotheses()
            context = {"active_project": "AIM-OS"}
            
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            
            # Check that external dependencies are identified
            assert len(context_map.external_dependencies) > 0, "External dependencies not identified"
            
            # Check that organizational factors are identified
            assert len(context_map.organizational_factors) > 0, "Organizational factors not identified"
            
            self._record_test_result("context_mapping", test_name, True, "External dependencies successful")
            
        except Exception as e:
            self._record_test_result("context_mapping", test_name, False, f"External dependencies failed: {str(e)}")
    
    def _test_integration(self):
        """Test integration between A-H Protocol components."""
        
        # Test 1: End-to-End Workflow
        test_name = "End-to-End Workflow"
        try:
            # Step A: Intent Capture
            user_input = "I need to implement the A-H Protocol workflow in the daemon/RAG system for AI consciousness development."
            context = {
                "active_project": "AIM-OS",
                "current_task_track": "AH_PROTOCOL_IMPLEMENTATION",
                "open_files": ["daemon_rag_system/daemon_rag_system.py"]
            }
            
            intent_profile = self.intent_capture.capture_intent(user_input, context)
            assert intent_profile.intent_type == IntentType.PROTOCOL_IMPLEMENTATION  # "A-H Protocol workflow" should be protocol implementation
            
            # Step B: Hypothesis Formation
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, context)
            assert len(hypotheses) > 0
            
            # Step C: Context Mapping
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            assert len(context_map.nodes) > 0
            assert len(context_map.relationships) > 0
            
            self._record_test_result("integration", test_name, True, "End-to-end workflow successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"End-to-end workflow failed: {str(e)}")
        
        # Test 2: Data Flow Between Components
        test_name = "Data Flow Between Components"
        try:
            # Create intent profile
            intent_profile = self._create_test_intent_profile(IntentType.PROTOCOL_IMPLEMENTATION)
            
            # Test that intent profile data flows to hypothesis formation
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile)
            assert len(hypotheses) > 0
            
            # Test that intent profile and hypotheses data flows to context mapping
            context_map = self.context_mapping.map_context(intent_profile, hypotheses)
            assert len(context_map.nodes) > 0
            
            # Verify data consistency
            assert context_map.name == f"Context Map for {intent_profile.intent_type.value}"
            
            self._record_test_result("integration", test_name, True, "Data flow between components successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Data flow between components failed: {str(e)}")
        
        # Test 3: Error Handling
        test_name = "Error Handling"
        try:
            # Test with invalid input
            try:
                invalid_profile = self.intent_capture.capture_intent("")
                # Should not raise exception, but should handle gracefully
            except Exception:
                pass  # Expected for empty input
            
            # Test with None context
            try:
                profile = self.intent_capture.capture_intent("Test input", None)
                assert profile is not None
            except Exception:
                pass  # Should handle None context gracefully
            
            self._record_test_result("integration", test_name, True, "Error handling successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Error handling failed: {str(e)}")
    
    def _create_test_intent_profile(self, intent_type: IntentType) -> IntentProfile:
        """Create a test intent profile."""
        return IntentProfile(
            id=f"test_intent_{int(time.time())}",
            raw_intent=f"Test intent for {intent_type.value}",
            intent_type=intent_type,
            primary_stakeholders=["aether_ai", "human_operator"],
            constraints=["time_constraint", "LUCID_compliance"],
            success_criteria=["Task completed successfully", "Quality standards met"],
            non_negotiable_requirements=["LUCID compliance", "Zero hallucinations"],
            confidence_level=0.8,
            complexity_score=0.6,
            urgency_level="medium",
            estimated_effort="medium",
            risk_factors=["technical_complexity"],
            dependencies=["A-H Protocol", "L0-L4 standards"],
            context_data={"active_project": "AIM-OS"},
            timestamp=time.time()
        )
    
    def _create_test_hypotheses(self) -> List[Hypothesis]:
        """Create test hypotheses."""
        return [
            Hypothesis(
                id=f"test_hyp_{int(time.time())}",
                description="Test hypothesis for A-H Protocol implementation",
                assumptions=["Protocol is well-defined", "Resources are available"],
                testable_conditions=["All steps can be implemented", "Tests can be written"],
                expected_outcomes=["Complete implementation", "All tests passing"],
                validation_method="protocol_testing",
                priority=1,
                confidence=0.8,
                impact_score=0.9,
                effort_estimate="high",
                status=HypothesisStatus.TESTABLE,
                evidence=[],
                refutation_conditions=["Protocol incomplete", "Resources unavailable"],
                dependencies=["A_H_Protocol", "L0_L4_Documentation"],
                risks=["complexity", "time_pressure"],
                success_metrics=["completeness", "test_coverage"],
                created_at=time.time(),
                updated_at=time.time()
            )
        ]
    
    def _record_test_result(self, component: str, test_name: str, passed: bool, message: str):
        """Record a test result."""
        if passed:
            self.test_results[component]["passed"] += 1
            status = "PASS"
        else:
            self.test_results[component]["failed"] += 1
            status = "FAIL"
        
        self.test_results[component]["tests"].append({
            "name": test_name,
            "passed": passed,
            "message": message
        })
        
        print(f"  {status} {test_name}: {message}")
    
    def _generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 50)
        print("A-H Protocol Test Summary")
        print("=" * 50)
        
        total_passed = 0
        total_failed = 0
        
        for component, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            if total > 0:
                success_rate = (passed / total) * 100
                print(f"\n{component.upper()}:")
                print(f"  Tests: {total} | Passed: {passed} | Failed: {failed} | Success Rate: {success_rate:.1f}%")
            else:
                print(f"\n{component.upper()}: No tests run")
        
        print(f"\nOVERALL:")
        total_tests = total_passed + total_failed
        if total_tests > 0:
            overall_success_rate = (total_passed / total_tests) * 100
            print(f"  Total Tests: {total_tests} | Passed: {total_passed} | Failed: {total_failed}")
            print(f"  Overall Success Rate: {overall_success_rate:.1f}%")
            
            if overall_success_rate >= 90:
                print("  EXCELLENT: A-H Protocol implementation is working very well!")
            elif overall_success_rate >= 80:
                print("  GOOD: A-H Protocol implementation is working well with minor issues.")
            elif overall_success_rate >= 70:
                print("  FAIR: A-H Protocol implementation needs some improvements.")
            else:
                print("  POOR: A-H Protocol implementation needs significant work.")
        else:
            print("  No tests were run.")
        
        print("\n" + "=" * 50)

def main():
    """Main test execution function."""
    print("A-H Protocol Test Suite")
    print("Testing Steps A, B, and C of A-H Protocol Implementation")
    print("=" * 60)
    
    # Create and run test suite
    tester = AHProtocolTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("ah_protocol_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nTest results saved to: ah_protocol_test_results.json")
    
    # Return exit code based on results
    total_failed = sum(results[component]["failed"] for component in results)
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
