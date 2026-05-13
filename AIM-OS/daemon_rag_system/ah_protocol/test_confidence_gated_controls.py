"""
Test Suite for Confidence-Gated Controls - Step F of A-H Protocol

This module tests the Confidence-Gated Controls implementation.
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
from .context_mapping import ContextMapping, ContextMap, ContextNode, ContextRelationship, DependencyType
from .deep_expansion_layer import DeepExpansionLayer, ExpansionAnalysis, TierLevel, ComplexityLevel
from .context_mesh_maps import ContextMeshMaps, ContextMeshMap, ContextMeshContract, ContextConstraint, ConstraintType, ContractStatus
from .confidence_gated_controls import (
    ConfidenceGatedControls, ConfidencePacket, ChangeRequest, ConfidenceGate,
    MutationMode, ValidationStatus, ConfidenceLevel
)

class ConfidenceGatedControlsTester:
    """Test suite for Confidence-Gated Controls implementation."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.intent_capture = IntentCapture()
        self.hypothesis_formation = HypothesisFormation()
        self.context_mapping = ContextMapping()
        self.deep_expansion = DeepExpansionLayer()
        self.context_mesh_maps = ContextMeshMaps()
        self.confidence_gated_controls = ConfidenceGatedControls()
        self.test_results = {
            "confidence_gated_controls": {"passed": 0, "failed": 0, "tests": []},
            "integration": {"passed": 0, "failed": 0, "tests": []}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("Confidence-Gated Controls Test Suite")
        print("=" * 50)
        
        # Test Confidence-Gated Controls
        print("\nTesting Confidence-Gated Controls (Step F)")
        self._test_confidence_gated_controls()
        
        # Test Integration
        print("\nTesting Integration")
        self._test_integration()
        
        # Generate summary
        self._generate_summary()
        
        return self.test_results
    
    def _test_confidence_gated_controls(self):
        """Test Confidence-Gated Controls functionality."""
        
        # Test 1: Basic Confidence Packet Creation
        test_name = "Basic Confidence Packet Creation"
        try:
            # Create test data
            change_request = self._create_test_change_request("Implement new feature")
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            context_map = self._create_test_context_map()
            hypotheses = self._create_test_hypotheses()
            expansion_analysis = self._create_test_expansion_analysis()
            mesh_map = self._create_test_mesh_map()
            
            # Create confidence packet
            confidence_packet = self.confidence_gated_controls.create_confidence_packet(
                change_request, intent_profile, context_map, expansion_analysis, mesh_map
            )
            
            # Verify basic properties
            assert confidence_packet.id is not None, "No confidence packet ID"
            assert confidence_packet.change_id == change_request.id, "Change ID mismatch"
            assert confidence_packet.mutation_mode is not None, "No mutation mode"
            assert confidence_packet.tier_level is not None, "No tier level"
            assert 0.0 <= confidence_packet.confidence_score <= 1.0, "Invalid confidence score"
            assert confidence_packet.status == ValidationStatus.PENDING, "Invalid initial status"
            assert confidence_packet.created_at > 0, "Invalid creation timestamp"
            assert confidence_packet.expires_at > confidence_packet.created_at, "Invalid expiration time"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Basic confidence packet creation successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Basic confidence packet creation failed: {str(e)}")
        
        # Test 2: Mutation Mode Determination
        test_name = "Mutation Mode Determination"
        try:
            # Test different change types
            test_cases = [
                ("cosmetic change", MutationMode.TRIVIAL),
                ("refactor code", MutationMode.GENTLE),
                ("implement feature", MutationMode.GOVERNED),
                ("critical security fix", MutationMode.CRITICAL)
            ]
            
            for change_type, expected_mode in test_cases:
                change_request = self._create_test_change_request(change_type)
                change_request.change_type = change_type.split()[0]  # Extract first word
                
                expansion_analysis = self._create_test_expansion_analysis()
                mutation_mode = self.confidence_gated_controls._determine_mutation_mode(change_request, expansion_analysis)
                
                assert mutation_mode == expected_mode, f"Expected {expected_mode}, got {mutation_mode} for {change_type}"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Mutation mode determination successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Mutation mode determination failed: {str(e)}")
        
        # Test 3: Tier Level Determination
        test_name = "Tier Level Determination"
        try:
            # Test different component counts
            test_cases = [
                (1, TierLevel.TIER_0),
                (2, TierLevel.TIER_1),
                (4, TierLevel.TIER_2),
                (6, TierLevel.TIER_3)
            ]
            
            for component_count, expected_tier in test_cases:
                change_request = self._create_test_change_request("test change")
                change_request.affected_components = [f"component_{i}" for i in range(component_count)]
                
                expansion_analysis = self._create_test_expansion_analysis()
                tier_level = self.confidence_gated_controls._determine_tier_level(change_request, expansion_analysis)
                
                assert tier_level == expected_tier, f"Expected {expected_tier}, got {tier_level} for {component_count} components"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Tier level determination successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Tier level determination failed: {str(e)}")
        
        # Test 4: Confidence Score Calculation
        test_name = "Confidence Score Calculation"
        try:
            # Test confidence score calculation
            change_request = self._create_test_change_request("Implement new feature")
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            intent_profile.confidence_level = 0.8  # High confidence
            context_map = self._create_test_context_map()
            expansion_analysis = self._create_test_expansion_analysis()
            mesh_map = self._create_test_mesh_map()
            
            confidence_score = self.confidence_gated_controls._calculate_confidence_score(
                change_request, intent_profile, context_map, expansion_analysis, mesh_map, {}
            )
            
            assert 0.0 <= confidence_score <= 1.0, f"Confidence score {confidence_score} out of range"
            assert confidence_score > 0.0, "Confidence score should be positive"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Confidence score calculation successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Confidence score calculation failed: {str(e)}")
        
        # Test 5: Change Validation
        test_name = "Change Validation"
        try:
            # Create a valid confidence packet
            change_request = self._create_test_change_request("Implement new feature")
            intent_profile = self._create_test_intent_profile(IntentType.FEATURE_DEVELOPMENT)
            context_map = self._create_test_context_map()
            expansion_analysis = self._create_test_expansion_analysis()
            mesh_map = self._create_test_mesh_map()
            
            confidence_packet = self.confidence_gated_controls.create_confidence_packet(
                change_request, intent_profile, context_map, expansion_analysis, mesh_map
            )
            
            # Test validation with valid context
            context = {"obtained_approvals": ["self_approval", "peer_review"]}
            is_valid, errors, details = self.confidence_gated_controls.validate_change(confidence_packet, context)
            
            assert isinstance(is_valid, bool), "Validation result should be boolean"
            assert isinstance(errors, list), "Errors should be a list"
            assert isinstance(details, dict), "Details should be a dictionary"
            assert "packet_id" in details, "Details should contain packet_id"
            assert "validation_steps" in details, "Details should contain validation_steps"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Change validation successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Change validation failed: {str(e)}")
        
        # Test 6: Risk Assessment
        test_name = "Risk Assessment"
        try:
            # Test risk assessment generation
            change_request = self._create_test_change_request("Critical security fix")
            change_request.change_type = "critical"
            change_request.affected_components = ["component_1", "component_2", "component_3"]
            change_request.risk_level = "high"
            
            context_map = self._create_test_context_map()
            expansion_analysis = self._create_test_expansion_analysis()
            mesh_map = self._create_test_mesh_map()
            
            risk_assessment = self.confidence_gated_controls._generate_risk_assessment(
                change_request, context_map, expansion_analysis, mesh_map
            )
            
            assert "risk_score" in risk_assessment, "Risk assessment missing risk_score"
            assert "risk_level" in risk_assessment, "Risk assessment missing risk_level"
            assert "risk_factors" in risk_assessment, "Risk assessment missing risk_factors"
            assert "mitigation_strategies" in risk_assessment, "Risk assessment missing mitigation_strategies"
            assert 0.0 <= risk_assessment["risk_score"] <= 1.0, "Risk score out of range"
            assert risk_assessment["risk_level"] in ["low", "medium", "high"], "Invalid risk level"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Risk assessment successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Risk assessment failed: {str(e)}")
        
        # Test 7: Blast Radius Calculation
        test_name = "Blast Radius Calculation"
        try:
            # Test blast radius calculation
            change_request = self._create_test_change_request("test change")
            context_map = self._create_test_context_map()
            expansion_analysis = self._create_test_expansion_analysis()
            
            # Test different component counts
            test_cases = [
                (0, "none"),
                (1, "local"),
                (2, "limited"),
                (3, "moderate"),
                (5, "system_wide")
            ]
            
            for component_count, expected_radius in test_cases:
                change_request.affected_components = [f"component_{i}" for i in range(component_count)]
                blast_radius = self.confidence_gated_controls._calculate_blast_radius(
                    change_request, context_map, expansion_analysis
                )
                assert blast_radius == expected_radius, f"Expected {expected_radius}, got {blast_radius} for {component_count} components"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Blast radius calculation successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Blast radius calculation failed: {str(e)}")
        
        # Test 8: Validation Proofs
        test_name = "Validation Proofs"
        try:
            # Test validation proof generation
            change_request = self._create_test_change_request("Implement new feature")
            expansion_analysis = self._create_test_expansion_analysis()
            
            # Test different mutation modes
            for mutation_mode in [MutationMode.TRIVIAL, MutationMode.GENTLE, MutationMode.GOVERNED, MutationMode.CRITICAL]:
                proofs = self.confidence_gated_controls._generate_validation_proofs(
                    change_request, mutation_mode, TierLevel.TIER_1
                )
                
                assert isinstance(proofs, list), "Proofs should be a list"
                for proof in proofs:
                    assert proof.id is not None, "Proof missing ID"
                    assert proof.proof_type is not None, "Proof missing type"
                    assert proof.description is not None, "Proof missing description"
                    assert proof.validator is not None, "Proof missing validator"
                    assert 0.0 <= proof.confidence <= 1.0, "Proof confidence out of range"
            
            self._record_test_result("confidence_gated_controls", test_name, True, "Validation proofs successful")
            
        except Exception as e:
            self._record_test_result("confidence_gated_controls", test_name, False, f"Validation proofs failed: {str(e)}")
    
    def _test_integration(self):
        """Test integration with other A-H Protocol components."""
        
        # Test 1: End-to-End A-H Protocol with CGC
        test_name = "End-to-End A-H Protocol with CGC"
        try:
            # Step A: Intent Capture
            user_input = "Implement comprehensive confidence-gated controls for the system."
            context = {
                "active_project": "AIM-OS",
                "current_task_track": "AH_PROTOCOL_IMPLEMENTATION",
                "obtained_approvals": ["self_approval", "peer_review"]
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
            
            # Step E: Context Mesh Maps
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, context)
            assert len(mesh_map.contracts) > 0
            
            # Step F: Confidence-Gated Controls
            change_request = self._create_test_change_request("Implement confidence-gated controls")
            confidence_packet = self.confidence_gated_controls.create_confidence_packet(
                change_request, intent_profile, context_map, expansion_analysis, mesh_map, context
            )
            assert confidence_packet.id is not None
            
            # Validate the change
            is_valid, errors, details = self.confidence_gated_controls.validate_change(confidence_packet, context)
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)
            assert isinstance(details, dict)
            
            self._record_test_result("integration", test_name, True, "End-to-end A-H Protocol with CGC successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"End-to-end A-H Protocol with CGC failed: {str(e)}")
        
        # Test 2: Data Flow Through CGC
        test_name = "Data Flow Through CGC"
        try:
            # Create test data
            change_request = self._create_test_change_request("Test change for CGC")
            intent_profile = self._create_test_intent_profile(IntentType.SYSTEM_ENHANCEMENT)
            context_map = self._create_test_context_map()
            expansion_analysis = self._create_test_expansion_analysis()
            mesh_map = self._create_test_mesh_map()
            
            # Test data flow
            confidence_packet = self.confidence_gated_controls.create_confidence_packet(
                change_request, intent_profile, context_map, expansion_analysis, mesh_map, {}
            )
            
            # Verify data flow
            assert confidence_packet.id is not None, "No confidence packet ID"
            assert confidence_packet.created_at > 0, "Invalid creation timestamp"
            assert confidence_packet.version == "1.0", "Invalid version"
            assert confidence_packet.mutation_mode is not None, "No mutation mode"
            assert confidence_packet.tier_level is not None, "No tier level"
            assert confidence_packet.confidence_score >= 0.0, "Invalid confidence score"
            
            self._record_test_result("integration", test_name, True, "Data flow through CGC successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Data flow through CGC failed: {str(e)}")
        
        # Test 3: Error Handling
        test_name = "Error Handling"
        try:
            # Test with invalid inputs
            try:
                confidence_packet = self.confidence_gated_controls.create_confidence_packet(
                    None, None, None, None, None, None
                )
                assert False, "Should have raised an exception"
            except Exception:
                pass  # Expected behavior
            
            # Test with empty inputs
            empty_change_request = ChangeRequest(
                id="empty_change",
                description="",
                change_type="",
                affected_components=[],
                proposed_changes={},
                requester="",
                priority="",
                urgency="",
                estimated_effort="",
                risk_level="",
                dependencies=[],
                created_at=time.time(),
                updated_at=time.time()
            )
            
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
            
            empty_expansion_analysis = ExpansionAnalysis(
                root_node_id="empty_root",
                total_nodes=0,
                total_effort_hours=0.0,
                max_depth=0,
                tier_distribution={},
                complexity_distribution={},
                critical_path=[],
                rollout_sequence=[],
                risk_factors=[],
                test_coverage_required=0.0,
                blast_radius_analysis={},
                spec_coverage_index=0.0,
                created_at=time.time()
            )
            
            empty_mesh_map = self._create_test_mesh_map()
            
            confidence_packet = self.confidence_gated_controls.create_confidence_packet(
                empty_change_request, empty_intent, empty_context_map, empty_expansion_analysis, empty_mesh_map, {}
            )
            assert confidence_packet is not None, "Should handle empty inputs gracefully"
            
            self._record_test_result("integration", test_name, True, "Error handling successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Error handling failed: {str(e)}")
    
    def _create_test_change_request(self, description: str) -> ChangeRequest:
        """Create a test change request."""
        return ChangeRequest(
            id=f"test_change_{int(time.time())}",
            description=description,
            change_type="feature",
            affected_components=["component_1", "component_2"],
            proposed_changes={"new_feature": "test_feature"},
            requester="test_user",
            priority="medium",
            urgency="medium",
            estimated_effort="2 days",
            risk_level="medium",
            dependencies=["dependency_1"],
            created_at=time.time(),
            updated_at=time.time()
        )
    
    def _create_test_intent_profile(self, intent_type: IntentType) -> IntentProfile:
        """Create a test intent profile."""
        return IntentProfile(
            id="test_intent",
            raw_intent="Test intent for CGC testing",
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
                "component_1": ContextNode(
                    id="component_1",
                    name="Component 1",
                    type="system",
                    description="Test system component",
                    dependencies=[],
                    dependents=[],
                    constraints=[],
                    resources_required={},
                    impact_level=1,
                    criticality="medium",
                    availability="available",
                    owner="test_owner",
                    last_updated=time.time()
                ),
                "component_2": ContextNode(
                    id="component_2",
                    name="Component 2",
                    type="system",
                    description="Test system component",
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
    
    def _create_test_expansion_analysis(self) -> ExpansionAnalysis:
        """Create a test expansion analysis."""
        return ExpansionAnalysis(
            root_node_id="test_root",
            total_nodes=2,
            total_effort_hours=16.0,
            max_depth=1,
            tier_distribution={TierLevel.TIER_1: 2},
            complexity_distribution={ComplexityLevel.MODERATE: 2},
            critical_path=["test_root"],
            rollout_sequence=["test_root"],
            risk_factors=["test_risk"],
            test_coverage_required=0.8,
            blast_radius_analysis={"distribution": {"local": 2}},
            spec_coverage_index=0.9,
            created_at=time.time()
        )
    
    def _create_test_mesh_map(self) -> ContextMeshMap:
        """Create a test mesh map."""
        # Create a simple mesh map for testing
        from .context_mesh_maps import ContextMeshMap, ContextMeshContract, ContextConstraint, ConstraintType, ContractStatus
        
        contract = ContextMeshContract(
            id="test_contract",
            name="Test Contract",
            description="Test contract for CGC testing",
            scope=["component_1", "component_2"],
            dependencies=[],
            constraints=[],
            enforcement_rules=["test_rule"],
            monitoring_config={"frequency": "5m"},
            violation_handling={"action": "warn"},
            status=ContractStatus.DRAFT,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        constraint = ContextConstraint(
            id="test_constraint",
            constraint_type=ConstraintType.MUST_NEVER,
            description="Test constraint",
            rationale="Test rationale",
            affected_nodes=["component_1", "component_2"],
            enforcement_mechanism="test_mechanism",
            violation_penalty="test_penalty",
            monitoring_frequency="test_frequency",
            created_at=time.time(),
            updated_at=time.time()
        )
        
        return ContextMeshMap(
            id="test_mesh_map",
            name="Test Mesh Map",
            description="Test mesh map for CGC testing",
            contracts={"test_contract": contract},
            global_constraints=[constraint],
            dependency_graph=None,  # Will be set by the actual implementation
            constraint_violations=[],
            monitoring_metrics={"test_metric": {"frequency": "5m"}},
            created_at=time.time(),
            updated_at=time.time()
        )
    
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
        print("Confidence-Gated Controls Test Summary")
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
            print("  EXCELLENT: Confidence-Gated Controls implementation is working very well!")
        elif overall_success_rate >= 80:
            print("  GOOD: Confidence-Gated Controls implementation is working well with minor issues.")
        elif overall_success_rate >= 70:
            print("  FAIR: Confidence-Gated Controls implementation needs some improvements.")
        else:
            print("  POOR: Confidence-Gated Controls implementation needs significant work.")
        
        print("=" * 50)
        
        # Save results
        with open("confidence_gated_controls_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nTest results saved to: confidence_gated_controls_test_results.json")

if __name__ == "__main__":
    tester = ConfidenceGatedControlsTester()
    tester.run_all_tests()
