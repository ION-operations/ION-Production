"""
SCOR Storage Layer

Storage for invariants, baselines, and attack scenarios.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import Invariant, Baseline


class InvariantStorage:
    """Storage for invariant rules"""
    
    def __init__(self, config):
        self.config = config
        self.invariants: Dict[str, Invariant] = {}
    
    def load(self) -> Dict[str, Invariant]:
        """Load invariants from YAML file"""
        if not self.config.invariants_file.exists():
            return {}
        
        with open(self.config.invariants_file, 'r') as f:
            data = yaml.safe_load(f)
        
        invariants = {}
        for item in data.get('invariants', []):
            invariant = Invariant(
                id=item['id'],
                category=item['category'],
                description=item['description'],
                severity=item['severity'],
                check_function=None,  # Set by loader
                admin_signature=item.get('admin_signature', ''),
                enabled=item.get('enabled', True)
            )
            invariants[invariant.id] = invariant
        
        return invariants
    
    def verify_signature(self, invariant: Invariant) -> bool:
        """Verify admin signature on invariant"""
        if not self.config.require_admin_signature:
            return True
        
        # TODO: Implement cryptographic verification
        return invariant.admin_signature.startswith("sig_")


class BaselineStorage:
    """Storage for baseline probe answers"""
    
    def __init__(self, config):
        self.config = config
    
    def load_baseline(self, probe_id: str) -> Optional[Baseline]:
        """Load baseline for specific probe"""
        baseline_file = self.config.baselines_dir / f"{probe_id}.json"
        
        if not baseline_file.exists():
            return None
        
        with open(baseline_file, 'r') as f:
            data = json.load(f)
        
        return Baseline(
            probe_id=data['probe_id'],
            answer=data['answer'],
            answer_embedding=data['answer_embedding'],
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            admin_signature=data.get('admin_signature', '')
        )
    
    def save_baseline(self, baseline: Baseline) -> None:
        """Save baseline to file"""
        baseline_file = self.config.baselines_dir / f"{baseline.probe_id}.json"
        
        with open(baseline_file, 'w') as f:
            json.dump({
                'probe_id': baseline.probe_id,
                'answer': baseline.answer,
                'answer_embedding': baseline.answer_embedding,
                'version': baseline.version,
                'timestamp': baseline.timestamp.isoformat(),
                'admin_signature': baseline.admin_signature
            }, f, indent=2)
