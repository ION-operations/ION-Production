"""
AIM-OS — Team Self-Audit Mission

The ultimate test: deploy the enhanced agent workforce to audit
the very AI Engine systems that power them.

Mission: 3 agents (researcher, auditor, architect) analyze
scripts/ai_engine/ — the system that built them.

This is the team testing themselves.
"""

import os
import sys
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))

from enhanced_worker import EnhancedWorker, EnhancedResult
from atlas_agent import Atlas


def run_mission():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  AIM-OS TEAM SELF-AUDIT MISSION                        ║")
    print("║  3 agents auditing the systems that power them          ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ── Pre-flight: Atlas Big Picture ─────────────────────
    print("\n═══ PRE-FLIGHT: Atlas Indexing ═══")
    atlas = Atlas(workspace_root=WORKSPACE)
    stats = atlas.index(force=True)
    print(f"  Modules: {stats['modules']}")
    print(f"  Files:   {stats['files']}")
    print(f"  Lines:   {stats['lines']:,}")
    print(f"  Rels:    {stats['relationships']}")
    print(f"  Time:    {stats['elapsed_ms']:.0f}ms")

    # ── Mission Briefing ──────────────────────────────────
    mission = (
        "Conduct a thorough audit of the AIM-OS AI Engine located in scripts/ai_engine/. "
        "Analyze the architecture, identify strengths and weaknesses, map subsystem relationships, "
        "and assess production readiness. Focus on:\n"
        "1. The 7-layer execution pipeline (Context→Agent→Genome→VIF→LLM→Trace→Learn)\n"
        "2. The swarm orchestration system (orchestrator, worker_manager, contracts)\n"
        "3. The context engine and context pack builder\n"
        "4. The enhanced worker and Atlas integration\n"
        "Report your findings with confidence levels and specific recommendations."
    )

    print(f"\n═══ MISSION BRIEFING ═══")
    print(f"  {mission[:120]}...")

    # ── Deploy Agents ─────────────────────────────────────
    agents = [
        {
            'role': 'researcher',
            'task': (
                f"{mission}\n\n"
                "YOUR ROLE: RESEARCHER — map the complete file inventory, "
                "identify all subsystems, count lines of code per module, "
                "and document the data flow through the pipeline."
            ),
        },
        {
            'role': 'auditor',
            'task': (
                f"{mission}\n\n"
                "YOUR ROLE: AUDITOR — evaluate code quality, identify bugs "
                "or incomplete implementations, check error handling and "
                "edge cases, assess test coverage, and flag security concerns."
            ),
        },
        {
            'role': 'architect',
            'task': (
                f"{mission}\n\n"
                "YOUR ROLE: ARCHITECT — evaluate the overall system design, "
                "identify architectural patterns and anti-patterns, assess "
                "scalability, and recommend structural improvements."
            ),
        },
    ]

    results: list = []
    total_start = time.monotonic()

    for i, agent_def in enumerate(agents):
        role = agent_def['role']
        print(f"\n{'═' * 60}")
        print(f"  DEPLOYING AGENT {i+1}/3: {role.upper()}")
        print(f"{'═' * 60}")

        worker = EnhancedWorker(
            workspace_root=WORKSPACE,
            role=role,
            timeout=120,
            enable_atlas=True,
            enable_context=True,
            enable_memory=True,
            enable_scoring=False,
            enable_comms=False,
            enable_evolution=False,
        )

        result = worker.execute(
            task=agent_def['task'],
            active_file='scripts/ai_engine/engine.py',
        )

        results.append(result)

        print(f"\n  ── {role.upper()} REPORT ──")
        print(f"  Success:  {result.success}")
        print(f"  Time:     {result.latency_ms:.0f}ms total")
        print(f"    Atlas:  context injected")
        print(f"    Ctx:    {result.context_tokens} tokens ({result.context_build_ms:.0f}ms)")
        print(f"    LLM:    {result.llm_ms:.0f}ms")
        print(f"    Genome: ~{result.genome_tokens} tokens")
        print(f"    Memory: {result.memory_items_retrieved} items")

        if result.success:
            # Print the actual analysis (first 500 chars)
            content = result.content.strip()
            print(f"\n  FINDINGS:")
            for line in content[:800].split('\n'):
                print(f"    {line}")
            if len(content) > 800:
                print(f"    ...(+{len(content) - 800} chars)")
        else:
            print(f"  ERROR: {result.error[:300]}")

    # ── Mission Summary ───────────────────────────────────
    total_time = (time.monotonic() - total_start) * 1000
    succeeded = [r for r in results if r.success]

    print(f"\n{'═' * 60}")
    print(f"  MISSION COMPLETE")
    print(f"{'═' * 60}")
    print(f"  Agents deployed:  {len(agents)}")
    print(f"  Succeeded:        {len(succeeded)}/{len(agents)}")
    print(f"  Total time:       {total_time:.0f}ms ({total_time/1000:.1f}s)")
    print(f"  Avg per agent:    {total_time/len(agents):.0f}ms")

    for r in results:
        icon = '✅' if r.success else '❌'
        print(f"  {icon} {r.role:12s} — {r.latency_ms:.0f}ms, "
              f"ctx={r.context_tokens} tokens, "
              f"output={len(r.content)} chars")

    # Save full reports to disk
    report_path = os.path.join(WORKSPACE, '.agent', 'mission_reports')
    os.makedirs(report_path, exist_ok=True)

    for r in succeeded:
        fpath = os.path.join(report_path, f'self_audit_{r.role}.md')
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(f"# Self-Audit Report: {r.role.title()}\n\n")
            f.write(f"**Worker:** {r.worker_id}\n")
            f.write(f"**Time:** {r.latency_ms:.0f}ms\n")
            f.write(f"**Context:** {r.context_tokens} tokens\n")
            f.write(f"**Genome:** ~{r.genome_tokens} tokens\n\n")
            f.write(f"---\n\n{r.content}\n")
        print(f"  📄 Report saved: {fpath}")

    # Save mission summary
    summary_path = os.path.join(report_path, 'mission_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'mission': 'self_audit',
            'timestamp': time.time(),
            'agents': len(agents),
            'succeeded': len(succeeded),
            'total_time_ms': total_time,
            'results': [
                {
                    'role': r.role,
                    'worker_id': r.worker_id,
                    'success': r.success,
                    'latency_ms': r.latency_ms,
                    'context_tokens': r.context_tokens,
                    'genome_tokens': r.genome_tokens,
                    'output_length': len(r.content),
                }
                for r in results
            ],
        }, f, indent=2)
    print(f"  📊 Summary: {summary_path}")

    return results


if __name__ == '__main__':
    run_mission()
