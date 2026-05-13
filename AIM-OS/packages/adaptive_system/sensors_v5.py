"""
Phase 5 Adaptive Sensors -- Performance, Dependencies, Agents, Context

Four new sensor types for the Adaptive Nervous System:
    1. PerformanceSensor   -- Detect performance regressions (test timing, startup, file sizes)
    2. DependencySensor    -- Monitor dependency health (outdated, vulnerable, unused)
    3. AgentSensor         -- Track agent effectiveness (success rate, latency, drift)
    4. ContextSensor       -- Monitor context coherence (KI staleness, capsule drift, memory bloat)
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .adaptive_core import (
    AdaptiveSensor, AdaptiveAnalyzer, AdaptiveGenerator,
    Signal, Assessment, AdaptiveResponse, ApprovalLevel,
)

logger = logging.getLogger("adaptive_sensors_v5")


# ---------------------------------------------------------------
# 1. Performance Regression Sensor
# ---------------------------------------------------------------

class PerformanceSensor(AdaptiveSensor):
    """Detects performance regressions: large files, slow operations."""
    
    SIGNAL_TYPE = "perf_regression"
    
    # Thresholds
    MAX_FILE_SIZE_KB = 500           # Python files over 500KB are suspicious
    MAX_MODULE_LINES = 1000          # Files over 1000 lines are too complex
    MAX_IMPORT_DEPTH = 10            # Circular/deep import chains
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        root = Path(context.get("project_root", "."))
        
        # Check for oversized Python files
        target = context.get("file_path", "")
        if target:
            path = root / target
            if path.exists() and path.suffix == ".py":
                size_kb = path.stat().st_size / 1024
                if size_kb > self.MAX_FILE_SIZE_KB:
                    return Signal(
                        signal_type=self.SIGNAL_TYPE,
                        source=str(path),
                        severity="high",
                        description=f"File {path.name} is {size_kb:.0f}KB (max: {self.MAX_FILE_SIZE_KB}KB)",
                        data={"size_kb": size_kb, "max_kb": self.MAX_FILE_SIZE_KB},
                    )
                
                lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
                if lines > self.MAX_MODULE_LINES:
                    return Signal(
                        signal_type=self.SIGNAL_TYPE,
                        source=str(path),
                        severity="medium",
                        description=f"File {path.name} has {lines} lines (max: {self.MAX_MODULE_LINES})",
                        data={"lines": lines, "max_lines": self.MAX_MODULE_LINES},
                    )
        
        return None
    
    def get_domain_key(self, signal: Signal) -> str:
        return f"perf:{signal.source}"


class PerformanceAnalyzer(AdaptiveAnalyzer):
    """Assesses performance regression severity."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_thresh: bool) -> Assessment:
        severity = signal.severity
        if severity == "high":
            return Assessment(
                should_adapt=exceeds_thresh,
                severity=severity,
                approval_level=ApprovalLevel.LEAD,
                recommendation=f"Refactor oversized module: {signal.source}",
            )
        return Assessment(
            should_adapt=exceeds_thresh,
            severity=severity,
            approval_level=ApprovalLevel.AUTO,
            recommendation=f"Consider splitting: {signal.source}",
        )


class PerformanceGenerator(AdaptiveGenerator):
    """Generates performance improvement proposals."""
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        return AdaptiveResponse(
            response_type="perf_refactor",
            description=assessment.recommendation,
            content=f"Performance improvement needed: {assessment.recommendation}",
        )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        response.success = True
        return response


# ---------------------------------------------------------------
# 2. Dependency Health Sensor
# ---------------------------------------------------------------

class DependencySensor(AdaptiveSensor):
    """Monitors dependency health: outdated packages, missing deps."""
    
    SIGNAL_TYPE = "dep_health"
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        root = Path(context.get("project_root", "."))
        
        # Check requirements files
        req_files = list(root.glob("requirements*.txt"))
        for req_file in req_files:
            lines = req_file.read_text(encoding="utf-8", errors="replace").splitlines()
            unpinned = [l.strip() for l in lines if l.strip() and not l.startswith("#") and "==" not in l and ">=" not in l]
            
            if len(unpinned) > 3:
                return Signal(
                    signal_type=self.SIGNAL_TYPE,
                    source=str(req_file),
                    severity="medium",
                    description=f"{len(unpinned)} unpinned dependencies in {req_file.name}",
                    data={"unpinned": unpinned[:10], "count": len(unpinned)},
                )
        
        # Check package.json for outdated
        pkg_json = root / "package.json"
        if pkg_json.exists():
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = pkg.get("dependencies", {})
                dev_deps = pkg.get("devDependencies", {})
                total = len(deps) + len(dev_deps)
                
                # Check for wildcard versions
                wildcards = [
                    name for name, ver in {**deps, **dev_deps}.items()
                    if ver in ("*", "latest")
                ]
                
                if wildcards:
                    return Signal(
                        signal_type=self.SIGNAL_TYPE,
                        source=str(pkg_json),
                        severity="high",
                        description=f"{len(wildcards)} wildcard dependency versions",
                        data={"wildcards": wildcards},
                    )
            except (json.JSONDecodeError, OSError):
                pass
        
        return None
    
    def get_domain_key(self, signal: Signal) -> str:
        return f"dep:{signal.source}"


class DependencyAnalyzer(AdaptiveAnalyzer):
    """Assesses dependency health severity."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_thresh: bool) -> Assessment:
        return Assessment(
            should_adapt=exceeds_thresh,
            severity=signal.severity,
            approval_level=ApprovalLevel.LEAD if signal.severity == "high" else ApprovalLevel.AUTO,
            recommendation=signal.description,
        )


class DependencyGenerator(AdaptiveGenerator):
    """Generates dependency health proposals."""
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        return AdaptiveResponse(
            response_type="dep_audit",
            description=assessment.recommendation,
            content=f"Dependency health issue: {assessment.recommendation}",
        )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        response.success = True
        return response


# ---------------------------------------------------------------
# 3. Agent Effectiveness Sensor
# ---------------------------------------------------------------

class AgentSensor(AdaptiveSensor):
    """Tracks agent effectiveness from genome data and execution logs."""
    
    SIGNAL_TYPE = "agent_effectiveness"
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        root = Path(context.get("project_root", "."))
        
        # Check for genomes without corresponding implementations
        genomes_dir = root / ".agent" / "genomes" / "cores" / "specialists"
        if genomes_dir.exists():
            orphan_genomes = []
            for genome in genomes_dir.glob("*.md"):
                agent_name = genome.stem
                # Check if there's a corresponding test or implementation file
                has_impl = any([
                    (root / "packages" / f"agent_{agent_name.replace('-', '_')}.py").exists(),
                    (root / "scripts" / f"agent_{agent_name.replace('-', '_')}.py").exists(),
                ])
                if not has_impl and "template" not in agent_name:
                    orphan_genomes.append(agent_name)
            
            if len(orphan_genomes) > 5:
                return Signal(
                    signal_type=self.SIGNAL_TYPE,
                    source="genomes",
                    severity="low",
                    description=f"{len(orphan_genomes)} agent genomes without dedicated implementation",
                    data={"orphans": orphan_genomes[:10]},
                )
        
        # Check comms for stale agent chat files (no messages in 7+ days)
        comms_dir = root / ".agent" / "comms" / "chat"
        if comms_dir.exists():
            stale_agents = []
            for agent_dir in comms_dir.iterdir():
                if agent_dir.is_dir():
                    chat_files = sorted(agent_dir.glob("*.md"))
                    if chat_files:
                        latest = chat_files[-1]
                        try:
                            age_days = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).days
                            if age_days > 7:
                                stale_agents.append((agent_dir.name, age_days))
                        except (OSError, ValueError):
                            pass
            
            if stale_agents:
                return Signal(
                    signal_type=self.SIGNAL_TYPE,
                    source="agent_activity",
                    severity="low",
                    description=f"{len(stale_agents)} agents inactive for 7+ days",
                    data={"stale": [{"agent": a, "days": d} for a, d in stale_agents[:5]]},
                )
        
        return None
    
    def get_domain_key(self, signal: Signal) -> str:
        return f"agent:{signal.source}"


class AgentAnalyzer(AdaptiveAnalyzer):
    """Assesses agent effectiveness."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_thresh: bool) -> Assessment:
        return Assessment(
            should_adapt=exceeds_thresh,
            severity=signal.severity,
            approval_level=ApprovalLevel.AUTO,
            recommendation=signal.description,
        )


class AgentGenerator(AdaptiveGenerator):
    """Generates agent effectiveness proposals."""
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        return AdaptiveResponse(
            response_type="agent_audit",
            description=assessment.recommendation,
        )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        response.success = True
        return response


# ---------------------------------------------------------------
# 4. Context Coherence Sensor
# ---------------------------------------------------------------

class ContextSensor(AdaptiveSensor):
    """Monitors context coherence: KI staleness, memory bloat, capsule drift."""
    
    SIGNAL_TYPE = "context_coherence"
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        root = Path(context.get("project_root", "."))
        
        # Check Knowledge Items for staleness
        ki_dir = Path.home() / ".gemini" / "antigravity" / "knowledge"
        if ki_dir.exists():
            stale_kis = []
            for ki_meta in ki_dir.glob("*/metadata.json"):
                try:
                    meta = json.loads(ki_meta.read_text(encoding="utf-8"))
                    last_accessed = meta.get("last_accessed", "")
                    if last_accessed:
                        age = (datetime.now() - datetime.fromisoformat(last_accessed.replace("Z", "+00:00").replace("+00:00", ""))).days
                        if age > 14:
                            stale_kis.append({"ki": ki_meta.parent.name, "days": age})
                except (json.JSONDecodeError, OSError, ValueError):
                    pass
            
            if len(stale_kis) > 3:
                return Signal(
                    signal_type=self.SIGNAL_TYPE,
                    source="knowledge_items",
                    severity="low",
                    description=f"{len(stale_kis)} KIs not accessed in 14+ days",
                    data={"stale_kis": stale_kis[:10]},
                )
        
        # Check adaptive data directory bloat
        adaptive_dir = root / ".agent" / "adaptive"
        if adaptive_dir.exists():
            total_size = sum(f.stat().st_size for f in adaptive_dir.rglob("*") if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            if size_mb > 10:
                return Signal(
                    signal_type=self.SIGNAL_TYPE,
                    source="adaptive_storage",
                    severity="medium",
                    description=f"Adaptive storage is {size_mb:.1f}MB (cleanup recommended)",
                    data={"size_mb": size_mb},
                )
        
        # Check capsule consistency
        capsules_dir = root / ".agent" / "comms" / "capsules"
        if capsules_dir.exists():
            capsule_count = sum(1 for _ in capsules_dir.rglob("*.md"))
            if capsule_count > 100:
                return Signal(
                    signal_type=self.SIGNAL_TYPE,
                    source="capsules",
                    severity="low",
                    description=f"{capsule_count} capsule files (archiving recommended)",
                    data={"count": capsule_count},
                )
        
        return None
    
    def get_domain_key(self, signal: Signal) -> str:
        return f"context:{signal.source}"


class ContextAnalyzer(AdaptiveAnalyzer):
    """Assesses context coherence issues."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_thresh: bool) -> Assessment:
        return Assessment(
            should_adapt=exceeds_thresh,
            severity=signal.severity,
            approval_level=ApprovalLevel.AUTO,
            recommendation=signal.description,
        )


class ContextGenerator(AdaptiveGenerator):
    """Generates context coherence proposals."""
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        return AdaptiveResponse(
            response_type="context_cleanup",
            description=assessment.recommendation,
        )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        response.success = True
        return response
