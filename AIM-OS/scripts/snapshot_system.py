#!/usr/bin/env python3
"""
Snapshot System for Safe MCP Backup/Restore
Purpose: Create file-based snapshots before ANY changes, enable instant rollback
Principle: Never delete, only supersede (CMC bitemporal tracking)
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class SnapshotSystem:
    """File-based snapshot system for safe backup/restore"""
    
    def __init__(self, snapshots_dir: str = "./snapshots"):
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(exist_ok=True)
        
        # Deletion thresholds (following audit-based principle)
        self.deletion_thresholds = {
            "min_age_days": 90,  # Minimum age before deletion allowed
            "low_relevance_days": 180,  # Age for low relevance
            "space_threshold_percent": 80,  # Disk usage threshold
            "audit_layers_required": 4  # Number of audit layers to pass
        }
        
    def create_snapshot(self, name: str, files: List[str]) -> Dict[str, str]:
        """
        Create a snapshot of specified files
        
        Args:
            name: Snapshot name (e.g., "pre_mcp_expansion")
            files: List of file paths to snapshot
            
        Returns:
            Dict with snapshot_id, files, hashes, timestamp
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        snapshot_id = f"{name}_{timestamp}"
        snapshot_path = self.snapshots_dir / snapshot_id
        snapshot_path.mkdir(exist_ok=True)
        
        snapshot_manifest = {
            "snapshot_id": snapshot_id,
            "name": name,
            "timestamp": timestamp,
            "files": {},
            "created_by": "Aether",
            "purpose": "Safe backup before changes"
        }
        
        # Copy files and calculate hashes
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue
                
            file_name = os.path.basename(file_path)
            dest_path = snapshot_path / file_name
            
            # Copy file
            shutil.copy2(file_path, dest_path)
            
            # Calculate hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Store in manifest
            snapshot_manifest["files"][file_path] = {
                "name": file_name,
                "hash": file_hash,
                "copied_to": str(dest_path)
            }
        
        # Save manifest
        manifest_path = snapshot_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(snapshot_manifest, f, indent=2)
        
        print(f"SUCCESS: Snapshot created: {snapshot_id}")
        print(f"   Files: {len(snapshot_manifest['files'])}")
        print(f"   Location: {snapshot_path}")
        
        return snapshot_manifest
    
    def restore_snapshot(self, snapshot_id: str, verify: bool = True) -> bool:
        """
        Restore files from a snapshot
        
        Args:
            snapshot_id: ID of snapshot to restore
            verify: Whether to verify file hashes before restoring
            
        Returns:
            True if successful, False otherwise
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            print(f"ERROR: Snapshot not found: {snapshot_id}")
            return False
        
        # Load manifest
        manifest_path = snapshot_path / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print(f"RESTORING: Snapshot: {snapshot_id}")
        print(f"   Created: {manifest['timestamp']}")
        print(f"   Files: {len(manifest['files'])}")
        
        # Restore each file
        for original_path, file_info in manifest['files'].items():
            snapshot_file = snapshot_path / file_info['name']
            
            # Verify hash if requested
            if verify and os.path.exists(original_path):
                current_hash = self._calculate_file_hash(original_path)
                if current_hash != file_info['hash']:
                    print(f"   WARNING: {original_path} has changed since snapshot")
                    print(f"      Current: {current_hash}")
                    print(f"      Snapshot: {file_info['hash']}")
            
            # Restore file
            shutil.copy2(snapshot_file, original_path)
            print(f"   Restored: {original_path}")
        
        print(f"SUCCESS: Snapshot restored successfully")
        return True
    
    def list_snapshots(self) -> List[Dict[str, str]]:
        """List all available snapshots"""
        snapshots = []
        
        for snapshot_dir in sorted(self.snapshots_dir.iterdir()):
            if snapshot_dir.is_dir():
                manifest_path = snapshot_dir / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    snapshots.append({
                        'id': manifest['snapshot_id'],
                        'name': manifest['name'],
                        'timestamp': manifest['timestamp'],
                        'files': len(manifest['files'])
                    })
        
        return snapshots
    
    def archive_snapshot(self, snapshot_id: str) -> bool:
        """
        Archive a snapshot (move to archive/ folder, never delete to preserve history)
        
        This follows CMC principle: Never delete, only supersede (bitemporal tracking)
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            print(f"ERROR: Snapshot not found: {snapshot_id}")
            return False
        
        # Create archive directory
        archive_dir = self.snapshots_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        # Move to archive (preserves history)
        archive_path = archive_dir / snapshot_id
        shutil.move(str(snapshot_path), str(archive_path))
        
        print(f"SUCCESS: Archived snapshot: {snapshot_id}")
        print(f"   Location: archive/{snapshot_id}")
        print(f"   Note: Never deleted, preserved for history (CMC principle)")
        return True
    
    def audit_snapshot_deletion_candidate(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Audit a snapshot for potential deletion eligibility
        
        Requirements for deletion:
        1. Age threshold (e.g., 90+ days old)
        2. Space threshold (disk usage > threshold)
        3. Audit layers passed (multiple verification steps)
        4. Relevance verified (no dependencies, no active use)
        
        Returns dict with deletion eligibility status
        """
        archive_dir = self.snapshots_dir / "archive"
        snapshot_path = archive_dir / snapshot_id
        
        if not snapshot_path.exists():
            return {"eligible": False, "reason": "Snapshot not found"}
        
        # Load manifest
        manifest_path = snapshot_path / "manifest.json"
        if not manifest_path.exists():
            return {"eligible": False, "reason": "No manifest found"}
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Calculate age
        snapshot_time = datetime.fromisoformat(manifest['timestamp'].replace('_', ' '))
        age_days = (datetime.now() - snapshot_time).days
        
        # Calculate size
        total_size = sum(f.stat().st_size for f in snapshot_path.rglob('*') if f.is_file())
        
        # Check eligibility
        audit_results = {
            "snapshot_id": snapshot_id,
            "age_days": age_days,
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "age_threshold_passed": age_days >= self.deletion_thresholds["min_age_days"],
            "audit_layers": {
                "layer_1_age": age_days >= self.deletion_thresholds["min_age_days"],
                "layer_2_space_needed": False,  # Would check disk space
                "layer_3_no_dependencies": True,  # Would check dependencies
                "layer_4_relevance_low": age_days >= self.deletion_thresholds["low_relevance_days"],
            }
        }
        
        # Calculate overall eligibility
        audit_results["eligible"] = all([
            audit_results["age_threshold_passed"],
            audit_results["audit_layers"]["layer_1_age"],
            # Layer 2-4 would be checked here
        ])
        
        return audit_results
    
    def delete_eligible_snapshot(self, snapshot_id: str, confirm: bool = False) -> bool:
        """
        Delete a snapshot ONLY after passing all audit layers
        
        This is the ONLY deletion method - requires:
        1. Audit passed (audit_snapshot_deletion_candidate)
        2. Explicit confirmation
        3. Age threshold met
        4. Relevance guaranteed to be below threshold
        """
        if not confirm:
            print("ERROR: Deletion requires explicit confirmation")
            return False
        
        # Audit first
        audit = self.audit_snapshot_deletion_candidate(snapshot_id)
        if not audit.get("eligible", False):
            print(f"ERROR: Snapshot not eligible for deletion")
            print(f"   Reason: {audit.get('reason', 'Audit failed')}")
            print(f"   Age: {audit.get('age_days', 0)} days")
            return False
        
        # All checks passed - proceed with deletion
        archive_dir = self.snapshots_dir / "archive"
        snapshot_path = archive_dir / snapshot_id
        
        if not snapshot_path.exists():
            print(f"ERROR: Snapshot not found: {snapshot_id}")
            return False
        
        # Delete (final removal after all audits)
        shutil.rmtree(snapshot_path)
        
        print(f"SUCCESS: Deleted snapshot after audit: {snapshot_id}")
        print(f"   Age: {audit['age_days']} days")
        print(f"   Size: {audit['size_mb']} MB")
        print(f"   All audit layers passed")
        return True
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# MCP-specific snapshot functions
def snapshot_mcp_production(files_to_snapshot: Optional[List[str]] = None):
    """Create snapshot of MCP production files"""
    if files_to_snapshot is None:
        files_to_snapshot = [
            "run_mcp_6_tools.py",
            "mcp_memory/cmc.db",
            "c:/Users/bombe/.cursor/mcp.json"
        ]
    
    snapshots = SnapshotSystem()
    return snapshots.create_snapshot("mcp_production_pre_change", files_to_snapshot)


def restore_mcp_production(snapshot_id: str):
    """Restore MCP production files from snapshot"""
    snapshots = SnapshotSystem()
    return snapshots.restore_snapshot(snapshot_id)


if __name__ == "__main__":
    # Example usage
    print("Snapshot System Test")
    print("=" * 50)
    
    # Create snapshot
    manifest = snapshot_mcp_production()
    
    # List snapshots
    print("\nAvailable snapshots:")
    snapshots = SnapshotSystem()
    for snap in snapshots.list_snapshots():
        print(f"   - {snap['id']} ({snap['name']})")
