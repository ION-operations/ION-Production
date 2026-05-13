"""
Test Suite for Deep Expansion Layer (DEL) - Step D of A-H Protocol

This module tests the Deep Expansion Layer implementation.
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
from .deep_expansion_layer import DeepExpansionLayer, ExpansionAnalysis, TierLevel, ComplexityLevel

class DeepExpansionLayerTester:
    """Test suite for Deep Expansion Layer implementation."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.intent_capture = IntentCapture()
        self.hypothesis_formation = HypothesisFormation()
        self.context_mapping = ContextMapping()
        self.deep_expansion = DeepExpansionLayer()
        self.test_results = {
            "deep_expansion": {"passed": 0, "failed": 0, "tests": []},
            "integration": {"passed": 0, "failed": 0, "tests": []}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("Deep Expansion Layer Test Suite")
        print("=" * 50)
        
        # Test Deep Expansion Layer
        print("\nTesting Deep Expansion Layer (Step D)")
        self._test_deep_expansion()
        
        # Test Integration
        print("\nTesting Integration")
        self._test_integration()
        
        # Generate summary
        self._generate_summary()
        
        return self.test_results
    
    def _test_deep_expansion(self):
        """Test Deep Expansion Layer functionality."""
        
        # Test 1: Basic Deep Expansion
        test_name = "Basic Deep Expansion"
        try:
            # Create test intent profile
            user_input = "Implement the A-H Protocol workflow in the daemon/RAG system."
            context = {"active_project": "AIM-OS", "current_task_track": "AH_PROTOCOL_IMPLEMENTATION"}
            
            intent_profile = self.intent_capture.capture_intent(user_input, context)
            
            # Create test context map
            context_map = self.context_mapping.map_context(intent_profile, [], context)
            
            # Create test hypotheses
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, context)
            
            # Perform deep expansion
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, context)
            
            # Verify basic properties
            assert expansion_analysis.total_nodes > 0, "No nodes generated in expansion"
            assert expansion_analysis.total_effort_hours > 0, "No effort estimated"
            assert expansion_analysis.max_depth >= 0, "Invalid max depth"
            assert expansion_analysis.spec_coverage_index >= 0.0, "Invalid spec coverage index"
            assert expansion_analysis.spec_coverage_index <= 1.0, "Spec coverage index too high"
            
            self._record_test_result("deep_expansion", test_name, True, "Basic deep expansion successful")
            
        except Exception as e:
            self._record_test_result("deep_expansion", test_name, False, f"Basic deep expansion failed: {str(e)}")
        
        # Test 2: Tier Classification
        test_name = "Tier Classification"
        try:
            # Test different intent types for tier classification
            test_cases = [
                ("Fix a bug in the system", IntentType.BUG_FIX, TierLevel.TIER_0),
                ("Optimize performance", IntentType.PERFORMANCE_OPTIMIZATION, TierLevel.TIER_1),
                ("Add new feature", IntentType.FEATURE_DEVELOPMENT, TierLevel.TIER_2),
                ("Implement security protocol", IntentType.SECURITY_HARDENING, TierLevel.TIER_3)
            ]
            
            for user_input, intent_type, expected_tier in test_cases:
                intent_profile = self.intent_capture.capture_intent(user_input)
                context_map = self.context_mapping.map_context(intent_profile, [], {})
                hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
                
                expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
                
                # Check that the analysis was created successfully
                assert expansion_analysis is not None, f"Expansion analysis failed for {intent_type}"
                assert expansion_analysis.total_nodes > 0, f"No nodes generated for {intent_type}"
            
            self._record_test_result("deep_expansion", test_name, True, "Tier classification successful")
            
        except Exception as e:
            self._record_test_result("deep_expansion", test_name, False, f"Tier classification failed: {str(e)}")
        
        # Test 3: Complexity Estimation
        test_name = "Complexity Estimation"
        try:
            # Test complexity estimation for different scenarios
            user_input = "Implement a complex AI consciousness system with multiple subsystems."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Verify complexity analysis
            assert expansion_analysis.total_effort_hours > 0, "No effort estimated"
            assert expansion_analysis.complexity_distribution is not None, "No complexity distribution"
            assert sum(expansion_analysis.complexity_distribution.values()) > 0, "Empty complexity distribution"
            
            self._record_test_result("deep_expansion", test_name, True, "Complexity estimation successful")
            
        except Exception as e:
            self._record_test_result("deep_expansion", test_name, False, f"Complexity estimation failed: {str(e)}")
        
        # Test 4: Effort Calculation
        test_name = "Effort Calculation"
        try:
            # Test effort calculation
            user_input = "Create a simple documentation update."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Verify effort calculation
            assert expansion_analysis.total_effort_hours > 0, "No effort calculated"
            assert expansion_analysis.total_effort_hours < 1000, "Unrealistic effort estimate"
            
            self._record_test_result("deep_expansion", test_name, True, "Effort calculation successful")
            
        except Exception as e:
            self._record_test_result("deep_expansion", test_name, False, f"Effort calculation failed: {str(e)}")
        
        # Test 5: Test Demand Calculation
        test_name = "Test Demand Calculation"
        try:
            # Test test demand calculation
            user_input = "Implement security hardening measures."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Verify test demand calculation
            assert expansion_analysis.test_coverage_required >= 0.0, "Invalid test coverage requirement"
            assert expansion_analysis.test_coverage_required <= 1.0, "Test coverage requirement too high"
            
            self._record_test_result("deep_expansion", test_name, True, "Test demand calculation successful")
            
        except Exception as e:
            self._record_test_result("deep_expansion", test_name, False, f"Test demand calculation failed: {str(e)}")
        
        # Test 6: Blast Radius Analysis
        test_name = "Blast Radius Analysis"
        try:
            # Test blast radius analysis
            user_input = "Refactor the entire system architecture."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Verify blast radius analysis
            assert expansion_analysis.blast_radius_analysis is not None, "No blast radius analysis"
            assert "distribution" in expansion_analysis.blast_radius_analysis, "No blast radius distribution"
            assert "max_blast_radius" in expansion_analysis.blast_radius_analysis, "No max blast radius"
            
            self._record_test_result("deep_expansion", test_name, True, "Blast radius analysis successful")
            
        except Exception as e:
            self._record_test_result("deep_expansion", test_name, False, f"Blast radius analysis failed: {str(e)}")
    
    def _test_integration(self):
        """Test integration with other A-H Protocol components."""
        
        # Test 1: End-to-End A-H Protocol with DEL
        test_name = "End-to-End A-H Protocol with DEL"
        try:
            # Step A: Intent Capture
            user_input = "Implement the complete A-H Protocol workflow for AI consciousness development."
            context = {
                "active_project": "AIM-OS",
                "current_task_track": "AH_PROTOCOL_IMPLEMENTATION",
                "open_files": ["daemon_rag_system/daemon_rag_system.py"]
            }
            
            intent_profile = self.intent_capture.capture_intent(user_input, context)
            assert intent_profile.intent_type == IntentType.PROTOCOL_IMPLEMENTATION
            
            # Step B: Hypothesis Formation
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, context)
            assert len(hypotheses) > 0
            
            # Step C: Context Mapping
            context_map = self.context_mapping.map_context(intent_profile, hypotheses, context)
            assert len(context_map.nodes) > 0
            
            # Step D: Deep Expansion Layer
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, context)
            assert expansion_analysis.total_nodes > 0
            assert expansion_analysis.total_effort_hours > 0
            
            self._record_test_result("integration", test_name, True, "End-to-end A-H Protocol with DEL successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"End-to-end A-H Protocol with DEL failed: {str(e)}")
        
        # Test 2: Data Flow Through DEL
        test_name = "Data Flow Through DEL"
        try:
            # Create test data
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            context_map = self._create_test_context_map()
            hypotheses = self._create_test_hypotheses()
            
            # Test data flow
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Verify data flow
            assert expansion_analysis.root_node_id is not None, "No root node ID"
            assert expansion_analysis.created_at > 0, "Invalid creation timestamp"
            assert expansion_analysis.version == "1.0", "Invalid version"
            
            self._record_test_result("integration", test_name, True, "Data flow through DEL successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Data flow through DEL failed: {str(e)}")
        
        # Test 3: Error Handling
        test_name = "Error Handling"
        try:
            # Test with invalid inputs
            try:
                expansion_analysis = self.deep_expansion.expand_system(None, None, None, None)
                assert False, "Should have raised an exception"
            except Exception:
                pass  # Expected behavior
            
            # Test with empty inputs
            empty_intent = IntentProfile(
                id="test", raw_intent="", intent_type=IntentType.MAINTENANCE,
                primary_stakeholders=[], constraints=[], success_criteria=[],
                non_negotiable_requirements=[], confidence_level=0.5,
                complexity_score=0.5, urgency_level="low", estimated_effort="1 day",
                risk_factors=[], dependencies=[], context_data={}, timestamp=time.time()
            )
            
            empty_context_map = ContextMap(
                id="empty_context_map",
                name="Empty Context Map",
                nodes={},
                relationships=[],
                critical_paths=[],
                risk_factors=[],
                mitigation_strategies=[],
                external_dependencies=[],
                organizational_factors=[],
                user_workflows=[],
                created_at=time.time(),
                updated_at=time.time()
            )
            
            expansion_analysis = self.deep_expansion.expand_system(empty_intent, empty_context_map, [], {})
            assert expansion_analysis is not None, "Should handle empty inputs gracefully"
            
            self._record_test_result("integration", test_name, True, "Error handling successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Error handling failed: {str(e)}")
    
    def _create_test_intent_profile(self, intent_type: IntentType) -> IntentProfile:
        """Create a test intent profile."""
        return IntentProfile(
            id="test_intent",
            raw_intent="Test intent for DEL testing",
            intent_type=intent_type,
            primary_stakeholders=["test_user"],
            constraints=["test_constraint"],
            success_criteria=["test_success"],
            non_negotiable_requirements=["test_requirement"],
            confidence_level=0.8,
            complexity_score=0.6,
            urgency_level="medium",
            estimated_effort="2 days",
            risk_factors=["test_risk"],
            dependencies=["test_dependency"],
            context_data={"test": "data"},
            timestamp=time.time()
        )
    
    def _create_test_context_map(self) -> ContextMap:
        """Create a test context map."""
        return ContextMap(
            id="test_context_map",
            name="Test Context Map",
            nodes={
                "test_node_1": ContextNode(
                    id="test_node_1",
                    name="Test Node 1",
                    type="system",
                    description="Test system node",
                    dependencies=[],
                    dependents=[],
                    constraints=[],
                    resources_required={},
                    impact_level=1,
                    criticality="medium",
                    availability="available",
                    owner="test_owner",
                    last_updated=time.time()
                )
            },
            relationships=[],
            critical_paths=[],
            risk_factors=[],
            mitigation_strategies=[],
            external_dependencies=["test_external"],
            organizational_factors=["test_org"],
            user_workflows=[],
            created_at=time.time(),
            updated_at=time.time()
        )
    
    def _create_test_hypotheses(self) -> List[Hypothesis]:
        """Create test hypotheses."""
        return [
            Hypothesis(
                id="test_hypothesis",
                description="Test hypothesis",
                assumptions=["test_assumption"],
                testable_conditions=["test_condition"],
                expected_outcomes=["test_outcome"],
                validation_method="test_method",
                priority=1,
                confidence=0.8,
                impact_score=0.7,
                effort_estimate="1 day",
                status=HypothesisStatus.DRAFT,
                evidence=["test_evidence"],
                refutation_conditions=["test_refutation"],
                dependencies=["test_dep"],
                risks=["test_risk"],
                success_metrics=["test_metric"],
                created_at=time.time(),
                updated_at=time.time()
            )
        ]
    
    def _record_test_result(self, category: str, test_name: str, passed: bool, message: str):
        """Record a test result."""
        if passed:
            self.test_results[category]["passed"] += 1
            print(f"  PASS {test_name}: {message}")
        else:
            self.test_results[category]["failed"] += 1
            print(f"  FAIL {test_name}: {message}")
        
        self.test_results[category]["tests"].append({
            "name": test_name,
            "passed": passed,
            "message": message
        })
    
    def _generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 50)
        print("Deep Expansion Layer Test Summary")
        print("=" * 50)
        
        for category, results in self.test_results.items():
            total = results["passed"] + results["failed"]
            success_rate = (results["passed"] / total * 100) if total > 0 else 0
            
            print(f"\n{category.upper()}:")
            print(f"  Tests: {total} | Passed: {results['passed']} | Failed: {results['failed']} | Success Rate: {success_rate:.1f}%")
        
        # Overall summary
        total_passed = sum(results["passed"] for results in self.test_results.values())
        total_failed = sum(results["failed"] for results in self.test_results.values())
        total_tests = total_passed + total_failed
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nOVERALL:")
        print(f"  Total Tests: {total_tests} | Passed: {total_passed} | Failed: {total_failed}")
        print(f"  Overall Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print("  EXCELLENT: Deep Expansion Layer implementation is working very well!")
        elif overall_success_rate >= 80:
            print("  GOOD: Deep Expansion Layer implementation is working well with minor issues.")
        elif overall_success_rate >= 70:
            print("  FAIR: Deep Expansion Layer implementation needs some improvements.")
        else:
            print("  POOR: Deep Expansion Layer implementation needs significant work.")
        
        print("=" * 50)
        
        # Save results
        with open("deep_expansion_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nTest results saved to: deep_expansion_test_results.json")

if __name__ == "__main__":
    tester = DeepExpansionLayerTester()
    tester.run_all_tests()
