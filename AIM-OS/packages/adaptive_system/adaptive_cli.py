#!/usr/bin/env python3
"""
Adaptive System CLI Runner

Usage (from AIM-OS root):
    python -m packages.adaptive_system.adaptive_cli run research_depth --context '{"topic":"CMC","confidence":0.3,"current_depth":"T0","evidence_count":1}'
    python -m packages.adaptive_system.adaptive_cli run test_coverage --context '{"module_name":"seg","coverage_percent":25,"has_test_file":true}'
    python -m packages.adaptive_system.adaptive_cli scan                    # Scan real codebase
    python -m packages.adaptive_system.adaptive_cli debug                   # Show tracker state
    python -m packages.adaptive_system.adaptive_cli status                  # System health
    python -m packages.adaptive_system.adaptive_cli test                    # Run all unit tests
    python -m packages.adaptive_system.adaptive_cli demo                    # Run demo scenarios

Designed for Gemini CLI integration — all output is structured, parseable, and color-coded.
"""

import argparse
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

# Force UTF-8 on Windows to handle em-dashes, unicode symbols etc.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass  # Python < 3.7 fallback

# ─────────────────────────────────────────────────────────────
# Colors for terminal output
# ─────────────────────────────────────────────────────────────

class C:
    """ANSI colors for terminal."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    
    @staticmethod
    def severity(sev: str) -> str:
        return {
            "low": f"{C.DIM}LOW{C.RESET}",
            "medium": f"{C.YELLOW}MEDIUM{C.RESET}",
            "high": f"{C.RED}HIGH{C.RESET}",
            "critical": f"{C.BOLD}{C.RED}CRITICAL{C.RESET}",
        }.get(sev, sev)
    
    @staticmethod
    def approval(approved: bool) -> str:
        return f"{C.GREEN}APPROVED{C.RESET}" if approved else f"{C.RED}GATED{C.RESET}"


# ─────────────────────────────────────────────────────────────
# System Registry
# ─────────────────────────────────────────────────────────────

SYSTEMS = {
    "research_depth":   "Research Depth Adaptor",
    "doc_depth":        "Documentation Depth Adaptor",
    "context_depth":    "Context Depth Adaptor",
    "test_coverage":    "Test Coverage Adaptor",
    "knowledge_decay":  "Knowledge Decay Detector",
    "security_posture": "Security Posture Adaptor",
    "arch_drift":       "Architectural Drift Detector",
    # Phase 5 v4 sensors
    "perf_regression":  "Performance Regression Sensor",
    "dep_health":       "Dependency Health Sensor",
    "agent_effective":  "Agent Effectiveness Sensor",
    "context_coherence":"Context Coherence Sensor",
}

DEMO_CONTEXTS = {
    "research_depth": {
        "topic": "CMC internal memory atom encoding",
        "current_depth": "T0",
        "confidence": 0.28,
        "evidence_count": 1,
    },
    "doc_depth": {
        "module_name": "adaptive_system",
        "file_path": "packages/adaptive_system/adaptive_core.py",
        "doc_exists": False,
        "parity_score": 0.0,
        "new_symbols": 12,
        "code_changes_since_doc": 8,
    },
    "context_depth": {
        "context_size_tokens": 115000,
        "max_context_tokens": 128000,
        "error_rate": 0.18,
        "confidence": 0.45,
        "working_memory_items": 35,
        "retrieval_quality": 0.55,
    },
    "test_coverage": {
        "module_name": "specialist_system",
        "coverage_percent": 42.0,
        "previous_coverage": 65.0,
        "has_test_file": True,
        "critical_module": True,
    },
    "knowledge_decay": {
        "ki_id": "aimos_core_infrastructure",
        "ki_title": "AIM-OS Core Infrastructure",
        "days_since_update": 45,
        "referenced_files": 15,
        "changed_files": 9,
        "changed_functions": 7,
        "ki_type": "implementation",
    },
    "security_posture": {
        "change_type": "new_endpoint",
        "module_name": "mcp_server",
        "new_endpoints": ["/api/execute", "/api/admin/reset"],
        "contains_auth_code": False,
    },
    "arch_drift": {
        "rule_id": "layer_bypass",
        "module_name": "api_handler",
        "file_path": "packages/api/handler.py",
        "description": "Direct SQLite query in API handler bypassing CMC service layer",
        "violation_count": 3,
    },
}


def get_storage_dir() -> Path:
    """Get the adaptive system storage directory."""
    return Path.cwd() / ".agent" / "adaptive"


def create_system(name: str, storage_dir: Optional[Path] = None):
    """Create an adaptive system by name."""
    storage = storage_dir or get_storage_dir()
    
    from .research_depth import create_research_depth_adaptor
    from .doc_depth import create_doc_depth_adaptor
    from .context_depth import create_context_depth_adaptor
    from .test_coverage import create_test_coverage_adaptor
    from .knowledge_decay import create_knowledge_decay_detector
    from .security_posture import create_security_posture_adaptor
    from .arch_drift import create_arch_drift_detector
    
    factories = {
        "research_depth": lambda: create_research_depth_adaptor(storage),
        "doc_depth": lambda: create_doc_depth_adaptor(storage),
        "context_depth": lambda: create_context_depth_adaptor(storage),
        "test_coverage": lambda: create_test_coverage_adaptor(storage, Path.cwd()),
        "knowledge_decay": lambda: create_knowledge_decay_detector(storage),
        "security_posture": lambda: create_security_posture_adaptor(storage),
        "arch_drift": lambda: create_arch_drift_detector(storage, storage / "drift_reports"),
    }
    
    factory = factories.get(name)
    if not factory:
        print(f"{C.RED}Unknown system: {name}{C.RESET}")
        print(f"Available: {', '.join(SYSTEMS.keys())}")
        sys.exit(1)
    
    return factory()


def print_header(title: str):
    """Print a formatted header."""
    width = 60
    print(f"\n{C.CYAN}{'═' * width}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {title}{C.RESET}")
    print(f"{C.CYAN}{'═' * width}{C.RESET}")


def print_result(result, system_name: str, elapsed: float):
    """Pretty-print an adaptive response."""
    if result is None:
        print(f"\n  {C.GREEN}✓ No action needed{C.RESET} — system healthy")
        print(f"  {C.DIM}Elapsed: {elapsed:.3f}s{C.RESET}")
        return
    
    print(f"\n  {C.BOLD}Signal:{C.RESET}    {result.response_type}")
    print(f"  {C.BOLD}Action:{C.RESET}    {result.description}")
    print(f"  {C.BOLD}Approved:{C.RESET}  {C.approval(result.approved)}")
    print(f"  {C.BOLD}Executed:{C.RESET}  {'Yes' if result.executed else 'No'}")
    
    if result.error:
        print(f"  {C.BOLD}Gate:{C.RESET}      {C.YELLOW}{result.error}{C.RESET}")
    
    if result.target_path:
        print(f"  {C.BOLD}Target:{C.RESET}    {result.target_path}")
    
    # Show content summary
    content = result.content
    if isinstance(content, dict):
        if "command" in content:
            print(f"  {C.BOLD}Command:{C.RESET}   {C.DIM}{content['command']}{C.RESET}")
        elif "commands" in content:
            for cmd in content["commands"]:
                print(f"  {C.BOLD}Command:{C.RESET}   {C.DIM}{cmd}{C.RESET}")
        elif "message" in content:
            print(f"  {C.BOLD}Message:{C.RESET}   {content['message']}")
    elif isinstance(content, str) and len(content) > 100:
        print(f"  {C.BOLD}Content:{C.RESET}   {content[:100]}...")
    
    print(f"  {C.DIM}Elapsed: {elapsed:.3f}s{C.RESET}")


def print_json(data: Any):
    """Print JSON for machine consumption."""
    print(json.dumps(data, indent=2, default=str))


# ─────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────

def cmd_run(args):
    """Run a single adaptive system with given context."""
    system_name = args.system
    
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            print(f"{C.RED}Invalid JSON context: {e}{C.RESET}")
            sys.exit(1)
    else:
        # Use demo context
        context = DEMO_CONTEXTS.get(system_name, {})
        print(f"{C.DIM}Using demo context (pass --context for custom){C.RESET}")
    
    print_header(f"Running {SYSTEMS.get(system_name, system_name)}")
    print(f"\n  {C.BOLD}Context:{C.RESET}")
    for k, v in context.items():
        print(f"    {k}: {C.CYAN}{v}{C.RESET}")
    
    system = create_system(system_name)
    
    start = time.time()
    try:
        result = system.process(context)
        elapsed = time.time() - start
        print_result(result, system_name, elapsed)
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n  {C.RED}ERROR: {e}{C.RESET}")
        if args.verbose:
            traceback.print_exc()
    
    if args.json:
        if result:
            print_json({
                "system": system_name,
                "response_type": result.response_type,
                "description": result.description,
                "approved": result.approved,
                "executed": result.executed,
                "content": result.content,
                "error": result.error,
                "elapsed": elapsed,
            })


def cmd_demo(args):
    """Run all adaptive systems with demo data."""
    print_header("Adaptive Nervous System -- Full Demo")
    
    results = []
    total_start = time.time()
    
    for name, title in SYSTEMS.items():
        context = DEMO_CONTEXTS.get(name, {})
        system = create_system(name)
        
        print(f"\n{C.BOLD}{'─' * 50}{C.RESET}")
        print(f"{C.MAGENTA}  [{name.upper()}]{C.RESET} {title}")
        
        start = time.time()
        try:
            result = system.process(context)
            elapsed = time.time() - start
            print_result(result, name, elapsed)
            results.append({
                "system": name,
                "triggered": result is not None,
                "approved": result.approved if result else None,
                "executed": result.executed if result else None,
                "elapsed": elapsed,
            })
        except Exception as e:
            elapsed = time.time() - start
            print(f"\n  {C.RED}ERROR: {e}{C.RESET}")
            results.append({"system": name, "error": str(e), "elapsed": elapsed})
    
    total = time.time() - total_start
    
    # Summary
    print(f"\n{C.CYAN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  DEMO SUMMARY{C.RESET}")
    print(f"{C.CYAN}{'═' * 60}{C.RESET}")
    
    triggered = sum(1 for r in results if r.get("triggered"))
    approved = sum(1 for r in results if r.get("approved"))
    errors = sum(1 for r in results if r.get("error"))
    
    print(f"\n  Systems:   {len(SYSTEMS)}")
    print(f"  Triggered: {triggered}")
    print(f"  Approved:  {C.GREEN}{approved}{C.RESET}")
    print(f"  Gated:     {C.YELLOW}{triggered - approved}{C.RESET}")
    print(f"  Errors:    {C.RED}{errors}{C.RESET}" if errors else f"  Errors:    {C.GREEN}0{C.RESET}")
    print(f"  Total:     {total:.3f}s\n")


def cmd_status(args):
    """Show system health status."""
    print_header("Adaptive Nervous System -- Status")
    
    storage = get_storage_dir()
    
    print(f"\n  {C.BOLD}Storage:{C.RESET}    {storage}")
    print(f"  {C.BOLD}Exists:{C.RESET}     {'Yes' if storage.exists() else 'No'}")
    
    # Check each tracker file
    print(f"\n  {C.BOLD}Tracker Files:{C.RESET}")
    tracker_files = {
        "research_depth": "research_depth.json",
        "doc_depth": "doc_depth.json",
        "context_depth": "context_depth.json",
        "test_coverage": "test_coverage.json",
        "knowledge_decay": "knowledge_decay.json",
        "security_posture": "security_posture.json",
        "arch_drift": "arch_drift.json",
    }
    
    for name, filename in tracker_files.items():
        path = storage / filename
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            count = sum(len(entries) for entries in data.values())
            domains = len(data)
            print(f"    {C.GREEN}●{C.RESET} {name:20s} {count:3d} entries across {domains} domains")
        else:
            print(f"    {C.DIM}○{C.RESET} {name:20s} {C.DIM}no data{C.RESET}")
    
    # Check proposals
    proposals_dir = storage / "proposals"
    if proposals_dir.exists():
        proposals = list(proposals_dir.glob("*.json"))
        print(f"\n  {C.BOLD}Pending Proposals:{C.RESET} {len(proposals)}")
        for p in proposals[:5]:
            data = json.loads(p.read_text(encoding="utf-8"))
            print(f"    {C.YELLOW}▸{C.RESET} {data.get('description', p.stem)}")
    else:
        print(f"\n  {C.BOLD}Pending Proposals:{C.RESET} 0")
    
    # Module import check
    print(f"\n  {C.BOLD}Module Imports:{C.RESET}")
    modules = [
        "packages.adaptive_system",
        "packages.adaptive_system.adaptive_core",
        "packages.adaptive_system.research_depth",
        "packages.adaptive_system.doc_depth",
        "packages.adaptive_system.context_depth",
        "packages.adaptive_system.test_coverage",
        "packages.adaptive_system.knowledge_decay",
        "packages.adaptive_system.security_posture",
        "packages.adaptive_system.arch_drift",
    ]
    for mod in modules:
        try:
            __import__(mod)
            print(f"    {C.GREEN}✓{C.RESET} {mod}")
        except ImportError as e:
            print(f"    {C.RED}✗{C.RESET} {mod}: {e}")


def cmd_debug(args):
    """Show tracker state and signal history."""
    print_header("Adaptive Nervous System -- Debug")
    
    storage = get_storage_dir()
    
    if not storage.exists():
        print(f"\n  {C.DIM}No tracker data found at {storage}{C.RESET}")
        return
    
    if args.system:
        files = [storage / f"{args.system}.json"]
    else:
        files = list(storage.glob("*.json"))
    
    for path in sorted(files):
        if not path.exists():
            continue
        
        name = path.stem
        print(f"\n  {C.BOLD}{C.MAGENTA}[{name.upper()}]{C.RESET}")
        
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"    {C.RED}Error reading: {e}{C.RESET}")
            continue
        
        # Tracker format: {version, updated_at, count, entries: [{signal: {...}, domain_key: str}]}
        entries = raw.get("entries", [])
        total = raw.get("count", len(entries))
        updated = raw.get("updated_at", "?")[:19]
        
        print(f"    {C.DIM}Updated: {updated}  Total entries: {total}{C.RESET}")
        
        if not entries:
            print(f"    {C.DIM}No signals recorded{C.RESET}")
            continue
        
        # Group entries by domain_key
        from collections import defaultdict
        groups = defaultdict(list)
        for entry in entries:
            dk = entry.get("domain_key", "unknown")
            groups[dk].append(entry)
        
        for domain, domain_entries in sorted(groups.items(), key=lambda x: -len(x[1])):
            print(f"\n    {C.CYAN}Domain:{C.RESET} {domain} ({len(domain_entries)} entries)")
            
            # Show last 3 entries per domain
            for entry in domain_entries[-3:]:
                sig = entry.get("signal", {})
                ts = sig.get("timestamp", "?")[:19]
                sev = sig.get("severity", "?")
                desc = sig.get("description", "")[:55]
                # Strip non-ASCII for Windows safety
                desc = desc.encode("ascii", "replace").decode("ascii")
                print(f"      {C.DIM}{ts}{C.RESET}  {C.severity(sev)}  {desc}")
    
    # Show proposals
    proposals_dir = storage / "proposals"
    if proposals_dir.exists():
        proposals = list(proposals_dir.glob("*.json"))
        if proposals:
            print(f"\n  {C.BOLD}{C.YELLOW}PENDING PROPOSALS ({len(proposals)}):{C.RESET}")
            for p in proposals[:10]:
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    desc = data.get("description", p.stem)
                    desc = desc.encode("ascii", "replace").decode("ascii")
                    print(f"    {C.YELLOW}>{C.RESET} [{data.get('required_approval', '?')}] {desc}")
                    print(f"      {C.DIM}File: {p.name}{C.RESET}")
                except (json.JSONDecodeError, OSError):
                    print(f"    {C.RED}>{C.RESET} {p.name} (unreadable)")



def cmd_scan(args):
    """Scan real codebase and feed results into adaptive systems."""
    # Delegate to scanner module
    from .adaptive_scanner import run_scan
    run_scan(verbose=args.verbose, json_output=args.json, systems=args.systems)


def cmd_test(args):
    """Run all adaptive system tests."""
    import subprocess
    print_header("Running Adaptive System Tests")
    cmd = [
        sys.executable, "-m", "pytest",
        "packages/adaptive_system/tests/",
        "packages/specialist_system/tests/test_specialist_genesis.py",
        "-v", "--no-cov", "--no-header",
    ]
    result = subprocess.run(cmd, cwd=str(Path.cwd()))
    sys.exit(result.returncode)


# ─────────────────────────────────────────────────────────────
# Phase 1 v4: Proposal Lifecycle Commands
# ─────────────────────────────────────────────────────────────

def _get_executor():
    """Create a ProposalExecutor for the proposals directory."""
    from .adaptive_executor import ProposalExecutor
    storage = get_storage_dir() / "proposals"
    return ProposalExecutor(storage)


def cmd_review(args):
    """Review all proposals by state."""
    print_header("Proposal Review")
    executor = _get_executor()
    
    # Migrate legacy proposals if any exist
    migrated = executor.ingest_legacy_proposals()
    if migrated:
        print(f"  {C.GREEN}Migrated {migrated} legacy proposal(s) to v4 format{C.RESET}\n")
    
    states = [args.state] if args.state else executor.SUBDIRS
    total = 0
    
    for state in states:
        proposals = executor.list_proposals(state)
        if not proposals:
            continue
        
        color = {
            "pending": C.YELLOW,
            "approved": C.CYAN,
            "completed": C.GREEN,
            "failed": C.RED,
            "rejected": C.DIM,
        }.get(state, "")
        
        print(f"\n  {C.BOLD}{color}{state.upper()} ({len(proposals)}):{C.RESET}")
        for p in proposals:
            desc = (p.description or p.proposal_id)[:65]
            desc = desc.encode("ascii", "replace").decode("ascii")
            sys_name = f" [{p.system_name}]" if p.system_name else ""
            approval = f" ({p.required_approval})" if state == "pending" else ""
            print(f"    {color}>{C.RESET} {desc}{C.DIM}{sys_name}{approval}{C.RESET}")
            print(f"      {C.DIM}ID: {p.proposal_id}{C.RESET}")
            
            if state == "completed" and p.outcome != "unknown":
                print(f"      {C.DIM}Outcome: {p.outcome} (score: {p.outcome_score}){C.RESET}")
        
        total += len(proposals)
    
    if total == 0:
        print(f"\n  {C.DIM}No proposals found{C.RESET}")
    
    # Stats
    stats = executor.get_stats()
    print(f"\n  {C.DIM}Effectiveness rate: {stats['effectiveness_rate']:.0%}{C.RESET}")


def cmd_approve(args):
    """Approve a pending proposal."""
    executor = _get_executor()
    executor.ingest_legacy_proposals()
    
    try:
        proposal = executor.approve(args.proposal_id, approved_by=args.by or "operator")
        print(f"  {C.GREEN}Approved:{C.RESET} {proposal.description}")
        print(f"  {C.DIM}Approved by: {proposal.approved_by}{C.RESET}")
        
        if args.execute:
            print(f"  {C.CYAN}Executing...{C.RESET}")
            result = executor.execute(args.proposal_id)
            if result.state == "completed":
                print(f"  {C.GREEN}Executed successfully{C.RESET}")
            else:
                print(f"  {C.RED}Execution failed: {result.execution_output}{C.RESET}")
    except ValueError as e:
        print(f"  {C.RED}Error: {e}{C.RESET}")


def cmd_reject(args):
    """Reject a pending proposal."""
    executor = _get_executor()
    executor.ingest_legacy_proposals()
    
    try:
        proposal = executor.reject(args.proposal_id, reason=args.reason or "")
        print(f"  {C.DIM}Rejected:{C.RESET} {proposal.description}")
        if args.reason:
            print(f"  {C.DIM}Reason: {args.reason}{C.RESET}")
    except ValueError as e:
        print(f"  {C.RED}Error: {e}{C.RESET}")


def cmd_auto_approve(args):
    """Auto-approve all AUTO-level proposals and optionally execute."""
    print_header("Auto-Approve Cycle")
    executor = _get_executor()
    
    migrated = executor.ingest_legacy_proposals()
    if migrated:
        print(f"  {C.GREEN}Migrated {migrated} legacy proposal(s){C.RESET}")
    
    approved = executor.auto_approve_all()
    print(f"  {C.GREEN}Auto-approved: {len(approved)}{C.RESET}")
    
    if args.execute and approved:
        print(f"\n  {C.CYAN}Executing approved proposals...{C.RESET}")
        executed = 0
        failed = 0
        for p in approved:
            result = executor.execute(p.proposal_id)
            status = C.GREEN + "OK" if result.state == "completed" else C.RED + "FAIL"
            desc = (p.description or p.proposal_id)[:50]
            desc = desc.encode("ascii", "replace").decode("ascii")
            print(f"    {status}{C.RESET}  {desc}")
            if result.state == "completed":
                executed += 1
            else:
                failed += 1
        
        print(f"\n  {C.BOLD}Results: {executed} executed, {failed} failed{C.RESET}")


def cmd_execute_approved(args):
    """Execute all approved proposals."""
    print_header("Executing Approved Proposals")
    executor = _get_executor()
    
    approved = executor.list_approved()
    if not approved:
        print(f"  {C.DIM}No approved proposals to execute{C.RESET}")
        return
    
    print(f"  {C.CYAN}Executing {len(approved)} proposal(s)...{C.RESET}\n")
    
    for p in approved:
        desc = (p.description or p.proposal_id)[:50]
        desc = desc.encode("ascii", "replace").decode("ascii")
        result = executor.execute(p.proposal_id)
        status = C.GREEN + "OK" if result.state == "completed" else C.RED + "FAIL"
        duration = f"{result.execution_duration:.1f}s" if result.execution_duration else ""
        print(f"    {status}{C.RESET}  {desc} {C.DIM}{duration}{C.RESET}")


# ---------------------------------------------------------------
# Phase 4 v4: Learning Engine Commands
# ---------------------------------------------------------------

def _get_learner():
    """Create an AdaptiveLearner."""
    from .adaptive_learner import AdaptiveLearner
    return AdaptiveLearner()


def cmd_learn(args):
    """Record outcome for a completed proposal and recalibrate."""
    learner = _get_learner()
    executor = _get_executor()
    
    proposal = executor.get_proposal(args.proposal_id)
    if not proposal:
        print(f"  {C.RED}Proposal not found: {args.proposal_id}{C.RESET}")
        return
    
    # Record outcome
    domain_key = ""
    if proposal.signal_data:
        domain_key = proposal.signal_data.get("source", "")
    
    learner.record_outcome(
        system_name=proposal.system_name or "unknown",
        proposal_id=proposal.proposal_id,
        outcome=args.outcome,
        domain_key=domain_key,
    )
    
    # Update proposal too
    executor.record_outcome(args.proposal_id, args.outcome, score=args.score)
    
    print(f"  {C.GREEN}Recorded:{C.RESET} {args.outcome} for {args.proposal_id}")
    print(f"  {C.DIM}System: {proposal.system_name}, Score: {args.score}{C.RESET}")
    
    # Auto-recalibrate
    changes = learner.recalibrate()
    if changes:
        print(f"\n  {C.CYAN}Recalibration:{C.RESET}")
        for sys_name, change in changes.items():
            print(f"    {sys_name}: threshold adj {change['old_adjustment']} -> {change['new_adjustment']}")
            if change.get("reason"):
                print(f"      {C.DIM}{change['reason']}{C.RESET}")


def cmd_calibrate(args):
    """Show learning engine calibration report."""
    print_header("Calibration Report")
    learner = _get_learner()
    
    if args.reset:
        learner.reset_system(args.reset)
        print(f"  {C.YELLOW}Reset calibration for: {args.reset}{C.RESET}\n")
    
    report = learner.get_report()
    print(f"  {C.DIM}File: {report['calibration_file']}{C.RESET}")
    print(f"  {C.DIM}Updated: {report['last_updated']}{C.RESET}")
    print(f"  {C.DIM}Total outcomes recorded: {report['total_outcomes']}{C.RESET}\n")
    
    systems = report.get("systems", {})
    if not systems:
        print(f"  {C.DIM}No calibration data yet. Use 'learn' to record outcomes.{C.RESET}")
        return
    
    for name, data in systems.items():
        eff = data.get("effectiveness_rate", 0)
        adj = data.get("threshold_adjustment", 0)
        sup = data.get("suppressed_domains", 0)
        
        color = C.GREEN if eff > 0.7 else C.YELLOW if eff > 0.4 else C.RED
        adj_str = f"+{adj}" if adj > 0 else str(adj)
        
        print(f"  {C.BOLD}{name}{C.RESET}")
        print(f"    Effectiveness:     {color}{eff:.0%}{C.RESET}")
        print(f"    Threshold adj:     {adj_str}")
        print(f"    Suppressed:        {sup} domain(s)")
        counts = data.get("outcome_breakdown", {})
        if counts:
            parts = [f"{k}={v}" for k, v in counts.items() if v > 0]
            print(f"    Outcomes:          {', '.join(parts)}")
        print()


# ---------------------------------------------------------------
# Phase 6 v4: Distributed Relay Commands
# ---------------------------------------------------------------

def cmd_relay(args):
    """Manage distributed relay operations."""
    from .adaptive_relay import SignalRelay, RelayConfig
    
    config = RelayConfig()
    relay = SignalRelay(config)
    
    action = getattr(args, "relay_action", "status")
    
    if action == "status":
        print_header("Relay Status")
        status = relay.get_status()
        print(f"  Local machine:  {status['local_machine']}")
        print(f"  Recent ops:     {status['recent_operations']}")
        last = status.get("last_relay")
        if last:
            print(f"  Last relay:     {last['action']} -> {last['peer']} ({last['timestamp'][:16]})")
        
        print(f"\n  {C.BOLD}Peers:{C.RESET}")
        for peer in status.get("peers", []):
            icon = f"{C.GREEN}OK{C.RESET}" if peer["reachable"] else f"{C.RED}UNREACHABLE{C.RESET}"
            active = "" if peer["active"] else f" {C.DIM}(inactive){C.RESET}"
            print(f"    {peer['name']}: {peer['url']} [{icon}]{active}")
    
    elif action == "push":
        target = getattr(args, "target", None)
        if target:
            result = relay.push_signals(target)
            print(f"  {'OK' if result['success'] else 'FAIL'}: pushed {result.get('pushed', 0)} signals to {target}")
        else:
            results = relay.push_to_all()
            for peer, result in results.items():
                status = f"{C.GREEN}OK{C.RESET}" if result["success"] else f"{C.RED}FAIL{C.RESET}"
                print(f"  {peer}: {status} ({result.get('pushed', 0)} signals)")
    
    elif action == "pull":
        source = getattr(args, "source", None)
        if source:
            result = relay.pull_proposals(source)
            print(f"  {'OK' if result['success'] else 'FAIL'}: pulled {result.get('pulled', 0)} proposals from {source}")
        else:
            results = relay.pull_from_all()
            for peer, result in results.items():
                status = f"{C.GREEN}OK{C.RESET}" if result["success"] else f"{C.RED}FAIL{C.RESET}"
                print(f"  {peer}: {status} ({result.get('pulled', 0)} proposals)")
    
    elif action == "sync":
        remote = getattr(args, "remote", None)
        if remote:
            result = relay.sync_calibration(remote)
            print(f"  {'OK' if result['success'] else 'FAIL'}: merged {result.get('merged_systems', 0)} systems with {remote}")
        else:
            results = relay.sync_all()
            for peer, result in results.items():
                status = f"{C.GREEN}OK{C.RESET}" if result["success"] else f"{C.RED}FAIL{C.RESET}"
                print(f"  {peer}: {status} ({result.get('merged_systems', 0)} systems merged)")
    
    elif action == "add-peer":
        name = args.peer_name
        url = args.peer_url
        config.add_peer(name, url, getattr(args, "description", ""))
        print(f"  {C.GREEN}Added peer:{C.RESET} {name} -> {url}")


def cmd_daemon(args):
    """Run the adaptive daemon."""
    from .adaptive_daemon import AdaptiveDaemon, DaemonConfig
    
    config = DaemonConfig(
        project_root=Path.cwd(),
        interval_minutes=getattr(args, "interval", 30),
        dry_run=getattr(args, "dry_run", False),
        incremental=getattr(args, "incremental", False),
        auto_execute=not getattr(args, "no_execute", False),
        max_cycles=0,
    )
    daemon = AdaptiveDaemon(config)
    
    if getattr(args, "status", False):
        # Show daemon status
        print_header("Daemon Status")
        status = daemon.get_status()
        print(f"  Total cycles:      {status['total_cycles']}")
        print(f"  Last cycle:        {status.get('last_cycle_at', 'never')}")
        print(f"  Last commit:       {status.get('last_commit_scanned', 'none')}")
        last = status.get("last_cycle_result", {})
        if last:
            print(f"  Last signals:      {last.get('signals', 0)}")
            print(f"  Last proposals:    {last.get('proposals', 0)}")
            print(f"  Last executed:     {last.get('executed', 0)}")
        ps = status.get("proposal_stats", {})
        print(f"\n  {C.BOLD}Proposal Pipeline:{C.RESET}")
        for state in ["pending", "approved", "completed", "failed", "rejected"]:
            count = ps.get(state, 0)
            if count:
                print(f"    {state}: {count}")
        return
    
    if getattr(args, "loop", False):
        print_header(f"Daemon Loop (every {config.interval_minutes}m)")
        if config.dry_run:
            print(f"  {C.YELLOW}DRY RUN MODE{C.RESET}")
        daemon.run_loop()
    else:
        # Single cycle
        print_header("Daemon Cycle")
        if config.dry_run:
            print(f"  {C.YELLOW}DRY RUN MODE{C.RESET}")
        if config.incremental:
            print(f"  {C.DIM}Mode: incremental{C.RESET}")
        
        result = daemon.run_cycle()
        
        print(f"\n  {C.BOLD}Cycle Results:{C.RESET}")
        print(f"    Signals:          {result.get('total_signals', 0)}")
        print(f"    Proposals:        {result.get('total_proposals', 0)}")
        print(f"    Auto-approved:    {result.get('auto_approved', 0)}")
        print(f"    Overseer-approved:{result.get('overseer_approved', 0)}")
        print(f"    Overseer-rejected:{result.get('overseer_rejected', 0)}")
        print(f"    Deferred:         {result.get('deferred', 0)}")
        print(f"    Executed:         {result.get('executed', 0)}")
        print(f"    Failed:           {result.get('failed', 0)}")
        print(f"    Duration:         {result.get('duration', 0):.1f}s")


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="adaptive_cli",
        description="AIM-OS Adaptive Nervous System -- Test & Debug CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python -m packages.adaptive_system.adaptive_cli demo
  python -m packages.adaptive_system.adaptive_cli run research_depth
  python -m packages.adaptive_system.adaptive_cli run test_coverage --context '{"module_name":"seg","coverage_percent":30}'
  python -m packages.adaptive_system.adaptive_cli scan
  python -m packages.adaptive_system.adaptive_cli debug
  python -m packages.adaptive_system.adaptive_cli status
  python -m packages.adaptive_system.adaptive_cli test
  python -m packages.adaptive_system.adaptive_cli review
  python -m packages.adaptive_system.adaptive_cli approve <id> --execute
  python -m packages.adaptive_system.adaptive_cli reject <id> --reason "noise"
  python -m packages.adaptive_system.adaptive_cli auto-approve --execute
        """,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output for machine parsing")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # run
    run_parser = subparsers.add_parser("run", help="Run a single system")
    run_parser.add_argument("system", choices=list(SYSTEMS.keys()), help="System to run")
    run_parser.add_argument("--context", "-c", help="JSON context string")
    run_parser.set_defaults(func=cmd_run)
    
    # demo
    demo_parser = subparsers.add_parser("demo", help="Run all systems with demo data")
    demo_parser.set_defaults(func=cmd_demo)
    
    # status
    status_parser = subparsers.add_parser("status", help="Show system health")
    status_parser.set_defaults(func=cmd_status)
    
    # debug
    debug_parser = subparsers.add_parser("debug", help="Inspect tracker state")
    debug_parser.add_argument("--system", "-s", help="Filter by system name")
    debug_parser.set_defaults(func=cmd_debug)
    
    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan real codebase")
    scan_parser.add_argument("--systems", nargs="+", help="Systems to scan with")
    scan_parser.set_defaults(func=cmd_scan)
    
    # test
    test_parser = subparsers.add_parser("test", help="Run unit tests")
    test_parser.set_defaults(func=cmd_test)
    
    # --- Phase 1 v4: Proposal Lifecycle ---
    
    # review
    review_parser = subparsers.add_parser("review", help="Review proposals by state")
    review_parser.add_argument("--state", choices=["pending", "approved", "completed", "failed", "rejected"], help="Filter by state")
    review_parser.set_defaults(func=cmd_review)
    
    # approve
    approve_parser = subparsers.add_parser("approve", help="Approve a pending proposal")
    approve_parser.add_argument("proposal_id", help="Proposal ID (filename stem)")
    approve_parser.add_argument("--by", help="Approver identity (default: operator)")
    approve_parser.add_argument("--execute", "-x", action="store_true", help="Execute immediately after approval")
    approve_parser.set_defaults(func=cmd_approve)
    
    # reject
    reject_parser = subparsers.add_parser("reject", help="Reject a pending proposal")
    reject_parser.add_argument("proposal_id", help="Proposal ID")
    reject_parser.add_argument("--reason", "-r", help="Rejection reason")
    reject_parser.set_defaults(func=cmd_reject)
    
    # auto-approve
    auto_parser = subparsers.add_parser("auto-approve", help="Auto-approve all AUTO-level proposals")
    auto_parser.add_argument("--execute", "-x", action="store_true", help="Execute after approval")
    auto_parser.set_defaults(func=cmd_auto_approve)
    
    # execute-approved
    exec_parser = subparsers.add_parser("execute-approved", help="Execute all approved proposals")
    exec_parser.set_defaults(func=cmd_execute_approved)
    
    # --- Phase 2 v4: Daemon ---
    
    daemon_parser = subparsers.add_parser("daemon", help="Run adaptive daemon cycle")
    daemon_parser.add_argument("--loop", action="store_true", help="Run continuously")
    daemon_parser.add_argument("--interval", type=int, default=30, help="Minutes between cycles (default: 30)")
    daemon_parser.add_argument("--dry-run", action="store_true", help="Scan and decide but don't execute")
    daemon_parser.add_argument("--incremental", action="store_true", help="Only scan changed files")
    daemon_parser.add_argument("--no-execute", action="store_true", help="Don't auto-execute approved proposals")
    daemon_parser.add_argument("--status", action="store_true", help="Show daemon status")
    daemon_parser.set_defaults(func=cmd_daemon)
    
    # --- Phase 4 v4: Learning Engine ---
    
    # learn
    learn_parser = subparsers.add_parser("learn", help="Record proposal outcome for learning")
    learn_parser.add_argument("proposal_id", help="Proposal ID to record outcome for")
    learn_parser.add_argument("outcome", choices=["effective", "noise", "false_positive", "rejected"], help="Outcome type")
    learn_parser.add_argument("--score", type=float, default=0.5, help="Outcome quality score 0-1 (default: 0.5)")
    learn_parser.set_defaults(func=cmd_learn)
    
    # calibrate
    cal_parser = subparsers.add_parser("calibrate", help="Show calibration report")
    cal_parser.add_argument("--reset", help="Reset calibration for a system")
    cal_parser.set_defaults(func=cmd_calibrate)
    
    # --- Phase 6 v4: Distributed Relay ---
    
    relay_parser = subparsers.add_parser("relay", help="Distributed relay operations")
    relay_subs = relay_parser.add_subparsers(dest="relay_action")
    
    relay_status = relay_subs.add_parser("status", help="Show relay status")
    
    relay_push = relay_subs.add_parser("push", help="Push signals to peer(s)")
    relay_push.add_argument("--target", help="Target URL (default: all peers)")
    
    relay_pull = relay_subs.add_parser("pull", help="Pull proposals from peer(s)")
    relay_pull.add_argument("--source", help="Source URL (default: all peers)")
    
    relay_sync = relay_subs.add_parser("sync", help="Sync calibration with peer(s)")
    relay_sync.add_argument("--remote", help="Remote URL (default: all peers)")
    
    relay_add = relay_subs.add_parser("add-peer", help="Add a relay peer")
    relay_add.add_argument("peer_name", help="Peer name")
    relay_add.add_argument("peer_url", help="Peer URL")
    relay_add.add_argument("--description", default="", help="Peer description")
    
    relay_parser.set_defaults(func=cmd_relay)
    
    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
