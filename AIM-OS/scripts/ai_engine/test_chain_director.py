"""Quick integration test: ChainDirector + ChainedMission."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ['PYTHONUNBUFFERED'] = '1'

from chain_director import ChainDirector, QualityEvaluator, ContextCompressor, TopologySelector, Topology, Action
from chained_mission import ChainedMission, ComplexityEstimator

print("═══ Integration Test: ChainDirector + ChainedMission ═══")

# 1. ChainedMission loads Director
m = ChainedMission()
assert m.director is not None, "Director should load"
print(f"✅ ChainedMission loaded with Director: {m.director is not None}")

# 2. Director plans correct topologies
plans = {
    'Audit the security of the AI Engine': 'gated',
    'Research how the context engine works': 'sequential',
    'Compare HHNI vs ContextPack for quality': 'debate',
}
for task, expected in plans.items():
    plan = m.director.plan_chain(task, complexity=0.8)
    ok = plan.topology.value == expected
    icon = '✅' if ok else '❌'
    print(f"{icon} '{task[:45]}' → {plan.topology.value} ({len(plan.phases)} phases)")
    assert ok, f"Expected {expected}, got {plan.topology.value}"

# 3. Quality evaluation differentiates good from bad
good = QualityEvaluator.evaluate(
    "### Analysis\n| A | B |\n|---|---|\n|x|y|\nConfidence: 0.9\n1. **REC** Recommend X\n2. **REC** Should Y",
    "Audit the system"
)
bad = QualityEvaluator.evaluate("fine", "Audit the system")
assert good.overall > bad.overall, "Good should score higher than bad"
print(f"✅ Quality: good={good.overall:.2f} > bad={bad.overall:.2f}")

# 4. Director makes correct decisions based on quality score
d = ChainDirector()
# good scored ~0.38 (short input) → correctly triggers rework (below 0.6)
# bad scored ~0.14 → correctly triggers rework first, skip after retries
decision_good = d.decide(good, 0, 3)
assert decision_good.value == 'rework', f"Quality {good.overall:.2f} should trigger rework (below 0.6)"
decision_bad = d.decide(bad, 0, 3)
assert decision_bad.value == 'rework', "Very low quality should trigger rework"
decision_bad_retried = d.decide(bad, 0, 3, retry_count=2)
assert decision_bad_retried.value == 'skip', "Low quality after 2 retries should skip"
# Timeout always triggers rework if retries left
from chain_director import QualityScore
decision_timeout = d.decide(QualityScore(overall=0.0), 0, 3, timed_out=True)
assert decision_timeout.value == 'rework'
print("✅ Decisions: rework/rework/skip/rework-timeout all correct")

# 5. Context compression
long_text = "### Header\n" + "content " * 500
compressed = ContextCompressor.compress(long_text, budget=200)
assert len(compressed) < len(long_text), "Compression should reduce size"
print(f"✅ Compression: {len(long_text)} → {len(compressed)} chars")

# 6. Complexity estimator
# Note: estimator uses `in` (boolean) for signals, not count
est = ComplexityEstimator.estimate(
    "Conduct a thorough audit of the entire AI Engine and evaluate architecture "
    "and assess code quality and comprehensively map all subsystem relationships "
    "and catalog every module and inventory all entry points and also review the docs"
)
assert est['score'] >= 0.3, f"Score {est['score']} should be non-trivial"
print(f"✅ Complexity: score={est['score']}")

# With previous_timeout, same task should definitely chain
est_timeout = ComplexityEstimator.estimate(
    "Audit the entire AI Engine thoroughly", previous_timeout=True
)
assert est_timeout['should_chain'] == True, f"Score {est_timeout['score']} should chain after timeout"
print(f"✅ Complexity+timeout: {est_timeout['score']} → chain={est_timeout['should_chain']}")

print("\n✅ ALL INTEGRATION TESTS PASSED")
