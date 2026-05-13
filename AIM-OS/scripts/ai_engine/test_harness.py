#!/usr/bin/env python3
"""
AIM-OS AI Engine — Test Harness

Run: python -m ai_engine.test_harness
Or:  python scripts/ai_engine/test_harness.py

Tests each subsystem independently without imports that
trigger workspace auto-indexing.
"""

import sys
import os
import time

# Ensure the scripts dir is on the path
scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

RESULTS = []

def test(name, fn):
    """Run a test and record the result."""
    try:
        fn()
        RESULTS.append(('OK', name))
        print(f'  ✓ {name}')
    except Exception as e:
        RESULTS.append(('FAIL', name, str(e)))
        print(f'  ✗ {name}: {e}')


def main():
    print('=== AIM-OS AI Engine v2.0 — Test Harness ===\n')

    # ── Layer 6: Safety (no external deps) ──
    print('[L6 Safety]')

    def test_vif_gates():
        from ai_engine.safety.vif_gates import VIFGate, GateVerdict
        gate = VIFGate()
        # High confidence file write — should pass
        r = gate.check('file:write', confidence=0.8)
        assert r.passed, f'Expected pass, got {r.verdict}'
        # Low confidence destructive — should block
        r = gate.check('file:delete', confidence=0.2)
        assert not r.passed, f'Expected block for low-confidence delete'
        # Red zone without token — should escalate
        r = gate.check('mcp:mutate_orchestration', confidence=0.9, has_human_token=False)
        assert r.verdict == GateVerdict.ESCALATE
        # Red zone with token — should pass
        r = gate.check('mcp:mutate_orchestration', confidence=0.9, has_human_token=True)
        assert r.passed
    test('VIF Gates', test_vif_gates)

    def test_two_phase_commit():
        from ai_engine.safety.vif_gates import VIFGate
        gate = VIFGate()
        proposal = gate.propose_risky_action('file:delete', 'Delete old logs', '/tmp/logs')
        assert proposal.action_id
        assert not gate.two_phase_gate.can_apply(proposal.action_id)
        gate.two_phase_gate.verify(proposal.action_id, approved=True)
        assert gate.two_phase_gate.can_apply(proposal.action_id)
    test('Two-Phase Commit', test_two_phase_commit)

    # ── Layer 5: Swarm Contracts ──
    print('\n[L5 Swarm]')

    def test_contracts():
        from ai_engine.swarm.contracts import (
            JobPacket, ResultPacket, CapabilityToken, RED_ZONE_CAPABILITIES,
            ROLE_CAPABILITIES, WorkerRole,
        )
        job = JobPacket(job_id='j_test', role='coder', task_description='Fix auth')
        assert job.job_id == 'j_test'
        coder_caps = ROLE_CAPABILITIES[WorkerRole.CODER]
        assert CapabilityToken.FILE_READ in coder_caps
        assert CapabilityToken.FILE_DELETE not in coder_caps
        assert CapabilityToken.MCP_MUTATE_ORCHESTRATION in RED_ZONE_CAPABILITIES
    test('Swarm Contracts', test_contracts)

    # ── Layer 7: Session ──
    print('\n[L7 Session]')

    def test_sessions():
        from ai_engine.session_manager import SessionManager, SessionState
        mgr = SessionManager()
        s = mgr.create(agent_id='coder_v1', job_id='j_test')
        assert s.state == SessionState.CREATED
        mgr.activate(s.session_id)
        assert mgr.get(s.session_id).state == SessionState.ACTIVE
        mgr.complete(s.session_id, summary='Done')
        assert mgr.get(s.session_id).state == SessionState.COMPLETED
    test('Session Manager', test_sessions)

    # ── Layer 3: Registry ──
    print('\n[L3 Registry]')

    def test_registry():
        from ai_engine.registry import AgentRegistry
        reg = AgentRegistry()
        status = reg.status()
        assert status['total_agents'] >= 6, f'Expected 6+ agents, got {status["total_agents"]}'
        coder = reg.find_best_for('coding')
        assert coder is not None
        assert coder.role == 'coder'
        architect = reg.find_best_for('planning')
        assert architect is not None
        assert architect.role == 'architect'
    test('Agent Registry', test_registry)

    # ── Layer 3: Genome Loader ──
    print('\n[L3 Genome]')

    def test_genome():
        from ai_engine.genome_loader import GenomeLoader
        loader = GenomeLoader(os.path.join(scripts_dir, '..'))
        genome = loader.build_genome(role='coder', task='Fix the auth module')
        prompt = genome.to_system_prompt()
        assert len(prompt) > 100, f'Genome prompt too short: {len(prompt)}'
        assert genome.total_tokens > 0
    test('Genome Loader', test_genome)

    # ── Layer 4: Traces ──
    print('\n[L4 Traces]')

    def test_traces():
        from ai_engine.traces.execution_trace import ExecutionTrace, TraceStore, TraceOutcome
        trace = ExecutionTrace(
            task_description='Fix auth module',
            task_type='coding',
            agent_name='coder_v1',
            model_used='gemini-2.0-flash',
            outcome=TraceOutcome.SUCCESS,
            confidence=0.85,
            total_time_ms=1200,
        )
        assert trace.trace_id.startswith('trace_')
        cmc_content = trace.to_cmc_content()
        assert 'Fix auth module' in cmc_content
        tags = trace.to_cmc_tags()
        assert tags['type'] == 'execution_trace'
    test('Execution Traces', test_traces)

    # ── Layer 4: Learner ──

    def test_learner():
        from ai_engine.learning.agent_learner import AgentLearner
        from ai_engine.traces.execution_trace import ExecutionTrace, TraceOutcome
        learner = AgentLearner()
        trace = ExecutionTrace(
            task_type='coding',
            agent_name='coder_v1',
            model_used='gemini-2.0-flash',
            outcome=TraceOutcome.SUCCESS,
            confidence=0.9,
            total_time_ms=800,
        )
        insights = learner.learn_from_trace(trace)
        stats = learner.get_model_stats()
        assert 'gemini-2.0-flash' in stats
    test('Agent Learner', test_learner)

    # ── v2.0 Integration Tests ──
    print('\n[v2.0 Integration]')

    def test_intent_classifier():
        workspace = os.path.join(scripts_dir, '..')
        sys.path.insert(0, workspace)
        from packages.intent_classification.classification_engine import ClassificationEngine
        engine = ClassificationEngine()
        result = engine.classify_intent("Fix the authentication bug in the login module")
        assert result.mission_intent is not None, 'No mission intent returned'
        assert result.classification_confidence > 0, 'Zero confidence'
        assert result.mission_intent.primary_category is not None
    test('Intent Classifier', test_intent_classifier)

    def test_work_detector():
        workspace = os.path.join(scripts_dir, '..')
        sys.path.insert(0, workspace)
        from packages.specialist_system.work_detector import WorkDetector
        detector = WorkDetector()
        work = detector.detect_work("Build a new React component for the dashboard UI")
        assert work is not None, 'No work detected'
        assert len(work.domain) > 0 or work.description, 'Empty work object'
    test('Work Detector', test_work_detector)

    def test_chain_executor():
        workspace = os.path.join(scripts_dir, '..')
        sys.path.insert(0, workspace)
        from packages.prompt_chain_executor.executor import ChainExecutor
        executor = ChainExecutor()
        # Minimal chain: start → end
        chain = {
            "chain_id": "test_chain",
            "nodes": [
                {"id": "start", "type": "start", "label": "Start"},
                {"id": "end", "type": "end", "label": "End"},
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "end"},
            ],
            "entryPoint": "start",
        }
        result = executor.execute_chain(chain)
        assert result.get('success'), f'Chain failed: {result.get("error")}'
    test('Chain Executor', test_chain_executor)

    def test_safety_orchestrator():
        workspace = os.path.join(scripts_dir, '..')
        sys.path.insert(0, workspace)
        from packages.safety_systems.safety_orchestrator import SafetyOrchestrator
        safety = SafetyOrchestrator()
        summary = safety.get_safety_summary()
        assert isinstance(summary, dict), f'Expected dict, got {type(summary)}'
        # Request a safe operation
        op_id = safety.request_operation(
            operation_type='create_file',
            file_path='/tmp/test_aim_os_safety.txt',
            content='test content',
        )
        assert op_id is not None, 'No operation ID returned'
    test('Safety Orchestrator', test_safety_orchestrator)

    # ── Summary ──
    ok = sum(1 for r in RESULTS if r[0] == 'OK')
    fail = sum(1 for r in RESULTS if r[0] == 'FAIL')
    print(f'\n{"="*40}')
    print(f'Result: {ok}/{ok+fail} tests passed')
    if fail > 0:
        print(f'\nFailed tests:')
        for r in RESULTS:
            if r[0] == 'FAIL':
                print(f'  - {r[1]}: {r[2]}')
    print()
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
