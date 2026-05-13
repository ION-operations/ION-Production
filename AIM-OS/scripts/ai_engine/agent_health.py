#!/usr/bin/env python3
"""
AIM-OS AI Engine — Agent Health Monitor

CLI-runnable health check that aggregates status from all agent subsystems.
Produces a structured JSON report + human-readable summary.

Checks:
    1. GeminiCLIProvider availability
    2. GenomeLoader status & genome file integrity
    3. AgentRegistry completeness
    4. Strategy plugin availability (5 strategies)
    5. Safety gates (VIF)
    6. Swarm contracts
    7. Core data files (CMC db, HHNI index, Atlas store)
    8. Engine facade subsystem count

Usage:
    python scripts/ai_engine/agent_health.py
    python scripts/ai_engine/agent_health.py --json
"""

import sys
import os
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE = os.path.dirname(SCRIPTS_DIR)

for p in [WORKSPACE, SCRIPTS_DIR, SCRIPT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ── Check Functions ───────────────────────────────────────

def check_provider():
    """Check GeminiCLIProvider availability."""
    try:
        from providers.gemini_cli_provider import GeminiCLIProvider
        provider = GeminiCLIProvider(working_directory=WORKSPACE)
        status = provider.check_available()
        return {
            'name': 'GeminiCLIProvider',
            'status': 'pass' if status['available'] else 'warn',
            'details': {
                'available': status['available'],
                'cli_path': status.get('cli_path', 'unknown'),
                'version': status.get('version', 'unknown'),
            },
            'message': 'CLI available' if status['available'] else 'CLI not found — headless mode disabled',
        }
    except Exception as e:
        return {
            'name': 'GeminiCLIProvider',
            'status': 'fail',
            'details': {},
            'message': f'Import/init failed: {e}',
        }


def check_codex_provider():
    """Check CodexCLIProvider availability."""
    try:
        from providers.codex_cli_provider import CodexCLIProvider
        provider = CodexCLIProvider(working_directory=WORKSPACE)
        status = provider.check_available()
        return {
            'name': 'CodexCLIProvider',
            'status': 'pass' if status['available'] else 'warn',
            'details': {
                'available': status['available'],
                'cli_path': status.get('cli_path', 'unknown'),
                'version': status.get('version', 'unknown'),
            },
            'message': f'CLI available ({status.get("version", "?")})' if status['available'] else 'CLI not found',
        }
    except Exception as e:
        return {
            'name': 'CodexCLIProvider',
            'status': 'fail',
            'details': {},
            'message': f'Import/init failed: {e}',
        }


def check_genomes():
    """Check GenomeLoader and genome file integrity."""
    try:
        from ai_engine.genome_loader import GenomeLoader
        loader = GenomeLoader(workspace_root=WORKSPACE)
        status = loader.status()

        genome_dir = os.path.join(WORKSPACE, '.agent', 'genomes')
        genome_files = []
        if os.path.exists(genome_dir):
            genome_files = [f for f in os.listdir(genome_dir) if f.endswith('.genome.md')]

        roles = status.get('builtin_roles', [])
        loadable = 0
        for role in roles:
            try:
                g = loader.build_genome(role=role, task='health check')
                if g and g.to_system_prompt():
                    loadable += 1
            except Exception:
                pass

        ok = loadable == len(roles) and len(roles) >= 3
        return {
            'name': 'Genome System',
            'status': 'pass' if ok else 'warn',
            'details': {
                'genome_files': len(genome_files),
                'builtin_roles': roles,
                'loadable_roles': loadable,
                'genome_dir_exists': os.path.exists(genome_dir),
            },
            'message': f'{loadable}/{len(roles)} roles loadable, {len(genome_files)} genome files',
        }
    except Exception as e:
        return {
            'name': 'Genome System',
            'status': 'fail',
            'details': {},
            'message': f'GenomeLoader failed: {e}',
        }


def check_registry():
    """Check AgentRegistry."""
    try:
        from ai_engine.registry import AgentRegistry
        reg = AgentRegistry()
        status = reg.status()
        total = status.get('total_agents', 0)
        ok = total >= 5
        return {
            'name': 'Agent Registry',
            'status': 'pass' if ok else 'warn',
            'details': status,
            'message': f'{total} agents registered',
        }
    except Exception as e:
        return {
            'name': 'Agent Registry',
            'status': 'fail',
            'details': {},
            'message': f'Registry failed: {e}',
        }


def check_strategies():
    """Check all 5 strategy plugins load."""
    try:
        sys.path.insert(0, os.path.join(SCRIPT_DIR, 'agent_loop'))
        from agent_loop.strategies import list_strategies, get_strategy

        available = list_strategies()
        expected = {'llm_research', 'pack_builder', 'hhni_direct', 'hybrid', 'atlas'}
        found = set(available.keys())
        missing = expected - found

        # Try loading each
        loadable = []
        errors = []
        for name in found:
            try:
                s = get_strategy(name, workspace_root=WORKSPACE)
                loadable.append(name)
            except Exception as e:
                errors.append(f'{name}: {e}')

        ok = not missing and len(errors) == 0
        return {
            'name': 'Context Strategies',
            'status': 'pass' if ok else ('warn' if not missing else 'warn'),
            'details': {
                'available': list(found),
                'missing': list(missing),
                'loadable': loadable,
                'errors': errors,
            },
            'message': f'{len(loadable)}/{len(found)} loadable'
                       + (f', missing: {missing}' if missing else ''),
        }
    except Exception as e:
        return {
            'name': 'Context Strategies',
            'status': 'fail',
            'details': {},
            'message': f'Strategy system failed: {e}',
        }


def check_safety():
    """Check VIF safety gates."""
    try:
        from ai_engine.safety.vif_gates import VIFGate, GateVerdict
        gate = VIFGate()
        # Quick functional test
        r1 = gate.check('file:read', confidence=0.9)
        r2 = gate.check('file:delete', confidence=0.1)
        r3 = gate.check('mcp:mutate_orchestration', confidence=0.9, has_human_token=False)

        working = r1.passed and not r2.passed and r3.verdict == GateVerdict.ESCALATE
        return {
            'name': 'VIF Safety Gates',
            'status': 'pass' if working else 'fail',
            'details': {
                'high_conf_read_passes': r1.passed,
                'low_conf_delete_blocks': not r2.passed,
                'red_zone_escalates': r3.verdict == GateVerdict.ESCALATE,
            },
            'message': 'All gate checks pass' if working else 'Gate logic mismatch',
        }
    except Exception as e:
        return {
            'name': 'VIF Safety Gates',
            'status': 'fail',
            'details': {},
            'message': f'VIF gates failed: {e}',
        }


def check_swarm():
    """Check swarm contracts and orchestrator."""
    try:
        from ai_engine.swarm.contracts import ROLE_CAPABILITIES, WorkerRole, RED_ZONE_CAPABILITIES
        roles = len(ROLE_CAPABILITIES)
        red_zones = len(RED_ZONE_CAPABILITIES)
        ok = roles >= 3 and red_zones > 0
        return {
            'name': 'Swarm Contracts',
            'status': 'pass' if ok else 'warn',
            'details': {
                'roles_defined': roles,
                'red_zone_capabilities': red_zones,
                'role_names': [r.value if hasattr(r, 'value') else str(r) for r in ROLE_CAPABILITIES.keys()],
            },
            'message': f'{roles} roles, {red_zones} red zone caps',
        }
    except Exception as e:
        return {
            'name': 'Swarm Contracts',
            'status': 'fail',
            'details': {},
            'message': f'Swarm contracts failed: {e}',
        }


def check_core_data():
    """Check core data files exist."""
    files_to_check = {
        'CMC Database': os.path.join(WORKSPACE, 'mcp_memory', 'cmc_store.db'),
        'Atlas Store': os.path.join(WORKSPACE, '.agent', 'atlas_store.json'),
        'MCP Server': os.path.join(WORKSPACE, 'lucid_mcp_server.py'),
        'Genome Protocol': os.path.join(WORKSPACE, '.agent', 'genomes', 'GENOME_PROTOCOL.md'),
    }

    results = {}
    for name, path in files_to_check.items():
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        results[name] = {'exists': exists, 'size_bytes': size}

    all_exist = all(r['exists'] for r in results.values())
    found = sum(1 for r in results.values() if r['exists'])

    return {
        'name': 'Core Data Files',
        'status': 'pass' if all_exist else 'warn',
        'details': results,
        'message': f'{found}/{len(files_to_check)} files present',
    }


def check_engine():
    """Check engine facade initialization."""
    try:
        from ai_engine.engine import AIEngine, EngineConfig
        config = EngineConfig(workspace_root=WORKSPACE)
        engine = AIEngine(config=config)

        subsystem_props = [
            'registry', 'genome_loader', 'sessions', 'traces',
            'learner', 'vif', 'context_builder', 'tool_advisor',
        ]
        available = [p for p in subsystem_props if hasattr(engine, p)]

        ok = len(available) >= 6
        return {
            'name': 'Engine Facade',
            'status': 'pass' if ok else 'warn',
            'details': {
                'subsystems_available': available,
                'subsystems_checked': len(subsystem_props),
                'subsystems_found': len(available),
            },
            'message': f'{len(available)}/{len(subsystem_props)} subsystem properties available',
        }
    except Exception as e:
        return {
            'name': 'Engine Facade',
            'status': 'fail',
            'details': {},
            'message': f'Engine init failed: {e}',
        }


# ── Main ──────────────────────────────────────────────────

def run_health_check():
    """Run all health checks and return structured report."""
    start = time.time()

    checks = [
        check_provider,
        check_codex_provider,
        check_genomes,
        check_registry,
        check_strategies,
        check_safety,
        check_swarm,
        check_core_data,
        check_engine,
    ]

    results = []
    for fn in checks:
        try:
            results.append(fn())
        except Exception as e:
            results.append({
                'name': fn.__name__,
                'status': 'fail',
                'details': {},
                'message': f'Unexpected error: {e}',
            })

    elapsed_ms = (time.time() - start) * 1000

    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'elapsed_ms': round(elapsed_ms, 1),
        'checks': results,
        'summary': {
            'total': len(results),
            'pass': sum(1 for r in results if r['status'] == 'pass'),
            'warn': sum(1 for r in results if r['status'] == 'warn'),
            'fail': sum(1 for r in results if r['status'] == 'fail'),
        },
    }

    return report


def print_report(report):
    """Print a human-readable health report."""
    icons = {'pass': '✅', 'warn': '⚠️', 'fail': '❌'}

    print('╔════════════════════════════════════════════════════════════╗')
    print('║   AIM-OS Agent Workforce — Health Monitor                ║')
    print('╚════════════════════════════════════════════════════════════╝')
    print()

    for check in report['checks']:
        icon = icons.get(check['status'], '?')
        print(f'  {icon} {check["name"]:.<40} {check["message"]}')

    s = report['summary']
    print(f'\n{"═" * 60}')
    print(f'  {s["pass"]} pass, {s["warn"]} warn, {s["fail"]} fail  '
          f'({report["elapsed_ms"]:.0f}ms)')
    print(f'{"═" * 60}')


def main():
    report = run_health_check()

    if '--json' in sys.argv:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    # Exit code: 0 if no failures, 1 if any failures
    return 0 if report['summary']['fail'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
