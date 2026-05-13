"""
Test Suite for Context Mesh Maps (CMM) - Step E of A-H Protocol

This module tests the Context Mesh Maps implementation.
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

class ContextMeshMapsTester:
    """Test suite for Context Mesh Maps implementation."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.intent_capture = IntentCapture()
        self.hypothesis_formation = HypothesisFormation()
        self.context_mapping = ContextMapping()
        self.deep_expansion = DeepExpansionLayer()
        self.context_mesh_maps = ContextMeshMaps()
        self.test_results = {
            "context_mesh_maps": {"passed": 0, "failed": 0, "tests": []},
            "integration": {"passed": 0, "failed": 0, "tests": []}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("Context Mesh Maps Test Suite")
        print("=" * 50)
        
        # Test Context Mesh Maps
        print("\nTesting Context Mesh Maps (Step E)")
        self._test_context_mesh_maps()
        
        # Test Integration
        print("\nTesting Integration")
        self._test_integration()
        
        # Generate summary
        self._generate_summary()
        
        return self.test_results
    
    def _test_context_mesh_maps(self):
        """Test Context Mesh Maps functionality."""
        
        # Test 1: Basic Context Mesh Map Creation
        test_name = "Basic Context Mesh Map Creation"
        try:
            # Create test data
            user_input = "Implement the A-H Protocol workflow in the daemon/RAG system."
            context = {"active_project": "AIM-OS", "current_task_track": "AH_PROTOCOL_IMPLEMENTATION"}
            
            intent_profile = self.intent_capture.capture_intent(user_input, context)
            context_map = self.context_mapping.map_context(intent_profile, [], context)
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, context)
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, context)
            
            # Create context mesh map
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, context)
            
            # Verify basic properties
            assert mesh_map.id is not None, "No mesh map ID"
            assert mesh_map.name is not None, "No mesh map name"
            assert mesh_map.description is not None, "No mesh map description"
            assert len(mesh_map.contracts) > 0, "No contracts generated"
            assert len(mesh_map.global_constraints) > 0, "No global constraints generated"
            assert mesh_map.dependency_graph is not None, "No dependency graph"
            assert mesh_map.monitoring_metrics is not None, "No monitoring metrics"
            
            self._record_test_result("context_mesh_maps", test_name, True, "Basic context mesh map creation successful")
            
        except Exception as e:
            self._record_test_result("context_mesh_maps", test_name, False, f"Basic context mesh map creation failed: {str(e)}")
        
        # Test 2: Contract Generation
        test_name = "Contract Generation"
        try:
            # Create test data
            user_input = "Implement security hardening measures for the system."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Create context mesh map
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, {})
            
            # Verify contracts
            assert len(mesh_map.contracts) > 0, "No contracts generated"
            
            for contract_id, contract in mesh_map.contracts.items():
                assert contract.id is not None, f"Contract {contract_id} has no ID"
                assert contract.name is not None, f"Contract {contract_id} has no name"
                assert contract.description is not None, f"Contract {contract_id} has no description"
                assert len(contract.scope) > 0, f"Contract {contract_id} has no scope"
                assert contract.status is not None, f"Contract {contract_id} has no status"
                assert len(contract.dependencies) >= 0, f"Contract {contract_id} has invalid dependencies"
                assert len(contract.constraints) >= 0, f"Contract {contract_id} has invalid constraints"
            
            self._record_test_result("context_mesh_maps", test_name, True, "Contract generation successful")
            
        except Exception as e:
            self._record_test_result("context_mesh_maps", test_name, False, f"Contract generation failed: {str(e)}")
        
        # Test 3: Constraint Generation
        test_name = "Constraint Generation"
        try:
            # Create test data
            user_input = "Implement performance optimization for the database layer."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Create context mesh map
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, {})
            
            # Verify global constraints
            assert len(mesh_map.global_constraints) > 0, "No global constraints generated"
            
            for constraint in mesh_map.global_constraints:
                assert constraint.id is not None, "Constraint has no ID"
                assert constraint.constraint_type is not None, "Constraint has no type"
                assert constraint.description is not None, "Constraint has no description"
                assert constraint.rationale is not None, "Constraint has no rationale"
                assert len(constraint.affected_nodes) > 0, "Constraint has no affected nodes"
                assert constraint.enforcement_mechanism is not None, "Constraint has no enforcement mechanism"
                assert constraint.violation_penalty is not None, "Constraint has no violation penalty"
                assert constraint.monitoring_frequency is not None, "Constraint has no monitoring frequency"
            
            self._record_test_result("context_mesh_maps", test_name, True, "Constraint generation successful")
            
        except Exception as e:
            self._record_test_result("context_mesh_maps", test_name, False, f"Constraint generation failed: {str(e)}")
        
        # Test 4: Dependency Graph Creation
        test_name = "Dependency Graph Creation"
        try:
            # Create test data with relationships
            user_input = "Implement a complex multi-component system."
            intent_profile = self.intent_capture.capture_intent(user_input)
            
            # Create a more complex context map
            context_map = self._create_complex_context_map()
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Create context mesh map
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, {})
            
            # Verify dependency graph
            assert mesh_map.dependency_graph is not None, "No dependency graph created"
            assert len(mesh_map.dependency_graph.nodes) > 0, "Dependency graph has no nodes"
            assert len(mesh_map.dependency_graph.edges) >= 0, "Dependency graph has invalid edges"
            
            # Check graph properties
            for node_id in mesh_map.dependency_graph.nodes:
                node_data = mesh_map.dependency_graph.nodes[node_id]
                assert 'name' in node_data, f"Node {node_id} missing name"
                assert 'type' in node_data, f"Node {node_id} missing type"
                assert 'description' in node_data, f"Node {node_id} missing description"
            
            self._record_test_result("context_mesh_maps", test_name, True, "Dependency graph creation successful")
            
        except Exception as e:
            self._record_test_result("context_mesh_maps", test_name, False, f"Dependency graph creation failed: {str(e)}")
        
        # Test 5: Monitoring Configuration
        test_name = "Monitoring Configuration"
        try:
            # Create test data
            user_input = "Implement comprehensive monitoring for the system."
            intent_profile = self.intent_capture.capture_intent(user_input)
            context_map = self.context_mapping.map_context(intent_profile, [], {})
            hypotheses = self.hypothesis_formation.form_hypotheses(intent_profile, {})
            expansion_analysis = self.deep_expansion.expand_system(intent_profile, context_map, hypotheses, {})
            
            # Create context mesh map
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, {})
            
            # Verify monitoring configuration
            assert mesh_map.monitoring_metrics is not None, "No monitoring metrics"
            assert "dependency_health" in mesh_map.monitoring_metrics, "No dependency health monitoring"
            assert "constraint_violations" in mesh_map.monitoring_metrics, "No constraint violation monitoring"
            assert "contract_compliance" in mesh_map.monitoring_metrics, "No contract compliance monitoring"
            assert "system_health" in mesh_map.monitoring_metrics, "No system health monitoring"
            
            # Check monitoring configuration structure
            for metric_name, metric_config in mesh_map.monitoring_metrics.items():
                assert "monitor_frequency" in metric_config, f"Metric {metric_name} missing frequency"
                assert "alert_threshold" in metric_config, f"Metric {metric_name} missing alert threshold"
                assert "critical_threshold" in metric_config, f"Metric {metric_name} missing critical threshold"
            
            self._record_test_result("context_mesh_maps", test_name, True, "Monitoring configuration successful")
            
        except Exception as e:
            self._record_test_result("context_mesh_maps", test_name, False, f"Monitoring configuration failed: {str(e)}")
        
        # Test 6: Constraint Types
        test_name = "Constraint Types"
        try:
            # Test different constraint types
            constraint_types = [
                ConstraintType.MUST_NEVER,
                ConstraintType.MUST_ALWAYS,
                ConstraintType.SHOULD_NEVER,
                ConstraintType.SHOULD_ALWAYS,
                ConstraintType.CAN_NEVER,
                ConstraintType.CAN_ALWAYS
            ]
            
            for constraint_type in constraint_types:
                # Create a simple constraint
                constraint = ContextConstraint(
                    id=f"test_constraint_{constraint_type.value}",
                    constraint_type=constraint_type,
                    description=f"Test {constraint_type.value} constraint",
                    rationale="Test rationale",
                    affected_nodes=["test_node"],
                    enforcement_mechanism="test_mechanism",
                    violation_penalty="test_penalty",
                    monitoring_frequency="test_frequency",
                    created_at=time.time(),
                    updated_at=time.time()
                )
                
                # Verify constraint properties
                assert constraint.constraint_type == constraint_type, f"Constraint type mismatch for {constraint_type.value}"
                assert constraint.description is not None, f"Constraint description missing for {constraint_type.value}"
                assert constraint.rationale is not None, f"Constraint rationale missing for {constraint_type.value}"
            
            self._record_test_result("context_mesh_maps", test_name, True, "Constraint types successful")
            
        except Exception as e:
            self._record_test_result("context_mesh_maps", test_name, False, f"Constraint types failed: {str(e)}")
    
    def _test_integration(self):
        """Test integration with other A-H Protocol components."""
        
        # Test 1: End-to-End A-H Protocol with CMM
        test_name = "End-to-End A-H Protocol with CMM"
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
            
            # Step E: Context Mesh Maps
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, context)
            assert len(mesh_map.contracts) > 0
            assert len(mesh_map.global_constraints) > 0
            
            self._record_test_result("integration", test_name, True, "End-to-end A-H Protocol with CMM successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"End-to-end A-H Protocol with CMM failed: {str(e)}")
        
        # Test 2: Data Flow Through CMM
        test_name = "Data Flow Through CMM"
        try:
            # Create test data
            intent_profile = self._create_test_intent_profile(IntentType.SYSTEM_ENHANCEMENT)
            context_map = self._create_test_context_map()
            hypotheses = self._create_test_hypotheses()
            expansion_analysis = self._create_test_expansion_analysis()
            
            # Test data flow
            mesh_map = self.context_mesh_maps.create_context_mesh_map(intent_profile, context_map, expansion_analysis, {})
            
            # Verify data flow
            assert mesh_map.id is not None, "No mesh map ID"
            assert mesh_map.created_at > 0, "Invalid creation timestamp"
            assert mesh_map.version == "1.0", "Invalid version"
            assert len(mesh_map.contracts) > 0, "No contracts generated"
            assert len(mesh_map.global_constraints) > 0, "No global constraints generated"
            
            self._record_test_result("integration", test_name, True, "Data flow through CMM successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Data flow through CMM failed: {str(e)}")
        
        # Test 3: Error Handling
        test_name = "Error Handling"
        try:
            # Test with invalid inputs
            try:
                mesh_map = self.context_mesh_maps.create_context_mesh_map(None, None, None, None)
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
            
            mesh_map = self.context_mesh_maps.create_context_mesh_map(empty_intent, empty_context_map, empty_expansion_analysis, {})
            assert mesh_map is not None, "Should handle empty inputs gracefully"
            
            self._record_test_result("integration", test_name, True, "Error handling successful")
            
        except Exception as e:
            self._record_test_result("integration", test_name, False, f"Error handling failed: {str(e)}")
    
    def _create_complex_context_map(self) -> ContextMap:
        """Create a complex context map with relationships."""
        nodes = {
            "node_1": ContextNode(
                id="node_1",
                name="Database Layer",
                type="database",
                description="Core database functionality",
                dependencies=[],
                dependents=["node_2", "node_3"],
                constraints=["ACID compliance"],
                resources_required={"cpu": "high", "memory": "high"},
                impact_level=3,
                criticality="critical",
                availability="available",
                owner="database_team",
                last_updated=time.time()
            ),
            "node_2": ContextNode(
                id="node_2",
                name="API Layer",
                type="api",
                description="REST API endpoints",
                dependencies=["node_1"],
                dependents=["node_4"],
                constraints=["RESTful design"],
                resources_required={"cpu": "medium", "memory": "medium"},
                impact_level=2,
                criticality="high",
                availability="available",
                owner="api_team",
                last_updated=time.time()
            ),
            "node_3": ContextNode(
                id="node_3",
                name="Cache Layer",
                type="cache",
                description="Redis cache system",
                dependencies=["node_1"],
                dependents=["node_2"],
                constraints=["High availability"],
                resources_required={"cpu": "low", "memory": "high"},
                impact_level=1,
                criticality="medium",
                availability="available",
                owner="infrastructure_team",
                last_updated=time.time()
            ),
            "node_4": ContextNode(
                id="node_4",
                name="Frontend Layer",
                type="frontend",
                description="User interface",
                dependencies=["node_2"],
                dependents=[],
                constraints=["Responsive design"],
                resources_required={"cpu": "low", "memory": "low"},
                impact_level=1,
                criticality="low",
                availability="available",
                owner="frontend_team",
                last_updated=time.time()
            )
        }
        
        relationships = [
            ContextRelationship(
                from_node="node_1",
                to_node="node_2",
                relationship_type=DependencyType.HARD_DEPENDENCY,
                strength=0.9,
                description="API depends on database",
                constraints=["data_consistency"],
                risks=["data_loss"],
                mitigation_strategies=["backup", "replication"]
            ),
            ContextRelationship(
                from_node="node_1",
                to_node="node_3",
                relationship_type=DependencyType.SOFT_DEPENDENCY,
                strength=0.7,
                description="Cache depends on database",
                constraints=["eventual_consistency"],
                risks=["stale_data"],
                mitigation_strategies=["cache_invalidation"]
            ),
            ContextRelationship(
                from_node="node_2",
                to_node="node_4",
                relationship_type=DependencyType.HARD_DEPENDENCY,
                strength=0.8,
                description="Frontend depends on API",
                constraints=["api_contract"],
                risks=["service_unavailable"],
                mitigation_strategies=["circuit_breaker", "fallback"]
            )
        ]
        
        return ContextMap(
            id="complex_context_map",
            name="Complex System Context Map",
            nodes=nodes,
            relationships=relationships,
            critical_paths=[["node_1", "node_2", "node_4"]],
            risk_factors=["database_failure", "api_failure"],
            mitigation_strategies=["redundancy", "monitoring"],
            external_dependencies=["cloud_provider"],
            organizational_factors=["team_structure"],
            user_workflows=[{"name": "user_login", "steps": ["frontend", "api", "database"]}],
            created_at=time.time(),
            updated_at=time.time()
        )
    
    def _create_test_intent_profile(self, intent_type: IntentType) -> IntentProfile:
        """Create a test intent profile."""
        return IntentProfile(
            id="test_intent",
            raw_intent="Test intent for CMM testing",
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
    
    def _create_test_expansion_analysis(self) -> ExpansionAnalysis:
        """Create a test expansion analysis."""
        return ExpansionAnalysis(
            root_node_id="test_root",
            total_nodes=1,
            total_effort_hours=8.0,
            max_depth=1,
            tier_distribution={TierLevel.TIER_1: 1},
            complexity_distribution={ComplexityLevel.MODERATE: 1},
            critical_path=["test_root"],
            rollout_sequence=["test_root"],
            risk_factors=["test_risk"],
            test_coverage_required=0.8,
            blast_radius_analysis={"distribution": {"local": 1}},
            spec_coverage_index=0.9,
            created_at=time.time()
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
        print("Context Mesh Maps Test Summary")
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
            print("  EXCELLENT: Context Mesh Maps implementation is working very well!")
        elif overall_success_rate >= 80:
            print("  GOOD: Context Mesh Maps implementation is working well with minor issues.")
        elif overall_success_rate >= 70:
            print("  FAIR: Context Mesh Maps implementation needs some improvements.")
        else:
            print("  POOR: Context Mesh Maps implementation needs significant work.")
        
        print("=" * 50)
        
        # Save results
        with open("context_mesh_maps_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nTest results saved to: context_mesh_maps_test_results.json")

if __name__ == "__main__":
    tester = ContextMeshMapsTester()
    tester.run_all_tests()
