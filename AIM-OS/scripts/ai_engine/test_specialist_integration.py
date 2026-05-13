"""Test specialist system integration with ChainDirector."""
import sys, os

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))

print("═══ Specialist Pipeline Integration Test ═══\n")

# Step 1: Test WorkDetector → Work
from specialist_system.work_detector import WorkDetector
detector = WorkDetector()
work = detector.detect_work("Build a REST API with WebSocket support and chat interface")
print(f"✅ WorkDetector: domains={work.domain}, systems={work.systems}, complexity={work.complexity}")
assert len(work.domain) > 0, "Should detect domains"
assert len(work.systems) > 0, "Should detect systems"

# Step 2: Test RelevanceCalculator + ActivationSystem  
from specialist_system.specialist_registry import SpecialistRegistry
from specialist_system.initial_specialists import register_initial_specialists
from specialist_system.relevance_calculator import RelevanceCalculator
from specialist_system.activation_system import ActivationSystem

registry = SpecialistRegistry()
register_initial_specialists(registry)
calc = RelevanceCalculator()
activation = ActivationSystem(registry, calc)
result = activation.activate_specialists(work)

print(f"✅ Activation pipeline: {len(result.scores)} specialists scored")
for spec_id, score in sorted(result.scores.items(), key=lambda x: -x[1].overall):
    name = registry.get(spec_id).name
    print(f"   {name}: {score.overall:.3f} (domain={score.domain_match:.2f}, "
          f"sys={score.system_connections:.2f})")

# Step 3: Verify Director._score_specialists returns scores  
from chain_director import ChainDirector
d = ChainDirector()
scores, act_result = d._score_specialists("Build a REST API with WebSocket and chat interface")
print(f"\n✅ Director scores: {scores}")
assert isinstance(scores, dict), "Scores should be a dict"
assert act_result is not None, "Activation result should be returned"
assert len(act_result.scores) == 5, "Should have 5 specialist scores"

# Step 4: Test plan_chain includes specialist info
plan = d.plan_chain("Build a REST API with WebSocket and chat interface")
print(f"\n✅ Plan: {plan.topology.value} topology, {len(plan.phases)} phases")
for p in plan.phases:
    spec_info = p.specialist_id or 'none (below threshold)'
    print(f"   {p.phase_name} ({p.role}) → {spec_info}")
print(f"   Specialist scores: {plan.specialist_scores}")

# Verify specialists in plan match specialist_scores
assert plan.specialist_scores == scores, "Plan should have same scores as scoring"

# Step 5: Test topology selection works for various tasks
for task, expected_topo in [
    ("Audit the security of all API endpoints", "gated"),
    ("Design a new chat UI with conversation threading", "sequential"),
    ("Compare REST vs GraphQL for our backend", "debate"),
]:
    plan2 = d.plan_chain(task)
    assert plan2.topology.value == expected_topo, f"Expected {expected_topo}, got {plan2.topology.value}"
    print(f"✅ '{task[:50]}' → {plan2.topology.value} "
          f"({len(plan2.specialist_scores)} scored)")

# Step 6: Verify that when specialists DO activate, they get assigned
# Create a specialist with LOW threshold to test assignment path
from specialist_system.specialist_registry import Specialist

test_spec = Specialist(
    id='test-api-expert',
    name='API Expert',
    domain=['Backend Integration', 'APIs', 'REST', 'WebSocket'],
    description='API development specialist',
    connections={
        'systems': ['REST', 'GraphQL', 'WebSocket', 'HTTP', 'gRPC'],
        'data': ['api-specs', 'integration-patterns'],
        'patterns': ['api-patterns', 'integration-patterns']
    },
    relevance_factors={
        'domain_match': 0.40, 'data_connections': 0.25,
        'system_connections': 0.20, 'pattern_recognition': 0.10,
        'complexity': 0.05
    },
    activation_thresholds={
        'ownership': 0.30, 'activation': 0.15, 'consultation': 0.05
    }
)

# Test with low-threshold specialist  
test_registry = SpecialistRegistry()
test_registry.register(test_spec)
test_calc = RelevanceCalculator()
test_activation = ActivationSystem(test_registry, test_calc)
test_result = test_activation.activate_specialists(work)

api_score = test_result.scores.get('test-api-expert')
activated = len(test_result.get_all_activated())
print(f"\n✅ Low-threshold test: API Expert scored {api_score.overall:.3f}")
print(f"   Ownership: {[s.name for s in test_result.ownership]}")
print(f"   Activation: {[s.name for s in test_result.activation]}")
assert activated > 0, f"API Expert should activate with low thresholds (score={api_score.overall:.3f})"
print(f"   → {activated} specialist(s) activated with low thresholds")

print("\n✅ ALL SPECIALIST INTEGRATION TESTS PASSED")
