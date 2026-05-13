"""
AIM-OS AI Engine — Context Lab CLI Runner

CLI entry point for the Context Lab — run 3-phase loops, baselines,
tournaments, comparisons, and strategy evolution tests.

Usage:
    # Standard 3-phase loop
    python scripts/ai_engine/agent_loop/runner.py --task "Audit the registry"

    # Baseline (single agent) for comparison
    python scripts/ai_engine/agent_loop/runner.py --task "..." --baseline

    # Context strategy tournament (head-to-head quality scoring)
    python scripts/ai_engine/agent_loop/runner.py --task "..." --tournament hhni_direct,pack_builder

    # Compare baseline vs 3-phase strategies
    python scripts/ai_engine/agent_loop/runner.py --task "..." --compare-with-baseline standard,minimal

    # Compare strategies only
    python scripts/ai_engine/agent_loop/runner.py --task "..." --compare standard,minimal,deep_research

    # Save diagnostics
    python scripts/ai_engine/agent_loop/runner.py --task "..." --verbose --save-diagnostics
"""

import argparse
import json
import logging
import os
import sys
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_AI_ENGINE_DIR = os.path.dirname(_THIS_DIR)
_SCRIPTS_DIR = os.path.dirname(_AI_ENGINE_DIR)
_AIMOS_ROOT = os.path.dirname(_SCRIPTS_DIR)

for p in [_AIMOS_ROOT, _AI_ENGINE_DIR, _THIS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models import LoopConfig
from orchestrator import LoopOrchestrator
from baseline import run_baseline, compare_baseline_vs_loop


def main():
    parser = argparse.ArgumentParser(
        description='AIM-OS Context Lab CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Strategies:
  standard       MCP context + no-MCP worker + MCP closeout (default)
  deep_research  Full indexing + extended worker + full docs
  minimal        Brief summary + minimal worker + lightweight handoff
  full_mcp       MCP access in all phases (like traditional IDE agents)

Context Strategies (for --tournament):
  hhni_direct    HHNI semantic retrieval + CMC atoms (fast, no LLM)
  pack_builder   ContextPackBuilder 4-stage pipeline
  llm_research   LLM analyzes task via Gemini CLI (original default)
  hybrid         Multi-source fusion with deduplication

Modes:
  (default)               Run 3-phase loop with --strategy
  --baseline              Run single-agent baseline only
  --tournament            Run context strategy tournament (head-to-head)
  --compare               Compare multiple 3-phase strategies
  --compare-with-baseline Compare strategies against single-agent baseline

Examples:
  %(prog)s --task "Audit the safety_systems package" --strategy standard
  %(prog)s --task "Report status" --baseline
  %(prog)s --task "Review registry" --tournament hhni_direct,pack_builder
  %(prog)s --task "Review registry" --compare-with-baseline standard,minimal
  %(prog)s --task "Analyze engine" --compare standard,minimal,deep_research -i 2
        """,
    )
    parser.add_argument('--task', '-t', required=True, help='Task to execute')
    parser.add_argument('--strategy', '-s', default='standard',
                        help='Strategy for single run')
    parser.add_argument('--iterations', '-i', type=int, default=3,
                        help='Max iterations per strategy (default: 3)')
    parser.add_argument('--baseline', '-b', action='store_true',
                        help='Run single-agent baseline only')
    parser.add_argument('--compare', '-c', default='',
                        help='Compare multiple 3-phase strategies (comma-separated)')
    parser.add_argument('--compare-with-baseline', default='',
                        help='Compare strategies against baseline (comma-separated)')
    parser.add_argument('--no-mcp', action='store_true',
                        help='Disable MCP access for baseline')
    parser.add_argument('--tournament', default='',
                        help='Run context strategy tournament (comma-separated strategies)')
    parser.add_argument('--evolve', default='',
                        help='Evolution action: fork:parent:child, tournament, leaderboard, lineage, best')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose logging')
    parser.add_argument('--save-diagnostics', '-d', action='store_true',
                        help='Save diagnostics JSON')
    parser.add_argument('--workspace', '-w', default='',
                        help='Workspace root directory')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(name)s] %(message)s',
        datefmt='%H:%M:%S',
    )

    workspace = args.workspace or _AIMOS_ROOT
    all_diagnostics = []

    if args.tournament:
        # ── Context Strategy Tournament ──
        from tournament import run_tournament, save_tournament
        strategies = [s.strip() for s in args.tournament.split(',')]
        tasks = [args.task]  # Could support multiple via comma-separated
        print(f"\n🏟️  Context Strategy Tournament")
        print(f"   Task: {args.task}")
        print(f"   Strategies: {', '.join(strategies)}\n")

        result = run_tournament(
            tasks=tasks,
            strategy_names=strategies,
            workspace_root=workspace,
            verbose=args.verbose,
        )

        print("\n" + result.format_report())

        if args.save_diagnostics:
            filepath = save_tournament(result)
            print(f"\n📊 Tournament saved: {filepath}")

    elif args.evolve:
        # ── Strategy Evolution Engine ──
        from evolution import EvolutionManager
        evo = EvolutionManager()

        parts = args.evolve.split(':')
        action = parts[0]

        if action == 'fork' and len(parts) >= 3:
            parent, child = parts[1], parts[2]
            mutations = {}
            if len(parts) > 3:
                # Parse key=value mutation pairs
                for kv in parts[3].split(','):
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        try:
                            mutations[k] = int(v)
                        except ValueError:
                            mutations[k] = v

            v = evo.fork(parent, child, mutations=mutations)
            print(f"\n🧬 Forked: {parent} → {child} (gen {v.generation})")
            if mutations:
                print(f"   Mutations: {mutations}")
            print(evo.format_lineage_tree())

        elif action == 'tournament':
            tasks_list = [args.task]
            variants_list = parts[1].split(',') if len(parts) > 1 else None
            print(f"\n🏟️  Evolution Tournament")
            result = evo.tournament(tasks_list, variants_list, workspace)
            print(evo.format_leaderboard())

        elif action == 'leaderboard':
            print(evo.format_leaderboard())

        elif action == 'lineage':
            print(evo.format_lineage_tree())

        elif action == 'best':
            base = parts[1] if len(parts) > 1 else ''
            best = evo.best_variant(base)
            print(f"\n🏆 Best variant: {best or '(no results yet)'}")

        else:
            print(f"Unknown evolve action: {action}")
            print("Usage: --evolve fork:parent:child[:key=val,key=val]")
            print("       --evolve tournament[:variant1,variant2]")
            print("       --evolve leaderboard | lineage | best[:base_strategy]")

    elif args.baseline:
        # ── Baseline Only ──
        print(f"\n🎯 Running Single-Agent Baseline")
        print(f"   Task: {args.task}")
        print(f"   MCP: {'yes' if not args.no_mcp else 'no'}\n")

        result, diag = run_baseline(
            task=args.task,
            mcp_access=not args.no_mcp,
            workspace=workspace,
        )
        all_diagnostics.append(diag)
        print("\n" + result.summary())
        if result.output:
            print("── Output ──")
            print(result.output[:2000])

    elif args.compare_with_baseline:
        # ── Baseline vs 3-Phase Comparison ──
        strategies = [s.strip() for s in args.compare_with_baseline.split(',')]
        print(f"\n🔬 Baseline vs 3-Phase Comparison")
        print(f"   Task: {args.task}")
        print(f"   Strategies: {', '.join(strategies)}")
        print(f"   Iterations: {args.iterations}\n")

        # Run baseline first
        print("── Running Baseline ──")
        bl_result, bl_diag = run_baseline(
            task=args.task,
            mcp_access=not args.no_mcp,
            workspace=workspace,
        )
        all_diagnostics.append(bl_diag)
        print(f"   Baseline: {bl_result.latency_ms/1000:.1f}s quality={bl_result.quality_score:.0%}\n")

        # Run each strategy
        for strategy in strategies:
            print(f"── Running 3-Phase: {strategy} ──")
            config = LoopConfig.from_strategy(
                strategy,
                workspace_root=workspace,
                max_iterations=args.iterations,
            )
            orchestrator = LoopOrchestrator(config)
            loop_result = orchestrator.run(args.task, max_iterations=args.iterations)
            all_diagnostics.append(orchestrator.diagnostics)

            print(f"   {strategy}: {loop_result.total_time_ms/1000:.1f}s "
                  f"quality={loop_result.final_quality_score:.0%}\n")

            # Print comparison
            print(compare_baseline_vs_loop(args.task, loop_result, bl_result))
            print()

    elif args.compare:
        # ── Strategy Comparison ──
        strategies = [s.strip() for s in args.compare.split(',')]
        print(f"\n🔬 Comparing strategies: {', '.join(strategies)}")
        print(f"   Task: {args.task}")
        print(f"   Iterations: {args.iterations}\n")

        config = LoopConfig(workspace_root=workspace)
        orchestrator = LoopOrchestrator(config)
        report = orchestrator.run_comparison(
            task=args.task,
            strategies=strategies,
            max_iterations=args.iterations,
        )
        all_diagnostics.append(orchestrator.diagnostics)
        print(report)

    else:
        # ── Single 3-Phase Run ──
        config = LoopConfig.from_strategy(
            args.strategy,
            workspace_root=workspace,
            max_iterations=args.iterations,
            verbose=args.verbose,
        )

        print(f"\n🚀 Running 3-Phase Agent Loop")
        print(f"   Task: {args.task}")
        print(f"   Strategy: {args.strategy}")
        print(f"   Max iterations: {args.iterations}\n")

        orchestrator = LoopOrchestrator(config)
        result = orchestrator.run(args.task, max_iterations=args.iterations)
        all_diagnostics.append(orchestrator.diagnostics)

        print("\n" + result.summary())
        print("\n" + orchestrator.diagnostics.format_report())

        if result.final_output:
            print(f"\n── Final Output ──")
            print(result.final_output[:2000])

    # Save diagnostics
    if args.save_diagnostics and all_diagnostics:
        diag_dir = os.path.join(workspace, 'diagnostics', 'agent_loop')
        os.makedirs(diag_dir, exist_ok=True)
        for diag in all_diagnostics:
            mode = 'baseline' if args.baseline else args.strategy
            diag_path = os.path.join(
                diag_dir, f'run_{int(time.time())}_{mode}.json'
            )
            diag.save_to_file(diag_path)
            print(f"📊 Diagnostics saved: {diag_path}")


if __name__ == '__main__':
    main()
