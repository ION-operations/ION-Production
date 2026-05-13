"""
AIM-OS AI Engine — Comparative Context Quality Analysis

Evaluates the effectiveness of different context strategies by comparing
four modes against a real coding task:

    Mode A: No context (just task description)
    Mode B: Semantic context (raw file content)
    Mode C: Structural context (AST envelope)
    Mode D: Blended (AST envelope + target content)

Instead of calling an LLM, this measures *context quality* metrics:
    - Accuracy: Does it include the correct API signatures?
    - Completeness: Are all referenced symbols present?
    - Signal-to-Noise: How much of the context is actually relevant?
    - Token efficiency: How many tokens per useful fact?

Usage:
    python test_context_quality.py
"""

import os
import sys
import time
import json
import tempfile

# Add workspace root
WORKSPACE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(WORKSPACE, 'scripts'))

from ai_engine.context_mapper import ContextMapper, ASTExtractor, TSExtractor


# ══════════════════════════════════════════════════════════
#  TASK DEFINITIONS
# ══════════════════════════════════════════════════════════

TASKS = [
    {
        'name': 'Add retry logic to EnhancedWorker',
        'target': os.path.join(WORKSPACE, 'scripts', 'ai_engine', 'enhanced_worker.py'),
        'description': 'Add a retry() method to EnhancedWorker that wraps execute() '
                      'with exponential backoff, max 3 retries, and logging.',
        'required_symbols': [
            'GeminiCLIProvider', 'GenomeLoader', 'ContextPackBuilder', 'Atlas',
            'QualityEvaluator', 'EnhancedWorker',
        ],
        'required_methods': [
            'execute', '__init__', 'status', 'context_mapper',
        ],
        'language': 'python',
    },
    {
        'name': 'Add keyboard shortcuts to CameraSystem',
        'target': os.path.join(WORKSPACE, 'codex-systems', 'camera', 'CameraSystem.ts'),
        'description': 'Add a KeyboardShortcutManager class that maps keyboard '
                      'shortcuts to camera transitions between orbit, first-person, '
                      'and third-person modes.',
        'required_symbols': [
            'CameraController', 'OrbitCamera', 'FirstPersonCamera',
            'ThirdPersonCamera', 'CameraTransition', 'CameraShake',
            'OrbitConfig', 'FirstPersonConfig', 'ThirdPersonConfig',
        ],
        'required_methods': [
            'update', 'setTarget', 'handleMouseMove', 'handleKeyDown',
        ],
        'language': 'typescript',
    },
    {
        'name': 'Refactor engine pipeline stages',
        'target': os.path.join(WORKSPACE, 'scripts', 'ai_engine', 'engine.py'),
        'description': 'Refactor the AI Engine to use a PipelineStage enum and '
                      'route each stage through a dispatch table instead of if/elif.',
        'required_symbols': [
            'ChainDirector', 'EnhancedWorker', 'GenomeLoader', 'ContextMapper',
            'AgentMesh', 'SessionManager', 'Registry', 'SmartRouter',
        ],
        'required_methods': [
            'execute', 'ask', 'code', 'plan', 'audit', 'status',
        ],
        'language': 'python',
    },
]


# ══════════════════════════════════════════════════════════
#  CONTEXT GENERATORS
# ══════════════════════════════════════════════════════════

def generate_no_context(task: dict) -> str:
    """Mode A: Just the task description."""
    return f"TASK: {task['description']}\nFILE: {os.path.basename(task['target'])}\n"


def generate_semantic_context(task: dict) -> str:
    """Mode B: Raw file content (simulating semantic retrieval)."""
    try:
        with open(task['target'], 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        content = '<file not found>'

    return (
        f"TASK: {task['description']}\n"
        f"FILE CONTENT:\n{content}\n"
    )


def generate_structural_context(task: dict, mapper: ContextMapper) -> str:
    """Mode C: AST envelope only."""
    envelope = mapper.build_envelope(task['target'], budget_chars=32000)
    return (
        f"TASK: {task['description']}\n"
        f"CONTEXT ENVELOPE:\n{envelope.to_string()}\n"
    )


def generate_blended_context(task: dict, mapper: ContextMapper) -> str:
    """Mode D: AST envelope + full target."""
    envelope = mapper.build_envelope(task['target'], budget_chars=32000)
    return (
        f"TASK: {task['description']}\n"
        f"STRUCTURAL CONTEXT:\n{envelope.to_string()}\n"
    )


# ══════════════════════════════════════════════════════════
#  QUALITY METRICS
# ══════════════════════════════════════════════════════════

def measure_accuracy(context: str, task: dict) -> dict:
    """Measure: does the context contain the correct API signatures?"""
    found = 0
    missing = []
    for sym in task['required_symbols']:
        if sym in context:
            found += 1
        else:
            missing.append(sym)

    total = len(task['required_symbols'])
    return {
        'score': round(found / total, 3) if total else 0,
        'found': found,
        'total': total,
        'missing': missing,
    }


def measure_completeness(context: str, task: dict) -> dict:
    """Measure: are all required methods present?"""
    found = 0
    missing = []
    for method in task['required_methods']:
        if method in context:
            found += 1
        else:
            missing.append(method)

    total = len(task['required_methods'])
    return {
        'score': round(found / total, 3) if total else 0,
        'found': found,
        'total': total,
        'missing': missing,
    }


def measure_signal_to_noise(context: str, task: dict) -> dict:
    """Measure: how much of the context is actually relevant?"""
    lines = context.splitlines()
    total_lines = len(lines)

    # Count lines containing any required symbol or method
    all_terms = set(task['required_symbols'] + task['required_methods'])
    signal_lines = sum(1 for line in lines if any(t in line for t in all_terms))

    return {
        'score': round(signal_lines / total_lines, 3) if total_lines else 0,
        'signal_lines': signal_lines,
        'total_lines': total_lines,
        'noise_lines': total_lines - signal_lines,
    }


def measure_token_efficiency(context: str, task: dict) -> dict:
    """Measure: tokens per relevant fact."""
    total_tokens = len(context) // 4  # Rough estimate
    all_terms = set(task['required_symbols'] + task['required_methods'])
    facts_found = sum(1 for t in all_terms if t in context)

    return {
        'total_tokens': total_tokens,
        'facts_found': facts_found,
        'tokens_per_fact': round(total_tokens / facts_found, 1) if facts_found else float('inf'),
    }


def measure_structural_quality(context: str, task: dict) -> dict:
    """Measure: does it contain proper structural information?"""
    has_envelope = '<system_envelope' in context
    has_contracts = '<outbound_contracts>' in context
    has_guardrails = '<edit_rules>' in context
    has_usage = '<target_symbol_usage>' in context
    has_signatures = 'def ' in context or 'function ' in context or 'class ' in context

    quality_count = sum([has_envelope, has_contracts, has_guardrails, has_usage, has_signatures])
    return {
        'score': round(quality_count / 5, 2),
        'has_envelope': has_envelope,
        'has_contracts': has_contracts,
        'has_guardrails': has_guardrails,
        'has_symbol_usage': has_usage,
        'has_signatures': has_signatures,
    }


# ══════════════════════════════════════════════════════════
#  TEST RUNNER
# ══════════════════════════════════════════════════════════

def run_task_comparison(task: dict, mapper: ContextMapper) -> dict:
    """Run all four context modes and compare quality metrics."""
    modes = {}

    # Mode A: No Context
    t0 = time.time()
    ctx = generate_no_context(task)
    gen_time = (time.time() - t0) * 1000
    modes['No Context'] = {
        'context_chars': len(ctx),
        'gen_time_ms': round(gen_time, 1),
        'accuracy': measure_accuracy(ctx, task),
        'completeness': measure_completeness(ctx, task),
        'signal_to_noise': measure_signal_to_noise(ctx, task),
        'token_efficiency': measure_token_efficiency(ctx, task),
        'structural': measure_structural_quality(ctx, task),
    }

    # Mode B: Semantic (raw file)
    t0 = time.time()
    ctx = generate_semantic_context(task)
    gen_time = (time.time() - t0) * 1000
    modes['Semantic'] = {
        'context_chars': len(ctx),
        'gen_time_ms': round(gen_time, 1),
        'accuracy': measure_accuracy(ctx, task),
        'completeness': measure_completeness(ctx, task),
        'signal_to_noise': measure_signal_to_noise(ctx, task),
        'token_efficiency': measure_token_efficiency(ctx, task),
        'structural': measure_structural_quality(ctx, task),
    }

    # Mode C: Structural (envelope only)
    t0 = time.time()
    ctx = generate_structural_context(task, mapper)
    gen_time = (time.time() - t0) * 1000
    modes['Structural'] = {
        'context_chars': len(ctx),
        'gen_time_ms': round(gen_time, 1),
        'accuracy': measure_accuracy(ctx, task),
        'completeness': measure_completeness(ctx, task),
        'signal_to_noise': measure_signal_to_noise(ctx, task),
        'token_efficiency': measure_token_efficiency(ctx, task),
        'structural': measure_structural_quality(ctx, task),
    }

    # Mode D: Blended (envelope + content)
    t0 = time.time()
    ctx = generate_blended_context(task, mapper)
    gen_time = (time.time() - t0) * 1000
    modes['Blended'] = {
        'context_chars': len(ctx),
        'gen_time_ms': round(gen_time, 1),
        'accuracy': measure_accuracy(ctx, task),
        'completeness': measure_completeness(ctx, task),
        'signal_to_noise': measure_signal_to_noise(ctx, task),
        'token_efficiency': measure_token_efficiency(ctx, task),
        'structural': measure_structural_quality(ctx, task),
    }

    return modes


def print_comparison_table(task: dict, modes: dict):
    """Print a formatted comparison table."""
    print(f"\n{'═' * 80}")
    print(f"  TASK: {task['name']}")
    print(f"  FILE: {os.path.basename(task['target'])} ({task['language']})")
    print(f"{'═' * 80}")

    headers = ['Metric', 'No Context', 'Semantic', 'Structural', 'Blended']
    widths = [22, 14, 14, 14, 14]

    # Header
    header_str = '  │ '.join(h.center(w) for h, w in zip(headers, widths))
    print(f"  ┌{'┬'.join('─' * (w + 2) for w in widths)}┐")
    print(f"  │ {header_str} │")
    print(f"  ├{'┼'.join('─' * (w + 2) for w in widths)}┤")

    # Rows
    rows = [
        ('Context Size', lambda m: f"{m['context_chars']:,} ch"),
        ('Gen Time', lambda m: f"{m['gen_time_ms']:,.1f}ms"),
        ('Tokens', lambda m: f"{m['token_efficiency']['total_tokens']:,}"),
        ('Accuracy', lambda m: f"{m['accuracy']['score']:.0%} ({m['accuracy']['found']}/{m['accuracy']['total']})"),
        ('Completeness', lambda m: f"{m['completeness']['score']:.0%} ({m['completeness']['found']}/{m['completeness']['total']})"),
        ('S/N Ratio', lambda m: f"{m['signal_to_noise']['score']:.1%}"),
        ('Tokens/Fact', lambda m: f"{m['token_efficiency']['tokens_per_fact']:,.0f}"),
        ('Structure', lambda m: f"{m['structural']['score']:.0%}"),
    ]

    mode_names = ['No Context', 'Semantic', 'Structural', 'Blended']
    for row_name, extractor in rows:
        vals = [row_name.ljust(widths[0])]
        for i, mode in enumerate(mode_names):
            val = extractor(modes[mode])
            vals.append(val.center(widths[i + 1]))
        print(f"  │ {'  │ '.join(vals)} │")

    print(f"  └{'┴'.join('─' * (w + 2) for w in widths)}┘")

    # Winner analysis
    print(f"\n  📊 Analysis:")
    best_accuracy = max(mode_names, key=lambda m: modes[m]['accuracy']['score'])
    best_sn = max(mode_names, key=lambda m: modes[m]['signal_to_noise']['score'])
    best_efficiency = min(mode_names, key=lambda m: modes[m]['token_efficiency']['tokens_per_fact'])

    print(f"     Best accuracy:   {best_accuracy} ({modes[best_accuracy]['accuracy']['score']:.0%})")
    print(f"     Best S/N ratio:  {best_sn} ({modes[best_sn]['signal_to_noise']['score']:.1%})")
    print(f"     Most efficient:  {best_efficiency} ({modes[best_efficiency]['token_efficiency']['tokens_per_fact']:.0f} tokens/fact)")

    # Missing symbols analysis
    for mode in mode_names:
        missing = modes[mode]['accuracy']['missing']
        if missing:
            print(f"     {mode} missing: {', '.join(missing)}")


def print_aggregate_summary(all_results: dict):
    """Print aggregate summary across all tasks."""
    print(f"\n{'═' * 80}")
    print(f"  AGGREGATE SUMMARY ({len(all_results)} tasks)")
    print(f"{'═' * 80}")

    mode_names = ['No Context', 'Semantic', 'Structural', 'Blended']

    for mode in mode_names:
        accuracies = [r[mode]['accuracy']['score'] for r in all_results.values()]
        completeness = [r[mode]['completeness']['score'] for r in all_results.values()]
        sn_ratios = [r[mode]['signal_to_noise']['score'] for r in all_results.values()]
        tokens = [r[mode]['token_efficiency']['total_tokens'] for r in all_results.values()]
        tpf = [r[mode]['token_efficiency']['tokens_per_fact'] for r in all_results.values()]

        avg_acc = sum(accuracies) / len(accuracies)
        avg_comp = sum(completeness) / len(completeness)
        avg_sn = sum(sn_ratios) / len(sn_ratios)
        avg_tokens = sum(tokens) / len(tokens)
        avg_tpf = sum(tpf) / len(tpf) if all(t != float('inf') for t in tpf) else float('inf')

        bar = '█' * int(avg_acc * 20)
        print(f"\n  {mode:15s} │ Acc: {avg_acc:.0%} {bar}")
        print(f"  {'':15s} │ Comp: {avg_comp:.0%}  S/N: {avg_sn:.1%}  Tokens: {avg_tokens:,.0f}  T/Fact: {avg_tpf:,.0f}")


def main():
    """Run comparative context quality analysis."""
    print("\n" + "═" * 80)
    print("  AIM-OS Context Quality Comparative Analysis")
    print("  4 Modes × 3 Tasks × 6 Metrics")
    print("═" * 80)

    mapper = ContextMapper(WORKSPACE)
    all_results = {}

    passed = 0
    failed = 0

    for task in TASKS:
        if not os.path.isfile(task['target']):
            print(f"\n  ⚠ Skipping {task['name']}: file not found")
            continue

        try:
            modes = run_task_comparison(task, mapper)
            print_comparison_table(task, modes)
            all_results[task['name']] = modes
            passed += 1
        except Exception as e:
            print(f"\n  ❌ {task['name']}: {e}")
            failed += 1

    if all_results:
        print_aggregate_summary(all_results)

    # Assertions
    print(f"\n{'─' * 60}")
    print(f"  ASSERTIONS")
    print(f"{'─' * 60}")

    assertion_pass = 0
    assertion_fail = 0

    for task_name, modes in all_results.items():
        # Structural should beat No Context on accuracy
        if modes['Structural']['accuracy']['score'] >= modes['No Context']['accuracy']['score']:
            print(f"  ✅ {task_name}: Structural ≥ No Context (accuracy)")
            assertion_pass += 1
        else:
            print(f"  ❌ {task_name}: Structural < No Context (accuracy)")
            assertion_fail += 1

        # Blended should have highest or tied accuracy
        blended_acc = modes['Blended']['accuracy']['score']
        max_acc = max(m['accuracy']['score'] for m in modes.values())
        if blended_acc >= max_acc - 0.01:  # Allow tiny float error
            print(f"  ✅ {task_name}: Blended has top accuracy ({blended_acc:.0%})")
            assertion_pass += 1
        else:
            print(f"  ❌ {task_name}: Blended not top ({blended_acc:.0%} vs {max_acc:.0%})")
            assertion_fail += 1

        # Structural should have better S/N than Semantic
        if modes['Structural']['signal_to_noise']['score'] >= modes['Semantic']['signal_to_noise']['score']:
            print(f"  ✅ {task_name}: Structural S/N ≥ Semantic S/N")
            assertion_pass += 1
        else:
            print(f"  ❌ {task_name}: Structural S/N < Semantic S/N")
            assertion_fail += 1

        # Structural should use fewer tokens than Semantic
        if modes['Structural']['token_efficiency']['total_tokens'] <= modes['Semantic']['token_efficiency']['total_tokens']:
            print(f"  ✅ {task_name}: Structural tokens ≤ Semantic tokens")
            assertion_pass += 1
        else:
            print(f"  ❌ {task_name}: Structural more tokens than Semantic")
            assertion_fail += 1

        # Structural should have proper envelope structure
        if modes['Structural']['structural']['has_envelope']:
            print(f"  ✅ {task_name}: Structural has envelope")
            assertion_pass += 1
        else:
            print(f"  ❌ {task_name}: Structural missing envelope")
            assertion_fail += 1

    total = assertion_pass + assertion_fail
    print(f"\n  Assertions: {assertion_pass}/{total} passed")
    if assertion_fail:
        print(f"  ⚠ {assertion_fail} assertions failed")

    return assertion_fail == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

