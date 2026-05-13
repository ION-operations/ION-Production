"""
SCOR Configuration

Configuration system for Sanity Core.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class SCORConfig:
    """Complete SCOR configuration"""
    
    # === Paths ===
    data_dir: Path = Path(__file__).parent.parent / "data"
    invariants_file: Path = data_dir / "invariants.yaml"
    baselines_dir: Path = data_dir / "baselines"
    attacks_dir: Path = data_dir / "attacks"
    logs_dir: Path = data_dir / "logs"
    
    # === Drift Detection Thresholds ===
    drift_threshold_stable: float = 0.9
    drift_threshold_mild: float = 0.7
    drift_threshold_moderate: float = 0.5
    drift_threshold_severe: float = 0.3
    
    # === Signal Detection Thresholds ===
    signal_threshold_low: float = 0.3
    signal_threshold_medium: float = 0.5
    signal_threshold_high: float = 0.7
    signal_threshold_critical: float = 0.9
    
    # === Gate Decision Thresholds ===
    gate_block_threshold: float = 0.5
    gate_high_confidence_threshold: float = 0.8
    
    # === Weights for Gate Decision ===
    weight_invariant: float = 0.40
    weight_drift: float = 0.30
    weight_social: float = 0.20
    weight_red_cell: float = 0.10
    
    # === Admin Signature Verification ===
    admin_public_key: Optional[str] = None
    require_admin_signature: bool = True
    
    # === Performance Settings ===
    max_probes_per_cycle: int = 10
    probe_timeout_seconds: int = 5
    simulation_timeout_seconds: int = 30
    max_simulation_attacks: int = 20
    
    # === Integration Flags ===
    enable_cas_integration: bool = True
    enable_rid_integration: bool = True
    enable_tcs_integration: bool = True
    enable_vif_integration: bool = True
    
    # === Logging ===
    enable_detailed_logging: bool = True
    log_level: str = "INFO"
    
    # === Advanced ===
    enable_quarantine: bool = True
    quarantine_timeout_seconds: int = 300
    enable_learning: bool = True
    
    def validate(self) -> None:
        """Validate configuration"""
        assert 0.0 <= self.drift_threshold_stable <= 1.0
        assert 0.0 <= self.drift_threshold_mild <= 1.0
        assert self.drift_threshold_stable > self.drift_threshold_mild
        assert self.max_probes_per_cycle > 0
        assert self.probe_timeout_seconds > 0
        assert sum([
            self.weight_invariant,
            self.weight_drift,
            self.weight_social,
            self.weight_red_cell
        ]) == 1.0
        
        # Create directories if they don't exist
        for dir_path in [self.data_dir, self.baselines_dir, self.attacks_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "data_dir": str(self.data_dir),
            "drift_threshold_stable": self.drift_threshold_stable,
            "drift_threshold_mild": self.drift_threshold_mild,
            "signal_threshold_high": self.signal_threshold_high,
            "gate_block_threshold": self.gate_block_threshold,
            "enable_cas_integration": self.enable_cas_integration,
            "require_admin_signature": self.require_admin_signature
        }
