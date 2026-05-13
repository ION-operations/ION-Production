"""
Adaptive Daemon -- Autonomous Sense-Decide-Act Cycle

The brain of the Adaptive Nervous System. Runs full cycles:
    1. Scan codebase (full or incremental)
    2. Process signals through all 8 adaptive systems
    3. Auto-approve safe proposals
    4. Evaluate gated proposals (via overseer logic or LLM)
    5. Execute approved proposals (spawn agents via genome_assembler)
    6. Collect feedback from executed proposals
    7. Update learning weights (Phase 4)

Designed for two invocation modes:
    - Schedule: Run via cron/task scheduler
    - Event-driven: Triggered by git hooks or agent requests

Usage:
    # Single cycle
    python -m packages.adaptive_system daemon --cycle
    
    # Continuous loop (every N minutes)
    python -m packages.adaptive_system daemon --loop --interval 30
    
    # Event-driven (scan only changed files)
    python -m packages.adaptive_system daemon --incremental
    
    # Dry run (scan + decide but don't execute)
    python -m packages.adaptive_system daemon --dry-run
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("adaptive_daemon")


# ---------------------------------------------------------------
# Daemon Configuration
# ---------------------------------------------------------------

class DaemonConfig:
    """Configuration for the adaptive daemon."""
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        interval_minutes: int = 30,
        max_cycles: int = 0,           # 0 = unlimited
        dry_run: bool = False,
        incremental: bool = False,
        auto_execute: bool = True,
        overseer_mode: str = "rules",  # "rules" or "llm"
        max_proposals_per_cycle: int = 20,
    ):
        self.project_root = project_root or Path.cwd()
        self.interval_minutes = interval_minutes
        self.max_cycles = max_cycles
        self.dry_run = dry_run
        self.incremental = incremental
        self.auto_execute = auto_execute
        self.overseer_mode = overseer_mode
        self.max_proposals_per_cycle = max_proposals_per_cycle


# ---------------------------------------------------------------
# Incremental Change Detector
# ---------------------------------------------------------------

class ChangeDetector:
    """Detects file changes since last daemon cycle."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_file = project_root / ".agent" / "adaptive" / "daemon_state.json"
    
    def _load_state(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}
    
    def _save_state(self, state: dict):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(state, indent=2, default=str),
            encoding="utf-8",
        )
    
    def get_changed_files(self) -> List[Path]:
        """Get files changed since last scan using git."""
        state = self._load_state()
        last_commit = state.get("last_commit_scanned", "")
        
        try:
            if last_commit:
                # Get files changed since last scanned commit
                result = subprocess.run(
                    ["git", "diff", "--name-only", last_commit, "HEAD"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(self.project_root),
                )
            else:
                # First run: get files changed in last commit
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(self.project_root),
                )
            
            if result.returncode == 0:
                files = [
                    self.project_root / f.strip()
                    for f in result.stdout.strip().split("\n")
                    if f.strip()
                ]
                return files
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return []
    
    def get_current_commit(self) -> str:
        """Get the current HEAD commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=10,
                cwd=str(self.project_root),
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""
    
    def update_state(self, commit: str, cycle_result: dict):
        """Update daemon state after a cycle."""
        state = self._load_state()
        state["last_commit_scanned"] = commit
        state["last_cycle_at"] = datetime.now().isoformat()
        state["last_cycle_result"] = {
            "signals": cycle_result.get("total_signals", 0),
            "proposals": cycle_result.get("total_proposals", 0),
            "executed": cycle_result.get("executed", 0),
        }
        state["total_cycles"] = state.get("total_cycles", 0) + 1
        self._save_state(state)
    
    def route_files_to_scanners(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Route changed files to the appropriate scanners."""
        routes = {
            "test_coverage": [],
            "arch_drift": [],
            "doc_depth": [],
            "security_posture": [],
            "knowledge_decay": [],
        }
        
        for f in files:
            name = f.name.lower()
            suffix = f.suffix.lower()
            parts = str(f).replace("\\", "/").lower()
            
            if suffix == ".py":
                routes["arch_drift"].append(f)
                routes["test_coverage"].append(f)
                if "__init__" in name or "docs" in parts:
                    routes["doc_depth"].append(f)
            
            if suffix in (".json", ".toml", ".cfg", ".ini", ".env"):
                routes["security_posture"].append(f)
            
            if "requirements" in name or "package.json" in name:
                routes["security_posture"].append(f)
            
            if ".gemini" in parts or "knowledge" in parts:
                routes["knowledge_decay"].append(f)
        
        return {k: v for k, v in routes.items() if v}


# ---------------------------------------------------------------
# Overseer (Proposal Evaluator)
# ---------------------------------------------------------------

class ProposalOverseer:
    """
    Evaluates gated proposals and decides approve/reject.
    
    Two modes:
    - "rules": Rule-based evaluation (fast, deterministic)
    - "llm": LLM-assisted evaluation via Gemini CLI (thorough, costly)
    """
    
    def __init__(self, mode: str = "rules"):
        self.mode = mode
        self.rules = self._load_rules()
    
    def _load_rules(self) -> dict:
        """Load overseer rules from calibration file."""
        return {
            # Auto-approve lead proposals for these safe response types
            "auto_approve_types": [
                "doc_enrich",
                "doc_stub",
                "test_unit",
            ],
            # Always reject proposals for suppressed domains
            "suppressed_domains": [],
            # Max proposals to approve per cycle
            "max_per_cycle": 10,
            # Reject if description contains these (safety catch)
            "reject_keywords": ["delete", "remove all", "drop table"],
        }
    
    def evaluate(self, proposal) -> Tuple[bool, str]:
        """Evaluate a gated proposal.
        
        Returns:
            (should_approve, reason)
        """
        if self.mode == "rules":
            return self._evaluate_rules(proposal)
        else:
            return self._evaluate_llm(proposal)
    
    def _evaluate_rules(self, proposal) -> Tuple[bool, str]:
        """Rule-based evaluation."""
        desc = (proposal.description or "").lower()
        
        # Safety: reject dangerous keywords
        for keyword in self.rules.get("reject_keywords", []):
            if keyword in desc:
                return False, f"Safety: contains '{keyword}'"
        
        # Suppressed domains
        signal_type = proposal.signal_data.get("signal_type", "") if proposal.signal_data else ""
        for suppressed in self.rules.get("suppressed_domains", []):
            if suppressed in signal_type or suppressed in desc:
                return False, f"Suppressed domain: {suppressed}"
        
        # Auto-approve safe types even if gated
        if proposal.response_type in self.rules.get("auto_approve_types", []):
            return True, "Safe response type (overseer auto-approved)"
        
        # For "lead" level: approve if it's a scan/audit (read-only)
        if proposal.required_approval == "lead":
            read_only_types = ["security_endpoint_scan", "decay_refresh"]
            if proposal.response_type in read_only_types:
                return True, "Read-only operation (overseer approved)"
        
        # Default: defer (don't approve, don't reject)
        return False, "Requires human review (overseer deferred)"
    
    def _evaluate_llm(self, proposal) -> Tuple[bool, str]:
        """LLM-assisted evaluation via Gemini CLI.
        
        TODO: Implement when Gemini CLI integration is mature.
        For now, falls back to rules.
        """
        return self._evaluate_rules(proposal)


# ---------------------------------------------------------------
# Adaptive Daemon
# ---------------------------------------------------------------

class AdaptiveDaemon:
    """
    The autonomous daemon that runs the full adaptive cycle.
    
    Cycle:
        1. Detect changes (full scan or incremental)
        2. Feed signals to adaptive systems
        3. Process proposals (auto-approve, overseer, defer to human)
        4. Execute approved proposals
        5. Record results for learning
    """
    
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.change_detector = ChangeDetector(config.project_root)
        self.overseer = ProposalOverseer(mode=config.overseer_mode)
        self._cycle_count = 0
    
    def _get_executor(self):
        from .adaptive_executor import ProposalExecutor
        storage = self.config.project_root / ".agent" / "adaptive" / "proposals"
        return ProposalExecutor(storage)
    
    def run_cycle(self) -> dict:
        """Run one full sense-decide-act cycle."""
        cycle_start = time.time()
        self._cycle_count += 1
        
        logger.info(f"[daemon] Starting cycle #{self._cycle_count}")
        result = {
            "cycle": self._cycle_count,
            "started_at": datetime.now().isoformat(),
            "total_signals": 0,
            "total_proposals": 0,
            "auto_approved": 0,
            "overseer_approved": 0,
            "overseer_rejected": 0,
            "deferred": 0,
            "executed": 0,
            "failed": 0,
        }
        
        # 1. Scan
        if self.config.incremental:
            result["scan_mode"] = "incremental"
            changed = self.change_detector.get_changed_files()
            routes = self.change_detector.route_files_to_scanners(changed)
            result["files_changed"] = len(changed)
            result["scanners_triggered"] = list(routes.keys())
            
            if not changed:
                result["status"] = "no_changes"
                logger.info("[daemon] No changes detected, skipping cycle")
                return result
            
            signals = self._scan_incremental(routes)
        else:
            result["scan_mode"] = "full"
            signals = self._scan_full()
        
        result["total_signals"] = signals
        
        # 2. Process proposals through executor
        executor = self._get_executor()
        executor.ingest_legacy_proposals()
        
        pending = executor.list_pending()
        result["total_proposals"] = len(pending)
        
        if self.config.dry_run:
            result["status"] = "dry_run"
            result["duration"] = time.time() - cycle_start
            logger.info(f"[daemon] Dry run: {signals} signals, {len(pending)} proposals")
            return result
        
        # 3. Auto-approve AUTO-level
        auto_approved = executor.auto_approve_all()
        result["auto_approved"] = len(auto_approved)
        
        # 4. Overseer evaluates remaining gated proposals
        remaining_pending = executor.list_pending()
        approved_count = 0
        
        for proposal in remaining_pending[:self.config.max_proposals_per_cycle]:
            should_approve, reason = self.overseer.evaluate(proposal)
            
            if should_approve:
                executor.approve(proposal.proposal_id, approved_by=f"overseer:{reason}")
                result["overseer_approved"] += 1
                approved_count += 1
            elif "deferred" in reason.lower():
                result["deferred"] += 1
            else:
                executor.reject(proposal.proposal_id, reason=reason)
                result["overseer_rejected"] += 1
        
        # 5. Execute all approved proposals
        if self.config.auto_execute:
            approved_proposals = executor.list_approved()
            for p in approved_proposals:
                try:
                    exec_result = executor.execute(p.proposal_id)
                    if exec_result.state == "completed":
                        result["executed"] += 1
                    else:
                        result["failed"] += 1
                except Exception as e:
                    logger.error(f"[daemon] Execution error: {e}")
                    result["failed"] += 1
        
        # 6. Learning Engine integration (Phase 4)
        try:
            from .adaptive_learner import AdaptiveLearner
            cal_path = self.config.project_root / ".agent" / "adaptive" / "calibration.json"
            learner = AdaptiveLearner(cal_path)
            
            # Feed noise suppressions into overseer
            for sys_name in learner.state.data.get("systems", {}):
                sys_cal = learner.state.get_system(sys_name)
                for domain in sys_cal.get("suppressed_domains", []):
                    if domain not in self.overseer.rules.get("suppressed_domains", []):
                        self.overseer.rules.setdefault("suppressed_domains", []).append(domain)
            
            # Run recalibration
            changes = learner.recalibrate()
            result["calibration_changes"] = len(changes)
            if changes:
                logger.info(f"[daemon] Recalibrated {len(changes)} system(s)")
        except Exception as e:
            logger.debug(f"[daemon] Learner integration skipped: {e}")
        
        # 7. Update daemon state
        commit = self.change_detector.get_current_commit()
        self.change_detector.update_state(commit, result)
        
        result["duration"] = time.time() - cycle_start
        result["status"] = "completed"
        
        logger.info(
            f"[daemon] Cycle #{self._cycle_count} complete: "
            f"{result['total_signals']} signals, "
            f"{result['auto_approved']} auto-approved, "
            f"{result['overseer_approved']} overseer-approved, "
            f"{result['executed']} executed in {result['duration']:.1f}s"
        )
        
        return result
    
    def _scan_full(self) -> int:
        """Run full codebase scan via scanner module."""
        try:
            from .adaptive_scanner import run_scan
            # Capture the output by redirecting -- run_scan prints directly
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                run_scan(verbose=False, json_output=False)
            finally:
                sys.stdout = old_stdout
            
            # Count signals from tracker files
            storage = self.config.project_root / ".agent" / "adaptive"
            total = 0
            for f in storage.glob("*.json"):
                if f.stem in ("daemon_state", "calibration"):
                    continue
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    total += data.get("count", 0)
                except (json.JSONDecodeError, OSError):
                    pass
            return total
        except Exception as e:
            logger.error(f"[daemon] Full scan error: {e}")
            return 0
    
    def _scan_incremental(self, routes: Dict[str, List[Path]]) -> int:
        """Run incremental scan on only changed files."""
        # For now, fall back to full scan since individual scanner functions
        # don't yet support file-level filtering. The routes dict is ready
        # for Phase 3 when we add targeted scanning.
        return self._scan_full()
    
    def run_loop(self):
        """Run daemon in continuous loop."""
        logger.info(
            f"[daemon] Starting continuous loop "
            f"(interval: {self.config.interval_minutes}m, "
            f"max_cycles: {self.config.max_cycles or 'unlimited'})"
        )
        
        while True:
            try:
                result = self.run_cycle()
                
                # Print cycle summary
                print(f"\n[daemon] Cycle #{result['cycle']}: "
                      f"{result.get('total_signals', 0)} signals, "
                      f"{result.get('executed', 0)} executed, "
                      f"{result.get('duration', 0):.1f}s")
                
                # Check max cycles
                if self.config.max_cycles and self._cycle_count >= self.config.max_cycles:
                    logger.info("[daemon] Max cycles reached, stopping")
                    break
                
                # Wait for next cycle
                wait_seconds = self.config.interval_minutes * 60
                logger.info(f"[daemon] Next cycle in {self.config.interval_minutes} minutes")
                time.sleep(wait_seconds)
                
            except KeyboardInterrupt:
                logger.info("[daemon] Stopped by user")
                break
            except Exception as e:
                logger.error(f"[daemon] Cycle error: {e}")
                # Wait before retrying
                time.sleep(60)
    
    def get_status(self) -> dict:
        """Get daemon status."""
        state = self.change_detector._load_state()
        executor = self._get_executor()
        stats = executor.get_stats()
        
        return {
            "total_cycles": state.get("total_cycles", 0),
            "last_cycle_at": state.get("last_cycle_at"),
            "last_commit_scanned": state.get("last_commit_scanned", "")[:8],
            "last_cycle_result": state.get("last_cycle_result", {}),
            "proposal_stats": stats,
        }
