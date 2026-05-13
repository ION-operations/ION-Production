"""
Comprehensive tests for the v4 Adaptive Nervous System modules.

Tests cover:
    Phase 1: ProposalExecutor state machine
    Phase 2: AdaptiveDaemon cycle logic
    Phase 4: AdaptiveLearner calibration
    Phase 5: v5 sensors
    Phase 6: Relay configuration
"""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------
# Phase 1: Proposal Executor Tests
# ---------------------------------------------------------------

class TestProposalExecutor:
    """Test the 5-state proposal machine."""
    
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        from packages.adaptive_system.adaptive_executor import ProposalExecutor
        self.executor = ProposalExecutor(self.tmpdir)
    
    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
    
    def _create_proposal(self, pid="test_001", rtype="doc_enrich", approval="auto"):
        """Helper: create a test proposal in pending state."""
        pending = self.tmpdir / "pending"
        pending.mkdir(parents=True, exist_ok=True)
        data = {
            "response_type": rtype,
            "description": f"Test proposal {pid}",
            "target_path": "test.py",
            "required_approval": approval,
            "created_at": datetime.now().isoformat(),
        }
        (pending / f"{pid}.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        return pid
    
    def test_list_pending(self):
        self._create_proposal("p1")
        self._create_proposal("p2")
        pending = self.executor.list_pending()
        assert len(pending) == 2
    
    def test_approve_moves_state(self):
        self._create_proposal("p1")
        result = self.executor.approve("p1", approved_by="test")
        assert result is not None
        assert result.state == "approved"
        assert (self.tmpdir / "approved" / "p1.json").exists()
        assert not (self.tmpdir / "pending" / "p1.json").exists()
    
    def test_reject_moves_state(self):
        self._create_proposal("p1")
        result = self.executor.reject("p1", reason="noise")
        assert result is not None
        assert result.state == "rejected"
        assert (self.tmpdir / "rejected" / "p1.json").exists()
    
    def test_auto_approve_all(self):
        self._create_proposal("p1", approval="auto")
        self._create_proposal("p2", approval="lead")
        self._create_proposal("p3", approval="auto")
        approved = self.executor.auto_approve_all()
        assert len(approved) == 2
        remaining = self.executor.list_pending()
        assert len(remaining) == 1
    
    def test_execute_approved_proposal(self):
        self._create_proposal("p1")
        self.executor.approve("p1", approved_by="test")
        result = self.executor.execute("p1")
        assert result.state in ("completed", "failed")
    
    def test_get_stats(self):
        self._create_proposal("p1")
        self._create_proposal("p2")
        self.executor.approve("p1", approved_by="test")
        stats = self.executor.get_stats()
        assert stats.get("pending", 0) == 1
        assert stats.get("approved", 0) == 1
    
    def test_approve_nonexistent_raises(self):
        with pytest.raises(ValueError):
            self.executor.approve("doesnt_exist")
    
    def test_reject_nonexistent_raises(self):
        with pytest.raises(ValueError):
            self.executor.reject("doesnt_exist")


# ---------------------------------------------------------------
# Phase 2: Daemon Tests
# ---------------------------------------------------------------

class TestAdaptiveDaemon:
    """Test daemon cycle logic."""
    
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / ".git").mkdir()
        (self.tmpdir / ".agent" / "adaptive" / "proposals").mkdir(parents=True)
    
    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
    
    def test_daemon_config_defaults(self):
        from packages.adaptive_system.adaptive_daemon import DaemonConfig
        config = DaemonConfig()
        assert config.interval_minutes == 30
        assert config.dry_run is False
        assert config.auto_execute is True
        assert config.max_cycles == 0
    
    def test_change_detector_empty_state(self):
        from packages.adaptive_system.adaptive_daemon import ChangeDetector
        detector = ChangeDetector(self.tmpdir)
        state = detector._load_state()
        assert state == {}
    
    def test_change_detector_update_state(self):
        from packages.adaptive_system.adaptive_daemon import ChangeDetector
        detector = ChangeDetector(self.tmpdir)
        detector.update_state("abc123", {"total_signals": 10, "executed": 2})
        state = detector._load_state()
        assert state["last_commit_scanned"] == "abc123"
        assert state["total_cycles"] == 1
    
    def test_file_routing(self):
        from packages.adaptive_system.adaptive_daemon import ChangeDetector
        detector = ChangeDetector(self.tmpdir)
        
        files = [
            self.tmpdir / "module.py",
            self.tmpdir / "requirements.txt",
            self.tmpdir / ".gemini" / "knowledge" / "foo.md",
        ]
        routes = detector.route_files_to_scanners(files)
        
        assert "arch_drift" in routes
        assert "test_coverage" in routes
        assert "security_posture" in routes
        assert "knowledge_decay" in routes
    
    def test_overseer_rejects_dangerous(self):
        from packages.adaptive_system.adaptive_daemon import ProposalOverseer
        overseer = ProposalOverseer(mode="rules")
        
        # Mock proposal with dangerous keyword
        proposal = MagicMock()
        proposal.description = "delete all production files"
        proposal.signal_data = {}
        proposal.response_type = "doc_enrich"
        proposal.required_approval = "auto"
        
        approved, reason = overseer.evaluate(proposal)
        assert not approved
        assert "delete" in reason.lower()
    
    def test_overseer_approves_safe_type(self):
        from packages.adaptive_system.adaptive_daemon import ProposalOverseer
        overseer = ProposalOverseer(mode="rules")
        
        proposal = MagicMock()
        proposal.description = "generate documentation stub for module"
        proposal.signal_data = {}
        proposal.response_type = "doc_stub"
        proposal.required_approval = "lead"
        
        approved, reason = overseer.evaluate(proposal)
        assert approved
    
    def test_overseer_defers_risky(self):
        from packages.adaptive_system.adaptive_daemon import ProposalOverseer
        overseer = ProposalOverseer(mode="rules")
        
        proposal = MagicMock()
        proposal.description = "refactor the core architecture"
        proposal.signal_data = {}
        proposal.response_type = "arch_refactor"
        proposal.required_approval = "executive"
        
        approved, reason = overseer.evaluate(proposal)
        assert not approved
        assert "deferred" in reason.lower() or "review" in reason.lower()
    
    def test_get_status_empty(self):
        from packages.adaptive_system.adaptive_daemon import AdaptiveDaemon, DaemonConfig
        config = DaemonConfig(project_root=self.tmpdir)
        daemon = AdaptiveDaemon(config)
        status = daemon.get_status()
        assert status["total_cycles"] == 0


# ---------------------------------------------------------------
# Phase 4: Learning Engine Tests
# ---------------------------------------------------------------

class TestAdaptiveLearner:
    """Test calibration and learning logic."""
    
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.cal_path = self.tmpdir / "calibration.json"
        from packages.adaptive_system.adaptive_learner import AdaptiveLearner
        self.learner = AdaptiveLearner(self.cal_path)
    
    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
    
    def test_record_outcome(self):
        self.learner.record_outcome("test_coverage", "p1", "effective")
        assert self.cal_path.exists()
        sys_data = self.learner.state.get_system("test_coverage")
        assert sys_data["outcome_counts"]["effective"] == 1
        assert sys_data["total_proposals"] == 1
    
    def test_effectiveness_rate(self):
        for i in range(8):
            self.learner.record_outcome("test_sys", f"p{i}", "effective")
        for i in range(2):
            self.learner.record_outcome("test_sys", f"n{i}", "noise")
        
        sys_data = self.learner.state.get_system("test_sys")
        assert abs(sys_data["effectiveness_rate"] - 0.8) < 0.01
    
    def test_recalibrate_raises_threshold_on_high_fp(self):
        # Create 40% FP rate
        for i in range(4):
            self.learner.record_outcome("noisy_sys", f"fp{i}", "false_positive")
        for i in range(6):
            self.learner.record_outcome("noisy_sys", f"e{i}", "effective")
        
        changes = self.learner.recalibrate()
        assert "noisy_sys" in changes
        assert changes["noisy_sys"]["new_adjustment"] > 0
    
    def test_recalibrate_lowers_threshold_on_high_effectiveness(self):
        # Create 90% effectiveness
        for i in range(9):
            self.learner.record_outcome("good_sys", f"e{i}", "effective")
        self.learner.record_outcome("good_sys", "n1", "noise")
        
        changes = self.learner.recalibrate()
        assert "good_sys" in changes
        assert changes["good_sys"]["new_adjustment"] < 0
    
    def test_noise_suppression_after_5_rejections(self):
        for i in range(6):
            self.learner.record_outcome(
                "test_sys", f"r{i}", "rejected",
                domain_key="noisy_domain"
            )
        
        changes = self.learner.recalibrate()
        assert "test_sys" in changes
        assert "noisy_domain" in changes["test_sys"].get("suppressions_added", [])
    
    def test_is_suppressed(self):
        for i in range(6):
            self.learner.record_outcome("s", f"r{i}", "rejected", domain_key="bad_domain")
        self.learner.recalibrate()
        assert self.learner.is_suppressed("s", "bad_domain")
        assert not self.learner.is_suppressed("s", "good_domain")
    
    def test_get_report(self):
        # Fresh learner to avoid state from other tests
        fresh_path = self.tmpdir / "report_cal.json"
        from packages.adaptive_system.adaptive_learner import AdaptiveLearner
        fresh = AdaptiveLearner(fresh_path)
        fresh.record_outcome("sys1", "p1", "effective")
        report = fresh.get_report()
        assert "sys1" in report["systems"]
        assert report["total_outcomes"] == 1
    
    def test_reset_system(self):
        self.learner.record_outcome("sys1", "p1", "effective")
        self.learner.reset_system("sys1")
        report = self.learner.get_report()
        assert "sys1" not in report["systems"]
    
    def test_min_samples_guard(self):
        """Don't recalibrate with fewer than MIN_SAMPLES outcomes."""
        for i in range(3):  # Less than MIN_SAMPLES (5)
            self.learner.record_outcome("small_sys", f"p{i}", "false_positive")
        changes = self.learner.recalibrate()
        assert "small_sys" not in changes
    
    def test_invalid_outcome_raises(self):
        with pytest.raises(ValueError):
            self.learner.record_outcome("sys1", "p1", "invalid_outcome")
    
    def test_outcome_history_capped_at_500(self):
        for i in range(550):
            self.learner.record_outcome("sys1", f"p{i}", "effective")
        history = self.learner.state.data.get("outcome_history", [])
        assert len(history) <= 500


# ---------------------------------------------------------------
# Phase 5: v5 Sensor Tests
# ---------------------------------------------------------------

class TestV5Sensors:
    """Test new sensor types."""
    
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
    
    def test_performance_sensor_large_file(self):
        from packages.adaptive_system.sensors_v5 import PerformanceSensor
        sensor = PerformanceSensor()
        
        big_file = self.tmpdir / "big_module.py"
        big_file.write_text("# " + "x" * 600_000, encoding="utf-8")
        
        signal = sensor.detect({
            "project_root": str(self.tmpdir),
            "file_path": "big_module.py",
        })
        assert signal is not None
        assert "perf_regression" in signal.signal_type
    
    def test_performance_sensor_long_file(self):
        from packages.adaptive_system.sensors_v5 import PerformanceSensor
        sensor = PerformanceSensor()
        
        long_file = self.tmpdir / "long_module.py"
        long_file.write_text("\n".join([f"line_{i} = {i}" for i in range(1200)]),
                             encoding="utf-8")
        
        signal = sensor.detect({
            "project_root": str(self.tmpdir),
            "file_path": "long_module.py",
        })
        assert signal is not None
        assert signal.severity == "medium"
    
    def test_performance_sensor_normal_file(self):
        from packages.adaptive_system.sensors_v5 import PerformanceSensor
        sensor = PerformanceSensor()
        
        normal = self.tmpdir / "small.py"
        normal.write_text("print('hello')", encoding="utf-8")
        
        signal = sensor.detect({
            "project_root": str(self.tmpdir),
            "file_path": "small.py",
        })
        assert signal is None
    
    def test_dependency_sensor_unpinned(self):
        from packages.adaptive_system.sensors_v5 import DependencySensor
        sensor = DependencySensor()
        
        req = self.tmpdir / "requirements.txt"
        req.write_text("flask\nrequests\ndjango\nnumpy\npandas\n", encoding="utf-8")
        
        signal = sensor.detect({"project_root": str(self.tmpdir)})
        assert signal is not None
        assert signal.data["count"] > 3
    
    def test_dependency_sensor_pinned(self):
        from packages.adaptive_system.sensors_v5 import DependencySensor
        sensor = DependencySensor()
        
        req = self.tmpdir / "requirements.txt"
        req.write_text("flask==2.0\nrequests==2.28\n", encoding="utf-8")
        
        signal = sensor.detect({"project_root": str(self.tmpdir)})
        assert signal is None
    
    def test_dependency_sensor_wildcard_npm(self):
        from packages.adaptive_system.sensors_v5 import DependencySensor
        sensor = DependencySensor()
        
        pkg = self.tmpdir / "package.json"
        pkg.write_text(json.dumps({
            "dependencies": {"react": "*", "express": "latest"},
        }), encoding="utf-8")
        
        signal = sensor.detect({"project_root": str(self.tmpdir)})
        assert signal is not None
        assert signal.severity == "high"
    
    def test_context_sensor_storage_bloat(self):
        from packages.adaptive_system.sensors_v5 import ContextSensor
        sensor = ContextSensor()
        
        adaptive_dir = self.tmpdir / ".agent" / "adaptive"
        adaptive_dir.mkdir(parents=True)
        # Create 15MB of files
        for i in range(15):
            (adaptive_dir / f"data_{i}.json").write_bytes(b"x" * 1024 * 1024)
        
        signal = sensor.detect({"project_root": str(self.tmpdir)})
        assert signal is not None
        assert signal.data["size_mb"] > 10
    
    def test_agent_sensor_domain_key(self):
        from packages.adaptive_system.sensors_v5 import AgentSensor
        sensor = AgentSensor()
        
        from packages.adaptive_system.adaptive_core import Signal
        sig = Signal(signal_type="agent_effectiveness", source="genomes")
        dk = sensor.get_domain_key(sig)
        assert dk == "agent:genomes"


# ---------------------------------------------------------------
# Phase 6: Relay Tests
# ---------------------------------------------------------------

class TestRelayConfig:
    """Test relay configuration."""
    
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
    
    def test_default_config(self):
        from packages.adaptive_system.adaptive_relay import RelayConfig
        config = RelayConfig(config_path=self.tmpdir / "relay.json")
        assert config.local_name == "windows"
        assert len(config.peers) == 1  # Default ghost peer
        assert config.peers[0]["name"] == "ghost"
    
    def test_add_peer(self):
        from packages.adaptive_system.adaptive_relay import RelayConfig
        config = RelayConfig(config_path=self.tmpdir / "relay.json")
        config.add_peer("cloud", "http://cloud:5001", "Cloud server")
        assert len(config.peers) == 2
        assert config.peers[1]["name"] == "cloud"
        assert (self.tmpdir / "relay.json").exists()
    
    def test_get_active_peers(self):
        from packages.adaptive_system.adaptive_relay import RelayConfig
        config = RelayConfig(
            peers=[
                {"name": "a", "url": "http://a:5001", "active": True},
                {"name": "b", "url": "http://b:5001", "active": False},
                {"name": "c", "url": "http://c:5001", "active": True},
            ],
            config_path=self.tmpdir / "relay.json",
        )
        active = config.get_active_peers()
        assert len(active) == 2
    
    def test_transport_ping_unreachable(self):
        from packages.adaptive_system.adaptive_relay import MCPBridgeTransport
        transport = MCPBridgeTransport()
        assert not transport.ping("http://nonexistent:9999")
    
    def test_signal_relay_push_no_signals(self):
        from packages.adaptive_system.adaptive_relay import SignalRelay, RelayConfig
        config = RelayConfig(config_path=self.tmpdir / "relay.json")
        relay = SignalRelay(config)
        
        # Push with no tracker data
        with patch.object(Path, 'cwd', return_value=self.tmpdir):
            result = relay.push_signals("http://localhost:5001")
            assert result["success"]
            assert result["pushed"] == 0
    
    def test_relay_status(self):
        from packages.adaptive_system.adaptive_relay import SignalRelay, RelayConfig
        config = RelayConfig(config_path=self.tmpdir / "relay.json")
        relay = SignalRelay(config)
        status = relay.get_status()
        assert status["local_machine"] == "windows"
        assert len(status["peers"]) == 1
