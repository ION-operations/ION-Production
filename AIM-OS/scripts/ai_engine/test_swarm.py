"""
AIM-OS AI Engine — Swarm Operational Test

End-to-end verification of the Gemini CLI agent workforce:
    1. GeminiCLIProvider availability
    2. Single-agent headless prompt
    3. GenomeLoader + system prompt assembly
    4. SwarmOrchestrator 2-worker task (if single-agent passes)

Usage:
    python scripts/ai_engine/test_swarm.py
"""

import os
import sys
import time
import json

# Ensure engine path is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(SCRIPT_DIR, '..', '..')
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, WORKSPACE)


def test_provider_availability():
    """Test 1: Can we find and instantiate the Gemini CLI provider?"""
    print("\n" + "=" * 60)
    print("TEST 1: GeminiCLIProvider Availability")
    print("=" * 60)

    from providers.gemini_cli_provider import GeminiCLIProvider

    provider = GeminiCLIProvider(working_directory=WORKSPACE)
    status = provider.check_available()

    print(f"  CLI path:  {status['cli_path']}")
    print(f"  Available: {status['available']}")
    print(f"  Version:   {status.get('version', 'unknown')}")

    assert status['available'], "Gemini CLI not found on PATH!"
    print("  ✅ PASS — Gemini CLI is available")
    return provider


def test_single_agent(provider):
    """Test 2: Can a single headless agent complete a prompt?"""
    print("\n" + "=" * 60)
    print("TEST 2: Single Agent Headless Prompt")
    print("=" * 60)

    prompt = (
        "You are a test agent. Respond ONLY with a JSON object: "
        '{"status": "alive", "agent": "gemini-cli-worker", "task": "operational_test"}'
    )

    print(f"  Prompt:  {prompt[:80]}...")
    print(f"  Timeout: 30s")
    start = time.monotonic()

    response = provider.run_headless(
        prompt=prompt,
        timeout=30,
    )

    elapsed = (time.monotonic() - start) * 1000

    print(f"  Success: {response.success}")
    print(f"  Latency: {elapsed:.0f}ms")
    print(f"  Content: {response.content[:200]}")

    if response.error:
        print(f"  Error:   {response.error[:200]}")

    assert response.success, f"Headless prompt failed: {response.error}"
    print("  ✅ PASS — Single agent responded")
    return response


def test_genome_loader():
    """Test 3: Can we load genomes and assemble system prompts?"""
    print("\n" + "=" * 60)
    print("TEST 3: GenomeLoader + System Prompt Assembly")
    print("=" * 60)

    from genome_loader import GenomeLoader

    loader = GenomeLoader(workspace_root=WORKSPACE)
    status = loader.status()

    print(f"  Genome dir: {status['genome_dir']}")
    print(f"  Dir exists: {status['genome_dir_exists']}")
    print(f"  Genomes:    {len(status['available_genomes'])}")
    print(f"  Roles:      {status['builtin_roles']}")

    # Build a researcher genome
    genome = loader.build_genome(
        role='researcher',
        task='Audit the AIM-OS CMC subsystem architecture',
        instance_id='test-worker-001',
    )

    prompt = genome.to_system_prompt()
    print(f"  Tokens:     ~{genome.total_tokens}")
    print(f"  Prompt len: {len(prompt)} chars")
    print(f"  Preview:    {prompt[:150]}...")

    assert len(prompt) > 100, "System prompt too short!"
    assert 'researcher' in prompt.lower() or 'research' in prompt.lower(), "Role not present!"
    print("  ✅ PASS — Genome assembled correctly")
    return loader


def test_genome_with_agent(provider, loader):
    """Test 4: Agent with genome overlay — does role specialization work?"""
    print("\n" + "=" * 60)
    print("TEST 4: Agent with Genome Overlay")
    print("=" * 60)

    genome = loader.build_genome(
        role='auditor',
        task='Report the number of files in the scripts/ai_engine directory',
    )

    system = genome.to_system_prompt()
    prompt = (
        "List the Python files you can see in scripts/ai_engine/. "
        "Respond with a short summary: how many .py files, their names."
    )

    print(f"  Role:     auditor")
    print(f"  Task:     scripts/ai_engine directory audit")
    print(f"  Timeout:  45s")
    start = time.monotonic()

    response = provider.complete(
        prompt=prompt,
        system=system,
        timeout=45,
    )

    elapsed = (time.monotonic() - start) * 1000
    print(f"  Success:  {response.success}")
    print(f"  Latency:  {elapsed:.0f}ms")
    print(f"  Content:  {response.content[:300]}")

    if response.error:
        print(f"  Error:    {response.error[:200]}")

    assert response.success, f"Genome agent failed: {response.error}"
    print("  ✅ PASS — Genome-specialized agent responded")
    return response


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  AIM-OS Gemini CLI Workforce — Operational Test Suite   ║")
    print("╚══════════════════════════════════════════════════════════╝")

    results = {}

    # Test 1: Provider
    try:
        provider = test_provider_availability()
        results['provider'] = 'PASS'
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results['provider'] = f'FAIL: {e}'
        return results

    # Test 2: Single agent
    try:
        test_single_agent(provider)
        results['single_agent'] = 'PASS'
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results['single_agent'] = f'FAIL: {e}'

    # Test 3: Genome loader
    try:
        loader = test_genome_loader()
        results['genome_loader'] = 'PASS'
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results['genome_loader'] = f'FAIL: {e}'
        loader = None

    # Test 4: Agent with genome
    if results.get('single_agent') == 'PASS' and loader:
        try:
            test_genome_with_agent(provider, loader)
            results['genome_agent'] = 'PASS'
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results['genome_agent'] = f'FAIL: {e}'

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v == 'PASS')
    total = len(results)
    for name, result in results.items():
        icon = '✅' if result == 'PASS' else '❌'
        print(f"  {icon} {name}: {result}")
    print(f"\n  {passed}/{total} tests passed")
    print("=" * 60)

    return results


if __name__ == '__main__':
    main()
