#!/usr/bin/env python3
"""
AIM-OS AI Engine — Sandbox Audit CLI
=====================================

Run sandbox audits from the command line.

Usage:
    # Package audit
    python scripts/ai_engine/sandbox/run_sandbox_audit.py --type package --target safety_systems

    # Ability audit
    python scripts/ai_engine/sandbox/run_sandbox_audit.py --type ability --target intent_classifier

    # Codebase scan
    python scripts/ai_engine/sandbox/run_sandbox_audit.py --type codebase --target packages --focus health

    # Custom prompt
    python scripts/ai_engine/sandbox/run_sandbox_audit.py --prompt "Analyze the router package and find optimization opportunities"
"""

import sys
import os
import argparse
import json

# Ensure paths
SANDBOX_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(os.path.dirname(SANDBOX_DIR))
AIMOS_ROOT = os.path.dirname(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if AIMOS_ROOT not in sys.path:
    sys.path.insert(0, AIMOS_ROOT)


def main():
    parser = argparse.ArgumentParser(
        description='AIM-OS Sandbox Audit Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --type package --target safety_systems
  %(prog)s --type ability --target intent_classifier
  %(prog)s --type codebase --target packages --focus health
  %(prog)s --prompt "Analyze the router package"
  %(prog)s --type package --target router --timeout 600
        """,
    )
    parser.add_argument('--type', choices=['package', 'ability', 'codebase', 'custom'],
                        default='custom', help='Audit type')
    parser.add_argument('--target', default='', help='Target to audit (package name, capability, etc.)')
    parser.add_argument('--focus', default='health', help='Focus area for codebase scans')
    parser.add_argument('--prompt', default='', help='Custom prompt (for --type custom)')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    parser.add_argument('--model', default='', help='Model override')
    parser.add_argument('--no-clean', action='store_true', help='Keep previous workspace files')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')

    args = parser.parse_args()

    from ai_engine.sandbox.sandbox_runner import SandboxRunner
    from ai_engine.sandbox.sandbox_config import SandboxConfig
    from ai_engine.sandbox import audit_tasks

    # Build config
    config = SandboxConfig(
        timeout_seconds=args.timeout,
        model=args.model,
    )

    runner = SandboxRunner(config=config)

    # Build task
    if args.type == 'package':
        if not args.target:
            print("Error: --target required for package audit")
            return 1
        task = audit_tasks.package_audit(args.target)
    elif args.type == 'ability':
        if not args.target:
            print("Error: --target required for ability audit")
            return 1
        task = audit_tasks.ability_audit(args.target)
    elif args.type == 'codebase':
        task = audit_tasks.codebase_scan(
            scope=args.target or 'packages',
            focus=args.focus,
        )
    elif args.type == 'custom':
        if not args.prompt:
            print("Error: --prompt required for custom audit")
            return 1
        from ai_engine.sandbox.audit_tasks import AuditTask, AuditType
        task = AuditTask(
            task_id='custom_audit',
            audit_type=AuditType.CODEBASE_SCAN,
            target=args.target or 'custom',
            description=args.prompt,
            expected_outputs=["Write findings to workspace"],
        )
    else:
        print(f"Unknown type: {args.type}")
        return 1

    # Run audit
    print(f"\n🔬 Starting sandbox audit...")
    print(f"   Type: {args.type}")
    print(f"   Target: {task.target}")
    print(f"   Timeout: {args.timeout}s\n")

    result = runner.run_audit(task, clean_workspace=not args.no_clean)

    # Output
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(f"\n✅ Audit complete. Reports saved to: {config.reports_dir}")
            if result.files_created:
                print(f"   Workspace files: {config.workspace_dir}")
        else:
            print(f"\n❌ Audit failed: {result.error}")

    return 0 if result.success else 1


if __name__ == '__main__':
    sys.exit(main())
